"""logging_config: JSON output shape and request-id injection."""

from __future__ import annotations

import json
import logging

from backend.src.logging_config import (
    JSONFormatter,
    _RequestIdFilter,
    current_request_id,
)


def _make_record(message: str = "hello") -> logging.LogRecord:
    return logging.LogRecord("test.logger", logging.INFO, __file__, 1, message, (), None)


def test_formatter_emits_valid_json_with_core_fields():
    record = _make_record()
    payload = json.loads(JSONFormatter().format(record))

    assert payload["message"] == "hello"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert "timestamp" in payload


def test_request_id_filter_injects_current_context():
    token = current_request_id.set("req-abc")
    try:
        record = _make_record()
        assert _RequestIdFilter().filter(record) is True
        payload = json.loads(JSONFormatter().format(record))
        assert payload["request_id"] == "req-abc"
    finally:
        current_request_id.reset(token)


def test_request_id_defaults_to_dash_when_unset():
    record = _make_record()
    _RequestIdFilter().filter(record)
    payload = json.loads(JSONFormatter().format(record))
    assert payload["request_id"] == "-"


def test_node_and_duration_fields_pass_through():
    record = _make_record()
    record.node = "aggregation"
    record.duration_ms = 12.3
    payload = json.loads(JSONFormatter().format(record))
    assert payload["node"] == "aggregation"
    assert payload["duration_ms"] == 12.3
