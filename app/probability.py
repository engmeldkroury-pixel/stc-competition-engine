from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class WinProbabilityEstimate:
    status: str
    sample_size: int
    wins: int
    losses: int
    observed_win_rate: float | None
    estimated_win_probability: float | None
    confidence_low: float | None
    confidence_high: float | None
    note: str


def estimate_win_probability(
    wins: int,
    losses: int,
    *,
    min_samples: int = 50,
    z: float = 1.96,
) -> WinProbabilityEstimate:
    """Estimate win probability from observed, comparable outcomes.

    This is deliberately not derived from a technical score. A setup-quality
    score and an empirical win probability are different quantities.
    """
    if wins < 0 or losses < 0:
        raise ValueError("wins/losses must be non-negative")
    total = wins + losses
    if total == 0:
        return WinProbabilityEstimate(
            status="INSUFFICIENT_DATA",
            sample_size=0,
            wins=0,
            losses=0,
            observed_win_rate=None,
            estimated_win_probability=None,
            confidence_low=None,
            confidence_high=None,
            note="No comparable closed outcomes are available for calibration.",
        )

    p = wins / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    half = (z * sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)) / denom
    low = max(0.0, center - half)
    high = min(1.0, center + half)

    if total < min_samples:
        return WinProbabilityEstimate(
            status="INSUFFICIENT_DATA",
            sample_size=total,
            wins=wins,
            losses=losses,
            observed_win_rate=p,
            estimated_win_probability=None,
            confidence_low=low,
            confidence_high=high,
            note=(
                f"Observed win rate is {p:.1%}, but at least {min_samples} comparable "
                "closed outcomes are required before STC displays it as a calibrated probability."
            ),
        )

    return WinProbabilityEstimate(
        status="CALIBRATED",
        sample_size=total,
        wins=wins,
        losses=losses,
        observed_win_rate=p,
        estimated_win_probability=p,
        confidence_low=low,
        confidence_high=high,
        note="Empirical estimate from comparable closed outcomes; not a guarantee of future profit.",
    )
