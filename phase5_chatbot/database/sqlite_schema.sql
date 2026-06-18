

-- Make the build repeatable.
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_demographics;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_account_terms;
DROP TABLE IF EXISTS fact_churn_metrics;
DROP TABLE IF EXISTS backup_raw_data;

-- ----------------------------------------------------------------------------
-- 1. Location dimension (city included up front; populated directly)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_location (
    zip_code  INTEGER PRIMARY KEY,
    latitude  REAL,
    longitude REAL,
    city      TEXT
);

-- ----------------------------------------------------------------------------
-- 2. Demographics dimension
-- ----------------------------------------------------------------------------
CREATE TABLE dim_demographics (
    customerid     TEXT PRIMARY KEY,
    gender         TEXT,
    senior_citizen TEXT,
    partner        TEXT,
    dependents     TEXT
);

-- ----------------------------------------------------------------------------
-- 3. Products dimension
-- ----------------------------------------------------------------------------
CREATE TABLE dim_products (
    customerid        TEXT PRIMARY KEY,
    phone_service     TEXT,
    multiple_lines    TEXT,
    internet_service  TEXT,
    online_security   TEXT,
    online_backup     TEXT,
    device_protection TEXT,
    tech_support      TEXT,
    streaming_tv      TEXT,
    streaming_movies  TEXT
);

-- ----------------------------------------------------------------------------
-- 4. Account terms dimension
-- ----------------------------------------------------------------------------
CREATE TABLE dim_account_terms (
    customerid        TEXT PRIMARY KEY,
    contract          TEXT,
    paperless_billing TEXT,
    payment_method    TEXT
);

-- ----------------------------------------------------------------------------
-- 5. Core fact table
-- ----------------------------------------------------------------------------
CREATE TABLE fact_churn_metrics (
    customerid             TEXT PRIMARY KEY,
    zip_code               INTEGER,
    tenure_months          INTEGER,
    tenure_group           TEXT,
    monthly_charges        REAL,
    total_charges          REAL,
    avg_monthly_usage      REAL,
    payment_risk           TEXT,
    customer_value_segment TEXT,
    cltv                   INTEGER,
    total_services         INTEGER,
    churn_score            INTEGER,
    churn_label            TEXT,
    churn_value            INTEGER,
    FOREIGN KEY (customerid) REFERENCES dim_demographics (customerid),
    FOREIGN KEY (zip_code)   REFERENCES dim_location (zip_code)
);

-- ----------------------------------------------------------------------------
-- Populate dimensions and fact from the staged CSV data.
-- GROUP BY zip_code guarantees one row per location primary key.
-- ----------------------------------------------------------------------------
INSERT INTO dim_location (zip_code, latitude, longitude, city)
SELECT zip_code, MIN(latitude), MIN(longitude), MIN(city)
FROM staging_churn_data
GROUP BY zip_code;

INSERT INTO dim_demographics (customerid, gender, senior_citizen, partner, dependents)
SELECT DISTINCT customerid, gender, senior_citizen, partner, dependents
FROM staging_churn_data;

INSERT INTO dim_products (customerid, phone_service, multiple_lines, internet_service,
                          online_security, online_backup, device_protection,
                          tech_support, streaming_tv, streaming_movies)
SELECT DISTINCT customerid, phone_service, multiple_lines, internet_service,
       online_security, online_backup, device_protection,
       tech_support, streaming_tv, streaming_movies
FROM staging_churn_data;

INSERT INTO dim_account_terms (customerid, contract, paperless_billing, payment_method)
SELECT DISTINCT customerid, contract, paperless_billing, payment_method
FROM staging_churn_data;

INSERT INTO fact_churn_metrics (customerid, zip_code, tenure_months, tenure_group,
                                monthly_charges, total_charges, avg_monthly_usage,
                                payment_risk, customer_value_segment, cltv,
                                total_services, churn_score, churn_label, churn_value)
SELECT customerid, zip_code, tenure_months, tenure_group,
       monthly_charges, total_charges, avg_monthly_usage,
       payment_risk, customer_value_segment, cltv,
       total_services, churn_score, churn_label, churn_value
FROM staging_churn_data;

-- ----------------------------------------------------------------------------
-- Keep the raw staged rows as a backup reference table (Phase 3 parity).
-- ----------------------------------------------------------------------------
ALTER TABLE staging_churn_data RENAME TO backup_raw_data;

-- Helpful indexes for the join-heavy analytical queries.
CREATE INDEX IF NOT EXISTS idx_fact_zip       ON fact_churn_metrics (zip_code);
CREATE INDEX IF NOT EXISTS idx_fact_churnval  ON fact_churn_metrics (churn_value);
