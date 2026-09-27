# Conditional replay of the pictured BTCUSD trade

Date: 27 September 2026. This case is separate from the aggregate R9 next-full-open model and is NOT an independently verified broker execution transcript.

## Evidence and assumptions

The owner's screenshot shows CAPITALCOM:BTCUSD LONG 0.5, entry fill 84,564.60, stop order 84,300, stop fill 84,299.80, target order 85,500, entry commission 4.2282 and exit commission 4.215. The displayed order placement time is 2026-09-27 09:17:01. Placement time is not a proven fill time or close time.

Conditional time interpretation: use the previously documented Egypt UTC+3 mapping, so placement is approximately 06:17:01 UTC, and model the shown fill as occurring within the 06:15-06:30 UTC source bar. The exact execution timestamp and broker bid/ask trigger basis remain unconfirmed.

The exact-provider TradingView connector supplied a 65-bar BTCUSD 15m response. Combining its earlier closed prefix with the preceding 40-bar probe and applying the original dataset cutoff 20:10:47 UTC yields 63 closed observed bars. The latest mutable tail was excluded. All 58 overlapping candles agree exactly with the stored normalized source; five observed candles are additional. This is a limited price-consistency check, not certification of all market history or sessions.

Bar snapshot canonical SHA256:
`d24205900021c2ea139831e3daec61bc6f3e2d8ef72a51a2fe1bb81d2fc8b68d`

## Conditional price-path findings

Initial price risk = 84,564.60 - 84,300 = 264.60 per unit. The initial 06:15 bar touches neither the stop nor 1R, so its unobserved intrabar ordering does not affect these particular barrier comparisons.

| Barrier from pictured entry | Price | First observed touch bar, UTC |
|---|---:|---|
| 1R | 84,829.20 | 08:15 |
| 1.5R | 84,961.50 | 10:00 |
| 2R | 85,093.80 | 13:30 |
| 2.5R | 85,226.10 | Not reached before stop touch |
| Initial stop | 84,300.00 | 17:00 |

Maximum observed high before the stop-touch bar: 85,118.60, on the 13:30 UTC bar. Favorable excursion from the shown entry is approximately 2.093726R or USD 277 of gross unrealized price movement for 0.5 units. This is NOT a realized gain, and a chart touch is not a guarantee of executable profit after spreads, fees, slippage or manual delay.

The first chart stop-touch bar at 17:00 UTC is NOT a verified broker close timestamp. Do not import this assumed timestamp into the ledger.

## Target difference does not alone explain the loss

The closest preceding stored plan, under the same timezone assumption, is `plan-b1c653b579bc53a16199a3aa705b81e6`, issued 06:15:13.492745 UTC, with initial stop approximately 84,301.7338 and final target approximately 85,189.5655. The pictured target is 85,500. Linkage remains tentative without matching execution/source-plan IDs.

Neither 85,189.5655 nor 85,500 was touched before the first stop-touch bar in this conditional replay. Therefore the target discrepancy alone cannot explain this case's loss. The favorable excursion does motivate further profit-retention testing tied to the actual entry, but does not validate a universal smaller target or any particular protection policy.

## Why this differs from the aggregate diagnostics

The R9 aggregate uses the next fully observable bar open after signal availability, an entry envelope, a fixed 32-bar horizon, and outcome-independent nonoverlap. This case uses the pictured actual entry, an assumed within-bar fill time, and a longer observed path. Those are different experiments and must not be mixed as if they used identical entries or denominators.

The aggregate finding that eight initially evaluable original-plan observations stopped before 1R is not a claim about this exact executed trade. Missing paths can also bias which hypothetical cases become evaluable first.

No bars from this case probe were silently added to the previously reported 73-case base or 75-case supplemented aggregate datasets. The case inputs and machine-readable result are preserved separately in the conversation evidence package as `btc-case-observed-bars.json` and `btc-screenshot-conditional-replay.json`.

## Decision

No ledger write, equity attestation, live stop widening, target change, broker action or strategy promotion. Obtain exact execution identities/times for confirmed attribution, then compare actual-entry-aware exit and initial-stop policies with independent evidence.
