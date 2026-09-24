# NEXT TASK

Updated: 2026-09-24 11:30 UTC

## CONTROLLING PROJECT
STC.

## URGENT PRODUCTION PRIORITY
Deploy the new combined Hostinger hotfix containing PR #155 locked-plan persistence and PR #156 Record Trade competition-field clarity. After deployment:
1. verify an unexpired locked plan remains visible when a newer same-direction monitor-only bar arrives;
2. verify an incompatible latest bar shows the old plan as RECOVERY ONLY and blocks a new entry;
3. use Record Trade only to register an already-open manual platform position;
4. never duplicate the EURUSD order merely because STC has not yet recorded it.

Current EURUSD recovery requires the actual platform position details (filled quantity, average fill price, current stop, current final TP) from Paper Trading > Positions before writing it into the STC ledger.

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

## HOSTINGER HOTFIX STATUS
DEPLOYED AND VERIFIED.

Evidence:
- post-upload readback run: `36005321334`;
- expired historical EURUSD eligibility probe: `expired_plan`, proving the deployed PHP reached expiry after accepting the competition grade;
- Telegram configured: true;
- historical Telegram deliveries: HTTP 200.

## IMMEDIATE AUTOMATED ACTION
1. Continue reading each fresh Capital cycle.
2. On the next natural `COMPETITION_OPPORTUNITY`, verify deployed `quality_gate_passed=true`.
3. Verify locked plan is visible while active.
4. Verify Telegram `NEW_LOCKED_PLAN` delivery is sent.
5. If the plan is still valid, present the manual order ticket to Mohamed for final human execution only.

## COMMUNITY INDICATOR TRACK — CONTINUE IN PARALLEL
- Corrected research complete: 13/26 profile-ready, 6/10 Capital.
- Lorentzian 3/26; VuManChu 0/26; QQE+SSL+WAE composite 0/26.
- Research-only community shadow plumbing merged; no live authority.
- Pine parity fixture run `35992849854` completed 6/6 successfully.
- First diagnostic Pine candidate is merged as PR #152 / `529f8efc3fa9bce06de16236dd8275cd6fb42c25`.
- It covers Trendilo, SSL Hybrid, Range Filter, Schaff Trend Cycle and HalfTrend only.
- Next engineering batch:
  1. compile the diagnostic Pine candidate in TradingView;
  2. compare event timestamps/values bar-by-bar against the frozen Python fixtures;
  3. fix every mismatch;
  4. implement the remaining BTCUSD/USDZAR components only after the simpler set has parity;
  5. only after parity, collect shadow observations;
  6. require a separate promotion decision before any weight can influence the live quality gate.

## LIVE BOUNDARY
- no automatic broker/order execution;
- human approval/manual order entry only;
- do not treat setup quality as win probability;
- do not promote research/shadow weights without parity + evidence;
- do not loosen thresholds merely to chase leaderboard returns.
