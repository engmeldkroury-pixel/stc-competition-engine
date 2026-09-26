# STC Full System Review — 2026-09-26

Status: ACTIVE DEVELOPMENT / PRODUCTION DEPLOYMENT BLOCKED ON ONE SSH-SECRET CORRECTION  
Repository: engmeldkroury-pixel/stc-competition-engine  
Default branch: main  
Execution boundary: manual approval and manual order entry only; no broker auto-execution.

## 1. Executive state

STC is no longer a simple signal script. It is a multi-layer competition decision-support system with:
- TradingView/Pine market-event ingestion;
- Hostinger/MySQL persistent bridge and owner console;
- GitHub Actions processing, CI, readback and release packaging;
- Capital.com Africa and AMP Futures competition profiles;
- multi-timeframe/family evidence;
- competition-specific quality gating;
- manual approval/risk controls;
- position ledger and portfolio supervision;
- Telegram notification delivery;
- research/shadow strategy evaluation separated from live authority.

Current main implements both Capital and AMP in competition mode with a shared 84/100 competition-opportunity floor. The deployed Hostinger runtime was proven stale before the current deployment work and still exposed older AMP 90/100 behavior.

A new SSH-key deployment workflow was added so approved Hostinger files can be deployed from GitHub without manual ZIP/file-manager replacement. The first two deployment attempts failed safely before any production file replacement:
1. first failure: OpenSSH private key could not be parsed by libcrypto;
2. hardened retry identified the precise cause: HOSTINGER_SSH_PRIVATE_KEY is not a private OpenSSH key.

No production Hostinger file was changed by either failed attempt.

## 2. New deployment architecture

New workflow:
- .github/workflows/stc-hostinger-deploy.yml

Current approved deploy set:
- approval.php
- cloud_control.php
- notification_control.php
- operator.php
- operator_snapshot.php
- portfolio_control.php
- position.php

Deployment design:
1. checkout current main;
2. PHP syntax-check all seven files;
3. build a checksum manifest and release archive;
4. load the dedicated Hostinger SSH private key from GitHub Actions Secrets;
5. validate that the secret is a real OpenSSH private key without printing it;
6. connect to Hostinger SSH on port 65002;
7. upload to a staging archive;
8. back up the existing seven production files;
9. replace only those seven files;
10. verify SHA-256 byte parity after deployment;
11. retain the server-side pre-deployment backup for rollback.

Explicitly excluded:
- config.php;
- database credentials;
- SQL migrations;
- automatic broker/order execution.

Hostinger target:
- /home/u317452451/domains/stc.feama.site/public_html

Security model:
- public repository contains only secret NAMES, never secret VALUES;
- Hostinger has a dedicated public SSH key;
- the private SSH key belongs only in GitHub Actions Secrets;
- old reusable-password deployment is superseded and should be removed after SSH deployment succeeds.

## 3. Current deployment blocker

Workflow run 36264123000 failed in the private-key validation step with the sanitized error:
HOSTINGER_SSH_PRIVATE_KEY is not the private OpenSSH key.

Required correction:
- replace that GitHub Secret with the entire contents of the local file named stc_hostinger_deploy;
- do NOT use stc_hostinger_deploy.pub;
- expected first line:
  -----BEGIN OPENSSH PRIVATE KEY-----
- expected last line:
  -----END OPENSSH PRIVATE KEY-----

After correction, re-trigger the Hostinger deploy workflow. No password needs to be shared in chat.

## 4. Current live strategy policy in main

The current event decision path treats:
- capital-africa-sep-2026;
- amp-futures-sep-2026

as competition-mode profiles.

Competition opportunity gate:
- setup quality floor: 84/100;
- base recommendation must be LONG or SHORT;
- historical context must exist;
- 1h/2h/4h intraday evidence requires majority alignment;
- short-term strength must be directional;
- blended technical and composite score must remain directional;
- higher-timeframe context must not be strongly opposed;
- family evidence must be present;
- family agreement/breadth/conflict limits remain enforced;
- volatility/liquidity cannot be poor;
- manual approval remains mandatory.

Outside competition mode, the stricter A+ high-conviction path retains a 90/100 quality floor.

Important semantic finding:
app/competition_strategy.py still returns A_PLUS_ONLY in its pace/advisory object even though the live event decision policy is now competition-opportunity 84 for both competitions. This appears to be stale semantic debt rather than the live gate itself, but it should be reconciled so dashboards/agents do not receive contradictory policy labels.

