# STC Live Trading Strategy — A-to-Z Technical Specification

Date: 2026-09-27  
Scope: CURRENT LIVE/PRODUCTION STRATEGY, not research wish-list  
Repository: engmeldkroury-pixel/stc-competition-engine  
Primary decision timeframe: 15 minutes  
Execution boundary: human approval + manual order entry only

---

## 0. Critical context before reviewing the strategy

This document describes what the code actually does today.

Important distinctions:

- Capital and AMP both run under the live `COMPETITION_OPPORTUNITY` policy with setup-quality floor 84/100.
- The strict non-competition path uses 90/100.
- Community / symbol-specific research components are currently SHADOW ONLY and have no live authority.
- `research/calibration_registry.json` is currently empty, therefore the live family engine uses the same default family priors for all symbols; no validated symbol-specific runtime calibration is active.
- News and macro are present as nominal 5% + 5% fields in the base composite formula, but the current live signal path passes them as zero and reports them as unavailable. Macro is instead used later as an approval blackout/risk control.
- Current live account-state risk fraction is 0.5% for both competitions.
- Current live account-state equity values remain owner-maintained seed values:
  - Capital: 100,000 USD
  - AMP: 250,000 USD
  These are not automatically synchronized to the current TradingView competition equity.

---

# A. Market universe

## Capital.com Africa

The production system scans all 10 allowed Capital symbols:

1. CAPITALCOM:BTCUSD
2. CAPITALCOM:ETHUSD
3. CAPITALCOM:DOGEUSD
4. CAPITALCOM:EURUSD
5. CAPITALCOM:AUDUSD
6. CAPITALCOM:USDZAR
7. CAPITALCOM:XAUUSD
8. CAPITALCOM:XAGUSD
9. CAPITALCOM:SPX500
10. CAPITALCOM:NAS100

Official/open-position caps configured in STC:

- BTCUSD: 0.5
- ETHUSD: 15
- DOGEUSD: 500,000
- EURUSD: 800,000
- AUDUSD: 1,200,000
- USDZAR: 800,000
- XAUUSD: 75
- XAGUSD: 5,000
- SPX500: 40
- NAS100: 10

## AMP Futures

The competition profile contains a much wider allowed universe, but the current production MTF core feed actively covers 16 symbols:

1. CME_MINI:MES1!
2. CME_MINI:MNQ1!
3. CBOT_MINI:MYM1!
4. CME_MINI:M2K1!
5. NYMEX:MCL1!
6. NYMEX:MNG1!
7. COMEX_MINI:MGC1!
8. COMEX_MINI:SIL1!
9. CME_MINI:M6E1!
10. CME_MINI:M6B1!
11. CME_MINI:MJY1!
12. CME_MINI:M6A1!
13. CME:MBT1!
14. CME:MET1!
15. CBOT:ZN1!
16. CBOT:ZB1!

This narrower production universe is an explicit item for strategic review because it can restrict opportunity supply.

---

# B. Data timing / anti-repaint architecture

Production feed timeframe: 15m.

The TradingView feed sends only on:
- `barstate.isconfirmed`
- `barstate.isrealtime`

The contextual timeframes are built from already closed higher-timeframe bars:

- entry / family evidence: 15m confirmed bar
- confirmation: previous closed 1h bar
- MTF trend: previous closed 2h bar
- MTF trend: previous closed 4h bar
- historical regime: previous closed 1D bar
- structural long horizon: previous closed 1M bar

The 1h/2h/4h/1D/1M contexts use prior closed values to reduce lookahead/repaint contamination.

---

# C. 15m short-term technical score

Function: `short_term_score_from_tradingview()`

Score starts at 0 and is clipped to [-1, +1].

### 1. EMA structure — weight 0.35
- close > EMA20 > EMA50 => +0.35
- close < EMA20 < EMA50 => -0.35
- otherwise => 0

### 2. MACD — weight 0.30
- MACD > signal => +0.30
- otherwise => -0.30

### 3. RSI14
- RSI 50..70 => +0.20
- RSI 30..<50 => -0.10
- otherwise => 0

### 4. Relative volume
If volume_ratio >= 1.5:
- if the accumulated score is >= 0 => +0.15
- if accumulated score is < 0 => -0.15

No additional volume score below 1.5.

