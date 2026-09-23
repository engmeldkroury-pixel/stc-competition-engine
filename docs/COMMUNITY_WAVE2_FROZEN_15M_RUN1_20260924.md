# STC Wave-Two Community Frozen 15m Confirmation — Run 1

Date: 2026-09-24  
Workflow run: 35926880568  
Status: SUCCESS

## Method
- 26 competition symbols.
- 5,000 exact-provider TradingView 15m bars per symbol.
- First 4,250 bars (85%) are the complete development set.
- Final 750 bars (15%) are untouched frozen confirmation.
- Parameters are selected inside development only.
- A component must first pass internal TEST/FORWARD before seeing the final holdout.
- Same-bar stop/target ambiguity remains conservative.
- live_authority=false.

## Expanded pool
The implemented community/composite research pool is now 17 components.

Wave-two additions tested:
- Trendilo.
- HalfTrend.
- Endpoint Nadaraya-Watson non-repainting adapter.

## Final result
- Symbols tested: 26/26.
- Symbols with any frozen survivor: 6/26.
- New wave-two frozen survivors: 2 component-symbol pairs.
- Both new survivors are Trendilo.
- HalfTrend: no 15m frozen survivor in this run.
- Endpoint Nadaraya-Watson non-repaint: no 15m frozen survivor in this run.

## New survivor — CAPITALCOM:BTCUSD / Trendilo
Parameters:
- smoothing=1
- lookback=50
- ALMA offset=0.85
- ALMA sigma=6.0
- RMS band multiplier=1.25

Development TEST:
- trades 21
- expectancy 0.0843R
- PF 1.142
- win rate 42.86%

Development FORWARD:
- trades 27
- expectancy 0.0955R
- PF 1.188
- win rate 40.74%

Final frozen holdout:
- trades 22
- expectancy 0.1953R
- PF 1.387
- win rate 45.45%
- max drawdown 7.285R

## New survivor — CME_MINI:MJY1! / Trendilo
Parameters:
- smoothing=1
- lookback=50
- ALMA offset=0.85
- ALMA sigma=6.0
- RMS band multiplier=1.25

Development TEST:
- trades 26
- expectancy 0.1209R
- PF 1.201
- win rate 38.46%

Development FORWARD:
- trades 19
- expectancy 0.0621R
- PF 1.103
- win rate 42.11%

Final frozen holdout:
- trades 22
- expectancy 0.1509R
- PF 1.271
- win rate 40.91%
- max drawdown 5.20R

## Existing frozen survivors retained by the expanded run
- USDZAR 15m — SuperTrend.
- XAUUSD 15m — Range Filter.
- ZB1! 15m — Range Filter.
- MJY1! 15m — AlphaTrend.
- MJY1! 15m — Waddah Attar Explosion.
- MCL1! 15m — SSL Hybrid.

## Interpretation
- Trendilo produced useful independent evidence on exactly two symbols; it is not treated as a universal winner.
- HalfTrend and endpoint Nadaraya-Watson remain in the research catalog, but receive no frozen-pass status on 15m from this dataset.
- Trendilo passes are promoted only to SHADOW, not to live A+ authority.
- Next step is multi-timeframe confirmation for BTCUSD/MJY Trendilo plus ongoing shadow observation.
