"""
rate_limit.py — In-process sliding-window rate limiter (Phase 1a).

IP-based and in-memory per worker process. This is a placeholder until real
authentication lands (Phase 2c), at which point limiting moves to per-user
accounts. It exists to stop a single client (or a buggy retry loop) from
burning the shared SerpApi/Gemini quota.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

_WINDOW_SECONDS = 60.0
_hits: dict[str, deque[float]] = defaultdict(deque)


def is_allowed(client_key: str, limit_per_minute: int) -> bool:
    """Return True and record the hit if `client_key` is under its limit."""
    now = time.monotonic()
    window = _hits[client_key]
    while window and now - window[0] >= _WINDOW_SECONDS:
        window.popleft()
    if len(window) >= limit_per_minute:
        return False
    window.append(now)
    return True


def retry_after(client_key: str) -> int:
    """Seconds until the oldest hit leaves the window (for 429 responses)."""
    window = _hits.get(client_key)
    if not window:
        return 0
    return max(1, int(_WINDOW_SECONDS - (time.monotonic() - window[0])))


def reset() -> None:
    """Clear all limiter state (used by tests)."""
    _hits.clear()
