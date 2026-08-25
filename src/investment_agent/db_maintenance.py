"""Database health checks and ingest lock (avoid concurrent writes)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from investment_agent.db import DEFAULT_DB_PATH, connect, init_db

INGEST_LOCK_PATH = DEFAULT_DB_PATH.parent / "ingest.lock"

REQUIRED_TABLES = (
    "watchlist",
    "ohlcv_daily",
    "quotes",
    "ticker_metrics",
    "app_settings",
    "screener_runs",
    "rank_snapshots",
    "close_reports",
    "trade_journal",
    "operator_day_log",
)


def ingest_lock_active() -> bool:
    return INGEST_LOCK_PATH.is_file()


def ingest_lock_message() -> str:
    if ingest_lock_stale():
        return (
            "Stale ingest lock from a prior crashed run (data/ingest.lock). "
            "End of Day clears this automatically; if you see this in Terminal, run: "
            "rm -f data/ingest.lock"
        )
    return (
        "Ingest is running in Terminal (database busy). "
        "Wait for ./scripts/run_ingest_mac.sh to finish, then try again."
    )


def ingest_lock_stale(*, max_age_hours: float = 2.0) -> bool:
    """True if lock file exists but is older than max_age_hours (likely crashed ingest)."""
    if not INGEST_LOCK_PATH.is_file():
        return False
    try:
        lines = INGEST_LOCK_PATH.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) < 2:
            return True
        ts = datetime.fromisoformat(lines[1].replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - ts.astimezone(timezone.utc)
        return age.total_seconds() > max_age_hours * 3600.0
    except (OSError, ValueError):
        return True


def clear_stale_ingest_lock(*, max_age_hours: float = 2.0) -> bool:
    """Remove ingest.lock if missing or stale. Returns True if a lock file was removed."""
    if not INGEST_LOCK_PATH.is_file():
        return False
    if not ingest_lock_stale(max_age_hours=max_age_hours):
        return False
    INGEST_LOCK_PATH.unlink(missing_ok=True)
    return True


def acquire_ingest_lock(*, detail: str = "ingest") -> None:
    INGEST_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INGEST_LOCK_PATH.exists():
        raise RuntimeError(ingest_lock_message())
    INGEST_LOCK_PATH.write_text(
        f"{detail}\n{datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )


def release_ingest_lock() -> None:
    INGEST_LOCK_PATH.unlink(missing_ok=True)


def repair_database(db_path: Path | None = None) -> dict:
    """Apply schema and verify database integrity."""
    path = init_db(db_path)
    conn = connect(path)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        missing = [t for t in REQUIRED_TABLES if t not in tables]
        if missing:
            raise RuntimeError(f"Missing tables after init: {', '.join(missing)}")

        cols = {row[1] for row in conn.execute("PRAGMA table_info(watchlist)")}
        if "source" not in cols or "added_via" not in cols:
            raise RuntimeError("watchlist schema out of date — missing source/added_via columns")

        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"integrity_check failed: {integrity}")

        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=60000")
        conn.commit()
        return {
            "ok": True,
            "db_path": str(path),
            "tables": len(tables),
            "integrity": integrity,
        }
    finally:
        conn.close()


def assert_db_available_for_writes() -> None:
    if ingest_lock_active():
        raise RuntimeError(ingest_lock_message())
