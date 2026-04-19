"""Perplexity API wrapper. Stubbed in phase 1 — signatures only."""

from __future__ import annotations

from src.config import Config


def news_for(config: Config, symbol: str, lookback_hours: int = 24) -> str:
    """Return a concise news summary for a ticker. TODO: implement in phase 2."""
    _ = (config, symbol, lookback_hours)
    return f"[STUB] news_for({symbol}) — implement in phase 2"


def market_summary(config: Config) -> str:
    """Return a one-paragraph pre-market summary. TODO: implement in phase 2."""
    _ = config
    return "[STUB] market_summary() — implement in phase 2"
