# GPT-6 Pro / Codex Work — Final STC Full-System Independent Audit + Execution Roadmap Prompt

## Mission

Act as an **independent principal quantitative researcher, trading-systems architect, software-correctness reviewer, risk engineer, production-reliability reviewer, and competition-strategy auditor**.

You are reviewing the entire **STC (Smart Trading / Competition) system** end to end — not only the trading formula. Review everything that can directly or indirectly affect whether STC can generate, approve, communicate, supervise, and evaluate high-quality competition trades reliably.

Your job in this pass is **AUDIT + DIAGNOSIS + FINAL IMPLEMENTATION PLAN**.

### Do NOT modify the repository in this first pass.
Do not commit, patch, deploy, change thresholds, change risk, edit production, create migrations, or alter live signals.

The final deliverable must be a **complete execution roadmap that we can implement afterwards inside this same project, one controlled batch at a time**.

---

# 0. Non-negotiable boundaries

1. **Human approval remains mandatory.**
2. **Manual broker/order entry remains mandatory.**
3. **No automatic broker execution.**
4. Do not recommend increasing risk merely to chase leaderboard rank.
5. Do not infer a win probability from the `84` setup-quality score.
6. Separate:
   - LIVE production behavior;
   - SHADOW/research behavior;
   - dead/legacy code;
   - planned-but-not-wired behavior.
7. Every important conclusion must be labeled as one of:
   - `VERIFIED_FROM_CODE`
   - `VERIFIED_FROM_LIVE_EVIDENCE`
   - `INFERENCE`
   - `HYPOTHESIS`
   - `RECOMMENDATION`
8. If summaries, comments, docs, and code disagree, **code + current live evidence win**.
9. Do not expose secrets, tokens, private SSH keys, passwords, or GitHub secrets.
10. Do not rewrite or redesign the entire project unless the evidence proves the current architecture is unsalvageable.
11. Prefer small, testable, reversible changes.
12. Do not change live behavior in the review phase.
13. Do not use the leaderboard gap alone as justification for leverage or looser risk.
14. If repository access is unavailable, stop and say so. Do not fabricate a code audit.

---

# 1. Repository and current authority

Repository:

`engmeldkroury-pixel/stc-competition-engine`

Branch:

`main`

Treat current `main` as the code baseline.

Before reviewing strategy, reconstruct the current project state from source and state files.

Read at minimum:

## Project/state/governance
- `PROJECT_STATE.md`
- `NEXT_TASK.md`
- `HANDOFF.md`
- `DECISIONS.md`
- `TEST_REGISTER.csv`
- `RISK_REGISTER.csv`
- `BATCH_REGISTER.csv`
- `docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md`

## Current strategy/review documents
- `docs/STC_LIVE_STRATEGY_A_TO_Z_2026-09-27.md`
- `docs/STC_FULL_SYSTEM_REVIEW_2026-09-26.md`
- `docs/EXTERNAL_AI_REVIEW_TRIAGE_2026-09-27.md`
- `docs/EXTERNAL_AI_REVIEW_TRIAGE_ROUND1_2026-09-27.md`
- `docs/STC_STRATEGY_REVIEW_PROMPT_2026-09-27.md`
- `docs/LEDGER_RECONCILIATION_EVIDENCE_2026-09-27.md`

Also read any newer strategy/review/state file if present.

---

# 2. Inspect the ACTUAL live strategy code

Read and trace call paths, not isolated files.

At minimum:

## Python decision engine
- `app/signals.py`
- `app/event_decision.py`
- `app/evidence_engine.py`
- `app/competition_profiles.py`
- `app/competition_strategy.py`
- `app/approval.py`
- `app/trade_plan.py`
- `app/risk.py`
- `app/portfolio.py`
- `app/calibration_registry.py`
- `app/community_shadow.py`
- `app/community_indicator_signals.py`
- `app/asset_classification.py`
- `app/probability.py`

## Production PHP / Hostinger
- `hostinger_patch/approval.php`
- `hostinger_patch/portfolio_control.php`
- `hostinger_patch/position.php`
- `hostinger_patch/operator.php`
- `hostinger_patch/operator_snapshot.php`
- `hostinger_patch/cloud_control.php`
- `hostinger_patch/macro_control.php`
- `hostinger_patch/account_state.php`
- `hostinger_patch/notification_control.php`

