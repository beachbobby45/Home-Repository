---
name: trade-proposals
description: Trade Proposal lifecycle, pullback limit plans, human approve/reject, proposal API and cards. Use for proposal generation, validation, and linking journal fills to proposal_id.
---

# Trade Proposals

## When to use

- Generate / refresh / approve / reject proposals
- Pullback limit buy, sell for net target, stop assignment
- Proposal DB schema and API routes
- Human-in-the-loop workflow before E*TRADE

## Owns (may edit)

- `src/investment_agent/trade_proposal.py`
- `src/investment_agent/pullback_entry.py`
- `tests/test_trade_proposal.py`, `test_pullback_entry.py`

## Do not touch

- Risk Engine verdict logic → **risk-engine**
- Dashboard proposal card markup → **dashboard-ux** (coordinate)
- Journal inserts → **journal-capital**

## Rules

1. Every proposal includes: entry, stop, target, shares, opportunity factors, risk snapshot at creation.
2. **Refresh live** before approve re-runs Risk Engine (`refresh_live_quotes`).
3. Limit fill deadline **11:30 ET** — cancel unfilled; do not chase market.
4. Stop on every buy (~0.75% / `STOP_PCT`) — non-negotiable.
5. Proposals link to journal via `proposal_id` on BUY.
6. Max **5** active proposals (existing cap).

## Lifecycle

```text
draft → risk_rejected | proposed → human_rejected | human_approved
     → executed (journal BUY) → closed (journal SELL) → expired
```

## Tests

```bash
python3 -m pytest tests/test_trade_proposal.py tests/test_pullback_entry.py tests/test_trade_plan.py -q
```

## Related docs

- `docs/PHASE1_CAPITAL_BUILDER_SPEC.md` §5.1 Trade Proposal

## Phase 1B notes (Inc 17)

- **Exceptional trade**: max 1/week after weekly guidance met; all signals GO; logged override.
- Do not create proposals when Market Activity = NO TRADE (wire in Inc 15).
