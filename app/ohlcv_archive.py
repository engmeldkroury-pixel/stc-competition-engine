from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ARCHIVE_SCHEMA = "stc-ohlcv-archive-v1"
_REQUIRED_BAR_FIELDS = ("t", "o", "h", "l", "c", "v")


@dataclass(frozen=True)
class ArchiveMergeReport:
    symbol: str
    interval: str
    existing_bars: int
    incoming_bars: int
    added_bars: int
    replaced_bars: int
    unchanged_overlap_bars: int
    total_bars: int
    first_t: int | None
    last_t: int | None


def _normalized_bar(raw: dict[str, Any]) -> dict[str, float | int]:
    if not isinstance(raw, dict):
        raise ValueError("OHLCV bar must be an object")
    missing = [key for key in _REQUIRED_BAR_FIELDS if key not in raw]
    if missing:
        raise ValueError(f"OHLCV bar missing fields: {missing}")

    try:
        t = int(raw["t"])
        o = float(raw["o"])
        h = float(raw["h"])
        l = float(raw["l"])
        c = float(raw["c"])
        v = float(raw["v"])
    except (TypeError, ValueError) as exc:
        raise ValueError("OHLCV bar contains non-numeric values") from exc

    if t <= 0:
        raise ValueError("OHLCV timestamp must be positive")
    if h < max(o, l, c) or l > min(o, h, c):
        raise ValueError(f"Invalid OHLC envelope at t={t}")
    if v < 0:
        raise ValueError(f"Negative volume at t={t}")

    def clean(value: float) -> int | float:
        return int(value) if value.is_integer() else value

    return {
        "t": t,
        "o": clean(o),
        "h": clean(h),
        "l": clean(l),
        "c": clean(c),
        "v": clean(v),
    }


def _identity(payload: dict[str, Any]) -> tuple[str, str]:
    if not isinstance(payload, dict):
        raise ValueError("OHLCV payload must be an object")
    symbol = str(payload.get("symbol") or "").strip()
    interval = str(payload.get("interval") or "").strip()
    if not symbol or not interval:
        raise ValueError("OHLCV payload requires symbol and interval")
    return symbol, interval


def _bars(payload: dict[str, Any]) -> list[dict[str, float | int]]:
    raw_bars = payload.get("bars")
    if not isinstance(raw_bars, list):
        raise ValueError("OHLCV payload requires bars list")
    normalized = [_normalized_bar(row) for row in raw_bars]
    timestamps = [int(row["t"]) for row in normalized]
    if len(timestamps) != len(set(timestamps)):
        raise ValueError("OHLCV payload contains duplicate timestamps")
    return normalized


def merge_ohlcv_payloads(
    existing: dict[str, Any] | None,
    incoming: dict[str, Any],
) -> tuple[dict[str, Any], ArchiveMergeReport]:
    """Merge exact-provider OHLCV snapshots without losing provenance.

    Overlapping timestamps are de-duplicated. If TradingView later revises a bar,
    the incoming snapshot replaces the older copy and the replacement is counted.
    Symbol/timeframe mixing fails closed.
    """
    incoming_symbol, incoming_interval = _identity(incoming)
    incoming_bars = _bars(incoming)

    if existing is None:
        existing_symbol, existing_interval = incoming_symbol, incoming_interval
        existing_bars: list[dict[str, float | int]] = []
        previous_archive = {}
    else:
        existing_symbol, existing_interval = _identity(existing)
        if (existing_symbol, existing_interval) != (incoming_symbol, incoming_interval):
            raise ValueError(
                "Cannot merge different OHLCV identities: "
                f"{existing_symbol} {existing_interval} vs "
                f"{incoming_symbol} {incoming_interval}"
            )
        existing_bars = _bars(existing)
        previous_archive = existing.get("archive") if isinstance(existing.get("archive"), dict) else {}

    merged = {int(row["t"]): row for row in existing_bars}
    added = 0
    replaced = 0
    unchanged = 0
    for row in incoming_bars:
        t = int(row["t"])
        old = merged.get(t)
        if old is None:
            added += 1
        elif old == row:
            unchanged += 1
        else:
            replaced += 1
        merged[t] = row

    bars = [merged[t] for t in sorted(merged)]
    first_t = int(bars[0]["t"]) if bars else None
    last_t = int(bars[-1]["t"]) if bars else None
    snapshots_merged = int(previous_archive.get("snapshots_merged") or (1 if existing_bars else 0)) + 1

    archive_meta = {
        "schema_version": ARCHIVE_SCHEMA,
        "provider": "TradingView Official MCP",
        "snapshots_merged": snapshots_merged,
        "coverage_first_t": first_t,
        "coverage_last_t": last_t,
        "last_merge": {
            "incoming_bars": len(incoming_bars),
            "added_bars": added,
            "replaced_bars": replaced,
            "unchanged_overlap_bars": unchanged,
        },
    }
    payload = {
        "success": True,
        "symbol": incoming_symbol,
        "interval": incoming_interval,
        "count": len(bars),
        "bars": bars,
        "archive": archive_meta,
    }
    if incoming.get("notice"):
        payload["notice"] = incoming["notice"]

    report = ArchiveMergeReport(
        symbol=incoming_symbol,
        interval=incoming_interval,
        existing_bars=len(existing_bars),
        incoming_bars=len(incoming_bars),
        added_bars=added,
        replaced_bars=replaced,
        unchanged_overlap_bars=unchanged,
        total_bars=len(bars),
        first_t=first_t,
        last_t=last_t,
    )
    return payload, report


def merge_report_dict(report: ArchiveMergeReport) -> dict[str, Any]:
    return asdict(report)