## TradingView production feeds
- `tradingview/STC_CAPITAL_MTF_FEED_A.pine`
- `tradingview/STC_CAPITAL_MTF_FEED_B.pine`
- `tradingview/STC_AMP_MTF_FEED_A.pine`
- `tradingview/STC_AMP_MTF_FEED_B.pine`
- `tradingview/STC_AMP_MTF_FEED_C.pine`
- `tradingview/STC_AMP_MTF_FEED_D.pine`

## Research / calibration
- `research/calibration_registry.json`
- relevant research runners, walk-forward code, shadow promotion code, datasets and reports.

## Tests
Inspect all tests that define or assert:
- signal math;
- setup-quality math;
- missing-evidence behavior;
- competition gate;
- MTF behavior;
- Pine causality / anti-repaint;
- risk sizing;
- position limits;
- cluster caps;
- cooldown;
- approval freshness;
- macro blackout;
- target1/target2 management;
- high-water protection;
- shadow promotion;
- walk-forward;
- deployment/readback.

---

# 3. Reconstruct the LIVE call graph

Produce a verified end-to-end map:

`TradingView confirmed bar`
→ Pine payload
→ webhook/bridge ingestion
→ event processing
→ factors
→ direction
→ MTF context
→ family evidence
→ setup-quality score
→ Boolean competition gate
→ locked trade plan
→ macro/risk/duplicate/cooldown checks
→ owner confirmation
→ execution ticket
→ manual order entry
→ position ledger
→ portfolio supervisor
→ Telegram/operator output
→ closed trade/research attribution.

For every stage state:
- file;
- function;
- input;
- output;
- authority;
- failure behavior;
- whether it is live, shadow, legacy, or unused.

Identify any point where:
- data can go stale;
- a failure becomes silent;
- a default changes semantics;
- one layer assumes another layer already validated something;
- Python and PHP can disagree;
- stored history can distort current logic.

---

# 4. Current known live facts that MUST be independently verified

Do not accept these blindly; verify them in code/live artifacts:

1. Capital and AMP currently use:
   - `COMPETITION_OPPORTUNITY`
   - quality floor `84/100`.
2. Non-competition strict path uses `90/100`.
3. Base feed timeframe is 15m.
4. Context includes prior closed:
   - 1h;
   - 2h;
   - 4h;
   - 1D;
   - 1M.
5. Community/symbol-specific research is currently shadow-only.
6. `research/calibration_registry.json` currently has no active records.
7. Default live family priors are therefore generic across symbols.
8. Live base composite nominal weights:
   - technical 60%;
   - news 5%;
   - macro 5%;
   - volatility 15%;
   - liquidity 15%.
9. Live bridge currently supplies news=0 and macro=0 to the direction composite.
10. Macro is separately enforced as approval blackout/risk control.
11. Setup-quality score 84 is separate from the base composite.
12. Missing optional setup-quality evidence is intentionally penalized and direction-symmetric.
13. Neutral value `0` in the setup-quality transform receives 50% component credit.
14. Current owner-maintained account state is approximately:
   - Capital 100,000 USD;
   - AMP 250,000 USD;
   - risk_fraction = 0.005.
15. Account equity is not automatically synchronized with current platform equity.
16. Production PHP uses single-TP / target1-protect behavior.
17. `app/portfolio.py` contains an older target1 partial-profit behavior.
18. Capital production covers all 10 competition symbols.
19. AMP production MTF core covers 16 symbols while the allowed competition profile is wider.
20. Execution is manual-only.
21. Duplicate same-symbol open-position block exists.
22. Same-symbol/same-direction post-loss cooldown exists.
23. Portfolio cap and deterministic asset-risk cluster cap exist.
24. Live statistical rolling correlation is NOT currently used.
25. Closed-bar high-water profit protection exists.
26. Ledger reconciliation was completed and current platform truth should override stale historical assumptions.

---

# 5. Current operational/live evidence to audit

Use the latest available Live Readback / operator snapshot / persisted gate audit.

Known recent diagnostic snapshot to verify against current evidence:

