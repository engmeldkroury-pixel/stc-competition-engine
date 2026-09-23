# STC Community Indicator Research Matrix

Updated: 2026-09-23

## Objective

Benchmark practical community indicators per symbol and timeframe, compare them with native STC strategies on the same out-of-sample/forward evidence standard, and build a symbol-specific research ensemble without weakening the live A+ gate.

This subsystem is research-only until a component passes frozen confirmation and is explicitly promoted.

## Core rule

A component never receives live weight because it is popular or highly reviewed.

Popularity, editor picks, comments, and community reviews are discovery/prioritization metadata only.

Trading participation is driven by:
- causal confirmed-bar signals;
- exact symbol and timeframe;
- train/test/forward separation;
- out-of-sample expectancy;
- forward expectancy;
- profit factor;
- drawdown;
- sample size;
- stability where available.

A community indicator may receive a larger research weight than a native STC strategy if its out-of-sample/forward robust score is higher on that exact symbol/timeframe.

## Per-symbol matrix

For every competition symbol:
- Capital.com Africa: 10 production symbols.
- AMP Futures: 16 production symbols.

And for every General Lab symbol supplied to the research runner:

1. determine asset class;
2. enumerate all compatible community indicators;
3. run each implemented indicator independently;
4. benchmark using next-bar entry after confirmed signal;
5. use conservative same-bar stop/target handling;
6. split history into train/test/forward segments;
7. reject weak, undersampled, degraded, or high-drawdown trials;
8. compare validated community trials with validated native STC strategy trials;
9. derive a symbol/timeframe research weight profile.

Weights are not inherited across symbols. A strong BTCUSD result does not automatically give the same indicator weight on ZN, EURUSD, gold, or MES.

## Continuous learning

Every live trade/outcome may be accumulated as new evidence, but STC must not change weights after every single trade.

Recalibration must happen only after a frozen evaluation batch/window with enough new observations. This prevents recency chasing and online overfitting.

Recommended promotion path:

historical backtest -> out-of-sample -> forward -> frozen confirmation -> research weight -> live shadow observation -> explicit live promotion

## Initial catalog

### Implemented causal research adapters
- UT Bot Alerts family
- Squeeze Momentum [LazyBear] family
- WaveTrend with Crosses family
- Hull Suite family
- SuperTrend family
- Chandelier Exit family
- Schaff Trend Cycle family
- Range Filter Buy/Sell family

These are independent conceptual implementations based on public algorithm descriptions. Third-party source code is not copied into STC.

### Pending exact-port / verification
- Machine Learning: Lorentzian Classification
- QQE MOD
- Optimized Trend Tracker
- HalfTrend
- SSL Hybrid
- AlphaTrend
- VuManChu Cipher B + Divergences
- Trendilo
- Nadaraya-Watson Envelope non-repainting mode

These require exact causal semantics and repaint/lookahead review before benchmarking.

### Native-proxy / double-counting check
- Smart Money Concepts [LuxAlgo]

STC already has BOS, CHoCH, order-block, FVG, liquidity, structure, and price-action families. The community implementation must be used first as a cross-check benchmark; it must not automatically duplicate existing structure/liquidity weight.

### Discovery queue
- %R Trend Exhaustion family
- CM Williams Vix Fix family
- additional open-source community indicators discovered through TradingView/community review research

## Source/review seed list

TradingView source pages:
- https://www.tradingview.com/script/WhBzgfDu-Machine-Learning-Lorentzian-Classification/
- https://www.tradingview.com/script/Pu38F2pB-Backtest-Adapter/
- https://www.tradingview.com/script/n8ss8BID-UT-Bot-Alerts/
- https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/
- https://www.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/
- https://www.tradingview.com/script/hg92pFwS-Hull-Suite/
- https://www.tradingview.com/script/TpUW4muw-QQE-MOD/
- https://www.tradingview.com/script/zVhoDQME/
- https://www.tradingview.com/script/CnB3fSph-Smart-Money-Concepts-SMC-LuxAlgo/

Community review/discussion seeds:
- https://www.reddit.com/r/TradingView/comments/1jbq7f2/top_3_community_indicators_on_tradingview/
- https://www.reddit.com/r/TradingView/comments/1lqg6ra/best_tradingview_indicators_3_years_experience/
- https://www.reddit.com/r/algotrading/comments/zxh9vb/is_the_ut_bot_alerts_indicator_legit_or_does_it/
- https://www.reddit.com/r/TradingView/comments/12gsrc9/ut_bot_alerts_linreg_candles_heikin_ashi/
- https://www.reddit.com/r/TradingView/comments/1ccl46q

