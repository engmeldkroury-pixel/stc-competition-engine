# STC HANDOFF

HANDOFF_STATUS: ACTIVE_BLOCKED_ON_OWNER_HOSTINGER_UPLOAD  
FROM_EXECUTOR: CODEX-0  
TO_EXECUTOR_OR_REVIEWER: Next STC chat / Mohamed  
TASK_OR_BATCH_ID: STC-20260924-CAPITAL-LIVE-HOTFIX  
REPOSITORY: engmeldkroury-pixel/stc-competition-engine  
CURRENT_MAIN_AFTER_ACCEPTED_SOURCE_WORK: includes PR #145, #146, #148, #149 and #150.

## Completed work
- Capital competition gate is live in Python/main.
- Production processing has accepted live Capital events.
- Live readback proved EURUSD SHORT / COMPETITION_OPPORTUNITY / quality 80.
- Deployed Hostinger PHP is stale and rejects/hides that grade.
- Six-file Hostinger hotfix bundle is built and SHA-256 recorded.
- Community corrected 26-symbol research is archived.
- Research-only community shadow plumbing is merged.
- Six-symbol Python parity reference run completed.

## Current external blocker
Mohamed must replace six PHP files on the existing Hostinger STC `public_html` deployment:
`approval.php`, `cloud_control.php`, `notification_control.php`, `operator.php`, `operator_snapshot.php`, `portfolio_control.php`.

No SQL and no config change are required.

## After upload
1. Update `ops/LIVE_READBACK_TRIGGER`.
2. Read `STC Live Readback` logs.
3. Require a fresh Capital COMPETITION_OPPORTUNITY to show deployed `quality_gate_passed=true`.
4. Confirm a locked plan is exposed while valid.
5. Confirm Telegram NEW_LOCKED_PLAN delivery.
6. Only then show Mohamed the manual competition order ticket.

## Parallel research continuation
Implement Pine streams against `research_benchmarks/community_pine_parity_manifest_20260924.json`.
Do not promote community weights before exact parity evidence.

## Protected scope
- no automatic broker execution;
- no secrets in repo/chat;
- no silent provider substitution;
- no setup-quality-as-win-probability claim;
- no weight promotion without parity and separate acceptance.


## Pine candidate status
- PR #152 merged as `529f8efc3fa9bce06de16236dd8275cd6fb42c25`.
- Diagnostic file: `tradingview/STC_COMMUNITY_SHADOW_PARITY_CANDIDATE.pine`.
- Critical CI passed.
- TradingView compile and exact event parity remain pending and are required before production-feed integration.
