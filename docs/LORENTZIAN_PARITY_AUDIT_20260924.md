# STC Lorentzian Classification Exact Parity Audit

Date: 2026-09-24

## Decision

STC will not use an approximate reimplementation of Machine Learning: Lorentzian Classification.

The benchmarkable research component is pinned to the public MIT reference port from:

- repository: artificial-intelligence-edge/lorentzian-classification
- source commit: 27776bd51cbd3e07b6383cfa468d4d33f4b50297
- upstream TradingView lineage: jdehorty Lorentzian Classification + Backtest Stream

Vendored reference files are stored under:

- app/_vendor/lorentzian_classification/

The original MIT license and copyright notice are retained.

## Parity gate

Before STC can benchmark Lorentzian, the vendored calculation must reproduce an official Pine/TradingView export fixture.

Pinned fixture:

- tests/fixtures/lorentzian/pine_btcusd_h1_trimmed_limited_history.csv

The parity contract compares:

- F1 RSI;
- F2 WaveTrend;
- F3 CCI;
- F4 ADX;
- F5 RSI9;
- kernel regression estimate;
- prediction;
- direction;
- buy;
- sell;
- stop-buy;
- stop-sell;
- Backtest Stream.

Numeric tolerance is 1e-6. Discrete signals must match exactly.

## Exact reference semantics retained

The reference implements:

- RSI / WaveTrend / CCI / ADX feature engineering;
- Lorentzian-distance approximate nearest-neighbor classification;
- neighbor cadence and prediction state;
- volatility filter;
- regime filter;
- optional ADX/EMA/SMA filters;
- rational-quadratic / Gaussian kernel filters;
- start-long/start-short signals;
- fixed/dynamic exit logic;
- hidden Backtest Stream.

STC does not rewrite these semantics to improve historical results.

## Causal research profile

The upstream default limited-history chart behavior uses the final chart index with max_bars_back=2000. That is valid for reproducing the TradingView display, but it makes early historical signal availability depend on the final chart length.

STC therefore separates two modes:

1. parity mode:
   - exact upstream defaults;
   - used only to prove Pine/reference equivalence.

2. causal benchmark mode:
   - same exact classifier/filter implementation;
   - include_full_history=True;
   - causal_history_cap=10,000, deliberately above the current 5,000-bar TradingView research dataset;
   - fails closed if a research series is as long as or longer than the cap.

This removes final-chart-length suppression while preserving the actual indicator mathematics.

## TRAIN-only parameter search

After parity is established, STC may compare a small bounded research grid:

- neighbors_count = 6;
- neighbors_count = 8;
- neighbors_count = 12.

Everything else starts from the pinned reference defaults unless a later independently justified research experiment is added.

Parameter selection occurs inside TRAIN only. TEST, FORWARD, and final frozen holdout cannot tune the configuration.

## Weighting and authority

Lorentzian is treated like every other community component:

- symbol/timeframe specific;
- no cross-symbol weight inheritance;
- no popularity-based weight;
- no review-based probability;
- must pass OOS TEST + FORWARD;
- must pass final frozen holdout before SHADOW;
- requires formal promotion ladder after SHADOW.

live_authority=false.

No A+ threshold, risk rule, competition rule, or broker execution behavior is changed by this audit.
