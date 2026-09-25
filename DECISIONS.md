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

## 2026-09-25 — Capital acceleration gate withdrawn after loss review
- The 2026-09-24 Capital-specific 78/100 acceleration decision is superseded.
- Capital must use the strict A+ high-conviction gate and a 90/100 quality floor before a new locked trade plan is eligible.
- Higher-timeframe confirmation is again hard-gated; 1M direction is not ignored for Capital.
- Forensic reason: the observed SPX500, XAGUSD and EURUSD plan shapes passed the relaxed gate but would have failed the already-existing strict A+ gate.
- This correction is a safety/quality change, not proof of profitability. It intentionally accepts fewer opportunities until symbol-specific component evidence is live-parity verified.
- Community/component research remains shadow-only; no component is promoted merely because the relaxed gate lost money.
