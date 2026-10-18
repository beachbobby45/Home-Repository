"""API: broker mirror + execution PDT / armed-plan endpoints."""

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
from investment_agent.execution.armed_plan import (
    AllocationMode,
    ArmedLeg,
    ArmedPlan,
    PlanStatus,
    save_armed_plan,
)
from investment_agent.execution.pdt_guard import can_open_day_trade


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


def test_broker_sync_fixture_and_status(client) -> None:
    http, _ = client
    sync = http.post(
        "/api/broker/sync/fixture",
        json={"equity": 5000, "cash": 5000, "account_id": "rh-test"},
    )
    assert sync.status_code == 200, sync.text
    assert sync.json()["equity"] == 5000

    status = http.get("/api/broker/status")
    assert status.status_code == 200
    body = status.json()
    assert body["pdt"]["cap"] == 3
    assert body["pdt"]["equity"] == 5000
    assert body["latest_balance"]["equity"] == 5000


def test_pdt_cap_five_when_equity_25k(client) -> None:
    http, _ = client
    http.post(
        "/api/broker/sync/fixture",
        json={"equity": 25000, "cash": 25000},
    )
    pdt = http.get("/api/execution/pdt")
    assert pdt.status_code == 200
    assert pdt.json()["cap"] == 5


def test_arm_plan_requires_propose_and_pdt(client) -> None:
    http, db_path = client
    http.post("/api/broker/sync/fixture", json={"equity": 5000, "cash": 5000})

    missing = http.post("/api/execution/armed-plan/arm")
    assert missing.status_code == 404

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        from investment_agent.trading_day import today_et_str

        day = today_et_str()
        gate = can_open_day_trade(conn, equity=5000, session_date=day)
        plan = ArmedPlan(
            session_date_et=day,
            allocation_mode=AllocationMode.SINGLE_TOP1,
            status=PlanStatus.PROPOSED,
            legs=[
                ArmedLeg(
                    rank=1,
                    ticker="TEST",
                    limit_buy=10.0,
                    limit_sell=10.2,
                    stop=9.95,
                    shares=100,
                    deploy=5000,
                )
            ],
            equity_snapshot=5000,
            pdt_cap=gate["cap"],
            pdt_used=gate["used"],
        )
        save_armed_plan(conn, plan)
        conn.commit()
    finally:
        conn.close()

    armed = http.post("/api/execution/armed-plan/arm")
    assert armed.status_code == 200, armed.text
    assert armed.json()["plan"]["status"] == "armed"
