"""5-minute bar fill/exit simulation for the paper ledger (same rules as blocked-day analysis)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.backtest import _bar_exit_price
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE

ET = ZoneInfo("America/New_York")


def _bar_time_et(bar: dict) -> datetime | None:
    ts = bar.get("ts")
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ET)
    return dt.astimezone(ET)


def simulate_round_trip_5m(
    day_bars: list[dict],
    *,
    buy: float,
    sell: float,
    stop: float,
    shares: int,
    buy_fee: float,
    sell_fee: float,
    as_of_et: datetime | None = None,
) -> dict[str, Any]:
    """Walk 5m bars for fill by 11:30 ET then target/stop/EOD.

    If ``as_of_et`` is set (live paper during the session), only bars at/before
    that time are considered — unfinished days may return ``open_waiting``.
    """
    if not day_bars:
        return {
            "scenario": "no_5m_bars",
            "filled": False,
            "net_pnl": None,
            "complete": True,
            "detail": "No 5m bars for this ticker/date",
        }

    bars = day_bars
    if as_of_et is not None:
        bars = []
        for bar in day_bars:
            t = _bar_time_et(bar)
            if t is not None and t <= as_of_et:
                bars.append(bar)
        if not bars:
            return {
                "scenario": "waiting_for_bars",
                "filled": False,
                "net_pnl": None,
                "complete": False,
                "detail": "No 5m bars yet today",
            }

    fill_bar = None
    fill_ts = None
    for bar in bars:
        t = _bar_time_et(bar)
        if t is None:
            continue
        if t.time() > LIMIT_FILL_DEADLINE:
            break
        if float(bar["low"]) <= buy:
            fill_bar = bar
            fill_ts = t.isoformat()
            break

    if fill_bar is None:
        # Past deadline with full day → no fill; still during morning → waiting
        last_t = _bar_time_et(bars[-1]) if bars else None
        if as_of_et is not None and (
            last_t is None or last_t.time() <= LIMIT_FILL_DEADLINE
        ):
            return {
                "scenario": "waiting_for_fill",
                "filled": False,
                "net_pnl": None,
                "complete": False,
                "detail": f"Limit ${buy:.2f} not touched yet (deadline 11:30 ET)",
            }
        return {
            "scenario": "no_fill_by_1130",
            "filled": False,
            "net_pnl": 0.0,
            "complete": True,
            "detail": f"Limit ${buy:.2f} not touched by 11:30 ET",
        }

    started = False
    for bar in bars:
        t = _bar_time_et(bar)
        if t is None:
            continue
        if not started:
            if bar is fill_bar or (fill_ts and t.isoformat() == fill_ts):
                started = True
            else:
                continue
            exit_px, reason = _bar_exit_price(target=sell, stop=stop, bar=bar)
            if exit_px is not None and reason is not None:
                net = round(shares * (exit_px - buy) - buy_fee - sell_fee, 2)
                return {
                    "scenario": f"exit_{reason}_same_bar_as_fill",
                    "filled": True,
                    "complete": True,
                    "fill_ts": fill_ts,
                    "exit_ts": t.isoformat(),
                    "exit_price": exit_px,
                    "exit_reason": reason,
                    "entry_price": buy,
                    "net_pnl": net,
                    "detail": f"Filled then {reason} on same 5m bar",
                }
            continue

        exit_px, reason = _bar_exit_price(target=sell, stop=stop, bar=bar)
        if exit_px is not None and reason is not None:
            net = round(shares * (exit_px - buy) - buy_fee - sell_fee, 2)
            return {
                "scenario": f"exit_{reason}",
                "filled": True,
                "complete": True,
                "fill_ts": fill_ts,
                "exit_ts": t.isoformat(),
                "exit_price": exit_px,
                "exit_reason": reason,
                "entry_price": buy,
                "net_pnl": net,
                "detail": f"Filled {fill_ts}; exited {reason} @ {exit_px:.2f}",
            }

    # Filled but no exit yet
    if as_of_et is not None:
        last = bars[-1]
        last_t = _bar_time_et(last)
        if last_t is None or last_t.time() < datetime.strptime("16:00", "%H:%M").time():
            return {
                "scenario": "open_waiting_exit",
                "filled": True,
                "complete": False,
                "fill_ts": fill_ts,
                "entry_price": buy,
                "exit_price": None,
                "exit_reason": None,
                "net_pnl": None,
                "detail": "Filled; waiting for target/stop/EOD",
            }

    last = bars[-1]
    last_t = _bar_time_et(last)
    close_px = float(last["close"])
    net = round(shares * (close_px - buy) - buy_fee - sell_fee, 2)
    return {
        "scenario": "exit_eod_close",
        "filled": True,
        "complete": True,
        "fill_ts": fill_ts,
        "exit_ts": last_t.isoformat() if last_t else None,
        "exit_price": close_px,
        "exit_reason": "eod_close",
        "entry_price": buy,
        "net_pnl": net,
        "detail": "Filled; EOD close exit",
    }
