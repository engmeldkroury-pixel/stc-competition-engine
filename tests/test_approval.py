from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import storage
from app.approval import (
    build_approval_envelope,
    entry_price_bounds,
    market_state_hash,
    revalidate_envelope,
    source_bar_close_time,
    timeframe_duration_minutes,
)


def test_dynamic_validity_depends_on_timeframe():
    base = {"competition_id":"capital-africa-sep-2026","symbol":"CAPITALCOM:XAUUSD","close":4000,"atr14":20,"ema20":3990,"ema50":3980,"rsi14":60,"macd":2,"macd_signal":1}
    e5 = build_approval_envelope({**base, "timeframe":"5"}, 0.7)
    e60 = build_approval_envelope({**base, "timeframe":"60"}, 0.7)
    e120 = build_approval_envelope({**base, "timeframe":"120"}, 0.7)
    assert e5["validity_minutes"] == 15
    assert e60["validity_minutes"] == 90
    assert e120["validity_minutes"] == 180
    assert timeframe_duration_minutes("120") == 120


def test_revalidation_accepts_fresh_unchanged_state():
    p={"competition_id":"c","symbol":"s","timeframe":"5","close":100,"atr14":2,"ema20":101,"ema50":99,"rsi14":55,"macd":1,"macd_signal":0.5}
    e=build_approval_envelope(p,0.6)
    cur={"current_price":100.2,"current_signal_score":0.55,"current_market_state_hash":e["market_state_hash"],"current_rule_version":"stc-rule-v1","news_block":False,"volatility_ratio":1.0,"quote_freshness_verified":True,"market_open_verified":True,"kill_switch":False,"safe_mode":False}
    r=revalidate_envelope(e,cur)
    assert r["valid"] is True


def test_revalidation_blocks_stale_or_changed_state():
    p={"competition_id":"c","symbol":"s","timeframe":"5","close":100,"atr14":2,"ema20":101,"ema50":99,"rsi14":55,"macd":1,"macd_signal":0.5}
    e=build_approval_envelope(p,0.6)
    e["valid_until"]=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
    cur={"current_price":110,"current_signal_score":0.1,"current_market_state_hash":"changed","current_rule_version":"new","news_block":True,"volatility_ratio":2.0,"kill_switch":True,"safe_mode":True}
    r=revalidate_envelope(e,cur)
    assert r["valid"] is False
    assert "expired" in r["reasons"]
    assert "price_outside_envelope" in r["reasons"]
    assert "market_state_changed" in r["reasons"]
    assert "kill_switch_active" in r["reasons"]


def test_runtime_control_round_trip(tmp_path: Path):
    storage.DB_PATH=tmp_path/'approval.db'
    storage.init_db()
    x=storage.set_runtime_control(safe_mode=True, kill_switch=False, reason='test')
    assert x["safe_mode"] is True
    assert x["kill_switch"] is False


def test_revalidation_blocks_unverified_quote_freshness():
    p={"competition_id":"c","symbol":"s","timeframe":"15m","close":100,"atr14":1,"ema20":101,"ema50":99,"rsi14":55,"macd":1,"macd_signal":0.5}
    e=build_approval_envelope(p,0.6)
    cur={"current_price":100,"current_signal_score":0.6,"current_market_state_hash":e["market_state_hash"],"current_rule_version":"stc-rule-v1","news_block":False,"volatility_ratio":1.0,"quote_freshness_verified":False,"market_open_verified":True,"kill_switch":False,"safe_mode":False}
    r=revalidate_envelope(e,cur)
    assert r["valid"] is False
    assert "quote_freshness_unverified" in r["reasons"]


def test_revalidation_blocks_closed_or_unverified_market():
    p={"competition_id":"c","symbol":"s","timeframe":"15m","close":100,"atr14":1,"ema20":101,"ema50":99,"rsi14":55,"macd":1,"macd_signal":0.5}
    e=build_approval_envelope(p,0.6)
    cur={"current_price":100,"current_signal_score":0.6,"current_market_state_hash":e["market_state_hash"],"current_rule_version":"stc-rule-v1","news_block":False,"volatility_ratio":1.0,"quote_freshness_verified":True,"market_open_verified":False,"kill_switch":False,"safe_mode":False}
    r=revalidate_envelope(e,cur)
    assert r["valid"] is False
    assert "market_closed_or_unverified" in r["reasons"]



def test_validity_is_anchored_to_confirmed_bar_close_not_worker_clock():
    payload = {
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T20:30:00Z",
        "close": 4300,
        "atr14": 10,
        "ema20": 4290,
        "ema50": 4280,
        "rsi14": 60,
        "macd": 2,
        "macd_signal": 1,
    }
    close_time = source_bar_close_time(payload)
    assert close_time.isoformat() == "2026-09-21T20:45:00+00:00"

    envelope = build_approval_envelope(payload, 0.7)
    assert envelope["source_bar_time"] == "2026-09-21T20:30:00Z"
    assert envelope["source_bar_close_time"] == "2026-09-21T20:45:00+00:00"
    assert envelope["valid_until"] == "2026-09-21T21:15:00+00:00"



def test_entry_price_bounds_match_dynamic_approval_tolerance():
    low, high, pct = entry_price_bounds(100.0, 2.0)
    assert pct == 0.01
    assert low == 99.0
    assert high == 101.0

    low2, high2, pct2 = entry_price_bounds(100.0, 0.01)
    assert pct2 == 0.001
    assert low2 == 99.9
    assert high2 == 100.1


def test_two_hour_source_bar_close_time_is_explicit():
    payload = {
        "timeframe": "120",
        "time": "2026-09-22T08:00:00Z",
    }
    assert source_bar_close_time(payload).isoformat() == "2026-09-22T10:00:00+00:00"
