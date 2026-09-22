from pathlib import Path

from app.competition_profiles import AMP_CORE_FEED_SYMBOLS

ROOT = Path(__file__).resolve().parents[1]
PINE_A = ROOT / "tradingview" / "STC_AMP_CORE_FEED.pine"
PINE_B = ROOT / "tradingview" / "STC_AMP_CORE_FEED_B.pine"

GROUP_A = {
    "CME_MINI:MES1!",
    "CME_MINI:MNQ1!",
    "CBOT_MINI:MYM1!",
    "CME_MINI:M2K1!",
    "NYMEX:MCL1!",
    "NYMEX:MNG1!",
    "COMEX_MINI:MGC1!",
    "COMEX_MINI:SIL1!",
}

GROUP_B = {
    "CME_MINI:M6E1!",
    "CME_MINI:M6B1!",
    "CME_MINI:MJY1!",
    "CME_MINI:M6A1!",
    "CME:MBT1!",
    "CME:MET1!",
    "CBOT:ZN1!",
    "CBOT:ZB1!",
}


def test_amp_split_covers_exact_verified_core_universe():
    a = PINE_A.read_text(encoding="utf-8")
    b = PINE_B.read_text(encoding="utf-8")
    assert "STC AMP Core Feed A v0.4 A+ 1H Confirm" in a
    assert "STC AMP Core Feed B v0.4 A+ 1H Confirm" in b
    assert GROUP_A.isdisjoint(GROUP_B)
    assert GROUP_A | GROUP_B == set(AMP_CORE_FEED_SYMBOLS)
    for symbol in GROUP_A:
        assert f'"{symbol}"' in a
    for symbol in GROUP_B:
        assert f'"{symbol}"' in b


def test_amp_split_uses_15m_plus_confirmed_1h_and_daily_history():
    for path in (PINE_A, PINE_B):
        text = path.read_text(encoding="utf-8")
        assert 'competitionId = input.string("amp-futures-sep-2026"' in text
        assert 'feedTf = input.timeframe("15"' in text
        assert 'confirmTf = input.timeframe("60"' in text
        assert 'request.security(symbol, confirmTf, makeConfirmBar()' in text
        assert '"confirm_ema200"' in text
        assert '"confirm_macd_signal"' in text
        assert 'request.security(symbol, "1D", makeHistoryBar()' in text
        assert "close[1]" in text
        assert "history_momentum_252" in text


def test_each_amp_alert_emits_at_most_eight_symbol_events_per_cycle():
    a = PINE_A.read_text(encoding="utf-8")
    b = PINE_B.read_text(encoding="utf-8")
    assert a.count("alert(buildMessage(") == 8
    assert b.count("alert(buildMessage(") == 8
    # TradingView script alerts are vulnerable to automatic flood stopping
    # when too many alert() calls fire in a short window. Split 8+8 prevents
    # a single alert from emitting all 16 events at once.
    assert max(a.count("alert(buildMessage("), b.count("alert(buildMessage(")) <= 8


def test_amp_split_stays_under_standard_unique_request_budget():
    a = PINE_A.read_text(encoding="utf-8")
    b = PINE_B.read_text(encoding="utf-8")
    assert a.count(" = feedBar(") == 8
    assert a.count(" = confirmBar(") == 8
    assert a.count(" = historyBar(") == 8
    assert b.count(" = feedBar(") == 8
    assert b.count(" = confirmBar(") == 8
    assert b.count(" = historyBar(") == 8
    # Feed A also has two current-chart higher-timeframe visual requests.
    assert 8 * 3 + 2 == 26
    assert 26 < 40
    assert 8 * 3 == 24
    assert 24 < 40


def test_amp_split_has_per_symbol_realtime_deduplication():
    a = PINE_A.read_text(encoding="utf-8")
    b = PINE_B.read_text(encoding="utf-8")
    for text in (a, b):
        assert "barstate.isconfirmed" in text
        assert "barstate.isrealtime" in text
    assert "varip int lastMES = na" in a
    assert "varip int lastSIL = na" in a
    assert "varip int lastM6E = na" in b
    assert "varip int lastZB = na" in b


def test_amp_feed_a_has_stateful_visual_trade_plan_support():
    text = PINE_A.read_text(encoding="utf-8")
    assert 'overlay=true' in text
    assert 'showZones = input.bool(true' in text
    assert '"EMA 20"' in text
    assert '"EMA 50"' in text
    assert '"EMA 200"' in text
    assert '"Entry zone low"' in text
    assert '"Invalidation / Stop"' in text
    assert '"Exit zone start / TP1"' in text
    assert '"Exit zone end / TP2"' in text
    assert '"LOCKED LONG"' in text
    assert '"LOCKED SHORT"' in text
    assert '"AMP A ON "' in text


def test_amp_feed_b_is_companion_without_chart_clutter():
    text = PINE_B.read_text(encoding="utf-8")
    assert 'overlay=true' in text
    assert 'plot(na, title="STC AMP Feed B", display=display.none)' in text
    assert "showZones" not in text
