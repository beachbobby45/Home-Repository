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
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_paper: bool
    alpaca_base_url: str
    anthropic_api_key: str
    fred_api_key: str
    finnhub_api_key: str
    massive_api_key: str | None
    verify_test_ticker: str

    @classmethod
    def from_env(cls) -> Settings:
        load_env()
        return cls(
            alpaca_api_key=os.getenv("ALPACA_API_KEY", ""),
            alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
            alpaca_paper=os.getenv("ALPACA_PAPER", "true").lower() == "true",
            alpaca_base_url=os.getenv(
                "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"
            ),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            fred_api_key=os.getenv("FRED_API_KEY", ""),
            finnhub_api_key=os.getenv("FINNHUB_API_KEY", ""),
            massive_api_key=os.getenv("MASSIVE_API_KEY") or None,
            verify_test_ticker=os.getenv("VERIFY_TEST_TICKER", "SPY"),
        )


def missing_required_keys(settings: Settings) -> list[str]:
    """Return names of required env vars that are empty."""
    required = {
        "ALPACA_API_KEY": settings.alpaca_api_key,
        "ALPACA_SECRET_KEY": settings.alpaca_secret_key,
        "ANTHROPIC_API_KEY": settings.anthropic_api_key,
        "FRED_API_KEY": settings.fred_api_key,
        "FINNHUB_API_KEY": settings.finnhub_api_key,
    }
    return [name for name, value in required.items() if not value.strip()]
