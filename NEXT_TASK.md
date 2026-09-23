# NEXT TASK

Updated: 2026-09-23

## PRIMARY OBJECTIVE
Execute the new community-indicator research matrix on real exact-provider historical data for the 26 competition symbols, then expand the verified indicator catalog without changing live trading weights on the same evidence used for discovery.

## VERIFIED CURRENT STATE
- Live Owner Console PR #100 is deployed; Record Trade and simplified EXECUTION TICKET are visible.
- Six v1.1 MTF production alerts remain the live evidence path.
- Human approval/manual order entry remains mandatory.
- Community indicator research framework PR #101 is merged.
- CI for PR #101: 347 passed.
- community_indicator_live_authority=false.

## RESEARCH MATRIX RULE
For every symbol/timeframe:
1. benchmark each implemented community indicator independently;
2. keep train/test/forward separated;
3. use confirmed-bar / next-bar causal execution;
4. compare validated community trials with native STC StrategyTrial results;
5. derive symbol/timeframe-specific research weights from OOS/forward robustness;
6. allow a community component to outrank a native strategy only when robust evidence is stronger;
7. do not use popularity/reviews as trading weights;
8. accumulate new live outcomes continuously, but recalibrate only on frozen batches/windows.

## CURRENT IMPLEMENTED COMMUNITY ADAPTERS
- UT Bot Alerts family.
- Squeeze Momentum [LazyBear] family.
- WaveTrend with Crosses family.
- Hull Suite family.

## NEXT IMPLEMENTATION QUEUE
Exact causal/repaint-safe ports and tests:
1. Lorentzian Classification + published Backtest Stream semantics.
2. QQE MOD.
3. Optimized Trend Tracker confirmed reversals.
4. expand discovery catalog with additional practical open-source community scripts.
5. audit LuxAlgo SMC versus STC native structure/liquidity families for information overlap before any added weight.

## DATA EXECUTION
Run the matrix first on 15m for all 26 competition symbols using the largest exact-provider history available, then extend to 5m/30m/1h/2h/4h/1D where history is sufficient.
- Prefer >=900 bars for the existing walk-forward strategy comparison.
- Community adapter benchmark can produce diagnostics from >=300 bars, but promotion still requires robust OOS/forward evidence.
- Do not promote a same-dataset winner directly to live production.

## GENERAL LAB
Any symbol added to General Lab must be routed through the same matrix:
asset classification -> indicator/strategy benchmark -> OOS/forward comparison -> symbol-specific weight profile.
No cross-symbol weight inheritance.

## REVIEW RESEARCH
Continue sourcing TradingView open-source pages and community discussions to discover candidates and identify:
- repaint/lookahead concerns;
- confirmed vs potential signals;
- asset/timeframe-specific behavior;
- parameter sensitivity;
- known implementation bugs.
Reviews are qualitative evidence only.

## EXECUTION BOUNDARY
- No automatic trading.
- No live community-indicator authority yet.
- Do not weaken A+ gates.
- Do not alter risk limits or competition rules from research results without frozen confirmation and explicit promotion.
