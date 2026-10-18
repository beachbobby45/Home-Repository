"""Notify, health check, fill modes, random control, PAPER audit idempotency."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.execution.health_check import run_health_check
from investment_agent.execution.ops_audit import (
    KIND_PAPER,
    list_audit_events,
    log_paper_day_complete,
    paper_day_audit_exists,
)
from investment_agent.execution.paper_ledger import (
    ACCOUNT_GATE,
    ensure_paper_accounts,
    paper_scoreboard,
    upsert_session_log,
)
from investment_agent.execution.paper_sim import (
    FILL_MODE_TOUCH,
    FILL_MODE_TRADE_THROUGH,
    simulate_round_trip_5m,
)
from investment_agent.execution.random_control import (
    run_random_pick_control,
    save_random_control_summary,
)
from investment_agent.notify import send_email


class NotifyTests(unittest.TestCase):
    @patch("investment_agent.notify._macos_banner", return_value=False)
    @patch("investment_agent.notify.smtplib.SMTP")
    def test_send_email_smtp_success(self, smtp_cls: MagicMock, _banner: MagicMock) -> None:
        smtp = MagicMock()
        smtp_cls.return_value.__enter__.return_value = smtp
        with patch.dict(
            "os.environ",
            {
                "NOTIFY_ENABLED": "1",
                "NOTIFY_EMAIL": "Beachbobby45@att.net",
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "u",
                "SMTP_PASSWORD": "p",
                "SMTP_USE_TLS": "1",
            },
            clear=False,
        ):
            result = send_email("subj", "body line")
        self.assertTrue(result["ok"])
        self.assertTrue(result["emailed"])
        self.assertEqual(result["to"], "Beachbobby45@att.net")
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("u", "p")
        smtp.send_message.assert_called_once()

    @patch("investment_agent.notify._macos_banner", return_value=True)
    def test_send_email_log_only_without_smtp(self, banner: MagicMock) -> None:
        with patch.dict(
            "os.environ",
            {
                "NOTIFY_ENABLED": "1",
                "NOTIFY_EMAIL": "Beachbobby45@att.net",
                "SMTP_HOST": "",
                "SMTP_USER": "",
                "SMTP_PASSWORD": "",
            },
            clear=False,
        ):
            result = send_email("log only", "no smtp")
        self.assertTrue(result["ok"])
        self.assertFalse(result["emailed"])
        self.assertTrue(result["banner"])
        self.assertIn("SMTP not configured", result["detail"])
        banner.assert_called_once()


class HealthCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)
        ensure_paper_accounts(self.conn, starting_cash=5_000)
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_health_check_basic_no_notify(self) -> None:
        result = run_health_check(self.conn, send_notify=False)
        self.assertIn("ok", result)
        self.assertIn("checks", result)
        self.assertIsNone(result["notify"])
        names = {c["name"] for c in result["checks"]}
        self.assertIn("paper_equity", names)
        self.assertTrue(any(c["name"] == "paper_equity" and c["ok"] for c in result["checks"]))


class FillModeTests(unittest.TestCase):
    def test_touch_fills_on_exact_low(self) -> None:
        bars = [
            {
                "ts": "2026-10-16T09:35:00-04:00",
                "open": 100,
                "high": 100.2,
                "low": 99.5,
                "close": 99.8,
            },
            {
                "ts": "2026-10-16T10:00:00-04:00",
                "open": 99.8,
                "high": 101.5,
                "low": 99.7,
                "close": 101.2,
            },
        ]
        touch = simulate_round_trip_5m(
            bars,
            buy=99.5,
            sell=101.0,
            stop=98.5,
            shares=10,
            buy_fee=7,
            sell_fee=7,
            fill_mode=FILL_MODE_TOUCH,
        )
        through = simulate_round_trip_5m(
            bars,
            buy=99.5,
            sell=101.0,
            stop=98.5,
            shares=10,
            buy_fee=7,
            sell_fee=7,
            fill_mode=FILL_MODE_TRADE_THROUGH,
        )
        self.assertTrue(touch["filled"])
        self.assertEqual(touch["exit_reason"], "target")
        # Exact touch of 99.5 does not trade through
        self.assertFalse(through["filled"])
        self.assertEqual(through["scenario"], "no_fill_by_1130")

    def test_trade_through_requires_strict_breach(self) -> None:
        bars = [
            {
                "ts": "2026-10-16T09:35:00-04:00",
                "open": 100,
                "high": 100.5,
                "low": 99.0,
                "close": 99.5,
            },
            {
                "ts": "2026-10-16T10:00:00-04:00",
                "open": 99.5,
                "high": 102.0,
                "low": 99.4,
                "close": 101.5,
            },
        ]
        sim = simulate_round_trip_5m(
            bars,
            buy=99.5,
            sell=101.0,
            stop=98.5,
            shares=10,
            buy_fee=7,
            sell_fee=7,
            fill_mode=FILL_MODE_TRADE_THROUGH,
        )
        self.assertTrue(sim["filled"])
        self.assertTrue(sim["complete"])
        self.assertEqual(sim["exit_reason"], "target")
        self.assertEqual(sim["fill_mode"], FILL_MODE_TRADE_THROUGH)


class RandomControlSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)
        ensure_paper_accounts(self.conn, starting_cash=5_000)
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_random_control_empty_window_smoke(self) -> None:
        # No OHLCV / ranks → skipped days, still returns structured summary
        summary = run_random_pick_control(
            self.conn,
            since="2026-10-20",
            until="2026-10-21",
            top_n=5,
            persist=True,
            lookback_days=5,
        )
        self.assertTrue(summary["ok"])
        self.assertIn("beats_random", summary)
        self.assertEqual(summary["fill_mode"], FILL_MODE_TRADE_THROUGH)
        sb = paper_scoreboard(self.conn)
        self.assertIn("random_control_ok", sb["checks"])

    def test_scoreboard_reads_persisted_control(self) -> None:
        save_random_control_summary(
            self.conn,
            {
                "ok": True,
                "beats_random": True,
                "random_control_ok": True,
                "top1": {"expectancy": 1.0},
                "random": {"expectancy": 0.5},
            },
        )
        self.conn.commit()
        sb = paper_scoreboard(self.conn)
        self.assertTrue(sb["checks"]["random_control_ok"])


class PaperAuditIdempotencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)
        ensure_paper_accounts(self.conn, starting_cash=5_000)
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_paper_day_audit_once(self) -> None:
        gate = {
            "session_date_et": "2026-10-20",
            "account_name": ACCOUNT_GATE,
            "status": "complete",
            "ticker": "TEST",
            "filled": True,
            "net_pnl": 12.5,
        }
        upsert_session_log(self.conn, gate)
        first = log_paper_day_complete(
            self.conn, session_date_et="2026-10-20", gate_log=gate
        )
        second = log_paper_day_complete(
            self.conn, session_date_et="2026-10-20", gate_log=gate
        )
        self.conn.commit()
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertTrue(paper_day_audit_exists(self.conn, "2026-10-20"))
        events = list_audit_events(self.conn, kind=KIND_PAPER, limit=10)
        self.assertEqual(len(events), 1)
        self.assertIn("PAPER day complete", events[0]["title"])


class PaperApiHealthTests(unittest.TestCase):
    def test_ops_health_and_health_endpoints(self) -> None:
        import sqlite3

        from fastapi.testclient import TestClient

        from investment_agent.dashboard.app import app

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_db(db_path)

            def fake_connect():
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                return conn

            with patch("investment_agent.dashboard.app.connect", fake_connect):
                with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                    http = TestClient(app)
                    h = http.get("/api/health")
                    self.assertEqual(h.status_code, 200, h.text)
                    self.assertTrue(h.json()["ok"])
                    self.assertIn("fill_mode", h.json())
                    ops = http.get("/api/ops/health")
                    self.assertEqual(ops.status_code, 200, ops.text)
                    self.assertIn("checks", ops.json())


if __name__ == "__main__":
    unittest.main()
