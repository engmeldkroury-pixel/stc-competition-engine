from datetime import datetime, timedelta, timezone
import json

import pytest

from app.calibration_registry import (
    candidate_record_from_research_result,
    load_registry,
    lookup_runtime_calibration,
    runtime_calibration_usable,
)


UTC = timezone.utc


def _research_result(probability=0.72, sample_size=80):
    return {
        "symbol": "CAPITALCOM:XAUUSD",
        "research_report": {
            "status": "VALIDATED",
            "selected_strategy": "smc_structure_liquidity",
            "selected_timeframe": "60",
            "robust_score": 62.0,
            "setup_probability": {
                "status": "CALIBRATED",
                "sample_size": sample_size,
                "wins": 58,
                "losses": 22,
                "observed_win_rate": 0.725,
                "estimated_win_probability": probability,
                "confidence_low": 0.61,
                "confidence_high": 0.80,
                "note": "test",
            },
            "test_expectancy_r": 0.31,
            "forward_expectancy_r": 0.22,
            "test_profit_factor": 1.48,
            "forward_profit_factor": 1.32,
            "feature_participation_pct": {
                "liquidity_sweep": 34.0,
                "choch": 28.0,
                "break_retest": 22.0,
                "relative_volume": 16.0,
            },
        },
    }


def test_candidate_registry_record_requires_calibrated_probability_and_forward_edge():
    now = datetime(2026, 9, 22, tzinfo=UTC)
    record = candidate_record_from_research_result(
        _research_result(),
        data_end_utc=now - timedelta(hours=1),
        generated_at_utc=now,
    )
    assert record["estimated_probability"] == 0.72
    assert record["sample_size"] == 80
    assert record["informational_only"] is True
    assert abs(sum(record["feature_weights"].values()) - 1.0) < 1e-12

    bad = _research_result(sample_size=20)
    with pytest.raises(ValueError, match="sample is below 50"):
        candidate_record_from_research_result(
            bad,
            data_end_utc=now,
            generated_at_utc=now,
        )


def test_runtime_registry_fails_closed_when_stale_or_unprofitable(tmp_path):
    now = datetime(2026, 9, 22, tzinfo=UTC)
    record = candidate_record_from_research_result(
        _research_result(),
        data_end_utc=now - timedelta(days=30),
        generated_at_utc=now - timedelta(days=29),
    )
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps({
            "schema_version": "stc-calibration-registry-v1",
            "records": [record],
        }),
        encoding="utf-8",
    )
    load_registry.cache_clear()
    found, reasons = lookup_runtime_calibration(
        "CAPITALCOM:XAUUSD",
        as_of=now,
        path=str(path),
    )
    assert found is None
    assert "research_calibration_stale" in reasons


def test_runtime_registry_returns_only_current_robust_record(tmp_path):
    now = datetime(2026, 9, 22, tzinfo=UTC)
    record = candidate_record_from_research_result(
        _research_result(),
        data_end_utc=now - timedelta(hours=2),
        generated_at_utc=now - timedelta(hours=1),
    )
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps({
            "schema_version": "stc-calibration-registry-v1",
            "records": [record],
        }),
        encoding="utf-8",
    )
    load_registry.cache_clear()
    found, reasons = lookup_runtime_calibration(
        "CAPITALCOM:XAUUSD",
        as_of=now,
        path=str(path),
    )
    assert reasons == ()
    assert found is not None
    ok, validation_reasons = runtime_calibration_usable(found, as_of=now)
    assert ok is True
    assert validation_reasons == ()
    assert found.strategy_id == "smc_structure_liquidity"
