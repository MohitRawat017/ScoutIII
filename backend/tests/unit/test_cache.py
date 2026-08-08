"""cache.py: roundtrip, expiry, miss, and corruption resilience (no network)."""

from __future__ import annotations

import sqlite3


def test_get_returns_none_on_miss(tmp_cache_db):
    from backend.src import cache

    assert cache.get_cached("product:NOPE") is None


def test_set_then_get_roundtrip(tmp_cache_db):
    from backend.src import cache

    cache.set_cached("product:B001", {"asin": "B001"}, 60)
    assert cache.get_cached("product:B001") == {"asin": "B001"}


def test_expired_entry_returns_none(tmp_cache_db):
    from backend.src import cache

    cache.set_cached("k", {"v": 1}, -1)  # TTL in the past → already expired
    assert cache.get_cached("k") is None


def test_corrupt_row_degrades_to_miss(tmp_cache_db):
    from backend.src import cache

    # Seed first so the schema exists, then inject a corrupt row directly
    cache.set_cached("seed", {"ok": True}, 60)
    conn = sqlite3.connect(str(tmp_cache_db))
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, value, expires_at) "
        "VALUES ('bad', '{notjson', 99999999999)"
    )
    conn.commit()
    conn.close()

    assert cache.get_cached("bad") is None
