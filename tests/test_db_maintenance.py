"""Tests for database maintenance helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from investment_agent.db import connect, init_db
from investment_agent.db_maintenance import (
    acquire_ingest_lock,
    clear_stale_ingest_lock,
    ingest_lock_active,
    ingest_lock_stale,
    release_ingest_lock,
    repair_database,
)


def test_ingest_lock(tmp_path):
    lock = tmp_path / "ingest.lock"
    import investment_agent.db_maintenance as dm

    dm.INGEST_LOCK_PATH = lock
    acquire_ingest_lock(detail="test")
    assert ingest_lock_active()
    assert not ingest_lock_stale(max_age_hours=2.0)
    release_ingest_lock()
    assert not ingest_lock_active()


def test_clear_stale_ingest_lock(tmp_path):
    lock = tmp_path / "ingest.lock"
    import investment_agent.db_maintenance as dm

    dm.INGEST_LOCK_PATH = lock
    old = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    lock.write_text(f"run_ingest\n{old}\n", encoding="utf-8")
    assert ingest_lock_stale(max_age_hours=2.0)
    assert clear_stale_ingest_lock(max_age_hours=2.0)
    assert not ingest_lock_active()


def test_repair_database(tmp_path):
    path = init_db(tmp_path / "t.db")
    result = repair_database(path)
    assert result["ok"]
    assert result["integrity"] == "ok"
