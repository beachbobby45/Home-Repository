"""Last-completed timestamps for Ranked screener dashboard actions."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from investment_agent.account import get_setting, set_setting

ACTION_SP100 = "sp100"
ACTION_SP500 = "sp500"
ACTION_DATACENTER_US = "datacenter_us"
ACTION_DAILY_INGEST = "daily_ingest"
ACTION_FULL_INGEST = "full_ingest"
ACTION_PERIOD_SCREENER = "period_screener"
ACTION_REFRESH_RANKED = "refresh_ranked"
ACTION_REFRESH_LIVE = "refresh_live"

PRESET_ACTIONS: dict[str, str] = {
    "sp100": ACTION_SP100,
    "sp500": ACTION_SP500,
    "datacenter_us": ACTION_DATACENTER_US,
}

SCREEN_ACTIONS: dict[str, str] = {
    ACTION_SP100: "SP100 load",
    ACTION_SP500: "S&P 500 load",
    ACTION_DATACENTER_US: "DC US watch load",
    ACTION_DAILY_INGEST: "Daily ingest",
    ACTION_FULL_INGEST: "Full ingest",
    ACTION_PERIOD_SCREENER: "Run screener",
    ACTION_REFRESH_RANKED: "Refresh ranked",
    ACTION_REFRESH_LIVE: "Refresh live (Step 3)",
}

_SETTING_PREFIX = "screen_action_"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _setting_key(action_id: str) -> str:
    return f"{_SETTING_PREFIX}{action_id}"


def record_screen_action(
    conn: sqlite3.Connection,
    action_id: str,
    *,
    detail: str = "",
) -> None:
    if action_id not in SCREEN_ACTIONS:
        raise ValueError(f"Unknown screen action: {action_id}")
    payload = json.dumps(
        {
            "completed_at": _utc_now_iso(),
            "detail": detail,
        }
    )
    set_setting(conn, _setting_key(action_id), payload)


def _parse_action_payload(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("completed_at"):
            return data
    except json.JSONDecodeError:
        pass
    if raw:
        return {"completed_at": raw, "detail": ""}
    return None


def _fallback_period_screener(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        """
        SELECT finished_at FROM screener_runs
        WHERE status = 'completed'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    if not row or not row["finished_at"]:
        return None
    return {"completed_at": row["finished_at"], "detail": "From saved screener run"}


def _fallback_ingest(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        "SELECT MAX(computed_at) AS last_at FROM ticker_metrics"
    ).fetchone()
    if not row or not row["last_at"]:
        return None
    return {"completed_at": row["last_at"], "detail": "From latest ticker metrics"}


def get_screen_action_status(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return last completion time per Ranked screener action."""
    out: dict[str, dict] = {}
    for action_id, label in SCREEN_ACTIONS.items():
        raw = get_setting(conn, _setting_key(action_id), "")
        payload = _parse_action_payload(raw)
        source = "recorded"
        if payload is None:
            if action_id == ACTION_PERIOD_SCREENER:
                payload = _fallback_period_screener(conn)
            elif action_id in (ACTION_DAILY_INGEST, ACTION_FULL_INGEST):
                payload = _fallback_ingest(conn)
            source = "inferred" if payload else "none"
        out[action_id] = {
            "id": action_id,
            "label": label,
            "completed_at": payload.get("completed_at") if payload else None,
            "detail": payload.get("detail", "") if payload else "",
            "source": source,
        }
    return out
