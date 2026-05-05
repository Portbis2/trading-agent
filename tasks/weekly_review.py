"""Friday 4:30 PM ET — weekly performance review and strategy re-screen."""

from __future__ import annotations

from datetime import datetime, timezone

from src.notify import notify
from src.screener import screen_universe
from src.state import read_stops, write_watchlist


def run(ctx: dict) -> None:
    config = ctx["config"]
    broker = ctx["broker"]
    positions = ctx["positions"]
    account = ctx["account"]
    universe = ctx["universe"]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    equity = float(account.get("equity", 0))

    lines = [f"Weekly Review — {today}", f"Equity: ${equity:,.2f}", ""]

    # Re-screen for next week's watchlist
    if broker:
        print("[weekly_review] Re-screening universe for next week…")
        results = screen_universe(broker, universe)
        write_watchlist(results)

        primaries = [r for r in results if r.get("score", 0) >= 80]
        stage2 = [r for r in results if r.get("score", 0) >= 60]

        lines.append(f"Universe screen ({len(universe)} symbols):")
        for r in results:
            if "error" in r:
                lines.append(f"  {r['symbol']}: ERROR — {r['error']}")
                continue
            brk = " [BREAKOUT]" if r.get("breakout_today") else ""
            lines.append(
                f"  {r['symbol']}: score={r['score']}  close={r['close']}  "
                f"pct_from_high={r['pct_from_high']}%  rs={r['rs_vs_spy_pct']}%{brk}"
            )
        lines.append("")
        lines.append(f"Primary targets next week: {[r['symbol'] for r in primaries] or 'none'}")
        lines.append(f"Stage 2 qualified: {[r['symbol'] for r in stage2] or 'none'}")
    else:
        lines.append("Broker unavailable — skipped re-screen.")

    # Open position review
    stops = read_stops()
    if positions:
        lines.append(f"\nOpen positions ({len(positions)}):")
        for symbol, pos in positions.items():
            qty = float(pos.get("qty", 0))
            avg = float(pos.get("avg_entry", 0))
            upl = float(pos.get("unrealized_pl", 0))
            upl_pct = (upl / (avg * qty) * 100) if avg * qty > 0 else 0
            meta = stops.get(symbol, {})
            entry_date = meta.get("entry_date", "?")
            lines.append(
                f"  {symbol}: {qty:.0f}sh @ ${avg:.2f}  held since {entry_date}  "
                f"UPL={upl_pct:+.1f}%  stop={meta.get('stop', '?')}  target={meta.get('target', '?')}"
            )
    else:
        lines.append("\nNo open positions.")

    report = "\n".join(lines)
    print(f"\n[weekly_review]\n{report}\n")
    notify(config, f"Weekly review — {today}", report)

    ctx["summary"] = f"weekly_review: equity=${equity:,.0f}  positions={len(positions)}"
