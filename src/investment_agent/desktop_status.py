"""Shared helpers for Mac desktop app — last-run labels and rhythm status."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")


def pt_time_str(dt: datetime) -> str:
    hour = dt.hour % 12 or 12
    return f"{hour}:{dt.strftime('%M %p')} PT"


def format_last_run(iso: str | None) -> str:
    if not iso:
        return "Last run: not yet"
    try:
        ts = iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local = dt.astimezone(PT)
        today = datetime.now(PT).date()
        when = "today" if local.date() == today else local.strftime("%a %b %d")
        return f"Last run: {when} at {pt_time_str(local)}"
    except ValueError:
        return "Last run: —"


def now_pt_label() -> str:
    now = datetime.now(PT)
    return f"{now.strftime('%a %b %d')} · {pt_time_str(now)}"


def fetch_rhythm_status(repo: Path) -> dict | None:
    """Load daily-rhythm last-run timestamps from the local database."""
    try:
        sys.path.insert(0, str(repo / "src"))
        from investment_agent.daily_rhythm import get_daily_rhythm_status
        from investment_agent.db import connect, init_db

        conn = connect(init_db())
        try:
            return get_daily_rhythm_status(conn)
        finally:
            conn.close()
    except Exception:
        return None
