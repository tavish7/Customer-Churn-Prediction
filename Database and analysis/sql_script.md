# 📈Analyse the data🤔
***

### Q1. What is the overall churn rate?
```sql
SELECT
    COUNT(*) AS total_customers,
    SUM(churn_value) AS churned_customers,
    ROUND(SUM(churn_value)*100.0/COUNT(*),2) AS churn_rate
FROM fact_churn_metrics;
```
<details>
<summary>Output</summary>

| total_customers | churned_customers | churn_rate |
|-------------------|-------------------|------------|
| 7043              | 1869              | 26.54      |

</details>

---

### Q2. How many customers are active and how many have churned?
```sql
SELECT
    churn_label,
    COUNT(*) AS customers
FROM fact_churn_metrics
GROUP BY churn_label;
```
<details>
<summary>Output</summary>

| churn_label | customers |
|-------------|-----------|
| No          | 5174      |
| Yes         | 1869      |

</details>

---

### Q3. Which gender has the highest churn rate?
```sql
SELECT
    d.gender,
    COUNT(*) AS customers,
    SUM(f.churn_value) AS churned,
    ROUND(SUM(f.churn_value)*100.0/COUNT(*),2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_demographics d
ON f.customerid = d.customerid
GROUP BY d.gender;
```

<details>
<summary>Output</summary>

| gender | customers | churned | churn_rate |
|--------|-----------|---------|------------|
| Female | 3488      | 939     | 26.92      |
| Male   | 3555      | 930     | 26.16      |

</details>

---

### Q4. Do senior citizen churn more?
```sql
SELECT
    senior_citizen,
    ROUND(AVG(churn_value)*100,2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_demographics d
ON f.customerid=d.customerid
GROUP BY senior_citizen;
```

<details>
<summary>Output</summary>

| senior_citizen | churn_rate |
|----------------|------------|
| No             | 23.61      |
| Yes            | 41.68      |

</details>

---

### Q5. Does having dependents reduce churn?
```sql
SELECT
    dependents,
    ROUND(AVG(churn_value)*100,2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_demographics d
ON f.customerid=d.customerid
GROUP BY dependents;

```

<details>
<summary>Output</summary>

| dependents | churn_rate |
|------------|------------|
| No         | 32.55      |
| Yes        | 6.52       |

</details>

---

### Q6. Which contract type has the highest churn ? or How much does a retreiving a customer for long term affect on churn rate?
```sql
SELECT
    contract,
    COUNT(*) customers,
    ROUND(AVG(churn_value)*100,2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_account_terms a
ON f.customerid=a.customerid
GROUP BY contract
ORDER BY churn_rate DESC;
```

<details>
<summary>Output</summary>

| contract       | customers | churn_rate |
|----------------|-----------|------------|
| Month-to-month | 3875      | 42.71      |
| One year       | 1473      | 11.27      |
| Two year       | 1695      | 2.83       |

</details>

---

### Q7. Which payment method is most associated with churn?
```sql
SELECT
    payment_method,
    ROUND(AVG(churn_value)*100,2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_account_terms a
ON f.customerid=a.customerid
GROUP BY payment_method
ORDER BY churn_rate DESC;
```

<details>
<summary>Output</summary>

| payment_method            | churn_rate |
|---------------------------|------------|
| Electronic check          | 45.29      |
| Mailed check              | 19.11      |
| Bank transfer (automatic) | 16.71      |
| Credit card (automatic)   | 15.24      |

</details>

---


### Q8. Does paperless billing affect churn?
```sql
SELECT
    paperless_billing,
    ROUND(AVG(churn_value)*100,2) AS churn_rate
FROM fact_churn_metrics f
JOIN dim_account_terms a
ON f.customerid=a.customerid
GROUP BY paperless_billing;
```

<details>
<summary>Output</summary>

| paperless_billing | churn_rate |
|---------------------|------------|
| Yes                 | 33.57      |
| No                  | 16.33      |

</details>

---

