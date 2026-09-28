from app.mtf_shadow import Bar, FROZEN_R10_CANDIDATES, evaluate_shadow_signal


def bars(count, seconds, start=1_700_000_000, slope=1.0, base=100.0):
    out = []
    for i in range(count):
        c = base + slope * i
        out.append(Bar(start + i * seconds, c - 0.2 * slope, c + 1.0, c - 1.0, c))
    return out


def test_candidates_are_shadow_only():
    assert set(FROZEN_R10_CANDIDATES) == {"CAPITALCOM:ETHUSD", "CAPITALCOM:DOGEUSD"}
    assert all(c.authority == "SHADOW_ONLY" for c in FROZEN_R10_CANDIDATES.values())


def test_unclosed_higher_timeframe_bar_is_not_used():
    b15 = bars(80, 900, slope=0.2)
    b1 = bars(80, 3600, slope=0.8)
    b4 = bars(80, 14400, slope=3.2)
    shifted = [Bar(x.ts + 10_000_000, x.open, x.high, x.low, x.close) for x in b4]
    c = FROZEN_R10_CANDIDATES["CAPITALCOM:ETHUSD"]
    assert evaluate_shadow_signal(candidate=c, bars_15m=b15, bars_1h=b1, bars_4h=shifted, signal_index=70) is None


def test_doge_outside_frozen_session_rejects():
    from datetime import datetime, timezone

    c = FROZEN_R10_CANDIDATES["CAPITALCOM:DOGEUSD"]
    b15 = bars(120, 900, start=1_699_920_000, slope=0.2)
    idx = next(i for i, b in enumerate(b15[50:], 50) if datetime.fromtimestamp(b.ts, timezone.utc).hour < 7)
    assert evaluate_shadow_signal(
        candidate=c,
        bars_15m=b15,
        bars_1h=bars(120, 3600, slope=0.8),
        bars_4h=bars(120, 14400, slope=3.2),
        signal_index=idx,
    ) is None


def test_large_next_open_gap_rejects():
    c = FROZEN_R10_CANDIDATES["CAPITALCOM:ETHUSD"]
    b15 = bars(90, 900, slope=0.2)
    i = 75
    nxt = b15[i + 1]
    b15[i + 1] = Bar(nxt.ts, nxt.open + 50, nxt.high + 50, nxt.low + 50, nxt.close + 50)
    assert evaluate_shadow_signal(
        candidate=c,
        bars_15m=b15,
        bars_1h=bars(90, 3600, slope=0.8),
        bars_4h=bars(90, 14400, slope=3.2),
        signal_index=i,
    ) is None


def test_signal_when_frozen_pullback_conditions_are_met():
    b15 = bars(120, 900, slope=0.10)
    i = 100
    b15[i] = Bar(b15[i].ts, b15[i].close - 0.05, b15[i].close + 0.3, b15[i].close - 0.3, b15[i].close)
    b15[i + 1] = Bar(b15[i + 1].ts, b15[i].close + 0.01, b15[i].close + 0.4, b15[i].close - 0.2, b15[i].close + 0.1)
    c = FROZEN_R10_CANDIDATES["CAPITALCOM:ETHUSD"]
    sig = evaluate_shadow_signal(
        candidate=c,
        bars_15m=b15,
        bars_1h=bars(120, 3600, slope=0.4),
        bars_4h=bars(120, 14400, slope=1.6),
        signal_index=i,
    )
    if sig is not None:
        assert sig.authority == "SHADOW_ONLY"
        assert sig.direction == "LONG"
        assert sig.stop < sig.entry < sig.target
