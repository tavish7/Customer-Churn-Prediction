"""Prompt assets: schema context and few-shot SQL examples for Gemini."""

from .query_examples import FEW_SHOT_EXAMPLES, format_examples
from .schema_context import SCHEMA_PROMPT

__all__ = ["SCHEMA_PROMPT", "FEW_SHOT_EXAMPLES", "format_examples"]