### Q9. Are we losing our cheap, premium or high paying subscribed customers for churned and not churned customer i.e. check for ARPU (Average Revenue Per User) Vs Churn status

```sql
SELECT
	churn_label,
	COUNT(customerid) AS total_customers,
	ROUND(AVG(monthly_charges), 2) AS arpu_monthly
FROM fact_churn_metrics
GROUP BY churn_label;
```

<details>
<summary>Output</summary>

| churn_label | total_customers | arpu_monthly |
|-------------|-----------------|--------------|
| No          | 5174            | 61.27        |
| Yes         | 1869            | 74.44        |

</details>

---

### Q10. Revenue lost during churn
```sql
SELECT
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue_lost
FROM fact_churn_metrics
WHERE churn_value=1;
```

<details>
<summary>Output</summary>

| total_active_users | total_monthly_revenue | true_arpu |
|--------------------|-----------------------|-----------|
| 5174               | 316985.75             | 61.27     |

</details>

---

### Q11. What is the true ARPU for our active customer base?
```sql
SELECT 
    COUNT(customerid) AS total_active_users,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue,
    ROUND(AVG(monthly_charges), 2) AS true_arpu
FROM fact_churn_metrics
WHERE churn_value = 0;
```

<details>
<summary>Output</summary>



</details>

---

### Q12. Revenue contribution by customers
```sql
SELECT
    churn_label,
    ROUND(SUM(monthly_charges),2) AS revenue
FROM fact_churn_metrics
GROUP BY churn_label;
```

<details>
<summary>Output</summary>



</details>

---

### Q13. Which customer value segment losses the most revenue?
```sql
SELECT
    customer_value_segment,
    ROUND(SUM(monthly_charges),2) AS revenue_lost
FROM fact_churn_metrics
WHERE churn_value=1
GROUP BY customer_value_segment
ORDER BY revenue_lost DESC;
```

<details>
<summary>Output</summary>



</details>


---

### Q14. How much does a retreiving a customer for long term affect on churn rate?
```sql
SELECT
	d.contract,
	COUNT(f.customerid) AS customer_base,
	ROUND((SUM(f.churn_value) / COUNT(f.customerid)) * 100, 2) AS churn_rate_pct
FROM fact_churn_metrics f
INNER JOIN dim_account_terms d ON f.customerid = d.customerid
GROUP BY d.contract
ORDER BY churn_rate_pct DESC;

```

<details>
<summary>Output</summary>



</details>

---

### Q15. Are customers who use more services less likely to leave?
```sql
SELECT
	f.total_services,
	COUNT(f.customerid) AS total_customers,
	ROUND((SUM(f.churn_value) / COUNT(f.customerid)) * 100, 2) AS churn_rate_pct
FROM fact_churn_metrics f
GROUP BY f.total_services
ORDER BY f.total_services ASC;
```

<details>
<summary>Output</summary>



</details>

---

### Q16. At what tenure do customers churn most?
```sql
SELECT
    tenure_group,
    COUNT(*) AS churned_customers
FROM fact_churn_metrics
WHERE churn_value=1
GROUP BY tenure_group
ORDER BY churned_customers DESC;
```

<details>
<summary>Output</summary>



</details>

---

### Q17. Churn rate by tenure group
```sql
SELECT
    tenure_group,
    ROUND(AVG(churn_value)*100,2) AS churn_rate
FROM fact_churn_metrics
GROUP BY tenure_group
ORDER BY churn_rate DESC;
```

<details>
<summary>Output</summary>



</details>

---

### Q18. Average tenure of churned vs retained customers
```sql
SELECT
    churn_label,
    ROUND(AVG(tenure_months),2) avg_tenure
FROM fact_churn_metrics
GROUP BY churn_label;
```

<details>
<summary>Output</summary>



</details>


---

### Q19. Spend quartile risk analysis - Are most expensive pricing tiers driving custimers away?
```sql
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
	ROUND((SUM(churn_value) / COUNT(customerid)) * 100, 2) AS churn_rate_pct
FROM SpendQuartiles
GROUP BY spend_quartile
ORDER BY spend_quartile ASC;
```

