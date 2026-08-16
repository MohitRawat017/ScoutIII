"""product tool: normalisation, review-insight extraction, cache behaviour, fetch cap."""

from __future__ import annotations

import pytest

from backend.src.tools import product


@pytest.fixture(autouse=True)
def fresh_detail_fetch_budget():
    """Give every test a fresh per-request detail-fetch budget."""
    product.reset_detail_fetches()


def test_get_product_details_normalises_response(sample_product_response, mocker, tmp_cache_db):
    mock_call = mocker.patch(
        "backend.src.tools.product.call_serpapi", return_value=sample_product_response
    )

    result = product.get_product_details("b01lp0u5x0")

    assert result["asin"] == "B01LP0U5X0"  # normalised to upper-case for ASIN joins
    assert result["title"] == "HydroFlask Water Bottle 32 oz"
    assert result["brand"] == "HydroFlask"
    assert result["extracted_price"] == 39.95
    assert result["extracted_old_price"] == 44.95
    assert result["about_item"] == ["Keeps drinks cold 24h", "BPA-free"]
    assert result["item_specifications"]["capacity"] == "32 oz"
    assert result["review_summary_text"].startswith("Customers love")
    assert result["review_insights"][0]["title"] == "Insulation performance"
    assert result["reviews_histogram"]["5_star"] == 78
    assert result["compare_with_similar"][0]["asin"] == "B08XYZ1234"
    assert mock_call.call_count == 1


def test_get_product_details_caches_per_asin(sample_product_response, mocker, tmp_cache_db):
    mock_call = mocker.patch(
        "backend.src.tools.product.call_serpapi", return_value=sample_product_response
    )

    first = product.get_product_details("B01LP0U5X0")
    second = product.get_product_details("B01LP0U5X0")

    assert mock_call.call_count == 1  # second call served from cache
    assert second == first


def test_get_product_details_allows_eight_fetches_per_request(
    sample_product_response, mocker, tmp_cache_db
):
    mock_call = mocker.patch(
        "backend.src.tools.product.call_serpapi", return_value=sample_product_response
    )

    for i in range(8):
        assert "error" not in product.get_product_details(f"B00000000{i}")

    assert mock_call.call_count == 8


def test_get_product_details_blocks_ninth_fetch_per_request(
    sample_product_response, mocker, tmp_cache_db
):
    mock_call = mocker.patch(
        "backend.src.tools.product.call_serpapi", return_value=sample_product_response
    )
    for i in range(8):
        product.get_product_details(f"B00000000{i}")

    ninth = product.get_product_details("B000000099")

    assert ninth == {"asin": "B000000099", "error": "detail-fetch limit reached (8 per request)"}
    assert mock_call.call_count == 8  # blocked before reaching SerpApi


def test_reset_detail_fetches_allows_new_request(sample_product_response, mocker, tmp_cache_db):
    mock_call = mocker.patch(
        "backend.src.tools.product.call_serpapi", return_value=sample_product_response
    )
    for i in range(8):
        product.get_product_details(f"B00000000{i}")
    assert "error" in product.get_product_details("B000000099")

    product.reset_detail_fetches()
    result = product.get_product_details("B000000099")

    assert "error" not in result
    assert mock_call.call_count == 9


def test_get_product_details_cache_hits_do_not_consume_budget(
    sample_product_response, mocker, tmp_cache_db
):
    mock_call = mocker.patch(
        "backend.src.tools.product.call_serpapi", return_value=sample_product_response
    )
    product.get_product_details("B01LP0U5X0")
    product.get_product_details("B01LP0U5X0")  # cache hit — free

    # The hit didn't consume budget, so 7 more misses still fit in the 8-call cap
    for i in range(7):
        assert "error" not in product.get_product_details(f"B00000000{i}")

    assert mock_call.call_count == 8
