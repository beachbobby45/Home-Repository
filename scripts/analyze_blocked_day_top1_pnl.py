#!/usr/bin/env python3
"""Day-by-day #1 pick counterfactual using REAL local agent.db only.

For each of the last N trading days with OHLCV data:
  - Resolve ranked #1 (prefer frozen rank_snapshots, else operator_day_log,
    else reconstruct via build_ranked_top20_for_date — labeled as such)
  - Compute the system's pullback limit buy / Growth Plan sell / stop
    for deploy=$10,000 (same formulas as Trade tab)
  - Check whether that day's daily bar LOW reached the buy and HIGH reached
    the sell (and stop)

IMPORTANT LIMITATIONS (do not ignore):
  1. Daily OHLCV cannot prove whether the limit filled before 11:30 ET.
  2. Daily OHLCV cannot prove whether the high happened after the fill
     (buy-then-sell vs sell-then-buy order within the day is unknown).
  3. P&L scenarios below are therefore labeled and conservative options
     are shown — not a guarantee of live fills.

Usage (on Tony's Mac):
  cd ~/Home-Repository
  PYTHONPATH=src .venv/bin/python3 scripts/analyze_blocked_day_top1_pnl.py --days 30
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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
from investment_agent.pullback_entry import compute_pullback_trade_plan  # noqa: E402


def _resolve_top1(conn, session_date: str) -> tuple[dict | None, str]:
    """Return (ranked row or None, source label)."""
    snap = get_rank_snapshot(conn, session_date)
    if snap:
        return snap[0], "rank_snapshot"

    op = conn.execute(
        """
        SELECT top_pick_ticker, market_activity_score, allow_trade, outcome
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
            {
                "ticker": op["top_pick_ticker"],
                "avg_range_pct": None,
                "score": None,
            },
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


