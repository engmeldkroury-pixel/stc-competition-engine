# STC External AI Review Triage — 2026-09-27

Status: REVIEWED AGAINST CURRENT MAIN  
Controlling branch at review start: main @ 634de19a3d0404826c4ecffeca2887f4f6af1159

## Purpose

This note reconciles the owner-supplied external AI reviews with the actual STC repository. It separates:
- findings confirmed by code/evidence;
- findings already implemented before the review;
- useful hypotheses that remain research-only;
- recommendations rejected or deferred because their numeric thresholds are unsupported.

No automatic broker execution is introduced.

## Confirmed / already implemented

### 1. SHORT missing-evidence asymmetry
Confirmed historical correctness defect, already fixed in commit 760796b58f0d763ea54b9fc452a8cd8aba119a49.

Current implementation uses one direction-aware helper and maps missing optional evidence to a direction-independent penalty.

Additional QA added in commit 634de19a3d0404826c4ecffeca2887f4f6af1159:
- each optional setup-quality component is now independently tested for LONG/SHORT symmetry;
- missing value must score below aligned present evidence.

Latest competition-critical CI after this QA patch:
- 198 passed, 1 warning.
Full-suite result for the same patch is tracked separately until completion.

### 2. Quantity oversizing / duplicate entry / post-loss cooldown
Already server-side, not merely client-side.

Current server controls include:
- approval rejection when an OPEN position already exists for the same competition/symbol;
- same-symbol/same-direction post-loss cooldown;
- approval-time maximum STC quantity;
- fill-record rejection when filled quantity exceeds both approved and current risk capacity;
- manual_external path only for owner-confirmed platform fills that already happened outside the compliant STC ticket.

Therefore the external recommendation to add these controls is directionally correct but mostly already implemented.

### 3. Correlation / concentration control
STC already uses deterministic risk clusters:
- equity_indices;
- crypto;
- metals;
- fx_usd;
- energy;
- rates.

Sizing is constrained by both portfolio open-risk capacity and same-cluster open-risk capacity.

What is NOT yet implemented:
- rolling statistical correlation;
- beta-weighted cross-asset exposure;
- correlation thresholds such as 0.70/0.85.

Decision:
- do not hard-code 0.70, 0.85 or a -10 quality penalty without same-provider out-of-sample evidence;
- statistical correlation is accepted as a research-only diagnostic, not a live blocker yet.

### 4. Competition clock pressure
Already exists in app/competition_strategy.py.

The pace model knows:
- hours/time fraction remaining;
- qualifying days remaining;
- late catch-up/protect-score/final-window phases.

It can broaden scanning or reduce the size band, but the active competition quality floor remains 84.

Decision:
- keep time pressure advisory;
- do not lower the quality floor merely because the competition is near its end.

### 5. Volatility normalization
The current volatility-quality model is already dimensionless:
- closed-bar range / ATR.

Therefore the external suggestion to replace an absolute volatility measure with Relative ATR is already substantially satisfied.

Remaining asset-class concern is more likely to involve:
- provider/tick-volume comparability;
- session structure;
- missing MTF bars;
- family-evidence behavior.

### 6. Deployment rollback / staging
The SSH deploy workflow already had:
- seven-file scope;
- target allowlist;
- pre-deploy backup;
- ERR trap restoring the backed-up files;
- post-deploy SHA-256 verification.

Commit 634de19a3d0404826c4ecffeca2887f4f6af1159 strengthened it further:
- the extracted staging package is checksum-verified BEFORE any production file is touched;
- regression test verifies stage-check -> backup -> rollback trap -> copy -> production checksum ordering.

The current blocker remains only the invalid HOSTINGER_SSH_PRIVATE_KEY secret.

### 7. HalfTrend repaint concern
The current Python HalfTrend research adapter is explicitly causal and uses only current/past bars.

The community adapter test suite includes prefix-invariance causal testing for HalfTrend and the other implemented research adapters.

The TradingView diagnostic Pine candidate also implements the same confirmed state-transition logic.

Still pending before any live authority:
- exact Pine/Python event parity on provider data;
- forward/shadow outcome evidence.

## Valid unresolved findings

### P0 — stale ledger / portfolio-management authority
This is the strongest unresolved issue in the reviews.

Known evidence previously showed the platform account and STC OPEN ledger disagreeing. The current supervisor calculates:
- R multiple;
- unrealized P/L;
- closed-bar peak R;
- progressive locked-profit floor;
- EXIT_NOW / PROTECT advice

from STC ledger quantity, entry, stop and OPEN status.

Therefore portfolio advice must remain non-authoritative until the STC ledger is reconciled to current platform truth.

