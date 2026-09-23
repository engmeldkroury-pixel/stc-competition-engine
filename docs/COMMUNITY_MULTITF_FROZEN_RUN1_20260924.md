# STC Multi-Timeframe Frozen Confirmation — Run 1

Date: 2026-09-24  
Workflow run: 35921398218  
Status: SUCCESS

## Scope
The five symbols that produced the six original 15m frozen survivors were tested again on independent exact-provider timeframes:

- 5m
- 30m
- 1h
- 2h derived only from exact 1h
- 4h
- 1D

The same exact 85% development / 15% unseen frozen confirmation method was used whenever history met the minimum requirement.

## Important result

**None of the six original 15m component candidates passed the final frozen gate again on another tested timeframe.**

Therefore none advances to MULTITF_CONFIRMED yet.

This is a useful fail-closed result: a good 15m component is not assumed to generalize to another timeframe.

## New independent frozen candidates discovered

### CAPITALCOM:XAUUSD — 5m — SuperTrend
- Parameters: ATR 10, multiplier 3.0
- Development TEST: 24 trades, expectancy 0.167R, PF 1.35
- Development FORWARD: 23 trades, expectancy 0.205R, PF 1.41
- Final frozen: 16 trades, expectancy 0.066R, PF 1.11, DD 4.18R

### CME_MINI:MJY1! — 5m — Squeeze Momentum
- Parameters: length 14, BB 2.0, KC 1.5
- Development TEST: 110 trades, expectancy 0.106R, PF 1.19
- Development FORWARD: 105 trades, expectancy 0.368R, PF 1.77
- Final frozen: 98 trades, expectancy 0.270R, PF 1.52, DD 5.65R

### NYMEX:MCL1! — 30m — UT Bot
- Parameters: ATR 10, key 1.0
- Development TEST: 64 trades, expectancy 0.094R, PF 1.23
- Development FORWARD: 68 trades, expectancy 0.043R, PF 1.10
- Final frozen: 63 trades, expectancy 0.264R, PF 1.64, DD 6.41R

### NYMEX:MCL1! — 1h — Hull Suite
- Parameters: length 89
- Development TEST: 102 trades, expectancy 0.129R, PF 1.26
- Development FORWARD: 105 trades, expectancy 0.063R, PF 1.12
- Final frozen: 93 trades, expectancy 0.167R, PF 1.34, DD 6.14R

## No frozen multi-timeframe passes

- CAPITALCOM:USDZAR: no additional timeframe pass.
- CBOT:ZB1!: no additional timeframe pass.
- Original XAUUSD 15m Range Filter did not independently pass another timeframe.
- Original MJY 15m AlphaTrend/WAE did not independently pass another timeframe.
- Original MCL 15m SSL Hybrid did not independently pass another timeframe.

## Provider-history constraints
- 2h is derived from exact 1h. With at most 5,000 source 1h bars, the derived 2h series is roughly 2,500 bars. The final 15% is below the 500-bar frozen minimum, so STC fails closed instead of changing the split.
- Some daily futures/CFD series are also shorter than the exact frozen minimum.
- Insufficient history is not treated as a failed strategy and is not filled from another provider.

## Authority
All results are research-only.

No A+ threshold, risk setting, competition rule, live weight, or trade-execution behavior changed.
