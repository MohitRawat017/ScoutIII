"""
query_understanding.py — Node 1: classify intent + extract keywords/ASINs.

Uses Gemini Flash with structured output so the result is always a typed QueryIntent.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from backend.src.config import GEMINI_FLASH, get_llm
from backend.src.cost import usage_entry
from backend.src.models import AgentState, QueryIntent

logger = logging.getLogger(__name__)

# Module-level LLM to avoid re-instantiation per request
_llm = get_llm(temperature=0.0, model_name=GEMINI_FLASH)
# include_raw so we can read token usage from the underlying AI message
_structured_llm = _llm.with_structured_output(QueryIntent, include_raw=True)

_SYSTEM = """You are an Amazon product research query classifier for a professional seller intelligence tool.

Given the user's message, output a structured classification:

intent options:
  - "search"     → user wants to find products matching criteria (e.g. "show me top coffee makers")
  - "analyze"    → user wants market / competitive analysis of a category (e.g. "analyze the protein powder market")
  - "compare"    → user explicitly wants to compare specific products or ASINs
  - "deep_dive"  → user wants exhaustive detail on one specific product / ASIN

Rules:
- Extract Amazon search keywords (concise noun phrases, NOT the whole sentence).
- If the user mentions specific ASINs (format: B followed by 9 alphanumeric chars, e.g. B07XXXXX), capture them in `asins`.
- top_n defaults to 6 unless the user specifies a different number.
- If the query is ambiguous between "search" and "analyze", prefer "analyze".
- Be concise in `reasoning` (one sentence).
"""


def query_understanding_node(state: AgentState) -> dict:
    message: str = state.get("message", "").strip()

    if not message:
        logger.warning("query_understanding_node called with empty message")
        return {
            "intent": "search",
            "keywords": [],
            "asins": [],
            "top_n": 6,
        }

    logger.info("Classifying query: %r", message[:100])

    try:
        raw_result: dict = _structured_llm.invoke(
            [SystemMessage(content=_SYSTEM), HumanMessage(content=message)]
        )
        result: QueryIntent | None = raw_result.get("parsed")
        if result is None:
            raise ValueError(f"structured output parse failed: {raw_result.get('parsing_error')}")

        usage = list(state.get("usage") or [])
        raw_message = raw_result.get("raw")
        if raw_message is not None and getattr(raw_message, "usage_metadata", None):
            usage.append(usage_entry("query_understanding", "flash", raw_message.usage_metadata))
    except Exception:
        # Degrade gracefully: fall back to raw-text keyword search so the
        # pipeline can still gather data instead of dying on the SSE stream.
        logger.exception("Intent classification failed; defaulting to search")
        errors = list(state.get("errors") or [])
        errors.append(
            "query_understanding: intent classification failed; fell back to keyword search"
        )
        return {
            "intent": "search",
            "keywords": [message],
            "asins": [],
            "top_n": 6,
            "errors": errors,
        }

    logger.info(
        "Intent: %s | Keywords: %s | ASINs: %s | top_n: %d",
        result.intent,
        result.keywords,
        result.asins,
        result.top_n,
    )

    return {
        "intent": result.intent,
        "keywords": result.keywords,
        "asins": result.asins,
        "top_n": result.top_n,
        "usage": usage,
    }
