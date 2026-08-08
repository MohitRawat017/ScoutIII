"""api.py: request validation and rate-limit enforcement (graph never invoked).

These hit the HTTP layer directly; both rejection paths return before any
agent/LLM work happens, so no mocks are needed.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_chat_sync_rejects_empty_message():
    resp = TestClient(app).post("/api/v1/chat/sync", json={"message": "   "})

    assert resp.status_code == 400


def test_chat_sync_returns_429_when_over_limit(monkeypatch):
    import backend.src.api as api
    from backend.src import rate_limit

    rate_limit.reset()
    monkeypatch.setattr(api, "RATE_LIMIT_PER_MINUTE", 0)  # deny everything

    resp = TestClient(app).post("/api/v1/chat/sync", json={"message": "yoga mats"})

    assert resp.status_code == 429
    assert "rate limit" in resp.json()["detail"]["error"].lower()
    assert resp.json()["detail"]["retry_after_seconds"] >= 0


def test_chat_sync_returns_duration_ms_and_usage(monkeypatch):
    import backend.src.api as api_mod

    class _FakeGraph:
        async def ainvoke(self, state: dict) -> dict:
            assert state["request_id"]  # api.py stamps a uuid per request
            return {
                "response": {
                    "answer": "ok",
                    "warnings": [],
                    "usage": {"estimated_cost_usd": 0.001},
                }
            }

    monkeypatch.setattr(api_mod, "agent_graph", _FakeGraph())

    resp = TestClient(app).post("/api/v1/chat/sync", json={"message": "yoga mats"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "ok"
    assert body["usage"]["estimated_cost_usd"] == 0.001
    assert "duration_ms" in body
