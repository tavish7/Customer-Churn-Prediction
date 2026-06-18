"""LangGraph node functions: generate SQL, execute it, format the answer."""
from __future__ import annotations

import re

from . import config
from .database import run_query
from .prompts import SCHEMA_PROMPT, format_examples
from .state import GraphState

# Cap rows handed to the formatter LLM so we never blow the context window.
_MAX_ROWS_FOR_LLM = 50


def _strip_sql_fences(text: str) -> str:
    """Remove markdown code fences / stray prose around generated SQL."""
    cleaned = text.strip()
    # ```sql ... ``` or ``` ... ```
    fence = re.match(r"^```(?:sql)?\s*(.*?)\s*```$", cleaned, re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    # Some models prefix "SQL:" - drop it.
    cleaned = re.sub(r"^sql\s*:\s*", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


def query_generator(state: GraphState) -> dict:
    """Prompt Gemini to produce a SQL query for the user's question.

    On a retry (``error_message`` set) the previous SQL and its error are added
    so the model can correct itself.
    """
    llm = config.get_llm()

    prompt_parts = [
        SCHEMA_PROMPT,
        "\n--- EXAMPLE QUESTIONS AND SQL ---\n",
        format_examples(),
        "\n--- TASK ---",
        f"Question: {state['user_question']}",
    ]

    if state.get("error_message"):
        prompt_parts.append(
            "\nYour previous attempt failed. Fix the SQL.\n"
            f"Previous SQL:\n{state.get('generated_query', '')}\n"
            f"Error:\n{state['error_message']}"
        )

    prompt_parts.append("\nReturn ONLY the corrected SQL statement.")
    prompt = "\n".join(prompt_parts)

    response = llm.invoke(prompt)
    sql = _strip_sql_fences(getattr(response, "content", str(response)))
    return {"generated_query": sql}


def query_executor(state: GraphState) -> dict:
    """Run the generated SQL. Capture results or the error for self-correction."""
    sql = state.get("generated_query", "")
    try:
        df = run_query(sql)
        return {
            "query_result": df.to_dict(orient="records"),
            "error_message": None,
        }
    except Exception as exc:  # noqa: BLE001 - we surface any failure to the LLM
        return {
            "query_result": None,
            "error_message": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0) + 1,
        }


def response_formatter(state: GraphState) -> dict:
    """Turn the query result into a concise, business-friendly answer.

    Also handles the exhausted-retries case with a graceful fallback message.
    """
    result = state.get("query_result")

    if not result:
        # Either the query returned no rows, or retries were exhausted.
        if state.get("error_message"):
            return {
                "final_response": (
                    "I couldn't build a working query for that question after "
                    f"{config.MAX_RETRIES} attempts. Could you try rephrasing it, "
                    "or ask about churn rate, contracts, revenue, tenure, services, "
                    "or cities?"
                )
            }
        return {
            "final_response": (
                "The query ran successfully but returned no matching rows. "
                "Try broadening your question."
            )
        }

    total_rows = len(result)
    preview = result[:_MAX_ROWS_FOR_LLM]
    truncated_note = (
        f"\n(Showing first {_MAX_ROWS_FOR_LLM} of {total_rows} rows.)"
        if total_rows > _MAX_ROWS_FOR_LLM
        else ""
    )

    llm = config.get_llm(temperature=0.2)
    prompt = (
        "You are a business analyst explaining Telco customer-churn data to a "
        "non-technical stakeholder. Answer the question in 1-4 sentences using "
        "the query results. Quote the key numbers, include units (%, USD, "
        "customers) and round sensibly. Do not mention SQL or databases.\n\n"
        f"Question: {state['user_question']}\n"
        f"Query results (JSON rows): {preview}{truncated_note}\n\n"
        "Answer:"
    )

    response = llm.invoke(prompt)
    answer = getattr(response, "content", str(response)).strip()
    return {"final_response": answer}
