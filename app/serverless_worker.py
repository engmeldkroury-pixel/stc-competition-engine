from __future__ import annotations

from dataclasses import dataclass, field

from .bridge_client import BridgeClient
from .event_decision import decide_bridge_event


@dataclass
class ServerlessRunResult:
    claimed: int = 0
    ingested: int = 0
    rejected: int = 0
    failed: int = 0
    signal_notification_attempted: int = 0
    signal_notification_delivered: int = 0
    signal_notification_skipped: int = 0
    signal_notification_no_delivery: int = 0
    signal_notification_errors: int = 0
    signal_notification_skip_reasons: dict[str, int] = field(default_factory=dict)
    portfolio_notification_attempted: int = 0
    portfolio_notification_errors: int = 0

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    def record_signal_notification_skip(self, reason: str) -> None:
        reason = reason or "unspecified"
        self.signal_notification_skipped += 1
        self.signal_notification_skip_reasons[reason] = (
            self.signal_notification_skip_reasons.get(reason, 0) + 1
        )


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
                notifier = getattr(client, "notify_signal", None)
                if callable(notifier) and outcome.get("decision", {}).get("locked_trade_plan"):
                    result.signal_notification_attempted += 1
                    try:
                        notification = notifier(item.event_id)
                        if bool(notification.get("skipped", False)):
                            result.record_signal_notification_skip(
                                str(notification.get("reason") or "unspecified")
                            )
                        elif bool((notification.get("dispatch") or {}).get("delivered_any", False)):
                            result.signal_notification_delivered += 1
                        else:
                            result.signal_notification_no_delivery += 1
                    except Exception:
                        # Notifications are secondary. Never turn a successfully
                        # persisted market event into a failed trading signal.
                        result.signal_notification_errors += 1
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



def run_serverless_drain(
    client: BridgeClient,
    *,
    worker_id: str = "stc-vercel-worker",
    limit: int = 20,
    max_batches: int = 5,
) -> ServerlessRunResult:
    """Drain multiple bridge batches in one runner invocation.

    A 10+16 symbol production cycle can enqueue 26 events at once. Draining
    several batches makes one successful workflow sufficient, instead of
    depending on a second queued workflow run.
    """
    limit = max(1, min(int(limit), 20))
    max_batches = max(1, min(int(max_batches), 10))
    total = ServerlessRunResult()

    for _ in range(max_batches):
        batch = run_serverless_once(client, worker_id=worker_id, limit=limit)
        total.claimed += batch.claimed
        total.ingested += batch.ingested
        total.rejected += batch.rejected
        total.failed += batch.failed
        total.signal_notification_attempted += batch.signal_notification_attempted
        total.signal_notification_delivered += batch.signal_notification_delivered
        total.signal_notification_skipped += batch.signal_notification_skipped
        total.signal_notification_no_delivery += batch.signal_notification_no_delivery
        total.signal_notification_errors += batch.signal_notification_errors
        for reason, count in batch.signal_notification_skip_reasons.items():
            total.signal_notification_skip_reasons[reason] = (
                total.signal_notification_skip_reasons.get(reason, 0) + count
            )
        if batch.claimed < limit:
            break

    portfolio_notifier = getattr(client, "notify_portfolio", None)
    if callable(portfolio_notifier) and total.claimed > 0:
        total.portfolio_notification_attempted += 1
        try:
            portfolio_notifier()
        except Exception:
            # Fail-soft: position-management alerts must never compromise
            # ingestion of the authoritative market-data cycle.
            total.portfolio_notification_errors += 1

    return total
