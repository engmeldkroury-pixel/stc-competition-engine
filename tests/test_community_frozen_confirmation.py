from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app import community_frozen_confirmation as cfc
from app.community_indicator_catalog import indicator_by_id
from app.models import Bar


def _bars(count: int = 4000) -> list[Bar]:
    start = datetime(2025, 1, 1, tzinfo=UTC)
    rows: list[Bar] = []
    price = 100.0
    for i in range(count):
        regime = 1 if (i // 180) % 2 == 0 else -1
        drift = regime * 0.025
        cycle = ((i % 23) - 11) * 0.004
        open_ = price
        close = max(1.0, open_ + drift + cycle)
        rows.append(
            Bar(
                timestamp=start + timedelta(minutes=15 * i),
                open=open_,
                high=max(open_, close) + 0.16,
                low=min(open_, close) - 0.16,
                close=close,
                volume=1000 + (i % 37) * 13,
            )
        )
        price = close
    return rows


def test_frozen_confirmation_keeps_final_holdout_out_of_development(monkeypatch):
    spec = indicator_by_id("ut_bot_alerts")
    monkeypatch.setattr(cfc, "benchmarkable_indicators", lambda *args, **kwargs: (spec,))

    bars = _bars()
    cut = int(len(bars) * 0.85)
    changed = list(bars)
    for i in range(cut, len(changed)):
        bar = changed[i]
        changed[i] = Bar(
            timestamp=bar.timestamp,
            open=bar.open,
            high=bar.high + 25.0,
            low=max(0.01, bar.low - 25.0),
            close=max(0.01, bar.close + (12.0 if i % 2 else -12.0)),
            volume=bar.volume * 10,
        )

    first = cfc.confirm_community_symbol(
        symbol="TEST:X",
        asset_class="forex",
        timeframe="15",
        bars=bars,
    )
    second = cfc.confirm_community_symbol(
        symbol="TEST:X",
        asset_class="forex",
        timeframe="15",
        bars=changed,
    )

    a = first.components[0]
    b = second.components[0]
    assert first.development_bars == second.development_bars == cut
    assert a.selected_parameters == b.selected_parameters
    assert a.development_trial == b.development_trial
    assert first.live_authority is False
    assert second.live_authority is False


def test_confirmation_pass_never_grants_live_authority(monkeypatch):
    spec = indicator_by_id("ut_bot_alerts")
    monkeypatch.setattr(cfc, "benchmarkable_indicators", lambda *args, **kwargs: (spec,))
    report = cfc.confirm_community_symbol(
        symbol="TEST:X",
        asset_class="forex",
        timeframe="15",
        bars=_bars(),
    )
    assert report.live_authority is False
    assert report.status in {
        "FROZEN_CONFIRMATION_PASSED",
        "NO_FROZEN_CONFIRMATION_PASS",
    }


def test_frozen_confirmation_requires_a_real_holdout():
    try:
        cfc.confirm_community_symbol(
            symbol="TEST:X",
            asset_class="forex",
            timeframe="15",
            bars=_bars(1500),
        )
    except ValueError as exc:
        assert "Need at least" in str(exc)
    else:
        raise AssertionError("Expected a minimum-history failure")
