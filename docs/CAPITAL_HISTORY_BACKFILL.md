# Capital.com historical backfill (research-only)

Purpose: obtain older Capital.com historical candles when TradingView Official MCP is capped at its current per-request history window.

## Safety and authority
- Read-only market-data integration only.
- No order, position, account-setting or execution endpoint is used.
- Credentials are read only from runtime environment variables and must never be committed.
- Capital.com REST bid/ask candles are **not assumed identical** to TradingView `CAPITALCOM:` chart bars.
- Derived OHLC therefore remains research/backfill evidence until overlap reconciliation proves the selected price basis and symbol/epic mapping are acceptable.
- A passing strategy on this backfill cannot directly promote live calibration.

## Required runtime variables
- `CAPITAL_API_KEY`
- `CAPITAL_IDENTIFIER`
- `CAPITAL_PASSWORD`

The script defaults to the Capital.com demo API. `--live` only changes the market-data base URL; it still does not include trading calls.

## Example shape
```bash
python scripts/fetch_capital_history.py \
  --symbol CAPITALCOM:XAUUSD \
  --epic GOLD \
  --resolution MINUTE_15 \
  --from 2025-09-01T00:00:00Z \
  --to 2026-09-01T00:00:00Z \
  --price-basis mid \
  --output research_archive/xauusd/capital_15m.json
```

Verify the Capital.com epic using the authenticated market catalogue before any real backfill. Do not assume TradingView ticker text equals the Capital.com epic.
