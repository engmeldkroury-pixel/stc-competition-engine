# STC Capital Performance Incident — 2026-09-24

## Source

Owner-supplied TradingView The Leap / Capital.com trade-history screenshot captured 2026-09-24. The screenshot itself is not stored in the repository because it contains private account/order details. This file records only the minimum sanitized evidence needed for project control.

## Observed competition state

- Account balance: USD 98,285.24.
- Equity at screenshot time: USD 98,120.18.
- Realized P/L: USD -1,714.76.
- Unrealized P/L: USD -165.06.
- Trading-day requirement: 3/3.
- One open EURUSD short remains in the account.

## Visible closed-trade evidence

| Symbol | Side | Entry time | Entry | Exit time | Exit | Approx. size | Net P/L | Return |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| XAGUSD | SHORT | 2026-09-24 18:03 | 63.24 | 2026-09-24 19:15 | 63.593 | 3.73K | USD -1,362.81 | -0.58% |
| ETHUSD | LONG | 2026-09-22 00:07 | 2,772.35 | 2026-09-22 03:58 | 2,753.74 | 9.02 | USD -172.80 | -0.69% |
| BTCUSD | LONG | 2026-09-22 01:28 | 86,384.45 | 2026-09-22 03:55 | 85,979.65 | 0.22 | USD -92.72 | -0.49% |
| BTCUSD | LONG | 2026-09-22 00:09 | 86,648.20 | 2026-09-22 01:28 | 86,358.70 | 0.23 | USD -70.78 | -0.35% |

The four visible closed trades sum to USD -1,699.11. The remaining approximately USD -15.65 of realized loss is consistent with entry/transaction cost on the still-open EURUSD position, but that attribution remains an inference until the platform ledger is reconciled.

## XAGUSD execution discrepancy

The last verified STC live readback before the XAGUSD execution exposed a locked SHORT plan with:

- source price/reference: 63.09;
- entry zone: 62.9745605492 to 63.2054394508;
- stop: 63.48249413272;
- proposed quantity: 1,234.226179 units;
- risk budget: approximately USD 500.

The platform trade history shows an actual XAGUSD SHORT size of approximately 3.73K units entered at 63.24 and exited at 63.593.

This is approximately 3.02 times the STC proposed quantity. Using the competition commission model already present in STC, the observed XAGUSD loss is consistent with the larger executed quantity. At the same exit price, the latest verified STC quantity would have produced an estimated loss around USD 451 rather than approximately USD 1,363. If the same verified STC stop had been respected from the observed entry, the estimated loss would have been materially lower again.

Important: this does not validate the XAGUSD signal. The directional call still failed. It shows that signal error and execution/risk deviation must be analyzed separately.

## Initial diagnosis

1. The dominant realized drawdown is concentrated in XAGUSD. That single trade accounts for roughly four-fifths of the currently visible realized loss.
2. The system's signal quality must still be audited because all four visible closed trades are losses.
3. Risk/execution discipline is a separate failure mode: the visible XAGUSD fill quantity materially exceeded the latest verified STC sizing ticket.
4. STC's internal ledger is incomplete relative to the competition account. It previously showed one open EURUSD position and zero closed trades while the platform now proves multiple closed trades and 3/3 trading days.
5. Community/composite indicator research was not live-authoritative for these decisions; it cannot be blamed for these losses, and it must not be promoted merely as a reaction to drawdown.

## Immediate controls

- Do not increase per-trade risk to chase the leaderboard or recover losses.
- Do not duplicate any position because STC failed to record it.
- For every future manual execution, the operator must copy the STC quantity exactly or use a smaller valid quantity if the platform forces a reduction.
- Do not widen a locked stop after entry without a separately recorded management decision.
- Reconcile the platform trade history into STC before using STC competition P/L/trading-day statistics as authoritative.
- Audit each losing trade against its source event, gate state, multi-timeframe evidence, sizing ticket, fill, stop and exit.

## Required next engineering work

1. Backfill the four visible closed trades into the STC ledger using historical closed-trade import.
2. Reconcile the still-open EURUSD position and platform transaction cost.
3. Build a trade-attribution report linking each imported trade to the nearest/actual STC source signal where evidence exists.
4. Add an operator-visible execution-compliance check showing planned quantity vs recorded actual quantity and variance.
5. Only after attribution is complete, decide whether any live factor weights, gates or symbol-specific rules should change.


