from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_v09_health_and_readiness_contract():
    health = client.get("/health")
    assert health.status_code == 200
    body = health.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.9.0"
    assert body["human_approval_required"] is True

    readiness = client.get("/readiness")
    assert readiness.status_code == 200
    r = readiness.json()
    assert r["analysis_ready"] is True
    assert r["execution_mode"] == "manual_only"
    assert r["automatic_execution_available"] is False
    assert r["human_approval_required"] is True
    assert r["capital_symbols_total"] == 10
    assert r["capital_symbols_verified"] == 10
