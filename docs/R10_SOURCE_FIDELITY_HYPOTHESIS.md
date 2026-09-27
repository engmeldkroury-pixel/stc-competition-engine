# R10 source fidelity hypothesis - not a verified root cause

## Observed evidence
On the R9 corrected snapshot and the pre-existing confirmed MNQ15m archive,112bar timestamps overlap and27OHLC rows disagree. Several differences are in close only; examples include2026-09-22T01:15Z:+2.75points and06:15Z:-6.25points (stored signal close minus archive close). No MNQbackfill was merged. BTCcomparison has143exact older-archive overlaps and35exact recent-probe overlaps.

## Code evidence to examine
At starting maincd55750821131aff446eb7bf2f2c88cd518251e2, AMP MTFfeed files request makeFeedBar() in request.security(symbol,feedTf,...lookahead_off), using current-context OHLC. Emission is gated by the host chart's barstate.isconfirmed and barstate.isrealtime (e.g.STC_AMP_MTF_FEED_A.pine:109and262). Higher-timeframe requests separately use prior-bar confirmation patterns.

## Hypothesis, not conclusion
Differences may arise from source-versus-host timing, delayed/incomplete requested bars, later feed revisions or another discrepancy. The code shape alone does not prove any of these caused the27mismatches, a specific loss or the current strategy performance. Do not repair all feeds blindly by shifting every field or assume one generic delay across exchanges.

## Official primary references accessed2026-09-27
- https://www.tradingview.com/pine-script-docs/concepts/repainting/
- https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- https://www.tradingview.com/pine-script-docs/concepts/bar-states/

TradingView documents that requested values can be unconfirmed in realtime, and chart-bar confirmation is not interchangeable with requested-context data confirmation. Its confirmed higher-timeframe offset/lookahead pattern must not be generalized to another context without checking its exact timing semantics.

## Verification protocol before any live change
1. Preserve the exact historical payload, sourcebaropen/close, receiptavailability, hostchartidentity/timeframe, requestcontext and feedversion. The R9normalized dataset lacks some of these transport/host fields; obtain a narrowly sanitized diagnostic read, not account credentials.
2. Compare paired current-source and explicitly previous-confirmed-source captures by exact symbol/time, after both bars are demonstrably closed. Distinguish all OHLC differences from close-only revisions.
3. Verify source close timing, freshness, missing/session intervals, static offsets, duplicateevent IDs and queue delay. Never reinterpret processing time as source close time.
4. Any Pinecandidate requires compilation, causal parity tests and natural shadow capture before manual owner alert replacement. No Pinecandidate has been deployed or claimed compiled in this R9batch.
5. Keep live84/risk0.005/currentpositions unchanged. This is an input-quality investigation, not evidence to increase risk or recover losses by widening stops.
