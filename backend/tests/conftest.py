"""
Shared pytest fixtures for the Scoutii test suite.

Dummy API keys are set BEFORE any backend import so module-level LLM/client
singletons construct successfully. No real network calls are ever made —
SerpApi and Gemini are mocked at their usage boundaries.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("SERPAPI_KEY", "test-key-not-real")
os.environ.setdefault("GEMINIAPI_KEY", "test-key-not-real")

_FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture()
def sample_search_response() -> dict:
    """Raw SerpApi `amazon` engine search response."""
    return load_fixture("sample_search_response.json")


@pytest.fixture()
def sample_product_response() -> dict:
    """Raw SerpApi `amazon_product` engine detail response."""
    return load_fixture("sample_product_response.json")


@pytest.fixture()
def sample_analysis_output() -> dict:
    """Gemini Pro structured analysis output."""
    return load_fixture("sample_analysis_output.json")


@pytest.fixture()
def tmp_cache_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the cache at a throwaway per-test database file."""
    db = tmp_path / "test_cache.db"
    monkeypatch.setattr("backend.src.cache.CACHE_DB_PATH", str(db))
    return db


@pytest.fixture()
def base_state() -> dict:
    """Minimal AgentState-shaped dict for node tests."""
    return {
        "message": "top insulated water bottles",
        "intent": "search",
        "keywords": ["insulated water bottle"],
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
