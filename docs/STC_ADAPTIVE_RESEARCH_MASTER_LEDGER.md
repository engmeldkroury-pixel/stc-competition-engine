# STC Adaptive Strategy & Community Indicator Master Ledger

Updated: 2026-09-23
Authority: latest owner instruction + merged main branch + verified TradingView exact-provider research evidence.

## Naming
- Project/runtime name is STC. Do not rename it CC or SCC in project files.
- General Lab is the non-competition research tab inside STC.

## Owner objective
Build STC as a symbol-specific adaptive research and decision system, not a fixed one-size-fits-all indicator stack.

For every competition symbol and every symbol later added to General Lab, STC must:
1. classify the asset;
2. test all practical native STC strategies compatible with that asset/timeframe;
3. test all practical verified community indicators compatible with that asset/timeframe;
4. tune bounded parameters on TRAIN only;
5. freeze parameters before TEST and FORWARD;
6. compare native strategies and community indicators on out-of-sample/forward robustness;
7. assign symbol/timeframe-specific research weights;
8. permit a community indicator to receive more research weight than a native strategy when the evidence is stronger;
9. accumulate new live outcomes as evidence;
10. recalibrate weights only after a frozen evidence window/batch, never after one isolated trade;
11. keep General Lab on the exact same research engine;
12. keep live competition execution human-approved/manual-only.

## Non-negotiable validation rules
- No lookahead.
- Confirmed-bar signal only.
- Entry no earlier than next bar/open or the existing conservative STC entry rule.
- Same-bar stop/target ambiguity resolves conservatively to STOP first.
- Include transaction-cost/slippage proxy in benchmark research.
- Popularity, follower/use count, editor picks, reviews and Reddit discussion may prioritize discovery/audit only.
- Popularity/reviews never create a trading weight or probability.
- Repainting indicators must be rejected or restricted to an explicitly verified non-repainting mode.
- Same-symbol exact-provider history is required for competition research; no silent cross-provider substitution.
- A winner on one symbol/timeframe never inherits its weight on another symbol/timeframe.
- Same-dataset backtest winners are never promoted directly to live authority.

## Research layers
### Layer A — Native STC strategy matrix
Existing native families include:
- SMC structure/liquidity
- trend pullback
- breakout expansion
- mean reversion
- VWAP intraday
- microtrend scalp
- momentum continuation
- volatility squeeze
- range rotation
- ADX/EMA trend
- Donchian/structure breakout
- Bollinger mean reversion
- VWAP reversion
- liquidity-sweep reversal
- failed-breakout reversal
- FVG/displacement continuation
- volume-confirmed breakout

### Layer B — Community indicator matrix
Catalog is intentionally expandable.

Implemented causal research adapters:
- UT Bot Alerts family
- Squeeze Momentum [LazyBear] family
- WaveTrend with Crosses family
- Hull Suite family
- SuperTrend family
- Chandelier Exit family
- Schaff Trend Cycle family
- Range Filter Buy/Sell family

Pending exact/repaint-safe implementation:
- Machine Learning: Lorentzian Classification
- QQE MOD
- Optimized Trend Tracker
- HalfTrend
- SSL Hybrid
- AlphaTrend
- VuManChu Cipher B + Divergences
- Trendilo
- Nadaraya-Watson Envelope — non-repainting mode only
- additional practical high-use/open-source candidates discovered later

Context/native-overlap audit:
- Smart Money Concepts [LuxAlgo] must be checked against STC native BOS/CHoCH/order-block/FVG/liquidity families before any added weight.
- Williams Vix Fix is initially context/reversal evidence, not an independent direction authority.

### Layer C — Symbol/timeframe ensemble
For each symbol/timeframe:
- native validated strategy components and validated community components enter the same research comparison;
- weight is derived from robust OOS/forward evidence and sample confidence;
- weak/failed components receive zero deployable research weight;
- component families should be monitored for duplicate information so correlated indicators do not create fake consensus.

### Layer D — General Lab automation
Any symbol added to General Lab must automatically inherit the research PROCESS, not the weights:
asset classification -> data-quality check -> native matrix -> community matrix -> OOS/forward comparison -> symbol/timeframe profile -> research report.

General Lab never copies weights from competition symbols merely because the asset class is similar.

## Weight adaptation policy
- Every completed live trade can be logged as new evidence.
- No weight changes after a single win/loss.
- Recalibration occurs only after a predefined frozen observation batch/window.
- Old and new windows must be compared for degradation, drift and sample sufficiency.
- A component can gain/lose weight only through the same validation standard.
- Research profiles remain shadow-only until explicit promotion.

## Community discovery/review policy
Research may use:
- TradingView open-source scripts and descriptions;
- TradingView popularity/use counts and editor picks;
- public comments/community discussion;
- Reddit discussion for user experience, repaint warnings and implementation concerns.

Review evidence is qualitative. It may change research priority but not backtest score.

