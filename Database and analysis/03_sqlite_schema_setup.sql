-- ============================================================================
-- Phase 5 - SQLite port of the Customer Churn star schema
-- ----------------------------------------------------------------------------
-- This is the SQLite equivalent of `01_database_schema_setup.sql` (MySQL).
-- It documents the full migration so the database can also be built manually
-- with the sqlite3 CLI. The chatbot itself builds the DB programmatically via
-- phase5_chatbot/database/init_db.py, which loads the CSV with pandas.
--
-- Key MySQL -> SQLite changes:
--   * No CREATE DATABASE / USE  -> everything lives in one churn.db file
--   * VARCHAR(n) -> TEXT, FLOAT -> REAL, INT -> INTEGER
--   * RENAME TABLE a TO b -> ALTER TABLE a RENAME TO b
--   * UPDATE ... INNER JOIN -> city is populated directly via GROUP BY
--
-- Manual build (from this folder):
--   sqlite3 churn.db
--   sqlite> .mode csv
--   sqlite> .import "../Data Files/customer_churn_clean.csv" staging_churn_data
--   sqlite> .read 03_sqlite_schema_setup.sql
-- ============================================================================

-- NOTE: `staging_churn_data` is expected to already exist, created either by
-- the .import command above or by pandas.to_sql in init_db.py.

DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_demographics;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_account_terms;
DROP TABLE IF EXISTS fact_churn_metrics;
DROP TABLE IF EXISTS backup_raw_data;

-- 1. Location dimension
CREATE TABLE dim_location (
    zip_code  INTEGER PRIMARY KEY,
    latitude  REAL,
    longitude REAL,
    city      TEXT
);

-- 2. Demographics dimension
CREATE TABLE dim_demographics (
    customerid     TEXT PRIMARY KEY,
    gender         TEXT,
    senior_citizen TEXT,
    partner        TEXT,
    dependents     TEXT
);

-- 3. Products dimension
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

-- 4. Account terms dimension
CREATE TABLE dim_account_terms (
    customerid        TEXT PRIMARY KEY,
    contract          TEXT,
    paperless_billing TEXT,
    payment_method    TEXT
);

-- 5. Core fact table
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

-- Populate dimensions
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

-- Populate fact
INSERT INTO fact_churn_metrics (customerid, zip_code, tenure_months, tenure_group,
                                monthly_charges, total_charges, avg_monthly_usage,
                                payment_risk, customer_value_segment, cltv,
                                total_services, churn_score, churn_label, churn_value)
SELECT customerid, zip_code, tenure_months, tenure_group,
       monthly_charges, total_charges, avg_monthly_usage,
       payment_risk, customer_value_segment, cltv,
       total_services, churn_score, churn_label, churn_value
FROM staging_churn_data;

-- Keep a backup of the raw staged rows (Phase 3 parity)
ALTER TABLE staging_churn_data RENAME TO backup_raw_data;

CREATE INDEX IF NOT EXISTS idx_fact_zip      ON fact_churn_metrics (zip_code);
CREATE INDEX IF NOT EXISTS idx_fact_churnval ON fact_churn_metrics (churn_value);
