# NEXT TASK

Updated: 2026-09-23

## PRIMARY PRODUCT OBJECTIVE
Operate and complete STC as a Hostinger-based competition control system, not as a research-only candle project.

Primary flow:
TradingView production feeds -> Hostinger/MySQL source of truth -> STC analysis/ranking -> Owner Console -> Telegram/mobile alert -> human approval -> manual competition order entry -> persistent open-position tracking -> HOLD/PROTECT/EXIT management -> competition progress/rule compliance.

Historical research, feature calibration, and frozen unseen-data confirmation remain supporting subsystems only. They must improve evidence quality without displacing the product workflow.

## VERIFIED LIVE PRODUCT
Live console:
- https://stc.feama.site/operator.php
- Capital.com Africa lane: 10 monitored symbols.
- AMP Futures lane: 16 monitored symbols.
- Portfolio Supervisor: deployed.
- Competition Progress: deployed.
- Macro calendar gate: connected.
- Browser/server notification center: deployed.
- Auto refresh: deployed.
- Safe Mode=true.
- Kill Switch=true.
- No automatic broker/order execution exists.

Latest authenticated readback: run 35813971595.
- 26 current cards total.
- 0 active opportunities at the readback instant.
- 0 manual-ready opportunities.
- 0 recorded open positions.
- Capital.com Africa progress: 0/3 qualifying days.
- AMP Futures progress: 0/5 qualifying days.
- Durable notification events: 35.
- Telegram configured=false.
- Email configured=false.
- Notification deliveries: 0.

## ACTIVE COMPETITIONS
1. The Leap by AMP Futures — September 2026
   - competition_id: amp-futures-sep-2026
   - initial balance: USD 250,000
   - first prize: USD 10,000
   - minimum trading days: 5
   - scoring: realized P/L on closed positions
   - futures leverage: 20:1
   - current STC production feed: 16 core symbols
2. The Leap by Capital.com Africa — September 2026
   - competition_id: capital-africa-sep-2026
   - initial balance: USD 100,000
   - first prize: USD 3,000
   - minimum trading days: 3
   - scoring: realized P/L on closed positions
   - leverage: forex 25:1, crypto 1:1, other 10:1
   - commission: 0.01%
   - current STC production feed: 10 symbols

The current authoritative project contains exactly these two active competition profiles. Do not invent a third profile.

## OWNER CONSOLE REQUIREMENTS
The live page must continue to provide:
- ranked active opportunities across both competitions;
- separate Capital.com Africa and AMP Futures tabs;
- explicit order type, quantity, risk, entry zone, Stop, and one Final TP;
- persistent executed/open positions that cannot be replaced by later signals;
- management state: HOLD / PROTECT / EXIT_NOW;
- no operational TP1/TP2 split; target1 remains internal management checkpoint only and target2 is the owner-facing Final TP;
- competition progress: qualifying days, days remaining, entries, open/closed trades, actions, realized P/L;
- official competition-rule summary and official-rule link;
- browser + Telegram/email notification status and delivery audit;
- manual approval/manual execution only.

## IMMEDIATE PRODUCT WORK
1. Merge the competition-rules dashboard patch only after CI passes.
2. Keep the live Owner Console as the primary operational surface.
3. Preserve signal ranking/filtering and only surface active A+ locked opportunities as actionable.
4. Preserve the 26-symbol dual-feed health: 10 Capital + 16 AMP.
5. Keep Portfolio Supervisor persistent for executed trades.
6. Continue background research only as support; do not change the product priority or enable 15m authority from research-only results.

## CURRENT OWNER-ONLY BLOCKERS
### Telegram
Telegram code and audit tables are deployed, but live Hostinger config currently has no Telegram credentials.
Required private Hostinger config values:
- telegram_bot_token
- telegram_chat_id
Never paste these into chat or commit them to GitHub.

### Historical/open trade ledger
The live ledger currently contains zero positions and zero past trades. STC can import them, but exact platform records are required. Do not invent prior trades. Use actual competition screenshots/records to backfill:
- competition
- symbol
- side
- quantity
- entry
- original open time
- final TP / stop if applicable
- close time and realized P/L for closed trades

## SAFETY
- Safe Mode and Kill Switch stay ON until owner explicitly changes them after product validation.
- Manual approval and manual execution remain mandatory.
- No auto-trading.
- New signals never replace an executed position.
- Competition rule validation must match the real active competition.
