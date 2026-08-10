"""Tests for database maintenance helpers."""

from __future__ import annotations

from investment_agent.db import connect, init_db
from investment_agent.db_maintenance import (
    acquire_ingest_lock,
    ingest_lock_active,
    release_ingest_lock,
    repair_database,
)


def test_ingest_lock(tmp_path):
    lock = tmp_path / "ingest.lock"
    import investment_agent.db_maintenance as dm

    dm.INGEST_LOCK_PATH = lock
    acquire_ingest_lock(detail="test")
    assert ingest_lock_active()
    release_ingest_lock()
    assert not ingest_lock_active()


def test_repair_database(tmp_path):
    path = init_db(tmp_path / "t.db")
    result = repair_database(path)
    assert result["ok"]
    assert result["integrity"] == "ok"
