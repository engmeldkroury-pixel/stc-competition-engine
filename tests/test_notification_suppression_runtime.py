"""Runtime proof of STC old-contest Telegram suppression.

Run in PHP CLI on Linux CI; skip on Windows laptops without PHP. No network,
DB, account, Telegram or email is accessed by these tests.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


SOURCE = Path("hostinger_patch/notification_control.php")


def _run_php(program: str) -> object:
    binary = shutil.which("php")
    if binary is None:
        pytest.skip("PHP CLI is not installed on this test host")
    result = subprocess.run(
        [binary, "-r", program],
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_notification_php_syntax():
    binary = shutil.which("php")
    if binary is None:
        pytest.skip("PHP CLI is not installed on this test host")
    result = subprocess.run(
        [binary, "-l", str(SOURCE)],
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_closed_contests_and_nonactionable_heartbeats_are_suppressed_dynamically():
    source = SOURCE.read_text(encoding="utf-8")
    begin = source.index("function stc_notification_suppression_reason(")
    end = source.index("function stc_dispatch_notification(", begin)
    helper = source[begin:end]
    # This fake rule summary is an isolated test fixture, never production code.
    script = """
    function stc_competition_rule_summary($id) {
        $end = $id === 'amp-futures-sep-2026'
            ? '2026-09-30T12:00:00+00:00'
            : ($id === 'capital-africa-sep-2026'
                ? '2026-10-02T08:00:00+00:00' : null);
        if ($end === null) throw new RuntimeException('unknown');
        return ['end_utc'=>$end];
    }
    """ + helper + """
    $after = new DateTimeImmutable('2026-10-13T21:00:00Z');
    $before = new DateTimeImmutable('2026-09-20T09:00:00Z');
    echo json_encode([
      'amp_expired' => stc_notification_suppression_reason([
         'event_type'=>'SIGNAL', 'competition_id'=>'amp-futures-sep-2026'], $after),
      'capital_expired' => stc_notification_suppression_reason([
         'event_type'=>'POSITION_MANAGEMENT', 'competition_id'=>'capital-africa-sep-2026'], $after),
      'old_during_contest' => stc_notification_suppression_reason([
         'event_type'=>'SIGNAL', 'competition_id'=>'amp-futures-sep-2026'], $before),
      'new_contest_untouched' => stc_notification_suppression_reason([
         'event_type'=>'SIGNAL', 'competition_id'=>'future-competition-2026'], $after),
      'spot_lab_untouched' => stc_notification_suppression_reason([
         'event_type'=>'SIGNAL', 'competition_id'=>'crypto-spot-lab'], $after),
      'routine_heartbeat_blocked' => stc_notification_suppression_reason([
         'event_type'=>'SYSTEM_HEARTBEAT'], $after),
    ], JSON_THROW_ON_ERROR);
    """
    actual = _run_php(script)
    assert actual == {
        "amp_expired": "competition_ended",
        "capital_expired": "competition_ended",
        "old_during_contest": None,
        "new_contest_untouched": None,
        "spot_lab_untouched": None,
        "routine_heartbeat_blocked": "routine_heartbeat_disabled",
    }


def test_mail_send_is_disconnected_from_all_code_paths():
    source = SOURCE.read_text(encoding="utf-8")
    assert "@mail(" not in source
    assert "'email_configured' => false" in source
    assert "email_disabled_by_owner" in source
