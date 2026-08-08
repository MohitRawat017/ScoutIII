"""
logging_config.py — Structured (JSON) logging setup.

One `configure_logging()` call at startup makes every application log line a
JSON object. A ContextVar carries the current request_id so it appears on
every line without touching call sites. uvicorn's own loggers keep their
default format so server logs stay readable.
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar

current_request_id: ContextVar[str | None] = ContextVar("current_request_id", default=None)


def set_request_id(request_id: str) -> None:
    current_request_id.set(request_id)


class _RequestIdFilter(logging.Filter):
    """Inject the current request_id into every record that lacks one."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = current_request_id.get() or "-"
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        for key in ("node", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    """Route the application log stream to stdout as JSON.

    uvicorn/uvicorn.access/uvicorn.error keep their default handlers and
    formatting (propagate=False) so server logs are untouched.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.addFilter(_RequestIdFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.propagate = False
        if not uv_logger.handlers:
            uv_logger.addHandler(logging.StreamHandler(sys.stdout))
