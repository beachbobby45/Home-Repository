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
    PLAN_START_CALENDAR_YEAR,
    PLAN_STARTING_BASIS,
    RH_LIVE_DATE,
    build_ten_year_growth_plan,
)


def test_build_ten_year_has_calendar_rows():
    data = build_ten_year_growth_plan()
    assert len(data["years"]) == 12
    assert data["years"][0]["year"] == PLAN_START_CALENDAR_YEAR == 2027
    assert data["years"][1]["year"] == 2028
    assert data["years"][-1]["year"] == 2038
    assert data["calendar_year_start"] == 2027


def test_opening_seed_counts_in_2027():
    data = build_ten_year_growth_plan()
    y2027 = data["years"][0]
    assert y2027["injection"]["capital_injection"] == 15_000.0
    assert y2027["base"]["capital_injection"] == 15_000.0
    assert y2027["injection"]["start_balance"] == PLAN_STARTING_BASIS
    # No staged ladder by default — base and funded paths match
    assert y2027["advantage_end_balance"] == 0.0


def test_months_to_goal_present():
    data = build_ten_year_growth_plan()
    base_m = data["months_to_goal"]["base"]
    inj_m = data["months_to_goal"]["injection"]
    assert base_m is not None and inj_m is not None
    assert inj_m == base_m
    gy = data["goal_year"]
    assert gy["injection"] is not None and gy["base"] is not None
    assert gy["injection"] == gy["base"]


def test_plan_starts_at_fifteen_k():
    data = build_ten_year_growth_plan()
    assert data["starting_basis"] == PLAN_STARTING_BASIS == 15_000.0
    assert data["funded_target"] == PLAN_FUNDED_TARGET
    assert data["assumptions"]["sessions_per_week_cap"] == 5
    assert data["assumptions"]["year_axis"] == "calendar"
    assert data["assumptions"]["injection_schedule"] == []
    assert data["assumptions"]["rh_live_date"] == RH_LIVE_DATE == "2027-01-04"
    cash = data["assumptions"]["cash_schedule"]
    assert cash[-1]["date"] == "2027-01-04" and cash[-1]["amount"] == 15_000.0
    assert "2027" in data["summary"]
    assert "$5,000 start" not in data["summary"]


def test_api_growth_plan_ten_year():
    client = TestClient(app)
    resp = client.get("/api/growth-plan/ten-year")
    assert resp.status_code == 200
    data = resp.json()
    assert data["starting_basis"] == PLAN_STARTING_BASIS
    assert data["goal"] == GOAL_ACCOUNT_VALUE
    assert data["years"][0]["year"] == 2027
    assert len(data["years"]) == 12
