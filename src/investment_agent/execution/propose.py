"""Build ArmedPlan proposals from today's ranking / trading-day panel."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary, get_day_gate_mode, get_setting
from investment_agent.backtest import _group_bars_by_date
from investment_agent.db import get_ohlcv_bars
from investment_agent.execution.armed_plan import (
    AllocationMode,
    ArmedLeg,
    ArmedPlan,
    PlanStatus,
    get_armed_plan_for_session,
    save_armed_plan,
)
from investment_agent.execution.pdt_guard import can_open_day_trade
from investment_agent.execution.tradable_now import TOP_N, select_best_tradable
from investment_agent.broker.sync import latest_broker_balance
from investment_agent.providers.yfinance_bars import get_intraday_bars
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE_LABEL
from investment_agent.trading_day import (
    build_trading_day_status,
    resolve_actionable_picks,
    today_et_str,
)

ET = ZoneInfo("America/New_York")

ALLOCATION_MODE_KEY = "allocation_mode"
# Paper default: best of top-3 soft score (Tony 2026-10-22).
DEFAULT_ALLOCATION_MODE = AllocationMode.BEST_TRADABLE_TOP3


def get_allocation_mode(conn: sqlite3.Connection) -> AllocationMode:
    raw = get_setting(conn, ALLOCATION_MODE_KEY, DEFAULT_ALLOCATION_MODE.value)
    try:
        return AllocationMode(raw)
    except ValueError:
        return DEFAULT_ALLOCATION_MODE


def resolve_equity_for_pdt(conn: sqlite3.Connection) -> float:
    """Prefer latest Robinhood mirror equity; fall back to dashboard tradable cash."""
    bal = latest_broker_balance(conn)
    if bal and bal.get("equity") is not None:
        return float(bal["equity"])
    summary = build_dashboard_summary(conn)
    return float(summary.tradable_cash or 0)


def _leg_from_pick(pick: dict[str, Any], *, rank: int, deploy_fallback: float) -> ArmedLeg | None:
    ticker = (pick.get("ticker") or "").upper()
    buy = pick.get("limit_buy_price") or pick.get("limit_buy") or pick.get("recommended_entry")
    sell = pick.get("limit_sell_price") or pick.get("limit_sell") or pick.get("target_price")
    stop = pick.get("stop_price") or pick.get("stop")
    shares = pick.get("recommended_shares") or pick.get("shares")
    if not ticker or buy is None or sell is None or stop is None or shares is None:
        return None
    deploy = float(pick.get("notional") or pick.get("deploy") or deploy_fallback or 0)
    return ArmedLeg(
        rank=rank,
        ticker=ticker,
        limit_buy=float(buy),
        limit_sell=float(sell),
        stop=float(stop),
        shares=int(shares),
        deploy=deploy,
        avg_range_pct=float(pick["avg_range_pct"]) if pick.get("avg_range_pct") is not None else None,
    )


def _daily_bars_for(conn: sqlite3.Connection, ticker: str, *, limit: int = 45) -> list[dict]:
    rows = get_ohlcv_bars(conn, ticker, limit=limit)
    return [dict(r) for r in rows]


def _session_5m_bars(ticker: str, session_date_et: str, *, lookback_days: int = 10) -> list[dict]:
    try:
        raw = get_intraday_bars(ticker, lookback_days=lookback_days, interval="5m")
    except Exception:  # noqa: BLE001 — scorer tolerates missing bars
        return []
    by_date = _group_bars_by_date(raw)
    return list(by_date.get(session_date_et[:10], []))


def _top_candidates_from_status(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Prefer explicit top_pick + second_pick; pad from status if present."""
    out: list[dict[str, Any]] = []
    for key in ("top_pick", "second_pick"):
        pick = status.get(key)
        if pick and pick.get("ticker"):
            row = dict(pick)
            row.setdefault("prep_rank", len(out) + 1)
            out.append(row)
    return out


