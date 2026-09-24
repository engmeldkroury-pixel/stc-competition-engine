from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_shadow_candidate_api_is_research_only():
    response = client.get("/research/shadow-candidates")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 16
    assert payload["live_authority"] is False
    assert payload["execution"] == "research_only"
    assert all(row["live_authority"] is False for row in payload["records"])


def test_shadow_candidate_api_filters_symbol():
    response = client.get("/research/shadow-candidates", params={"symbol": "CME_MINI:MJY1!"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 6
    assert {x["component_id"] for x in payload["records"]} == {"alphatrend", "waddah_attar_explosion", "squeeze_momentum_lazybear", "trendilo"}
    assert sum(x["component_id"] == "trendilo" for x in payload["records"]) == 3
    assert {x["timeframe"] for x in payload["records"] if x["component_id"] == "trendilo"} == {"5", "15", "30"}


def test_shadow_candidate_api_filters_new_wave2_btc_trendilo():
    response = client.get("/research/shadow-candidates", params={"symbol": "CAPITALCOM:BTCUSD"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 3
    rows = payload["records"]
    trendilo = [row for row in rows if row["component_id"] == "trendilo"]
    assert len(trendilo) == 1
    assert trendilo[0]["timeframe"] == "15"
    assert trendilo[0]["state"] == "SHADOW"
    assert trendilo[0]["live_authority"] is False
    assert {row["component_id"] for row in rows} == {
        "trendilo",
        "nadaraya_watson_endpoint_nonrepaint",
        "hull_suite",
    }