## Artifact register
- app/strategy_lab.py — native STC strategy catalog and robust selection.
- app/walkforward.py — native no-lookahead train/test/forward benchmark.
- app/community_indicator_catalog.py — community candidate registry.
- app/community_indicator_signals.py — verified causal community adapters.
- app/community_indicator_benchmark.py — standardized community benchmark, train-only parameter selection and ensemble weights.
- app/community_research_plan.py — 26-symbol + General Lab experiment matrix.
- app/research_runner.py — exports community trials/profiles with native research.
- docs/COMMUNITY_INDICATOR_RESEARCH.md — research rules and source seed list.
- tests/test_community_indicator_lab.py — causal/weighting/General-Lab contracts.
- research_benchmarks/community_15m_batch1_20260923.json — exact-provider Capital + partial AMP benchmark evidence.
- research_benchmarks/community_15m_batch2_20260923.json — exact-provider remaining AMP benchmark evidence.
- research_benchmarks/community_15m_summary_20260923.json — combined 26-symbol community benchmark summary.
- docs/COMMUNITY_15M_BENCHMARK_20260923.md — human-readable benchmark leaderboard.
- scripts/run_native_community_15m.py — native-vs-community exact-data comparison runner.
- .github/workflows/stc-native-community-15m.yml — reproducible benchmark workflow.

## Work-unit register
### WU-101 — adaptive community research foundation
Status: VERIFIED / MERGED.
- PR #101 merged: 8779c8ac8f66d1007ce962a5cfde46db65dfe1d2.
- CI: 347 passed.
- Added initial catalog, four causal adapters, symbol-specific benchmark, General Lab research planning, native/community ensemble research weights.
- Live authority deliberately false.

### WU-102 — expanded candidate set + train-only tuning
Status: VERIFIED / MERGED.
- PR #102 merged: f47bb7e3a630915de264dcabcde31988fa8eb7de.
- CI: 351 passed, 1 warning.
- Added SuperTrend, Chandelier Exit, Schaff Trend Cycle and Range Filter causal adapters.
- Expanded discovery queue with HalfTrend, SSL Hybrid, AlphaTrend, VuManChu Cipher B, Trendilo, Nadaraya-Watson non-repaint candidate, and Williams Vix Fix context candidate.
- Added bounded parameter grids selected on TRAIN only and frozen before TEST/FORWARD.

### WU-103 — 26-symbol exact-provider 15m community benchmark
Status: COMPLETED / EVIDENCE GENERATED / PENDING MERGE TO MAIN.
- Branch: research/community-15m-pilot-20260923.
- 26/26 competition symbols tested.
- 5,000 exact TradingView 15m bars per symbol.
- 8 implemented community indicator families tested per symbol.
- Total: 208 symbol-indicator trials.
- 8/26 symbols had at least one community component pass the full OOS+forward gate in this run.
- Cross-symbol validated counts:
  - Range Filter: 4/26
  - UT Bot: 3/26
  - Schaff Trend Cycle: 3/26
  - Chandelier Exit: 2/26
  - WaveTrend: 2/26
  - SuperTrend: 1/26
  - Squeeze Momentum: 1/26
  - Hull Suite: 0/26
- These counts prove why per-symbol weighting is required; no single community indicator works reliably everywhere.

Notable validated examples from the 15m research run:
- NYMEX:MCL1!: Chandelier Exit top robust score about 42.93.
- CBOT:ZB1!: Range Filter top robust score about 51.08.
- CBOT:ZN1!: Schaff Trend Cycle passed, score about 22.94.
- CME_MINI:MJY1!: WaveTrend passed, score about 30.26.
- CME:MET1!: UT Bot passed, score about 25.17.
- NYMEX:MNG1!: Range Filter passed, score about 24.30.
- CAPITALCOM:USDZAR: SuperTrend top robust score about 27.62.
- CAPITALCOM:DOGEUSD: Range Filter passed, score about 21.86.

### WU-104 — native-vs-community 15m benchmark
Status: IN PROGRESS.
- Branch: research/native-community-15m-20260923.
- Reproducible runner and GitHub workflow created.
- Exact 15m TradingView datasets are being staged for all 26 symbols.
- Goal: run native STC strategy matrix and community matrix on the same 5,000-bar source windows, then create an ensemble profile per symbol and compare native vs community evidence fairly.

## Decision register
D-01: STC name remains controlling.
D-02: Per-symbol/per-timeframe specialization is required.
D-03: Community components may outrank native components if robust evidence is stronger.
D-04: Reviews/popularity never become direct weights.
D-05: Parameter tuning uses TRAIN only.
D-06: Weight updates use frozen batches/windows, not one-trade reactions.
D-07: General Lab automatically uses the same research process for every newly added symbol.
D-08: Repainting or ambiguous future-dependent scripts are not eligible for live evidence.
D-09: Live A+ gate/risk rules remain unchanged until a separate frozen promotion decision.
D-10: Manual human execution remains mandatory; research code cannot place orders.

