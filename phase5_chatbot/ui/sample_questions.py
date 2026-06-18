"""Curated sample questions for the chatbot UI.

Grouped by business category and mapped to the Q1-Q26 analytical queries so the
user can explore by clicking, while free-text questions remain fully supported.
"""
from __future__ import annotations

# category -> list of (question, query_id)
SAMPLE_QUESTIONS: dict[str, list[tuple[str, str]]] = {
    "Overview": [
        ("What is our overall churn rate?", "Q1"),
        ("How many customers are active vs churned?", "Q2"),
    ],
    "Demographics": [
        ("Which gender has the highest churn rate?", "Q3"),
        ("Do senior citizens churn more?", "Q4"),
        ("Does having dependents reduce churn?", "Q5"),
    ],
    "Contracts & Billing": [
        ("Which contract type has the highest churn?", "Q6"),
        ("Which payment method is most associated with churn?", "Q7"),
        ("Does paperless billing affect churn?", "Q8"),
    ],
    "Revenue": [
        ("What is the ARPU for churned vs active customers?", "Q9"),
        ("How much monthly revenue are we losing to churn?", "Q10"),
        ("What is the true ARPU for our active customer base?", "Q11"),
        ("Which customer value segment loses the most revenue?", "Q13"),
    ],
    "Tenure & Services": [
        ("At what tenure do customers churn most?", "Q16"),
        ("What is the churn rate by tenure group?", "Q17"),
        ("Are customers with more services less likely to leave?", "Q15"),
        ("What is the average tenure of churned vs retained customers?", "Q18"),
    ],
    "Products": [
        ("Which internet service has the highest churn rate?", "Q22"),
        ("Does online security reduce churn?", "Q21"),
        ("Does technical support reduce churn for internet customers?", "Q24"),
    ],
    "Geography": [
        ("Which cities have the highest customer lifetime value?", "Q25"),
        ("In which cities are we losing the most lifetime value to churn?", "Q26"),
    ],
    "Risk & Retention": [
        ("Who are the top 50 at-risk active customers we should contact?", "Q23"),
        ("Are the most expensive pricing tiers driving customers away?", "Q19"),
    ],
}

# A short, high-impact set rendered as one-click chips in the main chat area.
FEATURED_QUESTIONS: list[str] = [
    "What is our overall churn rate?",
    "Which contract type has the highest churn?",
    "How much monthly revenue are we losing to churn?",
    "What is the churn rate by tenure group?",
    "Which internet service has the highest churn rate?",
    "Which cities have the highest customer lifetime value?",
]