### Review note
The zero case is treated as bullish for the volume add-on because the code uses `score >= 0`. This deserves independent review for direction symmetry.

---

# D. Daily historical-regime score

Function: `historical_regime_from_tradingview()`

Requires complete 1D history bundle. If any required field is missing, historical regime is None and the competition gate fails because historical context must be present.

Score:

- close >= EMA50: +0.15, else -0.15
- EMA50 >= EMA200: +0.20, else -0.20
- close >= EMA200: +0.15, else -0.15
- 20-day momentum >= 0: +0.10, else -0.10
- 63-day momentum >= 0: +0.10, else -0.10
- 126-day momentum >= 0: +0.10, else -0.10
- 252-day momentum >= 0: +0.10, else -0.10
- 252-day range location:
  - >= 65% of range => +0.10
  - <= 35% => -0.10
  - otherwise => 0

Clipped to [-1,+1].

Historical RSI, ATR and volatility are transported in the payload but are NOT used in this historical-regime score.

---

# E. Blended technical score

Function: `factors_from_tradingview()`

If historical regime exists:

`technical = 0.65 * short_term_15m + 0.35 * daily_historical_regime`

If historical regime is unavailable:

`technical = short_term_15m`

This blended technical is later reused in both the base composite and the gate/quality system.

---

# F. Live volatility quality

Function: `volatility_quality_from_tradingview()`

First compute:

`range_ATR = (15m high - 15m low) / ATR14`

Raw quality:
- 0.40 <= range/ATR <= 1.80 => +0.50
- 0.20 <= range/ATR <= 2.50 => +0.20
- range/ATR > 3.00 => -0.80
- otherwise => -0.20

This quality is then aligned with the sign of the blended technical thesis.

Therefore volatility does not create LONG/SHORT direction by itself; it rewards or penalizes the existing technical direction.

---

# G. Live liquidity / participation quality

Function: `liquidity_quality_from_tradingview()`

Uses 15m `volume_ratio = volume / SMA(volume,20)`.

Raw quality:
- ratio >= 1.50 => +0.60
- ratio >= 0.80 => +0.30
- ratio >= 0.40 => 0.00
- ratio < 0.40 => -0.50

Then aligned with the sign of the blended technical thesis.

Again, liquidity cannot create direction by itself.

---

# H. Base composite score

Function: `evaluate()`

Nominal formula:

- technical: 60%
- news: 5%
- macro: 5%
- volatility quality: 15%
- liquidity quality: 15%

`composite = 0.60*T + 0.05*News + 0.05*Macro + 0.15*VolQ + 0.15*LiqQ`

Direction:
- composite >= +0.35 => LONG
- composite <= -0.35 => SHORT
- otherwise => WAIT

### Current live reality
In the live bridge path, News and Macro are not supplied into the factor request, therefore both are currently 0.

Effective live composite today is therefore:

`composite_live = 0.60*T + 0.15*VolQ + 0.15*LiqQ`

The nominal remaining 10% is zero rather than re-normalized.

The displayed `confidence = abs(composite)` is not a calibrated win probability.

---

# I. 1h confirmation score

Function: `confirmation_score_from_tradingview()`

Uses the previous fully closed 1h bar.

- close > EMA20 > EMA50 => +0.30
- close < EMA20 < EMA50 => -0.30
- otherwise 0

- EMA50 >= EMA200 => +0.20
- else => -0.20

- MACD >= signal => +0.20
- else => -0.20

RSI:
- 50..68 => +0.15
- 32..<50 => -0.15
- otherwise => 0

If volume ratio >= 1.0:
- close >= EMA20 => +0.15
- else => -0.15

Clipped to [-1,+1].

---

# J. 2h and 4h trend score

Both use the same formula on the previous closed higher-timeframe bar:

- close > EMA20 > EMA50 => +0.30
- close < EMA20 < EMA50 => -0.30
- otherwise 0

- EMA50 >= EMA200 => +0.20
- else -0.20

- MACD >= signal => +0.20
- else -0.20

RSI:
- 52..72 => +0.15
- 28..48 => -0.15
- otherwise 0

If relative volume >= 1.0:
- green/flat-up bar => +0.15
- red bar => -0.15

Clipped to [-1,+1].

---

# K. 1M structural trend score

