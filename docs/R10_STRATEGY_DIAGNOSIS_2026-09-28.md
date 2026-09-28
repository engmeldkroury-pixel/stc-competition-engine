# R10 strategy diagnosis and frozen shadow protocol - 28 September 2026

## Authority and objective
This is strategy research after the owner reported that the manually executed competition trades have been losing. It does not authorize broker execution, quantity, account changes, approval, live stop/target changes or a promised profitable strategy. Existing live risk remains 0.005 and no current open stop is widened for recovery. The owner also requires zero additional paid infrastructure.

## R9/R10 diagnosis carried forward
R9 already showed that simply shortening the target, moving to breakeven or applying the tested trailing variants did not improve the same historical cohort. R10 therefore tested entry timing, anti-chase logic, initial-stop geometry, strategy family, asset/timeframe specialization, adaptive selection and direct regime/session gating instead of blaming the stop alone.

### Historical overextension hypothesis
On an outcome-independent Capital directional cohort, feature-available accepted cases were materially more extended than rejected directional cases at the source bar:
- thesis-direction distance from 20-bar mean / ATR: accepted mean about 1.967, rejected about 1.181;
- 3-bar thesis momentum / ATR: accepted about 1.560, rejected about 1.106;
- 8-bar thesis momentum / ATR: accepted about 2.414, rejected about 1.300;
- source range / ATR: accepted about 1.485, rejected about 1.174.

This is evidence for a late/chasing-entry hypothesis, not causal proof that the current gate is harmful.

### Short-horizon diagnostic
Using the same independent Capital source-open cohort with the conservative next-full-open model and an approximate 5 bps cost proxy, accepted cases were weak at several horizons and the rejected cohort was sometimes less negative or positive. Missingness and small accepted counts are severe, so this is not a causal gate ranking and is not a reason to invert the live gate.

## Approaches tested and rejected for live promotion
1. Uniform chase/trend-following across the 10 Capital symbols: negative on chronological train, validation and holdout.
2. Simple pullback/reclaim/breakout/mean-pull variants with ATR1.2/1.5/1.8 or swing stops and 1.5/2/2.5R targets: no stable positive train+validation+holdout result.
3. Mean-reversion/Bollinger fade alone: strong in some validation periods, then negative in the later holdout.
4. Per-asset/per-timeframe static selection on 15m/30m/1h: nearly every train+validation winner deteriorated in the later holdout. EURUSD and XAUUSD had no qualifying candidate under the tested rules.
5. Naive walk-forward recent-performance switching (1000-bar trailing calibration, 32-bar purge/embargo, reselect every 200 bars, 2 bps): aggregate 656 trades, mean about -0.157R, PF about 0.775, total about -102.725R. Rejected.
6. Stop widening alone: did not rescue the accepted-plan problem and remains prohibited as a recovery response.

These negative findings are preserved deliberately. They rule out several attractive but unsupported fixes.

## First historically stable region found
A direct regime model was then tested:
- only evaluate source bars during the London/New York overlap;
- ADX >= trend threshold: trade a non-extended EMA20/50/200-aligned pullback;
- ADX <= range threshold: fade a 20-bar z-score extreme;
- intermediate ADX: WAIT.

The first candidate found before neighborhood stress was session 12:00 <= UTC < 17:00, ADX trend >=28, range <=22, initial stop1.5ATR and single target2R. At2bps it was positive on train and validation and only slightly positive in the historical holdout (+0.018R per trade). Because that holdout was subsequently inspected, it is no longer an untouched selection holdout.

### Neighborhood stress
A local grid around the candidate was then tested at2bps: trend ADX25/28/30, range ADX20/22, stop1.5/1.8ATR, target1.5/2.0/2.5R. Of36 nearby combinations,33 were positive on train+validation and18 were positive on train+validation+the already-inspected historical holdout. This is parameter-stability evidence, not fresh out-of-sample proof.

The strongest stable neighborhood moved toward trend ADX>=30, range ADX<=20, stop1.5ATR, target2R. For session12-17UTC at2bps: train n68 mean+0.227R PF1.451; validation n27 mean+0.209R PF1.378; inspected historical holdout n24 mean+0.379R PF1.744.

### Cost and session stress
For ADX30/range20/stop1.5ATR/target2R, session12-17UTC:
- 1bps: train+0.282R, validation+0.248R, inspected holdout+0.437R;
- 2bps: +0.227 / +0.209 / +0.379R;
- 3bps: +0.172 / +0.170 / +0.321R;
- 5bps: +0.063 / +0.093 / +0.205R.

The same rule remained positive in the inspected history when the session boundary was perturbed to11-17,12-16,13-17 and12-18UTC at the tested costs. This reduces concern about a single hour boundary being the entire result.

## Cross-symbol warning
Aggregate results can hide poor symbols. In earlier candidate slices EURUSD and NAS100 were notably negative while BTC/DOGE/USDZAR contributed positively. Eventual promotion therefore requires symbol-level prospective evidence and realistic symbol-specific spread/commission/slippage, not an aggregate-only mean.

## Frozen prospective protocol
Historical search is stopped for the candidate in research_inputs/R10_REGIME_SESSION_FROZEN_PROTOCOL.json. The frozen protocol begins no earlier than 2026-09-28T12:00:00Z:15m;12:00-17:00UTC;trend ADX>=30;range ADX<=20;neutral ADX=>WAIT;trend entry requires aligned EMA20/50/200, limited ATR extension, RSI band and source-candle direction; range entry fades +/-2 z-score with RSI confirmation; initial stop1.5ATR; independent single target2R;32-bar evaluation horizon; cost sensitivity1/2/3/5bps.

The code is app/r10_regime_session_shadow.py. It emits no quantity, approval or execution authority. Synthetic tests cover research boundary, UTC session edges, forward boundary, ADX regimes, LONG/SHORT symmetry, anti-chase behavior, range fades, neutral WAIT and fail-closed invalid input.

Local focused verification before upload: R10-only10 passed; R10+R8 outcome+trade-plan focused set75 passed.

## Promotion rule
Do not tune the frozen protocol using observations at or after the forward boundary. No live promotion should occur merely because the already-inspected historical holdout looked positive. A separate promotion decision needs adequate prospective signals, realistic symbol-specific costs/fills, positive prospective expectancy/PF with acceptable drawdown, no concentration in one symbol/day, source-data and production-code parity, full regression CI, and preservation of manual execution/risk controls unless separately approved.

## Immediate operational conclusion
The evidence does not support trade more, widen the stop, or use a universal smaller TP. The strongest engineering direction is selective session/regime trading, rejecting overextended entries, and using WAIT aggressively when no demonstrated edge exists. This candidate is frozen as a shadow hypothesis so new data can falsify it instead of being used to retune it.
