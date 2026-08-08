"""
instrumentation.py — Per-node timing decorator.

Applied at graph registration in `agent.py`, so nodes stay timing-unaware.
Works on both sync and async node functions.
"""

from __future__ import annotations

import functools
import inspect
import logging
import time

logger = logging.getLogger("scoutii.timing")


def timed_node(node_name: str):
    def decorator(fn):
        def _run_sync(state, *args, **kwargs):
            start = time.monotonic()
            result = fn(state, *args, **kwargs)
            _log_completion(state, start)
            return result

        async def _run_async(state, *args, **kwargs):
            start = time.monotonic()
            result = await fn(state, *args, **kwargs)
            _log_completion(state, start)
            return result

        def _log_completion(state, start: float) -> None:
            duration_ms = (time.monotonic() - start) * 1000
            request_id = state.get("request_id") if isinstance(state, dict) else None
            logger.info(
                "%s completed",
                node_name,
                extra={
                    "node": node_name,
                    "duration_ms": round(duration_ms, 1),
                    "request_id": request_id,
                },
            )

        wrapped = _run_async if inspect.iscoroutinefunction(fn) else _run_sync
        return functools.wraps(fn)(wrapped)

    return decorator
