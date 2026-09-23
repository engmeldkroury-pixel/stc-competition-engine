from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Iterable

from .community_indicator_catalog import eligible_indicators
from .community_indicator_signals import atr_by_index, indicator_signal_series
from .models import Bar
from .strategy_lab import StrategyTrial, robust_trial_score


@dataclass(frozen=True)
class IndicatorBacktestParams:
    stop_atr: float = 1.5
    target_r: float = 2.0
    max_hold_bars: int = 16
    min_signal_strength: float = 0.55
    round_trip_cost_r: float = 0.04


@dataclass(frozen=True)
class IndicatorTrade:
    signal_index: int
    entry_index: int
    exit_index: int
    direction: int
    entry_price: float
    exit_price: float
    r_multiple: float
    exit_reason: str


@dataclass(frozen=True)
class IndicatorStats:
    trades: int
    wins: int
    losses: int
    win_rate: float
    expectancy_r: float
    profit_factor: float
    max_drawdown_r: float


@dataclass(frozen=True)
class CommunityIndicatorTrial:
    indicator_id: str
    symbol: str
    timeframe: str
    family: str
    train: IndicatorStats
    test: IndicatorStats
    forward: IndicatorStats
    robust_score: float
    validated: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class EnsembleComponentWeight:
    component_id: str
    source_type: str
    family: str
    symbol: str
    timeframe: str
    raw_score: float
    normalized_weight: float
    test_trades: int
    forward_trades: int
    note: str


@dataclass(frozen=True)
class SymbolEnsembleProfile:
    symbol: str
    timeframe: str
    components: tuple[EnsembleComponentWeight, ...]
    community_weight_share: float
    core_weight_share: float
    status: str
    notes: tuple[str, ...]


def _stats(trades: Iterable[IndicatorTrade]) -> IndicatorStats:
    rows = list(trades)
    if not rows:
        return IndicatorStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0)
    values = [trade.r_multiple for trade in rows]
    wins = sum(1 for value in values if value > 0)
    losses = len(rows) - wins
    gains = sum(value for value in values if value > 0)
    loss_abs = -sum(value for value in values if value < 0)
    profit_factor = gains / loss_abs if loss_abs > 1e-12 else (99.0 if gains > 0 else 0.0)

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    return IndicatorStats(
        trades=len(rows),
        wins=wins,
        losses=losses,
        win_rate=wins / len(rows),
        expectancy_r=sum(values) / len(rows),
        profit_factor=profit_factor,
        max_drawdown_r=max_dd,
    )


def backtest_indicator_signals(
    bars: list[Bar],
    signals: dict[int, float],
    *,
    start_index: int,
    end_index: int,
    params: IndicatorBacktestParams | None = None,
) -> tuple[list[IndicatorTrade], IndicatorStats]:
    """Standardized causal benchmark for apples-to-apples indicator comparison.

    A signal is known only at bar close and can enter no earlier than the next
    bar open. If both stop and target are touched in the same bar, the stop is
    assumed first. This is deliberately conservative.
    """
    p = params or IndicatorBacktestParams()
    atr = atr_by_index(bars, 14)
    trades: list[IndicatorTrade] = []
    i = max(15, start_index)
    final_index = min(end_index, len(bars) - 2)

    while i <= final_index:
        strength = float(signals.get(i, 0.0))
        if abs(strength) < p.min_signal_strength or i not in atr:
            i += 1
            continue
        direction = 1 if strength > 0 else -1
        entry_index = i + 1
        entry_price = bars[entry_index].open
        risk = float(atr[i]) * p.stop_atr
        if risk <= 0:
            i += 1
            continue
        stop = entry_price - direction * risk
        target = entry_price + direction * risk * p.target_r
        last = min(entry_index + p.max_hold_bars, final_index + 1)

        exit_index = last
        exit_price = bars[last].close
        exit_reason = "time_exit"

        for j in range(entry_index, last + 1):
            # A confirmed opposite signal from the previous bar may exit at the
            # next bar open before evaluating that bar's range.
            prev_signal = float(signals.get(j - 1, 0.0))
            if j > entry_index and direction * prev_signal <= -p.min_signal_strength:
                exit_index = j
                exit_price = bars[j].open
                exit_reason = "opposite_signal"
                break

            bar = bars[j]
            stop_hit = bar.low <= stop if direction > 0 else bar.high >= stop
            target_hit = bar.high >= target if direction > 0 else bar.low <= target
            if stop_hit and target_hit:
                exit_index = j
                exit_price = stop
                exit_reason = "stop_and_target_same_bar_conservative_stop"
                break
            if stop_hit:
                exit_index = j
                exit_price = stop
                exit_reason = "stop"
                break
            if target_hit:
                exit_index = j
                exit_price = target
                exit_reason = "target"
                break

        r_multiple = direction * (exit_price - entry_price) / risk - p.round_trip_cost_r
        trades.append(
            IndicatorTrade(
                signal_index=i,
                entry_index=entry_index,
                exit_index=exit_index,
                direction=direction,
                entry_price=entry_price,
                exit_price=exit_price,
                r_multiple=r_multiple,
                exit_reason=exit_reason,
            )
        )
        i = max(i + 1, exit_index)

    return trades, _stats(trades)


