"""cost.py: rate math, usage entries, SerpApi counting, summary aggregation."""

from __future__ import annotations

from backend.src import cost


def setup_function():
    cost.reset_serpapi_calls()


def test_estimate_llm_cost_default_rates():
    # flash: 1000 in @ 0.0003 + 1000 out @ 0.0025
    assert cost.estimate_llm_cost(1000, 1000, "flash") == round(0.0003 + 0.0025, 6)
    # pro: 1000 in @ 0.00125 + 1000 out @ 0.010
    assert cost.estimate_llm_cost(1000, 1000, "pro") == round(0.00125 + 0.010, 6)


def test_estimate_llm_cost_handles_zero_usage_and_unknown_tier():
    assert cost.estimate_llm_cost(0, 0, "pro") == 0.0
    assert cost.estimate_llm_cost(1000, 0, "unknown-tier") == 0.0003  # falls back to flash


def test_usage_entry_shape():
    entry = cost.usage_entry(
        "analysis", "pro", {"input_tokens": 500, "output_tokens": 300, "total_tokens": 800}
    )

    assert entry["node"] == "analysis"
    assert entry["tier"] == "pro"
    assert entry["input_tokens"] == 500
    assert entry["output_tokens"] == 300
    assert entry["estimated_cost_usd"] == cost.estimate_llm_cost(500, 300, "pro")


def test_serpapi_counter_roundtrip():
    assert cost.serpapi_call_count() == 0
    cost.record_serpapi_call()
    cost.record_serpapi_call()
    assert cost.serpapi_call_count() == 2
    cost.reset_serpapi_calls()
    assert cost.serpapi_call_count() == 0


def test_summarize_usage_totals():
    cost.record_serpapi_call()
    cost.record_serpapi_call()
    entries = [
        {"estimated_cost_usd": 0.001, "input_tokens": 100, "output_tokens": 50},
        {"estimated_cost_usd": 0.002, "input_tokens": 200, "output_tokens": 80},
    ]

    summary = cost.summarize_usage(entries)

    assert summary["input_tokens"] == 300
    assert summary["output_tokens"] == 130
    assert summary["serpapi_calls"] == 2
    expected = round(0.001 + 0.002 + 2 * cost.SERPAPI_COST_PER_CALL, 6)
    assert summary["estimated_cost_usd"] == expected
