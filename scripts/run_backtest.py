#!/usr/bin/env python3
"""Run 60-day intraday backtest on top ranked tickers (5-minute bars)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import backtest_to_dict, run_backtest_from_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Intraday backtest for ranked universe")
    parser.add_argument("--days", type=int, default=60, help="Lookback window (default 60)")
    parser.add_argument("--top", type=int, default=20, help="Top N ranked tickers (default 20)")
    parser.add_argument("--capital", type=float, default=10_000.0, help="Starting capital")
    parser.add_argument("--interval", default="5m", help="Bar interval (default 5m)")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write full JSON report to path",
    )
    args = parser.parse_args()

    print(f"Running {args.days}d intraday backtest on top {args.top} ranked tickers…")
    print("(Fetching 5-minute bars — may take 1–2 minutes.)")

    result = run_backtest_from_db(
        db_path=args.db,
        lookback_days=args.days,
        top_n=args.top,
        starting_capital=args.capital,
        bar_interval=args.interval,
    )
    payload = backtest_to_dict(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2))
        print(f"Full report written to {args.output}")

    print()
    print("=== BACKTEST SUMMARY ===")
    print(f"Period:        {result.start_date} → {result.end_date}")
    print(f"Top tickers:   {', '.join(result.top_tickers)}")
    print(f"Starting:      ${result.starting_capital:,.2f}")
    print(f"Ending:        ${result.ending_capital:,.2f}")
    print(f"Net P&L:       ${result.total_net_pnl:,.2f} ({result.total_return_pct:+.2f}%)")
    print(f"Trades:        {result.total_trades} (W {result.wins} / L {result.losses}, {result.win_rate_pct}% win)")
    print(f"Total fees:    ${result.total_fees:,.2f}")
    print(f"Max drawdown:  {result.max_drawdown_pct:.2f}%")
    if result.spy_return_pct is not None:
        print(f"SPY buy-hold:  {result.spy_return_pct:+.2f}%")
    if result.errors:
        print(f"Data errors:   {len(result.errors)} ticker(s) — see JSON report")

    active_days = [d for d in result.days if d.trades]
    print(f"Trading days:  {len(active_days)} with at least one round trip")
    print()
    print("=== SAMPLE TRADES (last 10) ===")
    for t in result.trades[-10:]:
        print(
            f"  {t.date} {t.ticker:5} {t.exit_reason:6} "
            f"${t.entry_price:.2f}→${t.exit_price:.2f} "
            f"net ${t.net_pnl:+.2f} bal ${t.balance_after:,.2f}"
        )

    print()
    print("=== ASSUMPTIONS ===")
    for line in result.assumptions:
        print(f"  • {line}")

    sys.exit(0)


if __name__ == "__main__":
    main()
