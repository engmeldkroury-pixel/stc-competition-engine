# NEXT TASK

Updated: 2026-09-24 11:30 UTC

## CONTROLLING PROJECT
STC.

## URGENT PRODUCTION PRIORITY
Deploy the six-file Hostinger PR #145 hotfix. Live Python processing is already producing Capital `COMPETITION_OPPORTUNITY` signals, but the deployed PHP still applies the older A_PLUS-only eligibility rule and suppresses those opportunities.

## VERIFIED LIVE EVIDENCE
- Main includes PR #145 competition quality eligibility fix.
- Live readback workflow run `35992932406`:
  - EURUSD: SHORT;
  - setup grade: `COMPETITION_OPPORTUNITY`;
  - setup quality: 80/100;
  - Python gate failures: none;
  - deployed PHP quality gate: false;
  - deployed PHP locked plan/opportunity: suppressed.
- Runtime controls: Safe Mode OFF, Kill Switch OFF.
- Competition progress: 0 entries, 0 qualifying days, USD 0 realized P/L.
- Official leaderboard checkpoint: 4,188 participants; rank 60 +11.16% realized; rank 1 +38.08%.

## OWNER ACTION REQUIRED — ONLY CURRENT EXTERNAL BLOCKER
Upload `STC_HOSTINGER_HOTFIX_145.zip` contents to the existing STC `public_html` directory and replace the six same-name files:
1. approval.php
2. cloud_control.php
3. notification_control.php
4. operator.php
5. operator_snapshot.php
6. portfolio_control.php

Do not upload config.php. No SQL migration is required.

Bundle SHA-256:
`a4b3acddc468a9f95c3813dd3a18b201b31e12517ebb788445202fdbd1b3a93a`

## IMMEDIATE AUTOMATED ACTION AFTER OWNER UPLOAD
1. Update `ops/LIVE_READBACK_TRIGGER`.
2. Verify a fresh Capital `COMPETITION_OPPORTUNITY` is accepted by deployed PHP.
3. Verify locked plan is visible while active.
4. Verify Telegram notification is sent/not skipped.
5. If the opportunity remains fresh, present the manual order ticket to Mohamed for final human execution only.

## COMMUNITY INDICATOR TRACK — CONTINUE IN PARALLEL
- Corrected research complete: 13/26 profile-ready, 6/10 Capital.
- Lorentzian 3/26; VuManChu 0/26; QQE+SSL+WAE composite 0/26.
- Research-only community shadow plumbing merged; no live authority.
- Pine parity fixture run `35992849854` completed 6/6 successfully.
- Next engineering batch:
  1. implement Pine component streams with frozen selected parameters;
  2. compare event timestamps/values bar-by-bar against the parity fixtures;
  3. fix every mismatch;
  4. only after parity, collect shadow observations;
  5. require a separate promotion decision before any weight can influence the live quality gate.

## LIVE BOUNDARY
- no automatic broker/order execution;
- human approval/manual order entry only;
- do not treat setup quality as win probability;
- do not promote research/shadow weights without parity + evidence;
- do not loosen thresholds merely to chase leaderboard returns.
