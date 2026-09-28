from pathlib import Path

FILES = [
    Path("tradingview/STC_CAPITAL_MTF_FEED_A_CONFIRMED_RESEARCH.pine"),
    Path("tradingview/STC_CAPITAL_MTF_FEED_B_CONFIRMED_RESEARCH.pine"),
]


def test_confirmed_base_candidates_are_research_only_and_disabled_by_default():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert "RESEARCH ONLY" in text
        assert 'input.bool(false, "Enable RESEARCH feed (never production webhook)"' in text
        assert '"research_only":true,"live_authorized":false' in text
        assert 'r10-confirmed-base-v12|' in text


def test_remote_base_bar_is_previous_confirmed_bar_with_lookahead_on():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert "FeedBar.new(time[1], open[1], high[1], low[1], close[1], volume[1]" in text
        assert (
            "request.security(symbol, feedTf, makeFeedBar(), gaps=barmerge.gaps_off, "
            "lookahead=barmerge.lookahead_on, ignore_invalid_symbol=false)"
        ) in text


def test_host_bar_still_requires_confirmed_realtime_trigger():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert "if feedEnabled and barstate.isconfirmed and barstate.isrealtime" in text


def test_research_event_ids_cannot_collide_with_v11_production_ids():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert 'eventId = "r10-confirmed-base-v12|" + competitionId' in text
        assert 'eventId = competitionId + "|" + symbol + "|" + feedTf' not in text
