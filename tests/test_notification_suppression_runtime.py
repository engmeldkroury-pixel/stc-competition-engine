"""PHP runtime proof of registered contest lifecycle and notification containment.

Never contacts the live DB, Telegram, Gmail or broker. Local PHP fixture only.
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
        pytest.skip("PHP CLI not available on this test host")
    result = subprocess.run(
        [binary, "-r", program], text=True, capture_output=True,
        timeout=10, check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _helper_source() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    begin = source.index("function stc_notification_suppression_reason(")
    end = source.index("function stc_dispatch_notification(", begin)
    return source[begin:end]


def _fake_registered_rules() -> str:
    return """
    function stc_competition_rule_summary($id) {
        $rules = [
          'amp-futures-sep-2026' => [
            'competition_id'=>'amp-futures-sep-2026',
            'start_utc'=>'2026-09-01T08:00:00+00:00',
            'end_utc'=>'2026-09-30T12:00:00+00:00',
          ],
          'capital-africa-sep-2026' => [
            'competition_id'=>'capital-africa-sep-2026',
            'start_utc'=>'2026-09-16T08:00:00+00:00',
            'end_utc'=>'2026-10-02T08:00:00+00:00',
          ],
          'future-competition-2027' => [
            'competition_id'=>'future-competition-2027',
            'start_utc'=>'2027-03-01T08:00:00Z',
            'end_utc'=>'2027-03-05T08:00:00Z',
            'status'=>'ACTIVE',
          ],
          'future-archived-2027' => [
            'competition_id'=>'future-archived-2027',
            'start_utc'=>'2027-03-01T08:00:00Z',
            'end_utc'=>'2027-03-05T08:00:00Z',
            'status'=>'ARCHIVED',
          ],
          'malformed-competition' => [
            'competition_id'=>'malformed-competition',
            'start_utc'=>'yesterday',
            'end_utc'=>'tomorrow',
          ],
          'inverted-competition' => [
            'competition_id'=>'inverted-competition',
            'start_utc'=>'2027-03-05T08:00:00Z',
            'end_utc'=>'2027-03-01T08:00:00Z',
          ],
          'forged-identity' => [
            'competition_id'=>'wrong-contest-id',
            'start_utc'=>'2027-03-01T08:00:00Z',
            'end_utc'=>'2027-03-05T08:00:00Z',
          ],
        ];
        if (!isset($rules[$id])) throw new RuntimeException('not registered');
        return $rules[$id];
    }
    """


def test_notification_php_syntax():
    binary = shutil.which("php")
    if binary is None:
        pytest.skip("PHP CLI not available on this test host")
    result = subprocess.run(
        [binary, "-l", str(SOURCE)],
        text=True, capture_output=True, timeout=10, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_old_and_new_contests_auto_stop_on_registered_utc_boundaries():
    program = _fake_registered_rules() + _helper_source() + """
    $oldAfter = new DateTimeImmutable('2026-10-13T21:00:00Z');
    $oldDuring = new DateTimeImmutable('2026-09-20T09:00:00Z');
    $oldBefore = new DateTimeImmutable('2026-08-30T09:00:00Z');
    $futureBefore = new DateTimeImmutable('2027-02-28T08:00:00Z');
    $futureLive = new DateTimeImmutable('2027-03-02T12:00:00Z');
    $futureBoundary = new DateTimeImmutable('2027-03-05T08:00:00Z');
    $signal = fn ($id) => ['competition_id'=>$id, 'event_type'=>'SIGNAL'];
    echo json_encode([
      'amp_after' => stc_notification_suppression_reason($signal('amp-futures-sep-2026'),$oldAfter),
      'capital_after' => stc_notification_suppression_reason($signal('capital-africa-sep-2026'),$oldAfter),
      'amp_during' => stc_notification_suppression_reason($signal('amp-futures-sep-2026'),$oldDuring),
      'amp_before' => stc_notification_suppression_reason($signal('amp-futures-sep-2026'),$oldBefore),
      'future_before' => stc_notification_suppression_reason($signal('future-competition-2027'),$futureBefore),
      'future_active' => stc_notification_suppression_reason($signal('future-competition-2027'),$futureLive),
      'future_at_end' => stc_notification_suppression_reason($signal('future-competition-2027'),$futureBoundary),
      'future_after' => stc_notification_suppression_reason($signal('future-competition-2027'),$oldAfter),
      'unknown' => stc_notification_suppression_reason($signal('unregistered-competition'),$futureLive),
      'missing_id' => stc_notification_suppression_reason(['event_type'=>'SIGNAL'],$futureLive),
      'archived' => stc_notification_suppression_reason($signal('future-archived-2027'),$futureLive),
      'malformed' => stc_notification_suppression_reason($signal('malformed-competition'),$futureLive),
      'inverted' => stc_notification_suppression_reason($signal('inverted-competition'),$futureLive),
      'wrong_id' => stc_notification_suppression_reason($signal('forged-identity'),$futureLive),
      'spot_research' => stc_notification_suppression_reason($signal('crypto-spot-lab'),$futureLive),
      'heartbeat' => stc_notification_suppression_reason(['event_type'=>'SYSTEM_HEARTBEAT'],$futureLive),
      'test_message' => stc_notification_suppression_reason(['event_type'=>'OWNER_TEST'],$futureLive),
    ], JSON_THROW_ON_ERROR);
    """
    actual = _run_php(program)
    assert actual == {
        "amp_after": "competition_ended",
        "capital_after": "competition_ended",
        "amp_during": None,
        "amp_before": "competition_not_started",
        "future_before": "competition_not_started",
        "future_active": None,
        "future_at_end": "competition_ended",
        # Oct 2026 is before the Mar 2027 contest, not after it.
        "future_after": "competition_not_started",
        "unknown": "competition_unregistered",
        "missing_id": "competition_id_missing",
        "archived": "competition_not_active",
        "malformed": "competition_schedule_unverified",
        "inverted": "competition_schedule_invalid",
        "wrong_id": "competition_identity_mismatch",
        "spot_research": "spot_lab_research_only",
        "heartbeat": "routine_heartbeat_disabled",
        "test_message": "unsolicited_test_messages_disabled",
    }


def test_unknown_contest_is_suppressed_before_any_db_or_telegram_side_effect():
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index("function stc_dispatch_notification(")
    end = source.index("function stc_account_state_for(", start)
    program = _fake_registered_rules() + _helper_source() + source[start:end] + """
    function stc_notification_id($key) { return 'fixture-' . $key; }
    class NoDatabaseCalls extends PDO { public function __construct() {} }
    $db = new NoDatabaseCalls();
    $result = stc_dispatch_notification($db, [], [
      'event_type'=>'NEW_LOCKED_PLAN',
      'event_key'=>'unauthorized:1',
      'competition_id'=>'unregistered-competition',
      'title'=>'No message',
      'body'=>'No message',
    ]);
    echo json_encode($result, JSON_THROW_ON_ERROR);
    """
    result = _run_php(program)
    assert result["skipped"] is True
    assert result["reason"] == "competition_unregistered"
    assert result["new_event"] is False
    assert result["delivered_any"] is False
    assert result["channels"] == []


def test_mail_transport_stays_hard_disabled():
    source = SOURCE.read_text(encoding="utf-8")
    assert "@mail(" not in source
    assert "'email_configured' => false" in source
    assert "email_disabled_by_owner" in source
