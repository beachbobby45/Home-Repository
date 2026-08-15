---
name: opportunity-engine
description: Multi-factor Opportunity Score (0–100), news significance, rule-based sentiment, ranking #1–#3. Use for scoring weights, factor computation, and EOD candidate quality — not intraday day authorization.
---

# Opportunity Engine

## When to use

- Opportunity Score composite and factor weights
- News significance + sentiment integration
- Ranking sort key for proposals and screener
- Claude-gated AI confidence (optional, ≤10/day)

## Owns (may edit)

- `src/investment_agent/opportunity_score.py`
- `src/investment_agent/news_service.py`
- `src/investment_agent/ai_service.py`
- `tests/test_opportunity_score.py`, `test_news_service.py`, `test_ai_service.py`

## Do not touch

- Intraday TRADE/NO TRADE → **market-activity** (Phase 1B)
- Per-stock morning confirmation → **confirmation-engine** (Phase 1B)
- Risk limits → **risk-engine**
- Proposal lifecycle → **trade-proposals**

## Rules

1. **Deterministic first** — rule-based sentiment default; Claude optional via `ANTHROPIC_API_KEY`.
2. Missing factors **renormalize** weights (see `composite_opportunity_score`).
3. `OPPORTUNITY_FLOOR = 65` — changing requires spec + tests.
4. Opportunity answers: *"Is this name structurally suitable over ~14 days?"*
5. **Never** merge intraday confirmation into opportunity score (different horizons).

## Factor map (Phase 1)

| Factor | Source module |
|--------|----------------|
| market_regime | `regime.py` / latest snapshot |
| technical_setup, momentum, RS, volume, volatility | bars + metrics |
| news_sentiment, news_significance | `news_service`, `ai_service` |
| earnings_events | calendar stub / significance |
| risk_reward, dollar_history | plan + `dollar_target` |
| ai_confidence | optional Claude |

## Tests

```bash
python3 -m pytest tests/test_opportunity_score.py tests/test_news_service.py tests/test_ai_service.py -q
```

## Related docs

- `docs/PHASE1_CAPITAL_BUILDER_SPEC.md` §5.2 Opportunity Score

## Phase 1B notes

- Opportunity Engine = **layer 1** (overnight #1–#3).
- Day must authorize via Market Activity before trading a high opportunity name.
