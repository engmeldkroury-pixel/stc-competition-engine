# R10 prospective forward-shadow ledger contract — 28 September 2026

## Purpose
Freeze the boundary between historical strategy research and prospective evidence. This ledger is research-only and cannot create broker orders, quantities, approvals, position changes, live stop/target changes or account writes.

## Frozen forward boundaries
- ETHUSD/DOGEUSD causal MTF shadow candidates: source bars opening at or after **2026-09-28T07:00:00Z**. This boundary is the first 15-minute boundary after PR #195 was merged at 06:48:46Z.
- Session/regime protocol: source bars opening at or after its already-frozen **2026-09-28T12:00:00Z** boundary.

Anything before those times is historical research and must never be relabeled prospective.

## Identity and anti-retuning
Every directional forward record carries:
- registry id;
- protocol id and SHA-256;
- candidate SHA-256 where applicable;
- symbol and exact source-open time;
- frozen entry/stop/target geometry;
- evaluation horizon;
- research-only / no-execution authority.

A parameter change creates a new protocol/candidate identity and a new forward experiment. Existing forward observations cannot be used to retune the same version and then remain in its validation set.

## Outcome rules
- Next-bar entry geometry is frozen at decision time.
- Missing 15-minute intervals censor unresolved paths; there is no interpolation.
- Opening stop gaps execute at the observed open.
- Same-bar stop + target ambiguity is conservatively scored stop-first.
- Unresolved 32-bar paths are marked at the final observed close only when the full horizon is present.
- Cost is reported in planned-R units and can be stressed independently.
- WAIT observations make no P/L claim.

## Promotion boundary
Historical results and early forward wins are insufficient for live promotion. Any later promotion requires a separate evidence review including prospective sample size, expectancy/PF after realistic symbol-specific costs, drawdown and concentration, source integrity, code/production parity and regression CI. Manual execution and current risk controls remain unchanged unless separately approved.


## Source-revision protection
A 20-row overlap check against the immutable R9 capture found close-only retrospective differences in 11/20 ETHUSD rows and 15/20 DOGEUSD rows while open/high/low matched in that sample. See `docs/R10_SOURCE_REVISION_FINDING_2026-09-28.md`.

Therefore each forward record also carries an SHA-256 of the exact as-observed evidence envelope used at decision time. Retrospective vendor history may be compared later, but it may not overwrite the frozen decision evidence.
