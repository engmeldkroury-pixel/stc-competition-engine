from pathlib import Path

from app import storage
from app.event_processor import process_bridge_event


def reset_db(tmp_path: Path):
    storage.DB_PATH = tmp_path / "stc-test.db"
    storage.init_db()


def test_test_event_is_archived_without_signal(tmp_path):
    reset_db(tmp_path)
    result = process_bridge_event(
        "evt-test-1",
        {"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"},
    )
    assert result["status"] == "ingested_context"
    assert storage.summary()["signals"] == 0


def test_incomplete_valid_competition_event_is_context_only(tmp_path):
    reset_db(tmp_path)
    result = process_bridge_event(
        "evt-context-1",
        {"competition_id": "capital-africa-sep-2026", "symbol": "CAPITALCOM:XAUUSD", "time": "2026-09-20T07:00:00Z"},
    )
    assert result["status"] == "ingested_context"
    assert result["decision"]["reason"] == "insufficient_signal_payload"
    assert storage.summary()["signals"] == 0


def test_full_event_creates_one_deterministic_signal(tmp_path):
    reset_db(tmp_path)
    payload = {
        "event_id": "evt-full-1",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "5",
        "time": "2026-09-20T07:00:00Z",
        "open": 3600,
        "high": 3615,
        "low": 3595,
        "close": 3610,
        "volume": 1000,
        "ema20": 3605,
        "ema50": 3590,
        "rsi14": 62,
        "atr14": 10,
        "macd": 5,
        "macd_signal": 2,
        "volume_ratio": 1.7,
    }
    first = process_bridge_event("evt-full-1", payload)
    second = process_bridge_event("evt-full-1", payload)
    assert first["status"] == "analyzed"
    assert second["local_duplicate"] is True
    assert storage.summary()["signals"] == 1
    signal = storage.recent_signals(10)[0]
    assert signal["signal_id"].startswith("bridge-")
