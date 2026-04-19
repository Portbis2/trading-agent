"""Paper mode is enforced. Live requires LIVE_TRADING=true AND a dated ARMED file."""

from __future__ import annotations

from datetime import date, timedelta

import pytest


def test_paper_mode_is_default(monkeypatch, tmp_repo):
    monkeypatch.delenv("LIVE_TRADING", raising=False)
    from src.config import load_config
    cfg = load_config()
    assert cfg.paper_mode is True
    assert cfg.live_trading is False


def test_live_env_without_armed_is_still_paper(monkeypatch, tmp_repo):
    monkeypatch.setenv("LIVE_TRADING", "true")
    # No ARMED file
    from src.config import load_config
    cfg = load_config()
    assert cfg.paper_mode is True
    assert cfg.live_trading is False


def test_armed_file_with_wrong_date_is_still_paper(monkeypatch, tmp_repo):
    monkeypatch.setenv("LIVE_TRADING", "true")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    (tmp_repo / "ARMED").write_text(yesterday + "\n")
    from src.config import load_config
    cfg = load_config()
    assert cfg.paper_mode is True


def test_armed_file_with_today_enables_live(monkeypatch, tmp_repo):
    monkeypatch.setenv("LIVE_TRADING", "true")
    (tmp_repo / "ARMED").write_text(date.today().isoformat() + "\n")
    # Need to also allow live-base-url so config doesn't force paper URL silently
    monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
    from src.config import load_config
    cfg = load_config()
    assert cfg.paper_mode is False
    assert cfg.live_trading is True


def test_config_forces_paper_url_when_paper_mode(monkeypatch, tmp_repo):
    monkeypatch.delenv("LIVE_TRADING", raising=False)
    monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")  # live URL
    from src.config import load_config
    cfg = load_config()
    assert cfg.paper_mode is True
    assert "paper-api" in cfg.alpaca_base_url


def test_missing_api_key_exits(monkeypatch, tmp_repo):
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    # Reload module to re-evaluate env — but _require reads os.environ live
    from src.config import load_config
    with pytest.raises(SystemExit):
        load_config()


def test_broker_rejects_live_url_in_paper_mode(monkeypatch, tmp_repo):
    """Defense in depth: if somehow a live URL reaches the Broker in paper mode, it refuses."""
    from src.broker import Broker, BrokerError
    from src.config import Config

    cfg = Config(
        alpaca_api_key="k",
        alpaca_secret_key="s",
        alpaca_base_url="https://api.alpaca.markets",  # live URL
        live_trading=False,
        paper_mode=True,                                # but paper mode on
        perplexity_api_key=None,
        clickup_api_token=None,
        clickup_list_id=None,
        debug=False,
        repo_root=tmp_repo,
    )
    with pytest.raises(BrokerError):
        Broker(cfg)
