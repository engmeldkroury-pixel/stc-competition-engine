from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .historical_features import HistoricalFeatureSnapshot
from .walkforward import (
    BacktestStats,
    SignalGate,
    TradeOutcome,
    WalkForwardValidation,
    materialize_feature_series,
    summarize_trades,
    walk_forward_validate,
)
from .strategy_lab import robust_trial_score


REGIMES = ("BULL_TREND", "BEAR_TREND", "RANGE", "TRANSITION")


@dataclass(frozen=True)
class RegimeSnapshot:
    regime: str
    direction_score: float
    trend_strength: float


@dataclass(frozen=True)
class RegimeBreakdown:
    regime: str
    trades: int
    stats: BacktestStats


@dataclass(frozen=True)
class RegimeValidationResult:
    regime: str
    validation: WalkForwardValidation
    robust_score: float
    test_retention: float
    forward_retention: float


def classify_market_regime(snapshot: HistoricalFeatureSnapshot) -> RegimeSnapshot:
    f = snapshot.values
    direction = (
        float(f.get("ema_9_20_50_100_200_alignment", 0.0)) * 0.30
        + float(f.get("linear_regression_slope", 0.0)) * 0.20
        + float(f.get("market_structure_trend", 0.0)) * 0.30
        + float(f.get("dmi_plus_minus", 0.0)) * 0.20
    )
    strength = max(
        abs(float(f.get("adx", 0.0))),
        abs(float(f.get("trend_efficiency_ratio", 0.0))),
        abs(float(f.get("market_structure_trend", 0.0))),
    )

    if strength >= 0.45 and direction >= 0.20:
        regime = "BULL_TREND"
    elif strength >= 0.45 and direction <= -0.20:
        regime = "BEAR_TREND"
    elif strength <= 0.30 and abs(direction) <= 0.25:
        regime = "RANGE"
    else:
        regime = "TRANSITION"

    return RegimeSnapshot(
        regime=regime,
        direction_score=max(-1.0, min(1.0, direction)),
        trend_strength=max(0.0, min(1.0, strength)),
    )


def trade_breakdown_by_regime(
    trades: list[TradeOutcome],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
) -> tuple[RegimeBreakdown, ...]:
    grouped: dict[str, list[TradeOutcome]] = {regime: [] for regime in REGIMES}
    for trade in trades:
        snapshot = snapshots.get(trade.signal_index)
        if snapshot is None:
            continue
        regime = classify_market_regime(snapshot).regime
        grouped[regime].append(trade)

    return tuple(
        RegimeBreakdown(
            regime=regime,
            trades=len(grouped[regime]),
            stats=summarize_trades(grouped[regime]),
        )
        for regime in REGIMES
    )


def make_regime_signal_gate(
    *,
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    allowed_regimes: tuple[str, ...],
) -> SignalGate:
    allowed = set(allowed_regimes)
    unknown = allowed - set(REGIMES)
    if unknown:
        raise ValueError("Unknown regimes: " + ",".join(sorted(unknown)))

    def gate(signal_index: int, side: int, score: float, summary) -> bool:
        del side, score, summary
        snapshot = snapshots.get(signal_index)
        if snapshot is None:
            return False
        return classify_market_regime(snapshot).regime in allowed

    return gate


def validate_strategy_by_regime(
    *,
    symbol: str,
    timeframe: str,
    bars,
    strategy_id: str,
    snapshots: Mapping[int, HistoricalFeatureSnapshot] | None = None,
) -> tuple[RegimeValidationResult, ...]:
    snapshots = snapshots or materialize_feature_series(symbol, timeframe, bars)
    baseline = walk_forward_validate(
        symbol,
        timeframe,
        bars,
        strategy_id,
        snapshots=snapshots,
    )

    results = []
    for regime in REGIMES:
        validation = walk_forward_validate(
            symbol,
            timeframe,
            bars,
            strategy_id,
            snapshots=snapshots,
            signal_gate=make_regime_signal_gate(
                snapshots=snapshots,
                allowed_regimes=(regime,),
            ),
        )
        test_retention = (
            validation.test_stats.trades / baseline.test_stats.trades
            if baseline.test_stats.trades
            else 0.0
        )
        forward_retention = (
            validation.forward_stats.trades / baseline.forward_stats.trades
            if baseline.forward_stats.trades
            else 0.0
        )
        results.append(
            RegimeValidationResult(
                regime=regime,
                validation=validation,
                robust_score=robust_trial_score(validation.trial),
                test_retention=test_retention,
                forward_retention=forward_retention,
            )
        )
    return tuple(results)
