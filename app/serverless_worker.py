from __future__ import annotations

from dataclasses import dataclass

from .bridge_client import BridgeClient
from .event_decision import decide_bridge_event


@dataclass
class ServerlessRunResult:
    claimed: int = 0
    ingested: int = 0
    rejected: int = 0
    failed: int = 0

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def run_serverless_once(
    client: BridgeClient,
    *,
    worker_id: str = "stc-vercel-worker",
    limit: int = 5,
) -> ServerlessRunResult:
    batch = client.claim(worker_id, limit)
    result = ServerlessRunResult(claimed=len(batch.events))
    if not batch.events:
        return result
    if not batch.claim_token:
        raise RuntimeError("Bridge returned events without claim_token")

    for item in batch.events:
        try:
            outcome = decide_bridge_event(item.event_id, item.payload)
            local_status = outcome["status"]
            bridge_status = "rejected" if local_status == "rejected" else "ingested"
            client.ack(
                item.event_id,
                batch.claim_token,
                bridge_status,
                outcome.get("note", local_status) or local_status,
                result=outcome,
            )
            if bridge_status == "rejected":
                result.rejected += 1
            else:
                result.ingested += 1
        except Exception as exc:
            result.failed += 1
            try:
                client.ack(
                    item.event_id,
                    batch.claim_token,
                    "failed",
                    type(exc).__name__,
                    result={
                        "event_id": item.event_id,
                        "status": "failed",
                        "decision": {"action": "worker_failure", "execution": "none"},
                        "note": type(exc).__name__,
                    },
                )
            except Exception:
                pass
    return result
