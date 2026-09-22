from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from math import inf
from statistics import fmean
from typing import Mapping

from .analysis import ema, rsi
from .approval import timeframe_duration_minutes
from .historical_features import HistoricalFeatureSnapshot
from .models import Bar
from .strategy_lab import StrategyTrial, candidate_strategies, robust_trial_score
from .walkforward import (
    BacktestParams,
    BacktestStats,
    MatrixSelection,
    _signal,
    backtest_strategy,
    materialize_feature_series,
    parameter_grid,
)


UTC = timezone.utc

MTF_BASE_STRATEGIES = (
    "smc_structure_liquidity",
    "trend_pullback",
    "breakout_expansion",
    "vwap_intraday",
)

MTF_WEIGHTS: Mapping[str, float] = {
    "60": 0.18,
    "120": 0.18,
    "240": 0.24,
    "1D": 0.28,
    "1M": 0.12,
}


@dataclass(frozen=True)
class MTFContext:
    scores: Mapping[str, float]
    weighted_score: float
    available_frames: int
    source_indices: Mapping[str, int]


@dataclass(frozen=True)
class MTFGateParams:
    min_weighted_alignment: float
    min_aligned_frames: int
    min_available_frames: int = 3
    frame_alignment_threshold: float = 0.05
    max_strong_conflicts: int = 1


@dataclass(frozen=True)
class MTFWalkForwardValidation:
    trial: StrategyTrial
    base_strategy_id: str
    selected_params: BacktestParams
    gate_params: MTFGateParams
    train_stats: BacktestStats
    test_stats: BacktestStats
    forward_stats: BacktestStats


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _sign(value: float) -> float:
    return 1.0 if value > 1e-12 else -1.0 if value < -1e-12 else 0.0


def _snapshot_trend_score(snapshot: HistoricalFeatureSnapshot) -> float:
    f = snapshot.values
    components = (
        (0.30, float(f.get("ema_9_20_50_100_200_alignment", 0.0))),
        (0.22, float(f.get("market_structure_trend", 0.0))),
        (0.14, float(f.get("trend_efficiency_ratio", 0.0))),
        (0.12, float(f.get("macd_histogram", 0.0))),
        (0.12, float(f.get("relative_strength_rank", 0.0))),
        (0.10, float(f.get("vwap_slope", 0.0))),
    )
    return _clamp(sum(weight * _clamp(value) for weight, value in components))


def _monthly_trend_scores(monthly_bars: list[Bar]) -> tuple[list[datetime], list[float], list[int]]:
    confirm_times: list[datetime] = []
    scores: list[float] = []
    source_indices: list[int] = []
    closes = [bar.close for bar in monthly_bars]
    for i, bar in enumerate(monthly_bars):
        if i < 23:
            continue
        prefix = closes[: i + 1]
        e6 = ema(prefix, 6)
        e12 = ema(prefix, 12)
        e24 = ema(prefix, 24)
        ordering = fmean(
            (
                _sign(prefix[-1] - e6),
                _sign(e6 - e12),
                _sign(e12 - e24),
            )
        )
        r = rsi(prefix, 14)
        momentum = _clamp((r - 50.0) / 20.0)
        recent = prefix[-7:]
        path = sum(abs(recent[j] - recent[j - 1]) for j in range(1, len(recent)))
        efficiency = _clamp((recent[-1] - recent[0]) / path) if path > 0 else 0.0
        score = _clamp(0.50 * ordering + 0.30 * momentum + 0.20 * efficiency)

        ts = bar.timestamp.astimezone(UTC)
        if ts.month == 12:
            confirmed = datetime(ts.year + 1, 1, 1, tzinfo=UTC)
        else:
            confirmed = datetime(ts.year, ts.month + 1, 1, tzinfo=UTC)
        confirm_times.append(confirmed)
        scores.append(score)
        source_indices.append(i)
    return confirm_times, scores, source_indices


