"""LangGraph state definition for the churn chatbot pipeline."""
from __future__ import annotations

from typing import Optional, TypedDict


class GraphState(TypedDict):
    """Shared state passed between graph nodes.

    Attributes:
        user_question: The natural-language question from the user.
        question_type: 'data' (needs SQL) or 'generic' (small talk / meta).
        generated_query: The SQL produced by the query_generator node.
        query_result: Successful query rows as a list of dicts, else None.
        error_message: Execution error text used to drive self-correction.
        retry_count: Number of failed execution attempts so far.
        final_response: The human-readable answer shown to the user.
    """

    user_question: str
    question_type: str
    generated_query: str
    query_result: Optional[list[dict]]
    error_message: Optional[str]
    retry_count: int
    final_response: str
