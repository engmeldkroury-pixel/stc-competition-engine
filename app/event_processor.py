from __future__ import annotations

from .event_decision import decide_bridge_event
from .storage import (
    bridge_event_finish,
    bridge_event_start,
    log_event,
    save_approval_envelope,
    save_signal,
)


TERMINAL_LOCAL_STATUSES = {"analyzed", "ingested_context", "rejected", "failed"}


def process_bridge_event(event_id: str, payload: dict) -> dict:
    started = bridge_event_start(event_id, payload)
    if not started["is_new"] and started["status"] in TERMINAL_LOCAL_STATUSES:
        return {
            "event_id": event_id,
            "local_duplicate": True,
            "status": started["status"],
            "decision": started.get("decision"),
            "note": started.get("note"),
        }

    outcome = decide_bridge_event(event_id, payload)
    status = outcome["status"]
    decision = outcome["decision"]
    note = outcome.get("note")

    if status == "analyzed" and decision.get("action") == "signal_created":
        signal = decision["signal"]
        envelope = decision["approval_envelope"]
        save_signal(signal)
        save_approval_envelope(signal["signal_id"], envelope)
        log_event(
            "bridge_event_analyzed",
            {
                "event_id": event_id,
                "signal_id": signal["signal_id"],
                "recommendation": signal["recommendation"],
            },
            signal["competition_id"],
            signal["symbol"],
        )

    bridge_event_finish(event_id, status, decision, note)
    return {
        "event_id": event_id,
        "local_duplicate": False,
        "status": status,
        "decision": decision,
        "note": note,
    }
