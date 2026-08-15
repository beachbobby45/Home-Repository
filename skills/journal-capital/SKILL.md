---
name: journal-capital
description: Trade journal (source of truth for cash/P&L), daily profit targets, Capital Builder milestone UI. Use for journal entries, FIFO P&L, tier math, weekly 3× daily guidance (Phase 1B Inc 10).
---

# Journal & Capital Model

## When to use

- Log BUY/SELL fills, fees, executed times (Pacific)
- Today / weekly / monthly realized net
- Open positions (FIFO)
- Capital Builder $10K→$30K progress
- **Phase 1B:** split-lot tier table, weekly 3×$150 at $10K

## Owns (may edit)

- `src/investment_agent/journal.py`
- `src/investment_agent/finance.py`
- `src/investment_agent/capital_builder.py`
- `src/investment_agent/account.py` (dashboard summary, cash)
- `tests/test_journal.py`, `test_finance.py`, `test_capital_builder.py`, `test_account.py`

## Do not touch

- Proposal generation → **trade-proposals**
- Risk limits → **risk-engine**
- Opportunity counting UI → **dashboard-ux** (coordinate)

## Rules

1. **Journal is source of truth** for realized P&L until execution service exists.
2. Executed times interpreted as **Pacific** unless timezone-aware ISO provided.
3. Every BUY should have a stop assigned in the plan (enforced upstream).
4. Current daily target: linear +$50/$5K from $10K base — **Phase 1B replaces** with split-lot table.

## Phase 1B tier model (to implement Inc 10)

| Balance | Structure | Daily | Weekly (3 opps) |
|--------:|-----------|------:|----------------:|
| $10,000 | 1× $10K | $150 | $450 |
| $15,000 | 1× $15K | $200 | $600 |
| $20,000 | $10K+$10K | $300 | $900 |
| $25,000 | $10K+$15K | $350 | $1,050 |
| $30,000 | $15K+$15K | $400 | $1,200 |

Lot rate: $150 at $10K lot, +$50 per additional $5K on lot size.

**Weekly:** 3 × $150 net **wins** at $10K tier — any day mix in the week.
**Exceptional:** 1 extra opportunity/week when all signals GO (Inc 17).

## Tests

```bash
python3 -m pytest tests/test_journal.py tests/test_finance.py tests/test_capital_builder.py tests/test_account.py -q
```

## Related docs

- `docs/FEES_AT_A_GLANCE.md`
- `docs/PHASE1_CAPITAL_BUILDER_SPEC.md` §2 Business Objectives
