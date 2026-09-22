# Frozen 15m confirmation

This stage exists to test pre-frozen STC hypotheses on genuinely unseen data without reopening optimization.

## Non-negotiable rules
- Strategy ID and all BacktestParams are loaded from the frozen manifest.
- No threshold, stop, target, hold period, confirmation count or regime rule is optimized on unseen data.
- Only confirmed archives with `provider=TradingView Official MCP` are accepted.
- Alternate historical sources such as Capital.com REST remain quarantined and cannot satisfy this gate.
- Mutable tail bars are rejected.
- Trades whose time exit is truncated by the current end of the archive are excluded as incomplete.
- Every output keeps `live_calibration_authority=false`.

## Statuses
- `NO_UNSEEN_DATA`: no confirmed bar exists after the hypothesis freeze timestamp.
- `ACCUMULATING`: unseen data exists but fewer than 30 completed trades have matured.
- `UNSEEN_FAILED`: at least 30 unseen trades matured but one or more unchanged performance gates failed.
- `UNSEEN_SUPPORT`: unseen completed trades passed the fixed performance gates and segment-stability screen.

`UNSEEN_SUPPORT` is not validation and does not authorize calibration or trading. It only opens a second confirmation decision.

## Fixed unseen-performance gates
Once at least 30 completed unseen trades exist:
- expectancy > 0.08R
- profit factor >= 1.15
- max drawdown <= 10R
- unseen segment stability >= 0.60

The development result remains part of the evidence record even if the unseen window improves.

## Current frozen baseline comparators
See `research_hypotheses/frozen_15m_v1.json` for exact values and source runs:
- CME_MINI:MNQ1! / vwap_reversion / 15m
- CAPITALCOM:BTCUSD / bollinger_mean_reversion / 15m
