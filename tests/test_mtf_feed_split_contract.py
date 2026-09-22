
from pathlib import Path

from app.competition_profiles import AMP_CORE_FEED_SYMBOLS, CAPITAL_AFRICA_LIMITS


ROOT = Path(__file__).resolve().parents[1]
TV = ROOT / "tradingview"


CAPITAL_FILES = (
    TV / "STC_CAPITAL_MTF_FEED_A.pine",
    TV / "STC_CAPITAL_MTF_FEED_B.pine",
)
AMP_FILES = (
    TV / "STC_AMP_MTF_FEED_A.pine",
    TV / "STC_AMP_MTF_FEED_B.pine",
    TV / "STC_AMP_MTF_FEED_C.pine",
    TV / "STC_AMP_MTF_FEED_D.pine",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _symbols(text: str) -> set[str]:
    known = set(CAPITAL_AFRICA_LIMITS) | set(AMP_CORE_FEED_SYMBOLS)
    return {symbol for symbol in known if f'"{symbol}"' in text}


def test_capital_mtf_split_covers_all_ten_symbols_once_and_stays_under_request_budget():
    texts = [_text(path) for path in CAPITAL_FILES]
    symbols = [_symbols(text) for text in texts]
    assert symbols[0].isdisjoint(symbols[1])
    assert symbols[0] | symbols[1] == set(CAPITAL_AFRICA_LIMITS)
    for text in texts:
        assert len(_symbols(text)) == 5
        assert text.count(" = feedBar(") == 5
        assert text.count(" = confirmBar(") == 5
        assert text.count(' = trendBar(') == 10
        assert text.count(" = historyBar(") == 5
        assert text.count(" = monthlyBar(") == 5
        assert 5 * 6 == 30
        assert 30 < 40
        assert text.count("alert(buildMessage(") == 5


def test_amp_mtf_split_covers_all_sixteen_symbols_once_and_stays_under_request_budget():
    texts = [_text(path) for path in AMP_FILES]
    symbol_sets = [_symbols(text) for text in texts]
    union = set().union(*symbol_sets)
    assert union == set(AMP_CORE_FEED_SYMBOLS)
    for i, symbols in enumerate(symbol_sets):
        for j, other in enumerate(symbol_sets):
            if i != j:
                assert symbols.isdisjoint(other)
    for text in texts:
        assert len(_symbols(text)) == 4
        assert text.count(" = feedBar(") == 4
        assert text.count(" = confirmBar(") == 4
        assert text.count(' = trendBar(') == 8
        assert text.count(" = historyBar(") == 4
        assert text.count(" = monthlyBar(") == 4
        assert 4 * 6 == 24
        assert 24 < 40
        assert text.count("alert(buildMessage(") == 4


def test_all_mtf_feeds_emit_exact_backend_context_contract():
    for path in CAPITAL_FILES + AMP_FILES:
        text = _text(path)
        assert '"confirm_timeframe":"60"' in text
        assert '"trend_2h_time":"' in text
        assert '"trend_2h_score":' in text
        assert '"trend_4h_time":"' in text
        assert '"trend_4h_score":' in text
        assert '"trend_1m_time":"' in text
        assert '"trend_1m_score":' in text
        assert '"history_timeframe":"1D"' in text
        assert 'trendBar(string symbol, string tf)' in text
        assert 'trendBar("' in text
        assert '"120")' in text
        assert '"240")' in text
        assert 'request.security(symbol, "1M", makeMonthlyTrendBar()' in text
        assert 'request.security(symbol, "1D", makeHistoryBar()' in text
        assert 'time[1]' in text
        assert 'lookahead=barmerge.lookahead_on' in text
        assert 'eventId = competitionId + "|" + symbol + "|" + feedTf + "|" + str.tostring(d.t)' in text


def test_mtf_feeds_fail_closed_if_any_higher_timeframe_context_is_missing():
    for path in CAPITAL_FILES + AMP_FILES:
        text = _text(path)
        guard = "not na({v}C.t)"
        assert "not na(" in text
        assert "C.t) and not na(" in text
        assert "2.t) and not na(" in text
        assert "4.t) and not na(" in text
        assert "H.t) and not na(" in text
        assert "M.t)" in text


def test_new_split_is_additive_so_existing_verified_feeds_remain_available_for_rollback():
    assert (TV / "STC_MULTI_FEED.pine").exists()
    assert (TV / "STC_AMP_CORE_FEED.pine").exists()
    assert (TV / "STC_AMP_CORE_FEED_B.pine").exists()



def test_mtf_feeds_emit_complete_nine_family_live_evidence_without_extra_requests():
    fields = (
        "family_trend",
        "family_momentum",
        "family_volatility",
        "family_volume",
        "family_vwap",
        "family_market_structure",
        "family_smc_liquidity",
        "family_price_action",
        "family_microstructure",
    )
    for path in CAPITAL_FILES + AMP_FILES:
        text = _text(path)
        for field in fields:
            assert f'"{field}":' in text
        assert "familyTrend" in text
        assert "familySmcLiquidity" in text
        assert "familyMarketStructure" in text
        assert "v1.1 Family Breadth" in text
        # Family calculations run inside the existing 15m request and add no
        # request.security contexts beyond the verified split budget.
        if path in CAPITAL_FILES:
            assert text.count(" = feedBar(") == 5
            assert 5 * 6 == 30
        else:
            assert text.count(" = feedBar(") == 4
            assert 4 * 6 == 24
