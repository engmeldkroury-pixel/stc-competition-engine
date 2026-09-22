
from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Mapping

from .analysis import atr
from .evidence_engine import EvidenceSummary, aggregate_evidence
from .historical_features import HistoricalFeatureSnapshot, extract_feature_snapshot
from .models import Bar
from .strategy_lab import StrategyTrial, candidate_strategies, robust_trial_score
from .trade_plan import LIVE_PLAN_FINAL_TARGET_RR, LIVE_PLAN_STOP_ATR_MULTIPLE


@dataclass(frozen=True)
class BacktestParams:
    threshold: float
    stop_atr: float
    target_r: float
    max_hold_bars: int
    min_agreement: float = 0.62
    min_independent_confirmations: int = 4
    min_hard_confirmations: int = 1
    round_turn_cost_r: float = 0.02


@dataclass(frozen=True)
class TradeOutcome:
    strategy_id: str
    signal_index: int
    entry_index: int
    exit_index: int
    side: str
    entry_price: float
    exit_price: float
    initial_stop: float
    target: float
    result_r: float
    exit_reason: str
    evidence_score: float
    agreement_ratio: float


@dataclass(frozen=True)
class BacktestStats:
    trades: int
    wins: int
    losses: int
    win_rate: float
    total_r: float
    expectancy_r: float
    profit_factor: float
    max_drawdown_r: float


@dataclass(frozen=True)
class WalkForwardValidation:
    trial: StrategyTrial
    selected_params: BacktestParams
    train_stats: BacktestStats
    test_stats: BacktestStats
    forward_stats: BacktestStats


@dataclass(frozen=True)
class MatrixSelection:
    status: str
    symbol: str
    strategy_id: str | None
    timeframe: str | None
    robust_score: float | None
    trial_count: int
    reason: str


def materialize_feature_series(
    symbol: str,
    timeframe: str,
    bars: list[Bar],
    *,
    warmup: int = 260,
) -> dict[int, HistoricalFeatureSnapshot]:
    if len(bars) <= warmup:
        raise ValueError("Not enough bars after feature warmup")
    return {
        i: extract_feature_snapshot(symbol, timeframe, bars[: i + 1])
        for i in range(warmup - 1, len(bars))
    }


def _strategy_score(
    strategy_id: str,
    snapshot: HistoricalFeatureSnapshot,
) -> tuple[float, EvidenceSummary]:
    summary = aggregate_evidence(snapshot.observations, strategy_id=strategy_id)
    f = snapshot.values
    score = summary.score

    if strategy_id == "mean_reversion":
        trend_strength = abs(f["market_structure_trend"]) + abs(f["trend_efficiency_ratio"])
        if trend_strength > 0.85:
            return 0.0, summary
        score = _clamp(
            -0.45 * f["range_location"]
            -0.35 * f["vwap_band_location"]
            -0.20 * f["bollinger_percent_b"]
        )
    elif strategy_id == "range_rotation":
        if abs(f["market_structure_trend"]) > 0.45 or abs(f["adx"]) > 0.65:
            return 0.0, summary
        score = _clamp(
            -0.55 * f["range_location"]
            -0.25 * f["support_resistance_distance"]
            -0.20 * f["vwap_band_location"]
        )
    elif strategy_id == "smc_structure_liquidity":
        structural = max(
            abs(f["liquidity_sweep"]),
            abs(f["choch"]),
            abs(f["bos"]),
            abs(f["break_retest"]),
        )
        if structural < 0.55 or summary.hard_confirmations < 2:
            return 0.0, summary
    elif strategy_id == "breakout_expansion":
        trigger = max(abs(f["bos"]), abs(f["displacement_candle"]), abs(f["liquidity_void"]))
        if trigger < 0.55:
            return 0.0, summary
        score = _clamp(score * 0.75 + f["volume_ratio"] * 0.15 + f["true_range_percentile"] * 0.10)
    elif strategy_id == "volatility_squeeze":
        if abs(f["squeeze_state"]) < 0.10:
            return 0.0, summary
        score = _clamp(score * 0.70 + f["squeeze_state"] * 0.15 + f["volume_ratio"] * 0.15)
    elif strategy_id == "trend_pullback":
        if abs(f["trend_efficiency_ratio"]) < 0.18:
            return 0.0, summary
        if f["micro_pullback_depth"] * score < -0.10:
            return 0.0, summary
    elif strategy_id == "vwap_intraday":
        vwap_signal = max(abs(f["vwap_reclaim_reject"]), abs(f["session_vwap_distance"]))
        if vwap_signal < 0.25:
            return 0.0, summary
        score = _clamp(score * 0.70 + f["vwap_reclaim_reject"] * 0.20 + f["relative_volume"] * 0.10)
    elif strategy_id == "microtrend_scalp":
        if abs(f["spread_proxy"]) < 0.15 or abs(f["tick_activity_proxy"]) < 0.10:
            return 0.0, summary
        score = _clamp(
            score * 0.55
            + f["micro_breakout_persistence"] * 0.20
            + f["bar_speed"] * 0.15
            + f["tick_activity_proxy"] * 0.10
        )
    elif strategy_id == "momentum_continuation":
        momentum = (
            f["rsi_14"] + f["macd_histogram"] + f["roc"] + f["relative_strength_rank"]
        ) / 4.0
        score = _clamp(score * 0.65 + momentum * 0.35)

    return score, summary


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _signal(
    strategy_id: str,
    snapshot: HistoricalFeatureSnapshot,
    params: BacktestParams,
) -> tuple[int, float, EvidenceSummary] | None:
    score, summary = _strategy_score(strategy_id, snapshot)
    if abs(score) < params.threshold:
        return None
    if summary.agreement_ratio < params.min_agreement:
        return None
    if summary.independent_confirmations < params.min_independent_confirmations:
        return None
    if strategy_id in {"smc_structure_liquidity", "breakout_expansion"}:
        if summary.hard_confirmations < params.min_hard_confirmations:
            return None
    if len(summary.conflicts) >= 3:
        return None
    return (1 if score > 0 else -1, score, summary)


