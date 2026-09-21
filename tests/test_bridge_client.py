import json

import httpx

from app.bridge_client import BridgeClient


def test_claim_and_ack_contract():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("authorization") == "Bearer secret"
        if request.url.path.endswith("/claim.php"):
            body = json.loads(request.content)
            assert body["worker_id"] == "worker-1"
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "claim_token": "abc",
                    "count": 1,
                    "events": [
                        {
                            "event_id": "evt-1",
                            "payload": {"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"},
                            "status": "claimed",
                            "process_attempts": 1,
                        }
                    ],
                },
            )
        if request.url.path.endswith("/ack.php"):
            seen.append(json.loads(request.content))
            return httpx.Response(200, json={"ok": True, "event_id": "evt-1", "status": "ingested"})
        return httpx.Response(404)

    client = BridgeClient("https://bridge.test", "secret", transport=httpx.MockTransport(handler))
    batch = client.claim("worker-1", 10)
    assert batch.claim_token == "abc"
    assert batch.events[0].event_id == "evt-1"
    ack = client.ack("evt-1", "abc", "ingested", "ok", result={"status": "analyzed"})
    assert ack["status"] == "ingested"
    assert seen[0]["claim_token"] == "abc"
    assert seen[0]["result"]["status"] == "analyzed"


def test_inbox_uses_bearer_auth():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("authorization") == "Bearer secret"
        assert request.url.params["status"] == "received"
        return httpx.Response(200, json={"ok": True, "count": 0, "events": []})

    client = BridgeClient("https://bridge.test", "secret", transport=httpx.MockTransport(handler))
    assert client.inbox()["count"] == 0


def test_runtime_control_and_approval_reads_use_bearer_auth():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("authorization") == "Bearer secret"
        seen.append((request.method, request.url.path, dict(request.url.params)))
        if request.url.path.endswith("/runtime_control.php"):
            return httpx.Response(200, json={
                "ok": True,
                "runtime_control": {
                    "safe_mode": True,
                    "kill_switch": True,
                    "reason": "test",
                    "version": 3,
                    "updated_at_utc": "2026-09-21 14:00:00",
                },
            })
        if request.url.path.endswith("/approval.php"):
            assert request.url.params["signal_id"] == "sig-1"
            return httpx.Response(200, json={
                "ok": True,
                "signal_id": "sig-1",
                "approval": None,
                "execution": "manual_only",
            })
        return httpx.Response(404)

    client = BridgeClient("https://bridge.test", "secret", transport=httpx.MockTransport(handler))
    assert client.runtime_control()["runtime_control"]["version"] == 3
    assert client.approval("sig-1")["signal_id"] == "sig-1"
    assert [x[1] for x in seen] == ["/runtime_control.php", "/approval.php"]


def test_notification_bridge_calls_are_authenticated():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("authorization") == "Bearer secret"
        body = json.loads(request.content)
        seen.append(body)
        if body["action"] == "signal":
            assert body["event_id"] == "evt-notify"
        return httpx.Response(200, json={"ok": True, "notifications": []})

    client = BridgeClient("https://bridge.test", "secret", transport=httpx.MockTransport(handler))
    assert client.notify_signal("evt-notify")["ok"] is True
    assert client.notify_portfolio()["ok"] is True
    assert [x["action"] for x in seen] == ["signal", "portfolio"]
