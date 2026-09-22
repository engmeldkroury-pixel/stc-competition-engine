from datetime import datetime, timedelta, timezone

from app.evidence_engine import EvidenceSummary
from app.historical_features import HistoricalFeatureSnapshot
from app.models import Bar
from app.mtf_research import (
    MTFContext,
    MTFGateParams,
    apply_mtf_gate,
    build_mtf_contexts,
    mtf_gate_grid,
)


UTC = timezone.utc


def _bar(ts: datetime, price: float = 100.0) -> Bar:
    return Bar(
        timestamp=ts,
        open=price,
        high=price + 1.0,
        low=price - 1.0,
        close=price + 0.25,
        volume=1000.0,
    )


def _snapshot(ts: datetime, score: float) -> HistoricalFeatureSnapshot:
    values = {
        "ema_9_20_50_100_200_alignment": score,
        "market_structure_trend": score,
        "trend_efficiency_ratio": score,
        "macd_histogram": score,
        "relative_strength_rank": score,
        "vwap_slope": score,
    }
    return HistoricalFeatureSnapshot(
        symbol="TEST:X",
        timeframe="60",
        timestamp=ts,
        values=values,
        observations=(),
    )


def _summary(score: float = 0.8) -> EvidenceSummary:
    return EvidenceSummary(
        score=score,
        agreement_ratio=0.85,
        independent_confirmations=6,
        hard_confirmations=2,
        family_scores={},
        family_weights_used={},
        conflicts=(),
        strongest_features=(),
    )


def test_higher_timeframe_bar_is_not_visible_before_its_close():
    start = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    hourly = [_bar(start + timedelta(hours=i), 100 + i) for i in range(260)]
    last = hourly[-1].timestamp

    # Previous confirmed hourly context is bearish, current still-forming hour is bullish.
    cache = {
        "60": {
            258: _snapshot(hourly[258].timestamp, -1.0),
            259: _snapshot(hourly[259].timestamp, 1.0),
        }
    }
    base = [
        _bar(last + timedelta(minutes=30)),  # closes at +45m: current 1h bar is NOT confirmed.
        _bar(last + timedelta(minutes=45)),  # closes at +60m: current 1h bar IS confirmed.
    ]

    contexts = build_mtf_contexts(
        symbol="TEST:X",
        base_bars=base,
        bars_by_timeframe={"60": hourly},
        snapshot_cache=cache,
    )

    assert contexts[0].source_indices["60"] == 258
    assert contexts[0].scores["60"] < 0
    assert contexts[1].source_indices["60"] == 259
    assert contexts[1].scores["60"] > 0


def test_strong_daily_conflict_vetoes_otherwise_aligned_long_signal():
    context = MTFContext(
        scores={
            "60": 0.8,
            "120": 0.7,
            "240": 0.8,
            "1D": -0.8,
        },
        weighted_score=0.30,
        available_frames=4,
        source_indices={"60": 1, "120": 1, "240": 1, "1D": 1},
    )
    gate = MTFGateParams(
        min_weighted_alignment=0.10,
        min_aligned_frames=3,
        max_strong_conflicts=1,
    )
    assert apply_mtf_gate((1, 0.8, _summary()), context, gate) is None


def test_aligned_mtf_context_keeps_signal_and_blends_evidence_score():
    context = MTFContext(
        scores={"60": 0.5, "120": 0.6, "240": 0.7, "1D": 0.8, "1M": 0.5},
        weighted_score=0.66,
        available_frames=5,
        source_indices={"60": 1, "120": 1, "240": 1, "1D": 1, "1M": 1},
    )
    gate = MTFGateParams(min_weighted_alignment=0.15, min_aligned_frames=3)
    result = apply_mtf_gate((1, 0.8, _summary()), context, gate)
    assert result is not None
    side, score, summary = result
    assert side == 1
    assert 0.66 < score < 0.8
    assert summary.score == score


def test_mtf_gate_grid_is_small_bounded_and_train_tunable():
    grid = mtf_gate_grid()
    assert len(grid) == 6
    assert {g.min_weighted_alignment for g in grid} == {0.05, 0.15, 0.25}
    assert {g.min_aligned_frames for g in grid} == {2, 3}
    assert all(g.min_available_frames == 3 for g in grid)