Uses previous closed monthly bar.

- close > EMA6 > EMA12 => +0.35
- close < EMA6 < EMA12 => -0.35
- otherwise 0

- EMA12 >= EMA24 => +0.25
- else -0.25

- MACD(6,13,5) >= signal => +0.20
- else -0.20

- RSI14 >= 52 => +0.20
- RSI14 <= 48 => -0.20
- otherwise 0

Clipped to [-1,+1].

The competition gate does not require monthly agreement; it only requires monthly evidence to be present and not strongly opposed.

---

# L. Nine 15m evidence families

These are calculated directly in the production Pine feed.

## 1. Trend family
`0.55*trendDir + 0.25*(EMA50 vs EMA200) + 0.20*(MACD vs signal)`

Where:
- clean bull EMA structure => trendDir +1
- clean bear EMA structure => -1
- otherwise close >= EMA50 => +0.30
- otherwise -0.30

## 2. Momentum family
- normalized RSI: 40%
- normalized Stochastic: 25%
- normalized MACD spread / ATR: 35%

## 3. Volatility family
Uses range/ATR quality multiplied by trend direction.

Pine family range/ATR raw values:
- 0.40..1.80 => +0.60
- 0.20..2.50 => +0.20
- >3.00 => -0.80
- otherwise => -0.20

Note: the separate live volatility factor uses +0.50 for the first band, while the family-volatility formula uses +0.60.

## 4. Volume family
`bar_direction * participation`

Participation:
`clamp((volume_ratio - 0.70) / 1.00, 0, 1)`

## 5. VWAP family
`clamp((close - VWAP) / ATR)`

## 6. Market-structure family
`0.65*BOS + 0.35*trendDir`

BOS:
- close > previous 20-bar high => +1
- close < previous 20-bar low => -1
- otherwise 0

## 7. SMC / liquidity family
`0.50*sweep + 0.20*FVG + 0.30*displacement`

Sweep:
- break prior high but close back below => -1
- break prior low but close back above => +1

FVG:
- low > high[2] => +1
- high < low[2] => -1

Displacement:
- candle body >= 1.20 ATR => current candle direction
- otherwise 0

## 8. Price-action family
`0.55*engulfing + 0.45*CLV`

CLV = close-location value within the current candle range.

## 9. Microstructure family
`bar_direction * (0.60*body_efficiency + 0.40*participation)`

where body efficiency = abs(close-open)/(high-low).

---

# M. Family aggregation weights

Current default live priors:

| Family | Weight |
|---|---:|
| market_structure | 16% |
| trend | 15% |
| smc_liquidity | 15% |
| momentum | 11% |
| volume | 10% |
| volatility | 10% |
| vwap | 8% |
| price_action | 8% |
| microstructure | 7% |

Total = 100%.

The family engine calculates:
1. weighted directional average;
2. weighted agreement ratio;
3. aligned-family count;
4. conflicting-family count.

Breadth penalty:

`breadth = min(1, aligned_families / 6)`

`family_score = weighted_score * (0.45 + 0.55*breadth)`

Aligned family:
`sign * family_value >= 0.35`

Conflicting family:
`sign * family_value <= -0.35`

### Current calibration reality
No runtime calibration record is active because `research/calibration_registry.json` contains zero records.

Therefore:
- no symbol-specific family-weight override is currently active;
- no validated strategy-family multiplier is currently active in the live decision path.

---

# N. Community / indicator composite status

The following research machinery exists:
- symbol-specific community profiles;
- HalfTrend;
- Trendilo;
- SSL Hybrid;
- Range Filter;
- Schaff;
- Lorentzian and other research candidates.

However:

`community_component_shadow.live_authority = false`

These components are recorded for research/shadow evaluation but do NOT change:
- live recommendation;
- setup-quality score;
- 84 gate;
- position size;
- execution ticket.

This distinction is important when reviewing whether the current live strategy already contains the research indicators discussed during development.

---

# O. Setup-quality score — 0 to 100

This is NOT win probability.

For LONG the component value is used directly.
For SHORT the sign is inverted so bullish/bearish quality is measured in the active trade direction.
Missing optional evidence is mapped to -1 before normalization, so it contributes zero rather than accidentally benefiting SHORT.

Each component is normalized:

