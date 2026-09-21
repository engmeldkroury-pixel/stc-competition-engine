# STC PROJECT STATE

Last updated: 2026-09-21
Current software version: v0.9.0
Repository: engmeldkroury-pixel/stc-competition-engine
Default branch: main

## Mission

Build a safe competition-assistant engine for TradingView The Leap paper-trading competitions with deterministic processing, automated verification, human approval before any order entry, and no real-money auto-execution.

## Accepted governance

- Automated tests are the primary verification gate.
- Human approval remains mandatory before competition order entry.
- No real-money order execution is implemented.
- Provider identity must be preserved; silent cross-provider substitution is blocked.
- Execution-time approval must fail closed if trusted quote/market evidence is missing, stale, mismatched, future-dated, or untrusted.
- Hostinger/MySQL bridge is the persistent cloud source of truth for serverless event results.
- TradingView MCP is treated as market/context evidence and alert transport support, not an execution account API.

## Implemented

### Competition/risk core
- Official competition profiles for AMP Futures Sep 2026 and Capital.com Africa Sep/Oct 2026.
- Symbol allowlists and maximum open-position rules.
- Transaction-rate protection.
- Minimum qualifying trading-day tracking.
- Realized-P/L scoring basis.
- Configurable risk-fraction guard.

### Analysis/signals
- Local EMA20, EMA50, RSI14, ATR14, MACD, momentum analysis.
- Multi-factor signal scoring with LONG/SHORT/WAIT output.
- Deterministic signal IDs for bridge events.
- Dynamic approval envelopes with validity, price tolerance, market-state hash, rule version, news and volatility revalidation.

### Data/provider safety
- Exact-provider capability matrix for the 10 Capital.com competition symbols.
- Local indicator fallback from exact-provider OHLCV when native technicals are unavailable.
- Explicit delayed-OHLCV warning.
- Silent provider substitution blocked.

### Bridge/cloud processing
- Authenticated claim/ack bridge client.
- Idempotent bridge event processing.
- GitHub Actions worker for Hostinger bridge events.
- Serverless processor that returns full decision payload back to Hostinger/MySQL in Ack.
- Deterministic pipeline receipt (v0.9) containing:
  - receipt_id
  - event_id
  - canonical payload SHA-256
  - competition_id
  - symbol
  - event_time
  - status/action
  - signal_id when applicable

### Approval hardening
- Approval request no longer accepts caller-supplied quote/market verification booleans.
- Persisted execution evidence model.
- Target/provider/competition matching.
- Freshness limits.
- Future-timestamp rejection.
- Streaming requirement for direct TradingView quote evidence.
- Safe Mode and Kill Switch.
- Approval remains manual-only.

### Automated verification
- Pytest suite exists for API, risk, bridge, serverless worker, capability matrix, approval, execution-context and deterministic event behavior.
- .github/workflows/stc-ci.yml added in v0.9:
  - runs on push to main
  - runs on pull requests to main
  - supports manual workflow_dispatch
  - executes pytest -q

## Live TradingView MCP evidence captured 2026-09-21

Read-only checks only. No alert creation and no order execution were performed.

- CAPITALCOM:XAUUSD 15m OHLCV: SUCCESS; 120 bars returned.
- OHLCV notice explicitly states delayed data and says latest bar is not a live quote.
- CAPITALCOM:XAUUSD news: SUCCESS.
- USD economic calendar: SUCCESS.
- Alert list: SUCCESS.
- Alert log: SUCCESS; prior webhook deliveries include HTTP 200 responses after earlier test failures.
- Batch quote read for all 10 Capital.com symbols at the time of check: no quote rows returned.
- Direct EURUSD quote/technicals at the time of check: TradingView scanner returned HTTP 429.
- XAUUSD native technicals at the time of check: TradingView scanner returned HTTP 429.

Interpretation: historical/context market data and alert plumbing are available; execution-time quote readiness must still be treated dynamically and fail closed whenever the direct quote path is unavailable.

## Current acceptance status

### Ready
- Competition-rule engine.
- Signal generation.
- Exact-provider analysis fallback.
- TradingView -> Hostinger bridge transport.
- Deterministic cloud processing result.
- Human approval envelope generation.
- Pipeline reconciliation receipt.
- Automated CI test gate definition.
- Safe/fail-closed approval logic.

### Not yet evidence-complete
- CI is confirmed green for the v0.9 release contract. GitHub Actions run 35538557690 on main completed successfully after the release-smoke fixes.
- End-to-end reconciliation of one new v0.9 TradingView-origin event through Hostinger/MySQL with the new receipt still requires one real incoming TradingView event.
- Execution-time direct quote availability is dynamic and was unavailable/rate-limited during the latest read-only MCP check.
- No broker/execution account read/write API is available in the verified TradingView MCP path. Manual execution remains required.

