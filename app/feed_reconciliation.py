from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from statistics import median
from typing import Any


@dataclass(frozen=True)
class FeedReconciliation:
    symbol: str
    interval: str
    reference_bars: int
    candidate_bars: int
    overlap_bars: int
    overlap_ratio_reference: float
    median_abs_close_bps: float | None
    p95_abs_close_bps: float | None
    median_abs_ohlc_bps: float | None
    return_correlation: float | None
    status: str
    live_calibration_authority: bool = False


def _identity(payload: dict[str, Any]) -> tuple[str, str]:
    symbol = str(payload.get("symbol") or "").strip()
    interval = str(payload.get("interval") or "").strip()
    if not symbol or not interval:
        raise ValueError("OHLCV payload requires symbol and interval")
    return symbol, interval


def _bars(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows = payload.get("bars")
    if not isinstance(rows, list):
        raise ValueError("OHLCV payload requires bars list")
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("OHLCV bar must be an object")
        try:
            t = int(row["t"])
            o = float(row["o"])
            h = float(row["h"])
            l = float(row["l"])
            c = float(row["c"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("OHLCV bar requires numeric t/o/h/l/c") from exc
        if t in out:
            raise ValueError("OHLCV payload contains duplicate timestamps")
        out[t] = {"t": t, "o": o, "h": h, "l": l, "c": c}
    return out


def _abs_bps(reference: float, candidate: float) -> float:
    denominator = abs(reference)
    if denominator <= 1e-12:
        return 0.0 if abs(candidate) <= 1e-12 else float("inf")
    return abs(candidate - reference) / denominator * 10000.0


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * q
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    weight = index - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def _returns(values: list[float]) -> list[float]:
    out = []
    for previous, current in zip(values, values[1:]):
        if abs(previous) <= 1e-12:
            continue
        out.append(current / previous - 1.0)
    return out


def _correlation(a: list[float], b: list[float]) -> float | None:
    n = min(len(a), len(b))
    if n < 3:
        return None
    a = a[:n]
    b = b[:n]
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    da = [value - mean_a for value in a]
    db = [value - mean_b for value in b]
    denom = sqrt(sum(value * value for value in da) * sum(value * value for value in db))
    if denom <= 1e-18:
        return None
    return sum(x * y for x, y in zip(da, db)) / denom


def reconcile_ohlcv_feeds(
    reference: dict[str, Any],
    candidate: dict[str, Any],
    *,
    min_overlap_bars: int = 200,
    max_median_close_bps: float | None = None,
    max_p95_close_bps: float | None = None,
    min_return_correlation: float | None = None,
) -> FeedReconciliation:
    """Compare two OHLCV feeds on identical timestamps without granting authority.

    Thresholds are optional. Without explicit acceptance thresholds, the result
    stays REVIEW_REQUIRED even if the feeds look very close.
    """
    ref_symbol, ref_interval = _identity(reference)
    cand_symbol, cand_interval = _identity(candidate)
    if (ref_symbol, ref_interval) != (cand_symbol, cand_interval):
        raise ValueError(
            f"Feed identity mismatch: {ref_symbol} {ref_interval} vs "
            f"{cand_symbol} {cand_interval}"
        )
    if min_overlap_bars < 3:
        raise ValueError("min_overlap_bars must be at least 3")

    ref = _bars(reference)
    cand = _bars(candidate)
    common = sorted(set(ref).intersection(cand))
    overlap_ratio = len(common) / len(ref) if ref else 0.0

    if not common:
        return FeedReconciliation(
            symbol=ref_symbol,
            interval=ref_interval,
            reference_bars=len(ref),
            candidate_bars=len(cand),
            overlap_bars=0,
            overlap_ratio_reference=overlap_ratio,
            median_abs_close_bps=None,
            p95_abs_close_bps=None,
            median_abs_ohlc_bps=None,
            return_correlation=None,
            status="NO_OVERLAP",
        )

    close_diffs = []
    ohlc_diffs = []
    ref_closes = []
    cand_closes = []
    for t in common:
        r = ref[t]
        c = cand[t]
        close_diffs.append(_abs_bps(r["c"], c["c"]))
        for key in ("o", "h", "l", "c"):
            ohlc_diffs.append(_abs_bps(r[key], c[key]))
        ref_closes.append(r["c"])
        cand_closes.append(c["c"])

    corr = _correlation(_returns(ref_closes), _returns(cand_closes))
    median_close = median(close_diffs)
    p95_close = _percentile(close_diffs, 0.95)
    median_ohlc = median(ohlc_diffs)

    if len(common) < min_overlap_bars:
        status = "INSUFFICIENT_OVERLAP"
    else:
        thresholds = (
            max_median_close_bps,
            max_p95_close_bps,
            min_return_correlation,
        )
        if all(value is None for value in thresholds):
            status = "REVIEW_REQUIRED"
        else:
            checks = []
            if max_median_close_bps is not None:
                checks.append(median_close <= max_median_close_bps)
            if max_p95_close_bps is not None:
                checks.append(p95_close is not None and p95_close <= max_p95_close_bps)
            if min_return_correlation is not None:
                checks.append(corr is not None and corr >= min_return_correlation)
            status = "CANDIDATE_MATCH" if checks and all(checks) else "MISMATCH"

    return FeedReconciliation(
        symbol=ref_symbol,
        interval=ref_interval,
        reference_bars=len(ref),
        candidate_bars=len(cand),
        overlap_bars=len(common),
        overlap_ratio_reference=overlap_ratio,
        median_abs_close_bps=median_close,
        p95_abs_close_bps=p95_close,
        median_abs_ohlc_bps=median_ohlc,
        return_correlation=corr,
        status=status,
    )


def reconciliation_dict(result: FeedReconciliation) -> dict[str, Any]:
    return asdict(result)
