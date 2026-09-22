from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping

from .feature_validation import FeatureValidation
from .probability import WinProbabilityEstimate, estimate_win_probability
from .strategy_lab import robust_trial_score
from .walkforward import MatrixSelection, WalkForwardValidation
from .weight_calibration import participation_percent


@dataclass(frozen=True)
class StrategyResearchReport:
    symbol: str
    status: str
    selected_strategy: str | None
    selected_timeframe: str | None
    robust_score: float | None
    setup_probability: WinProbabilityEstimate | None
    test_trades: int
    forward_trades: int
    test_expectancy_r: float | None
    forward_expectancy_r: float | None
    test_profit_factor: float | None
    forward_profit_factor: float | None
    max_drawdown_r: float | None
    feature_participation_pct: Mapping[str, float]
    deployable_feature_count: int
    blocked_feature_count: int
    notes: tuple[str, ...]


def build_strategy_research_report(
    *,
    selection: MatrixSelection,
    validations: Iterable[WalkForwardValidation],
    feature_validations: Iterable[FeatureValidation] = (),
    min_probability_samples: int = 50,
) -> StrategyResearchReport:
    rows = tuple(validations)
    features = tuple(feature_validations)
    if selection.status != "VALIDATED" or selection.strategy_id is None or selection.timeframe is None:
        return StrategyResearchReport(
            symbol=selection.symbol,
            status="NO_VALIDATED_STRATEGY",
            selected_strategy=None,
            selected_timeframe=None,
            robust_score=None,
            setup_probability=None,
            test_trades=0,
            forward_trades=0,
            test_expectancy_r=None,
            forward_expectancy_r=None,
            test_profit_factor=None,
            forward_profit_factor=None,
            max_drawdown_r=None,
            feature_participation_pct={},
            deployable_feature_count=0,
            blocked_feature_count=len(features),
            notes=(
                "No strategy/timeframe passed the out-of-sample and forward robustness gate.",
                "Do not convert a weak research result into a live trade recommendation.",
            ),
        )

    matches = [
        row for row in rows
        if row.trial.strategy_id == selection.strategy_id
        and row.trial.timeframe == selection.timeframe
        and row.trial.symbol == selection.symbol
    ]
    if not matches:
        raise ValueError("Matrix selection has no matching validation row")
    best = max(matches, key=lambda row: robust_trial_score(row.trial))

    # Probability uses only out-of-sample + forward closed outcomes, never train.
    wins = best.test_stats.wins + best.forward_stats.wins
    losses = best.test_stats.losses + best.forward_stats.losses
    probability = estimate_win_probability(
        wins,
        losses,
        min_samples=min_probability_samples,
    )

    relevant_features = [
        item for item in features
        if item.symbol == selection.symbol
        and item.strategy_id == selection.strategy_id
        and item.timeframe == selection.timeframe
    ]
    raw_weights = {
        item.feature: item.calibrated_weight.calibrated_reliability
        for item in relevant_features
        if item.deployable
    }
    participation = participation_percent(raw_weights)
    deployable_count = sum(item.deployable for item in relevant_features)
    blocked_count = len(relevant_features) - deployable_count

    notes = [
        "Win probability is empirical from out-of-sample/forward outcomes, not setup-quality score.",
        "Training trades are excluded from probability calibration.",
        "Indicator participation includes only features that passed test and forward validation.",
        "Manual approval and manual execution remain mandatory.",
    ]
    if probability.status != "CALIBRATED":
        notes.append("Probability is withheld until the comparable closed-outcome sample is large enough.")
    if not relevant_features:
        notes.append("Feature-level calibration has not yet been run for this selected strategy/timeframe.")

    return StrategyResearchReport(
        symbol=selection.symbol,
        status="VALIDATED",
        selected_strategy=selection.strategy_id,
        selected_timeframe=selection.timeframe,
        robust_score=selection.robust_score,
        setup_probability=probability,
        test_trades=best.test_stats.trades,
        forward_trades=best.forward_stats.trades,
        test_expectancy_r=best.test_stats.expectancy_r,
        forward_expectancy_r=best.forward_stats.expectancy_r if best.forward_stats.trades else None,
        test_profit_factor=best.test_stats.profit_factor,
        forward_profit_factor=best.forward_stats.profit_factor if best.forward_stats.trades else None,
        max_drawdown_r=max(best.test_stats.max_drawdown_r, best.forward_stats.max_drawdown_r),
        feature_participation_pct=participation,
        deployable_feature_count=deployable_count,
        blocked_feature_count=blocked_count,
        notes=tuple(notes),
    )


def report_to_dict(report: StrategyResearchReport) -> dict:
    return asdict(report)
