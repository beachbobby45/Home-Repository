---
name: intraday-trading-day
description: Intraday go/no-go, live quote refresh, tradability, regime gate, extended session monitoring. Use for trading_day status, Step 3 refresh, top pick card logic.
---

# Intraday Trading Day

## When to use

- `build_trading_day_status`, session phases, GO/NO_GO/WAIT
- Refresh live quotes (`run_refresh_live.py`)
- Tradability assessment, top pick resolution
- Extended session row + fill assumption toggle
- Regime block (SPY/DIA/QQQ all down)

## Owns (may edit)

- `src/investment_agent/trading_day.py`
- `src/investment_agent/tradability.py`
- `src/investment_agent/regime.py`
- `scripts/run_refresh_live.py`
- `tests/test_trading_day.py`, `test_tradability.py`, `test_regime.py`

## Do not touch

- Full Market Activity score (Phase 1B) → **market-activity** — will be called from here
- Confirmation per stock → **confirmation-engine**
- Dashboard rendering → **dashboard-ux**

## Rules

1. **30-min gate:** entry readiness from 10:00 ET (`ENTRY_READY`).
2. Limit fill deadline **11:30 ET** — missed limit = skip, no chase.
3. Regime: all three indices down → `block_new_longs`.
4. Extended session: pre-market / after-hours / weekend — RTH estimates unchanged.
5. Fill assumption: journal open position locks **Filled**; else toggle Not filled / Filled.

## Session phases

`weekend | pre_market | opening_wait | trade_window | late_day | after_hours`

## Tests

```bash
python3 -m pytest tests/test_trading_day.py tests/test_tradability.py tests/test_regime.py -q
```

## Phase 1B notes (Inc 11–16)

- Pre-open, 9:30, 9:45 ET evaluation schedule.
- Wire Market Activity + Confirmation into status before pick is GO.
- Intraday flip to NO TRADE → exit alert if holding (dashboard skill).
- Keep ranked list visible with DO NOT TRADE banner.
