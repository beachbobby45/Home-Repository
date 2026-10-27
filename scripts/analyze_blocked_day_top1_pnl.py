#!/usr/bin/env python3
"""Day-by-day #1 pick counterfactual using REAL local agent.db + 5m bars.

Rules (Tony, 2026-10-17):
  - Deploy exactly $10,000 per day (one stock only — T+1 settlement of sale).
  - Count a win/loss ONLY when 5-minute bars prove fill order (option B).
  - Limit buy must fill by LIMIT_FILL_DEADLINE (12:30 ET v1).
  - After fill: walk subsequent 5m bars; same-bar stop+target → stop
    (matches backtest._bar_exit_price conservatism).
  - No fill by deadline → no trade that day (net $0).
  - No 5m bars for that ticker/day → excluded from P&L (not guessed).

Usage (Mac with agent.db):
  cd ~/Home-Repository
  PYTHONPATH=src .venv/bin/python3 scripts/analyze_blocked_day_top1_pnl.py --days 30
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import _bar_exit_price, _group_bars_by_date  # noqa: E402
from investment_agent.close_report import (  # noqa: E402
    _day_bar,
    build_ranked_top20_for_date,
    get_rank_snapshot,
)
from investment_agent.db import connect, init_db  # noqa: E402
from investment_agent.finance import (  # noqa: E402
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
)
from investment_agent.period_screener import list_trading_dates  # noqa: E402
from investment_agent.providers.yfinance_bars import get_intraday_bars  # noqa: E402
from investment_agent.pullback_entry import (  # noqa: E402
    LIMIT_FILL_DEADLINE,
    compute_pullback_trade_plan,
)

ET = ZoneInfo("America/New_York")
DEPLOY_DEFAULT = 10_000.0


def _bar_time_et(bar: dict) -> datetime | None:
    ts = bar.get("ts")
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ET)
    return dt.astimezone(ET)


def _resolve_top1(conn, session_date: str) -> tuple[dict | None, str]:
    snap = get_rank_snapshot(conn, session_date)
    if snap:
        return snap[0], "rank_snapshot"

    op = conn.execute(
        """
        SELECT top_pick_ticker
        FROM operator_day_log
        WHERE session_date_et = ?
        """,
        (session_date,),
    ).fetchone()
    if op and op["top_pick_ticker"]:
        ranked = build_ranked_top20_for_date(conn, session_date)
        for row in ranked:
            if row.get("ticker") == op["top_pick_ticker"]:
                return row, "operator_day_log+rank"
        return (
            {"ticker": op["top_pick_ticker"], "avg_range_pct": None, "score": None},
            "operator_day_log_ticker_only",
        )

    ranked = build_ranked_top20_for_date(conn, session_date)
    if ranked:
        return ranked[0], "reconstructed_screener"
    return None, "missing"


def _avg_range(conn, ticker: str, row: dict) -> float | None:
    if row.get("avg_range_pct") is not None:
        try:
            return float(row["avg_range_pct"])
        except (TypeError, ValueError):
            pass
    m = conn.execute(
        """
        SELECT avg_range_pct FROM ticker_metrics
        WHERE ticker = ?
        ORDER BY computed_at DESC LIMIT 1
        """,
        (ticker,),
    ).fetchone()
    if m and m["avg_range_pct"] is not None:
        return float(m["avg_range_pct"])
    return None


def _simulate_5m(
    day_bars: list[dict],
    *,
    buy: float,
    sell: float,
    stop: float,
    shares: int,
) -> dict:
    """Proven fill/exit walk on one session's 5m bars. Never invents fills."""
    if not day_bars:
        return {
            "scenario": "no_5m_bars",
            "filled": False,
            "net_pnl": None,
            "counts_toward_pnl": False,
            "detail": "No 5m bars for this ticker/date — excluded (not guessed)",
        }

    fill_bar = None
    fill_ts = None
    for bar in day_bars:
        t = _bar_time_et(bar)
        if t is None:
            continue
        if t.time() > LIMIT_FILL_DEADLINE:
            break
        if float(bar["low"]) <= buy:
            fill_bar = bar
            fill_ts = t.isoformat()
            break

    if fill_bar is None:
        return {
            "scenario": "no_fill_by_1130",
            "filled": False,
            "fill_ts": None,
            "exit_ts": None,
            "exit_price": None,
            "net_pnl": 0.0,
            "counts_toward_pnl": True,
            "detail": f"Limit ${buy:.2f} not touched on any 5m bar by {LIMIT_FILL_DEADLINE.strftime('%H:%M')} ET",
        }

    # Walk bars at/after fill for exit
    started = False
    for bar in day_bars:
        t = _bar_time_et(bar)
        if t is None:
            continue
        if not started:
            if bar is fill_bar or (fill_ts and t.isoformat() == fill_ts):
                started = True
            else:
                continue
            # On fill bar itself: only count exits after assuming fill at this bar's low touch.
            # Conservative: if stop also in fill bar, take stop; elif target, take target.
            exit_px, reason = _bar_exit_price(target=sell, stop=stop, bar=bar)
            if exit_px is not None and reason is not None:
                net = round(shares * (exit_px - buy) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
                return {
                    "scenario": f"exit_{reason}_same_bar_as_fill",
                    "filled": True,
                    "fill_ts": fill_ts,
                    "exit_ts": t.isoformat(),
                    "exit_price": exit_px,
                    "exit_reason": reason,
                    "net_pnl": net,
                    "counts_toward_pnl": True,
                    "detail": f"Filled then {reason} on same 5m bar (stop preferred if both)",
                }
            continue

        exit_px, reason = _bar_exit_price(target=sell, stop=stop, bar=bar)
        if exit_px is not None and reason is not None:
            net = round(shares * (exit_px - buy) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
            return {
                "scenario": f"exit_{reason}",
                "filled": True,
                "fill_ts": fill_ts,
                "exit_ts": t.isoformat(),
                "exit_price": exit_px,
                "exit_reason": reason,
                "net_pnl": net,
                "counts_toward_pnl": True,
                "detail": f"Filled {fill_ts}; exited {reason} @ {exit_px:.2f}",
            }

    last = day_bars[-1]
    last_t = _bar_time_et(last)
    close_px = float(last["close"])
    net = round(shares * (close_px - buy) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
    return {
        "scenario": "exit_eod_close",
        "filled": True,
        "fill_ts": fill_ts,
        "exit_ts": last_t.isoformat() if last_t else None,
        "exit_price": close_px,
        "exit_reason": "eod_close",
        "net_pnl": net,
        "counts_toward_pnl": True,
        "detail": "Filled; neither target nor stop on later 5m bars → exit last 5m close",
    }


def analyze_day(
    conn,
    session_date: str,
    *,
    deploy: float,
    bars_by_ticker: dict[str, dict[str, list[dict]]],
    lookback_days: int,
) -> dict:
    top, source = _resolve_top1(conn, session_date)
    ma = conn.execute(
        """
        SELECT score, band, allow_trade, bull_gate_ok, summary
        FROM market_activity_evaluations e
        WHERE session_date_et = ?
          AND captured_at = (
            SELECT MAX(captured_at) FROM market_activity_evaluations e2
            WHERE e2.session_date_et = e.session_date_et
          )
        """,
        (session_date,),
    ).fetchone()

    base: dict = {
        "session_date_et": session_date,
        "top1_source": source,
        "ticker": None,
        "ma_score": int(ma["score"]) if ma else None,
        "ma_band": ma["band"] if ma else None,
        "allow_trade": bool(ma["allow_trade"]) if ma else None,
        "bull_gate_ok": bool(ma["bull_gate_ok"]) if ma else None,
        "data_ok": False,
        "counts_toward_pnl": False,
        "limitation": None,
        "deploy": deploy,
        "one_stock_per_day": True,
    }
    if not top or not top.get("ticker"):
        base["limitation"] = "No top-1 ticker stored or reconstructable"
        return base

    ticker = str(top["ticker"]).upper()
    base["ticker"] = ticker
    bar = _day_bar(conn, ticker, session_date)
    if not bar:
        base["limitation"] = f"No OHLCV daily bar for {ticker} on {session_date}"
        return base

    avg_range = _avg_range(conn, ticker, top)
    if avg_range is None:
        base["limitation"] = f"No avg_range_pct for {ticker}"
        base["day_open"] = bar["open"]
        base["day_high"] = bar["high"]
        base["day_low"] = bar["low"]
        base["day_close"] = bar["close"]
        return base

    net_target = daily_profit_target(deploy)
    plan = compute_pullback_trade_plan(
        session_open=bar["open"],
        avg_range_pct=avg_range,
        deploy_dollar=deploy,
        net_target=net_target,
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
    )
    if not plan:
        base["limitation"] = "Pullback plan empty"
        return base

    buy = float(plan["limit_buy_price"])
    sell = float(plan["limit_sell_price"])
    stop = float(plan["stop_price"])
    shares = int(plan["shares"])

    if ticker not in bars_by_ticker:
        try:
            raw = get_intraday_bars(ticker, lookback_days=lookback_days, interval="5m")
            bars_by_ticker[ticker] = _group_bars_by_date(raw)
        except Exception as exc:  # noqa: BLE001 — report, do not invent
            bars_by_ticker[ticker] = {}
            base.update(
                {
                    "data_ok": False,
                    "avg_range_pct": round(avg_range, 3),
                    "day_open": round(bar["open"], 2),
                    "day_high": round(bar["high"], 2),
                    "day_low": round(bar["low"], 2),
                    "day_close": round(bar["close"], 2),
                    "limit_buy": buy,
                    "limit_sell": sell,
                    "stop": stop,
                    "shares": shares,
                    "net_target": net_target,
                    "scenario": "intraday_fetch_failed",
                    "limitation": f"5m fetch failed for {ticker}: {exc}",
                    "counts_toward_pnl": False,
                }
            )
            return base

    day_bars = bars_by_ticker[ticker].get(session_date, [])
    sim = _simulate_5m(day_bars, buy=buy, sell=sell, stop=stop, shares=shares)

    return {
        **base,
        "data_ok": sim["scenario"] != "no_5m_bars" and sim.get("scenario") != "intraday_fetch_failed",
        "avg_range_pct": round(avg_range, 3),
        "day_open": round(bar["open"], 2),
        "day_high": round(bar["high"], 2),
        "day_low": round(bar["low"], 2),
        "day_close": round(bar["close"], 2),
        "limit_buy": buy,
        "limit_sell": sell,
        "stop": stop,
        "shares": shares,
        "net_target": net_target,
        "fill_deadline_et": LIMIT_FILL_DEADLINE.strftime("%H:%M"),
        **sim,
        "limitation": sim.get("detail") if not sim.get("counts_toward_pnl") else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Blocked-day #1 P&L (5m proven fills)")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--deploy", type=float, default=DEPLOY_DEFAULT,
                        help="Starting capital / fixed daily deploy unless --compound")
    parser.add_argument(
        "--compound",
        action="store_true",
        help=(
            "Each day deploy = prior ending capital (start + settled P&L). "
            "Resizes shares and Growth Plan sell target; re-walks 5m bars. "
            "Do not scale fixed-$10k nets — target price changes."
        ),
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=60,
        help="yfinance 5m lookback (Yahoo free tier ~60d)",
    )
    args = parser.parse_args()

    db_path = init_db(args.db)
    if not Path(db_path).is_file():
        print(f"ERROR: database not found at {db_path}")
        print("Run this on the Mac that has Home-Repository/data/agent.db")
        return 2

    conn = connect(db_path)
    try:
        trading_days = list_trading_dates(conn, count=args.days)
        if not trading_days:
            print("ERROR: no trading dates found in ohlcv_daily")
            return 3

        bars_cache: dict[str, dict[str, list[dict]]] = {}
        starting = float(args.deploy)
        capital = starting
        rows: list[dict] = []
        curve: list[dict] = []

        # Sequential: compound must resize plan each day from settled capital.
        for d in trading_days:
            day_deploy = capital if args.compound else starting
            if day_deploy < 50:
                r = {
                    "session_date_et": d,
                    "top1_source": "skipped",
                    "ticker": None,
                    "scenario": "capital_too_low",
                    "counts_toward_pnl": True,
                    "net_pnl": 0.0,
                    "deploy": day_deploy,
                    "limitation": f"Capital ${day_deploy:.2f} too low to trade",
                }
            else:
                r = analyze_day(
                    conn,
                    d,
                    deploy=day_deploy,
                    bars_by_ticker=bars_cache,
                    lookback_days=args.lookback_days,
                )
            rows.append(r)
            if r.get("counts_toward_pnl") and r.get("net_pnl") is not None:
                capital = round(capital + float(r["net_pnl"]), 2)
            curve.append(
                {
                    "date": r["session_date_et"],
                    "deploy": r.get("deploy"),
                    "capital": capital,
                    "net": r.get("net_pnl"),
                    "scenario": r.get("scenario"),
                    "counts_toward_pnl": r.get("counts_toward_pnl"),
                }
            )

        snap_n = conn.execute("SELECT COUNT(*) AS n FROM rank_snapshots").fetchone()["n"]
        ma_n = conn.execute("SELECT COUNT(*) AS n FROM market_activity_evaluations").fetchone()["n"]
        op_n = conn.execute("SELECT COUNT(*) AS n FROM operator_day_log").fetchone()["n"]
        ohlcv_days = conn.execute("SELECT COUNT(DISTINCT date) AS n FROM ohlcv_daily").fetchone()["n"]

        growth_pct = ((capital / starting) - 1.0) * 100.0 if starting else 0.0

        print("=== RULES ===")
        if args.compound:
            print(
                f"Deploy: COMPOUND — start ${starting:,.2f}, each day deploy = "
                f"prior ending capital (one stock; sale settles overnight)"
            )
        else:
            print(
                f"Deploy per day: FIXED ${starting:,.2f} "
                f"(one stock; sale settles overnight; surplus cash idle)"
            )
        print("Fill proof: 5-minute bars only (option B)")
        print(f"Limit deadline: {LIMIT_FILL_DEADLINE.strftime('%H:%M')} ET")
        print("Same 5m bar stop+target → count stop (conservative)")
        print()
        print("=== DATA INVENTORY ===")
        print(f"DB: {db_path}")
        print(f"rank_snapshots: {snap_n} | MA evals: {ma_n} | operator_day_log: {op_n}")
        print(f"ohlcv distinct dates: {ohlcv_days}")
        print(f"days: {len(trading_days)} ({trading_days[0]} → {trading_days[-1]})")
        print()

        print(
            f"{'DATE':<12} {'TCKR':<6} {'DEPLOY':>10} {'MA':>4} {'GO':>3} "
            f"{'BUY':>8} {'SELL':>8} {'SCENARIO':<28} {'NET':>9}"
        )
        for r in rows:
            net_s = "—"
            if r.get("counts_toward_pnl") and r.get("net_pnl") is not None:
                net_s = f"{float(r['net_pnl']):.2f}"
            elif r.get("net_pnl") is None:
                net_s = "EXCL"
            print(
                f"{r['session_date_et']:<12} {(r.get('ticker') or '—'):<6} "
                f"{(r.get('deploy') or 0):>10.2f} "
                f"{(r['ma_score'] if r.get('ma_score') is not None else '—'):>4} "
                f"{('Y' if r['allow_trade'] else 'N') if r.get('allow_trade') is not None else '—':>3} "
                f"{(r.get('limit_buy') or 0):>8.2f} {(r.get('limit_sell') or 0):>8.2f} "
                f"{(r.get('scenario') or 'NO_DATA'):<28} {net_s:>9}"
            )

        counted = [r for r in rows if r.get("counts_toward_pnl")]
        targets = [r for r in counted if (r.get("exit_reason") == "target")]
        stops = [r for r in counted if (r.get("exit_reason") == "stop")]
        eods = [r for r in counted if (r.get("exit_reason") == "eod_close")]
        no_fill = [r for r in counted if r.get("scenario") == "no_fill_by_1130"]
        excluded = [r for r in rows if not r.get("counts_toward_pnl")]

        print()
        print("=== SUMMARY (5m-proven only) ===")
        print(f"Mode: {'COMPOUND deploy' if args.compound else 'FIXED $deploy'}")
        print(f"Days counted in P&L:     {len(counted)}")
        print(f"  Target exits:          {len(targets)}")
        print(f"  Stop exits:            {len(stops)}")
        print(f"  EOD close exits:       {len(eods)}")
        print(f"  No fill by {LIMIT_FILL_DEADLINE.strftime('%H:%M')}:      {len(no_fill)}")
        print(f"Days excluded (no data): {len(excluded)}")
        print(f"Starting capital: ${starting:,.2f}")
        print(f"Ending capital:   ${capital:,.2f}")
        print(f"Net change:       ${capital - starting:,.2f}")
        print(f"Growth:           {growth_pct:+.2f}%")
        print()
        print("Capital curve:")
        for c in curve:
            flag = "" if c["counts_toward_pnl"] else " (excluded)"
            dep = c.get("deploy")
            dep_s = f"  deploy=${dep:,.2f}" if dep is not None else ""
            print(f"  {c['date']}  ${c['capital']:,.2f}{dep_s}{flag}")

        payload = {
            "rules": {
                "starting_capital": starting,
                "compound": bool(args.compound),
                "deploy_mode": "compound_prior_capital" if args.compound else "fixed",
                "one_stock_per_day": True,
                "settlement": "sale proceeds available next session (T+1 cash)",
                "fill_proof": "5m_bars",
                "limit_deadline_et": LIMIT_FILL_DEADLINE.strftime("%H:%M"),
                "same_bar_priority": "stop_over_target",
            },
            "db_path": str(db_path),
            "inventory": {
                "rank_snapshots": snap_n,
                "market_activity_evaluations": ma_n,
                "operator_day_log": op_n,
                "ohlcv_distinct_dates": ohlcv_days,
            },
            "days": rows,
            "capital_curve": curve,
            "ending_capital": capital,
            "growth_pct": round(growth_pct, 4),
        }
        default_name = (
            "blocked_day_top1_pnl_last30_compound.json"
            if args.compound
            else "blocked_day_top1_pnl_last30.json"
        )
        out = args.json_out or (Path(db_path).parent / default_name)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON: {out}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
