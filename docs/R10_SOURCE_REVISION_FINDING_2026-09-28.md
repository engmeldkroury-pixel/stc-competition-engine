# R10 TradingView retrospective close-revision finding — 28 September 2026

## Observation
A direct overlap check was made between the immutable R9 normalized STC dataset captured on 27 September and a fresh TradingView Official connector read for the same CAPITALCOM symbols and timestamps.

This is a limited 20-row-per-symbol sample, not a claim about every historical bar.

### ETHUSD
- 20 stored timestamps overlapped.
- 9 rows matched OHLC exactly.
- 11 rows disagreed.
- All 11 disagreements were **close-only**; open/high/low matched in this sample.
- Maximum relative field difference in the sample was about 0.0156%.
- Example: 2026-09-27T14:30Z stored close 2689.58 versus later retrospective close 2689.16.

### DOGEUSD
- 20 stored timestamps overlapped.
- 5 rows matched OHLC exactly.
- 15 rows disagreed.
- All 15 disagreements were **close-only**; open/high/low matched in this sample.
- Maximum relative field difference in the sample was about 0.0664%.
- Example: 2026-09-27T15:00Z stored close 0.0962629 versus later retrospective close 0.0963268.

## Interpretation
The evidence is consistent with retrospective close revisions or a difference between the close value frozen by the live STC observation and the later historical series. It does not by itself identify the vendor mechanism or prove that every revised close changes a signal.

Because EMA, RSI and MTF decisions depend on closes, historical backtests performed on the later revised series must not be treated as exact replicas of what the live engine saw.

## Forward correction
Every prospective R10 observation must freeze an **as-observed evidence envelope** at decision time and store its SHA-256 in the forward record. Later TradingView history may be used for reconciliation, but it cannot silently replace the frozen source/features that generated the decision.

The finding does not invalidate all R10 historical stress work, but it increases the importance of prospective evidence and prevents retrospective history from being presented as exact live parity.


## Direct alert-log proof on 28 September
TradingView's own production alert log was compared with a later TradingView Official OHLCV read for the same source timestamp 2026-09-28T06:45:00Z.

- ETHUSD production alert (HTTP 200) emitted close **2648.05**, volume **3515**. The later historical read returned the same O/H/L but close **2648.02**, volume **3519**.
- DOGEUSD production alert (HTTP 200) emitted close **0.0927054**, volume **2569**. The later historical read returned the same O/H/L but close **0.0927032**, volume **2571**.
- BTCUSD at the same timestamp remained exact: O/H/L/C and volume matched the alert payload.

This proves that at least some remote-symbol fields can differ retrospectively after a production alert has already fired. It does not prove the exact upstream mechanism, but it rules out the assumption that later historical OHLCV is always the exact immutable data seen by the live alert.

Therefore forward evidence must preserve the alert-time/as-observed payload and its digest. Retrospective history is reconciliation evidence only.
