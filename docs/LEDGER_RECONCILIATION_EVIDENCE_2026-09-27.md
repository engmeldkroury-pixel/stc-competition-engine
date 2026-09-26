# STC Ledger Reconciliation Evidence — 2026-09-27

Status: PARTIAL EVIDENCE COMPLETE / ONE CAPITAL HISTORY SCREEN STILL REQUIRED

## Source basis
Owner-supplied TradingView competition screenshots from 2026-09-27:
- Capital.com Positions;
- AMP Futures Positions;
- AMP Futures Trade history;
- Capital.com Trade history (upper and middle/lower portions).

No broker order is sent by this reconciliation work.

## Platform truth — current open positions

### Capital.com
Current platform Positions view shows exactly two open positions:

| Symbol | Side | Quantity | Avg fill | Take profit | Stop loss |
| --- | --- | ---: | ---: | ---: | ---: |
| CAPITALCOM:NAS100 | LONG | 7.7 | 30416.1 | 30758.6 | 30319.1 |
| CAPITALCOM:SPX500 | LONG | 40 | 7737.3 | 7797.0 | 7716.0 |

Capital account snapshot:
- realized P/L: -3425.26 USD;
- unrealized P/L: +1933.29 USD;
- trading days: 4/3.

### AMP Futures
Current platform Positions view shows no open positions.

AMP account snapshot:
- realized P/L: +991.25 USD;
- unrealized P/L: 0;
- trading days: 3/5.

## AMP trade history — complete evidence

| Symbol | Side | Entry local time | Entry | Exit local time | Exit | Qty | Net P/L |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| CME:MET1! | LONG | 2026-09-22 00:14 | 2777.5 | 2026-09-22 03:56 | 2761.5 | 25 | -40.00 |
| CBOT:ZN1! | SHORT | 2026-09-23 17:47 | 105.328 | 2026-09-23 20:02 | 104.984 | 3 | +1031.25 |

The two AMP trades sum exactly to +991.25 USD, matching the platform realized P/L.

## Time-zone reconciliation finding

The TradingView trade-history timestamps are consistent with Egypt local time UTC+03.

Converting the AMP timestamps by subtracting three hours yields:
- MET open: 2026-09-21 21:14 UTC;
- MET close: 2026-09-22 00:56 UTC;
- ZN open: 2026-09-23 14:47 UTC;
- ZN close: 2026-09-23 17:02 UTC.

STC competition progress counts a UTC day when an action opens or closes a position. These events span UTC dates Sep 21, Sep 22 and Sep 23, exactly explaining the platform's AMP 3/5 trading days.

This same UTC+03 conversion should be used for the Capital history import unless contradictory evidence appears.

## Capital trade history — visible complete rows

### Open positions
| Symbol | Side | Entry local time | Entry | Qty |
| --- | --- | --- | ---: | ---: |
| CAPITALCOM:NAS100 | LONG | 2026-09-24 23:13 | 30416.071 | 7.7 |
| CAPITALCOM:SPX500 | LONG | 2026-09-25 19:34 | 7737.25 | 40 |

Current stop/TP for these open rows must come from the current Positions view:
- NAS100 SL 30319.1 / TP 30758.6;
- SPX500 SL 7716.0 / TP 7797.0.

### Closed trades fully visible
| Symbol | Side | Entry local time | Entry | Exit local time | Exit | Qty | Net P/L |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| CAPITALCOM:SPX500 | LONG | 2026-09-25 12:04 | 7730.2 | 2026-09-25 17:05 | 7704.6 | 20 | -542.87 |
| CAPITALCOM:BTCUSD | LONG | 2026-09-25 14:23 | 85026.25 | 2026-09-25 14:33 | 84800.05 | 0.5 | -121.59 |
| CAPITALCOM:EURUSD | SHORT | 2026-09-24 16:47 | 1.137 | 2026-09-25 11:13 | 1.139 | 137.55K | -379.31 |
| CAPITALCOM:SPX500 | LONG | 2026-09-24 21:05 | 7697.1 | 2026-09-24 23:17 | 7690.7 | 39.2 | -311.20 |
| CAPITALCOM:SPX500 | LONG | 2026-09-24 20:21 | 7705.1 | 2026-09-24 20:45 | 7690.8 | 20 | -316.79 |
| CAPITALCOM:XAGUSD | SHORT | 2026-09-24 18:03 | 63.24 | 2026-09-24 19:15 | 63.593 | 3.73K | -1362.81 |
| CAPITALCOM:ETHUSD | LONG | 2026-09-22 00:07 | 2772.35 | 2026-09-22 03:58 | 2753.74 | 9.02 | -172.80 |
| CAPITALCOM:BTCUSD | LONG | 2026-09-22 01:28 | 86384.45 | 2026-09-22 03:55 | 85979.65 | 0.22 | -92.72 |

### Partially visible row
A further CAPITALCOM:BTCUSD LONG closed trade is partially visible:
- exit local time: 2026-09-22 01:28;
- exit price: 86358.7;
- quantity: 0.23;
- net P/L: -70.78.
Its entry time and entry price are not visible in the supplied screenshot.

## Capital completeness check

Visible closed-trade P/L including the partially visible -70.78 row sums to:
-3370.87 USD.

Platform realized P/L is:
-3425.26 USD.

Unreconciled difference:
-54.39 USD.

Therefore at least one additional closed-trade record or remaining P/L detail is still below the current screenshot range.

Do not finalize Capital historical import until the bottom of Trade history is captured.

## Current STC stale open ledger

Sanitized readback run 36273654355 shows four STC OPEN rows, all origin=manual_external:
- EURUSD SHORT 137552 @ 1.13677;
- XAGUSD SHORT 1224.597619 @ 63.157;
- NAS100 LONG 3.797603 @ 30444.7;
- SPX500 LONG 19.636645 @ 7705.8.

Current platform truth means:
- EURUSD STC OPEN row is stale/closed-on-platform;
- XAGUSD STC OPEN row is stale/closed-on-platform;
- NAS100 STC OPEN row has wrong quantity/entry;
- SPX500 STC OPEN row has wrong quantity/entry.

All four are eligible for ledger-only VOID reconciliation because they are manual_external, but do not execute the write until the remaining Capital history evidence is complete.

## One remaining owner evidence item

Scroll the Capital.com Trade history further downward from the partially visible BTCUSD row and capture the remaining bottom rows through the end of the history table.

Required purpose:
- recover the missing BTCUSD entry time/price;
- identify the remaining -54.39 USD realized P/L;
- confirm there are no further trades below.

After that final screenshot, the reconciliation plan can be executed deterministically:
1. VOID the four stale manual_external OPEN rows in STC as ledger-only records;
2. import all closed Capital and AMP trades using owner-platform P/L;
3. recreate only NAS100 and SPX500 as current open manual_external rows using exact platform quantity/entry/current SL/TP;
4. use UTC+03 -> UTC conversion for historical timestamps;
5. rerun Live Readback and compare positions, realized P/L and STC trading-day counts to platform evidence.
