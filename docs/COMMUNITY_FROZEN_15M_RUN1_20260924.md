# STC Community Frozen 15m Confirmation — Run 1

Date: 2026-09-24  
Workflow run: 35919916518  
Status: SUCCESS

## Method
- 26 competition symbols.
- 5,000 exact-symbol TradingView 15m bars per symbol.
- First 4,250 bars (85%) are the complete development set.
- Final 750 bars (15%) are untouched frozen confirmation.
- Parameter selection occurs only inside development.
- A component must first pass its internal development TEST/FORWARD gates.
- Frozen confirmation then requires minimum sample, positive expectancy, profit factor, controlled drawdown, and no severe degradation.
- Same-bar stop/target ambiguity remains conservative.
- A pass creates only a research promotion candidate; live_authority remains false.

## Result
- Symbols tested: 26/26.
- Symbols with at least one frozen-confirmation survivor: 5/26.
- Total frozen survivors: 6 component-symbol pairs.
- No live A+ gate, risk rule, competition rule, or execution setting changed.

## Frozen promotion candidates

### CAPITALCOM:USDZAR — SuperTrend
- Parameters: atr_period=14, multiplier=3.0.
- Development TEST: 22 trades, expectancy 0.114R, PF 1.23.
- Development FORWARD: 22 trades, expectancy 0.057R, PF 1.13.
- Frozen holdout: 20 trades, expectancy 0.372R, PF 2.06, max drawdown 2.49R.

### CAPITALCOM:XAUUSD — Range Filter
- Parameters: sampling_period=100, range_multiplier=2.0.
- Development TEST: 40 trades, expectancy 0.055R, PF 1.11.
- Development FORWARD: 34 trades, expectancy 0.089R, PF 1.19.
- Frozen holdout: 29 trades, expectancy 0.233R, PF 1.55, max drawdown 2.44R.

### CBOT:ZB1! — Range Filter
- Parameters: sampling_period=100, range_multiplier=3.0.
- Development TEST: 24 trades, expectancy 0.187R, PF 1.37.
- Development FORWARD: 25 trades, expectancy 0.484R, PF 2.36.
- Frozen holdout: 19 trades, expectancy 0.458R, PF 2.09, max drawdown 2.35R.

### CME_MINI:MJY1! — AlphaTrend
- Parameters: period=20, coefficient=1.0.
- Development TEST: 51 trades, expectancy 0.158R, PF 1.27.
- Development FORWARD: 64 trades, expectancy 0.061R, PF 1.10.
- Frozen holdout: 54 trades, expectancy 0.067R, PF 1.11, max drawdown 9.05R.

### CME_MINI:MJY1! — Waddah Attar Explosion
- Parameters: fast=12, slow=26, sensitivity=100, BB=20/2.0, ATR dead-zone=100/3.0.
- Development TEST: 28 trades, expectancy 0.124R, PF 1.23.
- Development FORWARD: 38 trades, expectancy 0.073R, PF 1.12.
- Frozen holdout: 30 trades, expectancy 0.307R, PF 1.60, max drawdown 5.03R.

### NYMEX:MCL1! — SSL Hybrid
- Parameters: baseline_length=100, ssl_length=20.
- Development TEST: 24 trades, expectancy 0.076R, PF 1.13.
- Development FORWARD: 15 trades, expectancy 0.556R, PF 2.31.
- Frozen holdout: 14 trades, expectancy 0.712R, PF 3.05, max drawdown 2.08R.

## Symbols with no final frozen survivor
CAPITALCOM:AUDUSD, CAPITALCOM:BTCUSD, CAPITALCOM:DOGEUSD, CAPITALCOM:ETHUSD, CAPITALCOM:EURUSD, CAPITALCOM:NAS100, CAPITALCOM:SPX500, CAPITALCOM:XAGUSD, CBOT_MINI:MYM1!, CBOT:ZN1!, CME:MBT1!, CME:MET1!, CME_MINI:M2K1!, CME_MINI:M6A1!, CME_MINI:M6B1!, CME_MINI:M6E1!, CME_MINI:MES1!, CME_MINI:MNQ1!, COMEX_MINI:MGC1!, COMEX_MINI:SIL1!, NYMEX:MNG1!.

## Interpretation
- The survivor rate is deliberately low because this is a final unseen test, not a tuning stage.
- Previous run-5 research weights are not automatically promoted.
- DOGEUSD, ETHUSD, ZN1!, MET1!, MGC1!, MNG1! and others that looked promising in development did not survive this final holdout.
- XAUUSD produced a frozen Range Filter candidate even though the earlier full-window run-5 profile did not validate a component; this is a different split and must be treated as a new research candidate, not as proof of live edge.
- The next stage is shadow registry + independent multi-timeframe confirmation; no automatic execution.