def _indicator_reasons(test: IndicatorStats, forward: IndicatorStats) -> list[str]:
    reasons: list[str] = []
    if test.trades < 20:
        reasons.append("insufficient_out_of_sample_trades")
    if forward.trades < 10:
        reasons.append("insufficient_forward_trades")
    if test.expectancy_r <= 0.05:
        reasons.append("weak_out_of_sample_expectancy")
    if forward.expectancy_r <= 0:
        reasons.append("negative_forward_expectancy")
    if test.profit_factor < 1.10:
        reasons.append("weak_out_of_sample_profit_factor")
    if forward.profit_factor < 1.02:
        reasons.append("weak_forward_profit_factor")
    if max(test.max_drawdown_r, forward.max_drawdown_r) > 12.0:
        reasons.append("drawdown_too_large")
    if test.expectancy_r > 0 and forward.expectancy_r < 0.35 * test.expectancy_r:
        reasons.append("forward_degradation")
    return reasons


def _indicator_score(test: IndicatorStats, forward: IndicatorStats) -> float:
    reasons = _indicator_reasons(test, forward)
    if reasons:
        return 0.0
    sample_confidence = min(1.0, (test.trades + forward.trades) / 80.0)
    score = (
        min(1.5, test.expectancy_r) * 22.0
        + min(1.5, forward.expectancy_r) * 26.0
        + min(2.5, test.profit_factor) * 8.0
        + min(2.5, forward.profit_factor) * 10.0
        + test.win_rate * 6.0
        + forward.win_rate * 8.0
        - min(12.0, max(test.max_drawdown_r, forward.max_drawdown_r)) * 1.6
    )
    return round(max(0.0, score) * (0.55 + 0.45 * sample_confidence), 4)


def benchmark_indicator(
    *,
    indicator_id: str,
    family: str,
    symbol: str,
    timeframe: str,
    bars: list[Bar],
    parameters: dict | None = None,
    params: IndicatorBacktestParams | None = None,
) -> CommunityIndicatorTrial:
    if len(bars) < 300:
        empty = IndicatorStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0)
        return CommunityIndicatorTrial(
            indicator_id=indicator_id,
            symbol=symbol,
            timeframe=timeframe,
            family=family,
            train=empty,
            test=empty,
            forward=empty,
            robust_score=0.0,
            validated=False,
            reasons=("insufficient_bars_300_minimum",),
        )

    signals = indicator_signal_series(indicator_id, bars, parameters=parameters)
    n = len(bars)
    train_end = max(1, int(n * 0.60))
    test_end = max(train_end + 1, int(n * 0.80))
    warmup = min(250, max(60, int(n * 0.10)))

    _, train = backtest_indicator_signals(
        bars, signals, start_index=warmup, end_index=train_end - 1, params=params
    )
    _, test = backtest_indicator_signals(
        bars, signals, start_index=train_end, end_index=test_end - 1, params=params
    )
    _, forward = backtest_indicator_signals(
        bars, signals, start_index=test_end, end_index=n - 2, params=params
    )
    reasons = tuple(_indicator_reasons(test, forward))
    score = _indicator_score(test, forward)
    return CommunityIndicatorTrial(
        indicator_id=indicator_id,
        symbol=symbol,
        timeframe=timeframe,
        family=family,
        train=train,
        test=test,
        forward=forward,
        robust_score=score,
        validated=not reasons,
        reasons=reasons,
    )


