# STC DECISIONS

## 2026-09-24 — Capital competition acceleration
- Capital.com Africa uses a competition-specific quality floor of 78/100.
- 1M alignment is not a hard Capital blocker.
- Other competitions retain the A+ high-conviction gate.
- Human approval/manual order entry remains mandatory.

## 2026-09-24 — Central quality eligibility
- `stc_signal_quality_gate_eligible()` is the single Hostinger-side eligibility contract.
- `COMPETITION_OPPORTUNITY` is eligible only for the Capital competition in competition mode.
- Deployed PHP must be updated as one compatible six-file hotfix; partial deployment is not accepted.

## 2026-09-24 — Community indicator policy
- No universal composite indicator is accepted.
- QQE+SSL+WAE composite failed 0/26 and receives no promotion.
- Community evidence is symbol/timeframe-specific.
- Frozen Capital community profiles exist for 6/10 symbols only.
- Community component weights remain research/shadow-only until Pine/Python parity is proven and a separate promotion decision is recorded.

## 2026-09-24 — Operational observability
- Permanent read-only Live Readback workflow is accepted for production evidence.
- Readback may expose sanitized signals, runtime controls and competition progress only.
- It never approves or places orders.

## 2026-09-24 — Performance incident and execution discipline
- The owner-supplied Capital trade history is controlling evidence for realized competition performance until STC is reconciled.
- Current visible realized P/L is negative and the visible XAGUSD trade dominates the drawdown; signal quality and execution/risk deviation must be diagnosed separately.
- Do not loosen quality thresholds or increase per-trade risk to recover losses.
- Future manual fills should use the STC proposed quantity exactly or a smaller valid quantity when the platform requires it; larger discretionary sizing is outside the STC risk ticket.
- Do not promote community/shadow indicators merely because the current live strategy experienced drawdown; promotion still requires parity and evidence.
- Before changing live weights or symbol rules, backfill the visible closed trades and attribute each one to its actual STC source evidence where possible.

## 2026-09-25 — Competition objective and gate-supply policy
- The controlling objective is competition performance: maximize the chance of positive leaderboard progress while keeping drawdown and execution errors controlled.
- Do not optimize for indicator count, model complexity, or theoretical elegance.
- Do not use a permanently loose 78/100 gate merely to create activity.
- Do not use a permanently strict 90/100-only gate without measuring whether it starves the competition of viable opportunities.
- PR #167 is held as a draft safety reference, not a final competition policy.
- Before changing the live gate, compare recent production signal supply under strict A+ and a balanced competition proxy using the same stored signal context.
- Any future relaxed tier must preserve higher-timeframe non-opposition, family breadth, conflict limits, reduced risk, and manual approval.
- Telegram/server notifications and owner-console visibility must represent the same actionable event stream; PR #166 is the controlling parity fix.

## 2026-09-26 — Profit-protection release
- PR #169 merged after green full CI and competition-critical CI.
- Open-position management now uses a closed-bar high-water R mark and a progressive locked-profit floor.
- If current R falls below the earned locked floor, STC recommends EXIT_NOW rather than allowing a large unrealized gain to drift back toward the original stop.
- This was cross-checked against the observed NAS100 and SPX500 profit-giveback incidents.
- Execution remains manual; the change is management advice, not broker automation.
- Latest Hostinger bundle workflow run: 36225098256.
- Latest deployment artifact: stc-hostinger-hotfix-169-36225098256, artifact id 10900587381.

## 2026-09-26 — Capital opportunity concentration audit
- Live production feed coverage is 10/10 Capital symbols; no symbol is omitted from the TradingView A/B feeds.
- Notification history shows actionable NEW_LOCKED_PLAN events are materially concentrated:
  - SPX500: 22;
  - NAS100: 19;
  - BTCUSD: 3;
  - ETHUSD: 1;
  - all other Capital symbols: 0 NEW_LOCKED_PLAN in the current 50-event audit window.
- Therefore the issue is not missing symbol ingestion; it is opportunity-source concentration in the generic live strategy.
- Do not manufacture equal recommendation counts by lowering all gates.
- Priority is symbol-specific opportunity sourcing using validated research components, with live/Pine parity and shadow evidence before promotion.

## 2026-09-26 — Dual-competition parity and AMP specialization
- Live pre-deployment readback proved the deployed AMP runtime is stale:
  - competition_mode is absent/null;
  - live reasons still report high_conviction_gate;
  - live quality floor remains 90/100;
  - AMP NEW_LOCKED_PLAN notification count is zero in the current audit window.
- Current main instead treats both Capital and AMP as competition mode with a shared 84/100 opportunity floor while retaining manual approval, sizing and risk controls.
- Consolidated Hostinger PHP bundle run 36248177372 and full CI run 36248177360 both succeeded.
- AMP core production feeds currently scan 16 symbols.
- Seven AMP core symbols have validated exact-provider Wave-3 15m research profiles: MCL, MNG, MGC, MJY, MET, ZN and ZB.
- PR #185 merged as 5173c1296a01573ff2bca94729eabf08a3b29b35 after full and critical CI success.
- AMP component profiles remain research/shadow-only until exact causal Pine payload parity is demonstrated. No approximate Pine mapping may receive live authority.

## 2026-09-26 — Secure Hostinger deployment channel
- Manual ZIP/File Manager replacement is superseded as the preferred STC deployment path.
- Production Hostinger updates should use the dedicated SSH-key GitHub Actions workflow `.github/workflows/stc-hostinger-deploy.yml`.
- The workflow is restricted to the approved seven PHP files, validates PHP syntax, creates a pre-deploy backup, verifies SHA-256 parity after replacement, and never deploys `config.php` or SQL.
- GitHub repository visibility does not expose secret values; only secret names appear in workflow source.
- Password-based reusable deployment credentials are not the preferred automation mechanism.
- Failed deployment attempts must be fail-closed before production replacement and recorded in the test/risk registers.

