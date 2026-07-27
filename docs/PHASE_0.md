# Phase 0 — Foundation (Product Spec v3)

## Goal

Verify API access, project skeleton, and financial model helpers before Phase 1 data pipeline.

## Required keys

| Key | Signup |
|-----|--------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `FRED_API_KEY` | [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/useraccount/apikey) |
| `FINNHUB_API_KEY` | [finnhub.io](https://finnhub.io) |

**Not required:** Alpaca (v3 uses **E*TRADE manual** execution).

## Commands

```bash
cp .env.example .env
# Edit .env with your keys

pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 scripts/verify_access.py
```

## Gate 0 pass criteria

- All tests pass
- `verify_access.py` exit code **0** for anthropic, fred, finnhub
- Massive optional (skip if no key)

## Deliverables (Phase 0)

- [x] `docs/PRODUCT_SPEC_V3.md` — authoritative product spec
- [x] `src/investment_agent/finance.py` — fees, goal %, month-end sweeps
- [x] `scripts/verify_access.py` — v3 required APIs
- [ ] **You:** `.env` filled + Gate 0 run on your machine

## Next: Phase 1

Data ingestion (Finnhub + FRED), liquidity + swing stats, SQLite schema expansion.