`normalized = clamp((direction_aligned_value + 1)/2, 0, 1)`

Weights:

| Component | Weight |
|---|---:|
| 1h confirmation | 15% |
| family evidence score | 15% |
| short-term 15m technical | 14% |
| 2h trend | 12% |
| 4h trend | 12% |
| 1D historical regime | 12% |
| 1M trend | 8% |
| blended technical | 6% |
| volatility quality | 3% |
| liquidity quality | 3% |

Total = 100%.

Important mathematical property:
- a neutral value 0 contributes 50% of its component weight;
- missing value contributes 0% of its component weight.

---

# P. Competition Opportunity gate — live gate for Capital + AMP

A trade must pass BOTH:
1. the Boolean competition gate;
2. setup quality >= 84/100.

Boolean requirements:

1. base recommendation is LONG or SHORT;
2. daily historical context is present;
3. 1h confirmation context is present;
4. at least 2 of {1h,2h,4h} have directional alignment >= +0.35 in trade direction;
5. short-term 15m technical >= +0.55 in trade direction;
6. blended technical >= +0.45;
7. base composite >= +0.35;
8. daily historical regime >= -0.15, i.e. not strongly opposed;
9. monthly evidence is present;
10. monthly trend >= -0.15, i.e. not strongly opposed;
11. family evidence is present;
12. family score >= +0.25;
13. family agreement >= 0.55;
14. at least 4 of 9 families aligned;
15. no more than 3 family conflicts;
16. volatility quality >= 0;
17. liquidity quality >= 0;
18. setup quality >= 84.

If any condition fails:
- final recommendation becomes WAIT;
- no locked trade plan is produced.

---

# Q. Strict A+ gate

Outside competition mode the stricter path requires setup quality >= 90 and materially stronger thresholds, including:

- 1h >= 0.70
- 2h >= 0.65
- 4h >= 0.65
- monthly >= 0.55
- family >= 0.45
- agreement >= 0.65
- at least 5 aligned families
- <=2 conflicts
- short-term >=0.75
- historical >=0.55
- blended >=0.70
- composite >=0.45
- volatility >=0.20
- liquidity >=0.30

Capital and AMP currently use the 84 competition gate, not this A+ gate.

---

# R. Locked entry envelope

Once a signal passes, STC builds an approval envelope.

Reference price = confirmed signal close.

Entry tolerance:

`tolerance = 0.5*ATR / reference_price`

bounded to:
- minimum 0.10%
- maximum 1.00%

Entry zone:
- entry_min = reference * (1 - tolerance)
- entry_max = reference * (1 + tolerance)

For a 15m signal the approval envelope remains valid for 30 minutes after the source bar close.

Other freshness rules:
- owner quote evidence <= 60 seconds old;
- market must be open;
- price must still be inside the envelope at approval;
- latest signal must not oppose the locked direction;
- safe mode / kill switch must be off.

---

# S. Macro event filter

News/macro do not currently drive the live composite direction.

But a separate approval-level macro filter is active.

Default behavior:
- block new approval 45 minutes BEFORE a High-impact relevant-currency event;
- block new approval 30 minutes AFTER;
- if calendar is unavailable and fail-closed is enabled => block approval.

Relevant currencies are mapped by symbol.

Current external calendar source is the configured weekly economic-calendar JSON endpoint, not the TradingView signal itself.

---

# T. Trade-plan geometry

Constants:

- stop ATR multiple = 1.20
- target 1 checkpoint = 1.50R
- final target = 2.50R

Entry midpoint:
`entry_mid = (entry_min + entry_max)/2`

Minimum stop distance:
`max(1.20*ATR, 0.20% of reference price)`

LONG:
- stop = entry_min - stop_distance
- target1 = entry_mid + 1.5R
- target2 = entry_mid + 2.5R

SHORT:
- stop = entry_max + stop_distance
- target1 = entry_mid - 1.5R
- target2 = entry_mid - 2.5R

The levels are frozen.
Later bars do not silently reprice the original plan.

---

# U. Approval / anti-churn checks

Before an approved execution ticket exists:

- safe_mode must be false;
- kill_switch must be false;
- signal cannot be WAIT;
- quality gate must still be eligible;
- locked plan must exist;
- no open position may already exist on the same competition + symbol;
- same-symbol, same-direction recent-loss cooldown must be inactive;
- signal must not be expired;
- newer signal must not oppose locked direction;
- macro blackout must be clear;
- owner must confirm current platform quote and market-open status;
- current risk capacity must remain available.

Cooldown:
`max(30 minutes, 2 * decision_timeframe)`

For current 15m feed:
- cooldown = 30 minutes.

---

# V. Current risk sizing

Current LIVE account-state values from production readback:

| Competition | Equity used by sizing | Risk fraction |
|---|---:|---:|
| Capital | 100,000 USD | 0.50% |
| AMP | 250,000 USD | 0.50% |

These are owner-maintained and currently still equal to the seed values, not live platform equity.

Per-trade configured risk:
`equity * 0.005`

Therefore current configured base risk budgets are:
- Capital: about 500 USD/trade
- AMP: about 1,250 USD/trade

Portfolio initial-risk cap:
`6 * per-trade risk`
= 3.0% of configured equity.

Correlation-cluster initial-risk cap:
`3 * per-trade risk`
= 1.5% of configured equity.

Risk budget actually used:
`min(per_trade_budget, remaining_portfolio_capacity, remaining_cluster_capacity)`

Capital commission assumption:
- 0.01% each side in the current formula;
- round-trip commission is included in risk-per-unit.

AMP:
- integer contracts only;
- configured competition commission in STC profile is 0.

Capital:
- fractional quantities allowed in STC arithmetic;
- broker/order-ticket quantity-step still needs manual confirmation.

---

# W. Correlation / concentration model

The live risk system currently uses deterministic clusters, NOT statistical rolling correlation.

Clusters:

- equity_indices
- crypto
- metals
- fx_usd
- energy
- rates
- other

Examples:
- NAS100 + SPX500 are one equity_indices cluster.
- BTC/ETH/DOGE are one crypto cluster.
- XAU/XAG are one metals cluster.

Cluster risk is capped at 1.5% of configured equity under the current 0.5% risk fraction.

No live rule currently says:
- correlation > 0.70 subtract score;
- correlation > 0.85 block.

Those ideas remain research proposals only.

---

# X. Execution ticket

If all approval checks pass, STC issues an execution ticket containing:

- competition;
- symbol;
- direction;
- approved quote;
- entry zone;
- initial stop;
- final TP;
- MAX quantity;
- risk amount;
- risk budget;
- risk fraction;
- suggested manual order type.

Rules:
- do not exceed quantity;
- smaller quantity is allowed;
- manual execution only.

If the actual fill exceeds the STC risk ticket, the server refuses to record it as an STC-compliant plan fill.

---

# Y. Position management — CURRENT PRODUCTION PHP behavior

The production Hostinger supervisor is controlling here.

Exit immediately if:
1. active stop is breached;
2. final target2 is reached;
3. two consecutive closed-bar signals strongly confirm the opposite direction.

Opposite-signal threshold:
- two consecutive opposite recommendations;
- composite magnitude at least 0.55 against the position.

## Closed-bar high-water protection

Peak R is calculated from closed signal-history prices since the position opened.

Dynamic locked floor:

- peak >= 3.0R => lock max(1.75R, peak - 0.60R)
- peak >= 2.5R => lock max(1.50R, peak - 0.75R)
- peak >= 2.0R => lock 1.25R
- peak >= 1.5R => lock 0.75R
- peak >= 1.0R => lock 0.25R

If current R falls below the earned locked floor:
- EXIT_NOW.

Otherwise:
- suggest a tightened stop at the locked-R level;
- never loosen an existing protective stop.

## Target1 behavior

Current production PHP is SINGLE-TP mode.

At target1:
- keep full quantity;
- protect stop at least to breakeven;
- do NOT automatically recommend 50% partial.

Final target remains target2 = 2.5R.

### Important code-consistency note
`app/portfolio.py` still contains an older/alternate target1 branch that suggests a 50% partial.
The deployed Hostinger `portfolio_control.php` instead uses the current single-TP/protect mode.
This Python/PHP semantic drift should be reviewed.

---

# Z. Competition pace layer

The competition clock does NOT lower the 84 quality threshold.

Phases:
- BUILD_SCORE
- QUALIFICATION_URGENT
- CATCH_UP
- PROTECT_SCORE
- FINAL_WINDOW
- ENDED

