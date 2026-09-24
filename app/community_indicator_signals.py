from __future__ import annotations

from math import exp, sqrt
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


def _alma_full(
    values: list[float],
    period: int,
    *,
    offset: float = 0.85,
    sigma: float = 6.0,
) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if period <= 0:
        return out
    m = offset * (period - 1)
    s = period / max(sigma, 1e-9)
    weights = [exp(-((i - m) ** 2) / (2.0 * s * s)) for i in range(period)]
    den = sum(weights)
    if den <= 1e-12:
        return out
    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        out[i] = sum(v * w for v, w in zip(window, weights)) / den
    return out


def _endpoint_nadaraya_watson(
    values: list[float],
    i: int,
    *,
    lookback: int,
    bandwidth: float,
) -> float | None:
    start = i - lookback + 1
    if lookback <= 1 or start < 0:
        return None
    h = max(0.25, float(bandwidth))
    weights = [exp(-0.5 * (lag / h) ** 2) for lag in range(lookback)]
    den = sum(weights)
    if den <= 1e-12:
        return None
    # lag 0 is the current confirmed bar; larger lags are progressively older.
    return sum(values[i - lag] * weights[lag] for lag in range(lookback)) / den


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


def _rsi_full(values: list[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if period <= 0 or len(values) <= period:
        return out
    gains = [0.0] * len(values)
    losses = [0.0] * len(values)
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains[i] = max(0.0, change)
        losses[i] = max(0.0, -change)
    avg_gain = fmean(gains[1 : period + 1])
    avg_loss = fmean(losses[1 : period + 1])
    out[period] = 100.0 if avg_loss <= 1e-12 else 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
    for i in range(period + 1, len(values)):
        avg_gain = ((period - 1) * avg_gain + gains[i]) / period
        avg_loss = ((period - 1) * avg_loss + losses[i]) / period
        out[i] = 100.0 if avg_loss <= 1e-12 else 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
    return out


def _mfi_full(bars: list[Bar], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(bars)
    if period <= 0 or len(bars) <= period:
        return out
    typical = [(bar.high + bar.low + bar.close) / 3.0 for bar in bars]
    positive = [0.0] * len(bars)
    negative = [0.0] * len(bars)
    for i in range(1, len(bars)):
        flow = typical[i] * max(0.0, bars[i].volume)
        if typical[i] > typical[i - 1]:
            positive[i] = flow
        elif typical[i] < typical[i - 1]:
            negative[i] = flow
    for i in range(period, len(bars)):
        pos = sum(positive[i - period + 1 : i + 1])
        neg = sum(negative[i - period + 1 : i + 1])
        if pos <= 1e-12 and neg <= 1e-12:
            continue
        out[i] = 100.0 if neg <= 1e-12 else 100.0 - 100.0 / (1.0 + pos / neg)
    return out


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


def supertrend_signals(
    bars: list[Bar],
    *,
    atr_period: int = 10,
    multiplier: float = 3.0,
) -> dict[int, float]:
    atr = _atr_full(bars, atr_period)
    final_upper: list[float | None] = [None] * len(bars)
    final_lower: list[float | None] = [None] * len(bars)
    trend: list[int | None] = [None] * len(bars)
    out: dict[int, float] = {}

    for i, bar in enumerate(bars):
        if atr[i] is None:
            continue
        mid = (bar.high + bar.low) / 2.0
        basic_upper = mid + multiplier * float(atr[i])
        basic_lower = mid - multiplier * float(atr[i])
        if i == 0 or final_upper[i - 1] is None or final_lower[i - 1] is None:
            final_upper[i] = basic_upper
            final_lower[i] = basic_lower
            trend[i] = 1
            continue

        prev_close = bars[i - 1].close
        final_upper[i] = (
            basic_upper
            if basic_upper < float(final_upper[i - 1]) or prev_close > float(final_upper[i - 1])
            else float(final_upper[i - 1])
        )
        final_lower[i] = (
            basic_lower
            if basic_lower > float(final_lower[i - 1]) or prev_close < float(final_lower[i - 1])
            else float(final_lower[i - 1])
        )

        prev_trend = int(trend[i - 1] or 1)
        if prev_trend < 0 and bar.close > float(final_upper[i]):
            trend[i] = 1
        elif prev_trend > 0 and bar.close < float(final_lower[i]):
            trend[i] = -1
        else:
            trend[i] = prev_trend
        if trend[i] != prev_trend:
            out[i] = float(trend[i])
    return out


def chandelier_exit_signals(
    bars: list[Bar],
    *,
    period: int = 22,
    multiplier: float = 3.0,
) -> dict[int, float]:
    atr = _atr_full(bars, period)
    long_stop: list[float | None] = [None] * len(bars)
    short_stop: list[float | None] = [None] * len(bars)
    direction: list[int | None] = [None] * len(bars)
    out: dict[int, float] = {}

    for i in range(len(bars)):
        if atr[i] is None or i - period + 1 < 0:
            continue
        high = max(bar.high for bar in bars[i - period + 1 : i + 1])
        low = min(bar.low for bar in bars[i - period + 1 : i + 1])
        raw_long = high - multiplier * float(atr[i])
        raw_short = low + multiplier * float(atr[i])

        if i == 0 or long_stop[i - 1] is None or short_stop[i - 1] is None:
            long_stop[i] = raw_long
            short_stop[i] = raw_short
            direction[i] = 1
            continue

        prev_close = bars[i - 1].close
        prev_long = float(long_stop[i - 1])
        prev_short = float(short_stop[i - 1])
        long_stop[i] = max(raw_long, prev_long) if prev_close > prev_long else raw_long
        short_stop[i] = min(raw_short, prev_short) if prev_close < prev_short else raw_short

        prev_direction = int(direction[i - 1] or 1)
        if bars[i].close > prev_short:
            direction[i] = 1
        elif bars[i].close < prev_long:
            direction[i] = -1
        else:
            direction[i] = prev_direction
        if direction[i] != prev_direction:
            out[i] = float(direction[i])
    return out


def schaff_trend_cycle_signals(
    bars: list[Bar],
    *,
    cycle_length: int = 10,
    fast_length: int = 23,
    slow_length: int = 50,
    smoothing: float = 0.5,
) -> dict[int, float]:
    closes = [bar.close for bar in bars]
    fast = _ema_full(closes, fast_length)
    slow = _ema_full(closes, slow_length)
    macd_line: list[float | None] = [None] * len(bars)
    for i in range(len(bars)):
        if fast[i] is not None and slow[i] is not None:
            macd_line[i] = float(fast[i]) - float(slow[i])

    d1: list[float | None] = [None] * len(bars)
    d2: list[float | None] = [None] * len(bars)
    stc: list[float | None] = [None] * len(bars)
    alpha = max(0.01, min(0.99, float(smoothing)))

    for i in range(len(bars)):
        start = i - cycle_length + 1
        if start < 0 or macd_line[i] is None:
            continue
        m_window = [x for x in macd_line[start : i + 1] if x is not None]
        if len(m_window) < cycle_length:
            continue
        low_m = min(m_window)
        high_m = max(m_window)
        raw_k1 = 0.0 if high_m == low_m else 100.0 * (float(macd_line[i]) - low_m) / (high_m - low_m)
        prev_d1 = d1[i - 1] if i > 0 and d1[i - 1] is not None else raw_k1
        d1[i] = float(prev_d1) + alpha * (raw_k1 - float(prev_d1))

        d1_window = [x for x in d1[start : i + 1] if x is not None]
        if len(d1_window) < cycle_length:
            continue
        low_d1 = min(d1_window)
        high_d1 = max(d1_window)
        raw_k2 = 0.0 if high_d1 == low_d1 else 100.0 * (float(d1[i]) - low_d1) / (high_d1 - low_d1)
        prev_d2 = d2[i - 1] if i > 0 and d2[i - 1] is not None else raw_k2
        d2[i] = float(prev_d2) + alpha * (raw_k2 - float(prev_d2))
        stc[i] = d2[i]

    out: dict[int, float] = {}
    for i in range(2, len(bars)):
        if stc[i] is None or stc[i - 1] is None or stc[i - 2] is None:
            continue
        now = float(stc[i])
        prev = float(stc[i - 1])
        older = float(stc[i - 2])
        if older >= prev < now and prev <= 25.0:
            out[i] = 1.0
        elif older <= prev > now and prev >= 75.0:
            out[i] = -1.0
        elif prev <= 50.0 < now:
            out[i] = 0.65
        elif prev >= 50.0 > now:
            out[i] = -0.65
    return out


def range_filter_signals(
    bars: list[Bar],
    *,
    sampling_period: int = 100,
    range_multiplier: float = 3.0,
) -> dict[int, float]:
    closes = [bar.close for bar in bars]
    changes = [0.0] * len(bars)
    for i in range(1, len(bars)):
        changes[i] = abs(closes[i] - closes[i - 1])
    first = _ema_full(changes, sampling_period)
    first_clean = [0.0 if value is None else float(value) for value in first]
    second = _ema_full(first_clean, max(1, sampling_period * 2 - 1))

    filt: list[float | None] = [None] * len(bars)
    direction: list[int] = [0] * len(bars)
    out: dict[int, float] = {}
    for i in range(len(bars)):
        if second[i] is None:
            continue
        smooth_range = float(second[i]) * range_multiplier
        if i == 0 or filt[i - 1] is None:
            filt[i] = closes[i]
            continue
        prev_filter = float(filt[i - 1])
        if closes[i] > prev_filter:
            filt[i] = max(prev_filter, closes[i] - smooth_range)
        elif closes[i] < prev_filter:
            filt[i] = min(prev_filter, closes[i] + smooth_range)
        else:
            filt[i] = prev_filter

        rising = float(filt[i]) > prev_filter
        falling = float(filt[i]) < prev_filter
        current = 1 if closes[i] > float(filt[i]) and rising else -1 if closes[i] < float(filt[i]) and falling else direction[i - 1]
        direction[i] = current
        if current != 0 and current != direction[i - 1]:
            out[i] = float(current)
    return out


def alphatrend_signals(
    bars: list[Bar],
    *,
    period: int = 14,
    coefficient: float = 1.0,
    force_rsi: bool = False,
) -> dict[int, float]:
    """Confirmed AlphaTrend-style line/2-bar-offset crosses.

    Uses MFI only when volume is sufficiently present; otherwise RSI is used,
    matching the published fallback intent for symbols without usable volume.
    """
    closes = [bar.close for bar in bars]
    atr = _atr_full(bars, period)
    zero_volume_fraction = (
        sum(bar.volume <= 0 for bar in bars) / len(bars) if bars else 1.0
    )
    use_rsi = force_rsi or zero_volume_fraction > 0.50
    momentum = _rsi_full(closes, period) if use_rsi else _mfi_full(bars, period)
    line: list[float | None] = [None] * len(bars)
    out: dict[int, float] = {}

    for i, bar in enumerate(bars):
        if atr[i] is None or momentum[i] is None:
            continue
        up = bar.low - float(atr[i]) * coefficient
        down = bar.high + float(atr[i]) * coefficient
        prev = line[i - 1] if i > 0 else None
        if float(momentum[i]) >= 50.0:
            line[i] = up if prev is None else max(up, float(prev))
        else:
            line[i] = down if prev is None else min(down, float(prev))

        if i < 3 or line[i - 1] is None or line[i - 2] is None or line[i - 3] is None:
            continue
        now_diff = float(line[i]) - float(line[i - 2])
        prev_diff = float(line[i - 1]) - float(line[i - 3])
        if prev_diff <= 0 < now_diff:
            out[i] = 1.0
        elif prev_diff >= 0 > now_diff:
            out[i] = -1.0
    return out


def optimized_trend_tracker_signals(
    bars: list[Bar],
    *,
    length: int = 2,
    percent: float = 1.4,
    cmo_length: int = 9,
) -> dict[int, float]:
    """Confirmed default-VAR Optimized Trend Tracker support-line crosses."""
    closes = [bar.close for bar in bars]
    var: list[float | None] = [None] * len(bars)
    long_stop: list[float | None] = [None] * len(bars)
    short_stop: list[float | None] = [None] * len(bars)
    direction: list[int] = [1] * len(bars)
    ott: list[float | None] = [None] * len(bars)
    alpha = 2.0 / (length + 1.0)
    pct = max(0.0001, percent) / 100.0
    out: dict[int, float] = {}

    up_moves = [0.0] * len(bars)
    down_moves = [0.0] * len(bars)
    for i in range(1, len(bars)):
        change = closes[i] - closes[i - 1]
        up_moves[i] = max(0.0, change)
        down_moves[i] = max(0.0, -change)

    for i in range(len(bars)):
        start = max(1, i - cmo_length + 1)
        up_sum = sum(up_moves[start : i + 1])
        down_sum = sum(down_moves[start : i + 1])
        den = up_sum + down_sum
        abs_cmo = abs((up_sum - down_sum) / den) if den > 1e-12 else 0.0
        prev_var = var[i - 1] if i > 0 and var[i - 1] is not None else closes[i]
        var[i] = alpha * abs_cmo * closes[i] + (1.0 - alpha * abs_cmo) * float(prev_var)

        raw_long = float(var[i]) * (1.0 - pct)
        raw_short = float(var[i]) * (1.0 + pct)
        if i == 0 or long_stop[i - 1] is None or short_stop[i - 1] is None:
            long_stop[i] = raw_long
            short_stop[i] = raw_short
            direction[i] = 1
        else:
            prev_long = float(long_stop[i - 1])
            prev_short = float(short_stop[i - 1])
            prev_var_value = float(var[i - 1]) if var[i - 1] is not None else float(var[i])
            long_stop[i] = max(raw_long, prev_long) if float(var[i]) > prev_long else raw_long
            short_stop[i] = min(raw_short, prev_short) if float(var[i]) < prev_short else raw_short
            prev_direction = direction[i - 1]
            if prev_direction < 0 and float(var[i]) > prev_short:
                direction[i] = 1
            elif prev_direction > 0 and float(var[i]) < prev_long:
                direction[i] = -1
            else:
                direction[i] = prev_direction

        mt = float(long_stop[i]) if direction[i] > 0 else float(short_stop[i])
        ott[i] = mt * ((200.0 + percent) / 200.0) if float(var[i]) > mt else mt * ((200.0 - percent) / 200.0)

        if i == 0 or ott[i - 1] is None or var[i - 1] is None:
            continue
        prev_diff = float(var[i - 1]) - float(ott[i - 1])
        diff = float(var[i]) - float(ott[i])
        if prev_diff <= 0 < diff:
            out[i] = 1.0
        elif prev_diff >= 0 > diff:
            out[i] = -1.0
    return out



def _qqe_state(
    bars: list[Bar],
    *,
    rsi_period: int = 6,
    smoothing: int = 5,
    factor: float = 3.0,
) -> tuple[list[float | None], list[float | None], list[int]]:
    """Return smoothed RSI, QQE trailing line and directional trend state."""
    closes = [bar.close for bar in bars]
    rsi = _rsi_full(closes, rsi_period)
    rsi_clean = [50.0 if value is None else float(value) for value in rsi]
    rsi_ma = _ema_full(rsi_clean, smoothing)
    delta = [0.0] * len(bars)
    for i in range(1, len(bars)):
        if rsi_ma[i] is not None and rsi_ma[i - 1] is not None:
            delta[i] = abs(float(rsi_ma[i]) - float(rsi_ma[i - 1]))

    wilders = max(1, rsi_period * 2 - 1)
    atr_rsi = _ema_full(delta, wilders)
    atr_clean = [0.0 if value is None else float(value) for value in atr_rsi]
    smooth_atr = _ema_full(atr_clean, wilders)

    long_band: list[float | None] = [None] * len(bars)
    short_band: list[float | None] = [None] * len(bars)
    trail: list[float | None] = [None] * len(bars)
    trend = [0] * len(bars)

    for i in range(len(bars)):
        if rsi_ma[i] is None or smooth_atr[i] is None:
            continue
        value = float(rsi_ma[i])
        dar = float(smooth_atr[i]) * factor
        new_long = value - dar
        new_short = value + dar

        if i == 0 or long_band[i - 1] is None or short_band[i - 1] is None or rsi_ma[i - 1] is None:
            long_band[i] = new_long
            short_band[i] = new_short
            trend[i] = 1
            trail[i] = new_long
            continue

        prev_value = float(rsi_ma[i - 1])
        prev_long = float(long_band[i - 1])
        prev_short = float(short_band[i - 1])
        long_band[i] = max(prev_long, new_long) if prev_value > prev_long and value > prev_long else new_long
        short_band[i] = min(prev_short, new_short) if prev_value < prev_short and value < prev_short else new_short

        prev_trend = trend[i - 1] if trend[i - 1] else 1
        if prev_value <= prev_short and value > prev_short:
            trend[i] = 1
        elif prev_value >= prev_long and value < prev_long:
            trend[i] = -1
        else:
            trend[i] = prev_trend
        trail[i] = float(long_band[i]) if trend[i] > 0 else float(short_band[i])

    return rsi_ma, trail, trend


def qqe_mod_signals(
    bars: list[Bar],
    *,
    rsi_period: int = 6,
    smoothing: int = 5,
    fast_factor: float = 3.0,
    slow_factor: float = 1.61,
    threshold: float = 3.0,
    bb_length: int = 50,
    bb_mult: float = 0.35,
) -> dict[int, float]:
    """Independent causal QQE MOD-style agreement adapter.

    Two QQE states must agree. The slower/secondary momentum must clear a
    threshold and the primary QQE must clear a Bollinger-style zero-line band.
    """
    primary_rsi, primary_trail, primary_trend = _qqe_state(
        bars, rsi_period=rsi_period, smoothing=smoothing, factor=fast_factor
    )
    secondary_rsi, _, secondary_trend = _qqe_state(
        bars, rsi_period=rsi_period, smoothing=smoothing, factor=slow_factor
    )
    primary_delta = [
        0.0 if primary_rsi[i] is None or primary_trail[i] is None
        else float(primary_rsi[i]) - float(primary_trail[i])
        for i in range(len(bars))
    ]
    out: dict[int, float] = {}
    state = 0
    for i in range(len(bars)):
        if primary_rsi[i] is None or secondary_rsi[i] is None:
            continue
        basis = _sma_at(primary_delta, i, bb_length)
        dev = _stddev_at(primary_delta, i, bb_length)
        if basis is None or dev is None:
            continue
        upper = basis + bb_mult * dev
        lower = basis - bb_mult * dev
        primary_momentum = float(primary_rsi[i]) - 50.0
        secondary_momentum = float(secondary_rsi[i]) - 50.0

        bullish = (
            primary_trend[i] > 0
            and secondary_trend[i] > 0
            and secondary_momentum > threshold
            and primary_delta[i] > upper
            and primary_momentum > 0
        )
        bearish = (
            primary_trend[i] < 0
            and secondary_trend[i] < 0
            and secondary_momentum < -threshold
            and primary_delta[i] < lower
            and primary_momentum < 0
        )
        current = 1 if bullish else -1 if bearish else 0
        if current != 0 and current != state:
            out[i] = float(current)
        if current != 0:
            state = current
    return out


def _ssl_hybrid_state(
    bars: list[Bar],
    *,
    baseline_length: int = 60,
    ssl_length: int = 15,
) -> tuple[list[float | None], list[int]]:
    """Simplified causal SSL-Hybrid baseline/SSL1 state for research."""
    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    lows = [bar.low for bar in bars]
    baseline = _ema_full(closes, baseline_length)
    high_ma = _ema_full(highs, ssl_length)
    low_ma = _ema_full(lows, ssl_length)
    state = [0] * len(bars)
    for i in range(len(bars)):
        if baseline[i] is None or high_ma[i] is None or low_ma[i] is None:
            continue
        prev = state[i - 1] if i > 0 else 0
        if closes[i] > float(high_ma[i]) and closes[i] > float(baseline[i]):
            state[i] = 1
        elif closes[i] < float(low_ma[i]) and closes[i] < float(baseline[i]):
            state[i] = -1
        else:
            state[i] = prev
    return baseline, state


def ssl_hybrid_signals(
    bars: list[Bar],
    *,
    baseline_length: int = 60,
    ssl_length: int = 15,
) -> dict[int, float]:
    """Baseline/SSL1 entry adapter inspired by the public SSL Hybrid strategy."""
    _, state = _ssl_hybrid_state(
        bars, baseline_length=baseline_length, ssl_length=ssl_length
    )
    out: dict[int, float] = {}
    for i in range(1, len(bars)):
        if state[i] != 0 and state[i] != state[i - 1]:
            out[i] = float(state[i])
    return out


def _macd_full(
    values: list[float],
    fast_length: int,
    slow_length: int,
    signal_length: int = 9,
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    fast = _ema_full(values, fast_length)
    slow = _ema_full(values, slow_length)
    line: list[float | None] = [None] * len(values)
    for i in range(len(values)):
        if fast[i] is not None and slow[i] is not None:
            line[i] = float(fast[i]) - float(slow[i])
    clean = [0.0 if value is None else float(value) for value in line]
    signal = _ema_full(clean, signal_length)
    hist: list[float | None] = [None] * len(values)
    for i in range(len(values)):
        if line[i] is not None and signal[i] is not None:
            hist[i] = float(line[i]) - float(signal[i])
    return line, signal, hist


def _waddah_attar_state(
    bars: list[Bar],
    *,
    fast_length: int = 20,
    slow_length: int = 40,
    bb_length: int = 20,
    bb_mult: float = 2.0,
    sensitivity: float = 150.0,
    dead_zone_atr_period: int = 100,
    dead_zone_mult: float = 3.7,
) -> tuple[list[int], list[float | None], list[float | None]]:
    closes = [bar.close for bar in bars]
    macd, _, _ = _macd_full(closes, fast_length, slow_length)
    atr = _atr_full(bars, dead_zone_atr_period)
    direction = [0] * len(bars)
    trend_power: list[float | None] = [None] * len(bars)
    explosion: list[float | None] = [None] * len(bars)

    for i in range(1, len(bars)):
        if macd[i] is None or macd[i - 1] is None or atr[i] is None:
            continue
        basis = _sma_at(closes, i, bb_length)
        dev = _stddev_at(closes, i, bb_length)
        if basis is None or dev is None:
            continue
        explosion_line = (basis + bb_mult * dev) - (basis - bb_mult * dev)
        power_signed = (float(macd[i]) - float(macd[i - 1])) * sensitivity
        power = abs(power_signed)
        dead_zone = float(atr[i]) * dead_zone_mult
        trend_power[i] = power
        explosion[i] = explosion_line
        if power > explosion_line and explosion_line > dead_zone:
            direction[i] = 1 if power_signed > 0 else -1 if power_signed < 0 else 0
    return direction, trend_power, explosion


def waddah_attar_explosion_signals(
    bars: list[Bar],
    *,
    fast_length: int = 20,
    slow_length: int = 40,
    bb_length: int = 20,
    bb_mult: float = 2.0,
    sensitivity: float = 150.0,
    dead_zone_atr_period: int = 100,
    dead_zone_mult: float = 3.7,
) -> dict[int, float]:
    """Confirmed Waddah Attar Explosion-style momentum/explosion entries."""
    direction, power, explosion = _waddah_attar_state(
        bars,
        fast_length=fast_length,
        slow_length=slow_length,
        bb_length=bb_length,
        bb_mult=bb_mult,
        sensitivity=sensitivity,
        dead_zone_atr_period=dead_zone_atr_period,
        dead_zone_mult=dead_zone_mult,
    )
    out: dict[int, float] = {}
    state = 0
    for i in range(2, len(bars)):
        current = direction[i]
        if current == 0 or power[i] is None or power[i - 1] is None or explosion[i] is None or explosion[i - 1] is None:
            continue
        strengthening = float(power[i]) > float(power[i - 1]) and float(explosion[i]) >= float(explosion[i - 1])
        if strengthening and current != state:
            out[i] = float(current)
            state = current
    return out


def qqe_ssl_wae_composite_signals(
    bars: list[Bar],
    *,
    qqe_rsi_period: int = 6,
    qqe_smoothing: int = 5,
    qqe_fast_factor: float = 3.0,
    qqe_slow_factor: float = 1.61,
    qqe_threshold: float = 3.0,
    ssl_baseline_length: int = 60,
    ssl_length: int = 15,
    wae_fast_length: int = 20,
    wae_slow_length: int = 40,
    wae_sensitivity: float = 150.0,
) -> dict[int, float]:
    """Causal composite based on the public QQE+SSL+WAE entry specification.

    QQE supplies the leading direction change. Entry is emitted only when SSL
    baseline state and WAE momentum/explosion direction agree on the same
    confirmed bar.
    """
    qqe = qqe_mod_signals(
        bars,
        rsi_period=qqe_rsi_period,
        smoothing=qqe_smoothing,
        fast_factor=qqe_fast_factor,
        slow_factor=qqe_slow_factor,
        threshold=qqe_threshold,
    )
    _, ssl_state = _ssl_hybrid_state(
        bars,
        baseline_length=ssl_baseline_length,
        ssl_length=ssl_length,
    )
    wae_state, power, explosion = _waddah_attar_state(
        bars,
        fast_length=wae_fast_length,
        slow_length=wae_slow_length,
        sensitivity=wae_sensitivity,
    )

    out: dict[int, float] = {}
    for i, qqe_direction in qqe.items():
        d = 1 if qqe_direction > 0 else -1
        if (
            i < len(ssl_state)
            and ssl_state[i] == d
            and wae_state[i] == d
            and power[i] is not None
            and explosion[i] is not None
        ):
            out[i] = float(d)
    return out


def halftrend_signals(
    bars: list[Bar],
    *,
    amplitude: int = 2,
) -> dict[int, float]:
    """Confirmed HalfTrend swing/SMA state transitions.

    The ATR/channel portion of HalfTrend is visual/risk context in the public
    indicator; STC benchmarks only the causal trend flip state.
    """
    if amplitude < 1 or len(bars) < max(3, amplitude):
        return {}

    trend = 0
    next_trend = 0
    max_low_price = bars[0].low
    min_high_price = bars[0].high
    out: dict[int, float] = {}

    for i in range(len(bars)):
        start_i = max(0, i - amplitude + 1)
        window = bars[start_i : i + 1]
        if len(window) < amplitude:
            continue

        high_price = max(bar.high for bar in window)
        low_price = min(bar.low for bar in window)
        high_ma = fmean(bar.high for bar in window)
        low_ma = fmean(bar.low for bar in window)
        prev_low = bars[i - 1].low if i > 0 else bars[i].low
        prev_high = bars[i - 1].high if i > 0 else bars[i].high
        previous_trend = trend

        if next_trend == 1:
            max_low_price = max(low_price, max_low_price)
            if high_ma < max_low_price and bars[i].close < prev_low:
                trend = 1
                next_trend = 0
                min_high_price = high_price
        else:
            min_high_price = min(high_price, min_high_price)
            if low_ma > min_high_price and bars[i].close > prev_high:
                trend = 0
                next_trend = 1
                max_low_price = low_price

        if trend != previous_trend:
            out[i] = 1.0 if trend == 0 else -1.0

    return out


def trendilo_signals(
    bars: list[Bar],
    *,
    smoothing: int = 1,
    lookback: int = 50,
    alma_offset: float = 0.85,
    alma_sigma: float = 6.0,
    band_multiplier: float = 1.0,
    band_length: int | None = None,
) -> dict[int, float]:
    """Confirmed Trendilo state transitions with no future-bar inputs.

    This preserves the parameter/semantic contract used by the frozen Trendilo
    research records already stored in the STC shadow registry.
    """
    if smoothing < 1 or lookback < 2:
        return {}
    closes = [bar.close for bar in bars]
    pch = [0.0] * len(bars)
    for i in range(smoothing, len(bars)):
        current = closes[i]
        if abs(current) <= 1e-15:
            continue
        pch[i] = (current - closes[i - smoothing]) / current * 100.0

    avpch = _alma_full(pch, lookback, offset=alma_offset, sigma=alma_sigma)
    rms_length = int(band_length or lookback)
    state: list[int] = [0] * len(bars)
    out: dict[int, float] = {}
    for i in range(len(bars)):
        if avpch[i] is None or i - rms_length + 1 < 0:
            continue
        window_values = avpch[i - rms_length + 1 : i + 1]
        if any(value is None for value in window_values):
            continue
        rms = band_multiplier * sqrt(
            sum(float(value) ** 2 for value in window_values if value is not None) / rms_length
        )
        value = float(avpch[i])
        current_state = 1 if value > rms else -1 if value < -rms else 0
        state[i] = current_state
        prev_state = state[i - 1] if i > 0 else 0
        if current_state in (-1, 1) and current_state != prev_state:
            out[i] = float(current_state)
    return out


def nadaraya_watson_endpoint_signals(
    bars: list[Bar],
    *,
    window: int = 500,
    bandwidth: float = 8.0,
    multiplier: float = 3.0,
    deviation_length: int | None = None,
) -> dict[int, float]:
    """Canonical endpoint-only non-repainting Nadaraya-Watson adapter.

    The component id and parameter schema intentionally match the frozen
    research/shadow records already stored by STC.
    """
    dev_len = max(10, int(deviation_length or min(window, 499)))
    return nadaraya_watson_nonrepaint_signals(
        bars,
        lookback=window,
        bandwidth=bandwidth,
        deviation_length=dev_len,
        envelope_multiplier=multiplier,
    )


def nadaraya_watson_nonrepaint_signals(
    bars: list[Bar],
    *,
    lookback: int = 50,
    bandwidth: float = 8.0,
    deviation_length: int = 50,
    envelope_multiplier: float = 2.5,
) -> dict[int, float]:
    """Endpoint-only non-repainting Nadaraya-Watson envelope adapter.

    Only past and current confirmed bars are used. The signal is contrarian:
    crossing below the lower envelope emits LONG; crossing above the upper
    envelope emits SHORT.
    """
    closes = [bar.close for bar in bars]
    estimate: list[float | None] = [None] * len(bars)
    abs_error: list[float | None] = [None] * len(bars)
    upper: list[float | None] = [None] * len(bars)
    lower: list[float | None] = [None] * len(bars)
    out: dict[int, float] = {}

    for i in range(len(bars)):
        est = _endpoint_nadaraya_watson(
            closes,
            i,
            lookback=lookback,
            bandwidth=bandwidth,
        )
        if est is None:
            continue
        estimate[i] = est
        abs_error[i] = abs(closes[i] - est)
        start_i = i - deviation_length + 1
        if start_i < 0:
            continue
        errors = [x for x in abs_error[start_i : i + 1] if x is not None]
        if len(errors) < deviation_length:
            continue
        width = fmean(float(x) for x in errors) * envelope_multiplier
        upper[i] = est + width
        lower[i] = est - width
        if i == 0 or upper[i - 1] is None or lower[i - 1] is None:
            continue
        if closes[i - 1] >= float(lower[i - 1]) and closes[i] < float(lower[i]):
            out[i] = 1.0
        elif closes[i - 1] <= float(upper[i - 1]) and closes[i] > float(upper[i]):
            out[i] = -1.0
    return out


def rsi_kernel_pivot_signals(
    bars: list[Bar],
    *,
    rsi_period: int = 14,
    pivot_length: int = 12,
    bandwidth: float = 4.0,
    min_samples: int = 12,
    dominance_ratio: float = 1.30,
) -> dict[int, float]:
    """Causal RSI/KDE pivot-family adapter.

    Pivot RSI samples enter the training pool only when the required right-hand
    bars have already closed. Current-bar KDE similarity is therefore computed
    from previously confirmed pivot samples only; no future bars leak into the
    live decision.
    """
    closes = [bar.close for bar in bars]
    rsi = _rsi_full(closes, rsi_period)
    low_samples: list[float] = []
    high_samples: list[float] = []
    out: dict[int, float] = {}
    state = 0
    h = max(0.25, float(bandwidth))

    def density(value: float, samples: list[float]) -> float:
        if not samples:
            return 0.0
        return fmean(exp(-0.5 * ((value - sample) / h) ** 2) for sample in samples)

    for i in range(len(bars)):
        pivot_i = i - pivot_length
        if pivot_i >= pivot_length and rsi[pivot_i] is not None:
            lo_start = pivot_i - pivot_length
            hi_end = i
            pivot_low = bars[pivot_i].low
            pivot_high = bars[pivot_i].high
            is_low = all(pivot_low <= bars[j].low for j in range(lo_start, hi_end + 1) if j != pivot_i)
            is_high = all(pivot_high >= bars[j].high for j in range(lo_start, hi_end + 1) if j != pivot_i)
            if is_low:
                low_samples.append(float(rsi[pivot_i]))
            if is_high:
                high_samples.append(float(rsi[pivot_i]))
            # Bound memory so the model adapts without using an ever-growing pool.
            if len(low_samples) > 300:
                low_samples = low_samples[-300:]
            if len(high_samples) > 300:
                high_samples = high_samples[-300:]

        if rsi[i] is None or len(low_samples) < min_samples or len(high_samples) < min_samples:
            continue
        value = float(rsi[i])
        low_d = density(value, low_samples)
        high_d = density(value, high_samples)
        bullish = low_d > high_d * dominance_ratio
        bearish = high_d > low_d * dominance_ratio
        current = 1 if bullish else -1 if bearish else 0
        if current != 0 and current != state:
            out[i] = float(current)
        if current != 0:
            state = current
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
    if indicator_id == "supertrend_kivanc":
        return supertrend_signals(bars, **params)
    if indicator_id == "chandelier_exit_everget":
        return chandelier_exit_signals(bars, **params)
    if indicator_id == "schaff_trend_cycle":
        return schaff_trend_cycle_signals(bars, **params)
    if indicator_id == "range_filter_guikroth":
        return range_filter_signals(bars, **params)
    if indicator_id == "alphatrend":
        return alphatrend_signals(bars, **params)
    if indicator_id == "optimized_trend_tracker":
        return optimized_trend_tracker_signals(bars, **params)
    if indicator_id == "qqe_mod":
        return qqe_mod_signals(bars, **params)
    if indicator_id == "ssl_hybrid":
        return ssl_hybrid_signals(bars, **params)
    if indicator_id == "waddah_attar_explosion":
        return waddah_attar_explosion_signals(bars, **params)
    if indicator_id == "qqe_ssl_wae_composite":
        return qqe_ssl_wae_composite_signals(bars, **params)
    if indicator_id == "halftrend_everget":
        return halftrend_signals(bars, **params)
    if indicator_id == "trendilo":
        return trendilo_signals(bars, **params)
    if indicator_id == "nadaraya_watson_endpoint_nonrepaint":
        return nadaraya_watson_endpoint_signals(bars, **params)
    if indicator_id == "nadaraya_watson_envelope_luxalgo":
        return nadaraya_watson_nonrepaint_signals(bars, **params)
    if indicator_id == "rsi_kernel_optimized_flux":
        return rsi_kernel_pivot_signals(bars, **params)
    raise KeyError(f"Community indicator is not implemented for causal benchmarking: {indicator_id}")
