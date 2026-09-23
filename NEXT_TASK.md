# NEXT TASK

Updated: 2026-09-24 00:00 EEST

## CONTROLLING PROJECT
STC.

## PRIMARY OBJECTIVE
Complete PR #108 exact frozen 85/15 holdout verification, then run the 26-symbol final unseen 15m confirmation on exact-provider history and archive the results.

## CURRENT VERIFIED BASELINE
- Native-vs-community 15m run #5 completed and archived.
- Native strict full-pass count: 0.
- Community research profiles: 10/26 symbols.
- 14 implemented community research components.
- General Lab research plan/evaluate endpoints exist and use the same process.
- community_indicator_live_authority=false.

## ACTIVE WORK UNIT
PR #108 — exact frozen holdout confirmation.
- PR #107 is superseded and closed unmerged.
- CI run #374 pending.
- Exact split rule: 85% development + 15% untouched final confirmation.
- No silent split resizing; insufficient holdout history fails closed.

## AFTER PR #108 PASSES
1. merge PR #108;
2. stage/run frozen confirmation on all 26 exact-symbol 15m datasets;
3. require each candidate to have passed development OOS/forward first;
4. replay frozen parameters on final 15% only;
5. archive per-symbol promotion candidates and rejection reasons;
6. keep live_authority=false;
7. update PROJECT_STATE.md and docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md;
8. continue next research wave only after the final holdout evidence is frozen.

## NON-NEGOTIABLE
- No lookahead.
- Train-only tuning.
- Final holdout untouched until development is frozen.
- No live weight/A+ changes from this research stage.
- No automatic trade execution.
