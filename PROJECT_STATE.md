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


## Capital multi-symbol feed candidate — 2026-09-21 09:16 UTC

Merged PR #7.
Main commit: c401cd2f2717108a71938e9a63a959f14135562e.
Main CI run 35582300372: SUCCESS.

Added tradingview/STC_MULTI_FEED.pine as a separate v0.3 candidate. Existing verified STC_FEED v0.2 remains unchanged and the live XAUUSD alert stays active.

Design:
- One Pine indicator can monitor all 10 exact Capital.com competition symbols using request.security() from a single 15m scheduler chart.
- Recommended scheduler chart: CAPITALCOM:BTCUSD on 15m so the script continues to evaluate on a 24/7 market while non-crypto markets may be closed.
- Each remote symbol carries the same payload contract as v0.2.
- Stable event identity: competition|symbol|feed_timeframe|remote_bar_time.
- Per-symbol lastSentTimes suppress duplicate submissions when a market is closed or not producing a new bar.
- alert.freq_all is used so multiple newly closed symbol bars can be emitted from one chart-bar calculation.
- 10 unique remote contexts are below TradingView's request.* limit.
- No execution or approval behavior was changed.

Evidence:
- Official TradingView Pine documentation states a single script alert on “Any alert() function call” includes all executed alert() calls; alert.freq_all allows all calls in the realtime bar to trigger.
- Official TradingView documentation permits multi-symbol monitoring through request.security() and documents the request.* context limits.
- Static repository contract tests cover all 10 exact Capital.com symbols, remote requests, event identity, duplicate suppression and alert frequency.
- TradingView compile/runtime acceptance of v0.3 is still pending and must not be marked verified until the owner loads it into Pine Editor and the first multi-symbol alert fires successfully through the production bridge.

Current next action:
Owner loads STC_MULTI_FEED.pine into TradingView Pine Editor on CAPITALCOM:BTCUSD 15m, saves/adds it to chart, and reports any compile/runtime error or confirms successful add-to-chart. Do not remove the verified XAUUSD v0.2 production alert during this validation.


## Multi-symbol production alert provisioned — 2026-09-21 09:32 UTC

TradingView alert:
- alert_id: 5659596015
- name: STC CAPITAL 10-SYMBOL 15m PROD
- scheduler symbol: CAPITALCOM:BTCUSD
- resolution: 15m
- alert type: pine_alert
- Pine: STC Capital Multi Feed v0.3
- monitored feed timeframe: 15
- active: true
- webhook configured: true
- auto_deactivate: false
- create_time: 2026-09-21T09:30:38Z
- expiration: 2026-10-21T09:30:01Z
- last_error: null
- first fire: pending at time of provisioning check

Existing verified XAUUSD v0.2 production alert remains active during v0.3 validation.

Acceptance pending:
Do not mark multi-symbol feed verified until the first v0.3 alert fire is observed with HTTP 200 webhook delivery, emitted-symbol coverage is inspected, and corresponding worker/persistence evidence is captured.


## Multi-symbol production fire-control finding + fix — 2026-09-21 09:54 UTC

Live v0.3 multi-feed evidence:
- TradingView alert id 5659596015 fired at 2026-09-21T09:45:00Z for the 09:30 remote bars.
- All 10 Capital.com competition symbols were observed in the alert log.
- Hostinger accepted/persisted all 10 unique events despite some TradingView-side webhook timeout reports.
- GitHub worker run 35585016862 claimed=10, ingested=10, rejected=0, failed=0.
- A later worker run 35585019963 found claimed=0, confirming the persisted batch had already been drained.
- TradingView automatically stopped alert 5659596015 with last_stop_reason=fire_control.
- Root cause evidence: several symbols were emitted more than once within the same scheduler bar. Pine realtime rollback reset normal var array state between intrabar executions, so duplicate suppression did not persist intrabar.
- The existing single-symbol XAUUSD v0.2 production alert remained active and healthy.

Fix:
- PR #8 merged.
- Main commit: 5052cfd7e3ec8a65e642f6d3ea7edc62b32f57c1.
- Main CI run 35585857595: SUCCESS.
- STC Capital Multi Feed upgraded to v0.4.
- lastSentTimes changed from var to varip so per-symbol send state persists across realtime rollback inside the scheduler bar.
- Contract test now requires intrabar-persistent duplicate suppression.
- No execution, approval, Safe Mode, Kill Switch, Hostinger schema, or broker behavior changed.

Current validation gate:
TradingView alerts snapshot the Pine script at alert creation. The stopped v0.3 alert cannot inherit the v0.4 fix automatically. Owner must update the Pine script to v0.4 and create a fresh multi-symbol alert. Keep the verified XAUUSD v0.2 alert active until v0.4 live proof passes.


## Immutable trade-plan state — 2026-09-21 11:22 UTC

Merged PR #10.
Main commit: 69863c3ef22b6259c15c823813818ca53bbd1569.
PR CI run 35593561765: SUCCESS.
Main CI run 35593621193: in progress at state update time.

Implemented:
- app/trade_plan.py builds deterministic locked plans for actionable LONG/SHORT signals.
- WAIT signals do not create a trade plan.
- Each locked plan freezes:
  - plan_id
  - direction
  - competition/symbol
  - decision timeframe
  - source event/signal/time
  - validity
  - entry_min / entry_max / entry_mid
  - initial_stop
  - target1 / target2
  - risk_per_unit and R multiples
  - source composite score
  - rule version
- Levels are marked levels_locked=true and management_policy=fixed_initial_plan_no_silent_repricing.
- A later bar creates a new plan_id instead of mutating/repricing the old plan.
- Cloud signal readback validates and exposes locked_trade_plan when present.
- No automatic order execution or auto-approval was introduced; execution remains manual_only and human approval remains mandatory.

TradingView alert snapshot at this stage:
- STC XAUUSD 15m PROD (5659303693): ACTIVE; last observed fire 2026-09-21T11:15:00Z.
- STC CAPITAL 10-SYMBOL 15m PROD v0.3 (5659596015): INACTIVE due prior fire_control stop.
- An older simple CAPITALCOM:XAUUSD cross alert (5651139895) remains active but has no observed fire in the current project proof.
- Attempt to mute mobile/popup/email on alert 5659303693 through TradingView MCP failed with webhook_requires_2fa; no alert settings were changed.

Operational rule:
Keep the verified XAUUSD v0.2 webhook alert active until a replacement multi-symbol alert with the fire-control fix is live-verified. User-facing notification noise may be muted manually in TradingView while leaving Webhook URL enabled; do not disable the webhook until replacement feed acceptance passes.

Next engineering gap:
The backend now has authoritative immutable trade plans, but Pine cannot fetch arbitrary backend HTTP state. Therefore automatic rendering of the authoritative backend locked plan on a TradingView chart requires either:
1) a TradingView-native stateful visual plan that is explicitly labeled technical-only and non-authoritative, or
2) manual input/synchronization of backend locked levels into Pine, or
3) a separate STC dashboard/UI that renders authoritative backend plans.
Do not misrepresent moving Pine technical zones as authoritative locked trade plans.


## Stateful Pine visual layer — 2026-09-21 11:24 UTC

Merged PR #11.
Main commit: c2166a6936fc8720903147ea5ff0e1c57f07f876.
PR CI run 35593772017: SUCCESS.

Implemented in tradingview/STC_MULTI_FEED.pine:
- Version renamed to STC Capital Multi Feed v0.6 Stateful Visual.
- Technical setup levels are created only on confirmed chart bars.
- Once created, visual entry zone, stop, TP1 and TP2 remain frozen.
- Locked visual setup expires only after configured setupLifetimeBars or invalidates when stop level is breached.
- While locked, later bars do not silently reprice the displayed setup.
- Visual status distinguishes LOCKED LONG SETUP / LOCKED SHORT SETUP / SCANNING-WAIT.
- Production multi-symbol 15m feed remains independent of chart timeframe.
- varip fire-control duplicate protection is preserved.
- No Pine strategy/order execution exists.

Architecture:
- Pine locked setup is technical-only chart state.
- Backend locked_trade_plan remains the authoritative multi-factor plan and is immutable per signal.
- Timeframe changes reload Pine chart context and may generate a new technical setup; they do not mutate an already persisted backend plan.
- No automatic order execution or auto-approval has been introduced.

Next owner validation:
Load STC Capital Multi Feed v0.6 Stateful Visual into TradingView Pine Editor, Save and Add to chart. Do not create a new production alert until compile/runtime and the fixed-zone behavior are visually confirmed.


## Historical context architecture — 2026-09-21 13:03 UTC

User raised a critical analysis-validity question: new webhook bars alone are not enough to establish long-term market context.

Verified TradingView historical access:
- Official TradingView MCP get_ohlcv supports up to 5000 bars per request.
- Exact-provider CAPITALCOM historical OHLCV was re-verified on all 10 competition symbols.
- 400 daily bars were returned for every allowed Capital.com symbol, providing at least a one-year regime window.
- Historical OHLCV is explicitly delayed/context data and is not accepted as an execution-time quote.

Merged PR #12.
Main commit: 314ef7a90a3753780374e69204ea84a993a6e552.
PR CI: SUCCESS.
Main CI run 35603066077: SUCCESS.

STC v0.7 changes:
- TradingView multi-feed now attaches confirmed previous-day historical context to every 15m event.
- Historical context uses 252 trading-day lookback and includes:
  - daily close
  - EMA50 / EMA200
  - RSI14 / ATR14
  - 252-day high / low
  - 20 / 63 / 126 / 252-day momentum
  - normalized 20-day volatility
- Daily history uses the previous confirmed daily bar to avoid using an unfinished daily candle.
- Backend accepts historical context only as complete-or-absent; partial/malformed history fails validation.
- Short-term technical score and historical regime score are stored separately in signal reasons.
- Blended technical score = 65% short-term + 35% historical regime when history is available.
- Backward compatibility is preserved for older v0.2/v0.6 events without history.
- app/history.py can independently derive the one-year regime from raw daily OHLCV for research/backtest validation.

Important architecture distinction:
- Pine has access to chart history and calculates indicators across historical bars even before the first realtime webhook fires.
- Hostinger/GitHub does not receive all raw old candles automatically from alerts; it receives new events.
- Therefore each new v0.7 event carries a compact, confirmed long-term regime summary derived from TradingView history.
- Raw historical OHLCV remains available through TradingView MCP for deeper research/backtesting and can be processed by app/history.py.
- Historical/delayed data is never used as a fresh execution quote.

Current production validation gate:
The owner is currently running v0.6.4 Clear Visual in TradingView. v0.7 Historical Context is merged and CI-green but is not yet compiled/live-validated in the TradingView UI. Existing XAUUSD v0.2 production alert remains active. Do not mark the 10-symbol v0.7 feed production-ready until the owner installs v0.7 and one live 15m cycle proves: compile success, no fire_control stop, all available symbol events accepted, historical fields persisted, and backend reasons show historical_regime + blended_technical.


