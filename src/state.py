"""Read/write memory/* files. Git is the durable store."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.config import REPO_ROOT

MEMORY_DIR = REPO_ROOT / "memory"
JOURNAL_DIR = MEMORY_DIR / "journal"
POSITIONS_FILE = MEMORY_DIR / "positions.json"
ACCOUNT_FILE = MEMORY_DIR / "account.json"
WATCHLIST_FILE = MEMORY_DIR / "watchlist.json"
STOPS_FILE = MEMORY_DIR / "stops.json"

STRATEGY_DIR = REPO_ROOT / "strategy"
RISK_LIMITS_FILE = STRATEGY_DIR / "risk_limits.yaml"
UNIVERSE_FILE = STRATEGY_DIR / "universe.yaml"
RULES_FILE = STRATEGY_DIR / "rules.md"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    text = path.read_text().strip()
    if not text:
        return default
    return json.loads(text)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n")


def read_positions() -> dict:
    return _read_json(POSITIONS_FILE, {})


def write_positions(positions: dict) -> None:
    _write_json(POSITIONS_FILE, positions)


def read_account() -> dict:
    return _read_json(ACCOUNT_FILE, {})


def write_account(account: dict) -> None:
    _write_json(ACCOUNT_FILE, account)


def read_watchlist() -> list:
    """Return the last pre-market screen results."""
    return _read_json(WATCHLIST_FILE, [])


def write_watchlist(watchlist: list) -> None:
    _write_json(WATCHLIST_FILE, watchlist)


def read_stops() -> dict:
    """Return stop/target metadata keyed by symbol: {stop, target, entry_date}."""
    return _read_json(STOPS_FILE, {})


def write_stops(stops: dict) -> None:
    _write_json(STOPS_FILE, stops)


def load_risk_limits() -> dict:
    return yaml.safe_load(RISK_LIMITS_FILE.read_text()) or {}


def load_universe() -> list[str]:
    data = yaml.safe_load(UNIVERSE_FILE.read_text()) or {}
    tickers = data.get("tickers") or []
    return [str(t).upper().strip() for t in tickers if t]


def load_rules() -> str:
    return RULES_FILE.read_text()


def append_journal(entry: dict) -> Path:
    """Append a journal entry to memory/journal/YYYY-MM-DD.md.

    Required keys: symbol, side, qty, entry, stop, target, reason, rule_citation.
    Timestamp is added automatically if not supplied.
    """
    ts = entry.get("timestamp") or datetime.now(timezone.utc).isoformat()
    day = ts[:10]
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    path = JOURNAL_DIR / f"{day}.md"

    lines = [
        "",
        f"## {ts} — {entry.get('symbol', '?')} {entry.get('side', '?')}",
        f"- qty: {entry.get('qty', '?')}",
        f"- entry: {entry.get('entry', '?')}",
        f"- stop: {entry.get('stop', '?')}",
        f"- target: {entry.get('target', '?')}",
        f"- reason: {entry.get('reason', '?')}",
        f"- rule: {entry.get('rule_citation', '?')}",
    ]
    if extra := entry.get("extra"):
        lines.append(f"- extra: {extra}")

    header_needed = not path.exists()
    with path.open("a") as f:
        if header_needed:
            f.write(f"# Journal — {day}\n")
        f.write("\n".join(lines) + "\n")
    return path
