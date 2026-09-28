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
