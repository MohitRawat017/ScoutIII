"""rate_limit.py: sliding-window allow/deny behaviour (no network)."""

from __future__ import annotations

from backend.src import rate_limit


def setup_function():
    rate_limit.reset()


def test_allows_up_to_limit():
    assert all(rate_limit.is_allowed("1.1.1.1", 3) for _ in range(3))


def test_denies_beyond_limit():
    for _ in range(3):
        rate_limit.is_allowed("1.1.1.1", 3)
    assert not rate_limit.is_allowed("1.1.1.1", 3)


def test_keys_are_independent():
    rate_limit.is_allowed("1.1.1.1", 1)
    assert not rate_limit.is_allowed("1.1.1.1", 1)
    assert rate_limit.is_allowed("2.2.2.2", 1)


def test_retry_after_is_positive_when_limited():
    rate_limit.is_allowed("1.1.1.1", 1)
    rate_limit.is_allowed("1.1.1.1", 1)
    assert rate_limit.retry_after("1.1.1.1") > 0