## 2026-09-26 — Strategy policy consistency debt
- Live event decision policy for Capital and AMP is the shared 84/100 COMPETITION_OPPORTUNITY gate.
- `app/competition_strategy.py` still reports `A_PLUS_ONLY` in the advisory competition-pace object.
- This advisory/live semantic mismatch is not evidence that the live gate is 90, but it is a policy-drift risk and must be reconciled before relying on the pace object for automation or UI decisions.
- Do not change live weights or thresholds merely to fix naming; first centralize the policy contract and lock it with regression tests.

## 2026-09-26 — Missing evidence is always fail-closed in setup quality
- Optional missing MTF/family evidence must never become positive evidence because of LONG/SHORT sign normalization.
- `setup_quality_score()` now applies direction alignment only to real values and maps missing values to the same penalty for both LONG and SHORT.
- This is a correctness fix, not a gate relaxation.
- Per-symbol gate-failure attribution is accepted as read-only research evidence for diagnosing opportunity concentration before any live weight/threshold change.

## 2026-09-27 — External AI review disposition
- Do not adopt arbitrary live correlation rules such as 0.70/0.85 or a fixed -10 quality penalty without same-provider out-of-sample evidence.
- Existing deterministic risk clusters remain the production concentration control; statistical correlation is research-only for now.
- Do not replace progressive high-water management directly with ATR trailing; compare alternatives in shadow/forward evidence first.
- Monte Carlo is a robustness tool for out-of-sample trade paths, not a standalone optimizer for the 84 threshold.
- Asset-class/session normalization is a research hypothesis to be tested using gate-failure distributions before live policy changes.
- Platform truth remains authoritative over an unreconciled STC position ledger.
- No portfolio-management output should be treated as authoritative until ledger reconciliation is exact.

## 2026-09-27 — Owner-accepted reconciliation tolerance
- Capital platform realized P/L exceeds the fully evidenced/imported trade-history total by 54.39 USD.
- Owner explicitly decided that further forensic reconciliation of this small residual is not worth delaying the project.
- STC must preserve the residual as an unattributed limitation; it must not fabricate a balancing trade, fee, or adjustment.
- Current open-position/platform parity and trading-day parity are treated as the controlling reconciliation acceptance criteria.
- Ledger-only VOID rows must never count toward competition progress.

## 2026-09-27 — Post-audit production-control decisions
- Account equity freshness is a hard prerequisite for new actionable entries; stale/seed account state fails closed.
- Position management must fail closed to HOLD when post-entry market evidence is stale. Old bars may not generate a fresh PROTECT/EXIT instruction.
- Production single-TP management remains authoritative; no Python-only partial take-profit branch may diverge from PHP semantics.
- Research calibration/community components have no live authority unless explicitly promoted after parity + OOS/forward evidence.
- Context timestamps must be causal; higher-timeframe/history evidence later than the event time is rejected.
- Approval signal degradation is direction-normalized so LONG and SHORT revalidation are symmetric.
- Keep the live 84 floor, Boolean gate, 1M context, 0.5% risk, and ATR geometry unchanged while exact rejected-trade outcomes are still missing.
- Exact Boolean-vs-quality gate quadrants are now observational evidence only, not a trigger for immediate strategy relaxation.
- Human approval and manual platform execution remain mandatory.


## 2026-09-27 - R8 causal diagnostic contract
- Capture pre-gate directional hypotheses in a separate inert research namespace; no locked plan or approval is created for a rejected signal.
- Use the frozen decision envelope and actual availability time. No backdated entry or refreshed historical expiry.
- Resolve known opening-price gaps before unknown intrabar ordering; simultaneous stop/target touches remain explicitly ambiguous with conservative stop-first scoring.
- Preserve planned-R versus fill-R, and distinguish pre-stop excursions from post-stop rebound.
- Censor unknown time gaps, unresolved horizons and missing data. Never turn missing outcomes into losses or wins silently.
- Report overlapping rejected-signal counts descriptively; no probability or gate-benefit claim without de-overlap, holdout and causal ablation.
- Current live threshold, filters, geometry and risk remain unchanged until evidence-backed promotion.


## STC-R8-FINAL-20260927 - accepted engineering, unapproved strategy promotion

- Accept PR190 core after CI36343737101 proved 536 tests pass; squash merge9a1c32e09fc43a5eff02fd3f6094581440b2aedc. All source-transfer helper files are absent from the main tree.
- Preserve original history and publish CURRENT_CHECKPOINT.md as first-read resume pointer.
- Readback36344826332 succeeded at19:34:12Z, but stale market/account data remain stale; HOLD is a data-freshness fallback, not a fresh recommendation.
- Treat the 5000-row report as bounded, censored, overlapping legacy research. Twenty-three 1R-then-stop cases justify testing exits, not universally replacing live2.5R with1R.
- Treat the visible BTC commissions (about0.063819 planned-risk R for its shown levels) as a warning that0.02R is a proxy, not a universal measured cost.
- Record the -195.23USD realized-P/L reconciliation difference between screenshot and STC; do not fabricate missing transactions or attest fresh equity.
- Treat returned TradingView BTC history as an unvalidated candidate backfill source until provider/time/session/overlap checks pass. No probe bar was merged into the accepted research dataset.
- No live threshold/risk/stop/target/position/notification/approval changes. R9 priority is data/fill reconciliation before controlled same-cohort OOS exit/ATR selection.
