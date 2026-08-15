---
name: dashboard-ux
description: FastAPI dashboard app, dashboard.html, style.css, API routes for trading-day, proposals, capital-builder. Use for UI, banners, status bar, and client-side refresh logic.
---

# Dashboard UX

## When to use

- Trade tab, proposal cards, go/no-go panel, top pick / second pick
- Account tab, Capital Builder bar, learning panels
- API routes in `dashboard/app.py`
- CSS and JavaScript in templates/static

## Owns (may edit)

- `src/investment_agent/dashboard/app.py`
- `src/investment_agent/dashboard/templates/dashboard.html`
- `src/investment_agent/dashboard/static/style.css`
- `tests/test_dashboard.py`, `test_dashboard_integration.py`

## Do not touch

- Core scoring math → domain skills (call APIs only)
- Ingest/screener batch jobs → **eod-ingest-screener**

## Rules

1. Preserve 3-step daily rhythm UX (EOD → Morning → Refresh Live).
2. Mobile-friendly status bar and verdict chips.
3. API key header support when `DASHBOARD_API_KEY` set.
4. Extended session: fill toggle uses localStorage; journal fill locks state.
5. Minimal diff — match existing CSS variables and component patterns.

## Key DOM areas

| Element | Purpose |
|---------|---------|
| `#top-pick-body` | Live pick card |
| `#verdict-headline` | Go/no-go headline |
| `#trading-checks` | Checklist |
| `#view-trade` | Main trading view |

## Tests

```bash
python3 -m pytest tests/test_dashboard.py tests/test_dashboard_integration.py -q
```

## Phase 1B notes (Inc 14–16)

- Red **DO NOT TRADE TODAY** banner (`#no-trade-banner`); ranked list still visible.
- **EXIT — sell at market** banner when day flips and position open.
- Weekly progress in status bar: `n of 3 · $X / $tier`.
- Market Activity breakdown panel (with n/a labels).
- Confirmation chips on #1–#3 (Inc 13).
- Proposal generate blocked when Market Activity = NO TRADE.

## Run locally

```bash
python3 scripts/run_dashboard.py --host 127.0.0.1 --port 8080
```
