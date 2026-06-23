r"""Compile the LangGraph self-correction pipeline.

Flow:
    question_classifier -> (generic) -> generic_responder -> END
                        \-> (data)    -> query_generator -> query_executor
    query_executor -> (success) -> response_formatter -> END
                   \-> (error, retries left) -> query_generator
                   \-> (error, retries exhausted) -> response_formatter
"""
from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from . import config
from .nodes import (
    generic_responder,
    query_executor,
    query_generator,
    question_classifier,
    response_formatter,
)
from .state import GraphState


def route_by_type(state: GraphState) -> str:
    """Route a freshly classified question to the right entry node."""
    return "generic" if state.get("question_type") == "generic" else "data"


def route_after_execution(state: GraphState) -> str:
    """Decide where to go after the executor runs.

    Returns one of: 'format' (success or retries exhausted) or 'retry'.
    """
    if state.get("error_message") is None:
        return "format"
    if state.get("retry_count", 0) < config.MAX_RETRIES:
        return "retry"
    return "format"  # give up gracefully; formatter emits a fallback message


def build_graph():
    """Construct and compile the LangGraph workflow."""
    workflow = StateGraph(GraphState)

    workflow.add_node("question_classifier", question_classifier)
    workflow.add_node("generic_responder", generic_responder)
    workflow.add_node("query_generator", query_generator)
    workflow.add_node("query_executor", query_executor)
    workflow.add_node("response_formatter", response_formatter)

    workflow.add_edge(START, "question_classifier")
    workflow.add_conditional_edges(
        "question_classifier",
        route_by_type,
        {
            "generic": "generic_responder",
            "data": "query_generator",
        },
    )
    workflow.add_edge("generic_responder", END)
    workflow.add_edge("query_generator", "query_executor")
    workflow.add_conditional_edges(
        "query_executor",
        route_after_execution,
        {
            "retry": "query_generator",
            "format": "response_formatter",
        },
    )
    workflow.add_edge("response_formatter", END)

    return workflow.compile()


@lru_cache(maxsize=1)
def get_graph():
    """Return a cached compiled graph (compiled once per process)."""
    return build_graph()


def _initial_state(question: str) -> GraphState:
    return {
        "user_question": question,
        "question_type": "",
        "generated_query": "",
        "query_result": None,
        "error_message": None,
        "retry_count": 0,
        "final_response": "",
    }


def answer_question(question: str) -> GraphState:
    """Run the full pipeline for a question and return the final state."""
    graph = get_graph()
    return graph.invoke(_initial_state(question))


def stream_question(question: str):
    """Run the pipeline, yielding ``(node_name, output, merged_state)`` per step.

    Lets the UI surface live progress while the LLM works. The final yielded
    ``merged_state`` is equivalent to what :func:`answer_question` returns.
    """
    graph = get_graph()
    merged: dict = _initial_state(question)
    for chunk in graph.stream(merged):  # default "updates" stream mode
        for node_name, output in chunk.items():
            if output:
                merged.update(output)
            yield node_name, output, merged
