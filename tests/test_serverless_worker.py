from app.bridge_client import ClaimBatch, ClaimedEvent
from app.serverless_worker import run_serverless_drain, run_serverless_once


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.acks = []

    def claim(self, worker_id, limit):
        return ClaimBatch(
            claim_token="claim-serverless",
            events=[
                ClaimedEvent(
                    event_id="evt-serverless-1",
                    payload=self.payload,
                    status="claimed",
                    process_attempts=1,
                )
            ],
        )

    def ack(self, event_id, claim_token, status, note="", result=None):
        self.acks.append({
            "event_id": event_id,
            "claim_token": claim_token,
            "status": status,
            "note": note,
            "result": result,
        })
        return {"ok": True, "event_id": event_id, "status": status}


def test_serverless_worker_archives_test_event_and_returns_result_to_bridge():
    client = FakeClient({"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"})
    result = run_serverless_once(client, worker_id="vercel-1", limit=5)
    assert result.claimed == 1
    assert result.ingested == 1
    assert client.acks[0]["status"] == "ingested"
    assert client.acks[0]["result"]["status"] == "ingested_context"


def test_serverless_worker_rejects_unknown_competition():
    client = FakeClient({"competition_id": "nope", "symbol": "X", "time": "2026-09-20T07:00:00Z"})
    result = run_serverless_once(client)
    assert result.rejected == 1
    assert client.acks[0]["status"] == "rejected"
    assert client.acks[0]["result"]["decision"]["reason"] == "unknown_competition"


class DrainFakeClient:
    def __init__(self, batches):
        self.batches = list(batches)
        self.acks = []

    def claim(self, worker_id, limit):
        items = self.batches.pop(0) if self.batches else []
        return ClaimBatch(
            claim_token="claim-drain" if items else None,
            events=[
                ClaimedEvent(
                    event_id=f"evt-{i}",
                    payload={"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"},
                    status="claimed",
                    process_attempts=1,
                )
                for i in items
            ],
        )

    def ack(self, event_id, claim_token, status, note="", result=None):
        self.acks.append((event_id, status))
        return {"ok": True}


def test_drain_processes_multiple_full_batches_in_one_invocation():
    client = DrainFakeClient([list(range(20)), list(range(20, 26)), []])
    result = run_serverless_drain(client, worker_id="drain", limit=20, max_batches=5)
    assert result.claimed == 26
    assert result.ingested == 26
    assert result.failed == 0
    assert len(client.acks) == 26