## TradingView v0.7.1 compile acceptance — 2026-09-21 13:18 UTC

Owner loaded STC Capital Multi Feed v0.7.1 Historical Context in TradingView Pine Editor on CAPITALCOM:BTCUSD 15m.
Visual evidence shows:
- Pine script compiled with no visible error banner.
- Script was added to the chart successfully.
- Indicator title on chart: STC Capital Multi Feed v0.7.1 Historical Context.
- Stateful visual setup rendered on chart with locked LONG label and entry/SL/TP1/TP2 values.
- Existing verified STC XAUUSD 15m PROD alert remains active separately.

This satisfies the Pine compile/add-to-chart gate for v0.7.1.

Remaining production gate:
TradingView indicator alerts snapshot script state at creation, so the old stopped v0.3 multi-symbol alert cannot validate v0.7.1. A fresh indicator alert must be created manually in TradingView UI because the TradingView MCP create-alert action does not support indicator/study alerts.

Required owner action:
Create one new alert on CAPITALCOM:BTCUSD 15m with:
- Condition: STC Capital Multi Feed v0.7.1 Historical Context
- Trigger: Any alert() function call
- Name: STC CAPITAL 10-SYMBOL 15m PROD v0.7.1
- Webhook URL: existing STC webhook endpoint already used by verified production alert
- Keep auto-deactivate OFF
- User-facing App/Toast notifications may be disabled to avoid 10-symbol notification noise
Do not stop the verified XAUUSD v0.2 production alert until v0.7.1 completes one full live acceptance cycle.

Acceptance after creation:
Observe one 15m fire cycle, confirm no fire_control stop, inspect alert log symbol coverage, verify Hostinger accepts unique events, confirm GitHub worker success, and verify historical_regime + blended_technical evidence in durable signal readback.


## v0.7.1 production alert provisioned — 2026-09-21 14:04 UTC

TradingView alert:
- alert_id: 5662088915
- name: STC CAPITAL 10-SYMBOL 15m PROD v0.7.1
- scheduler symbol: CAPITALCOM:BTCUSD
- resolution: 15m
- alert type: pine_alert
- active: true
- create_time: 2026-09-21T14:02:06Z
- expiration: 2026-10-21T13:59:22Z
- first fire: pending at initial verification
- existing verified XAUUSD v0.2 alert 5659303693 remains active as fallback.

Initial acceptance state:
- v0.7.1 Pine compile/add-to-chart: VERIFIED.
- Fresh v0.7.1 indicator alert creation: VERIFIED.
- First v0.7.1 live fire: PENDING.
- 10-symbol unique coverage: PENDING.
- historical context delivery/persistence: PENDING.
- GitHub worker ingestion: PENDING.
- durable signal reasons with historical_regime/blended_technical: PENDING.
- fire_control stability: PENDING.

Do not retire XAUUSD v0.2 until all pending v0.7.1 live acceptance gates pass.


## v0.7.1 live production acceptance — 2026-09-21 14:31 UTC

Acceptance is COMPLETE.

TradingView:
- alert_id 5662088915 (STC CAPITAL 10-SYMBOL 15m PROD v0.7.1) remains ACTIVE.
- Cycle 1 fired at 2026-09-21T14:15:01Z for remote bar time 2026-09-21T14:00:00Z.
- Cycle 2 fired at 2026-09-21T14:30:00Z for remote bar time 2026-09-21T14:15:00Z.
- Both cycles emitted exactly the 10 expected Capital.com symbols once each:
  BTCUSD, ETHUSD, DOGEUSD, EURUSD, AUDUSD, USDZAR, XAUUSD, XAGUSD, SPX500, NAS100.
- Every observed webhook delivery returned HTTP 200.
- No duplicate burst and no fire_control stop occurred across the two observed cycles.
- v0.7.1 alert remained active after cycle 2.

Hostinger / GitHub worker:
- First accepted batch: claimed=10, ingested=10, rejected=0, failed=0.
- Second accepted batch: claimed=10, ingested=10, rejected=0, failed=0.
- Extra repository_dispatch runs were concurrency-cancelled or drained claimed=0; no data loss was observed.
- Worker processing remained SUCCESS.

Durable readback for the first v0.7.1 cycle:
- count=10 current-cycle events.
- history_complete=true on all 10.
- historical_regime and blended_technical reasons were present on all 10.
- SPX500 produced an actionable LONG and immutable locked plan:
  plan_id=plan-b0859d87722568e03cc6a9bbb6673830
  levels_locked=true
  execution=manual_only.
- Other symbols in that cycle were WAIT and therefore correctly had no locked trade plan.
- This proves the historical-context scoring path and locked-plan path are live in production.

Repository:
- A temporary CI mismatch caused by the indicator version string v0.7 -> v0.7.1 was corrected.
- Main CI run 35611415039: SUCCESS.

Fallback retirement:
- Old single-symbol alert STC XAUUSD 15m PROD (5659303693) was PAUSED after v0.7.1 acceptance passed.
- It was not deleted, so history/settings remain available for rollback.
- v0.7.1 is now the active production market-data feed.

Operational conclusion:
The 10-symbol TradingView -> webhook -> Hostinger -> GitHub worker -> historical regime -> blended signal -> immutable trade-plan pipeline is production-verified.
Safe Mode / Kill Switch / human approval boundaries remain unchanged; no automatic trade execution has been enabled.


## Final software completion checkpoint — 2026-09-21 14:47 UTC

Repository implementation is complete for the agreed manual-execution competition architecture.

New production operator layer:
- PR #14 merged and CI-green: durable read-only operator API/dashboard for serverless deployments.
- PR #15 merged and CI-green: additive Hostinger owner console.
- Hostinger console files:
  - hostinger_patch/operator_snapshot.php
  - hostinger_patch/operator.php
- Owner console reads the latest authoritative analyzed signal per Capital.com symbol.
- It displays immutable backend locked plans and durable approval/runtime state.
- It permits explicit human approve/reject through the existing approval.php contract.
- It permits explicit owner Safe Mode / Kill Switch changes through runtime_control.php.
- It contains no order-placement endpoint and cannot execute, modify, or close a competition order.
- Owner token is entered only for the current browser session and is not stored by the console.

Production feed health at the final software checkpoint:
- Alert 5662088915 remained ACTIVE.
- Last observed fire: 2026-09-21T14:45:00Z.
- The 14:45 cycle emitted the expected 10 symbols once each.
- Observed webhook responses were HTTP 200.

Cleanup:
- The one-time GitHub live-acceptance readback workflow was removed after acceptance evidence was captured.
- Permanent CI and bridge-processing workflows remain.

Final external owner action required:
Upload operator_snapshot.php and operator.php to the existing Hostinger public_html STC location, then perform the first owner-console read-only check with Safe Mode and Kill Switch still ON.

After that validation, any decision to disable Safe Mode / Kill Switch and make manual approvals available is an explicit owner operational decision. STC never performs automatic order execution.


## Owner console deployment verified — 2026-09-21 15:24 UTC

Owner deployed:
- hostinger_patch/operator.php
- hostinger_patch/operator_snapshot.php

Browser validation:
- https://stc.feama.site/operator.php loaded successfully.
- Owner token authentication succeeded.
- Durable runtime controls were read successfully.
- Safe Mode=true.
- Kill Switch=true.
- Runtime version=1.
- Latest analyzed Capital.com cards rendered successfully.
- Visible cards showed WAIT recommendations and no locked plans, which correctly remained non-approvable and manual_ready=false.

Production feed re-check:
- Alert 5662088915 remains ACTIVE.
- Last observed fire at this checkpoint: 2026-09-21T15:15:00Z.
- The 15:15 cycle emitted all 10 expected Capital.com symbols exactly once.
- All 10 observed webhook deliveries returned HTTP 200.

Current final boundary:
The software and owner console are operationally deployed and readback-verified.
The system remains intentionally blocked from manual approvals because Safe Mode and Kill Switch are both ON.
No order execution path exists in STC.
Any future transition to manual approval availability requires an explicit owner runtime-control action.


## Final go-live requirements expanded by owner — 2026-09-21

Owner clarified that the final system must not be only a signal generator. It must have portfolio-level awareness of all open competition positions and avoid churn between opportunities.

Mandatory before declaring competition-ready:
- Do not enable manual approval mode yet.
- Add a durable open-position ledger for the production Hostinger path.
- Add a Portfolio Supervisor that evaluates every open position against current market state and new opportunities.
- Supervisor actions must distinguish: HOLD, PROTECT/TIGHTEN, PARTIAL TAKE PROFIT, EXIT NOW, CANCEL PENDING PLAN, and ROTATION CANDIDATE.
- A stronger new signal must not automatically close an existing trade. Rotation requires current-thesis deterioration/invalidation plus a materially better net risk-adjusted opportunity after spread/commission/slippage and portfolio exposure.
- Add anti-churn controls (state hysteresis/cooldown/closed-bar confirmation) so small score changes cannot repeatedly flip positions.
- Add final position sizing so an approved plan states exact proposed quantity subject to competition maximums and configured risk fraction.
- Add live portfolio risk aggregation across correlated/open positions.
- Add explicit multi-timeframe decision context in the backend; current production decision is 15m plus confirmed 1D historical regime. Final target should expose entry/decision TF and higher-timeframe confirmations explicitly.
- Integrate non-technical live factors before go-live. Current production event decision supplies technical factor only; news, macro, volatility-quality, and liquidity-quality remain zero unless populated elsewhere. Do not describe the current live signal as full multi-factor analysis until this is implemented and verified.
- Add actionable notifications for NEW PLAN and POSITION MANAGEMENT changes; do not notify on every raw 15m feed bar.
- Notification target should support redundant mobile channels (preferred: Telegram plus email or another push channel) in addition to browser notification.
- Owner console auto-refresh patch is merged in main; Hostinger operator.php must be replaced with the latest main version to activate 30-second auto refresh and browser notification opt-in.

Critical competition identity check:
Recent TradingView screenshots have shown a bottom trading account labelled The Leap / AMP FUTURES with a 250,000 balance while the active STC production feed/profile is capital-africa-sep-2026 using CAPITALCOM symbols and a 100,000 profile. Before any competition trade is approved, confirm which competition account is actually being used. Position sizing, allowed instruments, and rule validation must match the real active competition.


## Dual-competition owner-console UI validation — 2026-09-21 18:41 UTC

Owner deployed and visually validated the tabbed console:
- Overview tab works.
- Capital.com Africa tab renders 10 current cards.
- AMP Futures tab renders and is currently empty because its TradingView feed/alert has not yet been provisioned.
- General Lab tab renders isolated research-capital/currency/watch-symbol settings.
- Notifications tab renders browser/mobile/email channel status.
- Auto refresh is active in the browser.
- Safe Mode=true and Kill Switch=true remain unchanged.
- Current Capital cards are WAIT; locked opportunities=0 and manual-ready=0, which is expected.