def _confirmed_snapshot_lookup(
    *,
    higher_timeframe: str,
    higher_bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
) -> tuple[list[datetime], list[float], list[int]]:
    duration = timeframe_duration_minutes(higher_timeframe)
    if duration <= 0:
        raise ValueError(f"Unsupported higher timeframe: {higher_timeframe}")
    confirm_times: list[datetime] = []
    scores: list[float] = []
    indices: list[int] = []
    for i, bar in enumerate(higher_bars):
        snap = snapshots.get(i)
        if snap is None:
            continue
        confirm_times.append(bar.timestamp + timedelta(minutes=duration))
        scores.append(_snapshot_trend_score(snap))
        indices.append(i)
    return confirm_times, scores, indices


def build_mtf_contexts(
    *,
    symbol: str,
    base_bars: list[Bar],
    bars_by_timeframe: Mapping[str, list[Bar]],
    snapshot_cache: dict[str, dict[int, HistoricalFeatureSnapshot]] | None = None,
    base_timeframe: str = "15",
) -> dict[int, MTFContext]:
    """Align only *confirmed* higher-timeframe evidence to every base bar.

    Higher bars are eligible only after their own close time. Monthly evidence
    is eligible only from the first UTC day of the following calendar month.
    The function therefore never reads a higher-timeframe bar that was still
    forming at the base signal close.
    """
    cache = snapshot_cache if snapshot_cache is not None else {}
    sources: dict[str, tuple[list[datetime], list[float], list[int]]] = {}

    for timeframe in ("60", "120", "240", "1D"):
        bars = list(bars_by_timeframe.get(timeframe) or [])
        if len(bars) < 260:
            continue
        snapshots = cache.get(timeframe)
        if snapshots is None:
            snapshots = materialize_feature_series(symbol, timeframe, bars)
            cache[timeframe] = snapshots
        sources[timeframe] = _confirmed_snapshot_lookup(
            higher_timeframe=timeframe,
            higher_bars=bars,
            snapshots=snapshots,
        )

    monthly = list(bars_by_timeframe.get("1M") or [])
    if len(monthly) >= 24:
        sources["1M"] = _monthly_trend_scores(monthly)

    base_duration = timeframe_duration_minutes(base_timeframe)
    if base_duration <= 0:
        raise ValueError(f"Unsupported base timeframe: {base_timeframe}")

    contexts: dict[int, MTFContext] = {}
    for i, bar in enumerate(base_bars):
        base_close = bar.timestamp + timedelta(minutes=base_duration)
        frame_scores: dict[str, float] = {}
        frame_indices: dict[str, int] = {}
        weighted = 0.0
        total_weight = 0.0

        for timeframe, (confirm_times, scores, source_indices) in sources.items():
            pos = bisect_right(confirm_times, base_close) - 1
            if pos < 0:
                continue
            score = scores[pos]
            frame_scores[timeframe] = score
            frame_indices[timeframe] = source_indices[pos]
            weight = MTF_WEIGHTS[timeframe]
            weighted += score * weight
            total_weight += weight

        if not frame_scores:
            continue
        contexts[i] = MTFContext(
            scores=frame_scores,
            weighted_score=_clamp(weighted / total_weight) if total_weight > 0 else 0.0,
            available_frames=len(frame_scores),
            source_indices=frame_indices,
        )
    return contexts


def apply_mtf_gate(
    base_signal: tuple[int, float, object] | None,
    context: MTFContext | None,
    gate: MTFGateParams,
):
    if base_signal is None or context is None:
        return None
    side, base_score, summary = base_signal
    if context.available_frames < gate.min_available_frames:
        return None

    aligned = 0
    strong_conflicts = 0
    for score in context.scores.values():
        side_score = side * score
        if side_score >= gate.frame_alignment_threshold:
            aligned += 1
        if side_score <= -0.45:
            strong_conflicts += 1

    weighted_alignment = side * context.weighted_score
    if weighted_alignment < gate.min_weighted_alignment:
        return None
    if aligned < gate.min_aligned_frames:
        return None
    if strong_conflicts > gate.max_strong_conflicts:
        return None

    # A strong 1D/month conflict is a hard veto even if shorter frames agree.
    for key in ("1D", "1M"):
        if key in context.scores and side * context.scores[key] <= -0.55:
            return None

    combined = _clamp(0.65 * float(base_score) + 0.35 * context.weighted_score)
    if side * combined <= 0:
        return None
    return side, combined, replace(summary, score=combined)


