"""product tool: normalisation, review-insight extraction, cache behaviour."""

from __future__ import annotations

from backend.src.tools import product


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
