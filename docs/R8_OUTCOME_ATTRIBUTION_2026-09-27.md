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

## Implementation checkpoint
Status: IMPLEMENTED ON DEVELOPMENT BRANCH; NOT YET MERGED OR PRODUCTION VERIFIED.

- `app/outcome_attribution.py`: frozen inert outcome seeds and causal next-full-open replay; four alternative single-TP policies at 1/1.5/2/2.5 planned R.
- `app/event_decision.py`: seeds are stored in `research_outcome_seed`, NEVER in a rejected signal's `locked_trade_plan`. Errors in research capture cannot authorize a trade or change live scoring.
- `app/outcome_report.py`: validates persisted receipt/source/identity, deduplicates events, quarantines conflicting history and separates frozen forward seeds from `LEGACY_RECONSTRUCTED_GEOMETRY`.
- `scripts/run_outcome_attribution.py`: bounded authenticated GET inbox only, or offline JSON snapshot; no claim/ack/account/position/approval/notification writes. No broker execution.
- Each report states its cutoff, input digest, source coverage, excluded/quarantined rows, settled/censored sample counts and explicit cost proxy.
- Entry cannot precede decision availability or use an unobserved intrabar price. Entry expiry is not restarted for delayed signals.
- A missing time interval censors unresolved paths; it is not treated as a known session gap. A known next-bar price gap through stop fills at OPEN, not the stop price.
- Same-bar stop/target touches are flagged AMBIGUOUS_STOP_FIRST; open-price order is known and handled separately.
- Frozen stop and targets are not moved after entry. Planned R and actual-fill R use distinct denominators.
- Full-window MFE/MAE may include post-stop price action and are explicitly distinct from pre-stop MFE bounds. A later rebound does not turn a stopped trade into a win.
- Clause groups overlap. Settled-only averages are NOT unbiased expectancy or a calibrated win rate, and no causal filter benefit or strategy promotion is inferred.
- Forward capture preserves the current geometry. Legacy reconstructions are separately labelled and cannot prove the original historical stop/target plan.

## Local tests (synthetic correctness fixtures, not market performance)
- Targeted outcome/event/plan tests: 82 passed.
- Exact competition-critical workflow selection including R8: 273 passed.
- Full local suite cannot currently be accepted: first reproduced failure is the unavailable pinned `lorentzian_classification` dependency in this network-isolated container. No test was removed or marked skip. Full GitHub CI with requirements installed is required before merge.
- No live 84/Boolean/1M/ATR/risk parameter change.

## Remaining acceptance
1. Run PR critical + full CI with pinned dependencies.
2. Read a bounded production inbox and save the derived, credential-free outcome report.
3. Do not claim complete history or OOS profitability from the bounded capture.
4. Record actual mature sample/coverage deficits; then prepare de-overlapped exit/ATR ablation with a frozen holdout.
5. Remove all temporary branch source-transfer helpers before merge.


## STC-R8-FINAL-20260927 - superseding acceptance checkpoint

PR190 merged9a1c32e09fc43a5eff02fd3f6094581440b2aedc after fullCI36343737101:536passed1warning. Main tree exactly matches tested source. Production readback36344826332 SUCCESS19:34:12Z; no PHP deployment or live parameter changes. A new natural frozen seed has not yet been observed.

Read-only history36344024376SUCCESS produced real bounded evidence, not a validated strategy winner. See R8_HISTORY_RESULTS_2026-09-27.md for1947legacy observations and extensive censoring. Extra exporter/cohortdiagnostic tools remain research-only. All prior failed attempts and local dependency limitations are retained as historical evidence. CURRENT_CHECKPOINT.md is the latest resume entrypoint.
