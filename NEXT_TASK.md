# NEXT TASK

Updated: 2026-09-24 19:05 UTC

## CONTROLLING PROJECT
STC.

## CURRENT CAPITAL PERFORMANCE STATE

Owner-platform evidence now fully reconciles the visible realized loss:
- account balance: USD 97,938.28;
- equity: USD 98,372.77;
- realized P/L: USD -2,061.72;
- unrealized P/L at screenshot: USD +434.50;
- trading days: 3/3;
- open positions shown: 2.

Visible closed losses:
- SPX500 LONG 20: USD -316.79;
- XAGUSD SHORT 3.73K: USD -1,362.81;
- ETHUSD LONG 9.02: USD -172.80;
- BTCUSD LONG 0.22: USD -92.72;
- BTCUSD LONG 0.23: USD -70.78.

Closed losses total USD -2,015.90.
Visible entry/transaction charges on the two still-open positions are USD -15.64 EURUSD and USD -30.17 SPX500, totaling USD -45.81.
Combined visible amount USD -2,061.71 matches platform realized P/L within USD 0.01 rounding.

## IMMEDIATE OPEN-RISK PRIORITY

SPX500 has an open LONG:
- actual quantity: 39.2;
- actual entry: 7697.1 at 18:05 UTC;
- closest prior STC plan: 18:00:24 UTC;
- STC proposed quantity: 19.683465;
- STC entry zone: 7691.7006 to 7707.0994;
- STC stop: 7675.5378488959;
- STC final target: 7759.0553777602;
- setup quality: 82/100;
- score: +0.66.

The entry location was inside the STC zone, but the actual quantity is approximately 1.99x the STC sizing ticket.
Current actual stop for the open 39.2-unit SPX500 position is NOT evidenced and must not be guessed.

Immediate rule:
1. Do not add to SPX500.
2. Obtain current Positions/Orders evidence showing the actual active SPX500 stop and TP.
3. Reconcile this open position into STC.
4. Only then issue a position-management recommendation.

## SPX500 CLOSED-LOSS ATTRIBUTION

The prior SPX500 loss:
- LONG 20 units;
- entry 7705.1 at 17:21 UTC;
- exit 7690.8 at 17:45 UTC;
- net P/L USD -316.79.

Closest STC plan at 17:15:25 UTC:
- BUY MARKET at notification time;
- entry zone 7706.6856 to 7722.1144;
- stop 7690.9440665317;
- target 7773.0398336707;
- quantity 20.000949;
- quality 81/100;
- score +0.58;
- family agreement 100%, aligned 7/9.

The platform size matched STC and the exit was effectively the locked stop. This is strong evidence of a real strategy stop-out under approximately correct risk sizing.

The next SPX500 entry occurred about 20 minutes later at roughly 2x the new STC quantity. PR #161's 30-minute same-symbol/same-direction loss cooldown plus MAX-quantity enforcement would have blocked this execution pattern if already deployed.

## EXECUTION-GUARDRAIL STATUS

PR #161 merged:
- merge commit: 99b9241485e702ac97e2d3ac653f62b6243ad5a4;
- PR CI run: 36033893798 SUCCESS.

Guardrails:
- server-authoritative approval-time MAX STC QUANTITY;
- reject oversized STC-plan fill records;
- block new approval if same symbol already has an open position;
- same-symbol/same-direction loss cooldown;
- explicit Units/Contracts-only instructions;
- manual execution remains mandatory.

Latest Hostinger seven-file bundle:
- workflow run: 36036915549;
- artifact id: 10825132595;
- artifact digest: sha256:e142e05571405c329b1db0e422a069d9a1be882c514564f049c850015db2c6c4.

Production deployment is still pending owner upload.

## STRATEGY-QUALITY WORK

Do NOT react to the losing streak by blindly raising quality thresholds, increasing risk, or promoting shadow community indicators.

Required evidence-driven sequence:
1. Backfill/reconcile all five visible closed trades plus the two open positions into STC.
2. Attribute each trade to its exact source plan/signal where evidence exists.
3. Separate:
   - directional-signal failure;
   - stop-placement failure;
   - stale/manual execution deviation;
   - quantity/risk deviation;
   - rapid same-thesis reentry.
4. Run no-lookahead stop/entry sensitivity research before changing LIVE_PLAN_STOP_ATR_MULTIPLE=1.20.
5. Compare candidate live-weight/gate changes out of sample; no live weight promotion without evidence.
6. Community indicators remain shadow-only until parity and measured incremental value are proven.

