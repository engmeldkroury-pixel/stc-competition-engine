from __future__ import annotations

from math import exp, sqrt
from statistics import fmean

from .models import Bar


def _sma_at(values: list[float], i: int, period: int) -> float | None:
    start = i - period + 1
    if period <= 0 or start < 0:
        return None
    return fmean(values[start : i + 1])


def _stddev_at(values: list[float], i: int, period: int) -> float | None:
    start = i - period + 1
    if period <= 0 or start < 0:
        return None
    window = values[start : i + 1]
    mean = fmean(window)
    return sqrt(sum((x - mean) ** 2 for x in window) / period)


def _alma_at(
    values: list[float],
    i: int,
    period: int,
    *,
    offset: float,
    sigma: float,
) -> float | None:
    start = i - period + 1
    if period <= 0 or start < 0:
        return None
    m = offset * (period - 1)
    s = period / max(1e-9, sigma)
    weights = [exp(-((j - m) ** 2) / (2.0 * s * s)) for j in range(period)]
    den = sum(weights)
    if den <= 0:
        return None
    window = values[start : i + 1]
    return sum(value * weight for value, weight in zip(window, weights)) / den


def trendilo_signals(
    bars: list[Bar],
    *,
    change_length: int = 1,
    alma_length: int = 25,
    alma_offset: float = 0.85,
    alma_sigma: float = 6.0,
    rms_length: int = 20,
    rms_multiplier: float = 1.0,
) -> dict[int, float]:
    """Causal Trendilo-style ALMA percentage-change/RMS trend adapter.

    This is an independent implementation of the public algorithm description,
    using confirmed closes only. Signals are emitted only when the confirmed
    trend state changes between bullish and bearish.
    """
    closes = [bar.close for bar in bars]
    change = [0.0] * len(bars)
    for i in range(change_length, len(bars)):
        base = closes[i - change_length]
        if abs(base) > 1e-12:
            change[i] = (closes[i] - base) / base * 100.0

    alma: list[float | None] = [None] * len(bars)
    squared = [0.0] * len(bars)
    for i in range(len(bars)):
        alma[i] = _alma_at(
            change,
            i,
            alma_length,
            offset=alma_offset,
            sigma=alma_sigma,
        )
        if alma[i] is not None:
            squared[i] = float(alma[i]) ** 2

    out: dict[int, float] = {}
    state = 0
    for i in range(len(bars)):
        if alma[i] is None:
            continue
        rms_mean = _sma_at(squared, i, rms_length)
        if rms_mean is None:
            continue
        band = sqrt(max(0.0, rms_mean)) * rms_multiplier
        value = float(alma[i])
        current = 1 if value > band else -1 if value < -band else state
        if current != 0 and current != state:
            out[i] = float(current)
        if current != 0:
            state = current
    return out


def nadaraya_watson_nonrepaint_signals(
    bars: list[Bar],
    *,
    bandwidth: float = 8.0,
    window: int = 100,
    mae_length: int = 50,
    envelope_multiplier: float = 2.0,
) -> dict[int, float]:
    """Endpoint-only causal Nadaraya-Watson envelope research adapter.

    Only past/current confirmed closes contribute to each endpoint estimate.
    Historical estimates are never recomputed using future bars, so this is
    explicitly the non-repainting research mode, not centered smoothing.
    """
    closes = [bar.close for bar in bars]
    estimate: list[float | None] = [None] * len(bars)
    abs_error = [0.0] * len(bars)
    upper: list[float | None] = [None] * len(bars)
    lower: list[float | None] = [None] * len(bars)
    weights = [
        exp(-((lag * lag) / (2.0 * max(1e-9, bandwidth) ** 2)))
        for lag in range(window)
    ]

    for i in range(len(bars)):
        available = min(window, i + 1)
        den = sum(weights[:available])
        if den <= 0:
            continue
        estimate[i] = sum(
            closes[i - lag] * weights[lag]
            for lag in range(available)
        ) / den
        abs_error[i] = abs(closes[i] - float(estimate[i]))
        mae = _sma_at(abs_error, i, mae_length)
        if mae is None:
            continue
        width = mae * envelope_multiplier
        upper[i] = float(estimate[i]) + width
        lower[i] = float(estimate[i]) - width

    out: dict[int, float] = {}
    for i in range(1, len(bars)):
        if (
            upper[i] is None
            or lower[i] is None
            or upper[i - 1] is None
            or lower[i - 1] is None
        ):
            continue
        # Re-entry after an extreme is deliberately used instead of an
        # intrabar touch, so the benchmark waits for the confirmed close.
        if closes[i - 1] <= float(lower[i - 1]) and closes[i] > float(lower[i]):
            out[i] = 1.0
        elif closes[i - 1] >= float(upper[i - 1]) and closes[i] < float(upper[i]):
            out[i] = -1.0
    return out


def williams_vix_fix_dual_signals(
    bars: list[Bar],
    *,
    lookback: int = 22,
    bb_length: int = 20,
    bb_mult: float = 2.0,
    percentile_lookback: int = 50,
    percentile_factor: float = 0.85,
) -> dict[int, float]:
    """Causal dual-sided Williams Vix Fix reversal-context adapter.

    The original Vix Fix is a bottom detector. For symmetric research STC
    calculates the mirrored top condition as a separate context measure and
    emits a signal only after the confirmed spike condition releases.
    """
    closes = [bar.close for bar in bars]
    bottom = [0.0] * len(bars)
    top = [0.0] * len(bars)

    for i, bar in enumerate(bars):
        start = i - lookback + 1
        if start < 0:
            continue
        highest_close = max(closes[start : i + 1])
        lowest_close = min(closes[start : i + 1])
        if abs(highest_close) > 1e-12:
            bottom[i] = (highest_close - bar.low) / highest_close * 100.0
        if abs(lowest_close) > 1e-12:
            top[i] = (bar.high - lowest_close) / lowest_close * 100.0

    bottom_spike = [False] * len(bars)
    top_spike = [False] * len(bars)
    for i in range(len(bars)):
        b_mid = _sma_at(bottom, i, bb_length)
        b_sd = _stddev_at(bottom, i, bb_length)
        t_mid = _sma_at(top, i, bb_length)
        t_sd = _stddev_at(top, i, bb_length)
        p_start = i - percentile_lookback + 1
        if (
            b_mid is None
            or b_sd is None
            or t_mid is None
            or t_sd is None
            or p_start < 0
        ):
            continue
        bottom_range = max(bottom[p_start : i + 1]) * percentile_factor
        top_range = max(top[p_start : i + 1]) * percentile_factor
        bottom_spike[i] = bottom[i] >= max(b_mid + bb_mult * b_sd, bottom_range)
        top_spike[i] = top[i] >= max(t_mid + bb_mult * t_sd, top_range)

    out: dict[int, float] = {}
    for i in range(1, len(bars)):
        if bottom_spike[i - 1] and not bottom_spike[i]:
            out[i] = 1.0
        elif top_spike[i - 1] and not top_spike[i]:
            out[i] = -1.0
    return out
