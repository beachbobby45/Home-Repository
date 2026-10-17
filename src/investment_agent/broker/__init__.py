"""Broker adapters — Robinhood is the ledger; dashboard mirrors sync tables."""

from investment_agent.broker.client import (
    BrokerAccountSnapshot,
    StubBrokerClient,
    fixture_paper_snapshot,
)
from investment_agent.broker.sync import (
    latest_broker_balance,
    sync_account_snapshot,
    sync_from_client,
)

BROKER_ROBINHOOD = "robinhood"

__all__ = [
    "BROKER_ROBINHOOD",
    "BrokerAccountSnapshot",
    "StubBrokerClient",
    "fixture_paper_snapshot",
    "latest_broker_balance",
    "sync_account_snapshot",
    "sync_from_client",
]
