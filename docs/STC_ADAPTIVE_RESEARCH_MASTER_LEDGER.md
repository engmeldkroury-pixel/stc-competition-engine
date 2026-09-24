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


## Work-unit register update — 2026-09-23 23:40 EEST

### WU-104 — native vs community 15m benchmark
Status: VERIFIED / COMPLETED / ARCHIVED.
- Controlling workflow run: GitHub Actions run #5, run id 35916027610.
- 26/26 symbol jobs succeeded; combine job succeeded.
- Dataset: 5,000 exact-symbol TradingView 15m bars per competition symbol.
- Research pool: native STC strategy matrix + 14 implemented community research components.
- PR #106 merged as 52f43e5f057489d11d09211baabf118c2bc0b331.
- Durable evidence:
  - research_benchmarks/native_community_15m_run5_summary_20260923.json
  - docs/NATIVE_COMMUNITY_15M_RUN5_20260923.md
- Result:
  - native strategies passing every strict 15m robustness gate: 0;
  - symbols with at least one validated community component: 10/26;
  - symbols with no validated component: 16/26;
  - no live weight/A+ gate/risk/execution setting changed.

Cross-symbol community validation counts in run #5:
- SSL Hybrid: 4/26
- Range Filter: 4/26
- QQE MOD: 4/26
- Schaff Trend Cycle: 4/26
- Waddah Attar Explosion: 3/26
- UT Bot: 3/26
- Chandelier Exit: 2/26
- AlphaTrend: 2/26
- WaveTrend: 1/26
- SuperTrend: 1/26
- Squeeze Momentum: 1/26
- Hull Suite: 0/26
- QQE+SSL+WAE composite: 0/26
- Optimized Trend Tracker: 0/26

Validated 15m research profiles:
- CAPITALCOM:DOGEUSD: Range Filter 60.1%, Schaff Trend Cycle 39.9%.
- CAPITALCOM:ETHUSD: SSL Hybrid 100%.
- CAPITALCOM:USDZAR: AlphaTrend 37.4%, SuperTrend 37.1%, UT Bot 25.5%.
- CBOT:ZB1!: Range Filter 25.7%, Chandelier Exit 25.7%, WAE 20.3%, QQE MOD 14.4%, SSL Hybrid 13.8%.
- CBOT:ZN1!: Schaff Trend Cycle 37.0%, AlphaTrend 35.6%, QQE MOD 27.3%.
- CME:MET1!: WAE 60.8%, UT Bot 39.2%.
- CME_MINI:MJY1!: WaveTrend 36.3%, Schaff Trend Cycle 31.9%, WAE 31.8%.
- COMEX_MINI:MGC1!: QQE MOD 57.0%, SSL Hybrid 43.0%.
- NYMEX:MCL1!: SSL Hybrid 21.1%, QQE MOD 18.7%, Chandelier Exit 16.8%, Range Filter 12.7%, UT Bot 11.2%, Schaff Trend Cycle 11.0%, Squeeze Momentum 8.5%.
- NYMEX:MNG1!: Range Filter 100%.

Interpretation:
- These are research weights, not live trading weights.
- The fact that native 15m strategies produced zero full passes is not permission to weaken gates.
- The 10/26 community successes are strongly symbol-specific and reinforce the no-cross-symbol-inheritance rule.
- The final unseen holdout is still required before any promotion candidate can advance.

### WU-107 — final unseen community holdout
Status: IN IMPLEMENTATION / PR OPEN.
- PR #107 adds a final 15% frozen holdout that is excluded from parameter tuning and development validation.
- First 85% is the complete development set; within it each indicator still uses TRAIN-only tuning and internal TEST/FORWARD validation.
- Final 15% is replayed only after development parameters are frozen.
- Passing the holdout produces only a research promotion candidate; live_authority remains false.
- PR also adds a parallel 26-symbol frozen-confirmation workflow.


## Work-unit register update — 2026-09-24 00:00 EEST

### WU-107 — first frozen holdout implementation
Status: REJECTED / SUPERSEDED / NOT MERGED.
- PR #107 CI: 361 passed, 1 failed.
- Failure exposed a methodology mismatch: helper silently changed the requested 85/15 split when a 500-bar minimum holdout could not be met on the synthetic test history.
- Controlling decision: never silently resize the frozen holdout. Preserve the percentage exactly or fail closed for insufficient history.
- PR #107 closed unmerged.

### WU-108 — exact frozen holdout implementation
Status: IN VERIFICATION.
- PR #108 created from latest main.
- Exact first-85% development / final-15% unseen holdout.
- If the final 15% is smaller than the required confirmation sample floor, the run fails and requires more history instead of changing the split.
- Final holdout can create only a research promotion candidate; live_authority=false.
- CI run #374 pending.