def mtf_gate_grid() -> tuple[MTFGateParams, ...]:
    return tuple(
        MTFGateParams(
            min_weighted_alignment=alignment,
            min_aligned_frames=min_frames,
        )
        for alignment in (0.05, 0.15, 0.25)
        for min_frames in (2, 3)
    )


def _objective(stats: BacktestStats) -> float:
    if stats.trades < 12:
        return -inf
    return (
        stats.expectancy_r * 25.0
        + min(stats.profit_factor, 3.0) * 3.0
        + stats.win_rate * 3.0
        - stats.max_drawdown_r * 0.35
    )


def _evaluator(contexts: Mapping[int, MTFContext], gate: MTFGateParams):
    def evaluate(index, strategy_id, snapshot, params):
        base = _signal(strategy_id, snapshot, params)
        return apply_mtf_gate(base, contexts.get(index), gate)
    return evaluate


def _segment_stability(
    *,
    symbol: str,
    bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    base_strategy_id: str,
    params: BacktestParams,
    gate: MTFGateParams,
    contexts: Mapping[int, MTFContext],
    start: int,
    end: int,
) -> float:
    width = max(1, (end - start) // 3)
    positive = 0
    used = 0
    evaluator = _evaluator(contexts, gate)
    for part in range(3):
        a = start + part * width
        b = end if part == 2 else min(end, a + width)
        _, stats = backtest_strategy(
            symbol,
            "15",
            bars,
            snapshots,
            base_strategy_id,
            params,
            start_index=a,
            end_index=b,
            signal_evaluator=evaluator,
        )
        if stats.trades >= 3:
            used += 1
            if stats.expectancy_r >= 0 and stats.profit_factor >= 1.0:
                positive += 1
    return 0.0 if used == 0 else positive / used


def walk_forward_validate_mtf(
    *,
    symbol: str,
    bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    contexts: Mapping[int, MTFContext],
    base_strategy_id: str,
) -> MTFWalkForwardValidation:
    if len(bars) < 900:
        raise ValueError("Need at least 900 15m bars for MTF walk-forward validation")

    n = len(bars)
    train_end = max(520, int(n * 0.58))
    test_end = max(train_end + 120, int(n * 0.82))
    test_end = min(test_end, n - 80)

    candidates: list[
        tuple[float, BacktestParams, MTFGateParams, BacktestStats]
    ] = []
    for params in parameter_grid("15"):
        for gate in mtf_gate_grid():
            _, stats = backtest_strategy(
                symbol,
                "15",
                bars,
                snapshots,
                base_strategy_id,
                params,
                start_index=260,
                end_index=train_end,
                signal_evaluator=_evaluator(contexts, gate),
            )
            candidates.append((_objective(stats), params, gate, stats))

    candidates.sort(key=lambda item: item[0], reverse=True)
    if not candidates or candidates[0][0] == -inf:
        best_params = parameter_grid("15")[0]
        best_gate = mtf_gate_grid()[0]
        train_stats = BacktestStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    else:
        _, best_params, best_gate, train_stats = candidates[0]

    evaluator = _evaluator(contexts, best_gate)
    _, test_stats = backtest_strategy(
        symbol,
        "15",
        bars,
        snapshots,
        base_strategy_id,
        best_params,
        start_index=train_end,
        end_index=test_end,
        signal_evaluator=evaluator,
    )
    _, forward_stats = backtest_strategy(
        symbol,
        "15",
        bars,
        snapshots,
        base_strategy_id,
        best_params,
        start_index=test_end,
        end_index=n - 1,
        signal_evaluator=evaluator,
    )

    valid = [row for row in candidates if row[3].trades >= 8]
    top = valid[: max(3, len(valid) // 4)] if valid else []
    parameter_stability = (
        sum(row[3].expectancy_r > 0 and row[3].profit_factor >= 1.0 for row in top)
        / len(top)
        if top
        else 0.0
    )
    regime_stability = _segment_stability(
        symbol=symbol,
        bars=bars,
        snapshots=snapshots,
        base_strategy_id=base_strategy_id,
        params=best_params,
        gate=best_gate,
        contexts=contexts,
        start=train_end,
        end=test_end,
    )

    trial = StrategyTrial(
        strategy_id=f"mtf_{base_strategy_id}",
        symbol=symbol,
        timeframe="15",
        train_trades=train_stats.trades,
        test_trades=test_stats.trades,
        forward_trades=forward_stats.trades,
        train_expectancy_r=train_stats.expectancy_r,
        test_expectancy_r=test_stats.expectancy_r,
        forward_expectancy_r=forward_stats.expectancy_r if forward_stats.trades else None,
        test_profit_factor=test_stats.profit_factor,
        forward_profit_factor=forward_stats.profit_factor if forward_stats.trades else None,
        test_win_rate=test_stats.win_rate,
        max_drawdown_r=max(test_stats.max_drawdown_r, forward_stats.max_drawdown_r),
        parameter_stability=parameter_stability,
        regime_stability=regime_stability,
    )
    return MTFWalkForwardValidation(
        trial=trial,
        base_strategy_id=base_strategy_id,
        selected_params=best_params,
        gate_params=best_gate,
        train_stats=train_stats,
        test_stats=test_stats,
        forward_stats=forward_stats,
    )


def mtf_strategy_matrix(
    *,
    symbol: str,
    asset_class: str,
    bars_by_timeframe: Mapping[str, list[Bar]],
    snapshot_cache: dict[str, dict[int, HistoricalFeatureSnapshot]] | None = None,
) -> tuple[list[MTFWalkForwardValidation], MatrixSelection]:
    bars = list(bars_by_timeframe.get("15") or [])
    if len(bars) < 900:
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe="15",
            robust_score=None,
            trial_count=0,
            reason="Insufficient 15m history for MTF research.",
        )

    cache = snapshot_cache if snapshot_cache is not None else {}
    snapshots = cache.get("15")
    if snapshots is None:
        snapshots = materialize_feature_series(symbol, "15", bars)
        cache["15"] = snapshots

    contexts = build_mtf_contexts(
        symbol=symbol,
        base_bars=bars,
        bars_by_timeframe=bars_by_timeframe,
        snapshot_cache=cache,
        base_timeframe="15",
    )
    if not contexts:
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe="15",
            robust_score=None,
            trial_count=0,
            reason="No confirmed higher-timeframe context available.",
        )

    allowed = {
        spec.strategy_id
        for spec in candidate_strategies(asset_class, "15")
    }
    base_strategies = [
        strategy for strategy in MTF_BASE_STRATEGIES if strategy in allowed
    ]
    results = [
        walk_forward_validate_mtf(
            symbol=symbol,
            bars=bars,
            snapshots=snapshots,
            contexts=contexts,
            base_strategy_id=strategy,
        )
        for strategy in base_strategies
    ]

    scored = [
        (robust_trial_score(row.trial), row)
        for row in results
        if robust_trial_score(row.trial) > 0
    ]
    if not scored:
        return results, MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe="15",
            robust_score=None,
            trial_count=len(results),
            reason="No MTF-confirmed 15m strategy passed unchanged OOS/forward gates.",
        )

    score, best = max(scored, key=lambda item: item[0])
    return results, MatrixSelection(
        status="VALIDATED",
        symbol=symbol,
        strategy_id=best.trial.strategy_id,
        timeframe="15",
        robust_score=score,
        trial_count=len(results),
        reason="Selected from MTF-confirmed 15m variants by unchanged OOS/forward robustness gates.",
    )
