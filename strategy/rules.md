# Trading Rules

> PLACEHOLDER — replace with your own strategy. This file is loaded on every run
> and is the single source of truth for trading logic beyond hard risk limits.

## Entry Criteria

- TODO: Define signal(s) that trigger an open.
- TODO: Define confirmation requirements (volume, trend, news).

## Exit Criteria

- TODO: Define stop-loss placement (e.g., -1.5% from entry).
- TODO: Define profit target (e.g., +3% or trailing stop).
- TODO: Define time stop (e.g., close by EOD if not hit target).

## Position Sizing

- TODO: Define per-trade risk (e.g., 0.5% of equity at stop).
- TODO: Define max exposure per symbol.

## Market Regime Filters

- TODO: Skip trading if VIX > X.
- TODO: Skip trading on FOMC days / major econ prints.

## News Handling

- TODO: How Perplexity briefs inform watchlist.
- TODO: Hard stop on symbol if breaking negative news post-entry.

---

Risk limits in `strategy/risk_limits.yaml` are enforced by code and OVERRIDE anything in this file.
The symbol universe in `strategy/universe.yaml` is also enforced by code.
