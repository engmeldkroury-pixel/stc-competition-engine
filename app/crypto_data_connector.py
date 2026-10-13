"""Spot candle parsing and fail-closed research series quality checks.

For Binance klines, row[0] is open-time in milliseconds and row[6] is
close-time. A six-field synthetic row is accepted for parsing compatibility,
but its finalization cannot be established and it is NOT valid research data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class SpotBar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime | None = None


def parse_closed_spot_bars(rows: list[list[Any]]) -> list[SpotBar]:
    """Parse spot klines; preserve close-time evidence, never fabricate it."""
    bars: list[SpotBar] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 6:
            raise ValueError("Each Spot kline must have at least six fields")
        try:
            opened = datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc)
            closed = (
                datetime.fromtimestamp(int(row[6]) / 1000, tz=timezone.utc)
                if len(row) >= 7 and row[6] is not None
                else None
            )
            prices = [float(value) for value in row[1:6]]
        except (TypeError, ValueError, OverflowError, OSError) as exc:
            raise ValueError("Invalid Spot kline timestamp or OHLCV value") from exc
        bars.append(
            SpotBar(
                timestamp=opened,
                open=prices[0],
                high=prices[1],
                low=prices[2],
                close=prices[3],
                volume=prices[4],
                close_time=closed,
            )
        )
    return bars


def validate_spot_series(
    bars: list[SpotBar],
    minimum_bars: int = 900,
    *,
    as_of_utc: datetime | None = None,
) -> dict[str, Any]:
    """Reject inconsistent, stale/unclosed or unproven Spot research history.

    \`as_of_utc\` makes the closed-bar check deterministic for historical tests.
    Exchange close-time is necessary but NOT sufficient to prove provenance.
    """
    if len(bars) < minimum_bars:
        return {"valid": False, "reason": "insufficient_history", "bars": len(bars)}
    now = as_of_utc or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("as_of_utc must be timezone-aware")

    def utc_timestamp(time: datetime | None) -> bool:
        return (
            isinstance(time, datetime)
            and time.tzinfo is not None
            and time.utcoffset() is not None
            and time.utcoffset().total_seconds() == 0
        )

    utc_times = all(
        utc_timestamp(bar.timestamp)
        and (bar.close_time is None or utc_timestamp(bar.close_time))
        for bar in bars
    )
    ordered = utc_times and all(
        bars[index].timestamp < bars[index + 1].timestamp
        for index in range(len(bars) - 1)
    )
    finite_numbers = all(
        all(isfinite(value) for value in (bar.open, bar.high, bar.low, bar.close, bar.volume))
        for bar in bars
    )
    positive_prices = finite_numbers and all(
        bar.open > 0 and bar.high > 0 and bar.low > 0 and bar.close > 0
        for bar in bars
    )
    consistent_ohlc = positive_prices and all(
        bar.low <= min(bar.open, bar.close)
        and bar.high >= max(bar.open, bar.close)
        and bar.high >= bar.low
        for bar in bars
    )
    nonnegative_volume = finite_numbers and all(bar.volume >= 0 for bar in bars)
    closure_verified = utc_times and all(
        bar.close_time is not None
        and bar.timestamp < bar.close_time
        and bar.close_time < now
        for bar in bars
    )
    rules = (
        ("utc_timestamps", utc_times),
        ("chronological", ordered),
        ("finite_numbers", finite_numbers),
        ("positive_prices", positive_prices),
        ("ohlc_consistent", consistent_ohlc),
        ("nonnegative_volume", nonnegative_volume),
        ("closed_bars_only", closure_verified),
    )
    valid = all(passed for _, passed in rules)
    return {
        "valid": valid,
        "reason": "valid" if valid else next(name for name, passed in rules if not passed),
        "bars": len(bars),
        **dict(rules),
    }
