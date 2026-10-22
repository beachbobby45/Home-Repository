---
name: tradable-now
description: Top-3 best-tradable-now soft scorer for paper propose (MA/VWAP, volume, pullback, limit reachability). Use when changing selection among prep ranks #1–#3.
---

# Best tradable now (top-3)

## When to use

- Soft-score prep ranks #1–#3 for the session buy decision
- Allocation mode `best_tradable_top3` (default) vs `single_top1` shadow
- Paper dual-book: `gate_approved` = scored winner; `all_signals` = #1-only

## Owns (may edit)

- `src/investment_agent/execution/tradable_now.py`
- `src/investment_agent/execution/propose.py` (allocation / selection audit)
- `src/investment_agent/execution/paper_runner.py` (primary vs shadow signals)
- `src/investment_agent/execution/armed_plan.py` (`AllocationMode.BEST_TRADABLE_TOP3`)
- `tests/test_tradable_now.py`, `tests/test_best_tradable_propose.py`

## Do not touch

- Risk Engine → **risk-engine**
- Market Activity day gate → **market-activity**
- News veto (not in this increment)

## Frozen defaults (2026-10-22)

| Knob | Value |
|------|--------|
| Shortlist | #1–#3 |
| Scoring | **Soft** (prefer, do not hard-drop) |
| 30d MA / VWAP | prefer price above either |
| Volume | last 6×5m vs prior 20-bar avg |
| Short MA | 9×5m; pullback holds + bounce volume |
| Weights | reach 35% · trend 25% · volume 20% · pullback 20% |
| Ties | better prep rank |
| News | later |
| Shadow | `#1-only` on `all_signals` |

## Tests

```bash
python3 -m pytest tests/test_tradable_now.py tests/test_best_tradable_propose.py tests/test_paper_propose_race.py -q
```
