"""Lightweight logging plumbing for the chatbot.

A single named logger (``telco_bot``) is used across the graph nodes. The
Streamlit UI attaches a :class:`ListLogHandler` that captures formatted records
into an in-memory list so they can be shown in the sidebar "activity log" panel.
"""
from __future__ import annotations

import logging

LOGGER_NAME = "telco_bot"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)


class ListLogHandler(logging.Handler):
    """A logging handler that appends formatted records into a shared list."""

    def __init__(self, buffer: list[str], max_records: int = 500) -> None:
        super().__init__()
        self.buffer = buffer
        self.max_records = max_records
        self.setFormatter(logging.Formatter("%(asctime)s  %(message)s", "%H:%M:%S"))

    def emit(self, record: logging.LogRecord) -> None:
        self.buffer.append(self.format(record))
        # Keep memory bounded by trimming the oldest records in place.
        if len(self.buffer) > self.max_records:
            del self.buffer[: len(self.buffer) - self.max_records]


def attach_list_handler(buffer: list[str]) -> None:
    """Attach a :class:`ListLogHandler` for ``buffer`` exactly once.

    Streamlit reruns the script on every interaction, so we guard against
    registering duplicate handlers that would write the same record twice.
    """
    for handler in logger.handlers:
        if isinstance(handler, ListLogHandler):
            handler.buffer = buffer  # rebind to the current session's list
            return
    logger.addHandler(ListLogHandler(buffer))
