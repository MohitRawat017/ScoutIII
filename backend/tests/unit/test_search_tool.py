"""search tool: scoring formula, sponsored filtering, cache behaviour."""

from __future__ import annotations

import math

import pytest

from backend.src.tools import search


def test_parse_bought_last_month_formats():
    assert search.parse_bought_last_month("20K+ bought in past month") == 20000
    assert search.parse_bought_last_month("300+ bought in past month") == 300
    assert search.parse_bought_last_month(None) == 0
    assert search.parse_bought_last_month("") == 0


def test_score_product_formula():
    # rating × ln(reviews+1) + ln(blm+1)×0.5
    p = {"rating": 4.8, "reviews": 45231, "bought_last_month": "10K+ bought in past month"}
    expected = round(4.8 * math.log(45232) + math.log(10001) * 0.5, 4)
    assert search.score_product(p) == pytest.approx(expected)
    # Zero reviews → log(0+1) = 0 regardless of rating
    assert search.score_product({"rating": 5.0, "reviews": 0}) == 0.0


def test_search_products_prefers_non_sponsored(sample_search_response, mocker, tmp_cache_db):
    mock_call = mocker.patch(
        "backend.src.tools.search.call_serpapi", return_value=sample_search_response
    )

    result = search.search_products("insulated water bottle", n=2)

    asins = [p["asin"] for p in result["products"]]
    assert asins == ["B01LP0U5X0", "B08XYZ1234"]  # sponsored excluded, best score first
    assert result["total_results"] == 412
    assert mock_call.call_count == 1


def test_search_products_falls_back_to_include_sponsored(
    sample_search_response, mocker, tmp_cache_db
):
    mocker.patch("backend.src.tools.search.call_serpapi", return_value=sample_search_response)

    result = search.search_products("insulated water bottle", n=3)

    asins = [p["asin"] for p in result["products"]]
    assert "B07SPONS55" in asins  # organic pool smaller than n → sponsored included


def test_search_products_caches_results(sample_search_response, mocker, tmp_cache_db):
    mock_call = mocker.patch(
        "backend.src.tools.search.call_serpapi", return_value=sample_search_response
    )

    first = search.search_products("insulated water bottle")
    second = search.search_products("insulated water bottle")

    assert mock_call.call_count == 1  # second call served from cache
    assert second == first


def test_search_products_empty_query_short_circuits(mocker, tmp_cache_db):
    mock_call = mocker.patch("backend.src.tools.search.call_serpapi")

    result = search.search_products("   ")

    assert result["products"] == []
    assert result["total_results"] == 0
    mock_call.assert_not_called()