def benchmark_symbol_indicators(
    *,
    symbol: str,
    asset_class: str,
    timeframe: str,
    bars: list[Bar],
) -> tuple[CommunityIndicatorTrial, ...]:
    trials: list[CommunityIndicatorTrial] = []
    for spec in eligible_indicators(asset_class, timeframe, implemented_only=True):
        if spec.implementation_status != "implemented_conceptual":
            continue
        trials.append(
            benchmark_indicator(
                indicator_id=spec.indicator_id,
                family=spec.signal_family,
                symbol=symbol,
                timeframe=timeframe,
                bars=bars,
            )
        )
    return tuple(trials)


def _core_component_score(trial: StrategyTrial) -> float:
    return robust_trial_score(trial)


def _community_component_score(trial: CommunityIndicatorTrial) -> float:
    return trial.robust_score if trial.validated else 0.0


def build_symbol_ensemble_profile(
    *,
    symbol: str,
    timeframe: str,
    core_trials: Iterable[StrategyTrial],
    community_trials: Iterable[CommunityIndicatorTrial],
) -> SymbolEnsembleProfile:
    """Compare native STC strategies and community indicators on equal evidence rules.

    Popularity and review sentiment are intentionally absent from this function.
    A community indicator can receive a larger weight than a native strategy
    only when its out-of-sample/forward robust score is genuinely larger.
    """
    rows: list[dict] = []
    for trial in core_trials:
        if trial.symbol != symbol or trial.timeframe != timeframe:
            continue
        score = _core_component_score(trial)
        if score <= 0:
            continue
        rows.append({
            "component_id": trial.strategy_id,
            "source_type": "core_strategy",
            "family": "native_strategy",
            "score": score,
            "test_trades": trial.test_trades,
            "forward_trades": trial.forward_trades,
        })

    for trial in community_trials:
        if trial.symbol != symbol or trial.timeframe != timeframe:
            continue
        score = _community_component_score(trial)
        if score <= 0:
            continue
        rows.append({
            "component_id": trial.indicator_id,
            "source_type": "community_indicator",
            "family": trial.family,
            "score": score,
            "test_trades": trial.test.trades,
            "forward_trades": trial.forward.trades,
        })

    if not rows:
        return SymbolEnsembleProfile(
            symbol=symbol,
            timeframe=timeframe,
            components=(),
            community_weight_share=0.0,
            core_weight_share=0.0,
            status="NO_VALIDATED_COMPONENTS",
            notes=(
                "No component passed out-of-sample and forward robustness gates.",
                "Do not promote same-dataset backtest winners into live weights.",
            ),
        )

    total = sum(float(row["score"]) for row in rows)
    components = tuple(
        EnsembleComponentWeight(
            component_id=str(row["component_id"]),
            source_type=str(row["source_type"]),
            family=str(row["family"]),
            symbol=symbol,
            timeframe=timeframe,
            raw_score=float(row["score"]),
            normalized_weight=float(row["score"]) / total,
            test_trades=int(row["test_trades"]),
            forward_trades=int(row["forward_trades"]),
            note=(
                "Weight is driven by OOS/forward robustness with sample evidence. "
                "Popularity/reviews are discovery metadata only."
            ),
        )
        for row in sorted(rows, key=lambda item: float(item["score"]), reverse=True)
    )
    community_share = sum(
        item.normalized_weight for item in components if item.source_type == "community_indicator"
    )
    return SymbolEnsembleProfile(
        symbol=symbol,
        timeframe=timeframe,
        components=components,
        community_weight_share=community_share,
        core_weight_share=1.0 - community_share,
        status="RESEARCH_PROFILE_READY",
        notes=(
            "Profile is symbol/timeframe specific.",
            "Live outcomes may be accumulated trade by trade, but weights must be recalibrated only on a frozen evaluation window.",
            "Do not chase the latest trade by changing weights after every single outcome.",
        ),
    )
