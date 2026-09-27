# External AI Review Triage — Round 1 — 2026-09-27

## Scope
This triage compares:
- Reviewer A: pasted English independent quantitative/software review.
- Reviewer B: attached Arabic independent review.
- Current repository code on main.
- Latest sanitized production gate-audit readback available during triage.

No live strategy thresholds or risk settings are changed by this document.

---

## Executive verdict

### Strong convergence
Both reviewers correctly focus attention on:
1. opportunity starvation / low opportunity velocity;
2. stale owner-maintained equity used for sizing;
3. Python/PHP exit-policy drift;
4. redundancy among MTF + family evidence;
5. possible asset-class geometry bias;
6. need for measurement before changing risk.

### Important corrections
Several reviewer claims are not supported by the current code:

1. News/macro zero values do **not** directly reduce the 0-100 setup-quality score.
   - The 84 score is calculated by `setup_quality_score()`.
   - That function has no news or macro input.
   - News/macro zero values affect the separate base composite, whose competition threshold is 0.35.

2. Missing MTF evidence is not treated as bullish or neutral half-credit by mistake.
   - `competition_opportunity_assessment()` counts only non-None aligned intraday values.
   - `setup_quality_score()` maps missing optional evidence to -1 before normalization, which contributes zero points.
   - Existing tests explicitly verify missing evidence is direction-symmetric and penalized.

3. The current evidence does **not** support removing 1M immediately.
   - Latest Capital gate audit shows only 5 recent failures for `trend_1m_not_strongly_opposed`.
   - Much larger recent failure counts are:
     - intraday_majority_alignment: 92
     - family_direction_alignment: 85
     - short_term_strength: 64
     - family_breadth: 58
   - Therefore 1M is not currently the dominant observed Capital bottleneck.

4. The current evidence does **not** support removing ATR percentage bounds immediately.
   - The geometry may be asset-class biased, but the reviewers' typical-ATR assertions were not measured from STC signal data.
   - This remains an empirical experiment, not a correctness patch.

5. PHP does not execute broker trades.
   - STC remains manual-execution-only.
   - Production PHP generates approval, risk, position-management and execution-ticket guidance.
   - Human order entry remains mandatory.

---

## Live gate-audit evidence

Latest sanitized readback inspected 400 recent signal-created rows.

### Capital
- rows examined: 320
- directional rows: 135
- current 84 structural proxy passes: 2
- quality bins:
  - >=78: 4
  - >=84: 2
  - >=90: 0

Most frequent persisted failure reasons:
- intraday_majority_alignment: 92
- family_direction_alignment: 85
- short_term_strength: 64
- family_breadth: 58
- liquidity_quality: 14
- setup_quality_below_78: 14
- family_agreement: 5
- trend_1m_not_strongly_opposed: 5
- historical_not_strongly_opposed: 4
- setup_quality_below_84: 3
- family_conflicts: 2
- volatility_quality: 1

Interpretation:
- Recent Capital starvation is primarily MTF/family-direction/short-term confirmation related.
- Monthly opposition is a small observed contributor.
- The audit is a proxy; live volatility/liquidity/blended-technical factors are not fully replayed.

### AMP
- rows examined: 80
- directional rows: 16
- current 84 structural proxy passes: 0
- quality bins:
  - >=78: 2
  - >=84: 1
  - >=90: 0

AMP historical rows show broad weakness across blended technical, 1h/2h/4h alignment, family direction, and short-term strength.

Caution:
Some stored AMP rows predate the latest shared 84 competition deployment, so AMP failure labels are diagnostic history, not proof of the current worker's exact causal distribution.

---

## Reviewer claim triage