<details>
<summary>Output</summary>



</details>

---

### Q20. At what month in the customer lifecycle are they most vulnerable to leaving?
```sql
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
	ROUND((SUM(churned_at_tenure) OVER (ORDER BY tenure_months)) /
	(SUM(total_at_tenure) OVER (ORDER BY tenure_months)) * 100, 2) AS cumulative_churn_pct
FROM TenureAgg
LIMIT 12;
```

<details>
<summary>Output</summary>



</details>

---

### Q21. Does online security reduce churn?
```sql
SELECT
    online_security,
    ROUND(AVG(churn_value)*100,2) churn_rate
FROM fact_churn_metrics f
JOIN dim_products p
ON f.customerid=p.customerid
GROUP BY online_security;
```

<details>
<summary>Output</summary>



</details>

---

### Q22. Which internet service has the highest churn rate?
```sql
SELECT
    internet_service,
    ROUND(AVG(churn_value)*100,2) churn_rate
FROM fact_churn_metrics f
JOIN dim_products p
ON f.customerid=p.customerid
GROUP BY internet_service
ORDER BY churn_rate DESC;
```

<details>
<summary>Output</summary>



</details>

---

### Q23. "Who are the exact top 50 active customers that company should contact to save the most revenue?"
```sql
WITH RiskRanked AS (
SELECT
	f.customerid,
	f.monthly_charges,
	f.churn_score,
	t.contract,
	RANK() OVER (ORDER BY f.churn_score DESC, f.monthly_charges DESC) AS risk_rank
FROM fact_churn_metrics f
INNER JOIN dim_account_terms t ON f.customerid = t.customerid
WHERE f.churn_value = 0
)
SELECT * FROM RiskRanked
WHERE risk_rank <= 50;
```

<details>
<summary>Output</summary>



</details>


---

### Q24. Does providing technical support actually save us money in the long run?
```sql
SELECT 
    p.tech_support,
    COUNT(f.customerid) AS total_customers,
    SUM(f.churn_value) AS churned_customers,
    ROUND((SUM(f.churn_value) / COUNT(f.customerid)) * 100, 2) AS churn_rate_pct
FROM fact_churn_metrics f
INNER JOIN dim_products p 
    ON f.customerid = p.customerid
WHERE p.internet_service != 'No'
GROUP BY p.tech_support
ORDER BY churn_rate_pct DESC;
```

<details>
<summary>Output</summary>



</details>

---

### Q25. Which cities contain our highest-value customer bases, and what is their churn profile?
```sql
SELECT 
    l.city,
    COUNT(f.customerid) AS total_customers,
    ROUND(AVG(f.cltv), 2) AS average_cltv,
    ROUND(SUM(f.cltv), 2) AS total_neighborhood_value,
    ROUND((SUM(f.churn_value) / COUNT(f.customerid)) * 100, 2) AS city_churn_rate_pct
FROM fact_churn_metrics f
INNER JOIN dim_location l 
    ON f.zip_code = l.zip_code
GROUP BY l.city
HAVING COUNT(f.customerid) >= 30 
ORDER BY total_neighborhood_value DESC
LIMIT 10;
```

<details>
<summary>Output</summary>



</details>

---

### Q26. In which cities are we losing the most financial lifetime value due to churn?
```sql
SELECT 
    l.city,
    COUNT(CASE WHEN f.churn_value = 1 THEN 1 END) AS churned_count,
    ROUND(SUM(CASE WHEN f.churn_value = 1 THEN f.cltv ELSE 0 END), 2) AS total_lost_cltv,
    ROUND(AVG(CASE WHEN f.churn_value = 1 THEN f.cltv ELSE NULL END), 2) AS avg_lost_customer_cltv
FROM fact_churn_metrics f
INNER JOIN dim_location l 
    ON f.zip_code = l.zip_code
GROUP BY l.city
HAVING SUM(f.churn_value) > 0
ORDER BY total_lost_cltv DESC
LIMIT 10;
```

<details>
<summary>Output</summary>



</details>

---
