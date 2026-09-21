from datetime import datetime, timezone

from app.event_decision import decide_bridge_event
from app.trade_plan import build_locked_trade_plan, deterministic_plan_id


def _payload(**overrides):
    p = {
        "event_id": "evt-plan-1",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T10:00:00Z",
        "open": 3600.0,
        "high": 3620.0,
        "low": 3590.0,
        "close": 3610.0,
        "volume": 1000.0,
        "ema20": 3605.0,
        "ema50": 3590.0,
        "rsi14": 62.0,
        "atr14": 10.0,
        "macd": 5.0,
        "macd_signal": 2.0,
        "volume_ratio": 1.7,
    }
    p.update(overrides)
    return p


def test_actionable_signal_gets_locked_trade_plan():
    result = decide_bridge_event("evt-plan-1", _payload())
    plan = result["decision"]["locked_trade_plan"]
    assert plan is not None
    assert plan["state"] == "CANDIDATE_LOCKED"
    assert plan["levels_locked"] is True
    assert plan["execution"] == "manual_only"
    assert plan["requires_human_approval"] is True
    assert plan["source_signal_id"] == result["decision"]["signal"]["signal_id"]
    assert plan["decision_timeframe"] == "15"


def test_same_event_and_signal_produce_same_plan_id():
    a = decide_bridge_event("evt-plan-1", _payload())
    b = decide_bridge_event("evt-plan-1", _payload())
    assert a["decision"]["locked_trade_plan"]["plan_id"] == b["decision"]["locked_trade_plan"]["plan_id"]


def test_later_bar_produces_new_plan_without_repricing_old_one():
    a = decide_bridge_event("evt-plan-1", _payload(close=3610.0))
    b = decide_bridge_event("evt-plan-2", _payload(event_id="evt-plan-2", time="2026-09-21T10:15:00Z", close=3635.0, high=3640.0))
    pa = a["decision"]["locked_trade_plan"]
    pb = b["decision"]["locked_trade_plan"]
    assert pa["plan_id"] != pb["plan_id"]
    assert pa["entry_min"] != pb["entry_min"]
    assert pa["levels_locked"] is True
    assert pb["levels_locked"] is True


def test_wait_signal_has_no_locked_trade_plan():
    weak = _payload(
        close=3600.0,
        ema20=3600.0,
        ema50=3600.0,
        rsi14=50.0,
        macd=1.0,
        macd_signal=1.0,
        volume_ratio=1.0,
    )
    result = decide_bridge_event("evt-plan-wait", weak)
    assert result["decision"]["signal"]["recommendation"] == "WAIT"
    assert result["decision"]["locked_trade_plan"] is None