## 5. Why earlier production problems happened

### 5.1 Deployment drift
Python/main and packaged PHP advanced faster than the active Hostinger root files. Manual ZIP/file-manager deployment allowed older PHP to remain live even after main was correct.

Correction:
- reproducible seven-file package;
- permanent Live Readback;
- new SSH deployment workflow with checksum readback.

### 5.2 Capital/AMP policy drift
Older Hostinger PHP accepted competition-grade behavior differently and AMP remained on the older high-conviction 90 runtime.

Correction in main:
- symmetric Capital + AMP COMPETITION_OPPORTUNITY eligibility;
- shared 84 quality floor;
- dual-competition gate-supply audit.

### 5.3 Locked plan disappeared after a later monitoring bar
A valid plan could be replaced in the owner view by a newer monitor-only signal before the manual trade lifecycle was completed.

Correction:
- preserve unexpired locked plans;
- separate latest context from recovery/active plan state;
- prevent duplicate entry.

### 5.4 Record Trade target mismatch
Blank competition_id and bare symbols such as EURUSD did not match canonical CAPITALCOM:EURUSD targets.

Correction:
- strict competition selector;
- client/server canonical symbol normalization;
- unique safe inference only where unambiguous;
- AMP remains fail-closed.

### 5.5 Record Trade open-time rejection
Browser/local time could cause an existing real platform position to be rejected as outside the competition window.

Correction:
- server-time fallback;
- small clock-skew tolerance;
- genuinely invalid future/pre-window times still fail closed.

### 5.6 Oversizing and duplicate discretionary entries
Observed manual fills did not always match STC proposed quantities. XAGUSD and SPX500 evidence showed materially larger actual exposure and rapid re-entry after losses.

Correction:
- approval-time MAX STC QUANTITY;
- reject oversized STC-plan fill recording;
- duplicate-open-symbol block;
- same-symbol/same-direction post-loss cooldown;
- quantity must be STC proposed quantity or smaller valid quantity.

### 5.7 Stale STC position ledger
The platform later showed only one real NAS100 open position while STC still reported multiple stale opens and the wrong NAS100 quantity/entry.

Correction available:
- VOID/reconciliation support;
- platform evidence is controlling until STC ledger is reconciled;
- portfolio-management advice must not be trusted against a stale ledger.

### 5.8 Profit giveback
NAS100 and SPX500 reached material positive R but the prior supervisor protected too little unrealized profit.

Correction:
- closed-bar high-water R;
- progressive locked-profit floor;
- EXIT_NOW when current R falls below an already-earned floor;
- execution remains manual.

### 5.9 Opportunity concentration
All 10 Capital symbols were scanned, but actionable NEW_LOCKED_PLAN notifications were concentrated mainly in:
- SPX500;
- NAS100;
- BTCUSD;
- ETHUSD.

This is not an ingestion/coverage defect. It is a generic-strategy opportunity-source concentration problem.

Correction direction:
- symbol-specific validated research components;
- exact Pine/Python causal parity;
- shadow outcome collection;
- promotion only after non-redundant forward evidence.

### 5.10 Research CI infrastructure interruption
Several benchmark runs returned steps=null before checkout/setup began. This was recorded as external GitHub Actions runner/account/quota blockage, not a strategy test failure.

## 6. Research and strategy evidence accumulated

Important accepted findings:
- no universal community composite has been accepted;
- QQE + SSL + WAE composite: 0/26 validated in the benchmark and not promoted;
- native 15m strategy families were 0/26 under the strict robustness gates in the referenced exact-provider benchmark;
- community evidence improved symbol-specific profile coverage;
- Lorentzian Classification is pinned to an official third-party port and remains research-only;
- corrected Lorentzian partial authoritative result: 2/17 validated in the completed portion;
- VuManChu corrected diagnostic result: 0/26 validated;
- HalfTrend, Trendilo, SSL Hybrid, Range Filter, Schaff and other components are retained only where exact symbol/timeframe evidence supports them;
- adaptive shadow reweighting is capped, sealed-batch only, minimum-sample controlled and cannot grant live authority automatically.

Capital priority shadow profiles identified in project history:
- DOGEUSD: Range Filter + Schaff;
- EURUSD: Trendilo;
- ETHUSD: SSL Hybrid;
- NAS100: HalfTrend;
- then BTCUSD and USDZAR.

