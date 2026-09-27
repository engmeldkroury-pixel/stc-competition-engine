# R8 - Rejected-trade outcome attribution and stop/target diagnostics

## Start / authority
- Date: 2026-09-27.
- Verified starting main: f90944277b70d0e21b6a28ec8672929eff8d4f0a.
- Owner requested continuation, strategy/stop/target review, and durable history after every change.
- Controlling next task: rejected-signal MFE/MAE and +1R/+1.5R/+2R/+2.5R-before-stop attribution by exact failed gates.
- Status: IN PROGRESS; no strategy promotion, production deployment or performance improvement claimed.
- Read-only source export is branch-only because this session's local environment cannot resolve github.com. Export contains tracked source only, no secrets or production account payloads; remove helper before merge.

## Owner screenshot evidence (not a fresh sizing authorization)
Image supplied in this conversation: image(20260927-184627).png.
- Account: The Leap USD / Capital.com.
- Balance USD 96,433.90; equity USD 98,367.19.
- Realized P/L USD -3,566.10; unrealized P/L USD +1,933.29.
- Margin USD 54,562.70; available funds USD 43,804.49; margin buffer 44.53%.
- Positions 2; orders 4; qualifying trading days 5/3.
- Order-history counts: all 98 / filled 27 / cancelled 56 / rejected 15. These are order counts, NOT closed-trade counts or a win-rate denominator.
- Visible BTCUSD LONG 0.5: entry fill 84,564.60; stop fill 84,299.80; entry commission 4.2282; exit commission 4.215. Price P/L = -132.40; visible two-sided commission = 8.4432; net based on shown charges = -140.8432 USD. Do not infer financing or unshown charges.
- Visible rejected BTCUSD and ETHUSD market orders are not filled losing trades; rejection reasons are not visible.
- Capture time/timezone not independently verified. DO NOT refresh live account-equity timestamp, sizing eligibility, position stops or account controls from this image alone.

## Fixed safety boundary
- Research-only; manual approval/execution only.
- Preserve live 84 / Boolean / monthly gate / ATR settings / 0.5% risk.
- No broker actions, no ad-hoc stop widening, no automatic replacement trade.
- No synthetic performance presented as observed market evidence.

## Acceptance plan
1. Inspect existing data/event/bar contracts and research infrastructure.
2. Implement deterministic causal outcome attribution with explicit unknown/censored/ambiguous states.
3. Handle same-bar ambiguity, stop gaps, LONG/SHORT symmetry, costs and sample boundaries.
4. Aggregate by exact rejection clauses without pretending overlapping gate samples are independent.
5. Add regression tests; run critical and full CI.
6. Record what is implemented, tested, deployed and still blocked, and update the project registers without deleting history.
