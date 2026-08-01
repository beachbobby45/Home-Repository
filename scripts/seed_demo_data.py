#!/usr/bin/env python3
"""Seed demo/test data for dashboard verification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.db import DEFAULT_DB_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo data for dashboard testing")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="SQLite path (default: data/agent.db)",
    )
    args = parser.parse_args()

    path = seed_demo_db(args.db)
    summary = expected_demo_summary()
    print(json.dumps({"db_path": str(path), "expected": summary}, indent=2))


if __name__ == "__main__":
    main()