## Work-unit register update — 2026-09-24 00:05 EEST

### WU-108 — exact frozen holdout implementation
Status: VERIFIED / MERGED.
- PR #108 merged as 71d338dc34ec3804b042811c66d98aa7f4b1d89f.
- CI run #374 passed.
- Exact 85/15 frozen split is mandatory.
- Too-short final 15% fails closed; STC does not silently alter the split.
- live_authority=false.

### WU-109 — 26-symbol final unseen 15m confirmation
Status: IN PROGRESS.
- Branch: research/community-frozen-15m-20260924.
- Workflow run id: 35919916518.
- Inputs: same 26 exact-symbol TradingView 15m datasets, 5,000 bars each.
- Development: first 4,250 bars.
- Final unseen holdout: last 750 bars.
- Only components that pass development OOS/forward are eligible for final replay.
- Acceptance: 26 symbol jobs + combined artifact + archived pass/fail reasons; no live promotion in this work unit.


## Work-unit register update — 2026-09-24 00:25 EEST

### WU-110 — shadow registry foundation
Status: VERIFIED / MERGED.
- PR #109 merged as 6f855e16f52a97f662dff79f837326277d4a5a4f.
- CI: 367 passed, 1 warning.
- Six WU-109 frozen survivors were persisted in a research-only registry.
- Registry/API contract rejects live authority.
- Promotion ladder is explicit and cannot skip directly to live use.

### WU-111 — multi-timeframe frozen scan of 15m survivor symbols
Status: VERIFIED / COMPLETED / ARCHIVED.
- Workflow run: 35921398218 — SUCCESS.
- Symbols: USDZAR, XAUUSD, ZB1!, MJY1!, MCL1!.
- Timeframes: 5m, 30m, 1h, derived 2h, 4h, 1D where exact history satisfies the frozen split.
- Same-component support for the original 15m candidates: 0.
- New independent frozen candidates:
  - XAUUSD 5m / SuperTrend;
  - MJY1! 5m / Squeeze Momentum;
  - MCL1! 30m / UT Bot;
  - MCL1! 1h / Hull Suite.
- No candidate receives live authority.
- 2h and some 1D histories fail closed when the exact final 15% cannot meet the minimum evidence floor.

### WU-112 — reusable multi-timeframe research tooling
Status: VERIFIED / MERGED.
- PR #111 merged as 68ad095b9a62d926e9bb61b4b464341ba73c23f7.
- Keeps reusable workflow/runner in main without storing temporary bulk OHLCV input data.

### WU-113 — expanded shadow registry
Status: IN VERIFICATION.
- PR #113 supersedes #110 on current main.
- Target registry: 10 SHADOW component-symbol-timeframe records.
- MULTITF_CONFIRMED remains zero because none of the original 15m components passed the same component on another timeframe.


## Owner continuity checkpoint — 2026-09-24 00:50 EEST

Controlling owner instruction:
- Continue the STC adaptive-strategy program from the last verified state without waiting for repeated chat prompts.
- Preserve all new strategy, indicator, weighting, research-layer, General Lab, validation, and promotion decisions in durable project history before advancing work.
- A future/new chat must be able to continue from repository state alone.

The complete target architecture is therefore fixed as:
1. Native STC strategy matrix per symbol/timeframe.
2. Community/composite indicator discovery catalog, expanded continuously with practical/high-use candidates.
3. Causal/repaint audit before an indicator becomes benchmarkable.
4. Bounded parameter search on TRAIN only.
5. OOS TEST + FORWARD validation.
6. Exact final frozen holdout; insufficient history fails closed.
7. Symbol/timeframe-specific ensemble weights.
8. Redundancy/family normalization so correlated indicators cannot create fake consensus.
9. Shadow registry and multi-timeframe confirmation ladder.
10. Live outcomes accumulated as evidence, with recalibration only on frozen batches/windows.
11. General Lab must automatically inherit the entire PROCESS for every newly added symbol; it never inherits weights from another symbol.
12. Popularity/followers/reviews are discovery priority and qualitative audit evidence only, never direct trading weights.
13. Human manual execution remains mandatory; research never grants broker execution authority.
14. No live A+ / risk / competition rule change without a separate explicit promotion decision.

Current executable community pool in main is 14 components:
- UT Bot Alerts
- Squeeze Momentum
- WaveTrend Crosses
- Hull Suite
- SuperTrend
- Chandelier Exit
- Schaff Trend Cycle
- Range Filter Buy/Sell
- AlphaTrend
- Optimized Trend Tracker
- QQE MOD
- SSL Hybrid
- Waddah Attar Explosion
- QQE + SSL + WAE composite

