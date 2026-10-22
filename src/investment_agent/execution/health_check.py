"""Morning / session health checks for paper automation."""

from __future__ import annotations

import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.execution.paper_ledger import (
    ACCOUNT_GATE,
    ensure_paper_accounts,
    get_paper_balance,
    get_session_log,
)
from investment_agent.notify import send_email
from investment_agent.trading_day import today_et_str

PT = ZoneInfo("America/Los_Angeles")
ET = ZoneInfo("America/New_York")

PAPER_LABEL = "com.investment-agent.paper-worker"
DASH_LABEL = "com.investment-agent.dashboard"
MORNING_LABEL = "com.investment-agent.intraday.morning"


def _launchctl_loaded(label: str) -> bool:
    try:
        uid = subprocess.check_output(["id", "-u"], text=True).strip()
        r = subprocess.run(
            ["launchctl", "print", f"gui/{uid}/{label}"],
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    except OSError:
        return False


def _tail_log(path: Path, n: int = 8) -> str:
    if not path.is_file():
        return f"(missing {path})"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:]) if lines else "(empty)"
    except OSError as exc:
        return f"(read error: {exc})"


def run_health_check(
    conn: sqlite3.Connection,
    *,
    send_notify: bool = True,
) -> dict[str, Any]:
    ensure_paper_accounts(conn)
    day = today_et_str()
    now_pt = datetime.now(PT)
    bal = get_paper_balance(conn, ACCOUNT_GATE)
    today = get_session_log(conn, day, ACCOUNT_GATE)

    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    # launchctl only exists on macOS; elsewhere mark as skipped-ok (CI / Linux)
    import os
    import platform

    is_darwin = platform.system() == "Darwin"
    if is_darwin:
        paper_ok = _launchctl_loaded(PAPER_LABEL)
        add("paper_worker", paper_ok, "loaded" if paper_ok else "NOT loaded — reinstall paper worker")

        dash_ok = _launchctl_loaded(DASH_LABEL)
        add("dashboard", dash_ok, "loaded" if dash_ok else "NOT loaded")

        morning_ok = _launchctl_loaded(MORNING_LABEL)
        add("morning_prep_agent", morning_ok, "plist loaded" if morning_ok else "NOT loaded")

        log_dir = Path.home() / "Library" / "Logs" / "investment-agent"
        paper_err = log_dir / "paper-worker.err.log"
        err_tail = _tail_log(paper_err, 20)
        traceback_recent = "Traceback" in err_tail
        add(
            "paper_worker_logs",
            not traceback_recent,
            "clean" if not traceback_recent else "Traceback in paper-worker.err.log",
        )
    else:
        add("paper_worker", True, "skipped (not macOS)")
        add("dashboard", True, "skipped (not macOS)")
        add("morning_prep_agent", True, "skipped (not macOS)")
        add("paper_worker_logs", True, "skipped (not macOS)")

    add(
        "paper_equity",
        float(bal["equity"]) > 0,
        f"equity=${float(bal['equity']):.2f} settled=${float(bal['settled_cash']):.2f}",
    )

    # On weekdays after 4:30 PT, expect morning prep log activity or rank data
    weekday = now_pt.weekday() < 5
    if weekday and now_pt.hour >= 5:
        rank_n = conn.execute(
            "SELECT COUNT(*) AS n FROM rank_snapshots WHERE snapshot_date = ?",
            (day,),
        ).fetchone()["n"]
        add(
            "rank_snapshot_today",
            rank_n > 0,
            f"rank_snapshots today={rank_n}" if rank_n else "No rank snapshot for today yet",
        )
    else:
        add("rank_snapshot_today", True, "skipped (weekend or before 5:00 PT)")

    failed = [c for c in checks if not c["ok"]]
    overall = len(failed) == 0
    subject = (
        f"[Investment Agent] Health OK — {day}"
        if overall
        else f"[Investment Agent] Health ALERT — {day} ({len(failed)} issue(s))"
    )
    lines = [
        f"Session (ET): {day}",
        f"Checked (PT): {now_pt.strftime('%Y-%m-%d %H:%M %Z')}",
        f"Overall: {'OK' if overall else 'NEEDS ATTENTION'}",
        f"Paper equity: ${float(bal['equity']):.2f}",
        f"Today gate status: {(today or {}).get('status') or 'none'}",
        "",
        "Checks:",
    ]
    for c in checks:
        mark = "OK" if c["ok"] else "FAIL"
        lines.append(f"  [{mark}] {c['name']}: {c['detail']}")
    lines.extend(
        [
            "",
            "Logs: ~/Library/Logs/investment-agent/",
            "Dashboard: http://127.0.0.1:8080",
            "Paper status: http://127.0.0.1:8080/api/paper/status",
        ]
    )
    body = "\n".join(lines)

    # Always notify on failure; on success only if NOTIFY_ON_SUCCESS=1
    notify_success = os.getenv("NOTIFY_ON_SUCCESS", "0").strip() in {"1", "true", "yes"}
    notify_result = None
    if send_notify and ((not overall) or notify_success):
        notify_result = send_email(subject, body)

    return {
        "ok": overall,
        "session_date_et": day,
        "checks": checks,
        "failed": [c["name"] for c in failed],
        "subject": subject,
        "body": body,
        "notify": notify_result,
        "balances": dict(bal),
    }
