"""Tests for decision-time attribution (Phase 1B Inc 18)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_regime_snapshot, insert_ticker_metrics
from investment_agent.decision_attribution import (
    authorization_outcome,
    build_market_activity_band_stats,
    list_decision_attribution,
    log_decision_attribution,
    log_proposal_attribution,
)
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.learning import generate_learning_report
from investment_agent.trade_proposal import (
    approve_proposal,
    generate_proposals,
    list_proposals_for_session,
    reject_proposal,
)
from investment_agent.watchlist import load_preset_into_watchlist


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


def _conn() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def test_authorization_outcome_variants():
    assert authorization_outcome(market_activity={"allow_trade": True}) == "TRADE"
    assert authorization_outcome(market_activity={"allow_trade": False}) == "NO_TRADE"
    assert authorization_outcome(market_activity={"allow_trade": False}, exceptional_active=True) == "EXCEPTIONAL"
    assert authorization_outcome(market_activity=None) == "UNKNOWN"


def test_log_and_list_decision_attribution():
    conn = _conn()
    try:
        log_decision_attribution(
            conn,
            event_type="live_refresh",
            session_date_et="2026-08-03",
            market_activity={"score": 85, "band": "above_average", "allow_trade": True},
            confirmation={"score": 80, "passes": True},
        )
        conn.commit()
        rows = list_decision_attribution(conn, session_date_et="2026-08-03")
        assert len(rows) == 1
        assert rows[0]["authorization_outcome"] == "TRADE"
        assert rows[0]["market_activity_band"] == "above_average"
        assert rows[0]["confirmation_passes"] is True
    finally:
        conn.close()


def test_build_market_activity_band_stats():
    conn = _conn()
    try:
        conn.execute(
            """
            INSERT INTO trade_proposals
              (proposal_uuid, strategy_version, model_version, created_at, valid_until,
               session_date_et, ticker, direction, opportunity_score, factor_scores_json,
               plan_json, risk_verdict, risk_checks_json, status, outcome_net_pnl)
            VALUES (?, 'v1', 'test', ?, ?, '2026-08-03', 'AAPL', 'long', 80, '{}', '{}',
                    'approved', '[]', 'closed', 120.0)
            """,
            (
                str(uuid.uuid4()),
                datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            ),
        )
        log_decision_attribution(
            conn,
            event_type="proposal_approve",
            session_date_et="2026-08-03",
            ticker="AAPL",
            proposal_id=1,
            market_activity={"score": 90, "band": "exceptional", "allow_trade": True},
            confirmation={"score": 88, "passes": True},
            human_verdict="approved",
        )
        conn.commit()
        stats = build_market_activity_band_stats(conn, lookback_days=30)
        assert stats["lookback_days"] == 30
        assert len(stats["bands"]) >= 1
        exc = next(b for b in stats["bands"] if b["band"] == "exceptional")
        assert exc["events"] == 1
        assert exc["wins"] == 1
        assert exc["win_rate_pct"] == 100.0
    finally:
        conn.close()


def _seed_proposal_env(conn: sqlite3.Connection):
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


def test_generate_proposals_logs_attribution():
    conn = _conn()
    try:
        _seed_proposal_env(conn)
        with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
            with patch(
                "investment_agent.trade_proposal.get_latest_quote_rows",
                return_value={"AAPL": {"open": 100, "price": 100}, "NVDA": {"open": 100, "price": 100}},
            ):
                with patch("investment_agent.trading_day.session_phase", return_value="pre_market"):
                    result = generate_proposals(conn)
        assert result["ok"] is True
        rows = list_decision_attribution(conn)
        assert any(r["event_type"] == "proposal_generate" for r in rows)
    finally:
        conn.close()


def test_approve_and_reject_log_attribution():
    conn = _conn()
    try:
        _seed_proposal_env(conn)
        quotes = {"AAPL": {"open": 100, "price": 100}, "NVDA": {"open": 100, "price": 100}}
        with patch("investment_agent.trade_proposal.build_ranked_candidates", return_value=_mock_ranked()):
            with patch("investment_agent.trade_proposal.get_latest_quote_rows", return_value=quotes):
                with patch("investment_agent.trading_day.session_phase", return_value="pre_market"):
                    generate_proposals(conn, max_proposals=2)
        proposals = list_proposals_for_session(conn)
        approve_id = proposals[0]["id"]
        reject_id = proposals[1]["id"]
        with patch("investment_agent.trade_proposal.refresh_proposal_risk", return_value={"ok": True, "risk": {}}):
            approve_proposal(conn, approve_id)
        reject_proposal(conn, reject_id, reason_code="TIMING")
        conn.commit()
        rows = list_decision_attribution(conn)
        assert any(r["event_type"] == "proposal_approve" and r["human_verdict"] == "approved" for r in rows)
        assert any(r["event_type"] == "proposal_reject" and r["human_verdict"] == "rejected" for r in rows)
    finally:
        conn.close()


def test_learning_report_includes_market_activity_attribution():
    conn = _conn()
    try:
        log_decision_attribution(
            conn,
            event_type="live_refresh",
            session_date_et="2026-08-03",
            market_activity={"score": 70, "band": "average", "allow_trade": False},
            confirmation={"score": 60, "passes": False},
        )
        conn.commit()
        report = generate_learning_report(conn, report_date="2026-08-03")
        assert "market_activity_attribution" in report
        assert report["market_activity_attribution"]["lookback_days"] == 30
    finally:
        conn.close()


def test_log_proposal_attribution_helper():
    conn = _conn()
    try:
        _seed_proposal_env(conn)
        log_proposal_attribution(
            conn,
            event_type="proposal_generate",
            session_date_et="2026-08-03",
            ticker="AAPL",
            proposal_id=99,
        )
        conn.commit()
        rows = list_decision_attribution(conn)
        assert len(rows) == 1
        assert rows[0]["ticker"] == "AAPL"
        assert rows[0]["proposal_id"] == 99
    finally:
        conn.close()
