from pathlib import Path

PINE = Path(__file__).resolve().parents[1] / "tradingview" / "STC_MULTI_FEED.pine"

EXPECTED = {
    "CAPITALCOM:BTCUSD",
    "CAPITALCOM:ETHUSD",
    "CAPITALCOM:DOGEUSD",
    "CAPITALCOM:EURUSD",
    "CAPITALCOM:AUDUSD",
    "CAPITALCOM:USDZAR",
    "CAPITALCOM:XAUUSD",
    "CAPITALCOM:XAGUSD",
    "CAPITALCOM:SPX500",
    "CAPITALCOM:NAS100",
}


def test_multisymbol_feed_covers_exact_capital_profile_symbols():
    text = PINE.read_text(encoding="utf-8")
    present = {symbol for symbol in EXPECTED if f'"{symbol}"' in text}
    assert present == EXPECTED
    assert "STC Capital Multi Feed v0.8 A+ 1H Confirm" in text


def test_multisymbol_feed_uses_remote_security_and_all_alert_calls():
    text = PINE.read_text(encoding="utf-8")
    assert "request.security(" in text
    assert "makeFeedBar()" in text
    assert 'alert(buildMessage("CAPITALCOM:BTCUSD", btc, btcC, btcH), alert.freq_all)' in text
    assert 'confirmTf = input.timeframe("60"' in text
    assert 'request.security(symbol, confirmTf, makeConfirmBar()' in text
    assert '"confirm_ema200"' in text
    assert '"confirm_macd_signal"' in text
    assert "barstate.isconfirmed" in text
    assert "barstate.isrealtime" in text


def test_multisymbol_feed_has_stable_remote_bar_event_identity():
    text = PINE.read_text(encoding="utf-8")
    assert 'eventId = competitionId + "|" + symbol + "|" + feedTf + "|" + str.tostring(d.t)' in text
    assert '"event_id"' in text
    assert '"competition_id"' in text
    assert '"symbol"' in text
    assert '"timeframe"' in text
    assert '"time"' in text


def test_multisymbol_feed_deduplicates_closed_markets():
    text = PINE.read_text(encoding="utf-8")
    for token in (
        "varip int lastBTC = na",
        "varip int lastETH = na",
        "varip int lastXAU = na",
        "varip int lastNAS = na",
        "btc.t != lastBTC",
        "nas.t != lastNAS",
    ):
        assert token in text
