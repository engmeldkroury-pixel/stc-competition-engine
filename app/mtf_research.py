from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from .analysis import ema, macd, rsi
from .models import Bar
from .walkforward import (
    SignalGate,
    WalkForwardValidation,
    materialize_feature_series,
    robust_trial_score,
    walk_forward_validate,
)


MTF_TIMEFRAMES = ("60", "120", "240", "1D", "1M")


@dataclass(frozen=True)
class ConfirmedTrendPoint:
    confirmed_at: datetime
    score: float


@dataclass(frozen=True)
class MTFPolicy:
    name: str
    weights: Mapping[str, float]
    min_aligned: int
    min_weighted_alignment: float
    max_strong_conflicts: int
    higher_timeframe_floor: float | None = None


@dataclass(frozen=True)
class MTFDecision:
    passed: bool
    policy: str
    weighted_alignment: float
    aligned: int
    strong_conflicts: int
    directional_scores: Mapping[str, float]
    reason: str


@dataclass(frozen=True)
class MTFValidationResult:
    policy: str
    validation: WalkForwardValidation
    robust_score: float
    test_retention: float
    forward_retention: float


POLICIES: tuple[MTFPolicy, ...] = (
    MTFPolicy(
        name="MAJORITY",
        weights={"60": 0.15, "120": 0.20, "240": 0.25, "1D": 0.25, "1M": 0.15},
        min_aligned=4,
        min_weighted_alignment=0.10,
        max_strong_conflicts=1,
    ),
    MTFPolicy(
        name="TREND_WEIGHTED",
        weights={"60": 0.10, "120": 0.15, "240": 0.25, "1D": 0.30, "1M": 0.20},
        min_aligned=3,
        min_weighted_alignment=0.20,
        max_strong_conflicts=1,
        higher_timeframe_floor=-0.25,
    ),
    MTFPolicy(
        name="STRICT",
        weights={"60": 0.15, "120": 0.20, "240": 0.25, "1D": 0.25, "1M": 0.15},
        min_aligned=5,
        min_weighted_alignment=0.25,
        max_strong_conflicts=0,
        higher_timeframe_floor=0.0,
    ),
)


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def trend_score(bars: list[Bar]) -> float:
    """Conservative direction score from confirmed bars only.

    The score is deliberately compact and independent of the entry strategy.
    It is used only as a higher-timeframe research confirmation layer.
    """
    if len(bars) < 55:
        raise ValueError("Need at least 55 confirmed bars for MTF trend score")

    window = bars[-300:]
    closes = [bar.close for bar in window]
    close = closes[-1]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    r = rsi(closes, 14)
    m, ms = macd(closes)
    momentum20 = close / closes[-21] - 1.0

    score = 0.0
    if close > e20 > e50:
        score += 0.30
    elif close < e20 < e50:
        score -= 0.30

    if len(closes) >= 200:
        e200 = ema(closes, 200)
        score += 0.20 if e50 >= e200 else -0.20
    else:
        score += 0.20 if close >= e50 else -0.20

    score += 0.20 if m >= ms else -0.20

    if r >= 55:
        score += 0.15
    elif r <= 45:
        score -= 0.15

    if momentum20 > 0:
        score += 0.15
    elif momentum20 < 0:
        score -= 0.15

    return _clamp(score)


def confirmed_trend_series(bars: list[Bar]) -> tuple[ConfirmedTrendPoint, ...]:
    """Create no-lookahead trend points.

    A bar that opens at T is not considered confirmed until the next bar opens.
    Therefore point i is stamped with bars[i+1].timestamp. The final source bar
    is never used because its close cannot be proven from the series alone.
    """
    if len(bars) < 56:
        return ()

    out: list[ConfirmedTrendPoint] = []
    for i in range(54, len(bars) - 1):
        score = trend_score(bars[max(0, i - 299) : i + 1])
        out.append(
            ConfirmedTrendPoint(
                confirmed_at=bars[i + 1].timestamp,
                score=score,
            )
        )
    return tuple(out)


def build_mtf_trend_map(
    bundle: Mapping[str, list[Bar]],
) -> dict[str, tuple[ConfirmedTrendPoint, ...]]:
    return {
        timeframe: confirmed_trend_series(list(bundle.get(timeframe) or []))
        for timeframe in MTF_TIMEFRAMES
    }


def latest_confirmed_score(
    points: tuple[ConfirmedTrendPoint, ...],
    *,
    as_of: datetime,
) -> float | None:
    if not points:
        return None
    times = [point.confirmed_at for point in points]
    index = bisect_right(times, as_of) - 1
    if index < 0:
        return None
    return points[index].score


