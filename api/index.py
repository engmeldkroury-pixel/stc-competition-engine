from __future__ import annotations

import os
import secrets

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from app.bridge_client import BridgeClient, BridgeClientError
from app.cloud_approval import CloudSnapshotError, cloud_readiness, read_cloud_snapshot
from app.competition_profiles import PROFILES
from app.serverless_worker import run_serverless_once

app = FastAPI(title="STC Serverless Processor", version="0.9.0")


def _require_trigger(auth: str | None) -> None:
    expected = os.getenv("STC_TRIGGER_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="STC_TRIGGER_TOKEN is not configured")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    provided = auth.split(" ", 1)[1].strip()
    if not provided or not secrets.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.9.0",
        "runtime": "serverless",
        "execution": "manual_only",
    }


@app.post("/process")
def process_pending(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    bridge_url = os.getenv("STC_BRIDGE_URL", "").strip()
    worker_token = os.getenv("STC_WORKER_TOKEN", "").strip()
    if not bridge_url or not worker_token:
        raise HTTPException(status_code=503, detail="Bridge environment is not configured")
    worker_id = os.getenv("STC_WORKER_ID", "stc-vercel-worker")
    try:
        limit = int(os.getenv("STC_WORKER_BATCH_LIMIT", "5"))
    except ValueError:
        limit = 5
    limit = max(1, min(limit, 20))
    client = BridgeClient(bridge_url, worker_token, timeout_seconds=8.0)
    result = run_serverless_once(client, worker_id=worker_id, limit=limit)
    return {"ok": True, **result.to_dict(), "execution": "manual_only"}


@app.get("/cloud/readiness")
def cloud_status(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    return JSONResponse(cloud_readiness(), headers={"Cache-Control": "no-store"})


@app.get("/cloud/signals")
def cloud_signals(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    bridge_url = os.getenv("STC_BRIDGE_URL", "").strip()
    worker_token = os.getenv("STC_WORKER_TOKEN", "").strip()
    if not bridge_url or not worker_token:
        raise HTTPException(status_code=503, detail="Bridge environment is not configured")
    allowed = {key: profile.allowed_symbols for key, profile in PROFILES.items()}
    try:
        snapshot = read_cloud_snapshot(
            BridgeClient(bridge_url, worker_token, timeout_seconds=8.0),
            allowed,
        )
    except (BridgeClientError, CloudSnapshotError, httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Cloud bridge readback unavailable",
            headers={"Cache-Control": "no-store"},
        ) from None
    return JSONResponse(snapshot, headers={"Cache-Control": "no-store"})
