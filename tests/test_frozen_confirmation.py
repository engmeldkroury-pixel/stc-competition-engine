import json
from pathlib import Path

import pytest

from app import frozen_confirmation as fc
from app.walkforward import BacktestStats, TradeOutcome


def _archive(symbol="TEST:X", interval="15m", count=400, start_t=1700000000):
    bars = []
    for i in range(count):
        close = 100.0 + i * 0.01
        bars.append({
            "t": start_t + i * 900,
            "o": close - 0.01,
            "h": close + 0.05,
            "l": close - 0.05,
            "c": close,
            "v": 1000 + i,
        })
    last_t = bars[-1]["t"] if bars else None
    return {
        "symbol": symbol,
        "interval": interval,
        "bars": bars,
        "archive": {
            "schema_version": "stc-ohlcv-archive-v1",
            "provider": "TradingView Official MCP",
            "coverage_first_t": bars[0]["t"] if bars else None,
            "coverage_last_t": last_t,
            "withheld_unconfirmed_t": (last_t + 900) if last_t is not None else None,
        },
    }


def _hypothesis(freeze_t, threshold=0.72):
    return fc.hypothesis_from_dict({
        "hypothesis_id": "test_h1",
        "symbol": "TEST:X",
        "timeframe": "15",
        "strategy_id": "vwap_reversion",
        "archive_path": "unused.json",
        "freeze_t": freeze_t,
        "role": "BASELINE_COMPARATOR",
        "development_status": "FORWARD_FAILED",
        "source_run_id": 1,
        "allowed_regimes": [],
        "params": {
            "threshold": threshold,
            "stop_atr": 1.2,
            "target_r": 2.5,
            "max_hold_bars": 16,
            "min_agreement": 0.62,
            "min_independent_confirmations": 4,
            "min_hard_confirmations": 1,
            "round_turn_cost_r": 0.02,
        },
    })


def _trade(signal_index, result_r, exit_reason="TARGET", hold=2):
    return TradeOutcome(
        strategy_id="vwap_reversion",
        signal_index=signal_index,
        entry_index=signal_index + 1,
        exit_index=signal_index + 1 + hold,
        side="LONG",
        reference_price=100.0,
        entry_min=99.9,
        entry_max=100.1,
        entry_price=100.0,
        entry_wait_bars=1,
        exit_price=101.0 if result_r > 0 else 99.5,
        initial_stop=99.0,
        target=102.5,
        result_r=result_r,
        exit_reason=exit_reason,
        evidence_score=0.8,
        agreement_ratio=0.8,
    )


