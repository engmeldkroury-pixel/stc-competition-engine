import copy
import json
from pathlib import Path

import pytest

from app import frozen_confirmation as fc
from app.walkforward import BacktestStats


def _archive(count=1200, start_t=1700000000):
    bars = []
    for i in range(count):
        close = 100.0 + i * 0.01
        bars.append(
            {
                "t": start_t + i * 900,
                "o": close - 0.01,
                "h": close + 0.05,
                "l": close - 0.05,
                "c": close,
                "v": 1000 + i,
            }
        )
    return {
        "symbol": "TEST:X",
        "interval": "15m",
        "bars": bars,
        "archive": {
            "schema_version": "stc-ohlcv-archive-v1",
            "provider": "TradingView Official MCP",
            "coverage_first_t": bars[0]["t"],
            "coverage_last_t": bars[-1]["t"],
            "withheld_unconfirmed_t": bars[-1]["t"] + 900,
        },
    }


def _hypothesis(freeze_t, *, context_path="context.json"):
    return fc.hypothesis_from_dict(
        {
            "hypothesis_id": "test_h1",
            "symbol": "TEST:X",
            "timeframe": "15",
            "strategy_id": "vwap_reversion",
            "archive_path": "unused.json",
            "context_path": context_path,
            "freeze_t": freeze_t,
            "role": "BASELINE_COMPARATOR",
            "development_status": "FORWARD_FAILED",
            "source_run_id": 1,
            "allowed_regimes": [],
            "params": {
                "threshold": 0.72,
                "stop_atr": 1.2,
                "target_r": 2.5,
                "max_hold_bars": 16,
                "min_agreement": 0.62,
                "min_independent_confirmations": 4,
                "min_hard_confirmations": 1,
                "round_turn_cost_r": 0.02,
            },
        }
    )


def _context(archive, hypothesis, freeze_index):
    frozen = copy.deepcopy(archive["bars"][freeze_index - 999 : freeze_index + 1])
    return {
        "success": True,
        "symbol": archive["symbol"],
        "interval": archive["interval"],
        "count": len(frozen),
        "bars": frozen,
        "frozen_context": {
            "schema_version": "stc-frozen-context-v1",
            "provider": "TradingView Official MCP",
            "hypothesis_id": hypothesis.hypothesis_id,
            "freeze_t": hypothesis.freeze_t,
            "coverage_first_t": frozen[0]["t"],
            "coverage_last_t": frozen[-1]["t"],
            "context_bars": len(frozen),
        },
    }


def _empty_stats():
    return BacktestStats(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_v2_manifest_requires_frozen_context_path():
    raw = {
        "schema_version": "stc-frozen-confirmation-v2",
        "optimization_locked": True,
        "hypotheses": [
            {
                "hypothesis_id": "test_h1",
                "symbol": "TEST:X",
                "timeframe": "15",
                "strategy_id": "vwap_reversion",
                "archive_path": "unused.json",
                "freeze_t": 1700000000,
                "role": "BASELINE_COMPARATOR",
                "development_status": "FORWARD_FAILED",
                "params": {
                    "threshold": 0.72,
                    "stop_atr": 1.2,
                    "target_r": 2.5,
                    "max_hold_bars": 16,
                },
            }
        ],
    }
    with pytest.raises(ValueError, match="requires context_path"):
        fc.load_frozen_hypotheses(raw)


def test_context_lock_ignores_pre_freeze_archive_revisions(monkeypatch):
    original = _archive()
    freeze_index = 1099
    freeze_t = original["bars"][freeze_index]["t"]
    hypothesis = _hypothesis(freeze_t)
    context = _context(original, hypothesis, freeze_index)

    revised_archive = copy.deepcopy(original)
    revised_archive["bars"][500]["l"] -= 5.0
    revised_archive["bars"][500]["v"] += 99999

    captured = {}

    def fake_materialize(symbol, timeframe, bars, *, start_index):
        captured["bars"] = bars
        captured["start_index"] = start_index
        return {}

    def fake_backtest(*args, **kwargs):
        return [], _empty_stats()

    monkeypatch.setattr(fc, "_materialize_confirmation_snapshots", fake_materialize)
    monkeypatch.setattr(fc, "backtest_strategy", fake_backtest)

    result = fc.evaluate_frozen_hypothesis(
        revised_archive,
        hypothesis,
        frozen_context_payload=context,
    )

    combined = captured["bars"]
    assert captured["start_index"] == 1000
    assert len(combined) == 1100
    # Original archive bar 500 becomes context position 400; the later archive
    # revision must not leak into the frozen feature warm-up.
    assert combined[400].low == pytest.approx(original["bars"][500]["l"])
    assert combined[400].volume == pytest.approx(original["bars"][500]["v"])
    assert result.unseen_bars == 100
    assert result.historical_context_locked is True
    assert result.frozen_context_bars == 1000
    assert result.live_calibration_authority is False


def test_context_must_end_exactly_at_freeze():
    archive = _archive()
    freeze_index = 1099
    hypothesis = _hypothesis(archive["bars"][freeze_index]["t"])
    context = _context(archive, hypothesis, freeze_index)
    context["frozen_context"]["coverage_last_t"] -= 900

    with pytest.raises(ValueError, match="coverage metadata"):
        fc.evaluate_frozen_hypothesis(
            archive,
            hypothesis,
            frozen_context_payload=context,
        )


def test_real_v2_context_files_are_exactly_1000_bars_and_end_at_freeze():
    root = Path(".")
    manifest = json.loads(
        (root / "research_hypotheses/frozen_15m_v2.json").read_text(encoding="utf-8")
    )
    hypotheses = fc.load_frozen_hypotheses(manifest)
    assert len(hypotheses) == 2

    for hypothesis in hypotheses:
        assert hypothesis.context_path
        context = json.loads(
            (root / hypothesis.context_path).read_text(encoding="utf-8")
        )
        bars = context["bars"]
        assert len(bars) == 1000
        assert bars[-1]["t"] == hypothesis.freeze_t
        assert context["frozen_context"]["provider"] == "TradingView Official MCP"
        assert context["frozen_context"]["hypothesis_id"] == hypothesis.hypothesis_id