## Capital
- rows examined: about 320;
- directional rows: about 135;
- current-84 structural proxy passes: about 2;
- recent failure counts included roughly:
  - intraday_majority_alignment: 92;
  - family_direction_alignment: 85;
  - short_term_strength: 64;
  - family_breadth: 58;
  - liquidity_quality: 14;
  - setup_quality_below_78: 14;
  - family_agreement: 5;
  - trend_1m_not_strongly_opposed: 5;
  - historical_not_strongly_opposed: 4;
  - setup_quality_below_84: 3;
  - family_conflicts: 2;
  - volatility_quality: 1.

## AMP
Known diagnostic history was roughly:
- rows examined: 80;
- directional rows: 16;
- current-84 structural proxy passes: 0.

Important caveat:
some AMP stored rows may predate the latest shared 84 deployment.

### Your task
Verify the latest numbers and determine:
- what truly starves opportunities;
- what only appears to starve them;
- whether failure reasons are causally useful filters or redundant restatements of the same trend state.

Do NOT infer filter usefulness from failure count alone.
A filter that rejects 100 trades may be excellent if the rejected trades lose.

---

# 6. External-review claims that need adjudication

We have already received multiple Claude/Gemini/other AI reviews.

Do not agree with them automatically.

For EACH claim below, classify:
- VERIFIED;
- PARTIALLY VERIFIED;
- REJECTED;
- UNTESTED HYPOTHESIS.

Then cite exact code/evidence.

## A. Opportunity starvation
Claim:
STC's main problem is low opportunity velocity.

Test with:
- candidate count;
- directional count;
- gate pass count;
- actual trade count;
- rejected-trade outcomes.

## B. Evidence double-counting
Claim:
EMA/MACD/trend information is re-used across:
- short-term;
- 1h/2h/4h;
- daily/monthly;
- blended technical;
- family trend/momentum/structure;
- setup quality;
- Boolean gate.

Quantify actual effective dimensionality rather than only visual similarity.

## C. Neutral-half-credit
Claim:
`0 -> 50%` in the setup-quality transform may make 84 misleading.

Important:
distinguish:
- a real neutral value = 0;
- missing evidence = None / absent.

Verify that missing evidence does NOT receive neutral half-credit.

## D. Missing MTF
Claim:
missing 1h/2h/4h may accidentally count as neutral/bullish.

This was previously believed to be false.
Verify from current code/tests.

## E. News/macro zero injection
Claim:
news/macro zero directly corrupts the 84 score.

This was previously believed to be wrong because news/macro affect base composite, not `setup_quality_score()`.

Trace the actual call graph and settle this definitively.

Then separately answer:
- does zeroing 10% attenuate the base composite?
- should available weights be renormalized?
- should news/macro be removed from direction and remain risk-only?

## F. Monthly 1M drag
Claim:
remove 1M because it blocks short-term competition trades.

Do NOT decide by intuition.

Measure:
- incremental failures attributable only to 1M;
- monthly/daily agreement;
- marginal predictive value;
- ablation results.

## G. Boolean gate + 84
Claim:
the two are redundant double filtering.

Measure disagreement cases:
- Boolean pass + quality <84;
- Boolean fail + quality >=84;
- both pass;
- both fail.

Then calculate forward outcome distribution for each group.

## H. Family breadth
Claim:
`0.45 + 0.55*breadth` can punish concentrated strong signals and reward mediocre broad agreement.

Test, do not assume.

## I. ATR / geometry bounds
Claim:
0.1%-1.0% entry bounds and 0.2% stop floor bias FX/crypto/metals.

Measure actual boundary-hit frequency by symbol and asset class before recommending removal.

## J. Risk architecture
Claim:
0.5% risk + 2.5R final target is mathematically mismatched to a live leaderboard >38%.

Do not recommend more leverage by default.

Calculate:
- realistic number of remaining opportunities;
- historical/OOS expectancy;
- expected return distribution;
- max drawdown;
- probability of reaching different score bands under current edge/risk;
- same under candidate evidence-backed risk settings.

Use risk changes only after signal/selection edge is proven.

## K. AMP universe
Claim:
16-symbol feed creates opportunity starvation.

Quantify expected marginal opportunity supply and data/operational cost from expanding the universe.

