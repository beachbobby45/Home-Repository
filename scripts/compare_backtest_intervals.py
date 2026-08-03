#!/usr/bin/env python3
"""Compare 1m vs 5m backtest on the same short window (Yahoo 1m limit ~7 days)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import backtest_to_dict, run_backtest_from_db


def _summarize(label: str, result) -> dict:
    reasons = {}
    for t in result.trades:
        reasons[t.exit_reason] = reasons.get(t.exit_reason, 0) + 1
    return {
        "label": label,
        "period": f"{result.start_date} → {result.end_date}",
        "starting": result.starting_capital,
        "ending": result.ending_capital,
        "return_pct": result.total_return_pct,
        "trades": result.total_trades,
        "win_rate_pct": result.win_rate_pct,
        "fees": result.total_fees,
        "max_drawdown_pct": result.max_drawdown_pct,
        "exits": reasons,
    }


def main() -> None:
    days = 7
    top = 20
    capital = 10_000.0
    print(f"Comparing 1m vs 5m backtests on top {top} tickers, ~{days} calendar days")
    print("(Yahoo free tier caps 1-minute history at ~7 days.)\n")

    results = {}
    for interval in ("5m", "1m"):
        print(f"Running {interval}…")
        results[interval] = run_backtest_from_db(
            lookback_days=days,
            top_n=top,
            starting_capital=capital,
            bar_interval=interval,
        )

    s5 = _summarize("5-minute bars", results["5m"])
    s1 = _summarize("1-minute bars", results["1m"])

    out = Path("data/backtest_1m_vs_5m_compare.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "window_days": days,
                "five_minute": backtest_to_dict(results["5m"]),
                "one_minute": backtest_to_dict(results["1m"]),
            },
            indent=2,
        )
    )

    print("\n=== SIDE-BY-SIDE (same ~7-day window) ===")
    for key in ("period", "starting", "ending", "return_pct", "trades", "win_rate_pct", "fees", "max_drawdown_pct", "exits"):
        print(f"{key:18}  5m: {s5[key]}")
        print(f"{'':18}  1m: {s1[key]}")
        print()

    delta = s1["return_pct"] - s5["return_pct"]
    print(f"Return difference (1m − 5m): {delta:+.2f} percentage points")
    if abs(delta) < 2:
        print("→ No meaningful difference on this short window; bar size is not the main driver.")
    elif delta > 0:
        print("→ 1m bars improved results on this window (less pessimistic stop ordering).")
    else:
        print("→ 1m bars were worse (more stop-outs on noise).")

    sys.exit(0)


if __name__ == "__main__":
    main()
