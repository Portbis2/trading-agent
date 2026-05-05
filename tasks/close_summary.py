"""3:45 PM ET — end-of-day P&L summary and position report."""

from __future__ import annotations

from datetime import datetime, timezone

from src.notify import notify
from src.state import read_stops


def run(ctx: dict) -> None:
    config = ctx["config"]
    positions = ctx["positions"]
    account = ctx["account"]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    equity = float(account.get("equity", 0))
    day_pnl = float(account.get("day_pnl", 0))
    day_start = float(account.get("day_start_equity") or equity)
    day_pnl_pct = (day_pnl / day_start * 100) if day_start > 0 else 0

    stops = read_stops()

    lines = [
        f"Date: {today}",
        f"Equity: ${equity:,.2f}  |  Day P&L: ${day_pnl:+,.2f} ({day_pnl_pct:+.2f}%)",
        "",
    ]

    if positions:
        lines.append(f"Open positions ({len(positions)}):")
        for symbol, pos in positions.items():
            qty = float(pos.get("qty", 0))
            avg = float(pos.get("avg_entry", 0))
            mv = float(pos.get("market_value", 0))
            upl = float(pos.get("unrealized_pl", 0))
            upl_pct = (upl / (avg * qty) * 100) if avg * qty > 0 else 0
            stop_meta = stops.get(symbol, {})
            stop = stop_meta.get("stop", "?")
            target = stop_meta.get("target", "?")
            lines.append(
                f"  {symbol}: {qty:.0f} shares @ ${avg:.2f}  MV=${mv:,.0f}  "
                f"UPL=${upl:+,.0f} ({upl_pct:+.1f}%)  stop={stop}  target={target}"
            )
    else:
        lines.append("No open positions.")

    report = "\n".join(lines)
    print(f"\n[close_summary]\n{report}\n")
    notify(config, f"Close summary — {today}", report)

    pnl_sign = "+" if day_pnl >= 0 else ""
    ctx["summary"] = (
        f"close_summary: equity=${equity:,.0f}  day P&L={pnl_sign}{day_pnl_pct:.2f}%  "
        f"positions={len(positions)}"
    )
