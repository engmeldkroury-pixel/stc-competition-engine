import json
from pathlib import Path


def test_crypto_spot_research_protocol_is_research_only():
    path = Path(__file__).parents[1] / "research_inputs" / "CRYPTO_SPOT_RESEARCH_PROTOCOL_v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["mode"] == "RESEARCH_ONLY"
    assert data["promotion"]["live_money"] is False
    assert data["promotion"]["paper_trading_required"] is True
    assert data["promotion"]["walk_forward_required"] is True
    assert "BTC" not in data["strategies"]
    assert "EMA" in data["strategies"]["trend"]
