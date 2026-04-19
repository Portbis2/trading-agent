"""Loads env, validates, fails loud. Computes paper vs. live mode."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


REPO_ROOT = Path(__file__).resolve().parent.parent
ARMED_FILE = REPO_ROOT / "ARMED"
HALT_FILE = REPO_ROOT / "HALT"

REQUIRED_ENV_VARS = (
    "ALPACA_API_KEY",
    "ALPACA_SECRET_KEY",
)


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_base_url: str
    live_trading: bool
    paper_mode: bool
    perplexity_api_key: str | None
    clickup_api_token: str | None
    clickup_list_id: str | None
    debug: bool
    repo_root: Path


def _require(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise ConfigError(
            f"FATAL: required env var {name} is missing or empty. "
            f"Copy .env.example to .env and fill it in."
        )
    return val


def _armed_file_valid() -> bool:
    """ARMED must exist AND contain today's ISO date on its first non-empty line."""
    if not ARMED_FILE.exists():
        return False
    try:
        content = ARMED_FILE.read_text().strip()
    except OSError:
        return False
    today = date.today().isoformat()
    for line in content.splitlines():
        line = line.strip()
        if line and line == today:
            return True
    return False


def load_config() -> Config:
    """Load and validate config. Exits the process loudly on any fatal issue."""
    try:
        alpaca_key = _require("ALPACA_API_KEY")
        alpaca_secret = _require("ALPACA_SECRET_KEY")
    except ConfigError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    live_env = os.environ.get("LIVE_TRADING", "false").strip().lower() == "true"
    armed_ok = _armed_file_valid()
    live_trading = live_env and armed_ok
    paper_mode = not live_trading

    base_url = os.environ.get(
        "ALPACA_BASE_URL",
        "https://paper-api.alpaca.markets",
    ).strip()

    if paper_mode and "paper-api" not in base_url:
        base_url = "https://paper-api.alpaca.markets"

    if live_env and not armed_ok:
        print(
            "WARNING: LIVE_TRADING=true but ARMED file missing or stale. "
            "Forcing paper mode.",
            file=sys.stderr,
        )

    return Config(
        alpaca_api_key=alpaca_key,
        alpaca_secret_key=alpaca_secret,
        alpaca_base_url=base_url,
        live_trading=live_trading,
        paper_mode=paper_mode,
        perplexity_api_key=os.environ.get("PERPLEXITY_API_KEY") or None,
        clickup_api_token=os.environ.get("CLICKUP_API_TOKEN") or None,
        clickup_list_id=os.environ.get("CLICKUP_LIST_ID") or None,
        debug=os.environ.get("DEBUG", "false").strip().lower() == "true",
        repo_root=REPO_ROOT,
    )


def check_halt() -> str | None:
    """If HALT file exists, return its contents as the halt reason. Else None."""
    if not HALT_FILE.exists():
        return None
    try:
        reason = HALT_FILE.read_text().strip()
    except OSError as e:
        return f"HALT file present but unreadable: {e}"
    return reason or "HALT file present (no reason given)"
