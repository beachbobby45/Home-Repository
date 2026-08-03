"""Trading strategy constants (Product Spec v3)."""

from __future__ import annotations

TARGET_PCT = 1.50
STOP_PCT = 0.75
MAX_TRADES_PER_DAY = 2
ENTRY_DELAY_MINUTES = 30
STOP_DAY_AFTER_STOP = True
ENTRY_WINDOW_ET = "10:00–14:30"

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

# Queue states polled by intraday monitor (Phase 4)
MONITORED_STATES = ("armed", "alert", "in_trade", "eod")

ALERT_TYPES = (
    "TARGET_HIT",
    "STOP_HIT",
    "EOD_FLATTEN",
    "NEAR_TARGET",
    "NEAR_STOP",
)

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
