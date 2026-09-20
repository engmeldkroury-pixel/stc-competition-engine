import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("stc_vercel_entry", ROOT / "api" / "index.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def test_serverless_health():
    client = TestClient(module.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["version"] == "0.5.0"
    assert r.json()["execution"] == "manual_only"


def test_process_requires_trigger_token(monkeypatch):
    monkeypatch.setenv("STC_TRIGGER_TOKEN", "trigger-secret")
    client = TestClient(module.app)
    assert client.post("/process").status_code == 401
    assert client.post("/process", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_process_requires_bridge_config(monkeypatch):
    monkeypatch.setenv("STC_TRIGGER_TOKEN", "trigger-secret")
    monkeypatch.delenv("STC_BRIDGE_URL", raising=False)
    monkeypatch.delenv("STC_WORKER_TOKEN", raising=False)
    client = TestClient(module.app)
    r = client.post("/process", headers={"Authorization": "Bearer trigger-secret"})
    assert r.status_code == 503
