from app.bridge_client import ClaimBatch, ClaimedEvent
from app.serverless_worker import run_serverless_once


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
