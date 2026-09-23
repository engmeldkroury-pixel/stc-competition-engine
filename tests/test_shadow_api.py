from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_shadow_candidate_api_is_research_only():
    response = client.get("/research/shadow-candidates")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 6
    assert payload["live_authority"] is False
    assert payload["execution"] == "research_only"
    assert all(row["live_authority"] is False for row in payload["records"])


def test_shadow_candidate_api_filters_symbol():
    response = client.get("/research/shadow-candidates", params={"symbol": "CME_MINI:MJY1!"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert {x["component_id"] for x in payload["records"]} == {"alphatrend", "waddah_attar_explosion"}
