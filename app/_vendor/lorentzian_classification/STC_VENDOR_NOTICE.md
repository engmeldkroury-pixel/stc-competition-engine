# Lorentzian Classification vendored reference

Source repository: artificial-intelligence-edge/lorentzian-classification

Pinned source commit:

27776bd51cbd3e07b6383cfa468d4d33f4b50297

Vendored files:
- ports/python/lorentzian_classification/core.py
- ports/python/lorentzian_classification/settings.py
- ports/python/lorentzian_classification/__init__.py
- root LICENSE.md
- tests/parity/baselines/pine_btcusd_h1_trimmed_limited_history.csv as an exact Pine/TradingView parity fixture

Purpose:
- establish exact semantic/parity evidence before STC treats Lorentzian Classification as a benchmarkable research component;
- avoid a runtime network dependency;
- preserve the upstream MIT license and copyright notice.

STC integration rules:
- do not edit the vendored reference calculation to tune STC results;
- wrap it from STC research code;
- benchmark confirmed buy/sell signals causally;
- live_authority remains false.
