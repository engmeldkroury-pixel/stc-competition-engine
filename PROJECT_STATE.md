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
