from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class SpotBar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def parse_closed_spot_bars(rows: list[list[Any]]) -> list[SpotBar]:
    """Convert exchange kline rows into immutable closed spot bars.

    Expected row order:
    open_time_ms, open, high, low, close, volume, ...
    """
    bars: list[SpotBar] = []
    for row in rows:
        bars.append(
            SpotBar(
                timestamp=datetime.fromtimestamp(
                    int(row[0]) / 1000,
                    tz=timezone.utc,
                ),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
        )
    return bars


def validate_spot_series(
    bars: list[SpotBar],
    minimum_bars: int = 900,
) -> dict[str, Any]:
    if len(bars) < minimum_bars:
        return {
            "valid": False,
            "reason": "insufficient_history",
            "bars": len(bars),
        }

    ordered = all(
        bars[index].timestamp < bars[index + 1].timestamp
        for index in range(len(bars) - 1)
    )

    positive_prices = all(
        bar.open > 0
        and bar.high > 0
        and bar.low > 0
        and bar.close > 0
        for bar in bars
    )

    return {
        "valid": ordered and positive_prices,
        "bars": len(bars),
        "chronological": ordered,
        "positive_prices": positive_prices,
        "closed_bars_only": True,
    }
