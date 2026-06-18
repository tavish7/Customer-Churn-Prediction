"""SQLite data layer for the churn chatbot."""

from .connection import (
    ensure_database,
    get_connection,
    get_customer_count,
    run_query,
)

__all__ = [
    "ensure_database",
    "get_connection",
    "get_customer_count",
    "run_query",
]
