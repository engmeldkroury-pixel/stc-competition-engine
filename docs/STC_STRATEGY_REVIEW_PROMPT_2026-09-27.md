# Independent AI Review Prompt — STC Live Strategy A-to-Z

Date: 2026-09-27
Repository: engmeldkroury-pixel/stc-competition-engine
Primary source document: docs/STC_LIVE_STRATEGY_A_TO_Z_2026-09-27.md

You are an independent quantitative-trading, market-microstructure, risk, and software-correctness reviewer.

Your task is NOT to praise the system and NOT to propose a random indicator list. Audit the current STC live strategy as if it were a production competition decision-support engine.

## Mandatory boundaries

- No automatic broker execution.
- Human approval and manual order entry remain mandatory.
- Do not lower or raise risk solely to chase the leaderboard.
- Do not infer win probability from the 84 setup-quality score.
- Separate current LIVE production behavior from SHADOW / research-only components.
- Do not treat code that exists but is not on the live path as part of the active strategy.
- Any proposed live change must include an acceptance test and rollback criterion.

## Read first

1. docs/STC_LIVE_STRATEGY_A_TO_Z_2026-09-27.md
2. docs/STC_FULL_SYSTEM_REVIEW_2026-09-26.md
3. docs/EXTERNAL_AI_REVIEW_TRIAGE_2026-09-27.md
4. PROJECT_STATE.md
5. NEXT_TASK.md

Then inspect these source files:
- app/signals.py
- app/event_decision.py
- app/evidence_engine.py
- app/competition_profiles.py
- app/competition_strategy.py
- app/approval.py
- app/trade_plan.py
- app/risk.py
- app/portfolio.py
- app/calibration_registry.py
- research/calibration_registry.json
- hostinger_patch/approval.php
- hostinger_patch/portfolio_control.php
- hostinger_patch/position.php
- hostinger_patch/macro_control.php
- tradingview/STC_CAPITAL_MTF_FEED_A.pine
- tradingview/STC_CAPITAL_MTF_FEED_B.pine
- tradingview/STC_AMP_MTF_FEED_A.pine
- tradingview/STC_AMP_MTF_FEED_B.pine
- tradingview/STC_AMP_MTF_FEED_C.pine
- tradingview/STC_AMP_MTF_FEED_D.pine

## Review questions

### 1. Direction engine
Audit the exact mathematics of:
- 15m short-term score;
- daily regime;
- blended technical;
- volatility quality;
- liquidity quality;
- base composite.

Look for:
- asymmetric LONG/SHORT behavior;
- discontinuities;
- arbitrary thresholds;
- neutral states accidentally treated as bullish/bearish;
- missing-data effects;
- redundant information.

### 2. MTF design
Audit 15m + 1h + 2h + 4h + 1D + 1M.

Determine:
- whether these are sufficiently independent confirmations;
- whether long-horizon 1M context adds real information to a short competition;
- whether majority-MTF rules lag too much;
- whether closed-bar anti-repaint logic is correct.

### 3. Family evidence
Audit all nine families and their current weights:
- market_structure 16%
- trend 15%
- smc_liquidity 15%
- momentum 11%
- volume 10%
- volatility 10%
- vwap 8%
- price_action 8%
- microstructure 7%

Assess:
- statistical dependence;
- whether breadth/agreement double-counts the same evidence;
- whether the 0.45+0.55*breadth multiplier is justified;
- asset-class bias;
- provider/tick-volume bias.

### 4. Setup quality 84
Audit the exact 0-100 weights:
- 1h 15
- family 15
- short-term 14
- 2h 12
- 4h 12
- daily 12
- monthly 8
- blended technical 6
- volatility 3
- liquidity 3

Important:
neutral 0 gets 50% component credit.

Determine:
- how much truly independent evidence is represented;
- whether 84 is structurally too high/low;
- whether neutral-half-credit makes 84 misleading;
- whether a better scoring transformation exists.

Do NOT pick a new threshold by intuition. Specify the historical/walk-forward experiment that should decide it.

### 5. Boolean gate + quality gate
The live competition trade requires both:
- Boolean gate pass;
- quality >=84.

Determine whether this is:
- useful orthogonal protection;
- redundant double filtering;
- a source of opportunity starvation.

Use gate-failure attribution as the proposed evidence path.

### 6. News/macro discrepancy
The base composite nominally reserves:
- 5% news
- 5% macro

but live bridge supplies both as zero.
Macro is separately enforced as approval blackout.

Determine whether:
- the 10% should remain zero headroom;
- available factors should be renormalized;
- news/macro should be removed from the directional composite entirely;
- a separate risk-only treatment is mathematically cleaner.

### 7. Research/live mismatch
The system contains symbol-specific community research, but:
- community_component_shadow live_authority=false;
- calibration_registry currently has no active records.

Determine whether current live STC is effectively still a generic strategy across assets.
Propose a safe promotion protocol if symbol/asset-specific models are warranted.

### 8. Risk architecture vs competition objective
Current live risk:
- 0.5% per trade;
- 3% portfolio cap;
- 1.5% deterministic cluster cap;
- target2 2.5R.

The owner reports the live Capital leaderboard leader is already above 38%.

Do NOT simply recommend higher risk.
Determine:
- whether STC was optimized for safety rather than competition score;
- whether expected opportunity count × expectancy can plausibly bridge that gap;
- which changes would increase expected return through better edge/opportunity selection rather than mere leverage;
- what evidence would justify any risk change.

### 9. Trade geometry
Audit:
- entry envelope = 0.5 ATR bounded 0.1%-1%;
- stop distance = max(1.2 ATR, 0.2% reference);
- target1 checkpoint = 1.5R;
- target2 = 2.5R.

Evaluate by asset class:
- FX;
- indices;
- metals;
- crypto;
- futures/rates/energy.

Is one geometry appropriate for all?

### 10. Exit management
Audit:
- stop;
- 2.5R target;
- two-bar opposite confirmation;
- closed-bar high-water locking.

Also investigate drift:
- deployed PHP uses single-TP target1 protect mode;
- app/portfolio.py still contains an older partial-take-profit branch.

Specify one authoritative policy and tests.

### 11. Opportunity universe
Capital scans all 10.
AMP core production feed scans 16 while the competition allows many more.

Determine whether AMP starvation is partially universe limitation and how to expand safely without lowering quality.

### 12. Stale account equity
Live sizing uses owner-maintained seed equity:
- Capital 100,000
- AMP 250,000

while platform equity has changed.

Assess severity and propose a fail-closed synchronization method.

## Deliverable format

Return these sections:

1. Executive conclusion: is the main problem signal edge, filtering, risk geometry, opportunity supply, execution, or a combination?
2. P0 correctness bugs — exact file/function/line concept and patch.
3. P1 strategy design problems — evidence and proposed experiment.
4. P2 research hypotheses.
5. Redundancy/double-counting map.
6. Asset-class bias map.
7. A replacement candidate architecture if warranted, but preserve human approval.
8. Exact experiment matrix:
   - baseline;
   - one change at a time;
   - walk-forward;
   - out-of-sample;
   - shadow forward;
   - acceptance/rejection criteria.
9. Which current rules should NOT be changed yet.
10. Top five highest-leverage changes ranked by expected information gain, not by excitement.

Clearly label every statement as:
- VERIFIED FROM CODE;
- INFERENCE;
- HYPOTHESIS;
- RECOMMENDATION.

Do not modify the repository unless explicitly asked after the review.
