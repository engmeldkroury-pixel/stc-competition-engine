# R10 robustness extension - 28 September 2026

## Frozen Capital candidate
This note evaluates the already-frozen 15m Capital hypothesis without changing its parameters: session12-17UTC, ADX trend>=30, ADX range<=20, neutral WAIT, trend anti-chase pullback / range extreme fade, initial stop1.5ATR, single target2R.

## Cross-timeframe falsification
The same rule was applied without tuning to higher timeframes, scaling the evaluation horizon to approximately8hours.

30m,2bps proxy:
- train n86 mean -0.169R PF0.737;
- validation n27 mean -0.038R PF0.929;
- historical holdout n23 mean +0.134R PF1.271.

1h,2bps proxy:
- train n104 mean +0.030R PF1.068;
- validation n46 mean +0.203R PF1.561;
- historical holdout n39 mean -0.114R PF0.723.

Decision: do not claim multi-timeframe transfer. The current hypothesis is15m-specific until separate evidence exists.

## AMP out-of-universe falsification
The frozen Capital rule was applied unchanged to16 AMP symbols from the existing project universe: ZB,ZN,MYM,MBT,MET,M2K,M6A,M6B,M6E,MES,MJY,MNQ,MGC,SIL,MCL,MNG. These symbols were not used to select the Capital candidate.

Aggregate15m results:
- gross/no-cost proxy: train n114 +0.236R PF1.460; validation n36 +0.004R PF1.007; holdout n38 +0.101R PF1.183;
- 1bps proxy: train +0.174R; validation -0.051R; holdout +0.042R;
- 2bps proxy: train +0.112R; validation -0.106R; holdout -0.017R.

Several AMP instruments diverged materially from the aggregate. Futures costs are not accurately represented by a universal bps proxy.

Decision: do not transfer the Capital candidate to AMP. AMP needs family-specific futures logic and instrument-aware execution assumptions.

## Competition clocks
Official rules checked28Sep2026:
- Capital.com Africa ends02Oct2026 08:00UTC.
- AMP Futures ends30Sep2026 12:00UTC and requires at least5 trading days for prize eligibility.

The short remaining calendar does not make contaminated historical results forward evidence.

## AMP family-specific audit
After the frozen Capital rule failed to transfer across the full AMP universe, AMP symbols were partitioned into fixed market families and tested with family-appropriate UTC sessions. Candidate selection used train+validation only before exposing the later historical slice.

At a1bps proxy:
- Equity index futures (MYM/M2K/MES/MNQ),13-20UTC: selected trendADX30,stop1.5ATR,target2.5R was train+0.496R,validation+0.479R, then holdout -0.500R. Rejected.
- Rates (ZB/ZN),12-19UTC: no qualifying candidate. Rejected.
- FX micros (M6A/M6B/M6E/MJY),07-17UTC: selected trendADX30,stop2ATR,target2R was train+0.297R,validation+0.433R, then holdout -0.053R. Not promoted.
- Metals (MGC/SIL),11-18UTC: selected trendADX30,stop2ATR,target2R was train+0.026R,validation+0.919R, then holdout -0.856R. Rejected.
- Energy (MCL/MNG),12-19UTC: no qualifying candidate. Rejected.
- Crypto futures (MBT/MET),all sessions: trend-pullback ADX30,stop2ATR,target2R retained a positive later historical slice and was the only family kept for a separate frozen shadow hypothesis.

This reinforces asset-family separation and argues against applying one competition strategy to all AMP instruments.

## AMP crypto frozen historical candidate
The frozen AMP crypto universe is exactly CME:MBT1! and CME:MET1!,15m. Entry requires aligned EMA20/50/200 trend,ADX>=30,ATR-extension and RSI anti-chase bands,and source-candle confirmation. Initial stop2ATR,target2R,horizon32 bars. Historical selection is complete and no historical slice remains unseen for further tuning.

Cost sensitivity:
- 0bps: train n38 +0.130R PF1.272; validation n20 +0.273R PF1.645; inspected holdout n14 +0.376R PF1.877.
- 1bps: +0.115 / +0.258 / +0.362R.
- 2bps: +0.099 / +0.242 / +0.347R.
- 3bps: +0.083 / +0.227 / +0.333R.
- 5bps: +0.052 / +0.196 / +0.305R.

The14-case inspected holdout is evenly split:7MBT and7MET. At1bps MBT mean+0.219R PF1.501; MET mean+0.504R PF2.162. At5bps MBT remains+0.156R PF1.333 and MET+0.453R PF1.994. Sample size remains small and non-prospective.

Neighborhood stress at1bps covered ADX25/30/35,stop1.5/2/2.5ATR,target1.5/2/2.5R. Only6of27 combinations remained positive withPF>1 in train,validation and the already-inspected holdout. The stable region is narrower than the Capital candidate and centers nearADX30.

Decision: freeze the exact AMP-crypto hypothesis for prospective shadow evaluation only. Do not transfer it to AMP index/rates/FX/metals/energy.

## AMP official-instrument reconciliation
Official TradingView competition rules list CME:MBT1! and CME:MET1! as directly tradable competition instruments, with a maximum open position of25 contracts for each. Therefore the frozen AMP-crypto symbols are not proxy tickers outside the competition universe. The inspected rules do not specify a commission/spread schedule, so0/1/2/3/5bps remains sensitivity analysis rather than an exact execution-cost claim.

## Day-cluster uncertainty check
The inspected historical holdout means were stress-tested by resampling whole trading days rather than treating every trade as independent.

Capital frozen candidate at2bps:24 inspected-holdout trades across8days,mean+0.379R. Day-block bootstrap95% interval approximately[-0.289,+1.124]R per trade; about13.8% of bootstrap means were non-positive. Largest absolute day contribution was about+5.875R on2026-09-18.

AMP crypto at1bps:14 inspected-holdout trades across6days,mean+0.362R. Day-block bootstrap95% interval approximately[-0.357,+0.980]R; about16.2% of bootstrap means were non-positive. Largest absolute day contribution was about+4.573R on2026-09-18.

Decision: both historical candidates remain statistically uncertain and day-clustered. Positive inspected means are not sufficient for live promotion. Prospective evidence must be accumulated without retuning and assessed with day clustering/concentration.

## Forward-evidence gate
R10 adds a fail-closed evidence gate for prospective observations. It validates exact protocol SHA, prevents duplicate observations, forbids mixing cost scenarios as independent samples, sorts settled observations chronologically for drawdown, ignores censored rows as wins/losses, reports day concentration and day-block bootstrap uncertainty, and never grants live or automatic-promotion authority. Even a passing statistical gate only produces a candidate for human review.
