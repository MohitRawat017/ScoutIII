"""
cost.py — Token-usage → USD estimation for Gemini calls, and SerpApi call counting.

Token usage comes from LangChain `usage_metadata` on AI messages. Pricing is
approximate (public Gemini pricing at time of writing) and **env-overridable** —
verify at https://ai.google.dev/pricing and tune via .env if it drifts.

SerpApi calls are counted via a ContextVar because the tools layer has no access
to AgentState; the count is read back by the response_formatter at request end.
Entry points must call `reset_serpapi_calls()` before invoking the graph.
"""

from __future__ import annotations

import os
from contextvars import ContextVar

# Per-1K-token USD rates (verify against current Gemini pricing before relying
# on these for budgeting).
FLASH_COST_PER_1K_INPUT = float(os.getenv("FLASH_COST_PER_1K_INPUT", "0.0003"))
FLASH_COST_PER_1K_OUTPUT = float(os.getenv("FLASH_COST_PER_1K_OUTPUT", "0.0025"))
PRO_COST_PER_1K_INPUT = float(os.getenv("PRO_COST_PER_1K_INPUT", "0.00125"))
PRO_COST_PER_1K_OUTPUT = float(os.getenv("PRO_COST_PER_1K_OUTPUT", "0.010"))

# SerpApi is billed per call; default reflects a ~$50/10k-searches plan.
SERPAPI_COST_PER_CALL = float(os.getenv("SERPAPI_COST_PER_CALL", "0.005"))

_RATES: dict[str, tuple[float, float]] = {
    "flash": (FLASH_COST_PER_1K_INPUT, FLASH_COST_PER_1K_OUTPUT),
    "pro": (PRO_COST_PER_1K_INPUT, PRO_COST_PER_1K_OUTPUT),
}

_serpapi_calls: ContextVar[int] = ContextVar("serpapi_calls", default=0)


def estimate_llm_cost(input_tokens: int, output_tokens: int, tier: str) -> float:
    """Estimated USD cost for one tier ("flash" | "pro") of Gemini usage."""
    rate_in, rate_out = _RATES.get(tier, _RATES["flash"])
    cost = (input_tokens / 1000 * rate_in) + (output_tokens / 1000 * rate_out)
    return round(cost, 6)


def usage_entry(node: str, tier: str, usage_metadata: dict) -> dict:
    """Build a state-ready usage record from a LangChain usage_metadata dict."""
    in_tok = int(usage_metadata.get("input_tokens") or 0)
    out_tok = int(usage_metadata.get("output_tokens") or 0)
    return {
        "node": node,
        "tier": tier,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "estimated_cost_usd": estimate_llm_cost(in_tok, out_tok, tier),
    }


def record_serpapi_call() -> None:
    _serpapi_calls.set(_serpapi_calls.get() + 1)


def reset_serpapi_calls() -> None:
    _serpapi_calls.set(0)


def serpapi_call_count() -> int:
    return _serpapi_calls.get()


def summarize_usage(entries: list[dict]) -> dict:
    """Aggregate per-node usage entries plus SerpApi calls into a cost summary."""
    llm_cost = round(sum(e.get("estimated_cost_usd", 0.0) for e in entries), 6)
    calls = serpapi_call_count()
    return {
        "input_tokens": sum(e.get("input_tokens", 0) for e in entries),
        "output_tokens": sum(e.get("output_tokens", 0) for e in entries),
        "serpapi_calls": calls,
        "estimated_cost_usd": round(llm_cost + calls * SERPAPI_COST_PER_CALL, 6),
    }
