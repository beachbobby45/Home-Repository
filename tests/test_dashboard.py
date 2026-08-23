"""Tests for FastAPI dashboard routes."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app
from investment_agent.db import init_db


def test_dashboard_homepage():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/")
                assert resp.status_code == 200
                assert "AI Investment Agent" in resp.text


def test_dashboard_inline_script_parses():
    """Dashboard UI is one inline script — a syntax error bricks the whole page."""
    html = (ROOT / "src/investment_agent/dashboard/templates/dashboard.html").read_text(
        encoding="utf-8"
    )
    assert "<script>" in html
    assert "??" in html  # sanity: template uses nullish coalescing
    assert "?? cb.weekly_soft_progress_pct ||" not in html
    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    import subprocess

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
        script_path = fh.name
    try:
        proc = subprocess.run(
            ["node", "--check", script_path],
            capture_output=True,
            text=True,
        )
    finally:
        Path(script_path).unlink(missing_ok=True)
    assert proc.returncode == 0, proc.stderr


def test_api_summary_empty_db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/api/summary")
                assert resp.status_code == 200
                data = resp.json()
                assert data["tradable_cash"] == 15000.0
                assert "goal_pct" in data