Important implementation constraint:
- the current schema has no explicit persistent ledger_reconciliation_status field;
- inventing one silently would require a new state contract/schema decision.

Immediate rule:
- platform evidence is controlling;
- reconcile/VOID/replace stale rows before trusting management advice.

Future fail-closed reconciliation-state control is accepted as a design task after the current ledger is reconciled.

### P1 — evidence dependence / double counting
The external reviewers are directionally correct that several inputs are statistically dependent.

Current relationships include:
- blended_technical = 65% short-term + 35% historical regime;
- base composite reuses blended technical plus volatility/liquidity;
- the gate checks short-term, blended, composite and execution-quality factors;
- setup quality scores short-term, historical, blended, MTF, execution quality and family evidence again.

This does not automatically make the gate wrong, but the evidence is not independent.

Decision:
- do not change 84 yet;
- first measure redundancy on stored signals;
- use correlation/ablation/effective-dimension analysis and out-of-sample incremental value, not correlation alone.

### P1 — asset-class fairness / session effects
Plausible and important, but not proven.

Do not assume as a design axiom that FX is always mean-reverting and indices are always trending.

Evidence-first path:
1. collect gate_failure_counts by symbol/competition;
2. compare distributions by asset class and session;
3. inspect missing-data and volume-quality rejection rates;
4. only then propose research-only normalized profiles.

### P1 — trade attribution
Accepted.

Every completed trade should eventually link:
- source signal/event;
- setup quality;
- gate outcome/failures;
- STC proposed quantity;
- actual quantity;
- entry/stop deviations;
- MFE/MAE;
- realized R/P&L;
- management actions.

Keep execution quality separate from signal quality.

## Research-only recommendations accepted

### High-water vs ATR trailing
Do not replace the current high-water rule directly.

Run a forward/shadow comparison:
- current progressive high-water;
- volatility-aware trailing candidate;
- optionally a simple fixed-R benchmark.

Measure realized R, giveback, maximum drawdown and trend-capture.

### Threshold stress testing / Monte Carlo
Monte Carlo alone should not choose the 84 threshold.

Correct sequence:
1. create candidate threshold sets under walk-forward/out-of-sample evaluation;
2. compare expectancy, drawdown, coverage and trade count;
3. apply block/bootstrap Monte Carlo to the out-of-sample trade-return paths for robustness.

No dynamic live threshold until evidence is adequate.

### Quality vs timing separation
Useful research direction.

Potential future model:
- Setup Quality: structural/regime/evidence validity;
- Entry Timing: current execution/tactical timing.

Do not split the production score until historical events can be replayed and compared out of sample.

## Recommendations not accepted as live rules

The following external numeric rules are not adopted:
- correlation > 0.70 => subtract 10 quality points;
- correlation > 0.85 => hard block;
- universal beta-weighted delta across CFDs, FX, crypto and futures;
- immediately replacing high-water protection with ATR trailing;
- lowering/changing 84 based only on Monte Carlo;
- mandatory 30/60-day waiting window for the current competitions.

Reason:
the thresholds were not derived from STC same-provider out-of-sample evidence, and the active competitions end before a 30/60-day live collection window.

## Additional operational evidence found during this review

Recent STC Process Bridge failures were not one single code defect:
- run 36263645362: external network unreachable;
- run 36265392582: external network unreachable;
- run 36270598593: HTTP 403 HTML response from the Hostinger/edge path.

Later processor runs succeeded without a strategy change.

Classification:
- intermittent external transport/edge reliability;
- current worker already retries three times with exponential 1s/2s waits;
- do not change trading logic because of these infrastructure failures;
- continue monitoring recurrence before changing retry policy.

## Priority order after this review

P0:
1. correct HOSTINGER_SSH_PRIVATE_KEY;
2. deploy verified seven-file Hostinger release;
3. run Live Readback;
4. reconcile STC open-position ledger to current platform truth;
5. do not rely on portfolio-management advice until reconciliation is exact.

P1:
1. use gate-failure attribution to diagnose opportunity concentration;
2. automate trade-level signal-vs-execution attribution;
3. measure component redundancy and asset/session rejection distributions.

P2:
1. statistical correlation diagnostics in research only;
2. asset-class/session normalization experiments;
3. high-water vs volatility-trailing shadow A/B;
4. threshold walk-forward + Monte Carlo robustness;
5. Pine/Python parity and forward shadow evidence for symbol-specific components.

## Current owner intervention

Only one owner action is still required before automated Hostinger deployment:
replace GitHub Actions secret HOSTINGER_SSH_PRIVATE_KEY with the full OpenSSH PRIVATE key file contents (file without .pub).

Do not paste the key into chat.
