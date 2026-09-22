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
    withheld_unconfirmed_bars: int
    removed_existing_unconfirmed_bars: int
    total_bars: int
    first_t: int | None
    last_t: int | None
    latest_input_t: int | None
    confirmed_through_t: int | None


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


def _last_bar_may_change(payload: dict[str, Any]) -> bool:
    notice = str(payload.get("notice") or "").lower()
    return "last bar" in notice and (
        "may still change" in notice
        or "not a live price" in notice
    )


def merge_ohlcv_payloads(
    existing: dict[str, Any] | None,
    incoming: dict[str, Any],
) -> tuple[dict[str, Any], ArchiveMergeReport]:
    """Merge exact-provider OHLCV snapshots without losing provenance.

    Overlapping timestamps are de-duplicated. If TradingView later revises a
    confirmed bar, the incoming snapshot replaces the older copy and the
    replacement is counted. When the provider notice says the final bar may
    still change, that bar is withheld from the archive until a later snapshot
    proves it is no longer the tail. Symbol/timeframe mixing fails closed.
    """
    incoming_symbol, incoming_interval = _identity(incoming)
    incoming_bars = sorted(_bars(incoming), key=lambda row: int(row["t"]))
    latest_input_t = int(incoming_bars[-1]["t"]) if incoming_bars else None
    withhold_last = bool(incoming_bars) and _last_bar_may_change(incoming)
    withheld_unconfirmed_bars = 1 if withhold_last else 0
    pending_t = latest_input_t if withhold_last else None
    confirmed_incoming = incoming_bars[:-1] if withhold_last else incoming_bars
    confirmed_through_t = (
        int(confirmed_incoming[-1]["t"]) if confirmed_incoming else None
    )

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
    removed_existing_unconfirmed_bars = 0
    if pending_t is not None and pending_t in merged:
        merged.pop(pending_t)
        removed_existing_unconfirmed_bars = 1

    added = 0
    replaced = 0
    unchanged = 0
    for row in confirmed_incoming:
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
        "latest_input_t": latest_input_t,
        "confirmed_through_t": confirmed_through_t,
        "withheld_unconfirmed_t": pending_t,
        "last_merge": {
            "incoming_bars": len(incoming_bars),
            "confirmed_incoming_bars": len(confirmed_incoming),
            "withheld_unconfirmed_bars": withheld_unconfirmed_bars,
            "removed_existing_unconfirmed_bars": removed_existing_unconfirmed_bars,
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
        withheld_unconfirmed_bars=withheld_unconfirmed_bars,
        removed_existing_unconfirmed_bars=removed_existing_unconfirmed_bars,
        total_bars=len(bars),
        first_t=first_t,
        last_t=last_t,
        latest_input_t=latest_input_t,
        confirmed_through_t=confirmed_through_t,
    )
    return payload, report


def merge_report_dict(report: ArchiveMergeReport) -> dict[str, Any]:
    return asdict(report)
