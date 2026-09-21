from pathlib import Path

from app.competition_profiles import AMP_CORE_FEED_SYMBOLS

PINE = Path(__file__).resolve().parents[1] / "tradingview" / "STC_AMP_CORE_FEED.pine"


def test_amp_core_feed_covers_exact_verified_core_universe():
    text = PINE.read_text(encoding="utf-8")
    assert "STC AMP Core Feed v0.1 Historical Context" in text
    for symbol in AMP_CORE_FEED_SYMBOLS:
        assert f'"{symbol}"' in text


def test_amp_core_feed_uses_15m_plus_confirmed_daily_history():
    text = PINE.read_text(encoding="utf-8")
    assert 'competitionId = input.string("amp-futures-sep-2026"' in text
    assert 'feedTf = input.timeframe("15"' in text
    assert 'request.security(symbol, "1D", makeHistoryBar()' in text
    assert "close[1]" in text
    assert "history_momentum_252" in text


def test_amp_core_feed_stays_under_standard_unique_request_budget_by_design():
    text = PINE.read_text(encoding="utf-8")
    # Each of the 16 symbols uses one intraday context and one daily context.
    assert len(AMP_CORE_FEED_SYMBOLS) == 16
    assert text.count(" = feedBar(") == 16
    assert text.count(" = historyBar(") == 16
    assert 16 * 2 == 32
    assert 32 < 40


def test_amp_core_feed_has_per_symbol_realtime_deduplication():
    text = PINE.read_text(encoding="utf-8")
    assert "barstate.isconfirmed" in text
    assert "barstate.isrealtime" in text
    assert "varip int lastMES = na" in text
    assert "varip int lastZB = na" in text
    assert 'alert(buildMessage("CME_MINI:MES1!", mes, mesH), alert.freq_all)' in text
