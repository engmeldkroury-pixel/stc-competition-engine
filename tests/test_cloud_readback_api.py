import importlib.util
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("stc_cloud_api", ROOT / "api" / "index.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)

HEADERS = {"Authorization": "Bearer test-trigger-secret"}


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("STC_TRIGGER_TOKEN", "test-trigger-secret")
    monkeypatch.setenv("STC_BRIDGE_URL", "https://bridge.invalid")
    monkeypatch.setenv("STC_WORKER_TOKEN", "test-worker-secret")


def test_cloud_routes_require_auth():
    client = TestClient(module.app)
    assert client.get("/cloud/readiness").status_code == 401
    assert client.get("/cloud/signals").status_code == 401


def test_cloud_readiness_is_blocked_and_no_store():
    r = TestClient(module.app).get("/cloud/readiness", headers=HEADERS)
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-store"
    assert r.json()["cloud_approval_ready"] is False


def test_cloud_signals_reads_only_inbox(monkeypatch):
    requests = []
    def handle(request):
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == "/inbox.php"
        assert request.url.params["status"] == "ingested"
        return httpx.Response(200, json={"ok": True, "events": []})
    real = module.BridgeClient
    monkeypatch.setattr(module, "BridgeClient", lambda url, token, **kwargs:
                        real(url, token, transport=httpx.MockTransport(handle), **kwargs))
    r = TestClient(module.app).get("/cloud/signals", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["cards"] == []
    assert len(requests) == 1


def test_no_cloud_write_route_added():
    routes = {(route.path, method) for route in module.app.routes
              for method in getattr(route, "methods", set()) if route.path.startswith("/cloud/")}
    assert routes == {("/cloud/signals", "GET"), ("/cloud/readiness", "GET")}