UI polish merged in PR #20 after CI success:
- top control row now supports token + Refresh + browser alerts + Clear token without wrapping oddly;
- Overview empty state now says no actionable locked opportunities rather than misleadingly saying no analyzed signals.

Next owner-required step:
Provision the AMP Futures TradingView Pine feed from tradingview/STC_AMP_CORE_FEED.pine and create its indicator alert to the existing STC webhook. Do not disable Safe Mode/Kill Switch.


## AMP alert flood-stop discovered and fixed — 2026-09-21 19:22 UTC

Owner created TradingView alert:
- name: STC AMP 16-SYMBOL 15m PROD v0.2
- alert_id: 5664628299
- scheduler symbol: CME_MINI:MES1!
- resolution: 15m

Immediate verification found:
- active=false
- last_fire_time=null
- no AMP alert-log events

Root cause:
The single Pine script could emit 16 alert() calls in one realtime cycle. This exceeds the safe script-alert burst design and can trigger TradingView's alert flood-stop behavior.

Fix merged in PR #22 after CI success:
- Feed A: tradingview/STC_AMP_CORE_FEED.pine
  - STC AMP Core Feed A v0.3 Stateful Visual
  - 8 symbols: MES, MNQ, MYM, M2K, MCL, MNG, MGC, SIL
  - retains stateful chart visuals
- Feed B: tradingview/STC_AMP_CORE_FEED_B.pine
  - STC AMP Core Feed B v0.3 Companion
  - 8 symbols: M6E, M6B, MJY, M6A, MBT, MET, ZN, ZB
  - no chart clutter
- Regression tests cap each production alert at 8 symbol events per cycle.
- Full 16-symbol AMP coverage remains intact.

Owner next action:
Replace the current AMP v0.2 visual with Feed A v0.3, add Feed B v0.3 to the chart, and create two webhook alerts:
1) STC AMP A 8-SYMBOL 15m PROD v0.3
2) STC AMP B 8-SYMBOL 15m PROD v0.3
Both use Any alert() function call, 15m, same STC webhook, Webhook notification only.
Do not re-enable or reuse the stopped 16-symbol v0.2 alert.


## AMP v0.3 alert verification — 2026-09-21 19:31 UTC

Visual validation from owner screenshots:
- Feed A v0.3 Stateful Visual is on MES1! and correctly draws EMA/entry/stop/TP zones plus current LONG label.
- Feed B v0.3 Companion is on the chart and intentionally has no visible lines/labels.

TradingView alert verification:
- STC AMP B 8-SYMBOL 15m PROD v0.3 (5664684004): ACTIVE, webhook configured, no error, created 19:30:15Z and awaiting its next 15m cycle.
- An extra alert named STC AMP Core Feed B v0.3 Companion (5664675386) fired 8 valid webhook events at 19:30Z with HTTP 200 for the Feed B symbols. This duplicate alert was manually STOPPED through the official MCP to prevent duplicate batches.
- STC AMP A 8-SYMBOL 15m PROD v0.3 (5664682003): INACTIVE with last_error=study_error and last_stop_reason=error, with no fire events.
- Full alert payload proves the faulty A alert captured the OLD Pine snapshot whose study description is STC AMP Core Feed v0.2 Stateful Visual, not the current v0.3 Feed A script. It cannot be repaired by changing alert settings because indicator-based alert conditions snapshot the Pine script at creation.

Required owner action:
Create a fresh Feed A alert from the CURRENT STC AMP Core Feed A v0.3 Stateful Visual indicator:
- Any alert() function call
- 15m
- Webhook only
- same STC webhook
- use a distinct name such as STC AMP A 8-SYMBOL 15m PROD v0.3 FIX
Do not restart the inactive A alert 5664682003.


## AMP Feed A v0.3 alert recreated correctly — 2026-09-21 19:40 UTC

Owner recreated Feed A alert from the CURRENT v0.3 Pine snapshot:
- alert_id: 5664752419
- name: STC AMP A 8-SYMBOL 15m PROD v0.3 FIX
- active=true
- resolution=15
- webhook configured
- mobile_push=false
- popup=false
- last_error=null
- TradingView alert payload confirms study description:
  STC AMP Core Feed A v0.3 Stateful Visual

Feed B production alert:
- alert_id: 5664684004
- name: STC AMP B 8-SYMBOL 15m PROD v0.3
- active=true
- resolution=15
- webhook configured
- last_error=null

The duplicate Feed B alert 5664675386 remains stopped.
The broken A alert 5664682003 remains stopped.
The old 16-symbol v0.2 alert 5664628299 remains stopped.

Next validation gate:
Observe the next 15-minute cycle (19:45 UTC / 22:45 Cairo) and confirm A emits 8 events and B emits 8 events, all with HTTP 200, without either production alert being auto-stopped.


## AMP 8+8 production acceptance passed — 2026-09-21 19:46 UTC

TradingView production cycle at 19:45 UTC:
- Feed A alert 5664752419 remained ACTIVE after firing.
- Feed B alert 5664684004 remained ACTIVE after firing.
- Feed A emitted exactly 8 events:
  CBOT_MINI:MYM1!, CME_MINI:M2K1!, CME_MINI:MES1!, CME_MINI:MNQ1!, COMEX_MINI:MGC1!, COMEX_MINI:SIL1!, NYMEX:MCL1!, NYMEX:MNG1!
- Feed B emitted exactly 8 events:
  CBOT:ZB1!, CBOT:ZN1!, CME:MBT1!, CME:MET1!, CME_MINI:M6A1!, CME_MINI:M6B1!, CME_MINI:M6E1!, CME_MINI:MJY1!
- All 16 AMP webhook deliveries returned HTTP 200.
- Neither production alert auto-stopped.
- Combined 15m cycle produced 26 bridge events total when the existing 10-symbol Capital.com feed is included.
- Worker drained the batch successfully across two successful runs:
  - claimed=20, ingested=20, rejected=0, failed=0
  - claimed=6, ingested=6, rejected=0, failed=0
- Total: claimed=26, ingested=26, rejected=0, failed=0.

Acceptance conclusion:
The dual competition market-data ingestion path is now production-verified for 10 Capital.com symbols + 16 AMP Futures symbols per 15-minute cycle.

## Opportunity lifecycle / notification UX fix ready on main; Hostinger deploy pending — 2026-09-22

Owner reported from the live console that actionable cards were difficult to read, order type was unclear, expired opportunities remained visible, and an opportunity appeared without an owner notification.

Code-side fix is complete on main at commit 058844580eeae37d2631b61d83bbba30abe6a6b5. GitHub Actions STC CI run 35655238485 completed successfully.

Implemented behavior:
- 15m plan validity is anchored to the confirmed TradingView bar close, not delayed worker processing time.
- LONG/SHORT cards are actionable only while their locked plan is ACTIVE.
- Expired opportunities auto-hide immediately when the countdown reaches zero, independent of the 30-second server refresh.
- WAIT remains current-signal context only and is not counted as an opportunity.
- Console times are browser-local and human-readable, with a live seconds/minutes countdown.
- Card layout keeps labels and values closer for easier scanning.
- Planned manual order instruction is explicit and live-price aware: MARKET, BUY_LIMIT, BUY_STOP_LIMIT, SELL_LIMIT, or SELL_STOP_LIMIT as applicable to direction and entry-zone relationship.
- Owner-entered current TradingView price recalculates the manual order instruction before approval.
- Browser alerts no longer silently suppress an already-active unseen plan when permission is enabled after page load; seen-plan state is persisted in localStorage.
- Telegram/email notification generation skips expired plans and includes ACTIVE time-left plus order type.
- No automatic broker/order execution path was added. Safe Mode / Kill Switch governance remains unchanged.

Production drift check:
- A live read of https://stc.feama.site/operator.php still shows the older Owner Console shell: competition tabs are present, but the deployed HTML still says Telegram and Email are merely "Planned", and it lacks the newer account/portfolio blocks and opportunity-lifecycle UI.
- Therefore the user's screenshots are consistent with an older Hostinger deployment, not the current main branch.

Deployment gate before production validation:
Replace the Hostinger production copies with the current main versions of:
- hostinger_patch/operator.php
- hostinger_patch/operator_snapshot.php
- hostinger_patch/portfolio_control.php
- hostinger_patch/notification_control.php

After deployment, validate the live console with Safe Mode=true and Kill Switch=true, confirm expired cards disappear on countdown, confirm readable local time/order instructions, and test browser/server notification behavior. Telegram/email delivery still requires private channel configuration and must not be committed to GitHub.

## Persistent executed-position tracking + sizing + qualification progress merged — 2026-09-22

Merged PR #30 to main as commit f01e7a296b20666b61e6a29f8ae77c123bd6e8a0.

Post-merge STC CI run 35660463740 completed successfully.

Owner-facing behavior now implemented in the Hostinger patch set:
- Executed/open positions are persistent Portfolio Supervisor records and are not replaced by later signals on the same symbol.
- New same-symbol signals become management evidence for the existing position instead of replacement entry opportunities.
- Existing manually opened competition positions can be backfilled into STC with original open time, quantity, entry, current stop and one final take-profit.
- Single-TP owner workflow: target1 is retained only as an internal management checkpoint; target2 is the owner-facing final take-profit. No automatic partial-TP recommendation is generated at the checkpoint.
- New opportunities show proposed quantity, trade risk in USD/percent, configured risk budget, official max open position and projected open quantity.
- Competition progress is exposed from recorded position activity, including qualifying trading days, days remaining, entries, open/closed positions, trade actions and realized P/L.
- Capital.com Africa profile requires 3 qualifying trading days; AMP Futures profile requires 5.
- Telegram/email notification payloads now include direction/order context, quantity, risk, official max, stop, management checkpoint, final TP and signal score.
- Manual execution and human approval remain mandatory; no broker order path was added.

Production deployment is still required for Hostinger to use the new main-branch patch files.
Telegram delivery additionally requires private Hostinger config values for telegram_bot_token and telegram_chat_id; never commit those secrets to GitHub.
## Live Owner Console recovered; historical trade import merged — 2026-09-22

Production screenshot confirmed the Owner Console is connected again after the missing Hostinger files/migrations were completed:
- Capital.com symbols monitored: 10
- AMP Futures symbols monitored: 16
- Macro calendar: CONNECTED
- Safe Mode: true
- Kill Switch: true
- ACTIVE opportunities at validation moment: 0
- Open positions tracked at validation moment: 0

The HTTP 500 deployment drift was resolved by completing the current Hostinger dependency set, including portfolio/account/notification tables and the required macro-control dependency.

Merged PR #31 as commit d772575c02f2ef199e7837153d3812f54a0a8cde.
Post-merge STC CI run 35662614893 completed successfully.

PR #31 adds:
- owner-only import of already-closed historical competition trades;
- original open/close timestamps preserved for qualification-day accounting;
- optional actual realized P/L from the competition platform, otherwise STC estimate;
- historical open/close audit events without broker execution;
- Owner Console button for past closed-trade import;
- competition progress counting historical closed dates rather than import date;
- complete Hostinger production file manifest to prevent future partial-deployment drift.

