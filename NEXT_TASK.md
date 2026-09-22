# NEXT TASK

Updated: 2026-09-22

## Active objective
Find evidence-backed strategy/timeframe candidates for the STC competition universe without weakening the current robustness gates.

## Current execution sequence
1. Use TradingView exact-provider OHLCV.
2. Run matrix-only screening first to reduce research cost.
3. Review per-timeframe rejection diagnostics and sample coverage.
4. Run full feature calibration only for a strategy/timeframe that passes out-of-sample + forward robustness.
5. Permit runtime weighting only when the calibration timeframe exactly matches the live entry timeframe.
6. Preserve manual approval/manual execution, Safe Mode and Kill Switch governance.

## Current evidence
- CAPITALCOM:XAUUSD: no validated strategy; some positive under-sampled research candidates.
- CME_MINI:MES1!: no validated strategy; some positive under-sampled research candidates.
- CAPITALCOM:BTCUSD: overall 1D trend_pullback validated (robust score 44.59), but probability sample is 49 < 50 and live-entry 15m is not validated. Informational only; not promotable to 15m runtime.
- CAPITALCOM:EURUSD: no validated strategy; several positive-test candidates failed forward robustness.
- TradingView OHLCV max per request: 5000 bars; no time-pagination argument is exposed by the current connector.
- Do not lower validation/sample gates to manufacture a recommendation.

## Production migration gate
The six v1.1 Family Breadth Pine feeds are code-ready on main but the active TradingView alerts are still the verified legacy production snapshots. Fresh indicator alerts must be created manually later and verified in parallel before old alerts are stopped.

## Immediate next screen
Run matrix-only screening on highly liquid index/futures candidates, starting with CAPITALCOM:NAS100 and CME_MINI:MNQ1!, then expand to metals/energy if no 15m candidate validates.

## Owner dependency
None for the current research-screening phase.
