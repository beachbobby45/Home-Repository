#!/usr/bin/env python3
"""Run Phase 1 data ingestion (FRED + Finnhub quotes + yfinance bars). No Claude."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.ingest import DEFAULT_TICKERS, run_ingest

LAST_RUN_PATH = ROOT / "data" / "ingest_last_run.json"
LAST_ERROR_PATH = ROOT / "data" / "ingest_last_error.txt"

# After close: refresh quotes if older than 2h; daily bars if older than 12h.
AFTER_CLOSE_QUOTE_STALE_HOURS = 2.0
AFTER_CLOSE_BAR_STALE_HOURS = 12.0


def _write_last_run(summary: dict, *, mode: str) -> None:
    LAST_RUN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "finished_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "mode": mode,
        **summary,
    }
    LAST_RUN_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_error_report(errors: list[str]) -> None:
    LAST_ERROR_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = ["INGEST FAILED — errors:"]
    for err in errors[:12]:
        lines.append(f"  • {err}")
    if len(errors) > 12:
        lines.append(f"  … and {len(errors) - 12} more")
    lines.append(
        "Fix: check FRED_API_KEY and FINNHUB_API_KEY in .env, then retry End of Day."
    )
    LAST_ERROR_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _clear_error_report() -> None:
    LAST_ERROR_PATH.unlink(missing_ok=True)


def _print_failure(errors: list[str]) -> None:
    """Print failure to stdout so Desktop app Activity log always captures it."""
    print("INGEST FAILED — errors:")
    for err in errors[:12]:
        print(f"  • {err}")
    if len(errors) > 12:
        print(f"  … and {len(errors) - 12} more")
    print(
        "Fix: check FRED_API_KEY and FINNHUB_API_KEY in .env, then retry End of Day."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 ingest — macro, quotes, metrics")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Symbols to ingest (default: all active watchlist symbols)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="SQLite path (default: data/agent.db)",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=60,
        help="Daily history window (default: 60)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Skip symbols with fresh quotes/bars (default: full refresh)",
    )
    parser.add_argument(
        "--after-close",
        action="store_true",
        help="Incremental with fresh quotes (2h) and daily bars (12h) — use after market close",
    )
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=20.0,
        help="Age threshold for incremental mode (default: 20)",
    )
    args = parser.parse_args()

    settings = Settings.from_env()
    if not settings.fred_api_key or not settings.finnhub_api_key:
        msg = "FRED_API_KEY and FINNHUB_API_KEY required in .env"
        print(f"ERROR: {msg}")
        _write_error_report([msg])
        sys.exit(2)

    incremental = args.incremental or args.after_close
    quote_stale = None
    bar_stale = None
    mode = "full"
    if args.after_close:
        mode = "after_close"
        quote_stale = AFTER_CLOSE_QUOTE_STALE_HOURS
        bar_stale = AFTER_CLOSE_BAR_STALE_HOURS
    elif args.incremental:
        mode = "incremental"

    try:
        summary = run_ingest(
            settings,
            tickers=args.tickers,
            db_path=args.db,
            lookback_days=args.lookback_days,
            incremental=incremental,
            stale_hours=args.stale_hours,
            quote_stale_hours=quote_stale,
            bar_stale_hours=bar_stale,
        )
    except Exception as exc:
        errors = [f"crash: {exc}"]
        _write_last_run(
            {
                "ok": False,
                "partial": False,
                "errors": errors,
                "error_count": 1,
            },
            mode=mode,
        )
        _write_error_report(errors)
        _print_failure(errors)
        print(traceback.format_exc())
        sys.exit(1)

    _write_last_run(summary, mode=mode)
    print(json.dumps(summary, indent=2))
    if summary.get("ok"):
        _clear_error_report()
        sys.exit(0)
    if summary.get("partial"):
        _clear_error_report()
        print(
            f"\nPartial success: {summary.get('bars_refreshed', 0)} bars, "
            f"{summary.get('quotes_refreshed', 0)} quotes refreshed "
            f"({summary.get('error_count', 0)} errors). Re-run to retry failures.",
        )
        sys.exit(0)

    errors = list(summary.get("errors") or [])
    if not errors:
        errors = ["unknown ingest failure (no error details captured)"]
    _write_error_report(errors)
    _print_failure(errors)
    sys.exit(1)


if __name__ == "__main__":
    main()