## Owner boundary

The system may analyze, rank signals, validate competition rules, generate approval envelopes, and reconcile evidence automatically.

The system must NOT place a competition or real-money order automatically. The owner remains the final approval and execution authority.

## E2E verification findings on 2026-09-21

- A one-time GitHub Actions E2E client was created only for testing and then removed.
- Direct POST attempts from GitHub Actions reached Hostinger but were rejected with HTTP 403 `source_not_allowed`.
- This is expected because the bridge intentionally enforces a TradingView source/IP allowlist.
- Therefore a non-TradingView client cannot be used to fake final transport acceptance.
- TradingView MCP can restart an existing webhook alert, but modifying/creating webhook alerts currently returns `webhook_requires_2fa`.
- Existing old test alerts carry already-used event IDs and are not suitable to prove a new v0.9 receipt because bridge idempotency intentionally rejects/absorbs duplicates.

## End-to-end acceptance evidence — 2026-09-20 21:39 UTC

The v0.9 transport + processing + reconciliation path is now independently verified end to end with a safe STC-TEST event.

- TradingView alert id: 5655506323
- Event id: stc-v09-e2e-manual-20260921-001
- Symbol: BITSTAMP:BTCUSD
- TradingView fired at: 2026-09-20T21:39:00Z
- TradingView webhook delivery: HTTP 200
- GitHub repository_dispatch worker run: 35539353831
- Worker conclusion: success
- Worker processing result: claimed=1, ingested=1, rejected=0, failed=0
- Hostinger readback status: ingested
- Hostinger process_attempts: 1
- STC result status: ingested_context
- STC action: archive_test_event
- Receipt id: stc-receipt-eb06cf422ad3a79bdbfd38c80ae0b398
- Payload SHA-256: af2b843b6a3b0c41e04cf815033b98a4d425d2a6d71121934a30c62540b56db4
- Receipt execution mode: manual_only
- Signal id: null, as expected for STC-TEST
- No trade analysis or order execution occurred.

Acceptance conclusion:
- TradingView -> Hostinger webhook transport: VERIFIED
- TradingView source/IP allowlist: VERIFIED
- Hostinger -> GitHub repository_dispatch: VERIFIED
- GitHub bridge worker: VERIFIED
- Hostinger/MySQL Ack/result persistence: VERIFIED
- v0.9 deterministic receipt persistence: VERIFIED
- Safe STC-TEST no-execution behavior: VERIFIED
- Automated CI on main: VERIFIED GREEN

The temporary readback workflow used to obtain the final evidence was removed after verification. The assistant-created diagnostic TradingView alert was also deleted after use.

## Current next action

Proceed to pre-market operational validation for the Capital.com competition path: verify current competition profile/rules, exact Capital.com symbols, runtime market-data availability, Safe Mode/Kill Switch state, and approval evidence requirements. Human approval remains mandatory before any competition order entry; automatic execution remains unavailable/disabled.


## Pre-market validation — 2026-09-21 02:04 UTC

Read-only Capital.com/TradingView runtime checks:
- Exact-provider 15m OHLCV returned successfully for all 10 Capital.com competition symbols.
- Direct batch quote rows were available for CAPITALCOM:EURUSD, CAPITALCOM:AUDUSD, and CAPITALCOM:USDZAR.
- Direct batch quote rows were unavailable for the other 7 symbols at the check time; this remains a dynamic runtime condition and approval must fail closed without fresh trusted quote evidence.
- No cross-provider substitution was used.

Feed hardening:
- tradingview/STC_FEED.pine upgraded to v0.2.
- The feed now emits a deterministic event_id derived from competition + exact provider/symbol + timeframe + bar time.
- This removes dependence on transport-generated payload hashes for normal feed idempotency and gives the cloud pipeline a stable bar identity.
- tests/test_pine_feed_contract.py locks the webhook payload contract.
- GitHub Actions CI run 35552943819 passed after the change.

Operational architecture finding:
- Cloud bridge processing is persistent in Hostinger/MySQL and verified.
- The interactive approval/runtime-control implementation in app/main.py currently uses local SQLite state.
- The production GitHub worker is serverless/stateless and returns signal/envelope results to Hostinger; it does not persist approval envelopes into a durable shared approval store.
- Therefore cloud signal generation is verified, but a unified cloud approval UI/state path is not yet operationally complete.
- Until that gap is closed, human approval/manual execution remains a hard boundary and the system must not claim cloud approval readiness.

## Current next action

Build the smallest durable cloud approval-state contract on top of the existing Hostinger bridge result source of truth, without adding automatic execution. The contract must expose analyzed signal + approval envelope, preserve Safe Mode/Kill Switch semantics, accept only trusted fresh evidence, and keep final order entry manual.
