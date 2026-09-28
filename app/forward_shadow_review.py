"""Pre-registered review gates for R10 prospective shadow evidence.

This module does not promote a strategy and has no live authority. It converts
forward-only valued observations into deterministic evidence states so the
project cannot move the goalposts after seeing wins or losses.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Iterable, Literal

ReviewState = Literal[
    "COLLECTING", "EARLY_POSITIVE", "REJECT_OR_RESEARCH",
    "ELIGIBLE_FOR_REVIEW",
]


@dataclass(frozen=True)
class ValuedForwardTrade:
    source_open_utc: str
    net_r: float
    record_sha256: str


@dataclass(frozen=True)
class ForwardReview:
    state: ReviewState
    n: int
    distinct_utc_days: int
    mean_r: float | None
    profit_factor: float | None
    win_rate: float | None
    max_drawdown_r: float | None
    max_positive_day_share: float | None
    lower_80_mean_r: float | None
    reasons: tuple[str, ...]
    automatic_live_promotion: Literal[False] = False


MIN_EARLY_N = 12
MIN_REVIEW_N = 30
MIN_REVIEW_DAYS = 5
MIN_REVIEW_MEAN_R = 0.10
MIN_REVIEW_PF = 1.20
MAX_REVIEW_DRAWDOWN_R = 6.0
MAX_POSITIVE_DAY_SHARE = 0.60


def _utc_day(value: str) -> str:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("utc_timestamp_required")
    return dt.astimezone(timezone.utc).date().isoformat()


def review_forward_trades(trades: Iterable[ValuedForwardTrade]) -> ForwardReview:
    rows = list(trades)
    if len({row.record_sha256 for row in rows}) != len(rows):
        raise ValueError("duplicate_forward_record")
    values: list[float] = []
    by_day: dict[str, float] = {}
    for row in rows:
        if isinstance(row.net_r, bool) or not isinstance(row.net_r, (int, float)):
            raise ValueError("finite_net_r_required")
        value = float(row.net_r)
        if not math.isfinite(value):
            raise ValueError("finite_net_r_required")
        day = _utc_day(row.source_open_utc)
        values.append(value)
        by_day[day] = by_day.get(day, 0.0) + value

    n = len(values)
    if n == 0:
        return ForwardReview(
            state="COLLECTING", n=0, distinct_utc_days=0, mean_r=None,
            profit_factor=None, win_rate=None, max_drawdown_r=None,
            max_positive_day_share=None, lower_80_mean_r=None,
            reasons=("no_valued_forward_trades",),
        )

    mean = sum(values) / n
    gains = sum(value for value in values if value > 0)
    losses = -sum(value for value in values if value < 0)
    pf = math.inf if losses == 0 and gains > 0 else (gains / losses if losses > 0 else None)
    wins = sum(value > 0 for value in values) / n

    equity = peak = max_dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    positive_days = [value for value in by_day.values() if value > 0]
    positive_sum = sum(positive_days)
    max_day_share = max(positive_days) / positive_sum if positive_sum > 0 else None

    if n >= 2:
        variance = sum((value - mean) ** 2 for value in values) / (n - 1)
        standard_error = math.sqrt(variance / n)
        lower80 = mean - 1.2815515655446004 * standard_error
    else:
        lower80 = None

    reasons: list[str] = []
    state: ReviewState
    if n < MIN_EARLY_N:
        state = "COLLECTING"
        reasons.append(f"need_at_least_{MIN_EARLY_N}_valued_trades")
    elif mean <= 0 or (pf is not None and pf < 0.90) or max_dd > 8.0:
        state = "REJECT_OR_RESEARCH"
        if mean <= 0:
            reasons.append("nonpositive_forward_expectancy")
        if pf is not None and pf < 0.90:
            reasons.append("forward_profit_factor_below_0_90")
        if max_dd > 8.0:
            reasons.append("forward_drawdown_above_8R")
    else:
        state = "EARLY_POSITIVE"
        reasons.append("positive_but_not_yet_review_eligible")
        review_checks = (
            n >= MIN_REVIEW_N,
            len(by_day) >= MIN_REVIEW_DAYS,
            mean >= MIN_REVIEW_MEAN_R,
            pf is not None and pf >= MIN_REVIEW_PF,
            max_dd <= MAX_REVIEW_DRAWDOWN_R,
            max_day_share is not None and max_day_share <= MAX_POSITIVE_DAY_SHARE,
            lower80 is not None and lower80 > 0,
        )
        if all(review_checks):
            state = "ELIGIBLE_FOR_REVIEW"
            reasons = ("pre_registered_forward_gates_passed",)
        else:
            if n < MIN_REVIEW_N:
                reasons.append(f"need_{MIN_REVIEW_N}_valued_trades_for_review")
            if len(by_day) < MIN_REVIEW_DAYS:
                reasons.append(f"need_{MIN_REVIEW_DAYS}_distinct_utc_days")
            if mean < MIN_REVIEW_MEAN_R:
                reasons.append("mean_below_0_10R")
            if pf is None or pf < MIN_REVIEW_PF:
                reasons.append("profit_factor_below_1_20")
            if max_dd > MAX_REVIEW_DRAWDOWN_R:
                reasons.append("drawdown_above_6R")
            if max_day_share is None or max_day_share > MAX_POSITIVE_DAY_SHARE:
                reasons.append("positive_result_too_day_concentrated")
            if lower80 is None or lower80 <= 0:
                reasons.append("lower_80pct_mean_not_positive")

    return ForwardReview(
        state=state,
        n=n,
        distinct_utc_days=len(by_day),
        mean_r=mean,
        profit_factor=pf,
        win_rate=wins,
        max_drawdown_r=max_dd,
        max_positive_day_share=max_day_share,
        lower_80_mean_r=lower80,
        reasons=tuple(reasons),
    )