Time pressure can:
- broaden scanning;
- reduce/increase the suggested size band within existing controls;
- prioritize top setups.

It does NOT automatically:
- bypass the gate;
- lower 84;
- override official position limits;
- remove human approval.

---

# Current strategic mismatch with a >38% leaderboard

With current live base risk of 0.50% and a final target of 2.50R:

A fully risk-budgeted trade reaching final target is approximately:
`0.50% * 2.50 = +1.25%`
before friction and before position/cluster caps.

Therefore a leaderboard above 38% represents a substantially more aggressive return objective than the current STC production risk architecture was designed to pursue.

This does not prove the signal logic is bad.
It does prove that the objective function and the current risk/return architecture must be reviewed together.

---

# Review flags — highest-value questions for independent AIs

## 1. Double-counting / dependence
The same price trend can influence:
- short-term score;
- blended technical;
- base composite;
- 1h/2h/4h scores;
- family trend/momentum/market structure;
- setup-quality score;
- Boolean gate.

Question:
How much truly independent information exists after correlation/redundancy control?

## 2. Neutral-value scoring
Quality normalization maps 0 to 50% credit.

Question:
Should neutral evidence contribute half-credit, or should a quality score represent affirmative evidence only?

## 3. News/macro 10% zero weight
The base composite reserves 10% for news+macro, but live event decision currently sends zero.

Question:
Should live weights be renormalized to 100% of available factors, or is the intentional 10% headroom desirable?

## 4. Short-term volume zero-case
`score >= 0` gives a +0.15 volume add-on when pre-volume score is exactly zero.

Question:
Is that an unintended LONG bias?

## 5. Family-volatility inconsistency
Pine family volatility uses +0.60 for normal range/ATR, while Python live volatility factor uses +0.50.

Question:
Is this deliberate or drift?

## 6. Symbol-specific research is not live
Calibration registry has no records and community shadow has no live authority.

Question:
Was the intended design to use validated symbol-specific strategy routing already, or only after forward evidence?

## 7. AMP opportunity coverage
Competition profile permits far more AMP contracts than the 16-symbol production core feed.

Question:
Is opportunity starvation partly universe restriction rather than gate strictness?

## 8. Account equity is stale/manual
Position sizing currently uses seed account equity, not current competition equity.

Question:
Should owner-confirmed equity be refreshed daily / before approval, or should a safer read-only synchronization mechanism be added?

## 9. Risk objective mismatch
0.5% risk + 2.5R final target is conservative relative to a current competition leader above 38%.

Question:
What risk architecture can be justified by forward evidence without simply increasing risk to chase rank?

## 10. Management parity
Python and production PHP differ at target1.

Question:
Which one is the controlling policy, and should one shared management contract eliminate drift?

---

# Files an independent reviewer should inspect

Core live strategy:
- app/signals.py
- app/event_decision.py
- app/evidence_engine.py
- app/competition_profiles.py
- app/competition_strategy.py
- app/approval.py
- app/trade_plan.py
- app/risk.py
- app/portfolio.py

Production / operator:
- hostinger_patch/approval.php
- hostinger_patch/portfolio_control.php
- hostinger_patch/position.php
- hostinger_patch/macro_control.php
- hostinger_patch/cloud_control.php

TradingView production feeds:
- tradingview/STC_CAPITAL_MTF_FEED_A.pine
- tradingview/STC_CAPITAL_MTF_FEED_B.pine
- tradingview/STC_AMP_MTF_FEED_A.pine
- tradingview/STC_AMP_MTF_FEED_B.pine
- tradingview/STC_AMP_MTF_FEED_C.pine
- tradingview/STC_AMP_MTF_FEED_D.pine

Research/shadow:
- app/community_shadow.py
- app/community_indicator_signals.py
- app/calibration_registry.py
- research/calibration_registry.json

---

# Review discipline

An external reviewer should separate:
- LIVE production behavior;
- dead/unused code;
- research-only/shadow logic;
- operational controls;
- hypotheses not yet validated.

Do not infer a win probability from the 84 setup-quality score.
Do not suggest arbitrary higher leverage/risk solely because the leaderboard is high.
Any live strategy change should have an explicit test, acceptance criterion, and rollback path.
