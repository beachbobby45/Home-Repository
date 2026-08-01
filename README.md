# AI Investment Agent (Product Spec v3)

Intraday **alerting and analysis** system: CIO + sub-agents → dashboard recommendations (+1.13% / −0.50%, ~3% swing proof). **You** execute in **E*TRADE** and log trades. Target goal tracking: **$5M** from **$10K** basis.

## Documentation

| Doc | Purpose |
|-----|---------|
| **[PRODUCT_SPEC_V3.md](docs/PRODUCT_SPEC_V3.md)** | **Authoritative** product & financial rules |
| **[PHASE_0.md](docs/PHASE_0.md)** | Gate 0 checklist |
| **[FEES_AT_A_GLANCE.md](docs/FEES_AT_A_GLANCE.md)** | API costs |
| **[AI_Investment_Agent_Spec.md](docs/AI_Investment_Agent_Spec.md)** | Technical appendix (gates, schemas; some v2 items superseded by v3) |

## Phase 0 — Start here

```bash
cp .env.example .env
# Add FRED_API_KEY, FINNHUB_API_KEY (ANTHROPIC later when you add ~$25 credits)

pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 scripts/verify_access.py --no-claude
```

Gate 0 must pass before Phase 1. Use full `verify_access.py` once Anthropic credits are added.

## Phase 1 — Data ingest (no Claude)

```bash
PYTHONPATH=src python3 scripts/run_ingest.py
PYTHONPATH=src python3 scripts/run_ingest.py --tickers SPY AAPL
```

Fetches FRED macro (VIX), Finnhub live quotes, yfinance daily bars, liquidity metrics, and SPY/DIA/QQQ regime gate.

## Phase 2–3 — Dashboard (no Claude)

```bash
PYTHONPATH=src python3 scripts/sync_queue.py      # populate queue from screener
PYTHONPATH=src python3 scripts/run_dashboard.py   # http://127.0.0.1:8080
```

Dashboard: **$5M goal**, tradable cash, month P&amp;L, sweep preview, regime banner, trade queue, manual journal.

## v3 highlights

- **CIO + sub-agents** (research, stock team, regime, monitor, learning) — one repo
- **$7 buy / $7 sell** fees in P&amp;L model
- **Month-end sweeps:** 10% management + **editable** 25% tax reserve on **realized gains only**
- **No Alpaca orders**; optional Massive for backtest later
- **Progress:** `% of $5M goal` month by month

## Status

| Phase | Status |
|-------|--------|
| 0 — Foundation | **Done** (Option A: `--no-claude` Gate 0) |
| 1 — Data pipeline | **Done** (ingest + regime gate) |
| 2–3 — Screener + dashboard | **Done** (queue, journal, goal, sweeps) |
| 4 — Intraday monitor | Not started |