| Claim | Verdict | Reason |
|---|---|---|
| Opportunity starvation is a major problem | CONFIRMED | Live Capital audit: only 2 structural proxy passes from 135 directional rows |
| Stale account equity is a sizing correctness issue | CONFIRMED | Production still uses 100k Capital / 250k AMP seed account states at 0.5% |
| PHP/Python target1 behavior drifts | CONFIRMED | Production PHP = single-TP protect; Python portfolio branch = 50% partial |
| News/macro dead-weight corrupts the 84-point scale | REJECT AS STATED | 84 quality score does not include news/macro |
| News/macro zero values attenuate base composite | CONFIRMED | Live bridge sends zero for both; composite nominal weights sum to 0.90 live |
| Missing MTF may accidentally pass as neutral/bullish | REJECT | Code + tests fail closed/punish missing evidence |
| Remove 1M now | NOT SUPPORTED | Only 5 recent Capital monthly-opposition failures vs much larger MTF/family failures |
| Remove ATR percentage bounds now | NOT SUPPORTED YET | Needs per-asset empirical boundary-hit/MAE/MFE analysis |
| 84 + Boolean may be redundant double filtering | TEST REQUIRED | Must measure disagreement cases and their forward outcomes |
| Evidence is likely redundant / multicollinear | PLAUSIBLE; TEST REQUIRED | MTF and family definitions reuse EMA/MACD/RSI/structure concepts |
| AMP universe should expand | PLAUSIBLE; TEST REQUIRED | 16 production symbols vs wider allowed profile, but edge must be validated first |
| Raise risk to chase leaderboard | REJECT FOR NOW | No evidence justifies risk increase; first diagnose edge/opportunity and stale equity |
| Decouple direction from quality | GOOD RESEARCH CANDIDATE | Conceptually useful, but requires shadow comparison |
| PCA/inverse-correlation weighting | RESEARCH ONLY | Useful for redundancy diagnosis, not immediate live patch |

---

## Immediate P0/P1 classification

### P0 correctness
1. Stale equity source / no freshness enforcement.
2. Python/PHP exit-policy semantic drift.

### P1 design questions requiring evidence
1. Base composite live renormalization with news/macro unavailable.
2. Boolean gate vs quality gate redundancy.
3. MTF redundancy and lag.
4. Family redundancy and breadth multiplier.
5. ATR envelope/stop geometry by asset class.
6. Monthly context information gain.
7. AMP universe expansion.

### Not a bug
- Neutral value 0 mapping to 50% of a component is a deliberate linear normalization choice. It may be a poor design choice, but it is not a correctness defect by itself.
- Missing evidence is already treated differently: missing -> zero component credit.

---

## Next experiment order

### Experiment 1 — gate-failure attribution + rejected-trade outcomes
Do not change live behavior.
For each directional candidate, persist:
- Boolean pass/fail;
- quality score;
- exact failed clauses;
- 15m/1h/2h/4h/1D/1M values;
- family score/agreement/breadth;
- forward MFE/MAE and whether 1.5R/2.5R would have been reached before stop.

Purpose:
Identify which filters destroy positive expectancy rather than merely reducing frequency.

### Experiment 2 — redundancy matrix
For recent/historical candidate rows:
- correlation matrix;
- PCA;
- mutual-information or rank-correlation view;
- by symbol and asset class.

Do not reweight live until out-of-sample evidence exists.

### Experiment 3 — geometry boundary audit
By asset class and symbol:
- fraction of signals where 0.1% entry floor binds;
- fraction where 1.0% entry cap binds;
- fraction where 0.2% stop floor binds;
- ATR multiple at stop;
- MFE/MAE in R units.

Only then test asset-class-specific geometry.

### Experiment 4 — monthly ablation
Compare baseline vs no-1M / reduced-1M in shadow only.
Measure:
- trade frequency;
- expectancy R;
- profit factor;
- max drawdown;
- false-negative recovery;
- by asset class.

### Experiment 5 — base composite availability normalization
Compare:
A. current 0.60/0.15/0.15 with news/macro zero;
B. renormalized available weights;
C. remove news/macro from directional composite and retain macro blackout only.

Keep setup-quality score unchanged during this experiment.

---

## Rules not to change during Round 1
- manual human approval;
- no automatic broker execution;
- closed-bar anti-repaint;
- 0.5% live risk fraction;
- 84 live quality floor;
- Boolean gate;
- current 1M rule;
- current ATR bounds.

These stay fixed until experiments isolate the effect of each component.

---

## Safe corrective patches to prepare separately

### Patch A — equity freshness
Preferred safe behavior:
- do not invent broker API access;
- add explicit account-state freshness metadata;
- block new STC approval when owner-maintained equity is older than a configured safe freshness window;
- owner refreshes current platform equity from the operator console;
- no order execution capability is added.

### Patch B — exit-policy parity
Choose production PHP policy as the current authority:
- target1 is a management checkpoint;
- protect to at least breakeven;
- keep full quantity;
- final target target2;
- remove/deprecate Python partial-profit behavior;
- add parity regression tests.

These patches are correctness/consistency fixes and should be tested independently from strategy optimization.
