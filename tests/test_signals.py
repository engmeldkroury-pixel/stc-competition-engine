import pytest

from app.models import FactorScores, SignalEvaluationRequest, TradingViewWebhook
from app.signals import competition_opportunity_assessment, evaluate, liquidity_quality_from_tradingview, setup_quality_score, volatility_quality_from_tradingview


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

def test_news_and_macro_are_context_not_primary_direction_drivers():
    r = evaluate(
        SignalEvaluationRequest(
            competition_id="capital-africa-sep-2026",
            symbol="CAPITALCOM:XAUUSD",
            factors=FactorScores(
                technical=-0.8,
                news=1.0,
                macro=1.0,
                volatility_quality=-0.4,
                liquidity_quality=-0.4,
            ),
        )
    )
    assert r.recommendation == "SHORT"
    assert r.composite_score < 0



def test_competition_opportunity_gate_accepts_majority_intraday_alignment():
    passed, failures = competition_opportunity_assessment(
        recommendation="LONG",
        composite_score=0.52,
        short_term_technical=0.75,
        historical_regime=0.10,
        blended_technical=0.62,
        volatility_quality=0.20,
        liquidity_quality=0.30,
        confirmation_score=0.55,
        trend_2h_score=0.60,
        trend_4h_score=0.10,
        trend_1m_score=0.20,
        family_evidence_score=0.45,
        family_agreement_ratio=0.67,
        family_aligned_count=6,
        family_conflict_count=2,
    )
    assert passed is True
    assert failures == []


def test_competition_opportunity_gate_blocks_weak_or_conflicted_setup():
    passed, failures = competition_opportunity_assessment(
        recommendation="LONG",
        composite_score=0.36,
        short_term_technical=0.40,
        historical_regime=-0.40,
        blended_technical=0.30,
        volatility_quality=-0.20,
        liquidity_quality=0.10,
        confirmation_score=0.20,
        trend_2h_score=-0.30,
        trend_4h_score=0.10,
        trend_1m_score=-0.60,
        family_evidence_score=0.10,
        family_agreement_ratio=0.44,
        family_aligned_count=3,
        family_conflict_count=5,
    )
    assert passed is False
    assert "intraday_majority_alignment" in failures
    assert "short_term_strength" in failures
    assert "historical_not_strongly_opposed" in failures


def test_competition_gate_blocks_strongly_opposed_monthly_regime():
    passed, failures = competition_opportunity_assessment(
        recommendation="SHORT",
        composite_score=-0.58,
        short_term_technical=-0.75,
        historical_regime=-1.00,
        blended_technical=-0.75,
        volatility_quality=-0.50,
        liquidity_quality=-0.50,
        confirmation_score=-0.70,
        trend_2h_score=-0.70,
        trend_4h_score=-0.70,
        trend_1m_score=0.60,
        family_evidence_score=-0.64,
        family_agreement_ratio=0.80,
        family_aligned_count=6,
        family_conflict_count=0,
    )
    assert passed is False
    assert "trend_1m_not_strongly_opposed" in failures


@pytest.mark.parametrize(
    "direction,short_term,confirmation,t2,t4,hist,m1,blend,vol,liq,family",
    [
        ("LONG", 0.65, 0.70, 0.15, 0.45, 1.00, 1.00, 0.75, 0.50, 0.50, 0.50),
        ("SHORT", -0.75, -0.85, -1.00, -0.60, -0.60, 0.60, -0.75, -0.50, -0.50, -0.61),
        ("SHORT", -0.75, -0.60, -0.55, -0.85, -1.00, 0.60, -0.75, -0.50, -0.50, -0.64),
    ],
)
def test_incident_shapes_do_not_reach_balanced_84_quality_floor(
    direction, short_term, confirmation, t2, t4, hist, m1, blend, vol, liq, family
):
    score = setup_quality_score(
        recommendation=direction,
        short_term_technical=short_term,
        confirmation_score=confirmation,
        trend_2h_score=t2,
        trend_4h_score=t4,
        historical_regime=hist,
        trend_1m_score=m1,
        blended_technical=blend,
        volatility_quality=vol,
        liquidity_quality=liq,
        family_evidence_score=family,
    )
    assert score < 84