## LIVE BOUNDARY
- no automatic broker/order execution;
- human approval/manual entry only;
- do not exceed STC MAX quantity;
- do not widen stops ad hoc;
- do not add to an already-open symbol;
- do not increase risk to recover losses;
- setup quality is not a win probability.

## 2026-09-25 — Current next task update

Owner objective:
- future competitions are judged by results, not by indicator complexity;
- avoid both extremes: weak high-frequency entries and an over-tight gate that produces no progress.

Current actions:
1. PR #166 merged: Telegram/server notification history and owner-console signal context parity restored in main.
2. PR #167 moved to DRAFT: 90/100 strict-only Capital gating is not final until opportunity starvation is measured.
3. PR #168 adds a research-only audit over the recent stored Capital signal rows. It compares quality counts >=78, >=84 and >=90, plus strict-A+ and balanced-competition MTF/family proxies.
4. After PR #168 passes CI and is deployed, run Live Readback and use the measured supply to choose the competition gate. No guess-based threshold change.
5. Facebook links remain unreadable through public fetch because Facebook blocks the current fetchers. Opera Browser Connector is the preferred authenticated-browser path once connected; screenshots remain a zero-cost fallback.

Competition design principle:
- maximize validated opportunity flow, not raw trade count;
- quality gate + opportunity supply + smaller risk on secondary-tier setups;
- no automatic execution; human approval remains mandatory.

## 2026-09-25 — NAS100 profit-protection correction

New platform evidence supersedes the previous open-position state:
- actual platform open positions: 1;
- actual position: NAS100 LONG 7.7 @ 30,416.1;
- active TP: 30,758.6;
- active SL: 30,319.1;
- realized P/L: approximately USD -3,394.31.

Live STC readback is not authoritative for account state because it still reports four OPEN positions and tracks NAS100 with the wrong quantity/entry.

Priority sequence:
1. Do not use STC portfolio supervision as authoritative until the open-position ledger is reconciled to the platform.
2. Deploy the already-merged VOID/reconciliation support and latest operator/notification parity files to Hostinger.
3. Void stale EURUSD/XAGUSD/SPX500 manual_external OPEN records after confirming they are not open on the platform.
4. Replace the incorrect NAS100 ledger row with the actual 7.7 @ 30,416.1 position and current platform stop/target.
5. Complete and test PR for closed-bar high-water profit protection.
6. Rebuild one Hostinger bundle after CI passes.
7. Re-run live readback and require exact agreement between platform and STC open-position count/quantity before trusting management alerts.

The NAS100 incident confirms that competition management must protect MFE, not only original stop risk.

## 2026-09-26 — Deployment-ready update

Latest production-ready hotfix:
- PR #169 merged successfully;
- full CI: SUCCESS;
- competition-critical CI: SUCCESS;
- Hostinger bundle run: 36225098256 — SUCCESS;
- artifact id: 10900587381;
- package contains seven PHP files only;
- no SQL migration;
- no config.php or credential changes.

Owner deployment action:
1. upload/replace the seven PHP files in the existing STC public_html directory;
2. do not upload config.php;
3. after upload, run Live Readback;
4. reconcile STC OPEN positions to the competition platform before trusting position-management alerts;
5. verify Telegram/server notification parity and high-water management fields.

## 2026-09-26 — Opportunity concentration correction

Live audit confirms all 10 Capital symbols are being scanned, but NEW_LOCKED_PLAN events are concentrated in only four symbols:
SPX500, NAS100, BTCUSD and ETHUSD.

Immediate engineering objective:
1. keep all 10 symbols in the production scan;
2. expose symbol-coverage status so the owner can see SCANNED / WAIT / BLOCKED / ACTIVE for every symbol;
3. carry exact symbol-specific validated community component states into the live shadow payload for profile-ready symbols;
4. start with DOGEUSD (Range Filter + Schaff), EURUSD (Trendilo), ETHUSD (SSL Hybrid), NAS100 (HalfTrend), then BTCUSD and USDZAR;
5. do not grant live authority merely to increase trade count;
6. promote only non-redundant component evidence that passes live/Pine parity and forward shadow checks.

Latest live evidence also shows no current ACTIVE opportunity; NAS100 latest directional setup was quality 84 but blocked by liquidity quality.

