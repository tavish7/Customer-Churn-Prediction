CREATE DATABASE customer_churn;
USE customer_churn;

/*
Create Tables
*/

-- 1. Create Location Dimension
CREATE TABLE dim_location (
    zip_code INT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT
);

-- 2. Create Demographics Dimension
CREATE TABLE dim_demographics (
    customerid VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen VARCHAR(5),
    partner VARCHAR(5),
    dependents VARCHAR(5)
);

-- 3. Create Products Dimension (Only actual services)
CREATE TABLE dim_products (
    customerid VARCHAR(20) PRIMARY KEY,
    phone_service VARCHAR(5),
    multiple_lines VARCHAR(20),
    internet_service VARCHAR(20),
    online_security VARCHAR(25),
    online_backup VARCHAR(25),
    device_protection VARCHAR(25),
    tech_support VARCHAR(25),
    streaming_tv VARCHAR(25),
    streaming_movies VARCHAR(25)
);

-- 4. Create Account Terms Dimension (Only administrative/billing details)
CREATE TABLE dim_account_terms (
    customerid VARCHAR(20) PRIMARY KEY,
    contract VARCHAR(20),
    paperless_billing VARCHAR(5),
    payment_method VARCHAR(30)
);

-- 5. Create the Core Fact Table
CREATE TABLE fact_churn_metrics (
    customerid VARCHAR(20) PRIMARY KEY,
    zip_code INT,
    tenure_months INT,
    tenure_group VARCHAR(20),
    monthly_charges FLOAT,
    total_charges FLOAT,
    avg_monthly_usage FLOAT,
    payment_risk VARCHAR(20),
    customer_value_segment VARCHAR(20),
    cltv INT,
    total_services INT,
    churn_score INT,
    churn_label VARCHAR(5),
    churn_value INT,
    FOREIGN KEY (customerid) REFERENCES dim_demographics(customerid),
    FOREIGN KEY (customerid) REFERENCES dim_products(customerid),
    FOREIGN KEY (customerid) REFERENCES dim_account_terms(customerid),
    FOREIGN KEY (zip_code) REFERENCES dim_location(zip_code)
);

/*
Insert values inside tables
*/

-- Populate Location
INSERT INTO dim_location (zip_code, latitude, longitude)
SELECT DISTINCT zip_code, latitude, longitude
FROM staging_churn_data;

-- Populate Demographics
INSERT INTO dim_demographics (customerid, gender, senior_citizen, partner, dependents)
SELECT DISTINCT customerid, gender, senior_citizen, partner, dependents
FROM staging_churn_data;

-- Populate Products
INSERT INTO dim_products (customerid, phone_service, multiple_lines, internet_service, online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies)
SELECT DISTINCT customerid, phone_service, multiple_lines, internet_service, online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies
FROM staging_churn_data;

-- Populate Account Terms
INSERT INTO dim_account_terms (customerid, contract, paperless_billing, payment_method)
SELECT DISTINCT customerid, contract, paperless_billing, payment_method
FROM staging_churn_data;

-- Populate Fact Table
INSERT INTO fact_churn_metrics (customerid, zip_code, tenure_months, tenure_group, monthly_charges, total_charges, avg_monthly_usage, payment_risk, customer_value_segment, cltv, total_services, churn_score, churn_label, churn_value)
SELECT customerid, zip_code, tenure_months, tenure_group, monthly_charges, total_charges, avg_monthly_usage, payment_risk, customer_value_segment, cltv, total_services, churn_score, churn_label, churn_value
FROM staging_churn_data;

/*
Rename staging_churn_data to backup_raw_data as a backup reference
*/
RENAME TABLE staging_churn_data TO backup_raw_data;

