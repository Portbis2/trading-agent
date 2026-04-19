"""6:00 AM ET — pull news, update watchlist. Phase 1 stub."""

from __future__ import annotations


def run(ctx: dict) -> None:
    print("[premarket_brief] STUB — implement in phase 2")
    print(f"  universe: {ctx.get('universe')}")
    print(f"  open positions: {len(ctx.get('positions', {}))}")
    ctx["summary"] = "premarket_brief stub ran"
