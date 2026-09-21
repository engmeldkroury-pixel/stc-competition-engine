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


## Cloud approval readback batch — 2026-09-21 07:52 UTC

Merged PR #5: STC cloud approval readback — fail-closed.
Main commit: a29a3ef93555e41e9c063b3ea4783071ef40544e.
Main CI run 35574957270: SUCCESS.

Implemented:
- Authenticated GET /cloud/readiness.
- Authenticated GET /cloud/signals.
- Read-only projection from Hostinger bridge inbox.
- Receipt/payload consistency validation.
- Exact competition/provider/symbol checks.
- Deterministic signal identity check.
- Finite numeric and timestamp/expiry validation.
- Conflicting/tampered records are quarantined.
- No cloud approval write endpoint exists.
- Effective cloud policy remains fail-closed with Safe Mode and Kill Switch represented as active defaults until durable persisted controls are connected.
- Automatic execution remains unavailable; every signal remains manual-only and unapproved.

Remaining production blocker:
The active Hostinger PHP bridge source is not present in the GitHub repository or File Library. Durable cloud approval/runtime-control writes cannot be implemented safely without inspecting the live-compatible PHP contract and current database queries.

Required source files only (credentials redacted):
- public_html/_bootstrap.php
- public_html/inbox.php
- public_html/claim.php
- public_html/ack.php

Do NOT provide config.php, passwords, tokens, database dumps, or secret values.

## Current next action

Inspect the four current Hostinger PHP bridge files and design the smallest compatible durable approval/runtime-control extension. No production schema or PHP deployment should be guessed before those files are reviewed.


## Durable Hostinger approval patch — 2026-09-21 08:12 UTC

Owner supplied the live-compatible Hostinger public_html PHP bridge package. Reviewed:
- _bootstrap.php
- inbox.php
- claim.php
- ack.php
- plus health.php/status.php/webhook.php for compatibility context.

Implemented and merged PR #6.
Main commit: ae6d56d8b2f4812d4cdf144e039ee1d57f8cc00e.
Main CI run 35576621843: SUCCESS.

Additive production patch now exists in hostinger_patch/:
- cloud_control.php
- runtime_control.php
- approval.php
- migrations/001_cloud_approval.sql
- README_DEPLOY.md

Safety properties:
- Existing webhook.php, claim.php, ack.php, inbox.php and _bootstrap.php are not replaced by this batch.
- Runtime controls persist in MySQL and start fail-closed: safe_mode=1, kill_switch=1.
- Owner approval uses a separate owner_api_token and never reuses worker/GitHub credentials.
- Approval requires exact persisted signal/receipt identity, current signal freshness, no newer signal for the same target, fresh owner platform confirmation, market=open and price inside the approval envelope.
- Approval records remain audit-only and always return execution=manual_only.
- No broker/order endpoint is introduced.

Current blocker:
Production deployment requires owner access to Hostinger hPanel/phpMyAdmin/private config.php. The assistant does not have an authenticated Hostinger file/database management connector in this environment.

Required owner deployment actions:
1. Upload the three new PHP files from hostinger_patch/ to public_html.
2. Run migrations/001_cloud_approval.sql once in the existing STC MySQL database.
3. Add a new separate owner_api_token entry to the private config.php outside public_html. Do not share its value.
4. Leave safe_mode and kill_switch ON after migration.
5. Return after those steps for live read-only/blocked-approval verification before controls are disabled.


## Capital.com live signal + cloud approval boundary proof — 2026-09-21 08:30 UTC

TradingView manual Capital.com test alert:
- Alert id: 5659023932
- Symbol: CAPITALCOM:XAUUSD
- Event id: stc-capital-e2e-manual-20260921-001
- Fired: 2026-09-21T08:26:49Z
- Webhook result: HTTP 200
- Alert auto-deactivated after fire.

Bridge processing:
- GitHub repository_dispatch run: 35577945674
- Worker conclusion: SUCCESS
- Processing result: claimed=1, ingested=1, rejected=0, failed=0

Persisted signal:
- signal_id: bridge-6892e51a1282c352aaafd4a4d1e35aac
- recommendation: WAIT
- composite_score: -0.0675
- receipt_id: stc-receipt-938021575b1b1405d07a00c1e0962873
- receipt execution: manual_only
- approval envelope valid_until: 2026-09-21T08:57:06.647864+00:00

