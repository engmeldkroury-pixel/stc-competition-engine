import hashlib
import json
from datetime import datetime, timezone

from app.cloud_approval import build_cloud_snapshot, cloud_readiness

NOW = datetime(2026, 9, 21, 8, 0, tzinfo=timezone.utc)
ALLOWED = {"capital-africa-sep-2026": {"CAPITALCOM:XAUUSD"}}


def _row():
    event_id = "stc-unit-synthetic-001"
    signal_id = "bridge-" + hashlib.sha256(event_id.encode()).hexdigest()[:32]
    payload = {
        "event_id": event_id,
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "time": "2026-09-21T07:45:00Z",
        "close": 4000.0,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    receipt = {
        "receipt_id": "stc-receipt-" + hashlib.sha256(f"{event_id}|{digest}".encode()).hexdigest()[:32],
        "event_id": event_id,
        "payload_sha256": digest,
        "competition_id": payload["competition_id"],
        "symbol": payload["symbol"],
        "event_time": payload["time"],
        "status": "analyzed",
        "action": "signal_created",
        "signal_id": signal_id,
        "execution": "manual_only",
    }
    signal = {
        "signal_id": signal_id,
        "competition_id": payload["competition_id"],
        "symbol": payload["symbol"],
        "composite_score": 0.4,
        "recommendation": "LONG",
        "requires_human_approval": True,
    }
    envelope = {
        "competition_id": payload["competition_id"],
        "symbol": payload["symbol"],
        "reference_signal_score": 0.4,
        "reference_price": 4000.0,
        "entry_min": 3990.0,
        "entry_max": 4010.0,
        "issued_at": "2026-09-21T07:59:00Z",
        "valid_until": "2026-09-21T08:29:00Z",
    }
    return {
        "event_id": event_id,
        "status": "ingested",
        "payload": payload,
        "result": {
            "event_id": event_id,
            "status": "analyzed",
            "receipt": receipt,
            "decision": {
                "action": "signal_created",
                "execution": "manual_approval_required",
                "signal": signal,
                "approval_envelope": envelope,
            },
        },
    }


def test_valid_cloud_signal_is_visible_but_blocked():
    result = build_cloud_snapshot({"ok": True, "events": [_row()]}, ALLOWED, now=NOW)
    assert len(result["cards"]) == 1
    card = result["cards"][0]
    assert card["approved"] is False
    assert card["execution"] == "manual_only"
    assert "durable_owner_approval_not_connected" in card["blockers"]


def test_tampered_receipt_is_quarantined():
    row = _row()
    row["result"]["receipt"]["payload_sha256"] = "0" * 64
    result = build_cloud_snapshot({"ok": True, "events": [row]}, ALLOWED, now=NOW)
    assert result["cards"] == []
    assert result["quarantined_count"] == 1


def test_cloud_readiness_fails_closed():
    r = cloud_readiness()
    assert r["cloud_approval_ready"] is False
    assert r["effective_policy"]["safe_mode"] is True
    assert r["effective_policy"]["kill_switch"] is True
    assert r["automatic_execution_available"] is False
