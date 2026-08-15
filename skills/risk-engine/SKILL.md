---
name: risk-engine
description: Independent Risk Engine — approves or rejects proposals. LLM and strategy never override. Use for position limits, daily/weekly loss, drawdown, kill switch, min R:R.
---

# Risk Engine

## When to use

- Per-proposal and portfolio-level risk checks
- Kill switch, high-water mark, drawdown
- Daily / weekly loss limits, max open positions, max trades per day
- Risk API and dashboard risk panel

## Owns (may edit)

- `src/investment_agent/risk_engine.py`
- `tests/test_risk_engine.py`

## Do not touch

- Tradability intraday filters → **intraday-trading-day** / **confirmation-engine**
- Opportunity scoring → **opportunity-engine**
- `regime.py` index logic → **intraday-trading-day** (Risk consumes `block_new_longs`)

## Rules

1. **Sovereign gate** — rejected proposals cannot become human_approved without spec violation.
2. Defaults (Phase 1): 1% max risk/trade, 2% daily loss, 5% weekly loss, 10% max drawdown, min 1.5 R:R, max 2 open positions.
3. Kill switch auto-engages on drawdown breach — human must clear intentionally.
4. Risk runs at proposal creation **and** pre-approve refresh.

## Tests

```bash
python3 -m pytest tests/test_risk_engine.py -q
```

## Related docs

- `docs/PHASE1_CAPITAL_BUILDER_SPEC.md` §5.3 Risk Engine

## Phase 1B notes

- Market Activity NO TRADE should block **new entries** before Risk Engine (coordination, not replacement).
- Exceptional weekly trade still must pass full Risk Engine.
