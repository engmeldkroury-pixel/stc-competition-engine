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

