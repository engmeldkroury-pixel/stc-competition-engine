# NEXT TASK

Updated: 2026-09-23

## PRIMARY OBJECTIVE
Get STC operational for the active competitions now. The research subsystem is secondary.

Primary runtime path:
TradingView production alerts -> Hostinger/MySQL -> STC ranking/A+ gate -> Owner Console -> notification -> human approval -> manual order -> persistent position supervision.

## VERIFIED CURRENT LIVE STATE
- 26 live cards: 10 Capital.com Africa + 16 AMP Futures.
- Production webhook transport is healthy and returning HTTP 200.
- Capital legacy production alert active.
- AMP A/B legacy production alerts active.
- Safe Mode=true.
- Kill Switch=true.
- 0 active A+ opportunities.
- 0 manual-ready opportunities.
- 0 open positions tracked.

## ROOT CAUSE OF ZERO ACTIONABLE TRADES
The A+ gate is correctly fail-closed because fresh legacy feed cards do not contain the required v1.1 live confirmation context:
- 1h confirmation unavailable.
- 2h trend unavailable.
- 4h trend unavailable.
- 1m trend unavailable.
- family evidence unavailable.

Do NOT weaken the quality gate to compensate.

## URGENT OWNER ACTION 1 — DEPLOY DASHBOARD PATCH
Upload the current main version of:
- hostinger_patch/operator.php

to the existing STC public_html directory, replacing only the deployed operator.php.

Expected visible additions:
- Competition Watchlist — strongest blocked candidates.
- MTF LIVE CONFIRMATION OFFLINE warning when required evidence is absent.

Do not replace bridge/database files.

## URGENT OWNER ACTION 2 — CREATE SIX v1.1 TRADINGVIEW ALERTS
Follow:
- docs/MTF_PRODUCTION_ACTIVATION.md

Create these six fresh indicator alerts from the current scripts:
1. STC CAPITAL MTF A v1.1 PROD
2. STC CAPITAL MTF B v1.1 PROD
3. STC AMP MTF A v1.1 PROD
4. STC AMP MTF B v1.1 PROD
5. STC AMP MTF C v1.1 PROD
6. STC AMP MTF D v1.1 PROD

Settings:
- chart timeframe 15m;
- Any alert() function call;
- existing STC webhook;
- keep legacy production alerts running in parallel;
- do not disable Safe Mode/Kill Switch.

After creation, immediately perform a full-cycle acceptance:
- Capital A 5 events.
- Capital B 5 events.
- AMP A/B/C/D 4 events each.
- all webhook HTTP 200.
- no study_error/auto-stop.
- fresh Hostinger cards must no longer show missing MTF/family evidence.

Only then reassess current A+ opportunities.

## CURRENT WATCH-ONLY CANDIDATES
Not actionable and no locked plan:
- CME_MINI:M6E1! bearish bias.
- CAPITALCOM:ETHUSD bullish bias.
- CAPITALCOM:SPX500 bullish bias.
- CAPITALCOM:EURUSD bearish bias.
- CAPITALCOM:BTCUSD bullish bias.

Do not enter these from the watchlist.

## TELEGRAM
Telegram delivery remains blocked by missing private Hostinger config:
- telegram_bot_token
- telegram_chat_id
Do not paste values into chat or commit them.

## EXECUTION BOUNDARY
- No automatic trading.
- A trade is actionable only after fresh v1.1 evidence produces an A+ locked plan.
- Human approval and manual order entry remain mandatory.
- Executed positions remain persistent and are managed by Portfolio Supervisor.
- One Final TP only.
