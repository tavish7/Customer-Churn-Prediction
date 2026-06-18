"""Database schema context injected into Gemini's SQL-generation prompt.

This string is static text derived from the Phase 3 star schema
(`01_database_schema_setup.sql`) and the feature-engineering rules in the
Phase 1 notebook (`01_EDA_and_Preprocessing.ipynb`). The running chatbot reads
this module, never the notebook itself.
"""
from __future__ import annotations

SCHEMA_PROMPT = """
You are querying a SQLite database about Telco customer churn (7,043 customers).
The data uses a star schema: one fact table joined to four dimension tables on
`customerid`, plus a location dimension joined on `zip_code`.

TABLES AND COLUMNS
------------------
fact_churn_metrics  (one row per customer -- the central fact table)
  customerid              TEXT     PK, e.g. '3668-QPYBK'
  zip_code                INTEGER  FK -> dim_location.zip_code
  tenure_months           INTEGER  months the customer has stayed
  tenure_group            TEXT     '0-1 Year','1-2 Years','2-4 Years','4+ Years'
  monthly_charges         REAL     current monthly bill (USD)
  total_charges           REAL     lifetime amount billed (USD)
  avg_monthly_usage       REAL     total_charges / tenure_months
  payment_risk            TEXT     'Low Risk','Medium Risk','High Risk'
  customer_value_segment  TEXT     'Bronze','Silver','Gold','Platinum' (CLTV quartiles)
  cltv                    INTEGER  customer lifetime value score
  total_services          INTEGER  count of active services (0-9)
  churn_score             INTEGER  propensity-to-churn score (0-100)
  churn_label             TEXT     'Yes' = churned, 'No' = retained
  churn_value             INTEGER  1 = churned, 0 = retained

dim_demographics  (join: customerid)
  customerid TEXT PK, gender ('Male'/'Female'), senior_citizen ('Yes'/'No'),
  partner ('Yes'/'No'), dependents ('Yes'/'No')

dim_products  (join: customerid)
  customerid TEXT PK, phone_service ('Yes'/'No'),
  multiple_lines ('Yes'/'No'/'No phone service'),
  internet_service ('DSL'/'Fiber optic'/'No'),
  online_security, online_backup, device_protection, tech_support,
  streaming_tv, streaming_movies
    -- each of the above is 'Yes'/'No'/'No internet service'

dim_account_terms  (join: customerid)
  customerid TEXT PK,
  contract ('Month-to-month'/'One year'/'Two year'),
  paperless_billing ('Yes'/'No'),
  payment_method ('Electronic check'/'Mailed check'/
                  'Bank transfer (automatic)'/'Credit card (automatic)')

dim_location  (join: zip_code)
  zip_code INTEGER PK, latitude REAL, longitude REAL, city TEXT

JOIN RULES
----------
- Demographics / products / account terms: JOIN ... ON f.customerid = d.customerid
- Location: JOIN dim_location l ON f.zip_code = l.zip_code

SQLITE DIALECT RULES (important)
--------------------------------
- This is SQLite. `/` between two integers does INTEGER division.
  To compute a percentage rate, multiply by 100.0 BEFORE dividing, e.g.
      ROUND(SUM(churn_value) * 100.0 / COUNT(*), 2)
  or use AVG(churn_value) * 100 (AVG returns a float).
- Use single quotes for text literals.
- Window functions (NTILE, RANK, SUM() OVER) are supported.
- Return only the columns needed to answer the question.

BUSINESS DEFINITIONS
--------------------
- "Churn rate" = percentage of customers with churn_value = 1.
- "Active" / "retained" customers have churn_value = 0 (churn_label = 'No').
- "ARPU" = AVG(monthly_charges).
- "Revenue lost to churn" = SUM(monthly_charges) WHERE churn_value = 1.
- "At-risk" active customers = churn_value = 0 ordered by churn_score DESC.

OUTPUT CONTRACT
---------------
- Generate a SINGLE read-only SELECT (or WITH ... SELECT) statement.
- Do NOT use INSERT/UPDATE/DELETE/DROP/ALTER/CREATE or multiple statements.
- Return ONLY the SQL. No markdown fences, no commentary.
""".strip()
