
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
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


def bars_fingerprint(bars: list[Bar]) -> str:
    """Return a deterministic SHA-256 fingerprint for an exact OHLCV series."""
    digest = sha256()
    for bar in bars:
        ts = int(bar.timestamp.timestamp())
        digest.update(
            (
                f"{ts}|{bar.open:.12g}|{bar.high:.12g}|{bar.low:.12g}|"
                f"{bar.close:.12g}|{bar.volume:.12g}\n"
            ).encode("utf-8")
        )
    return digest.hexdigest()


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



def _aggregate_group(group: list[Bar]) -> Bar:
    if not group:
        raise ValueError("Cannot aggregate an empty bar group")
    return Bar(
        timestamp=group[0].timestamp,
        open=group[0].open,
        high=max(b.high for b in group),
        low=min(b.low for b in group),
        close=group[-1].close,
        volume=sum(b.volume for b in group),
    )


def resample_hourly_to_two_hour(bars: list[Bar]) -> list[Bar]:
    """Build deterministic 2h research bars from ordered 1h bars.

    Bars are bucketed on even UTC hours. Missing hours are never invented;
    partial buckets are dropped so a 2h bar always represents two source bars.
    """
    ordered = normalize_confirmed_bars(bars)
    buckets: dict[tuple[int, int, int, int], list[Bar]] = {}
    for bar in ordered:
        ts = bar.timestamp.astimezone(UTC)
        even_hour = ts.hour - (ts.hour % 2)
        key = (ts.year, ts.month, ts.day, even_hour)
        buckets.setdefault(key, []).append(bar)

    out: list[Bar] = []
    for key in sorted(buckets):
        group = sorted(buckets[key], key=lambda b: b.timestamp)
        if len(group) != 2:
            continue
        spacing = (group[1].timestamp - group[0].timestamp).total_seconds()
        if spacing < 55 * 60 or spacing > 65 * 60:
            continue
        out.append(_aggregate_group(group))
    return out


def resample_daily_to_monthly(bars: list[Bar]) -> list[Bar]:
    """Build calendar-month research bars from daily data without filling gaps."""
    ordered = normalize_confirmed_bars(bars)
    buckets: dict[tuple[int, int], list[Bar]] = {}
    for bar in ordered:
        ts = bar.timestamp.astimezone(UTC)
        buckets.setdefault((ts.year, ts.month), []).append(bar)
    return [
        _aggregate_group(sorted(buckets[key], key=lambda b: b.timestamp))
        for key in sorted(buckets)
        if buckets[key]
    ]


def research_timeframe_bundle(
    *,
    bars_15m: list[Bar],
    bars_1h: list[Bar],
    bars_4h: list[Bar],
    bars_1d: list[Bar],
    bars_5m: list[Bar] | None = None,
    bars_30m: list[Bar] | None = None,
) -> dict[str, list[Bar]]:
    """Create the standard STC research matrix timeframes.

    2h is derived from exact-provider 1h bars because the verified TradingView
    OHLCV connector does not expose a native 2h interval. Monthly is derived
    from exact-provider daily bars. Native 5m/30m series are included when
    supplied. No cross-provider substitution is allowed.
    """
    bundle = {
        "15": drop_latest_unconfirmed_bar(normalize_confirmed_bars(bars_15m)),
        "60": drop_latest_unconfirmed_bar(normalize_confirmed_bars(bars_1h)),
        "120": drop_latest_unconfirmed_bar(resample_hourly_to_two_hour(bars_1h)),
        "240": drop_latest_unconfirmed_bar(normalize_confirmed_bars(bars_4h)),
        "1D": drop_latest_unconfirmed_bar(normalize_confirmed_bars(bars_1d)),
        "1M": drop_latest_unconfirmed_bar(resample_daily_to_monthly(bars_1d)),
    }
    if bars_5m is not None:
        bundle["5"] = drop_latest_unconfirmed_bar(normalize_confirmed_bars(bars_5m))
    if bars_30m is not None:
        bundle["30"] = drop_latest_unconfirmed_bar(normalize_confirmed_bars(bars_30m))
    return bundle
