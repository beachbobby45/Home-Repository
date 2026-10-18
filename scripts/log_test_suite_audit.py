#!/usr/bin/env python3
"""Run pytest (or accept counts) and log results to ops_audit as TEST (no P&L impact).

Usage:
  PYTHONPATH=src .venv/bin/python3 scripts/log_test_suite_audit.py
  PYTHONPATH=src .venv/bin/python3 scripts/log_test_suite_audit.py --suite paper --pytest-args tests/test_paper_ledger.py
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.execution.ops_audit import list_audit_events, log_test_suite_results


def _parse_pytest_summary(text: str) -> tuple[int, int, int]:
    # "326 passed in 8.10s" or "15 passed, 2 failed"
    passed = failed = 0
    m = re.search(r"(\d+)\s+passed", text)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", text)
    if m:
        failed = int(m.group(1))
    total = passed + failed
    m = re.search(r"collected\s+(\d+)\s+items?", text)
    if m and total == 0:
        total = int(m.group(1))
    if total == 0:
        total = passed + failed
    return passed, failed, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="full")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--pytest-args", nargs="*", default=["tests/"])
    parser.add_argument("--skip-run", action="store_true", help="Only use --passed/--failed")
    parser.add_argument("--passed", type=int, default=None)
    parser.add_argument("--failed", type=int, default=0)
    parser.add_argument("--total", type=int, default=None)
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    details: list[dict] = []
    if args.skip_run:
        passed = int(args.passed or 0)
        failed = int(args.failed or 0)
        total = int(args.total or (passed + failed))
        notes = args.notes or "Manual TEST audit entry"
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "--tb=line", *args.pytest_args]
        env = {**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(ROOT / "src")}
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
        text = (proc.stdout or "") + "\n" + (proc.stderr or "")
        passed, failed, total = _parse_pytest_summary(text)
        if total == 0 and proc.returncode != 0:
            failed = max(failed, 1)
            total = max(total, failed)
        notes = args.notes or f"pytest exit={proc.returncode}"
        details.append({"stdout_tail": "\n".join(text.strip().splitlines()[-20:])})

    db_path = init_db(args.db)
    conn = connect(db_path)
    try:
        eid = log_test_suite_results(
            conn,
            suite_name=args.suite,
            passed=passed,
            failed=failed,
            total=total,
            details=details,
            notes=notes,
        )
        conn.commit()
        print(f"Logged TEST audit id={eid} suite={args.suite} {passed}/{total} passed (affects_pnl=false)")
        latest = list_audit_events(conn, kind="TEST", limit=1)
        if latest:
            print(f"  title: {latest[0]['title']}")
    finally:
        conn.close()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
