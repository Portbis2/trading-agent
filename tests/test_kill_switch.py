"""HALT file must stop any trading run cold."""

from __future__ import annotations


def test_check_halt_returns_none_when_no_file(tmp_repo):
    from src.config import check_halt
    assert check_halt() is None


def test_check_halt_returns_reason_from_file(tmp_repo):
    (tmp_repo / "HALT").write_text("manual stop: broker outage\n")
    from src.config import check_halt
    reason = check_halt()
    assert reason is not None
    assert "broker outage" in reason


def test_check_halt_empty_file_still_halts(tmp_repo):
    (tmp_repo / "HALT").write_text("")
    from src.config import check_halt
    reason = check_halt()
    assert reason is not None
    assert "HALT" in reason


def test_orchestrator_exits_clean_on_halt(tmp_repo, monkeypatch, capsys):
    """run_cycle must exit 0 without invoking the task function when HALT exists."""
    (tmp_repo / "HALT").write_text("scheduled maintenance\n")

    # Write minimal strategy files so load_rules etc. don't fail if reached
    (tmp_repo / "strategy" / "rules.md").write_text("# rules\n")
    (tmp_repo / "strategy" / "universe.yaml").write_text("tickers:\n  - SPY\n")
    (tmp_repo / "strategy" / "risk_limits.yaml").write_text(
        "max_position_pct: 5\nmax_daily_loss_pct: 2\nmax_open_positions: 5\n"
        "allow_options: false\nallow_shorts: false\nallow_leverage: false\n"
    )

    from src.orchestrator import run_cycle

    called = {"ran": False}

    def task_fn(ctx):
        called["ran"] = True

    code = run_cycle("test_task", task_fn)
    out = capsys.readouterr().out

    assert code == 0
    assert called["ran"] is False
    assert "HALTED" in out
    assert "scheduled maintenance" in out