Next owner dependency:
- deploy current main versions of hostinger_patch/operator.php, hostinger_patch/position.php, and hostinger_patch/portfolio_control.php to expose the historical closed-trade import UI/logic;
- then backfill the owner's earlier competition trades using actual platform records/screenshots;
- Telegram delivery remains pending private bot token + chat ID configuration on Hostinger. Secrets must not be committed to GitHub.
## Production validation after historical-import deployment — 2026-09-22

Owner screenshot and live page inspection confirm the latest Owner Console is deployed successfully:
- Console connected with 30-second auto refresh.
- Capital.com lane: 10 symbols monitored.
- AMP Futures lane: 16 symbols monitored.
- Macro calendar: CONNECTED.
- Safe Mode: true.
- Kill Switch: true.
- At validation moment the Overview showed 1 ACTIVE opportunity, 0 manual-ready, and 0 tracked open positions.
- Live page contains `Import a past closed trade` controls for both competition lanes.

The active opportunity shown in the owner screenshot was AMP Futures `CBOT:ZN1!`, direction SHORT, with a 15-minute decision timeframe. Manual-ready correctly remained zero because Safe Mode and Kill Switch were still enabled.

Post-merge STC CI run 35662614893 for historical trade import completed successfully.

Next production tasks:
- backfill prior real competition trades from platform records/screenshots;
- configure Telegram privately in Hostinger with `telegram_bot_token` and `telegram_chat_id`, then use the built-in notification test;
- only after notification and ledger validation consider any runtime-control change. No automatic order execution is available.
## Reliability-weighted evidence engine merged — 2026-09-22

Merged PR #33 as commit 2dca9a35069842bd9a0559fd4a9e419815548273.
Post-merge STC CI run 35684556356 completed successfully.

New evidence architecture:
- Technical price/structure evidence is the primary direction engine.
- Indicators/features are not equal votes. Each feature has a reliability prior, family weight, freshness and independence group.
- Structural confirmations such as BOS/CHoCH, liquidity sweep, break/retest and market-structure trend start with higher priors than standalone oscillators.
- Correlated indicators (for example RSI/Stochastic/StochRSI/CCI) are discounted so they do not count as multiple independent confirmations.
- Evidence breadth across multiple independent families is required before the aggregate score can become strong.
- Conflicting evidence families are surfaced explicitly rather than silently averaged away.
- Feature reliability can be calibrated per symbol/strategy/timeframe from sample size, directional hit rate, forward expectancy, profit factor and regime stability, with shrinkage to prevent small samples from creating fake certainty.
- A transparent participation-percent utility converts calibrated raw weights to percentage contribution.

News/macro policy:
- Directional news and macro weights in the legacy composite were reduced to 5% each; technical/market-quality evidence remains dominant.
- A separate news/macro overlay caps total directional influence at 10%.
- Scheduled high-impact events can block new entries shortly before/after the event even when the technical thesis remains intact.
- Unscheduled market shocks fail closed and block entry.
- News/macro context can reduce size when it conflicts with technical evidence, but cannot independently create a large LONG/SHORT signal.

Strategy-family naming was aligned with the feature catalog (`smc_liquidity`).

Next strategy-engine work:
- build the historical data/feature pipeline that materializes the >80 catalogued features for each symbol/timeframe;
- run strategy x symbol x timeframe backtests, out-of-sample and walk-forward validation;
- write calibrated feature/strategy weights back into the runtime decision engine;
- expose family/feature participation and conflict breakdown in the Owner Console;
- wire live news source context while keeping it as a risk/context overlay rather than the main directional vote.


## Historical research + timeframe-safe calibration checkpoint — 2026-09-22

Status: CODE COMPLETE FOR CURRENT PHASE; broad research screening in progress. No automatic execution authority.

### Research engine now on main
- Full >80-feature historical feature materialization from confirmed OHLCV.
- Strict no-lookahead historical evaluation.
- Conservative next-bar/approved-entry-zone fill logic aligned with the live approval envelope.
- Live-aligned risk model: 1.20 ATR initial stop and one final 2.50R take-profit; TP1 is management checkpoint only.
- Chronological train / out-of-sample test / forward validation.
- Strategy x symbol x timeframe matrix with explicit rejection reasons.
- Exact-provider research timeframes: native 5m, 15m, 30m, 1h, 4h, 1D where supplied; deterministic 2h from complete 1h pairs and calendar month from daily bars.
- Latest potentially mutable source bar is dropped from research series.
- Feature reliability/participation calibration is permitted only after strategy/timeframe robustness passes.
- Runtime research calibration lookup is exact-timeframe specific. A 4h/1h research winner cannot silently reweight a 15m live entry.
- Matrix-only screening mode exists for broad universe discovery; it cannot be promoted into runtime calibration without validated feature participation.
- Historical feature snapshots are cached/reused across the strategy matrix and calibration to reduce repeated >80-feature computation.
- Owner Console code now exposes matching research strategy/timeframe, empirical probability confidence interval, validated feature participation, family weights actually used and MTF scores.

### Real exact-provider pilot results
TradingView Official MCP was used with provider-exact symbols and up to 5000 bars per request. The connector does not expose time pagination beyond the 5000-bar maximum.

CAPITALCOM:XAUUSD full multi-timeframe pilot:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- No calibration candidate was promoted.
- Strongest encouraging but rejected examples:
  - 2h trend_pullback: test expectancy +0.418R, PF 2.61, 16 test trades; forward expectancy +0.267R, PF 1.97, 12 forward trades. Rejected for insufficient out-of-sample sample depth.
  - 1D trend_pullback: test expectancy +0.376R, PF 2.07, 17 test trades; forward expectancy +0.579R, PF 2.42, 20 forward trades. Rejected for insufficient out-of-sample sample depth.
  - 4h breakout_expansion had positive test results but forward expectancy turned negative, so it was rejected rather than promoted.
- Conclusion: promising research candidates exist, but no strategy currently satisfies all robustness/sample gates.

CME_MINI:MES1! full multi-timeframe pilot:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- No calibration candidate was promoted.
- Strongest encouraging but rejected examples:
  - 30m breakout_expansion: test expectancy +0.439R, PF 2.56, 8 test trades; forward expectancy +0.441R, PF 2.60, 7 forward trades. Rejected for insufficient sample depth and parameter instability.
  - 15m smc_structure_liquidity: test expectancy +0.130R, PF 1.68, 9 test trades; forward expectancy -0.021R, PF 0.95, 15 forward trades. Rejected for insufficient sample depth, regime instability and negative/weak forward performance.
- Conclusion: no MES strategy/timeframe is currently permitted to become a calibrated live strategy.

Research policy:
- Do NOT lower validation gates merely to create a trade signal.
- Setup Quality remains separate from empirical win probability.
- No percentage win probability is displayed as calibrated unless the comparable out-of-sample + forward sample passes the probability gate.
- Positive-looking but under-sampled candidates remain research-only.

### Production feed status vs code-ready feed
Current TradingView production alerts remain active on the previously verified feeds:
- Capital.com: STC CAPITAL 10-SYMBOL 15m PROD v0.7.1.
- AMP Feed A: STC AMP A 8-SYMBOL 15m PROD v0.3 FIX.
- AMP Feed B: STC AMP B 8-SYMBOL 15m PROD v0.3.
These remain the production ingestion rollback baseline.

The repository main branch also contains the newer six-way multi-timeframe Family Breadth feed set:
- STC_CAPITAL_MTF_FEED_A.pine v1.1
- STC_CAPITAL_MTF_FEED_B.pine v1.1
- STC_AMP_MTF_FEED_A.pine v1.1
- STC_AMP_MTF_FEED_B.pine v1.1
- STC_AMP_MTF_FEED_C.pine v1.1
- STC_AMP_MTF_FEED_D.pine v1.1

The v1.1 feeds add confirmed 1h/2h/4h/1D/monthly context plus nine live evidence-family scores. They are code-ready but are not yet the active TradingView alert snapshots. Indicator-alert conditions cannot be replaced through the available TradingView MCP; fresh Pine alerts must eventually be created manually from the current v1.1 scripts.

Do not stop the verified old production alerts until the new v1.1 alerts have completed a full parallel-cycle acceptance test with HTTP 200 and correct symbol counts.

### Immediate engineering next action
1. Run matrix-only exact-provider screening across representative and then full competition universe symbols.
2. Use the per-timeframe diagnostics to identify candidates that genuinely pass OOS + forward gates.
3. Run full feature calibration only for validated candidates.
4. Promote only same-entry-timeframe calibration records.
5. Keep Safe Mode / Kill Switch and manual execution governance unchanged.
6. After a useful validated 15m candidate exists, owner intervention will be required to create the six fresh TradingView v1.1 indicator alerts and later configure private Telegram credentials if not already configured.

Owner intervention required now: NO.


### Matrix-only screening expansion — BTCUSD + EURUSD — 2026-09-22

CAPITALCOM:BTCUSD:
- Overall research status: VALIDATED.
- Selected overall strategy/timeframe: trend_pullback on 1D.
- Robust score: 44.59.
- Test: 30 trades, expectancy +0.194R, PF 1.357.
- Forward: 19 trades, expectancy +0.105R, PF 1.194.
- Empirical probability status: INSUFFICIENT_DATA because total comparable OOS+forward sample is 49, below the 50-sample calibration floor.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- Therefore this 1D result remains informational research only and is not eligible to reweight the 15m live decision engine.
- No calibration candidate was promoted.

CAPITALCOM:EURUSD:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- 1h mean_reversion produced 51 test trades with positive test PF 1.336, but forward expectancy was -0.250R with PF 0.269 and parameter instability, so it was rejected.
- 2h mean_reversion and 4h volatility_squeeze also showed positive test metrics but negative forward performance, so they were rejected.
- No calibration candidate was promoted.

Research interpretation:
- The engine is correctly distinguishing an overall research winner from a live-entry winner.
- A validated higher-timeframe strategy does not authorize or weight a 15m entry.
- The current 5000-bar TradingView connector cap materially limits low-timeframe sample depth; validation gates remain unchanged rather than being relaxed.
- Broad screening should continue with matrix-only mode, prioritizing highly liquid index/metals/energy symbols where 15m signal count may be sufficient.

Owner intervention required now: NO.


### BTCUSD full feature calibration + research performance checkpoint — 2026-09-22

CAPITALCOM:BTCUSD full-mode follow-up:
- Overall research remains VALIDATED only for trend_pullback on 1D.
- Robust score remains 44.59.
- Test: 30 trades, expectancy +0.194R, PF 1.357.
- Forward: 19 trades, expectancy +0.105R, PF 1.194.
- Full feature validation produced 19 deployable research features and blocked 25.
- Empirical win probability remains intentionally withheld: 49 comparable OOS+forward outcomes is below the 50-sample calibration floor.
- Live-entry 15m remains NO_VALIDATED_STRATEGY.
- No runtime calibration candidate was promoted; the validated 1D result remains informational only for live 15m execution.