## Risk / blocker register
- Current community exact adapters are conceptual independent implementations where noted; pending scripts need exact semantic/repaint verification before inclusion.
- TradingView connector returns up to 5,000 bars per request and has no unlimited historical cursor in the current interface; archive accumulation remains useful for deeper history.
- Correlated indicators can double-count the same information. Family-correlation/diversity control remains a required next refinement before live promotion.
- A 15m winner is not automatically a winner on 5m/30m/1h/2h/4h/1D; each timeframe must be tested independently.
- General Lab UI currently stores symbols locally; automatic research execution/report display still needs its runtime bridge after the research engine is finalized.

## Acceptance / promotion ladder
DISCOVERED -> CAUSAL_VERIFIED -> BACKTESTED -> OOS_PASSED -> FORWARD_PASSED -> SHADOW_WEIGHT -> FROZEN_CONFIRMATION -> EXPLICIT_PROMOTION -> LIVE_EVIDENCE

No stage may be skipped solely because an indicator is popular.

## Next-action card
1. Finish staging exact 15m OHLCV for all 26 symbols on research/native-community-15m-20260923.
2. Trigger the reproducible native+community workflow.
3. Read the combined artifact and compare native vs community winner/weight by symbol.
4. Merge evidence results to main after verification.
5. Add family-correlation/diversity penalty to prevent duplicate evidence weight.
6. Implement the next exact community adapters in priority order: Lorentzian, QQE MOD, OTT, then HalfTrend/SSL Hybrid/AlphaTrend/VuManChu subject to repaint/source audit.
7. Extend validated matrix to additional timeframes.
8. Build the General Lab runtime bridge so newly added symbols automatically run the same matrix and show a compact report.


## Work-unit register update — 2026-09-23 23:35 EEST

### WU-103A — General Lab routing + discovery wave 2
Status: VERIFIED / MERGED.
- PR #103 merged as 22150b34cffbc47a1481d5b7a196fb76b1fa341b.
- Added POST /research/general-lab/plan and POST /research/general-lab/evaluate.
- Any General Lab symbol can be routed through the same symbol/timeframe native + community research matrix when exact-provider OHLCV series are supplied.
- Added second-wave candidates: Koncorde Plus, RSI Kernel Optimized, VWAP Stdev Bands v2, Flux Order Blocks, Flux Market Structure Dashboard, Machine Learning Supertrend variants, AI-SuperTrend KNN, Tri-State Supertrend.
- AlphaTrend and Optimized Trend Tracker were promoted to implemented causal research adapters.
- Ensemble normalization became redundancy-aware by evidence family so several similar trend indicators cannot manufacture fake consensus.
- General Lab remains research_only/live_authority=false.

### WU-103B — archive first 26-symbol community benchmark
Status: VERIFIED / MERGED.
- PR #104 merged as eea0c49a65091a76acadae974b0a9b1d18975c4d.
- Archived the 26-symbol / 208-trial 15m benchmark evidence and human-readable leaderboard in main.
- Evidence is historical/research only and did not modify live weights.

### WU-105 — composite strategy research wave
Status: VERIFIED / MERGED.
- PR #105 merged as d120d460db9d0b8614a5e81fd7e6a60d875ddba8.
- CI: 359 passed, 1 warning.
- Added causal/conceptual research adapters for:
  - QQE MOD dual-QQE/Bollinger agreement;
  - SSL Hybrid baseline/SSL1 entry state;
  - Waddah Attar Explosion MACD/Bollinger/ATR-dead-zone state;
  - QQE MOD + SSL Hybrid + Waddah Attar Explosion composite strategy.
- Added TRAIN-only bounded parameter grids for all four.
- Public composite rule recorded: QQE direction change + SSL alignment + WAE explosion alignment on the same confirmed bar.
- No live A+ gate/risk/execution behavior changed.

### WU-104 status refinement — latest native-vs-community benchmark
Status: IN PROGRESS.
- Exact 15m datasets for all 26 competition symbols are staged on research/native-community-15m-20260923.
- Runner was converted to parallel per-symbol GitHub Actions jobs after the sequential version proved too slow.
- Older runs 1-4 were cancelled/superseded by newer code/data snapshots.
- Run 5 is the controlling benchmark request.
- Run 5 uses latest research branch state containing 14 implemented community research components plus the native STC strategy matrix.
- Acceptance evidence required:
  1. all 26 symbol jobs complete successfully;
  2. combined summary artifact produced;
  3. native and community components compared on identical 5,000-bar 15m windows;
  4. per-symbol ensemble weights generated with redundancy-aware family normalization;
  5. results archived to main before any promotion discussion.

## Current implemented community research set
The executable research pool now includes at least:
1. UT Bot Alerts
2. Squeeze Momentum
3. WaveTrend Crosses
4. Hull Suite
5. SuperTrend
6. Chandelier Exit
7. Schaff Trend Cycle
8. Range Filter
9. AlphaTrend
10. Optimized Trend Tracker
11. QQE MOD
12. SSL Hybrid baseline/SSL1 adapter
13. Waddah Attar Explosion
14. QQE + SSL + WAE composite

The catalog remains larger than the executable pool. Pending candidates remain pending until causal/repaint-safe semantics are verified.