def collect_propose_candidates(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    limit: int = TOP_N,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build up to `limit` tradable candidates with limit/stop/shares for scoring."""
    status = build_trading_day_status(conn)
    from_status = _top_candidates_from_status(status)
    if len(from_status) >= limit:
        return from_status[:limit], status

    # Fall back: re-resolve actionable picks (covers #3 when status only has #1/#2).
    summary = build_dashboard_summary(conn)
    day = session_date_et[:10]
    from investment_agent.regime import REGIME_SYMBOLS
    from investment_agent.trading_day import (
        _latest_quote_rows,
        _live_ranked_candidates,
        compute_today_realized_net,
    )

    watch = list(REGIME_SYMBOLS)
    for row in _live_ranked_candidates(conn):
        watch.append(row["ticker"])
    quotes = _latest_quote_rows(conn, watch)
    today_net = compute_today_realized_net(conn, day)
    remaining = max(float(summary.daily_target) - today_net, 0)
    net_for_plan = remaining or float(summary.daily_target)

    selected, _skipped = resolve_actionable_picks(
        conn,
        quotes=quotes,
        deploy=float(summary.tradable_cash or 0),
        net_target=net_for_plan,
        block_new_longs=bool(summary.block_new_longs),
        limit=limit,
    )
    if selected:
        return selected, status
    return from_status[:limit], status


def propose_armed_plan(
    conn: sqlite3.Connection,
    *,
    session_date_et: str | None = None,
    replace_existing: bool = True,
    persist: bool = True,
    allocation_mode: AllocationMode | str | None = None,
    as_of_et: datetime | None = None,
    bars_5m_by_ticker: dict[str, list[dict]] | None = None,
    daily_by_ticker: dict[str, list[dict]] | None = None,
) -> dict[str, Any]:
    """Create a proposed ArmedPlan. No broker submit.

    Modes:
      - best_tradable_top3 (default): soft-score top-3, arm the winner
      - single_top1: arm prep/actionable #1 only (shadow book)
      - dual_lot_top2: not enabled

    Set persist=False for shadow/counterfactual proposes that must not
    overwrite the session's stored armed plan.
    """
    day = session_date_et or today_et_str()
    if allocation_mode is None:
        mode = get_allocation_mode(conn)
    elif isinstance(allocation_mode, AllocationMode):
        mode = allocation_mode
    else:
        try:
            mode = AllocationMode(str(allocation_mode))
        except ValueError:
            return {"ok": False, "error": f"Unknown allocation_mode={allocation_mode}"}

    if mode == AllocationMode.DUAL_LOT_TOP2:
        return {
            "ok": False,
            "error": (
                f"allocation_mode={mode.value} not enabled yet — "
                "complete Top2 backtest before dual_lot_top2"
            ),
        }

    existing = get_armed_plan_for_session(conn, day) if persist else None
    if (
        persist
        and existing
        and existing.status.value not in ("cancelled", "expired", "rejected")
        and not replace_existing
    ):
        return {
            "ok": True,
            "replaced": False,
            "plan": existing.to_payload(),
            "pdt": can_open_day_trade(conn, equity=resolve_equity_for_pdt(conn), session_date=day),
        }

    equity = resolve_equity_for_pdt(conn)
    pdt = can_open_day_trade(conn, equity=equity, session_date=day)
    summary = build_dashboard_summary(conn)
    deploy_fallback = float(summary.tradable_cash or 0)

    selection_audit: dict[str, Any] | None = None
    leg: ArmedLeg | None = None
    status: dict[str, Any]

    if mode == AllocationMode.SINGLE_TOP1:
        status = build_trading_day_status(conn)
        pick = status.get("top_pick") or {}
        leg = _leg_from_pick(pick, rank=1, deploy_fallback=deploy_fallback)
        if leg is None:
            return {"ok": False, "error": "No top pick available to propose"}
        selection_audit = {
            "mode": mode.value,
            "reason": f"single_top1 → {leg.ticker}",
            "winner": {"ticker": leg.ticker, "rank": 1},
            "scored": [],
        }
    else:
        # best_tradable_top3
        candidates, status = collect_propose_candidates(conn, session_date_et=day, limit=TOP_N)
        if not candidates:
            return {"ok": False, "error": "No top pick available to propose"}

        bars_map: dict[str, list[dict]] = dict(bars_5m_by_ticker or {})
        daily_map: dict[str, list[dict]] = dict(daily_by_ticker or {})
        for c in candidates:
            ticker = str(c.get("ticker") or "").upper()
            if not ticker:
                continue
            if ticker not in bars_map:
                bars_map[ticker] = _session_5m_bars(ticker, day)
            if ticker not in daily_map:
                daily_map[ticker] = _daily_bars_for(conn, ticker)

        when = as_of_et or datetime.now(ET)
        selection = select_best_tradable(
            candidates,
            bars_5m_by_ticker=bars_map,
            daily_by_ticker=daily_map,
            as_of_et=when,
            top_n=TOP_N,
        )
        selection_audit = selection.to_dict()
        if selection.winner is None:
            # Fall back to first candidate with complete levels (soft path never empty if candidates ok)
            leg = _leg_from_pick(candidates[0], rank=1, deploy_fallback=deploy_fallback)
            if leg is None:
                return {
                    "ok": False,
                    "error": selection.reason or "No tradeable signal among top-3",
                }
        else:
            w = selection.winner
            leg = ArmedLeg(
                rank=w.rank,
                ticker=w.ticker,
                limit_buy=w.limit_buy,
                limit_sell=w.limit_sell,
                stop=w.stop,
                shares=w.shares,
                deploy=w.deploy or deploy_fallback,
                avg_range_pct=w.avg_range_pct,
            )

    assert leg is not None
    ma = status.get("market_activity") or {}
    notes = selection_audit.get("reason") if selection_audit else None
    if not pdt["allowed"]:
        blocked = f"PDT blocked: {pdt.get('reason')} — propose saved for review only"
        notes = f"{notes} · {blocked}" if notes else blocked

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
        notes=notes,
        selection_audit=selection_audit,
    )
    if persist and existing and replace_existing:
        plan.plan_uuid = existing.plan_uuid
        plan.id = existing.id

    if persist:
        save_armed_plan(conn, plan)
    return {
        "ok": True,
        "replaced": bool(existing) if persist else False,
        "persisted": persist,
        "plan": plan.to_payload(),
        "pdt": pdt,
        "selection": selection_audit,
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
