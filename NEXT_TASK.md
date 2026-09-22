# NEXT TASK

Updated: 2026-09-23

## Active objective
Increase genuinely unseen 15m evidence depth without reopening same-dataset tuning, weakening any validation/risk gate, or mixing alternate-provider history into exact-provider evidence.

## Research state
- Strategy Lab v2: completed.
- No-lookahead MTF comparison: completed; no 15m rescue.
- Single-regime comparison: completed; no 15m validation.
- Bounded regime-pool comparison: completed; no 15m validation.
- Same-dataset combinatorial tuning: CLOSED.
- XAUUSD 4h adx_ema_trend remains VALIDATED research-only.
- BTCUSD 1D trend_pullback remains VALIDATED research-only.
- No higher-timeframe result authorizes 15m runtime.

## Exact-provider archive state
- Archive merger is confirmed-bar only; mutable TradingView tail bars are withheld.
- CME_MINI:MNQ1!:
  - freeze timestamp actually used by development research: 1790103600
  - confirmed archive through: 1790109000
  - unseen confirmed bars: 6
- CAPITALCOM:BTCUSD:
  - freeze timestamp actually used by development research: 1790089200
  - confirmed archive through: 1790113500
  - unseen confirmed bars: 27

## Frozen hypotheses
Manifest: research_hypotheses/frozen_15m_v1.json

1. MNQ vwap_reversion / 15m
   - threshold 0.72
   - stop 1.2 ATR
   - target 2.5R
   - max hold 16 bars
2. BTCUSD bollinger_mean_reversion / 15m
   - threshold 0.50
   - stop 1.2 ATR
   - target 2.5R
   - max hold 16 bars

No parameter or regime retuning is allowed during unseen confirmation.

## Current frozen-confirmation result
Optimized smoke run: 35791585192
- MNQ: 6 unseen bars, 0 completed trades, ACCUMULATING.
- BTCUSD: 27 unseen bars, 1 completed trade, -0.32121976097584065R, ACCUMULATING.
- Minimum judgment floor: 30 completed unseen trades.
- ACCUMULATING is not a failure.
- Any future UNSEEN_SUPPORT still requires a second confirmation decision.
- live_calibration_authority remains false.

## Ready automatic paths
### A. Future exact-provider accumulation
1. Pull TradingView Official MCP 15m snapshots.
2. Merge into research_archive with timestamp de-duplication and revised-bar evidence.
3. Withhold current mutable tail.
4. Do not retune hypotheses.
5. Re-run frozen confirmation only when meaningful new evidence exists.

### B. Capital.com deeper-history path for CAPITALCOM symbols
Infrastructure is merged and ready:
- read-only market discovery;
- from/to historical backfill;
- explicit bid/ask/mid price basis;
- secure GitHub Actions secret handling;
- overlap reconciliation against TradingView;
- alternate-provider quarantine.

After owner adds the required GitHub Actions secrets:
1. Create a capital-backfill/** discovery branch/request.
2. Discover and verify the exact Capital.com epic.
3. Fetch an overlap window first.
4. Run cross-feed reconciliation.
5. Review basis-point and return-correlation evidence.
6. Only if the feed is sufficiently compatible for research, fetch the older historical window.
7. Keep Capital history separate from research_archive; never silently merge providers.
8. Use alternate-source results only as additional research evidence, not as frozen exact-provider confirmation.

### C. MNQ immediate older-history path
TradingView MCP cannot page backward beyond 5000 bars.
For immediate older MNQ 15m evidence, owner must provide one of:
- TradingView CSV export with deeper loaded chart history; or
- authorized CME DataMine historical access/entitlement.
Otherwise continue future exact-provider accumulation.

## Production safeguards
- Safe Mode and Kill Switch remain enabled.
- Manual approval and manual execution remain mandatory.
- Validation gates remain unchanged.
- Research outputs always have live_calibration_authority=false.
- Verified legacy TradingView production alerts remain the rollback baseline.
- No current result authorizes a 15m competition trade.

## Owner dependency — CURRENT
Immediate deep-history work is now blocked only by user-controlled data access.

For Capital.com workflow, set these GitHub Actions repository secrets securely:
- CAPITAL_API_KEY
- CAPITAL_IDENTIFIER
- CAPITAL_PASSWORD

Do not paste these values into ChatGPT or commit them to the repository.

For MNQ, provide a deeper TradingView CSV export or authorized CME DataMine access if immediate backfill is required.