## Follow-up reconciliation — 2026-09-24 22:00 EEST screenshot

The owner supplied two additional TradingView trade-history screenshots showing the full currently visible loss set and two open positions.

### Current account state
- Account balance: USD 97,938.28.
- Equity: USD 98,372.77.
- Realized P/L: USD -2,061.72.
- Unrealized P/L: USD +434.50.
- Trading days: 3/3.
- Open positions shown by the platform: 2.
- Open symbols evidenced in trade history:
  - CAPITALCOM:EURUSD SHORT, quantity about 137.55K, entry 1.137 rounded in history;
  - CAPITALCOM:SPX500 LONG, quantity 39.2, entry 7697.1.

### Closed-trade reconciliation
Visible closed losses are now:
- SPX500 LONG 20 units: entry 7705.1 at 2026-09-24 20:21 EEST, exit 7690.8 at 20:45 EEST, net P/L USD -316.79.
- XAGUSD SHORT 3.73K: USD -1,362.81.
- ETHUSD LONG 9.02: USD -172.80.
- BTCUSD LONG 0.22: USD -92.72.
- BTCUSD LONG 0.23: USD -70.78.

These five closed losses total USD -2,015.90.

The same screenshot shows entry/transaction charges on the two still-open positions:
- EURUSD open entry charge shown as USD -15.64;
- SPX500 open entry charge shown as USD -30.17.

Those charges total USD -45.81. Closed losses plus the two visible open-position entry charges total USD -2,061.71, which reconciles to the platform's realized P/L of USD -2,061.72 within USD 0.01 rounding. There is therefore no material unexplained realized-loss remainder in the visible platform history.

### SPX500 closed-loss attribution
The platform closed trade:
- side: LONG;
- quantity: 20;
- entry: 7705.1 at 20:21 EEST = 17:21 UTC;
- exit: 7690.8 at 20:45 EEST = 17:45 UTC;
- loss: USD -316.79.

The immediately preceding STC locked plan was created at 17:15:25 UTC:
- direction: LONG;
- order instruction at notification time: BUY MARKET;
- entry zone: 7706.6856 to 7722.1144;
- stop: 7690.9440665317;
- final target: 7773.0398336707;
- proposed quantity: 20.000949;
- risk budget: USD 500;
- setup quality: 81/100;
- signal score: +0.58;
- family agreement: 100%;
- aligned families: 7/9;
- MTF: 15m +0.65, 1H +0.70, 2H +0.15, 4H +0.45, 1D +1.00, 1M +1.00.

The platform size of 20 units materially matched the STC sizing ticket, and the platform exit at 7690.8 is effectively the locked stop at 7690.944. This is therefore strong evidence of a genuine stop-out under approximately correct sizing and stop discipline. The actual fill was 1.59 index points below the locked entry-zone minimum because execution occurred about six minutes after the notification. The lower fill did not cause the loss; it was actually a slightly better long entry than the locked-zone boundary. The directional thesis still failed before later recovery.

### SPX500 immediate same-direction re-entry
The second SPX500 position shown open in the trade history:
- LONG;
- quantity: 39.2;
- entry: 7697.1 at 21:05 EEST = 18:05 UTC.

The closest preceding STC plan was generated at 18:00:24 UTC:
- direction: LONG;
- order: BUY MARKET;
- entry zone: 7691.7006 to 7707.0994;
- stop: 7675.5378488959;
- final target: 7759.0553777602;
- proposed quantity: 19.683465;
- risk budget: USD 500;
- setup quality: 82/100;
- signal score: +0.66;
- family agreement: 100%;
- aligned families: 6/9.

The actual 39.2-unit open position is approximately 1.99 times that STC quantity. It was opened about 20 minutes after the prior SPX500 stop-out, so the new PR #161 same-symbol/same-direction 30-minute cooldown would have blocked this immediate re-entry if the guardrail had already been deployed. The actual entry price was inside the new locked entry zone, so the dominant execution deviation is quantity, not entry location.

