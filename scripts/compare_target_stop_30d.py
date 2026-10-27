#!/usr/bin/env python3
"""Compare current vs proposed target/stop on last N #1 pullback days (5m proof).

Arm A (current paper rules at $5k):
  net target $75, stop 0.75% of deploy

Arm B (proposed):
  net target $55, stop 0.50% of deploy

Both arms use the same #1 ticker per day, same pullback limit buy, RH-like $0 fees,
and the same 5m fill/exit walk (limit by 11:30 ET; same-bar stop beats target).

Usage (Mac with live agent.db):
  cd ~/Home-Repository
  git fetch origin cursor/compare-target-stop-backtest-cd1d
  git checkout cursor/compare-target-stop-backtest-cd1d
  PYTHONPATH=src .venv/bin/python3 scripts/compare_target_stop_30d.py --days 30 --deploy 5000
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from investment_agent.db import connect, init_db  # noqa: E402
from investment_agent.period_screener import list_trading_dates  # noqa: E402
from investment_agent.strategy import STOP_PCT  # noqa: E402

from analyze_blocked_day_top1_pnl import analyze_day  # noqa: E402


def _summarize(rows: list[dict], *, starting: float) -> dict:
    counted = [r for r in rows if r.get("counts_toward_pnl")]
    filled = [r for r in counted if r.get("filled")]
    targets = [r for r in counted if r.get("exit_reason") == "target"]
    stops = [r for r in counted if r.get("exit_reason") == "stop"]
    eods = [r for r in counted if r.get("exit_reason") == "eod_close"]
    no_fill = [r for r in counted if r.get("scenario") == "no_fill_by_1130"]
    excluded = [r for r in rows if not r.get("counts_toward_pnl")]
    pnl = sum(float(r.get("net_pnl") or 0) for r in counted)
    wins = [r for r in filled if float(r.get("net_pnl") or 0) > 0]
    losses = [r for r in filled if float(r.get("net_pnl") or 0) < 0]
    avg_win = (
        sum(float(r["net_pnl"]) for r in wins) / len(wins) if wins else 0.0
    )
    avg_loss = (
        sum(float(r["net_pnl"]) for r in losses) / len(losses) if losses else 0.0
    )
    return {
        "days": len(rows),
        "days_counted": len(counted),
        "days_excluded": len(excluded),
        "fills": len(filled),
        "no_fill_by_1130": len(no_fill),
        "target_exits": len(targets),
        "stop_exits": len(stops),
        "eod_exits": len(eods),
        "win_rate_pct_on_fills": round(100.0 * len(wins) / max(len(filled), 1), 1),
        "net_pnl": round(pnl, 2),
        "ending_capital": round(starting + pnl, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
    }


def _run_arm(
    conn,
    trading_days: list[str],
    *,
    deploy: float,
    bars_cache: dict,
    lookback_days: int,
    net_target: float,
    stop_pct: float,
    buy_fee: float,
    sell_fee: float,
) -> list[dict]:
    rows: list[dict] = []
    for d in trading_days:
        rows.append(
            analyze_day(
                conn,
                d,
                deploy=deploy,
                bars_by_ticker=bars_cache,
                lookback_days=lookback_days,
                net_target=net_target,
                stop_pct=stop_pct,
                buy_fee=buy_fee,
                sell_fee=sell_fee,
            )
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare current vs proposed $ target / stop on last N days"
    )
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--deploy", type=float, default=5_000.0)
    parser.add_argument("--current-target", type=float, default=75.0)
    parser.add_argument("--current-stop-pct", type=float, default=STOP_PCT)
    parser.add_argument("--proposed-target", type=float, default=55.0)
    parser.add_argument("--proposed-stop-pct", type=float, default=0.50)
    parser.add_argument(
        "--fees",
        type=float,
        default=0.0,
        help="Per-side fee (buy and sell). Default 0 = Robinhood-like stocks.",
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    db_path = init_db(args.db)
    if not Path(db_path).is_file():
        print(f"ERROR: database not found at {db_path}")
        print("Run this on the Mac that has ~/Home-Repository/data/agent.db")
        return 2

    conn = connect(db_path)
    try:
        trading_days = list_trading_dates(conn, count=args.days)
        if not trading_days:
            print("ERROR: no trading dates in ohlcv_daily — ingest first.")
            return 3

        ohlcv_n = conn.execute(
            "SELECT COUNT(DISTINCT date) AS n FROM ohlcv_daily"
        ).fetchone()["n"]
        print("=== COMPARE TARGET/STOP (5m-proven #1 pullback) ===")
        print(f"DB: {db_path}")
        print(f"Days: {len(trading_days)} ({trading_days[0]} → {trading_days[-1]})")
        print(f"ohlcv distinct dates: {ohlcv_n}")
        print(f"Deploy (fixed): ${args.deploy:,.2f}")
        print(f"Fees per side: ${args.fees:.2f} (RH stocks ≈ $0)")
        print()
        print(
            f"Arm A CURRENT : target ${args.current_target:.2f}  "
            f"stop {args.current_stop_pct:.2f}% of deploy "
            f"(≈${args.deploy * args.current_stop_pct / 100:.2f})"
        )
        print(
            f"Arm B PROPOSED: target ${args.proposed_target:.2f}  "
            f"stop {args.proposed_stop_pct:.2f}% of deploy "
            f"(≈${args.deploy * args.proposed_stop_pct / 100:.2f})"
        )
        print()
        print("Fetching/replaying 5m bars (shared cache for both arms)…")

        bars_cache: dict = {}
        fee = float(args.fees)
        rows_a = _run_arm(
            conn,
            trading_days,
            deploy=float(args.deploy),
            bars_cache=bars_cache,
            lookback_days=args.lookback_days,
            net_target=float(args.current_target),
            stop_pct=float(args.current_stop_pct),
            buy_fee=fee,
            sell_fee=fee,
        )
        rows_b = _run_arm(
            conn,
            trading_days,
            deploy=float(args.deploy),
            bars_cache=bars_cache,
            lookback_days=args.lookback_days,
            net_target=float(args.proposed_target),
            stop_pct=float(args.proposed_stop_pct),
            buy_fee=fee,
            sell_fee=fee,
        )

        sum_a = _summarize(rows_a, starting=float(args.deploy))
        sum_b = _summarize(rows_b, starting=float(args.deploy))

        print()
        print(
            f"{'DATE':<12} {'TCKR':<6} {'A_SCENARIO':<26} {'A_NET':>8} "
            f"{'B_SCENARIO':<26} {'B_NET':>8} {'Δ':>8}"
        )
        for a, b in zip(rows_a, rows_b):
            a_net = a.get("net_pnl")
            b_net = b.get("net_pnl")
            a_s = f"{float(a_net):.2f}" if a.get("counts_toward_pnl") and a_net is not None else "EXCL"
            b_s = f"{float(b_net):.2f}" if b.get("counts_toward_pnl") and b_net is not None else "EXCL"
            delta = "—"
            if (
                a.get("counts_toward_pnl")
                and b.get("counts_toward_pnl")
                and a_net is not None
                and b_net is not None
            ):
                delta = f"{float(b_net) - float(a_net):+.2f}"
            print(
                f"{a['session_date_et']:<12} {(a.get('ticker') or '—'):<6} "
                f"{(a.get('scenario') or 'NO_DATA'):<26} {a_s:>8} "
                f"{(b.get('scenario') or 'NO_DATA'):<26} {b_s:>8} {delta:>8}"
            )

        def _line(label: str, ka: str, kb: str | None = None) -> None:
            kb = kb or ka
            va, vb = sum_a[ka], sum_b[kb]
            print(f"  {label:<22} {va!s:>12} {vb!s:>12}")

        print()
        print("=== SUMMARY ===")
        print(f"  {'metric':<22} {'CURRENT':>12} {'PROPOSED':>12}")
        _line("fills", "fills")
        _line("no fill by 11:30", "no_fill_by_1130")
        _line("target exits", "target_exits")
        _line("stop exits", "stop_exits")
        _line("eod exits", "eod_exits")
        _line("win rate on fills %", "win_rate_pct_on_fills")
        _line("avg win $", "avg_win")
        _line("avg loss $", "avg_loss")
        _line("net P&L $", "net_pnl")
        _line("ending capital $", "ending_capital")
        _line("excluded days", "days_excluded")
        print()
        delta_pnl = sum_b["net_pnl"] - sum_a["net_pnl"]
        print(f"Proposed − Current net P&L: ${delta_pnl:+,.2f}")
        if sum_b["net_pnl"] > sum_a["net_pnl"]:
            print("Verdict (this window): PROPOSED did better on net P&L.")
        elif sum_b["net_pnl"] < sum_a["net_pnl"]:
            print("Verdict (this window): CURRENT did better on net P&L.")
        else:
            print("Verdict (this window): tie on net P&L.")

        payload = {
            "deploy": args.deploy,
            "fees_per_side": args.fees,
            "days": trading_days,
            "arm_a_current": {
                "net_target": args.current_target,
                "stop_pct": args.current_stop_pct,
                "summary": sum_a,
                "days": rows_a,
            },
            "arm_b_proposed": {
                "net_target": args.proposed_target,
                "stop_pct": args.proposed_stop_pct,
                "summary": sum_b,
                "days": rows_b,
            },
            "delta_net_pnl": round(delta_pnl, 2),
        }
        out = args.json_out or (
            ROOT / "data" / "compare_target_stop_30d.json"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2))
        print(f"\nWrote {out}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
