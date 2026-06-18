"""Build the SQLite churn database from the cleaned CSV.

Workflow:
  1. Load ``Data Files/customer_churn_clean.csv`` into ``staging_churn_data``.
  2. Execute ``sqlite_schema.sql`` to create and populate the star schema.
  3. Validate the build by checking the overall churn rate (~26.54%).

Run directly to (re)build the database::

    python -m phase5_chatbot.database.init_db
"""
from __future__ import annotations

import sqlite3

import pandas as pd

from .. import config


def _load_staging(conn: sqlite3.Connection) -> int:
    """Load the cleaned CSV into the ``staging_churn_data`` table."""
    if not config.DATA_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {config.DATA_CSV_PATH}. "
            "Run the Phase 1 notebook (01_EDA_and_Preprocessing.ipynb) first."
        )

    df = pd.read_csv(config.DATA_CSV_PATH)
    df.to_sql("staging_churn_data", conn, if_exists="replace", index=False)
    return len(df)


def _run_schema(conn: sqlite3.Connection) -> None:
    """Execute the schema build script."""
    schema_sql = config.SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()


def _validate(conn: sqlite3.Connection) -> float:
    """Return the overall churn rate; raise if it is implausible."""
    cur = conn.execute(
        "SELECT ROUND(SUM(churn_value) * 100.0 / COUNT(*), 2) "
        "FROM fact_churn_metrics"
    )
    churn_rate = cur.fetchone()[0]
    if churn_rate is None or not (20.0 <= churn_rate <= 35.0):
        raise ValueError(
            f"Build validation failed: unexpected churn rate {churn_rate}. "
            "Expected ~26.54%."
        )
    return churn_rate


def build_database(force: bool = False) -> None:
    """Create the SQLite database file and populate the star schema.

    Args:
        force: When True, delete any existing database file and rebuild.
    """
    config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    if config.DB_PATH.exists():
        if not force:
            return
        config.DB_PATH.unlink()

    conn = sqlite3.connect(config.DB_PATH)
    try:
        rows = _load_staging(conn)
        _run_schema(conn)
        churn_rate = _validate(conn)
        print(
            f"Built {config.DB_PATH.name}: {rows} customers loaded, "
            f"overall churn rate {churn_rate}%."
        )
    except Exception:
        conn.close()
        # Remove a partially built database so the next run starts clean.
        if config.DB_PATH.exists():
            config.DB_PATH.unlink()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    build_database(force=True)