def backtest_strategy(
    symbol: str,
    timeframe: str,
    bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    strategy_id: str,
    params: BacktestParams,
    *,
    start_index: int,
    end_index: int,
) -> tuple[list[TradeOutcome], BacktestStats]:
    if start_index < 260:
        start_index = 260
    end_index = min(end_index, len(bars) - 1)
    trades: list[TradeOutcome] = []
    i = start_index
    while i < end_index - 1:
        snap = snapshots.get(i)
        if snap is None:
            i += 1
            continue
        signal = _signal(strategy_id, snap, params)
        if signal is None:
            i += 1
            continue

        side, score, summary = signal
        entry_i = i + 1
        entry = bars[entry_i].open
        local_atr = max(atr(bars[: i + 1], 14), abs(entry) * 1e-8, 1e-9)
        risk = params.stop_atr * local_atr
        stop = entry - side * risk
        target = entry + side * risk * params.target_r
        last_i = min(end_index, entry_i + params.max_hold_bars)

        exit_i = last_i
        exit_price = bars[last_i].close
        reason = "TIME"

        for j in range(entry_i, last_i + 1):
            b = bars[j]
            if side > 0:
                stop_hit = b.low <= stop
                target_hit = b.high >= target
            else:
                stop_hit = b.high >= stop
                target_hit = b.low <= target

            if stop_hit and target_hit:
                exit_i = j
                exit_price = stop
                reason = "STOP_AMBIGUOUS_BAR"
                break
            if stop_hit:
                exit_i = j
                exit_price = stop
                reason = "STOP"
                break
            if target_hit:
                exit_i = j
                exit_price = target
                reason = "TARGET"
                break

        gross_r = side * (exit_price - entry) / risk
        result_r = gross_r - params.round_turn_cost_r
        trades.append(
            TradeOutcome(
                strategy_id=strategy_id,
                signal_index=i,
                entry_index=entry_i,
                exit_index=exit_i,
                side="LONG" if side > 0 else "SHORT",
                entry_price=entry,
                exit_price=exit_price,
                initial_stop=stop,
                target=target,
                result_r=result_r,
                exit_reason=reason,
                evidence_score=score,
                agreement_ratio=summary.agreement_ratio,
            )
        )
        i = max(i + 1, exit_i + 1)

    return trades, summarize_trades(trades)


def summarize_trades(trades: list[TradeOutcome]) -> BacktestStats:
    if not trades:
        return BacktestStats(
            trades=0,
            wins=0,
            losses=0,
            win_rate=0.0,
            total_r=0.0,
            expectancy_r=0.0,
            profit_factor=0.0,
            max_drawdown_r=0.0,
        )

    wins = sum(t.result_r > 0 for t in trades)
    losses = sum(t.result_r <= 0 for t in trades)
    total = sum(t.result_r for t in trades)
    gross_win = sum(t.result_r for t in trades if t.result_r > 0)
    gross_loss = abs(sum(t.result_r for t in trades if t.result_r < 0))
    pf = 99.0 if gross_loss <= 1e-12 and gross_win > 0 else _safe(gross_win, gross_loss)

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for t in trades:
        equity += t.result_r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    return BacktestStats(
        trades=len(trades),
        wins=wins,
        losses=losses,
        win_rate=wins / len(trades),
        total_r=total,
        expectancy_r=total / len(trades),
        profit_factor=pf,
        max_drawdown_r=max_dd,
    )


def _safe(num: float, den: float, default: float = 0.0) -> float:
    return default if abs(den) <= 1e-12 else num / den


