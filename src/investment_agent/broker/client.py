"""Broker client interface — Robinhood live adapter plugs in later."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class BrokerAccountSnapshot:
    external_account_id: str
    equity: float
    cash: float
    buying_power: float | None
    positions: list[dict[str, Any]]
    open_orders: list[dict[str, Any]]
    fills: list[dict[str, Any]]
    raw: dict[str, Any] | None = None
    is_paper: bool = True


class BrokerClient(Protocol):
    def fetch_account_snapshot(self) -> BrokerAccountSnapshot: ...


class StubBrokerClient:
    """Deterministic client for dry-run / tests until RH credentials arrive."""

    def __init__(self, snapshot: BrokerAccountSnapshot) -> None:
        self._snapshot = snapshot

    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        return self._snapshot


def fixture_paper_snapshot(
    *,
    equity: float = 5_000.0,
    cash: float = 5_000.0,
    account_id: str = "rh-paper-fixture-001",
) -> BrokerAccountSnapshot:
    return BrokerAccountSnapshot(
        external_account_id=account_id,
        equity=equity,
        cash=cash,
        buying_power=cash,
        positions=[],
        open_orders=[],
        fills=[],
        raw={"source": "fixture"},
        is_paper=True,
    )
