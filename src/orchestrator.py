"""Wake-up cycle wrapper. Every task runs inside run_cycle()."""

from __future__ import annotations

import subprocess
import sys
import traceback
from pathlib import Path
from typing import Callable

from src.broker import Broker
from src.config import Config, check_halt, load_config
from src.notify import notify
from src.state import (
    load_risk_limits,
    load_rules,
    load_universe,
    read_account,
    read_positions,
    write_account,
    write_positions,
)


TaskFn = Callable[[dict], None]


def _git(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)


def commit_and_push(config: Config, task_name: str, summary: str) -> None:
    root = config.repo_root
    code, out = _git(["add", "-A"], root)
    if code != 0:
        print(f"[GIT] add failed: {out}")
        return

    code, out = _git(["diff", "--cached", "--quiet"], root)
    if code == 0:
        print("[GIT] no changes to commit")
        return

    msg = f"{task_name}: {summary}"
    code, out = _git(["commit", "-m", msg], root)
    if code != 0:
        print(f"[GIT] commit failed: {out}")
        return
    print(f"[GIT] committed: {msg}")

    code, out = _git(["push"], root)
    if code != 0:
        print(f"[GIT] push failed (non-fatal): {out}")
    else:
        print("[GIT] pushed")


def run_cycle(task_name: str, task_fn: TaskFn) -> int:
    """Execute the mandatory 10-step wake-up cycle around a task function.

    Returns exit code (0 on success, non-zero on fatal error).
    """
    # Step 1 — config
    config = load_config()
    print(f"[WAKE] {task_name} | paper={config.paper_mode}")

    # Step 2 — HALT check
    halt_reason = check_halt()
    if halt_reason:
        msg = f"HALTED: {halt_reason}"
        print(msg)
        notify(config, f"HALT: {task_name}", halt_reason, level="urgent")
        return 0

    # Step 3 — strategy
    try:
        rules = load_rules()
        universe = load_universe()
        limits = load_risk_limits()
    except Exception as e:
        notify(config, f"{task_name}: strategy load failed", str(e), level="urgent")
        print(f"[FATAL] strategy load: {e}")
        return 3

    # Step 4 — memory
    positions_snapshot = read_positions()
    account_snapshot = read_account()

    # Step 5 — broker reconcile
    broker: Broker | None = None
    try:
        broker = Broker(config)
        live_account = broker.get_account()
        live_positions = broker.get_positions()

        drift = set(live_positions) ^ set(positions_snapshot)
        if drift:
            print(f"[RECONCILE] position symbol drift: {sorted(drift)}")

        account_snapshot = live_account
        positions_snapshot = live_positions
    except Exception as e:
        print(f"[RECONCILE] broker reconcile failed: {e}")
        notify(
            config,
            f"{task_name}: broker reconcile failed",
            traceback.format_exc(),
            level="high",
        )

    # Step 6 — task
    ctx = {
        "config": config,
        "broker": broker,
        "rules": rules,
        "universe": universe,
        "limits": limits,
        "positions": positions_snapshot,
        "account": account_snapshot,
        "summary": "",
    }
    try:
        task_fn(ctx)
    except Exception as e:
        print(f"[TASK] {task_name} raised: {e}")
        notify(config, f"{task_name}: task error", traceback.format_exc(), level="urgent")
        return 4

    # Steps 7+8 — risk gate and journal happen inside task_fn via src.risk / src.state

    # Step 9 — persist memory
    try:
        write_positions(ctx.get("positions", positions_snapshot))
        write_account(ctx.get("account", account_snapshot))
    except Exception as e:
        print(f"[PERSIST] memory write failed: {e}")
        notify(config, f"{task_name}: memory write failed", str(e), level="urgent")

    # Step 10 — commit and push
    summary = ctx.get("summary") or "no changes"
    commit_and_push(config, task_name, summary)

    print(f"[DONE] {task_name}")
    return 0


def main() -> int:
    """Dispatch entry — python -m src.orchestrator <task_name>."""
    if len(sys.argv) < 2:
        print("usage: python -m src.orchestrator <task_name>", file=sys.stderr)
        return 64

    task_name = sys.argv[1]
    import importlib
    try:
        mod = importlib.import_module(f"tasks.{task_name}")
    except ImportError as e:
        print(f"unknown task: {task_name} ({e})", file=sys.stderr)
        return 64

    fn = getattr(mod, "run", None)
    if fn is None:
        print(f"task {task_name} has no run(ctx) function", file=sys.stderr)
        return 64

    return run_cycle(task_name, fn)


if __name__ == "__main__":
    sys.exit(main())
