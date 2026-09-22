from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class FeaturePerformance:
    feature: str
    symbol: str
    strategy_id: str
    timeframe: str
    sample_size: int
    directional_hits: int
    average_forward_r: float
    profit_factor_when_present: float
    regime_stability: float


@dataclass(frozen=True)
class CalibratedWeight:
    feature: str
    prior_reliability: float
    posterior_hit_rate: float
    sample_confidence: float
    expectancy_multiplier: float
    stability_multiplier: float
    calibrated_reliability: float
    note: str


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def calibrate_feature_reliability(
    performance: FeaturePerformance,
    *,
    prior_reliability: float,
    prior_sample_strength: int = 40,
) -> CalibratedWeight:
    """Calibrate a feature weight with shrinkage toward its prior.

    A small backtest sample is never allowed to turn one indicator into an
    apparently 'certain' signal. Reliability grows only with repeated,
    out-of-sample evidence and remains capped below 1.0.
    """
    if performance.sample_size < 0 or performance.directional_hits < 0:
        raise ValueError("sample counts must be non-negative")
    if performance.directional_hits > performance.sample_size:
        raise ValueError("directional_hits cannot exceed sample_size")
    if prior_sample_strength <= 0:
        raise ValueError("prior_sample_strength must be positive")

    prior = _clamp(prior_reliability)
    n = performance.sample_size
    hits = performance.directional_hits

    posterior = (
        prior * prior_sample_strength + hits
    ) / (prior_sample_strength + n)

    # Smooth confidence: ~0.39 at 20 samples, ~0.71 at 50, ~0.92 at 100.
    sample_confidence = 1.0 - exp(-n / 40.0)

    # Positive forward expectancy can modestly raise participation; negative
    # expectancy penalizes it aggressively. Cap to avoid runaway optimization.
    if performance.average_forward_r <= 0:
        expectancy_multiplier = max(0.35, 1.0 + performance.average_forward_r)
    else:
        expectancy_multiplier = min(1.20, 1.0 + performance.average_forward_r * 0.25)

    pf = max(0.0, performance.profit_factor_when_present)
    if pf < 1.0:
        pf_multiplier = max(0.50, pf)
    else:
        pf_multiplier = min(1.10, 0.90 + pf * 0.10)

    stability = _clamp(performance.regime_stability)
    stability_multiplier = 0.55 + 0.45 * stability

    empirical = posterior * expectancy_multiplier * pf_multiplier * stability_multiplier

    # Blend empirical value back toward the prior until the sample is mature.
    calibrated = prior * (1.0 - sample_confidence) + empirical * sample_confidence
    calibrated = min(0.95, max(0.20, calibrated))

    return CalibratedWeight(
        feature=performance.feature,
        prior_reliability=prior,
        posterior_hit_rate=posterior,
        sample_confidence=sample_confidence,
        expectancy_multiplier=expectancy_multiplier * pf_multiplier,
        stability_multiplier=stability_multiplier,
        calibrated_reliability=calibrated,
        note=(
            "Reliability is sample-size-shrunk and capped; it is a participation "
            "weight, not a standalone probability of trade success."
        ),
    )


def participation_percent(weights: dict[str, float]) -> dict[str, float]:
    """Convert positive raw weights to transparent percentage participation."""
    clean = {name: max(0.0, float(value)) for name, value in weights.items()}
    total = sum(clean.values())
    if total <= 0:
        return {name: 0.0 for name in clean}
    return {name: (value / total) * 100.0 for name, value in clean.items()}
