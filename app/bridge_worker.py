from __future__ import annotations

from dataclasses import dataclass

from .bridge_client import BridgeClient
from .event_processor import process_bridge_event
from .storage import bridge_event_finish


@dataclass
class WorkerRunResult:
    claimed: int = 0
    ingested: int = 0
    rejected: int = 0
    failed: int = 0
    local_duplicates: int = 0

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def run_once(client: BridgeClient, worker_id: str = "stc-worker", limit: int = 10) -> WorkerRunResult:
    batch = client.claim(worker_id, limit)
    result = WorkerRunResult(claimed=len(batch.events))
    if not batch.events:
        return result
    if not batch.claim_token:
        raise RuntimeError("Bridge returned events without claim_token")

    for item in batch.events:
        try:
            processed = process_bridge_event(item.event_id, item.payload)
            if processed.get("local_duplicate"):
                result.local_duplicates += 1
            local_status = processed["status"]
            bridge_status = "rejected" if local_status == "rejected" else "ingested"
            note = local_status
            client.ack(item.event_id, batch.claim_token, bridge_status, note)
            if bridge_status == "rejected":
                result.rejected += 1
            else:
                result.ingested += 1
        except Exception as exc:
            result.failed += 1
            bridge_event_finish(item.event_id, "failed", {"action": "worker_failure", "execution": "none"}, type(exc).__name__)
            try:
                client.ack(item.event_id, batch.claim_token, "failed", type(exc).__name__)
            except Exception:
                pass
    return result
