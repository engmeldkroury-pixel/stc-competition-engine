from datetime import datetime, timezone

import pytest

from app.evidence_engine import EvidenceObservation
from app.historical_features import HistoricalFeatureSnapshot
from app.regime_research import (
    classify_market_regime,
    make_regime_signal_gate,
)


UTC = timezone.utc


def _snapshot(**values):
    base = {
        "ema_9_20_50_100_200_alignment": 0.0,
        "linear_regression_slope": 0.0,
        "market_structure_trend": 0.0,
        "dmi_plus_minus": 0.0,
        "adx": 0.0,
        "trend_efficiency_ratio": 0.0,
    }
    base.update(values)
    return HistoricalFeatureSnapshot(
        symbol="TEST:X",
        timeframe="15",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        values=base,
        observations=(),
    )


def test_regime_classifier_recognizes_bull_and_bear_trends():
    bull = _snapshot(
        ema_9_20_50_100_200_alignment=0.8,
        linear_regression_slope=0.7,
        market_structure_trend=0.9,
        dmi_plus_minus=0.7,
        adx=0.8,
        trend_efficiency_ratio=0.7,
    )
    bear = _snapshot(
        ema_9_20_50_100_200_alignment=-0.8,
        linear_regression_slope=-0.7,
        market_structure_trend=-0.9,
        dmi_plus_minus=-0.7,
        adx=-0.8,
        trend_efficiency_ratio=-0.7,
    )
    assert classify_market_regime(bull).regime == "BULL_TREND"
    assert classify_market_regime(bear).regime == "BEAR_TREND"


def test_regime_classifier_recognizes_range_when_trend_strength_is_low():
    snap = _snapshot(
        ema_9_20_50_100_200_alignment=0.05,
        linear_regression_slope=-0.05,
        market_structure_trend=0.10,
        dmi_plus_minus=0.02,
        adx=0.15,
        trend_efficiency_ratio=0.12,
    )
    result = classify_market_regime(snap)
    assert result.regime == "RANGE"
    assert result.trend_strength <= 0.30


def test_regime_classifier_marks_mixed_strength_as_transition():
    snap = _snapshot(
        ema_9_20_50_100_200_alignment=0.20,
        linear_regression_slope=-0.20,
        market_structure_trend=0.50,
        dmi_plus_minus=-0.20,
        adx=0.55,
        trend_efficiency_ratio=0.40,
    )
    assert classify_market_regime(snap).regime == "TRANSITION"


def test_regime_signal_gate_fails_closed_for_missing_snapshot_and_filters_regime():
    snapshots = {
        10: _snapshot(
            ema_9_20_50_100_200_alignment=0.8,
            market_structure_trend=0.8,
            dmi_plus_minus=0.8,
            adx=0.8,
            trend_efficiency_ratio=0.7,
        )
    }
    gate = make_regime_signal_gate(
        snapshots=snapshots,
        allowed_regimes=("BULL_TREND",),
    )
    assert gate(10, 1, 0.8, None) is True
    assert gate(11, 1, 0.8, None) is False


def test_regime_signal_gate_rejects_unknown_regime_name():
    with pytest.raises(ValueError):
        make_regime_signal_gate(
            snapshots={},
            allowed_regimes=("MAGIC_REGIME",),
        )
