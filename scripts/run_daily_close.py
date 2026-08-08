#!/usr/bin/env python3
"""Generate Daily Close or Weekly Close report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.close_report import (
    generate_daily_close_report,
    generate_weekly_close_report,
    save_close_report,
)
from investment_agent.db import connect, init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily / Weekly Close report")
    parser.add_argument("--daily", action="store_true", help="Daily close (default)")
    parser.add_argument("--weekly", action="store_true", help="Weekly close")
    parser.add_argument("--date", help="Report date (YYYY-MM-DD)")
    parser.add_argument("--fetch-10et", action="store_true", help="Fetch 5m bars for 10:00 ET entries")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    path = init_db(args.db)
    conn = connect(path)
    try:
        if args.weekly:
            report = generate_weekly_close_report(
                conn, args.date, fetch_10_et=args.fetch_10et,
            )
        else:
            report = generate_daily_close_report(
                conn, args.date, fetch_10_et=args.fetch_10et,
            )
        save_close_report(conn, report)
        conn.commit()
    finally:
        conn.close()

    if args.output:
        args.output.write_text(json.dumps(report, indent=2))
        print(f"Wrote {args.output}")

    print(f"=== {report['report_type'].upper()} CLOSE ===")
    print(f"Date: {report.get('report_date')}")
    for h in report.get("highlights", [])[:5]:
        print(f"  • {h}")
    if report["report_type"] == "daily":
        s = report["tabs"]["full_top20"]["summary"]
        print(f"Journal net: ${s.get('journal_realized_net', 0):.2f}")
        print(f"Best on list (open): {s.get('best_hit_ticker_open')} → ${s.get('best_net_at_high_open')}")
        print(f"Ranked #1: {report.get('rank1_ticker')} → ${s.get('rank1_net_at_high_open')}")


if __name__ == "__main__":
    main()
