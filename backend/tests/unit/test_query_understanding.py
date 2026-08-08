"""query_understanding node: intent passthrough, ASIN capture, degraded fallback."""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage

from backend.src.models import QueryIntent
from backend.src.nodes import query_understanding as qu


def _intent(intent: str, asins: list[str] | None = None) -> QueryIntent:
    return QueryIntent(
        intent=intent,
        keywords=["insulated water bottle"],
        asins=asins or [],
        top_n=6,
        reasoning="test reasoning",
    )


def _patch_llm(mocker, *, return_value=None, side_effect=None):
    """Replace the module-level structured LLM binding (RunnableSequence attrs
    are frozen, so the module binding — not the object attribute — is patched).
    Return values use the include_raw shape: {"raw": AIMessage, "parsed": ...}."""
    mock_llm = mocker.MagicMock()
    if side_effect is not None:
        mock_llm.invoke.side_effect = side_effect
    else:
        raw = AIMessage(
            content="",
            usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        )
        mock_llm.invoke.return_value = {"raw": raw, "parsed": return_value}
    mocker.patch.object(qu, "_structured_llm", mock_llm)


@pytest.mark.parametrize("intent", ["search", "analyze", "compare", "deep_dive"])
def test_all_intents_pass_through(base_state, mocker, intent):
    _patch_llm(mocker, return_value=_intent(intent))

    out = qu.query_understanding_node(base_state)

    assert out["intent"] == intent
    assert out["keywords"] == ["insulated water bottle"]
    assert out["top_n"] == 6
    # Token usage is recorded from the raw AI message (Phase 1c)
    assert out["usage"][0]["tier"] == "flash"
    assert out["usage"][0]["input_tokens"] == 10


def test_asins_are_captured(base_state, mocker):
    _patch_llm(mocker, return_value=_intent("deep_dive", asins=["B01LP0U5X0"]))

    out = qu.query_understanding_node(base_state)

    assert out["asins"] == ["B01LP0U5X0"]


def test_llm_failure_degrades_to_keyword_search(base_state, mocker):
    _patch_llm(mocker, side_effect=Exception("gemini unavailable"))

    out = qu.query_understanding_node(base_state)

    assert out["intent"] == "search"
    assert out["keywords"] == [base_state["message"]]
    assert any("query_understanding" in e for e in out["errors"])


def test_empty_message_returns_defaults():
    out = qu.query_understanding_node({"message": "  ", "errors": []})

    assert out == {"intent": "search", "keywords": [], "asins": [], "top_n": 6}