Research performance improvement merged to main:
- Commit 6d2d912497b806c910320cd1eb9d94593f27306d eliminates quadratic full-prefix list copies during historical feature materialization.
- Each snapshot now receives the exact latest-1000-bar window that the feature extractor already consumed internally.
- Regression testing proved timestamp, feature values and observations remain identical to the previous full-prefix semantics at multiple historical indices.
- No formula, score, threshold, risk rule or execution behavior changed.

Active screening batches:
- research/index-screen-b-20260922: CAPITALCOM:NAS100 + CME_MINI:MNQ1!, matrix_only, full six input timeframes each.
- research/metals-energy-screen-c-20260922: CAPITALCOM:XAGUSD + NYMEX:MCL1!, matrix_only, full six input timeframes each.
- At this checkpoint both batches are in the no-lookahead computation step with complete input sets and no active data-quality failure.

Owner intervention required now: NO.


## Broad screening checkpoint — NAS100 / MNQ / XAGUSD / MCL — 2026-09-22

All results below are from exact-provider TradingView OHLCV, no-lookahead matrix-only screening with unchanged robustness gates.

CAPITALCOM:NAS100:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- 15m best candidate was range_rotation: test expectancy +0.043R, PF 1.106, 20 trades; forward expectancy -0.547R, PF 0.220, 10 trades.
- 1h SMC showed test expectancy +0.145R and forward +0.170R but only 11 test / 11 forward trades and parameter instability; research-only.
- No calibration candidate promoted.

CME_MINI:MNQ1!:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- 15m best candidate was mean_reversion and failed forward: test expectancy -0.039R, PF 0.917; forward expectancy -0.266R, PF 0.477.
- 30m SMC was the strongest encouraging candidate: test expectancy +0.282R, PF 1.512, 17 trades; forward expectancy +0.132R, PF 1.230, 9 trades. Rejected for insufficient sample depth and parameter instability.
- No calibration candidate promoted.

CAPITALCOM:XAGUSD:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- 15m best candidate range_rotation failed forward: test expectancy -0.137R, PF 0.768; forward expectancy -0.375R, PF 0.528.
- 30m SMC showed test expectancy +0.457R, PF 2.213, 14 trades, but forward expectancy -0.701R, PF 0.211.
- 4h SMC and volatility_squeeze had positive test results but negative forward results.
- No calibration candidate promoted.

NYMEX:MCL1!:
- Overall status: NO_VALIDATED_STRATEGY.
- Live-entry 15m status: NO_VALIDATED_STRATEGY.
- 15m SMC failed forward: test expectancy -0.016R, PF 0.974; forward expectancy -0.606R, PF 0.325.
- 2h volatility_squeeze was the strongest positive-forward research candidate: test expectancy +0.046R, PF 1.100, 21 trades; forward expectancy +0.364R, PF 2.478, 16 trades. Rejected for insufficient sample depth / weak OOS expectancy / parameter instability.
- No calibration candidate promoted.

Cross-symbol conclusion:
- The current strict gate is correctly rejecting attractive in-sample results when forward performance or sample robustness is inadequate.
- No 15m live-entry research calibration has been validated across XAUUSD, MES, BTCUSD, EURUSD, NAS100, MNQ, XAGUSD or MCL.
- Do not relax gates to manufacture a 15m signal.
- Continue broad matrix-only screening across remaining competition symbols.
- Full feature calibration remains reserved for a robust validated strategy/timeframe only.

Engineering note:
- ATR feature-calibration caching was merged to main as commit 582d9d4f836c18f3f0ae8648c5e11342f9da34ea after successful CI.
- Duplicate re-screening of NAS100/MNQ was accidentally launched during state reconciliation; its result is non-authoritative unless it reveals a reproducibility mismatch. The earlier completed documented run remains the baseline.
- A separate XAGUSD + MGC screening run is active; XAGUSD is duplicate confirmation, while MGC is new evidence.

Owner intervention required now: NO.

## Strategy Lab v2 + no-lookahead MTF research checkpoint — 2026-09-22

Status: ACTIVE RESEARCH. Owner intervention required now: NO.

### Strategy research expansion merged
- Commit 6c945612348ee5ddbccbc7c602cec4303a7469b6 expanded the research-only strategy matrix from 9 to 17 strategy families.
- Added: adx_ema_trend, donchian_structure_breakout, bollinger_mean_reversion, vwap_reversion, liquidity_sweep_reversal, failed_breakout_reversal, fvg_displacement_continuation and volume_confirmed_breakout.
- Existing SMC, trend pullback, breakout, mean reversion, VWAP intraday, scalping/microtrend, momentum, volatility squeeze and range rotation remain.
- Strategy-specific family weights and hard-confirmation rules remain research-only until validated.
- No validation gate, risk rule, Safe Mode, Kill Switch or manual execution rule was relaxed.

### No-lookahead multi-timeframe research merged
- Commit d724a5993aba3068b11848471d6cb9dc701343c0 added a research-only optional signal gate.
- Confirmed higher-timeframe context is aligned without lookahead: a higher-TF bar is usable only after the next bar proves it closed.
- Required confirmation research set: 1H, 2H, 4H, 1D and 1M.
- Three alternative policies are tested rather than assuming one rule is best:
  - MAJORITY
  - TREND_WEIGHTED
  - STRICT
- Missing required higher-timeframe context fails closed.
- MTF validation is evaluated with the same chronological train / OOS test / forward framework as baseline strategy trials.

### Selective MTF comparison runner merged
- Commit 61443ea8223c76b6767373f0c4f3e5314aba5be0 added research_mode=mtf_compare.
- The runner first executes the normal strategy matrix.
- Only the strongest adequately sampled 15m candidates are selected for MTF comparison.
- Each selected candidate is compared under MAJORITY / TREND_WEIGHTED / STRICT.
- Research diagnostics include test/forward expectancy, profit factor, trade retention, robust score and rejection reasons.
- mtf_compare does not perform feature calibration and cannot create live authority.
- Full feature calibration remains reserved for a genuinely validated same-entry-timeframe candidate.

### Additional completed exact-provider screening evidence
COMEX_MINI:MGC1!:
- Overall: NO_VALIDATED_STRATEGY.
- Live-entry 15m: NO_VALIDATED_STRATEGY.
- 15m range_rotation showed positive test/forward tendencies but failed sample/stability gates.
- 4h trend_pullback and other attractive test results failed forward or stability gates.
- No calibration candidate promoted.

CAPITALCOM:SPX500:
- Overall: NO_VALIDATED_STRATEGY.
- Live-entry 15m: NO_VALIDATED_STRATEGY.
- 2h SMC produced strong-looking PF but only 4 test / 8 forward trades, therefore rejected as under-sampled.
- No calibration candidate promoted.

CME_MINI:M2K1!:
- Overall: NO_VALIDATED_STRATEGY.
- Live-entry 15m: NO_VALIDATED_STRATEGY.
- Multiple candidates failed forward robustness or had materially insufficient samples.
- No calibration candidate promoted.

Research conclusion remains unchanged:
- Do not lower sample, stability, OOS, forward or risk gates simply to manufacture trade frequency.
- Attractive small-sample results remain research-only.
- Setup Quality is not Win Probability.
- A higher-timeframe research winner cannot silently authorize/reweight a 15m live entry.



### ETHUSD + M6E completed screening — 2026-09-22
CAPITALCOM:ETHUSD:
- Overall: NO_VALIDATED_STRATEGY.
- Live-entry 15m: NO_VALIDATED_STRATEGY.
- 2h SMC looked strong numerically (test expectancy +0.495R, PF 4.05; forward +0.571R, PF 2.74) but had only 5 test / 4 forward trades and parameter instability, so it was rejected.
- 15m VWAP intraday had positive test expectancy +0.254R but forward expectancy -0.268R and PF 0.634; rejected.
- No calibration candidate promoted.

CME_MINI:M6E1!:
- Overall: NO_VALIDATED_STRATEGY.
- Live-entry 15m: NO_VALIDATED_STRATEGY.
- 2h SMC had positive test/forward but only 4 test / 6 forward trades plus instability; rejected.
- 1h mean reversion had 54 test trades but weak OOS edge and strongly negative forward expectancy; rejected.
- 15m range rotation and volatility squeeze remained weak/forward-negative.
- No calibration candidate promoted.

Interpretation:
- Strong-looking PF/expectancy on tiny samples is not treated as confidence.
- Neither ETHUSD nor M6E is eligible for runtime calibration from this screen.

### Active research batches
1. research/strategy-v2-xau-mnq-20260922
   - CAPITALCOM:XAUUSD
   - CME_MINI:MNQ1!
   - exact same historical datasets reused for fair Strategy Lab v1 vs v2 comparison
   - matrix_only with 17 strategies
   - status at checkpoint: in progress

2. research/strategy-v2-btc-mcl-20260922
   - CAPITALCOM:BTCUSD
   - NYMEX:MCL1!
   - exact same historical datasets reused for fair comparison
   - matrix_only with 17 strategies
   - status at checkpoint: in progress

### Immediate next execution sequence
1. Read the three active batch results when complete.
2. Identify any 15m candidate with meaningful OOS + forward evidence.
3. For promising 15m candidates, launch research_mode=mtf_compare.
4. Compare baseline vs MAJORITY / TREND_WEIGHTED / STRICT and reject policies that create insufficient sample depth.
5. Run full feature calibration only if a same-entry-timeframe strategy actually passes robustness gates.
6. Only after a validated 15m research candidate exists consider promotion to the runtime calibration registry.
7. TradingView production alert migration to six v1.1 Family Breadth feeds remains a later owner-manual step; keep verified legacy alerts running until parallel acceptance.

Owner intervention required now: NO.

## Strategy Lab v2 / regime research continuation checkpoint — 2026-09-23

Status: ACTIVE RESEARCH. Owner intervention required now: NO.

### Completed Strategy Lab v2 exact-provider runs
CAPITALCOM:XAUUSD:
- 4h adx_ema_trend is VALIDATED: 33 OOS trades, +0.219728R expectancy, PF 1.502719; 18 forward trades, +0.031997R expectancy, PF 1.066191; robust score 47.216.
- Probability calibration is available for this 4h research result only: n=51, estimated win probability 0.450980.
- 15m remains NO_VALIDATED_STRATEGY. The higher-timeframe result does not authorize 15m competition entry.

CME_MINI:MNQ1!:
- 15m remains NO_VALIDATED_STRATEGY.
- vwap_reversion baseline: 46 OOS trades, +0.179866R, PF 1.476996; 31 forward trades, -0.192629R, PF 0.648403.
- Rejected for parameter instability and forward failure.

CAPITALCOM:BTCUSD:
- 1D trend_pullback remains VALIDATED as research-only higher-timeframe evidence.
- 15m remains NO_VALIDATED_STRATEGY.
- 15m bollinger_mean_reversion: 41 OOS trades, +0.117741R, PF 1.248510; 26 forward trades, -0.043356R, PF 0.927128; rejected.

