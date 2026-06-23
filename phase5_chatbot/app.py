"""Interactive Streamlit chat UI for the Customer Churn Insights chatbot.

Run from the project root:
    streamlit run phase5_chatbot/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make the package importable whether launched as a script or a module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phase5_chatbot import config 
from phase5_chatbot.database import get_customer_count 
from phase5_chatbot.graph import stream_question 
from phase5_chatbot.logging_utils import attach_list_handler 
from phase5_chatbot.ui.sample_questions import (  
    FEATURED_QUESTIONS,
    SAMPLE_QUESTIONS,
)

st.set_page_config(
    page_title="Telco Bot",
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
    if "logs" not in st.session_state:
        st.session_state.logs = []  # in-memory activity log lines
    # Route the named logger's records into this session's log buffer.
    attach_list_handler(st.session_state.logs)


def queue_question(question: str) -> None:
    """Stage a question (from a chip or chat input) and trigger a rerun."""
    st.session_state.pending_question = question
    st.rerun()


# Friendly, user-facing labels for each pipeline step shown in the status box.
_STEP_LABELS = {
    "question_classifier": "Understanding your question...",
    "generic_responder": "Putting together an answer...",
    "query_generator": "Working out how to look that up...",
    "query_executor": "Searching the customer database...",
    "response_formatter": "Summarizing the answer...",
}


def process_question(question: str) -> None:
    """Run the LangGraph pipeline for a question and store the exchange.

    Streams per-node progress into a live status box so the user can see what
    the assistant is doing while the LLM works.
    """
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

    final_state: dict = {}
    with st.status("Thinking...", expanded=True) as status:
        try:
            for node_name, output, final_state in stream_question(question):
                label = _STEP_LABELS.get(node_name, node_name)
                st.write(label)
                if node_name == "query_executor" and output and output.get("error_message"):
                    st.write("That query didn't work - trying a different approach...")
            status.update(label="Done", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="Something went wrong", state="error")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Something went wrong while answering: {exc}",
            })
            return

    st.session_state.messages.append({
        "role": "assistant",
        "content": final_state.get("final_response", "Sorry, I couldn't answer that."),
        "sql": final_state.get("generated_query", ""),
        "data": final_state.get("query_result"),
    })


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.title("\U0001F4CA Telco Bot")
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
        st.subheader("Activity log")
        st.caption("See what the assistant is doing behind the scenes.")
        if st.toggle("Show activity log", key="show_logs"):
            logs = st.session_state.get("logs", [])
            if logs:
                st.code("\n".join(logs[-100:]), language=None)
            else:
                st.caption("No activity yet - ask a question to see the log.")
            if st.button("Clear log", use_container_width=True):
                st.session_state.logs.clear()
                st.rerun()

        st.divider()
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.session_state.logs.clear()
            st.rerun()


# ----------------------------------------------------------------------------
# Main area
# ----------------------------------------------------------------------------
def render_welcome() -> None:
    st.subheader("Welcome \U0001F44B")
    st.write(
        "I'm **Telco Bot**. I can answer questions about **7,043 Telco customers** "
        "and their churn behaviour. Our overall churn rate is **26.54%**. "
        "Click a sample question below or type your own at the bottom."
    )


def render_history() -> None:
    # Only the natural-language answer is shown; the underlying SQL and raw
    # query rows are kept in session state for logging but hidden from users.
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


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

    st.title("Telco Bot - Customer Churn Insights")

    # Process any staged question (from a chip or the chat input) first so the
    # new exchange is included in the history render below. The live status box
    # is rendered inside process_question itself.
    pending = st.session_state.pending_question
    if pending:
        st.session_state.pending_question = None
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
