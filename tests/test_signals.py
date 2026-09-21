import pytest

from app.models import FactorScores, SignalEvaluationRequest, TradingViewWebhook
from app.signals import evaluate, liquidity_quality_from_tradingview, volatility_quality_from_tradingview


def test_strong_positive_signal_requires_human_approval():
    r = evaluate(
        SignalEvaluationRequest(
            competition_id="capital-africa-sep-2026",
            symbol="CAPITALCOM:XAUUSD",
            factors=FactorScores(
                technical=1.0,
                news=0.8,
                macro=0.7,
                volatility_quality=0.5,
                liquidity_quality=0.8,
            ),
        )
    )
    assert r.recommendation == "LONG"
    assert r.requires_human_approval is True


def test_disallowed_symbol_raises():
    with pytest.raises(ValueError):
        evaluate(
            SignalEvaluationRequest(
                competition_id="capital-africa-sep-2026",
                symbol="BAD:SYMBOL",
                factors=FactorScores(technical=1.0),
            )
        )



def _tv(**overrides):
    data = dict(
        event_id="evt-quality",
        event="bar_close",
        competition_id="capital-africa-sep-2026",
        symbol="CAPITALCOM:XAUUSD",
        timeframe="15",
        time="2026-09-21T18:00:00Z",
        open=4300,
        high=4310,
        low=4300,
        close=4308,
        volume=1000,
        ema20=4305,
        ema50=4290,
        rsi14=60,
        atr14=10,
        macd=4,
        macd_signal=2,
        volume_ratio=1.0,
    )
    data.update(overrides)
    return TradingViewWebhook.model_validate(data)


def test_volatility_quality_is_direction_symmetric_and_never_creates_direction():
    tv = _tv(high=4310, low=4300, atr14=10)
    assert volatility_quality_from_tradingview(tv, 0.8) == pytest.approx(0.5)
    assert volatility_quality_from_tradingview(tv, -0.8) == pytest.approx(-0.5)
    assert volatility_quality_from_tradingview(tv, 0.0) == 0.0


def test_extreme_volatility_dampens_existing_thesis():
    tv = _tv(high=4340, low=4300, atr14=10)
    # Raw quality is negative; directional alignment reduces either thesis.
    assert volatility_quality_from_tradingview(tv, 0.8) == pytest.approx(-0.8)
    assert volatility_quality_from_tradingview(tv, -0.8) == pytest.approx(0.8)


def test_liquidity_quality_boosts_or_dampens_without_directional_bias():
    liquid = _tv(volume=1000, volume_ratio=1.7)
    thin = _tv(volume=1000, volume_ratio=0.2)
    assert liquidity_quality_from_tradingview(liquid, 0.8) == pytest.approx(0.6)
    assert liquidity_quality_from_tradingview(liquid, -0.8) == pytest.approx(-0.6)
    assert liquidity_quality_from_tradingview(thin, 0.8) == pytest.approx(-0.5)
    assert liquidity_quality_from_tradingview(thin, -0.8) == pytest.approx(0.5)


def test_missing_volume_keeps_liquidity_quality_neutral():
    tv = _tv(volume=0, volume_ratio=0)
    assert liquidity_quality_from_tradingview(tv, 1.0) == 0.0
