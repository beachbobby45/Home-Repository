"""Environment configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def load_env(env_file: str | None = None) -> None:
    """Load .env from project root if present."""
    if env_file:
        load_dotenv(env_file)
        return
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    fred_api_key: str
    finnhub_api_key: str
    massive_api_key: str | None
    verify_test_ticker: str
    app_api_key: str
    # Optional Alpaca (data only — not required v3)
    alpaca_api_key: str | None
    alpaca_secret_key: str | None

    @classmethod
    def from_env(cls) -> Settings:
        load_env()
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            fred_api_key=os.getenv("FRED_API_KEY", ""),
            finnhub_api_key=os.getenv("FINNHUB_API_KEY", ""),
            massive_api_key=os.getenv("MASSIVE_API_KEY") or None,
            verify_test_ticker=os.getenv("VERIFY_TEST_TICKER", "SPY"),
            app_api_key=os.getenv("APP_API_KEY", ""),
            alpaca_api_key=os.getenv("ALPACA_API_KEY") or None,
            alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY") or None,
        )


def missing_required_keys(
    settings: Settings,
    *,
    require_anthropic: bool = True,
) -> list[str]:
    """Return names of required env vars that are empty (v3: no Alpaca)."""
    required = {
        "FRED_API_KEY": settings.fred_api_key,
        "FINNHUB_API_KEY": settings.finnhub_api_key,
    }
    if require_anthropic:
        required["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    return [name for name, value in required.items() if not value.strip()]
