"""Shared fixtures. Sets dummy env so src.config never bails out in tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("ALPACA_API_KEY", "test-key")
os.environ.setdefault("ALPACA_SECRET_KEY", "test-secret")
os.environ.setdefault("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
os.environ.setdefault("LIVE_TRADING", "false")


@pytest.fixture
def default_limits() -> dict:
    return {
        "max_position_pct": 5,
        "max_daily_loss_pct": 2,
        "max_open_positions": 5,
        "allow_options": False,
        "allow_shorts": False,
        "allow_leverage": False,
    }


@pytest.fixture
def default_universe() -> list[str]:
    return ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]


@pytest.fixture
def flat_account():
    from src.risk import AccountSnapshot
    return AccountSnapshot(
        equity=100_000.0,
        cash=100_000.0,
        day_pnl=0.0,
        day_start_equity=100_000.0,
    )


@pytest.fixture
def tmp_repo(tmp_path, monkeypatch):
    """Redirect config REPO_ROOT and related paths to a temp dir."""
    (tmp_path / "memory" / "journal").mkdir(parents=True)
    (tmp_path / "strategy").mkdir(parents=True)

    import src.config as config_mod
    import src.state as state_mod

    monkeypatch.setattr(config_mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(config_mod, "ARMED_FILE", tmp_path / "ARMED")
    monkeypatch.setattr(config_mod, "HALT_FILE", tmp_path / "HALT")

    monkeypatch.setattr(state_mod, "MEMORY_DIR", tmp_path / "memory")
    monkeypatch.setattr(state_mod, "JOURNAL_DIR", tmp_path / "memory" / "journal")
    monkeypatch.setattr(state_mod, "POSITIONS_FILE", tmp_path / "memory" / "positions.json")
    monkeypatch.setattr(state_mod, "ACCOUNT_FILE", tmp_path / "memory" / "account.json")
    monkeypatch.setattr(state_mod, "STRATEGY_DIR", tmp_path / "strategy")
    monkeypatch.setattr(state_mod, "RISK_LIMITS_FILE", tmp_path / "strategy" / "risk_limits.yaml")
    monkeypatch.setattr(state_mod, "UNIVERSE_FILE", tmp_path / "strategy" / "universe.yaml")
    monkeypatch.setattr(state_mod, "RULES_FILE", tmp_path / "strategy" / "rules.md")

    return tmp_path
