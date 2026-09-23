# STC Community Indicator Wave 3 Audit

Updated: 2026-09-24

## Purpose

Expand the practical community-indicator research pool without allowing popularity or chart appearance to bypass the STC causal/OOS/frozen-evidence rules.

## Public-source findings

### Trendilo
Source:
- https://www.tradingview.com/script/h5kMWewu-Trendilo-OPEN-SOURCE/

Public description:
- open-source;
- trend state is based on smoothed percentage change;
- ALMA is compared with an RMS band;
- bullish/bearish/sideways state is derived from that comparison.

STC treatment:
- independent confirmed-bar ALMA/RMS implementation;
- bounded parameters selected on TRAIN only;
- no direct live authority.

### Nadaraya-Watson Envelope [LuxAlgo]
Source:
- https://www.tradingview.com/script/Iko0E2kL-Nadaraya-Watson-Envelope-LuxAlgo/

Public description/release note:
- the script can run in repainting or non-repainting mode;
- a later release explicitly added a full non-repainting mode.

STC treatment:
- only endpoint/past-current-bar kernel estimation is implemented;
- centered smoothing/repainting mode is forbidden from benchmark use;
- a signal is emitted only after a confirmed close re-enters from outside the causal envelope.

### CM Williams Vix Fix
Source:
- https://www.tradingview.com/script/og7JPrRA-CM-Williams-Vix-Fix-Finds-Market-Bottoms/
- https://www.tradingview.com/script/fDvRQGmk-CM-Williams-Vix-Fix-Market-Top-and-Bottom-with-multi-timeframe/

Public description:
- original script is a synthetic volatility-spike detector intended to find market bottoms;
- the author notes that settings may need adjustment by asset class;
- an open-source derivative documents a mirrored market-top context and says confirmed-close operation does not repaint.

STC treatment:
- original bottom context plus an independently calculated mirrored top context;
- entries are generated only on confirmed spike release;
- parameters are asset/symbol/timeframe tested rather than assumed universal.

## Lorentzian Classification audit — remains pending exact implementation

Source:
- https://www.tradingview.com/script/WhBzgfDu-Machine-Learning-Lorentzian-Classification/

Verified public design facts:
- Lorentzian-distance Approximate Nearest Neighbors classifier;
- default neighbors count 8;
- default max bars back 2000;
- up to five engineered feature slots;
- feature choices include RSI, WaveTrend, CCI and ADX;
- volatility/regime/ADX filters are available;
- kernel-regression filter is part of the public design;
- public author states that closed bars do not repaint;
- author explicitly warns that the built-in Trade Stats display is not a substitute for proper backtesting.

STC decision:
- keep the original named component pending until its ANN neighbor-selection, feature normalization, filters and kernel semantics are reproduced causally enough to justify calling it the same indicator.
- do not substitute a simplistic KNN approximation under the original name merely to increase the catalog count.

## Community review handling

Community discussions are used only to identify:
- repaint warnings;
- live-usage issues;
- candidate popularity;
- which indicators deserve source audit next.

They do not contribute to robust score, expected win rate, or live trading weight.

## Resulting executable research pool

Wave 3 adds:
- Trendilo;
- Nadaraya-Watson Envelope — non-repainting endpoint mode only;
- CM Williams Vix Fix dual reversal-context adapter.

The executable community research pool increases from 14 to 17 components if CI passes.

No live A+ gate, risk rule, competition rule or order-execution behavior changes.