Community reports are evidence about usability, repaint concerns, or discovery priority. They are not proof of profitability.

## Live boundary

This PR does not:
- authorize any trade;
- change the A+ gate;
- change risk limits;
- change competition rules;
- automatically deploy any community indicator to live production;
- use reviews/popularity as a probability estimate.

The research output is exposed by app.research_runner under:
- community_indicator_trials
- community_ensemble_profiles
- community_indicator_live_authority = false


## Train-only parameter selection

Community indicators are not compared with one arbitrary default setting. Each implemented adapter now has a bounded parameter grid. STC selects the parameter set on the training segment only, then freezes it for test and forward segments. The test/forward segments cannot choose or tune parameters.

This preserves the intended per-symbol specialization without letting the same out-of-sample data both choose and judge the configuration.

## Expanded popularity/discovery snapshot

The current discovery catalog includes several widely used open-source scripts, including SuperTrend, Chandelier Exit, AlphaTrend, VuManChu Cipher B, SSL Hybrid, Range Filter, HalfTrend, and Williams Vix Fix. Popularity can move a script higher in the research queue, but cannot improve its benchmark score or ensemble weight.


## Discovery wave 2

The discovery pool was expanded to include:
- Koncorde Plus — volume composite; only where reliable volume exists.
- RSI (Kernel Optimized) | Flux Charts — KDE pivot probability; requires explicit confirmation-delay handling because pivots use bars on both sides.
- VWAP Stdev Bands v2 — session VWAP mean-reversion/continuation context.
- Order Blocks | Flux Charts — volumized structure/liquidity proxy; double-counting audit required.
- Market Structure Dashboard | Flux Charts — MTF composite; double-counting/information-gain audit required.
- Machine Learning Supertrend [Aslan] — adaptive optimizer; must be replayed sequentially, never hindsight-optimized.
- AI-SuperTrend KNN — pending exact causal port.
- Machine Learning SuperTrend Strategy [YinYangAlgorithms] — pending exact causal port.
- Tri-State Supertrend — explicit range state intended to reduce trend whipsaw.

## General Lab automatic research interface

STC now exposes two research-only API routes:
- POST /research/general-lab/plan
- POST /research/general-lab/evaluate

The plan route expands any supplied General Lab symbols through the same per-symbol/timeframe strategy + community-indicator research matrix.

The evaluate route accepts exact-provider multi-timeframe OHLCV series and runs the same research runner used by STC. Output is explicitly research-only, live_authority=false, and requires later promotion before any live decision authority.


## Composite indicator wave 3 — 2026-09-23

The catalog now also benchmarks a practical composite stack frequently used as an executable public strategy:

- QQE MOD — dual QQE agreement plus Bollinger-style zero-line confirmation.
- SSL Hybrid — STC uses a causal baseline/SSL1 entry adapter for research; the full third-party script is not copied.
- Waddah Attar Explosion — MACD/Bollinger momentum/explosion state with ATR dead-zone filtering.
- QQE MOD + SSL Hybrid + Waddah Attar Explosion composite — entry is allowed only when the QQE direction change, SSL baseline state and WAE explosion direction agree on the same confirmed bar.

Public TradingView descriptions explicitly document the composite strategy's long/short conditions and recommend parameter tuning/backtesting. The public author reports better behavior on longer timeframes than on the shortest intraday windows, so STC does not assume one universal timeframe; each symbol/timeframe must earn its own OOS/forward evidence.

Source pages:
- https://www.tradingview.com/script/TpUW4muw-QQE-MOD/
- https://www.tradingview.com/script/C3MlAWCw-SSL-Hybrid/
- https://www.tradingview.com/script/d9IjcYyS-Waddah-Attar-Explosion-V2-SHK/
- https://www.tradingview.com/script/YCob5r03-QQE-MOD-SSL-Hybrid-Waddah-Attar-Explosion/
- https://www.tradingview.com/script/as3c4gh4-QQE-MOD-SSL-Hybrid-Waddah-Attar-Explosion-Indicator/

The adapters are independent causal research implementations. They must still pass the same train/test/forward gate before receiving any research weight.
