import pytest

from app.models import FactorScores, SignalEvaluationRequest
from app.signals import evaluate


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
