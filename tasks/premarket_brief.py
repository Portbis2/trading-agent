"""6:00 AM ET — screen universe with SDS Trend Template, build watchlist, check open positions."""

from __future__ import annotations

from datetime import datetime, timezone

from src.notify import notify
from src.screener import screen_universe
from src.state import write_watchlist


def run(ctx: dict) -> None:
    config = ctx["config"]
    broker = ctx["broker"]
    universe = ctx["universe"]
    positions = ctx["positions"]

    if broker is None:
        notify(config, "premarket_brief: no broker", "Skipping — broker unavailable.", level="high")
        ctx["summary"] = "premarket_brief skipped (no broker)"
        return

    print(f"[premarket_brief] Screening {len(universe)} symbols via SDS Trend Template…")
    results = screen_universe(broker, universe)
    write_watchlist(results)

    # Market regime: SPY must be in Stage 2 for new opens
    spy_row = next((r for r in results if r["symbol"] == "SPY"), None)
    spy_score = spy_row["score"] if spy_row else 0
    market_ok = spy_score >= 60
    regime_msg = (
        "SPY Stage 2 ✓" if market_ok
        else f"SPY score={spy_score} — market NOT Stage 2, no new opens today"
    )
    print(f"[premarket_brief] Market regime: {regime_msg}")

    # Print screen results table
    header = f"{'Symbol':<8} {'Score':>5}  {'Close':>7}  {'%FromHi':>8}  {'RS%':>6}  {'↑W':>4}  {'↓W':>4}  {'Breakout':>8}  TT1.0"
    print(header)
    print("-" * len(header))
    for r in results:
        if "error" in r:
            print(f"{r['symbol']:<8}  ERROR: {r['error']}")
            continue
        brk = "YES" if r.get("breakout_today") else "no"
        t10 = "PASS" if r.get("t10_pass") else "fail"
        print(
            f"{r['symbol']:<8} {r['score']:>5}  {r['close']:>7.2f}  "
            f"{r['pct_from_high']:>8.1f}%  {r['rs_vs_spy_pct']:>6.1f}%  "
            f"{r['up_weeks']:>4}  {r['down_weeks']:>4}  {brk:>8}  {t10}"
        )

    primaries = [r for r in results if r.get("score", 0) >= 80]
    watchlist = [r for r in results if 60 <= r.get("score", 0) < 80]
    breakouts = [r for r in results if r.get("score", 0) >= 60 and r.get("breakout_today")]

    lines = [f"Market: {regime_msg}"]
    if primaries:
        lines.append(f"Primary targets (≥80): {', '.join(r['symbol'] for r in primaries)}")
    if watchlist:
        lines.append(f"Watchlist (60-79): {', '.join(r['symbol'] for r in watchlist)}")
    if breakouts:
        lines.append(f"Breakout signals: {', '.join(r['symbol'] for r in breakouts)}")
    if positions:
        lines.append(f"Open positions: {', '.join(positions.keys())}")

    notify(
        config,
        f"Pre-market — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "\n".join(lines),
    )

    ctx["summary"] = (
        f"screened {len(universe)}: {len(primaries)} primary, "
        f"{len(breakouts)} breakout(s) | {regime_msg}"
    )
