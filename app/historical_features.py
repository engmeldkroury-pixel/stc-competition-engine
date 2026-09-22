
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import sqrt
from statistics import fmean, median, pstdev
from typing import Mapping

from .analysis import atr, ema, macd, rsi
from .evidence_engine import EvidenceObservation, make_observation
from .indicator_catalog import FEATURE_FAMILIES
from .models import Bar


@dataclass(frozen=True)
class HistoricalFeatureSnapshot:
    symbol: str
    timeframe: str
    timestamp: datetime
    values: Mapping[str, float]
    observations: tuple[EvidenceObservation, ...]


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _sign(x: float) -> float:
    return 1.0 if x > 1e-12 else -1.0 if x < -1e-12 else 0.0


def _safe(num: float, den: float, default: float = 0.0) -> float:
    return default if abs(den) <= 1e-12 else num / den


def _sma(values: list[float], n: int) -> float:
    return fmean(values[-n:])


def _slope(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    xm = (n - 1) / 2.0
    ym = fmean(values)
    den = sum((i - xm) ** 2 for i in range(n))
    return _safe(sum((i - xm) * (y - ym) for i, y in enumerate(values)), den)


def _efficiency(values: list[float]) -> float:
    path = sum(abs(values[i] - values[i - 1]) for i in range(1, len(values)))
    return _clamp(_safe(values[-1] - values[0], path))


def _rank(values: list[float], current: float) -> float:
    if not values:
        return 0.5
    lt = sum(x < current for x in values)
    eq = sum(x == current for x in values)
    return (lt + 0.5 * eq) / len(values)


def _stochastic(highs: list[float], lows: list[float], closes: list[float], n: int = 14) -> float:
    hi = max(highs[-n:])
    lo = min(lows[-n:])
    return 50.0 if hi <= lo else 100.0 * (closes[-1] - lo) / (hi - lo)


def _cci(highs: list[float], lows: list[float], closes: list[float], n: int = 20) -> float:
    tp = [(h + l + c) / 3.0 for h, l, c in zip(highs[-n:], lows[-n:], closes[-n:])]
    avg = fmean(tp)
    mad = fmean(abs(x - avg) for x in tp)
    return _safe(tp[-1] - avg, 0.015 * mad)


def _williams(highs: list[float], lows: list[float], closes: list[float], n: int = 14) -> float:
    hi = max(highs[-n:])
    lo = min(lows[-n:])
    return -50.0 if hi <= lo else -100.0 * (hi - closes[-1]) / (hi - lo)


def _adx_dmi(bars: list[Bar], n: int = 14) -> tuple[float, float]:
    plus = 0.0
    minus = 0.0
    tr = 0.0
    for i in range(len(bars) - n, len(bars)):
        up = bars[i].high - bars[i - 1].high
        down = bars[i - 1].low - bars[i].low
        plus += up if up > down and up > 0 else 0.0
        minus += down if down > up and down > 0 else 0.0
        pc = bars[i - 1].close
        tr += max(bars[i].high - bars[i].low, abs(bars[i].high - pc), abs(bars[i].low - pc))
    pdi = 100.0 * _safe(plus, tr)
    mdi = 100.0 * _safe(minus, tr)
    direction = _safe(pdi - mdi, pdi + mdi)
    adx_proxy = 100.0 * abs(direction)
    return adx_proxy, direction


def _aroon(highs: list[float], lows: list[float], n: int = 25) -> float:
    h = highs[-n:]
    l = lows[-n:]
    hi_i = max(range(len(h)), key=lambda i: h[i])
    lo_i = min(range(len(l)), key=lambda i: l[i])
    return _clamp((hi_i - lo_i) / max(1, n - 1))


def _vwap(bars: list[Bar]) -> float:
    den = sum(max(0.0, b.volume) for b in bars)
    if den <= 0:
        return fmean((b.high + b.low + b.close) / 3.0 for b in bars)
    return sum(((b.high + b.low + b.close) / 3.0) * max(0.0, b.volume) for b in bars) / den


def _obv_direction(bars: list[Bar], n: int = 20) -> float:
    sample = bars[-(n + 1):]
    obv = [0.0]
    value = 0.0
    for i in range(1, len(sample)):
        value += sample[i].volume if sample[i].close > sample[i - 1].close else -sample[i].volume if sample[i].close < sample[i - 1].close else 0.0
        obv.append(value)
    scale = sum(max(0.0, b.volume) for b in sample[1:])
    return _clamp(_safe(_slope(obv) * n * 6.0, scale + 1e-9))


def _cmf(bars: list[Bar], n: int = 20) -> float:
    num = 0.0
    den = 0.0
    for b in bars[-n:]:
        rng = b.high - b.low
        mult = 0.0 if rng <= 0 else ((b.close - b.low) - (b.high - b.close)) / rng
        num += mult * b.volume
        den += b.volume
    return _clamp(_safe(num, den))


def _mfi(bars: list[Bar], n: int = 14) -> float:
    sample = bars[-(n + 1):]
    tp = [(b.high + b.low + b.close) / 3.0 for b in sample]
    pos = 0.0
    neg = 0.0
    for i in range(1, len(sample)):
        flow = tp[i] * max(0.0, sample[i].volume)
        if tp[i] > tp[i - 1]:
            pos += flow
        elif tp[i] < tp[i - 1]:
            neg += flow
    if neg <= 0:
        return 100.0 if pos > 0 else 50.0
    ratio = pos / neg
    return 100.0 - 100.0 / (1.0 + ratio)


def _volume_poc(bars: list[Bar], bins: int = 16) -> float:
    sample = bars[-80:]
    lo = min(b.low for b in sample)
    hi = max(b.high for b in sample)
    if hi <= lo:
        return sample[-1].close
    width = (hi - lo) / bins
    buckets = [0.0] * bins
    for b in sample:
        p = (b.high + b.low + b.close) / 3.0
        idx = min(bins - 1, max(0, int((p - lo) / width)))
        buckets[idx] += max(0.0, b.volume)
    idx = max(range(bins), key=lambda i: buckets[i])
    return lo + (idx + 0.5) * width


def _catalog() -> dict[str, str]:
    return {feature: family.name for family in FEATURE_FAMILIES for feature in family.features}


def extract_feature_snapshot(symbol: str, timeframe: str, bars: list[Bar]) -> HistoricalFeatureSnapshot:
    if len(bars) < 260:
        raise ValueError("Need at least 260 confirmed bars for full historical features")

    bars = bars[-1000:]
    o = [b.open for b in bars]
    h = [b.high for b in bars]
    l = [b.low for b in bars]
    c = [b.close for b in bars]
    v = [max(0.0, b.volume) for b in bars]
    last = bars[-1]
    prev = bars[-2]
    a = max(atr(bars, 14), abs(last.close) * 1e-8, 1e-9)
    rets = [_safe(c[i], c[i - 1], 1.0) - 1.0 for i in range(1, len(c))]
    vol20 = pstdev(rets[-20:]) if len(rets) >= 20 else 0.0
    vol60 = pstdev(rets[-60:]) if len(rets) >= 60 else max(vol20, 1e-9)
    ret1 = rets[-1]
    ret10 = _safe(c[-1], c[-11], 1.0) - 1.0
    ret20 = _safe(c[-1], c[-21], 1.0) - 1.0

    e9, e20, e50, e100, e200 = ema(c, 9), ema(c, 20), ema(c, 50), ema(c, 100), ema(c, 200)
    s20, s50, s100, s200 = _sma(c, 20), _sma(c, 50), _sma(c, 100), _sma(c, 200)
    trend = _sign(e20 - e50) or _sign(ret20)
    ema_align = fmean([_sign(c[-1] - e9), _sign(e9 - e20), _sign(e20 - e50), _sign(e50 - e100), _sign(e100 - e200)])
    sma_align = fmean([_sign(c[-1] - s20), _sign(s20 - s50), _sign(s50 - s100), _sign(s100 - s200)])
    adx, dmi = _adx_dmi(bars)
    aroon = _aroon(h, l)
    slope20 = _clamp(_slope(c[-20:]) * 10.0 / a)
    er20 = _efficiency(c[-21:])
    hh = max(h[-10:]) > max(h[-20:-10])
    hl = min(l[-10:]) > min(l[-20:-10])
    lh = max(h[-10:]) < max(h[-20:-10])
    ll = min(l[-10:]) < min(l[-20:-10])
    hhll = 1.0 if hh and hl else -1.0 if lh and ll else 0.0

    tenkan = (max(h[-9:]) + min(l[-9:])) / 2.0
    kijun = (max(h[-26:]) + min(l[-26:])) / 2.0
    span_a = (tenkan + kijun) / 2.0
    span_b = (max(h[-52:]) + min(l[-52:])) / 2.0
    cloud_mid = (span_a + span_b) / 2.0
    ichimoku = _clamp((c[-1] - cloud_mid) / a)
    psar_proxy = _clamp((c[-1] - e20) / a)

    r14 = rsi(c, 14)
    stoch = _stochastic(h, l, c)
    rsi_hist = [rsi(c[:i], 14) for i in range(len(c) - 20, len(c) + 1)]
    rsi_lo, rsi_hi = min(rsi_hist[-14:]), max(rsi_hist[-14:])
    stoch_rsi = 50.0 if rsi_hi <= rsi_lo else 100.0 * (rsi_hist[-1] - rsi_lo) / (rsi_hi - rsi_lo)
    macd_line, macd_signal = macd(c)
    macd_hist = _clamp((macd_line - macd_signal) / max(a * 0.35, 1e-9))
    cci = _cci(h, l, c)
    will = _williams(h, l, c)
    tsi_proxy = _clamp((ret10 + ret20) / max(vol20 * 8.0, 1e-6))
    uo_proxy = _clamp((stoch - 50.0) / 35.0 * 0.6 + (r14 - 50.0) / 30.0 * 0.4)
    ppo = 100.0 * _safe(ema(c, 12) - ema(c, 26), ema(c, 26))
    rs20 = [_safe(c[i], c[i - 20], 1.0) - 1.0 for i in range(20, len(c))]
    rs_mag_rank = _rank([abs(x) for x in rs20[-252:]], abs(rs20[-1]))
    rs_rank_directional = _sign(rs20[-1]) * (0.5 + 0.5 * rs_mag_rank)

    rng = max(last.high - last.low, 1e-9)
    tr = max(last.high - last.low, abs(last.high - prev.close), abs(last.low - prev.close))
    tr_hist = [max(bars[i].high - bars[i].low, abs(bars[i].high - bars[i - 1].close), abs(bars[i].low - bars[i - 1].close)) for i in range(len(bars) - 100, len(bars))]
    tr_pct = _rank(tr_hist, tr)
    natr = _safe(a, abs(c[-1]))
    bb_mean = s20
    bb_std = pstdev(c[-20:])
    bb_width = _safe(4.0 * bb_std, abs(bb_mean))
    bb_pos = _safe(c[-1] - (bb_mean - 2 * bb_std), 4 * bb_std, 0.5)
    kc_width = _safe(3.0 * a, abs(e20))
    squeeze = 1.0 if bb_width < kc_width else 0.0
    realized_vol = sqrt(sum(x * x for x in rets[-20:]) / 20.0)
    vol_regime = _safe(vol20, max(vol60, 1e-9), 1.0)
    don_hi, don_lo = max(h[-20:]), min(l[-20:])
    don_pos = _safe(c[-1] - don_lo, don_hi - don_lo, 0.5)

    bar_dir = _sign(last.close - last.open) or _sign(ret1)
    volume_ratio = _safe(v[-1], max(fmean(v[-20:]), 1e-9), 1.0)
    relative_volume = _safe(v[-1], max(median(v[-20:]), 1e-9), 1.0)
    obv = _obv_direction(bars)
    mfi = _mfi(bars)
    cmf = _cmf(bars)
    adl_proxy = _clamp(cmf * 0.7 + obv * 0.3)
    vol_roc = _safe(v[-1], max(v[-11], 1e-9), 1.0) - 1.0
    poc = _volume_poc(bars)
    up_vol = sum(b.volume for b in bars[-20:] if b.close >= b.open)
    dn_vol = sum(b.volume for b in bars[-20:] if b.close < b.open)
    up_down = _safe(up_vol, max(dn_vol, 1e-9), 1.0)

    session = [b for b in bars if b.timestamp.date() == last.timestamp.date()]
    if len(session) < 2:
        session = bars[-20:]
    session_vwap = _vwap(session)
    avwap = _vwap(bars[-50:])
    vw20 = _vwap(bars[-20:])
    vw20_prev = _vwap(bars[-21:-1])
    vw_std = pstdev([(b.high + b.low + b.close) / 3.0 for b in bars[-20:]])
    prev_vw = vw20_prev
    reclaim = 1.0 if prev.close < prev_vw and last.close > vw20 else -1.0 if prev.close > prev_vw and last.close < vw20 else _sign(last.close - vw20) * 0.2

    prior_hi = max(h[-21:-1])
    prior_lo = min(l[-21:-1])
    range_pos = _safe(c[-1] - prior_lo, prior_hi - prior_lo, 0.5)
    bos = 1.0 if c[-1] > prior_hi else -1.0 if c[-1] < prior_lo else 0.0
    prior_trend = _sign(_slope(c[-21:-1]))
    choch = -1.0 if prior_trend > 0 and c[-1] < prior_lo else 1.0 if prior_trend < 0 and c[-1] > prior_hi else 0.0
    p_hi = max(h[-22:-2])
    p_lo = min(l[-22:-2])
    retest = 1.0 if prev.close > p_hi and last.low <= p_hi <= last.close else -1.0 if prev.close < p_lo and last.high >= p_lo >= last.close else 0.0
    support_dist = abs(c[-1] - prior_lo)
    resistance_dist = abs(prior_hi - c[-1])
    sr = _clamp(_safe(resistance_dist - support_dist, resistance_dist + support_dist))
    pivot = (prev.high + prev.low + prev.close) / 3.0
    failed = -1.0 if prev.high > p_hi and c[-1] < p_hi else 1.0 if prev.low < p_lo and c[-1] > p_lo else 0.0
    inside = last.high <= prev.high and last.low >= prev.low
    outside = last.high > prev.high and last.low < prev.low

    sweep = -1.0 if last.high > prior_hi and last.close < prior_hi else 1.0 if last.low < prior_lo and last.close > prior_lo else 0.0
    highs_sorted = sorted(h[-12:-1], reverse=True)
    lows_sorted = sorted(l[-12:-1])
    eq_hi = abs(highs_sorted[0] - highs_sorted[1]) <= 0.20 * a
    eq_lo = abs(lows_sorted[0] - lows_sorted[1]) <= 0.20 * a
    equal_liq = 0.55 if eq_hi and not eq_lo else -0.55 if eq_lo and not eq_hi else 0.0
    bull_fvg = l[-1] > h[-3]
    bear_fvg = h[-1] < l[-3]
    fvg = 1.0 if bull_fvg else -1.0 if bear_fvg else 0.0
    body = last.close - last.open
    prev_body = prev.close - prev.open
    displacement = _sign(body) if abs(body) >= 1.2 * a else 0.0
    order_block = displacement if displacement and _sign(prev_body) == -displacement else 0.0
    breaker = 1.0 if prev.close < prev.open and last.close > prev.high else -1.0 if prev.close > prev.open and last.close < prev.low else 0.0
    premium_discount = _safe(c[-1] - min(l[-50:]), max(h[-50:]) - min(l[-50:]), 0.5)
    liquidity_void = _sign(sum(b.close - b.open for b in bars[-3:])) if all(abs(b.close - b.open) >= 0.65 * a for b in bars[-3:]) else 0.0
    imbalance_fill = fvg * 0.65 if fvg else 0.0
    mitigation = retest * 0.8 if retest else 0.0

    bull_engulf = prev.close < prev.open and last.close > last.open and last.close >= prev.open and last.open <= prev.close
    bear_engulf = prev.close > prev.open and last.close < last.open and last.open >= prev.close and last.close <= prev.open
    engulf = 1.0 if bull_engulf else -1.0 if bear_engulf else 0.0
    upper_wick = last.high - max(last.open, last.close)
    lower_wick = min(last.open, last.close) - last.low
    pin = 1.0 if lower_wick >= 2 * abs(body) and lower_wick > upper_wick else -1.0 if upper_wick >= 2 * abs(body) and upper_wick > lower_wick else 0.0
    doji = abs(body) / rng
    marubozu = abs(body) / rng
    b1, b2, b3 = bars[-3], bars[-2], bars[-1]
    three = 1.0 if b1.close < b1.open and abs(b2.close - b2.open) < abs(b1.close - b1.open) * 0.6 and b3.close > b3.open and b3.close > (b1.open + b1.close) / 2 else -1.0 if b1.close > b1.open and abs(b2.close - b2.open) < abs(b1.close - b1.open) * 0.6 and b3.close < b3.open and b3.close < (b1.open + b1.close) / 2 else 0.0
    gap = 1.0 if last.low > prev.high else -1.0 if last.high < prev.low else 0.0
    body_wick = _safe(abs(body), upper_wick + lower_wick + 1e-9)
    clv = _safe((last.close - last.low) - (last.high - last.close), rng)

    spread_proxy = _safe(rng, abs(last.close))
    median_spread = median([_safe(b.high - b.low, abs(b.close)) for b in bars[-20:] if b.close])
    spread_quality = 1.0 - _clamp(_safe(spread_proxy, max(2 * median_spread, 1e-9)), 0.0, 1.0)
    median_abs_ret = median(abs(x) for x in rets[-20:])
    speed = _safe(abs(ret1), max(median_abs_ret, 1e-9))
    range_eff = _safe(abs(body), rng)
    pullback = _safe(max(h[-10:]) - c[-1], a) if trend > 0 else _safe(c[-1] - min(l[-10:]), a)
    pull_score = trend * (0.7 if 0.2 <= pullback <= 1.2 else -0.5 if pullback > 2.0 else 0.2)
    persistence = 1.0 if c[-3] < c[-2] < c[-1] else -1.0 if c[-3] > c[-2] > c[-1] else 0.0

    vol_quality = 0.55 if 0.25 <= tr_pct <= 0.80 else -0.55 if tr_pct >= 0.95 else 0.10
    vol_regime_quality = 0.50 if 0.7 <= vol_regime <= 1.6 else -0.45

    values = {
        "ema_9_20_50_100_200_alignment": _clamp(ema_align),
        "sma_20_50_100_200_alignment": _clamp(sma_align),
        "adx": _clamp(dmi * min(1.0, adx / 40.0)),
        "dmi_plus_minus": _clamp(dmi),
        "supertrend": _clamp((c[-1] - e20) / a),
        "aroon": aroon,
        "ichimoku_cloud": ichimoku,
        "parabolic_sar": psar_proxy,
        "linear_regression_slope": slope20,
        "higher_high_lower_low_sequence": hhll,
        "trend_efficiency_ratio": er20,
        "rsi_14": _clamp((r14 - 50.0) / 20.0),
        "stochastic": _clamp((stoch - 50.0) / 35.0),
        "stoch_rsi": _clamp((stoch_rsi - 50.0) / 35.0),
        "macd_histogram": macd_hist,
        "roc": _clamp(ret20 / max(vol20 * sqrt(20.0) * 2.0, 1e-6)),
        "momentum_10": _clamp(ret10 / max(vol20 * sqrt(10.0) * 2.0, 1e-6)),
        "cci": _clamp(cci / 180.0),
        "williams_r": _clamp((will + 50.0) / 35.0),
        "tsi": tsi_proxy,
        "ultimate_oscillator": uo_proxy,
        "ppo": _clamp(ppo / 2.5),
        "relative_strength_rank": _clamp(rs_rank_directional),
        "atr": trend * vol_quality,
        "normalized_atr": trend * vol_quality,
        "bollinger_width": trend * vol_quality,
        "bollinger_percent_b": _clamp((bb_pos - 0.5) * 2.0),
        "keltner_width": trend * vol_quality,
        "squeeze_state": trend * (0.15 if squeeze else 0.40),
        "historical_volatility": trend * vol_regime_quality,
        "realized_volatility": trend * vol_regime_quality,
        "true_range_percentile": trend * vol_quality,
        "volatility_regime": trend * vol_regime_quality,
        "donchian_width": _clamp((don_pos - 0.5) * 2.0),
        "volume_ratio": bar_dir * _clamp((volume_ratio - 0.7) / 1.0, 0.0, 1.0),
        "obv": obv,
        "mfi": _clamp((mfi - 50.0) / 30.0),
        "cmf": _clamp(cmf * 2.0),
        "accumulation_distribution": adl_proxy,
        "volume_roc": bar_dir * _clamp(vol_roc / 1.5),
        "volume_profile_poc_distance": _clamp((c[-1] - poc) / (2.0 * a)),
        "relative_volume": bar_dir * _clamp((relative_volume - 0.75) / 1.25, 0.0, 1.0),
        "up_down_volume_ratio": _clamp((up_down - 1.0) / 1.5),
        "session_vwap_distance": _clamp((c[-1] - session_vwap) / a),
        "anchored_vwap_distance": _clamp((c[-1] - avwap) / (1.5 * a)),
        "vwap_slope": _clamp((vw20 - vw20_prev) / max(a * 0.25, 1e-9)),
        "vwap_band_location": _clamp(_safe(c[-1] - vw20, max(2.0 * vw_std, 1e-9))),
        "vwap_reclaim_reject": reclaim,
        "bos": bos,
        "choch": choch,
        "swing_high_low": _clamp((range_pos - 0.5) * 2.0),
        "break_retest": retest,
        "range_location": _clamp((range_pos - 0.5) * 2.0),
        "support_resistance_distance": sr,
        "pivot_structure": _clamp((c[-1] - pivot) / a),
        "market_structure_trend": hhll,
        "failed_breakout": failed,
        "inside_outside_structure": 0.0 if inside else bar_dir * 0.75 if outside else bar_dir * 0.20,
        "liquidity_sweep": sweep,
        "equal_highs_lows": equal_liq,
        "fair_value_gap": fvg,
        "order_block": order_block,
        "breaker_block": breaker,
        "mitigation_block": mitigation,
        "premium_discount_zone": _clamp(-(premium_discount - 0.5) * 2.0),
        "displacement_candle": _clamp(body / (1.5 * a)),
        "imbalance_fill_ratio": imbalance_fill,
        "liquidity_void": liquidity_void,
        "engulfing": engulf,
        "pin_bar": pin,
        "inside_bar": 0.0 if inside else bar_dir * 0.10,
        "outside_bar": bar_dir * (0.75 if outside else 0.0),
        "doji_context": 0.0 if doji <= 0.10 else bar_dir * 0.15,
        "marubozu": bar_dir * _clamp((marubozu - 0.55) / 0.35, 0.0, 1.0),
        "three_bar_reversal": three,
        "gap_behavior": gap,
        "body_wick_ratio": bar_dir * _clamp(body_wick / 2.0),
        "close_location_value": _clamp(clv),
        "spread_proxy": bar_dir * spread_quality,
        "bar_speed": _sign(ret1) * _clamp(speed / 3.0),
        "tick_activity_proxy": bar_dir * _clamp((volume_ratio - 0.5) / 1.5),
        "short_term_range_efficiency": bar_dir * range_eff,
        "micro_pullback_depth": _clamp(pull_score),
        "micro_breakout_persistence": persistence,
    }

    catalog = _catalog()
    if set(values) != set(catalog):
        missing = sorted(set(catalog) - set(values))
        extra = sorted(set(values) - set(catalog))
        raise RuntimeError(f"feature catalog mismatch missing={missing} extra={extra}")

    observations = tuple(
        make_observation(name, catalog[name], values[name])
        for name in sorted(values)
    )
    return HistoricalFeatureSnapshot(
        symbol=symbol,
        timeframe=timeframe,
        timestamp=last.timestamp,
        values=values,
        observations=observations,
    )
