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
