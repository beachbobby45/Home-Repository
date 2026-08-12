"""Three-step daily trading rhythm — status for dashboard."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary
from investment_agent.db import DEFAULT_DB_PATH
from investment_agent.monitor import get_latest_quotes
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.screen_actions import (
    ACTION_DAILY_INGEST,
    ACTION_PERIOD_SCREENER,
    get_screen_action_status,
)
from investment_agent.stock_team import build_analysis_card, _latest_metrics
from investment_agent.pullback_entry import compute_pullback_trade_plan
from investment_agent.trading_day import compute_trade_plan
from investment_agent.watchlist import compute_data_freshness

ET = ZoneInfo("America/New_York")
PT = ZoneInfo("America/Los_Angeles")
INGEST_LAST_RUN = DEFAULT_DB_PATH.parent / "ingest_last_run.json"
SCHEDULE_PLIST = Path.home() / "Library/LaunchAgents/com.investment-agent.ingest.plist"


def _parse_iso(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        ts = iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _same_calendar_day_pt(a: datetime | None, b: datetime | None) -> bool:
    if not a or not b:
        return False
    return a.astimezone(PT).date() == b.astimezone(PT).date()


def _read_last_ingest() -> dict | None:
    if not INGEST_LAST_RUN.is_file():
        return None
    try:
        return json.loads(INGEST_LAST_RUN.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def ingest_schedule_installed() -> bool:
    return SCHEDULE_PLIST.is_file()


def build_trading_candidates(
    conn: sqlite3.Connection,
    *,
    limit: int = 15,
    period_days: int = 14,
) -> list[dict]:
    """Top ranked names with buy size, sell target, and stop for pre-market review."""
    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or 0)
    net_target = float(summary.daily_target or 150)
    quotes = get_latest_quotes(conn)
    metrics = {r["ticker"]: r for r in _latest_metrics(conn)}
    ranked = build_ranked_candidates(conn, period_days=period_days).get("ranked", [])[:limit]

    rows: list[dict] = []
    for item in ranked:
        sym = item["ticker"]
        m = metrics.get(sym)
        session_open = (
            float(m["last_quote"] if m else 0)
            or float(m["last_close"] if m else 0)
            or float(quotes.get(sym) or 0)
        )
        avg_range = float(item.get("avg_range_pct") or (m["avg_range_pct"] if m else 0) or 0)
        card = build_analysis_card(m, deploy) if m else None
        size = float(card.suggested_size) if card else deploy
        if session_open and avg_range > 0:
            plan = compute_pullback_trade_plan(
                session_open=session_open,
                avg_range_pct=avg_range,
                deploy_dollar=size,
                net_target=net_target,
            )
        elif session_open:
            plan = compute_trade_plan(
                entry_price=session_open,
                deploy_dollar=size,
                net_target=net_target,
            )
        else:
            plan = {}
        rows.append(
            {
                "ticker": sym,
                "score": item.get("score"),
                "hit_rate_pct": item.get("hit_rate_pct"),
                "dollar_hit_rate_pct": item.get("dollar_hit_rate_pct"),
                "live_pass_today": item.get("live_pass_today"),
                "session_open": plan.get("session_open"),
                "limit_buy_price": plan.get("limit_buy_price"),
                "limit_sell_price": plan.get("limit_sell_price") or plan.get("target_price"),
                "limit_fill_deadline_et": plan.get("limit_fill_deadline_et"),
                "entry_price": plan.get("limit_buy_price") or plan.get("entry_price"),
                "recommended_shares": plan.get("shares"),
                "suggested_size": round(size, 0),
                "target_price": plan.get("target_price"),
                "stop_price": plan.get("stop_price"),
                "net_target": plan.get("net_target"),
                "pullback_pct": plan.get("pullback_pct"),
                "step3_pass": card is not None,
            }
        )
    return rows


def get_daily_rhythm_status(conn: sqlite3.Connection) -> dict:
    """Status for the 3-step daily workflow shown on Trade / Screen tabs."""
    now = datetime.now(timezone.utc)
    fresh = compute_data_freshness(conn)
    actions = get_screen_action_status(conn)
    last_ingest = _read_last_ingest() or {}

    ingest_action = actions.get(ACTION_DAILY_INGEST, {})
    screener_action = actions.get(ACTION_PERIOD_SCREENER, {})

    ingest_at = _parse_iso(last_ingest.get("finished_at")) or _parse_iso(
        ingest_action.get("completed_at")
    )
    screener_at = _parse_iso(screener_action.get("completed_at"))
    quote_age = fresh.get("quotes_max_age_hours")
    metric_age = fresh.get("metrics_max_age_hours")

    # Step 1 — after close: quotes fresh enough for overnight / next morning
    step1_state = "needed"
    if quote_age is not None and quote_age <= 8 and (metric_age or 999) <= 36:
        step1_state = "ready"
    elif quote_age is not None and quote_age <= 16:
        step1_state = "ok"

    step1_detail = "Pulls Range, ADV, and Step 3 metrics for your watchlist."
    if ingest_schedule_installed():
        step1_detail += " Auto-refresh runs at 4:30 PM and 6:30 AM (Mac local time)."
    else:
        step1_detail += " Enable auto-refresh once in Setup, or double-click Run After-Close Ingest.command."

    # Step 2 — pre-market: screener run today with fresh data
    step2_state = "needed"
    if screener_at and _same_calendar_day_pt(screener_at, now):
        if step1_state in ("ready", "ok") or (ingest_at and screener_at >= ingest_at):
            step2_state = "ready"
        else:
            step2_state = "ok"
    elif screener_at:
        step2_state = "stale"

    # Step 3 — intraday: always available via Refresh live
    step3_state = "ready"
    step3_detail = "Right before you buy in E*TRADE, refresh live prices and validate the symbol."

    return {
        "schedule_installed": ingest_schedule_installed(),
        "freshness": fresh,
        "last_ingest": {
            "finished_at": last_ingest.get("finished_at"),
            "mode": last_ingest.get("mode"),
            "quotes_refreshed": last_ingest.get("quotes_refreshed"),
            "bars_refreshed": last_ingest.get("bars_refreshed"),
        },
        "steps": [
            {
                "id": "after_close",
                "number": 1,
                "title": "After market close",
                "subtitle": "Refresh stock metrics",
                "state": step1_state,
                "last_at": ingest_at.isoformat() if ingest_at else None,
                "detail": step1_detail,
                "manual": "Double-click: scripts/Run After-Close Ingest.command",
            },
            {
                "id": "pre_market",
                "number": 2,
                "title": "Before trading starts",
                "subtitle": "Rank candidates · size · sell · stop",
                "state": step2_state,
                "last_at": screener_at.isoformat() if screener_at else None,
                "detail": "Runs the 14-day screener and fills in buy size, sell target, and stop loss per stock on the Trade tab.",
                "browser_action": "prepare_morning",
            },
            {
                "id": "before_buy",
                "number": 3,
                "title": "Right before you buy",
                "subtitle": "Confirm live prices",
                "state": step3_state,
                "last_at": None,
                "detail": step3_detail,
                "browser_action": "refresh_live",
            },
        ],
    }
