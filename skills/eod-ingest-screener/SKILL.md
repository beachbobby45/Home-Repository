---
name: eod-ingest-screener
description: EOD ingest, FRED/Finnhub/yfinance data, 14-day period screener, ranked live candidates. Use for after-close pipelines, historical bars, watchlist metrics, and period_screener changes.
---

# EOD Ingest & 14-Day Screener

## When to use

- End-of-day or scheduled ingest (`run_ingest.py`, `run_end_of_day_mac.sh`)
- Period screener / ranked candidates (`run_period_screener.py`)
- OHLCV, quotes, liquidity metrics, data freshness
- Watchlist universe changes

## Owns (may edit)

- `src/investment_agent/ingest.py`
- `src/investment_agent/period_screener.py`
- `src/investment_agent/historical.py`
- `src/investment_agent/watchlist.py`
- `src/investment_agent/liquidity.py`
- `src/investment_agent/dollar_target.py` (historical hit-rate sim only)
- `src/investment_agent/providers/finnhub.py`, `fred.py`, `yfinance_bars.py`
- `scripts/run_ingest.py`, `run_period_screener.py`, `run_historical.py`
- `tests/test_ingest.py`, `test_historical.py`, `test_trading_days_period.py`, `test_data_freshness.py`

## Do not touch (unless task explicitly crosses domains)

- `trading_day.py` intraday gates → use **intraday-trading-day** skill
- `opportunity_score.py` composite weights → use **opportunity-engine** skill
- Dashboard HTML → use **dashboard-ux** skill

## Rules

1. Respect Finnhub rate limit (~1 req/sec) in `FinnhubClient`.
2. Incremental ingest: skip fresh quotes/bars when configured.
3. Screener uses **trading days**, not calendar days (14d window).
4. `live_pass_today` and dollar rank gate feed the Opportunity Engine — do not remove without spec update.
5. Free tier only — no paid data assumptions.

## Data flow

```text
FRED + Finnhub quotes + yfinance daily bars
  → ohlcv_daily, quotes, ticker_metrics, regime_snapshots
  → period_screener.build_ranked_candidates()
  → ranked list (#1, #2, #3…) for next session
```

## Tests

```bash
python3 -m pytest tests/test_ingest.py tests/test_historical.py tests/test_trading_days_period.py tests/test_data_freshness.py -q
```

## Related docs

- `docs/PHASE1_TECHNICAL_AUDIT.md` § Market Data
- `docs/DASHBOARD_ONE_PAGER.md` Step 1 (EOD)

## Phase 1B notes (Inc 11)

- Add **quote snapshot** storage at pre-open, 9:30, 9:45 ET for market/confirmation engines.
- Extend ingest or `trading_day.refresh_live_quotes` — coordinate with **intraday-trading-day** skill.
