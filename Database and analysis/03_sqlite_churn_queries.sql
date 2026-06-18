-- ============================================================================
-- Phase 5 - SQLite port of the 26 churn analysis queries
-- ----------------------------------------------------------------------------
-- SQLite equivalent of `02_churn_analysis_queries.sql` (MySQL).
--
-- IMPORTANT DIALECT FIX:
--   In MySQL, `/` between two integers returns a decimal. In SQLite, `/`
--   between two integers performs INTEGER division (e.g. 1869 / 7043 = 0).
--   Every churn-rate expression of the form
--       (SUM(churn_value) / COUNT(...)) * 100
--   has been rewritten as
--       SUM(churn_value) * 100.0 / COUNT(...)
--   so the division happens in floating point. AVG(churn_value) is already a
--   float in SQLite and needs no change.
--
--   Window functions (NTILE, RANK, SUM() OVER) require SQLite 3.25+.
-- ============================================================================

-- Q1. What is the overall churn rate?   (expected: 7043 / 1869 / 26.54)
SELECT
    COUNT(*) AS total_customers,
    SUM(churn_value) AS churned_customers,
    ROUND(SUM(churn_value) * 100.0 / COUNT(*), 2) AS churn_rate
FROM fact_churn_metrics;

-- ----------------------------------------------------------------------------
-- Q2. How many customers are active and how many have churned?
SELECT
    churn_label,
    COUNT(*) AS customers
FROM fact_churn_metrics
GROUP BY churn_label;

