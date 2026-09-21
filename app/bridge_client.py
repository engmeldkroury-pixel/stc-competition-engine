from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class BridgeClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class ClaimedEvent:
    event_id: str
    payload: dict[str, Any]
    status: str
    process_attempts: int


@dataclass(frozen=True)
class ClaimBatch:
    claim_token: str | None
    events: list[ClaimedEvent]


class BridgeClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout_seconds: float = 5.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=self.timeout_seconds, transport=self.transport)

    def claim(self, worker_id: str, limit: int = 10) -> ClaimBatch:
        with self._client() as client:
            response = client.post(
                f"{self.base_url}/claim.php",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"worker_id": worker_id, "limit": limit},
            )
        if response.status_code != 200:
            raise BridgeClientError(f"claim_failed:{response.status_code}:{response.text[:200]}")
        body = response.json()
        if body.get("ok") is not True:
            raise BridgeClientError(f"claim_rejected:{body}")
        events = [
            ClaimedEvent(
                event_id=item["event_id"],
                payload=item.get("payload") or {},
                status=item.get("status", "claimed"),
                process_attempts=int(item.get("process_attempts", 0)),
            )
            for item in body.get("events", [])
        ]
        return ClaimBatch(claim_token=body.get("claim_token"), events=events)

    def ack(
        self,
        event_id: str,
        claim_token: str,
        status: str,
        note: str = "",
        result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "event_id": event_id,
            "claim_token": claim_token,
            "status": status,
            "note": note,
        }
        if result is not None:
            payload["result"] = result
        with self._client() as client:
            response = client.post(
                f"{self.base_url}/ack.php",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
            )
        if response.status_code != 200:
            raise BridgeClientError(f"ack_failed:{response.status_code}:{response.text[:200]}")
        body = response.json()
        if body.get("ok") is not True:
            raise BridgeClientError(f"ack_rejected:{body}")
        return body

    def inbox(self, status: str = "received", limit: int = 20) -> dict[str, Any]:
        with self._client() as client:
            response = client.get(
                f"{self.base_url}/inbox.php",
                headers=self.headers,
                params={"status": status, "limit": limit},
            )
        if response.status_code != 200:
            raise BridgeClientError(f"inbox_failed:{response.status_code}:{response.text[:200]}")
        return response.json()


    def runtime_control(self) -> dict[str, Any]:
        with self._client() as client:
            response = client.get(
                f"{self.base_url}/runtime_control.php",
                headers=self.headers,
            )
        if response.status_code != 200:
            raise BridgeClientError(
                f"runtime_control_failed:{response.status_code}:{response.text[:200]}"
            )
        body = response.json()
        if body.get("ok") is not True:
            raise BridgeClientError(f"runtime_control_rejected:{body}")
        return body

    def approval(self, signal_id: str) -> dict[str, Any]:
        with self._client() as client:
            response = client.get(
                f"{self.base_url}/approval.php",
                headers=self.headers,
                params={"signal_id": signal_id},
            )
        if response.status_code != 200:
            raise BridgeClientError(
                f"approval_read_failed:{response.status_code}:{response.text[:200]}"
            )
        body = response.json()
        if body.get("ok") is not True:
            raise BridgeClientError(f"approval_read_rejected:{body}")
        return body


    def notify_signal(self, event_id: str) -> dict[str, Any]:
        with self._client() as client:
            response = client.post(
                f"{self.base_url}/notification.php",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"action": "signal", "event_id": event_id},
            )
        if response.status_code != 200:
            raise BridgeClientError(
                f"notify_signal_failed:{response.status_code}:{response.text[:200]}"
            )
        body = response.json()
        if body.get("ok") is not True:
            raise BridgeClientError(f"notify_signal_rejected:{body}")
        return body

    def notify_portfolio(self) -> dict[str, Any]:
        with self._client() as client:
            response = client.post(
                f"{self.base_url}/notification.php",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"action": "portfolio"},
            )
        if response.status_code != 200:
            raise BridgeClientError(
                f"notify_portfolio_failed:{response.status_code}:{response.text[:200]}"
            )
        body = response.json()
        if body.get("ok") is not True:
            raise BridgeClientError(f"notify_portfolio_rejected:{body}")
        return body
