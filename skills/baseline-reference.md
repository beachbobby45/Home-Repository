# Baseline reference — v0.8-pre-phase1b

Frozen snapshot **before** Phase 1B (Market Activity, Confirmation, split-lot tiers).

## Git

```bash
git fetch origin --tags
git checkout baseline/pre-phase1b-aug2026
# read-only inspection, or:
git checkout -b my-work-from-baseline
```

Or checkout tag (detached HEAD):

```bash
git checkout v0.8-pre-phase1b
```

Return to latest main:

```bash
git checkout main
git pull origin main
```

## What this baseline includes

- Phase 0 audit + Phase 1 Capital Builder spec (docs)
- Increment 1: Risk Engine
- Increment 2: News Service
- Increment 3: Opportunity Score
- Increment 4: Trade Proposals + UI
- Increment 5: Capital Builder progress UI
- Increment 6: AI Sentiment (no-Claude-first)
- Increment 7: Learning v2 + dashboard polish
- Extended session row + filled/not-filled toggle
- **220** pytest tests passing

## What this baseline does NOT include (Phase 1B+)

- Market Activity Engine / NO TRADE day banner
- Candidate Confirmation Engine
- Split-lot tier table ($450/week at $10K)
- Quote snapshot schedule (pre-open, +15 min)
- Intraday flip → sell-at-market alert
- `skills/` layout (added after baseline on main)

## Database backup (recommended on Mac)

Code is in git; **`data/agent.db` is not.**

Before Phase 1B on your Mac:

```bash
cp data/agent.db "backups/agent-$(date +%Y%m%d)-pre-phase1b.db"
```

Restore:

```bash
cp backups/agent-YYYYMMDD-pre-phase1b.db data/agent.db
```

## Dashboard

```bash
python scripts/run_dashboard.py --host 127.0.0.1 --port 8080
```

Mac: **Open Dashboard.command** or morning/evening prep scripts as today.

## Merge note

`main` was fast-forwarded to this baseline on merge (commit `cc36611`).
The baseline branch and tag point to the **same commit** for redundancy.
