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
    assert "STC Capital Multi Feed v0.6 Stateful Visual" in text


def test_multisymbol_feed_uses_remote_security_and_all_alert_calls():
    text = PINE.read_text(encoding="utf-8")
    assert "request.security(" in text
    assert "makeFeedBar()" in text
    assert "alert(buildMessage(symbol, d), alert.freq_all)" in text
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
    assert "varip array<int> lastSentTimes" in text
    assert "d.t != previousTime" in text
    assert "array.set(lastSentTimes, i, d.t)" in text
