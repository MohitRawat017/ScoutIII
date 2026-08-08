"""Full-graph integration: LLMs and the ReAct agent mocked at their boundaries.

Exercises the real compiled StateGraph wiring (query_understanding -> react_agent
-> aggregation -> analysis -> response_formatter) without any network calls.
Module-level singletons are replaced via the module binding (RunnableSequence
and CompiledGraph attributes are frozen).
"""

from __future__ import annotations

import json

from langchain_core.messages import AIMessage, ToolMessage

from backend.src.agent import agent_graph
from backend.src.models import AnalysisOutput, QueryIntent
from backend.src.nodes import analysis, query_understanding, react_agent


def _initial_state(message: str = "top insulated water bottles") -> dict:
    return {
        "message": message,
        "intent": "",
        "keywords": [],
        "asins": [],
        "top_n": 6,
        "raw_search_results": {},
        "raw_product_details": [],
        "aggregated_products": [],
        "analysis": {},
        "response": {},
        "errors": [],
        "request_id": "test-request-id",
        "usage": [],
    }


def _search_tool_output() -> dict:
    # Shape produced by tools/search.py (already normalised by the tool)
    return {
        "query": "insulated water bottle",
        "total_results": 412,
        "products": [
            {
                "rank": 1,
                "asin": "B01LP0U5X0",
                "title": "HydroFlask Water Bottle 32 oz",
                "extracted_price": 39.95,
                "rating": 4.8,
                "reviews": 45231,
                "bought_last_month": "10K+ bought in past month",
                "badges": ["Best Seller"],
                "sponsored": False,
                "score": 56.06,
            }
        ],
        "related_searches": ["insulated water bottle 32 oz"],
    }


def _product_tool_output() -> dict:
    # Shape produced by tools/product.py (already normalised by the tool)
    return {
        "asin": "B01LP0U5X0",
        "title": "HydroFlask Water Bottle 32 oz",
        "brand": "HydroFlask",
        "extracted_price": 39.95,
        "rating": 4.8,
        "reviews": 45231,
        "bought_last_month": "10K+ bought in past month",
        "badges": ["Best Seller"],
        "about_item": ["Keeps drinks cold 24h"],
        "item_specifications": {"capacity": "32 oz"},
        "review_summary_text": "Customers love the insulation.",
        "review_insights": [{"title": "Insulation performance"}],
        "reviews_histogram": {"5_star": 78},
        "compare_with_similar": [],
    }


def _mock_pipeline(mocker, sample_analysis_output, react_side_effect=None):
    query_llm = mocker.MagicMock()
    query_llm.invoke.return_value = {
        "raw": AIMessage(
            content="",
            usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        ),
        "parsed": QueryIntent(
            intent="search",
            keywords=["insulated water bottle"],
            asins=[],
            top_n=3,
            reasoning="test reasoning",
        ),
    }
    mocker.patch.object(query_understanding, "_structured_llm", query_llm)

    agent = mocker.MagicMock()
    if react_side_effect is not None:
        agent.invoke.side_effect = react_side_effect
    else:
        agent.invoke.return_value = {
            "messages": [
                AIMessage(
                    content="",
                    usage_metadata={"input_tokens": 200, "output_tokens": 80, "total_tokens": 280},
                ),
                ToolMessage(content=json.dumps(_search_tool_output()), tool_call_id="1"),
                ToolMessage(content=json.dumps(_product_tool_output()), tool_call_id="2"),
            ]
        }
    mocker.patch.object(react_agent, "_agent", agent)

    analysis_llm = mocker.MagicMock()
    analysis_llm.invoke.return_value = {
        "raw": AIMessage(
            content="",
            usage_metadata={"input_tokens": 500, "output_tokens": 300, "total_tokens": 800},
        ),
        "parsed": AnalysisOutput(**sample_analysis_output),
    }
    mocker.patch.object(analysis, "_structured_llm", analysis_llm)


async def test_full_graph_produces_well_formed_report(mocker, sample_analysis_output):
    _mock_pipeline(mocker, sample_analysis_output)

    result = await agent_graph.ainvoke(_initial_state())

    response = result["response"]
    assert response["answer"] == sample_analysis_output["answer"]
    assert response["warnings"] == []

    products = result["aggregated_products"]
    assert len(products) == 1
    assert products[0]["asin"] == "B01LP0U5X0"
    assert products[0]["title"] == "HydroFlask Water Bottle 32 oz"
    assert products[0]["revenue_estimate"]["monthly_sales_est"] == 10000

    stats = result["analysis"]["market_stats"]
    assert stats["total_products_analyzed"] == 1

    # Cost visibility (Phase 1c): 10+200+500 input, 5+80+300 output tokens
    usage = response["usage"]
    assert usage["input_tokens"] == 710
    assert usage["output_tokens"] == 385
    assert usage["estimated_cost_usd"] > 0


async def test_full_graph_node_failure_completes_with_partial_notice(
    mocker, sample_analysis_output
):
    _mock_pipeline(mocker, sample_analysis_output, react_side_effect=Exception("serpapi down"))

    result = await agent_graph.ainvoke(_initial_state())

    response = result["response"]
    assert "Partial results" in response["answer"]  # formatter prepends notice
    assert any("react_agent" in w for w in response["warnings"])  # failure surfaced
    assert result["aggregated_products"] == []  # downstream nodes still ran
