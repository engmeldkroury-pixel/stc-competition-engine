# R10 confirmed-remote-base-feed hypothesis — 28 September 2026

## Why this exists
The production Capital MTF v1.1 Pine scripts gate alert emission with outer-chart `barstate.isconfirmed`, but each remote symbol's 15m base data is obtained through:

`request.security(symbol, feedTf, makeFeedBar(), lookahead=barmerge.lookahead_off)`

and `makeFeedBar()` returns the remote symbol's current `time/open/high/low/close`.

The higher-timeframe evidence already uses the safer previous-bar pattern (`[1]` with `lookahead_on`).

A limited R9-vs-fresh-TradingView overlap check found close-only retrospective differences in 11/20 ETHUSD rows and 15/20 DOGEUSD rows while O/H/L matched. This does **not** prove the current remote-bar contract caused the revisions, but it is a falsifiable source-fidelity hypothesis.

## Research candidate
Two v1.2 RESEARCH files are added for Capital A/B. They:
- default the feed to disabled;
- use the previous remote 15m bar for every FeedBar field (`[1]`);
- use `lookahead_on` with that previous-bar expression;
- retain the outer confirmed/realtime host trigger;
- use a distinct `r10-confirmed-base-v12|` event-id namespace;
- mark payloads `research_only=true` and `live_authorized=false`.

They must never be pointed at the production webhook during research.

## Expected trade-off
This contract deliberately introduces one 15-minute bar of remote-source latency. The benefit is that the remote source bar is frozen before use, which should reduce decision drift caused by late/revised closes.

## Acceptance before any production consideration
1. Pine compile must succeed in TradingView.
2. A parallel research-only cycle must show no event-id collision and exact expected symbol coverage.
3. For matching timestamps, compare v1.1 current-remote and v1.2 previous-confirmed payloads with later retrospective history.
4. Demonstrate whether v1.2 materially reduces close revisions / decision drift.
5. Re-run strategy opportunity and outcome analysis with the delayed contract.
6. Only then consider a separate production PR. No automatic migration or live strategy change is authorized by this research branch.


## Historical latency stress before any deployment
A paired historical stress was run on the already-frozen ETHUSD/DOGEUSD MTF pullback candidates at a 5 bps cost proxy. This is exploratory because later TradingView history can contain close revisions; it is not prospective evidence.

The test compared the normal next-bar entry with an additional one-15m-bar latency, and used the same 0.25 ATR maximum source-close-to-entry-open gap.

- ETHUSD: 91 raw source setups; normal entry eligible 91; delayed entry eligible 33. On the **same 33 delayed-eligible source setups**, normal mean was about +0.253R and delayed mean +0.328R (paired mean difference about +0.075R).
- DOGEUSD: 102 raw source setups; normal eligible 102; delayed eligible 32. On the **same 32 delayed-eligible source setups**, normal mean was about +0.537R and delayed mean +0.577R (paired difference about +0.040R).

This does **not** establish that latency improves the strategy. The delayed source contract filters out roughly two-thirds of these source setups under the frozen gap rule, creating major opportunity starvation. The common-cohort result only shows that delayed entry did not collapse the small subset that remained eligible.

Decision: keep v1.2 RESEARCH ONLY. The current preferred engineering control is to freeze alert-time/as-observed v1.1 evidence for causal forward validation while testing whether confirmed-base data materially improves source fidelity enough to justify its opportunity cost.
