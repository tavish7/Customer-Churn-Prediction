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

| monthly_revenue_lost |
|------------------------|
| 139130.85              |

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

| total_active_users | total_monthly_revenue | true_arpu |
|--------------------|-----------------------|-----------|
| 5174               | 316985.75             | 61.27     |


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

| churn_label | revenue   |
|-------------|-----------|
| No          | 316985.75 |
| Yes         | 139130.85 |

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

| customer_value_segment | revenue_lost |
|------------------------|--------------|
| Bronze                 | 44456.4      |
| Silver                 | 35137.55     |
| Gold                   | 31720.1      |
| Platinum               | 27816.8      |

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

| contract       | customer_base | churn_rate_pct |
|----------------|---------------|----------------|
| Month-to-month | 3875          | 42.71          |
| One year       | 1473          | 11.27          |
| Two year       | 1695          | 2.83           |

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

| total_services | total_customers | churn_rate_pct |
|------------------|-----------------|----------------|
| 1                | 1264            | 10.92          |
| 2                | 859             | 30.97          |
| 3                | 846             | 44.92          |
| 4                | 965             | 36.48          |
| 5                | 922             | 31.34          |
| 6                | 908             | 25.55          |
| 7                | 676             | 22.49          |
| 8                | 395             | 12.41          |
| 9                | 208             | 5.29           |

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

| tenure_group | churned_customers | churn_rate_pct |
|--------------|-------------------|----------------|
| 0-1 Year     | 1037              | 10.92          |
| 2-4 Years    | 325               | 30.97          |
| 1-2 Years    | 294               | 44.92          |
| 4+ Years     | 213               | 36.48          |

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

| tenure_group | churn_rate |
|----------------|------------|
| 0-1 Year       | 47.44      |
| 1-2 Years      | 28.71      |
| 2-4 Years      | 20.39      |
| 4+ Years       | 9.51       |

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

| spend_quartile | customers_in_bucket | churn_rate_pct |
|----------------|---------------------|----------------|
| 1              | 1761                | 32.88          |
| 2              | 1761                | 37.42          |
| 3              | 1761                | 24.59          |
| 4              | 1760                | 11.25          |

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

| tenure_months | churned_at_tenure | cumulative_churn_pct |
|---------------|-------------------|----------------------|
| 0             | 0                 | 0.00                 |
| 1             | 380               | 60.90                |
| 2             | 123               | 58.35                |
| 3             | 94                | 56.21                |
| 4             | 83                | 54.93                |
| 5             | 64                | 54.27                |
| 6             | 40                | 52.94                |
| 7             | 51                | 51.80                |
| 8             | 42                | 50.55                |
| 9             | 46                | 49.78                |
| 10            | 45                | 49.14                |
| 11            | 31                | 48.28                |

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

| online_security   | churn_rate |
|---------------------|------------|
| No                  | 41.77      |
| Yes                 | 14.61      |
| No internet service | 7.40       |

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

| internet_service | churn_rate |
|------------------|------------|
| Fiber optic      | 41.89      |
| DSL              | 18.96      |
| No               | 7.40       |

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

