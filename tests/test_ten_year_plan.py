"""Tests for 10-year growth plan table API."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app
from investment_agent.finance import GOAL_ACCOUNT_VALUE, ORIGINAL_BASIS
from investment_agent.growth_projection import build_ten_year_growth_plan


def test_build_ten_year_has_ten_rows():
    data = build_ten_year_growth_plan()
    assert len(data["years"]) == 10
    assert data["years"][0]["year"] == 1
    assert data["years"][9]["year"] == 10


def test_injection_advantage_year_one():
    data = build_ten_year_growth_plan()
    y1 = data["years"][0]
    assert y1["injection"]["capital_injection"] == 10_000.0
    assert y1["advantage_end_balance"] > 0
    assert y1["injection"]["end_balance"] > y1["base"]["end_balance"]


def test_months_to_goal_injection_faster_than_base():
    data = build_ten_year_growth_plan()
    base_m = data["months_to_goal"]["base"]
    inj_m = data["months_to_goal"]["injection"]
    assert base_m is not None and inj_m is not None
    assert inj_m <= base_m


def test_api_growth_plan_ten_year():
    client = TestClient(app)
    resp = client.get("/api/growth-plan/ten-year")
    assert resp.status_code == 200
    data = resp.json()
    assert data["starting_basis"] == ORIGINAL_BASIS
    assert data["goal"] == GOAL_ACCOUNT_VALUE
    assert len(data["years"]) == 10
