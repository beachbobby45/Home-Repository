"""FRED API client (macro — Phase 1)."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def fetch_latest_observation(
    api_key: str,
    series_id: str,
    client: httpx.Client | None = None,
) -> tuple[str, float]:
    """Return (observation_date, value) for the latest observation."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    own_client = client is None
    if own_client:
        client = httpx.Client(timeout=30.0)
    try:
        resp = client.get(FRED_BASE, params=params)
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        if not obs:
            raise ValueError(f"No observations for {series_id}")
        row = obs[0]
        value = float(row["value"])
        return row["date"], value
    finally:
        if own_client:
            client.close()


def fetch_vix(api_key: str, client: httpx.Client | None = None) -> tuple[str, float]:
    return fetch_latest_observation(api_key, "VIXCLS", client=client)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
