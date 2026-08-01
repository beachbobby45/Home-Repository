"""Full dashboard integration tests with seeded demo data."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app, _require_api_key
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db


class DashboardIntegration:
    """Context manager wrapping patched TestClient with auth bypass for POST routes."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._patches = []

    def __enter__(self) -> TestClient:
        def fake_connect():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

        self._patches = [
            patch("investment_agent.dashboard.app.connect", fake_connect),
            patch("investment_agent.dashboard.app.init_db", lambda: self.db_path),
        ]
        for p in self._patches:
            p.start()
        app.dependency_overrides[_require_api_key] = lambda: None
        return TestClient(app)

    def __exit__(self, *args) -> None:
        app.dependency_overrides.pop(_require_api_key, None)
        for p in self._patches:
            p.stop()


def test_full_dashboard_flow_with_demo_data():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "integration.db"
        seed_demo_db(db_path)
        expected = expected_demo_summary()

        with DashboardIntegration(db_path) as client:
            # Page loads
            home = client.get("/")
            assert home.status_code == 200
            for section_id in (
                "regime-banner", "scenario-panel", "cio-headline", "learning-panel",
            ):
                assert section_id in home.text or section_id.replace("-", "_") in home.text

            # Summary
            summary = client.get("/api/summary").json()
            assert abs(summary["tradable_cash"] - expected["tradable_cash"]) < 0.02
            assert summary["vix"] == expected["vix"]
            assert summary["regime"]["summary"].startswith("Regime OK")
            assert summary["market_brief"]
            assert "sweep_preview" in summary

            # Queue with live fields
            queue = client.get("/api/queue").json()
            assert len(queue) == expected["queue_count"]
            nvda = next(q for q in queue if q["ticker"] == "NVDA")
            assert nvda["state"] == "in_trade"
            assert nvda["current_price"] is not None
            assert nvda["pnl_pct"] is not None

            # Journal
            journal = client.get("/api/journal").json()
            assert len(journal) == expected["journal_count"]

            # Phase 6 — Scenario visualizer
            scenario = client.get("/api/scenario/visualizer").json()
            assert scenario["goal"] == 5_000_000
            assert len(scenario["actual_timeline"]) >= 3
            assert scenario["scenarios"]["journal_pace"]["months_to_goal"] is not None
            assert "scenario-panel" in home.text or "Scenario Visualizer" in home.text

            # Candidates from metrics
            candidates = client.get("/api/candidates").json()
            assert isinstance(candidates, list)
            assert len(candidates) >= 1

            # Monitor + alerts
            mon = client.post("/api/monitor/run").json()
            assert mon["ok"] is True
            assert mon["new_alerts"] >= 1

            alerts = client.get("/api/alerts").json()
            assert len(alerts) >= 1
            assert any(a["alert_type"] == "TARGET_HIT" for a in alerts)

            # Acknowledge
            alert_id = alerts[0]["id"]
            ack = client.post(f"/api/alerts/{alert_id}/acknowledge").json()
            assert ack["ok"] is True
            remaining = client.get("/api/alerts").json()
            assert all(a["id"] != alert_id for a in remaining)

            # Queue advance
            amd = next(q for q in queue if q["ticker"] == "AMD")
            adv = client.post(f"/api/queue/{amd['id']}/advance").json()
            assert adv["ok"] is True
            assert adv["to_state"] == "approved"

            # Log trade
            trade = client.post(
                "/api/journal",
                json={"ticker": "AMD", "side": "BUY", "shares": 5, "price": 160.0},
            ).json()
            assert trade["ok"] is True

            # Tax rate
            tax = client.put("/api/settings/tax-rate", json={"tax_rate": 0.28}).json()
            assert tax["tax_rate"] == 0.28

            # Sync queue
            sync = client.post("/api/queue/sync").json()
            assert "added" in sync or "message" in sync

            # Static
            assert client.get("/static/style.css").status_code == 200

            # Phase 5 — CIO + Learning
            cio = client.get("/api/cio/summary").json()
            assert cio["headline"]
            assert len(cio["action_items"]) >= 1
            assert cio["sub_agents"]["regime"].startswith("Regime OK")

            learning = client.get("/api/learning/report").json()
            assert learning["active_positions"]
            assert learning["round_trips"]

            gen = client.post("/api/learning/generate").json()
            assert gen["ok"] is True
            assert gen["report"]["highlights"]


def test_verify_dashboard_script_matches_integration():
    """Ensure verify_dashboard.py checks align with integration expectations."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "verify.db"
        seed_demo_db(db_path)

        import importlib.util

        script = ROOT / "scripts" / "verify_dashboard.py"
        spec = importlib.util.spec_from_file_location("verify_dashboard", script)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        report = mod.verify(db_path)
        assert report["failed"] == 0, report["results"]
