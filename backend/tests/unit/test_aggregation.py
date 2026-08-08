"""aggregation node: merge rules, score recompute, revenue heuristic, degradation."""

from __future__ import annotations

from backend.src.nodes.aggregation import _estimate_revenue, aggregation_node


def _state(search_products: list[dict], details: list[dict]) -> dict:
    return {
        "raw_search_results": {"products": search_products},
        "raw_product_details": details,
        "errors": [],
    }


def _search_product() -> dict:
    return {
        "asin": "B01LP0U5X0",
        "title": "search title",
        "extracted_price": 39.95,
        "rating": 4.8,
        "reviews": 100,
        "badges": ["SearchBadge"],
        "sponsored": False,
    }


def _detail() -> dict:
    return {
        "asin": "B01LP0U5X0",
        "title": "detail title",
        "brand": "HydroFlask",
        "extracted_price": 39.95,
        "rating": 4.8,
        "reviews": 45231,
        "bought_last_month": "10K+ bought in past month",
        "badges": ["DetailBadge"],
        "about_item": ["Keeps drinks cold 24h"],
        "item_specifications": {"capacity": "32 oz"},
        "review_insights": [{"title": "Insulation performance"}],
        "reviews_histogram": {"5_star": 78},
        "compare_with_similar": [],
    }


def test_estimate_revenue_uses_bought_last_month():
    est = _estimate_revenue(
        {
            "asin": "B01",
            "title": "T",
            "extracted_price": 39.95,
            "reviews": 45231,
            "bought_last_month": "10K+ bought in past month",
        }
    )

    assert est["monthly_sales_est"] == 10000
    assert est["monthly_revenue_est"] == int(10000 * 39.95)
    assert est["basis"] == "bought_last_month"


def test_estimate_revenue_returns_none_without_signal():
    assert _estimate_revenue({}) is None
    assert _estimate_revenue({"extracted_price": 0.0, "reviews": 0}) is None


def test_merge_detail_wins_and_enriches():
    out = aggregation_node(_state([_search_product()], [_detail()]))

    (p,) = out["aggregated_products"]
    assert p["title"] == "detail title"
    assert p["brand"] == "HydroFlask"
    assert sorted(p["badges"]) == ["DetailBadge", "SearchBadge"]
    assert p["about_item"] == ["Keeps drinks cold 24h"]
    assert p["review_insights"] == [{"title": "Insulation performance"}]
    assert p["revenue_estimate"]["monthly_sales_est"] == 10000
    assert isinstance(p["score"], float) and p["score"] > 0

    stats = out["analysis"]["market_stats"]
    assert stats["total_products_analyzed"] == 1
    assert stats["avg_rating"] == 4.8
    assert stats["price_range"]["min"] == 39.95


def test_detail_only_products_are_included():
    detail = _detail()
    detail["asin"] = "B08XYZ1234"

    out = aggregation_node(_state([], [detail]))

    assert [p["asin"] for p in out["aggregated_products"]] == ["B08XYZ1234"]
    assert out["aggregated_products"][0]["rank"] == 1


def test_empty_input_returns_empty_market_stats():
    out = aggregation_node(_state([], []))

    assert out["aggregated_products"] == []
    assert out["analysis"]["market_stats"]["total_products_analyzed"] == 0


def test_failure_returns_safe_defaults_and_appends_errors(mocker):
    mocker.patch("backend.src.nodes.aggregation._aggregate", side_effect=Exception("boom"))

    out = aggregation_node(_state([], []))

    assert out["aggregated_products"] == []
    assert out["analysis"]["market_stats"]["total_products_analyzed"] == 0
    assert any("aggregation" in e for e in out["errors"])