def mtf_scores_as_of(
    trend_map: Mapping[str, tuple[ConfirmedTrendPoint, ...]],
    *,
    as_of: datetime,
) -> dict[str, float | None]:
    return {
        timeframe: latest_confirmed_score(
            tuple(trend_map.get(timeframe) or ()),
            as_of=as_of,
        )
        for timeframe in MTF_TIMEFRAMES
    }


def evaluate_mtf_policy(
    *,
    side: int,
    scores: Mapping[str, float | None],
    policy: MTFPolicy,
) -> MTFDecision:
    if side not in {-1, 1}:
        raise ValueError("side must be +1 or -1")
    missing = [tf for tf in MTF_TIMEFRAMES if scores.get(tf) is None]
    if missing:
        return MTFDecision(
            passed=False,
            policy=policy.name,
            weighted_alignment=0.0,
            aligned=0,
            strong_conflicts=0,
            directional_scores={},
            reason="missing_confirmed_timeframes:" + ",".join(missing),
        )

    directional = {
        tf: side * float(scores[tf])
        for tf in MTF_TIMEFRAMES
    }
    weight_total = sum(float(policy.weights[tf]) for tf in MTF_TIMEFRAMES)
    weighted = sum(
        directional[tf] * float(policy.weights[tf])
        for tf in MTF_TIMEFRAMES
    ) / weight_total
    aligned = sum(value >= 0.05 for value in directional.values())
    strong_conflicts = sum(value <= -0.45 for value in directional.values())

    if strong_conflicts > policy.max_strong_conflicts:
        reason = "too_many_strong_conflicts"
        passed = False
    elif aligned < policy.min_aligned:
        reason = "insufficient_timeframe_alignment"
        passed = False
    elif weighted < policy.min_weighted_alignment:
        reason = "weighted_alignment_below_policy_floor"
        passed = False
    elif (
        policy.higher_timeframe_floor is not None
        and any(
            directional[tf] < policy.higher_timeframe_floor
            for tf in ("240", "1D", "1M")
        )
    ):
        reason = "higher_timeframe_floor_failed"
        passed = False
    else:
        reason = "mtf_policy_passed"
        passed = True

    return MTFDecision(
        passed=passed,
        policy=policy.name,
        weighted_alignment=weighted,
        aligned=aligned,
        strong_conflicts=strong_conflicts,
        directional_scores=directional,
        reason=reason,
    )


def make_mtf_signal_gate(
    *,
    entry_bars: list[Bar],
    trend_map: Mapping[str, tuple[ConfirmedTrendPoint, ...]],
    policy: MTFPolicy,
) -> SignalGate:
    """Return a backtest gate evaluated at the 15m signal close.

    In the research engine a signal on bar i is only actionable from bar i+1.
    The timestamp of bar i+1 is therefore the conservative signal-close time.
    """

    def gate(signal_index: int, side: int, score: float, summary) -> bool:
        del score, summary
        if signal_index + 1 >= len(entry_bars):
            return False
        as_of = entry_bars[signal_index + 1].timestamp
        scores = mtf_scores_as_of(trend_map, as_of=as_of)
        return evaluate_mtf_policy(
            side=side,
            scores=scores,
            policy=policy,
        ).passed

    return gate


def validate_mtf_policies(
    *,
    symbol: str,
    strategy_id: str,
    bundle: Mapping[str, list[Bar]],
    policies: tuple[MTFPolicy, ...] = POLICIES,
) -> tuple[MTFValidationResult, ...]:
    """Compare the same 15m strategy under alternative MTF confirmation rules."""
    entry_bars = list(bundle.get("15") or [])
    if len(entry_bars) < 900:
        raise ValueError("Need at least 900 15m bars for MTF validation")

    snapshots = materialize_feature_series(symbol, "15", entry_bars)
    trend_map = build_mtf_trend_map(bundle)

    baseline = walk_forward_validate(
        symbol,
        "15",
        entry_bars,
        strategy_id,
        snapshots=snapshots,
    )

    results: list[MTFValidationResult] = []
    for policy in policies:
        validation = walk_forward_validate(
            symbol,
            "15",
            entry_bars,
            strategy_id,
            snapshots=snapshots,
            signal_gate=make_mtf_signal_gate(
                entry_bars=entry_bars,
                trend_map=trend_map,
                policy=policy,
            ),
        )
        test_retention = (
            validation.test_stats.trades / baseline.test_stats.trades
            if baseline.test_stats.trades
            else 0.0
        )
        forward_retention = (
            validation.forward_stats.trades / baseline.forward_stats.trades
            if baseline.forward_stats.trades
            else 0.0
        )
        results.append(
            MTFValidationResult(
                policy=policy.name,
                validation=validation,
                robust_score=robust_trial_score(validation.trial),
                test_retention=test_retention,
                forward_retention=forward_retention,
            )
        )
    return tuple(results)