NYMEX:MCL1!:
- No validated 15m strategy. No promotion.

### Completed MTF comparison evidence
- ETHUSD MTF comparison did not rescue a 15m candidate; stricter policies often reduced trade count to near-zero.
- XAUUSD MTF comparison did not rescue a 15m candidate. Some test slices improved, but forward performance and/or sample depth remained inadequate.
- Conclusion: do not increase MTF strictness simply to manufacture backtest quality.

### Completed single-regime comparison evidence
XAUUSD:
- No individual BULL_TREND / BEAR_TREND / RANGE / TRANSITION filter validated a 15m strategy.

MNQ:
- vwap_reversion in BEAR_TREND improved materially but still failed gates:
  - OOS: 25 trades, +0.114414R, PF 1.312752.
  - Forward: 16 trades, +0.011505R, PF 1.026927.
  - Still rejected for insufficient OOS sample, parameter/regime instability and forward PF below 1.05.

BTCUSD:
- bollinger_mean_reversion in TRANSITION was the closest single-regime result:
  - OOS: 33 trades, +0.070312R, PF 1.136974.
  - Forward: 21 trades, +0.127331R, PF 1.277691.
  - Still rejected because OOS expectancy/PF remain below gates and parameter stability is inadequate.

### Regime-pool research guardrail merged
- PR #76 merged to main as e0e083a068ffe4fc39b6f218b13a11a94b0ca22f.
- Full CI on the latest PR head: 288 tests passed.
- Added research_mode=regime_pool_compare for a bounded exploratory sweep over predefined symmetric regime pools.
- Only the two strongest adequately sampled 15m candidates are evaluated.
- A same-dataset apparent pass is explicitly tagged FRESH_CONFIRMATION_REQUIRED.
- Pool research cannot change matrix_selection, live_entry_selection or live_trading_authority.
- Existing OOS/forward/stability/drawdown gates remain unchanged.

### XAUUSD full higher-timeframe feature calibration completed
- Research mode full completed successfully on the same exact-provider XAU dataset.
- 4h adx_ema_trend remains VALIDATED.
- 16 features were deployable at the validated 4h research scope; 17 were blocked.
- Leading participation included break_retest (~9.07%), BOS (~7.34%), PPO (~6.54%) plus EMA/SMA alignment, trend-efficiency and related structure/momentum features.
- 15m live-entry scope remains NO_VALIDATED_STRATEGY with 0 deployable features.
- This calibration is informational/higher-timeframe only.

### Historical data depth control merged
- TradingView Official MCP OHLCV currently exposes count up to 5000 bars and no historical date cursor in the connected schema.
- PR #77 merged to main as 8faaa8eea3c3053fdb0b1465c73d0be5517b786a.
- CI after archive addition: 295 tests passed.
- Added exact-provider OHLCV archive merge utility:
  - fails closed on symbol/timeframe mismatch,
  - validates OHLCV structure,
  - deduplicates timestamps,
  - records revised overlapping bars,
  - preserves coverage/provenance metadata.
- This supports accumulation of deeper forward history across future exact-provider pulls; it does not falsely claim old backfill that the current MCP cannot retrieve.

### Active research runs
1. research/regime-pool-mnq-20260923
   - run 35788119034
   - same MNQ historical dataset
   - research_mode=regime_pool_compare
   - status at this checkpoint: in progress

2. research/regime-pool-btcusd-20260923
   - run 35788144497
   - same BTCUSD historical dataset
   - research_mode=regime_pool_compare
   - status at this checkpoint: in progress

### Current decision
- Do not relax any validation threshold.
- Do not promote XAU 4h or BTC 1D research into 15m runtime.
- Do not treat a regime-pool winner on reused data as confirmation.
- If a pool appears to pass, require genuinely fresh/unseen confirmation before any promotion discussion.
- Safe Mode, Kill Switch, manual approval and manual execution remain unchanged.

Owner intervention required now: NO.

### Regime-pool comparison final results — 2026-09-23

MNQ run 35788119034 — COMPLETED SUCCESS:
- Overall live-entry 15m remains NO_VALIDATED_STRATEGY.
- No tested regime pool produced a non-zero robust score or a VALIDATED 15m result.
- vwap_reversion TREND_ONLY retained 40 OOS trades with strong OOS figures (+0.213297R, PF 1.566365) but forward remained negative (-0.060762R, PF 0.882527) and parameter stability failed.
- vwap_reversion BEAR_OR_RANGE produced positive OOS/forward quality (22 OOS trades, +0.103418R, PF 1.221531; 15 forward trades, +0.219413R, PF 1.510963) but was rejected for insufficient OOS sample and parameter/regime instability.
- Pools retaining 30+ OOS trades did not cure the forward failure.
- Decision: stop same-dataset regime tuning for MNQ. No promotion and no full feature calibration.

BTCUSD run 35788144497 — COMPLETED SUCCESS:
- Higher-timeframe 1D trend_pullback remains VALIDATED research-only; live-entry 15m remains NO_VALIDATED_STRATEGY.
- No tested regime pool produced a non-zero robust score or a VALIDATED 15m result.
- bollinger_mean_reversion pools with 30+ OOS trades (EXCLUDE_BULL, EXCLUDE_BEAR, EXCLUDE_RANGE) had weak/negative OOS expectancy and/or PF despite some positive forward slices.
- BULL_OR_RANGE showed +0.088015R / PF 1.199006 in OOS but only 17 OOS trades and negative forward expectancy, therefore rejected.
- failed_breakout_reversal pool results were all under-sampled and/or OOS-negative.
- Decision: stop same-dataset regime tuning for BTCUSD. No promotion and no 15m calibration.

Cross-market research conclusion:
- Strategy expansion, no-lookahead MTF confirmation, single-regime filtering and bounded regime-pool testing have now all failed to produce a validated 15m competition strategy on the strongest re-screened candidates.
- Do not add more same-dataset combinatorial filters to chase a pass.
- Do not reduce sample, expectancy, profit-factor, drawdown, stability or forward gates.
- Next evidence priority is genuinely unseen data and deeper history, not further same-window parameter/filter search.

Fresh-data clock at checkpoint:
- MNQ stored research dataset last 15m timestamp: 1790104500.
- TradingView current available last 15m timestamp observed at checkpoint: 1790109900.
- Approximately 6 new 15m bars exist beyond the development dataset: insufficient for confirmation.
- BTCUSD stored research dataset last 15m timestamp: 1790090100.
- TradingView current available last 15m timestamp observed at checkpoint: 1790113500.
- Approximately 26 new 15m bars exist beyond the development dataset: insufficient for confirmation.
- These bars start the unseen-data accumulation clock; they are not enough to claim fresh validation.

Final decision for this stage:
- Same-dataset 15m tuning is CLOSED for MNQ/BTC/XAU until additional unseen evidence is available.
- Historical OHLCV accumulation becomes the next automatic research activity.
- Existing higher-timeframe validated findings remain informational only.
- Safe Mode, Kill Switch, manual approval and manual execution remain unchanged.
- Owner intervention required now: NO.



## Confirmed-history, alternate-backfill and frozen-confirmation checkpoint — 2026-09-23

Status: IMPLEMENTATION COMPLETE TO OWNER DATA-ACCESS GATE.

### Exact-provider archive integrity
- PR #84 merged as commit 16d6c93d04f541bbf1a4242ce560c7d42a6e2dfc.
- Root cause found from live evidence: TradingView states its returned final bar may still change, but the first archive implementation stored that mutable tail.
- The archive merger now withholds a mutable final bar until a later snapshot proves it is no longer the tail.
- If an older seed already contains the current mutable tail, that copy is removed.
- Stale snapshots cannot delete a bar already confirmed by later history.
- CI for the final fix: 314 passed, 2 warnings.
- PR #85 merged as commit 4ce3fc0d13fc5d895ae238bd1c9b3f9b7deb3eb2 to apply the confirmed-only rule to the seeded archives.

Current confirmed 15m archive state after PR #85:
- CME_MINI:MNQ1!: 4,999 confirmed bars.
  - freeze/development research end actually used by the engine: 1790103600 / 2026-09-22T19:00:00Z.
  - archive confirmed-through: 1790109000.
  - genuinely unseen confirmed bars after the research freeze: 6.
  - current mutable tail 1790109900 is withheld.
- CAPITALCOM:BTCUSD: 5,000 confirmed bars.
  - freeze/development research end actually used by the engine: 1790089200 / 2026-09-22T15:00:00Z.
  - archive confirmed-through: 1790113500.
  - genuinely unseen confirmed bars after the research freeze: 27.
  - the previously mutable bar at 1790113500 was confirmed on the next snapshot and its final observed values replaced the provisional seed copy.
  - current mutable tail 1790114400 is withheld.
- CI for the confirmed-archive data refresh: 314 passed, 2 warnings.

### Capital.com older-history path
- PR #82 merged as commit c3f623b42221bd953845092f54eaf02c1c7648ea.
- CI: 310 passed, 2 warnings.
- Added read-only Capital.com REST historical adapter:
  - authenticated market discovery;
  - historical from/to pagination;
  - explicit bid / ask / mid conversion;
  - no committed credentials;
  - no order/trading endpoint;
  - alternate feed quarantined from exact-provider evidence.
- Added cross-feed reconciliation:
  - identical-timestamp overlap;
  - median/p95 close difference in basis points;
  - median OHLC difference;
  - close-return correlation.
- Capital.com REST history is NOT assumed identical to TradingView CAPITALCOM chart bars.
- Even a future CANDIDATE_MATCH reconciliation keeps live_calibration_authority=false and cannot silently merge into the TradingView archive.
- PR #88 merged as commit e4b11980d6010ba9be467f9d9a8547e9dd806f28.
- CI for PR #88: 331 passed, 2 warnings.
- Added secure branch-triggered GitHub Actions orchestration:
  - discovery and backfill requests contain no credentials;
  - credentials are read only from repository Actions secrets;
  - outputs are quarantined artifacts only;
  - no automatic commit/merge into exact-provider history.

### Frozen unseen-data confirmation
- PR #86 merged as commit 19e30bfa93c832f13d95d5a9971ce3c27e9dd25c.
- CI: 323 passed, 2 warnings.
- Added a locked manifest at research_hypotheses/frozen_15m_v1.json.
- The initial frozen baseline comparators are:
  1. CME_MINI:MNQ1! / vwap_reversion / 15m
     - threshold 0.72
     - stop 1.2 ATR
     - target 2.5R
     - max hold 16 bars
     - freeze timestamp 1790103600
     - source run 35781036628
  2. CAPITALCOM:BTCUSD / bollinger_mean_reversion / 15m
     - threshold 0.50
     - stop 1.2 ATR
     - target 2.5R
     - max hold 16 bars
     - freeze timestamp 1790089200
     - source run 35781933861