## L. Generic model problem
Claim:
because calibration registry is empty and community research has no live authority, one generic strategy is applied across different asset classes.

Verify exactly what is generic and what is symbol/asset-specific today.

## M. Python/PHP exit drift
Verify target1 behavior and every other management semantic.

## N. Stale equity
Verify exactly how current equity is used in:
- risk budget;
- max quantity;
- portfolio cap;
- cluster cap;
- approval ticket.

## O. Potential LONG bias
Review:
`if volume_ratio >= 1.5: +0.15 if score >= 0 else -0.15`

If pre-volume score is exactly zero, does elevated volume create a bullish bias?

## P. RSI asymmetry
Review any short-term rule equivalent to:
- RSI 50–70 => +0.20
- RSI 30–<50 => -0.10

Determine whether this is intentional, empirically justified, or an accidental directional bias.

## Q. Volatility-score drift
Verify whether Pine family volatility uses +0.60 for the normal ATR band while the Python live volatility factor uses +0.50.

Determine if deliberate or inconsistent.

---

# 7. Quantitative audit required

Do not stop at code review.

Design the exact research needed to determine whether STC's current strategy has real edge.

## Required diagnostics

### 7.1 Rejected-trade outcome attribution
For every directional candidate:
- timestamp;
- symbol;
- side;
- all component values;
- quality score;
- Boolean result;
- exact failed clauses;
- entry reference;
- ATR;
- candidate stop/target geometry;
- forward MFE;
- forward MAE;
- whether +1R, +1.5R, +2R, +2.5R hit before stop;
- time to stop/target;
- session;
- asset class;
- macro state.

This is the highest-priority experiment.

### 7.2 Correlation / redundancy
Calculate:
- Pearson;
- Spearman;
- VIF if appropriate;
- PCA/effective dimensionality;
- mutual-information or nonlinear dependence where useful.

Inputs:
- short-term;
- 1h;
- 2h;
- 4h;
- daily;
- monthly;
- blended;
- composite;
- 9 families;
- family score/agreement/breadth;
- volatility;
- liquidity;
- final quality.

Do this globally AND by:
- symbol;
- asset class;
- LONG vs SHORT;
- session/regime.

### 7.3 Ablation
One change at a time:
- remove/downweight 1M;
- remove blended duplicate;
- family breadth on/off;
- family score only vs family score+agreement+breadth;
- neutral transform;
- base-composite renormalization;
- symmetric RSI;
- zero-case volume fix;
- quality gate only;
- Boolean gate only;
- both;
- selected MTF combinations.

### 7.4 Asset-class geometry
For each symbol/class:
- how often entry min floor binds;
- how often entry max cap binds;
- how often stop % floor binds;
- ATR-at-signal;
- spread/slippage if available;
- MFE/MAE;
- best empirically stable ATR stop;
- best stable R target;
- whether trailing/high-water beats fixed target.

### 7.5 Walk-forward / OOS
No in-sample-only conclusions.

Use:
- rolling train/test;
- purging/embargo if labels overlap;
- final untouched holdout;
- forward shadow after historical validation.

Report:
- expectancy R;
- profit factor;
- win rate;
- opportunity count/day;
- max DD;
- average adverse excursion;
- average favorable excursion;
- score calibration;
- long/short symmetry;
- stability by symbol/class.

### 7.6 Threshold research
Do not simply say “change 84 to 75/78/80”.

Sweep candidate thresholds and show:
- coverage;
- expectancy;
- drawdown;
- stability;
- false negatives;
- confidence intervals.

Then use bootstrap/block-bootstrap Monte Carlo only as robustness validation AFTER OOS trade sequences exist.

---

# 8. Competition-objective audit

The owner reports the live Capital leaderboard leader is already above 38%.

Treat this as a competition-objective problem, but not as permission to gamble.

Answer:

1. Is current STC mathematically capable of producing enough expected score under:
   - current opportunity count;
   - current risk;
   - current edge;
   - remaining competition time?
2. Is the bottleneck:
   - edge;
   - filtering;
   - opportunity universe;
   - trade geometry;
   - risk size;
   - exit management;
   - manual execution latency;
   - operational reliability;
   - some combination?
