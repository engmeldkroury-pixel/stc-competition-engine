from __future__ import annotations

from dataclasses import dataclass

from .models import Bar
from .strategy_lab import StrategyTrial, candidate_strategies, trial_rejection_reasons
from .walkforward import (
    BacktestParams,
    BacktestStats,
    backtest_strategy,
    materialize_feature_series,
    walk_forward_validate,
)


@dataclass(frozen=True)
class NativeFrozenConfirmation:
    strategy_id: str
    symbol: str
    timeframe: str
    selected_params: BacktestParams
    development_trial: StrategyTrial
    confirmation: BacktestStats
    confirmation_passed: bool
    confirmation_reasons: tuple[str, ...]


@dataclass(frozen=True)
class NativeFrozenSymbolReport:
    symbol: str
    timeframe: str
    development_bars: int
    confirmation_bars: int
    components: tuple[NativeFrozenConfirmation, ...]
    promotion_candidates: tuple[str, ...]
    status: str
    live_authority: bool
    notes: tuple[str, ...]


def _cutoff(
    bars: list[Bar],
    *,
    development_fraction: float,
    min_development_bars: int = 1200,
    min_confirmation_bars: int = 500,
) -> int:
    if not 0.60 <= development_fraction <= 0.90:
        raise ValueError("development_fraction must be between 0.60 and 0.90")
    if len(bars) < min_development_bars + min_confirmation_bars:
        raise ValueError(
            f"Need at least {min_development_bars + min_confirmation_bars} bars "
            "for native frozen confirmation"
        )
    cut = int(len(bars) * development_fraction)
    if cut < min_development_bars:
        raise ValueError(
            f"Requested development split yields {cut} bars; "
            f"need at least {min_development_bars}"
        )
    holdout = len(bars) - cut
    if holdout < min_confirmation_bars:
        raise ValueError(
            f"Requested frozen confirmation split yields {holdout} bars; "
            f"need at least {min_confirmation_bars}. Increase history rather than "
            "silently changing the frozen percentage."
        )
    return cut


def _empty_stats() -> BacktestStats:
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


def _confirmation_reasons(
    stats: BacktestStats,
    *,
    reference_expectancy_r: float | None,
    min_trades: int = 10,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if stats.trades < min_trades:
        reasons.append("insufficient_frozen_confirmation_trades")
    if stats.expectancy_r <= 0:
        reasons.append("negative_frozen_confirmation_expectancy")
    if stats.profit_factor < 1.05:
        reasons.append("weak_frozen_confirmation_profit_factor")
    if stats.max_drawdown_r > 10.0:
        reasons.append("frozen_confirmation_drawdown_too_large")
    if (
        reference_expectancy_r is not None
        and reference_expectancy_r > 0.08
        and stats.expectancy_r < 0.25 * reference_expectancy_r
    ):
        reasons.append("frozen_confirmation_degradation")
    return tuple(reasons)


def confirm_native_symbol(
    *,
    symbol: str,
    asset_class: str,
    timeframe: str,
    bars: list[Bar],
    development_fraction: float = 0.85,
) -> NativeFrozenSymbolReport:
    """Apply the same final-unseen principle to native STC strategies.

    Strategy parameters are selected and development robustness is judged only
    on the first development_fraction of bars. The final holdout is replayed
    with those parameters frozen. Full-history feature snapshots remain causal:
    each snapshot consumes only bars up to its own timestamp.
    """
    cut = _cutoff(bars, development_fraction=development_fraction)
    development = bars[:cut]
    full_snapshots = materialize_feature_series(symbol, timeframe, bars)
    components: list[NativeFrozenConfirmation] = []

    for spec in candidate_strategies(asset_class, timeframe):
        validation = walk_forward_validate(
            symbol,
            timeframe,
            development,
            spec.strategy_id,
        )
        trial = validation.trial
        development_reasons = trial_rejection_reasons(trial)
        confirmation = _empty_stats()
        passed = False

        if not development_reasons:
            _, confirmation = backtest_strategy(
                symbol,
                timeframe,
                bars,
                full_snapshots,
                spec.strategy_id,
                validation.selected_params,
                start_index=cut,
                end_index=len(bars) - 1,
            )
            reasons = _confirmation_reasons(
                confirmation,
                reference_expectancy_r=trial.forward_expectancy_r,
            )
            passed = not reasons
        else:
            reasons = ("development_not_validated",) + tuple(development_reasons)

        components.append(
            NativeFrozenConfirmation(
                strategy_id=spec.strategy_id,
                symbol=symbol,
                timeframe=timeframe,
                selected_params=validation.selected_params,
                development_trial=trial,
                confirmation=confirmation,
                confirmation_passed=passed,
                confirmation_reasons=reasons,
            )
        )

    candidates = tuple(
        row.strategy_id for row in components if row.confirmation_passed
    )
    return NativeFrozenSymbolReport(
        symbol=symbol,
        timeframe=timeframe,
        development_bars=cut,
        confirmation_bars=len(bars) - cut,
        components=tuple(components),
        promotion_candidates=candidates,
        status=(
            "FROZEN_CONFIRMATION_PASSED"
            if candidates
            else "NO_FROZEN_CONFIRMATION_PASS"
        ),
        live_authority=False,
        notes=(
            "Native strategy tuning and development gates use only the first 85% by default.",
            "Final holdout is excluded from parameter selection and development validation.",
            "A frozen pass is research evidence only and cannot grant live authority.",
        ),
    )