- Frozen confirmation does not optimize any parameter on unseen data.
- It accepts only confirmed TradingView Official MCP archives.
- Alternate-provider history and mutable-tail archives fail closed.
- Truncated open/time-exit trades at the archive edge are excluded.
- UNSEEN_SUPPORT requires at least 30 completed unseen trades plus unchanged performance gates and at least two usable unseen time segments.
- UNSEEN_SUPPORT is still not validation; it only opens a second confirmation decision.
- live_calibration_authority is always false.

First real frozen-confirmation smoke run 35791259901:
- COMPLETED SUCCESS.
- MNQ:
  - unseen confirmed bars: 6
  - completed unseen trades: 0
  - status: ACCUMULATING
- BTCUSD:
  - unseen confirmed bars: 27
  - completed unseen trades: 1
  - trade result: -0.32121976097584065R
  - status: ACCUMULATING
- These are deliberately not judged as pass/fail because the 30-completed-trade floor has not been reached.

### Frozen-confirmation performance improvement
- PR #87 merged as commit 3d74ddbe8be49fd964b532259879e3e6dd769557.
- CI: 324 passed, 2 warnings.
- Confirmation feature snapshots are now materialized only at/after the unseen start index while preserving the identical latest-1000-bar history window for each snapshot.
- Reference smoke run 35791259901 workflow duration: approximately 156 seconds.
- Optimized smoke run 35791585192 workflow duration: approximately 20 seconds.
- MNQ and BTCUSD confirmation outputs were identical between the reference and optimized runs.
- This is an observed workflow-duration reduction of about 87% with no evidence/result change.

### Current research decision
- Same-dataset strategy / MTF / regime / pool tuning remains CLOSED.
- Exact-provider archives are confirmed-bar only.
- Frozen candidates are locked; no retuning is allowed during unseen accumulation.
- Current unseen depth remains insufficient for 15m confirmation.
- No current research result authorizes a 15m competition trade.
- XAUUSD 4h and BTCUSD 1D validated research remain informational only.
- Safe Mode, Kill Switch, manual approval and manual execution remain unchanged.

### Owner data-access gate reached
For immediate deeper history rather than waiting for future TradingView bars:
- CAPITALCOM symbols:
  - the code and secure workflow are ready;
  - repository Actions secrets CAPITAL_API_KEY, CAPITAL_IDENTIFIER and CAPITAL_PASSWORD are now required to execute authenticated Capital.com discovery/backfill;
  - these values must NOT be pasted into chat or committed to the repository.
- CME_MINI:MNQ1!:
  - the connected TradingView MCP cannot page backward beyond its 5000-bar window;
  - immediate older 15m history requires a user-controlled TradingView CSV export with deeper loaded chart history, or authorized CME DataMine historical access/entitlement.
- Without one of those owner-controlled sources, the only exact-provider path is future-bar accumulation.

Owner intervention required now: YES — only for historical-data access, not for strategy decisions or code execution.


## Capital.com secret-visibility blocker — 2026-09-23
- Owner reported that the three Capital.com credentials had been added.
- Discovery branch: capital-backfill/discover-gold-20260923.
- Discovery commit: 2e380caadffdce891d66d58d83802f2da079b91a.
- Workflow run: 35804984405.
- Result: FAILED before any Capital.com network authentication request.
- GitHub Actions environment showed all three required secret-backed variables as empty:
  - CAPITAL_API_KEY
  - CAPITAL_IDENTIFIER
  - CAPITAL_PASSWORD
- The CLI then failed closed with: Missing required environment variable: CAPITAL_API_KEY.
- No credential value was exposed and no external trading/data action occurred.
- Interpretation: the secrets are not available in the repository Actions context under the exact required names. Likely causes include wrong repository, wrong scope, wrong names, environment-only secrets without matching job environment, or values added as variables instead of repository Actions secrets.
- Owner action required: make the three exact names available under this repository's Settings > Secrets and variables > Actions > Repository secrets. Do not paste values into chat.


## Context-locked frozen confirmation checkpoint — 2026-09-23
- Owner clarified that no Capital.com account exists. Capital.com credentials/backfill are therefore parked as an optional future path; no account creation is required for the STC project.
- Exact-provider path remains TradingView Official MCP.
- PR #91 merged to main as 0553d5e0423ee038645183de0598097af539f7f3.
- CI on PR #91: 335 passed, 2 warnings.
- TradingView confirmed-only archives were refreshed:
  - MNQ archive confirmed through t=1790129700; latest mutable tail t=1790130600 withheld.
  - BTCUSD archive confirmed through t=1790130600; latest mutable tail t=1790131500 withheld.
- BTCUSD overlap refresh showed 21 same-provider pre-freeze revisions. Close was unchanged on all 21; changes were primarily volume, with one low+volume revision.
- This exposed a scientific-integrity issue: mutable/revised pre-freeze history could otherwise alter feature warm-up during a supposedly frozen unseen test.
- Frozen confirmation v2 now locks exactly 1000 pre-freeze development bars copied from the original Strategy Lab v2 research-input branches and ending exactly at each freeze timestamp.
- Context source branches:
  - MNQ: research/strategy-v2-xau-mnq-20260922 / research_inputs/mnq/15m.json / run 35781036628.
  - BTCUSD: research/strategy-v2-btc-mcl-20260922 / research_inputs/btcusd/15m.json / run 35781933861.
- Frozen confirmation run 35812474596 completed successfully:
  - MNQ: 25 unseen confirmed bars, 0 completed trades, 1 incomplete open trade, ACCUMULATING.
  - BTCUSD: 46 unseen confirmed bars, 1 completed trade, -0.32121976097584065R, ACCUMULATING.
  - Both: historical_context_locked=true; frozen_context_bars=1000; optimization_locked=true; live_calibration_authority=false.
- The 30-completed-unseen-trade judgment floor remains unchanged.
- Same-dataset tuning remains CLOSED.
- No 15m competition trade is authorized.


## Exact-provider accumulation refresh — 2026-09-23
- PR #93 merged to main as 5e3fb864b03ffe152a2808f2919f30ad469da4c4.
- PR #93 CI: 335 passed, 2 warnings.
- One additional confirmed TradingView Official MCP 15m bar was archived for each active frozen hypothesis; current mutable tails remained withheld.
- Confirmed archive state after merge:
  - MNQ confirmed through t=1790130600; mutable t=1790131500 withheld.
  - BTCUSD confirmed through t=1790131500; mutable t=1790132400 withheld.
- Context-locked frozen confirmation run 35813263594 completed successfully:
  - MNQ: 26 unseen bars, 0 completed trades, 1 incomplete open trade, ACCUMULATING.
  - BTCUSD: 47 unseen bars, 1 completed trade, -0.32121976097584065R, ACCUMULATING.
  - historical_context_locked=true and frozen_context_bars=1000 for both.
  - optimization_locked=true; live_calibration_authority=false.
- No 15m competition trade is authorized.


## Automatic exact-provider accumulation watch — 2026-09-23
- A ChatGPT recurring condition-watch is enabled at hourly frequency for the normal TradingView exact-provider accumulation path.
- Each iteration must read current main before acting.
- It checks CME_MINI:MNQ1! and CAPITALCOM:BTCUSD 15m through TradingView Official MCP.
- If no meaningful newly confirmed evidence exists, it remains silent and makes no unnecessary repository change.
- If newly confirmed evidence exists, it performs the controlled archive -> PR/CI -> frozen confirmation v2 -> state checkpoint workflow.
- Mutable final bars remain withheld.
- Frozen pre-freeze contexts remain immutable.
- Same-dataset retuning remains prohibited.
- No trade authorization or execution is permitted by this watch.
- A user notification is required only for meaningful evidence/status changes or a genuine owner-only blocker.


## Product-priority recovery and live control readback — 2026-09-23
- Project-control drift was identified: NEXT_TASK had incorrectly elevated unseen-data research accumulation into the primary STC objective.
- Correct product hierarchy restored:
  1. Hostinger Owner Console / competition control plane is the primary product.
  2. TradingView feeds, historical research, and frozen confirmation are supporting signal-quality subsystems.
  3. Human approval and manual execution remain mandatory.
- Verified live URL: https://stc.feama.site/operator.php
  - HTTP 200 from Hostinger.
  - The live shell exposes Capital.com Africa, AMP Futures, Portfolio Supervisor, General Lab, and Notification Center.
- Authenticated live readback run: 35813971595.
- Live product state at readback:
  - 26 current signal cards: 10 Capital.com Africa + 16 AMP Futures.
  - Safe Mode=true; Kill Switch=true.
  - Macro calendar connected and healthy.
  - Active opportunities at readback moment: 0.
  - Manual-ready opportunities: 0.
  - Open positions recorded in STC: 0.
  - Capital.com Africa progress: 0/3 qualifying trading days; 0 entries; realized P/L USD 0.
  - AMP Futures progress: 0/5 qualifying trading days; 0 entries; realized P/L USD 0.
  - 35 notification events exist in the durable notification ledger from prior actionable plans.
  - Telegram configured=false; email configured=false; no notification deliveries recorded.
- Root cause of missing Telegram delivery is therefore confirmed: channel credentials are not configured in private Hostinger config.
- Historical position tracking code is present and supports both open-position backfill and already-closed trade import, but no owner competition trades are currently recorded in the live ledger.
- Live examples in notification ledger prove product-side opportunity generation and ticket formatting existed for AMP MCL/ZN/M6A and Capital AUDUSD, including quantity, risk, stop, management checkpoint, and one Final TP.
- The hourly ChatGPT continuation watch was corrected from research-only accumulation to the full STC competition-control workflow. The older research-only daily watch was disabled to prevent duplicate scope drift.
- This recovery patch adds explicit competition-rule summaries to the Owner Console so each competition lane shows the verified competition window, initial balance, first prize, minimum trading days, scoring basis, leverage, commission, monitored production-feed count, and official rules link.


## Urgent competition activation checkpoint — 2026-09-23
- Product priority reconfirmed: competition operation is primary; research is supporting only.
- Live TradingView production transport is healthy:
  - Capital alert 5662088915 active, latest fire 2026-09-23T03:30:00Z.
  - AMP Feed A alert 5664752419 active, latest fire 2026-09-23T03:30:04Z.
  - AMP Feed B alert 5664684004 active, latest fire 2026-09-23T03:30:04Z.
  - observed webhook deliveries HTTP 200.
- Fresh authenticated Hostinger readback run 35814639023 at 2026-09-23T03:31:10Z:
  - 26 current cards: 10 Capital + 16 AMP.
  - 0 active A+ opportunities.
  - 0 manual-ready.
  - 0 tracked open positions.
  - Safe Mode=true; Kill Switch=true.
- Root cause of zero actionable opportunities identified:
  current legacy production alerts do not provide the v1.1 live MTF/family inputs required by the A+ gate. Fresh cards show confirmation_1h, trend_2h, trend_4h, trend_1m, and family evidence unavailable; the gate therefore fails closed.
