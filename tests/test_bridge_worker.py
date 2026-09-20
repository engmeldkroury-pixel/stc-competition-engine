from pathlib import Path

from app import storage
from app.bridge_client import ClaimBatch, ClaimedEvent
from app.bridge_worker import run_once


class FakeClient:
    def __init__(self):
        self.acks = []

    def claim(self, worker_id, limit):
        return ClaimBatch(
            claim_token="claim-1",
            events=[
                ClaimedEvent(
                    event_id="evt-worker-1",
                    payload={"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"},
                    status="claimed",
                    process_attempts=1,
                )
            ],
        )

    def ack(self, event_id, claim_token, status, note=""):
        self.acks.append((event_id, claim_token, status, note))
        return {"ok": True, "event_id": event_id, "status": status}


def test_worker_claims_processes_and_acks(tmp_path: Path):
    storage.DB_PATH = tmp_path / "stc-worker.db"
    storage.init_db()
    client = FakeClient()
    result = run_once(client, worker_id="worker-1", limit=10)
    assert result.claimed == 1
    assert result.ingested == 1
    assert result.failed == 0
    assert client.acks[0][2] == "ingested"
    assert storage.bridge_inbox_summary()["by_status"]["ingested_context"] == 1


class FailingClient(FakeClient):
    pass


def test_worker_marks_local_failure_when_processing_raises(tmp_path: Path, monkeypatch):
    storage.DB_PATH = tmp_path / "stc-worker-fail.db"
    storage.init_db()
    client = FailingClient()

    import app.bridge_worker as bw

    def explode(event_id, payload):
        storage.bridge_event_start(event_id, payload)
        raise ValueError("boom")

    monkeypatch.setattr(bw, "process_bridge_event", explode)
    result = bw.run_once(client, worker_id="worker-1", limit=10)
    assert result.failed == 1
    event = storage.bridge_event_get("evt-worker-1")
    assert event is not None
    assert event["status"] == "failed"
    assert client.acks[0][2] == "failed"
