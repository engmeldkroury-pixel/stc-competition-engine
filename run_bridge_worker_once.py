from __future__ import annotations

import os

from app.bridge_client import BridgeClient
from app.serverless_worker import run_serverless_once


def main() -> None:
    base_url = os.environ.get("STC_BRIDGE_URL", "https://stc.feama.site").strip()
    token = os.environ.get("STC_WORKER_TOKEN", "").strip()
    worker_id = os.environ.get("STC_WORKER_ID", "stc-github-worker").strip()
    try:
        limit = int(os.environ.get("STC_WORKER_BATCH_LIMIT", "20"))
    except ValueError:
        limit = 20
    limit = max(1, min(limit, 20))
    if not base_url or not token:
        raise SystemExit("STC_BRIDGE_URL and STC_WORKER_TOKEN are required")
    result = run_serverless_once(
        BridgeClient(base_url, token, timeout_seconds=8.0),
        worker_id=worker_id,
        limit=limit,
    )
    print(result.to_dict())


if __name__ == "__main__":
    main()
