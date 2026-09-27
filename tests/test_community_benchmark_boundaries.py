from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import app.community_indicator_benchmark as cib
from app.community_indicator_benchmark import IndicatorBacktestParams, backtest_indicator_signals
from app.models import Bar


UTC = timezone.utc


def _fixture(count: int = 24) -> list[Bar]:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        Bar(
            timestamp=t0 + timedelta(minutes=15 * i),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=100.0,
        )
        for i in range(count)
    ]


def test_indicator_backtest_does_not_cross_outcome_partition_boundary(monkeypatch):
    bars = _fixture()
    monkeypatch.setattr(cib, "atr_by_index", lambda bars, period: {i: 2.0 for i in range(len(bars))})
    params = IndicatorBacktestParams(stop_atr=1.5, target_r=2.0, max_hold_bars=8, round_trip_cost_r=0.0)

    trades, _ = backtest_indicator_signals(
        bars, {19: 1.0}, start_index=15, end_index=19, params=params
    )
    assert trades == []

    trades, _ = backtest_indicator_signals(
        bars, {18: 1.0}, start_index=15, end_index=19, params=params
    )
    assert len(trades) == 1
    assert trades[0].entry_index == 19
    assert trades[0].exit_index == 19


def test_indicator_backtest_gap_through_stop_uses_first_executable_open(monkeypatch):
    bars = _fixture()
    bars[17] = Bar(
        timestamp=bars[17].timestamp,
        open=90.0, high=91.0, low=89.0, close=90.0, volume=100.0,
    )
    monkeypatch.setattr(cib, "atr_by_index", lambda bars, period: {i: 2.0 for i in range(len(bars))})
    params = IndicatorBacktestParams(stop_atr=1.5, target_r=2.0, max_hold_bars=8, round_trip_cost_r=0.04)
    trades, _ = backtest_indicator_signals(
        bars, {15: 1.0}, start_index=15, end_index=22, params=params
    )
    assert len(trades) == 1
    trade = trades[0]
    assert trade.entry_index == 16
    assert trade.exit_index == 17
    assert trade.exit_price == pytest.approx(90.0)
    assert trade.exit_reason == "stop_gap_first_executable_price"
    assert trade.r_multiple == pytest.approx(-10.0 / 3.0 - 0.04)
