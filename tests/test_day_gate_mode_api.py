"""API tests for day gate mode (Preserve vs Produce)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.account import get_day_gate_mode
from investment_agent.dashboard.app import app
from investment_agent.db import init_db


@pytest.fixture
def client():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                yield TestClient(app), db_path


def test_day_gate_mode_get_and_put(client) -> None:
    http, db_path = client
    r = http.get("/api/settings/day-gate-mode")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "produce"  # v1 paper default
    assert body["trade_min"] == 60
    assert body["produce_trade_min"] == 50
    assert body["bull_gate_required"] is False

    put = http.put("/api/settings/day-gate-mode", json={"mode": "preserve"})
    assert put.status_code == 200, put.text
    assert put.json()["mode"] == "preserve"
    assert put.json()["bull_gate_required"] is True

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        assert get_day_gate_mode(conn) == "preserve"
    finally:
        conn.close()

    summary = http.get("/api/summary")
    assert summary.status_code == 200
    assert summary.json()["day_gate_mode"] == "preserve"

    put_back = http.put("/api/settings/day-gate-mode", json={"mode": "produce"})
    assert put_back.status_code == 200
    assert put_back.json()["produce_trade_min"] == 50


def test_day_gate_mode_rejects_invalid(client) -> None:
    http, _ = client
    bad = http.put("/api/settings/day-gate-mode", json={"mode": "yolo"})
    assert bad.status_code == 400
