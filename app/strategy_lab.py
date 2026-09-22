from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str
    family: str
    description: str
    preferred_timeframes: tuple[str, ...]
    feature_families: tuple[str, ...]
    suitable_asset_classes: tuple[str, ...]


@dataclass(frozen=True)
class StrategyTrial:
    strategy_id: str
    symbol: str
    timeframe: str
    train_trades: int
    test_trades: int
    forward_trades: int
    train_expectancy_r: float
    test_expectancy_r: float
    forward_expectancy_r: float | None
    test_profit_factor: float
    forward_profit_factor: float | None
    test_win_rate: float
    max_drawdown_r: float
    parameter_stability: float
    regime_stability: float


@dataclass(frozen=True)
class StrategySelection:
    status: str
    strategy_id: str | None
    robust_score: float | None
    reasons: tuple[str, ...]


STRATEGIES: tuple[StrategySpec, ...] = (
    StrategySpec(
        "smc_structure_liquidity",
        "SMC",
        "Market structure, BOS/CHoCH, liquidity sweep, order-block/FVG confluence.",
        ("15", "30", "60", "120", "240"),
        ("market_structure", "smc_liquidity", "price_action", "volatility"),
        ("forex", "crypto", "indices", "metals", "energy", "rates"),
    ),
    StrategySpec(
        "trend_pullback",
        "TREND",
        "Trade pullbacks in an established multi-timeframe trend.",
        ("15", "30", "60", "120", "240", "1D"),
        ("trend", "momentum", "market_structure", "volatility"),
        ("forex", "crypto", "indices", "metals", "energy", "rates"),
    ),
    StrategySpec(
        "breakout_expansion",
        "BREAKOUT",
        "Compression-to-expansion breakout with volume and volatility confirmation.",
        ("15", "30", "60", "120", "240"),
        ("volatility", "volume", "trend", "price_action"),
        ("forex", "crypto", "indices", "metals", "energy"),
    ),
    StrategySpec(
        "mean_reversion",
        "MEAN_REVERSION",
        "Fade statistically stretched moves only inside a verified non-trending regime.",
        ("15", "30", "60", "120"),
        ("mean_reversion", "volatility", "momentum", "market_structure"),
        ("forex", "indices", "rates", "metals"),
    ),
    StrategySpec(
        "vwap_intraday",
        "INTRADAY",
        "VWAP/anchored-VWAP continuation or reversion with session structure.",
        ("5", "15", "30", "60"),
        ("vwap", "volume", "market_structure", "smc_liquidity"),
        ("indices", "metals", "energy", "forex", "crypto"),
    ),
    StrategySpec(
        "microtrend_scalp",
        "SCALP",
        "Short-horizon momentum scalp requiring high liquidity and tight spread/volatility control.",
        ("1", "3", "5", "15"),
        ("microstructure", "smc_liquidity", "momentum", "volatility"),
        ("indices", "forex", "metals", "energy", "crypto"),
    ),
    StrategySpec(
        "momentum_continuation",
        "MOMENTUM",
        "Continuation after persistent relative strength and market-structure confirmation.",
        ("15", "30", "60", "120", "240", "1D"),
        ("momentum", "trend", "volume", "market_structure"),
        ("forex", "crypto", "indices", "metals", "energy"),
    ),
    StrategySpec(
        "volatility_squeeze",
        "VOLATILITY",
        "Trade post-squeeze expansion only after direction and liquidity confirmation.",
        ("15", "30", "60", "120", "240"),
        ("volatility", "volume", "trend", "smc_liquidity"),
        ("forex", "crypto", "indices", "metals", "energy"),
    ),
    StrategySpec(
        "range_rotation",
        "RANGE",
        "Rotate between validated range extremes; disabled when trend strength expands.",
        ("15", "30", "60", "120"),
        ("market_structure", "mean_reversion", "volatility", "volume"),
        ("forex", "rates", "indices", "metals"),
    ),
)


def candidate_strategies(asset_class: str, timeframe: str) -> tuple[StrategySpec, ...]:
    return tuple(
        spec
        for spec in STRATEGIES
        if asset_class in spec.suitable_asset_classes and timeframe in spec.preferred_timeframes
    )


