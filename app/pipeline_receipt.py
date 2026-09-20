from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    """Return a stable SHA-256 hash for a source event payload."""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_pipeline_receipt(
    event_id: str,
    payload: dict[str, Any],
    *,
    status: str,
    action: str,
    signal_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic reconciliation receipt for one bridge event.

    The receipt is intentionally free of process-local timestamps so the same
    event/payload produces the same receipt across retries and workers.
    """
    payload_hash = canonical_payload_hash(payload)
    receipt_key = f"{event_id}|{payload_hash}"
    receipt_id = "stc-receipt-" + hashlib.sha256(receipt_key.encode("utf-8")).hexdigest()[:32]
    return {
        "receipt_id": receipt_id,
        "event_id": event_id,
        "payload_sha256": payload_hash,
        "competition_id": payload.get("competition_id"),
        "symbol": payload.get("symbol"),
        "event_time": payload.get("time"),
        "status": status,
        "action": action,
        "signal_id": signal_id,
        "execution": "manual_only",
    }
