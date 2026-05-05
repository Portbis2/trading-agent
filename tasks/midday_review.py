"""12:00 PM ET — check open positions against stops and SDS sell signals."""

from __future__ import annotations

from src.notify import notify
from src.risk import AccountSnapshot, ProposedOrder, check_order
from src.screener import compute_indicators, check_sell_signals
from src.state import append_journal, read_stops, write_stops


def run(ctx: dict) -> None:
    config = ctx["config"]
    broker = ctx["broker"]
    positions = ctx["positions"]
    account = ctx["account"]
    limits = ctx["limits"]
    universe = ctx["universe"]

    if broker is None:
        notify(config, "midday_review: no broker", level="high")
        ctx["summary"] = "midday_review skipped (no broker)"
        return

    if not positions:
        print("[midday_review] No open positions.")
        ctx["summary"] = "midday_review: no positions to review"
        return

    stops = read_stops()
    exits_triggered: list[str] = []
    equity = float(account.get("equity", 0))

    acct_snap = AccountSnapshot(
        equity=equity,
        cash=float(account.get("cash", equity)),
        day_pnl=float(account.get("day_pnl", 0)),
        day_start_equity=float(account.get("day_start_equity") or equity),
    )

    for symbol, pos in list(positions.items()):
        stop_meta = stops.get(symbol, {})
        stop_price = float(stop_meta.get("stop", 0))
        target_price = float(stop_meta.get("target", 0))
        entry_price = float(stop_meta.get("entry_price") or pos.get("avg_entry", 0))

        if stop_price <= 0:
            print(f"[midday_review] {symbol}: no stop recorded — skipping signal check")
            continue

        # Fetch latest bars for indicator computation
        try:
            bars = broker.get_bars(symbol, timeframe="1Day", lookback_days=320)
        except Exception as e:
            print(f"[midday_review] {symbol}: bars fetch error — {e}")
            continue

        ind = compute_indicators(bars)
        if ind is None:
            print(f"[midday_review] {symbol}: insufficient data for indicators")
            continue

        current_price = ind["close"]
        pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
        print(
            f"[midday_review] {symbol}: price={current_price:.2f}  stop={stop_price:.2f}  "
            f"target={target_price:.2f}  P&L={pnl_pct:+.1f}%"
        )

        signal = check_sell_signals(ind, entry_price, stop_price)
        if not signal["triggered"]:
            continue

        # Sell signal fired — submit exit order
        qty = float(pos.get("qty", 0))
        if qty <= 0:
            continue

        order = ProposedOrder(
            symbol=symbol,
            side="sell",
            qty=qty,
            est_price=current_price,
            order_type="market",
            is_opening=False,
        )
        ok, reason = check_order(order, acct_snap, positions, limits, universe)
        if not ok:
            print(f"[midday_review] {symbol}: sell blocked by risk gate — {reason}")
            continue

        try:
            broker.submit_order(symbol=symbol, side="sell", qty=qty, order_type="market", time_in_force="day")
            print(f"[midday_review] SELL {qty}× {symbol} @ ~{current_price:.2f}  reason: {signal['signal_name']}")
        except Exception as e:
            notify(config, f"midday_review: sell error {symbol}", str(e), level="urgent")
            continue

        append_journal({
            "symbol": symbol,
            "side": "sell",
            "qty": qty,
            "entry": entry_price,
            "stop": stop_price,
            "target": target_price,
            "reason": signal["reason"],
            "rule_citation": f"strategy/rules.md §5 Exit — {signal['signal_name']}",
        })

        notify(
            config,
            f"midday_review: EXIT {symbol}",
            f"{signal['signal_name']}: {signal['reason']}\nP&L: {pnl_pct:+.1f}%",
        )

        del positions[symbol]
        if symbol in stops:
            del stops[symbol]
        exits_triggered.append(symbol)

    write_stops(stops)
    ctx["positions"] = positions

    if exits_triggered:
        exited = ", ".join(exits_triggered)
        ctx["summary"] = f"midday_review: exited [{exited}]"
    else:
        ctx["summary"] = f"midday_review: {len(positions)} position(s) held, no exit signals"
