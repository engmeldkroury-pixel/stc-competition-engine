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


## In-progress screening batches
- CAPITALCOM:NAS100 + CME_MINI:MNQ1!: matrix-only six-timeframe screening in progress.
- CAPITALCOM:XAGUSD + NYMEX:MCL1!: matrix-only six-timeframe screening in progress.
- Once results complete: run full feature calibration only for any VALIDATED candidate, prioritizing an exact 15m live-entry match.
- BTCUSD 1D trend_pullback is validated research with 19 deployable features, but is not promotable to 15m and probability remains uncalibrated at n=49.

## Research performance
Historical feature materialization now passes only the exact latest-1000-bar window used by the extractor; regression tests prove semantic equivalence.


## Latest completed screen
- CAPITALCOM:XAGUSD + NYMEX:MCL1!: screening completed; neither has a validated strategy and neither has a validated 15m live-entry strategy.
- Do not full-calibrate these symbols from the current research snapshot.
- NAS100 + MNQ screening remains the next pending result.

## Research branch trigger rule
Upload all exact-provider OHLCV files first, then create/update research_inputs/READY once. Do not trigger research on partial datasets.


## Strategy-engine next phase: MTF research
The latest NAS100/MNQ screen also found no validated 15m strategy. Stop broadening the universe blindly.
Build a separate no-lookahead MTF research layer that:
1. keeps the existing single-timeframe trials as baselines;
2. aligns only confirmed 1h/2h/4h/1D/month context to each 15m signal;
3. tests MTF-confirmed variants of SMC, trend-pullback, breakout and intraday/VWAP families;
4. tunes MTF gate parameters on train only, then applies them unchanged to test and forward;
5. does not lower sample, expectancy, PF, drawdown, parameter-stability or forward gates;
6. promotes nothing to live unless the exact 15m MTF variant passes robustness and later full feature calibration.