def parameter_grid(timeframe: str) -> tuple[BacktestParams, ...]:
    hold = 12 if timeframe in {"1", "3", "5"} else 16 if timeframe == "15" else 12 if timeframe in {"30", "60"} else 8
    return tuple(
        BacktestParams(
            threshold=threshold,
            stop_atr=LIVE_PLAN_STOP_ATR_MULTIPLE,
            target_r=LIVE_PLAN_FINAL_TARGET_RR,
            max_hold_bars=hold,
        )
        for threshold in (0.50, 0.62, 0.72)
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


def _segment_stability(
    symbol: str,
    timeframe: str,
    bars: list[Bar],
    snapshots: Mapping[int, HistoricalFeatureSnapshot],
    strategy_id: str,
    params: BacktestParams,
    start: int,
    end: int,
) -> float:
    width = max(1, (end - start) // 3)
    positive = 0
    used = 0
    for n in range(3):
        a = start + n * width
        b = end if n == 2 else min(end, a + width)
        _, stats = backtest_strategy(
            symbol,
            timeframe,
            bars,
            snapshots,
            strategy_id,
            params,
            start_index=a,
            end_index=b,
        )
        if stats.trades >= 3:
            used += 1
            if stats.expectancy_r >= 0 and stats.profit_factor >= 1.0:
                positive += 1
    return 0.0 if used == 0 else positive / used


def walk_forward_validate(
    symbol: str,
    timeframe: str,
    bars: list[Bar],
    strategy_id: str,
    *,
    snapshots: Mapping[int, HistoricalFeatureSnapshot] | None = None,
) -> WalkForwardValidation:
    if len(bars) < 900:
        raise ValueError("Need at least 900 bars for train/test/forward validation")
    snapshots = snapshots or materialize_feature_series(symbol, timeframe, bars)

    n = len(bars)
    train_end = max(520, int(n * 0.58))
    test_end = max(train_end + 120, int(n * 0.82))
    test_end = min(test_end, n - 80)

    candidates: list[tuple[float, BacktestParams, BacktestStats]] = []
    for params in parameter_grid(timeframe):
        _, stats = backtest_strategy(
            symbol,
            timeframe,
            bars,
            snapshots,
            strategy_id,
            params,
            start_index=260,
            end_index=train_end,
        )
        candidates.append((_objective(stats), params, stats))

    candidates.sort(key=lambda x: x[0], reverse=True)
    if not candidates or candidates[0][0] == -inf:
        best_params = parameter_grid(timeframe)[0]
        train_stats = BacktestStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    else:
        _, best_params, train_stats = candidates[0]

    _, test_stats = backtest_strategy(
        symbol,
        timeframe,
        bars,
        snapshots,
        strategy_id,
        best_params,
        start_index=train_end,
        end_index=test_end,
    )
    _, forward_stats = backtest_strategy(
        symbol,
        timeframe,
        bars,
        snapshots,
        strategy_id,
        best_params,
        start_index=test_end,
        end_index=n - 1,
    )

    valid_candidates = [x for x in candidates if x[2].trades >= 8]
    top = valid_candidates[: max(3, len(valid_candidates) // 4)] if valid_candidates else []
    parameter_stability = (
        sum(x[2].expectancy_r > 0 and x[2].profit_factor >= 1.0 for x in top) / len(top)
        if top
        else 0.0
    )
    regime_stability = _segment_stability(
        symbol,
        timeframe,
        bars,
        snapshots,
        strategy_id,
        best_params,
        train_end,
        test_end,
    )

    trial = StrategyTrial(
        strategy_id=strategy_id,
        symbol=symbol,
        timeframe=timeframe,
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
    return WalkForwardValidation(
        trial=trial,
        selected_params=best_params,
        train_stats=train_stats,
        test_stats=test_stats,
        forward_stats=forward_stats,
    )


def strategy_matrix(
    symbol: str,
    asset_class: str,
    bars_by_timeframe: Mapping[str, list[Bar]],
) -> tuple[list[WalkForwardValidation], MatrixSelection]:
    results: list[WalkForwardValidation] = []
    for timeframe, bars in bars_by_timeframe.items():
        if len(bars) < 900:
            continue
        snapshots = materialize_feature_series(symbol, timeframe, bars)
        for spec in candidate_strategies(asset_class, timeframe):
            results.append(
                walk_forward_validate(
                    symbol,
                    timeframe,
                    bars,
                    spec.strategy_id,
                    snapshots=snapshots,
                )
            )

    scored = [
        (robust_trial_score(result.trial), result)
        for result in results
        if robust_trial_score(result.trial) > 0
    ]
    if not scored:
        return results, MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe=None,
            robust_score=None,
            trial_count=len(results),
            reason="No strategy/timeframe passed out-of-sample and forward robustness gates.",
        )

    score, best = max(scored, key=lambda x: x[0])
    return results, MatrixSelection(
        status="VALIDATED",
        symbol=symbol,
        strategy_id=best.trial.strategy_id,
        timeframe=best.trial.timeframe,
        robust_score=score,
        trial_count=len(results),
        reason="Selected by out-of-sample and forward robustness, not headline in-sample profit.",
    )
