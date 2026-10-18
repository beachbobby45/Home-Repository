"""Run one paper session tick: settle cash, propose/arm, dual-arm 5m sim, log."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.account import get_day_gate_mode
from investment_agent.backtest import _group_bars_by_date
from investment_agent.execution.armed_plan import PlanStatus, set_armed_plan_status
from investment_agent.execution.paper_ledger import (
    ACCOUNT_ALL,
    ACCOUNT_GATE,
    PAPER_ACCOUNTS,
    PAPER_STARTING_CASH,
    apply_round_trip,
    ensure_paper_accounts,
    get_paper_balance,
    get_session_log,
    paper_scoreboard,
    settle_due_cash,
    upsert_session_log,
)
from investment_agent.execution.paper_sim import simulate_round_trip_5m
from investment_agent.execution.pdt_guard import can_open_day_trade, record_day_trade
from investment_agent.execution.propose import propose_armed_plan
from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE
from investment_agent.providers.yfinance_bars import get_intraday_bars
from investment_agent.risk_engine import is_kill_switch_active
from investment_agent.trading_day import today_et_str

ET = ZoneInfo("America/New_York")


def _resize_shares_for_cash(deploy_target: float, limit_buy: float, settled: float) -> tuple[int, float]:
    """Shares affordable from settled cash after buy fee."""
    budget = min(deploy_target, settled) - DEFAULT_BUY_FEE
    if budget <= 0 or limit_buy <= 0:
        return 0, 0.0
    shares = int(budget / limit_buy)
    deploy = shares * limit_buy + DEFAULT_BUY_FEE if shares else 0.0
    return shares, deploy


def _plan_signal(conn: sqlite3.Connection, session_date_et: str) -> dict[str, Any]:
    proposed = propose_armed_plan(conn, session_date_et=session_date_et, replace_existing=True)
    if not proposed.get("ok"):
        return {
            "ok": False,
            "error": proposed.get("error"),
            "session_date_et": session_date_et,
        }
    plan = proposed["plan"]
    # Auto-arm for paper when ops slot free (no human veto in paper mode)
    pdt = proposed.get("pdt") or {}
    if pdt.get("allowed") and plan.get("status") == PlanStatus.PROPOSED.value:
        set_armed_plan_status(conn, plan["plan_uuid"], PlanStatus.ARMED)
        plan["status"] = PlanStatus.ARMED.value
    leg = (plan.get("legs") or [{}])[0]
    return {
        "ok": True,
        "session_date_et": session_date_et,
        "plan": plan,
        "pdt": pdt,
        "ticker": leg.get("ticker"),
        "limit_buy": leg.get("limit_buy"),
        "limit_sell": leg.get("limit_sell"),
        "stop": leg.get("stop"),
        "shares": leg.get("shares"),
        "deploy": leg.get("deploy"),
        "allow_trade": plan.get("allow_trade"),
        "ma_score": plan.get("ma_score"),
        "day_gate_mode": plan.get("day_gate_mode") or get_day_gate_mode(conn),
    }


def _fetch_day_bars(ticker: str, session_date_et: str, *, lookback_days: int = 10) -> list[dict]:
    try:
        raw = get_intraday_bars(ticker, lookback_days=lookback_days, interval="5m")
    except Exception as exc:  # noqa: BLE001
        return []
    by_date = _group_bars_by_date(raw)
    return list(by_date.get(session_date_et[:10], []))


def _process_arm(
    conn: sqlite3.Connection,
    *,
    account_name: str,
    signal: dict[str, Any],
    day_bars: list[dict],
    as_of_et: datetime | None,
    force_complete: bool,
) -> dict[str, Any]:
    day = signal["session_date_et"][:10]
    existing = get_session_log(conn, day, account_name)
    if existing and existing.get("status") in {"complete", "skipped_gate", "skipped_cap", "skipped_cash", "no_signal"}:
        return {"account_name": account_name, "skipped": True, "reason": "already_final", "log": existing}

    settle_due_cash(conn, session_date_et=day, account_name=account_name)
    bal = get_paper_balance(conn, account_name)
    allow = signal.get("allow_trade")
    ticker = signal.get("ticker")

    base = {
        "session_date_et": day,
        "account_name": account_name,
        "ticker": ticker,
        "allow_trade": allow,
        "ma_score": signal.get("ma_score"),
        "day_gate_mode": signal.get("day_gate_mode"),
        "settled_cash_before": float(bal["settled_cash"]),
    }

    if not ticker or signal.get("limit_buy") is None:
        row = {
            **base,
            "status": "no_signal",
            "scenario": "no_top_pick",
            "filled": False,
            "net_pnl": 0.0,
            "settled_cash_after": float(bal["settled_cash"]),
            "equity_after": float(bal["equity"]),
            "detail": signal.get("error") or "No tradeable signal",
        }
        upsert_session_log(conn, row)
        return {"account_name": account_name, "log": row}

    if account_name == ACCOUNT_GATE and allow is False:
        row = {
            **base,
            "status": "skipped_gate",
            "scenario": "gate_blocked",
            "filled": False,
            "net_pnl": 0.0,
            "settled_cash_after": float(bal["settled_cash"]),
            "equity_after": float(bal["equity"]),
            "detail": "allow_trade=false — gate_approved book skips",
        }
        upsert_session_log(conn, row)
        return {"account_name": account_name, "log": row}

    if account_name == ACCOUNT_GATE:
        gate = can_open_day_trade(conn, equity=float(bal["equity"]), session_date=day)
        if not gate["allowed"]:
            row = {
                **base,
                "status": "skipped_cap",
                "scenario": gate.get("reason"),
                "filled": False,
                "net_pnl": 0.0,
                "settled_cash_after": float(bal["settled_cash"]),
                "equity_after": float(bal["equity"]),
                "detail": f"Ops gate: {gate.get('reason')} ({gate['used']}/{gate['cap']})",
            }
            upsert_session_log(conn, row)
            return {"account_name": account_name, "log": row}

    shares, deploy = _resize_shares_for_cash(
        float(signal.get("deploy") or 0),
        float(signal["limit_buy"]),
        float(bal["settled_cash"]),
    )
    if shares < 1:
        row = {
            **base,
            "status": "skipped_cash",
            "scenario": "insufficient_settled",
            "filled": False,
            "shares": 0,
            "deploy": deploy,
            "net_pnl": 0.0,
            "settled_cash_after": float(bal["settled_cash"]),
            "equity_after": float(bal["equity"]),
            "detail": f"Settled ${bal['settled_cash']:.2f} cannot fund a share",
        }
        upsert_session_log(conn, row)
        return {"account_name": account_name, "log": row}

    sim_as_of = None if force_complete else as_of_et
    sim = simulate_round_trip_5m(
        day_bars,
        buy=float(signal["limit_buy"]),
        sell=float(signal["limit_sell"]),
        stop=float(signal["stop"]),
        shares=shares,
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
        as_of_et=sim_as_of,
    )

    if not sim.get("complete"):
        row = {
            **base,
            "status": "in_progress",
            "scenario": sim.get("scenario"),
            "filled": bool(sim.get("filled")),
            "fill_ts": sim.get("fill_ts"),
            "entry_price": sim.get("entry_price") or float(signal["limit_buy"]),
            "shares": shares,
            "deploy": deploy,
            "detail": sim.get("detail"),
            "settled_cash_after": float(bal["settled_cash"]),
            "equity_after": float(bal["equity"]),
            "payload_json": sim,
        }
        upsert_session_log(conn, row)
        return {"account_name": account_name, "log": row, "in_progress": True}

    if not sim.get("filled"):
        row = {
            **base,
            "status": "complete",
            "scenario": sim.get("scenario"),
            "filled": False,
            "shares": shares,
            "deploy": deploy,
            "net_pnl": float(sim.get("net_pnl") or 0.0),
            "settled_cash_after": float(bal["settled_cash"]),
            "equity_after": float(bal["equity"]),
            "detail": sim.get("detail"),
            "payload_json": sim,
        }
        upsert_session_log(conn, row)
        return {"account_name": account_name, "log": row}

    # Apply round trip once (idempotent: skip if already complete with fill)
    if existing and existing.get("filled") and existing.get("status") == "complete":
        return {"account_name": account_name, "skipped": True, "reason": "already_filled", "log": existing}

    applied = apply_round_trip(
        conn,
        account_name=account_name,
        session_date_et=day,
        ticker=str(ticker),
        shares=shares,
        entry_price=float(sim["entry_price"]),
        exit_price=float(sim["exit_price"]),
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
        fill_ts=sim.get("fill_ts"),
        exit_ts=sim.get("exit_ts"),
    )
    # Record day trade once per session (gate book owns the ops counter)
    if account_name == ACCOUNT_GATE:
        try:
            record_day_trade(
                conn,
                session_date_et=day,
                ticker=str(ticker),
                equity_at_trade=float(applied["equity_after"]),
                notes="paper_gate_approved",
            )
        except ValueError:
            pass

    row = {
        **base,
        "status": "complete",
        "scenario": sim.get("scenario"),
        "filled": True,
        "fill_ts": sim.get("fill_ts"),
        "exit_ts": sim.get("exit_ts"),
        "exit_reason": sim.get("exit_reason"),
        "entry_price": float(sim["entry_price"]),
        "exit_price": float(sim["exit_price"]),
        "shares": shares,
        "deploy": deploy,
        "net_pnl": applied["net_pnl"],
        "settled_cash_after": applied["settled_after"],
        "equity_after": applied["equity_after"],
        "detail": sim.get("detail"),
        "payload_json": {**sim, "ledger": applied},
    }
    upsert_session_log(conn, row)
    return {"account_name": account_name, "log": row, "applied": applied}


def run_paper_tick(
    conn: sqlite3.Connection,
    *,
    session_date_et: str | None = None,
    starting_cash: float = PAPER_STARTING_CASH,
    force_complete: bool = False,
    lookback_days: int = 10,
) -> dict[str, Any]:
    """One worker cycle for the paper books."""
    ensure_paper_accounts(conn, starting_cash=starting_cash)
    day = (session_date_et or today_et_str())[:10]
    settle_due_cash(conn, session_date_et=day)

    if is_kill_switch_active(conn):
        return {
            "ok": False,
            "session_date_et": day,
            "error": "kill_switch_active",
            "balances": {n: get_paper_balance(conn, n) for n in PAPER_ACCOUNTS},
        }

    signal = _plan_signal(conn, day)
    as_of = datetime.now(ET)
    day_bars: list[dict] = []
    if signal.get("ok") and signal.get("ticker"):
        day_bars = _fetch_day_bars(str(signal["ticker"]), day, lookback_days=lookback_days)

    results = []
    for name in PAPER_ACCOUNTS:
        if not signal.get("ok"):
            row = {
                "session_date_et": day,
                "account_name": name,
                "status": "no_signal",
                "scenario": "propose_failed",
                "filled": False,
                "net_pnl": 0.0,
                "detail": signal.get("error"),
                "settled_cash_before": get_paper_balance(conn, name)["settled_cash"],
                "settled_cash_after": get_paper_balance(conn, name)["settled_cash"],
                "equity_after": get_paper_balance(conn, name)["equity"],
            }
            upsert_session_log(conn, row)
            results.append({"account_name": name, "log": row})
            continue
        results.append(
            _process_arm(
                conn,
                account_name=name,
                signal=signal,
                day_bars=day_bars,
                as_of_et=as_of,
                force_complete=force_complete,
            )
        )

    return {
        "ok": True,
        "session_date_et": day,
        "signal": {
            "ticker": signal.get("ticker"),
            "allow_trade": signal.get("allow_trade"),
            "ma_score": signal.get("ma_score"),
            "error": signal.get("error"),
        },
        "arms": results,
        "balances": {n: get_paper_balance(conn, n) for n in PAPER_ACCOUNTS},
        "scoreboard": paper_scoreboard(conn),
    }


def paper_status_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    ensure_paper_accounts(conn)
    day = today_et_str()
    return {
        "ok": True,
        "execution_mode": "paper",
        "session_date_et": day,
        "balances": {n: get_paper_balance(conn, n) for n in PAPER_ACCOUNTS},
        "today": {
            n: get_session_log(conn, day, n) for n in PAPER_ACCOUNTS
        },
        "scoreboard": paper_scoreboard(conn),
        "kill_switch_active": is_kill_switch_active(conn),
    }
