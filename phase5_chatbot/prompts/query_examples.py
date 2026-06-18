"""Few-shot question -> SQL examples for the query generator.

These pairs are the SQLite-adapted versions of the 26 analytical queries in
`Database and analysis/03_sqlite_churn_queries.sql`. They teach Gemini the
preferred join patterns and the `* 100.0` rate idiom, and double as the
catalogue behind the UI's sample-question chips.
"""
from __future__ import annotations

FEW_SHOT_EXAMPLES: list[dict[str, str]] = [
    {
        "id": "Q1",
        "question": "What is the overall churn rate?",
        "sql": "SELECT COUNT(*) AS total_customers, SUM(churn_value) AS churned_customers, "
               "ROUND(SUM(churn_value) * 100.0 / COUNT(*), 2) AS churn_rate "
               "FROM fact_churn_metrics;",
    },
    {
        "id": "Q2",
        "question": "How many customers are active and how many have churned?",
        "sql": "SELECT churn_label, COUNT(*) AS customers FROM fact_churn_metrics "
               "GROUP BY churn_label;",
    },
    {
        "id": "Q3",
        "question": "Which gender has the highest churn rate?",
        "sql": "SELECT d.gender, COUNT(*) AS customers, SUM(f.churn_value) AS churned, "
               "ROUND(SUM(f.churn_value) * 100.0 / COUNT(*), 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_demographics d "
               "ON f.customerid = d.customerid GROUP BY d.gender;",
    },
    {
        "id": "Q4",
        "question": "Do senior citizens churn more?",
        "sql": "SELECT senior_citizen, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_demographics d "
               "ON f.customerid = d.customerid GROUP BY senior_citizen;",
    },
    {
        "id": "Q5",
        "question": "Does having dependents reduce churn?",
        "sql": "SELECT dependents, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_demographics d "
               "ON f.customerid = d.customerid GROUP BY dependents;",
    },
    {
        "id": "Q6",
        "question": "Which contract type has the highest churn?",
        "sql": "SELECT contract, COUNT(*) AS customers, "
               "ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_account_terms a "
               "ON f.customerid = a.customerid GROUP BY contract ORDER BY churn_rate DESC;",
    },
    {
        "id": "Q7",
        "question": "Which payment method is most associated with churn?",
        "sql": "SELECT payment_method, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_account_terms a "
               "ON f.customerid = a.customerid GROUP BY payment_method ORDER BY churn_rate DESC;",
    },
    {
        "id": "Q8",
        "question": "Does paperless billing affect churn?",
        "sql": "SELECT paperless_billing, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_account_terms a "
               "ON f.customerid = a.customerid GROUP BY paperless_billing;",
    },
    {
        "id": "Q9",
        "question": "What is the average revenue per user (ARPU) for churned vs active customers?",
        "sql": "SELECT churn_label, COUNT(customerid) AS total_customers, "
               "ROUND(AVG(monthly_charges), 2) AS arpu_monthly "
               "FROM fact_churn_metrics GROUP BY churn_label;",
    },
    {
        "id": "Q10",
        "question": "How much monthly revenue are we losing to churn?",
        "sql": "SELECT ROUND(SUM(monthly_charges), 2) AS monthly_revenue_lost "
               "FROM fact_churn_metrics WHERE churn_value = 1;",
    },
    {
        "id": "Q11",
        "question": "What is the true ARPU for our active customer base?",
        "sql": "SELECT COUNT(customerid) AS total_active_users, "
               "ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue, "
               "ROUND(AVG(monthly_charges), 2) AS true_arpu "
               "FROM fact_churn_metrics WHERE churn_value = 0;",
    },
    {
        "id": "Q12",
        "question": "What is the revenue contribution by churn status?",
        "sql": "SELECT churn_label, ROUND(SUM(monthly_charges), 2) AS revenue "
               "FROM fact_churn_metrics GROUP BY churn_label;",
    },
    {
        "id": "Q13",
        "question": "Which customer value segment loses the most revenue?",
        "sql": "SELECT customer_value_segment, ROUND(SUM(monthly_charges), 2) AS revenue_lost "
               "FROM fact_churn_metrics WHERE churn_value = 1 "
               "GROUP BY customer_value_segment ORDER BY revenue_lost DESC;",
    },
    {
        "id": "Q14",
        "question": "How does contract length affect the churn rate?",
        "sql": "SELECT a.contract, COUNT(f.customerid) AS customer_base, "
               "ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS churn_rate_pct "
               "FROM fact_churn_metrics f JOIN dim_account_terms a "
               "ON f.customerid = a.customerid GROUP BY a.contract ORDER BY churn_rate_pct DESC;",
    },
    {
        "id": "Q15",
        "question": "Are customers who use more services less likely to leave?",
        "sql": "SELECT total_services, COUNT(customerid) AS total_customers, "
               "ROUND(SUM(churn_value) * 100.0 / COUNT(customerid), 2) AS churn_rate_pct "
               "FROM fact_churn_metrics GROUP BY total_services ORDER BY total_services ASC;",
    },
    {
        "id": "Q16",
        "question": "At what tenure do the most customers churn?",
        "sql": "SELECT tenure_group, COUNT(*) AS churned_customers "
               "FROM fact_churn_metrics WHERE churn_value = 1 "
               "GROUP BY tenure_group ORDER BY churned_customers DESC;",
    },
    {
        "id": "Q17",
        "question": "What is the churn rate by tenure group?",
        "sql": "SELECT tenure_group, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics GROUP BY tenure_group ORDER BY churn_rate DESC;",
    },
    {
        "id": "Q18",
        "question": "What is the average tenure of churned vs retained customers?",
        "sql": "SELECT churn_label, ROUND(AVG(tenure_months), 2) AS avg_tenure "
               "FROM fact_churn_metrics GROUP BY churn_label;",
    },
    {
        "id": "Q19",
        "question": "Are the most expensive pricing tiers driving customers away?",
        "sql": "WITH SpendQuartiles AS (SELECT customerid, churn_value, "
               "NTILE(4) OVER (ORDER BY monthly_charges DESC) AS spend_quartile "
               "FROM fact_churn_metrics) "
               "SELECT spend_quartile, COUNT(customerid) AS customers_in_bucket, "
               "ROUND(SUM(churn_value) * 100.0 / COUNT(customerid), 2) AS churn_rate_pct "
               "FROM SpendQuartiles GROUP BY spend_quartile ORDER BY spend_quartile ASC;",
    },
    {
        "id": "Q20",
        "question": "At what point in the first year are customers most vulnerable to leaving?",
        "sql": "WITH TenureAgg AS (SELECT tenure_months, COUNT(customerid) AS total_at_tenure, "
               "SUM(churn_value) AS churned_at_tenure FROM fact_churn_metrics GROUP BY tenure_months) "
               "SELECT tenure_months, churned_at_tenure, "
               "ROUND((SUM(churned_at_tenure) OVER (ORDER BY tenure_months)) * 100.0 / "
               "(SUM(total_at_tenure) OVER (ORDER BY tenure_months)), 2) AS cumulative_churn_pct "
               "FROM TenureAgg LIMIT 12;",
    },
    {
        "id": "Q21",
        "question": "Does online security reduce churn?",
        "sql": "SELECT online_security, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_products p "
               "ON f.customerid = p.customerid GROUP BY online_security;",
    },
    {
        "id": "Q22",
        "question": "Which internet service has the highest churn rate?",
        "sql": "SELECT internet_service, ROUND(AVG(churn_value) * 100, 2) AS churn_rate "
               "FROM fact_churn_metrics f JOIN dim_products p "
               "ON f.customerid = p.customerid GROUP BY internet_service ORDER BY churn_rate DESC;",
    },
    {
        "id": "Q23",
        "question": "Who are the top 50 at-risk active customers we should contact to save revenue?",
        "sql": "WITH RiskRanked AS (SELECT f.customerid, f.monthly_charges, f.churn_score, "
               "t.contract, RANK() OVER (ORDER BY f.churn_score DESC, f.monthly_charges DESC) AS risk_rank "
               "FROM fact_churn_metrics f JOIN dim_account_terms t ON f.customerid = t.customerid "
               "WHERE f.churn_value = 0) SELECT * FROM RiskRanked WHERE risk_rank <= 50;",
    },
    {
        "id": "Q24",
        "question": "Does providing technical support reduce churn for internet customers?",
        "sql": "SELECT p.tech_support, COUNT(f.customerid) AS total_customers, "
               "SUM(f.churn_value) AS churned_customers, "
               "ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS churn_rate_pct "
               "FROM fact_churn_metrics f JOIN dim_products p ON f.customerid = p.customerid "
               "WHERE p.internet_service != 'No' GROUP BY p.tech_support ORDER BY churn_rate_pct DESC;",
    },
    {
        "id": "Q25",
        "question": "Which cities contain our highest-value customer bases and what is their churn profile?",
        "sql": "SELECT l.city, COUNT(f.customerid) AS total_customers, "
               "ROUND(AVG(f.cltv), 2) AS average_cltv, ROUND(SUM(f.cltv), 2) AS total_neighborhood_value, "
               "ROUND(SUM(f.churn_value) * 100.0 / COUNT(f.customerid), 2) AS city_churn_rate_pct "
               "FROM fact_churn_metrics f JOIN dim_location l ON f.zip_code = l.zip_code "
               "GROUP BY l.city HAVING COUNT(f.customerid) >= 30 "
               "ORDER BY total_neighborhood_value DESC LIMIT 10;",
    },
    {
        "id": "Q26",
        "question": "In which cities are we losing the most lifetime value due to churn?",
        "sql": "SELECT l.city, COUNT(CASE WHEN f.churn_value = 1 THEN 1 END) AS churned_count, "
               "ROUND(SUM(CASE WHEN f.churn_value = 1 THEN f.cltv ELSE 0 END), 2) AS total_lost_cltv, "
               "ROUND(AVG(CASE WHEN f.churn_value = 1 THEN f.cltv ELSE NULL END), 2) AS avg_lost_customer_cltv "
               "FROM fact_churn_metrics f JOIN dim_location l ON f.zip_code = l.zip_code "
               "GROUP BY l.city HAVING SUM(f.churn_value) > 0 ORDER BY total_lost_cltv DESC LIMIT 10;",
    },
]


def format_examples(limit: int | None = None) -> str:
    """Render the few-shot examples as a text block for the prompt.

    Args:
        limit: optionally cap the number of examples included.
    """
    examples = FEW_SHOT_EXAMPLES if limit is None else FEW_SHOT_EXAMPLES[:limit]
    blocks = [
        f"Question: {ex['question']}\nSQL: {ex['sql']}"
        for ex in examples
    ]
    return "\n\n".join(blocks)
