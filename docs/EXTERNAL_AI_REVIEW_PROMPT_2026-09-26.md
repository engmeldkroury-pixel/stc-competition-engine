# External AI Review Prompt — STC — 2026-09-26

You are acting as an independent senior reviewer of the STC competition decision-support system.

Repository:
`engmeldkroury-pixel/stc-competition-engine`

Start by reading:
1. `docs/STC_FULL_SYSTEM_REVIEW_2026-09-26.md`
2. `HANDOFF.md`
3. `NEXT_TASK.md`
4. `DECISIONS.md`
5. `RISK_REGISTER.csv`
6. `TEST_REGISTER.csv`
7. `docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md`
8. `docs/PERFORMANCE_INCIDENT_2026-09-24.md`

Then inspect the implementation, especially:
- `app/event_decision.py`
- `app/signals.py`
- `app/evidence_engine.py`
- `app/competition_profiles.py`
- `app/competition_strategy.py`
- `app/community_shadow.py`
- `app/portfolio.py`
- `app/strategy_lab.py`
- `hostinger_patch/cloud_control.php`
- `hostinger_patch/operator_snapshot.php`
- `hostinger_patch/notification_control.php`
- `.github/workflows/stc-hostinger-deploy.yml`

## System boundaries

Do not propose or implement automatic broker/order execution.
Human approval and manual order entry are mandatory.
Do not expose or request secret values.
Do not use cross-provider market data as a silent substitute.
Do not treat setup-quality scores as win probabilities.
Do not recommend increasing risk or weakening controls merely to chase a leaderboard.
Research/shadow components must not gain live authority without causal parity, forward evidence and an explicit promotion decision.

## Current policy to verify

Both active competitions are intended to use competition mode:
- Capital.com Africa
- AMP Futures

Current shared competition opportunity quality floor:
- 84/100

The gate also requires:
- directional base recommendation;
- historical context;
- intraday majority alignment;
- short-term and blended strength;
- higher-timeframe non-opposition;
- family evidence/agreement/breadth/conflict limits;
- acceptable volatility/liquidity;
- manual approval.

The strict non-competition A+ path remains 90/100.

## Review tasks

### 1. Find correctness bugs
Look for:
- direction asymmetry;
- missing-data behavior;
- duplicated or contradictory policy constants;
- stale/dead code paths;
- score/gate mismatch;
- timestamp/session/futures edge cases;
- quantity/unit confusion;
- unsafe deployment assumptions;
- stale-ledger hazards;
- notification vs console divergence.

For every finding provide:
- severity;
- exact file/function;
- concrete failure mechanism;
- evidence;
- smallest safe patch;
- tests required.

### 2. Audit strategy mathematics
Check whether the 84 gate and quality score double-count correlated evidence.

Specifically examine overlap among:
- short-term technical;
- blended technical;
- historical regime;
- 1h/2h/4h/1M evidence;
- family evidence;
- volatility/liquidity quality.

Do not simply suggest more indicators.
Identify whether existing evidence is redundant, improperly normalized, asset-class biased or session biased.

### 3. Audit asset-class fairness
The same engine covers:
- CFD forex;
- crypto;
- indices;
- metals;
- futures including energy/rates/FX/index micros.

Determine whether:
- relative volume thresholds;
- range/ATR quality;
- timeframe rules;
- session behavior;
- historical regime;
- family priors

should be normalized differently by asset class or symbol.

Any proposed adaptive rule must be research-only first and validated out-of-sample.

### 4. Diagnose opportunity concentration
All 10 Capital symbols are scanned, but historical actionable notifications were concentrated mainly in:
- SPX500;
- NAS100;
- BTCUSD;
- ETHUSD.

Use the new gate-failure attribution data design in `operator_snapshot.php` to explain how you would distinguish:
- true market weakness;
- missing family evidence;
- quality-floor starvation;
- liquidity/volatility blocking;
- MTF blocking;
- model structural bias.

Do not solve concentration by blindly lowering all gates.

### 5. Review symbol-specific research
Evaluate whether the current shadow profiles are genuinely additive or likely redundant.

Capital examples:
- DOGEUSD: Range Filter + Schaff
- EURUSD: Trendilo
- ETHUSD: SSL Hybrid
- NAS100: HalfTrend
- BTCUSD: RSI Kernel
- USDZAR: multi-component profile

AMP profile-ready symbols:
- MCL
- MNG
- MGC
- MJY
- MET
- ZN
- ZB

Check:
- causal implementation;
- no-lookahead risk;
- Pine/Python semantic parity requirements;
- redundancy;
- sample size;
- regime dependence;
- forward/shadow promotion criteria.

### 6. Audit trade and portfolio management
Review:
- quantity/risk ticket enforcement;
- duplicate/re-entry controls;
- stale position ledger hazards;
- closed-bar high-water profit protection;
- MFE/MAE attribution.

Assess whether the progressive profit-lock policy may exit trends too early.
Propose a forward-test design rather than an unsupported live change.

### 7. Review deployment reliability
Inspect the SSH deployment workflow.
Verify that it:
- deploys only seven approved PHP files;
- backs up before replacement;
- fails before production change if the key is invalid;
- verifies deployed checksums;
- excludes config.php and SQL.

Identify any additional rollback/atomicity/security improvement that is warranted.

### 8. Give a prioritized engineering plan
Return three groups:
- P0 correctness/safety defects;
- P1 strategy/observability improvements;
- P2 research experiments.

For each item include:
- expected benefit;
- risk;
- files involved;
- acceptance tests;
- whether it changes live trading behavior.

## Evidence discipline

Separate:
- verified fact;
- inference;
- hypothesis;
- recommendation.

Do not claim a strategy improvement without out-of-sample/forward evidence.
Do not infer current platform positions from the STC ledger if the ledger is not reconciled.
Do not treat historical stored signal metadata as proof of post-deployment runtime behavior.

## Deliverable

Produce:
1. executive summary;
2. architecture/correctness findings;
3. strategy audit;
4. deployment audit;
5. risk/control audit;
6. prioritized patch plan;
7. test plan;
8. questions/unknowns that require new evidence.

Do not modify the repository unless explicitly instructed after the review.
