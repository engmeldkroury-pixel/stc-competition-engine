from __future__ import annotations

import json

import pytest

from app.shadow_promotion_registry import (
    ALLOWED_STATES,
    load_shadow_registry,
    next_research_state,
    public_shadow_record,
)


def test_default_shadow_registry_is_research_only():
    load_shadow_registry.cache_clear()
    rows = load_shadow_registry()
    assert len(rows) == 6
    assert {x.state for x in rows} == {"FROZEN_PASS"}
    assert all(x.live_authority is False for x in rows)
    assert all(next_research_state(x) == "SHADOW" for x in rows)


def test_shadow_registry_rejects_live_authority(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({
        "schema_version": "stc-community-shadow-registry-v1",
        "records": [{
            "symbol": "TEST:X",
            "timeframe": "15",
            "component_id": "x",
            "family": "trend",
            "state": "SHADOW",
            "selected_parameters": {},
            "development_test_trades": 30,
            "development_test_expectancy_r": 0.1,
            "development_test_profit_factor": 1.2,
            "development_forward_trades": 20,
            "development_forward_expectancy_r": 0.1,
            "development_forward_profit_factor": 1.2,
            "frozen_trades": 20,
            "frozen_expectancy_r": 0.1,
            "frozen_profit_factor": 1.2,
            "frozen_max_drawdown_r": 2.0,
            "source_run_id": 1,
            "source_date": "2026-09-24",
            "live_authority": True
        }]
    }), encoding="utf-8")
    load_shadow_registry.cache_clear()
    with pytest.raises(ValueError, match="cannot grant live authority"):
        load_shadow_registry(str(path))


def test_public_shadow_record_never_grants_execution():
    load_shadow_registry.cache_clear()
    row = load_shadow_registry()[0]
    public = public_shadow_record(row)
    assert public["live_authority"] is False
    assert public["execution"] == "research_only"
    assert public["next_research_state"] == "SHADOW"
    assert tuple(ALLOWED_STATES) == (
        "FROZEN_PASS",
        "SHADOW",
        "MULTITF_CONFIRMED",
        "ELIGIBLE_FOR_OWNER_PROMOTION",
    )