Current durable research evidence:
- 26-symbol 15m native-vs-community run completed.
- Exact 85/15 final unseen confirmation completed.
- 10 research-only SHADOW records now exist across 15m/5m/30m/1h.
- No same-component multi-timeframe confirmation yet for the original 15m survivors.
- community_indicator_live_authority remains false.

General Lab current runtime boundary:
- Main already exposes protected research-only endpoints for plan/evaluate/shadow-candidates.
- Evaluation requires exact-provider OHLCV series; the hosted STC server cannot itself call the ChatGPT TradingView MCP by ticker.
- Therefore the UI can automate plan/queue/status, but full automatic historical evaluation requires an authorized exact-provider data worker/connector or supplied exact series.
- This limitation must be shown as a data-source blocker, never bypassed with silent provider substitution.

Next implementation order:
A. finish General Lab owner-console/runtime bridge;
B. add durable research-request/queue status so adding a Lab symbol creates a research job request automatically;
C. keep evaluation fail-closed until exact-provider series arrives;
D. continue indicator expansion/audit, prioritizing Lorentzian Classification and other practical high-use composites;
E. extend frozen multi-timeframe scans only where the evidence floor is met;
F. keep all candidates SHADOW until promotion rules are independently satisfied.


## Work-unit register update — 2026-09-24 01:05 EEST

### WU-114 — General Lab durable runtime bridge
Status: VERIFIED / MERGED.
- PR #117 merged as 9469dccfafa1a3b66eaddd8d9e7ff072c5cdb3fa.
- CI: 373 passed, 1 warning.
- Added additive migration hostinger_patch/migrations/004_general_lab_queue.sql.
- Added authenticated hostinger_patch/general_lab.php using existing owner/worker bearer roles.
- General Lab request states:
  - WAITING_FOR_SYMBOL_RESOLUTION;
  - WAITING_FOR_EXACT_HISTORY;
  - RUNNING;
  - EVALUATED;
  - FAILED;
  - CANCELLED.
- Owner Console General Lab now queues durable research requests, displays queue/running/evaluated state, and keeps research isolated from both competition accounts.
- Added app/general_lab_request.py and scripts/run_general_lab_request.py so an authorized exact-data worker can submit exact-provider series to the existing STC research engine and create a completion payload.
- Completed General Lab results remain:
  - execution=research_only;
  - live_authority=false;
  - promotion_required=true.
- Existing SHADOW context is included when a symbol is evaluated.
- No new secret was introduced.
- No broker execution, A+ threshold, risk rule, competition rule, or live research authority changed.
- Deployment still required on Hostinger:
  1. run migration 004 once;
  2. upload general_lab.php;
  3. replace operator.php.
- Data-source boundary remains: Hostinger cannot itself call ChatGPT TradingView MCP; exact-provider history requires an authorized data worker/connector. No provider substitution.


### WU-115 — Wave-two causal community adapters
Status: VERIFIED / MERGED.
- PR #118 merged as 485f6d03479846e9060d82fe6906d6a3de6501b0.
- CI: 378 passed, 1 warning.
- Added research-only causal adapters:
  - Trendilo: percentage change -> ALMA -> RMS state transition.
  - HalfTrend: documented swing-extreme/SMA transition state; confirmed flips only.
  - Endpoint Nadaraya-Watson non-repainting: one-sided Gaussian endpoint estimate + causal MAD envelope.
- Added TRAIN-only bounded parameter grids and prefix-invariance causality tests.
- Added docs/COMMUNITY_WAVE2_AUDIT_20260924.md.
- Original LuxAlgo Nadaraya-Watson repainting output remains excluded.
- Lorentzian Classification remains pending exact semantic audit rather than being approximated.
- VuManChu remains pending confirmation-delay/divergence audit.
- Community implemented pool increases from 14 to 17 research components.
- live_authority remains false.


## Work-unit register update — 2026-09-24 05:21 EEST

### WU-116 — wave-two expanded 17-component frozen 15m confirmation
Status: VERIFIED / COMPLETED / ARCHIVED.
- Workflow run 35926880568: SUCCESS.
- 26/26 competition symbols evaluated on 5,000 exact-provider TradingView 15m bars each.
- Exact frozen method retained:
  - first 4,250 bars development;
  - last 750 bars untouched final holdout.
- New wave-two frozen survivors:
  1. CAPITALCOM:BTCUSD / 15m / Trendilo.
  2. CME_MINI:MJY1! / 15m / Trendilo.