def analyze_day(conn, session_date: str, *, deploy: float) -> dict:
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

    base = {
        "session_date_et": session_date,
        "top1_source": source,
        "ticker": None,
        "ma_score": int(ma["score"]) if ma else None,
        "ma_band": ma["band"] if ma else None,
        "allow_trade": bool(ma["allow_trade"]) if ma else None,
        "bull_gate_ok": bool(ma["bull_gate_ok"]) if ma else None,
        "data_ok": False,
        "limitation": None,
    }
    if not top or not top.get("ticker"):
        base["limitation"] = "No top-1 ticker stored or reconstructable for this date"
        return base

    ticker = top["ticker"]
    base["ticker"] = ticker
    bar = _day_bar(conn, ticker, session_date)
    if not bar:
        base["limitation"] = f"No OHLCV daily bar for {ticker} on {session_date}"
        return base

    avg_range = _avg_range(conn, ticker, top)
    if avg_range is None:
        base["limitation"] = f"No avg_range_pct for {ticker} — cannot compute pullback plan"
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
        base["limitation"] = "Pullback plan empty (bad open/deploy)"
        return base

    buy = float(plan["limit_buy_price"])
    sell = float(plan["limit_sell_price"])
    stop = float(plan["stop_price"])
    shares = int(plan["shares"])

    buy_touched = bar["low"] <= buy
    sell_touched = bar["high"] >= sell
    stop_touched = bar["low"] <= stop

    # Scenario A — optimistic same-day (daily bar ambiguity): buy+sell touched → target
    # Scenario B — if buy+stop and not sell → stop
    # Scenario C — buy only → mark to close
    # Scenario D — buy not touched → no trade / flat
    scenario = "no_fill"
    exit_px = None
    net = 0.0
    if buy_touched and sell_touched:
        scenario = "target_hit_ambiguous_order"
        exit_px = sell
        net = round(shares * (sell - buy) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
    elif buy_touched and stop_touched:
        scenario = "stop_hit_ambiguous_order"
        exit_px = stop
        net = round(shares * (stop - buy) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
    elif buy_touched:
        scenario = "filled_exit_close"
        exit_px = bar["close"]
        net = round(shares * (bar["close"] - buy) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)

    return {
        **base,
        "data_ok": True,
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
        "buy_touched": buy_touched,
        "sell_touched": sell_touched,
        "stop_touched": stop_touched,
        "scenario": scenario,
        "exit_price": exit_px,
        "net_pnl": net,
        "limitation": (
            "Daily OHLC cannot prove fill-by-11:30 or buy-before-sell order; "
            "scenario uses touch rules only"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Blocked-day #1 counterfactual P&L")
    parser.add_argument("--days", type=int, default=30, help="Trading days to analyze")
    parser.add_argument("--deploy", type=float, default=10_000.0)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    db_path = init_db(args.db)
    if not Path(db_path).is_file():
        print(f"ERROR: database not found at {db_path}")
        print("This script must run on the Mac that has Home-Repository/data/agent.db")
        return 2

    conn = connect(db_path)
    try:
        trading_days = list_trading_dates(conn, count=args.days)
        if not trading_days:
            print("ERROR: no trading dates found in ohlcv_daily")
            return 3

        rows = [analyze_day(conn, d, deploy=args.deploy) for d in trading_days]

        capital = float(args.deploy)
        curve = []
        for r in rows:
            if r.get("data_ok") and r.get("scenario") != "no_fill":
                capital = round(capital + float(r["net_pnl"]), 2)
            curve.append({"date": r["session_date_et"], "capital": capital, "net": r.get("net_pnl")})

        # Inventory checks
        snap_n = conn.execute("SELECT COUNT(*) AS n FROM rank_snapshots").fetchone()["n"]
        ma_n = conn.execute("SELECT COUNT(*) AS n FROM market_activity_evaluations").fetchone()["n"]
        op_n = conn.execute("SELECT COUNT(*) AS n FROM operator_day_log").fetchone()["n"]
        ohlcv_days = conn.execute("SELECT COUNT(DISTINCT date) AS n FROM ohlcv_daily").fetchone()["n"]

        print("=== DATA INVENTORY (real DB) ===")
        print(f"DB path: {db_path}")
        print(f"rank_snapshots rows: {snap_n}")
        print(f"market_activity_evaluations rows: {ma_n}")
        print(f"operator_day_log rows: {op_n}")
        print(f"distinct ohlcv dates: {ohlcv_days}")
        print(f"trading days analyzed: {len(trading_days)} ({trading_days[0]} → {trading_days[-1]})")
        print(f"deploy / starting capital: ${args.deploy:,.2f}")
        print()
        print("LIMITATIONS:")
        print("  • Daily bars only — cannot prove 11:30 ET limit deadline")
        print("  • Daily bars only — cannot prove buy filled before sell/stop")
        print("  • Fees: $7 buy + $7 sell (system defaults)")
        print()

        print(
            f"{'DATE':<12} {'TCKR':<6} {'SRC':<22} {'MA':>4} {'ALLOW':>5} "
            f"{'BUY':>8} {'SELL':>8} {'B?':>3} {'S?':>3} {'SCENARIO':<28} {'NET':>9}"
        )
        for r in rows:
            if not r.get("ticker"):
                print(
                    f"{r['session_date_et']:<12} {'—':<6} {r['top1_source']:<22} "
                    f"{'—':>4} {'—':>5} {'—':>8} {'—':>8} {'—':>3} {'—':>3} "
                    f"{'NO_DATA':<28} {'—':>9}"
                )
                continue
            print(
                f"{r['session_date_et']:<12} {r['ticker']:<6} {r['top1_source']:<22} "
                f"{(r['ma_score'] if r['ma_score'] is not None else '—'):>4} "
                f"{('Y' if r['allow_trade'] else 'N') if r['allow_trade'] is not None else '—':>5} "
                f"{r.get('limit_buy') or 0:>8.2f} {r.get('limit_sell') or 0:>8.2f} "
                f"{'Y' if r.get('buy_touched') else 'N':>3} "
                f"{'Y' if r.get('sell_touched') else 'N':>3} "
                f"{(r.get('scenario') or '—'):<28} "
                f"{(r.get('net_pnl') if r.get('data_ok') else 0):>9.2f}"
            )

        filled = [r for r in rows if r.get("data_ok") and r.get("scenario") != "no_fill"]
        targets = [r for r in filled if r["scenario"] == "target_hit_ambiguous_order"]
        stops = [r for r in filled if r["scenario"] == "stop_hit_ambiguous_order"]
        closes = [r for r in filled if r["scenario"] == "filled_exit_close"]
        no_fill = [r for r in rows if r.get("data_ok") and r.get("scenario") == "no_fill"]
        missing = [r for r in rows if not r.get("data_ok")]

        print()
        print("=== SUMMARY ===")
        print(f"Days with usable #1 + bar + plan: {sum(1 for r in rows if r.get('data_ok'))}")
        print(f"Buy NOT touched (no fill):        {len(no_fill)}")
        print(f"Target-touch days (ambiguous):    {len(targets)}")
        print(f"Stop-touch days (ambiguous):      {len(stops)}")
        print(f"Filled → exit close:              {len(closes)}")
        print(f"Missing data days:                {len(missing)}")
        print(f"Starting capital: ${args.deploy:,.2f}")
        print(f"Ending capital (touch scenarios): ${capital:,.2f}")
        print(f"Net change: ${capital - args.deploy:,.2f}")
        print()
        print("Capital curve (end of each day):")
        for c in curve:
            print(f"  {c['date']}  ${c['capital']:,.2f}")

        payload = {
            "db_path": str(db_path),
            "deploy": args.deploy,
            "inventory": {
                "rank_snapshots": snap_n,
                "market_activity_evaluations": ma_n,
                "operator_day_log": op_n,
                "ohlcv_distinct_dates": ohlcv_days,
            },
            "days": rows,
            "capital_curve": curve,
            "ending_capital": capital,
        }
        if args.json_out:
            args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"\nWrote JSON: {args.json_out}")
        else:
            # Always write next to DB for easy paste/share
            out = Path(db_path).parent / "blocked_day_top1_pnl_last30.json"
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"\nWrote JSON: {out}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
