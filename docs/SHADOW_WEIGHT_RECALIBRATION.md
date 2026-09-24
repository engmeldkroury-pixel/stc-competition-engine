# Frozen Shadow Weight Recalibration

Updated: 2026-09-24

## Purpose
Implement the owner's adaptive-weight rule without allowing one recent trade to move the live system.

Every observed shadow outcome may be stored immediately, but weights may be recalculated only from a sealed/frozen batch with enough observations.

## Rules
- No recalibration from an open/growing batch.
- Default minimum: 30 exact symbol/timeframe/component observations.
- Duplicate observation ids fail closed.
- Positive/negative expectancy, profit factor, directional hit rate and drawdown all influence the research candidate weight.
- Hit rate is shrunk toward 50% and sample confidence grows gradually.
- One batch may change a component by at most 25% relative by default.
- Negative expectancy or PF below 1 cannot increase weight.
- Components without enough new evidence keep the prior weight.
- Candidate weights are normalized only within the same symbol/timeframe profile.
- The output remains research-only: live_authority=false.
- No output is treated as a probability of trade success.

## Promotion boundary
A recalibrated candidate weight must still pass the existing frozen/SHADOW/MULTITF and explicit owner-promotion governance before it can influence live A+ behavior.

This module does not write production weights and does not execute trades.
