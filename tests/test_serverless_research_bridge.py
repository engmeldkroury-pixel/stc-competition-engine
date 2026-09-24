from __future__ import annotations

from fastapi.testclient import TestClient

from api.index import app


client = TestClient(app)
AUTH = {"Authorization": "Bearer test-trigger"}


def test_serverless_general_lab_plan_is_protected_and_research_only(monkeypatch):
    monkeypatch.setenv("STC_TRIGGER_TOKEN", "test-trigger")
    unauthorized = client.post("/research/general-lab/plan", json={"symbols": ["CAPITALCOM:XAUUSD"]})
    assert unauthorized.status_code == 401

    response = client.post(
        "/research/general-lab/plan",
        json={"symbols": ["CAPITALCOM:XAUUSD"]},
        headers=AUTH,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["live_authority"] is False
    assert payload["execution"] == "research_only"
    assert payload["symbols_requested"] == ["CAPITALCOM:XAUUSD"]


def test_serverless_shadow_candidates_are_protected(monkeypatch):
    monkeypatch.setenv("STC_TRIGGER_TOKEN", "test-trigger")
    response = client.get("/research/shadow-candidates", headers=AUTH)
    assert response.status_code == 200
    payload = response.json()
    assert payload["live_authority"] is False
    assert payload["execution"] == "research_only"
    assert payload["count"] >= 6
