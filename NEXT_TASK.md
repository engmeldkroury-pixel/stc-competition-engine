# NEXT TASK

Updated: 2026-09-23

## Active objective
Increase genuinely unseen evidence depth for 15m competition research without weakening any validation or risk gate.

## Research stage just completed
- Strategy Lab v2: completed.
- No-lookahead MTF comparison: completed; no 15m rescue.
- Single-regime comparison: completed; no 15m validation.
- Bounded regime-pool comparison on MNQ and BTCUSD: completed; no 15m validation.
- Same-dataset combinatorial tuning is now CLOSED for the strongest current candidates.

## Confirmed research evidence
- XAUUSD 4h adx_ema_trend: VALIDATED research-only; full feature calibration completed with 16 deployable / 17 blocked features.
- XAUUSD 15m: NO_VALIDATED_STRATEGY.
- BTCUSD 1D trend_pullback: VALIDATED research-only; 15m remains NO_VALIDATED_STRATEGY.
- MNQ 15m: NO_VALIDATED_STRATEGY after baseline, single-regime and pool testing.
- BTCUSD 15m: NO_VALIDATED_STRATEGY after baseline, single-regime and pool testing.
- No higher-timeframe result authorizes 15m runtime.

## Fresh-data status
- MNQ has only about 6 new 15m bars beyond the development dataset at this checkpoint.
- BTCUSD has only about 26 new 15m bars beyond the development dataset.
- This is insufficient for confirmation.
- Treat these as the beginning of the unseen-data accumulation window.

## Next automatic actions
1. Use the exact-provider OHLCV archive merger on future TradingView pulls to accumulate bars beyond the current 5000-bar rolling window.
2. Preserve source identity, timeframe, timestamp deduplication and revised-bar evidence.
3. Do not retune regime/MTF/pool rules on each small update.
4. Once a materially larger unseen window exists, run confirmatory evaluation using frozen candidate hypotheses and unchanged gates.
5. If a candidate passes on genuinely unseen data, require a second confirmation decision before any runtime calibration proposal.
6. Run full feature calibration only for a genuinely validated same-entry-timeframe candidate.
7. Continue keeping higher-timeframe validated research informational only.

## Historical-source constraint
The connected TradingView Official MCP currently exposes OHLCV count up to 5000 bars and no date cursor/offset. It cannot backfill a full older 15m year window in chunks. Any alternate historical source or manual export must be explicitly verified and must not be silently mixed with exact-provider evidence.

## Production safeguards
- Safe Mode and Kill Switch remain enabled.
- Manual approval and manual execution remain mandatory.
- Research outputs always have live_trading_authority=false.
- Validation gates remain unchanged.
- Verified legacy TradingView production alerts remain the rollback baseline.
- No current research result authorizes a 15m competition trade.

## Owner dependency
None now. Owner intervention is required only if a later step genuinely needs a user-controlled historical export/alternate source, private Telegram credentials, or verified manual competition position/trade input.
