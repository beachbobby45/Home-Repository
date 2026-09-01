"""Tests for operator day log API routes."""

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

from investment_agent.dashboard.app import app
from investment_agent.db import init_db


@pytest.fixture
def client_with_api_key():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        settings = patch(
            "investment_agent.dashboard.app.Settings.from_env",
            return_value=type(
                "S",
                (),
                {"app_api_key": "secret-key"},
            )(),
        )
        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                with settings:
                    yield TestClient(app)


def test_operator_day_log_no_trade_localhost_skips_api_key(client_with_api_key) -> None:
    """Local dashboard (127.0.0.1) should log attendance without X-API-Key header."""
    client = client_with_api_key
    resp = client.post(
        "/api/operator-day-log/no-trade",
        json={"session_date_et": "2026-09-01"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["entry"]["session_date_et"] == "2026-09-01"
    assert data["entry"]["outcome"] in ("NO_TRADE_SYSTEM", "NO_TRADE_OPERATOR")


def test_operator_day_log_list_no_auth_required(client_with_api_key) -> None:
    client = client_with_api_key
    resp = client.get("/api/operator-day-log?limit=5")
    assert resp.status_code == 200
    assert "entries" in resp.json()
