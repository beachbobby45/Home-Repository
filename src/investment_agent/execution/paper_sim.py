"""5-minute bar fill/exit simulation for the paper ledger.

Fill modes:
  - touch: bar extreme reaches the limit (legacy / optimistic)
  - trade_through: price must trade strictly through the limit (stricter; scoreboard default)
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE, LIMIT_FILL_DEADLINE_LABEL

ET = ZoneInfo("America/New_York")

FillMode = Literal["touch", "trade_through"]
FILL_MODE_TOUCH = "touch"
FILL_MODE_TRADE_THROUGH = "trade_through"
VALID_FILL_MODES = frozenset({FILL_MODE_TOUCH, FILL_MODE_TRADE_THROUGH})


def resolve_fill_mode(explicit: str | None = None) -> FillMode:
    raw = (explicit or os.getenv("PAPER_FILL_MODE", FILL_MODE_TRADE_THROUGH)).strip().lower()
    if raw not in VALID_FILL_MODES:
        return FILL_MODE_TRADE_THROUGH  # type: ignore[return-value]
    return raw  # type: ignore[return-value]


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


def _entry_hit(bar: dict, buy: float, mode: FillMode) -> bool:
    low = float(bar["low"])
    if mode == FILL_MODE_TRADE_THROUGH:
        return low < buy
    return low <= buy


def _bar_exit_price(
    *,
    target: float,
    stop: float,
    bar: dict,
    mode: FillMode,
) -> tuple[float | None, str | None]:
    h, l = float(bar["high"]), float(bar["low"])
    if mode == FILL_MODE_TRADE_THROUGH:
        hit_stop = l < stop
        hit_target = h > target
    else:
        hit_stop = l <= stop
        hit_target = h >= target
    if hit_stop and hit_target:
        return stop, "stop"
    if hit_stop:
        return stop, "stop"
    if hit_target:
        return target, "target"
    return None, None


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
    fill_mode: str | None = None,
) -> dict[str, Any]:
    """Walk 5m bars for fill by LIMIT_FILL_DEADLINE then target/stop/EOD."""
    mode = resolve_fill_mode(fill_mode)
    if not day_bars:
        # Empty feed before the fill deadline is temporary (Yahoo lag / pre-open).
        # Finalizing as no_5m_bars here locked paper books overnight (Oct 2026).
        # as_of_et is None → full-day / force_complete path → finalize.
        if as_of_et is not None:
            when = as_of_et
            if when.tzinfo is None:
                when = when.replace(tzinfo=ET)
            else:
                when = when.astimezone(ET)
            if when.timetz().replace(tzinfo=None) <= LIMIT_FILL_DEADLINE:
                return {
                    "scenario": "waiting_for_bars",
                    "filled": False,
                    "net_pnl": None,
                    "complete": False,
                    "fill_mode": mode,
                    "detail": (
                        "No 5m bars yet — waiting until "
                        f"{LIMIT_FILL_DEADLINE_LABEL} (or until bars arrive)"
                    ),
                }
        return {
            "scenario": "no_5m_bars",
            "filled": False,
            "net_pnl": None,
            "complete": True,
            "fill_mode": mode,
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
                "fill_mode": mode,
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
        if _entry_hit(bar, buy, mode):
            fill_bar = bar
            fill_ts = t.isoformat()
            break

    verb = "traded through" if mode == FILL_MODE_TRADE_THROUGH else "touched"
    if fill_bar is None:
        last_t = _bar_time_et(bars[-1]) if bars else None
        if as_of_et is not None and (
            last_t is None or last_t.time() <= LIMIT_FILL_DEADLINE
        ):
            return {
                "scenario": "waiting_for_fill",
                "filled": False,
                "net_pnl": None,
                "complete": False,
                "fill_mode": mode,
                "detail": (
                    f"Limit ${buy:.2f} not {verb} yet "
                    f"(deadline {LIMIT_FILL_DEADLINE_LABEL})"
                ),
            }
        return {
            # Historical scenario key (deadline was 11:30); keep for scoreboard/tests.
            "scenario": "no_fill_by_1130",
            "filled": False,
            "net_pnl": 0.0,
            "complete": True,
            "fill_mode": mode,
            "detail": (
                f"Limit ${buy:.2f} not {verb} by {LIMIT_FILL_DEADLINE_LABEL} ({mode})"
            ),
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
            exit_px, reason = _bar_exit_price(target=sell, stop=stop, bar=bar, mode=mode)
            if exit_px is not None and reason is not None:
                net = round(shares * (exit_px - buy) - buy_fee - sell_fee, 2)
                return {
                    "scenario": f"exit_{reason}_same_bar_as_fill",
                    "filled": True,
                    "complete": True,
                    "fill_mode": mode,
                    "fill_ts": fill_ts,
                    "exit_ts": t.isoformat(),
                    "exit_price": exit_px,
                    "exit_reason": reason,
                    "entry_price": buy,
                    "net_pnl": net,
                    "detail": f"Filled ({mode}) then {reason} on same 5m bar",
                }
            continue

        exit_px, reason = _bar_exit_price(target=sell, stop=stop, bar=bar, mode=mode)
        if exit_px is not None and reason is not None:
            net = round(shares * (exit_px - buy) - buy_fee - sell_fee, 2)
            return {
                "scenario": f"exit_{reason}",
                "filled": True,
                "complete": True,
                "fill_mode": mode,
                "fill_ts": fill_ts,
                "exit_ts": t.isoformat(),
                "exit_price": exit_px,
                "exit_reason": reason,
                "entry_price": buy,
                "net_pnl": net,
                "detail": f"Filled {fill_ts} ({mode}); exited {reason} @ {exit_px:.2f}",
            }

    if as_of_et is not None:
        last = bars[-1]
        last_t = _bar_time_et(last)
        if last_t is None or last_t.time() < datetime.strptime("16:00", "%H:%M").time():
            return {
                "scenario": "open_waiting_exit",
                "filled": True,
                "complete": False,
                "fill_mode": mode,
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
        "fill_mode": mode,
        "fill_ts": fill_ts,
        "exit_ts": last_t.isoformat() if last_t else None,
        "exit_price": close_px,
        "exit_reason": "eod_close",
        "entry_price": buy,
        "net_pnl": net,
        "detail": f"Filled ({mode}); EOD close exit",
    }
