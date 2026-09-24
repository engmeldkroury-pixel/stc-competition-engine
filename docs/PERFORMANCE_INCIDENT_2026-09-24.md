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
