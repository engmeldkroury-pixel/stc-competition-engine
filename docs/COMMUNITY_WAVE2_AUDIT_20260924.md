# STC Community Indicator Wave 2 Audit

Updated: 2026-09-24

Purpose: expand practical community/composite research coverage while preserving STC's no-lookahead, no-repaint, OOS/forward/frozen-validation rules.

## Promotion rule

Popularity and reviews are discovery priority only. They never create trading weight, win probability, or live authority.

Every component must pass:
DISCOVERED -> CAUSAL_VERIFIED -> BACKTESTED -> OOS_PASSED -> FORWARD_PASSED -> FROZEN_CONFIRMATION -> SHADOW -> MULTITF_CONFIRMATION -> explicit owner promotion.

## Trendilo

Source:
- https://www.tradingview.com/script/h5kMWewu-Trendilo-OPEN-SOURCE/

Public method:
- percentage change of the selected source;
- ALMA smoothing;
- RMS band around the smoothed percentage-change series;
- bullish state above +RMS;
- bearish state below -RMS;
- neutral state inside the band.

STC implementation:
- independent Python implementation from the published methodology;
- current/past bars only;
- confirmed state-transition signals only;
- bounded parameters selected on TRAIN only;
- no review/popularity contribution to benchmark score.

Status: CAUSAL_VERIFIED adapter; benchmark evidence pending.

## Endpoint Nadaraya-Watson envelope — non-repainting only

Primary source:
- https://www.tradingview.com/script/Iko0E2kL-Nadaraya-Watson-Envelope-LuxAlgo/

Important source warning:
- the original indicator supports a repainting mode;
- the author also provides a non-repainting endpoint mode;
- the publisher states there is no evidence the tool outperforms classical band/envelope methods.

STC implementation:
- separate independent adapter ID: nadaraya_watson_endpoint_nonrepaint;
- one-sided Gaussian endpoint estimate using current/past prices only;
- causal rolling mean absolute deviation envelope;
- contrarian signal only on confirmed upper/lower envelope cross;
- repainting output is never used;
- bounded parameters selected on TRAIN only.

Status: CAUSAL_VERIFIED independent endpoint adapter; benchmark evidence pending.

The original catalog item nadaraya_watson_envelope_luxalgo remains pending_non_repaint_port so STC never confuses the independent endpoint adapter with an exact copy of the third-party implementation.

## Machine Learning: Lorentzian Classification

Primary source:
- https://www.tradingview.com/script/WhBzgfDu-Machine-Learning-Lorentzian-Classification/

Backtest adapter:
- https://www.tradingview.com/script/Pu38F2pB-Backtest-Adapter/

Verified public design facts:
- Lorentzian-distance approximate-nearest-neighbor direction classifier;
- default neighbor count 8;
- default maximum bars back 2000;
- up to five features;
- public feature choices include RSI, WaveTrend, CCI and ADX;
- volatility/regime/ADX filters;
- kernel-regression filter;
- publisher states closed bars do not repaint;
- publisher explicitly warns its on-chart trade-stat table is not a substitute for proper backtesting;
- a dedicated Backtest Stream is exposed for Strategy Tester integration.

Research caution:
- a separate open-source TT-Lorentzian publication reports that the stock/default classifier produced a negative median walk-forward Sortino in that publisher's 50-symbol x 3-timeframe test. This is an external claim, not an STC result, and is recorded only as a reason to insist on independent validation.

STC decision:
- do not build a simplified fake "Lorentzian" and label it as the original;
- keep pending_exact_port until ANN neighbor selection, feature transforms, filters, kernel logic, signal timing and Backtest Stream semantics are reproduced causally and covered by prefix-invariance tests.

Status: HIGH_PRIORITY_AUDIT / NOT YET BENCHMARKABLE.

## HalfTrend

Source:
- https://www.tradingview.com/script/U1SJ8ubc-HalfTrend-everget/

Verified public description:
- open-source ATR-based trend indicator;
- similar purpose to SuperTrend but different trend-identification logic.

STC implementation:
- independent causal implementation of the documented HalfTrend swing-extreme + SMA transition state;
- benchmark emits only confirmed trend flips;
- ATR channel visuals do not create additional entry signals;
- bounded amplitude is selected on TRAIN only;
- prefix-invariance test protects against future-bar dependence.

Status: CAUSAL_VERIFIED adapter; benchmark evidence pending.

## VuManChu Cipher B + Divergences

Source:
- https://www.tradingview.com/script/Msm4SjwI-VuManChu-Cipher-B-Divergences/

Verified public characteristics:
- composite momentum panel with WaveTrend, RSI/money-flow/divergence elements and explicit buy/sell dots;
- the author documented an October 2023 correction because money-flow logic had been behind the momentum waves.

STC decision:
- high-value composite candidate;
- core oscillator logic can be audited separately;
- divergence/pivot evidence must be shifted to the actual confirmation bar, never the historical pivot bar;
- no adapter becomes benchmarkable until this timing audit is explicit.

Status: PENDING_CONFIRMATION_DELAY_AUDIT.

## Review/community evidence policy

Community comments and reviews may record:
- repaint complaints;
- parameter sensitivity;
- practical asset/timeframe observations;
- implementation bugs;
- whether a script is mainly confirmation vs standalone signal.

They do not change the robust score.

## Next benchmark

Once CI accepts the two new causal adapters:
1. run the same exact-provider 5,000-bar 15m dataset used for the prior 26-symbol research;
2. tune only on TRAIN;
3. evaluate TEST and FORWARD untouched;
4. run exact frozen holdout for survivors;
5. compare new survivors to existing native/community profiles using redundancy-aware family normalization;
6. add only frozen survivors to SHADOW;
7. keep live_authority=false.
