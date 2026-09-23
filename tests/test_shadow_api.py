from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_shadow_candidate_api_is_research_only():
    response = client.get("/research/shadow-candidates")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 12
    assert payload["live_authority"] is False
    assert payload["execution"] == "research_only"
    assert all(row["live_authority"] is False for row in payload["records"])


def test_shadow_candidate_api_filters_symbol():
    response = client.get("/research/shadow-candidates", params={"symbol": "CME_MINI:MJY1!"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 4
    assert {x["component_id"] for x in payload["records"]} == {"alphatrend", "waddah_attar_explosion", "squeeze_momentum_lazybear", "trendilo"}


def test_shadow_candidate_api_filters_new_wave2_btc_trendilo():
    response = client.get("/research/shadow-candidates", params={"symbol": "CAPITALCOM:BTCUSD"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    row = payload["records"][0]
    assert row["component_id"] == "trendilo"
    assert row["state"] == "SHADOW"
    assert row["live_authority"] is False
