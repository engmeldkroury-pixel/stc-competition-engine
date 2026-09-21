from app.models import TradingViewWebhook
from app.signals import (
    factors_from_tradingview,
    historical_regime_from_tradingview,
    short_term_score_from_tradingview,
)


def _payload(**overrides):
    data = {
        "event_id": "evt-history",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T12:00:00Z",
        "open": 4300.0,
        "high": 4320.0,
        "low": 4290.0,
        "close": 4310.0,
        "volume": 1000.0,
        "ema20": 4305.0,
        "ema50": 4290.0,
        "rsi14": 62.0,
        "atr14": 12.0,
        "macd": 5.0,
        "macd_signal": 2.0,
        "volume_ratio": 1.7,
    }
    data.update(overrides)
    return TradingViewWebhook.model_validate(data)


def test_history_is_optional_for_backward_compatibility():
    p = _payload()
    assert historical_regime_from_tradingview(p) is None
    assert factors_from_tradingview(p) == short_term_score_from_tradingview(p)


def test_one_year_daily_regime_materially_changes_blended_technical_score():
    p = _payload(
        history_timeframe="1D",
        history_time="2026-09-20T00:00:00Z",
        history_close=4310.0,
        history_ema50=4400.0,
        history_ema200=4500.0,
        history_rsi14=40.0,
        history_atr14=70.0,
        history_high_252=4700.0,
        history_low_252=3900.0,
        history_momentum_20=-0.04,
        history_momentum_63=-0.08,
        history_momentum_126=-0.12,
        history_momentum_252=-0.18,
        history_volatility_20=0.02,
    )
    short_term = short_term_score_from_tradingview(p)
    historical = historical_regime_from_tradingview(p)
    blended = factors_from_tradingview(p)

    assert short_term > 0
    assert historical is not None and historical < 0
    assert blended < short_term


def test_bullish_one_year_regime_scores_positive():
    p = _payload(
        history_timeframe="1D",
        history_time="2026-09-20T00:00:00Z",
        history_close=4600.0,
        history_ema50=4400.0,
        history_ema200=4000.0,
        history_rsi14=65.0,
        history_atr14=70.0,
        history_high_252=4700.0,
        history_low_252=3000.0,
        history_momentum_20=0.03,
        history_momentum_63=0.08,
        history_momentum_126=0.20,
        history_momentum_252=0.45,
        history_volatility_20=0.02,
    )
    assert historical_regime_from_tradingview(p) is not None
    assert historical_regime_from_tradingview(p) > 0.5
