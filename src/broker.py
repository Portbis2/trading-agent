"""Alpaca wrapper. Paper mode is enforced — live requires env + ARMED gate via config."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from src.config import Config


class BrokerError(RuntimeError):
    pass


@dataclass
class Broker:
    """Thin facade over alpaca-py. Constructed from a validated Config.

    Phase 1 methods: get_account, get_positions, submit_order, get_bars.
    """

    config: Config

    def __post_init__(self) -> None:
        if self.config.paper_mode and "paper-api" not in self.config.alpaca_base_url:
            raise BrokerError(
                "Paper mode required but ALPACA_BASE_URL is not a paper endpoint. "
                f"Got: {self.config.alpaca_base_url}"
            )

        try:
            from alpaca.trading.client import TradingClient
            from alpaca.data.historical import StockHistoricalDataClient
        except ImportError as e:
            raise BrokerError(
                "alpaca-py is not installed. Run: uv sync"
            ) from e

        self._trading = TradingClient(
            api_key=self.config.alpaca_api_key,
            secret_key=self.config.alpaca_secret_key,
            paper=self.config.paper_mode,
        )
        self._data = StockHistoricalDataClient(
            api_key=self.config.alpaca_api_key,
            secret_key=self.config.alpaca_secret_key,
        )

    @property
    def paper(self) -> bool:
        return self.config.paper_mode

    def get_account(self) -> dict:
        """Return account snapshot as a plain dict."""
        a = self._trading.get_account()
        equity = float(getattr(a, "equity", 0) or 0)
        last_equity = float(getattr(a, "last_equity", 0) or 0)
        return {
            "equity": equity,
            "cash": float(getattr(a, "cash", 0) or 0),
            "buying_power": float(getattr(a, "buying_power", 0) or 0),
            "day_start_equity": last_equity,
            "day_pnl": equity - last_equity,
            "paper": self.paper,
            "status": str(getattr(a, "status", "")),
        }

    def get_positions(self) -> dict:
        """Return positions keyed by uppercase symbol."""
        out: dict[str, dict] = {}
        for p in self._trading.get_all_positions():
            sym = str(getattr(p, "symbol", "")).upper()
            if not sym:
                continue
            out[sym] = {
                "qty": float(getattr(p, "qty", 0) or 0),
                "avg_entry": float(getattr(p, "avg_entry_price", 0) or 0),
                "market_value": float(getattr(p, "market_value", 0) or 0),
                "unrealized_pl": float(getattr(p, "unrealized_pl", 0) or 0),
                "side": str(getattr(p, "side", "")),
            }
        return out

    def submit_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        order_type: str = "market",
        time_in_force: str = "day",
        limit_price: float | None = None,
    ) -> dict:
        """Submit an order. Risk gate MUST be checked upstream before calling this."""
        from alpaca.trading.enums import OrderSide, TimeInForce
        from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest

        side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        tif_map = {"day": TimeInForce.DAY, "gtc": TimeInForce.GTC}
        tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)

        if order_type == "market":
            req = MarketOrderRequest(
                symbol=symbol.upper(),
                qty=qty,
                side=side_enum,
                time_in_force=tif,
            )
        elif order_type == "limit":
            if limit_price is None:
                raise BrokerError("limit order requires limit_price")
            req = LimitOrderRequest(
                symbol=symbol.upper(),
                qty=qty,
                side=side_enum,
                time_in_force=tif,
                limit_price=limit_price,
            )
        else:
            raise BrokerError(f"unsupported order_type: {order_type}")

        resp = self._trading.submit_order(req)
        return {
            "id": str(getattr(resp, "id", "")),
            "symbol": symbol.upper(),
            "side": side.lower(),
            "qty": qty,
            "order_type": order_type,
            "limit_price": limit_price,
            "status": str(getattr(resp, "status", "")),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "paper": self.paper,
        }

    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Day",
        lookback_days: int = 30,
    ) -> list[dict]:
        """Return list of OHLCV bars for a single symbol."""
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

        tf_map = {
            "1Min": TimeFrame(1, TimeFrameUnit.Minute),
            "5Min": TimeFrame(5, TimeFrameUnit.Minute),
            "15Min": TimeFrame(15, TimeFrameUnit.Minute),
            "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
            "1Day": TimeFrame(1, TimeFrameUnit.Day),
        }
        tf = tf_map.get(timeframe, TimeFrame(1, TimeFrameUnit.Day))
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=lookback_days)

        req = StockBarsRequest(
            symbol_or_symbols=symbol.upper(),
            timeframe=tf,
            start=start,
            end=end,
        )
        resp = self._data.get_stock_bars(req)
        data: Any = getattr(resp, "data", {}) or {}
        bars = data.get(symbol.upper(), [])
        return [
            {
                "t": getattr(b, "timestamp", None).isoformat() if getattr(b, "timestamp", None) else None,
                "o": float(getattr(b, "open", 0) or 0),
                "h": float(getattr(b, "high", 0) or 0),
                "l": float(getattr(b, "low", 0) or 0),
                "c": float(getattr(b, "close", 0) or 0),
                "v": float(getattr(b, "volume", 0) or 0),
            }
            for b in bars
        ]
