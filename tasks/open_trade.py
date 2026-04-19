"""8:30 AM ET — act on premarket brief. Phase 1 stub."""

from __future__ import annotations


def run(ctx: dict) -> None:
    print("[open_trade] STUB — implement in phase 2")
    print(f"  paper_mode: {ctx['config'].paper_mode}")
    ctx["summary"] = "open_trade stub ran"
