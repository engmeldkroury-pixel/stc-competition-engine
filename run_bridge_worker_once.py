from __future__ import annotations

import os
import time

import httpx

from app.bridge_client import BridgeClient, BridgeClientError
from app.serverless_worker import run_serverless_drain


def main() -> None:
    base_url = os.environ.get("STC_BRIDGE_URL", "https://stc.feama.site").strip()
    token = os.environ.get("STC_WORKER_TOKEN", "").strip()
    worker_id = os.environ.get("STC_WORKER_ID", "stc-github-worker").strip()
    try:
        limit = int(os.environ.get("STC_WORKER_BATCH_LIMIT", "20"))
    except ValueError:
        limit = 20
    limit = max(1, min(limit, 20))
    try:
        max_batches = int(os.environ.get("STC_WORKER_MAX_BATCHES", "3"))
    except ValueError:
        max_batches = 3
    max_batches = max(1, min(max_batches, 5))
    if not base_url or not token:
        raise SystemExit("STC_BRIDGE_URL and STC_WORKER_TOKEN are required")
    client = BridgeClient(base_url, token, timeout_seconds=8.0)
    last_error: Exception | None = None
    retry_delays = (0, 5, 15, 30)
    for attempt, delay_seconds in enumerate(retry_delays):
        if delay_seconds:
            time.sleep(delay_seconds)
        try:
            result = run_serverless_drain(
                client,
                worker_id=worker_id,
                limit=limit,
                max_batches=max_batches,
            )
            print(result.to_dict())
            return
        except (httpx.HTTPError, BridgeClientError) as exc:
            last_error = exc
            if attempt == len(retry_delays) - 1:
                break
    if last_error is not None:
        raise last_error


if __name__ == "__main__":
    main()