- BTCUSD Trendilo:
  - dev TEST 21 trades, 0.0843R expectancy, PF 1.142;
  - dev FORWARD 27 trades, 0.0955R expectancy, PF 1.188;
  - frozen 22 trades, 0.1953R expectancy, PF 1.387, max DD 7.285R.
- MJY Trendilo:
  - dev TEST 26 trades, 0.1209R expectancy, PF 1.201;
  - dev FORWARD 19 trades, 0.0621R expectancy, PF 1.103;
  - frozen 22 trades, 0.1509R expectancy, PF 1.271, max DD 5.20R.
- HalfTrend: no 15m frozen survivor.
- endpoint Nadaraya-Watson non-repaint: no 15m frozen survivor.
- Durable evidence:
  - research_benchmarks/community_wave2_frozen_15m_run1_summary_20260924.json
  - docs/COMMUNITY_WAVE2_FROZEN_15M_RUN1_20260924.md

### WU-117 — durable 32-candidate community/composite inventory
Status: VERIFIED / MERGED.
- Main commit c45947f328aef83426ac54382535218f1efde707.
- Durable matrix:
  - docs/COMMUNITY_INDICATOR_CANDIDATE_MATRIX_20260924.md
- Catalog inventory: 32 candidate/component families.
- Implemented causal research pool: 17.
- Native-overlap/context-only candidates remain non-independent until overlap audit.
- Pending causal/exact-audit candidates include Lorentzian Classification, VuManChu Cipher B, RSI Kernel Optimized, VWAP Stdev Bands, ML Supertrend variants, AI-SuperTrend KNN, Tri-State Supertrend, Koncorde Plus and %R Trend Exhaustion.

### WU-118 — wave-two SHADOW registry promotion
Status: VERIFIED / MERGED.
- Main commit 3112d3c3d82e96dc4f99312ab3f7a942980d5980.
- Added BTCUSD/15m/Trendilo and MJY1!/15m/Trendilo to research/community_shadow_registry.json.
- Shadow registry total: 12 research-only records.
- live_authority=false remains enforced.
- No owner/live promotion occurred.

### Controlling next research order
1. Run exact-provider multi-timeframe frozen scan for the two Trendilo survivors:
   - CAPITALCOM:BTCUSD;
   - CME_MINI:MJY1!.
2. Seek same-component Trendilo confirmation on 5m/30m/1h/2h/4h/1D where exact history meets evidence floor.
3. Update SHADOW registry only if new independent frozen evidence is produced; same-component support is required before MULTITF_CONFIRMED.
4. Continue exact Lorentzian Classification semantic audit rather than approximating it.
5. Continue VuManChu divergence confirmation-delay audit.
6. Preserve General Lab rule: every new symbol inherits the full process automatically, never another symbol's weights.
7. Do not change live A+ gates/risk/competition rules without separate owner promotion.


## Work-unit register update — 2026-09-24

### WU-119 — Trendilo multi-timeframe frozen confirmation
Status: VERIFIED / COMPLETED / PENDING MERGE.
- Workflow run 35947248551: SUCCESS.
- Symbols: CAPITALCOM:BTCUSD and CME_MINI:MJY1!.
- Timeframes tested: 5m, 30m, 1h, derived 2h, 4h, 1D where exact-provider history met the frozen evidence floor.
- Same-component result:
  - MJY Trendilo passed 15m + 5m + 30m and is now MULTITF_CONFIRMED.
  - BTCUSD Trendilo had no supporting timeframe pass and remains SHADOW.
- New independent frozen candidates:
  - BTCUSD 5m / endpoint Nadaraya-Watson non-repaint;
  - BTCUSD 1D / Hull Suite.
- Existing MJY 5m Squeeze Momentum passed again.
- Registry after update:
  - 16 total records;
  - 3 MULTITF_CONFIRMED records, all MJY Trendilo at 15m/5m/30m;
  - all records live_authority=false.
- Promotion ladder is unchanged. MULTITF_CONFIRMED is still research-only and requires sufficient positive shadow observations before ELIGIBLE_FOR_OWNER_PROMOTION.

### Controlling next research actions
1. Begin formal shadow observation accumulation for MULTITF_CONFIRMED MJY Trendilo without changing live authority.
2. Continue Lorentzian Classification exact semantic/parity audit using the official open-source Pine/Python reference.
3. Continue VuManChu divergence confirmation-delay audit.
4. Preserve General Lab automatic full-process routing for every newly added symbol.
5. Expand practical open-source candidates only after causal/repaint review.
