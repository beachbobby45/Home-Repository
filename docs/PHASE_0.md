# Phase 0 — Foundation (Product Spec v3)

## Goal

Verify API access, project skeleton, and financial model helpers before Phase 1 data pipeline.

## Required keys

| Key | Signup | Required now (Option A) |
|-----|--------|-------------------------|
| `FRED_API_KEY` | [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/useraccount/apikey) | **Yes** |
| `FINNHUB_API_KEY` | [finnhub.io](https://finnhub.io) | **Yes** (quotes) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | **Later** (~$25 credits) |

**Not required:** Alpaca (v3 uses **E*TRADE manual** execution).

Daily history uses **yfinance** (free). Finnhub `/stock/candle` is paid-only on free accounts.

## Commands

```bash
cp .env.example .env
# Edit .env with your keys

pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 scripts/verify_access.py --no-claude
```

## Gate 0 pass criteria

- All tests pass
- `verify_access.py --no-claude` exit code **0** for fred + finnhub (Option A — no Claude yet)
- When Anthropic credits are added: `verify_access.py` (full) exit code **0**
- Massive optional (skip if no key)

## Deliverables (Phase 0)

- [x] `docs/PRODUCT_SPEC_V3.md` — authoritative product spec
- [x] `src/investment_agent/finance.py` — fees, goal %, month-end sweeps
- [x] `scripts/verify_access.py` — v3 required APIs
- [ ] **You:** `.env` filled + Gate 0 run on your machine

## Next: Phase 1

Data ingestion (FRED + Finnhub quotes + yfinance daily bars), liquidity + swing stats, regime gate (SPY/DIA/QQQ), SQLite schema.
