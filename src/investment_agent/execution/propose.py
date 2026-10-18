"""Build ArmedPlan proposals from today's ranking / trading-day panel."""

from __future__ import annotations

import sqlite3
from typing import Any

from investment_agent.account import build_dashboard_summary, get_day_gate_mode
from investment_agent.execution.armed_plan import (
    AllocationMode,
    ArmedLeg,
    ArmedPlan,
    PlanStatus,
    get_armed_plan_for_session,
    save_armed_plan,
)
from investment_agent.execution.pdt_guard import can_open_day_trade
from investment_agent.broker.sync import latest_broker_balance
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE_LABEL
from investment_agent.trading_day import build_trading_day_status, today_et_str


ALLOCATION_MODE_KEY = "allocation_mode"


def get_allocation_mode(conn: sqlite3.Connection) -> AllocationMode:
    from investment_agent.account import get_setting

    raw = get_setting(conn, ALLOCATION_MODE_KEY, AllocationMode.SINGLE_TOP1.value)
    try:
        return AllocationMode(raw)
    except ValueError:
        return AllocationMode.SINGLE_TOP1


def resolve_equity_for_pdt(conn: sqlite3.Connection) -> float:
    """Prefer latest Robinhood mirror equity; fall back to dashboard tradable cash."""
    bal = latest_broker_balance(conn)
    if bal and bal.get("equity") is not None:
        return float(bal["equity"])
    summary = build_dashboard_summary(conn)
    return float(summary.tradable_cash or 0)


def propose_armed_plan(
    conn: sqlite3.Connection,
    *,
    session_date_et: str | None = None,
    replace_existing: bool = True,
) -> dict[str, Any]:
    """Create a proposed ArmedPlan for #1 (single_top1). No broker submit."""
    day = session_date_et or today_et_str()
    mode = get_allocation_mode(conn)
    if mode != AllocationMode.SINGLE_TOP1:
        return {
            "ok": False,
            "error": (
                f"allocation_mode={mode.value} not enabled yet — "
                "complete Top2 backtest before dual_lot_top2"
            ),
        }

    existing = get_armed_plan_for_session(conn, day)
    if existing and existing.status.value not in ("cancelled", "expired", "rejected") and not replace_existing:
        return {
            "ok": True,
            "replaced": False,
            "plan": existing.to_payload(),
            "pdt": can_open_day_trade(conn, equity=resolve_equity_for_pdt(conn), session_date=day),
        }

    status = build_trading_day_status(conn)
    pick = status.get("top_pick") or {}
    ticker = (pick.get("ticker") or "").upper()
    if not ticker:
        return {"ok": False, "error": "No top pick available to propose"}

    buy = pick.get("limit_buy_price") or pick.get("recommended_entry") or pick.get("entry_price")
    sell = pick.get("limit_sell_price") or pick.get("target_price")
    stop = pick.get("stop_price")
    shares = pick.get("recommended_shares") or pick.get("shares")
    if not buy or not sell or not stop or not shares:
        return {
            "ok": False,
            "error": "Top pick missing limit buy / sell / stop / shares — refresh trading day first",
            "ticker": ticker,
        }

    equity = resolve_equity_for_pdt(conn)
    pdt = can_open_day_trade(conn, equity=equity, session_date=day)
    summary = build_dashboard_summary(conn)
    deploy = float(pick.get("notional") or pick.get("deploy") or summary.tradable_cash or 0)

    ma = status.get("market_activity") or {}
    leg = ArmedLeg(
        rank=1,
        ticker=ticker,
        limit_buy=float(buy),
        limit_sell=float(sell),
        stop=float(stop),
        shares=int(shares),
        deploy=deploy,
        avg_range_pct=float(pick["avg_range_pct"]) if pick.get("avg_range_pct") is not None else None,
    )
    plan = ArmedPlan(
        session_date_et=day,
        allocation_mode=mode,
        status=PlanStatus.PROPOSED,
        legs=[leg],
        day_gate_mode=get_day_gate_mode(conn),
        allow_trade=bool(ma.get("allow_trade")) if ma else status.get("allow_trade"),
        ma_score=ma.get("score"),
        equity_snapshot=equity,
        pdt_cap=pdt["cap"],
        pdt_used=pdt["used"],
        arm_deadline_et="09:25",
        fill_deadline_et=LIMIT_FILL_DEADLINE_LABEL.replace(" ET", ""),
        notes=(
            None
            if pdt["allowed"]
            else f"PDT blocked: {pdt.get('reason')} — propose saved for review only"
        ),
    )
    # Reuse uuid if replacing same-session proposed plan
    if existing and replace_existing:
        plan.plan_uuid = existing.plan_uuid
        plan.id = existing.id

    save_armed_plan(conn, plan)
    return {
        "ok": True,
        "replaced": bool(existing),
        "plan": plan.to_payload(),
        "pdt": pdt,
        "trading_paused_hint": not pdt["allowed"],
    }


def pdt_status_payload(conn: sqlite3.Connection, session_date_et: str | None = None) -> dict[str, Any]:
    day = session_date_et or today_et_str()
    equity = resolve_equity_for_pdt(conn)
    gate = can_open_day_trade(conn, equity=equity, session_date=day)
    bal = latest_broker_balance(conn)
    return {
        "session_date_et": day,
        "equity_source": "broker_balances" if bal else "dashboard_summary",
        "equity": equity,
        "broker_balance": {
            "equity": bal.get("equity"),
            "cash": bal.get("cash"),
            "captured_at": bal.get("captured_at"),
            "external_account_id": bal.get("external_account_id"),
        }
        if bal
        else None,
        "allocation_mode": get_allocation_mode(conn).value,
        **gate,
    }
