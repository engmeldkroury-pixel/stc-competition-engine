# NEXT TASK

Updated: 2026-09-23

## PRIMARY OBJECTIVE
Finish the live Owner Console execution UX update, deploy it to Hostinger, then record and supervise the already-open AMP CBOT:ZN1! position without changing strategy/risk logic.

Primary runtime path:
TradingView v1.1 MTF alerts -> Hostinger/MySQL -> STC A+ gate -> simplified Execution Ticket -> Telegram -> human approval/manual order -> Record Trade page -> Portfolio Supervisor.

## VERIFIED CURRENT STATE
- 26-symbol production universe: 10 Capital.com Africa + 16 AMP Futures.
- Six v1.1 MTF alerts are active.
- Three legacy alerts are paused to prevent duplicate event_id collisions.
- v1.1 transport acceptance passed and Hostinger no longer shows MTF LIVE CONFIRMATION OFFLINE.
- Telegram configured and test delivery received.
- Manual approval mode is enabled:
  - Safe Mode=false.
  - Kill Switch=false.
- No automatic trading is available.

## CURRENT LIVE POSITION / OWNER BLOCKER
- Owner manually opened an AMP CBOT:ZN1! SHORT position for 3 contracts on the competition platform.
- The position is not yet recorded in the STC ledger.
- The old console workflow blocked signal approval with HTTP 409 once the live price moved outside the locked entry envelope.
- The old existing-position import used multiple browser prompt windows and was too fragile for copy/paste and the 30-second auto-refresh.

## PR #100 — MERGED / READY FOR HOSTINGER
Merged commit:
- ddb017d3c9e5bf8cb46c3c4b41dd358871e4fcba

CI:
- 339 passed.

Changed production file:
- hostinger_patch/operator.php

Key UX changes:
- Large EXECUTION TICKET at the top of each actionable card.
- Main ticket shows only:
  - symbol;
  - BUY/SELL direction;
  - exact order type;
  - entry zone;
  - exact quantity;
  - platform sizing mode;
  - stop loss;
  - one Final TP;
  - trade risk.
- AMP Futures explicitly instructs:
  - use Units / Contracts;
  - do NOT use % balance.
- Advanced research/MTF/family evidence is collapsed under Advanced details.
- ZN/ZB use TradingView Treasury 32nds/half-32nds formatting plus exact tick-aligned decimal parsing.
- Ambiguous off-tick ZN values such as 105.13 are rejected.
- Live-price input survives the 30-second console refresh.
- Existing manual positions use one dedicated Record Trade page/form instead of chained popups.
- The Record Trade page keeps all fields visible at once and supports copy/paste.
- An already-filled trade can be recorded even when approval is no longer possible because price left the original envelope.
- HTTP 409 displays the actual blocking reason instead of a generic status code.

## NEXT OWNER ACTION
Upload ONLY the latest:
- hostinger_patch/operator.php

to the live STC public_html location, replacing the current operator.php.

Do not change:
- config.php;
- secrets;
- database/migrations;
- webhook files;
- Pine scripts;
- strategy thresholds;
- risk settings.

After upload:
1. hard refresh operator.php;
2. confirm the simplified EXECUTION TICKET is visible;
3. open AMP Futures -> Record Trade;
4. record the already-open CBOT:ZN1! SHORT 3-contract position using the actual competition-platform fill/stop/final-TP values;
5. confirm it appears under Open positions / Portfolio Supervisor;
6. only then continue normal A+ monitoring.

## EXECUTION BOUNDARY
- Human approval/manual execution only.
- Do not weaken the A+ gate to create more trades.
- Do not use % balance for AMP futures position sizing; use the exact contracts/units shown by STC.
- One Final TP only; TP1 remains an internal management checkpoint.
