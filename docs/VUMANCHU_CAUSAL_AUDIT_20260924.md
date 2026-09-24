# VuManChu Cipher B Causal Source Audit

Date: 2026-09-24

## Research purpose
Audit the public VuManChu Cipher B + Divergences logic and convert only reproducible, causal signal semantics into STC research. This is not a live recommendation and does not grant live authority.

## Public sources inspected
- TradingView source page:
  https://www.tradingview.com/script/Msm4SjwI-VuManChu-Cipher-B-Divergences/
- Public Pine strategy mirror used to inspect explicit formulas and timing:
  https://github.com/fmzquant/strategies/blob/master/VuManChu-Cipher-B-Divergences-Strategy.md

## Source findings
1. Default WaveTrend settings in the inspected source are channel 9, average 12 and signal MA 3.
2. Explicit large-dot buy intent:
   - WaveTrend crosses up;
   - signal wave is oversold.
3. Explicit large-dot sell intent:
   - WaveTrend crosses down;
   - signal wave is overbought.
4. Regular divergence uses a five-bar fractal centered two bars in the past.
5. The public plot visually uses offset=-2 for divergence markers. That is valid chart annotation but is not a causal execution timestamp.
6. Some Sommi / higher-timeframe candle code uses barmerge.lookahead_on. Those paths are not eligible for STC causal research.
7. The source itself warns that circles/triangles are information and are not certain trade instructions, and notes that defaults were mainly discussed for higher timeframes.

## STC causalization decision
STC independently implements:
- confirmed WaveTrend oversold cross-up as LONG evidence;
- confirmed WaveTrend overbought cross-down as SHORT evidence;
- regular WaveTrend divergence as weaker supporting evidence;
- divergence emitted only on the bar where the centered pivot becomes knowable, i.e. pivot + 2 bars.

STC explicitly excludes:
- backdated divergence execution;
- any Sommi/HTF path dependent on lookahead_on;
- social/reputation claims as performance evidence;
- the simplified mirror strategy rule wt2 < wt1 / wt2 > wt1 as a substitute for the original explicit buy/sell-dot semantics.

## Validation requirements
- prefix-invariance causality test;
- dedicated divergence timing test proving no event at the historical pivot and event only at confirmation;
- TRAIN-only bounded parameter selection;
- untouched TEST/FORWARD;
- frozen 85/15 confirmation for survivors;
- symbol/timeframe-specific weighting only;
- live_authority=false until the normal promotion ladder is completed.

## Component identity
- indicator_id: vumanchu_cipher_b
- family: composite_momentum
- implementation status after this audit: implemented_conceptual
