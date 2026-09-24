# Corrected Lorentzian + VuManChu 15m Evidence Checkpoint

Updated: 2026-09-24

## Scope

This checkpoint records the corrected post-PR #129/#132 research run without overstating incomplete evidence.

- Workflow: 35969652488.
- Trigger: `2ed98f6b110cfbcb4f7a02c8af542109dd7362ab`.
- Intended scope: 26 competition symbols, 5,000 exact TradingView 15m bars each.
- Corrected successful artifacts: 17 symbols.
- Deferred before runner start: 9 symbols.
- Each successful corrected artifact contains 20 community trials and explicitly includes both `lorentzian_classification` and `vumanchu_cipher_b`.

## Official Lorentzian — authoritative partial result

The pinned official AI Edge port is verified in 17 corrected artifacts.

Validated so far:

- CAPITALCOM:USDZAR — robust score 44.3006.
  - TEST: 28 trades, expectancy 0.4091R, PF 2.001.
  - FORWARD: 19 trades, expectancy 0.2944R, PF 1.812.
- CBOT:ZB1! — robust score 23.2508.
  - TEST: 39 trades, expectancy 0.1962R, PF 1.399.
  - FORWARD: 36 trades, expectancy 0.1576R, PF 1.272.

Current official-port statement is therefore **2/17 validated**, not 2/26.

The remaining nine symbols require execution of the same official pinned port before a full 26-symbol Lorentzian pass rate can be stated.

## VuManChu Cipher B

- Corrected GitHub artifacts: 0/17 validated.
- The nine deferred symbols were independently checked against fresh exact TradingView 15m data using the current causal STC VuManChu semantics and TRAIN-only parameter grid: 0/9 validated.
- Combined diagnostic result: **0/26 validated**.

This negative completion is research diagnostic evidence. It does not grant or remove live authority by itself.

## Infrastructure blocker

The nine deferred jobs did not fail inside STC code. They failed before any workflow step began:

- the same nine matrix entries returned `steps=null` across workflow attempts;
- dedicated retry workflow 35971669454 also returned `steps=null` for all nine;
- unrelated PR #135/#136 CI jobs also returned `steps=null`.

This is classified as a GitHub Actions runner/account/quota pre-start blocker, not a strategy or test failure.

The canonical full benchmark workflow was restored on the research branch at:

`aa21f072ca5d1d0a2b2e5c92e17b3dee56ac5e13`

## Live boundary

No A+ threshold, risk setting, competition rule, position sizing rule, or execution behavior is changed by this checkpoint.

`live_authority=false`
