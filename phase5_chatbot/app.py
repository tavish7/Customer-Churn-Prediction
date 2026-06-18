"""Interactive Streamlit chat UI for the Customer Churn Insights chatbot.

Run from the project root:
    streamlit run phase5_chatbot/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Make the package importable whether launched as a script or a module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phase5_chatbot import config 
from phase5_chatbot.database import get_customer_count 
from phase5_chatbot.graph import answer_question 
from phase5_chatbot.ui.sample_questions import (  
    FEATURED_QUESTIONS,
    SAMPLE_QUESTIONS,
)

st.set_page_config(
    page_title="Churn Insights Chatbot",
    page_icon="\U0001F4CA",
    layout="wide",
)

CHIP_CSS = """
<style>
.stButton > button {
    border-radius: 999px;
    border: 1px solid rgba(128, 128, 128, 0.4);
    padding: 0.35rem 0.9rem;
    font-size: 0.9rem;
    text-align: left;
    white-space: normal;
    height: auto;
}
.stButton > button:hover {
    border-color: #2e7bf6;
    color: #2e7bf6;
}
</style>
"""
st.markdown(CHIP_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list of dicts: role, content, sql?, data?
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


def queue_question(question: str) -> None:
    """Stage a question (from a chip or chat input) and trigger a rerun."""
    st.session_state.pending_question = question
    st.rerun()


def process_question(question: str) -> None:
    """Run the LangGraph pipeline for a question and store the exchange."""
    st.session_state.messages.append({"role": "user", "content": question})

    if not config.get_api_key():
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "No Gemini API key found. Copy `phase5_chatbot/.env.example` to "
                "`phase5_chatbot/.env`, add your `GOOGLE_API_KEY`, and restart."
            ),
        })
        return

    try:
        result = answer_question(question)
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("final_response", "Sorry, I couldn't answer that."),
            "sql": result.get("generated_query", ""),
            "data": result.get("query_result"),
        })
    except Exception as exc:  # noqa: BLE001
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Something went wrong while answering: {exc}",
        })


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.title("\U0001F4CA Churn Insights")
        st.caption("Ask questions about Telco customer churn in plain English.")

        st.subheader("Status")
        if config.get_api_key():
            st.success("Gemini API key detected", icon="\u2705")
        else:
            st.warning("No GOOGLE_API_KEY set", icon="\u26A0\uFE0F")

        customer_count = get_customer_count()
        if customer_count:
            st.info(f"Database ready: {customer_count:,} customers", icon="\U0001F5C4\uFE0F")
        else:
            st.error("Database not available", icon="\u274C")

        if config.ERD_IMAGE_PATH.exists():
            with st.expander("View data model (ERD)"):
                st.image(str(config.ERD_IMAGE_PATH), use_container_width=True)

        st.subheader("Sample questions")
        for category, items in SAMPLE_QUESTIONS.items():
            with st.expander(category):
                for question, query_id in items:
                    if st.button(question, key=f"side_{query_id}", use_container_width=True):
                        queue_question(question)

        st.divider()
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()


# ----------------------------------------------------------------------------
# Main area
# ----------------------------------------------------------------------------
def render_welcome() -> None:
    st.subheader("Welcome \U0001F44B")
    st.write(
        "I can answer questions about **7,043 Telco customers** and their churn "
        "behaviour. Our overall churn rate is **26.54%**. "
        "Click a sample question below or type your own at the bottom."
    )


def render_history() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                sql = msg.get("sql")
                if sql:
                    with st.expander("View generated SQL"):
                        st.code(sql, language="sql")
                data = msg.get("data")
                if data:
                    with st.expander(f"View raw data ({len(data)} rows)"):
                        st.dataframe(pd.DataFrame(data), use_container_width=True)


def render_featured_chips() -> None:
    st.caption("Try a sample question:")
    cols = st.columns(2)
    for i, question in enumerate(FEATURED_QUESTIONS):
        if cols[i % 2].button(question, key=f"feat_{i}", use_container_width=True):
            queue_question(question)


# ----------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------
def main() -> None:
    _init_state()
    render_sidebar()

    st.title("Customer Churn Insights Chatbot")

    # Process any staged question (from a chip or the chat input) first so the
    # new exchange is included in the history render below.
    pending = st.session_state.pending_question
    if pending:
        st.session_state.pending_question = None
        with st.spinner("Analyzing your question..."):
            process_question(pending)

    if not st.session_state.messages:
        render_welcome()
    else:
        render_history()

    render_featured_chips()

    if prompt := st.chat_input("Ask anything about customer churn..."):
        queue_question(prompt)


if __name__ == "__main__":
    main()
