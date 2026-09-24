from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Iterable

from .community_indicator_catalog import eligible_indicators
from .community_indicator_signals import atr_by_index, indicator_signal_series
from .models import Bar
from .strategy_lab import STRATEGIES, StrategyTrial, robust_trial_score


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
    selected_parameters: dict
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


def indicator_parameter_grid(indicator_id: str) -> tuple[dict, ...]:
    grids: dict[str, tuple[dict, ...]] = {
        "ut_bot_alerts": (
            {"atr_period": 10, "key_value": 1.0},
            {"atr_period": 10, "key_value": 1.5},
            {"atr_period": 14, "key_value": 1.5},
            {"atr_period": 14, "key_value": 2.0},
        ),
        "squeeze_momentum_lazybear": (
            {"length": 20, "bb_mult": 2.0, "kc_mult": 1.5},
            {"length": 20, "bb_mult": 2.0, "kc_mult": 2.0},
            {"length": 14, "bb_mult": 2.0, "kc_mult": 1.5},
        ),
        "wavetrend_crosses": (
            {"channel_length": 10, "average_length": 21, "signal_length": 4},
            {"channel_length": 9, "average_length": 12, "signal_length": 3},
            {"channel_length": 14, "average_length": 21, "signal_length": 4},
        ),
        "hull_suite": (
            {"length": 34},
            {"length": 55},
            {"length": 89},
        ),
        "supertrend_kivanc": (
            {"atr_period": 10, "multiplier": 2.0},
            {"atr_period": 10, "multiplier": 3.0},
            {"atr_period": 14, "multiplier": 3.0},
            {"atr_period": 14, "multiplier": 4.0},
        ),
        "chandelier_exit_everget": (
            {"period": 14, "multiplier": 2.0},
            {"period": 14, "multiplier": 3.0},
            {"period": 22, "multiplier": 2.0},
            {"period": 22, "multiplier": 3.0},
        ),
        "schaff_trend_cycle": (
            {"cycle_length": 10, "fast_length": 23, "slow_length": 50, "smoothing": 0.5},
            {"cycle_length": 12, "fast_length": 26, "slow_length": 50, "smoothing": 0.5},
            {"cycle_length": 10, "fast_length": 9, "slow_length": 30, "smoothing": 0.5},
        ),
        "range_filter_guikroth": (
            {"sampling_period": 50, "range_multiplier": 2.0},
            {"sampling_period": 50, "range_multiplier": 3.0},
            {"sampling_period": 100, "range_multiplier": 2.0},
            {"sampling_period": 100, "range_multiplier": 3.0},
        ),
        "alphatrend": (
            {"period": 10, "coefficient": 0.75},
            {"period": 14, "coefficient": 1.0},
            {"period": 20, "coefficient": 1.0},
            {"period": 14, "coefficient": 1.5},
        ),
        "optimized_trend_tracker": (
            {"length": 2, "percent": 1.0, "cmo_length": 9},
            {"length": 2, "percent": 1.4, "cmo_length": 9},
            {"length": 3, "percent": 1.4, "cmo_length": 9},
            {"length": 5, "percent": 2.0, "cmo_length": 9},
        ),
        "qqe_mod": (
            {"rsi_period": 6, "smoothing": 5, "fast_factor": 3.0, "slow_factor": 1.61, "threshold": 3.0, "bb_length": 50, "bb_mult": 0.35},
            {"rsi_period": 6, "smoothing": 5, "fast_factor": 2.5, "slow_factor": 1.61, "threshold": 2.0, "bb_length": 50, "bb_mult": 0.35},
            {"rsi_period": 8, "smoothing": 5, "fast_factor": 3.0, "slow_factor": 1.8, "threshold": 3.0, "bb_length": 40, "bb_mult": 0.35},
        ),
        "ssl_hybrid": (
            {"baseline_length": 60, "ssl_length": 15},
            {"baseline_length": 50, "ssl_length": 10},
            {"baseline_length": 100, "ssl_length": 20},
        ),
        "waddah_attar_explosion": (
            {"fast_length": 20, "slow_length": 40, "bb_length": 20, "bb_mult": 2.0, "sensitivity": 150.0, "dead_zone_atr_period": 100, "dead_zone_mult": 3.7},
            {"fast_length": 12, "slow_length": 26, "bb_length": 20, "bb_mult": 2.0, "sensitivity": 100.0, "dead_zone_atr_period": 100, "dead_zone_mult": 3.0},
            {"fast_length": 20, "slow_length": 40, "bb_length": 20, "bb_mult": 2.0, "sensitivity": 100.0, "dead_zone_atr_period": 50, "dead_zone_mult": 2.5},
        ),
        "qqe_ssl_wae_composite": (
            {"qqe_rsi_period": 6, "qqe_smoothing": 5, "qqe_fast_factor": 3.0, "qqe_slow_factor": 1.61, "qqe_threshold": 3.0, "ssl_baseline_length": 60, "ssl_length": 15, "wae_fast_length": 20, "wae_slow_length": 40, "wae_sensitivity": 150.0},
            {"qqe_rsi_period": 6, "qqe_smoothing": 5, "qqe_fast_factor": 2.5, "qqe_slow_factor": 1.61, "qqe_threshold": 2.0, "ssl_baseline_length": 50, "ssl_length": 10, "wae_fast_length": 12, "wae_slow_length": 26, "wae_sensitivity": 100.0},
        ),
        "halftrend_everget": (
            {"amplitude": 2},
            {"amplitude": 3},
            {"amplitude": 5},
            {"amplitude": 10},
        ),
        "trendilo": (
            {"smoothing": 1, "lookback": 50, "alma_offset": 0.85, "alma_sigma": 6.0, "band_multiplier": 1.0},
            {"smoothing": 1, "lookback": 34, "alma_offset": 0.85, "alma_sigma": 6.0, "band_multiplier": 1.0},
            {"smoothing": 2, "lookback": 50, "alma_offset": 0.85, "alma_sigma": 6.0, "band_multiplier": 1.0},
            {"smoothing": 1, "lookback": 50, "alma_offset": 0.85, "alma_sigma": 6.0, "band_multiplier": 1.25},
        ),
        "nadaraya_watson_endpoint_nonrepaint": (
            {"window": 500, "bandwidth": 8.0, "multiplier": 3.0, "deviation_length": 499},
            {"window": 500, "bandwidth": 6.0, "multiplier": 2.5, "deviation_length": 499},
            {"window": 250, "bandwidth": 8.0, "multiplier": 3.0, "deviation_length": 249},
            {"window": 250, "bandwidth": 12.0, "multiplier": 2.5, "deviation_length": 249},
        ),
        "rsi_kernel_optimized_flux": (
            {"rsi_period": 14, "pivot_length": 8, "bandwidth": 4.0, "min_samples": 10, "dominance_ratio": 1.25},
            {"rsi_period": 14, "pivot_length": 12, "bandwidth": 4.0, "min_samples": 12, "dominance_ratio": 1.30},
            {"rsi_period": 21, "pivot_length": 12, "bandwidth": 6.0, "min_samples": 12, "dominance_ratio": 1.35},
        ),
    }
    return grids.get(indicator_id, ({},))


