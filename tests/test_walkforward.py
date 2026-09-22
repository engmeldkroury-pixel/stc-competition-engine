
from datetime import datetime, timedelta, timezone

import pytest

import app.walkforward as wf
from app.evidence_engine import EvidenceSummary
from app.historical_features import HistoricalFeatureSnapshot, extract_feature_snapshot
from app.models import Bar
from app.walkforward import BacktestParams, backtest_strategy, parameter_grid, walk_forward_validate


UTC = timezone.utc


def _bars(count: int = 1000, slope: float = 0.08) -> list[Bar]:
    out = []
    t0 = datetime(2025, 1, 1, tzinfo=UTC)
    price = 100.0
    for i in range(count):
        noise = 0.08 if i % 5 in (0, 1, 2) else -0.05
        price += slope + noise
        op = price - slope * 0.4
        out.append(
            Bar(
                timestamp=t0 + timedelta(minutes=15 * i),
                open=op,
                high=max(op, price) + 0.55,
                low=min(op, price) - 0.55,
                close=price,
                volume=1000 + (i % 30) * 25,
            )
        )
    return out


def test_historical_snapshot_does_not_read_future_bars():
    bars = _bars(340)
    a = extract_feature_snapshot("TEST:X", "15", bars[:300])
    modified = bars[:300] + [
        b.model_copy(update={"close": b.close * 5, "high": b.high * 5, "low": b.low * 5, "open": b.open * 5})
        for b in bars[300:]
    ]
    b = extract_feature_snapshot("TEST:X", "15", modified[:300])
    assert a.values == b.values
    assert a.timestamp == b.timestamp


def test_backtest_enters_next_bar_and_treats_ambiguous_bar_conservatively(monkeypatch):
    bars = _bars(300, slope=0.0)
    entry_i = 261
    bars[entry_i] = Bar(
        timestamp=bars[entry_i].timestamp,
        open=100.0,
        high=110.0,
        low=90.0,
        close=101.0,
        volume=1500.0,
    )

    dummy = HistoricalFeatureSnapshot(
        symbol="TEST:X",
        timeframe="15",
        timestamp=bars[260].timestamp,
        values={},
        observations=(),
    )
    summary = EvidenceSummary(
        score=0.9,
        agreement_ratio=1.0,
        independent_confirmations=8,
        hard_confirmations=3,
        family_scores={},
        family_weights_used={},
        conflicts=(),
        strongest_features=(),
    )
    monkeypatch.setattr(wf, "_signal", lambda *args, **kwargs: (1, 0.9, summary))

    params = BacktestParams(
        threshold=0.5,
        stop_atr=1.0,
        target_r=1.0,
        max_hold_bars=3,
        round_turn_cost_r=0.0,
    )
    trades, stats = backtest_strategy(
        "TEST:X",
        "15",
        bars,
        {260: dummy},
        "trend_pullback",
        params,
        start_index=260,
        end_index=270,
    )
    assert len(trades) == 1
    trade = trades[0]
    assert trade.signal_index == 260
    assert trade.entry_index == 261
    assert trade.exit_reason == "STOP_AMBIGUOUS_BAR"
    assert trade.result_r == pytest.approx(-1.0)
    assert stats.losses == 1


def test_parameter_grid_is_bounded_and_contains_no_zero_risk_configs():
    grid = parameter_grid("15")
    assert 10 <= len(grid) <= 30
    assert all(p.stop_atr > 0 and p.target_r > 0 for p in grid)
    assert all(0.4 <= p.threshold <= 0.8 for p in grid)


def test_walk_forward_engine_runs_on_chronological_synthetic_history():
    bars = _bars(930, slope=0.10)
    result = walk_forward_validate(
        "TEST:X",
        "15",
        bars,
        "trend_pullback",
    )
    assert result.trial.symbol == "TEST:X"
    assert result.trial.timeframe == "15"
    assert result.selected_params.stop_atr > 0
    assert result.test_stats.trades >= 0
    assert result.forward_stats.trades >= 0
