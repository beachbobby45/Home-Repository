"""Lightweight ops notifications: log file + optional SMTP email + macOS banner."""

from __future__ import annotations

import os
import smtplib
import subprocess
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

from investment_agent.config import load_env

ET = ZoneInfo("America/New_York")
PT = ZoneInfo("America/Los_Angeles")

DEFAULT_NOTIFY_EMAIL = "Beachbobby45@att.net"


def _log_dir() -> Path:
    home = Path.home()
    d = home / "Library" / "Logs" / "investment-agent"
    try:
        d.mkdir(parents=True, exist_ok=True)
        return d
    except OSError:
        fallback = Path("/tmp/investment-agent-logs")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def notify_config() -> dict:
    load_env()
    return {
        "to": os.getenv("NOTIFY_EMAIL", DEFAULT_NOTIFY_EMAIL).strip(),
        "from_addr": os.getenv("NOTIFY_FROM", os.getenv("SMTP_USER", "")).strip()
        or os.getenv("NOTIFY_EMAIL", DEFAULT_NOTIFY_EMAIL).strip(),
        "smtp_host": os.getenv("SMTP_HOST", "").strip(),
        "smtp_port": int(os.getenv("SMTP_PORT", "587") or "587"),
        "smtp_user": os.getenv("SMTP_USER", "").strip(),
        "smtp_password": os.getenv("SMTP_PASSWORD", "").strip(),
        "smtp_use_tls": os.getenv("SMTP_USE_TLS", "1").strip() not in {"0", "false", "no"},
        "enabled": os.getenv("NOTIFY_ENABLED", "1").strip() not in {"0", "false", "no"},
    }


def append_notify_log(subject: str, body: str) -> Path:
    path = _log_dir() / "health-notify.log"
    stamp = datetime.now(PT).strftime("%Y-%m-%d %H:%M:%S %Z")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n===== {stamp} =====\n{subject}\n{body}\n")
    return path


def _macos_banner(subject: str, body: str) -> bool:
    if os.uname().sysname != "Darwin":
        return False
    # Keep body short for notification
    text = body.replace("\\", "\\\\").replace('"', '\\"')[:400]
    title = subject.replace('"', '\\"')[:80]
    script = f'display notification "{text}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
        return True
    except OSError:
        return False


def send_email(subject: str, body: str, *, to: str | None = None) -> dict:
    """Send email if SMTP is configured. Always logs locally."""
    cfg = notify_config()
    log_path = append_notify_log(subject, body)
    result = {
        "ok": False,
        "logged": str(log_path),
        "emailed": False,
        "banner": False,
        "to": to or cfg["to"],
        "detail": "",
    }
    if not cfg["enabled"]:
        result["detail"] = "NOTIFY_ENABLED=0"
        return result

    result["banner"] = _macos_banner(subject, body)

    if not cfg["smtp_host"] or not cfg["smtp_user"] or not cfg["smtp_password"]:
        result["detail"] = (
            "SMTP not configured — wrote log only. "
            "Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env to email "
            f"{result['to']}"
        )
        result["ok"] = True  # log-only success
        return result

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["from_addr"]
    msg["To"] = result["to"]
    msg.set_content(body)

    try:
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=30) as smtp:
            if cfg["smtp_use_tls"]:
                smtp.starttls()
            smtp.login(cfg["smtp_user"], cfg["smtp_password"])
            smtp.send_message(msg)
        result["emailed"] = True
        result["ok"] = True
        result["detail"] = "email sent"
    except Exception as exc:  # noqa: BLE001
        result["detail"] = f"SMTP failed: {exc}"
        result["ok"] = False
    return result
