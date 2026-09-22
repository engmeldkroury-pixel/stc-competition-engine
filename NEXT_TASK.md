# NEXT TASK

Updated: 2026-09-23

## Active objective
Find a robust same-entry-timeframe competition strategy without weakening sample, OOS, forward, stability or risk gates, while increasing historical evidence depth.

## Current research architecture
- 17 research strategy families.
- Exact-provider TradingView OHLCV.
- No-lookahead historical features.
- Train / OOS test / forward validation.
- Exact-timeframe runtime calibration only.
- MTF confirmation research across 1H / 2H / 4H / 1D / 1M.
- Single-regime comparison across BULL_TREND / BEAR_TREND / RANGE / TRANSITION.
- regime_pool_compare: bounded exploratory pool testing for the two strongest adequately sampled 15m candidates.
- Any same-dataset pool pass is FRESH_CONFIRMATION_REQUIRED and has no live authority.
- Exact-provider OHLCV archive merger is available for accumulating deeper history across future pulls.

## Completed evidence
- XAUUSD 4h adx_ema_trend: VALIDATED research-only; full feature calibration completed with 16 deployable / 17 blocked features.
- XAUUSD 15m: NO_VALIDATED_STRATEGY.
- BTCUSD 1D trend_pullback: VALIDATED research-only; 15m remains unvalidated.
- MNQ 15m: no validated strategy; vwap_reversion improves materially in BEAR_TREND but still fails sample/stability/forward-PF gates.
- BTCUSD 15m: bollinger_mean_reversion improves materially in TRANSITION but still misses OOS expectancy/PF and parameter-stability gates.
- ETHUSD and XAUUSD MTF comparisons did not produce a validated 15m candidate.
- MCL and other screened symbols remain unvalidated at 15m.
- Do not promote any higher-timeframe result into 15m runtime.

## Active batches
- research/regime-pool-mnq-20260923 — run 35788119034.
- research/regime-pool-btcusd-20260923 — run 35788144497.

## Next automatic actions
1. Read both regime-pool runs when complete.
2. Rank pool results by unchanged OOS/forward/stability/risk gates and sample retention.
3. Treat any apparent same-dataset pass as a hypothesis only; require fresh/unseen confirmation.
4. Update PROJECT_STATE.md with final pool evidence.
5. Begin using the OHLCV archive merger on future exact-provider pulls so the 15m evidence window grows beyond the current ~5000-bar source limit.
6. Run full feature calibration only for a genuinely VALIDATED same-entry-timeframe candidate.
7. Only after fresh confirmation consider any runtime calibration-registry proposal.

## Production safeguards
- Safe Mode and Kill Switch remain enabled.
- Manual approval and manual execution remain mandatory.
- Research outputs never set live_trading_authority.
- Verified legacy TradingView production alerts remain the rollback baseline.
- Six v1.1 MTF Family Breadth Pine feeds remain code-ready but are not silently promoted.

## Owner dependency
None now. Owner intervention is required only for a step that genuinely needs user-controlled TradingView/export access, private Telegram credentials, or verified manual competition position/trade input.
