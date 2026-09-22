from datetime import datetime, timezone

from app.event_decision import decide_bridge_event
from app.trade_plan import build_locked_trade_plan, deterministic_plan_id




def _confirm_history():
    return {
        "confirm_timeframe": "60",
        "confirm_time": "2026-09-21T09:00:00Z",
        "confirm_close": 3608.0,
        "confirm_ema20": 3600.0,
        "confirm_ema50": 3580.0,
        "confirm_ema200": 3400.0,
        "confirm_rsi14": 60.0,
        "confirm_atr14": 20.0,
        "confirm_macd": 8.0,
        "confirm_macd_signal": 4.0,
        "confirm_volume_ratio": 1.4,
        "trend_2h_time": "2026-09-21T08:00:00Z",
        "trend_2h_score": 0.86,
        "trend_4h_time": "2026-09-21T08:00:00Z",
        "trend_4h_score": 0.82,
        "trend_1m_time": "2026-09-01T00:00:00Z",
        "trend_1m_score": 0.72,
        "family_trend": 0.85,
        "family_momentum": 0.78,
        "family_volatility": 0.65,
        "family_volume": 0.72,
        "family_vwap": 0.70,
        "family_market_structure": 0.88,
        "family_smc_liquidity": 0.86,
        "family_price_action": 0.75,
        "family_microstructure": 0.68,
        "history_timeframe": "1D",
        "history_time": "2026-09-20T00:00:00Z",
        "history_close": 3610.0,
        "history_ema50": 3500.0,
        "history_ema200": 3300.0,
        "history_rsi14": 62.0,
        "history_atr14": 80.0,
        "history_high_252": 3650.0,
        "history_low_252": 2500.0,
        "history_momentum_20": 0.08,
        "history_momentum_63": 0.15,
        "history_momentum_126": 0.20,
        "history_momentum_252": 0.35,
        "history_volatility_20": 0.02,
    }


def _payload(**overrides):
    p = {
        "event_id": "evt-plan-1",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T10:00:00Z",
        "open": 3600.0,
        "high": 3614.0,
        "low": 3598.0,
        "close": 3610.0,
        "volume": 1000.0,
        "ema20": 3605.0,
        "ema50": 3590.0,
        "rsi14": 62.0,
        "atr14": 10.0,
        "macd": 5.0,
        "macd_signal": 2.0,
        "volume_ratio": 1.7,
        **_confirm_history(),
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
    b = decide_bridge_event("evt-plan-2", _payload(event_id="evt-plan-2", time="2026-09-21T10:15:00Z", close=3635.0, open=3626.0, high=3640.0, low=3624.0, ema20=3628.0, ema50=3605.0))
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
