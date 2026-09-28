# R10 pre-registered forward review gates — 28 September 2026

These gates are frozen before prospective outcomes are available. They exist to prevent changing the definition of success after seeing the data.

States:
- **COLLECTING**: fewer than 12 valued forward trades.
- **REJECT_OR_RESEARCH**: once at least 12 are valued, non-positive mean, PF below 0.90, or drawdown above 8R is a rejection/research signal.
- **EARLY_POSITIVE**: positive early evidence that is still insufficient for promotion review.
- **ELIGIBLE_FOR_REVIEW**: only a request for a separate human/code review. It is never automatic live promotion.

To become ELIGIBLE_FOR_REVIEW, the same frozen protocol version must have at least 30 valued trades across at least 5 UTC days, mean net result >=0.10R, PF>=1.20, max drawdown<=6R, no single positive day contributing over60% of all positive day P/L, and a positive one-sided 80% lower bound on mean R.

Forward evidence must use the frozen record identities and realistic cost stress. Censored paths do not count as valued wins/losses. No retuning on forward observations is allowed for the same protocol version.

These thresholds are engineering review gates, not a guarantee of future profitability or permission for automatic execution.
