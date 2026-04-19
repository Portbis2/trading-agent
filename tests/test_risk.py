"""Verify that every hard limit in risk_limits.yaml actually blocks bad orders."""

from __future__ import annotations

from src.risk import AccountSnapshot, ProposedOrder, check_order


def _mk(symbol="AAPL", qty=1, price=100.0, **kw) -> ProposedOrder:
    return ProposedOrder(symbol=symbol, side="buy", qty=qty, est_price=price, **kw)


# --- Universe ---

def test_blocks_symbol_outside_universe(flat_account, default_limits, default_universe):
    ok, reason = check_order(_mk(symbol="TSLA"), flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "universe" in reason.lower()


def test_allows_symbol_in_universe(flat_account, default_limits, default_universe):
    ok, _ = check_order(_mk(symbol="AAPL"), flat_account, {}, default_limits, default_universe)
    assert ok is True


# --- max_position_pct ---

def test_blocks_position_over_max_pct(flat_account, default_limits, default_universe):
    # 100 shares * $100 = $10,000 on $100k equity = 10% > 5% cap
    order = _mk(symbol="AAPL", qty=100, price=100.0)
    ok, reason = check_order(order, flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "max_position_pct" in reason


def test_allows_position_under_max_pct(flat_account, default_limits, default_universe):
    # $4,000 = 4% of $100k
    order = _mk(symbol="AAPL", qty=40, price=100.0)
    ok, _ = check_order(order, flat_account, {}, default_limits, default_universe)
    assert ok is True


# --- max_daily_loss_pct ---

def test_blocks_new_open_after_daily_loss_hit(default_limits, default_universe):
    acct = AccountSnapshot(
        equity=97_900.0,
        cash=0.0,
        day_pnl=-2_100.0,
        day_start_equity=100_000.0,
    )
    ok, reason = check_order(_mk(), acct, {}, default_limits, default_universe)
    assert ok is False
    assert "daily loss" in reason.lower()


def test_allows_close_after_daily_loss_hit(default_limits, default_universe):
    acct = AccountSnapshot(
        equity=97_900.0,
        cash=0.0,
        day_pnl=-2_100.0,
        day_start_equity=100_000.0,
    )
    # Closing is permitted even past the daily loss cap
    ok, _ = check_order(_mk(is_opening=False), acct, {}, default_limits, default_universe)
    assert ok is True


# --- max_open_positions ---

def test_blocks_new_symbol_when_at_max_positions(flat_account, default_limits, default_universe):
    positions = {s: {"qty": 1, "avg_entry": 1} for s in default_universe}  # 5 open
    ok, reason = check_order(
        _mk(symbol="AAPL"),
        flat_account,
        {"QQQ": {"qty": 1, "avg_entry": 1}, "SPY": {"qty": 1}, "NVDA": {"qty": 1}, "MSFT": {"qty": 1}, "GOOGL": {"qty": 1}},
        default_limits,
        default_universe + ["GOOGL"],
    )
    assert ok is False
    assert "max_open_positions" in reason


def test_allows_adding_to_existing_position_at_max(flat_account, default_limits, default_universe):
    positions = {s: {"qty": 1, "avg_entry": 1} for s in ["QQQ", "SPY", "NVDA", "MSFT", "AAPL"]}
    # Adding to AAPL which is already open: is_opening=False should pass
    ok, _ = check_order(
        _mk(symbol="AAPL", is_opening=False),
        flat_account,
        positions,
        default_limits,
        default_universe,
    )
    assert ok is True


# --- instrument gates ---

def test_blocks_options(flat_account, default_limits, default_universe):
    ok, reason = check_order(_mk(is_option=True), flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "options" in reason.lower()


def test_blocks_shorts(flat_account, default_limits, default_universe):
    ok, reason = check_order(_mk(is_short=True), flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "shorts" in reason.lower()


def test_blocks_leverage(flat_account, default_limits, default_universe):
    ok, reason = check_order(_mk(is_leveraged=True), flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "leverage" in reason.lower()


# --- sanity ---

def test_blocks_zero_qty(flat_account, default_limits, default_universe):
    ok, reason = check_order(_mk(qty=0), flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "qty" in reason.lower()


def test_blocks_bad_price(flat_account, default_limits, default_universe):
    ok, reason = check_order(_mk(price=0), flat_account, {}, default_limits, default_universe)
    assert ok is False
    assert "price" in reason.lower()
