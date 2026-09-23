from __future__ import annotations

from dataclasses import dataclass

from .community_indicator_benchmark import (
    CommunityIndicatorTrial,
    IndicatorStats,
    backtest_indicator_signals,
    benchmark_indicator,
)
from .community_indicator_catalog import eligible_indicators
from .community_indicator_signals import indicator_signal_series
from .models import Bar


@dataclass(frozen=True)
class CommunityFrozenConfirmation:
    indicator_id: str
    symbol: str
    timeframe: str
    selected_parameters: dict
    development_trial: CommunityIndicatorTrial
    confirmation: IndicatorStats
    confirmation_passed: bool
    confirmation_reasons: tuple[str, ...]


@dataclass(frozen=True)
class CommunityFrozenSymbolReport:
    symbol: str
    timeframe: str
    development_bars: int
    confirmation_bars: int
    components: tuple[CommunityFrozenConfirmation, ...]
    promotion_candidates: tuple[str, ...]
    status: str
    live_authority: bool
    notes: tuple[str, ...]


def _empty_stats() -> IndicatorStats:
    return IndicatorStats(
        trades=0,
        wins=0,
        losses=0,
        win_rate=0.0,
        expectancy_r=0.0,
        profit_factor=0.0,
        max_drawdown_r=0.0,
    )


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
            "for community frozen confirmation"
        )
    cut = int(len(bars) * development_fraction)
    development_bars = cut
    confirmation_bars = len(bars) - cut
    if development_bars < min_development_bars:
        raise ValueError(
            f"Requested development split yields {development_bars} bars; "
            f"need at least {min_development_bars}"
        )
    if confirmation_bars < min_confirmation_bars:
        raise ValueError(
            f"Requested frozen confirmation split yields {confirmation_bars} bars; "
            f"need at least {min_confirmation_bars}. Increase history rather than "
            "silently changing the frozen percentage."
        )
    return cut


def _reasons(
    stats: IndicatorStats,
    *,
    reference_expectancy_r: float | None,
    min_trades: int = 10,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if stats.trades < min_trades:
        reasons.append("insufficient_frozen_confirmation_trades")
    if stats.expectancy_r <= 0.0:
        reasons.append("negative_frozen_confirmation_expectancy")
    if stats.profit_factor < 1.02:
        reasons.append("weak_frozen_confirmation_profit_factor")
    if stats.max_drawdown_r > 12.0:
        reasons.append("frozen_confirmation_drawdown_too_large")
    if (
        reference_expectancy_r is not None
        and reference_expectancy_r > 0.08
        and stats.expectancy_r < 0.25 * reference_expectancy_r
    ):
        reasons.append("frozen_confirmation_degradation")
    return tuple(reasons)


def confirm_community_symbol(
    *,
    symbol: str,
    asset_class: str,
    timeframe: str,
    bars: list[Bar],
    development_fraction: float = 0.85,
) -> CommunityFrozenSymbolReport:
    """Run a truly unseen final holdout after normal development validation.

    The first development fraction of history is the entire development
    dataset. Each indicator tunes its bounded parameters only inside that
    development dataset and must pass its internal TEST/FORWARD gate there.
    The final holdout is never used for parameter choice or development score.
    """
    cut = _cutoff(bars, development_fraction=development_fraction)
    development = bars[:cut]
    components: list[CommunityFrozenConfirmation] = []

    for spec in eligible_indicators(asset_class, timeframe, implemented_only=True):
        if spec.implementation_status != "implemented_conceptual":
            continue
        trial = benchmark_indicator(
            indicator_id=spec.indicator_id,
            family=spec.signal_family,
            symbol=symbol,
            timeframe=timeframe,
            bars=development,
        )
        confirmation = _empty_stats()
        passed = False

        if trial.validated:
            signals = indicator_signal_series(
                spec.indicator_id,
                bars,
                parameters=trial.selected_parameters,
            )
            _, confirmation = backtest_indicator_signals(
                bars,
                signals,
                start_index=cut,
                end_index=len(bars) - 2,
            )
            reasons = _reasons(
                confirmation,
                reference_expectancy_r=trial.forward.expectancy_r,
            )
            passed = not reasons
        else:
            reasons = ("development_not_validated",) + tuple(trial.reasons)

        components.append(
            CommunityFrozenConfirmation(
                indicator_id=spec.indicator_id,
                symbol=symbol,
                timeframe=timeframe,
                selected_parameters=dict(trial.selected_parameters),
                development_trial=trial,
                confirmation=confirmation,
                confirmation_passed=passed,
                confirmation_reasons=reasons,
            )
        )

    candidates = tuple(
        item.indicator_id for item in components if item.confirmation_passed
    )
    return CommunityFrozenSymbolReport(
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
            "Final holdout is excluded from tuning and development validation.",
            "A frozen-confirmation pass creates only a research promotion candidate.",
            "Explicit promotion and live shadow observation remain required before live weight authority.",
        ),
    )
