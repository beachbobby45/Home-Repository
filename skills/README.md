# Cursor Skills — AI Investment Agent

Domain-specific skills for **controlled, incremental** work on the modular monolith.
Each skill maps to Python modules and dashboard areas — **not** separate runtime services.

## Baseline (restore pre–Phase 1B)

| Ref | Value |
|-----|-------|
| **Tag** | `v0.8-pre-phase1b` |
| **Branch** | `baseline/pre-phase1b-aug2026` |
| **Commit** | `cc36611` (main as of Aug 2026) |
| **Contents** | Increments 1–7 + extended session row + fill toggle · 220 tests |

```bash
git fetch origin
git checkout baseline/pre-phase1b-aug2026   # or: git checkout v0.8-pre-phase1b
```

See [baseline-reference.md](./baseline-reference.md) for DB backup and Mac restore notes.

## Skill index

| Skill | Role | Primary modules | Status |
|-------|------|-----------------|--------|
| [eod-ingest-screener](./eod-ingest-screener/SKILL.md) | EOD ingest, 14d screener, ranked candidates | `ingest.py`, `period_screener.py`, `historical.py` | **Active** |
| [opportunity-engine](./opportunity-engine/SKILL.md) | Multi-factor opportunity score, #1–#3 ranks | `opportunity_score.py`, `news_service.py`, `ai_service.py` | **Active** |
| [trade-proposals](./trade-proposals/SKILL.md) | Trade proposals, pullback plan, human approval | `trade_proposal.py`, `pullback_entry.py` | **Active** |
| [risk-engine](./risk-engine/SKILL.md) | Sovereign risk gate, kill switch, limits | `risk_engine.py`, `strategy.py` | **Active** |
| [journal-capital](./journal-capital/SKILL.md) | Journal, P&L, capital tiers (Phase 1B tiers TBD) | `journal.py`, `finance.py`, `capital_builder.py` | **Active** |
| [intraday-trading-day](./intraday-trading-day/SKILL.md) | Go/no-go, live refresh, extended session | `trading_day.py`, `tradability.py`, `regime.py` | **Active** |
| [market-activity](./market-activity/SKILL.md) | Day gate: TRADE / NO TRADE (Phase 1B) | `market_activity.py` | **Active Inc 12** |
| [confirmation-engine](./confirmation-engine/SKILL.md) | Stock confirms today (Phase 1B) | `confirmation.py` | **Active Inc 13** |
| [dashboard-ux](./dashboard-ux/SKILL.md) | Dashboard UI, banners, APIs | `dashboard/app.py`, `templates/dashboard.html`, `static/style.css` | **Active** |
| [learning-analytics](./learning-analytics/SKILL.md) | Learning reports, proposal attribution | `learning.py`, `close_report.py` | **Active** |

## Architecture principle

```text
Runtime: ONE monolith (src/investment_agent/) — extend modules, do not split services.
Cursor:  ONE skill per domain — narrow context, small diffs, run listed tests.
```

## Phase 1B build sequence (after skills)

| Inc | Skill(s) to invoke | Deliverable |
|-----|-------------------|-------------|
| 9 | (docs only) | `PHASE1B_*` specs |
| 10 | journal-capital | Split-lot tier + weekly 3× daily | **Done Inc 10** |
| 11 | intraday-trading-day, eod-ingest-screener | Quote snapshots | **Done Inc 11** |
| 12 | market-activity | Market Activity Score v0 | **Done Inc 12** |
| 13 | confirmation-engine | Confirmation on #1–#3 | **Done Inc 13** |
| 14–16 | dashboard-ux, intraday-trading-day | Banner, exit alert, wiring |
| 17 | trade-proposals, risk-engine | Exceptional trade rule |
| 18 | learning-analytics | Score attribution |

## Using a skill in Cursor

1. Open the skill file for the domain you are changing.
2. Tell Cursor: *"Follow `skills/<name>/SKILL.md`; do not modify modules listed under Do Not Touch."*
3. Run the skill's **Tests** section before committing.
4. One increment per PR; branch prefix `cursor/<descriptive>-cd1d`.

## Authoritative docs

- [docs/PHASE1_CAPITAL_BUILDER_SPEC.md](../docs/PHASE1_CAPITAL_BUILDER_SPEC.md)
- [docs/PHASE1_TECHNICAL_AUDIT.md](../docs/PHASE1_TECHNICAL_AUDIT.md)
- [docs/PRODUCT_SPEC_V3.md](../docs/PRODUCT_SPEC_V3.md)
- Phase 1B specs (Inc 9): [PHASE1B_ASSUMPTIONS_AND_DEFINITIONS.md](../docs/PHASE1B_ASSUMPTIONS_AND_DEFINITIONS.md), [PHASE1B_MARKET_ACTIVITY.md](../docs/PHASE1B_MARKET_ACTIVITY.md)