def _trial_reasons(trial: StrategyTrial) -> list[str]:
    reasons: list[str] = []
    if trial.test_trades < 30:
        reasons.append("insufficient_out_of_sample_trades")
    if trial.test_expectancy_r <= 0.08:
        reasons.append("weak_out_of_sample_expectancy")
    if trial.test_profit_factor < 1.15:
        reasons.append("weak_out_of_sample_profit_factor")
    if trial.max_drawdown_r > 10.0:
        reasons.append("drawdown_too_large")
    if trial.parameter_stability < 0.65:
        reasons.append("parameter_instability")
    if trial.regime_stability < 0.60:
        reasons.append("regime_instability")
    if trial.train_expectancy_r > 0 and trial.test_expectancy_r < 0.45 * trial.train_expectancy_r:
        reasons.append("train_test_degradation")
    if trial.forward_trades >= 15:
        if trial.forward_expectancy_r is None or trial.forward_expectancy_r <= 0:
            reasons.append("negative_forward_expectancy")
        if trial.forward_profit_factor is None or trial.forward_profit_factor < 1.05:
            reasons.append("weak_forward_profit_factor")
    return reasons


def trial_rejection_reasons(trial: StrategyTrial) -> tuple[str, ...]:
    """Public diagnostics for why a trial did not pass robustness gates."""
    return tuple(_trial_reasons(trial))


def classify_trial_status(trial: StrategyTrial) -> str:
    """Explain *why* a trial is not deployable without weakening any gate."""
    reasons = set(_trial_reasons(trial))
    if not reasons:
        return "VALIDATED"
    if "negative_forward_expectancy" in reasons or "weak_forward_profit_factor" in reasons:
        return "FORWARD_FAILED"
    if "drawdown_too_large" in reasons:
        return "RISK_FAILED"
    if "weak_out_of_sample_expectancy" in reasons or "weak_out_of_sample_profit_factor" in reasons:
        return "WEAK_EDGE"
    if "parameter_instability" in reasons or "regime_instability" in reasons:
        return "UNSTABLE"
    if "train_test_degradation" in reasons:
        return "OVERFIT_RISK"
    if reasons == {"insufficient_out_of_sample_trades"}:
        return "SAMPLE_LIMITED"
    return "REJECTED"


def robust_trial_score(trial: StrategyTrial) -> float:
    """Score robustness, not headline backtest return."""
    reasons = _trial_reasons(trial)
    if reasons:
        return 0.0
    forward_expectancy = (
        trial.forward_expectancy_r
        if trial.forward_trades >= 15 and trial.forward_expectancy_r is not None
        else trial.test_expectancy_r
    )
    forward_pf = (
        trial.forward_profit_factor
        if trial.forward_trades >= 15 and trial.forward_profit_factor is not None
        else trial.test_profit_factor
    )
    score = (
        min(2.0, trial.test_expectancy_r) * 20.0
        + min(2.0, forward_expectancy) * 20.0
        + min(2.5, trial.test_profit_factor) * 10.0
        + min(2.5, forward_pf) * 10.0
        + trial.parameter_stability * 15.0
        + trial.regime_stability * 15.0
        + min(1.0, trial.test_win_rate) * 10.0
        - min(10.0, trial.max_drawdown_r) * 2.0
    )
    return round(max(0.0, score), 3)


def select_strategy(trials: Iterable[StrategyTrial]) -> StrategySelection:
    scored: list[tuple[float, StrategyTrial]] = []
    rejected: list[str] = []
    for trial in trials:
        reasons = _trial_reasons(trial)
        if reasons:
            rejected.append(f"{trial.strategy_id}:{','.join(reasons)}")
            continue
        scored.append((robust_trial_score(trial), trial))

    if not scored:
        return StrategySelection(
            status="NO_VALIDATED_STRATEGY",
            strategy_id=None,
            robust_score=None,
            reasons=tuple(rejected) if rejected else ("no_trials",),
        )

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best = scored[0]
    return StrategySelection(
        status="VALIDATED",
        strategy_id=best.strategy_id,
        robust_score=best_score,
        reasons=(
            "selected_by_out_of_sample_forward_robustness",
            "not_selected_by_in_sample_profit",
        ),
    )
