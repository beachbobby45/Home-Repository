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
# Add ANTHROPIC_API_KEY, FRED_API_KEY, FINNHUB_API_KEY

pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 scripts/verify_access.py
```

Gate 0 must pass before Phase 1.

## v3 highlights

- **CIO + sub-agents** (research, stock team, regime, monitor, learning) — one repo
- **$7 buy / $7 sell** fees in P&amp;L model
- **Month-end sweeps:** 10% management + **editable** 25% tax reserve on **realized gains only**
- **No Alpaca orders**; optional Massive for backtest later
- **Progress:** `% of $5M goal` month by month

## Status

| Phase | Status |
|-------|--------|
| 0 — Foundation | **In progress** (code); awaiting your `.env` Gate 0 |
| 1 — Data pipeline | Not started |
