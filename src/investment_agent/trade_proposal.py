"""Trade Proposal Service — persisted decision artifacts (Phase 1 Increment 4)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary
from investment_agent.ai_service import enrich_proposal
from investment_agent.config import Settings
from investment_agent.finance import ORIGINAL_BASIS, target_move_pct
from investment_agent.monitor import get_latest_quotes
from investment_agent.opportunity_score import (
    OPPORTUNITY_FLOOR,
    composite_opportunity_score,
    finalize_proposal_factor_scores,
    passes_opportunity_floor,
)
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE, compute_pullback_trade_plan
from investment_agent.risk_engine import (
    MarketSnapshot,
    TradeProposalPlan,
    build_portfolio_snapshot,
    evaluate_proposal,
    risk_decision_to_dict,
)
from investment_agent.trading_day import refresh_live_quotes, today_et_str

ET = ZoneInfo("America/New_York")

STRATEGY_VERSION = "phase1-capital-builder-v1"
MAX_PROPOSALS_PER_GENERATE = 5
DIRECTION_LONG = "long"

REJECTION_REASONS: dict[str, str] = {
    "NO_CONVICTION": "Don't agree with setup",
    "NEWS_RISK": "News/event too risky",
    "MARKET_RISK": "Market conditions",
    "SIZE_TOO_LARGE": "Position too big",
    "ALREADY_EXPOSED": "Already have exposure",
    "TIMING": "Bad timing / missed entry",
    "OTHER": "Other (see notes)",
}

STATUS_DRAFT = "draft"
STATUS_RISK_REJECTED = "risk_rejected"
STATUS_PROPOSED = "proposed"
STATUS_HUMAN_REJECTED = "human_rejected"
STATUS_HUMAN_APPROVED = "human_approved"
STATUS_EXECUTED = "executed"
STATUS_CLOSED = "closed"
STATUS_EXPIRED = "expired"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _valid_until_iso(session_date_et: str) -> str:
    y, m, d = map(int, session_date_et.split("-"))
    dt = datetime(y, m, d, LIMIT_FILL_DEADLINE.hour, LIMIT_FILL_DEADLINE.minute, tzinfo=ET)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _session_open_from_quote(quote: dict | None, fallback: float | None = None) -> float | None:
    if not quote:
        return fallback
    open_px = quote.get("open") or quote.get("price")
    if open_px and float(open_px) > 0:
        return float(open_px)
    return fallback


def _build_plan_for_candidate(
    row: dict,
    *,
    deploy: float,
    net_target: float,
    quote: dict | None,
) -> dict:
    avg_range = float(row.get("avg_range_pct") or 0)
    session_open = _session_open_from_quote(
        quote,
        fallback=float(row.get("entry_price") or row.get("last_quote") or 0) or None,
    )
    if not session_open or session_open <= 0:
        return {}
    plan = compute_pullback_trade_plan(
        session_open=session_open,
        avg_range_pct=avg_range,
        deploy_dollar=float(row.get("suggested_size") or deploy),
        net_target=net_target,
    )
    if plan:
        plan["liquidity_cap"] = row.get("liquidity_cap")
    return plan


def _row_to_dict(row: sqlite3.Row) -> dict:
    plan = json.loads(row["plan_json"])
    return {
        "id": row["id"],
        "proposal_uuid": row["proposal_uuid"],
        "strategy_version": row["strategy_version"],
        "model_version": row["model_version"],
        "created_at": row["created_at"],
        "valid_until": row["valid_until"],
        "session_date_et": row["session_date_et"],
        "ticker": row["ticker"],
        "direction": row["direction"],
        "opportunity_score": row["opportunity_score"],
        "factor_scores": json.loads(row["factor_scores_json"]),
        "plan": plan,
        "risk_verdict": row["risk_verdict"],
        "risk_checks": json.loads(row["risk_checks_json"]),
        "risk_rejection_reason": row["risk_rejection_reason"],
        "human_verdict": row["human_verdict"],
        "human_rejection_reason": row["human_rejection_reason"],
        "human_approved_at": row["human_approved_at"],
        "explanation": row["explanation"],
        "explanation_short": row["explanation_short"],
        "status": row["status"],
        "journal_buy_id": row["journal_buy_id"],
        "journal_sell_id": row["journal_sell_id"],
        "outcome_net_pnl": row["outcome_net_pnl"],
        "outcome_exit_reason": row["outcome_exit_reason"],
    }


def list_proposals_for_session(
    conn: sqlite3.Connection,
    session_date_et: str | None = None,
) -> list[dict]:
    day = session_date_et or today_et_str()
    rows = conn.execute(
        """
        SELECT * FROM trade_proposals
        WHERE session_date_et = ?
        ORDER BY opportunity_score DESC, id ASC
        """,
        (day,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_proposal(conn: sqlite3.Connection, proposal_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM trade_proposals WHERE id = ?",
        (proposal_id,),
    ).fetchone()
    return _row_to_dict(row) if row else None


def _insert_proposal(conn: sqlite3.Connection, payload: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO trade_proposals (
          proposal_uuid, strategy_version, model_version, created_at, valid_until,
          session_date_et, ticker, direction, opportunity_score, factor_scores_json,
          plan_json, risk_verdict, risk_checks_json, risk_rejection_reason,
          human_verdict, human_rejection_reason, human_approved_at,
          explanation, explanation_short, status,
          journal_buy_id, journal_sell_id, outcome_net_pnl, outcome_exit_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["proposal_uuid"],
            payload["strategy_version"],
            payload["model_version"],
            payload["created_at"],
            payload.get("valid_until"),
            payload["session_date_et"],
            payload["ticker"],
            payload.get("direction", DIRECTION_LONG),
            payload["opportunity_score"],
            json.dumps(payload["factor_scores"]),
            json.dumps(payload["plan"]),
            payload["risk_verdict"],
            json.dumps(payload["risk_checks"]),
            payload.get("risk_rejection_reason"),
            payload.get("human_verdict"),
            payload.get("human_rejection_reason"),
            payload.get("human_approved_at"),
            payload.get("explanation"),
            payload.get("explanation_short"),
            payload["status"],
            payload.get("journal_buy_id"),
            payload.get("journal_sell_id"),
            payload.get("outcome_net_pnl"),
            payload.get("outcome_exit_reason"),
        ),
    )
    return int(cur.lastrowid)


def _evaluate_candidate_risk(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    plan: dict,
    block_new_longs: bool,
    regime_summary: str | None,
) -> dict:
    portfolio = build_portfolio_snapshot(conn)
    market = MarketSnapshot(block_new_longs=block_new_longs, regime_summary=regime_summary)
    entry = float(plan.get("limit_buy_price") or plan.get("entry_price") or 0)
    stop = float(plan.get("stop_price") or 0)
    target = float(plan.get("limit_sell_price") or plan.get("target_price") or 0)
    shares = int(plan.get("shares") or 0)
    proposal = TradeProposalPlan(
        ticker=ticker,
        entry_price=entry,
        stop_price=stop,
        target_price=target,
        shares=shares,
        liquidity_cap=plan.get("liquidity_cap"),
    )
    decision = evaluate_proposal(proposal=proposal, portfolio=portfolio, market=market)
    return risk_decision_to_dict(decision)


def generate_proposals(
    conn: sqlite3.Connection,
    *,
    session_date_et: str | None = None,
    max_proposals: int = MAX_PROPOSALS_PER_GENERATE,
    replace_existing: bool = False,
    settings: Settings | None = None,
) -> dict:
    """Morning generate — up to 5 proposals sorted by opportunity score."""
    day = session_date_et or today_et_str()
    cfg = settings or Settings.from_env()
    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or ORIGINAL_BASIS)
    net_target = float(summary.daily_target or 150)

    if replace_existing:
        conn.execute(
            """
            DELETE FROM trade_proposals
            WHERE session_date_et = ?
              AND status IN (?, ?, ?)
            """,
            (day, STATUS_DRAFT, STATUS_PROPOSED, STATUS_RISK_REJECTED),
        )

    ranked = build_ranked_candidates(
        conn,
        period_days=14,
        require_dollar_rank_gate=True,
        require_opportunity_floor=True,
    )["ranked"]

    quotes = get_latest_quotes(conn)
    regime_summary = summary.regime["summary"] if summary.regime else None
    block_new_longs = bool(summary.block_new_longs)

    created: list[dict] = []
    skipped: list[dict] = []
    seen_tickers: set[str] = set()

    for row in ranked:
        if len(created) >= max_proposals:
            break
        ticker = row["ticker"].upper()
        if ticker in seen_tickers:
            continue
        seen_tickers.add(ticker)

        if not passes_opportunity_floor(row.get("opportunity_score")):
            skipped.append({"ticker": ticker, "reason": "Below opportunity floor"})
            continue

        quote = quotes.get(ticker)
        plan = _build_plan_for_candidate(
            row, deploy=deploy, net_target=net_target, quote=quote
        )
        if not plan or not plan.get("limit_buy_price"):
            skipped.append({"ticker": ticker, "reason": "Could not build trade plan"})
            continue

        risk = _evaluate_candidate_risk(
            conn,
            ticker=ticker,
            plan=plan,
            block_new_longs=block_new_longs,
            regime_summary=regime_summary,
        )

        entry = float(plan.get("limit_buy_price") or plan.get("entry_price"))
        target = float(plan.get("limit_sell_price") or plan.get("target_price"))
        stop = float(plan.get("stop_price"))
        shares = int(plan.get("shares") or 0)
        per_share_risk = max(entry - stop, 0)
        expected_rr = None
        if per_share_risk > 0:
            expected_rr = round((target - entry) / per_share_risk, 2)

        plan_payload = {
            **plan,
            "entry_mode": "pullback_limit",
            "notional": round(entry * shares, 2),
            "max_risk_dollars": round(per_share_risk * shares, 2),
            "expected_rr": expected_rr,
            "net_target": net_target,
            "target_pct": plan.get("target_pct")
            or round(target_move_pct(entry, target), 2),
        }

        enrichment = enrich_proposal(
            conn,
            ticker=ticker,
            session_date_et=day,
            row={**row, "opportunity_floor": OPPORTUNITY_FLOOR},
            plan=plan_payload,
            risk_headline=risk["headline"],
            settings=cfg,
        )

        factor_scores = finalize_proposal_factor_scores(
            row.get("factor_scores") or {},
            conn=conn,
            ticker=ticker,
            expected_rr=expected_rr,
            news_sentiment=enrichment.news_sentiment,
            ai_confidence=enrichment.ai_confidence if enrichment.ai_confidence > 0 else None,
        )
        opportunity_score, _weights = composite_opportunity_score(factor_scores)

        if not passes_opportunity_floor(opportunity_score):
            skipped.append({"ticker": ticker, "reason": "Below opportunity floor after AI factors"})
            continue

        if risk["verdict"] == "approved":
            status = STATUS_PROPOSED
            risk_reason = None
        else:
            status = STATUS_RISK_REJECTED
            risk_reason = risk["blockers"][0] if risk.get("blockers") else risk["headline"]

        proposal_id = _insert_proposal(
            conn,
            {
                "proposal_uuid": str(uuid.uuid4()),
                "strategy_version": STRATEGY_VERSION,
                "model_version": enrichment.model_version,
                "created_at": _utc_now(),
                "valid_until": _valid_until_iso(day),
                "session_date_et": day,
                "ticker": ticker,
                "direction": DIRECTION_LONG,
                "opportunity_score": float(opportunity_score),
                "factor_scores": {
                    k: (round(v, 1) if v is not None else None) for k, v in factor_scores.items()
                },
                "plan": plan_payload,
                "risk_verdict": risk["verdict"],
                "risk_checks": risk.get("checks") or [],
                "risk_rejection_reason": risk_reason,
                "explanation": enrichment.explanation,
                "explanation_short": enrichment.explanation_short,
                "status": status,
            },
        )
        proposal = get_proposal(conn, proposal_id)
        if proposal:
            if status == STATUS_PROPOSED:
                created.append(proposal)
            else:
                skipped.append({"ticker": ticker, "reason": risk_reason, "proposal_id": proposal_id})

    actionable = [p for p in created if p["status"] == STATUS_PROPOSED]
    return {
        "ok": True,
        "session_date_et": day,
        "generated": len(created),
        "actionable_count": len(actionable),
        "proposals": list_proposals_for_session(conn, day),
        "created": created,
        "skipped": skipped,
        "max_proposals": max_proposals,
    }


def refresh_proposal_risk(
    conn: sqlite3.Connection,
    proposal_id: int,
    settings: Settings | None = None,
) -> dict:
    """Refresh live quote and re-run Risk Engine before human approve."""
    proposal = get_proposal(conn, proposal_id)
    if not proposal:
        return {"ok": False, "error": "Proposal not found"}

    summary = build_dashboard_summary(conn)
    if settings and settings.finnhub_api_key:
        refresh_live_quotes(conn, settings)

    plan = proposal["plan"]
    risk = _evaluate_candidate_risk(
        conn,
        ticker=proposal["ticker"],
        plan=plan,
        block_new_longs=bool(summary.block_new_longs),
        regime_summary=summary.regime["summary"] if summary.regime else None,
    )

    new_status = proposal["status"]
    risk_reason = None
    if risk["verdict"] != "approved":
        new_status = STATUS_RISK_REJECTED
        risk_reason = risk["blockers"][0] if risk.get("blockers") else risk["headline"]
    elif proposal["status"] == STATUS_RISK_REJECTED:
        new_status = STATUS_PROPOSED

    conn.execute(
        """
        UPDATE trade_proposals
        SET risk_verdict = ?, risk_checks_json = ?, risk_rejection_reason = ?, status = ?
        WHERE id = ?
        """,
        (
            risk["verdict"],
            json.dumps(risk.get("checks") or []),
            risk_reason,
            new_status,
            proposal_id,
        ),
    )

    return {
        "ok": risk["verdict"] == "approved",
        "risk": risk,
        "proposal": get_proposal(conn, proposal_id),
        "live_refreshed": bool(settings and settings.finnhub_api_key),
    }


def approve_proposal(
    conn: sqlite3.Connection,
    proposal_id: int,
    *,
    settings: Settings | None = None,
    approved_by: str = "operator",
) -> dict:
    proposal = get_proposal(conn, proposal_id)
    if not proposal:
        return {"ok": False, "error": "Proposal not found"}
    if proposal["status"] not in (STATUS_PROPOSED, STATUS_RISK_REJECTED, STATUS_DRAFT):
        return {
            "ok": False,
            "error": f"Cannot approve proposal in status {proposal['status']}",
        }

    risk_result = refresh_proposal_risk(conn, proposal_id, settings)
    if not risk_result["ok"]:
        return {
            "ok": False,
            "error": "Risk Engine rejected on live refresh — not approved",
            "risk": risk_result.get("risk"),
            "proposal": risk_result.get("proposal"),
        }

    now = _utc_now()
    conn.execute(
        """
        UPDATE trade_proposals
        SET human_verdict = 'approved', human_approved_at = ?, status = ?, human_rejection_reason = NULL
        WHERE id = ?
        """,
        (now, STATUS_HUMAN_APPROVED, proposal_id),
    )
    updated = get_proposal(conn, proposal_id)
    return {
        "ok": True,
        "proposal": updated,
        "approved_by": approved_by,
        "risk": risk_result.get("risk"),
    }


def reject_proposal(
    conn: sqlite3.Connection,
    proposal_id: int,
    *,
    reason_code: str,
    reason_text: str | None = None,
) -> dict:
    code = reason_code.upper().strip()
    if code not in REJECTION_REASONS:
        return {"ok": False, "error": f"Invalid rejection reason: {reason_code}"}
    if code == "OTHER" and not (reason_text or "").strip():
        return {"ok": False, "error": "OTHER requires reason_text"}

    proposal = get_proposal(conn, proposal_id)
    if not proposal:
        return {"ok": False, "error": "Proposal not found"}
    if proposal["status"] in (STATUS_EXECUTED, STATUS_CLOSED, STATUS_HUMAN_APPROVED):
        return {"ok": False, "error": f"Cannot reject proposal in status {proposal['status']}"}

    label = REJECTION_REASONS[code]
    full_reason = f"{code}: {label}"
    if reason_text and reason_text.strip():
        full_reason = f"{full_reason} — {reason_text.strip()}"

    conn.execute(
        """
        UPDATE trade_proposals
        SET human_verdict = 'rejected', human_rejection_reason = ?, status = ?, human_approved_at = NULL
        WHERE id = ?
        """,
        (full_reason, STATUS_HUMAN_REJECTED, proposal_id),
    )
    return {"ok": True, "proposal": get_proposal(conn, proposal_id)}


def mark_proposal_executed(
    conn: sqlite3.Connection,
    proposal_id: int,
    journal_buy_id: int,
) -> dict:
    proposal = get_proposal(conn, proposal_id)
    if not proposal:
        return {"ok": False, "error": "Proposal not found"}
    if proposal["status"] != STATUS_HUMAN_APPROVED:
        return {
            "ok": False,
            "error": f"Proposal must be human_approved before journal BUY (status={proposal['status']})",
        }

    conn.execute(
        """
        UPDATE trade_proposals
        SET status = ?, journal_buy_id = ?
        WHERE id = ?
        """,
        (STATUS_EXECUTED, journal_buy_id, proposal_id),
    )
    return {"ok": True, "proposal": get_proposal(conn, proposal_id)}


def validate_journal_buy_proposal(
    conn: sqlite3.Connection,
    *,
    proposal_id: int,
    ticker: str,
    side: str,
) -> dict:
    if side.upper() != "BUY":
        return {"ok": True}
    proposal = get_proposal(conn, proposal_id)
    if not proposal:
        return {"ok": False, "error": "Proposal not found"}
    if proposal["ticker"].upper() != ticker.upper():
        return {"ok": False, "error": f"Ticker {ticker} does not match proposal {proposal['ticker']}"}
    if proposal["status"] != STATUS_HUMAN_APPROVED:
        return {
            "ok": False,
            "error": f"Proposal {proposal_id} is not human-approved (status={proposal['status']})",
        }
    return {"ok": True, "proposal": proposal}
