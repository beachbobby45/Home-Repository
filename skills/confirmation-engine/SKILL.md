---
name: confirmation-engine
description: Phase 1B Candidate Confirmation Score — does #1/#2/#3 confirm this morning? Planned Inc 13. Requires Market Activity ≥ Above Average first.
---

# Confirmation Engine (Phase 1B — Planned)

## Status

**Implemented (Inc 13).** Per-ticker confirmation on ranked #1–#3; never overrides NO TRADE day.

## When to use

- Per-stock confirmation at pre-open, 9:30, 9:45 ET
- Align ranked #1, #2, #3 with day type (Exceptional vs Above Average)
- PASS / TRADE chips on dashboard

## Will own (future)

- `src/investment_agent/confirmation.py` (new)
- `tests/test_confirmation.py`

## Rules (approved direction)

1. **Day authorizes first** (Market Activity) — confirmation never overrides NO TRADE.
2. High EOD opportunity score **does not** auto-trade without confirmation.
3. Exceptional day: multiple names may confirm; Above Average: #1 primary.

## Weight table v0 (hypothesis)

| Component | Weight |
|-----------|-------:|
| Relative volume | 20% |
| Volume acceleration | 15% |
| Price momentum | 15% |
| Relative strength | 15% |
| VWAP | 10% |
| Breakout/technical | 10% |
| Sector confirmation | 5% |
| News/catalyst | 10% |

Free tier: VWAP/acceleration use snapshot proxies; mark n/a when missing.

## Example decision matrix

| Stock | Opportunity (EOD) | Confirmation (AM) | Decision |
|-------|------------------:|------------------:|----------|
| NVDA | 94 | 93 | TRADE |
| AVGO | 91 | 76 | PASS |

## Tests (when implemented)

```bash
python3 -m pytest tests/test_confirmation.py -q
```

## Dependencies

- **market-activity** (day gate)
- **opportunity-engine** (ranked candidates)
- **intraday-trading-day** (wire into status)
