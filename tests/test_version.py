"""Tests for application version metadata."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app
from investment_agent.version import __version__, version_info


def test_version_info():
    info = version_info()
    assert info["version"] == __version__
    assert info["version"] == "0.9.10"
    assert "paper" in info["release"].lower() or "bars" in info["release"].lower()


def test_api_version_endpoint():
    client = TestClient(app)
    resp = client.get("/api/version")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "0.9.10"
    assert "paper" in data["release"].lower() or "bars" in data["release"].lower()
