"""Read persisted bridge signals without granting or persisting approval.

A matching receipt proves internal consistency, not authenticity. Read only
through the authenticated bridge. No SQLite, claims, acknowledgements or trades.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Collection, Mapping
from datetime import datetime, timezone
from typing import Any, Protocol


class CloudSnapshotError(ValueError):
    """An upstream snapshot cannot safely be interpreted."""


class InboxReader(Protocol):
    def inbox(self, status: str = "received", limit: int = 20) -> dict[str, Any]: ...


BLOCKERS = (
    "durable_runtime_control_not_connected",
    "durable_owner_approval_not_connected",
    "fresh_execution_evidence_not_assessed",
)
EVENT_ID = re.compile(r"[A-Za-z0-9:|._!/-]{1,512}\Z")


def cloud_readiness() -> dict[str, Any]:
    return {
        "scope": "cloud_read_only",
        "cloud_approval_ready": False,
        "approval_runtime_ready": False,
        "automatic_execution_available": False,
        "human_approval_required": True,
        "execution_mode": "manual_only",
        "persisted_runtime_control": None,
        "effective_policy": {
            "safe_mode": True, "kill_switch": True,
            "source": "fail_closed_default", "persisted": False,
        },
        "blockers": list(BLOCKERS),
    }


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("invalid_timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone_required")
    return parsed.astimezone(timezone.utc)


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid_number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite_number")
    return number


def _validate_record(row: dict) -> tuple[dict, dict, dict]:
    event_id = row.get("event_id")
    if not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
        raise ValueError("invalid_event_id")
    if row.get("status") != "ingested":
        raise ValueError("event_not_ingested")
    result, payload = row.get("result"), row.get("payload")
    if not isinstance(result, dict) or not isinstance(payload, dict):
        raise ValueError("missing_result_or_source_payload")
    receipt, decision = result.get("receipt"), result.get("decision")
    if not isinstance(receipt, dict) or not isinstance(decision, dict):
        raise ValueError("missing_receipt_or_decision")
    if result.get("event_id") != event_id or payload.get("event_id") not in (None, event_id):
        raise ValueError("event_identity_mismatch")
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    receipt_id = "stc-receipt-" + hashlib.sha256(f"{event_id}|{digest}".encode()).hexdigest()[:32]
    expected = {
        "receipt_id": receipt_id, "event_id": event_id, "payload_sha256": digest,
        "competition_id": payload.get("competition_id"), "symbol": payload.get("symbol"),
        "event_time": payload.get("time"), "status": result.get("status"),
        "action": decision.get("action"), "execution": "manual_only",
    }
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError("receipt_mismatch")
    for key in ("competition_id", "symbol"):
        if row.get(key) is not None and row[key] != payload.get(key):
            raise ValueError("row_target_mismatch")
    return result, receipt, payload


def _card(
    row: dict,
    result: dict,
    receipt: dict,
    payload: dict,
    allowed: Mapping[str, Collection[str]],
    now: datetime,
) -> dict:
    decision = result["decision"]
    signal, envelope = decision.get("signal"), decision.get("approval_envelope")
    if not isinstance(signal, dict) or not isinstance(envelope, dict):
        raise ValueError("missing_signal_or_envelope")
    competition, symbol = receipt["competition_id"], receipt["symbol"]
    if not isinstance(competition, str) or competition not in allowed:
        raise ValueError("unknown_competition")
    if not isinstance(symbol, str) or symbol not in allowed[competition]:
        raise ValueError("symbol_not_allowed")
    for obj in (signal, envelope):
        if obj.get("competition_id") != competition or obj.get("symbol") != symbol:
            raise ValueError("target_mismatch")
    signal_id = "bridge-" + hashlib.sha256(row["event_id"].encode()).hexdigest()[:32]
    if signal.get("signal_id") != signal_id or receipt.get("signal_id") != signal_id:
        raise ValueError("signal_identity_mismatch")
    if decision.get("execution") != "manual_approval_required" or signal.get("requires_human_approval") is not True:
        raise ValueError("human_approval_required")
    recommendation = signal.get("recommendation")
    if recommendation not in ("LONG", "SHORT", "WAIT"):
        raise ValueError("invalid_recommendation")
    score = _number(signal.get("composite_score"))
    if not -1 <= score <= 1 or _number(envelope.get("reference_signal_score")) != score:
        raise ValueError("score_mismatch")
    lower, ref, upper = (_number(envelope.get(key)) for key in ("entry_min", "reference_price", "entry_max"))
    if not 0 < lower <= ref <= upper or _number(payload.get("close")) != ref:
        raise ValueError("invalid_price_envelope")
    issued, expires, source_time = (
        _utc(value)
        for value in (envelope.get("issued_at"), envelope.get("valid_until"), payload.get("time"))
    )
    if expires <= issued:
        raise ValueError("invalid_envelope_window")
    blockers = list(BLOCKERS)
    if issued > now or source_time > now:
        blockers.append("future_dated_signal")
    if now >= expires:
        blockers.append("signal_expired")
    if recommendation == "WAIT":
        blockers.append("wait_is_not_an_order")
    return {
        "event_id": row["event_id"],
        "signal_id": signal_id,
        "competition_id": competition,
        "symbol": symbol,
        "recommendation": recommendation,
        "composite_score": score,
        "receipt_id": receipt["receipt_id"],
        "payload_sha256": receipt["payload_sha256"],
        "source_time": source_time.isoformat(),
        "envelope": {
            "issued_at": issued.isoformat(),
            "valid_until": expires.isoformat(),
            "entry_min": lower,
            "reference_price": ref,
            "entry_max": upper,
        },
        "approved": False,
        "approval_status": "blocked",
        "human_approval_required": True,
        "execution": "manual_only",
        "blockers": blockers,
    }


def build_cloud_snapshot(
    body: dict[str, Any],
    allowed: Mapping[str, Collection[str]],
    *,
    now: datetime | None = None,
    scan_limit: int = 100,
) -> dict[str, Any]:
    """Inspect top-level records only; quarantine conflicting duplicate IDs."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise CloudSnapshotError("timezone_required")
    now = now.astimezone(timezone.utc)
    if type(scan_limit) is not int or not 1 <= scan_limit <= 100:
        raise CloudSnapshotError("invalid_scan_limit")
    if not isinstance(body, dict) or body.get("ok") is not True or not isinstance(body.get("events"), list):
        raise CloudSnapshotError("invalid_bridge_inbox_contract")
    rows = body["events"]
    if len(rows) > scan_limit:
        raise CloudSnapshotError("bridge_page_exceeds_limit")
    groups: dict[str, list[dict]] = {}
    quarantined, contexts, cards = 0, 0, []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("event_id"), str):
            quarantined += 1
        else:
            groups.setdefault(row["event_id"], []).append(row)
    for records in groups.values():
        try:
            if len({_canonical(record) for record in records}) != 1:
                raise ValueError("conflicting_duplicate_event")
            row = records[0]
            result, receipt, payload = _validate_record(row)
            if result.get("status") == "ingested_context":
                if result["decision"].get("execution") != "none" or receipt.get("signal_id") is not None:
                    raise ValueError("unsafe_context_result")
                contexts += 1
            elif result.get("status") == "analyzed" and result["decision"].get("action") == "signal_created":
                cards.append(_card(row, result, receipt, payload, allowed, now))
            else:
                raise ValueError("unsupported_result_kind")
        except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
            quarantined += 1
    return {
        "ok": True,
        "observed_at_utc": now.isoformat(),
        "source": "hostinger_bridge_inbox",
        "scope": "bounded_read_only_snapshot",
        "records_scanned": len(rows),
        "unique_event_ids": len(groups),
        "scan_limit": scan_limit,
        "page_may_be_truncated": len(rows) == scan_limit,
        "context_events": contexts,
        "quarantined_count": quarantined,
        "cards": cards,
        "readiness": cloud_readiness(),
    }


def read_cloud_snapshot(
    client: InboxReader,
    allowed: Mapping[str, Collection[str]],
    *,
    now: datetime | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    if type(limit) is not int or not 1 <= limit <= 100:
        raise CloudSnapshotError("invalid_scan_limit")
    return build_cloud_snapshot(
        client.inbox(status="ingested", limit=limit),
        allowed,
        now=now,
        scan_limit=limit,
    )