## 2026-09-26 — Current deployment blocker and next verification

Engineering work completed before owner intervention:
1. Both competitions use competition-opportunity mode in current main.
2. Shared competition quality floor is 84/100, with higher-timeframe non-opposition and existing risk/manual-approval controls.
3. Hostinger notification eligibility accepts COMPETITION_OPPORTUNITY for both Capital and AMP.
4. Closed-bar high-water profit protection remains included.
5. Telegram/server-to-console parity remains included.
6. Dual-competition supply diagnostics are included.
7. AMP exact research profiles for MCL/MNG/MGC/MJY/MET/ZN/ZB are merged as shadow evidence only.

Blocking production fact:
- Hostinger is still running the older AMP high-conviction 90/100 runtime.
- The next required owner action is upload/replace the seven PHP files from STC_DUAL_COMPETITION_HOTFIX_20260926.zip in the existing STC public_html directory.
- Do not upload or change config.php. No SQL migration is required.

Immediately after owner reports upload complete:
1. run Live Readback;
2. require AMP competition_mode=true and quality_floor=84;
3. require notification eligibility parity for both competitions;
4. verify high-water portfolio fields;
5. reconcile stale Capital open-position ledger against the actual competition platform;
6. continue exact Pine/Python parity work for symbol-specific community component signals before any live promotion.

## 2026-09-26 — Secure deployment handoff replaces manual Hostinger upload

A dedicated SSH-key deployment workflow now exists:
- workflow: `.github/workflows/stc-hostinger-deploy.yml`;
- approved scope: seven PHP files only;
- target: existing STC public_html;
- PHP lint, server-side backup and SHA-256 post-deploy verification are mandatory;
- `config.php`, SQL and secrets are excluded.

Deployment evidence:
- run `36264035149`: failed safely before production replacement because the configured private key could not be parsed;
- workflow hardened in `8f26c50474084f30b4938dee693567eea3717a9b`;
- run `36264123000`: failed safely in pre-upload validation with explicit diagnosis that `HOSTINGER_SSH_PRIVATE_KEY` is not the private OpenSSH key;
- no production replacement occurred in either run.

Single owner intervention required:
1. Edit GitHub Actions repository secret `HOSTINGER_SSH_PRIVATE_KEY`.
2. Replace its value with the complete contents of local file `stc_hostinger_deploy` (the file WITHOUT `.pub`).
3. The value must start with `-----BEGIN OPENSSH PRIVATE KEY-----` and end with `-----END OPENSSH PRIVATE KEY-----`.
4. Do not expose the key in chat.

After the secret is corrected, continue without manual Hostinger file upload:
1. retrigger secure Hostinger deploy;
2. require checksum verification;
3. run Live Readback;
4. verify fresh dual-competition 84 policy evidence;
5. reconcile platform/STC open positions;
6. continue symbol-specific strategy parity/shadow work.

Full cross-chat/external-AI checkpoint:
- `docs/STC_FULL_SYSTEM_REVIEW_2026-09-26.md`.

Additional strategy consistency issue to repair after deployment/reconciliation:
- live `event_decision.py` uses shared competition-opportunity 84 for Capital + AMP;
- advisory `competition_strategy.py` still reports `A_PLUS_ONLY`;
- centralize the policy contract and regression-test it before any future gate-policy change.

## 2026-09-26 — Strategy correctness work completed while deployment is blocked
Completed on main:
- centralized Capital/AMP competition policy constants and removed advisory A_PLUS_ONLY drift;
- added per-competition/per-symbol gate-failure attribution to Hostinger readback;
- fixed a direction-asymmetric missing-evidence bug that could inflate SHORT setup quality;
- added regression tests;
- competition-critical CI on the corrected code passed 191 tests with 1 warning;
- created independent-review prompt `docs/EXTERNAL_AI_REVIEW_PROMPT_2026-09-26.md`.

Only owner intervention currently required:
- correct `HOSTINGER_SSH_PRIVATE_KEY` so it contains the full private key file `stc_hostinger_deploy`, not the one-line `.pub` key.

Then:
1. trigger secure Hostinger deployment;
2. require seven-file checksum verification;
3. run Live Readback;
4. use new gate-failure counts to diagnose concentration by symbol;
5. require fresh AMP competition_mode=true / quality_floor=84 evidence;
6. reconcile STC positions to platform truth;
7. choose the next research experiment from observed failure/outcome evidence rather than trade-count pressure.

