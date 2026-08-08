"""instrumentation.timed_node: duration logging for sync and async nodes."""

from __future__ import annotations

import logging

from backend.src.instrumentation import timed_node


def test_timed_node_logs_duration_and_request_id(caplog):
    @timed_node("aggregation")
    def sample_node(state: dict) -> dict:
        return {}

    with caplog.at_level(logging.INFO, logger="scoutii.timing"):
        result = sample_node({"request_id": "rid-123"})

    assert result == {}
    (record,) = caplog.records
    assert record.node == "aggregation"
    assert record.duration_ms >= 0
    assert record.request_id == "rid-123"


async def test_timed_node_supports_async_functions(caplog):
    @timed_node("analysis")
    async def async_node(state: dict) -> dict:
        return {"ok": True}

    with caplog.at_level(logging.INFO, logger="scoutii.timing"):
        result = await async_node({"request_id": "rid-456"})

    assert result == {"ok": True}
    (record,) = caplog.records
    assert record.node == "analysis"
    assert record.request_id == "rid-456"


def test_timed_node_preserves_function_name():
    @timed_node("react_agent")
    def my_node(state: dict) -> dict:
        return {}

    assert my_node.__name__ == "my_node"  # functools.wraps keeps LangGraph naming intact
