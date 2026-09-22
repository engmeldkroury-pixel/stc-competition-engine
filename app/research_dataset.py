
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import median
from typing import Any

from .models import Bar


UTC = timezone.utc


@dataclass(frozen=True)
class DataQualityReport:
    symbol: str
    interval: str
    bars: int
    start_utc: datetime | None
    end_utc: datetime | None
    duplicate_timestamps: int
    non_monotonic_pairs: int
    large_gap_count: int
    median_spacing_seconds: float | None
    zero_volume_fraction: float
    quality_ok: bool
    notes: tuple[str, ...]


def bars_from_tradingview_ohlcv(payload: dict[str, Any]) -> list[Bar]:
    raw = payload.get("bars")
    if not isinstance(raw, list):
        raise ValueError("TradingView OHLCV payload must contain a bars list")
    out: list[Bar] = []
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError("Each OHLCV row must be an object")
        try:
            ts = datetime.fromtimestamp(int(row["t"]), tz=UTC)
            out.append(
                Bar(
                    timestamp=ts,
                    open=float(row["o"]),
                    high=float(row["h"]),
                    low=float(row["l"]),
                    close=float(row["c"]),
                    volume=float(row.get("v") or 0.0),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid TradingView OHLCV row: {row}") from exc
    return out


def data_quality_report(symbol: str, interval: str, bars: list[Bar]) -> DataQualityReport:
    if not bars:
        return DataQualityReport(
            symbol=symbol,
            interval=interval,
            bars=0,
            start_utc=None,
            end_utc=None,
            duplicate_timestamps=0,
            non_monotonic_pairs=0,
            large_gap_count=0,
            median_spacing_seconds=None,
            zero_volume_fraction=0.0,
            quality_ok=False,
            notes=("no_bars",),
        )

    timestamps = [b.timestamp for b in bars]
    duplicates = len(timestamps) - len(set(timestamps))
    non_monotonic = sum(timestamps[i] <= timestamps[i - 1] for i in range(1, len(timestamps)))
    spacings = [
        (timestamps[i] - timestamps[i - 1]).total_seconds()
        for i in range(1, len(timestamps))
        if timestamps[i] > timestamps[i - 1]
    ]
    med = median(spacings) if spacings else None
    gap_count = 0
    if med and med > 0:
        gap_count = sum(x > med * 8.0 for x in spacings)

    zero_volume = sum(b.volume <= 0 for b in bars) / len(bars)
    notes: list[str] = []
    if duplicates:
        notes.append("duplicate_timestamps")
    if non_monotonic:
        notes.append("non_monotonic_timestamps")
    if gap_count:
        notes.append("large_time_gaps_present")
    if zero_volume > 0.50:
        notes.append("mostly_zero_volume")
    if len(bars) < 900:
        notes.append("insufficient_for_walk_forward_900_bar_minimum")

    fatal = duplicates > 0 or non_monotonic > 0 or len(bars) < 900
    return DataQualityReport(
        symbol=symbol,
        interval=interval,
        bars=len(bars),
        start_utc=timestamps[0],
        end_utc=timestamps[-1],
        duplicate_timestamps=duplicates,
        non_monotonic_pairs=non_monotonic,
        large_gap_count=gap_count,
        median_spacing_seconds=med,
        zero_volume_fraction=zero_volume,
        quality_ok=not fatal,
        notes=tuple(notes),
    )


def normalize_confirmed_bars(bars: list[Bar]) -> list[Bar]:
    """Return strictly ordered de-duplicated bars without inventing missing data."""
    by_time: dict[datetime, Bar] = {}
    for bar in bars:
        by_time[bar.timestamp] = bar
    return [by_time[t] for t in sorted(by_time)]


def drop_latest_unconfirmed_bar(bars: list[Bar]) -> list[Bar]:
    """Research helper for delayed feeds whose latest bar may still mutate."""
    return bars[:-1] if bars else []
