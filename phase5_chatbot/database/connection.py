"""SQLite connection helpers and a guarded read-only query runner."""
from __future__ import annotations

import sqlite3

import pandas as pd

from .. import config

# Statements the chatbot is allowed to run. The agent only ever needs to read.
_ALLOWED_PREFIXES = ("select", "with")
_FORBIDDEN_TOKENS = (
    "insert", "update", "delete", "drop", "alter",
    "create", "replace", "attach", "detach", "pragma",
)


def ensure_database() -> None:
    """Build the database on first use if it does not exist yet."""
    if not config.DB_PATH.exists():
        # Imported lazily to avoid a circular import at module load time.
        from .init_db import build_database

        build_database()


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection, building the database if necessary."""
    ensure_database()
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _assert_read_only(sql: str) -> None:
    """Reject anything that is not a single read-only SELECT/WITH statement."""
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        raise ValueError("Empty SQL statement.")

    lowered = stripped.lower()
    if not lowered.startswith(_ALLOWED_PREFIXES):
        raise ValueError("Only SELECT/WITH (read-only) queries are allowed.")

    # Disallow multiple statements (a simple SQL-injection / mutation guard).
    if ";" in stripped:
        raise ValueError("Only a single SQL statement may be executed.")

    for token in _FORBIDDEN_TOKENS:
        # Word-boundary-ish check to avoid false positives inside identifiers.
        if f" {token} " in f" {lowered} " or lowered.startswith(f"{token} "):
            raise ValueError(f"Disallowed keyword in query: {token}.")


def run_query(sql: str) -> pd.DataFrame:
    """Execute a read-only query and return the result as a DataFrame.

    Raises:
        ValueError: if the statement is not an allowed read-only query.
        sqlite3.Error: if the SQL fails to parse or execute.
    """
    _assert_read_only(sql)
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def get_customer_count() -> int:
    """Return the number of rows in the fact table (for UI status display)."""
    try:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT COUNT(*) FROM fact_churn_metrics")
            return int(cur.fetchone()[0])
        finally:
            conn.close()
    except Exception:
        return 0
