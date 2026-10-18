"""Tests for 10-year growth plan table API."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app
from investment_agent.finance import GOAL_ACCOUNT_VALUE
from investment_agent.growth_projection import (
    PLAN_FUNDED_TARGET,
    PLAN_STARTING_BASIS,
    build_ten_year_growth_plan,
)


def test_build_ten_year_has_ten_rows():
    data = build_ten_year_growth_plan()
    assert len(data["years"]) == 10
    assert data["years"][0]["year"] == 1
    assert data["years"][9]["year"] == 10


def test_funding_ladder_advantage_year_one():
    data = build_ten_year_growth_plan()
    y1 = data["years"][0]
    # Three staged +$5K deposits in year 1 → $15K capital in
    assert y1["injection"]["capital_injection"] == 15_000.0
    assert y1["advantage_end_balance"] > 0
    assert y1["injection"]["end_balance"] > y1["base"]["end_balance"]


def test_months_to_goal_funded_faster_than_base():
    data = build_ten_year_growth_plan()
    base_m = data["months_to_goal"]["base"]
    inj_m = data["months_to_goal"]["injection"]
    assert base_m is not None and inj_m is not None
    assert inj_m <= base_m


def test_plan_starts_at_five_k():
    data = build_ten_year_growth_plan()
    assert data["starting_basis"] == PLAN_STARTING_BASIS == 5_000.0
    assert data["funded_target"] == PLAN_FUNDED_TARGET
    assert data["assumptions"]["sessions_per_week_cap"] == 5
    assert len(data["assumptions"]["injection_schedule"]) == 3
    assert data["assumptions"]["rh_live_date"] == "2026-12-01"
    cash = data["assumptions"]["cash_schedule"]
    assert cash[0]["date"] == "2026-12-01" and cash[0]["amount"] == 5_000.0
    assert cash[-1]["date"] == "2027-04-09" and cash[-1]["invested_after"] == 20_000.0
    assert data["summary"].startswith("$5,000 start")
    assert "$15,000 start" not in data["summary"]
    assert "+$10K" not in (data["assumptions"].get("capital_injection") or "")


def test_api_growth_plan_ten_year():
    client = TestClient(app)
    resp = client.get("/api/growth-plan/ten-year")
    assert resp.status_code == 200
    data = resp.json()
    assert data["starting_basis"] == PLAN_STARTING_BASIS
    assert data["goal"] == GOAL_ACCOUNT_VALUE
    assert len(data["years"]) == 10
