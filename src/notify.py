"""Notifications: ClickUp primary, stdout fallback."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import Config


def notify(config: Config, title: str, body: str = "", level: str = "info") -> bool:
    """Send a notification. Returns True if delivered to ClickUp, False if stdout-only.

    Never raises — a notify failure must never kill a trading run.
    """
    prefix = f"[{level.upper()}] {datetime.now(timezone.utc).isoformat()}"
    print(f"{prefix} | {title}")
    if body:
        print(body)

    if not (config.clickup_api_token and config.clickup_list_id):
        return False

    try:
        import requests

        r = requests.post(
            f"https://api.clickup.com/api/v2/list/{config.clickup_list_id}/task",
            headers={
                "Authorization": config.clickup_api_token,
                "Content-Type": "application/json",
            },
            json={
                "name": title,
                "description": body or title,
                "priority": {"urgent": 1, "high": 2, "info": 3, "low": 4}.get(level, 3),
            },
            timeout=10,
        )
        if r.status_code >= 300:
            print(f"[NOTIFY] ClickUp responded {r.status_code}: {r.text[:200]}")
            return False
        return True
    except Exception as e:
        print(f"[NOTIFY] ClickUp call failed: {e}")
        return False
