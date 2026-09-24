# NEXT TASK

Updated: 2026-09-24 17:05 UTC

## CONTROLLING PROJECT
STC.

## URGENT PRODUCTION PRIORITY — PERFORMANCE RECONCILIATION

The Capital.com Africa competition account now has owner-platform evidence of:
- realized P/L: USD -1,714.76;
- one open EURUSD SHORT;
- four visible closed losing trades;
- trading-day requirement completed: 3/3.

Sanitized incident evidence is recorded in `docs/PERFORMANCE_INCIDENT_2026-09-24.md`.

### Immediate controlled actions
1. Backfill the four visible closed trades into STC using the historical closed-trade import path:
   - XAGUSD SHORT: 63.24 -> 63.593, P/L -1362.81;
   - ETHUSD LONG: 2772.35 -> 2753.74, P/L -172.80;
   - BTCUSD LONG: 86384.45 -> 85979.65, P/L -92.72;
   - BTCUSD LONG: 86648.20 -> 86358.70, P/L -70.78.
2. Keep the existing EURUSD open position as one tracked position; do not duplicate it.
3. Reconcile the remaining ~USD 15.65 realized difference against the platform transaction/entry cost before declaring STC P/L fully matched.
4. Build trade attribution for each closed trade:
   - source event/signal if available;
   - setup quality/gate state;
   - MTF/family evidence;
   - proposed quantity/risk;
   - actual fill quantity;
   - planned stop vs actual exit.
5. Do not change live weights or loosen gates until the attribution is complete.

## XAGUSD INCIDENT FINDING
- Latest verified STC XAGUSD sizing before the observed execution: 1,234.226179 units for ~USD 500 risk budget.
- Owner platform history shows approximately 3.73K units actually executed.
- Approximate sizing multiple: 3.02x the verified STC ticket.
- The signal direction was still wrong, so signal quality remains under review.
- The larger manual fill materially amplified the loss and must be treated as a separate execution/risk-control failure.

## BATCH STATUS
- PR #159 merged as `ae51f8010ab1f7ba93fadc3661066397cc167268`.
- CI run `36023363966`: SUCCESS.
- PR #159 adds per-competition:
  - open trade count;
  - completed trade count;
  - STC confirmed-bar open P/L estimate;
  - realized P/L;
  - tracked P/L;
  - recent completed-trade cards.
- Hostinger deployment of the new operator files is still pending.

## COMMUNITY INDICATOR TRACK
- Research/shadow components remain non-authoritative live.
- No community weight is to be promoted as a reaction to current losses.
- Continue Pine/Python parity work only after the immediate competition ledger/performance reconciliation is under control.

## LIVE BOUNDARY
- no automatic broker/order execution;
- human approval/manual order entry only;
- do not exceed the STC quantity ticket;
- do not widen a locked stop without an explicit recorded management decision;
- do not increase risk to chase losses;
- do not treat setup quality as win probability.
