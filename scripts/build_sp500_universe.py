#!/usr/bin/env python3
"""Refresh universe/sp500.txt from the public S&P 500 constituents CSV."""

from __future__ import annotations

import csv
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "universe" / "sp500.txt"
CSV_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"


def fetch_sp500_symbols() -> list[str]:
    with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
        rows = list(csv.DictReader(resp.read().decode().splitlines()))
    symbols: list[str] = []
    seen: set[str] = set()
    for row in rows:
        sym = row["Symbol"].strip().upper().replace(".", "-")
        if sym and sym not in seen:
            seen.add(sym)
            symbols.append(sym)
    for etf in ("SPY", "DIA", "QQQ"):
        if etf not in seen:
            symbols.insert(0, etf)
            seen.add(etf)
    return symbols


def write_sp500_file(path: Path | None = None) -> int:
    target = path or OUT
    symbols = fetch_sp500_symbols()
    lines = [
        "# S&P 500 constituents + regime ETFs (SPY/DIA/QQQ)",
        "# Source: https://github.com/datasets/s-and-p-500-companies",
        *symbols,
    ]
    target.write_text("\n".join(lines) + "\n")
    return len(symbols)


def main() -> None:
    count = write_sp500_file()
    print(f"Wrote {count} tickers to {OUT}")
    sys.exit(0)


if __name__ == "__main__":
    main()