3. Which improvements increase expected score by improving **edge or opportunity quality**, not just leverage?
4. Only after edge is proven, what risk settings should be tested in shadow/backtest?
5. What is the probability distribution of competition-score outcomes under:
   - current policy;
   - each candidate policy?

Do not make rank or win guarantees.

---

# 9. Operational reliability audit

Review everything that can prevent a good signal from reaching the owner.

Audit:
- TradingView alert coverage;
- Pine feed coverage;
- 15m close timing;
- duplicate/missed webhook risk;
- webhook ingestion;
- bridge worker retries;
- GitHub Actions reliability;
- transient network failures;
- 403/edge failures;
- stale queue items;
- processing latency;
- signal freshness;
- approval freshness;
- Telegram delivery;
- operator snapshot parity;
- Hostinger deployment/readback;
- deployment rollback;
- live vs repo drift;
- logging and observability;
- CI coverage.

Quantify:
- signal loss rate;
- duplicate rate;
- average ingestion latency;
- average decision latency;
- notification latency;
- stale-signal rejection rate.

Distinguish strategy starvation from transport starvation.

---

# 10. Data-provider and market-data audit

For each asset class determine:
- whether volume is true volume, tick volume, broker proxy, or unavailable;
- session behavior;
- gaps;
- rollover/continuous-contract issues;
- spread/commission/slippage assumptions;
- price multiplier correctness;
- provider symbol mapping;
- futures contract multipliers;
- UTC/session alignment.

Verify especially:
- Capital CFDs;
- CME/CBOT/NYMEX/COMEX futures;
- FX;
- crypto;
- metals;
- indices;
- rates;
- energy.

Identify any place where the same threshold is applied to fundamentally different data quality.

---

# 11. Position sizing / risk / portfolio audit

Audit:
- account equity freshness;
- risk_fraction;
- price-value conversions;
- commissions;
- quantity rounding;
- official maximum open positions;
- symbol caps;
- portfolio cap;
- cluster cap;
- cluster definitions;
- deterministic cluster vs statistical correlation;
- existing-position duplicate block;
- same-direction loss cooldown;
- current open risk;
- stale ledger effects;
- manual_external positions;
- approval vs fill re-sizing;
- whether actual fill can exceed ticket;
- whether current stop updates correctly change open risk.

Verify that all calculations remain correct after:
- partial closes;
- stop moves;
- manually entered positions;
- ledger reconciliation;
- changing equity.

---

# 12. Position-management audit

Audit every exit condition:

- active stop breach;
- target2;
- target1 management checkpoint;
- high-water protection;
- opposite two-bar confirmation;
- thesis degradation;
- stale signal history;
- market close/gap;
- macro event proximity;
- competition final window.

Compare:
- Python;
- PHP;
- tests;
- operator output;
- Telegram message behavior.

Produce ONE authoritative management contract.

Do not change it yet; propose the contract and migration/test plan.

---

# 13. Research/shadow audit

Review all existing research work, not just the live engine.

Inventory:
- community indicators;
- HalfTrend;
- Trendilo;
- SSL Hybrid;
- Range Filter;
- Schaff;
- Lorentzian;
- QQE/SSL/WAE composite;
- native families;
- any symbol-specific profile;
- shadow promotion registry;
- calibration registry;
- walk-forward engine;
- research datasets.

For each:
- current status;
- provider/data used;
- sample size;
- OOS status;
- forward status;
- causal/non-repainting status;
- why it was rejected/not promoted;
- whether it should remain dead, shadow, or be retested.

Do not promote anything just because it looks promising.

---

# 14. Strategy architecture review

After all measurements, answer whether STC should remain:

### Option A — current architecture with calibrated patches
or
### Option B — simplified orthogonal architecture
or
### Option C — asset-class/symbol-specific routing
or
### Option D — hybrid.

If you propose a replacement architecture, it must preserve:
- human approval;
- manual execution;
- auditable locked plans;
- fail-closed risk;
- deterministic rollback;
- shadow-before-live promotion.

Do not recommend ML complexity unless simpler baselines fail.

---

# 15. Security / production-control audit

Audit:
- owner vs worker auth boundaries;
- approval authority;
- manual execution boundary;
- secrets handling;
- logs;
- SSH deploy workflow;
- seven-file production allowlist;
- backup/rollback;
- checksum verification;
- live readback;
- accidental config exposure;
- SQL/migration safety.

