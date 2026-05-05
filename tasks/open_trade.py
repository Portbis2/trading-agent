"""9:30 AM ET — enter positions on SDS breakout signals confirmed from pre-market screen."""

from __future__ import annotations

from datetime import datetime, timezone

from src.notify import notify
from src.risk import AccountSnapshot, ProposedOrder, check_order
from src.screener import STOP_PCT, calc_position
from src.state import append_journal, read_stops, read_watchlist, write_stops


def run(ctx: dict) -> None:
    config = ctx["config"]
    broker = ctx["broker"]
    positions = ctx["positions"]
    account = ctx["account"]
    limits = ctx["limits"]
    universe = ctx["universe"]

    if broker is None:
        notify(config, "open_trade: no broker", level="high")
        ctx["summary"] = "open_trade skipped (no broker)"
        return

    watchlist = read_watchlist()
    if not watchlist:
        print("[open_trade] Watchlist empty — run premarket_brief first.")
        ctx["summary"] = "open_trade skipped (empty watchlist)"
        return

    # Market regime gate: SPY must be Stage 2
    spy_row = next((r for r in watchlist if r["symbol"] == "SPY"), None)
    if spy_row and spy_row.get("score", 0) < 60:
        msg = f"Market regime check failed (SPY score={spy_row['score']}). No new opens."
        print(f"[open_trade] {msg}")
        notify(config, "open_trade: no-trade day", msg)
        ctx["summary"] = msg
        return

    equity = float(account.get("equity", 0))
    if equity <= 0:
        print("[open_trade] Account equity unavailable.")
        ctx["summary"] = "open_trade skipped (no equity)"
        return

    stops = read_stops()
    orders_placed: list[str] = []
    orders_blocked: list[str] = []

    # Candidates: score ≥ 80 AND breakout today AND not already in position
    candidates = [
        r for r in watchlist
        if r.get("score", 0) >= 80
        and r.get("breakout_today")
        and r["symbol"] not in positions
        and "error" not in r
    ]

    if not candidates:
        print("[open_trade] No breakout candidates at score ≥ 80 today.")
        ctx["summary"] = "open_trade: no valid breakout candidates"
        return

    print(f"[open_trade] {len(candidates)} candidate(s): {[r['symbol'] for r in candidates]}")

    acct_snap = AccountSnapshot(
        equity=equity,
        cash=float(account.get("cash", equity)),
        day_pnl=float(account.get("day_pnl", 0)),
        day_start_equity=float(account.get("day_start_equity") or equity),
    )

    for candidate in candidates:
        symbol = candidate["symbol"]
        entry_price = candidate["close"]  # use last close as proxy for entry

        sizing = calc_position(equity, entry_price, max_pos_pct=limits.get("max_position_pct", 5) / 100)
        shares = sizing["shares"]
        stop_price = sizing["stop"]
        target_price = sizing["target"]

        order = ProposedOrder(
            symbol=symbol,
            side="buy",
            qty=float(shares),
            est_price=entry_price,
            order_type="market",
            is_opening=True,
        )

        ok, reason = check_order(order, acct_snap, positions, limits, universe)
        if not ok:
            msg = f"{symbol}: blocked by risk gate — {reason}"
            print(f"[open_trade] {msg}")
            orders_blocked.append(symbol)
            notify(config, f"open_trade: blocked {symbol}", msg)
            continue

        try:
            resp = broker.submit_order(
                symbol=symbol,
                side="buy",
                qty=float(shares),
                order_type="market",
                time_in_force="day",
            )
            print(f"[open_trade] BUY {shares}× {symbol} @ ~{entry_price:.2f}  stop={stop_price:.2f}  target={target_price:.2f}")
        except Exception as e:
            msg = f"{symbol}: order submission failed — {e}"
            print(f"[open_trade] ERROR: {msg}")
            notify(config, f"open_trade: submit error {symbol}", msg, level="urgent")
            orders_blocked.append(symbol)
            continue

        # Update in-memory positions and stop metadata
        positions[symbol] = {
            "qty": float(shares),
            "avg_entry": entry_price,
            "market_value": entry_price * shares,
            "unrealized_pl": 0.0,
            "side": "long",
        }
        stops[symbol] = {
            "stop": stop_price,
            "target": target_price,
            "entry_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "entry_price": entry_price,
        }

        append_journal({
            "symbol": symbol,
            "side": "buy",
            "qty": shares,
            "entry": entry_price,
            "stop": stop_price,
            "target": target_price,
            "reason": (
                f"SDS breakout: score={candidate['score']}, "
                f"pct_from_high={candidate['pct_from_high']}%, "
                f"rs_vs_spy={candidate['rs_vs_spy_pct']}%"
            ),
            "rule_citation": (
                "strategy/rules.md §3 Entry Criteria — score ≥ 80 + breakout on volume ≥ 1.5× avg"
            ),
        })
        orders_placed.append(symbol)

    write_stops(stops)
    ctx["positions"] = positions

    placed_str = ", ".join(orders_placed) if orders_placed else "none"
    blocked_str = ", ".join(orders_blocked) if orders_blocked else "none"
    if orders_placed:
        notify(
            config,
            f"open_trade: placed {len(orders_placed)} order(s)",
            f"Bought: {placed_str}\nBlocked: {blocked_str}",
        )
    ctx["summary"] = f"open_trade: bought [{placed_str}] blocked [{blocked_str}]"
