# NEXT TASK

Updated: 2026-09-24 01:05 EEST

## CONTROLLING PROJECT
STC.

## READ FIRST
- docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md
- PROJECT_STATE.md

## VERIFIED COMPLETE
- Adaptive native/community research framework.
- 14 implemented community/composite research adapters.
- Train-only tuning, OOS TEST, FORWARD, exact final frozen holdout.
- Redundancy-aware family normalization.
- 26-symbol 15m benchmark + frozen confirmation + multi-timeframe scan.
- 10-record research-only SHADOW registry.
- General Lab serverless research endpoints.
- General Lab durable Hostinger queue/runtime bridge merged in PR #117.
- community_indicator_live_authority=false.

## REQUIRED HOSTINGER DEPLOYMENT FOR WU-114
Run once:
- hostinger_patch/migrations/004_general_lab_queue.sql

Upload:
- hostinger_patch/general_lab.php
- updated hostinger_patch/operator.php

No new secret/config change is required.

## NEXT RESEARCH WORK UNIT
Expand practical community/composite research coverage without weakening validation:
1. implement/audit Trendilo as a causal conceptual adapter;
2. implement a separate endpoint Nadaraya-Watson non-repainting adapter rather than using repainting output;
3. continue exact audit of Lorentzian Classification and Backtest Stream semantics;
4. keep HalfTrend and VuManChu pending until causal transition/divergence timing is defensible;
5. add causality/prefix-invariance tests and TRAIN-only parameter grids;
6. run exact-provider 26-symbol 15m frozen benchmark on newly implemented candidates;
7. only successful frozen survivors enter SHADOW; no live authority.

## GENERAL LAB CONTINUATION
- New symbols automatically queue the research PROCESS.
- If provider-qualified exact history is absent, status stays WAITING_FOR_EXACT_HISTORY.
- Bare symbols remain WAITING_FOR_SYMBOL_RESOLUTION until an authorized data worker resolves the TradingView ticker.
- Never inherit another symbol's weights.

## NON-NEGOTIABLE
- no lookahead;
- no repainting evidence;
- no silent provider substitution;
- no popularity/review-based trading weights;
- no cross-symbol weight inheritance;
- no automatic broker execution;
- no live A+/risk-rule changes from research alone.
