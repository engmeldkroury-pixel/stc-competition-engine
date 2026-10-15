# STC — Next TradingView The Leap Contest Readiness (2026-10-15)

Owner scope: prepare NOW for the next legally eligible future competition. No enrollment or account execution was authorized. Separately maintain Crypto Spot Lab (16 USDT pairs, cash spot long-only, no futures/leverage/short).

## Immutable contest entry gate
A new event must be declared UNKNOWN / NOT_ACTIVE until the official rules URL, timing, eligible legal residence, cutoff, eligible account and symbol universe, initial Paper balance, minimum qualifying trading days, drawdown scoring, risk/penalty restrictions, actual owner registration and exact TradingView Paper subaccount are verified.

Official source: https://www.tradingview.com/the-leap/ ; official help: https://www.tradingview.com/support/solutions/43000721308-how-to-compete-in-the-leap/ .
Each The Leap edition has its OWN Terms and Conditions and allowed symbols. Do not claim the user's legal residence simply from their laptop location. Never fabricate registration, positions or an eligible competitor account.

## Score-policy router, contest-specific
- Some events rank REALIZED PNL% only; do not confuse open PnL with closed PnL or guess sizing when account history is missing.
- Other events, such as the October Commodities 2026 contest, rank realized profit (%) divided by max(max_equity_drawdown_percent, 5%). The drawdown path may include OPEN positions; exact official rules override the generic formula.
- Qualification may require trading on at least three distinct days or different rules, and a successful backtest is not evidence of satisfying the actual Paper account requirements.
- A tournament-maximizing strategy is NOT automatically the same as robust individual-account cash Spot performance. Never transpose Futures/short/leverage signals into the owner's cash Spot 16-track.
- The October 2026 Commodities event registration closed Oct 14 08:00 UTC. The Phillip Nova Oct event may be region-restricted; never auto-join without independently confirming legal territory.

## Template for the next official event
Intake required fields: `competition_id`, `official_rules_url`, `rules_sha256`, `owner_registration_evidence`, `verified_legal_country`, `open_utc`, `registration_close_utc`, `end_utc`, `permitted_exact_symbols`, `Paper_account_id`, `scoring_type`, `score_floor`, `qualifying_days`, `initial_balance`, `manual_execution_mode`.
State machine: DISCOVERED -> RULES_VERIFIED -> OWNER_ELIGIBILITY_CONFIRMED -> REGISTRATION_CONFIRMED -> RESEARCH_READY -> MANUAL_PAPER_READY (only if strategy independently validated) -> ENDED_ARCHIVE.

## Competition strategy qualification
1. Parse fixed contest score; prevent strategy selection against a wrong leaderboard objective.
2. Obtain original exact-symbol bars and correct timezones/provider source; never substitute Binance Spot for a restricted CME futures Paper instrument.
3. Compare credible simple baselines and a small set of predeclared alternative hypotheses, with realistic spreads, costs, execution delay and account risk. Positive contaminated historical holdout or one lucky ticker is NOT enough.
4. Validate true chronological untouched test and actual forward manual Paper fills/stops, risk budget and score path.
5. Owner approves all Stage 1 entries/exits manually, with 60-second independent server supervision only for genuinely verified account and fresh price data.
6. End of event -> archival, no old-event email/Telegram or stale entry signals. Do not close or declare closed a position without external proof.

## Current gate status
- Competition engine intake gateway present in `app/competition_intake_gate.py` (fails closed on unknown cutoff/country).
- STC production 60-second Cron monitoring already demonstrated 30 consecutive minutes in GitHub run `38726148905`. This is infrastructure health only, NOT a winning strategy or validated account data feed.
- Previous Sept contest notifications still suppressed; STC email disabled.
- No future The Leap event fully identified and confirmed as both owner eligible and registered at the time of this document. No manual contest Paper orders or financial market purchases authorized by this research.
- Elite KERNEL Council requires genuine Claude/Gemini/DeepSeek/Grok readbacks; do not create fabricated approvals.

**Disposition: infrastructure PREPARED; future event STRATEGY HOLD pending official event and real forward evidence; no trade authority.**
