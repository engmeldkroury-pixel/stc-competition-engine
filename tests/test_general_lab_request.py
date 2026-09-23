from __future__ import annotations

import pytest

import app.general_lab_request as general_lab_request


def test_general_lab_completion_requires_provider_qualified_symbol():
    with pytest.raises(ValueError, match="provider-qualified"):
        general_lab_request.build_general_lab_completion(
            {
                "request_id": "lab-1",
                "resolved_symbol": "XAUUSD",
                "series": {"15m": {"bars": []}},
            }
        )


def test_general_lab_completion_is_research_only_and_includes_shadow_context(monkeypatch):
    seen = {}

    def fake_run(payload):
        seen["payload"] = payload
        return {
            "symbol": payload["symbol"],
            "research_report": {"status": "NO_VALIDATED_STRATEGY"},
            "community_ensemble_profiles": {},
        }

    class Row:
        pass

    row = Row()
    monkeypatch.setattr(general_lab_request, "run_symbol_research", fake_run)
    monkeypatch.setattr(general_lab_request, "shadow_candidates", lambda symbol: (row,))
    monkeypatch.setattr(
        general_lab_request,
        "public_shadow_record",
        lambda _: {
            "symbol": "CAPITALCOM:XAUUSD",
            "timeframe": "15",
            "component_id": "range_filter_guikroth",
            "live_authority": False,
        },
    )

    completion = general_lab_request.build_general_lab_completion(
        {
            "request_id": "lab-2",
            "resolved_symbol": "capitalcom:xauusd",
            "series": {"15m": {"bars": [{"t": 1}]}},
        }
    )

    assert completion["action"] == "COMPLETE"
    assert completion["request_id"] == "lab-2"
    assert completion["resolved_symbol"] == "CAPITALCOM:XAUUSD"
    assert seen["payload"]["symbol"] == "CAPITALCOM:XAUUSD"
    result = completion["result"]
    assert result["general_lab"] is True
    assert result["execution"] == "research_only"
    assert result["live_authority"] is False
    assert result["promotion_required"] is True
    assert result["data_source_policy"] == "exact_provider_history_required_no_silent_substitution"
    assert result["existing_shadow_records"][0]["component_id"] == "range_filter_guikroth"