def _train_objective(stats: IndicatorStats) -> float:
    if stats.trades < 15:
        return -inf
    return (
        min(1.5, stats.expectancy_r) * 25.0
        + min(3.0, stats.profit_factor) * 8.0
        + stats.win_rate * 5.0
        - min(15.0, stats.max_drawdown_r) * 1.2
    )


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
            selected_parameters=dict(parameters or {}),
            train=empty,
            test=empty,
            forward=empty,
            robust_score=0.0,
            validated=False,
            reasons=("insufficient_bars_300_minimum",),
        )

    n = len(bars)
    train_end = max(1, int(n * 0.60))
    test_end = max(train_end + 1, int(n * 0.80))
    warmup = min(250, max(60, int(n * 0.10)))

    grid = (parameters,) if parameters is not None else indicator_parameter_grid(indicator_id)
    candidates: list[tuple[float, dict, dict[int, float], IndicatorStats]] = []
    for candidate_params in grid:
        signals = indicator_signal_series(indicator_id, bars, parameters=candidate_params)
        _, train_stats = backtest_indicator_signals(
            bars, signals, start_index=warmup, end_index=train_end - 1, params=params
        )
        candidates.append((_train_objective(train_stats), dict(candidate_params), signals, train_stats))

    candidates.sort(key=lambda item: item[0], reverse=True)
    if not candidates:
        raise RuntimeError(f"No parameter candidates for {indicator_id}")
    _, selected_parameters, signals, train = candidates[0]
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
        selected_parameters=selected_parameters,
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
        family = next((spec.family for spec in STRATEGIES if spec.strategy_id == trial.strategy_id), "native_strategy")
        rows.append({
            "component_id": trial.strategy_id,
            "source_type": "core_strategy",
            "family": family,
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

    family_rows: dict[str, list[dict]] = {}
    for row in rows:
        family_rows.setdefault(str(row["family"]), []).append(row)

    # Redundancy-aware normalization: evidence families receive diminishing
    # returns before components split their family share. This prevents several
    # correlated trend/momentum variants from overwhelming structurally
    # independent evidence merely because many similar indicators were tested.
    family_strength = {
        family: sum(float(row["score"]) for row in members)
        for family, members in family_rows.items()
    }
    family_power = 0.75
    powered = {
        family: max(0.0, strength) ** family_power
        for family, strength in family_strength.items()
    }
    powered_total = sum(powered.values())

    weighted_rows: list[tuple[float, dict]] = []
    for family, members in family_rows.items():
        family_share = powered[family] / powered_total if powered_total > 0 else 0.0
        member_total = family_strength[family]
        for row in members:
            within = float(row["score"]) / member_total if member_total > 0 else 0.0
            weighted_rows.append((family_share * within, row))

    components = tuple(
        EnsembleComponentWeight(
            component_id=str(row["component_id"]),
            source_type=str(row["source_type"]),
            family=str(row["family"]),
            symbol=symbol,
            timeframe=timeframe,
            raw_score=float(row["score"]),
            normalized_weight=weight,
            test_trades=int(row["test_trades"]),
            forward_trades=int(row["forward_trades"]),
            note=(
                "Weight is driven by OOS/forward robustness and redundancy-aware family normalization. "
                "Popularity/reviews are discovery metadata only."
            ),
        )
        for weight, row in sorted(weighted_rows, key=lambda item: item[0], reverse=True)
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
            "Correlated evidence is normalized by family with diminishing returns before component weights are assigned.",
            "Live outcomes may be accumulated trade by trade, but weights must be recalibrated only on a frozen evaluation window.",
            "Do not chase the latest trade by changing weights after every single outcome.",
        ),
    )
