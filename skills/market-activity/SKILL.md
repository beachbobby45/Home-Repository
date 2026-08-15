---
name: market-activity
description: Phase 1B Market Activity Engine — 0–100 day score, TRADE/NO TRADE/EXCEPTIONAL bands, bull gate. Planned Inc 12. Do not implement until PHASE1B spec approved.
---

# Market Activity Engine (Phase 1B — Planned)

## Status

**Implemented (Inc 12).** Baseline scoring v0 with bull gate and flip detection.

## When to use

- Implementing day-level authorization (is today worth trading?)
- Pre-open, 9:30, 9:45 ET score passes
- Red **DO NOT TRADE TODAY** banner input
- Intraday degradation / flip detection

## Will own (future)

- `src/investment_agent/market_activity.py` (new)
- Snapshot readers from quote_snapshots table
- Tests: `tests/test_market_activity.py`

## Do not touch without coordination

- `regime.py` — may wrap or extend, not duplicate blindly
- Opportunity score — different layer (**opportunity-engine**)

## Business rules (approved direction)

| Band | Score (hypothesis) | New entries |
|------|-------------------|-------------|
| Exceptional | 90+ | Yes; #1–#3 if confirm |
| Above average | 75–89 | Yes; #1 primary |
| Average and below | <75 | **NO TRADE** |
| Not bull | SPY 20d ≤ 0 + weak today | **NO TRADE** |

**Average = NO TRADE** (strict gate).

## Weight table v0 (renormalize when n/a)

| Component | Weight | Free tier |
|-----------|-------:|-----------|
| Market direction | 20% | SPY/QQQ/DIA |
| Market volume | 15% | snapshot proxy |
| Market breadth | 15% | n/a v0 |
| Volatility | 10% | VIX |
| Momentum | 15% | daily bars |
| Sector participation | 10% | sector ETF RS |
| VWAP/trend | 10% | n/a v0 |
| News/catalysts | 5% | macro flag |

## Evaluation schedule (ET)

1. Pre-open — preliminary
2. 9:30 — open match/improve
3. 9:45 — authoritative day type
4. Each refresh — detect flip → exit alert if holding

## Tests (when implemented)

```bash
python3 -m pytest tests/test_market_activity.py -q
```

## Related docs (to be added Inc 9)

- `docs/PHASE1B_MARKET_ACTIVITY.md` (draft pending)

## Dependencies

- Inc 11 quote snapshots (**eod-ingest-screener** / **intraday-trading-day**)
- Inc 14 dashboard banner (**dashboard-ux**)
