"""Run one paper session tick: settle cash, propose/arm, dual-arm 5m sim, log."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.account import get_day_gate_mode
from investment_agent.backtest import _group_bars_by_date
from investment_agent.execution.armed_plan import AllocationMode, PlanStatus, set_armed_plan_status
from investment_agent.execution.ops_audit import (
    LEDGER_SOURCE_PAPER,
    get_ledger_source,
    log_paper_day_complete,
    set_ledger_source,
)
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
from investment_agent.execution.paper_sim import resolve_fill_mode, simulate_round_trip_5m
from investment_agent.execution.pdt_guard import can_open_day_trade, record_day_trade
from investment_agent.execution.propose import get_allocation_mode, propose_armed_plan
from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE
from investment_agent.notify import notify_paper_buy, notify_paper_sell
from investment_agent.providers.yfinance_bars import get_intraday_bars
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE
from investment_agent.risk_engine import is_kill_switch_active
from investment_agent.trading_day import today_et_str

ET = ZoneInfo("America/New_York")

# Terminal day outcomes (do not reopen).
_FINAL_STATUSES = frozenset(
    {"complete", "skipped_gate", "skipped_cap", "skipped_cash", "no_signal"}
)
# Soft holding state while morning prep / ranks are still catching up.
_WAITING_SIGNAL = "waiting_signal"
_PROPOSE_FAILED = "propose_failed"


def _before_fill_deadline(as_of_et: datetime | None) -> bool:
    now = as_of_et or datetime.now(ET)
    if now.tzinfo is None:
        now = now.replace(tzinfo=ET)
    else:
        now = now.astimezone(ET)
    return now.timetz().replace(tzinfo=None) <= LIMIT_FILL_DEADLINE


def _is_retryable_no_signal(existing: dict[str, Any] | None) -> bool:
    """True when an early propose miss should be retried after prep catches up."""
    if not existing:
        return False
    status = existing.get("status")
    if status == _WAITING_SIGNAL:
        return True
    if status != "no_signal":
        return False
    scenario = (existing.get("scenario") or "").strip()
    detail = (existing.get("detail") or "").lower()
    return scenario in {_PROPOSE_FAILED, "no_top_pick"} or "no top pick" in detail


def _session_already_final(
    existing: dict[str, Any] | None,
    *,
    signal_ok: bool,
    as_of_et: datetime | None,
    force_complete: bool,
) -> bool:
    """Block re-entry only for true finals — not premature no_signal before deadline."""
    if not existing:
        return False
    status = existing.get("status")
    if status == _WAITING_SIGNAL:
        return False
    if status not in _FINAL_STATUSES:
        return False
    # Early propose failures must not lock the day before 11:30 ET when a pick appears later.
    if (
        _is_retryable_no_signal(existing)
        and signal_ok
        and (force_complete or _before_fill_deadline(as_of_et))
    ):
        return False
    return True


def _resize_shares_for_cash(deploy_target: float, limit_buy: float, settled: float) -> tuple[int, float]:
    """Shares affordable from settled cash after buy fee."""
    budget = min(deploy_target, settled) - DEFAULT_BUY_FEE
    if budget <= 0 or limit_buy <= 0:
        return 0, 0.0
    shares = int(budget / limit_buy)
    deploy = shares * limit_buy + DEFAULT_BUY_FEE if shares else 0.0
    return shares, deploy


def _plan_signal(
    conn: sqlite3.Connection,
    session_date_et: str,
    *,
    allocation_mode: AllocationMode | str | None = None,
    persist_plan: bool = True,
    as_of_et: datetime | None = None,
    bars_5m_by_ticker: dict[str, list[dict]] | None = None,
) -> dict[str, Any]:
    proposed = propose_armed_plan(
        conn,
        session_date_et=session_date_et,
        replace_existing=True,
        persist=persist_plan,
        allocation_mode=allocation_mode,
        as_of_et=as_of_et,
        bars_5m_by_ticker=bars_5m_by_ticker,
    )
    if not proposed.get("ok"):
        return {
            "ok": False,
            "error": proposed.get("error"),
            "session_date_et": session_date_et,
            "allocation_mode": (
                allocation_mode.value
                if isinstance(allocation_mode, AllocationMode)
                else allocation_mode
            ),
            "selection": proposed.get("selection"),
        }
    plan = proposed["plan"]
    # Auto-arm for paper when ops slot free (no human veto in paper mode)
    pdt = proposed.get("pdt") or {}
    if (
        persist_plan
        and pdt.get("allowed")
        and plan.get("status") == PlanStatus.PROPOSED.value
    ):
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
        "allocation_mode": plan.get("allocation_mode"),
        "selection": proposed.get("selection") or plan.get("selection_audit"),
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
    if _session_already_final(
        existing,
        signal_ok=bool(signal.get("ticker") and signal.get("limit_buy") is not None),
        as_of_et=as_of_et,
        force_complete=force_complete,
    ):
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
    fill_mode = resolve_fill_mode()
    sim = simulate_round_trip_5m(
        day_bars,
        buy=float(signal["limit_buy"]),
        sell=float(signal["limit_sell"]),
        stop=float(signal["stop"]),
        shares=shares,
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
        as_of_et=sim_as_of,
        fill_mode=fill_mode,
    )

    prev_filled = bool(existing and existing.get("filled"))
    prev_complete = bool(existing and existing.get("status") == "complete")
    # Email only the primary (gate) book so Tony gets one buy + one sell per day.
    notify_arm = account_name == ACCOUNT_GATE

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
        notify_out = None
        if notify_arm and row["filled"] and not prev_filled:
            notify_out = notify_paper_buy(
                session_date_et=day,
                ticker=str(ticker),
                shares=shares,
                entry_price=float(row["entry_price"]),
                deploy=float(deploy),
                fill_ts=row.get("fill_ts"),
                account_name=account_name,
            )
        return {
            "account_name": account_name,
            "log": row,
            "in_progress": True,
            "notify": notify_out,
        }

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
                session_date=day,
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
    notify_out: dict[str, Any] | None = None
    if notify_arm and not prev_complete:
        notes: dict[str, Any] = {}
        if not prev_filled:
            notes["buy"] = notify_paper_buy(
                session_date_et=day,
                ticker=str(ticker),
                shares=shares,
                entry_price=float(row["entry_price"]),
                deploy=float(deploy),
                fill_ts=row.get("fill_ts"),
                account_name=account_name,
            )
        notes["sell"] = notify_paper_sell(
            session_date_et=day,
            ticker=str(ticker),
            shares=shares,
            entry_price=float(row["entry_price"]),
            exit_price=float(row["exit_price"]),
            net_pnl=float(row["net_pnl"]),
            exit_reason=row.get("exit_reason") or sim.get("scenario"),
            exit_ts=row.get("exit_ts"),
            account_name=account_name,
        )
        notify_out = notes
    return {
        "account_name": account_name,
        "log": row,
        "applied": applied,
        "notify": notify_out,
    }


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
    # Paper worker owns Account $ display until RH is wired.
    if get_ledger_source(conn) != LEDGER_SOURCE_PAPER:
        set_ledger_source(conn, LEDGER_SOURCE_PAPER)
    day = (session_date_et or today_et_str())[:10]
    settle_due_cash(conn, session_date_et=day)

    if is_kill_switch_active(conn):
        return {
            "ok": False,
            "session_date_et": day,
            "error": "kill_switch_active",
            "balances": {n: get_paper_balance(conn, n) for n in PAPER_ACCOUNTS},
        }

    as_of = datetime.now(ET)
    primary_mode = get_allocation_mode(conn)
    # Shadow book: always #1-only selection for comparison when primary is top-3.
    shadow_mode = (
        AllocationMode.SINGLE_TOP1
        if primary_mode == AllocationMode.BEST_TRADABLE_TOP3
        else primary_mode
    )

    primary_signal = _plan_signal(
        conn,
        day,
        allocation_mode=primary_mode,
        persist_plan=True,
        as_of_et=as_of,
    )
    # Shadow propose must not overwrite the primary armed plan row.
    shadow_signal = _plan_signal(
        conn,
        day,
        allocation_mode=shadow_mode,
        persist_plan=False,
        as_of_et=as_of,
    )

    bars_cache: dict[str, list[dict]] = {}

    def _bars_for(ticker: str | None) -> list[dict]:
        if not ticker:
            return []
        key = str(ticker).upper()
        if key not in bars_cache:
            bars_cache[key] = _fetch_day_bars(key, day, lookback_days=lookback_days)
        return bars_cache[key]

    results = []
    for name in PAPER_ACCOUNTS:
        signal = primary_signal if name == ACCOUNT_GATE else shadow_signal
        existing = get_session_log(conn, day, name)
        if not signal.get("ok"):
            # Do not finalize the day before ranks/prep catch up — worker often
            # ticks at midnight while morning prep is at 4:00 PT / ~7:00 ET.
            if _session_already_final(
                existing,
                signal_ok=False,
                as_of_et=as_of,
                force_complete=force_complete,
            ):
                results.append(
                    {"account_name": name, "skipped": True, "reason": "already_final", "log": existing}
                )
                continue
            waiting = _before_fill_deadline(as_of) and not force_complete
            row = {
                "session_date_et": day,
                "account_name": name,
                "status": _WAITING_SIGNAL if waiting else "no_signal",
                "scenario": "propose_failed",
                "filled": False,
                "net_pnl": 0.0,
                "detail": signal.get("error")
                or (
                    "Waiting for morning prep / top pick"
                    if waiting
                    else "No top pick available to propose"
                ),
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
                day_bars=_bars_for(signal.get("ticker")),
                as_of_et=as_of,
                force_complete=force_complete,
            )
        )

    # Idempotent PAPER audit once the gate arm reaches a true final status for the day
    gate_log = get_session_log(conn, day, ACCOUNT_GATE) or {}
    audit_id = None
    if gate_log.get("status") in _FINAL_STATUSES and gate_log.get("status") != _WAITING_SIGNAL:
        audit_id = log_paper_day_complete(
            conn,
            session_date_et=day,
            gate_log=gate_log,
            arms=[{
                "account_name": r.get("account_name"),
                "status": (r.get("log") or {}).get("status"),
                "skipped": r.get("skipped"),
            } for r in results],
        )

    return {
        "ok": True,
        "session_date_et": day,
        "signal": {
            "ticker": primary_signal.get("ticker"),
            "allow_trade": primary_signal.get("allow_trade"),
            "ma_score": primary_signal.get("ma_score"),
            "error": primary_signal.get("error"),
            "allocation_mode": primary_signal.get("allocation_mode") or primary_mode.value,
            "selection": primary_signal.get("selection"),
        },
        "shadow_signal": {
            "ticker": shadow_signal.get("ticker"),
            "allocation_mode": shadow_signal.get("allocation_mode") or shadow_mode.value,
            "error": shadow_signal.get("error"),
            "selection": shadow_signal.get("selection"),
        },
        "arms": results,
        "balances": {n: get_paper_balance(conn, n) for n in PAPER_ACCOUNTS},
        "scoreboard": paper_scoreboard(conn),
        "paper_audit_id": audit_id,
        "fill_mode": resolve_fill_mode(),
    }


def paper_status_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    ensure_paper_accounts(conn)
    day = today_et_str()
    mode = get_allocation_mode(conn)
    return {
        "ok": True,
        "execution_mode": "paper",
        "session_date_et": day,
        "fill_mode": resolve_fill_mode(),
        "allocation_mode": mode.value,
        "shadow_allocation_mode": (
            AllocationMode.SINGLE_TOP1.value
            if mode == AllocationMode.BEST_TRADABLE_TOP3
            else mode.value
        ),
        "balances": {n: get_paper_balance(conn, n) for n in PAPER_ACCOUNTS},
        "today": {
            n: get_session_log(conn, day, n) for n in PAPER_ACCOUNTS
        },
        "scoreboard": paper_scoreboard(conn),
        "kill_switch_active": is_kill_switch_active(conn),
    }
