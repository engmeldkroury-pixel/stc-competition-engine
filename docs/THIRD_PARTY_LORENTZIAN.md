# Third-Party Research Dependency — AI Edge Lorentzian Classification

Updated: 2026-09-24

STC research uses the official AI Edge Python port of **Machine Learning: Lorentzian Classification** as a pinned research dependency.

Upstream:
- Repository: https://github.com/artificial-intelligence-edge/lorentzian-classification
- Pinned commit: 27776bd51cbd3e07b6383cfa468d4d33f4b50297
- Python package location: ports/python
- License: MIT
- Original TradingView indicator: https://www.tradingview.com/script/WhBzgfDu-Machine-Learning-Lorentzian-Classification/

Why STC uses the official port:
- the owner requested exact/credible community-indicator benchmarking rather than loose approximations;
- the upstream Python port is explicitly parity-tested against Pine/TradingView fixtures;
- it preserves the original feature engineering, Lorentzian ANN, filters, kernel logic, prediction/direction stream, Buy/Sell markers, exits, alerts, backtest stream and trade-stat behavior.

STC integration boundary:
- STC does not copy upstream source into its own indicator implementation.
- requirements.txt pins the exact upstream commit and Python subdirectory.
- STC maps only the official confirmed buy / sell booleans into the generic research signal format.
- STC's own standardized benchmark controls entry timing, transaction-cost proxy, stop/target handling, train/test/forward separation and frozen confirmation.
- Popularity/reviews do not affect score or weight.
- This dependency has research authority only; it cannot change the live A+ gate or execute orders.

License notice:
The upstream project is MIT licensed. Copyright and license terms remain those of AI Edge and are available in the upstream LICENSE.md.
