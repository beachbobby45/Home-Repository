"""Tests for Phase 1 Trade Proposal Service (Increment 4)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.config import Settings
from investment_agent.dashboard.app import app
from investment_agent.db import init_db, insert_regime_snapshot, insert_ticker_metrics
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.journal import insert_trade, list_trades
from investment_agent.trade_proposal import (
    REJECTION_REASONS,
    STATUS_EXECUTED,
    STATUS_HUMAN_APPROVED,
    STATUS_HUMAN_REJECTED,
    STATUS_PROPOSED,
    STATUS_RISK_REJECTED,
    approve_proposal,
    generate_proposals,
    get_proposal,
    list_proposals_for_session,
    mark_proposal_executed,
    reject_proposal,
    validate_journal_buy_proposal,
)
from investment_agent.watchlist import load_preset_into_watchlist


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _seed_ranked_env(conn):
    load_preset_into_watchlist(conn, "starter10")
    now = datetime.now(timezone.utc)
    _seed_ohlcv_history(conn, ["AAPL", "MSFT", "NVDA", "SPY", "DIA", "QQQ"], end=now)
    insert_regime_snapshot(
        conn,
        {
            "captured_at": now.replace(microsecond=0).isoformat(),
            "spy_change_pct": 0.4,
            "dia_change_pct": 0.3,
            "qqq_change_pct": 0.5,
            "all_indices_down": False,
            "block_new_longs": False,
            "summary": "Regime OK",
        },
    )
    for ticker in ("AAPL", "MSFT", "NVDA"):
        insert_ticker_metrics(
            conn,
            {
                "ticker": ticker,
                "computed_at": now.replace(microsecond=0).isoformat(),
                "adv_dollar": 50_000_000,
                "avg_range_pct": 3.0,
                "liquidity_cap": 400_000,
                "last_close": 100,
                "last_quote": 100,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
    conn.commit()


def _mock_ranked():
    return {
        "ranked": [
            {
                "ticker": "AAPL",
                "opportunity_score": 82,
                "factor_scores": {"market_regime": 80, "dollar_history": 75},
                "avg_range_pct": 3.0,
                "suggested_size": 10000,
                "liquidity_cap": 400000,
                "dollar_hit_rate_pct": 65,
                "live_pass_today": True,
                "near_swing_target": True,
                "meets_liquidity": True,
                "entry_price": 100,
            },
            {
                "ticker": "NVDA",
                "opportunity_score": 78,
                "factor_scores": {"market_regime": 75},
                "avg_range_pct": 3.5,
                "suggested_size": 10000,
                "liquidity_cap": 400000,
                "dollar_hit_rate_pct": 60,
                "live_pass_today": True,
                "near_swing_target": True,
                "meets_liquidity": True,
                "entry_price": 100,
            },
        ],
        "excluded": [],
    }


from contextlib import contextmanager


@contextmanager
def _bypass_market_activity_gate():
    """Proposal unit tests focus on ranking/risk — not live market-activity gate."""
    with patch("investment_agent.trading_day.session_phase", return_value="pre_market"):
        yield


def test_rejection_reasons_enum():
    assert "NO_CONVICTION" in REJECTION_REASONS
    assert "OTHER" in REJECTION_REASONS


def test_generate_blocked_when_market_activity_no_trade():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        ma_blocked = {
            "session_date_et": "2026-08-03",
            "captured_at": "2026-08-03T14:00:00+00:00",
            "score": 52,
            "band": "below_average",
            "band_label": "Below average",
            "allow_trade": False,
            "bull_gate_ok": False,
            "exit_alert": False,
            "summary": "NO TRADE",
            "index_changes": {},
            "components": {},
        }
        with patch("investment_agent.trading_day.session_phase", return_value="trade_window"):
            with patch(
                "investment_agent.market_activity.evaluate_market_activity",
                return_value=ma_blocked,
            ):
                result = generate_proposals(conn, max_proposals=1)
        assert result["ok"] is False
        assert "DO NOT TRADE" in result["error"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_generate_proposals_max_five_sorted():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}, "NVDA": {"open": 100, "price": 100}}):
                    result = generate_proposals(conn, max_proposals=5)
        assert result["ok"] is True
        assert result["generated"] <= 5
        proposals = list_proposals_for_session(conn, result["session_date_et"])
        assert len(proposals) <= 5
        if len(proposals) >= 2:
            assert proposals[0]["opportunity_score"] >= proposals[1]["opportunity_score"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_generate_proposals_with_null_dollar_hit_rate():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        ranked = _mock_ranked()
        ranked["ranked"][0]["dollar_hit_rate_pct"] = None
        ranked["ranked"][0]["ticker"] = "GEN"
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=ranked):
                with patch(
                    "investment_agent.trade_proposal.get_latest_quotes",
                    return_value={"GEN": {"open": 100, "price": 100}},
                ):
                    result = generate_proposals(conn, max_proposals=1)
        assert result["ok"] is True
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_generate_skips_risk_rejected():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        ranked = _mock_ranked()
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=ranked):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    with patch(
                        "investment_agent.trade_proposal._evaluate_candidate_risk",
                        return_value={"verdict": "rejected", "headline": "Blocked", "blockers": ["Kill switch"], "checks": []},
                    ):
                        result = generate_proposals(conn, max_proposals=1)
        proposals = list_proposals_for_session(conn, result["session_date_et"])
        assert proposals[0]["status"] == STATUS_RISK_REJECTED
        assert result["actionable_count"] == 0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_reject_proposal_persists_reason():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    generate_proposals(conn, max_proposals=1)
        pid = list_proposals_for_session(conn)[0]["id"]
        result = reject_proposal(conn, pid, reason_code="NO_CONVICTION")
        assert result["ok"] is True
        assert result["proposal"]["status"] == STATUS_HUMAN_REJECTED
        assert "NO_CONVICTION" in result["proposal"]["human_rejection_reason"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_reject_other_requires_text():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    generate_proposals(conn, max_proposals=1)
        pid = list_proposals_for_session(conn)[0]["id"]
        result = reject_proposal(conn, pid, reason_code="OTHER", reason_text=None)
        assert result["ok"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_approve_reruns_risk_on_live_refresh():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    generate_proposals(conn, max_proposals=1)
        pid = list_proposals_for_session(conn)[0]["id"]
        settings = Settings(
            anthropic_api_key="",
            fred_api_key="",
            finnhub_api_key="test",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        with patch("investment_agent.trade_proposal.refresh_live_quotes", return_value={"ok": True}) as mock_refresh:
            with patch(
                "investment_agent.trade_proposal._evaluate_candidate_risk",
                return_value={"verdict": "approved", "headline": "OK", "blockers": [], "checks": []},
            ):
                result = approve_proposal(conn, pid, settings=settings)
        assert result["ok"] is True
        assert result["proposal"]["status"] == STATUS_HUMAN_APPROVED
        mock_refresh.assert_called_once()
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_approve_blocked_when_risk_fails_refresh():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    generate_proposals(conn, max_proposals=1)
        pid = list_proposals_for_session(conn)[0]["id"]
        with patch(
            "investment_agent.trade_proposal.refresh_proposal_risk",
            return_value={"ok": False, "risk": {"verdict": "rejected", "blockers": ["Daily loss"]}},
        ):
            result = approve_proposal(conn, pid, settings=None)
        assert result["ok"] is False
        assert get_proposal(conn, pid)["status"] != STATUS_HUMAN_APPROVED
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_journal_buy_links_proposal():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    generate_proposals(conn, max_proposals=1)
        proposal = list_proposals_for_session(conn)[0]
        conn.execute(
            "UPDATE trade_proposals SET status = ?, human_verdict = 'approved' WHERE id = ?",
            (STATUS_HUMAN_APPROVED, proposal["id"]),
        )
        conn.commit()
        check = validate_journal_buy_proposal(
            conn, proposal_id=proposal["id"], ticker="AAPL", side="BUY"
        )
        assert check["ok"] is True
        trade_id = insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=99,
            proposal_id=proposal["id"],
        )
        mark_proposal_executed(conn, proposal["id"], trade_id)
        conn.commit()
        trades = list_trades(conn, limit=1)
        assert trades[0].proposal_id == proposal["id"]
        assert get_proposal(conn, proposal["id"])["status"] == STATUS_EXECUTED
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_validate_journal_buy_requires_approved():
    conn, path = _conn()
    try:
        _seed_ranked_env(conn)
        with _bypass_market_activity_gate():
            with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
                with patch("investment_agent.trade_proposal.get_latest_quotes", return_value={"AAPL": {"open": 100, "price": 100}}):
                    generate_proposals(conn, max_proposals=1)
        pid = list_proposals_for_session(conn)[0]["id"]
        check = validate_journal_buy_proposal(conn, proposal_id=pid, ticker="AAPL", side="BUY")
        assert check["ok"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_api_proposals_generate_and_today():
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
                with patch("investment_agent.dashboard.app.generate_proposals") as mock_gen:
                    mock_gen.return_value = {
                        "ok": True,
                        "session_date_et": "2026-08-14",
                        "generated": 2,
                        "actionable_count": 2,
                        "proposals": [],
                        "created": [],
                        "skipped": [],
                        "max_proposals": 5,
                    }
                    resp = client.post("/api/proposals/generate", json={"replace_existing": True})
                    assert resp.status_code == 200
                    assert resp.json()["generated"] == 2
                with patch("investment_agent.dashboard.app.list_proposals_for_session", return_value=[{"id": 1, "ticker": "AAPL", "status": STATUS_PROPOSED, "opportunity_score": 80}]):
                    resp2 = client.get("/api/proposals/today")
                    assert resp2.status_code == 200
                    assert resp2.json()["count"] == 1


def test_init_db_has_trade_proposals_table():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.db"
        init_db(path)
        conn = sqlite3.connect(path)
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        conn.close()
        assert "trade_proposals" in tables
