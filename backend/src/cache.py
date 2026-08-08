"""
cache.py — SQLite TTL cache for SerpApi responses (Phase 1a).

Goals: cut redundant SerpApi calls (cost) and latency for repeated queries.
Product details are cached for 24h by default (price/ratings drift slowly),
search results for 1h (ranking/sponsorship shifts faster).

The cache must never break the pipeline: any failure degrades to a cache miss
logged as a warning, and the caller simply calls SerpApi as before.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path

from backend.src.config import CACHE_DB_PATH

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    expires_at REAL NOT NULL
)
"""


def _connect() -> sqlite3.Connection:
    Path(CACHE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.execute(_SCHEMA)
    return conn


def get_cached(key: str) -> dict | None:
    """Return the cached payload for `key`, or None on miss/expiry/any error."""
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
            ).fetchone()
            if row is None:
                return None
            value, expires_at = row
            if expires_at < time.time():
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None
            return json.loads(value)
    except (sqlite3.Error, json.JSONDecodeError, OSError) as exc:
        logger.warning("Cache get failed for key %r: %s", key, exc)
        return None


def set_cached(key: str, value: dict, ttl_seconds: int) -> None:
    """Store `value` under `key` with a TTL. Failures are logged, never raised."""
    try:
        with _connect() as conn:
            # Opportunistic cleanup of expired rows to bound DB size
            conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), time.time() + ttl_seconds),
            )
    except (sqlite3.Error, TypeError, OSError) as exc:
        logger.warning("Cache set failed for key %r: %s", key, exc)
