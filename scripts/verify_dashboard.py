#!/usr/bin/env python3
"""Verify all dashboard API endpoints against seeded demo data."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from unittest.mock import patch

from investment_agent.dashboard.app import app, _require_api_key
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.db import DEFAULT_DB_PATH


def _checks() -> list[tuple[str, callable]]:
    return []


def verify(db_path: Path) -> dict:
    results: list[dict] = []
    passed = 0
    failed = 0
    expected = expected_demo_summary()

    def record(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed, failed
        results.append({"check": name, "ok": ok, "detail": detail})
        if ok:
            passed += 1
        else:
            failed += 1

    def fake_connect():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    with patch("investment_agent.dashboard.app.connect", fake_connect):
        with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
            app.dependency_overrides[_require_api_key] = lambda: None
            client = TestClient(app)

            # Homepage
            r = client.get("/")
            record("GET /", r.status_code == 200 and "AI Investment Agent" in r.text, f"status={r.status_code}")

            # Summary
            r = client.get("/api/summary")
            data = r.json()
            record("GET /api/summary", r.status_code == 200, "")
            record(
                "summary.tradable_cash",
                abs(data.get("tradable_cash", 0) - expected["tradable_cash"]) < 0.02,
                f"got {data.get('tradable_cash')} want {expected['tradable_cash']}",
            )
            record(
                "summary.monthly_realized_net",
                abs(data.get("monthly_realized_net", 0) - expected["monthly_realized_net"]) < 0.02,
                f"got {data.get('monthly_realized_net')} want {expected['monthly_realized_net']}",
            )
            record("summary.vix", data.get("vix") == expected["vix"], str(data.get("vix")))
            record(
                "summary.regime",
                data.get("regime") and not data.get("block_new_longs"),
                str(data.get("regime", {}).get("summary", "")[:60]),
            )
            record("summary.market_brief", bool(data.get("market_brief")), "")
            record("summary.sweep_preview", "sweep_preview" in data, "")

            # Queue
            r = client.get("/api/queue")
            queue = r.json()
            record("GET /api/queue", r.status_code == 200, f"count={len(queue)}")
            record(
                "queue.count",
                len(queue) == expected["queue_count"],
                f"got {len(queue)} want {expected['queue_count']}",
            )
            nvda = next((q for q in queue if q["ticker"] == "NVDA"), None)
            record(
                "queue.nvda_monitor",
                nvda is not None
                and nvda.get("current_price") is not None
                and nvda.get("pnl_pct") is not None,
                str(nvda),
            )

            # Candidates
            r = client.get("/api/candidates")
            record("GET /api/candidates", r.status_code == 200, f"count={len(r.json())}")

            # Journal
            r = client.get("/api/journal")
            journal = r.json()
            record("GET /api/journal", r.status_code == 200, f"count={len(journal)}")
            record(
                "journal.count",
                len(journal) == expected["journal_count"],
                f"got {len(journal)} want {expected['journal_count']}",
            )

            # Monitor run
            r = client.post("/api/monitor/run")
            mon = r.json()
            record("POST /api/monitor/run", r.status_code == 200 and mon.get("ok"), str(mon.get("new_alerts")))
            record(
                "monitor.target_alert",
                mon.get("new_alerts", 0) >= 1,
                f"evaluations={len(mon.get('evaluations', []))}",
            )

            # Alerts
            r = client.get("/api/alerts")
            alerts = r.json()
            record("GET /api/alerts", r.status_code == 200, f"count={len(alerts)}")
            record(
                "alerts.non_empty",
                len(alerts) >= 1,
                f"types={[a.get('alert_type') for a in alerts]}",
            )

            target = next((a for a in alerts if a.get("alert_type") == "TARGET_HIT"), None)
            record("alerts.target_hit", target is not None, str(target.get("ticker") if target else ""))

            if target:
                r = client.post(f"/api/alerts/{target['id']}/acknowledge")
                record("POST /api/alerts/acknowledge", r.status_code == 200 and r.json().get("ok"), "")

            # Queue sync (should not fail; may add 0 if all active)
            r = client.post("/api/queue/sync")
            record("POST /api/queue/sync", r.status_code == 200, str(r.json()))

            # Tax rate
            r = client.put("/api/settings/tax-rate", json={"tax_rate": 0.30})
            record("PUT /api/settings/tax-rate", r.status_code == 200 and r.json().get("tax_rate") == 0.30, "")

            # Trade log
            r = client.post(
                "/api/journal",
                json={
                    "ticker": "AMD",
                    "side": "BUY",
                    "shares": 1,
                    "price": 160.0,
                    "notes": "verify_dashboard test",
                },
            )
            record("POST /api/journal", r.status_code == 200 and r.json().get("ok"), "")

            # Phase 5 — CIO + Learning
            r = client.get("/api/cio/summary")
            cio = r.json()
            record("GET /api/cio/summary", r.status_code == 200 and bool(cio.get("headline")), "")
            record("cio.action_items", len(cio.get("action_items", [])) >= 1, "")
            record("cio.sub_agents", len(cio.get("sub_agents", {})) >= 4, "")

            r = client.get("/api/learning/report")
            learning = r.json()
            record("GET /api/learning/report", r.status_code == 200, "")
            record("learning.active_positions", len(learning.get("active_positions", [])) >= 1, "")
            record("learning.round_trips", len(learning.get("round_trips", [])) >= 1, "")

            r = client.post("/api/learning/generate")
            gen = r.json()
            record("POST /api/learning/generate", r.status_code == 200 and gen.get("ok"), "")

            # Static assets
            r = client.get("/static/style.css")
            record("GET /static/style.css", r.status_code == 200, "")

            app.dependency_overrides.pop(_require_api_key, None)

    return {
        "ok": failed == 0,
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify dashboard with demo data")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--seed", action="store_true", help="Re-seed demo data first")
    args = parser.parse_args()

    if args.seed:
        seed_demo_db(args.db)
        print(f"Seeded demo data → {args.db}")

    report = verify(args.db)
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