| customerid | monthly_charges | churn_score | contract       | risk_rank |
|------------|-----------------|-------------|----------------|-----------|
| 5914-XRFQB | 115.8           | 80          | Two year       | 1         |
| 3396-DKDEL | 115.15          | 80          | Two year       | 2         |
| 0619-OLYUR | 111.9           | 80          | Two year       | 3         |
| 2499-AJYUA | 110.8           | 80          | Two year       | 4         |
| 3766-EJLFL | 109.05          | 80          | Two year       | 5         |
| 4016-BJKTZ | 108.9           | 80          | Two year       | 6         |
| 9137-UIYPG | 106.9           | 80          | Month-to-month | 7         |
| 4010-YLMVT | 106.6           | 80          | Month-to-month | 8         |
| 8777-MBMTS | 105.85          | 80          | Two year       | 9         |
| 5074-FBGHB | 104.65          | 80          | One year       | 10        |
| 1442-OKRJE | 103.15          | 80          | One year       | 11        |
| 4062-HBMOS | 103.05          | 80          | Month-to-month | 12        |
| 6693-FRIRW | 101.3           | 80          | Month-to-month | 13        |
| 7315-WYOAW | 100.75          | 80          | Month-to-month | 14        |
| 6196-HBOBZ | 99.35           | 80          | Two year       | 15        |
| 5150-LJNSR | 98.05           | 80          | One year       | 16        |
| 6728-VOIFY | 96              | 80          | One year       | 17        |
| 7375-WMVMT | 95.5            | 80          | Two year       | 18        |
| 0248-PGHBZ | 92.45           | 80          | Two year       | 19        |
| 5222-IMUKT | 91.05           | 80          | Month-to-month | 20        |
| 4377-VDHYI | 90.8            | 80          | One year       | 21        |
| 2400-XIWIO | 90.1            | 80          | Two year       | 22        |
| 1187-WILMM | 89.4            | 80          | Two year       | 23        |
| 5429-LWCMV | 89.15           | 80          | Month-to-month | 24        |
| 8132-YPVBX | 85.95           | 80          | Month-to-month | 25        |
| 4536-PLEQY | 85.05           | 80          | Month-to-month | 26        |
| 9121-PHQSR | 85.05           | 80          | Month-to-month | 26        |
| 9314-IJWSQ | 84.8            | 80          | Month-to-month | 28        |
| 8714-CTZJW | 82.85           | 80          | Month-to-month | 29        |
| 9110-HSGTV | 82.45           | 80          | Two year       | 30        |
| 6617-WLBQC | 81.85           | 80          | One year       | 31        |
| 6968-GMKPR | 81.55           | 80          | Month-to-month | 32        |
| 0454-OKRCT | 80.6            | 80          | Two year       | 33        |
| 8212-CRQXP | 80              | 80          | Month-to-month | 34        |
| 3955-JBZZM | 78.8            | 80          | Month-to-month | 35        |
| 4626-OZDTJ | 78.65           | 80          | One year       | 36        |
| 9552-TGUZV | 75              | 80          | Month-to-month | 37        |
| 5233-AOZUF | 74.95           | 80          | Month-to-month | 38        |
| 5148-ORICT | 74.35           | 80          | Two year       | 39        |
| 9840-EFJQB | 74.35           | 80          | Month-to-month | 39        |
| 6384-VMJHP | 73              | 80          | Two year       | 41        |
| 3200-MNQTF | 70.9            | 80          | Two year       | 42        |
| 0958-YHXGP | 69.9            | 80          | Month-to-month | 43        |
| 5018-LXQQG | 66.3            | 80          | Month-to-month | 44        |
| 5568-DMXZS | 65.45           | 80          | Month-to-month | 45        |
| 6652-YFFJO | 64.9            | 80          | Month-to-month | 46        |
| 0384-RVBPI | 64.4            | 80          | Month-to-month | 47        |
| 5387-ASZNZ | 63.85           | 80          | One year       | 48        |
| 9670-BPNXF | 62.55           | 80          | One year       | 49        |
| 9220-CXRSC | 61.4            | 80          | Two year       | 50        |

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

| tech_support | total_customers | churned_customers | churn_rate_pct | risk_rank |
|----------------|-----------------|-------------------|----------------|-----------|
| No             | 3473            | 1446              | 41.64          | 1         |
| Yes            | 2044            | 310               | 15.17          | 2         |

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

| city          | total_customers | average_cltv | total_neighborhood_value | city_churn_rate_pct |
|---------------|-----------------|--------------|--------------------------|---------------------|
| Los Angeles   | 305             | 4377.33      | 1335085                  | 29.51               |
| San Diego     | 150             | 4368.01      | 655202                   | 33.33               |
| Sacramento    | 108             | 4540.66      | 490391                   | 24.07               |
| San Jose      | 112             | 4233.38      | 474138                   | 25.89               |
| San Francisco | 104             | 4335.46      | 450888                   | 29.81               |
| Fresno        | 64              | 4338.33      | 277653                   | 25.00               |
| Long Beach    | 60              | 4494.22      | 269653                   | 25.00               |
| Oakland       | 52              | 4334.40      | 225389                   | 25.00               |
| Stockton      | 44              | 4371.18      | 192332                   | 27.27               |
| Bakersfield   | 40              | 4607.55      | 184302                   | 7.50                |

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

| city          | churned_count | total_lost_cltv | avg_lost_customer_cltv |
|---------------|---------------|-----------------|------------------------|
| Los Angeles   | 90            | 373341          | 4148.23                |
| San Diego     | 50            | 209199          | 4183.98                |
| San Francisco | 31            | 124680          | 4021.94                |
| San Jose      | 29            | 111626          | 3849.17                |
| Sacramento    | 26            | 107058          | 4117.62                |
| Fresno        | 16            | 65320           | 4082.50                |
| Long Beach    | 15            | 64433           | 4295.53                |
| Oakland       | 13            | 54984           | 4229.54                |
| Glendale      | 13            | 53262           | 4097.08                |
| Modesto       | 12            | 46055           | 3837.92                |

</details>

---
