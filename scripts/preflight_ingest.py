#!/usr/bin/env python3
"""Quick checks before ingest — runs in a few seconds."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings  # noqa: E402
from investment_agent.db_maintenance import (  # noqa: E402
    clear_stale_ingest_lock,
    ingest_lock_active,
    ingest_lock_message,
)
from investment_agent.providers.finnhub import FinnhubClient  # noqa: E402
from investment_agent.providers.fred import fetch_vix  # noqa: E402


def _check_pandas_numpy() -> int | None:
    import platform

    label = f"{platform.python_version()} · {sys.executable}"
    try:
        import numpy  # noqa: F401
        import pandas  # noqa: F401
    except ImportError as exc:
        msg = str(exc)
        print(f"ERROR: pandas/numpy not usable with this Python ({label})")
        if "incompatible architecture" in msg or "mach-o" in msg.lower():
            print(
                "  Cause: NumPy was built for a different CPU (arm64 vs x86_64). "
                "Common when /usr/local/bin/python3 is used on Apple Silicon."
            )
        else:
            print(f"  {msg}")
        print("Fix: run once in Terminal: ./scripts/fix_ingest_python_mac.sh")
        return 5
    print(f"Checking pandas/numpy ({platform.machine()})…")
    print("  OK — imports work")
    return None


def main() -> int:
    code = _check_pandas_numpy()
    if code is not None:
        return code

    clear_stale_ingest_lock()
    if ingest_lock_active():
        print(f"ERROR: {ingest_lock_message()}")
        print("Fix: wait for the other ingest to finish, or check Terminal for run_ingest_mac.sh")
        return 1

    settings = Settings.from_env()
    missing = []
    if not settings.fred_api_key.strip():
        missing.append("FRED_API_KEY")
    if not settings.finnhub_api_key.strip():
        missing.append("FINNHUB_API_KEY")
    if missing:
        print("ERROR: Missing in .env:", ", ".join(missing))
        print("Fix: add keys to Home-Repository/.env then retry End of Day.")
        return 2

    print("Checking FRED (VIX)…")
    try:
        obs_date, vix = fetch_vix(settings.fred_api_key)
        print(f"  OK — VIXCLS={vix} on {obs_date}")
    except Exception as exc:
        print(f"ERROR: FRED API failed: {exc}")
        print("Fix: verify FRED_API_KEY at https://fred.stlouisfed.org/docs/api/api_key.html")
        return 3

    print("Checking Finnhub (SPY quote)…")
    fh = FinnhubClient(settings.finnhub_api_key)
    try:
        q = fh.get_quote("SPY")
        price = q.get("c")
        if price is None or float(price) <= 0:
            print("ERROR: Finnhub returned no price for SPY — check FINNHUB_API_KEY")
            return 4
        print(f"  OK — SPY ${float(price):.2f}")
    except Exception as exc:
        print(f"ERROR: Finnhub failed: {exc}")
        print("Fix: verify FINNHUB_API_KEY at https://finnhub.io/dashboard")
        return 4
    finally:
        fh.close()

    print("Preflight passed — ingest can run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
