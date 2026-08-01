"""Trading strategy constants (Product Spec v3)."""

from __future__ import annotations

TARGET_PCT = 1.13
STOP_PCT = 0.50

QUEUE_STATES = (
    "watching",
    "approved",
    "armed",
    "alert",
    "in_trade",
    "eod",
    "closed",
    "runner",
)

ACTIVE_QUEUE_STATES = ("watching", "approved", "armed", "alert", "in_trade", "eod", "runner")

# Indices used for regime — not primary trade candidates
REGIME_ONLY_TICKERS = frozenset({"SPY", "DIA", "QQQ"})

NEXT_STATE: dict[str, str | None] = {
    "watching": "approved",
    "approved": "armed",
    "armed": "alert",
    "alert": "in_trade",
    "in_trade": "eod",
    "eod": "closed",
    "closed": "runner",
    "runner": None,
}
