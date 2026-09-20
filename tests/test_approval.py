from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import storage
from app.approval import build_approval_envelope, market_state_hash, revalidate_envelope


def test_dynamic_validity_depends_on_timeframe():
    base = {"competition_id":"capital-africa-sep-2026","symbol":"CAPITALCOM:XAUUSD","close":4000,"atr14":20,"ema20":3990,"ema50":3980,"rsi14":60,"macd":2,"macd_signal":1}
    e5 = build_approval_envelope({**base, "timeframe":"5"}, 0.7)
    e60 = build_approval_envelope({**base, "timeframe":"60"}, 0.7)
    assert e5["validity_minutes"] == 15
    assert e60["validity_minutes"] == 90


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