- Strongest current WATCH-ONLY candidates at readback:
  - CME_MINI:M6E1!: bearish bias, |score| about 0.684.
  - CAPITALCOM:ETHUSD: bullish bias, score about 0.6195.
  - CAPITALCOM:SPX500: bullish bias, score about 0.6165.
  - CAPITALCOM:EURUSD: bearish bias, |score| about 0.5805.
  - CAPITALCOM:BTCUSD: bullish bias, score about 0.5745.
  These are not trade approvals and have no locked plan.
- PR #97 merged as 13be5c766ab2fa19248a02a9827c8e9dbd4793bb:
  - adds Competition Watchlist for strongest blocked candidates;
  - adds MTF LIVE CONFIRMATION OFFLINE warning;
  - adds docs/MTF_PRODUCTION_ACTIVATION.md with exact six-alert activation plan.
  - CI: 336 passed, 2 warnings.
- Live Hostinger operator.php does not auto-deploy from GitHub and still shows the pre-PR #97 shell. Latest operator.php must be uploaded manually.
- TradingView Official MCP cannot create indicator/Pine alerts. Six fresh v1.1 alerts must be created manually from the current Pine scripts before live A+ confirmation can function.
- Browser automation fallback was attempted but could not start because the connected TinyFish wallet is out of funds; no TradingView change occurred.


## Hostinger control-bundle deployment confirmed — 2026-09-23
- Owner updated the current STC control bundle in public_html.
- Visual owner-console evidence shows the new Competition Watchlist and MTF LIVE CONFIRMATION OFFLINE panel.
- Independent live fetch confirms https://stc.feama.site/operator.php exposes the new watchlist section.
- Live bridge status remains healthy and continues ingesting production events.
- TradingView legacy production alerts remain active:
  - 5662088915 Capital 10-symbol 15m.
  - 5664752419 AMP Feed A 8-symbol 15m.
  - 5664684004 AMP Feed B 8-symbol 15m.
- No additional Hostinger file deployment is required before v1.1 MTF alert activation.
- Safe Mode and Kill Switch remain ON.
- Next owner-only activation step is creation of the six v1.1 Pine indicator alerts documented in docs/MTF_PRODUCTION_ACTIVATION.md.


## Live competition UX simplification + first AMP execution issue — 2026-09-23
- Six TradingView v1.1 MTF production alerts are active and accepted at the transport layer; the three legacy alerts were paused to eliminate same-event_id collisions.
- Owner Console no longer reports MTF LIVE CONFIRMATION OFFLINE after the v1.1-only cycle.
- Telegram is configured and a server notification test was received successfully by the owner.
- Manual approval mode is enabled in the live Owner Console:
  - Safe Mode=false.
  - Kill Switch=false.
  - execution remains human-approved and manually entered only.
- First actionable AMP opportunity observed on CBOT:ZN1!:
  - direction SHORT;
  - A_PLUS setup quality shown by the live console;
  - owner manually opened 3 contracts on the competition platform;
  - the trade is not yet recorded in the STC position ledger because the approval attempt was blocked with HTTP 409 after the live price moved outside the locked entry envelope, and the old manual-import UX used fragile chained browser prompts.
- A futures-price usability defect was confirmed:
  - STC displayed Treasury futures plan prices as generic decimals;
  - TradingView uses 32nds / half-32nds style quotations for ZN/ZB;
  - owner needs exact platform-ready price notation plus explicit quantity mode.
- PR #100 merged as ddb017d3c9e5bf8cb46c3c4b41dd358871e4fcba after CI success:
  - 339 automated tests passed.
  - Adds a large simplified EXECUTION TICKET with only symbol, BUY/SELL, order type, entry zone, exact quantity, size mode, stop, final TP, and risk.
  - AMP futures explicitly says Units / Contracts — NOT % balance.
  - Research/MTF/family evidence is collapsed under Advanced details.
  - ZN/ZB prices are displayed/accepted in TradingView-style Treasury notation as well as exact tick-aligned decimals; off-tick ambiguous values such as 105.13 are rejected for ZN.
  - Typed live-price drafts survive the 30-second console refresh.
  - Replaces chained prompt dialogs for existing open positions with one dedicated Record Trade page/form containing all fields at once.
  - Allows an already-filled platform trade to be recorded directly from the signal card even if approval later became blocked.
  - HTTP 409 approval failures now display the actual blocking reason inline.
  - No strategy threshold, risk gate, database schema, secret, or broker execution behavior changed.
- PR #100 is merged in GitHub but operator.php must still be uploaded to Hostinger because the live site does not auto-deploy from GitHub.


## Community indicator adaptive research matrix — 2026-09-23
- Owner requested a scalable CC/STC research layer that studies practical free/community indicators per symbol/timeframe, compares them with native STC strategies by backtest, and derives symbol-specific weights that can evolve only from validated new evidence.
- Owner Console PR #100 deployment is visually confirmed live:
  - Record Trade tab visible.
  - simplified EXECUTION TICKET visible.
  - research details collapsed under Advanced details.
- Design decision:
  - community indicators are benchmarked independently on every compatible competition symbol and timeframe;
  - General Lab symbols use the same engine and do not inherit weights from unrelated symbols;
  - a validated community component may receive more research weight than a native STC strategy when its out-of-sample/forward robust score is higher on the exact same symbol/timeframe;
  - popularity/reviews are discovery and audit metadata only, never direct trading weights;
  - each live outcome may be accumulated, but weights are not changed after every single trade; recalibration requires a frozen evaluation window with enough new evidence to prevent recency chasing/online overfit.
- PR #101 merged as 8779c8ac8f66d1007ce962a5cfde46db65dfe1d2.
- CI: 347 passed, 1 warning.
- New research components:
  - app/community_indicator_catalog.py
  - app/community_indicator_signals.py
  - app/community_indicator_benchmark.py
  - app/community_research_plan.py
  - docs/COMMUNITY_INDICATOR_RESEARCH.md
  - tests/test_community_indicator_lab.py
  - app/research_runner.py now exports community_indicator_trials and community_ensemble_profiles.
- Initial catalog includes:
  - Machine Learning: Lorentzian Classification;
  - UT Bot Alerts;
  - Squeeze Momentum [LazyBear];
  - WaveTrend with Crosses;
  - Hull Suite;
  - QQE MOD;
  - Optimized Trend Tracker;
  - Smart Money Concepts [LuxAlgo];
  - %R Trend Exhaustion discovery family;
  - CM Williams Vix Fix discovery family.
- Causal research adapters are currently implemented for:
  - UT Bot family;
  - Squeeze Momentum family;
  - WaveTrend family;
  - Hull Suite family.
- Pending exact/repaint-safe ports:
  - Lorentzian Classification;
  - QQE MOD;
  - Optimized Trend Tracker.
- LuxAlgo SMC is treated first as a native-proxy/double-counting audit because STC already contains BOS/CHoCH/order-block/FVG/liquidity families.
- community_indicator_live_authority remains false.
- No live A+ threshold, risk rule, competition rule, broker execution, or manual-approval boundary was changed.


## Adaptive research master checkpoint — 2026-09-23 23:15 EEST
- Controlling owner correction: project name is STC.
- A durable authoritative research ledger has been added at docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md so a new chat/agent can continue without reconstructing the strategy plan from conversation history.
- PR #102 merged as f47bb7e3a630915de264dcabcde31988fa8eb7de.
  - CI: 351 passed, 1 warning.
  - Community catalog expanded substantially.
  - New causal adapters: SuperTrend, Chandelier Exit, Schaff Trend Cycle, Range Filter.
  - Train-only bounded parameter tuning is frozen before test/forward.
- Exact-provider community 15m benchmark completed on all 26 competition symbols on research/community-15m-pilot-20260923:
  - 5,000 TradingView bars per symbol.
  - 8 implemented community families per symbol.
  - 208 symbol-indicator trials.
  - 8/26 symbols produced at least one fully validated community trial.
  - Cross-symbol pass counts: Range Filter 4, UT Bot 3, Schaff Trend Cycle 3, Chandelier Exit 2, WaveTrend 2, SuperTrend 1, Squeeze Momentum 1, Hull Suite 0.
  - This is research evidence only; no live A+ weight was changed.
- Native-vs-community exact-data benchmark is now the active work unit on branch research/native-community-15m-20260923.
- General Lab controlling requirement is explicit: every newly added Lab symbol must automatically run the same asset classification -> native matrix -> community matrix -> OOS/forward comparison -> symbol/timeframe weight profile process. It inherits process, never weights.
- Weight-learning rule is explicit: every live outcome may be stored, but recalibration is batch/window based and frozen; never change weight after one isolated trade.


## Adaptive research progress update — 2026-09-23 23:35 EEST
- PR #103 merged: General Lab research routing endpoints, discovery wave 2, AlphaTrend + OTT causal adapters, redundancy-aware family weighting.
- PR #104 merged: first 26-symbol exact-provider 15m community benchmark evidence archived in main.
- PR #105 merged: QQE MOD, SSL Hybrid baseline adapter, Waddah Attar Explosion, and QQE+SSL+WAE composite research adapters.
- PR #105 CI: 359 passed, 1 warning.
- Implemented community research pool is now 14 components before native strategy comparison.
- Controlling native-vs-community benchmark is GitHub Actions run #5 on branch research/native-community-15m-20260923; older benchmark runs are superseded/cancelled.
- General Lab rule is now both documented and exposed through API: new Lab symbols use the same research process and never inherit weights from another symbol.
- Live competition authority remains unchanged: human approval/manual execution only; community_indicator_live_authority=false.


## Frozen holdout repair checkpoint — 2026-09-24 00:00 EEST
- PR #107 failed CI because its test expected an exact 85/15 split on only 2,000 bars while the implementation silently expanded the holdout to a 500-bar minimum, producing 1,500/500 instead of 1,700/300.
- Method decision: the requested frozen percentage must remain exact. STC must never silently change an 85/15 research split to satisfy a sample floor.
- PR #107 was closed unmerged and explicitly superseded.
- PR #108 created from latest main:
  - branch feature/frozen-confirmation-v2-20260923;
  - exact 85/15 split is preserved;
  - if the 15% frozen segment is below the minimum sample floor, research fails closed and asks for more history;
  - test history increased so the invariance test has a valid >=500-bar unseen holdout;
  - live_authority remains false.
- PR #108 CI run #374 is currently in progress.


## Frozen confirmation execution checkpoint — 2026-09-24 00:05 EEST
- PR #108 merged as 71d338dc34ec3804b042811c66d98aa7f4b1d89f.
- PR #108 CI run #374 passed.
- Exact frozen methodology is now in main:
  - 85% development;
  - 15% untouched final holdout;
  - insufficient holdout sample fails closed instead of silently resizing the split;
  - frozen pass creates research promotion candidate only;
  - live_authority=false.
- Research execution branch created: research/community-frozen-15m-20260924.
- It reuses the 26 exact-provider 5,000-bar 15m datasets from the completed native-community benchmark and includes the merged frozen-confirmation code.
- GitHub Actions frozen-confirmation run id 35919916518 started for all 26 symbols.
