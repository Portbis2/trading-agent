"""Pre-trade risk gate. Every order passes through check_order() BEFORE submission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Side = Literal["buy", "sell"]


@dataclass(frozen=True)
class ProposedOrder:
    symbol: str
    side: Side
    qty: float
    est_price: float              # best-available estimate for notional sizing
    order_type: str = "market"    # "market", "limit", etc.
    is_opening: bool = True       # opening a new position vs. closing existing
    is_short: bool = False
    is_option: bool = False
    is_leveraged: bool = False


@dataclass(frozen=True)
class AccountSnapshot:
    equity: float
    cash: float
    day_pnl: float = 0.0
    day_start_equity: float | None = None


def check_order(
    order: ProposedOrder,
    account: AccountSnapshot,
    positions: dict,
    limits: dict,
    universe: list[str],
) -> tuple[bool, str]:
    """Return (ok, reason). If ok is False, reason cites which rule blocked."""

    # 1. Universe
    symbol = order.symbol.upper().strip()
    if symbol not in {t.upper() for t in universe}:
        return False, f"symbol {symbol} not in universe.yaml"

    # 2. Instrument type gates
    if order.is_option and not limits.get("allow_options", False):
        return False, "options blocked by risk_limits.yaml (allow_options=false)"
    if order.is_short and not limits.get("allow_shorts", False):
        return False, "shorts blocked by risk_limits.yaml (allow_shorts=false)"
    if order.is_leveraged and not limits.get("allow_leverage", False):
        return False, "leverage blocked by risk_limits.yaml (allow_leverage=false)"

    # 3. Sanity on inputs
    if order.qty <= 0:
        return False, f"qty must be > 0 (got {order.qty})"
    if order.est_price <= 0:
        return False, f"est_price must be > 0 (got {order.est_price})"
    if account.equity <= 0:
        return False, f"account equity must be > 0 (got {account.equity})"

    # 4. Daily loss halt — only blocks new OPENS, not closes/risk-offs
    if order.is_opening:
        max_daily_loss_pct = float(limits.get("max_daily_loss_pct", 100))
        start_eq = account.day_start_equity or account.equity
        if start_eq > 0:
            loss_pct = (-account.day_pnl / start_eq) * 100.0
            if loss_pct >= max_daily_loss_pct:
                return (
                    False,
                    f"daily loss {loss_pct:.2f}% >= max_daily_loss_pct "
                    f"{max_daily_loss_pct}%",
                )

    # 5. Max open positions — only blocks new OPENS on NEW symbols
    if order.is_opening and symbol not in positions:
        max_open = int(limits.get("max_open_positions", 999))
        if len(positions) >= max_open:
            return (
                False,
                f"open positions {len(positions)} >= max_open_positions {max_open}",
            )

    # 6. Max position size as % of equity (opens only)
    if order.is_opening:
        max_pos_pct = float(limits.get("max_position_pct", 100))
        notional = order.qty * order.est_price

        existing_qty = 0.0
        if symbol in positions:
            try:
                existing_qty = float(positions[symbol].get("qty", 0) or 0)
            except (TypeError, ValueError, AttributeError):
                existing_qty = 0.0
        projected_notional = notional + (existing_qty * order.est_price)
        pct = (projected_notional / account.equity) * 100.0
        if pct > max_pos_pct:
            return (
                False,
                f"position size {pct:.2f}% of equity > max_position_pct "
                f"{max_pos_pct}% (notional ${projected_notional:.2f})",
            )

    return True, "ok"