-- ----------------------------------------------------------------------------
-- Q3. Which gender has the highest churn rate?
SELECT
    d.gender,
    COUNT(*) AS customers,
    SUM(f.churn_value) AS churned,
    ROUND(SUM(f.churn_value) * 100.0 / COUNT(*), 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_demographics d ON f.customerid = d.customerid
GROUP BY d.gender;

-- ----------------------------------------------------------------------------
-- Q4. Do senior citizens churn more?
SELECT
    senior_citizen,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_demographics d ON f.customerid = d.customerid
GROUP BY senior_citizen;

-- ----------------------------------------------------------------------------
-- Q5. Does having dependents reduce churn?
SELECT
    dependents,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_demographics d ON f.customerid = d.customerid
GROUP BY dependents;

-- ----------------------------------------------------------------------------
-- Q6. Which contract type has the highest churn?
SELECT
    contract,
    COUNT(*) AS customers,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_account_terms a ON f.customerid = a.customerid
GROUP BY contract
ORDER BY churn_rate DESC;

-- ----------------------------------------------------------------------------
-- Q7. Which payment method is most associated with churn?
SELECT
    payment_method,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_account_terms a ON f.customerid = a.customerid
GROUP BY payment_method
ORDER BY churn_rate DESC;

-- ----------------------------------------------------------------------------
-- Q8. Does paperless billing affect churn?
SELECT
    paperless_billing,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_account_terms a ON f.customerid = a.customerid
GROUP BY paperless_billing;

-- ----------------------------------------------------------------------------
-- Q9. ARPU (Average Revenue Per User) vs churn status
SELECT
    churn_label,
    COUNT(customerid) AS total_customers,
    ROUND(AVG(monthly_charges), 2) AS arpu_monthly
FROM fact_churn_metrics
GROUP BY churn_label;

-- ----------------------------------------------------------------------------
-- Q10. Monthly revenue lost during churn
SELECT
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue_lost
FROM fact_churn_metrics
WHERE churn_value = 1;

-- ----------------------------------------------------------------------------
-- Q11. True ARPU for the active customer base
SELECT
    COUNT(customerid) AS total_active_users,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue,
    ROUND(AVG(monthly_charges), 2) AS true_arpu
FROM fact_churn_metrics
WHERE churn_value = 0;

-- ----------------------------------------------------------------------------
-- Q12. Revenue contribution by churn status
SELECT
    churn_label,
    ROUND(SUM(monthly_charges), 2) AS revenue
FROM fact_churn_metrics
GROUP BY churn_label;

-- ----------------------------------------------------------------------------
-- Q13. Which customer value segment loses the most revenue?
SELECT
    customer_value_segment,
    ROUND(SUM(monthly_charges), 2) AS revenue_lost
FROM fact_churn_metrics
WHERE churn_value = 1
GROUP BY customer_value_segment
ORDER BY revenue_lost DESC;

-- ----------------------------------------------------------------------------
-- Q14. Effect of long-term contracts on churn rate
SELECT
    a.contract,
    COUNT(f.customerid) AS customer_base,
    ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS churn_rate_pct
FROM fact_churn_metrics f
JOIN dim_account_terms a ON f.customerid = a.customerid
GROUP BY a.contract
ORDER BY churn_rate_pct DESC;

-- ----------------------------------------------------------------------------
-- Q15. Are customers who use more services less likely to leave?
SELECT
    f.total_services,
    COUNT(f.customerid) AS total_customers,
    ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS churn_rate_pct
FROM fact_churn_metrics f
GROUP BY f.total_services
ORDER BY f.total_services ASC;

-- ----------------------------------------------------------------------------
-- Q16. At what tenure do customers churn most? (count of churners)
SELECT
    tenure_group,
    COUNT(*) AS churned_customers
FROM fact_churn_metrics
WHERE churn_value = 1
GROUP BY tenure_group
ORDER BY churned_customers DESC;

-- ----------------------------------------------------------------------------
-- Q17. Churn rate by tenure group
SELECT
    tenure_group,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics
GROUP BY tenure_group
ORDER BY churn_rate DESC;

-- ----------------------------------------------------------------------------
-- Q18. Average tenure of churned vs retained customers
SELECT
    churn_label,
    ROUND(AVG(tenure_months), 2) AS avg_tenure
FROM fact_churn_metrics
GROUP BY churn_label;

-- ----------------------------------------------------------------------------
-- Q19. Spend quartile risk analysis
WITH SpendQuartiles AS (
    SELECT
        customerid,
        churn_value,
        NTILE(4) OVER (ORDER BY monthly_charges DESC) AS spend_quartile
    FROM fact_churn_metrics
)
SELECT
    spend_quartile,
    COUNT(customerid) AS customers_in_bucket,
    ROUND(SUM(churn_value) * 100.0 / COUNT(customerid), 2) AS churn_rate_pct
FROM SpendQuartiles
GROUP BY spend_quartile
ORDER BY spend_quartile ASC;

-- ----------------------------------------------------------------------------
-- Q20. Cumulative churn across the first 12 months of lifecycle
WITH TenureAgg AS (
    SELECT
        tenure_months,
        COUNT(customerid) AS total_at_tenure,
        SUM(churn_value) AS churned_at_tenure
    FROM fact_churn_metrics
    GROUP BY tenure_months
)
SELECT
    tenure_months,
    churned_at_tenure,
    ROUND(
        (SUM(churned_at_tenure) OVER (ORDER BY tenure_months)) * 100.0 /
        (SUM(total_at_tenure) OVER (ORDER BY tenure_months)), 2
    ) AS cumulative_churn_pct
FROM TenureAgg
LIMIT 12;

-- ----------------------------------------------------------------------------
-- Q21. Does online security reduce churn?
SELECT
    online_security,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_products p ON f.customerid = p.customerid
GROUP BY online_security;

-- ----------------------------------------------------------------------------
-- Q22. Which internet service has the highest churn rate?
SELECT
    internet_service,
    ROUND(AVG(churn_value) * 100, 2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_products p ON f.customerid = p.customerid
GROUP BY internet_service
ORDER BY churn_rate DESC;

-- ----------------------------------------------------------------------------
-- Q23. Top 50 active customers to contact to save the most revenue
WITH RiskRanked AS (
    SELECT
        f.customerid,
        f.monthly_charges,
        f.churn_score,
        t.contract,
        RANK() OVER (ORDER BY f.churn_score DESC, f.monthly_charges DESC) AS risk_rank
    FROM fact_churn_metrics f
    JOIN dim_account_terms t ON f.customerid = t.customerid
    WHERE f.churn_value = 0
)
SELECT * FROM RiskRanked
WHERE risk_rank <= 50;

-- ----------------------------------------------------------------------------
-- Q24. Does technical support save money in the long run? (internet customers)
SELECT
    p.tech_support,
    COUNT(f.customerid) AS total_customers,
    SUM(f.churn_value) AS churned_customers,
    ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS churn_rate_pct
FROM fact_churn_metrics f
JOIN dim_products p ON f.customerid = p.customerid
WHERE p.internet_service != 'No'
GROUP BY p.tech_support
ORDER BY churn_rate_pct DESC;

-- ----------------------------------------------------------------------------
-- Q25. Highest-value cities and their churn profile
SELECT
    l.city,
    COUNT(f.customerid) AS total_customers,
    ROUND(AVG(f.cltv), 2) AS average_cltv,
    ROUND(SUM(f.cltv), 2) AS total_neighborhood_value,
    ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS city_churn_rate_pct
FROM fact_churn_metrics f
JOIN dim_location l ON f.zip_code = l.zip_code
GROUP BY l.city
HAVING COUNT(f.customerid) >= 30
ORDER BY total_neighborhood_value DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q26. Cities where we lose the most lifetime value to churn
SELECT
    l.city,
    COUNT(CASE WHEN f.churn_value = 1 THEN 1 END) AS churned_count,
    ROUND(SUM(CASE WHEN f.churn_value = 1 THEN f.cltv ELSE 0 END), 2) AS total_lost_cltv,
    ROUND(AVG(CASE WHEN f.churn_value = 1 THEN f.cltv ELSE NULL END), 2) AS avg_lost_customer_cltv
FROM fact_churn_metrics f
JOIN dim_location l ON f.zip_code = l.zip_code
GROUP BY l.city
HAVING SUM(f.churn_value) > 0
ORDER BY total_lost_cltv DESC
LIMIT 10;
