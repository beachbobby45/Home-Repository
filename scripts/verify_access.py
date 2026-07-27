#!/usr/bin/env python3
"""
Gate 0 — verify required external API connections (Product Spec v3).

Required: anthropic, fred, finnhub.
Optional: massive. Alpaca not used (E*TRADE manual execution).

Usage:
    python scripts/verify_access.py              # required + optional massive
    python scripts/verify_access.py --check anthropic
    python scripts/verify_access.py --check fred
    python scripts/verify_access.py --check finnhub
    python scripts/verify_access.py --check massive   # optional

Exit codes:
    0 = all required checks passed
    1 = one or more required checks failed
    2 = configuration error (missing .env keys)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow running from repo root without installing the package
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import httpx

from investment_agent.config import Settings, load_env, missing_required_keys


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    required: bool = True


def check_alpaca(settings: Settings) -> CheckResult:
    """Optional legacy check — skipped unless Alpaca keys are set."""
    if not settings.alpaca_api_key or not settings.alpaca_secret_key:
        return CheckResult(
            "alpaca",
            True,
            "Skipped — optional; v3 uses E*TRADE manual execution",
            required=False,
        )
    return CheckResult(
        "alpaca",
        True,
        "Keys present (optional data-only; not required for Gate 0)",
        required=False,
    )


def check_anthropic(settings: Settings) -> CheckResult:
    """
    Verify Anthropic API with a minimal Haiku call (cheapest model for Gate 0).

    Note: This consumes a small amount of credits. Check your Console billing
    balance before and after. Official docs confirm new users receive a small
    amount of free credits — exact amount varies by account/region.
    """
    if not settings.anthropic_api_key:
        return CheckResult("anthropic", False, "Missing ANTHROPIC_API_KEY")

    try:
        import anthropic
    except ImportError:
        return CheckResult(
            "anthropic",
            False,
            "anthropic SDK not installed — run: pip install -r requirements.txt",
        )

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=16,
            temperature=0,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        )
        text = response.content[0].text if response.content else ""
        usage = response.usage
        input_tokens = usage.input_tokens if usage else 0
        output_tokens = usage.output_tokens if usage else 0

        return CheckResult(
            "anthropic",
            True,
            f"API OK — model=claude-haiku-4-5, "
            f"tokens in={input_tokens} out={output_tokens}, "
            f"reply={text[:20]!r}. "
            f"Check Console billing for remaining credits.",
        )
    except Exception as exc:
        err = str(exc)
        if "credit" in err.lower() or "billing" in err.lower() or "balance" in err.lower():
            return CheckResult(
                "anthropic",
                False,
                f"Billing/credits error: {exc}. "
                f"Add credits at console.anthropic.com → Billing.",
            )
        return CheckResult("anthropic", False, f"Anthropic error: {exc}")


def check_fred(settings: Settings) -> CheckResult:
    """Verify FRED API with VIXCLS (VIX) series."""
    if not settings.fred_api_key:
        return CheckResult("fred", False, "Missing FRED_API_KEY")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "VIXCLS",
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        obs = data.get("observations", [])
        if not obs:
            return CheckResult("fred", False, "No VIXCLS observations returned")
        value = obs[0].get("value")
        date = obs[0].get("date")
        return CheckResult("fred", True, f"VIXCLS latest: {value} on {date}")
    except Exception as exc:
        return CheckResult("fred", False, f"FRED error: {exc}")


def check_finnhub(settings: Settings) -> CheckResult:
    """Verify Finnhub quote endpoint."""
    if not settings.finnhub_api_key:
        return CheckResult("finnhub", False, "Missing FINNHUB_API_KEY")

    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": settings.verify_test_ticker, "token": settings.finnhub_api_key}
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        price = data.get("c")
        if price is None or price <= 0:
            return CheckResult(
                "finnhub",
                False,
                f"Invalid quote for {settings.verify_test_ticker}: {data}",
            )
        return CheckResult(
            "finnhub",
            True,
            f"{settings.verify_test_ticker} current price: ${price:.2f}",
        )
    except Exception as exc:
        return CheckResult("finnhub", False, f"Finnhub error: {exc}")


def check_massive(settings: Settings) -> CheckResult:
    """Optional: verify Massive/Polygon API."""
    if not settings.massive_api_key:
        return CheckResult(
            "massive",
            True,
            "Skipped — MASSIVE_API_KEY not set (optional)",
            required=False,
        )

    # Massive REST endpoint (formerly Polygon)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{settings.verify_test_ticker}/range/"
        f"1/day/{week_ago}/{today}"
    )
    params = {"apiKey": settings.massive_api_key, "limit": 1}
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 429:
                return CheckResult(
                    "massive",
                    True,
                    "Key valid but rate-limited (429) — expected on free tier",
                    required=False,
                )
            resp.raise_for_status()
            data = resp.json()
        results = data.get("results", [])
        if not results:
            return CheckResult(
                "massive",
                False,
                f"No aggregate data for {settings.verify_test_ticker}",
                required=False,
            )
        return CheckResult(
            "massive",
            True,
            f"Historical agg OK for {settings.verify_test_ticker}",
            required=False,
        )
    except Exception as exc:
        return CheckResult("massive", False, f"Massive error: {exc}", required=False)


CHECKS = {
    "alpaca": check_alpaca,
    "anthropic": check_anthropic,
    "fred": check_fred,
    "finnhub": check_finnhub,
    "massive": check_massive,
}

REQUIRED_CHECKS = ["anthropic", "fred", "finnhub"]
DEFAULT_CHECKS = REQUIRED_CHECKS + ["massive"]


def run_checks(selected: list[str] | None = None) -> list[CheckResult]:
    load_env()
    settings = Settings.from_env()
    missing = missing_required_keys(settings)
    if missing and (selected is None or any(c in REQUIRED_CHECKS for c in (selected or []))):
        print("ERROR: Missing required environment variables:")
        for name in missing:
            print(f"  - {name}")
        print("\nCopy .env.example to .env and fill in your keys.")
        print("See docs/FEES_AT_A_GLANCE.md for signup links and costs.")
        sys.exit(2)

    names = selected or DEFAULT_CHECKS
    results = []
    for name in names:
        fn = CHECKS.get(name)
        if fn is None:
            print(f"Unknown check: {name}")
            sys.exit(2)
        results.append(fn(settings))
    return results


def print_results(results: list[CheckResult]) -> int:
    print("\nGate 0 — API Access Verification")
    print("=" * 50)
    required_failed = False
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        tag = "required" if result.required else "optional"
        print(f"[{status}] {result.name} ({tag})")
        print(f"       {result.message}")
        if not result.passed and result.required:
            required_failed = True

    print("=" * 50)
    if required_failed:
        print("RESULT: Gate 0 FAILED — resolve errors before building.")
        return 1
    print("RESULT: Gate 0 PASSED — all required connections verified.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify external API access (Gate 0)")
    parser.add_argument(
        "--check",
        choices=list(CHECKS.keys()),
        action="append",
        help="Run a specific check (can repeat). Default: all checks.",
    )
    args = parser.parse_args()
    results = run_checks(args.check)
    sys.exit(print_results(results))


if __name__ == "__main__":
    main()
