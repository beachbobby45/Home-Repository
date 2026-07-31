"""Finnhub API client (quotes + daily candles — Phase 1)."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import httpx

FINNHUB_BASE = "https://finnhub.io/api/v1"


class FinnhubClient:
    def __init__(
        self,
        api_key: str,
        min_interval_sec: float = 1.05,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.min_interval_sec = min_interval_sec
        self._client = client or httpx.Client(timeout=30.0)
        self._owns_client = client is None
        self._last_call = 0.0

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_call
        if elapsed < self.min_interval_sec:
            time.sleep(self.min_interval_sec - elapsed)
        self._last_call = time.monotonic()

    def get_quote(self, symbol: str) -> dict:
        self._throttle()
        resp = self._client.get(
            f"{FINNHUB_BASE}/quote",
            params={"symbol": symbol.upper(), "token": self.api_key},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("c") in (None, 0):
            raise ValueError(f"Invalid quote for {symbol}: {data}")
        return data

    def get_daily_candles(
        self,
        symbol: str,
        from_ts: int,
        to_ts: int,
    ) -> list[dict]:
        self._throttle()
        resp = self._client.get(
            f"{FINNHUB_BASE}/stock/candle",
            params={
                "symbol": symbol.upper(),
                "resolution": "D",
                "from": from_ts,
                "to": to_ts,
                "token": self.api_key,
            },
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("s") != "ok":
            raise ValueError(f"Candle fetch failed for {symbol}: {payload}")
        rows = []
        for i, ts in enumerate(payload["t"]):
            rows.append(
                {
                    "ticker": symbol.upper(),
                    "date": datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
                        "%Y-%m-%d"
                    ),
                    "open": float(payload["o"][i]),
                    "high": float(payload["h"][i]),
                    "low": float(payload["l"][i]),
                    "close": float(payload["c"][i]),
                    "volume": int(payload["v"][i]),
                    "source": "finnhub",
                }
            )
        return rows


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
