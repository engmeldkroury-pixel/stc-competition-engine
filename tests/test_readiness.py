from app.readiness import build_readiness


def test_readiness_reports_analysis_ready_and_manual_execution_only():
    result = build_readiness({"safe_mode": False, "kill_switch": False, "reason": None, "updated_utc": "2026-09-21T00:00:00+00:00"})
    assert result["analysis_ready"] is True
    assert result["historical_context_capable"] is True
    assert result["historical_context_required"] is True
    assert result["historical_window_trading_days"] == 252
    assert result["historical_context_timeframe"] == "1D"
    assert result["historical_context_policy"] == "previous_confirmed_daily_bar"
    assert result["approval_runtime_ready"] is True
    assert result["execution_mode"] == "manual_only"
    assert result["automatic_execution_available"] is False
    assert result["human_approval_required"] is True
    assert result["capital_symbols_total"] == 10
    assert result["capital_symbols_verified"] == 10
    assert result["runtime_quote_evidence_required_for_all_approvals"] is True


def test_readiness_blocks_when_safe_mode_or_kill_switch_is_active():
    safe = build_readiness({"safe_mode": True, "kill_switch": False})
    kill = build_readiness({"safe_mode": False, "kill_switch": True})
    assert safe["approval_runtime_ready"] is False
    assert "safe_mode_active" in safe["blockers"]
    assert kill["approval_runtime_ready"] is False
    assert "kill_switch_active" in kill["blockers"]
