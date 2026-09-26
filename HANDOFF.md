# STC HANDOFF

HANDOFF_STATUS: ACTIVE_DEPLOYMENT_BLOCKED_ON_ONE_OWNER_SECRET_CORRECTION  
FROM_EXECUTOR: ChatGPT / STC project control  
TO_EXECUTOR_OR_REVIEWER: Next STC chat / Mohamed / independent AI reviewer  
TASK_OR_BATCH_ID: STC-20260926-SECURE-DEPLOY-STRATEGY-REVIEW  
REPOSITORY: engmeldkroury-pixel/stc-competition-engine  
DEFAULT_BRANCH: main  
REPORTING_DATE: 2026-09-26

## Controlling boundaries
- No automatic broker execution.
- Human approval and manual competition order entry remain mandatory.
- No secret values in repo/chat.
- No silent provider substitution.
- Setup quality is not win probability.
- Platform account evidence overrides stale STC ledger state until reconciliation.
- Research/shadow evidence cannot gain live authority without parity, forward evidence and explicit promotion.

## Current main policy
- Capital.com Africa: competition mode.
- AMP Futures: competition mode.
- Shared competition-opportunity setup-quality floor: 84/100.
- Higher-timeframe non-opposition, family evidence, liquidity/volatility quality and existing risk controls remain enforced.
- Hostinger current-main eligibility accepts COMPETITION_OPPORTUNITY for both competitions.

## Production deployment state
A secure SSH-key deployment channel now exists:
- workflow: `.github/workflows/stc-hostinger-deploy.yml`;
- approved deploy scope: seven PHP files only;
- PHP lint before upload;
- server-side backup;
- SHA-256 post-deploy verification;
- no config.php;
- no SQL migration.

Approved files:
1. approval.php
2. cloud_control.php
3. notification_control.php
4. operator.php
5. operator_snapshot.php
6. portfolio_control.php
7. position.php

Hostinger target:
`/home/u317452451/domains/stc.feama.site/public_html`

## Current blocker
Two deployment attempts failed safely before any production replacement:
- run 36264035149: private key parse/libcrypto failure;
- run 36264123000: hardened validation proved `HOSTINGER_SSH_PRIVATE_KEY` is not the private OpenSSH key.

Required owner action:
- replace only GitHub Secret `HOSTINGER_SSH_PRIVATE_KEY` with the COMPLETE contents of local file `stc_hostinger_deploy` (without `.pub`);
- it must begin with `-----BEGIN OPENSSH PRIVATE KEY-----` and end with `-----END OPENSSH PRIVATE KEY-----`;
- do not paste the key in chat.

No Hostinger production file was replaced by the failed runs.

## After owner correction
1. retrigger STC Hostinger Deploy;
2. require seven-file checksum verification;
3. run permanent Live Readback;
4. require structured dual-competition gate audit;
5. require fresh AMP signal evidence with `competition_mode=true` and `quality_floor=84`;
6. verify notification parity and high-water fields;
7. reconcile STC open-position ledger to the actual competition platform before trusting portfolio-management output.

## Strategy/research state
- All 10 Capital symbols are scanned; opportunity concentration is not a scan-coverage defect.
- Current actionable notification history is concentrated mainly in SPX500, NAS100, BTCUSD and ETHUSD.
- Symbol-specific research/shadow direction:
  - DOGEUSD: Range Filter + Schaff;
  - EURUSD: Trendilo;
  - ETHUSD: SSL Hybrid;
  - NAS100: HalfTrend;
  - then BTCUSD and USDZAR.
- AMP exact-provider Wave-3 profile-ready core symbols:
  - MCL, MNG, MGC, MJY, MET, ZN, ZB.
- These remain research/shadow-only until exact causal Pine/Python parity and forward shadow evidence are complete.
- No universal community composite is accepted.
- QQE+SSL+WAE composite remains rejected from promotion.
- Lorentzian corrected benchmark is only partially authoritative (2/17 completed subset); VuManChu diagnostic result is 0/26.
- Adaptive shadow recalibration is sealed-batch/minimum-sample/capped and cannot self-promote live weights.

## Current strategy consistency debt
- `app/event_decision.py` is the controlling live gate and uses shared 84 for Capital + AMP.
- `app/competition_strategy.py` still exposes advisory `A_PLUS_ONLY` pace semantics.
- Treat this as semantic/policy drift risk, not as evidence of a live 90 floor.
- Next code-quality task after deployment/account reconciliation: centralize competition policy and add regression tests across advisory/live/Hostinger contracts.

## Historical incidents already corrected in code
- stale Hostinger eligibility vs current main;
- locked-plan disappearance after a newer monitor-only bar;
- Record Trade blank competition/bare-symbol target mismatch;
- Record Trade browser-time/open-time rejection;
- oversize fill recording and duplicate/same-direction re-entry;
- weak profit protection after large MFE;
- notification/server-console parity.

## Still unresolved operational issue
STC position ledger was proven stale versus the competition platform. Do not treat portfolio supervision as authoritative until positions/quantities/entry/stop/TP are reconciled.

## Durable review
Full architecture + incident + strategy review:
`docs/STC_FULL_SYSTEM_REVIEW_2026-09-26.md`

Project history/evidence:
- `PROJECT_STATE.md`
- `NEXT_TASK.md`
- `DECISIONS.md`
- `BATCH_REGISTER.csv`
- `TEST_REGISTER.csv`
- `RISK_REGISTER.csv`
- `docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md`

## One next executable action
Correct `HOSTINGER_SSH_PRIVATE_KEY`; then rerun secure Hostinger deployment and Live Readback. No other owner action is required before that.

## Latest strategy correctness additions
- Policy centralization: `81415fbcafd64e3202fbf7150a1c21e1bfe807c0`.
- Gate-failure attribution: `d0089bb99d9da9938f711e1d744ea9d9c1351aef`.
- Missing-evidence SHORT asymmetry fix: `760796b58f0d763ea54b9fc452a8cd8aba119a49`.
- Corrected-code critical CI: 191 passed, 1 warning.
- Independent reviewer prompt: `docs/EXTERNAL_AI_REVIEW_PROMPT_2026-09-26.md`.

Important correctness fix:
A missing optional score previously used raw `-1.0` before direction-sign multiplication; on SHORT this could become `+1.0` and inflate setup quality. Missing evidence is now direction-symmetric and fail-closed.

The only owner blocker before automated Hostinger deployment is correcting `HOSTINGER_SSH_PRIVATE_KEY` with the private file (no `.pub`).

