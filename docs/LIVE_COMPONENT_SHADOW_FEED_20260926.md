# STC Live Exact-Component Shadow Feed — 2026-09-26

Status: PROPOSED / SHADOW-ONLY / NO LIVE AUTHORITY

## Objective

Reduce the gap between symbol-specific research evidence and the generic live production feed without changing entry authority prematurely.

The existing production MTF feeds already carry nine generic evidence families. Those generic families are not semantically equivalent to exact community/research indicators such as Trendilo, HalfTrend, SSL Hybrid or Range Filter.

This change adds exact confirmed-bar component events to the existing `community_component_signals` payload field for a small set of profiles whose exact causal Pine semantics and frozen parameters are already available.

## Capital.com exact shadow events

- CAPITALCOM:ETHUSD
  - SSL Hybrid
  - baseline 60, SSL length 15
- CAPITALCOM:DOGEUSD
  - Range Filter
  - sampling 100, multiplier 3.0
  - Schaff Trend Cycle
  - cycle 12, fast 26, slow 50, smoothing 0.5
- CAPITALCOM:EURUSD
  - Trendilo
  - smoothing 1, lookback 50, ALMA offset 0.85, sigma 6.0, band multiplier 1.0
- CAPITALCOM:NAS100
  - HalfTrend
  - amplitude 5

BTCUSD is deliberately not approximated because the validated RSI Kernel component is not yet implemented in the production Pine parity set.

USDZAR is deliberately not approximated because its validated research profile is a multi-component ensemble and the exact full ensemble is not yet implemented in the production Pine parity set.

AUDUSD, SPX500, XAGUSD and XAUUSD remain without a validated 15-minute community profile in the controlling frozen study.

## AMP Futures exact shadow events

Only final-frozen survivors that also have an existing causal Pine parity implementation are included:

- NYMEX:MCL1!
  - SSL Hybrid
  - baseline 100, SSL length 20
  - final frozen: 14 trades, expectancy +0.712R, PF 3.05
- CME_MINI:MJY1!
  - Trendilo
  - smoothing 1, lookback 50, ALMA offset 0.85, sigma 6.0, band multiplier 1.25
  - state: MULTITF_CONFIRMED
  - 15m final frozen: 22 trades, expectancy +0.151R, PF 1.27
- CBOT:ZB1!
  - Range Filter
  - sampling 100, multiplier 3.0
  - final frozen: 19 trades, expectancy +0.458R, PF 2.09

Other AMP production symbols remain generic-family-only until an exact component survives the frozen process and has a causal Pine implementation.

## Authority boundary

The emitted component values are SHADOW evidence only.

The existing Python `build_community_component_shadow()` contract keeps:
- live_authority = false
- used_in_quality_gate = false
- used_in_risk = false
- used_in_approval = false

This patch therefore does not manufacture more trades by silently promoting research results.

## Deployment dependency

TradingView alerts keep the Pine script snapshot that existed when the alert was created. Repository changes alone do not update an existing TradingView alert.

After merge, the owner must:
1. replace the affected Pine scripts in TradingView;
2. save/add the updated v1.2 scripts;
3. recreate the affected `Any alert() function call` production alerts;
4. verify webhook delivery and component-shadow fields;
5. accumulate causal shadow observations before any promotion decision.

Affected feeds:
- STC Capital MTF Feed A
- STC Capital MTF Feed B
- STC AMP MTF Feed B
- STC AMP MTF Feed C
- STC AMP MTF Feed D

AMP Feed A has no current final-frozen exact component with the existing parity adapters and is intentionally unchanged.
