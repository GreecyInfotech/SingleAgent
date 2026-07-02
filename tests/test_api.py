from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"


def test_chat() -> None:
    res = client.post(
        "/api/v1/chat",
        json={"message": "place order for sku 1", "session_id": "abc"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body
    assert body["route"] == "order_agent"
