"""
api.py — FastAPI router.

Endpoints:
  POST /chat        → SSE streaming (progress events → final data → done)
  POST /chat/sync   → JSON response (convenient for curl / testing)

SSE event protocol
──────────────────
event: progress
data: {"step": "<node_name>", "message": "<human readable status>"}

event: data
data: {"answer": "<full Markdown report>"}

event: error
data: {"error": "<message>"}

event: done
data: {}
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from backend.src.agent import agent_graph
from backend.src.config import RATE_LIMIT_PER_MINUTE
from backend.src.cost import reset_serpapi_calls
from backend.src.logging_config import set_request_id
from backend.src.models import ChatRequest
from backend.src.rate_limit import is_allowed, retry_after

logger = logging.getLogger(__name__)
router = APIRouter()


def _enforce_rate_limit(request: Request) -> None:
    """IP-based sliding-window limit. Temporary: becomes per-user once auth
    lands (Phase 2c)."""
    client_key = request.client.host if request.client else "unknown"
    if not is_allowed(client_key, RATE_LIMIT_PER_MINUTE):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded. Please wait before sending another request.",
                "retry_after_seconds": retry_after(client_key),
            },
        )


# Human-readable status messages for each graph node
_NODE_MESSAGES: dict[str, str] = {
    "query_understanding": "🔍 Classifying your query...",
    "react_agent": "⚙️  Fetching Amazon data (search + product details)...",
    "aggregation": "📊 Aggregating and scoring products...",
    "analysis": "🧠 Analysing insights, pricing, and review sentiment...",
    "response_formatter": "✍️  Structuring your research report...",
}

_INITIAL_STATE_TEMPLATE = {
    "intent": "",
    "keywords": [],
    "asins": [],
    "top_n": 6,
    "tool_plan": [],
    "raw_search_results": {},
    "raw_product_details": [],
    "aggregated_products": [],
    "analysis": {},
    "response": {},
    "errors": [],
    "request_id": "",
    "usage": [],
}


async def _event_stream(message: str) -> AsyncIterator[dict]:
    """
    Run the agent graph with astream_events and yield SSE-compatible dicts.

    LangGraph v2 events used:
      - on_chain_start  → progress event when a named node begins
      - on_chain_end    → scan every end event for a non-empty `response` key
    """
    # Per-request observability context (Phase 1c): request id + cost counters
    request_id = str(uuid.uuid4())
    set_request_id(request_id)
    reset_serpapi_calls()
    start_time = time.monotonic()

    if not message or not message.strip():
        yield {
            "event": "error",
            "data": json.dumps({"error": "Message cannot be empty."}),
        }
        yield {"event": "done", "data": json.dumps({})}
        return

    initial_state = {
        **_INITIAL_STATE_TEMPLATE,
        "message": message,
        "request_id": request_id,
    }
    final_response: dict | None = None

    try:
        async for event in agent_graph.astream_events(initial_state, version="v2"):
            kind = event.get("event", "")
            name = event.get("name", "")

            # ── Node start → progress SSE ──────────────────────────────────────
            if kind == "on_chain_start" and name in _NODE_MESSAGES:
                yield {
                    "event": "progress",
                    "data": json.dumps({"step": name, "message": _NODE_MESSAGES[name]}),
                }

            # ── Any node end → try to capture the response ─────────────────────
            # We scan all on_chain_end events (not just response_formatter) to be
            # resilient to LangGraph sub-graph naming differences across versions.
            elif kind == "on_chain_end":
                output = event.get("data", {}).get("output") or {}
                if isinstance(output, dict) and output.get("response"):
                    candidate = output["response"]
                    # Accept if it's a non-empty dict with an "answer" key
                    if isinstance(candidate, dict) and candidate.get("answer"):
                        final_response = candidate
                        logger.info("Captured final response from node: %s", name)

    except Exception:
        logger.exception("Error during agent graph streaming for message: %r", message[:80])
        yield {
            "event": "error",
            "data": json.dumps(
                {"error": "An internal error occurred during research. Please try again."}
            ),
        }
        yield {"event": "done", "data": json.dumps({})}
        return

    # ── Emit final structured data ─────────────────────────────────────────────
    if final_response:
        duration_ms = round((time.monotonic() - start_time) * 1000, 1)
        payload = {**final_response, "duration_ms": duration_ms}
        yield {"event": "data", "data": json.dumps(payload)}
    else:
        logger.error("Agent produced no response for message: %r", message[:80])
        yield {
            "event": "error",
            "data": json.dumps(
                {"error": "The agent produced no response. The query may have returned no data."}
            ),
        }

    yield {"event": "done", "data": json.dumps({})}


@router.post("/chat")
async def chat(request: ChatRequest, raw_request: Request) -> EventSourceResponse:
    """
    Streaming SSE chat endpoint.
    Emits: progress* → (data | error) → done
    """
    _enforce_rate_limit(raw_request)
    return EventSourceResponse(_event_stream(request.message))


@router.post("/chat/sync")
async def chat_sync(request: ChatRequest, raw_request: Request) -> JSONResponse:
    """
    Synchronous (non-streaming) chat endpoint — useful for testing with curl.
    Runs the full agent pipeline and returns the final JSON response.
    """
    _enforce_rate_limit(raw_request)
    if not request.message or not request.message.strip():
        return JSONResponse({"error": "Message cannot be empty."}, status_code=400)

    request_id = str(uuid.uuid4())
    set_request_id(request_id)
    reset_serpapi_calls()
    start_time = time.monotonic()

    initial_state = {
        **_INITIAL_STATE_TEMPLATE,
        "message": request.message,
        "request_id": request_id,
    }
    final_state = await agent_graph.ainvoke(initial_state)
    response = (final_state or {}).get("response") or {}

    if not response:
        return JSONResponse(
            {"error": "The agent produced no response. The query may have returned no data."},
            status_code=500,
        )
    response["duration_ms"] = round((time.monotonic() - start_time) * 1000, 1)
    return JSONResponse(response)