No secrets should be printed in the report.

---

# 16. Required adjudication of previous reviews

We have at least two major independent reviews, plus internal triage.

Their strongest repeated findings include:
- opportunity starvation;
- stale equity;
- Python/PHP exit drift;
- evidence redundancy;
- possible asset-class geometry bias;
- generic live model;
- AMP universe limitation.

Disputed/uncertain findings include:
- “remove 1M now”;
- “remove ATR bounds now”;
- “news/macro zero corrupts the 84 score”;
- “missing MTF passes incorrectly”;
- “lower 84 now”;
- “raise risk now”.

Do not count reviewer votes.

For each disputed point, return:
1. reviewer claim;
2. actual code truth;
3. actual live evidence;
4. experiment needed;
5. final status:
   - FIX NOW;
   - TEST FIRST;
   - REJECT;
   - DEFER.

---

# 17. Deliverable — Part A: Executive verdict

Give a short executive answer:

1. What are the top 3 real problems?
2. What is NOT actually a problem?
3. What is blocking competition performance?
4. What is blocking safety/correctness?
5. What is blocking opportunity supply?
6. What is blocking research promotion?
7. Is the current architecture salvageable?

---

# 18. Deliverable — Part B: Full findings matrix

Create a table with columns:

- ID
- Area
- Finding
- Classification
- Evidence
- Severity
- Live impact
- Competition impact
- Safety impact
- Fix/test
- Exact files
- Exact functions
- Regression tests
- Rollback
- Live / Shadow / Research
- Dependency

Severity:
- P0 correctness
- P1 performance/design
- P2 research
- P3 cleanup

---

# 19. Deliverable — Part C: COMPLETE implementation roadmap

This is essential.

Build the roadmap we will execute afterwards in this project.

Use sequential batches:

`BATCH STC-R1`, `STC-R2`, `STC-R3` ...

For EVERY batch include:

1. Objective.
2. Why it comes in this order.
3. Exact files to inspect/edit.
4. Exact functions/sections.
5. Database/schema impact.
6. Environment/config impact.
7. Production impact.
8. Whether behavior changes live.
9. Whether it is shadow-only.
10. Tests to add/update.
11. Acceptance criteria.
12. Rejection criteria.
13. Rollback procedure.
14. Required evidence before starting next batch.
15. Owner action required, if any.
16. Estimated implementation complexity:
   - low;
   - medium;
   - high.
17. Whether deployment is required.
18. Whether Live Readback is required.

The roadmap must include at least these categories:

### Phase 0 — correctness and observability
- equity freshness;
- Python/PHP parity;
- possible zero-case LONG bias;
- possible RSI asymmetry;
- volatility score consistency;
- logging/attribution gaps.

### Phase 1 — rejected-trade outcome attribution
- MFE/MAE;
- gate clause attribution;
- 1.5R/2.5R-before-stop;
- session/class metadata.

### Phase 2 — redundancy / effective-dimensionality research
- correlation;
- PCA;
- ablation;
- MTF independence.

### Phase 3 — quality/gate research
- neutral transform;
- Boolean vs quality gate;
- threshold sweep;
- news/macro composite variants.

### Phase 4 — asset-class geometry
- ATR bounds;
- stops;
- targets;
- sessions;
- volume proxy differences.

### Phase 5 — universe / symbol-specific routing
- AMP expansion;
- calibration registry;
- symbol/asset-class promotion criteria.

### Phase 6 — exit-management experiments
- fixed target;
- current high-water;
- volatility trailing;
- single-TP vs any candidate alternative.

### Phase 7 — risk-objective research
Only after edge is established:
- current 0.5%;
- candidate risk bands;
- portfolio/cluster limits;
- competition-score distribution;
- Monte Carlo robustness.

### Phase 8 — controlled promotion
- shadow;
- forward evidence;
- canary;
- live promotion;
- automatic rollback criteria.

---

# 20. Deliverable — Part D: What NOT to change

Explicitly list every rule that should remain untouched until a named experiment passes.

Include at minimum:
- human approval;
- manual execution;
- closed-bar anti-repaint;
- risk caps;
- 84;
- Boolean gate;
- 1M;
- ATR bounds;
- macro blackout;
- family priors;
- community live authority.

