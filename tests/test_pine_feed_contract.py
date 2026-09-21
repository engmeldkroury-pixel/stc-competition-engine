from pathlib import Path


PINE = Path(__file__).resolve().parents[1] / "tradingview" / "STC_FEED.pine"


def test_pine_feed_emits_deterministic_event_id_and_required_contract_fields():
    text = PINE.read_text(encoding="utf-8")
    assert 'STC Competition Feed v0.2' in text
    assert 'eventId = competitionId + "|" + syminfo.prefix + ":" + syminfo.ticker + "|" + timeframe.period + "|" + str.tostring(time)' in text
    for field in [
        '"event_id"',
        '"competition_id"',
        '"symbol"',
        '"timeframe"',
        '"time"',
        '"open"',
        '"high"',
        '"low"',
        '"close"',
        '"ema20"',
        '"ema50"',
        '"rsi14"',
        '"atr14"',
        '"macd"',
        '"macd_signal"',
        '"volume_ratio"',
    ]:
        assert field in text
    assert "barstate.isconfirmed" in text
    assert "alert(msg, alert.freq_once_per_bar_close)" in text
