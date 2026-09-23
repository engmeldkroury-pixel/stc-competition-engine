from __future__ import annotations

from math import sqrt
from statistics import fmean

from .models import Bar


def _ema_full(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if period <= 0 or len(values) < period:
        return out
    alpha = 2.0 / (period + 1.0)
    value = fmean(values[:period])
    out[period - 1] = value
    for i in range(period, len(values)):
        value = alpha * values[i] + (1.0 - alpha) * value
        out[i] = value
    return out


def _sma_at(values: list[float], i: int, period: int) -> float | None:
    start = i - period + 1
    if period <= 0 or start < 0:
        return None
    return fmean(values[start : i + 1])


def _wma_at(values: list[float], i: int, period: int) -> float | None:
    start = i - period + 1
    if period <= 0 or start < 0:
        return None
    window = values[start : i + 1]
    weights = range(1, period + 1)
    den = period * (period + 1) / 2.0
    return sum(v * w for v, w in zip(window, weights)) / den


def _hma_full(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    half = max(1, period // 2)
    root = max(1, int(sqrt(period)))
    diff: list[float | None] = [None] * len(values)
    for i in range(len(values)):
        fast = _wma_at(values, i, half)
        slow = _wma_at(values, i, period)
        if fast is not None and slow is not None:
            diff[i] = 2.0 * fast - slow
    for i in range(len(values)):
        if i - root + 1 < 0:
            continue
        window = diff[i - root + 1 : i + 1]
        if any(value is None for value in window):
            continue
        clean = [float(value) for value in window if value is not None]
        weights = range(1, root + 1)
        den = root * (root + 1) / 2.0
        out[i] = sum(v * w for v, w in zip(clean, weights)) / den
    return out


def _atr_full(bars: list[Bar], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(bars)
    if len(bars) < period + 1:
        return out
    trs: list[float] = [0.0] * len(bars)
    for i in range(1, len(bars)):
        prev = bars[i - 1].close
        bar = bars[i]
        trs[i] = max(bar.high - bar.low, abs(bar.high - prev), abs(bar.low - prev))
    value = fmean(trs[1 : period + 1])
    out[period] = value
    for i in range(period + 1, len(bars)):
        value = ((period - 1) * value + trs[i]) / period
        out[i] = value
    return out


def atr_by_index(bars: list[Bar], period: int = 14) -> dict[int, float]:
    return {i: float(value) for i, value in enumerate(_atr_full(bars, period)) if value is not None}


def _stddev_at(values: list[float], i: int, period: int) -> float | None:
    start = i - period + 1
    if start < 0:
        return None
    window = values[start : i + 1]
    mean = fmean(window)
    return sqrt(sum((x - mean) ** 2 for x in window) / period)


def _linreg_last(values: list[float], i: int, period: int) -> float | None:
    start = i - period + 1
    if start < 0:
        return None
    y = values[start : i + 1]
    x_mean = (period - 1) / 2.0
    y_mean = fmean(y)
    den = sum((x - x_mean) ** 2 for x in range(period))
    if den <= 0:
        return y[-1]
    slope = sum((x - x_mean) * (y[x] - y_mean) for x in range(period)) / den
    intercept = y_mean - slope * x_mean
    return intercept + slope * (period - 1)


def ut_bot_signals(
    bars: list[Bar],
    *,
    atr_period: int = 10,
    key_value: float = 1.0,
) -> dict[int, float]:
    """Causal ATR-trailing-stop family inspired by the public UT Bot logic.

    Signals are generated only from confirmed bar closes. This is an independent
    conceptual implementation for research; it is not a copy of third-party code.
    """
    closes = [bar.close for bar in bars]
    atr = _atr_full(bars, atr_period)
    trail: list[float | None] = [None] * len(bars)
    out: dict[int, float] = {}
    for i in range(len(bars)):
        if atr[i] is None:
            continue
        loss = key_value * float(atr[i])
        prev_trail = trail[i - 1] if i > 0 else None
        prev_close = closes[i - 1] if i > 0 else closes[i]
        if prev_trail is None:
            trail[i] = closes[i] - loss
        elif closes[i] > prev_trail and prev_close > prev_trail:
            trail[i] = max(prev_trail, closes[i] - loss)
        elif closes[i] < prev_trail and prev_close < prev_trail:
            trail[i] = min(prev_trail, closes[i] + loss)
        elif closes[i] > prev_trail:
            trail[i] = closes[i] - loss
        else:
            trail[i] = closes[i] + loss

        if i == 0 or trail[i - 1] is None:
            continue
        previous = float(trail[i - 1])
        if prev_close <= previous and closes[i] > previous:
            out[i] = 1.0
        elif prev_close >= previous and closes[i] < previous:
            out[i] = -1.0
    return out


def squeeze_momentum_signals(
    bars: list[Bar],
    *,
    length: int = 20,
    bb_mult: float = 2.0,
    kc_mult: float = 1.5,
) -> dict[int, float]:
    """Confirmed-bar squeeze-release momentum signal.

    Uses the corrected public intent: Bollinger multiplier 2.0 and Keltner
    multiplier 1.5, with linear-regression momentum after a squeeze release.
    """
    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    lows = [bar.low for bar in bars]
    atr = _atr_full(bars, length)
    momentum: list[float | None] = [None] * len(bars)
    squeeze_on: list[bool | None] = [None] * len(bars)
    out: dict[int, float] = {}

    for i in range(len(bars)):
        mid = _sma_at(closes, i, length)
        sd = _stddev_at(closes, i, length)
        if mid is None or sd is None or atr[i] is None:
            continue
        bb_upper = mid + bb_mult * sd
        bb_lower = mid - bb_mult * sd
        kc_upper = mid + kc_mult * float(atr[i])
        kc_lower = mid - kc_mult * float(atr[i])
        squeeze_on[i] = bb_lower > kc_lower and bb_upper < kc_upper

        start = i - length + 1
        if start < 0:
            continue
        highest = max(highs[start : i + 1])
        lowest = min(lows[start : i + 1])
        baseline = (highest + lowest) / 4.0 + mid / 2.0
        detrended = closes.copy()
        detrended[i] = closes[i] - baseline
        # Build the exact causal detrended window rather than using any future bars.
        window: list[float] = []
        for j in range(start, i + 1):
            j_start = j - length + 1
            if j_start < 0:
                window.append(0.0)
                continue
            j_mid = _sma_at(closes, j, length)
            if j_mid is None:
                window.append(0.0)
                continue
            j_high = max(highs[j_start : j + 1])
            j_low = min(lows[j_start : j + 1])
            j_base = (j_high + j_low) / 4.0 + j_mid / 2.0
            window.append(closes[j] - j_base)
        if len(window) == length:
            x_mean = (length - 1) / 2.0
            y_mean = fmean(window)
            den = sum((x - x_mean) ** 2 for x in range(length))
            slope = 0.0 if den <= 0 else sum(
                (x - x_mean) * (window[x] - y_mean) for x in range(length)
            ) / den
            momentum[i] = y_mean + slope * ((length - 1) - x_mean)

        if i < 1 or momentum[i] is None or momentum[i - 1] is None:
            continue
        released = squeeze_on[i - 1] is True and squeeze_on[i] is False
        if released:
            if float(momentum[i]) > 0:
                out[i] = 1.0
            elif float(momentum[i]) < 0:
                out[i] = -1.0
        elif squeeze_on[i] is False:
            # Continuation state is allowed, but only while momentum strengthens.
            if float(momentum[i]) > 0 and float(momentum[i]) > float(momentum[i - 1]):
                out[i] = 0.65
            elif float(momentum[i]) < 0 and float(momentum[i]) < float(momentum[i - 1]):
                out[i] = -0.65
    return out


def wavetrend_signals(
    bars: list[Bar],
    *,
    channel_length: int = 10,
    average_length: int = 21,
    signal_length: int = 4,
) -> dict[int, float]:
    ap = [(bar.high + bar.low + bar.close) / 3.0 for bar in bars]
    esa = _ema_full(ap, channel_length)
    abs_dev: list[float] = [0.0] * len(bars)
    for i in range(len(bars)):
        if esa[i] is not None:
            abs_dev[i] = abs(ap[i] - float(esa[i]))
    dev = _ema_full(abs_dev, channel_length)
    ci: list[float] = [0.0] * len(bars)
    valid_ci: list[bool] = [False] * len(bars)
    for i in range(len(bars)):
        if esa[i] is None or dev[i] is None or float(dev[i]) <= 1e-12:
            continue
        ci[i] = (ap[i] - float(esa[i])) / (0.015 * float(dev[i]))
        valid_ci[i] = True
    wt1 = _ema_full(ci, average_length)
    wt2: list[float | None] = [None] * len(bars)
    for i in range(len(bars)):
        if i - signal_length + 1 < 0:
            continue
        window = wt1[i - signal_length + 1 : i + 1]
        if any(x is None for x in window):
            continue
        wt2[i] = fmean(float(x) for x in window if x is not None)

    out: dict[int, float] = {}
    for i in range(1, len(bars)):
        if not valid_ci[i] or wt1[i] is None or wt2[i] is None or wt1[i - 1] is None or wt2[i - 1] is None:
            continue
        prev_diff = float(wt1[i - 1]) - float(wt2[i - 1])
        diff = float(wt1[i]) - float(wt2[i])
        if prev_diff <= 0 < diff:
            out[i] = 1.0 if float(wt1[i]) <= 0 else 0.65
        elif prev_diff >= 0 > diff:
            out[i] = -1.0 if float(wt1[i]) >= 0 else -0.65
    return out


def hull_suite_signals(
    bars: list[Bar],
    *,
    length: int = 55,
) -> dict[int, float]:
    closes = [bar.close for bar in bars]
    hull = _hma_full(closes, length)
    out: dict[int, float] = {}
    for i in range(2, len(bars)):
        if hull[i] is None or hull[i - 1] is None or hull[i - 2] is None:
            continue
        now = float(hull[i])
        prev = float(hull[i - 1])
        older = float(hull[i - 2])
        if now > prev >= older:
            out[i] = 1.0
        elif now < prev <= older:
            out[i] = -1.0
    return out


def indicator_signal_series(
    indicator_id: str,
    bars: list[Bar],
    *,
    parameters: dict | None = None,
) -> dict[int, float]:
    params = dict(parameters or {})
    if indicator_id == "ut_bot_alerts":
        return ut_bot_signals(bars, **params)
    if indicator_id == "squeeze_momentum_lazybear":
        return squeeze_momentum_signals(bars, **params)
    if indicator_id == "wavetrend_crosses":
        return wavetrend_signals(bars, **params)
    if indicator_id == "hull_suite":
        return hull_suite_signals(bars, **params)
    raise KeyError(f"Community indicator is not implemented for causal benchmarking: {indicator_id}")
