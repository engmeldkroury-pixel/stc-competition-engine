# NEXT TASK

Updated: 2026-09-23

## Active objective
Accumulate genuinely unseen, confirmed 15m TradingView Official MCP evidence against immutable pre-freeze development context. Do not reopen same-dataset tuning, weaken validation/risk gates, or mix alternate-provider data into exact-provider confirmation.

## Research state
- Strategy Lab v2: completed.
- No-lookahead MTF comparison: completed; no 15m rescue.
- Single-regime comparison: completed; no 15m validation.
- Bounded regime-pool comparison: completed; no 15m validation.
- Same-dataset combinatorial tuning: CLOSED.
- XAUUSD 4h adx_ema_trend remains VALIDATED research-only.
- BTCUSD 1D trend_pullback remains VALIDATED research-only.
- No higher-timeframe result authorizes 15m runtime.

## Frozen-confirmation integrity
Active manifest: research_hypotheses/frozen_15m_v2.json

Frozen confirmation v2 uses exactly 1000 immutable pre-freeze development bars from the original Strategy Lab v2 research inputs for feature warm-up. Later TradingView revisions to pre-freeze history cannot alter the frozen confirmation context.

1. MNQ vwap_reversion / 15m
   - freeze_t: 1790103600
   - threshold 0.72
   - stop 1.2 ATR
   - target 2.5R
   - max hold 16 bars
2. BTCUSD bollinger_mean_reversion / 15m
   - freeze_t: 1790089200
   - threshold 0.50
   - stop 1.2 ATR
   - target 2.5R
   - max hold 16 bars

No parameter or regime retuning is allowed during unseen confirmation.

## Latest exact-provider archive state
- MNQ:
  - confirmed through: 1790129700
  - mutable tail 1790130600 withheld
- BTCUSD:
  - confirmed through: 1790130600
  - mutable tail 1790131500 withheld

## Latest frozen-confirmation result
Run: 35812474596
- MNQ: 25 unseen bars, 0 completed trades, 1 incomplete open trade, ACCUMULATING.
- BTCUSD: 46 unseen bars, 1 completed trade, -0.32121976097584065R, ACCUMULATING.
- Both use historical_context_locked=true and frozen_context_bars=1000.
- Minimum judgment floor: 30 completed unseen trades.
- ACCUMULATING is not a failure.
- Any future UNSEEN_SUPPORT still requires a second confirmation decision.
- live_calibration_authority remains false.

## Active automatic path
1. Pull fresh TradingView Official MCP 15m snapshots for CME_MINI:MNQ1! and CAPITALCOM:BTCUSD.
2. Merge by timestamp into research_archive.
3. Withhold the current mutable final bar.
4. Preserve provider revision evidence; frozen v2 context remains immutable.
5. Do not retune hypotheses.
6. Re-run context-locked frozen confirmation when meaningful confirmed new evidence exists.
7. Keep Safe Mode, Kill Switch, manual approval, and manual execution enabled.

## Optional deeper-history paths
### TradingView / MNQ
TradingView MCP cannot back-page older than its rolling 5000 bars. Immediate deeper MNQ 15m history requires either:
- a deeper TradingView CSV export; or
- authorized CME DataMine access.

### Capital.com
Capital.com backfill infrastructure remains implemented but is PARKED because the owner does not have a Capital.com account. Do not request credentials and do not require account creation for STC. If the owner independently chooses to use Capital.com later, the existing discovery/overlap/reconciliation workflow can be reactivated.

## Production safeguards
- Safe Mode and Kill Switch remain enabled.
- Manual approval and manual execution remain mandatory.
- Validation gates remain unchanged.
- Research outputs always have live_calibration_authority=false.
- Verified legacy TradingView production alerts remain the rollback baseline.
- No current result authorizes a 15m competition trade.

## Owner dependency — CURRENT
No owner action is required for the normal future TradingView accumulation path.

Immediate historical expansion beyond the rolling TradingView MCP window is the only owner-controlled dependency. If immediate backfill is required, provide a deeper TradingView CSV export or authorized CME DataMine access. Otherwise continue exact-provider accumulation as new confirmed bars arrive.