A later STC plan at 18:30:24 UTC proposed only 19.636645 units with final target 7765.603593579. The chart screenshot displays a 39.2-unit target at about 7765.6, suggesting the open position target may have been updated to the later plan while retaining the oversized quantity. Current stop placement for the open 39.2-unit position is not evidenced by the supplied trade-history screenshots and must not be guessed.

### Diagnostic conclusion
1. XAGUSD remains the largest loss and involved both a wrong directional call and approximately 3x oversizing versus the latest verified STC ticket.
2. SPX500 now provides a cleaner signal-quality failure example: the first 20-unit long approximately matched STC sizing and stop discipline and still stopped out.
3. The second SPX500 entry demonstrates a separate anti-churn/oversizing failure: it was opened ~20 minutes after the stop and at ~2x the nearest STC sizing ticket.
4. PR #161 directly addresses both execution failure modes by persisting an approval-time MAX STC QUANTITY, rejecting oversized STC-plan fill records, blocking duplicate open-symbol entries, and applying a same-symbol/same-direction loss cooldown.
5. Indicator weights and the competition quality floor should not be changed from these few trades alone. The next research priority is trade-level attribution and stop/entry sensitivity using no-lookahead evidence.

## Order-state follow-up — owner screenshots at approximately 19:23 UTC / 22:23 EEST

The platform screenshot now provides direct evidence for the active exit orders and exposes a pending-order lifecycle gap.

### Active positions and protective exits

**SPX500 LONG**
- quantity: 39.2;
- average fill: 7697.1;
- active take profit: 7765.6 for 39.2;
- active stop loss: 7690.8 for 39.2;
- last price shown: about 7706.3;
- unrealized P/L shown: about USD +360.64.

Gross price risk from average entry to the active stop is approximately:
- (7697.1 - 7690.8) x 39.2 = USD 246.96, before exit commission.

The current position is still larger than the nearest single STC ticket, but the active tightened stop materially reduces current downside versus using the wider later-plan stop.

The order history also shows a **filled SPX500 Buy Limit for 19.6 units**, limit 7707.0, fill 7705.8, with TP 7765.6 and SL 7690.8. This is consistent with the current 39.2-unit aggregate position having been increased by another 19.6-unit tranche.

**EURUSD SHORT**
- quantity: 137,552;
- average fill: 1.13677;
- active take profit: 1.12740 for 137,552;
- active stop loss: 1.13930 for 137,552;
- last price shown: about 1.13738;
- unrealized P/L shown: about USD -83.91.

### Working-order inventory

TradingView shows:
- All orders: 13;
- Working: 6;
- Inactive: 4;
- Filled: 1;
- Cancelled: 2.

The six working orders can be reconciled from the screenshots as:
1. EURUSD protective stop-loss;
2. EURUSD take-profit;
3. SPX500 protective stop-loss for 39.2;
4. SPX500 take-profit for 39.2;
5. NAS100 Buy Limit 3.7 at 30357.7;
6. NAS100 Buy Limit 3.7 at 30407.8.

The NAS100 limit orders have separate inactive child brackets visible:
- one bracket around TP 30722.9 / SL 30282.8;
- another around TP 30758.6 / SL 30319.1.

There is **no open NAS100 position on the platform**, so the two working NAS100 entry orders represent latent future exposure. If both fill, the resulting 7.4-unit NAS100 position would stack two separate plans/orders.

### New control gap

STC currently models open positions but does not authoritatively know whether an owner has left an unfilled broker/platform entry order working. Therefore:
- a plan can expire while its TradingView pending order remains live;
- a newer plan can create another pending order on the same symbol;
- multiple pending entries can stack before any position exists;
- STC may incorrectly backfill a pending order as though it were an open position.

This is now a production-safety issue, not merely a UI improvement.

Required follow-up:
1. cancel/reconcile stale NAS100 working entry orders on the platform before any new NAS100 entry is permitted;
2. void mistaken STC manual_external open records for symbols that are not actually open on the platform;
3. add an explicit pending-entry-order lifecycle / reservation control so an unfilled entry plan blocks new same-symbol entry authorization until cancelled, filled, or expired-and-confirmed-cancelled;
4. on plan expiry, surface a clear **CANCEL UNFILLED ENTRY ORDER** instruction rather than silently letting the broker order survive;
5. never count a pending entry order as an open position.
