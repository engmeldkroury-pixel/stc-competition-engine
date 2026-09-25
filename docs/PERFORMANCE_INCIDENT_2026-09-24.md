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

## Follow-up incident — 2026-09-25 NAS100 profit giveback and stale ledger

Owner screenshots on 2026-09-25 show the competition account at approximately:
- account balance: USD 96,605.69;
- realized P/L: USD -3,394.31;
- one actual open position only;
- actual open position: CAPITALCOM:NAS100 LONG 7.7, average fill 30,416.1, active TP 30,758.6, active SL 30,319.1.

The current actual position is composed from at least two visible filled NAS100 entry orders:
- 3.7 @ approximately 30,407.5;
- 4.0 @ approximately 30,424.0.

The account order history also shows additional stopped/closed losses after the prior reconciliation, including:
- EURUSD short stopped at 1.13930;
- SPX500 39.2 aggregate long stopped around 7,690.7;
- a later SPX500 20 long entered around 7,730.2 and stopped around 7,704.6;
- BTCUSD 0.5 long entered around 85,026.25 and stopped around 84,800.

### NAS100 missed profit protection

TradingView 15-minute market history for the actual NAS100 position shows:
- actual average entry: 30,416.1;
- initial active stop: 30,319.1;
- initial risk distance: 97.0 index points;
- maximum observed intrabar high after entry: 30,714.6 at 2026-09-25 11:30 UTC;
- maximum closed-bar close after entry: 30,696.7 at 2026-09-25 11:15 UTC;
- closed-bar peak R: approximately +2.89R;
- intrabar peak R: approximately +3.08R;
- gross peak open P/L on 7.7 units: approximately USD +2,298 before commission.

This confirms the owner's report that the trade exceeded USD +2,000 unrealized profit.

By 2026-09-25 around 15:30 UTC, NAS100 had retraced to roughly 30,569, around +1.58R on the actual position. The original stop was still 30,319.1, so the platform had already surrendered more than 1R of open profit while still leaving the trade capable of turning into a full initial-risk loss.

### Root cause

This is not only an entry-quality problem. The profit-management layer is inadequate for the competition objective.

Two separate failures were confirmed:
1. The live STC ledger is stale and does not match the platform. Live readback still shows four STC OPEN positions (EURUSD, XAGUSD, NAS100, SPX500), while the platform screenshot shows only one actual open NAS100 position.
2. STC tracks NAS100 as only 3.797603 units entered at 30,444.7, not the actual 7.7 units at 30,416.1. Therefore its portfolio supervisor cannot calculate or communicate the real account's risk/profit correctly.

The existing production supervisor also used only current R and a weak fixed profit lock:
- +1.0R to +1.5R -> lock +0.25R;
- >= +1.5R -> lock only +0.50R.

That rule is too permissive after a 2.5R-3R excursion for a realized-P/L competition.

### Corrective design

The new branch `stc-profit-lock-highwater-20260925` changes the supervisor to use a closed-bar high-water mark from stored signal history and a progressive profit floor:
- peak 1.0R-1.5R -> floor +0.25R;
- peak 1.5R-2.0R -> floor +0.75R;
- peak 2.0R-2.5R -> floor +1.25R;
- peak 2.5R-3.0R -> floor at least +1.50R and approximately peak minus 0.75R;
- peak >=3.0R -> floor at least +1.75R and approximately peak minus 0.60R.

If current R falls below the already-earned dynamic floor, the supervisor recommends EXIT_NOW instead of allowing the position to drift back toward the original stop.

Execution remains manual.
