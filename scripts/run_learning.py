#!/usr/bin/env python3
"""Generate and save daily learning report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.learning import generate_learning_report, save_learning_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate learning report")
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()

    path = init_db(args.db)
    with connect(path) as conn:
        report = generate_learning_report(conn)
        report_id = save_learning_report(conn, report)
        conn.commit()
    print(json.dumps({"ok": True, "id": report_id, "report": report}, indent=2))


if __name__ == "__main__":
    main()
