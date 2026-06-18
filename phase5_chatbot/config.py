"""Central configuration for the Phase 5 churn chatbot.

Holds filesystem paths, model settings, and a lazy LLM factory. The LLM and
its third-party imports are created only when ``get_llm`` is called, so the
database layer can import this module without requiring ``langchain`` to be
installed.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional for the bare database layer.
    def load_dotenv(*_args, **_kwargs) -> bool:  # type: ignore[misc]
        return False

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
# phase5_chatbot/ (this file's directory)
PACKAGE_DIR = Path(__file__).resolve().parent
# Repository root (one level up from phase5_chatbot/)
PROJECT_ROOT = PACKAGE_DIR.parent

DATA_CSV_PATH = PROJECT_ROOT / "Data Files" / "customer_churn_clean.csv"
ERD_IMAGE_PATH = PROJECT_ROOT / "Database and analysis" / "erd.png"

DATABASE_DIR = PACKAGE_DIR / "database"
DB_PATH = DATABASE_DIR / "churn.db"
SCHEMA_SQL_PATH = DATABASE_DIR / "sqlite_schema.sql"

# Load environment variables from phase5_chatbot/.env if present.
load_dotenv(PACKAGE_DIR / ".env")

# ----------------------------------------------------------------------------
# LLM settings
# ----------------------------------------------------------------------------
MODEL_NAME = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.0
MAX_RETRIES = 3  # self-correction attempts for the SQL generator


def get_api_key() -> str | None:
    return os.getenv("GOOGLE_API_KEY")


def get_llm(temperature: float = DEFAULT_TEMPERATURE):
    """Create a configured ``ChatGoogleGenerativeAI`` instance."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
        )

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=temperature,
        google_api_key=api_key,
    )