Production readback:
- approval.php GET is reachable and authenticated with worker read credential.
- No prior owner approval existed at readback.
- Runtime control remained safe_mode=true, kill_switch=true, version=1.
- Worker credential POST to approval.php returned HTTP 401.
- Worker credential POST attempting to disable runtime controls returned HTTP 401.
- Runtime controls remained unchanged after the denied write attempts.

Owner-auth production gate:
- Workflow .github/workflows/stc-owner-approval-gate.yml is prepared.
- First run 35578258416 intentionally failed at the prerequisite step because STC_OWNER_TOKEN is not configured as a GitHub Actions secret.
- No owner approval write occurred in that failed run.
- Next proof will POST an approve request for the persisted WAIT signal and must be blocked by safe_mode + kill_switch + WAIT safeguards, then read back the durable blocked approval. No trade execution is possible in this workflow.

Temporary Hostinger production/readback proof workflows were removed after their evidence was captured.

## Current owner action required

Add the same private owner_api_token value already configured in Hostinger config.php as a GitHub Actions repository secret named STC_OWNER_TOKEN. Do not paste or expose the value in chat. After the secret exists, re-run only the failed owner approval gate job; the assistant can perform the rerun through the GitHub connector.


## Owner-auth durable approval gate — 2026-09-21 08:36 UTC

GitHub Actions repository secret STC_OWNER_TOKEN was configured by the owner without exposing its value.

Owner approval production gate:
- Workflow run: 35578258416
- Attempt: 2
- Conclusion: SUCCESS
- Owner credential was accepted by Hostinger approval.php.
- POST approve request for signal bridge-6892e51a1282c352aaafd4a4d1e35aac returned a durable blocked decision as designed.
- Blocking reasons included safe_mode_active, kill_switch_active, and wait_is_not_an_order.
- Durable approval readback returned approval.decision=blocked.
- Runtime control remained safe_mode=true, kill_switch=true, version=1.
- Execution remained manual_only.
- No trade or broker action occurred.

The temporary owner approval gate workflow was removed after evidence capture. STC_OWNER_TOKEN remains stored as a GitHub Actions secret for future authenticated owner-control workflows; its value is not recorded in project files or chat.

Current operational gap:
The backend control/approval path is now production-verified, but continuous TradingView feed operation for the Capital.com competition still requires the production Pine feed/alerts to be installed for the allowed competition symbols. The TradingView MCP webhook-alert creation path previously returned webhook_requires_2fa despite browser 2FA being enabled, so production alert provisioning may require manual TradingView UI steps unless that MCP defect is resolved.


## First production Pine feed event — 2026-09-21 09:00 UTC

TradingView production alert:
- alert_id: 5659303693
- name: STC XAUUSD 15m PROD
- symbol: CAPITALCOM:XAUUSD
- resolution: 15m
- alert type: pine_alert
- active: true
- webhook configured: true
- auto_deactivate: false
- first fire: 2026-09-21T09:00:00Z
- bar_time: 2026-09-21T08:45:00Z
- webhook HTTP result: 200

Production Pine payload:
- event_id: capital-africa-sep-2026|CAPITALCOM:XAUUSD|15|1789980300000
- competition_id: capital-africa-sep-2026
- symbol: CAPITALCOM:XAUUSD
- timeframe: 15
- source values were generated by STC Competition Feed v0.2 at confirmed bar close.

Cloud processing:
- repository_dispatch run: 35580844492
- worker result: claimed=1, ingested=1, rejected=0, failed=0
- worker conclusion: SUCCESS

Durable readback:
- production readback run: 35581471915
- conclusion: SUCCESS
- signal_id: bridge-5a8dff64b1031392936e601d26092119
- recommendation: WAIT
- composite_score: -0.0675
- receipt_id: stc-receipt-aad26224d41f6d0f7b943de377b2b49e
- approval envelope valid_until: 2026-09-21T09:30:22.087848+00:00
- execution: manual_only
- prior approval: none
- safe_mode: true
- kill_switch: true
- runtime control version: 1

Acceptance:
- Continuous TradingView Pine alert transport for CAPITALCOM:XAUUSD 15m: VERIFIED.
- Hostinger persistence + GitHub worker processing: VERIFIED.
- Durable signal/receipt readback: VERIFIED.
- Manual-only approval boundary: VERIFIED.
- No trade execution occurred.

The one-time production readback workflow was removed after evidence capture.

Current next action:
Provision the same STC Competition Feed v0.2 + Any alert() function call + webhook configuration for the remaining Capital.com competition symbols required by the profile. Keep Safe Mode and Kill Switch ON until multi-symbol feed coverage and pre-market readiness checks are completed.