def _empty_stats():
    return BacktestStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_manifest_freezes_original_mnq_and_btc_params():
    path = Path("research_hypotheses/frozen_15m_v1.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    rows = {row.hypothesis_id: row for row in fc.load_frozen_hypotheses(manifest)}

    mnq = rows["mnq_vwap_reversion_baseline_15m_v1"]
    btc = rows["btcusd_bollinger_mean_reversion_baseline_15m_v1"]
    assert mnq.params.threshold == 0.72
    assert btc.params.threshold == 0.50
    assert mnq.freeze_t == 1790103600
    assert btc.freeze_t == 1790089200
    assert mnq.allowed_regimes == ()
    assert btc.allowed_regimes == ()


def test_frozen_confirmation_passes_exact_params_and_never_grants_live_authority(monkeypatch):
    archive = _archive()
    freeze_t = archive["bars"][299]["t"]
    hypothesis = _hypothesis(freeze_t, threshold=0.72)

    monkeypatch.setattr(fc, "materialize_feature_series", lambda *args, **kwargs: {})

    def fake_backtest(symbol, timeframe, bars, snapshots, strategy_id, params, *, start_index, end_index, signal_gate=None):
        assert symbol == "TEST:X"
        assert timeframe == "15"
        assert strategy_id == "vwap_reversion"
        assert params.threshold == 0.72
        assert params.stop_atr == 1.2
        assert params.target_r == 2.5
        assert params.max_hold_bars == 16
        assert start_index == 300
        assert signal_gate is None

        trades = []
        width = max(1, (end_index - start_index + 1) // 3)
        for segment in range(3):
            base = start_index + segment * width
            for n in range(10):
                result_r = 1.0 if n < 7 else -0.5
                trades.append(_trade(base + n * 2, result_r, "TARGET" if result_r > 0 else "STOP"))
        return trades, _empty_stats()

    monkeypatch.setattr(fc, "backtest_strategy", fake_backtest)
    result = fc.evaluate_frozen_hypothesis(archive, hypothesis)

    assert result.status == "UNSEEN_SUPPORT"
    assert result.completed_trades == 30
    assert result.stats.expectancy_r > 0.08
    assert result.stats.profit_factor >= 1.15
    assert result.segment_stability == 1.0
    assert result.optimization_locked is True
    assert result.second_confirmation_required is True
    assert result.live_calibration_authority is False


def test_frozen_confirmation_excludes_truncated_time_exit(monkeypatch):
    archive = _archive()
    freeze_t = archive["bars"][299]["t"]
    hypothesis = _hypothesis(freeze_t)

    monkeypatch.setattr(fc, "materialize_feature_series", lambda *args, **kwargs: {})

    def fake_backtest(*args, **kwargs):
        start = kwargs["start_index"]
        trades = [_trade(start + i * 2, 0.2, "TARGET") for i in range(5)]
        trades.append(_trade(start + 20, -99.0, "TIME", hold=5))
        return trades, _empty_stats()

    monkeypatch.setattr(fc, "backtest_strategy", fake_backtest)
    result = fc.evaluate_frozen_hypothesis(archive, hypothesis)

    assert result.status == "ACCUMULATING"
    assert result.completed_trades == 5
    assert result.incomplete_open_trades == 1
    assert result.stats.total_r == pytest.approx(1.0)
    assert "insufficient_unseen_trades" in result.rejection_reasons
    assert result.live_calibration_authority is False


def test_frozen_confirmation_returns_no_unseen_data_without_running_backtest(monkeypatch):
    archive = _archive()
    freeze_t = archive["bars"][-1]["t"]
    hypothesis = _hypothesis(freeze_t)

    def should_not_run(*args, **kwargs):
        raise AssertionError("No feature/backtest work should run without unseen bars")

    monkeypatch.setattr(fc, "materialize_feature_series", should_not_run)
    monkeypatch.setattr(fc, "backtest_strategy", should_not_run)

    result = fc.evaluate_frozen_hypothesis(archive, hypothesis)
    assert result.status == "NO_UNSEEN_DATA"
    assert result.completed_trades == 0
    assert result.live_calibration_authority is False


def test_frozen_confirmation_fails_closed_on_archive_identity_mismatch():
    archive = _archive(symbol="TEST:Y")
    hypothesis = _hypothesis(archive["bars"][299]["t"])
    with pytest.raises(ValueError, match="archive identity mismatch"):
        fc.evaluate_frozen_hypothesis(archive, hypothesis)


def test_manifest_requires_optimization_lock():
    with pytest.raises(ValueError, match="optimization_locked=true"):
        fc.load_frozen_hypotheses({
            "schema_version": "stc-frozen-confirmation-v1",
            "optimization_locked": False,
            "hypotheses": [{}],
        })


def test_frozen_confirmation_rejects_alternate_provider_backfill():
    archive = _archive()
    archive["archive"]["provider"] = "Capital.com REST API"
    hypothesis = _hypothesis(archive["bars"][299]["t"])

    with pytest.raises(ValueError, match="TradingView Official MCP"):
        fc.evaluate_frozen_hypothesis(archive, hypothesis)


def test_frozen_confirmation_rejects_archive_that_still_contains_mutable_tail():
    archive = _archive()
    archive["archive"]["withheld_unconfirmed_t"] = archive["bars"][-1]["t"]
    hypothesis = _hypothesis(archive["bars"][299]["t"])

    with pytest.raises(ValueError, match="unconfirmed tail"):
        fc.evaluate_frozen_hypothesis(archive, hypothesis)
