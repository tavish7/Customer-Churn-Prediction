"""LangGraph node functions: classify, generate SQL, execute it, format the answer."""
from __future__ import annotations

import re

from . import config
from .database import run_query
from .logging_utils import logger
from .prompts import SCHEMA_PROMPT, format_examples
from .state import GraphState


_MAX_ROWS_FOR_LLM = 50


BOT_NAME = "Telco Bot"
PERSONA_PROMPT = f"""
You are {BOT_NAME}, a friendly analytics assistant for a Telco company.
You help business users understand customer churn for 7,043 Telco customers
(the overall churn rate is about 26.5%). You can answer questions about churn
rate, contracts, payment methods, revenue/ARPU, tenure, services, internet
products, customer value segments, payment risk, at-risk customers, and cities.
You speak in plain, friendly English and never mention SQL, databases, or tables.
""".strip()


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


def question_classifier(state: GraphState) -> dict:
    """Decide whether a question needs the data pipeline or a direct answer.

    Returns ``question_type`` = 'data' (churn metrics -> SQL) or 'generic'
    (small talk / meta questions about the assistant itself).
    """
    question = state["user_question"]
    logger.info("Classifying question: %s", question)

    llm = config.get_llm()
    prompt = (
        "Classify the user's message into exactly one word.\n"
        "- 'data' if it asks about the Telco customers, churn, metrics, revenue, "
        "or any number that would come from the customer dataset.\n"
        "- 'generic' if it is small talk or asks who you are, what you can do, "
        "your responsibilities, your capabilities, or whether you can handle "
        "something.\n\n"
        f"Message: {question}\n"
        "Answer with only the single word 'data' or 'generic'."
    )
    label = getattr(llm.invoke(prompt), "content", "").strip().lower()
    question_type = "generic" if "generic" in label else "data"
    logger.info("Question classified as: %s", question_type)
    return {"question_type": question_type}


def generic_responder(state: GraphState) -> dict:
    """Answer small-talk / meta questions directly from the persona (no SQL)."""
    logger.info("Answering as %s persona (no database query needed).", BOT_NAME)
    llm = config.get_llm(temperature=0.4)
    prompt = (
        f"{PERSONA_PROMPT}\n\n"
        "Answer the user's message in 1-4 friendly sentences. If they ask what "
        "you can do or whether you can handle something, briefly say yes and give "
        "2-3 concrete example questions they could ask about churn.\n\n"
        f"User: {state['user_question']}\n"
        "Answer:"
    )
    answer = getattr(llm.invoke(prompt), "content", str(llm)).strip()
    return {"final_response": answer}


def query_generator(state: GraphState) -> dict:
    """Prompt Gemini to produce a SQL query for the user's question.

    On a retry (``error_message`` set) the previous SQL and its error are added
    so the model can correct itself.
    """
    if state.get("error_message"):
        logger.info("Retrying query generation after error (attempt %d).",
                    state.get("retry_count", 0) + 1)
    else:
        logger.info("Generating a database query for the question.")
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
    logger.info("Generated query, executing against the customer database.")
    return {"generated_query": sql}


def query_executor(state: GraphState) -> dict:
    """Run the generated SQL. Capture results or the error for self-correction."""
    sql = state.get("generated_query", "")
    logger.info("Searching the customer database...")
    try:
        df = run_query(sql)
        logger.info("Query succeeded: %d row(s) returned.", len(df))
        return {
            "query_result": df.to_dict(orient="records"),
            "error_message": None,
        }
    except Exception as exc: 
        logger.info("Query failed: %s", exc)
        return {
            "query_result": None,
            "error_message": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0) + 1,
        }


def response_formatter(state: GraphState) -> dict:
    """Turn the query result into a concise, business-friendly answer.

    Also handles the exhausted-retries case with a graceful fallback message.
    """
    logger.info("Summarizing the results into an answer.")
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