Do not say “change later” without naming the evidence required.

---

# 21. Deliverable — Part E: Final proposed target strategy

After reviewing all evidence, describe the **target STC architecture we should aim for**.

But separate:

### Proven changes
supported by current evidence.

### Candidate changes
requiring experiment.

### Rejected ideas
not supported.

### Deferred ideas
useful but not urgent.

Do not pretend untested changes are proven.

---

# 22. Deliverable — Part F: Immediate next executable batch

At the very end give exactly ONE first implementation batch for us to execute here.

It must be:
- the highest-priority;
- smallest safe scope;
- independently testable;
- reversible;
- with exact file list;
- exact tests;
- exact acceptance criteria;
- exact rollback.

Do not provide 10 simultaneous code patches as the immediate next action.

The larger roadmap can contain all phases, but the immediate executable action must be one controlled batch only.

---

# 23. Additional questions you must answer

1. Is `84` currently meaningful as a quality measure, or mostly repeated trend agreement?
2. How many independent information dimensions does STC likely contain?
3. Is the 15m/1h/2h/4h stack over-correlated?
4. Does 1D/1M add incremental predictive value after intraday evidence?
5. Are families true independent evidence or mostly repackaged OHLCV?
6. Are Capital CFDs and AMP futures being scored fairly under the same family priors?
7. Is tick volume creating class bias?
8. Is the current strategy structurally LONG-biased anywhere?
9. Does SHORT missing-evidence handling remain symmetric everywhere?
10. Does zero-value handling remain symmetric everywhere?
11. Does the current trade geometry fit all asset classes?
12. Is 2.5R a good universal final target?
13. Is current high-water management better than ATR trailing?
14. Is the Boolean gate redundant with the quality gate?
15. Does the current 0.5% risk make sense after account equity changes?
16. Is the 3% portfolio / 1.5% cluster model too conservative, appropriate, or unproven?
17. Should statistical correlation become live, remain research-only, or be abandoned?
18. Should AMP expand beyond 16 symbols?
19. Should symbol-specific calibrated models become live eventually?
20. Which existing research components deserve another forward test?
21. Which components should be permanently retired?
22. Is operational transport reliability reducing signal opportunity materially?
23. Are any tests giving false confidence because they assert implementation rather than predictive validity?
24. What minimum dataset do we need to answer the remaining quant questions credibly?
25. Can the current system realistically pursue a high competition score without increasing risk, purely through better opportunity selection?
26. If not, what sequence of evidence must exist before even testing higher risk?

---

# 24. Final report discipline

Do not:
- praise the project;
- repeat documentation without verifying code;
- recommend indicator shopping;
- recommend leverage because the leader is +38%;
- equate backtest win rate with live edge;
- optimize on the final holdout;
- use Monte Carlo before obtaining an OOS trade sequence;
- use one global parameter because it is convenient;
- declare a reviewer correct because multiple AIs repeated the same idea.

Do:
- trace code;
- reproduce formulas;
- inspect tests;
- inspect live-state evidence;
- distinguish correctness from strategy design;
- distinguish safety from competition objective;
- quantify opportunity starvation;
- quantify information redundancy;
- quantify asset-class bias;
- produce a controlled implementation roadmap.

---

# 25. Output format

Return the report in this exact high-level order:

1. **Repository access / audit scope confirmation**
2. **Executive verdict**
3. **Current live architecture truth map**
4. **Live vs shadow vs legacy matrix**
5. **P0 correctness findings**
6. **P1 strategy/performance findings**
7. **P2 research findings**
8. **Previous-review adjudication matrix**
9. **Opportunity-starvation root-cause analysis**
10. **Redundancy / effective-dimensionality analysis**
11. **Asset-class bias analysis**
12. **Risk and competition-objective analysis**
13. **Operational reliability analysis**
14. **Research/shadow-state audit**
15. **What not to change yet**
16. **Full phased implementation roadmap**
17. **Immediate next executable batch**
18. **Open questions / missing evidence**
19. **Final target STC architecture**

Make the report specific enough that another engineer can implement the roadmap without asking what you meant.

No repository modifications in this review pass.
