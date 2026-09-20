# STC Competition Engine v0.9

This is the first executable STC build for TradingView The Leap paper-trading competitions.

## Current scope

- Official competition profiles for:
  - The Leap by AMP Futures — Sep 2026
  - The Leap by Capital.com Africa — Sep/Oct 2026
- Official symbol allowlists and max-open-position limits
- Transaction-rate guard below the official `60 or more per minute` prohibition threshold
- Minimum qualifying trading-day tracker
- Realized-P/L competition scoring rule
- Deterministic technical analysis endpoint
- Multi-factor signal evaluation with mandatory human approval
- TradingView webhook receiver
- SQLite audit trail
- Automated tests
- No real-money execution

## Run

```bash
cd STC_APP_v0_1
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`.

## Test

```bash
cd STC_APP_v0_1
pytest -q
```

## Important

This version does not log into TradingView or place orders. It is deliberately an analysis/rule/approval engine so it can be tested safely against competition conditions first.


## v0.2 data-provider hardening
- Adds a provider/symbol capability matrix.
- Blocks silent provider substitution by default.
- Marks CAPITALCOM:XAUUSD native MCP technicals as unsupported and uses STC local calculations from OHLCV where appropriate.
- Warns that OHLCV may be delayed and is not an execution-time quote.
- Adds idempotent TradingView webhook receipt handling to tolerate retries/duplicates.

## v0.4 bridge worker

Adds a pull-based, idempotent bridge worker contract:

- `app/bridge_client.py`: authenticated Claim/Ack client for STC Webhook Bridge v0.2.
- `app/event_processor.py`: validates competition/symbol and creates a deterministic signal only when a full TradingView signal payload is present.
- `app/bridge_worker.py`: one-shot worker with explicit ack outcomes; no order execution.
- `run_bridge_worker_once.py`: reads bridge URL/token from environment variables only.
- `bridge_inbox` local audit table tracks processed event state.

No auto-trading is added. Human approval remains mandatory.


## v0.4 approval safety
- Dynamic approval validity by timeframe.
- Price/score/market-state/rule/news/volatility revalidation before approval is accepted.
- Runtime Safe Mode and Kill Switch.
- Approval still never executes a trade automatically.


## v0.5 zero-new-spend serverless processor
- Adds a pure event-decision layer with no persistence side effects.
- Adds `api/index.py` as a Vercel-compatible FastAPI serverless entrypoint.
- Adds `/process` protected by `STC_TRIGGER_TOKEN`; it claims events from Hostinger Bridge, analyzes them, and writes the full result back during Ack.
- Uses Hostinger/MySQL as the persistent source of truth so Vercel's ephemeral filesystem is not relied on.
- Required runtime environment variables: `STC_TRIGGER_TOKEN`, `STC_BRIDGE_URL`, `STC_WORKER_TOKEN`. Optional: `STC_WORKER_ID`, `STC_WORKER_BATCH_LIMIT`.
- No automatic order execution. Human approval and execution confirmation remain mandatory.

## GitHub Actions zero-new-spend primary runner
The repository includes `.github/workflows/stc-process.yml`.

- Trigger: `repository_dispatch` event type `stc_event` or manual `workflow_dispatch`.
- Repository secret required: `STC_WORKER_TOKEN`.
- Hostinger bridge remains the persistent source of truth.
- The workflow processes up to 20 pending events in one run to reduce Actions minute usage.
- Concurrency is serialized so overlapping dispatches do not create simultaneous workers.
- No artifact upload is required; results are acknowledged back to Hostinger/MySQL.
- No automatic trade execution is implemented.


## v0.9 reconciliation and readiness
- Adds deterministic pipeline receipts for every bridge decision so TradingView events can be reconciled through Hostinger/MySQL results.
- Each receipt carries event id, canonical payload SHA-256, competition/symbol, event time, status/action, and signal id when generated.
- Adds `/readiness` to report static analysis readiness, runtime Safe Mode/Kill Switch state, quote-evidence requirements, and manual-only execution mode.
- Adds `.github/workflows/stc-ci.yml` as the automated pytest gate on pushes and pull requests to `main`.
- Adds `PROJECT_STATE.md` as the persistent project/evidence ledger.
- TradingView MCP remains read/context transport only; execution-time approval fails closed without fresh trusted evidence.
