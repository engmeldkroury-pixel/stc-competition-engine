from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINE = ROOT / "tradingview" / "STC_AMP_CRYPTO_24X7_FEED.pine"

WEEKEND_CRYPTO = {
    "CME:MBT1!",
    "CME:MET1!",
    "CME:MSL1!",
    "CME:MXP1!",
}


def test_amp_crypto_24x7_feed_exists_and_covers_four_micro_crypto_symbols():
    text = PINE.read_text(encoding="utf-8")
    assert 'indicator("STC AMP Crypto 24x7 Feed v1.0"' in text
    for symbol in WEEKEND_CRYPTO:
        assert f'"{symbol}"' in text
    assert text.count(" = feedBar(") == 4
    assert text.count(" = confirmBar(") == 4
    assert text.count(" = trendBar(") == 8
    assert text.count(" = historyBar(") == 4
    assert text.count(" = monthlyBar(") == 4
    assert text.count("alert(buildMessage(") == 4
    assert 4 * 6 == 24
    assert 24 < 40


def test_amp_crypto_24x7_feed_is_realtime_deduped_and_host_chart_safe():
    text = PINE.read_text(encoding="utf-8")
    assert "barstate.isconfirmed" in text
    assert "barstate.isrealtime" in text
    assert "recommended CME:MBT1! on 15m" in text
    assert "A weekday-only host can starve Saturday/Sunday crypto updates." in text
    assert 'eventId = competitionId + "|" + symbol + "|" + feedTf + "|" + str.tostring(d.t)' in text
    for token in ("lastMBT", "lastMET", "lastMSL", "lastMXP"):
        assert f"varip int {token} = na" in text


def test_amp_crypto_24x7_feed_emits_same_backend_context_contract():
    text = PINE.read_text(encoding="utf-8")
    for field in (
        "family_trend",
        "family_momentum",
        "family_volatility",
        "family_volume",
        "family_vwap",
        "family_market_structure",
        "family_smc_liquidity",
        "family_price_action",
        "family_microstructure",
        "trend_2h_score",
        "trend_4h_score",
        "trend_1m_score",
        "history_momentum_252",
    ):
        assert f'"{field}"' in text
    assert '"confirm_timeframe":"60"' in text
    assert 'request.security(symbol, "1M", makeMonthlyTrendBar()' in text
    assert 'request.security(symbol, "1D", makeHistoryBar()' in text
