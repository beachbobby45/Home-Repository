---
name: learning-analytics
description: Learning reports, close reports, proposal outcome attribution, review tab. Use for post-trade analytics and Phase 1B score logging (Inc 18).
---

# Learning & Analytics

## When to use

- Generate learning report (`run_learning.py`)
- Close report / weekly summaries
- Proposal learning panel (opportunity buckets, rejections)
- Factor attribution for closed trades

## Owns (may edit)

- `src/investment_agent/learning.py`
- `src/investment_agent/close_report.py`
- `scripts/run_learning.py`, `run_daily_close.py`
- `tests/test_learning.py`, `test_close_report.py`

## Do not touch

- Live scoring → **opportunity-engine**, **market-activity**
- Journal writes → **journal-capital**

## Rules

1. Learning reads journal + proposals + quotes — read-only on trades.
2. Proposal learning links outcomes when `proposal_id` present on journal BUY.
3. Reports must work **without Claude** (Option A).

## Tests

```bash
python3 -m pytest tests/test_learning.py tests/test_close_report.py -q
```

## Phase 1B notes (Inc 18)

Persist at decision time:

- Market Activity score + band
- Confirmation score per ticker
- Authorization outcome (TRADE / NO TRADE / exceptional)
- Human approve/reject reason

Enables answering: *Does Above Average day actually improve win rate?*

## Related docs

- `docs/PHASE1_CAPITAL_BUILDER_SPEC.md` § Learning
- Phase 5 learning loop in planning conversation (future)
