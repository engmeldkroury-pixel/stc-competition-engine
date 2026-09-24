# STC Community / Composite Indicator Candidate Matrix

Updated: 2026-09-24

This document is the durable inventory for the owner's request to study as many practical free/community indicators as is useful, benchmark each one per symbol/timeframe, and compare them with native STC strategies.

## Rules

- Popularity/use count helps decide what to audit first; it is not a trading weight.
- Reviews/comments help identify repainting, bugs, parameter sensitivity, and practical use cases; they are not a profitability score.
- Every implementable signal must be causal and confirmed-bar safe.
- Every component is tested independently before it can participate in an ensemble.
- A component's weight is symbol/timeframe specific.
- Native STC and community components compete on the same robustness evidence.
- A failed OOS/forward/frozen component receives no deployable research weight.
- Correlated families are normalized so many similar indicators cannot manufacture consensus.
- General Lab applies the same process automatically to new symbols.

## Current inventory

Current catalog size: 32 candidate/component families.

Implemented causal research pool: 20.

### Implemented / benchmarkable

| Component | Family | Approx. public use count recorded in catalog | Current role |
|---|---|---:|---|
| Squeeze Momentum [LazyBear] | volatility_momentum | 3,083,229 | benchmark |
| SuperTrend | atr_trend | 2,226,640 | benchmark |
| UT Bot Alerts | atr_trend | 1,605,966 | benchmark |
| Chandelier Exit | atr_trend | 992,640 | benchmark |
| AlphaTrend | composite_trend | 710,443 | benchmark |
| Hull Suite | trend | 635,066 | benchmark |
| Optimized Trend Tracker | trend | 575,019 | benchmark |
| SSL Hybrid | composite_trend | 558,129 | benchmark |
| WaveTrend Crosses | momentum | 540,320 | benchmark |
| Range Filter Buy/Sell | adaptive_range_trend | 426,291 | benchmark |
| HalfTrend | atr_trend | 415,742 | benchmark |
| QQE MOD | momentum | 406,909 | benchmark |
| Waddah Attar Explosion | volatility_momentum | 180,243 | benchmark |
| QQE + SSL + WAE composite | multi_indicator_composite | 149,806 | benchmark |
| Schaff Trend Cycle | momentum_cycle | 134,434 | benchmark |
| Trendilo | adaptive_momentum | 55,235 | benchmark |
| VuManChu Cipher B + Divergences | composite_momentum | 616,385 | source-audited causal benchmark; divergence emitted at true +2-bar confirmation |
| Endpoint Nadaraya-Watson non-repaint | kernel_reversal | independent STC adapter | benchmark |

### Native-overlap / context only

| Candidate | Family | Approx. use count | Reason not given a separate live weight |
|---|---|---:|---|
| Smart Money Concepts [LuxAlgo] | structure_liquidity | 4,903,394 | STC already has BOS/CHoCH/order-block/FVG/liquidity families; overlap audit first |
| Order Blocks [Flux] | structure_liquidity | 682,000 | native structure/liquidity overlap |
| Market Structure Dashboard [Flux] | mtf_structure_composite | 186,281 | native MTF/structure overlap |
| Williams Vix Fix | volatility_reversal | 1,353,052 | context/reversal detector; asset-specific threshold calibration required |

### Pending causal / exact audit

| Candidate | Family | Approx. use count | Blocking audit |
|---|---|---:|---|
| Lorentzian Classification | machine_learning | 1,229,919 | exact ANN/features/filters/kernel/Backtest Stream semantics |

| RSI Kernel Optimized [Flux] | kernel_reversal | 226,304 | pivot confirmation delay |
| VWAP Stdev Bands v2 | vwap_mean_reversion | 94,046 | exact session/VWAP reset semantics |
| Machine Learning Supertrend [Aslan] | adaptive_trend_ml | 81,568 | adaptive/replay behavior |
| ML SuperTrend TP/SL [YinYang] | machine_learning_trend | 64,443 | exact ML + TP/SL signal semantics |
| AI-SuperTrend KNN | machine_learning_trend | 46,278 | exact KNN training/sample alignment |
| Tri-State Supertrend | range_filtered_trend | 7,612 | exact range-filter transition semantics |
| Nadaraya-Watson Envelope [LuxAlgo] | kernel_regression | n/a | original has repainting and non-repainting modes; only non-repaint is eligible |
| Koncorde Plus | volume_composite | n/a | exact volume/PVI/NVI composite semantics and reliable-volume requirement |
| %R Trend Exhaustion family | reversal | n/a | exact source/version discovery |

## Research priority — not profitability ranking

Priority A:
- Lorentzian Classification: very high use, explicit Backtest Stream, non-trivial independent information family.
- VuManChu Cipher B: source-audited causal adapter now excludes lookahead-on MTF paths and shifts divergence to its true confirmation bar.
- Nadaraya-Watson: non-repainting endpoint variant is now benchmarkable; exact third-party non-repaint parity remains separate.
- HalfTrend/Trendilo: now causal and entering frozen benchmark.

Priority B:
- machine-learning SuperTrend variants after sample-alignment/replay audit.
- Koncorde Plus where reliable real volume exists.
- RSI Kernel Optimized after pivot confirmation is shifted to the true confirmation bar.
- VWAP Stdev Bands where exact session reset behavior can be preserved.

Priority C / overlap study:
- additional SMC/order-block dashboards, because STC already has the same information family.
- simple variants that add no independent evidence beyond existing implemented components.

## Benchmark policy

The comparison table that matters is not popularity. For every symbol/timeframe STC records:
- selected TRAIN-only parameters;
- TEST trades / expectancy / profit factor;
- FORWARD trades / expectancy / profit factor;
- drawdown;
- robust score;
- final frozen holdout trades / expectancy / profit factor / drawdown;
- family redundancy;
- research weight if validated;
- SHADOW / MULTITF status.

That table decides research participation.

## General Lab

Any symbol added to General Lab is processed through the same inventory automatically:
1. resolve exact provider symbol;
2. acquire exact-provider history;
3. classify asset;
4. test native STC strategies;
5. test every compatible implemented community component;
6. train-only tune;
7. OOS TEST + FORWARD;
8. final frozen holdout when evidence is sufficient;
9. redundancy-aware symbol/timeframe research weights;
10. SHADOW status only if the evidence ladder is passed.

No other symbol's weights are copied into the new symbol.
