"""Contract and PHP runtime tests for the no-trade 60-second supervisor.

Tests use synthetic positions and plans only. No production endpoints, email,
Telegram, broker, secrets, or account data.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "hostinger_patch" / "supervisor_60s_core.php"
RUNNER = ROOT / "hostinger_patch" / "supervisor_60s.php"
STATUS = ROOT / "hostinger_patch" / "supervisor_status.php"
MIGRATION = ROOT / "hostinger_patch" / "migrations" / "005_manual_supervisor_audit.sql"


def php_eval(script: str):
    php = shutil.which("php")
    if php is None:
        pytest.skip("PHP CLI not installed")
    result = subprocess.run(
        [php, "-r", script], cwd=ROOT, text=True, capture_output=True,
        check=False, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("source", [CORE, RUNNER, STATUS])
def test_all_php_files_syntax_valid(source):
    php = shutil.which("php")
    if php is None:
        pytest.skip("PHP CLI not installed")
    result = subprocess.run(
        [php, "-l", str(source)], cwd=ROOT, text=True,
        capture_output=True, timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_positions_fail_closed_when_history_missing_stale_or_unverified():
    code = r"""
    function stc_notification_suppression_reason(array $event, ?DateTimeImmutable $now=null) {
      return $event['competition_id']==='closed-sep' ? 'competition_ended' : null;
    }
    require 'hostinger_patch/supervisor_60s_core.php';
    $now = new DateTimeImmutable('2026-10-14T12:00:00Z');
    $position = [
      'position_id'=>'paper-pos-1','competition_id'=>'active-contest','symbol'=>'OANDA:XAUUSD',
      'status'=>'OPEN','current_stop'=>100,'opened_at_utc'=>'2026-10-14 11:00:00',
    ];
    $history = fn($time) => [[
      'time'=>$time,'close'=>150,'recommendation'=>'WAIT','composite_score'=>0.0,
    ]];
    $states=[
      'none'=>stc_supervisor_position_state($position,[],$now),
      'stale'=>stc_supervisor_position_state($position,$history('2026-10-14T11:00:00Z'),$now),
      'recent'=>stc_supervisor_position_state($position,$history('2026-10-14T11:55:00Z'),$now),
      'future'=>stc_supervisor_position_state($position,$history('2026-10-14T12:03:00Z'),$now),
      'ended'=>stc_supervisor_position_state(array_merge($position,['competition_id'=>'closed-sep']),[],$now),
    ];
    echo json_encode($states, JSON_THROW_ON_ERROR);
    """
    got = php_eval(code)
    assert got["none"]["state"] == "SOURCE_UNVERIFIED"
    assert got["stale"]["state"] == "DATA_STALE"
    assert got["recent"]["state"] == "EXTERNAL_FILL_UNVERIFIED"
    assert got["future"]["reason"] == "source_in_future"
    assert got["ended"]["state"] == "ENDED_RECONCILIATION"
    for state in got.values():
        assert state["quote_verified"] is False
        assert state["external_fill_verified"] is False
        assert state["manual_action"] != "EXECUTE"


def test_manual_signal_ttl_never_extends_for_sleeping_owner_or_unverified_fill():
    code = r"""
    function stc_notification_suppression_reason(array $event, ?DateTimeImmutable $now=null) {
      return $event['competition_id']==='closed-sep' ? 'competition_ended' : null;
    }
    require 'hostinger_patch/supervisor_60s_core.php';
    $now=new DateTimeImmutable('2026-10-14T12:10:00Z');
    $base=['competition_id'=>'active-contest','plan_id'=>'plan-1'];
    $before=stc_supervisor_signal_state($base+['valid_until'=>'2026-10-14T12:05:00Z'],$now);
    $active=stc_supervisor_signal_state($base+['valid_until'=>'2026-10-14T12:15:00Z'],$now);
    $duplicate=stc_supervisor_signal_state($base+[
      'valid_until'=>'2026-10-14T12:15:00Z','owner_recorded_open'=>true],$now);
    $invalid=stc_supervisor_signal_state($base+['valid_until'=>'2026-10-14 12:15:00'],$now);
    $ended=stc_supervisor_signal_state(array_merge($base,[
      'competition_id'=>'closed-sep','valid_until'=>'2026-12-01T12:00:00Z']),$now);
    echo json_encode(compact('before','active','duplicate','invalid','ended'),JSON_THROW_ON_ERROR);
    """
    got=php_eval(code)
    assert got["before"]["state"]=="EXPIRED_SIGNAL"
    assert got["before"]["manual_action"]=="NO_ENTRY"
    assert got["active"]["state"]=="PENDING_MANUAL_CONFIRMATION"
    assert got["active"]["manual_action"]=="REVALIDATE_LIVE_PRICE_AND_ACCOUNT"
    assert got["duplicate"]["manual_action"]=="NO_DUPLICATE_ENTRY"
    assert got["invalid"]["state"]=="SIGNAL_TTL_UNVERIFIED"
    assert got["invalid"]["manual_action"]=="NO_ENTRY"
    assert got["ended"]["state"]=="EXPIRED_SIGNAL"


def test_job_is_cli_only_audit_only_and_idempotent():
    text=RUNNER.read_text(encoding="utf-8")
    assert "PHP_SAPI !== 'cli'" in text
    assert "['--dry-run', '--tick']" in text
    assert "GET_LOCK('stc_supervisor_60s_v1', 0)" in text
    assert "INSERT IGNORE INTO stc_supervisor_ticks" in text
    assert "INSERT IGNORE INTO stc_supervisor_watch_receipts" in text
    assert "READ_ONLY_DRY_RUN" in text
    assert "ALREADY_RECORDED" in text
    assert "2001" in text and "501" in text
    assert "MONITOR_UNHEALTHY" in text
    for forbidden in (
        "stc_dispatch_notification(", "stc_send_email(", "stc_send_telegram(",
        "mail(", "curl_init(", "place_order(", "strategy.entry",
        "UPDATE stc_positions", "DELETE FROM stc_positions",
        "UPDATE stc_account_state",
    ):
        assert forbidden not in text


def test_schema_is_additive_and_evidence_cannot_be_deleted_through_code():
    source=MIGRATION.read_text(encoding="utf-8")
    upper=source.upper()
    for name in (
        "stc_supervisor_ticks", "stc_supervisor_watches",
        "stc_supervisor_watch_receipts"
    ):
        assert "CREATE TABLE IF NOT EXISTS "+name in source
    assert "UNIQUE KEY uniq_stc_supervisor_receipt" in source
    for prohibited in ("DROP TABLE","DELETE FROM","TRUNCATE TABLE","ALTER TABLE","CREATE TRIGGER"):
        assert prohibited not in upper


def test_health_endpoint_requires_owner_and_never_claims_live_quotes():
    text=STATUS.read_text(encoding="utf-8")
    assert "stc_require_owner_auth($config)" in text
    assert "TICK_RECEIPTS_RECENT" in text
    assert "'poll_interval_proven' => $minuteCadenceProven" in text
    assert "count($recentTicks) === 30" in text
    assert "!== 60" in text
    assert "'external_tradingview_paper_fills_connected' => false" in text
    assert "'live_market_quote_connected' => false" in text
    assert "'email_enabled' => false" in text
    assert "'automatic_execution_available' => false" in text


def test_old_finished_contests_are_only_readonly_reconciliation():
    source=CORE.read_text(encoding="utf-8")
    assert "'ENDED_RECONCILIATION'" in source
    assert "'EXPIRED_SIGNAL'" in source
    assert "'NO_ENTRY'" in source
    assert "stc_notification_suppression_reason(" in source


def test_terminal_signals_are_not_written_each_minute_and_backlog_is_bounded():
    source = RUNNER.read_text(encoding="utf-8")
    assert "INTERVAL 2 HOUR" in source
    assert "INTERVAL 1 HOUR" in source
    assert "watch_state_capacity_exceeded" in source
    assert "priorStates" in source
    assert "'EXPIRED_SIGNAL', 'OWNER_RECORDED_OPEN'" in source
    assert "Already terminal: no resurrection or minute replay" in source
    assert "status['state'] !== 'PENDING_MANUAL_CONFIRMATION'" in source
    assert "incomplete_supervisor_tick_receipts" in source
    # Competition identity is part of signal idempotency, so two contests
    # can never dedupe one another when an upstream plan_id repeats.
    assert "stc_supervisor_watch_key('SIGNAL', $cid . '|' . $planId)" in source


def test_cadence_cannot_be_proven_using_stale_historical_tick_rows():
    source = STATUS.read_text(encoding="utf-8")
    assert "lastAge <= 150" in source
    assert "$minuteCadenceProven = $minuteCadenceProven && $healthy;" in source
    assert "count($recentTicks) === 30" in source
    assert "!== 60" in source


def test_time_parser_rejects_relative_and_invalid_calendar_dates():
    script = r"""
    require 'hostinger_patch/supervisor_60s_core.php';
    echo json_encode([
      'relative' => stc_supervisor_parse_time('tomorrow') === null,
      'wrong_calendar' => stc_supervisor_parse_time('2026-02-30T12:00:00Z') === null,
      'valid' => stc_supervisor_parse_time('2026-10-14T12:00:00Z')?->format('Y-m-d H:i:s'),
      'mysql_valid' => stc_supervisor_parse_time('2026-10-14 12:00:00')?->format('Y-m-d H:i:s'),
    ], JSON_THROW_ON_ERROR);
    """
    got = php_eval(script)
    assert got == {
        "relative": True, "wrong_calendar": True,
        "valid": "2026-10-14 12:00:00",
        "mysql_valid": "2026-10-14 12:00:00",
    }


def test_ingested_event_window_uses_production_analysis_completion_column():
    """Production has analysis_completed_at_utc, not webhook created_at_utc."""
    source = RUNNER.read_text(encoding="utf-8")
    assert "AND analysis_completed_at_utc >= UTC_TIMESTAMP() - INTERVAL 2 HOUR" in source
    assert "AND created_at_utc >= UTC_TIMESTAMP()" not in source
    cloud = (ROOT / "hostinger_patch" / "cloud_control.php").read_text(encoding="utf-8")
    assert "analysis_completed_at_utc" in cloud