AMP exact-provider Wave-3 profile-ready core symbols:
- MCL;
- MNG;
- MGC;
- MJY;
- MET;
- ZN;
- ZB.

These remain shadow/research-only until exact causal Pine payload parity and forward shadow evidence are complete.

## 7. Strategy weaknesses still worth improving

### A. Policy centralization
The live 84 policy is hard-coded in event_decision while competition_strategy still advertises A_PLUS_ONLY. Create one authoritative competition-policy contract and regression tests so Python, PHP, console and documentation cannot drift.

### B. Per-symbol strategy routing
The current generic core is strong at filtering but naturally concentrates on symbols whose market structure, volume proxy and multi-timeframe factors fit the generic scoring model. Add a research-only router that chooses validated symbol/timeframe components rather than applying one universal indicator mix.

### C. Gate-failure attribution
Persist per-symbol counts for each blocking reason:
- intraday majority;
- short-term strength;
- family agreement/breadth/conflicts;
- volatility;
- liquidity;
- quality score;
- higher-timeframe opposition.

This distinguishes a truly weak market from a model that structurally starves one symbol.

### D. Outcome attribution
Every completed competition trade should be tied to:
- source event/signal;
- quality score;
- gate failures/pass;
- proposed quantity vs actual quantity;
- entry deviation;
- stop deviation;
- MFE/MAE;
- realized R/P&L;
- management actions.

Without this, strategy and execution errors are mixed together.

### E. Exact parity before promotion
For every symbol-specific community component:
1. exact TradingView/Pine implementation;
2. causal no-lookahead timing proof;
3. bar-by-bar Python/Pine payload parity;
4. sealed shadow sample;
5. forward outcome evidence;
6. redundancy check;
7. explicit owner promotion decision.

### F. Competition objective
Do not optimize for trade count. Optimize for validated positive realized-P/L opportunity flow while controlling drawdown and execution mistakes. A higher number of weak trades is not a strategy improvement.

## 8. Highest-priority execution sequence

1. Correct HOSTINGER_SSH_PRIVATE_KEY.
2. Run secure seven-file Hostinger deployment.
3. Require checksum verification success.
4. Run permanent Live Readback.
5. Confirm deployed dual-competition gate audit is structured rather than empty.
6. Confirm fresh AMP signals show competition_mode=true and quality_floor=84; historical stored rows are not expected to mutate.
7. Confirm notification eligibility parity.
8. Reconcile STC open-position ledger to the actual competition platform.
9. Only after ledger parity, trust portfolio/high-water management.
10. Continue symbol-specific Pine/Python parity and shadow collection.
11. Centralize competition policy to remove A_PLUS_ONLY/84 semantic drift.
12. Build trade-level attribution and gate-failure analytics before changing live weights.

## 9. Questions for an external AI reviewer

Ask an independent AI reviewer to focus on:
1. Is the 84 competition-opportunity gate internally coherent, or does it double-count correlated evidence?
2. Are family breadth/agreement thresholds likely to structurally bias the system toward indices versus FX/metals/futures?
3. Should execution-quality factors be asset-class normalized rather than using one common relative-volume/range mapping?
4. Is the current multi-timeframe majority logic robust to missing/timezone/session-specific futures data?
5. Is 84 best treated as a fixed threshold, or should the research layer estimate symbol-specific thresholds subject to strict out-of-sample constraints?
6. How should trade-level MFE/MAE and actual-vs-proposed execution be incorporated without contaminating signal-quality assessment?
7. Which symbol-specific community components are genuinely additive after redundancy control?
8. Does the progressive high-water exit rule over-protect normal trend continuation, and what forward test should decide that?
9. Which policy fields should be centralized into one contract to eliminate Python/PHP/UI drift?
10. What additional fail-closed tests should be added before any strategy component receives live authority?

## 10. Non-negotiable boundaries

- No automatic broker execution.
- No secret values in repository or chat.
- No cross-provider market-data substitution.
- Setup quality is not win probability.
- Do not increase risk to recover losses or chase leaderboard rank.
- Do not promote research/shadow evidence directly into live authority.
- Platform account evidence overrides stale STC ledger state until reconciliation.
- Failed/not-run tests remain recorded as failed/not-run, never silently treated as passed.
