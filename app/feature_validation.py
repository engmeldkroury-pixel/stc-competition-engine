from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Mapping

from .analysis import atr
from .evidence_engine import reliability_for_feature
from .historical_features import HistoricalFeatureSnapshot
from .models import Bar
from .weight_calibration import CalibratedWeight, FeaturePerformance, calibrate_feature_reliability


@dataclass(frozen=True)
class FeatureValidation:
    feature: str
    symbol: str
    strategy_id: str
    timeframe: str
    test_performance: FeaturePerformance
    forward_performance: FeaturePerformance
    calibrated_weight: CalibratedWeight
    forward_consistent: bool
    deployable: bool
    reason: str


def _segment_performance(
    *,
    feature: str,
    symbol: str,
    strategy_id: str,
    timeframe: str,
    bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    start_index: int,
    end_index: int,
    horizon_bars: int,
    activation_threshold: float,
) -> FeaturePerformance:
    outcomes: list[float] = []
    hits = 0
    for i in range(max(260, start_index), min(end_index, len(bars) - horizon_bars - 1)):
        snap = snapshots.get(i)
        if snap is None:
            continue
        direction = float(snap.values.get(feature, 0.0))
        if abs(direction) < activation_threshold:
            continue
        local_atr = max(atr(bars[: i + 1], 14), abs(bars[i].close) * 1e-8, 1e-9)
        future = bars[i + horizon_bars].close
        signed_r = (1.0 if direction > 0 else -1.0) * (future - bars[i].close) / local_atr
        outcomes.append(signed_r)
        if signed_r > 0:
            hits += 1

    if outcomes:
        positive = sum(x for x in outcomes if x > 0)
        negative = abs(sum(x for x in outcomes if x < 0))
        pf = 99.0 if negative <= 1e-12 and positive > 0 else positive / negative if negative > 0 else 0.0
        avg = fmean(outcomes)
    else:
        pf = 0.0
        avg = 0.0

    thirds: list[bool] = []
    width = max(1, (end_index - start_index) // 3)
    for part in range(3):
        a = start_index + part * width
        b = end_index if part == 2 else min(end_index, a + width)
        seg: list[float] = []
        for i in range(max(260, a), min(b, len(bars) - horizon_bars - 1)):
            snap = snapshots.get(i)
            if snap is None:
                continue
            direction = float(snap.values.get(feature, 0.0))
            if abs(direction) < activation_threshold:
                continue
            local_atr = max(atr(bars[: i + 1], 14), abs(bars[i].close) * 1e-8, 1e-9)
            future = bars[i + horizon_bars].close
            seg.append((1.0 if direction > 0 else -1.0) * (future - bars[i].close) / local_atr)
        if len(seg) >= 3:
            thirds.append(fmean(seg) > 0)

    stability = sum(thirds) / len(thirds) if thirds else 0.0
    return FeaturePerformance(
        feature=feature,
        symbol=symbol,
        strategy_id=strategy_id,
        timeframe=timeframe,
        sample_size=len(outcomes),
        directional_hits=hits,
        average_forward_r=avg,
        profit_factor_when_present=pf,
        regime_stability=stability,
    )


def validate_feature_weight(
    *,
    feature: str,
    symbol: str,
    strategy_id: str,
    timeframe: str,
    bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    test_start: int,
    test_end: int,
    forward_end: int,
    horizon_bars: int = 8,
    activation_threshold: float = 0.45,
    min_test_samples: int = 40,
    min_forward_samples: int = 15,
) -> FeatureValidation:
    test = _segment_performance(
        feature=feature,
        symbol=symbol,
        strategy_id=strategy_id,
        timeframe=timeframe,
        bars=bars,
        snapshots=snapshots,
        start_index=test_start,
        end_index=test_end,
        horizon_bars=horizon_bars,
        activation_threshold=activation_threshold,
    )
    forward = _segment_performance(
        feature=feature,
        symbol=symbol,
        strategy_id=strategy_id,
        timeframe=timeframe,
        bars=bars,
        snapshots=snapshots,
        start_index=test_end,
        end_index=forward_end,
        horizon_bars=horizon_bars,
        activation_threshold=activation_threshold,
    )

    calibrated = calibrate_feature_reliability(
        test,
        prior_reliability=reliability_for_feature(feature),
    )
    forward_consistent = (
        forward.sample_size >= min_forward_samples
        and forward.average_forward_r > 0
        and forward.profit_factor_when_present >= 1.05
    )
    deployable = (
        test.sample_size >= min_test_samples
        and test.average_forward_r > 0
        and test.profit_factor_when_present >= 1.10
        and test.regime_stability >= 0.60
        and forward_consistent
    )
    if test.sample_size < min_test_samples:
        reason = "insufficient_out_of_sample_feature_occurrences"
    elif test.average_forward_r <= 0 or test.profit_factor_when_present < 1.10:
        reason = "feature_not_profitable_out_of_sample"
    elif test.regime_stability < 0.60:
        reason = "feature_unstable_across_test_regimes"
    elif not forward_consistent:
        reason = "feature_not_confirmed_in_forward_segment"
    else:
        reason = "validated_for_runtime_calibration"

    return FeatureValidation(
        feature=feature,
        symbol=symbol,
        strategy_id=strategy_id,
        timeframe=timeframe,
        test_performance=test,
        forward_performance=forward,
        calibrated_weight=calibrated,
        forward_consistent=forward_consistent,
        deployable=deployable,
        reason=reason,
    )
