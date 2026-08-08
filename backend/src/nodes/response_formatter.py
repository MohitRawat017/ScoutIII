"""
response_formatter.py — Node 6: assemble the final response dict.

The LLM in analysis_node produces the complete Markdown report as `analysis["answer"]`.
This node is a thin pass-through that packages it into the ChatResponse schema.
"""

from __future__ import annotations

import logging

from backend.src.cost import summarize_usage
from backend.src.models import AgentState, ChatResponse

logger = logging.getLogger(__name__)


def response_formatter_node(state: AgentState) -> dict:
    analysis = state.get("analysis") or {}
    answer = analysis.get("answer") or "No analysis could be produced for this query."

    # Surface node failures as an explicit partial-results notice (Phase 1a)
    errors = list(state.get("errors") or [])
    if errors:
        notice = "> ⚠️ **Partial results** — some pipeline steps failed:\n"
        notice += "\n".join(f"> - {e}" for e in errors)
        notice += "\n\n"
        answer = notice + answer

    # Cost visibility (Phase 1c): aggregate per-node LLM usage + SerpApi calls
    usage = summarize_usage(list(state.get("usage") or []))
    logger.info(
        "Request cost estimate: $%s (%d in / %d out tokens, %d SerpApi calls)",
        usage["estimated_cost_usd"],
        usage["input_tokens"],
        usage["output_tokens"],
        usage["serpapi_calls"],
    )

    response = ChatResponse(answer=answer, warnings=errors, usage=usage)
    return {"response": response.model_dump()}
