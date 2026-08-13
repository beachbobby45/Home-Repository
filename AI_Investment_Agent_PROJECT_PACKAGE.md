# AI Investment Agent — Complete Project Package

**Generated:** 2026-08-13 15:56:27 UTC  
**Branch:** `cursor/patch-investment-agent-spec-cd1d`  
**Files included:** 132  

> Single-file export of the Home-Repository codebase (docs, source, scripts, tests).
> Secrets excluded: `.env`, `data/`, databases, caches.

---

## Table of Contents

1. [.env.example](#-env-example)
2. [.gitignore](#-gitignore)
3. [README.md](#readme-md)
4. [docs/AI_Investment_Agent_Spec.md](#docs-ai_investment_agent_spec-md)
5. [docs/DASHBOARD_ONE_PAGER.md](#docs-dashboard_one_pager-md)
6. [docs/FEES_AT_A_GLANCE.md](#docs-fees_at_a_glance-md)
7. [docs/PHASE_0.md](#docs-phase_0-md)
8. [docs/PHASE_7_SPEC.md](#docs-phase_7_spec-md)
9. [docs/PRODUCT_SPEC_V3.md](#docs-product_spec_v3-md)
10. [requirements.txt](#requirements-txt)
11. [scripts/Enable Auto Refresh.command](#scripts-enable auto refresh-command)
12. [scripts/Open Dashboard.command](#scripts-open dashboard-command)
13. [scripts/Run After-Close Ingest.command](#scripts-run after-close ingest-command)
14. [scripts/Run Daily Ingest.command](#scripts-run daily ingest-command)
15. [scripts/Run End of Day.command](#scripts-run end of day-command)
16. [scripts/Run Morning Prep.command](#scripts-run morning prep-command)
17. [scripts/Run Refresh Live.command](#scripts-run refresh live-command)
18. [scripts/backfill_metrics_yfinance.py](#scripts-backfill_metrics_yfinance-py)
19. [scripts/build_sp500_universe.py](#scripts-build_sp500_universe-py)
20. [scripts/check_ticker.py](#scripts-check_ticker-py)
21. [scripts/compare_backtest_intervals.py](#scripts-compare_backtest_intervals-py)
22. [scripts/dashboard_service_status_mac.sh](#scripts-dashboard_service_status_mac-sh)
23. [scripts/doctor_dashboard_mac.sh](#scripts-doctor_dashboard_mac-sh)
24. [scripts/generate_daily_rhythm_pdf.py](#scripts-generate_daily_rhythm_pdf-py)
25. [scripts/generate_one_pager_pdf.py](#scripts-generate_one_pager_pdf-py)
26. [scripts/hard_restart_dashboard_mac.sh](#scripts-hard_restart_dashboard_mac-sh)
27. [scripts/install_dashboard_service_mac.sh](#scripts-install_dashboard_service_mac-sh)
28. [scripts/install_ingest_schedule_mac.sh](#scripts-install_ingest_schedule_mac-sh)
29. [scripts/manage_watchlist.py](#scripts-manage_watchlist-py)
30. [scripts/repair_dashboard_mac.sh](#scripts-repair_dashboard_mac-sh)
31. [scripts/restart_dashboard_mac.sh](#scripts-restart_dashboard_mac-sh)
32. [scripts/run_backtest.py](#scripts-run_backtest-py)
33. [scripts/run_daily_close.py](#scripts-run_daily_close-py)
34. [scripts/run_dashboard.py](#scripts-run_dashboard-py)
35. [scripts/run_end_of_day_mac.sh](#scripts-run_end_of_day_mac-sh)
36. [scripts/run_historical.py](#scripts-run_historical-py)
37. [scripts/run_ingest.py](#scripts-run_ingest-py)
38. [scripts/run_ingest_mac.sh](#scripts-run_ingest_mac-sh)
39. [scripts/run_ingest_scheduled_mac.sh](#scripts-run_ingest_scheduled_mac-sh)
40. [scripts/run_learning.py](#scripts-run_learning-py)
41. [scripts/run_monitor.py](#scripts-run_monitor-py)
42. [scripts/run_morning_prep_mac.sh](#scripts-run_morning_prep_mac-sh)
43. [scripts/run_period_screener.py](#scripts-run_period_screener-py)
44. [scripts/run_refresh_live.py](#scripts-run_refresh_live-py)
45. [scripts/run_refresh_live_mac.sh](#scripts-run_refresh_live_mac-sh)
46. [scripts/run_strategy_models.py](#scripts-run_strategy_models-py)
47. [scripts/seed_demo_data.py](#scripts-seed_demo_data-py)
48. [scripts/start_dashboard_cloud.sh](#scripts-start_dashboard_cloud-sh)
49. [scripts/start_dashboard_mac.sh](#scripts-start_dashboard_mac-sh)
50. [scripts/sync_queue.py](#scripts-sync_queue-py)
51. [scripts/uninstall_dashboard_service_mac.sh](#scripts-uninstall_dashboard_service_mac-sh)
52. [scripts/uninstall_ingest_schedule_mac.sh](#scripts-uninstall_ingest_schedule_mac-sh)
53. [scripts/verify_access.py](#scripts-verify_access-py)
54. [scripts/verify_dashboard.py](#scripts-verify_dashboard-py)
55. [src/investment_agent/__init__.py](#src-investment_agent-__init__-py)
56. [src/investment_agent/account.py](#src-investment_agent-account-py)
57. [src/investment_agent/backtest.py](#src-investment_agent-backtest-py)
58. [src/investment_agent/backtest_strategy.py](#src-investment_agent-backtest_strategy-py)
59. [src/investment_agent/cio.py](#src-investment_agent-cio-py)
60. [src/investment_agent/close_report.py](#src-investment_agent-close_report-py)
61. [src/investment_agent/config.py](#src-investment_agent-config-py)
62. [src/investment_agent/daily_rhythm.py](#src-investment_agent-daily_rhythm-py)
63. [src/investment_agent/dashboard/__init__.py](#src-investment_agent-dashboard-__init__-py)
64. [src/investment_agent/dashboard/app.py](#src-investment_agent-dashboard-app-py)
65. [src/investment_agent/dashboard/static/style.css](#src-investment_agent-dashboard-static-style-css)
66. [src/investment_agent/dashboard/templates/dashboard.html](#src-investment_agent-dashboard-templates-dashboard-html)
67. [src/investment_agent/db.py](#src-investment_agent-db-py)
68. [src/investment_agent/db_maintenance.py](#src-investment_agent-db_maintenance-py)
69. [src/investment_agent/demo_seed.py](#src-investment_agent-demo_seed-py)
70. [src/investment_agent/dollar_target.py](#src-investment_agent-dollar_target-py)
71. [src/investment_agent/finance.py](#src-investment_agent-finance-py)
72. [src/investment_agent/historical.py](#src-investment_agent-historical-py)
73. [src/investment_agent/ingest.py](#src-investment_agent-ingest-py)
74. [src/investment_agent/journal.py](#src-investment_agent-journal-py)
75. [src/investment_agent/learning.py](#src-investment_agent-learning-py)
76. [src/investment_agent/liquidity.py](#src-investment_agent-liquidity-py)
77. [src/investment_agent/monitor.py](#src-investment_agent-monitor-py)
78. [src/investment_agent/period_screener.py](#src-investment_agent-period_screener-py)
79. [src/investment_agent/providers/__init__.py](#src-investment_agent-providers-__init__-py)
80. [src/investment_agent/providers/finnhub.py](#src-investment_agent-providers-finnhub-py)
81. [src/investment_agent/providers/fred.py](#src-investment_agent-providers-fred-py)
82. [src/investment_agent/providers/yfinance_bars.py](#src-investment_agent-providers-yfinance_bars-py)
83. [src/investment_agent/pullback_entry.py](#src-investment_agent-pullback_entry-py)
84. [src/investment_agent/regime.py](#src-investment_agent-regime-py)
85. [src/investment_agent/scenario.py](#src-investment_agent-scenario-py)
86. [src/investment_agent/screen_actions.py](#src-investment_agent-screen_actions-py)
87. [src/investment_agent/step3_status.py](#src-investment_agent-step3_status-py)
88. [src/investment_agent/stock_team.py](#src-investment_agent-stock_team-py)
89. [src/investment_agent/strategy.py](#src-investment_agent-strategy-py)
90. [src/investment_agent/strategy_models.py](#src-investment_agent-strategy_models-py)
91. [src/investment_agent/tradability.py](#src-investment_agent-tradability-py)
92. [src/investment_agent/trading_day.py](#src-investment_agent-trading_day-py)
93. [src/investment_agent/watchlist.py](#src-investment_agent-watchlist-py)
94. [tests/test_account.py](#tests-test_account-py)
95. [tests/test_backtest.py](#tests-test_backtest-py)
96. [tests/test_cio.py](#tests-test_cio-py)
97. [tests/test_close_report.py](#tests-test_close_report-py)
98. [tests/test_daily_rhythm.py](#tests-test_daily_rhythm-py)
99. [tests/test_dashboard.py](#tests-test_dashboard-py)
100. [tests/test_dashboard_integration.py](#tests-test_dashboard_integration-py)
101. [tests/test_data_freshness.py](#tests-test_data_freshness-py)
102. [tests/test_db.py](#tests-test_db-py)
103. [tests/test_db_maintenance.py](#tests-test_db_maintenance-py)
104. [tests/test_demo_seed.py](#tests-test_demo_seed-py)
105. [tests/test_dollar_backtest.py](#tests-test_dollar_backtest-py)
106. [tests/test_dollar_rank_gate.py](#tests-test_dollar_rank_gate-py)
107. [tests/test_dollar_target.py](#tests-test_dollar_target-py)
108. [tests/test_finance.py](#tests-test_finance-py)
109. [tests/test_historical.py](#tests-test_historical-py)
110. [tests/test_ingest.py](#tests-test_ingest-py)
111. [tests/test_journal.py](#tests-test_journal-py)
112. [tests/test_learning.py](#tests-test_learning-py)
113. [tests/test_liquidity.py](#tests-test_liquidity-py)
114. [tests/test_monitor.py](#tests-test_monitor-py)
115. [tests/test_phase7.py](#tests-test_phase7-py)
116. [tests/test_pullback_entry.py](#tests-test_pullback_entry-py)
117. [tests/test_regime.py](#tests-test_regime-py)
118. [tests/test_scenario.py](#tests-test_scenario-py)
119. [tests/test_screen_actions.py](#tests-test_screen_actions-py)
120. [tests/test_special_watch.py](#tests-test_special_watch-py)
121. [tests/test_stock_team.py](#tests-test_stock_team-py)
122. [tests/test_strategy_models.py](#tests-test_strategy_models-py)
123. [tests/test_tradability.py](#tests-test_tradability-py)
124. [tests/test_trade_plan.py](#tests-test_trade_plan-py)
125. [tests/test_trading_day.py](#tests-test_trading_day-py)
126. [tests/test_trading_days_period.py](#tests-test_trading_days_period-py)
127. [tests/test_verify_access.py](#tests-test_verify_access-py)
128. [tests/test_yfinance_bars.py](#tests-test_yfinance_bars-py)
129. [universe/datacenter_us.txt](#universe-datacenter_us-txt)
130. [universe/sp100.txt](#universe-sp100-txt)
131. [universe/sp500.txt](#universe-sp500-txt)
132. [universe/starter10.txt](#universe-starter10-txt)

---

<a id="-env-example"></a>
## `.env.example`

```text
# =============================================================================
# AI Investment Agent — Environment Variables (Product Spec v3)
# Copy to .env and fill in your keys. NEVER commit .env to git.
# See docs/FEES_AT_A_GLANCE.md and docs/PRODUCT_SPEC_V3.md
# =============================================================================

# --- REQUIRED (Phase 0 / Gate 0) ---

# Anthropic Claude API (https://console.anthropic.com)
ANTHROPIC_API_KEY=

# FRED / St. Louis Fed (https://fredaccount.stlouisfed.org/useraccount/apikey)
FRED_API_KEY=

# Finnhub (https://finnhub.io/dashboard) — personal use only on free tier
FINNHUB_API_KEY=

# --- OPTIONAL ---

# Massive / Polygon (https://massive.com/dashboard) — historical backfill / backtest
MASSIVE_API_KEY=

# FastAPI dashboard password (optional). Leave blank for local-only — no password bar.
# Set any random string if you expose the dashboard via tunnel or --host 0.0.0.0
APP_API_KEY=

# Test ticker used by verify_access.py
VERIFY_TEST_TICKER=SPY

# Alpaca — NOT used for v3 execution (E*TRADE manual). Optional data-only later.
# ALPACA_API_KEY=
# ALPACA_SECRET_KEY=
```


---

<a id="-gitignore"></a>
## `.gitignore`

```text
# Environment and secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Database
*.db
*.sqlite
*.sqlite3
data/

# IDE / OS
.idea/
.vscode/
.DS_Store
*.swp
*.swo

# Logs and local notes
*.log
logs/
.env.local.notes
```


---

<a id="readme-md"></a>
## `README.md`

# AI Investment Agent (Product Spec v3)

Intraday **alerting and analysis** system: CIO + sub-agents → dashboard recommendations (+1.13% / −0.50%, ~3% swing proof). **You** execute in **E*TRADE** and log trades. Target goal tracking: **$5M** from **$10K** basis.

## Documentation

| Doc | Purpose |
|-----|---------|
| **[PRODUCT_SPEC_V3.md](docs/PRODUCT_SPEC_V3.md)** | **Authoritative** product & financial rules |
| **[PHASE_0.md](docs/PHASE_0.md)** | Gate 0 checklist |
| **[FEES_AT_A_GLANCE.md](docs/FEES_AT_A_GLANCE.md)** | API costs |
| **[AI_Investment_Agent_Spec.md](docs/AI_Investment_Agent_Spec.md)** | Technical appendix (gates, schemas; some v2 items superseded by v3) |

## Phase 0 — Start here

```bash
cp .env.example .env
# Add FRED_API_KEY, FINNHUB_API_KEY (ANTHROPIC later when you add ~$25 credits)

pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 scripts/verify_access.py --no-claude
```

Gate 0 must pass before Phase 1. Use full `verify_access.py` once Anthropic credits are added.

## Phase 1 — Data ingest (no Claude)

```bash
PYTHONPATH=src python3 scripts/run_ingest.py
PYTHONPATH=src python3 scripts/run_ingest.py --tickers SPY AAPL
```

Fetches FRED macro (VIX), Finnhub live quotes, yfinance daily bars, liquidity metrics, and SPY/DIA/QQQ regime gate.

## Phase 2–3 — Dashboard (no Claude)

```bash
PYTHONPATH=src python3 scripts/sync_queue.py      # populate queue from screener
PYTHONPATH=src python3 scripts/run_dashboard.py   # http://127.0.0.1:8080
```

**Mac — background service (no Terminal window):** `./scripts/install_dashboard_service_mac.sh` once; opens http://127.0.0.1:8080 on login. Status: `./scripts/dashboard_service_status_mac.sh`

Dashboard: **$5M goal**, tradable cash, month P&amp;L, sweep preview, regime banner, **intraday alerts**, trade queue, manual journal.

```bash
# Demo mode — seed test data and verify all dashboard endpoints (24 checks)
PYTHONPATH=src python3 scripts/seed_demo_data.py
PYTHONPATH=src python3 scripts/verify_dashboard.py --seed

# Intraday monitor (uses quotes in DB; add --refresh-quotes for live Finnhub)
PYTHONPATH=src python3 scripts/run_monitor.py

# Phase 7 — watchlist + period screener (no Claude)
PYTHONPATH=src python3 scripts/manage_watchlist.py load-preset sp100
PYTHONPATH=src python3 scripts/manage_watchlist.py load-preset sp500   # ~506 tickers
PYTHONPATH=src python3 scripts/run_historical.py pull --lookback-days 60
PYTHONPATH=src python3 scripts/run_period_screener.py --days 14 --save
PYTHONPATH=src python3 scripts/run_ingest.py              # full refresh (first run)
PYTHONPATH=src python3 scripts/run_ingest.py --incremental   # daily morning ingest

# Learning + CIO summary (Phase 5, no Claude)
PYTHONPATH=src python3 scripts/run_learning.py

# $5M scenario visualizer — journal-fed chart + projections (Phase 6)
PYTHONPATH=src python3 scripts/verify_dashboard.py --seed   # 34 checks incl. scenario
```

## v3 highlights

- **CIO + sub-agents** (research, stock team, regime, monitor, learning) — one repo
- **$7 buy / $7 sell** fees in P&amp;L model
- **Month-end sweeps:** 10% management + **editable** 25% tax reserve on **realized gains only**
- **No Alpaca orders**; optional Massive for backtest later
- **Progress:** `% of $5M goal` month by month

## Status

| Phase | Status |
|-------|--------|
| 0 — Foundation | **Done** (Option A: `--no-claude` Gate 0) |
| 1 — Data pipeline | **Done** (ingest + regime gate) |
| 2–3 — Screener + dashboard | **Done** (queue, journal, goal, sweeps) |
| 4 — Intraday monitor | **Done** (target/stop/EOD alerts) |
| 5 — Learning + CIO | **Done** (daily report, rule-based CIO panel) |
| 6 — $5M scenario visualizer | **Done** (journal timeline + projections) |
| 7 — Expandable watchlist + period screener | **Done** (sp100/sp500 presets, incremental ingest, ranked candidates, dashboard) |


---

<a id="docs-ai_investment_agent_spec-md"></a>
## `docs/AI_Investment_Agent_Spec.md`

# AI Investment Agent — Full Architecture & Build Spec

> **Authoritative product rules:** **[PRODUCT_SPEC_V3.md](./PRODUCT_SPEC_V3.md)** (July 27, 2026 — approved)  
> **This file:** technical appendix (layers, gates, schemas). Where v2 conflicts with v3, **v3 wins** (E*TRADE manual, intraday rules, no 8% cap, no Alpaca execution).

> **Purpose:** Complete handoff document for building an AI-powered stock market analysis and **alerting** agent.

> **Version:** 3.0 (Phase 0 started July 27, 2026)
> **Changes from v1:** Added pre-build access checklist, verified external dependency matrix, Layer 1.5 signal gate, complete risk engine spec, formal thesis schema, anti-hallucination validation, order lifecycle, expanded database schema, gate-based testing plan, realistic cost model, and removed/replaced data sources that are unavailable or impractical on free tiers.
>
> **Fees & billing:** See **[Fees at a Glance](./FEES_AT_A_GLANCE.md)** for every key, cost, and Anthropic trial credit details.

---

## Table of Contents

0. [Fees at a Glance](./FEES_AT_A_GLANCE.md) ← **read before spending anything**
1. [Pre-Build Access Checklist (Read First)](#pre-build-access-checklist-read-first)
2. [External Dependencies Matrix](#external-dependencies-matrix)
3. [Overview](#overview)
4. [Architecture](#architecture)
5. [Layer 1 — Signal Collection](#layer-1--signal-collection)
6. [Layer 1.5 — Signal Gate](#layer-15--signal-gate)
7. [Layer 2 — Reasoning Engine](#layer-2--reasoning-engine)
8. [Layer 3 — Risk Guardrail](#layer-3--risk-guardrail)
9. [Layer 4 — Human-in-the-Loop Dashboard](#layer-4--human-in-the-loop-dashboard)
10. [Order Lifecycle](#order-lifecycle)
11. [Tech Stack](#tech-stack)
12. [Database Schema](#database-schema)
13. [Thesis JSON Schema](#thesis-json-schema)
14. [Gate-Based Testing Plan](#gate-based-testing-plan)
15. [Phased Build Plan](#phased-build-plan)
16. [Estimated Monthly Cost](#estimated-monthly-cost)
17. [Observability, Security & Operations](#observability-security--operations)
18. [Evaluation Metrics](#evaluation-metrics)
19. [Design Decisions & Critical Mistakes](#design-decisions--critical-mistakes)
20. [Future Enhancements](#future-enhancements)
21. [Legal Disclaimer](#legal-disclaimer)

---

## Pre-Build Access Checklist (Read First)

**Do not start coding until every required item below is verified.** Each gate in the [Gate-Based Testing Plan](#gate-based-testing-plan) depends on these connections being live.

### Required before Phase 0 (account setup)

| # | Service | What you need | Cost | Access type | Blocker if missing |
|---|---------|---------------|------|-------------|-------------------|
| 1 | **Alpaca Markets** | Broker account + **paper** API key/secret | $0 | Self-serve signup at [alpaca.markets](https://alpaca.markets). US retail accounts only. | Cannot paper trade or sync portfolio |
| 2 | **Anthropic Claude API** | API key from [console.anthropic.com](https://console.anthropic.com) | ~$5–25/mo with gating (see [Fees at a Glance](./FEES_AT_A_GLANCE.md)) | Self-serve. Phone verification required. **No permanent free tier.** Official docs: *"New users receive a small amount of free credits to test the API"* ([pricing FAQ](https://platform.claude.com/docs/en/about-claude/pricing)). Exact amount not published — **verify your balance in Console → Billing before testing.** Ongoing use requires prepaid credits. | Cannot generate theses |
| 3 | **FRED (St. Louis Fed)** | Free API key from [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/useraccount/apikey) | $0 | Self-serve, instant | Cannot fetch VIX proxy, macro series, or release dates |
| 4 | **Finnhub** | Free API key from [finnhub.io](https://finnhub.io) | $0 (personal use) | Self-serve, instant. **License: personal use only.** US-focused on free tier. | Cannot fetch fundamentals/news on free path |

### Required before Phase 1 (data ingestion at scale)

| # | Service | What you need | Cost | Notes |
|---|---------|---------------|------|-------|
| 5 | **Alpaca Market Data** | Included with Alpaca account | $0 on paper | Paper-only accounts get **IEX data only** (not full SIP). Sufficient for v1 paper trading. Real-time multi-exchange data requires paid Alpaca data subscription (~$9–99/mo depending on plan). |
| 6 | **Massive (formerly Polygon.io)** | API key from [massive.com](https://massive.com) | $0 free tier **or** $29+/mo | Free tier: **5 REST calls/min**, 15-min delayed data, ~2 years history. **Not viable** for polling 20–30 tickers every 15 min. Use Alpaca for live bars; use Massive only for historical backfill (batched, rate-limited). |

### Optional (enable specific features)

| # | Service | Feature enabled | Cost | Availability verdict |
|---|---------|-----------------|------|---------------------|
| 7 | **Benzinga Basic News** (AWS Marketplace) | Financial news headlines | $0 free tier via AWS Marketplace subscription | Self-serve. Headline + teaser only (not full article body). |
| 8 | **NewsAPI.org** | General news headlines | $0 dev tier only | **100 requests/day**, 24-hour delay, **dev/testing only — not production**. Business tier $449/mo for production. |
| 9 | **SiftingIO Economic Calendar** | Fed/CPI blackout windows (Rule 6) | Free tier: 5,000 calls/day | Requires API key from sifting.io. Alternative: FRED `releases/dates` endpoint (free, less structured). |
| 10 | **VPS hosting** | Run scheduler 24/5 during market hours | ~$10/mo | Optional for v1; can run locally on your PC instead. |

### Removed from v1 — do NOT plan on these without paid/approval paths

| Service | v1 assumption | v2 verdict |
|---------|---------------|------------|
| **Reddit API** | Free social sentiment | **Not recommended for v1.** Commercial/personal-investment-tool use may require paid contract ($0.24/1K calls) and **manual approval (2–4 weeks, not guaranteed)**. Self-service OAuth registration is restricted. |
| **StockTwits official API** | Free sentiment | **Not available for new developers.** Enterprise-only (contact sales). Unofficial public endpoints exist but are undocumented, rate-limited (~200 req/hr/IP), and may break without notice. **Do not depend on them.** |
| **Alpha Vantage (free)** | Earnings & fundamentals | **Not viable for v1.** Free tier = **25 requests/day** (was 500/day in older docs). Cannot support 20–30 tickers. Use **Finnhub** instead for fundamentals on free tier. |
| **alpaca-trade-api** (Python package) | Broker SDK | **Deprecated.** Use **`alpaca-py`** (official SDK). |

### Pre-build verification script (run before Phase 1)

Run the included verification script:

```bash
cp .env.example .env   # fill in your keys first
pip install -r requirements.txt
python scripts/verify_access.py
```

Checks performed:
- `alpaca` — paper account + daily bars for test ticker
- `anthropic` — minimal Haiku call (consumes small credit; check balance before/after)
- `fred` — VIXCLS latest observation
- `finnhub` — quote for test ticker
- `massive` — optional; skipped if key not set

**Gate rule:** If any **required** check fails, stop and resolve before proceeding to the next phase. See [Fees at a Glance](./FEES_AT_A_GLANCE.md) for Anthropic credit verification steps.

---

## External Dependencies Matrix

Verified against official docs and pricing pages as of **July 2026**. Re-verify before production; free tiers change frequently.

| Provider | Auth | Free tier limits | Paid entry | v1 role | SDK |
|----------|------|------------------|------------|---------|-----|
| Alpaca | API key + secret | 200 trading req/min; paper free | Live trading = funded account | Broker + primary OHLCV | `alpaca-py` |
| Anthropic | API key (`sk-ant-...`) | ~$5 one-time trial credits only | Prepaid credits, pay-per-token | Thesis generation | `anthropic` |
| FRED | API key (32 chars) | ~120 req/min | N/A (always free) | VIX, macro, release dates | `fredapi` or REST |
| Finnhub | API key | 60 req/min, personal use | $50+/mo (pricing page shows higher tiers) | Fundamentals, company news | `finnhub-python` or REST |
| Massive/Polygon | API key | 5 req/min, delayed | Stocks Starter ~$29/mo | Historical backfill only | `massive` (formerly polygon-api-client) |
| Benzinga | AWS Marketplace key | Basic tier free | Premium tiers paid | Optional news | REST via AWS |
| NewsAPI.org | API key | 100 req/day, dev only | $449/mo business | Optional news (dev) | REST |

---

## Overview

This agent does **not** auto-trade. It is a **5-layer** reasoning system that:

- Continuously ingests market signals
- **Pre-filters** tickers through deterministic rules (Layer 1.5) to control cost and noise
- Builds falsifiable investment theses using AI (Layer 2)
- Enforces hard risk rules in code (Layer 3)
- Presents ranked opportunities for **human approval** before any order executes (Layer 4)

### Benchmark Reference

A similar architecture produced +41% over 18 months vs. +22% S&P 500 and +15% passive portfolio over the same period (per newsletter case study). Past performance does not guarantee future results. **Do not use this benchmark to skip paper trading or backtesting.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Signal Collection                                     │
│  Alpaca bars, Finnhub fundamentals/news, FRED macro, indicators │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1.5: Signal Gate (deterministic, no LLM)                 │
│  RSI cross, volume spike, MA break, news event, invalidation hit  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼ (only triggered tickers)
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Reasoning Engine (Claude)                             │
│  Structured thesis JSON + citation validation                   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Risk Guardrail (hard rules in Python)                 │
│  7 rules + liquidity, cash reserve, dedup, drawdown breaker     │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Human-in-the-Loop Dashboard                           │
│  Approve / Reject / Snooze → idempotent order submission        │
└─────────────────────────────────────────────────────────────────┘
```

Each layer has a discrete job. Their combination — not any single layer — produces the result.

---

## Layer 1 — Signal Collection

All feeds pipe into a **central data normalizer**: a Python service that timestamps, cleans, validates freshness, and stores everything in a database.

### v1 Data Source Plan (verified accessible)

| Signal Type | Primary Source | Fallback | Tier | Est. Cost |
|---|---|---|---|---|
| Real-time / recent OHLCV | **Alpaca Market Data API** | — | Free (IEX on paper) | $0 |
| Historical OHLCV (backfill) | **Massive (Polygon)** | Alpaca history | Free tier (rate-limited) | $0 |
| Earnings & fundamentals | **Finnhub** | — | Free (60/min, personal) | $0 |
| Company news headlines | **Finnhub company-news** | Benzinga Basic (optional) | Free | $0 |
| Macro indicators (VIX, rates) | **FRED** | — | Free | $0 |
| Sector/ETF comparison | Alpaca bars | — | Free | $0 |
| Economic calendar (Rule 6) | **FRED releases/dates** or **SiftingIO** | Static FOMC schedule file | Free | $0 |
| Social sentiment | **Removed from v1** | — | — | — |

### Data Normalizer Requirements

- Timestamp and tag every data point by `source`, `ticker`, and ` ingested_at`
- Deduplicate news headlines within a rolling 1-hour window (hash on normalized title)
- Store OHLCV in standard format: `(ticker, timestamp, open, high, low, close, volume)`
- Sentiment scores normalized to range: `-1.0` (negative) to `+1.0` (positive)
- **Staleness detection:** reject signal generation if latest price for ticker is > 20 minutes old during market hours
- **Market calendar:** respect NYSE holidays and early-close days; do not poll outside 9:30am–4:00pm ET (or configured extended hours if explicitly enabled later)
- **Corporate actions:** log splits/dividends when detected; flag affected tickers for manual review until adjustment logic is implemented
- **Rate limiting:** enforce per-provider limits in code (see External Dependencies Matrix)
- Run on a **15-minute polling cycle** during market hours for fundamentals/news/macro; use Alpaca WebSocket or batched REST for prices

### Polling Budget (20–30 tickers, 15-min cycle)

| Provider | Calls per cycle (estimated) | Daily calls (6.5 hr × 4 cycles) | Within free tier? |
|----------|----------------------------|----------------------------------|-------------------|
| Alpaca bars | 1 batch or 30 individual | ~120 | Yes (200/min) |
| Finnhub (quote + news) | ~2 per ticker max | ~240–360 | Yes (60/min with throttling) |
| FRED (VIX + macro) | ~5 total | ~20 | Yes |
| Massive (backfill) | Off hot path | N/A | Yes if batched separately |
| Claude (Layer 2) | **Only gated tickers** (~2–8/day target) | ~2–8 | Yes (cost-controlled) |

### Technical Indicators to Compute (per ticker)

Compute in Python using `pandas-ta` (preferred; pure Python) or `ta-lib` (optional; requires C library install):

- RSI (14-period)
- MACD (12/26/9)
- 50-day and 200-day moving averages
- Bollinger Bands (20-period, 2 std dev)
- Volume vs. 30-day average volume
- ATR (14-period) for volatility

Store computed indicators in `technical_indicators` table (do not recompute inside Claude prompts).

### Error Handling

- Retry with exponential backoff on 429/5xx (max 3 retries)
- Circuit breaker: after 5 consecutive failures for a provider, pause that provider for 15 minutes and alert
- Log every failed fetch with provider, ticker, status code, and timestamp

---

## Layer 1.5 — Signal Gate

**Purpose:** Reduce Claude API cost by 80–95% and reduce noise. Only tickers that pass deterministic pre-filters proceed to Layer 2.

### Pre-Filter Triggers (any one fires → candidate)

| Trigger ID | Condition | Data required |
|------------|-----------|---------------|
| `RSI_CROSS` | RSI(14) crossed above 30 or below 70 since last cycle | `technical_indicators` |
| `MA_CROSS` | Price crossed 50-day MA or 200-day MA | `ohlcv`, indicators |
| `VOLUME_SPIKE` | Volume > 2× 30-day average | `ohlcv`, indicators |
| `NEWS_EVENT` | New headline in last 2h for ticker (from Finnhub) | `news_headlines` |
| `INVALIDATION_HIT` | Open position breached an active thesis invalidation condition | `portfolio_positions`, `theses` |
| `MANUAL_WATCH` | User manually flagged ticker for re-analysis | `watchlist.force_scan` |

### Gate Output

```json
{
  "ticker": "NVDA",
  "triggered_at": "2026-07-23T14:30:00Z",
  "triggers": ["RSI_CROSS", "VOLUME_SPIKE"],
  "gate_status": "PASS",
  "market_data_bundle_id": "uuid-reference-to-snapshot"
}
```

### Dedup Rule

- Do not re-send the same ticker to Claude within **24 hours** unless `INVALIDATION_HIT` or `MANUAL_WATCH` fired

---

## Layer 2 — Reasoning Engine

This is the AI core. For each **gated** ticker, Claude generates a **structured investment thesis** in JSON format. The thesis must be falsifiable — not vague.

### Claude API Configuration

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    temperature=0,  # deterministic output
    system=SYSTEM_PROMPT,
    messages=[{
        "role": "user",
        "content": f"Analyze the following market data for {ticker} and produce a JSON thesis:\n\n{json.dumps(market_data)}"
    }],
    # Prefer structured output when available; otherwise parse + validate
)
```

**Pricing reference (July 2026):** Claude Sonnet 4.6 = **$3/M input tokens, $15/M output tokens**. Use prompt caching for the static system prompt (~90% savings on repeated calls). Typical gated thesis call ≈ 4–8K input + 500–1K output ≈ **$0.02–0.05 per thesis** with caching.

### System Prompt (Reasoning Layer)

```
You are a disciplined quantitative investment analyst. You do not give vague opinions.
For every ticker you analyze, you must produce a structured thesis with:
1. Specific, data-backed reasons to buy, sell, or hold
2. Explicit risks that could undermine the position
3. Exact invalidation conditions — the specific price level, event, or data point
   that would prove the thesis wrong
4. A conviction score from 1–10, where 10 means extremely high confidence
   (scores above 9.5 trigger an automatic 24-hour review delay)

You must cite which data signals drove each conclusion using the citation format:
  {"field": "<key from market_data>", "value": "<exact value from market_data>"}

Never recommend a position without an invalidation condition.
Never cite data that is not present in the provided market_data bundle.
Always consider the macro environment, sector trends, and correlation to existing holdings.
Output must be valid JSON matching the provided schema exactly.
```

### Post-Generation Validation (mandatory, in code)

1. **Schema validation** — Pydantic model `ThesisOutput` (see [Thesis JSON Schema](#thesis-json-schema))
2. **Citation validation** — every claim in `buy_reasons`, `risks`, and `invalidation_conditions` must reference a field present in `market_data`
3. **Retry once** on validation failure with error feedback to Claude
4. **Quarantine** on second failure — status = `VALIDATION_FAILED`, do not show in dashboard

### Signal Types

| Type | When generated |
|------|----------------|
| `BUY` | New entry opportunity |
| `SELL` | Exit recommendation for existing position |
| `HOLD` | Maintain position, no new action |
| `REDUCE` | Trim position size |

---

## Layer 3 — Risk Guardrail

These rules are enforced **in code**, before any signal reaches the dashboard. They **cannot** be overridden by the AI.

### The 7 Hard Rules (+ 4 additional v2 rules)

| Rule | ID | Description | Action on breach |
|------|----|-------------|------------------|
| 1 | `MAX_POSITION` | No single stock > 8% of total portfolio value | Cap `suggested_position_size_pct` at 8% |
| 2 | `SECTOR_CAP` | No single sector > 25% of portfolio | Status = `BLOCKED` |
| 3 | `STOP_LOSS` | Auto-flag any open position down > 7% from entry | Create `SELL` suggestion with status `STOP_LOSS_FLAGGED` |
| 4 | `OVERCONFIDENCE` | Conviction > 9.5 | Status = `DELAYED_24HR` (show after 24h) |
| 5 | `CORRELATION` | Block new BUY if correlation to any holding > 0.85 | Status = `BLOCKED` |
| 6 | `NEWS_BLACKOUT` | No new BUY signals within 2hr of scheduled high-impact macro release (FOMC, CPI, NFP) | Status = `BLOCKED` |
| 7 | `VOLATILITY_GATE` | If VIX > 35, reduce all suggested position sizes by 50% | Halve size, add flag |
| 8 | `CASH_RESERVE` | Never deploy more than 90% of portfolio | Cap total deployed + new suggestion |
| 9 | `LIQUIDITY` | Block if 30-day avg daily dollar volume < $1M | Status = `BLOCKED` |
| 10 | `DRAWDOWN_BREAKER` | If portfolio down > 15% from peak, pause all new BUY signals | Status = `BLOCKED` until manual reset |
| 11 | `SIGNAL_DEDUP` | Same ticker BUY signal within 24h | Status = `BLOCKED` (unless invalidation trigger) |

### Rule Implementation Details

**Rule 3 — Stop-loss:** Checked every polling cycle against `portfolio_positions` synced from Alpaca. Does not auto-sell; creates a dashboard alert and optional `SELL` thesis.

**Rule 5 — Correlation:** 90-day daily return correlation matrix, refreshed daily. Uses `pandas` correlation on aligned return series.

**Rule 6 — News blackout:** Load high-impact events from FRED `releases/dates` (release_id for FOMC, CPI) or SiftingIO economic calendar. Block window = `[event_time - 2hr, event_time + 2hr]`.

**Rule 2 — Sector:** Resolve sector from `watchlist.sector` (required field). Thesis JSON also includes `sector` for audit.

### Risk Engine Python Interface

```python
from dataclasses import dataclass
from enum import Enum

class ThesisStatus(str, Enum):
    PENDING = "PENDING"
    DELAYED_24HR = "DELAYED_24HR"
    BLOCKED = "BLOCKED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SNOOZED = "SNOOZED"
    STOP_LOSS_FLAGGED = "STOP_LOSS_FLAGGED"

@dataclass
class RiskResult:
    thesis: dict
    status: ThesisStatus
    flags: list[str]
    blocked_rules: list[str]

def apply_risk_guardrails(
    thesis: dict,
    portfolio: PortfolioState,
    macro: MacroSnapshot,
    calendar: EconomicCalendar,
) -> RiskResult:
    """Apply all 11 rules. Returns modified thesis with status and flags."""
    ...
```

### Unit Test Requirement

Every rule must have **at least 2 unit tests**: one pass case, one breach case. See [Gate-Based Testing Plan](#gate-based-testing-plan).

---

## Layer 4 — Human-in-the-Loop Dashboard

You **never** receive an order — you receive a **briefing**. Nothing executes without your approval.

### Dashboard Features

- **Signal queue:** Top 3–5 ranked opportunities by conviction score (excludes BLOCKED, DELAYED, VALIDATION_FAILED)
- **Thesis card per signal:** Full reasoning, data sources, risk flags, citation links to raw data
- **Blocked signals panel:** Show BLOCKED/DELAYED signals with reason (transparency)
- **Risk flags:** Highlighted prominently in red/amber
- **Actions per card:** `Approve` / `Reject` / `Snooze 24hrs`
- **Portfolio view:** Current positions synced from Alpaca, P&L, stop-loss alerts
- **Macro panel:** VIX, S&P 500, sector heatmap
- **Audit log:** Every decision timestamped with full thesis snapshot at decision time
- **Performance view:** Rolling win rate, avg return per signal, vs SPY benchmark

### Authentication (v1 minimum)

- FastAPI backend protected by API key header (`X-API-Key`) or HTTP Basic Auth
- Keys stored in `.env`, never committed
- CORS restricted to localhost in dev; specific origin in production

### Real-Time Updates

- Server-Sent Events (SSE) or WebSocket for new signals and portfolio updates
- Fallback: 30-second polling

### Snooze Behavior

- Snoozed thesis hidden from queue for 24 hours
- After expiry, status returns to `PENDING` if still valid (re-run risk checks first)

### On Approval Flow

1. User taps **Approve** on a thesis card
2. Frontend sends `POST /execute` with `thesis_id` and `idempotency_key` (UUID)
3. Backend verifies: thesis status = PENDING, not expired, risk re-check passes
4. Backend calculates share count: `floor((portfolio_value × position_pct / 100) / current_price)`
5. Order submitted to **Alpaca paper account** via `alpaca-py` as **limit order** at current ask (or market order with explicit user setting)
6. Order confirmation stored in database with thesis ID, idempotency key, and market snapshot
7. If idempotency key already used → return existing order (no duplicate)

---

## Order Lifecycle

```
THESIS_PENDING
    ├── APPROVE (human) ──► ORDER_SUBMITTING ──► ORDER_SUBMITTED ──► FILLED
    │                                              ├── PARTIAL_FILL ──► FILLED
    │                                              └── REJECTED (broker)
    ├── REJECT (human) ──► REJECTED (terminal)
    └── SNOOZE ──► SNOOZED ──► (24h expiry) ──► THESIS_PENDING (re-validate)

INVALIDATION_TRIGGERED ──► SELL_SUGGESTION (PENDING) ──► (human approve) ──► ORDER flow

STOP_LOSS_FLAGGED ──► SELL_SUGGESTION (PENDING) ──► (human approve) ──► ORDER flow
```

### Order Types (v1)

| Scenario | Order type | Notes |
|----------|-----------|-------|
| New BUY (default) | Limit at current ask + 0.1% buffer | Avoids bad market fills |
| Urgent exit (stop-loss) | Limit at current bid − 0.1% | User can override to market |
| Partial exit (REDUCE) | Limit, qty = calculated trim | |

### Idempotency

- Every approve action requires a client-generated UUID
- Stored in `orders.idempotency_key` with UNIQUE constraint
- Duplicate submit returns HTTP 200 with existing order (not a new order)

---

## Tech Stack

```
Language:         Python 3.11+
Broker:           Alpaca Markets (paper first, then live) via alpaca-py
Market Data:      Alpaca (live/recent) + Massive/Polygon (historical backfill)
Fundamentals/News: Finnhub (primary)
Macro:            FRED
Economic Calendar: FRED releases/dates or SiftingIO (optional)
AI Reasoning:     Anthropic Claude API (claude-sonnet-4-6)
Tech Indicators:  pandas-ta
Scheduler:        APScheduler (15-min scans during market hours)
Database:         SQLite (v1) → PostgreSQL (v2 / production)
Backend API:      FastAPI (Python)
Validation:       Pydantic v2
Migrations:       Alembic (when moving to PostgreSQL)
Frontend:         React + Tailwind CSS
Hosting:          Local PC (v1) or VPS (~$10/mo)
Testing:          pytest
```

### Key Python Libraries

```
alpaca-py              # NOT alpaca-trade-api (deprecated)
anthropic
finnhub-python         # or requests
fredapi                # or requests
massive                # formerly polygon-api-client
pandas
pandas-ta
pydantic>=2.0
apscheduler
fastapi
uvicorn
sqlalchemy
alembic
pytest
pytest-asyncio
httpx
python-dotenv
```

---

## Database Schema

SQLite v1 with indexes and constraints. Upgrade path to PostgreSQL via Alembic.

```sql
-- Tickers being watched
CREATE TABLE watchlist (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL UNIQUE,
  sector TEXT NOT NULL,           -- required for Rule 2
  added_date DATE,
  force_scan BOOLEAN DEFAULT 0,   -- manual re-scan trigger
  active BOOLEAN DEFAULT 1
);

-- Raw price data
CREATE TABLE ohlcv (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  open REAL, high REAL, low REAL, close REAL, volume INTEGER,
  source TEXT NOT NULL DEFAULT 'alpaca',
  UNIQUE(ticker, timestamp, source)
);
CREATE INDEX idx_ohlcv_ticker_ts ON ohlcv(ticker, timestamp);

-- Precomputed indicators
CREATE TABLE technical_indicators (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  rsi_14 REAL,
  macd REAL, macd_signal REAL, macd_hist REAL,
  ma_50 REAL, ma_200 REAL,
  bb_upper REAL, bb_mid REAL, bb_lower REAL,
  volume_ratio REAL,          -- vs 30-day avg
  atr_14 REAL,
  UNIQUE(ticker, timestamp)
);

-- News headlines
CREATE TABLE news_headlines (
  id INTEGER PRIMARY KEY,
  ticker TEXT,
  headline TEXT NOT NULL,
  headline_hash TEXT NOT NULL,  -- for dedup
  source TEXT NOT NULL,
  url TEXT,
  published_at DATETIME,
  sentiment_score REAL,         -- -1.0 to +1.0, optional
  ingested_at DATETIME NOT NULL,
  UNIQUE(headline_hash)
);

-- Macro snapshots
CREATE TABLE macro_snapshots (
  id INTEGER PRIMARY KEY,
  captured_at DATETIME NOT NULL,
  vix REAL,
  spy_close REAL,
  ten_year_yield REAL,
  raw_json TEXT
);

-- Portfolio positions (synced from Alpaca)
CREATE TABLE portfolio_positions (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  qty REAL NOT NULL,
  avg_entry_price REAL NOT NULL,
  current_price REAL,
  market_value REAL,
  unrealized_pl REAL,
  unrealized_pl_pct REAL,
  sector TEXT,
  synced_at DATETIME NOT NULL
);

-- Signal gate events
CREATE TABLE signal_gate_events (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  triggered_at DATETIME NOT NULL,
  triggers TEXT NOT NULL,       -- JSON array of trigger IDs
  gate_status TEXT NOT NULL,    -- PASS, SKIP
  market_data_bundle_id TEXT
);

-- Market data bundles (snapshot at thesis time)
CREATE TABLE market_data_bundles (
  id TEXT PRIMARY KEY,          -- UUID
  ticker TEXT NOT NULL,
  created_at DATETIME NOT NULL,
  bundle_json TEXT NOT NULL     -- full payload sent to Claude
);

-- Generated theses
CREATE TABLE theses (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  sector TEXT NOT NULL,
  generated_at DATETIME NOT NULL,
  signal_type TEXT NOT NULL,    -- BUY, SELL, HOLD, REDUCE
  conviction_score REAL,
  thesis_json TEXT NOT NULL,
  risk_flags TEXT,              -- JSON array
  blocked_rules TEXT,           -- JSON array of rule IDs
  status TEXT NOT NULL,
  market_data_bundle_id TEXT REFERENCES market_data_bundles(id),
  delayed_until DATETIME,       -- for DELAYED_24HR
  UNIQUE(ticker, generated_at)  -- prevent exact duplicates
);
CREATE INDEX idx_theses_status ON theses(status, generated_at);

-- User decisions (immutable audit)
CREATE TABLE decisions (
  id INTEGER PRIMARY KEY,
  thesis_id INTEGER NOT NULL REFERENCES theses(id),
  decision TEXT NOT NULL,       -- APPROVED, REJECTED, SNOOZED
  decided_at DATETIME NOT NULL,
  notes TEXT,
  snapshot_json TEXT NOT NULL   -- full thesis + market state at decision time
);

-- Orders placed
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  thesis_id INTEGER NOT NULL REFERENCES theses(id),
  idempotency_key TEXT NOT NULL UNIQUE,
  ticker TEXT NOT NULL,
  side TEXT NOT NULL,           -- buy, sell
  qty REAL NOT NULL,
  order_type TEXT NOT NULL,     -- limit, market
  limit_price REAL,
  alpaca_order_id TEXT,
  submitted_at DATETIME,
  filled_at DATETIME,
  filled_qty REAL,
  filled_avg_price REAL,
  status TEXT NOT NULL          -- SUBMITTED, FILLED, PARTIAL, REJECTED, CANCELLED
);

-- System audit log
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  event_type TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  details_json TEXT,
  created_at DATETIME NOT NULL
);
```

---

## Thesis JSON Schema

Formal contract for Layer 2 output. Implement as Pydantic model `ThesisOutput`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "ticker", "sector", "signal_date", "signal_type",
    "conviction_score", "thesis", "suggested_position_size_pct",
    "time_horizon", "data_sources_used", "citations"
  ],
  "properties": {
    "ticker": { "type": "string", "pattern": "^[A-Z]{1,5}$" },
    "sector": { "type": "string" },
    "signal_date": { "type": "string", "format": "date" },
    "signal_type": { "enum": ["BUY", "SELL", "HOLD", "REDUCE"] },
    "conviction_score": { "type": "number", "minimum": 1, "maximum": 10 },
    "thesis": {
      "type": "object",
      "required": ["buy_reasons", "risks", "invalidation_conditions"],
      "properties": {
        "buy_reasons": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
        "risks": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
        "invalidation_conditions": { "type": "array", "items": { "type": "string" }, "minItems": 1 }
      }
    },
    "suggested_position_size_pct": { "type": "number", "minimum": 0, "maximum": 8 },
    "time_horizon": { "type": "string" },
    "data_sources_used": { "type": "array", "items": { "type": "string" } },
    "citations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["field", "value"],
        "properties": {
          "field": { "type": "string" },
          "value": {}
        }
      },
      "minItems": 1
    }
  }
}
```

### Example Thesis Output

```json
{
  "ticker": "NVDA",
  "sector": "Technology",
  "signal_date": "2026-06-28",
  "signal_type": "BUY",
  "conviction_score": 7.2,
  "thesis": {
    "buy_reasons": [
      "RSI(14) at 38.2 crossed above 35 after 3-week oversold period",
      "Q1 EPS beat consensus by 12%",
      "News sentiment +0.74 over last 48hrs (3 headlines)"
    ],
    "risks": [
      "Export restriction news pending",
      "P/E at 38x — elevated vs semiconductor peer median 28x"
    ],
    "invalidation_conditions": [
      "Price breaks below $112.00",
      "Negative earnings revision published",
      "Sector ETF SOXX drops more than 5% in a single session"
    ]
  },
  "suggested_position_size_pct": 4.5,
  "time_horizon": "4-8 weeks",
  "data_sources_used": ["price", "earnings", "news_sentiment", "rsi", "sector_momentum"],
  "citations": [
    {"field": "indicators.rsi_14", "value": 38.2},
    {"field": "fundamentals.eps_surprise_pct", "value": 12.0},
    {"field": "news.sentiment_48h", "value": 0.74}
  ]
}
```

---

## Gate-Based Testing Plan

**Principle:** No phase begins until all gates for the previous phase pass. All tests run via `pytest`. CI runs on every commit (GitHub Actions or local pre-push hook).

### Gate 0 — Access Verification

| Test | Pass criteria |
|------|---------------|
| `test_alpaca_account` | Paper account returns valid balance |
| `test_alpaca_bars` | SPY daily bar returned |
| `test_anthropic_api` | Minimal message returns 200 |
| `test_fred_vix` | VIXCLS series has recent observation |
| `test_finnhub_quote` | AAPL quote returns price > 0 |

**Script:** `scripts/verify_access.py` — exit code 0 required.

### Gate 1 — Data Pipeline

| Test | Pass criteria |
|------|---------------|
| `test_ohlcv_ingestion` | 5 tickers stored with no duplicates |
| `test_indicator_computation` | RSI/MACD/MA values computed and stored |
| `test_staleness_detection` | Stale data (>20 min) flagged |
| `test_rate_limiter` | 429 from provider triggers backoff, not crash |
| `test_market_calendar` | No ingestion scheduled on NYSE holiday |

### Gate 1.5 — Backtest Skeleton

| Test | Pass criteria |
|------|---------------|
| `test_backtest_runs` | 2-year replay on 5 tickers completes without error |
| `test_backtest_metrics` | Outputs win rate, max drawdown, total return vs SPY |
| `test_signal_gate_historical` | Gate triggers fire on known RSI cross dates |

### Gate 2 — Reasoning Engine

| Test | Pass criteria |
|------|---------------|
| `test_thesis_schema_validation` | Valid JSON passes; invalid rejected |
| `test_citation_validation` | Thesis citing nonexistent field rejected |
| `test_retry_on_failure` | Second attempt succeeds after first invalid response |
| `test_quarantine` | Two failures → status VALIDATION_FAILED |
| `test_gate_dedup` | Same ticker not sent twice within 24h |

### Gate 3 — Risk Engine

| Test | Pass criteria |
|------|---------------|
| `test_rule_max_position` | 10% suggestion capped to 8% |
| `test_rule_sector_cap` | Blocked when sector at 26% |
| `test_rule_stop_loss` | 8% loss triggers STOP_LOSS_FLAGGED |
| `test_rule_overconfidence` | Score 9.7 → DELAYED_24HR |
| `test_rule_correlation` | 0.90 correlation → BLOCKED |
| `test_rule_blackout` | BUY blocked within 2hr of FOMC event |
| `test_rule_vix` | VIX=40 → position halved |
| `test_rule_cash_reserve` | Cannot deploy beyond 90% |
| `test_rule_liquidity` | Low volume ticker blocked |
| `test_rule_drawdown` | 16% drawdown pauses new BUYs |
| `test_rule_dedup` | Duplicate BUY within 24h blocked |

### Gate 4 — Dashboard & Execution

| Test | Pass criteria |
|------|---------------|
| `test_api_auth` | Unauthenticated request → 401 |
| `test_signals_endpoint` | Returns ranked pending theses |
| `test_approve_idempotent` | Same idempotency key → same order, not duplicate |
| `test_paper_order` | Approved thesis → Alpaca paper order FILLED or SUBMITTED |
| `test_audit_snapshot` | Decision record contains full thesis JSON |
| `test_sse_updates` | New signal pushes to connected client |

### Gate 5 — Paper Trading (60–90 days, manual)

| Metric | Track weekly |
|--------|-------------|
| Signal win rate (30d rolling) | vs 50% baseline |
| Avg return per approved BUY | After estimated slippage |
| Invalidation hit rate | Did exits happen when conditions met? |
| Sharpe ratio vs SPY | Rolling 90d |
| Max drawdown | Must stay < 15% or investigate |

**Gate 5 pass criteria:** 60+ days paper trading with documented metrics before considering live.

### Gate 6 — Live (manual decision)

- Switch to Alpaca live keys in separate `.env.live` file
- Start with $5,000–$10,000 max
- Human approval remains permanent — never enable auto-execution

---

## Phased Build Plan

### Phase 0 — Foundation & Access (before any feature code)

- [ ] Complete [Pre-Build Access Checklist](#pre-build-access-checklist-read-first)
- [ ] Run `scripts/verify_access.py` — all required checks pass
- [ ] Create Python project with virtual environment
- [ ] Set up `.env` with all API keys (never commit)
- [ ] Define Pydantic models for all schemas
- [ ] Set up pytest + CI skeleton
- [ ] **Gate 0 must pass**

### Phase 1 — Data Pipeline

- [ ] Build data fetcher for 20–30 watched tickers (Alpaca OHLCV)
- [ ] Compute and store technical indicators (pandas-ta)
- [ ] Integrate Finnhub for fundamentals + company news
- [ ] Integrate FRED for VIX and macro snapshots
- [ ] SQLite database with full schema + indexes
- [ ] APScheduler for 15-min polling during market hours
- [ ] Rate limiter per provider
- [ ] **Gate 1 must pass**

### Phase 1.5 — Signal Gate + Backtest

- [ ] Implement all pre-filter triggers
- [ ] Build 2–5 year backtest replay on watchlist
- [ ] Output metrics: win rate, max drawdown, return vs SPY
- [ ] Tune gate thresholds based on backtest results
- [ ] **Gate 1.5 must pass**

### Phase 2 — Reasoning Layer

- [ ] Integrate Anthropic Claude API with prompt caching
- [ ] Thesis generation for gated tickers only
- [ ] Schema + citation validation with retry/quarantine
- [ ] Store market data bundles for audit
- [ ] **Gate 2 must pass**

### Phase 3 — Risk Layer

- [ ] Implement all 11 risk rules
- [ ] Portfolio sync from Alpaca (positions, cash, equity)
- [ ] Correlation matrix (90-day, daily refresh)
- [ ] Economic calendar integration for Rule 6
- [ ] Unit tests for every rule
- [ ] **Gate 3 must pass**

### Phase 4 — Dashboard & Execution

- [ ] React frontend with Tailwind CSS
- [ ] Thesis cards, blocked signals panel, portfolio view, macro panel
- [ ] FastAPI endpoints: `/signals`, `/portfolio`, `/execute`, `/health`
- [ ] API authentication
- [ ] SSE for real-time updates
- [ ] Approve → idempotent Alpaca paper order
- [ ] Immutable audit log with decision snapshots
- [ ] **Gate 4 must pass**

### Phase 5 — Paper Trading (60–90 days)

- [ ] Run on paper only — do not go live
- [ ] Track all [Evaluation Metrics](#evaluation-metrics) weekly
- [ ] Refine prompts and gate thresholds based on results
- [ ] Tune risk rules based on observed behavior
- [ ] **Gate 5 must pass (manual review)**

### Phase 6 — Live (only after Gate 5)

- [ ] Switch to Alpaca live keys (separate env file)
- [ ] Start with small capital ($5,000–$10,000)
- [ ] Never enable auto-execution
- [ ] Monthly performance review vs S&P 500

---

## Estimated Monthly Cost

### v1 Realistic (personal use, gated Claude calls)

| Item | Cost | Notes |
|------|------|-------|
| Alpaca brokerage + paper | $0 | |
| Finnhub (free, personal) | $0 | |
| FRED | $0 | |
| Massive/Polygon (free, backfill only) | $0 | |
| Claude API (2–8 theses/day, cached) | **$5–25** | ~60–240 theses/month; free starter credits may cover early Gate 0–2 testing |
| VPS (optional) | $0–10 | Can run locally for v1 |
| Benzinga news (optional) | $0 | AWS Marketplace free tier |
| **Total v1** | **$5–35/mo** | |

### v1 If You Skip Signal Gating (NOT recommended)

| Item | Cost |
|------|------|
| Claude API (780 calls/day, 30 tickers × 26 cycles) | **$150–400/mo** |

### Paid Upgrades (only if needed later)

| Upgrade | When needed | Cost |
|---------|-------------|------|
| Massive Stocks Starter | Faster historical backfill | ~$29/mo |
| Alpaca real-time data | Live trading with multi-exchange quotes | ~$9–99/mo |
| Finnhub All-In-One | Global fundamentals, more history | $50+/mo (verify current pricing) |
| NewsAPI Business | Production news in app | $449/mo |
| Reddit commercial API | Social sentiment at scale | $0.24/1K calls + approval |

---

## Observability, Security & Operations

### Logging

- Structured JSON logs (timestamp, level, component, ticker, event)
- Log every API call: provider, endpoint, latency, status code
- Log every thesis generation: ticker, status, token count, cost estimate

### Health Checks

```
GET /health  → {"status": "ok", "db": "ok", "scheduler": "running"}
GET /ready   → {"alpaca": "ok", "anthropic": "ok", "last_ingestion": "..."}
```

### Alerts (v1 minimum)

- Email or console alert if ingestion fails for 2+ consecutive cycles during market hours
- Alert if Claude validation failure rate > 20% in a day
- Alert if any order submission fails

### Secrets Management

- All keys in `.env` (local) or environment variables (VPS)
- Separate `.env.paper` and `.env.live` — never mix keys
- `.gitignore` must include `.env*`

### Backup

- Daily SQLite backup to local directory (or cloud if on VPS)
- Retain 30 days of backups

---

## Evaluation Metrics

Track weekly during Phase 5 paper trading:

| Metric | Formula | Target (investigate if) |
|--------|---------|------------------------|
| Signal win rate | % of approved BUYs profitable at horizon | < 45% |
| Avg return per signal | Mean return of approved signals at time_horizon | < 0% |
| Invalidation accuracy | % of invalidation triggers that preceded further loss | < 60% |
| Sharpe vs SPY | (portfolio return − risk-free) / std dev vs SPY | Below SPY for 90d |
| Max drawdown | Peak-to-trough portfolio decline | > 15% |
| Claude cost per signal | API spend / signals generated | > $0.10 |
| Gate pass rate | % of tickers passing gate per cycle | < 1% or > 30% (tune thresholds) |
| Validation failure rate | VALIDATION_FAILED / total Claude calls | > 10% |

---

## Design Decisions & Critical Mistakes

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Human approval required, always | Removes emotional bias from execution while keeping human judgment |
| Falsifiable thesis format | Forces AI to define when it's wrong — prevents holding losers |
| Signal gate before Claude | Controls cost and noise; makes backtesting feasible |
| Citation validation | Prevents AI hallucination of data not in the bundle |
| Overconfidence block at 9.5+ | High conviction is often a blind spot |
| Paper trade 60–90 days minimum | Live slippage and psychology differ from backtests |
| SQLite for v1 | Zero-config; upgrade to PostgreSQL when multi-user |
| Limit orders by default | Better fill control than market orders |
| Idempotent order submission | Prevents duplicate orders from double-click or retry |

### 3 Critical Mistakes to Avoid

1. **Skipping paper trading** — minimum 60 days paper before live
2. **No invalidation conditions** — every thesis must define when it's wrong
3. **Auto-execution** — human approval is permanent, not a feature to remove
4. **Skipping signal gating** — will burn API budget and generate noise (added v2)
5. **Building on unavailable free APIs** — verify access before coding (added v2)

---

## Future Enhancements (v2+)

- Options signal layer (covered calls on existing positions)
- Earnings calendar integration (suppress signals ±48hr around earnings)
- Multi-timeframe analysis (short vs medium-term thesis tracks)
- Performance attribution (which signals drive wins)
- Email/SMS alerts for time-sensitive signals
- Portfolio rebalancing agent (quarterly review)
- PostgreSQL migration + multi-user auth
- Reddit/StockTwits sentiment (only after paid API approval)

---

## Legal Disclaimer

This document is for educational and informational purposes only. Nothing here constitutes investment advice. All investing involves risk of loss. Past performance does not guarantee future results. Always do your own research and consult a licensed financial advisor before making investment decisions.

**Additional notes:**
- Finnhub free tier is licensed for **personal use only**
- NewsAPI free tier is for **development/testing only**
- Alpaca retail accounts are **US-only**
- Pattern Day Trader (PDT) rules apply if account < $25,000 and day trading
- Maintain immutable audit records of all decisions for personal review

---

## Reference Sources

- Newsletter case study: *"I Built an AI Investment Agent That Made My Portfolio +41% in 18 Months"* — Future Digest, June 28, 2026
- Alpaca docs: [docs.alpaca.markets](https://docs.alpaca.markets)
- Alpaca Python SDK: [alpaca-py](https://github.com/alpacahq/alpaca-py)
- Anthropic pricing: [docs.anthropic.com/en/docs/about-claude/pricing](https://docs.anthropic.com/en/docs/about-claude/pricing)
- FRED API: [fred.stlouisfed.org/docs/api/fred](https://fred.stlouisfed.org/docs/api/fred/)
- Finnhub: [finnhub.io/docs/api](https://finnhub.io/docs/api)
- Massive (Polygon): [massive.com/docs](https://massive.com/docs)
- Reddit developer terms: [redditinc.com/policies/developer-terms](https://redditinc.com/policies/developer-terms)

---

*Document prepared: June 28, 2026 (v1)*
*Patched: July 23, 2026 (v2.1 — added Fees at a Glance + Gate 0 script)*
*Ready for handoff to development agent or PC environment*


---

<a id="docs-dashboard_one_pager-md"></a>
## `docs/DASHBOARD_ONE_PAGER.md`

# AI Investment Agent — Daily One-Pager

**You trade in E\*TRADE. This board screens, alerts, and records. No auto-orders.**

| Strategy | +1.13% target · −0.50% stop · ~3% swing · $7 buy + $7 sell · $10K → $5M goal |
|----------|--------------------------------------------------------------------------------|

---

## Before you start (once per session)

- [ ] Dashboard open · `APP_API_KEY` pasted → **Save**
- [ ] Regime banner **green** (if red = SPY+DIA+QQQ all down → **no new longs**)

---

## Morning (pre-market / open)

- [ ] Refresh data: `run_ingest.py` **or** **Pull history** + **Sync from screener**
- [ ] Read **Market Brief** (VIX + regime)
- [ ] Review **Trade Queue** — advance only names you agree with  
  `watching → approved → armed → alert → in_trade → eod → closed`
- [ ] Note **Target +1.13%** · **Stop −0.50%** · **Size** on each row

---

## During market hours

- [ ] **Run monitor** every 15–30 min (or on alert)
- [ ] On **TARGET_HIT** / **STOP_HIT** / **EOD_FLATTEN**:
  1. Execute in **E\*TRADE**
  2. **Log fill** in Trade Journal (BUY or SELL)
  3. **Acknowledge** alert on board
- [ ] Same-day flat default — close before close unless overnight approved

---

## End of day

- [ ] Final **Run monitor**
- [ ] All open positions closed in E\*TRADE (or overnight exception documented)
- [ ] Every fill logged in **Trade Journal** (buy **and** sell)
- [ ] **Generate report** (Learning) · skim **CIO Summary**
- [ ] Glance **Historical Analysis** — prior-day screener vs actual

---

## End of month (if month P&L > 0)

- [ ] Check **Month-end Sweep Preview** (10% mgmt + tax %)
- [ ] Adjust tax rate if needed → **Save rate**
- [ ] **Apply month-end sweep**

---

## Quick reference

| Section | Why |
|---------|-----|
| Regime banner | Gate for new longs |
| Goal / Cash / Month P&L | Account health |
| Trade Queue | What to watch / trade |
| Intraday Alerts | Target · stop · EOD |
| Trade Journal | Source of truth — log every fill |
| Learning + CIO | Daily feedback + actions |

**Needs API key:** Sync queue · Run monitor · Pull history · Generate report · Log trade · Apply sweep

**CLI:** `run_ingest.py` · `run_monitor.py` · `run_dashboard.py` · `run_learning.py`

---

*v3 · E\*TRADE manual · Option A (no Claude) · Product Spec v3*


---

<a id="docs-fees_at_a_glance-md"></a>
## `docs/FEES_AT_A_GLANCE.md`

# Fees at a Glance — AI Investment Agent

> **Last verified:** July 23, 2026  
> **Purpose:** One-page reference for every key, fee, and billing surprise before you start building.  
> **Related:** [Full Architecture Spec](./AI_Investment_Agent_Spec.md)

---

## Step 1 Required Keys (Phase 0)

These four keys are required before any feature code. **Only Anthropic has ongoing usage fees** for this project.

| # | Service | Key cost | Usage fees | Typical v1 monthly cost | Credit card required? |
|---|---------|----------|------------|---------------------------|----------------------|
| 1 | **Alpaca (paper)** | $0 | $0 for paper trading | $0 | No (for paper account) |
| 2 | **Anthropic (Claude API)** | $0 | **Pay-per-token** after free credits | **$0 during trial, then ~$5–25/mo** | No to start; **yes before credits run out** |
| 3 | **FRED (St. Louis Fed)** | $0 | $0 | $0 | No |
| 4 | **Finnhub** | $0 | $0 on free personal tier | $0 | No |

**Daily OHLCV note:** Finnhub **free tier does not include** `/stock/candle` (403). Phase 1 uses **yfinance** for daily bars (free) and **Finnhub** for live quotes only. Upgrade Finnhub or add Massive/Polygon later if you want a single vendor.

**Minimum cash to start building:** **$0** if Anthropic free credits are available on your account.  
**Minimum cash to finish building + paper trade:** plan **~$5–25/month** for Claude API (with signal gating).

---

## Anthropic Trial Credits — Verified Facts

Sources checked:
- [Anthropic official pricing FAQ](https://platform.claude.com/docs/en/about-claude/pricing) (July 2026)
- [Anthropic Help Center — How do I pay for API usage?](https://support.anthropic.com/en/articles/8977456-how-do-i-pay-for-my-api-usage)

### What Anthropic officially states

| Claim | Official source | Verdict |
|-------|----------------|---------|
| New users get free credits to test | Pricing FAQ: *"New users receive a **small amount of free credits** to test the API"* | **Confirmed** |
| Exact dollar amount of free credits | Not published in official docs | **Unknown — do not assume $5** |
| Permanent free API tier | Not offered | **No permanent free tier** |
| Billing model after credits | Prepaid usage credits; API stops when balance is $0 | **Confirmed** |
| Credit expiry | Purchased credits expire **1 year** from purchase date | **Confirmed** (paid credits) |
| Failed API calls charged? | Failed requests are **not charged** | **Confirmed** |

### What community reports (not guaranteed)

Third-party guides often report **~$5** after phone verification, sometimes with a "Claim" banner in Console. Treat this as **anecdotal** until you confirm on your own account under **Settings → Billing → Credit Balance**.

### How to verify on YOUR account (do this in Step 1)

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Complete email + phone verification
3. Open **Settings → Billing** (or Plans & Billing)
4. Check **Credit Balance** — note exact amount and any expiry shown
5. Run `python scripts/verify_access.py --check anthropic` (minimal test call)
6. Re-check credit balance to see cost of one test call

**Gate 0 rule:** Document your actual starting credit balance in `.env.local notes` or a personal log. Do not proceed assuming unlimited free usage.

### Estimated burn rate during build (with signal gating)

| Phase | Estimated Claude calls | Est. cost (Sonnet 4.6) |
|-------|------------------------|-------------------------|
| Gate 0 — access test | 1–3 calls | ~$0.01–0.05 |
| Gate 2 — thesis engine dev | 20–50 test calls | ~$0.50–2.00 |
| Gate 4 — dashboard integration | 10–30 test calls | ~$0.20–1.00 |
| Paper trading (60 days, gated) | ~120–480 theses | ~$5–25 total |

**Without signal gating:** costs can exceed **$150/month** — do not disable the gate.

### Cost controls built into the project

- **Signal gate (Layer 1.5):** only send triggered tickers to Claude
- **`temperature=0`:** consistent outputs, fewer retries
- **Prompt caching:** ~90% savings on repeated system prompt
- **`scripts/verify_access.py`:** uses Haiku or minimal Sonnet call for Gate 0 (cheapest possible test)
- **Validation retry limit:** max 1 retry per thesis (prevents runaway spend on bad outputs)

### When you must add payment

Add a credit card and purchase credits when:
- Free credits are exhausted (API returns billing error), OR
- You want auto-reload enabled for uninterrupted paper trading

Recommended: set a **monthly spend cap** in Console Billing before enabling auto-reload.

---

## Optional Keys (Not Required for Step 1)

| Service | Key cost | Usage fees | When needed | Skip if |
|---------|----------|------------|-------------|---------|
| **Massive (Polygon)** | $0 | $0 free tier; $29+/mo paid | Historical backfill | Using Alpaca history only |
| **Benzinga Basic** (AWS) | $0 | $0 free tier | Extra news headlines | Finnhub news is enough |
| **NewsAPI.org** | $0 dev key | **$449/mo** for production | General news (dev only) | Not using in v1 |
| **SiftingIO calendar** | $0 free tier | Paid tiers exist | Structured economic calendar | FRED release dates suffice |
| **VPS (DigitalOcean etc.)** | N/A | ~$5–12/mo | 24/5 scheduling away from PC | Running on your PC |

---

## Services Removed from v1 (Would Cost Money or Require Approval)

| Service | Why not in v1 | Cost if you insist |
|---------|---------------|-------------------|
| **Reddit API** | Manual approval; commercial use likely paid | ~$0.24/1K calls + contract |
| **StockTwits official API** | Not open to new developers | Enterprise sales |
| **Alpha Vantage free** | 25 requests/day — unusable | $49.99+/mo paid |
| **NewsAPI production** | Dev tier not for live use | $449/mo |
| **Finnhub commercial** | Free = personal use only | $50+/mo |

---

## Live Trading Fees (Phase 6 Only — Not Now)

| Item | Paper (now) | Live (later) |
|------|-------------|--------------|
| Alpaca stock/ETF commissions | $0 | $0 (commission-free) |
| Alpaca account minimum | $0 | $0 |
| SEC/FINRA fees | Simulated | Small per-trade regulatory fees |
| Pattern Day Trader rule | N/A in paper | Applies if account < $25K + day trading |
| Real-time market data | IEX on free paper | Paid data plans optional (~$9–99/mo) |

---

## Total Monthly Cost Summary

| Scenario | Monthly cost |
|----------|-------------|
| **Building + paper trading (v1, gated)** | **$0–25** (Anthropic only; rest free) |
| **Building without signal gating** | **$150–400** (avoid this) |
| **+ VPS hosting** | +$5–12 |
| **+ Massive paid tier** | +$29 |
| **+ Finnhub paid tier** | +$50+ |

---

## Quick Checklist Before You Spend Anything

- [ ] Alpaca paper account created — **$0**
- [ ] FRED API key obtained — **$0**
- [ ] Finnhub API key obtained — **$0**
- [ ] Anthropic Console account created — **$0**
- [ ] Anthropic **Credit Balance checked** — note exact amount
- [ ] Gate 0 test call run — note cost of one call
- [ ] Monthly spend cap set in Anthropic Console (recommended before adding card)

---

## Official Links

- Alpaca: [alpaca.markets](https://alpaca.markets)
- Anthropic pricing: [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Anthropic billing help: [support.anthropic.com/en/articles/8977456](https://support.anthropic.com/en/articles/8977456-how-do-i-pay-for-my-api-usage)
- FRED API keys: [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/useraccount/apikey)
- Finnhub: [finnhub.io/pricing](https://finnhub.io/pricing)

---

*This page is updated when provider pricing or access terms change. Re-verify before Phase 6 (live trading).*


---

<a id="docs-phase_0-md"></a>
## `docs/PHASE_0.md`

# Phase 0 — Foundation (Product Spec v3)

## Goal

Verify API access, project skeleton, and financial model helpers before Phase 1 data pipeline.

## Required keys

| Key | Signup | Required now (Option A) |
|-----|--------|-------------------------|
| `FRED_API_KEY` | [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/useraccount/apikey) | **Yes** |
| `FINNHUB_API_KEY` | [finnhub.io](https://finnhub.io) | **Yes** (quotes) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | **Later** (~$25 credits) |

**Not required:** Alpaca (v3 uses **E*TRADE manual** execution).

Daily history uses **yfinance** (free). Finnhub `/stock/candle` is paid-only on free accounts.

## Commands

```bash
cp .env.example .env
# Edit .env with your keys

pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 scripts/verify_access.py --no-claude
```

## Gate 0 pass criteria

- All tests pass
- `verify_access.py --no-claude` exit code **0** for fred + finnhub (Option A — no Claude yet)
- When Anthropic credits are added: `verify_access.py` (full) exit code **0**
- Massive optional (skip if no key)

## Deliverables (Phase 0)

- [x] `docs/PRODUCT_SPEC_V3.md` — authoritative product spec
- [x] `src/investment_agent/finance.py` — fees, goal %, month-end sweeps
- [x] `scripts/verify_access.py` — v3 required APIs
- [ ] **You:** `.env` filled + Gate 0 run on your machine

## Next: Phase 1

Data ingestion (FRED + Finnhub quotes + yfinance daily bars), liquidity + swing stats, regime gate (SPY/DIA/QQQ), SQLite schema.


---

<a id="docs-phase_7_spec-md"></a>
## `docs/PHASE_7_SPEC.md`

# Phase 7 — Expandable Watchlist + Historical Period Screener

> **Status:** Spec (approved for build)  
> **Goal:** Maximize rule-based discovery and validation **before** Claude intelligence  
> **Depends on:** Phases 0–6, `historical.py` (partial), `stock_team.py`, dashboard  
> **Does not include:** Claude thesis, auto-execution, intraday minute bars

---

## 1. Problem statement

Today the agent can:

- Ingest a **fixed ~10-ticker watchlist**
- Screen **today’s snapshot** for liquidity + ~3% swing
- Push matches to the **Trade Queue**
- Replay **prior day** or a **CLI date range** against stored daily bars

What’s missing for pre-Claude confidence:

| Gap | Impact |
|-----|--------|
| No **expandable universe** (S&P 100, custom list, sector) | User can’t discover names outside hardcoded list |
| No **dashboard period screener** (“last 14 days, show every match”) | Historical is validation-only, not a picker |
| No **ranked output** combining live + historical hit rate | Hard to prioritize before Claude |
| No **persisted screener runs** | Can’t compare Monday vs Friday scans |

**Phase 7** closes these gaps with rule-based tooling only.

---

## 2. Product outcomes

After Phase 7, a user can:

1. **Define or import a watchlist** (50–500+ symbols) without editing code
2. **Pull limited history** (default 60d, max 252d) for that universe
3. **Run live screener** → today’s candidates on dashboard
4. **Run period screener** → “In the last N days, which symbols screened and how often did +1.13% / −0.50% simulate as target/stop?”
5. **Promote** a symbol from period results → Trade Queue with one click
6. **Review** pass/fail stats before paying for Claude

---

## 3. Universe & filter reference (Step 3)

### 3.1 How many stocks?

| Universe | Approx. count | In system today |
|----------|---------------|-----------------|
| **Default watchlist** | **10** tickers | ✅ `DEFAULT_TICKERS` in ingest |
| **US listed (NYSE + NASDAQ)** | **~6,000–7,000** | ❌ not scanned automatically |
| **S&P 500** | **500** | ❌ (Phase 7 preset) |
| **Russell 1000** | **~1,000** | ❌ (Phase 7 optional preset) |
| **Sample liquid large/mid (Jul 2026 test)** | **81 analyzed** | 48 passed Step 3 (62%) |

### 3.2 Step 3 filter rules (unchanged)

| Filter | Rule | Typical eliminator |
|--------|------|------------------|
| **Liquidity** | 20-day avg daily dollar volume ≥ **$2M** | Removes illiquid small caps |
| **Swing proof** | 20-day avg daily range **2.0–4.0%** (target 3% ±1%) | Removes low-vol large caps (BRK, COST) and extreme-vol names outside band |
| **Regime indices** | SPY, DIA, QQQ excluded from **trade** candidates | N/A (used for gate only) |
| **Regime gate** | All three indices down intraday → no **new** queue adds | Macro day filter |

### 3.3 Empirical filter rates (sample, not full market)

Run on **81** mostly large/liquid US names (Jul 2026, 60d yfinance):

| Metric | Result |
|--------|--------|
| Pass liquidity | **100%** (sample was pre-filtered to liquid names) |
| Pass swing (2–4% band) | **~59%** of all tickers |
| Pass **both** Step 3 (tradeable) | **48 / 78** → **62% pass, 38% filtered out** |
| Fail swing only (liquid but too quiet/wild) | e.g. IWM 1.3%, BRK 1.4%, CRM 4.0% |

**Expect on full S&P 500:**

- Liquidity: **~85–95%** pass (most S&P names are liquid)
- Swing band: **~40–55%** pass (many megacaps average 1.5–2.5% daily range)
- **Combined Step 3:** rough estimate **~35–50%** of S&P 500 on a given refresh  
- **Full 6,000+ market:** liquidity removes **~50–70%**; swing removes more → **~15–25%** might pass both

*Exact counts will be computed by Phase 7 `universe_stats` after each ingest.*

---

## 4. Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Watchlist mgr   │────▶│ Ingest / History │────▶│ ohlcv_daily     │
│ (presets+CSV)   │     │ pull (yfinance)  │     │ ticker_metrics  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
         ┌────────────────────────────────────────────────┼────────────────────┐
         ▼                                                ▼                    ▼
┌─────────────────┐                          ┌──────────────────┐   ┌─────────────────┐
│ Live screener   │                          │ Period screener  │   │ Regime gate     │
│ (today)         │                          │ (N days/weeks)   │   │ (unchanged)     │
└────────┬────────┘                          └────────┬─────────┘   └─────────────────┘
         │                                            │
         └────────────────────┬───────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Ranked candidates │
                    │ + promote → queue │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Dashboard UI      │
                    │ (Phase 7 panels)  │
                    └──────────────────┘
```

**Claude slot (Phase 8+):** sits **after** ranked candidates, before final queue promotion — not in Phase 7.

---

## 5. Deliverables

### 5.1 Watchlist manager

**DB**

```sql
-- extend watchlist
ALTER TABLE watchlist ADD COLUMN source TEXT DEFAULT 'manual';  -- manual|preset|csv
ALTER TABLE watchlist ADD COLUMN added_via TEXT;

CREATE TABLE IF NOT EXISTS watchlist_presets (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,        -- 'sp500', 'starter10', 'custom'
  description TEXT,
  ticker_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS screener_runs (
  id INTEGER PRIMARY KEY,
  run_type TEXT NOT NULL,           -- 'live' | 'period'
  started_at TEXT NOT NULL,
  finished_at TEXT,
  params_json TEXT NOT NULL,        -- {lookback_days, start_date, end_date, ...}
  summary_json TEXT,
  status TEXT NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS period_screener_hits (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  ticker TEXT NOT NULL,
  hit_date TEXT NOT NULL,
  predicted_range_pct REAL,
  actual_range_pct REAL,
  simulated_outcome TEXT,           -- target|stop|neither
  would_screen INTEGER NOT NULL,
  FOREIGN KEY (run_id) REFERENCES screener_runs(id)
);
```

**Presets (v1)**

| Preset | Source | ~Count |
|--------|--------|--------|
| `starter10` | Current DEFAULT_TICKERS | 10 |
| `sp100` | Static file `data/universe/sp100.txt` | ~100 |
| `sp500` | Static file or Wikipedia scrape cache | ~500 |

**API**

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/api/watchlist` | GET | No | Active tickers + counts |
| `/api/watchlist/presets` | GET | No | Available presets |
| `/api/watchlist/load-preset` | POST | Key | Load preset into watchlist |
| `/api/watchlist/import` | POST | Key | CSV/text body: one ticker per line |
| `/api/watchlist/{ticker}` | DELETE | Key | Deactivate ticker |

**CLI**

```bash
PYTHONPATH=src python3 scripts/manage_watchlist.py load-preset sp100
PYTHONPATH=src python3 scripts/manage_watchlist.py import --file my_tickers.txt
PYTHONPATH=src python3 scripts/manage_watchlist.py stats
```

---

### 5.2 Bulk historical pull

Extend `pull_historical_data()`:

- Accept full active watchlist (not just DEFAULT_TICKERS)
- **Incremental fetch:** `MAX(date)` per ticker → fetch only missing days
- **Rate limit:** yfinance batch with delay; cap 500 tickers/run default
- **Progress log** in `ingest_log` + dashboard status

**API**

| Route | Method | Description |
|-------|--------|-------------|
| `/api/historical/pull` | POST | `lookback_days`, optional `tickers[]` |
| `/api/historical/pull/status` | GET | Last run progress, bars inserted, errors |

---

### 5.3 Period screener (core)

**Module:** `src/investment_agent/period_screener.py`

```python
def run_period_screener(
    conn,
    *,
    start_date: str,
    end_date: str,
    tradable_cash: float = ORIGINAL_BASIS,
    min_hit_rate: float | None = None,  # optional filter
) -> PeriodScreenerResult:
    """
    For each trading day in [start_date, end_date]:
      - evaluate_trading_day(conn, day)  # reuse historical.py
    Aggregate per ticker:
      - days_screened: int
      - days_target / days_stop / days_neither: int
      - hit_rate_pct: targets / (targets + stops)
      - avg_range_delta_pct
    Rank by: hit_rate desc, days_screened desc, proximity to 3% swing
    """
```

**Outputs**

| Field | Meaning |
|-------|---------|
| `days_screened` | Days symbol passed Step 3 |
| `simulated_targets` | Days high reached +1.13% from open |
| `simulated_stops` | Days low hit −0.50% |
| `hit_rate_pct` | targets / (targets + stops) |
| `last_screened_date` | Most recent pass |
| `live_pass_today` | bool — also passes live screener now |

**Simulation rule (unchanged):** daily bars only; target if `high >= open*1.0113`, else stop if `low <= open*0.995`.

---

### 5.4 Dashboard UI — “Period Screener” panel

New section between **Historical Analysis** and **Learning Report**:

**Controls**

- Date range: Last **7d** | **14d** | **30d** | custom
- Button: **Run period screener**
- Filter toggles: min days screened ≥ 2, min hit rate ≥ 50%

**Results table**

| Ticker | Days screened | Targets | Stops | Hit rate | Avg range | Live? | Action |
|--------|---------------|---------|-------|----------|-----------|-------|--------|
| NVDA | 8 | 5 | 2 | 71% | 3.1% | ✅ | **Add to queue** |

**Actions**

- **Add to queue** → `sync_queue`-style insert as `watching` (respects regime)
- **Export CSV** of results
- Link row → day-by-day drill-down (modal or sub-table)

---

### 5.5 Live + historical combined rank

**Endpoint:** `GET /api/screener/ranked?period_days=14`

Returns merge of:

1. `screen_candidates()` — live today
2. `run_period_screener()` — last N days

**Score (rule-based, no Claude):**

```
score = 0.4 * live_pass
      + 0.3 * (hit_rate_pct / 100)
      + 0.2 * min(days_screened / 10, 1)
      + 0.1 * (1 - abs(avg_range - 3) / 3)
```

Used to sort **Top candidates today** widget on dashboard home.

---

### 5.6 Universe stats (answers “how many filtered?”)

After each ingest/screener run, store and display:

```json
{
  "universe_size": 100,
  "pass_liquidity": 98,
  "pass_swing": 52,
  "pass_both": 48,
  "filtered_out": 52,
  "filter_pct_out": 52.0,
  "regime_blocked": false
}
```

Shown in **Watchlist** panel and period screener header.

---

## 6. User workflow (post Phase 7)

### One-time setup

```bash
# Load a bigger universe
PYTHONPATH=src python3 scripts/manage_watchlist.py load-preset sp100

# Pull 60 days history for all active tickers
PYTHONPATH=src python3 scripts/run_historical.py pull --lookback-days 60
```

### Daily (pre-Claude)

1. `run_ingest.py` — refresh quotes + metrics  
2. Check **regime** banner  
3. **Run period screener** (14d) — see repeat offenders with good hit rate  
4. **Sync live screener** — today’s matches  
5. Compare **ranked** list → pick 1–3 names → queue  
6. Monitor + journal (unchanged)

### When Claude arrives (Phase 8)

Claude receives **only** top 5–10 ranked candidates + period stats + rule-based thesis → richer narrative. Phase 7 data reduces Claude calls and noise.

---

## 7. Build phases (implementation order)

| Step | Deliverable | Est. invasiveness |
|------|-------------|-------------------|
| **7a** | Watchlist presets + import + `manage_watchlist.py` | Low |
| **7b** | Bulk/incremental historical pull for full watchlist | Medium |
| **7c** | `period_screener.py` + persist `screener_runs` / hits | Medium |
| **7d** | Dashboard period screener panel + ranked API | Medium |
| **7e** | Universe stats + drill-down + CSV export | Low |
| **7f** | Tests + `verify_dashboard` + demo seed with sp100 subset | Low |

**Gate (unchanged, post-7):** intraday minute backtest with fees — optional Phase 7.5 or separate Gate.

---

## 8. Non-goals (Phase 7)

- Claude / Anthropic integration  
- Automatic E*TRADE orders  
- Real-time scanning of full 6,000+ market every minute  
- Minute-level intraday backtest  
- News/earnings/spread filters (defer to Phase 8 with Claude or 7.5)  
- Paid Massive/Polygon (optional acceleration, not required)

---

## 9. Acceptance criteria

- [ ] Load **sp100** preset; watchlist shows ~100 active tickers  
- [ ] Pull history completes for sp100 without manual ticker list  
- [ ] Period screener **14d** returns ranked table on dashboard  
- [ ] **Add to queue** from period results respects regime block  
- [ ] Universe stats show pass/filter counts after ingest  
- [ ] `verify_dashboard.py` + pytest cover new endpoints  
- [ ] Works with `--no-claude` / Option A keys only  

---

## 10. API cost (Option A)

| Action | Cost |
|--------|------|
| yfinance daily bars | $0 |
| Finnhub quotes (watchlist batch) | $0 tier; rate limits apply at 500+ tickers |
| FRED VIX | $0 |
| Claude | **$0 in Phase 7** |

**Practical limit:** start with **sp100**; expand to sp500 once pull + screener runtime is acceptable (~2–5 min for 100 tickers on yfinance).

---

## 11. Files to add/change

| Path | Change |
|------|--------|
| `docs/PHASE_7_SPEC.md` | This document |
| `data/universe/sp100.txt`, `sp500.txt` | Preset ticker lists |
| `src/investment_agent/watchlist.py` | New module |
| `src/investment_agent/period_screener.py` | New module |
| `src/investment_agent/historical.py` | Incremental pull |
| `src/investment_agent/db.py` | Schema migrations |
| `scripts/manage_watchlist.py` | CLI |
| `scripts/run_period_screener.py` | CLI |
| `dashboard/app.py` + `dashboard.html` | New panels |
| `tests/test_period_screener.py` | Tests |

---

*v3 · Pre-Claude intelligence · Builds on Phase 6*


---

<a id="docs-product_spec_v3-md"></a>
## `docs/PRODUCT_SPEC_V3.md`

# AI Investment Agent — Product Spec v3 (Authoritative)

> **Status:** Approved for build (July 27, 2026)  
> **Supersedes:** v1/v2 swing-thesis + Alpaca execution assumptions in older sections of `AI_Investment_Agent_Spec.md`  
> **Technical appendix:** `AI_Investment_Agent_Spec.md` (gates, schemas — updated references below)

---

## 1. Product summary

**One product**, one dashboard, one repository: a **CIO managing agent** coordinates **specialist sub-agents** that produce **macro context → qualified stocks → intraday recommendations**. **You** execute all orders in **E*TRADE** and **log fills** on the dashboard. **No automatic broker orders** until you explicitly enable a later phase.

**Default strategy:** Intraday range trading — **+1.13%** target, **−0.50%** stop, **~3% swing proof**, **liquidity-sized** one-batch entries, **no shorts**, **triple-index intraday down → no new longs**, **same-day flat** with **overnight exception** only after EOD analysis + your approval.

---

## 2. Financial model

| Item | Rule |
|------|------|
| Original basis | **$10,000** |
| Phase-one goal | **$5,000,000** account value (tradable balance toward goal) |
| Goal display | `(tradable_balance / 5_000_000) × 100` each month |
| Per buy fee | **$7.00** (configurable) |
| Per sell fee | **$7.00** (configurable) |
| Position size | `min(liquidity_cap, tradable_cash)` — **no 8% cap** |
| Liquidity cap | Section 7 math (ADV$, participation rate, 0.80 buffer, spread/earnings filters) |

### Month-end sweeps (gains only)

- **Monthly realized net** = sum of **closed** logged trades, **net of buy/sell fees**.
- If **monthly realized net ≤ 0:** **no** sweeps.
- If **monthly realized net > 0:**
  - **During the month:** full tradable cash (including amounts that will be swept) **may be used for trading**.
  - **At month-end:** remove from trading account:
    - **10%** of that month’s positive realized net → **management jar**
    - **25%** (editable on dashboard) → **tax planning jar**
  - Jars are **not reinvested** by default.

*Not tax advice. 25% is a planning default.*

---

## 3. Pipeline (order mandatory)

1. **Research agent** — macro, economy, historical context, session/open bias (best-effort).
2. **Regime agent** — SPY + Dow + Nasdaq all down intraday → **no new longs**; no shorts.
3. **Stock team agent** — liquidity + ~3% swing proof → cycle shortlist.
4. **Analysis agent** — data-bound thesis (Claude): what/why/risks.
5. **Monitor agent** — buy zone, +1.13%, −0.50%, EOD flatten / overnight path.
6. **Dashboard** — one queue; **you** + **CIO** review → **E*TRADE** → **journal**.
7. **Learning agent** — daily feedback on **active trades** + **watchlist** (near metrics, not yet live).

---

## 4. CIO and sub-agents (one codebase)

| Agent | Responsibility |
|--------|----------------|
| **CIO** | Orchestrate, summarize dashboard, challenge sub-agents, learn from your actions; more responsibility over time — **not** unsupervised trading in v1 |
| **Research** | Macro / market brief |
| **Regime** | Index intraday rule |
| **Stock team** | Screener, swing proof, shortlist |
| **Analysis** | Claude thesis with citation validation |
| **Monitor** | Alerts and EOD |
| **Learning** | Post-trade and watchlist analytics |

Implementation: shared DB + scheduled jobs + orchestration layer (same repo), not external repos.

---

## 5. Dashboard (v1)

- **$5M goal progress** (% and chart)
- **Tradable cash**, basis, fee totals
- **Month P&L** (net of $7/$7)
- **Month-end sweep preview** (10% + editable tax %)
- **Tax & management jars** (cumulative)
- **Market brief** + regime banner
- **One queue** (states: watching → approved → armed → alert → in trade → EOD → closed → runner)
- **Trade journal** (manual entry — source of truth for cash and learning)
- **CIO summary** panel (Phase 5+)

---

## 6. Trading rules (reference)

| Rule | Value |
|------|--------|
| Target | +1.13% |
| Stop | −0.50% |
| Starting cadence | ~3–4 trades/day, 4 days/week (may increase) |
| Repeat same symbol | Allowed while criteria pass |
| Broker | **E*TRADE manual only** (v1) |
| Alpaca / auto-execute | **Out of scope v1** |

---

## 7. Learning (imperative)

Daily analysis for:

- **Active** positions / completed round-trips
- **Watchlist** names near thresholds

Track: predicted vs actual ~3% range, entry/exit vs recommendation, multi-round same day, EOD hold vs flat, regime days.

---

## 8. Access (Phase 0 required)

| Service | Purpose | Required |
|---------|---------|----------|
| Anthropic | CIO + sub-agents (Claude) | **Yes** |
| FRED | Macro | **Yes** |
| Finnhub | Quotes, news, bars (limits) | **Yes** |
| Massive/Polygon | Historical / backtest | Optional |
| E*TRADE | You execute | **Yes (no API v1)** |
| Alpaca | — | **Not required** |

See `FEES_AT_A_GLANCE.md`.

---

## 9. Build phases

| Phase | Deliverable |
|-------|-------------|
| **0** | Keys, verify_access, finance skeleton, tests |
| **1** | Data pipeline, liquidity + swing stats |
| **1b** | Regime + market brief |
| **2** | Stock team + analysis cards |
| **3** | Dashboard: queue, goal, journal, sweeps, fees |
| **4** | Intraday monitor + alerts |
| **5** | Learning reports + CIO summary |
| **6** | $5M scenario visualizer (journal-fed) |
| **Gate** | Intraday backtest with 1.13/0.50 + fees |

---

## 10. Evolution

| Stage | Execution |
|-------|-----------|
| v1 | Human E*TRADE + journal |
| Later | E*TRADE read sync (optional) |
| Future | Auto-execution only when you approve |

---

## Superseded v2 items

| Old | v3 |
|-----|-----|
| Alpaca paper orders | E*TRADE manual |
| 8% max position | Liquidity + cash only |
| 4–8 week default hold | Same-day intraday default |
| Approve → `/execute` Alpaca | Alerts + manual journal |
| Alpaca required Gate 0 | Anthropic + FRED + Finnhub only |


---

<a id="requirements-txt"></a>
## `requirements.txt`

```text
# Core (Phase 0)
python-dotenv>=1.0.0
httpx>=0.27.0
pydantic>=2.0.0

# Market data (Phase 1 — free daily bars; Finnhub candles are paid-only)
yfinance>=0.2.40

# Dashboard (Phase 3)
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
jinja2>=3.1.0

# AI (Phase 0 verification — optional until Anthropic credits added)
anthropic>=0.49.0

# Testing
pytest>=8.0.0

# Docs / printable one-pagers
fpdf2>=2.8.0
```


---

<a id="scripts-enable auto refresh-command"></a>
## `scripts/Enable Auto Refresh.command`

```bash
#!/bin/bash
# One-time: enable automatic data refresh at 6:30 AM and 4:30 PM (Mac local time).
# Double-click in Finder. No Terminal typing needed after this.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Enable automatic data refresh"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/install_ingest_schedule_mac.sh" ]]; then
  echo "ERROR: install script not found."
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/install_ingest_schedule_mac.sh" 2>/dev/null || true
"$ROOT/scripts/install_ingest_schedule_mac.sh"
STATUS=$?

echo ""
read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-open dashboard-command"></a>
## `scripts/Open Dashboard.command`

```bash
#!/bin/bash
# Double-click this file in Finder (Mac) to start the dashboard and open the browser.
# First time: right-click → Open (macOS may block unknown scripts).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — starting dashboard"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/hard_restart_dashboard_mac.sh" ]]; then
  echo "ERROR: Cannot find scripts/hard_restart_dashboard_mac.sh"
  echo "Make sure Home-Repository is cloned to ~/Home-Repository"
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/hard_restart_dashboard_mac.sh" "$ROOT/scripts/doctor_dashboard_mac.sh" 2>/dev/null || true
"$ROOT/scripts/hard_restart_dashboard_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -ne 0 ]]; then
  echo "Start failed. Running doctor…"
  "$ROOT/scripts/doctor_dashboard_mac.sh" || true
  echo ""
  echo "Copy the output above and send it for help."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-run after-close ingest-command"></a>
## `scripts/Run After-Close Ingest.command`

```bash
#!/bin/bash
# Double-click after market close — refreshes quotes + today's daily bars.
# Use when ranked table / Special Watch look stale same-day.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — After-close ingest"
echo "  Folder: $ROOT"
echo "  Refreshes quotes (2h threshold) and daily bars (12h). ~15–25 min for S&P 500."
echo ""

chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_ingest_mac.sh" --after-close
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "After-close ingest finished. Refresh browser → Screen → Run screener."
else
  echo "Ingest exited with code $STATUS — scroll up for errors."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-run daily ingest-command"></a>
## `scripts/Run Daily Ingest.command`

```bash
#!/bin/bash
# Double-click in Finder (Mac) to run daily incremental ingest.
# First time: right-click → Open (macOS may block unknown scripts).
# Takes ~15–25 minutes for a full S&P 500 watchlist — leave this window open.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Daily ingest (incremental)"
echo "  Folder: $ROOT"
echo "  This may take 15–25 minutes. Do not close this window."
echo ""

if [[ ! -f "$ROOT/scripts/run_ingest_mac.sh" ]]; then
  echo "ERROR: Cannot find scripts/run_ingest_mac.sh"
  echo "Make sure Home-Repository is at ~/Home-Repository"
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_ingest_mac.sh" --incremental
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "Daily ingest finished OK. Refresh the dashboard in your browser (Screen tab)."
else
  echo "Ingest exited with code $STATUS. Scroll up for errors."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-run end of day-command"></a>
## `scripts/Run End of Day.command`

```bash
#!/bin/bash
# Double-click after market close — ingest + screener + daily close report.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — End of day"
echo "  Folder: $ROOT"
echo "  Ingest + screener + close report (~15–30 min for S&P 500)"
echo ""

chmod +x "$ROOT/scripts/run_end_of_day_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_end_of_day_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "End-of-day pipeline finished. Hard-refresh browser (Cmd+Shift+R)."
else
  echo "Pipeline exited with code $STATUS — scroll up for errors."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-run morning prep-command"></a>
## `scripts/Run Morning Prep.command`

```bash
#!/bin/bash
# Double-click before open — screener + trade candidates (Step 2).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Morning prep"
echo "  Folder: $ROOT"
echo ""

chmod +x "$ROOT/scripts/run_morning_prep_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_morning_prep_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "Morning prep done. Before buying: double-click Run Refresh Live.command"
else
  echo "Morning prep exited with code $STATUS."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-run refresh live-command"></a>
## `scripts/Run Refresh Live.command`

```bash
#!/bin/bash
# Double-click right before you place a limit buy or sell in E*TRADE (Step 3).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Refresh live before buy/sell"
echo "  Folder: $ROOT"
echo ""

chmod +x "$ROOT/scripts/run_refresh_live_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_refresh_live_mac.sh"
STATUS=$?

echo ""
read -r -p "Press Enter to close this window…"
exit $STATUS
```


---

<a id="scripts-backfill_metrics_yfinance-py"></a>
## `scripts/backfill_metrics_yfinance.py`

```python
#!/usr/bin/env python3
"""Backfill ticker_metrics from yfinance daily bars (no Finnhub required)."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db, get_active_watchlist, insert_ticker_metrics
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.liquidity import DailyBar, compute_liquidity_metrics
from investment_agent.providers.yfinance_bars import get_daily_bars


def main() -> int:
    init_db()
    conn = connect()
    symbols = get_active_watchlist(conn)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ok, err = 0, 0
    for i, sym in enumerate(symbols, 1):
        try:
            candles = get_daily_bars(sym, lookback_days=60)
            bars = [
                DailyBar(high=r["high"], low=r["low"], close=r["close"], volume=r["volume"])
                for r in sorted(candles, key=lambda x: x["date"])
            ]
            m = compute_liquidity_metrics(bars, tradable_cash=ORIGINAL_BASIS)
            last_close = bars[-1].close if bars else 0.0
            insert_ticker_metrics(
                conn,
                {
                    "ticker": sym,
                    "computed_at": now,
                    "adv_dollar": m.adv_dollar,
                    "avg_range_pct": m.avg_range_pct,
                    "liquidity_cap": m.liquidity_cap,
                    "last_close": last_close,
                    "last_quote": last_close,
                    "meets_liquidity_min": m.meets_liquidity_min,
                    "near_swing_target": m.near_swing_target,
                },
            )
            ok += 1
        except Exception as exc:
            err += 1
            print(f"ERR {sym}: {exc}", file=sys.stderr)
        if i % 25 == 0:
            conn.commit()
            print(f"... {i}/{len(symbols)} ok={ok} err={err}", flush=True)
    conn.commit()
    conn.close()
    print(f"DONE ok={ok} err={err} total={len(symbols)}")
    return 0 if err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
```


---

<a id="scripts-build_sp500_universe-py"></a>
## `scripts/build_sp500_universe.py`

```python
#!/usr/bin/env python3
"""Refresh universe/sp500.txt from the public S&P 500 constituents CSV."""

from __future__ import annotations

import csv
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "universe" / "sp500.txt"
CSV_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"


def fetch_sp500_symbols() -> list[str]:
    with urllib.request.urlopen(CSV_URL, timeout=30) as resp:
        rows = list(csv.DictReader(resp.read().decode().splitlines()))
    symbols: list[str] = []
    seen: set[str] = set()
    for row in rows:
        sym = row["Symbol"].strip().upper().replace(".", "-")
        if sym and sym not in seen:
            seen.add(sym)
            symbols.append(sym)
    for etf in ("SPY", "DIA", "QQQ"):
        if etf not in seen:
            symbols.insert(0, etf)
            seen.add(etf)
    return symbols


def write_sp500_file(path: Path | None = None) -> int:
    target = path or OUT
    symbols = fetch_sp500_symbols()
    lines = [
        "# S&P 500 constituents + regime ETFs (SPY/DIA/QQQ)",
        "# Source: https://github.com/datasets/s-and-p-500-companies",
        *symbols,
    ]
    target.write_text("\n".join(lines) + "\n")
    return len(symbols)


def main() -> None:
    count = write_sp500_file()
    print(f"Wrote {count} tickers to {OUT}")
    sys.exit(0)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-check_ticker-py"></a>
## `scripts/check_ticker.py`

```python
#!/usr/bin/env python3
"""Report why a ticker is or is not an actionable pick today."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import build_dashboard_summary
from investment_agent.db import connect, get_active_watchlist, init_db
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.step3_status import STEP3_STATUS_LABELS, classify_step3_status
from investment_agent.stock_team import screen_candidates
from investment_agent.strategy import REGIME_ONLY_TICKERS
from investment_agent.trading_day import _latest_quote_rows, resolve_actionable_pick
from investment_agent.watchlist import UNIVERSE_DIR, load_tickers_from_file


def _in_preset(ticker: str) -> list[str]:
    presets: list[str] = []
    for path in UNIVERSE_DIR.glob("*.txt"):
        try:
            if ticker in load_tickers_from_file(path):
                presets.append(path.stem)
        except OSError:
            continue
    return presets


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose ticker eligibility for today's pick")
    parser.add_argument("ticker", help="Symbol e.g. AXON")
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()
    sym = args.ticker.upper().strip()

    path = init_db(args.db)
    conn = connect(path)
    try:
        active = set(get_active_watchlist(conn))
        metrics = conn.execute(
            """
            SELECT m.*
            FROM ticker_metrics m
            INNER JOIN (
              SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
            ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
            WHERE m.ticker = ?
            """,
            (sym,),
        ).fetchone()

        step3 = classify_step3_status(
            ticker=sym,
            meets_liquidity=bool(metrics["meets_liquidity_min"]) if metrics else None,
            near_swing=bool(metrics["near_swing_target"]) if metrics else None,
            avg_range_pct=float(metrics["avg_range_pct"]) if metrics and metrics["avg_range_pct"] is not None else None,
            regime_only=sym in REGIME_ONLY_TICKERS,
        )

        live_cards = {c.ticker: c for c in screen_candidates(conn)}
        ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
        rank_row = next((r for r in ranked if r["ticker"] == sym), None)

        summary = build_dashboard_summary(conn)
        net_for_plan = max(summary.daily_target - 0, summary.daily_target)
        quotes = _latest_quote_rows(conn, [sym])
        pick, skipped = resolve_actionable_pick(
            conn,
            quotes=quotes,
            deploy=summary.tradable_cash,
            net_target=net_for_plan,
        )
        skipped_row = next((s for s in skipped if s["ticker"] == sym), None)

        report = {
            "ticker": sym,
            "in_active_watchlist": sym in active,
            "in_universe_files": _in_preset(sym),
            "has_metrics": metrics is not None,
            "step3_status": step3,
            "step3_label": STEP3_STATUS_LABELS.get(step3, step3),
            "live_step3_today": sym in live_cards,
            "in_ranked_list": rank_row is not None,
            "rank_score": rank_row.get("score") if rank_row else None,
            "rank_position": next(
                (i + 1 for i, r in enumerate(ranked) if r["ticker"] == sym),
                None,
            ),
            "live_pass_today_flag": bool(rank_row.get("live_pass_today")) if rank_row else False,
            "is_actionable_top_pick": pick is not None and pick["ticker"] == sym,
            "skipped_as_not_tradable": skipped_row,
            "avg_range_pct": float(metrics["avg_range_pct"]) if metrics and metrics["avg_range_pct"] is not None else None,
            "meets_liquidity_min": bool(metrics["meets_liquidity_min"]) if metrics else None,
            "near_swing_target": bool(metrics["near_swing_target"]) if metrics else None,
        }
        if not report["in_active_watchlist"]:
            report["hint"] = (
                "Not in active watchlist — load a preset that includes this symbol "
                "(AXON is in sp500 only), run ingest, then run period screener."
            )
        elif not report["live_step3_today"]:
            report["hint"] = f"On watchlist but fails Step 3 today: {report['step3_label']}."
        elif skipped_row:
            report["hint"] = skipped_row.get("reason") or "Fails live tradability for today's $ goal."
        elif report["is_actionable_top_pick"]:
            report["hint"] = "This is today's actionable top pick (or would be if ranked first)."
        elif rank_row and not rank_row.get("live_pass_today"):
            report["hint"] = "On ranked list historically but not a live Step 3 passer today."

        print(json.dumps(report, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
```


---

<a id="scripts-compare_backtest_intervals-py"></a>
## `scripts/compare_backtest_intervals.py`

```python
#!/usr/bin/env python3
"""Compare 1m vs 5m backtest on the same short window (Yahoo 1m limit ~7 days)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import backtest_to_dict, run_backtest_from_db


def _summarize(label: str, result) -> dict:
    reasons = {}
    for t in result.trades:
        reasons[t.exit_reason] = reasons.get(t.exit_reason, 0) + 1
    return {
        "label": label,
        "period": f"{result.start_date} → {result.end_date}",
        "starting": result.starting_capital,
        "ending": result.ending_capital,
        "return_pct": result.total_return_pct,
        "trades": result.total_trades,
        "win_rate_pct": result.win_rate_pct,
        "fees": result.total_fees,
        "max_drawdown_pct": result.max_drawdown_pct,
        "exits": reasons,
    }


def main() -> None:
    days = 7
    top = 20
    capital = 10_000.0
    print(f"Comparing 1m vs 5m backtests on top {top} tickers, ~{days} calendar days")
    print("(Yahoo free tier caps 1-minute history at ~7 days.)\n")

    results = {}
    for interval in ("5m", "1m"):
        print(f"Running {interval}…")
        results[interval] = run_backtest_from_db(
            lookback_days=days,
            top_n=top,
            starting_capital=capital,
            bar_interval=interval,
        )

    s5 = _summarize("5-minute bars", results["5m"])
    s1 = _summarize("1-minute bars", results["1m"])

    out = Path("data/backtest_1m_vs_5m_compare.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "window_days": days,
                "five_minute": backtest_to_dict(results["5m"]),
                "one_minute": backtest_to_dict(results["1m"]),
            },
            indent=2,
        )
    )

    print("\n=== SIDE-BY-SIDE (same ~7-day window) ===")
    for key in ("period", "starting", "ending", "return_pct", "trades", "win_rate_pct", "fees", "max_drawdown_pct", "exits"):
        print(f"{key:18}  5m: {s5[key]}")
        print(f"{'':18}  1m: {s1[key]}")
        print()

    delta = s1["return_pct"] - s5["return_pct"]
    print(f"Return difference (1m − 5m): {delta:+.2f} percentage points")
    if abs(delta) < 2:
        print("→ No meaningful difference on this short window; bar size is not the main driver.")
    elif delta > 0:
        print("→ 1m bars improved results on this window (less pessimistic stop ordering).")
    else:
        print("→ 1m bars were worse (more stop-outs on noise).")

    sys.exit(0)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-dashboard_service_status_mac-sh"></a>
## `scripts/dashboard_service_status_mac.sh`

```bash
#!/bin/bash
# Check background dashboard service status (Mac).
# Usage: ./scripts/dashboard_service_status_mac.sh

PLIST_LABEL="com.investment-agent.dashboard"
LOG_DIR="$HOME/Library/Logs/investment-agent"

echo "=== Investment Agent Dashboard ==="
if launchctl print "gui/$(id -u)/$PLIST_LABEL" &>/dev/null; then
  echo "LaunchAgent: installed (running in background)"
else
  echo "LaunchAgent: not installed"
  echo "Install: ./scripts/install_dashboard_service_mac.sh"
fi

HTTP=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/ 2>/dev/null || echo "000")
if [[ "$HTTP" == "200" ]]; then
  echo "Dashboard:   UP at http://127.0.0.1:8080"
else
  echo "Dashboard:   not responding on port 8080"
fi

if [[ -f "$LOG_DIR/dashboard.err.log" ]]; then
  echo ""
  echo "Recent errors (last 5 lines):"
  tail -5 "$LOG_DIR/dashboard.err.log"
fi
```


---

<a id="scripts-doctor_dashboard_mac-sh"></a>
## `scripts/doctor_dashboard_mac.sh`

```bash
#!/bin/bash
# Diagnose why http://127.0.0.1:8080 won't open (Mac).
# Usage: ./scripts/doctor_dashboard_mac.sh

set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
URL="http://127.0.0.1:8080"

echo "=== Dashboard doctor ==="
echo "Repo: $ROOT"
echo ""

fail=0
warn() { echo "WARN: $*"; }
ok() { echo "OK:   $*"; }
bad() { echo "FAIL: $*"; fail=1; }

# 1. Python
if command -v python3 >/dev/null 2>&1; then
  ok "python3 at $(command -v python3) — $(python3 --version 2>&1)"
else
  bad "python3 not found — install Python 3 from python.org or: brew install python"
fi

# 2. Dependencies
for mod in uvicorn fastapi jinja2 dotenv; do
  if python3 -c "import $mod" 2>/dev/null; then
    ok "import $mod"
  else
    bad "missing Python module '$mod' — run: pip3 install -r requirements.txt"
  fi
done

# 3. App import
if PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.dashboard.app import app" 2>/dev/null; then
  ok "dashboard app imports"
else
  bad "dashboard app failed to import:"
  PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.dashboard.app import app" 2>&1 | tail -5
fi

# 4. .env / db
[[ -f "$ROOT/.env" ]] && ok ".env exists" || warn ".env missing (will be created on start)"
[[ -f "$ROOT/data/agent.db" ]] && ok "data/agent.db exists" || warn "data/agent.db missing (will be seeded on start)"

# 5. Port 8080
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    ok "port 8080 in use by PID(s): $PIDS"
    CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 "$URL/api/config" 2>/dev/null || echo "000")
    if [[ "$CODE" == "200" ]]; then
      ok "server responds HTTP 200 at $URL"
    else
      bad "port 8080 busy but server returned HTTP $CODE (not our dashboard?)"
    fi
  else
    bad "nothing listening on port 8080 — dashboard is NOT running"
    echo "      Fix: ./scripts/hard_restart_dashboard_mac.sh"
  fi
else
  warn "lsof not available — cannot check port 8080"
fi

# 6. Recent log
LOG="$ROOT/data/dashboard.log"
if [[ -f "$LOG" ]]; then
  echo ""
  echo "--- Last 15 lines of data/dashboard.log ---"
  tail -15 "$LOG"
else
  warn "no data/dashboard.log yet — server may never have been started"
fi

echo ""
if [[ $fail -eq 0 ]]; then
  echo "All checks passed. Open: $URL"
else
  echo "Fix the FAIL items above, then run:"
  echo "  ./scripts/hard_restart_dashboard_mac.sh"
fi
exit $fail
```


---

<a id="scripts-generate_daily_rhythm_pdf-py"></a>
## `scripts/generate_daily_rhythm_pdf.py`

```python
#!/usr/bin/env python3
"""Generate one-page printable Daily Rhythm PDF for the dashboard Screen tab."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DAILY_RHYTHM_ONE_PAGE.pdf"


class DailyRhythmPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-11)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(110, 110, 110)
        self.cell(
            0,
            6,
            "AI Investment Agent | Growth Plan | E*TRADE manual | http://127.0.0.1:8080",
            align="C",
        )


def _section(pdf: FPDF, w: float, title: str, lines: list[str]) -> None:
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 5, title, ln=True)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(25, 25, 25)
    for line in lines:
        pdf.multi_cell(w, 3.8, line)
    pdf.ln(1)


def build_pdf(path: Path) -> Path:
    pdf = DailyRhythmPDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    pdf.set_margins(12, 10, 12)
    w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 45, 95)
    pdf.cell(w, 8, "AI Investment Agent - Daily Rhythm", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(55, 55, 55)
    pdf.multi_cell(
        w,
        4,
        "One-page reference for Screen tab pills + Trade tab. Times are Eastern (ET). "
        "Pacific = ET minus 3 hours.",
    )
    pdf.ln(1)

    pdf.set_fill_color(235, 242, 252)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 40, 80)
    pdf.multi_cell(
        w,
        4,
        "Morning chain:  Daily ingest  ->  Run screener  ->  Trade tab -> Refresh live",
        fill=True,
    )
    pdf.ln(2)

    _section(
        pdf,
        w,
        "ONE-TIME SETUP (do once, or when changing universe)",
        [
            "[ ] Screen -> S&P 500  (adds ~500 tickers; you already have ~537)",
            "[ ] Full ingest  OR  Terminal:  ./scripts/run_ingest_mac.sh  (15-25 min first time)",
            "[ ] Run screener",
            "    Goal: 'Missing metrics' near 0 on Screen tab stats line",
        ],
    )

    _section(
        pdf,
        w,
        "EVERY TRADING MORNING (before 10:00 AM ET / 7:00 AM PT)",
        [
            "[ ] Daily ingest  (updates overnight data; ~5-15 min)",
            "[ ] Run screener  (rebuilds 14-day rank + Step 3 list; ~1 min)",
            "[ ] Trade tab -> Refresh live  (live prices for Pick #1; ~15 sec)",
            "[ ] Read Pick #1 / Pick #2 and Planned purchase check before any E*TRADE buy",
            "    NO TRADES today is OK if nothing passes Step 3 + $150 tradability",
        ],
    )

    _section(
        pdf,
        w,
        "DURING THE MARKET (10:00 AM - 2:30 PM ET entry window)",
        [
            "[ ] Trade tab -> Refresh live  before you buy and every 30-60 min if watching",
            "[ ] Run monitor  ONLY if you have an open position (Screen tab)",
            "[ ] Do NOT run Full ingest during session (slow, locks database)",
            "[ ] Refresh ranked  = reload table only (no new market data)",
            "[ ] Execute in E*TRADE -> log fill in Account -> Trade journal",
        ],
    )

    _section(
        pdf,
        w,
        "AFTER THE CLOSE (optional, ~4:00-6:00 PM ET)",
        [
            "[ ] Daily ingest  ->  Run screener  (prepare tomorrow's rank)",
            "[ ] Review tab -> Daily close / Learning report",
            "[ ] Confirm all positions flat; journal matches E*TRADE",
        ],
    )

    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 5, "WHAT EACH SCREEN TAB PILL DOES", ln=True)
    pdf.ln(0.5)

    pills = [
        ("SP100 / S&P 500 / DC watch", "Add tickers to pool", "Once (setup)"),
        ("Full ingest", "Download ALL history + metrics", "Once, then weekly"),
        ("Daily ingest", "Update stale quotes + bars", "Every trading morning"),
        ("Run screener", "14-day rank + Step 3 pass list", "After every ingest"),
        ("Refresh ranked", "Reload table from database", "Anytime (display only)"),
    ]
    c0, c1, c2 = w * 0.28, w * 0.48, w * 0.24
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(225, 230, 240)
    pdf.cell(c0, 5, "Button", border=1, fill=True)
    pdf.cell(c1, 5, "Purpose", border=1, fill=True)
    pdf.cell(c2, 5, "How often", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    for row in pills:
        pdf.cell(c0, 5, row[0], border=1)
        pdf.cell(c1, 5, row[1], border=1)
        pdf.cell(c2, 5, row[2], border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4, "Timestamps:", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(
        w,
        3.6,
        "Under each pill on Screen tab: Last: [date/time PT] = when that action last finished. "
        "Terminal ingest counts after git pull. est. = estimated from older data.",
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(w, 4, "Terminal shortcuts (Mac):", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.multi_cell(
        w,
        3.6,
        "Open Dashboard.command  |  ./scripts/run_ingest_mac.sh  |  "
        "./scripts/run_ingest_mac.sh --incremental  (daily)",
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path


def main() -> None:
    out = build_pdf(OUT)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
```


---

<a id="scripts-generate_one_pager_pdf-py"></a>
## `scripts/generate_one_pager_pdf.py`

```python
#!/usr/bin/env python3
"""Generate printable PDF for docs/DASHBOARD_ONE_PAGER.md content."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DASHBOARD_ONE_PAGER.pdf"


class OnePagerPDF(FPDF):
    def header(self) -> None:
        pass

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "AI Investment Agent v3 | E*TRADE manual | Option A (no Claude)", align="C")


def build_pdf(path: Path) -> Path:
    pdf = OnePagerPDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_margins(14, 12, 14)

    w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(w, 10, "AI Investment Agent", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(w, 5, "Daily One-Pager  |  You trade in E*TRADE. This board screens, alerts, and records. No auto-orders.")
    pdf.ln(2)

    pdf.set_fill_color(240, 245, 252)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w, 7, "Strategy: +1.13% target  |  -0.50% stop  |  ~3% swing  |  $7 buy + $7 sell  |  $10K to $5M goal", ln=True, fill=True)
    pdf.ln(3)

    sections = [
        (
            "Before you start (once per session)",
            [
                "[ ] Dashboard open  |  APP_API_KEY pasted -> Save",
                "[ ] Regime banner GREEN (if red = SPY+DIA+QQQ all down -> NO new longs)",
            ],
        ),
        (
            "Morning (pre-market / open)",
            [
                "[ ] Refresh data: run_ingest.py OR Pull history + Sync from screener",
                "[ ] Read Market Brief (VIX + regime)",
                "[ ] Review Trade Queue - advance only names you agree with",
                "    watching -> approved -> armed -> alert -> in_trade -> eod -> closed",
                "[ ] Note Target +1.13%  |  Stop -0.50%  |  Size on each row",
            ],
        ),
        (
            "During market hours",
            [
                "[ ] Run monitor every 15-30 min (or on alert)",
                "[ ] On TARGET_HIT / STOP_HIT / EOD_FLATTEN:",
                "    1. Execute in E*TRADE",
                "    2. Log fill in Trade Journal (BUY or SELL)",
                "    3. Acknowledge alert on board",
                "[ ] Same-day flat default - close before close unless overnight approved",
            ],
        ),
        (
            "End of day",
            [
                "[ ] Final Run monitor",
                "[ ] All open positions closed in E*TRADE (or overnight exception documented)",
                "[ ] Every fill logged in Trade Journal (buy AND sell)",
                "[ ] Generate report (Learning)  |  skim CIO Summary",
                "[ ] Glance Historical Analysis - prior-day screener vs actual",
            ],
        ),
        (
            "End of month (if month P&L > 0)",
            [
                "[ ] Check Month-end Sweep Preview (10% mgmt + tax %)",
                "[ ] Adjust tax rate if needed -> Save rate",
                "[ ] Apply month-end sweep",
            ],
        ),
    ]

    for title, lines in sections:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(20, 40, 80)
        pdf.cell(w, 6, title, ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        for line in lines:
            pdf.multi_cell(w, 4.2, line)
        pdf.ln(1.5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(w, 6, "Quick reference", ln=True)
    pdf.ln(1)

    table = [
        ("Section", "Why"),
        ("Regime banner", "Gate for new longs"),
        ("Goal / Cash / Month P&L", "Account health"),
        ("Trade Queue", "What to watch / trade"),
        ("Intraday Alerts", "Target, stop, EOD"),
        ("Trade Journal", "Source of truth - log every fill"),
        ("Learning + CIO", "Daily feedback + actions"),
    ]
    col1 = w * 0.42
    col2 = w * 0.58
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(col1, 5.5, table[0][0], border=1, fill=True)
    pdf.cell(col2, 5.5, table[0][1], border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for row in table[1:]:
        pdf.cell(col1, 5.5, row[0], border=1)
        pdf.cell(col2, 5.5, row[1], border=1, ln=True)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(w, 4, "Needs API key:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(
        w,
        4,
        "Sync queue  |  Run monitor  |  Pull history  |  Generate report  |  Log trade  |  Apply sweep",
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(w, 4, "CLI:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(w, 4, "run_ingest.py  |  run_monitor.py  |  run_dashboard.py  |  run_learning.py")

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path


def main() -> None:
    out = build_pdf(OUT)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
```


---

<a id="scripts-hard_restart_dashboard_mac-sh"></a>
## `scripts/hard_restart_dashboard_mac.sh`

```bash
#!/bin/bash
# Hard restart dashboard, wait until healthy, open browser (Mac).
# Usage: ./scripts/hard_restart_dashboard_mac.sh

set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
LOG="$ROOT/data/dashboard.log"
PIDFILE="$ROOT/data/dashboard.pid"
URL="http://127.0.0.1:8080"

echo "=== Hard restart AI Investment Agent Dashboard ==="
echo "Repo: $ROOT"
echo ""

mkdir -p "$ROOT/data"

stop_pid() {
  if [[ -f "$PIDFILE" ]]; then
    OLD=$(cat "$PIDFILE" 2>/dev/null || true)
    if [[ -n "$OLD" ]] && kill -0 "$OLD" 2>/dev/null; then
      echo "Stopping prior dashboard PID $OLD"
      kill "$OLD" 2>/dev/null || true
      sleep 1
      kill -9 "$OLD" 2>/dev/null || true
    fi
    rm -f "$PIDFILE"
  fi
}

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    echo "Stopping process on port 8080: $PIDS"
    kill $PIDS 2>/dev/null || true
    sleep 1
    PIDS=$(lsof -ti:8080 2>/dev/null || true)
    [[ -n "$PIDS" ]] && kill -9 $PIDS 2>/dev/null || true
  fi
fi
stop_pid

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example"
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

if ! python3 -c "import uvicorn, fastapi, jinja2" 2>/dev/null; then
  echo "Installing dependencies (this may take a minute)…"
  python3 -m pip install -r "$ROOT/requirements.txt" || pip3 install -r "$ROOT/requirements.txt"
fi

if ! PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.dashboard.app import app" 2>/dev/null; then
  echo ""
  echo "ERROR: Dashboard failed to load. Run ./scripts/doctor_dashboard_mac.sh for details."
  exit 1
fi

if [[ ! -f "$ROOT/data/agent.db" ]]; then
  echo "Initializing database…"
  PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.demo_seed import seed_demo_db; seed_demo_db()"
fi

export PYTHONPATH="$ROOT/src"
: > "$LOG"
echo "[$(date)] Starting run_dashboard.py on 127.0.0.1:8080" >> "$LOG"

# Start server (background)
nohup python3 "$ROOT/scripts/run_dashboard.py" --host 127.0.0.1 --port 8080 >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
PID=$(cat "$PIDFILE")
echo "Starting dashboard (PID $PID)…"

READY=0
for i in $(seq 1 30); do
  if ! kill -0 "$PID" 2>/dev/null; then
    echo ""
    echo "ERROR: Dashboard process exited before becoming ready."
    echo "--- Log ---"
    tail -50 "$LOG" || true
    echo ""
    echo "Run: ./scripts/doctor_dashboard_mac.sh"
    exit 1
  fi
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 "$URL/api/config" 2>/dev/null || echo "000")
  if [[ "$CODE" == "200" ]]; then
    READY=1
    break
  fi
  printf "."
  sleep 1
done
echo ""

if [[ "$READY" != "1" ]]; then
  echo "ERROR: Dashboard not responding after 30s (last HTTP $CODE)."
  echo "--- Log ---"
  tail -50 "$LOG" || true
  echo ""
  echo "Run: ./scripts/doctor_dashboard_mac.sh"
  exit 1
fi

echo "Dashboard UP: $URL"
if command -v open >/dev/null 2>&1; then
  open "$URL"
  echo "Opened in your default browser."
else
  echo "Open this URL manually: $URL"
fi
echo "Log: $LOG"
echo "Stop: kill \$(cat $PIDFILE)"
echo ""
echo "If the browser still says 'can't be reached', wait 2s and refresh (Cmd+R)."
exit 0
```


---

<a id="scripts-install_dashboard_service_mac-sh"></a>
## `scripts/install_dashboard_service_mac.sh`

```bash
#!/bin/bash
# Install macOS LaunchAgent — dashboard runs in background (no Terminal window).
# Usage: ./scripts/install_dashboard_service_mac.sh
# Open: http://127.0.0.1:8080

set -e
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
PYTHON="$(command -v python3)"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"

if [[ -z "$PYTHON" ]]; then
  echo "ERROR: python3 not found. Install Python 3 first."
  exit 1
fi

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env — add FINNHUB_API_KEY before Refresh live data."
fi

if ! "$PYTHON" -c "import uvicorn, yfinance, jinja2" 2>/dev/null; then
  echo "Installing Python dependencies (one time)…"
  pip3 install -r "$ROOT/requirements.txt"
fi

mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

# Stop foreground/background process on 8080 if present
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
fi

# Unload old agent if reloading
launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>${ROOT}/src</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>${ROOT}/scripts/run_dashboard.py</string>
    <string>--port</string>
    <string>8080</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/dashboard.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/dashboard.err.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/$PLIST_LABEL"
launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL"

echo "Waiting for dashboard to start…"
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1
  if curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/ 2>/dev/null | grep -q 200; then
    echo ""
    echo "Dashboard service installed and running."
    echo "  Open: http://127.0.0.1:8080"
    echo "  Logs: ${LOG_DIR}/dashboard.out.log"
    echo ""
    echo "No Terminal window needed. Starts automatically on login."
    echo "Stop:    ./scripts/uninstall_dashboard_service_mac.sh"
    echo "Restart: launchctl kickstart -k gui/$(id -u)/${PLIST_LABEL}"
    exit 0
  fi
done

echo "Service installed but dashboard not responding yet."
echo "Run these commands and paste the output if you need help:"
echo "  cat ${LOG_DIR}/dashboard.err.log"
echo "  cd ${ROOT} && PYTHONPATH=src python3 scripts/run_dashboard.py --port 8080"
exit 1
```


---

<a id="scripts-install_ingest_schedule_mac-sh"></a>
## `scripts/install_ingest_schedule_mac.sh`

```bash
#!/bin/bash
# Install automatic daily ingest (no Terminal typing).
# Runs: 6:30 AM incremental + 4:30 PM after-close refresh (Mac local time).
# Mac must be awake at those times (or ingest runs at next wake).
# Usage: ./scripts/install_ingest_schedule_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
PLIST_LABEL="com.investment-agent.ingest"
PLIST_AFTER="${PLIST_LABEL}.afterclose"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PLIST_AFTER_PATH="$HOME/Library/LaunchAgents/${PLIST_AFTER}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"
SCHEDULE_SCRIPT="$ROOT/scripts/run_ingest_scheduled_mac.sh"

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: .env missing — add FINNHUB_API_KEY and FRED_API_KEY first."
  exit 1
fi

chmod +x "$SCHEDULE_SCRIPT" "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/$PLIST_AFTER" 2>/dev/null || true

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>${ROOT}/src</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${SCHEDULE_SCRIPT}</string>
    <string>morning</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>6</integer>
    <key>Minute</key>
    <integer>30</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/ingest-morning.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/ingest-morning.err.log</string>
</dict>
</plist>
EOF

cat > "$PLIST_AFTER_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_AFTER}</string>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>${ROOT}/src</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${SCHEDULE_SCRIPT}</string>
    <string>afterclose</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>16</integer>
    <key>Minute</key>
    <integer>30</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/ingest-afterclose.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/ingest-afterclose.err.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/$PLIST_LABEL"
launchctl bootstrap "gui/$(id -u)" "$PLIST_AFTER_PATH"
launchctl enable "gui/$(id -u)/$PLIST_AFTER"

echo ""
echo "Automatic ingest installed (Mac local time):"
echo "  6:30 AM  — morning incremental ingest"
echo "  4:30 PM  — after-close ingest + screener + daily close report"
echo ""
echo "Logs: $LOG_DIR/ingest.log"
echo "Manual EOD:  double-click scripts/Run End of Day.command"
echo "Manual AM:   double-click scripts/Run Morning Prep.command"
echo "Before buy:  double-click scripts/Run Refresh Live.command"
echo "Uninstall:   ./scripts/uninstall_ingest_schedule_mac.sh"
echo ""
echo "Note: Mac must be on (or awake) at scheduled times."
```


---

<a id="scripts-manage_watchlist-py"></a>
## `scripts/manage_watchlist.py`

```python
#!/usr/bin/env python3
"""Manage watchlist presets and imports (Phase 7)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.watchlist import (
    PRESETS,
    compute_universe_stats,
    deactivate_ticker,
    get_active_watchlist_details,
    import_tickers,
    list_presets,
    load_preset_into_watchlist,
    load_tickers_from_file,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watchlist manager")
    parser.add_argument("--db", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("presets", help="List available presets")

    load = sub.add_parser("load-preset", help="Load a preset into active watchlist")
    load.add_argument("name", choices=sorted(PRESETS.keys()))
    load.add_argument(
        "--replace",
        action="store_true",
        help="Deactivate all tickers before loading preset",
    )

    imp = sub.add_parser("import", help="Import tickers from file")
    imp.add_argument("--file", type=Path, required=True)

    sub.add_parser("list", help="List active watchlist tickers")
    sub.add_parser("stats", help="Universe Step 3 pass/filter stats")

    rm = sub.add_parser("remove", help="Deactivate a ticker")
    rm.add_argument("ticker")

    args = parser.parse_args()
    path = init_db(args.db)
    conn = connect(path)

    try:
        if args.command == "presets":
            result = [
                {
                    "name": p.name,
                    "description": p.description,
                    "ticker_count": p.ticker_count,
                }
                for p in list_presets()
            ]
        elif args.command == "load-preset":
            result = load_preset_into_watchlist(conn, args.name, replace=args.replace)
            conn.commit()
        elif args.command == "import":
            tickers = load_tickers_from_file(args.file)
            result = import_tickers(conn, tickers, added_via=str(args.file))
            conn.commit()
        elif args.command == "list":
            result = {"tickers": get_active_watchlist_details(conn)}
        elif args.command == "stats":
            result = compute_universe_stats(conn)
        elif args.command == "remove":
            result = deactivate_ticker(conn, args.ticker)
            conn.commit()
        else:
            result = {"ok": False, "error": "unknown command"}
    finally:
        conn.close()

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-repair_dashboard_mac-sh"></a>
## `scripts/repair_dashboard_mac.sh`

```bash
#!/bin/bash
# Repair dashboard database and restart background service (Mac).
# Fixes schema migrations, WAL mode, and stale locks.
# Usage: ./scripts/repair_dashboard_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
DB="$ROOT/data/agent.db"

echo "=== Repair Investment Agent Dashboard ==="

# Stop dashboard to release DB lock
if launchctl print "gui/$(id -u)/$PLIST_LABEL" &>/dev/null; then
  echo "Stopping background dashboard…"
  launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 2
fi
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill -9 $PIDS 2>/dev/null || true
  sleep 1
fi

# Remove stale WAL locks if present
if [[ -f "$DB-wal" || -f "$DB-shm" ]]; then
  echo "Clearing WAL sidecar files…"
  rm -f "$DB-wal" "$DB-shm" 2>/dev/null || true
fi

echo "Applying database schema + migrations…"
export PYTHONPATH="$ROOT/src"
python3 - <<'PY'
from investment_agent.db_maintenance import repair_database
from investment_agent.watchlist import compute_universe_stats
from investment_agent.db import connect, init_db

result = repair_database()
print("repair:", result)
conn = connect(init_db())
stats = compute_universe_stats(conn)
conn.close()
print("stats:", stats)
PY

echo ""
echo "Repair OK. Restarting dashboard…"
if [[ -f "$PLIST_PATH" ]]; then
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
  launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 3
fi

if curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:8080/ | grep -q 200; then
  echo "Dashboard UP: http://127.0.0.1:8080"
  echo ""
  echo "Next: ./scripts/run_ingest_mac.sh   (loads metrics — 15–25 min for S&P 500)"
else
  echo "Dashboard not responding — run: ./scripts/install_dashboard_service_mac.sh"
  exit 1
fi
```


---

<a id="scripts-restart_dashboard_mac-sh"></a>
## `scripts/restart_dashboard_mac.sh`

```bash
#!/bin/bash
# Stop anything on port 8080 and start the dashboard fresh (Mac).
# Usage: ./scripts/restart_dashboard_mac.sh
#
# For background start + auto-open browser, use:
#   ./scripts/hard_restart_dashboard_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"

if [[ "${1:-}" == "--open" ]]; then
  exec "$ROOT/scripts/hard_restart_dashboard_mac.sh"
fi

echo "=== Restart AI Investment Agent Dashboard ==="

# Stop prior dashboard on 8080
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    echo "Stopping old process on port 8080: $PIDS"
    kill $PIDS 2>/dev/null || true
    sleep 1
    PIDS=$(lsof -ti:8080 2>/dev/null || true)
    [[ -n "$PIDS" ]] && kill -9 $PIDS 2>/dev/null || true
  fi
fi

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example"
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Add FINNHUB_API_KEY and FRED_API_KEY to .env before Refresh live data."
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
  echo "Installing dependencies…"
  pip3 install -r "$ROOT/requirements.txt"
fi

echo ""
echo "Starting dashboard at http://127.0.0.1:8080"
echo "UI v2 — look for Trade | Screen | Review tabs and Pick #1 / #2 side by side."
echo "If you still see the old layout: hard-refresh the browser (Cmd+Shift+R)."
echo "Keep this Terminal window open. Press Ctrl+C to stop."
echo ""

export PYTHONPATH="$ROOT/src"
exec python3 "$ROOT/scripts/run_dashboard.py" --port 8080
```


---

<a id="scripts-run_backtest-py"></a>
## `scripts/run_backtest.py`

```python
#!/usr/bin/env python3
"""Run 60-day intraday backtest on top ranked tickers (5-minute bars)."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import backtest_to_dict, run_backtest_from_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Intraday backtest for ranked universe")
    parser.add_argument("--days", type=int, default=60, help="Lookback window (default 60)")
    parser.add_argument("--top", type=int, default=20, help="Top N ranked tickers (default 20)")
    parser.add_argument("--capital", type=float, default=10_000.0, help="Starting capital")
    parser.add_argument("--interval", default="5m", help="Bar interval (default 5m)")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write full JSON report to path",
    )
    parser.add_argument(
        "--dollar-target",
        action="store_true",
        help="Use Growth Plan $ net sell target instead of fixed +1.5%%",
    )
    parser.add_argument(
        "--daily-only",
        action="store_true",
        help="Run daily-bar dollar backtest (no 5m fetch; uses stored OHLCV)",
    )
    args = parser.parse_args()

    if args.daily_only:
        from investment_agent.backtest import run_dollar_daily_backtest
        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        conn.row_factory = sqlite3.Row
        try:
            result = run_dollar_daily_backtest(conn, lookback_days=args.days, starting_capital=args.capital)
        finally:
            conn.close()
        if args.output:
            import json
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2))
        print("=== DAILY DOLLAR BACKTEST ===")
        print(f"Period:     {result['start_date']} → {result['end_date']}")
        print(f"Trades:     {result['total_trades']} (${result['dollar_target_hits']} hit $ goal, {result['dollar_hit_rate_pct']}%)")
        print(f"Net P&L:    ${result['total_net_pnl']:,.2f}")
        print(f"Ending:     ${result['ending_capital']:,.2f}")
        sys.exit(0)

    print(f"Running {args.days}d intraday backtest on top {args.top} ranked tickers…")
    print("(Fetching 5-minute bars — may take 1–2 minutes.)")

    result = run_backtest_from_db(
        db_path=args.db,
        lookback_days=args.days,
        top_n=args.top,
        starting_capital=args.capital,
        bar_interval=args.interval,
        use_dollar_target=args.dollar_target,
    )
    payload = backtest_to_dict(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2))
        print(f"Full report written to {args.output}")

    print()
    print("=== BACKTEST SUMMARY ===")
    print(f"Period:        {result.start_date} → {result.end_date}")
    print(f"Top tickers:   {', '.join(result.top_tickers)}")
    print(f"Starting:      ${result.starting_capital:,.2f}")
    print(f"Ending:        ${result.ending_capital:,.2f}")
    print(f"Net P&L:       ${result.total_net_pnl:,.2f} ({result.total_return_pct:+.2f}%)")
    print(f"Trades:        {result.total_trades} (W {result.wins} / L {result.losses}, {result.win_rate_pct}% win)")
    print(f"Total fees:    ${result.total_fees:,.2f}")
    print(f"Max drawdown:  {result.max_drawdown_pct:.2f}%")
    if result.spy_return_pct is not None:
        print(f"SPY buy-hold:  {result.spy_return_pct:+.2f}%")
    if result.errors:
        print(f"Data errors:   {len(result.errors)} ticker(s) — see JSON report")

    active_days = [d for d in result.days if d.trades]
    print(f"Trading days:  {len(active_days)} with at least one round trip")
    print()
    print("=== SAMPLE TRADES (last 10) ===")
    for t in result.trades[-10:]:
        print(
            f"  {t.date} {t.ticker:5} {t.exit_reason:6} "
            f"${t.entry_price:.2f}→${t.exit_price:.2f} "
            f"net ${t.net_pnl:+.2f} bal ${t.balance_after:,.2f}"
        )

    print()
    print("=== ASSUMPTIONS ===")
    for line in result.assumptions:
        print(f"  • {line}")

    sys.exit(0)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_daily_close-py"></a>
## `scripts/run_daily_close.py`

```python
#!/usr/bin/env python3
"""Generate Daily Close or Weekly Close report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.close_report import (
    generate_daily_close_report,
    generate_weekly_close_report,
    save_close_report,
)
from investment_agent.db import connect, init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily / Weekly Close report")
    parser.add_argument("--daily", action="store_true", help="Daily close (default)")
    parser.add_argument("--weekly", action="store_true", help="Weekly close")
    parser.add_argument("--date", help="Report date (YYYY-MM-DD)")
    parser.add_argument("--fetch-10et", action="store_true", help="Fetch 5m bars for 10:00 ET entries")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    path = init_db(args.db)
    conn = connect(path)
    try:
        if args.weekly:
            report = generate_weekly_close_report(
                conn, args.date, fetch_10_et=args.fetch_10et,
            )
        else:
            report = generate_daily_close_report(
                conn, args.date, fetch_10_et=args.fetch_10et,
            )
        save_close_report(conn, report)
        conn.commit()
    finally:
        conn.close()

    if args.output:
        args.output.write_text(json.dumps(report, indent=2))
        print(f"Wrote {args.output}")

    print(f"=== {report['report_type'].upper()} CLOSE ===")
    print(f"Date: {report.get('report_date')}")
    for h in report.get("highlights", [])[:5]:
        print(f"  • {h}")
    if report["report_type"] == "daily":
        s = report["tabs"]["full_top20"]["summary"]
        print(f"Journal net: ${s.get('journal_realized_net', 0):.2f}")
        print(f"Best on list (open): {s.get('best_hit_ticker_open')} → ${s.get('best_net_at_high_open')}")
        print(f"Ranked #1: {report.get('rank1_ticker')} → ${s.get('rank1_net_at_high_open')}")


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_dashboard-py"></a>
## `scripts/run_dashboard.py`

```python
#!/usr/bin/env python3
"""Start the Phase 3 dashboard (FastAPI + uvicorn)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run investment agent dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--reload", action="store_true", help="Dev auto-reload")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn not installed — run: pip install -r requirements.txt")
        sys.exit(2)

    bind = f"http://{args.host}:{args.port}"
    if args.host in ("127.0.0.1", "localhost"):
        print(f"Dashboard (local only): {bind}")
    else:
        print(f"WARNING: Dashboard listening on {args.host} — reachable on your network. Set APP_API_KEY in .env.")
        print(f"  Open: {bind}")

    uvicorn.run(
        "investment_agent.dashboard.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_end_of_day_mac-sh"></a>
## `scripts/run_end_of_day_mac.sh`

```bash
#!/bin/bash
# End-of-day pipeline — run after market close (~4:30 PM local or later).
# 1) Refresh quotes + daily bars for full watchlist
# 2) Rebuild 14-day ranked screener (pullback $ metrics)
# 3) Save daily close report for Review tab
#
# Usage:
#   ./scripts/run_end_of_day_mac.sh
#   ./scripts/run_end_of_day_mac.sh --skip-report   # ingest + screener only

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
SKIP_REPORT=0
for arg in "$@"; do
  case "$arg" in
    --skip-report) SKIP_REPORT=1 ;;
  esac
done

echo ""
echo "  AI Investment Agent — end of day"
echo "  Folder: $ROOT"
echo "  Steps: after-close ingest → screener → daily close report"
echo ""

chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true

echo "── Step 1/3: After-close ingest (~15–25 min for S&P 500) ──"
"$ROOT/scripts/run_ingest_mac.sh" --after-close

echo ""
echo "── Step 2/3: Ranked screener (14 trading days) ──"
export PYTHONPATH="$ROOT/src"
python3 "$ROOT/scripts/run_period_screener.py" --days 14 --save >/dev/null
python3 - <<'PY'
import json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from investment_agent.db import connect, init_db
from investment_agent.screen_actions import ACTION_PERIOD_SCREENER, record_screen_action

conn = connect(init_db())
try:
    n = conn.execute("SELECT COUNT(*) AS c FROM screener_runs").fetchone()["c"]
    record_screen_action(conn, ACTION_PERIOD_SCREENER, detail=f"EOD pipeline · run #{n}")
    conn.commit()
finally:
    conn.close()
print("Screener saved.")
PY

if [[ "$SKIP_REPORT" -eq 0 ]]; then
  echo ""
  echo "── Step 3/3: Daily close report ──"
  python3 "$ROOT/scripts/run_daily_close.py" --daily
fi

echo ""
echo "── Freshness check ──"
python3 "$ROOT/scripts/manage_watchlist.py" stats | python3 -c "
import json, sys
s = json.load(sys.stdin)
f = s.get('freshness', {})
print('Newest quote:', f.get('quotes_newest_at', '—'))
print('Newest metrics:', f.get('metrics_newest_at', '—'))
print('Step 3 pass:', s.get('pass_both_step3'), 'of', s.get('tradeable_universe'))
"

echo ""
echo "Done. Tomorrow: Trade tab → Prepare today's trades, then Refresh live before buy."
echo "Or run: ./scripts/run_morning_prep_mac.sh"
echo ""
```


---

<a id="scripts-run_historical-py"></a>
## `scripts/run_historical.py`

```python
#!/usr/bin/env python3
"""Pull limited historical OHLCV and evaluate prior day / date range."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.historical import (
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    pull_historical_data,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Historical OHLCV pull + day evaluation")
    sub = parser.add_subparsers(dest="command", required=True)

    pull = sub.add_parser("pull", help="Fetch limited daily bars into SQLite")
    pull.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Explicit tickers (default: all active watchlist symbols)",
    )
    pull.add_argument("--lookback-days", type=int, default=60)
    pull.add_argument("--db", type=Path, default=None)

    prior = sub.add_parser("prior-day", help="Evaluate prior trading day vs historical view")
    prior.add_argument("--db", type=Path, default=None)

    day = sub.add_parser("evaluate-day", help="Evaluate a specific YYYY-MM-DD")
    day.add_argument("date")
    day.add_argument("--db", type=Path, default=None)

    period = sub.add_parser("period", help="Evaluate each day in a date range")
    period.add_argument("--from", dest="start_date", required=True)
    period.add_argument("--to", dest="end_date", required=True)
    period.add_argument("--db", type=Path, default=None)

    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "pull":
        result = pull_historical_data(
            settings,
            tickers=args.tickers,
            db_path=args.db,
            lookback_days=args.lookback_days,
        )
    elif args.command == "prior-day":
        import sqlite3

        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        try:
            result = evaluate_prior_day(conn)
            if result is None:
                print(json.dumps({"ok": False, "error": "No historical bars in database — run pull first"}))
                sys.exit(1)
        finally:
            conn.close()
    elif args.command == "evaluate-day":
        import sqlite3

        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        try:
            result = evaluate_trading_day(conn, args.date)
        finally:
            conn.close()
    else:
        import sqlite3

        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        try:
            result = evaluate_period(conn, args.start_date, args.end_date)
        finally:
            conn.close()

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_ingest-py"></a>
## `scripts/run_ingest.py`

```python
#!/usr/bin/env python3
"""Run Phase 1 data ingestion (FRED + Finnhub quotes + yfinance bars). No Claude."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.ingest import DEFAULT_TICKERS, run_ingest

LAST_RUN_PATH = ROOT / "data" / "ingest_last_run.json"

# After close: refresh quotes if older than 2h; daily bars if older than 12h.
AFTER_CLOSE_QUOTE_STALE_HOURS = 2.0
AFTER_CLOSE_BAR_STALE_HOURS = 12.0


def _write_last_run(summary: dict, *, mode: str) -> None:
    LAST_RUN_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "finished_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "mode": mode,
        **summary,
    }
    LAST_RUN_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 ingest — macro, quotes, metrics")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Symbols to ingest (default: all active watchlist symbols)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="SQLite path (default: data/agent.db)",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=60,
        help="Daily history window (default: 60)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Skip symbols with fresh quotes/bars (default: full refresh)",
    )
    parser.add_argument(
        "--after-close",
        action="store_true",
        help="Incremental with fresh quotes (2h) and daily bars (12h) — use after market close",
    )
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=20.0,
        help="Age threshold for incremental mode (default: 20)",
    )
    args = parser.parse_args()

    settings = Settings.from_env()
    if not settings.fred_api_key or not settings.finnhub_api_key:
        print("ERROR: FRED_API_KEY and FINNHUB_API_KEY required in .env")
        sys.exit(2)

    incremental = args.incremental or args.after_close
    quote_stale = None
    bar_stale = None
    mode = "full"
    if args.after_close:
        mode = "after_close"
        quote_stale = AFTER_CLOSE_QUOTE_STALE_HOURS
        bar_stale = AFTER_CLOSE_BAR_STALE_HOURS
    elif args.incremental:
        mode = "incremental"

    summary = run_ingest(
        settings,
        tickers=args.tickers,
        db_path=args.db,
        lookback_days=args.lookback_days,
        incremental=incremental,
        stale_hours=args.stale_hours,
        quote_stale_hours=quote_stale,
        bar_stale_hours=bar_stale,
    )
    _write_last_run(summary, mode=mode)
    print(json.dumps(summary, indent=2))
    if summary.get("ok"):
        sys.exit(0)
    if summary.get("partial"):
        print(
            f"\nPartial success: {summary.get('bars_refreshed', 0)} bars, "
            f"{summary.get('quotes_refreshed', 0)} quotes refreshed "
            f"({summary.get('error_count', 0)} errors). Re-run to retry failures.",
            file=sys.stderr,
        )
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_ingest_mac-sh"></a>
## `scripts/run_ingest_mac.sh`

```bash
#!/bin/bash
# Run full/incremental ingest on Mac while dashboard service is paused (avoids DB lock).
# Usage: ./scripts/run_ingest_mac.sh
#        ./scripts/run_ingest_mac.sh --incremental

set -e
cd "$(dirname "$0")/.." || {
  echo "ERROR: Could not find Home-Repository folder."
  exit 1
}
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — ingest"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/run_ingest.py" ]]; then
  echo "ERROR: Missing scripts/run_ingest.py — are you in Home-Repository?"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3 or run: xcode-select --install"
  exit 1
fi
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PAUSED=0

cleanup() {
  if [[ "$PAUSED" -eq 1 && -f "$PLIST_PATH" ]]; then
    echo ""
    echo "Restarting dashboard service…"
    launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
    launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
    echo "Dashboard back at http://127.0.0.1:8080"
  fi
}
trap cleanup EXIT

# macOS default FD limit (~256) is too low for 500+ yfinance requests.
ulimit -n 10240 2>/dev/null || ulimit -n 4096 2>/dev/null || true

# Dedicated yfinance cache — avoids corrupt/default cache and "unable to open database file".
export YFINANCE_CACHE_DIR="$ROOT/data/yfinance_cache"
mkdir -p "$YFINANCE_CACHE_DIR"
export YFINANCE_MIN_INTERVAL_SEC="${YFINANCE_MIN_INTERVAL_SEC:-0.2}"

# Clear stale lock from a prior crashed ingest.
rm -f "$ROOT/data/ingest.lock"

if launchctl print "gui/$(id -u)/$PLIST_LABEL" &>/dev/null; then
  echo "Pausing background dashboard (database unlock for ingest)…"
  launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 2
  PAUSED=1
fi

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
  sleep 1
fi

PIDFILE="$ROOT/data/dashboard.pid"
if [[ -f "$PIDFILE" ]]; then
  DPID=$(cat "$PIDFILE" 2>/dev/null || true)
  [[ -n "$DPID" ]] && kill "$DPID" 2>/dev/null || true
  rm -f "$PIDFILE"
fi

echo "Starting ingest…"
export PYTHONPATH="$ROOT/src"
python3 "$ROOT/scripts/run_ingest.py" "$@"

echo ""
echo "Stats:"
python3 "$ROOT/scripts/manage_watchlist.py" stats
```


---

<a id="scripts-run_ingest_scheduled_mac-sh"></a>
## `scripts/run_ingest_scheduled_mac.sh`

```bash
#!/bin/bash
# Non-interactive ingest for LaunchAgent schedule (logs to ~/Library/Logs/investment-agent/).
# Usage: ./scripts/run_ingest_scheduled_mac.sh morning|afterclose

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
MODE="${1:-morning}"
LOG_DIR="$HOME/Library/Logs/investment-agent"
LOG_FILE="$LOG_DIR/ingest.log"

mkdir -p "$LOG_DIR"
exec >>"$LOG_FILE" 2>&1

echo ""
echo "======== $(date '+%Y-%m-%d %H:%M:%S %Z') — scheduled ingest ($MODE) ========"

if [[ ! -x "$ROOT/scripts/run_ingest_mac.sh" ]]; then
  chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
fi

case "$MODE" in
  morning)
    "$ROOT/scripts/run_ingest_mac.sh" --incremental
    ;;
  afterclose)
    "$ROOT/scripts/run_ingest_mac.sh" --after-close
    echo "── scheduled screener after ingest ──"
    export PYTHONPATH="$ROOT/src"
    python3 "$ROOT/scripts/run_period_screener.py" --days 14 --save
    python3 "$ROOT/scripts/run_daily_close.py" --daily
    ;;
  *)
    echo "ERROR: unknown mode $MODE (use morning or afterclose)"
    exit 1
    ;;
esac

echo "======== finished $(date '+%Y-%m-%d %H:%M:%S %Z') ========"
```


---

<a id="scripts-run_learning-py"></a>
## `scripts/run_learning.py`

```python
#!/usr/bin/env python3
"""Generate and save daily learning report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.learning import generate_learning_report, save_learning_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate learning report")
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()

    path = init_db(args.db)
    with connect(path) as conn:
        report = generate_learning_report(conn)
        report_id = save_learning_report(conn, report)
        conn.commit()
    print(json.dumps({"ok": True, "id": report_id, "report": report}, indent=2))


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_monitor-py"></a>
## `scripts/run_monitor.py`

```python
#!/usr/bin/env python3
"""Run one intraday monitor cycle (+1.13% / −0.50% alerts)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import connect, init_db, insert_quote
from investment_agent.monitor import run_monitor_cycle, utc_now_iso
from investment_agent.providers.finnhub import FinnhubClient


def _refresh_quotes(conn, tickers: list[str], api_key: str) -> int:
    fh = FinnhubClient(api_key)
    count = 0
    try:
        for symbol in tickers:
            try:
                q = fh.get_quote(symbol)
                insert_quote(
                    conn,
                    {
                        "ticker": symbol,
                        "captured_at": utc_now_iso(),
                        "price": float(q["c"]),
                        "open": float(q.get("o") or 0) or None,
                        "high": float(q.get("h") or 0) or None,
                        "low": float(q.get("l") or 0) or None,
                        "prev_close": float(q.get("pc") or 0) or None,
                    },
                )
                count += 1
            except Exception as exc:
                print(f"WARN: quote {symbol}: {exc}", file=sys.stderr)
    finally:
        fh.close()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Run intraday monitor cycle")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--refresh-quotes",
        action="store_true",
        help="Fetch live Finnhub quotes for monitored tickers first",
    )
    args = parser.parse_args()

    path = init_db(args.db)
    with connect(path) as conn:
        if args.refresh_quotes:
            settings = Settings.from_env()
            if not settings.finnhub_api_key:
                print("ERROR: FINNHUB_API_KEY required for --refresh-quotes")
                sys.exit(2)
            rows = conn.execute(
                """
                SELECT DISTINCT ticker FROM queue_items
                WHERE state IN ('armed','alert','in_trade','eod')
                """
            ).fetchall()
            tickers = [r[0] for r in rows]
            updated = _refresh_quotes(conn, tickers, settings.finnhub_api_key)
            print(f"Refreshed {updated} quote(s)", file=sys.stderr)

        result = run_monitor_cycle(conn)
        conn.commit()

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_morning_prep_mac-sh"></a>
## `scripts/run_morning_prep_mac.sh`

```bash
#!/bin/bash
# Morning precheck — before you place limit orders (~6:30–9:30 AM local).
# 1) Optional incremental ingest (skip if after-close EOD ran last night)
# 2) Re-run screener + build Trade tab candidates
# Does NOT replace Step 3 — run ./scripts/run_refresh_live_mac.sh right before you buy.
#
# Usage:
#   ./scripts/run_morning_prep_mac.sh
#   ./scripts/run_morning_prep_mac.sh --with-ingest   # force incremental ingest first

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
WITH_INGEST=0
for arg in "$@"; do
  case "$arg" in
    --with-ingest) WITH_INGEST=1 ;;
  esac
done

echo ""
echo "  AI Investment Agent — morning prep"
echo "  Folder: $ROOT"
echo ""

export PYTHONPATH="$ROOT/src"

if [[ "$WITH_INGEST" -eq 1 ]]; then
  echo "── Incremental ingest ──"
  chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
  "$ROOT/scripts/run_ingest_mac.sh" --incremental
  echo ""
fi

echo "── Prepare today's trades (screener + candidates) ──"
python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from investment_agent.db import connect, init_db
from investment_agent.daily_rhythm import build_trading_candidates
from investment_agent.period_screener import date_range_for_period, list_trading_dates, run_period_screener, save_screener_run
from investment_agent.screen_actions import ACTION_PERIOD_SCREENER, record_screen_action
from investment_agent.account import build_dashboard_summary
from investment_agent.trading_day import build_trading_day_status

conn = connect(init_db())
try:
    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or 10000)
    start, end = date_range_for_period(14, conn=conn)
    trading_dates = list_trading_dates(conn, count=14)
    result = run_period_screener(
        conn, start_date=start, end_date=end, tradable_cash=deploy,
        min_days_screened=1, trading_dates=trading_dates, requested_trading_days=14,
    )
    save_screener_run(conn, result)
    record_screen_action(conn, ACTION_PERIOD_SCREENER, detail=f"Morning prep · {len(result.get('candidates', []))} candidates")
    candidates = build_trading_candidates(conn, limit=15, period_days=14)
    status = build_trading_day_status(conn)
    conn.commit()
    print(json.dumps({
        "candidate_count": len(candidates),
        "top_pick": (status.get("top_pick") or {}).get("ticker"),
        "verdict": status.get("verdict"),
        "headline": status.get("headline"),
    }, indent=2))
finally:
    conn.close()
PY

echo ""
echo "Next: open dashboard → Trade tab → Refresh live before buy"
echo "Or:  ./scripts/run_refresh_live_mac.sh"
echo ""
```


---

<a id="scripts-run_period_screener-py"></a>
## `scripts/run_period_screener.py`

```python
#!/usr/bin/env python3
"""Run period screener over date range (Phase 7)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.period_screener import (
    date_range_for_period,
    list_trading_dates,
    run_period_screener,
    save_screener_run,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Period screener — historical Step 3 aggregation")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--days", type=int, default=14, help="Trading sessions lookback (default 14)")
    parser.add_argument("--from", dest="start_date", default=None)
    parser.add_argument("--to", dest="end_date", default=None)
    parser.add_argument("--min-days", type=int, default=1)
    parser.add_argument("--min-hit-rate", type=float, default=None)
    parser.add_argument("--save", action="store_true", help="Persist run to screener_runs")
    args = parser.parse_args()

    path = init_db(args.db)
    conn = connect(path)
    try:
        if args.start_date and args.end_date:
            start, end = args.start_date, args.end_date
            trading_dates = None
            requested_trading_days = None
        else:
            start, end = date_range_for_period(args.days, conn=conn)
            trading_dates = list_trading_dates(conn, count=args.days)
            requested_trading_days = args.days

        result = run_period_screener(
            conn,
            start_date=start,
            end_date=end,
            min_days_screened=args.min_days,
            min_hit_rate_pct=args.min_hit_rate,
            trading_dates=trading_dates,
            requested_trading_days=requested_trading_days,
        )
        if args.save:
            run_id = save_screener_run(conn, result)
            conn.commit()
            result["saved_run_id"] = run_id
    finally:
        conn.close()

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_refresh_live-py"></a>
## `scripts/run_refresh_live.py`

```python
#!/usr/bin/env python3
"""Refresh live Finnhub quotes and print go/no-go for Step 3 (before buy or sell)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import connect, init_db
from investment_agent.trading_day import build_trading_day_status, refresh_live_quotes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 3 — refresh live quotes before placing limit orders in E*TRADE"
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Print full JSON status")
    args = parser.parse_args()

    settings = Settings.from_env()
    if not settings.finnhub_api_key:
        print("ERROR: FINNHUB_API_KEY required in .env")
        sys.exit(2)

    path = init_db(args.db)
    conn = connect(path)
    try:
        refresh = refresh_live_quotes(conn, settings)
        if not refresh.get("ok"):
            print(refresh.get("error") or "Refresh failed")
            sys.exit(1)
        conn.commit()
        status = build_trading_day_status(conn)
    finally:
        conn.close()

    if args.json:
        print(json.dumps({"refresh": refresh, "status": status}, indent=2))
        sys.exit(0)

    updated = refresh.get("updated") or []
    print(f"Live refresh OK — {len(updated)} symbols updated")
    print(f"Verdict: {status.get('verdict')} — {status.get('headline')}")
    if status.get("detail"):
        print(f"Detail: {status['detail']}")

    pick = status.get("top_pick")
    if pick:
        limit_buy = pick.get("limit_buy_price") or pick.get("entry_price")
        limit_sell = pick.get("limit_sell_price") or pick.get("target_price")
        print(
            f"\n#1 {pick['ticker']}: limit buy ${limit_buy:.2f} · "
            f"limit sell ${limit_sell:.2f} · stop ${pick.get('stop_price', 0):.2f}"
        )
        if pick.get("pullback_pct") is not None:
            print(
                f"   Open ${pick.get('session_open', 0):.2f} · "
                f"pullback −{pick['pullback_pct']}% · cancel unfilled by 11:30 ET"
            )
    else:
        print("\nNo tradable #1 pick for today's dollar goal.")
        skipped = status.get("skipped_not_tradable") or []
        if skipped:
            print("Skipped:")
            for row in skipped[:5]:
                print(f"  {row.get('ticker')}: {row.get('reason', row.get('verdict'))}")

    sys.exit(0 if status.get("verdict") in ("GO", "CAUTION", "WAIT") else 1)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-run_refresh_live_mac-sh"></a>
## `scripts/run_refresh_live_mac.sh`

```bash
#!/bin/bash
# Step 3 — refresh live Finnhub quotes right before you buy or sell in E*TRADE.
# Safe to run with dashboard open (read-only refresh; no full ingest).
#
# Usage: ./scripts/run_refresh_live_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — refresh live (Step 3)"
echo "  Folder: $ROOT"
echo ""

export PYTHONPATH="$ROOT/src"
python3 "$ROOT/scripts/run_refresh_live.py"
```


---

<a id="scripts-run_strategy_models-py"></a>
## `scripts/run_strategy_models.py`

```python
#!/usr/bin/env python3
"""Compare original, recommended, and daily-$350 strategy models (60d backtest)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import sqlite3

from investment_agent.backtest_strategy import run_strategy_backtest
from investment_agent.db import connect, init_db
from investment_agent.providers.yfinance_bars import REGIME_INDICES, get_intraday_bars
from investment_agent.strategy_models import (
    DAILY_TARGET_MODEL,
    ORIGINAL_MODEL,
    RECOMMENDED_MODEL,
    daily_profit_target,
)
from investment_agent.period_screener import build_ranked_candidates


def _cache_bars(conn, lookback: int = 60) -> dict:
    ranked = build_ranked_candidates(conn, period_days=lookback)
    top = [
        r["ticker"]
        for r in ranked["ranked"]
        if r["ticker"] not in {"SPY", "DIA", "QQQ"}
    ][:20]
    symbols = sorted(set(top) | set(REGIME_INDICES))
    cache: dict = {}
    print(f"Fetching 5m bars for {len(symbols)} symbols…")
    for sym in symbols:
        cache[sym] = get_intraday_bars(sym, lookback_days=lookback, interval="5m")
    return cache


def _print_result(r) -> None:
    print(f"\n{'=' * 60}")
    print(f"MODEL: {r.model_name}")
    for a in r.assumptions:
        print(f"  • {a}")
    print(f"\n  Starting:     ${r.starting_capital:,.2f}")
    print(f"  Ending:       ${r.ending_capital:,.2f}")
    print(f"  Net return:   {r.total_return_pct:+.2f}%")
    print(f"  Trades:       {r.total_trades} ({r.win_rate_pct}% win)")
    print(f"  Fees:         ${r.total_fees:,.2f}")
    print(f"  Max drawdown: {r.max_drawdown_pct:.2f}%")
    if r.total_swept:
        print(f"  Total swept:  ${r.total_swept:,.2f} (mgmt + tax jars)")
    if r.model_name == DAILY_TARGET_MODEL.name:
        print(f"  Avg daily target: ${r.avg_daily_target:,.0f}")
        print(f"  Days hit target:  {r.days_hit_target} / {len([d for d in r.days if d.qualifiers])}")
    if r.months:
        print("  Months:")
        for m in r.months:
            print(
                f"    {m.month}: net ${m.gross_net:+,.2f} | "
                f"swept ${m.total_sweep:,.2f} | balance ${m.balance_after_sweep:,.2f}"
            )


def main() -> None:
    path = init_db()
    conn = connect(path)
    conn.row_factory = sqlite3.Row

    print("=== DAILY TARGET SCALE (theory) ===")
    for bal in (10_000, 15_000, 20_000, 25_000, 50_000):
        print(f"  ${bal:,.0f} balance → ${daily_profit_target(bal):,.0f}/day target")

    cache = _cache_bars(conn)
    models = [ORIGINAL_MODEL, RECOMMENDED_MODEL, DAILY_TARGET_MODEL]
    results = []
    for model in models:
        print(f"\nRunning {model.name}…")
        results.append(run_strategy_backtest(conn, model, lookback_days=60, intraday_cache=cache))

    conn.close()

    out = Path("data/strategy_model_compare.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            [
                {
                    "model": r.model_name,
                    "ending": r.ending_capital,
                    "return_pct": r.total_return_pct,
                    "trades": r.total_trades,
                    "fees": r.total_fees,
                    "swept": r.total_swept,
                    "days_hit_target": r.days_hit_target,
                }
                for r in results
            ],
            indent=2,
        )
    )

    for r in results:
        _print_result(r)

    print(f"\nComparison saved to {out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-seed_demo_data-py"></a>
## `scripts/seed_demo_data.py`

```python
#!/usr/bin/env python3
"""Seed demo/test data for dashboard verification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.db import DEFAULT_DB_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo data for dashboard testing")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="SQLite path (default: data/agent.db)",
    )
    args = parser.parse_args()

    path = seed_demo_db(args.db)
    summary = expected_demo_summary()
    print(json.dumps({"db_path": str(path), "expected": summary}, indent=2))


if __name__ == "__main__":
    main()
```


---

<a id="scripts-start_dashboard_cloud-sh"></a>
## `scripts/start_dashboard_cloud.sh`

```bash
#!/bin/bash
# Start dashboard for Cursor Cloud / dev VM (port 8080).
set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
mkdir -p "$ROOT/data"

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env" 2>/dev/null || true
fi

if [[ ! -f "$ROOT/data/agent.db" ]]; then
  PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.demo_seed import seed_demo_db; seed_demo_db()" 2>/dev/null || true
fi

pip install -q -r "$ROOT/requirements.txt" 2>/dev/null || true

export PYTHONPATH="$ROOT/src"
echo "Dashboard: http://127.0.0.1:8080 (use Cursor Ports tab if remote)"
exec python3 "$ROOT/scripts/run_dashboard.py" --host 0.0.0.0 --port 8080
```


---

<a id="scripts-start_dashboard_mac-sh"></a>
## `scripts/start_dashboard_mac.sh`

```bash
#!/bin/bash
# Start the AI Investment Agent dashboard on your Mac.
# Usage: ./scripts/start_dashboard_mac.sh
# Then open: http://127.0.0.1:8080

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"

echo "=== AI Investment Agent Dashboard ==="
echo "Project: $ROOT"
echo ""

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example — add your FINNHUB_API_KEY before trading day refresh."
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
  echo "Installing Python dependencies (first time only)…"
  pip3 install -r "$ROOT/requirements.txt"
fi

echo ""
echo "Starting dashboard at http://127.0.0.1:8080"
echo "Keep this window open. Press Ctrl+C to stop."
echo ""

export PYTHONPATH="$ROOT/src"
exec python3 "$ROOT/scripts/run_dashboard.py" --port 8080
```


---

<a id="scripts-sync_queue-py"></a>
## `scripts/sync_queue.py`

```python
#!/usr/bin/env python3
"""Sync trade queue from stock team screener (Phase 2 → queue)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.stock_team import sync_queue_from_screener


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync queue from liquidity screener")
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()

    path = init_db(args.db)
    with connect(path) as conn:
        result = sync_queue_from_screener(conn)
        conn.commit()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
```


---

<a id="scripts-uninstall_dashboard_service_mac-sh"></a>
## `scripts/uninstall_dashboard_service_mac.sh`

```bash
#!/bin/bash
# Remove background dashboard LaunchAgent.
# Usage: ./scripts/uninstall_dashboard_service_mac.sh

set -e
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
rm -f "$PLIST_PATH"

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
fi

echo "Dashboard background service stopped and removed."
```


---

<a id="scripts-uninstall_ingest_schedule_mac-sh"></a>
## `scripts/uninstall_ingest_schedule_mac.sh`

```bash
#!/bin/bash
# Remove scheduled ingest LaunchAgents.
# Usage: ./scripts/uninstall_ingest_schedule_mac.sh

set -e
PLIST_LABEL="com.investment-agent.ingest"
PLIST_AFTER="${PLIST_LABEL}.afterclose"

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/$PLIST_AFTER" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
rm -f "$HOME/Library/LaunchAgents/${PLIST_AFTER}.plist"

echo "Scheduled ingest removed."
```


---

<a id="scripts-verify_access-py"></a>
## `scripts/verify_access.py`

```python
#!/usr/bin/env python3
"""
Gate 0 — verify required external API connections (Product Spec v3).

Required: anthropic, fred, finnhub.
Optional: massive. Alpaca not used (E*TRADE manual execution).

Usage:
    python scripts/verify_access.py              # required + optional massive
    python scripts/verify_access.py --check anthropic
    python scripts/verify_access.py --check fred
    python scripts/verify_access.py --check finnhub
    python scripts/verify_access.py --check massive   # optional

Exit codes:
    0 = all required checks passed
    1 = one or more required checks failed
    2 = configuration error (missing .env keys)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow running from repo root without installing the package
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import httpx

from investment_agent.config import Settings, load_env, missing_required_keys


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    required: bool = True


def check_alpaca(settings: Settings) -> CheckResult:
    """Optional legacy check — skipped unless Alpaca keys are set."""
    if not settings.alpaca_api_key or not settings.alpaca_secret_key:
        return CheckResult(
            "alpaca",
            True,
            "Skipped — optional; v3 uses E*TRADE manual execution",
            required=False,
        )
    return CheckResult(
        "alpaca",
        True,
        "Keys present (optional data-only; not required for Gate 0)",
        required=False,
    )


def check_anthropic(settings: Settings) -> CheckResult:
    """
    Verify Anthropic API with a minimal Haiku call (cheapest model for Gate 0).

    Note: This consumes a small amount of credits. Check your Console billing
    balance before and after. Official docs confirm new users receive a small
    amount of free credits — exact amount varies by account/region.
    """
    if not settings.anthropic_api_key:
        return CheckResult("anthropic", False, "Missing ANTHROPIC_API_KEY")

    try:
        import anthropic
    except ImportError:
        return CheckResult(
            "anthropic",
            False,
            "anthropic SDK not installed — run: pip install -r requirements.txt",
        )

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=16,
            temperature=0,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        )
        text = response.content[0].text if response.content else ""
        usage = response.usage
        input_tokens = usage.input_tokens if usage else 0
        output_tokens = usage.output_tokens if usage else 0

        return CheckResult(
            "anthropic",
            True,
            f"API OK — model=claude-haiku-4-5, "
            f"tokens in={input_tokens} out={output_tokens}, "
            f"reply={text[:20]!r}. "
            f"Check Console billing for remaining credits.",
        )
    except Exception as exc:
        err = str(exc)
        if "credit" in err.lower() or "billing" in err.lower() or "balance" in err.lower():
            return CheckResult(
                "anthropic",
                False,
                f"Billing/credits error: {exc}. "
                f"Add credits at console.anthropic.com → Billing.",
            )
        return CheckResult("anthropic", False, f"Anthropic error: {exc}")


def check_fred(settings: Settings) -> CheckResult:
    """Verify FRED API with VIXCLS (VIX) series."""
    if not settings.fred_api_key:
        return CheckResult("fred", False, "Missing FRED_API_KEY")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "VIXCLS",
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        obs = data.get("observations", [])
        if not obs:
            return CheckResult("fred", False, "No VIXCLS observations returned")
        value = obs[0].get("value")
        date = obs[0].get("date")
        return CheckResult("fred", True, f"VIXCLS latest: {value} on {date}")
    except Exception as exc:
        return CheckResult("fred", False, f"FRED error: {exc}")


def check_finnhub(settings: Settings) -> CheckResult:
    """Verify Finnhub quote endpoint."""
    if not settings.finnhub_api_key:
        return CheckResult("finnhub", False, "Missing FINNHUB_API_KEY")

    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": settings.verify_test_ticker, "token": settings.finnhub_api_key}
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        price = data.get("c")
        if price is None or price <= 0:
            return CheckResult(
                "finnhub",
                False,
                f"Invalid quote for {settings.verify_test_ticker}: {data}",
            )
        return CheckResult(
            "finnhub",
            True,
            f"{settings.verify_test_ticker} current price: ${price:.2f}",
        )
    except Exception as exc:
        return CheckResult("finnhub", False, f"Finnhub error: {exc}")


def check_massive(settings: Settings) -> CheckResult:
    """Optional: verify Massive/Polygon API."""
    if not settings.massive_api_key:
        return CheckResult(
            "massive",
            True,
            "Skipped — MASSIVE_API_KEY not set (optional)",
            required=False,
        )

    # Massive REST endpoint (formerly Polygon)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{settings.verify_test_ticker}/range/"
        f"1/day/{week_ago}/{today}"
    )
    params = {"apiKey": settings.massive_api_key, "limit": 1}
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 429:
                return CheckResult(
                    "massive",
                    True,
                    "Key valid but rate-limited (429) — expected on free tier",
                    required=False,
                )
            resp.raise_for_status()
            data = resp.json()
        results = data.get("results", [])
        if not results:
            return CheckResult(
                "massive",
                False,
                f"No aggregate data for {settings.verify_test_ticker}",
                required=False,
            )
        return CheckResult(
            "massive",
            True,
            f"Historical agg OK for {settings.verify_test_ticker}",
            required=False,
        )
    except Exception as exc:
        return CheckResult("massive", False, f"Massive error: {exc}", required=False)


CHECKS = {
    "alpaca": check_alpaca,
    "anthropic": check_anthropic,
    "fred": check_fred,
    "finnhub": check_finnhub,
    "massive": check_massive,
}

REQUIRED_CHECKS = ["anthropic", "fred", "finnhub"]
REQUIRED_CHECKS_NO_CLAUDE = ["fred", "finnhub"]
DEFAULT_CHECKS = REQUIRED_CHECKS + ["massive"]


def run_checks(
    selected: list[str] | None = None,
    *,
    require_anthropic: bool = True,
) -> list[CheckResult]:
    load_env()
    settings = Settings.from_env()
    missing = missing_required_keys(settings, require_anthropic=require_anthropic)
    required = REQUIRED_CHECKS if require_anthropic else REQUIRED_CHECKS_NO_CLAUDE
    if missing and (selected is None or any(c in required for c in (selected or []))):
        print("ERROR: Missing required environment variables:")
        for name in missing:
            print(f"  - {name}")
        print("\nCopy .env.example to .env and fill in your keys.")
        print("See docs/FEES_AT_A_GLANCE.md for signup links and costs.")
        sys.exit(2)

    names = selected or (DEFAULT_CHECKS if require_anthropic else REQUIRED_CHECKS_NO_CLAUDE + ["massive"])
    results = []
    for name in names:
        if name == "anthropic" and not require_anthropic:
            results.append(
                CheckResult(
                    "anthropic",
                    True,
                    "Skipped — building without Claude (Option A); add credits later",
                    required=False,
                )
            )
            continue
        fn = CHECKS.get(name)
        if fn is None:
            print(f"Unknown check: {name}")
            sys.exit(2)
        results.append(fn(settings))
    return results


def print_results(results: list[CheckResult]) -> int:
    print("\nGate 0 — API Access Verification")
    print("=" * 50)
    required_failed = False
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        tag = "required" if result.required else "optional"
        print(f"[{status}] {result.name} ({tag})")
        print(f"       {result.message}")
        if not result.passed and result.required:
            required_failed = True

    print("=" * 50)
    if required_failed:
        print("RESULT: Gate 0 FAILED — resolve errors before building.")
        return 1
    print("RESULT: Gate 0 PASSED — all required connections verified.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify external API access (Gate 0)")
    parser.add_argument(
        "--check",
        choices=list(CHECKS.keys()),
        action="append",
        help="Run a specific check (can repeat). Default: all checks.",
    )
    parser.add_argument(
        "--no-claude",
        action="store_true",
        help="Option A: skip Anthropic as required (FRED + Finnhub only)",
    )
    args = parser.parse_args()
    results = run_checks(args.check, require_anthropic=not args.no_claude)
    sys.exit(print_results(results))


if __name__ == "__main__":
    main()
```


---

<a id="scripts-verify_dashboard-py"></a>
## `scripts/verify_dashboard.py`

```python
#!/usr/bin/env python3
"""Verify all dashboard API endpoints against seeded demo data."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from unittest.mock import patch

from investment_agent.dashboard.app import app, _require_api_key
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.db import DEFAULT_DB_PATH


def _checks() -> list[tuple[str, callable]]:
    return []


def verify(db_path: Path) -> dict:
    results: list[dict] = []
    passed = 0
    failed = 0
    expected = expected_demo_summary()

    def record(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed, failed
        results.append({"check": name, "ok": ok, "detail": detail})
        if ok:
            passed += 1
        else:
            failed += 1

    def fake_connect():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    with patch("investment_agent.dashboard.app.connect", fake_connect):
        with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
            app.dependency_overrides[_require_api_key] = lambda: None
            client = TestClient(app)

            # Homepage
            r = client.get("/")
            record("GET /", r.status_code == 200 and "AI Investment Agent" in r.text, f"status={r.status_code}")

            # Summary
            r = client.get("/api/summary")
            data = r.json()
            record("GET /api/summary", r.status_code == 200, "")
            record(
                "summary.tradable_cash",
                abs(data.get("tradable_cash", 0) - expected["tradable_cash"]) < 0.02,
                f"got {data.get('tradable_cash')} want {expected['tradable_cash']}",
            )
            record(
                "summary.monthly_realized_net",
                abs(data.get("monthly_realized_net", 0) - expected["monthly_realized_net"]) < 0.02,
                f"got {data.get('monthly_realized_net')} want {expected['monthly_realized_net']}",
            )
            record("summary.vix", data.get("vix") == expected["vix"], str(data.get("vix")))
            record(
                "summary.regime",
                data.get("regime") and not data.get("block_new_longs"),
                str(data.get("regime", {}).get("summary", "")[:60]),
            )
            record("summary.market_brief", bool(data.get("market_brief")), "")
            record("summary.sweep_preview", "sweep_preview" in data, "")

            # Queue
            r = client.get("/api/queue")
            queue = r.json()
            record("GET /api/queue", r.status_code == 200, f"count={len(queue)}")
            record(
                "queue.count",
                len(queue) == expected["queue_count"],
                f"got {len(queue)} want {expected['queue_count']}",
            )
            nvda = next((q for q in queue if q["ticker"] == "NVDA"), None)
            record(
                "queue.nvda_monitor",
                nvda is not None
                and nvda.get("current_price") is not None
                and nvda.get("pnl_pct") is not None,
                str(nvda),
            )

            # Candidates
            r = client.get("/api/candidates")
            record("GET /api/candidates", r.status_code == 200, f"count={len(r.json())}")

            # Journal
            r = client.get("/api/journal")
            journal = r.json()
            record("GET /api/journal", r.status_code == 200, f"count={len(journal)}")
            record(
                "journal.count",
                len(journal) == expected["journal_count"],
                f"got {len(journal)} want {expected['journal_count']}",
            )

            # Monitor run
            r = client.post("/api/monitor/run")
            mon = r.json()
            record("POST /api/monitor/run", r.status_code == 200 and mon.get("ok"), str(mon.get("new_alerts")))
            record(
                "monitor.target_alert",
                mon.get("new_alerts", 0) >= 1,
                f"evaluations={len(mon.get('evaluations', []))}",
            )

            # Alerts
            r = client.get("/api/alerts")
            alerts = r.json()
            record("GET /api/alerts", r.status_code == 200, f"count={len(alerts)}")
            record(
                "alerts.non_empty",
                len(alerts) >= 1,
                f"types={[a.get('alert_type') for a in alerts]}",
            )

            target = next((a for a in alerts if a.get("alert_type") == "TARGET_HIT"), None)
            record("alerts.target_hit", target is not None, str(target.get("ticker") if target else ""))

            if target:
                r = client.post(f"/api/alerts/{target['id']}/acknowledge")
                record("POST /api/alerts/acknowledge", r.status_code == 200 and r.json().get("ok"), "")

            # Queue sync (should not fail; may add 0 if all active)
            r = client.post("/api/queue/sync")
            record("POST /api/queue/sync", r.status_code == 200, str(r.json()))

            # Tax rate
            r = client.put("/api/settings/tax-rate", json={"tax_rate": 0.30})
            record("PUT /api/settings/tax-rate", r.status_code == 200 and r.json().get("tax_rate") == 0.30, "")

            # Trade log
            r = client.post(
                "/api/journal",
                json={
                    "ticker": "AMD",
                    "side": "BUY",
                    "shares": 1,
                    "price": 160.0,
                    "notes": "verify_dashboard test",
                },
            )
            record("POST /api/journal", r.status_code == 200 and r.json().get("ok"), "")

            # Phase 5 — CIO + Learning
            r = client.get("/api/cio/summary")
            cio = r.json()
            record("GET /api/cio/summary", r.status_code == 200 and bool(cio.get("headline")), "")
            record("cio.action_items", len(cio.get("action_items", [])) >= 1, "")
            record("cio.sub_agents", len(cio.get("sub_agents", {})) >= 4, "")

            r = client.get("/api/learning/report")
            learning = r.json()
            record("GET /api/learning/report", r.status_code == 200, "")
            record("learning.active_positions", len(learning.get("active_positions", [])) >= 1, "")
            record("learning.round_trips", len(learning.get("round_trips", [])) >= 1, "")
            record("learning.continual", "continual_learning" in learning, "")
            record("learning.prior_day", learning.get("prior_day_evaluation") is not None, "")

            r = client.get("/api/historical/summary")
            hist = r.json()
            record("GET /api/historical/summary", r.status_code == 200 and hist.get("has_data"), "")

            r = client.get("/api/historical/evaluate")
            prior = r.json()
            record("GET /api/historical/evaluate", r.status_code == 200 and prior.get("eval_date"), "")

            r = client.get("/api/learning/history")
            record("GET /api/learning/history", r.status_code == 200 and "dates" in r.json(), "")

            r = client.post("/api/learning/generate")
            gen = r.json()
            record("POST /api/learning/generate", r.status_code == 200 and gen.get("ok"), "")

            # Phase 6 — Scenario visualizer
            r = client.get("/api/scenario/visualizer")
            scenario = r.json()
            record("GET /api/scenario/visualizer", r.status_code == 200, "")
            record(
                "scenario.timeline",
                len(scenario.get("actual_timeline", [])) >= 3,
                f"points={len(scenario.get('actual_timeline', []))}",
            )
            record(
                "scenario.journal_pace",
                scenario.get("scenarios", {}).get("journal_pace", {}).get("months_to_goal") is not None,
                str(scenario.get("scenarios", {}).get("journal_pace", {})),
            )
            record("scenario.summary", bool(scenario.get("summary")), "")

            # Static assets
            r = client.get("/static/style.css")
            record("GET /static/style.css", r.status_code == 200, "")

            # Phase 7 — watchlist + period screener
            r = client.get("/api/screener/ranked")
            ranked = r.json()
            record("GET /api/screener/ranked", r.status_code == 200 and "ranked" in ranked, "")

            r = client.get("/api/watchlist/stats")
            record("GET /api/watchlist/stats", r.status_code == 200, "")

            r = client.get("/api/watchlist/presets")
            record("GET /api/watchlist/presets", r.status_code == 200 and len(r.json()) >= 2, "")

            app.dependency_overrides.pop(_require_api_key, None)

    return {
        "ok": failed == 0,
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify dashboard with demo data")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--seed", action="store_true", help="Re-seed demo data first")
    args = parser.parse_args()

    if args.seed:
        seed_demo_db(args.db)
        print(f"Seeded demo data → {args.db}")

    report = verify(args.db)
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
```


---

<a id="src-investment_agent-__init__-py"></a>
## `src/investment_agent/__init__.py`

```python
"""AI Investment Agent — Phase 0 foundation."""

__version__ = "0.1.0"
```


---

<a id="src-investment_agent-account-py"></a>
## `src/investment_agent/account.py`

```python
"""Account balance, jars, and dashboard summary (Product Spec v3)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.finance import (
    DAILY_TARGET_BASE,
    DAILY_TARGET_EVERY,
    DAILY_TARGET_MILESTONE_AT,
    DAILY_TARGET_MILESTONE_GOAL,
    DAILY_TARGET_STEP,
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    DEFAULT_TAX_RESERVE_RATE,
    GOAL_ACCOUNT_VALUE,
    ORIGINAL_BASIS,
    compute_month_end_sweep,
    daily_profit_target,
    goal_progress_pct,
    growth_plan_milestones,
    next_growth_tier,
    round_trip_fees,
)
from investment_agent.journal import (
    compute_monthly_realized_net,
    compute_today_realized_net,
    compute_total_fees,
    journal_cash_balance,
)
from investment_agent.strategy import (
    ENTRY_DELAY_MINUTES,
    ENTRY_WINDOW_ET,
    MAX_TRADES_PER_DAY,
    STOP_DAY_AFTER_STOP,
    STOP_PCT,
)

TRADING_MODE_KEY = "trading_mode"
TRADING_MODE_PAPER = "paper"
TRADING_MODE_LIVE = "live"
VALID_TRADING_MODES = frozenset({TRADING_MODE_PAPER, TRADING_MODE_LIVE})


@dataclass(frozen=True)
class DashboardSummary:
    tradable_cash: float
    original_basis: float
    goal_pct: float
    goal_target: float
    month_key: str
    monthly_realized_net: float
    total_fees_paid: float
    sweep_preview: dict
    management_jar: float
    tax_jar: float
    tax_rate: float
    sweep_already_applied: bool
    vix: float | None
    regime: dict | None
    market_brief: str
    block_new_longs: bool
    daily_target: float
    today_realized_net: float
    today_target_progress_pct: float
    growth_tier: dict
    growth_plan: list[dict]
    strategy_rules: dict
    trading_mode: str


def _month_key(dt: datetime | None = None) -> str:
    when = dt or datetime.now(timezone.utc)
    return when.strftime("%Y-%m")


def get_setting(conn: sqlite3.Connection, key: str, default: str) -> str:
    row = conn.execute(
        "SELECT value FROM app_settings WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO app_settings (key, value, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(key) DO UPDATE SET
          value = excluded.value,
          updated_at = excluded.updated_at
        """,
        (key, value),
    )


def get_tax_rate(conn: sqlite3.Connection) -> float:
    raw = get_setting(conn, "tax_reserve_rate", str(DEFAULT_TAX_RESERVE_RATE))
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_TAX_RESERVE_RATE


def get_trading_mode(conn: sqlite3.Connection) -> str:
    raw = get_setting(conn, TRADING_MODE_KEY, TRADING_MODE_PAPER).lower().strip()
    return raw if raw in VALID_TRADING_MODES else TRADING_MODE_PAPER


def set_trading_mode(conn: sqlite3.Connection, mode: str) -> str:
    normalized = mode.lower().strip()
    if normalized not in VALID_TRADING_MODES:
        raise ValueError(f"trading_mode must be one of: {', '.join(sorted(VALID_TRADING_MODES))}")
    set_setting(conn, TRADING_MODE_KEY, normalized)
    return normalized


def format_journal_notes(notes: str | None, mode: str) -> str | None:
    """Prefix journal notes with [PAPER] or [LIVE] unless already tagged."""
    prefix = "[PAPER]" if mode == TRADING_MODE_PAPER else "[LIVE]"
    if notes is None or not notes.strip():
        return prefix
    upper = notes.strip().upper()
    if upper.startswith("[PAPER]") or upper.startswith("[LIVE]"):
        return notes.strip()
    return f"{prefix} {notes.strip()}"


def get_jar_balance(conn: sqlite3.Connection, jar_type: str) -> float:
    row = conn.execute(
        "SELECT balance FROM jar_balances WHERE jar_type = ?", (jar_type,)
    ).fetchone()
    return float(row["balance"]) if row else 0.0


def cumulative_sweeps(conn: sqlite3.Connection) -> float:
    row = conn.execute(
        "SELECT COALESCE(SUM(management_amount + tax_amount), 0) AS total FROM sweep_history"
    ).fetchone()
    return float(row["total"]) if row else 0.0


def sweep_applied_for_month(conn: sqlite3.Connection, month_key: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sweep_history WHERE month_key = ?", (month_key,)
    ).fetchone()
    return row is not None


def apply_month_end_sweep(conn: sqlite3.Connection, month_key: str | None = None) -> dict:
    """Record month-end sweep into jars (idempotent per month)."""
    mk = month_key or _month_key()
    if sweep_applied_for_month(conn, mk):
        return {"ok": False, "error": f"Sweep already applied for {mk}"}

    tax_rate = get_tax_rate(conn)
    realized = compute_monthly_realized_net(conn, mk)
    sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
    if not sweep.applies:
        return {
            "ok": False,
            "error": f"No positive realized net for {mk} (${realized:.2f})",
        }

    conn.execute(
        """
        INSERT INTO sweep_history
          (month_key, realized_net, management_amount, tax_amount, tax_rate)
        VALUES (?, ?, ?, ?, ?)
        """,
        (mk, realized, sweep.management_sweep, sweep.tax_sweep, tax_rate),
    )
    for jar_type, amount in (
        ("management", sweep.management_sweep),
        ("tax", sweep.tax_sweep),
    ):
        conn.execute(
            """
            INSERT INTO jar_balances (jar_type, balance, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(jar_type) DO UPDATE SET
              balance = balance + excluded.balance,
              updated_at = datetime('now')
            """,
            (jar_type, amount),
        )
    return {
        "ok": True,
        "month_key": mk,
        "realized_net": realized,
        "management_sweep": sweep.management_sweep,
        "tax_sweep": sweep.tax_sweep,
        "total_sweep": sweep.total_sweep,
    }


def latest_vix(conn: sqlite3.Connection) -> float | None:
    row = conn.execute(
        """
        SELECT value FROM macro_snapshots
        WHERE series_id = 'VIXCLS'
        ORDER BY observation_date DESC
        LIMIT 1
        """
    ).fetchone()
    return float(row["value"]) if row else None


def latest_regime(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        """
        SELECT captured_at, spy_change_pct, dia_change_pct, qqq_change_pct,
               block_new_longs, summary
        FROM regime_snapshots
        ORDER BY captured_at DESC
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return None
    return {
        "captured_at": row["captured_at"],
        "spy_change_pct": row["spy_change_pct"],
        "dia_change_pct": row["dia_change_pct"],
        "qqq_change_pct": row["qqq_change_pct"],
        "block_new_longs": bool(row["block_new_longs"]),
        "summary": row["summary"],
    }


def build_market_brief(vix: float | None, regime: dict | None) -> str:
    parts: list[str] = []
    if vix is not None:
        tone = "elevated" if vix >= 20 else "moderate" if vix >= 15 else "calm"
        parts.append(f"VIX {vix:.2f} ({tone}).")
    if regime:
        parts.append(regime["summary"])
    else:
        parts.append("Run ingest to refresh regime data.")
    parts.append(
        "Rule-based brief (no Claude). Add Anthropic credits later for CIO narratives."
    )
    return " ".join(parts)


def build_dashboard_summary(conn: sqlite3.Connection) -> DashboardSummary:
    mk = _month_key()
    tax_rate = get_tax_rate(conn)
    journal_cash = journal_cash_balance(conn)
    sweeps = cumulative_sweeps(conn)
    tradable = journal_cash - sweeps
    realized = compute_monthly_realized_net(conn, mk)
    sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
    vix = latest_vix(conn)
    regime = latest_regime(conn)
    daily_target = daily_profit_target(tradable)
    today_net = compute_today_realized_net(conn)
    today_progress = (today_net / daily_target * 100.0) if daily_target > 0 else 0.0

    return DashboardSummary(
        tradable_cash=tradable,
        original_basis=ORIGINAL_BASIS,
        goal_pct=goal_progress_pct(tradable),
        goal_target=GOAL_ACCOUNT_VALUE,
        month_key=mk,
        monthly_realized_net=realized,
        total_fees_paid=compute_total_fees(conn),
        sweep_preview={
            "applies": sweep.applies,
            "management_sweep": sweep.management_sweep,
            "tax_sweep": sweep.tax_sweep,
            "total_sweep": sweep.total_sweep,
            "monthly_realized_net": realized,
        },
        management_jar=get_jar_balance(conn, "management"),
        tax_jar=get_jar_balance(conn, "tax"),
        tax_rate=tax_rate,
        sweep_already_applied=sweep_applied_for_month(conn, mk),
        vix=vix,
        regime=regime,
        market_brief=build_market_brief(vix, regime),
        block_new_longs=bool(regime and regime.get("block_new_longs")),
        daily_target=daily_target,
        today_realized_net=today_net,
        today_target_progress_pct=today_progress,
        growth_tier=next_growth_tier(tradable),
        growth_plan=growth_plan_milestones(),
        strategy_rules={
            "daily_net_target": daily_target,
            "stop_pct": STOP_PCT,
            "max_trades_per_day": MAX_TRADES_PER_DAY,
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "entry_window_et": ENTRY_WINDOW_ET,
            "stop_day_after_stop": STOP_DAY_AFTER_STOP,
            "daily_target_base": DAILY_TARGET_BASE,
            "daily_target_step": DAILY_TARGET_STEP,
            "daily_target_every": DAILY_TARGET_EVERY,
            "milestone_daily_goal": DAILY_TARGET_MILESTONE_GOAL,
            "milestone_at_balance": DAILY_TARGET_MILESTONE_AT,
        },
        trading_mode=get_trading_mode(conn),
    )


def summary_to_dict(summary: DashboardSummary) -> dict:
    return {
        "tradable_cash": summary.tradable_cash,
        "original_basis": summary.original_basis,
        "goal_pct": summary.goal_pct,
        "goal_target": summary.goal_target,
        "month_key": summary.month_key,
        "monthly_realized_net": summary.monthly_realized_net,
        "total_fees_paid": summary.total_fees_paid,
        "round_trip_fee": round_trip_fees(DEFAULT_BUY_FEE, DEFAULT_SELL_FEE),
        "sweep_preview": summary.sweep_preview,
        "management_jar": summary.management_jar,
        "tax_jar": summary.tax_jar,
        "tax_rate": summary.tax_rate,
        "sweep_already_applied": summary.sweep_already_applied,
        "vix": summary.vix,
        "regime": summary.regime,
        "market_brief": summary.market_brief,
        "block_new_longs": summary.block_new_longs,
        "daily_target": summary.daily_target,
        "today_realized_net": summary.today_realized_net,
        "today_target_progress_pct": summary.today_target_progress_pct,
        "growth_tier": summary.growth_tier,
        "growth_plan": summary.growth_plan,
        "strategy": summary.strategy_rules,
        "trading_mode": summary.trading_mode,
    }
```


---

<a id="src-investment_agent-backtest-py"></a>
## `src/investment_agent/backtest.py`

```python
"""Intraday backtest — 5-minute bar replay for ranked universe (Gate 1.5)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Literal

from investment_agent.db import connect, get_ohlcv_bars, init_db
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    ORIGINAL_BASIS,
    daily_profit_target,
    sell_price_for_net_target,
)
from investment_agent.historical import evaluate_trading_day
from investment_agent.period_screener import build_ranked_candidates, date_range_for_period
from investment_agent.providers.yfinance_bars import REGIME_INDICES, get_intraday_bars
from investment_agent.strategy import REGIME_ONLY_TICKERS, STOP_PCT, TARGET_PCT

ExitReason = Literal["target", "stop", "eod"]


@dataclass
class BacktestTrade:
    date: str
    ticker: str
    rank_score: float
    entry_ts: str
    exit_ts: str
    entry_price: float
    exit_price: float
    shares: float
    gross_pnl: float
    fees: float
    net_pnl: float
    exit_reason: ExitReason
    balance_after: float


@dataclass
class BacktestDaySummary:
    date: str
    regime_blocked: bool
    qualifiers: list[str]
    trades: list[BacktestTrade] = field(default_factory=list)
    day_pnl: float = 0.0


@dataclass
class BacktestResult:
    start_date: str
    end_date: str
    starting_capital: float
    ending_capital: float
    total_return_pct: float
    total_trades: int
    wins: int
    losses: int
    win_rate_pct: float
    total_fees: float
    total_net_pnl: float
    max_drawdown_pct: float
    top_tickers: list[str]
    bar_interval: str
    days: list[BacktestDaySummary]
    trades: list[BacktestTrade]
    spy_return_pct: float | None
    assumptions: list[str]
    errors: list[str]


@dataclass
class _OpenPosition:
    ticker: str
    rank_score: float
    entry_ts: str
    entry_price: float
    shares: float
    target: float
    stop: float
    buy_fee: float


def _group_bars_by_date(bars: list[dict]) -> dict[str, list[dict]]:
    by_date: dict[str, list[dict]] = {}
    for bar in bars:
        by_date.setdefault(bar["date"], []).append(bar)
    for day in by_date:
        by_date[day].sort(key=lambda b: b["ts"])
    return by_date


def _regime_blocks(index_bars: dict[str, list[dict]], bar_idx: int) -> bool:
    """True when SPY, DIA, QQQ are all below their session open at bar_idx."""
    opens: dict[str, float] = {}
    for sym in REGIME_INDICES:
        bars = index_bars.get(sym, [])
        if not bars:
            return False
        opens[sym] = float(bars[0]["open"])
    for sym in REGIME_INDICES:
        bars = index_bars.get(sym, [])
        if bar_idx >= len(bars):
            return False
        if float(bars[bar_idx]["close"]) >= opens[sym]:
            return False
    return True


def _bar_exit_price(
    *,
    target: float,
    stop: float,
    bar: dict,
) -> tuple[float | None, ExitReason | None]:
    h, l = float(bar["high"]), float(bar["low"])
    hit_stop = l <= stop
    hit_target = h >= target
    if hit_stop and hit_target:
        return stop, "stop"
    if hit_stop:
        return stop, "stop"
    if hit_target:
        return target, "target"
    return None, None


def _simulate_trading_day(
    *,
    date: str,
    ordered_tickers: list[str],
    rank_by_ticker: dict[str, float],
    liquidity_caps: dict[str, float],
    ticker_bars: dict[str, list[dict]],
    index_bars: dict[str, list[dict]],
    cash: float,
    buy_fee: float,
    sell_fee: float,
    target_pct: float = TARGET_PCT,
    stop_pct: float = STOP_PCT,
    max_trades: int | None = None,
    use_dollar_target: bool = False,
    net_target: float | None = None,
) -> tuple[list[BacktestTrade], float]:
    """One position at a time; multiple round trips; rotate through ranked qualifiers."""
    master = index_bars.get("SPY") or next(iter(ticker_bars.values()), [])
    if not master:
        return [], cash

    trades: list[BacktestTrade] = []
    position: _OpenPosition | None = None
    n = len(master)
    queue = list(ordered_tickers)

    for i in range(n):
        if position is not None:
            tbars = ticker_bars.get(position.ticker, [])
            if i >= len(tbars):
                continue
            px, reason = _bar_exit_price(
                target=position.target,
                stop=position.stop,
                bar=tbars[i],
            )
            if px is None:
                continue
            exit_ts = tbars[i]["ts"]
            proceeds = position.shares * px - sell_fee
            gross = position.shares * (px - position.entry_price)
            fees = position.buy_fee + sell_fee
            net = gross - fees
            cash += proceeds
            closed_ticker = position.ticker
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=closed_ticker,
                    rank_score=position.rank_score,
                    entry_ts=position.entry_ts,
                    exit_ts=exit_ts,
                    entry_price=round(position.entry_price, 4),
                    exit_price=round(px, 4),
                    shares=position.shares,
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason=reason,
                    balance_after=round(cash, 2),
                )
            )
            position = None
            if max_trades is not None and len(trades) >= max_trades:
                break
            # rotate to back of queue so other ranked names get turns same day
            if closed_ticker in queue:
                queue.remove(closed_ticker)
                queue.append(closed_ticker)
            continue

        if _regime_blocks(index_bars, i):
            continue

        for ticker in queue:
            tbars = ticker_bars.get(ticker, [])
            if i >= len(tbars):
                continue
            entry_price = float(tbars[i]["open"])
            if entry_price <= 0:
                continue
            cap = liquidity_caps.get(ticker, cash)
            deploy = min(cap, cash - buy_fee)
            if deploy <= 0:
                continue
            shares = int(deploy / entry_price)
            if shares <= 0:
                continue
            cost = shares * entry_price + buy_fee
            if cost > cash:
                continue
            cash -= cost
            if use_dollar_target:
                goal = net_target if net_target is not None else daily_profit_target(deploy)
                target_px = sell_price_for_net_target(
                    entry_price=entry_price,
                    shares=shares,
                    net_target=goal,
                    buy_fee=buy_fee,
                    sell_fee=sell_fee,
                )
            else:
                target_px = entry_price * (1 + target_pct / 100)
            position = _OpenPosition(
                ticker=ticker,
                rank_score=rank_by_ticker.get(ticker, 0),
                entry_ts=tbars[i]["ts"],
                entry_price=entry_price,
                shares=float(shares),
                target=target_px,
                stop=entry_price * (1 - stop_pct / 100),
                buy_fee=buy_fee,
            )
            break

    if position is not None:
        tbars = ticker_bars.get(position.ticker, [])
        if tbars:
            last = tbars[-1]
            px = float(last["close"])
            proceeds = position.shares * px - sell_fee
            gross = position.shares * (px - position.entry_price)
            fees = position.buy_fee + sell_fee
            net = gross - fees
            cash += proceeds
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=position.ticker,
                    rank_score=position.rank_score,
                    entry_ts=position.entry_ts,
                    exit_ts=last["ts"],
                    entry_price=round(position.entry_price, 4),
                    exit_price=round(px, 4),
                    shares=position.shares,
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason="eod",
                    balance_after=round(cash, 2),
                )
            )
    return trades, cash


def _top_ranked_tickers(conn: sqlite3.Connection, *, period_days: int, top_n: int) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=period_days)
    out: list[dict] = []
    for row in ranked["ranked"]:
        if row["ticker"] in REGIME_ONLY_TICKERS:
            continue
        out.append(row)
        if len(out) >= top_n:
            break
    return out


def _qualifiers_for_day(
    conn: sqlite3.Connection,
    eval_date: str,
    tickers: set[str],
    *,
    tradable_cash: float,
) -> dict[str, dict]:
    day = evaluate_trading_day(conn, eval_date, tradable_cash=tradable_cash)
    return {
        m["ticker"]: m
        for m in day["screened_matches"]
        if m["ticker"] in tickers
    }


def _spy_return(conn: sqlite3.Connection, start_date: str, end_date: str) -> float | None:
    bars = get_ohlcv_bars(conn, "SPY", start_date=start_date, end_date=end_date)
    if len(bars) < 2:
        return None
    first = next((b for b in bars if b["date"] >= start_date), bars[0])
    last = next((b for b in reversed(bars) if b["date"] <= end_date), bars[-1])
    o, c = float(first["open"]), float(last["close"])
    if o <= 0:
        return None
    return round((c - o) / o * 100, 2)


def run_intraday_backtest(
    conn: sqlite3.Connection,
    *,
    lookback_days: int = 60,
    top_n: int = 20,
    starting_capital: float = ORIGINAL_BASIS,
    bar_interval: str = "5m",
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    target_pct: float = TARGET_PCT,
    stop_pct: float = STOP_PCT,
    max_trades_per_day: int | None = None,
    intraday_cache: dict[str, list[dict]] | None = None,
    use_dollar_target: bool = False,
    net_target: float | None = None,
) -> BacktestResult:
    start_date, end_date = date_range_for_period(lookback_days, conn=conn)
    top_rows = _top_ranked_tickers(conn, period_days=lookback_days, top_n=top_n)
    top_tickers = {r["ticker"] for r in top_rows}
    rank_by_ticker = {r["ticker"]: float(r.get("score") or 0) for r in top_rows}

    errors: list[str] = []
    cache = intraday_cache if intraday_cache is not None else {}
    symbols = sorted(top_tickers | set(REGIME_INDICES))

    for sym in symbols:
        if sym in cache:
            continue
        try:
            cache[sym] = get_intraday_bars(sym, lookback_days=lookback_days, interval=bar_interval)
        except Exception as exc:
            errors.append(f"{sym}: {exc}")
            cache[sym] = []

    ticker_by_date = {sym: _group_bars_by_date(cache.get(sym, [])) for sym in top_tickers}
    index_by_date = {sym: _group_bars_by_date(cache.get(sym, [])) for sym in REGIME_INDICES}

    trading_dates = sorted(
        {
            d
            for sym in top_tickers
            for d in ticker_by_date.get(sym, {})
            if start_date <= d <= end_date
        }
    )

    cash = starting_capital
    all_trades: list[BacktestTrade] = []
    day_summaries: list[BacktestDaySummary] = []
    peak = starting_capital
    max_dd = 0.0

    for date in trading_dates:
        qualifiers = _qualifiers_for_day(conn, date, top_tickers, tradable_cash=cash)
        ordered = sorted(
            qualifiers.keys(),
            key=lambda t: (-rank_by_ticker.get(t, 0), t),
        )

        index_bars = {sym: index_by_date[sym].get(date, []) for sym in REGIME_INDICES}
        regime_blocked = bool(index_bars.get("SPY")) and _regime_blocks(index_bars, 0)

        ticker_bars = {
            t: ticker_by_date[t].get(date, [])
            for t in ordered
            if ticker_by_date.get(t, {}).get(date)
        }
        caps = {t: float(qualifiers[t].get("liquidity_cap") or cash) for t in ordered}

        day_trades: list[BacktestTrade] = []
        if ordered and not regime_blocked:
            day_trades, cash = _simulate_trading_day(
                date=date,
                ordered_tickers=ordered,
                rank_by_ticker=rank_by_ticker,
                liquidity_caps=caps,
                ticker_bars=ticker_bars,
                index_bars=index_bars,
                cash=cash,
                buy_fee=buy_fee,
                sell_fee=sell_fee,
                target_pct=target_pct,
                stop_pct=stop_pct,
                max_trades=max_trades_per_day,
                use_dollar_target=use_dollar_target,
                net_target=net_target,
            )
            all_trades.extend(day_trades)

        peak = max(peak, cash)
        dd = (peak - cash) / peak * 100 if peak > 0 else 0
        max_dd = max(max_dd, dd)

        day_summaries.append(
            BacktestDaySummary(
                date=date,
                regime_blocked=regime_blocked,
                qualifiers=ordered,
                trades=day_trades,
                day_pnl=round(sum(t.net_pnl for t in day_trades), 2),
            )
        )

    wins = sum(1 for t in all_trades if t.net_pnl > 0)
    losses = sum(1 for t in all_trades if t.net_pnl <= 0)
    total_fees = sum(t.fees for t in all_trades)
    total_net = cash - starting_capital

    return BacktestResult(
        start_date=start_date,
        end_date=end_date,
        starting_capital=starting_capital,
        ending_capital=round(cash, 2),
        total_return_pct=round(total_net / starting_capital * 100, 2),
        total_trades=len(all_trades),
        wins=wins,
        losses=losses,
        win_rate_pct=round(100.0 * wins / max(len(all_trades), 1), 1),
        total_fees=round(total_fees, 2),
        total_net_pnl=round(total_net, 2),
        max_drawdown_pct=round(max_dd, 2),
        top_tickers=[r["ticker"] for r in top_rows],
        bar_interval=bar_interval,
        days=day_summaries,
        trades=all_trades,
        spy_return_pct=_spy_return(conn, start_date, end_date),
        assumptions=[
            f"Top {top_n} tickers by {lookback_days}d rank score; Yahoo {bar_interval} bars (not tick data).",
            (
                f"Entry at {bar_interval} bar open; exit on Growth Plan sell price (~${net_target or daily_profit_target(starting_capital):.0f} net) / −{stop_pct}% stop."
                if use_dollar_target
                else f"Entry at {bar_interval} bar open; exit on first touch of +{target_pct}% / −{stop_pct}% (stop wins if both in same bar)."
            ),
            "Step 3 qualification from daily bars (liquidity + ~3% swing band) per day.",
            "One position at a time; multiple round trips/day; rotates through ranked qualifiers."
            + (f"; max {max_trades_per_day} trades/day." if max_trades_per_day else "."),
            f"Fees: ${buy_fee:.0f} buy + ${sell_fee:.0f} sell per round trip.",
            "Regime gate: no new entries when SPY/DIA/QQQ all below session open.",
        ],
        errors=errors,
    )


def backtest_to_dict(result: BacktestResult) -> dict:
    return {
        "start_date": result.start_date,
        "end_date": result.end_date,
        "starting_capital": result.starting_capital,
        "ending_capital": result.ending_capital,
        "total_return_pct": result.total_return_pct,
        "total_trades": result.total_trades,
        "wins": result.wins,
        "losses": result.losses,
        "win_rate_pct": result.win_rate_pct,
        "total_fees": result.total_fees,
        "total_net_pnl": result.total_net_pnl,
        "max_drawdown_pct": result.max_drawdown_pct,
        "top_tickers": result.top_tickers,
        "bar_interval": result.bar_interval,
        "spy_return_pct": result.spy_return_pct,
        "assumptions": result.assumptions,
        "errors": result.errors,
        "days": [
            {
                "date": d.date,
                "regime_blocked": d.regime_blocked,
                "qualifiers": d.qualifiers,
                "day_pnl": d.day_pnl,
                "trades": [
                    {
                        "ticker": t.ticker,
                        "rank_score": t.rank_score,
                        "entry_ts": t.entry_ts,
                        "exit_ts": t.exit_ts,
                        "entry_price": t.entry_price,
                        "exit_price": t.exit_price,
                        "shares": t.shares,
                        "net_pnl": t.net_pnl,
                        "exit_reason": t.exit_reason,
                        "balance_after": t.balance_after,
                    }
                    for t in d.trades
                ],
            }
            for d in result.days
        ],
        "trades": [
            {
                "date": t.date,
                "ticker": t.ticker,
                "rank_score": t.rank_score,
                "entry_ts": t.entry_ts,
                "exit_ts": t.exit_ts,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "shares": t.shares,
                "gross_pnl": t.gross_pnl,
                "fees": t.fees,
                "net_pnl": t.net_pnl,
                "exit_reason": t.exit_reason,
                "balance_after": t.balance_after,
            }
            for t in result.trades
        ],
    }


def run_dollar_daily_backtest(
    conn: sqlite3.Connection,
    *,
    lookback_days: int = 14,
    starting_capital: float = ORIGINAL_BASIS,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    stop_pct: float = STOP_PCT,
) -> dict:
    """Daily-bar backtest using Growth Plan $ net targets (open entry, high/low exit)."""
    from investment_agent.dollar_target import simulate_dollar_outcome, net_at_high_from_open
    from investment_agent.period_screener import date_range_for_period

    start_date, end_date = date_range_for_period(lookback_days, conn=conn)
    top_rows = _top_ranked_tickers(conn, period_days=lookback_days, top_n=50)
    rank_by_ticker = {r["ticker"]: float(r.get("score") or 0) for r in top_rows}
    top_tickers = set(rank_by_ticker)

    dates = conn.execute(
        """
        SELECT DISTINCT date FROM ohlcv_daily
        WHERE date >= ? AND date <= ?
        ORDER BY date ASC
        """,
        (start_date, end_date),
    ).fetchall()

    cash = starting_capital
    trades: list[dict] = []
    days_summary: list[dict] = []
    goal = daily_profit_target(starting_capital)

    for row in dates:
        day = row["date"]
        day_eval = evaluate_trading_day(conn, day, tradable_cash=cash)
        screened = [
            m for m in day_eval["screened_matches"]
            if m["ticker"] in top_tickers
        ]
        screened.sort(key=lambda m: (-rank_by_ticker.get(m["ticker"], 0), m["ticker"]))
        day_pnl = 0.0
        day_trade: dict | None = None

        if screened:
            pick = screened[0]
            ticker = pick["ticker"]
            open_px = float(pick["open"])
            high = float(pick["high"])
            low = float(pick["low"])
            deploy = min(float(pick.get("liquidity_cap") or cash), cash)
            shares = int((deploy - buy_fee) / open_px) if open_px > 0 else 0
            if shares > 0:
                goal = daily_profit_target(deploy)
                outcome = simulate_dollar_outcome(
                    open_px, high, low,
                    deploy_dollar=deploy,
                    net_target=goal,
                    stop_pct=stop_pct,
                    buy_fee=buy_fee,
                    sell_fee=sell_fee,
                )
                target_px = sell_price_for_net_target(
                    entry_price=open_px,
                    shares=shares,
                    net_target=goal,
                    buy_fee=buy_fee,
                    sell_fee=sell_fee,
                )
                stop_px = open_px * (1 - stop_pct / 100)
                if outcome == "target":
                    exit_px = target_px
                    exit_reason = "target"
                elif outcome == "stop":
                    exit_px = stop_px
                    exit_reason = "stop"
                else:
                    exit_px = float(pick["close"])
                    exit_reason = "eod"

                gross = shares * (exit_px - open_px)
                fees = buy_fee + sell_fee
                net = round(gross - fees, 2)
                cash += net
                day_pnl = net
                net_at_high = net_at_high_from_open(
                    open_px, high, deploy_dollar=deploy, buy_fee=buy_fee, sell_fee=sell_fee,
                )
                day_trade = {
                    "date": day,
                    "ticker": ticker,
                    "entry_price": round(open_px, 2),
                    "exit_price": round(exit_px, 2),
                    "exit_reason": exit_reason,
                    "dollar_outcome": outcome,
                    "net_pnl": net,
                    "net_at_high": net_at_high,
                    "net_target": goal,
                    "balance_after": round(cash, 2),
                }
                trades.append(day_trade)

        days_summary.append({
            "date": day,
            "trade": day_trade,
            "day_pnl": day_pnl,
            "qualifiers": [m["ticker"] for m in screened[:5]],
        })

    wins = sum(1 for t in trades if t["net_pnl"] > 0)
    dollar_hits = sum(1 for t in trades if t.get("dollar_outcome") == "target")
    return {
        "start_date": start_date,
        "end_date": end_date,
        "starting_capital": starting_capital,
        "ending_capital": round(cash, 2),
        "total_net_pnl": round(cash - starting_capital, 2),
        "total_trades": len(trades),
        "wins": wins,
        "dollar_target_hits": dollar_hits,
        "dollar_hit_rate_pct": round(100.0 * dollar_hits / max(len(trades), 1), 1),
        "daily_net_target": goal,
        "days": days_summary,
        "trades": trades,
        "assumptions": [
            f"Top ranked Step 3 qualifier per day over {lookback_days}d window.",
            f"Open entry; exit on Growth Plan sell (~${daily_profit_target(starting_capital):.0f} net), stop, or close.",
            "Uses stored daily OHLCV only (no intraday bars).",
            f"Fees: ${buy_fee:.0f} buy + ${sell_fee:.0f} sell per round trip.",
        ],
    }


def run_backtest_from_db(db_path=None, **kwargs) -> BacktestResult:
    path = init_db(db_path)
    conn = connect(path)
    conn.row_factory = sqlite3.Row
    try:
        return run_intraday_backtest(conn, **kwargs)
    finally:
        conn.close()
```


---

<a id="src-investment_agent-backtest_strategy-py"></a>
## `src/investment_agent/backtest_strategy.py`

```python
"""Strategy-model backtest with daily dollar targets and month-end sweeps."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from investment_agent.backtest import (
    BacktestDaySummary,
    BacktestTrade,
    BacktestResult,
    _bar_exit_price,
    _group_bars_by_date,
    _qualifiers_for_day,
    _regime_blocks,
    _spy_return,
    _top_ranked_tickers,
)
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    ORIGINAL_BASIS,
    compute_month_end_sweep,
    round_trip_fees,
)
from investment_agent.period_screener import date_range_for_period
from investment_agent.providers.yfinance_bars import REGIME_INDICES, get_intraday_bars
from investment_agent.strategy import REGIME_ONLY_TICKERS
from investment_agent.strategy_models import (
    DAILY_TARGET_MODEL,
    RECOMMENDED_MODEL,
    StrategyModel,
    daily_profit_target,
    target_pct_for_dollars,
)


@dataclass
class MonthSummary:
    month: str
    trading_days: int
    gross_net: float
    management_sweep: float
    tax_sweep: float
    total_sweep: float
    balance_after_sweep: float


@dataclass
class StrategyBacktestResult(BacktestResult):
    model_name: str = ""
    months: list[MonthSummary] = field(default_factory=list)
    total_swept: float = 0.0
    avg_daily_target: float = 0.0
    days_hit_target: int = 0


def _simulate_day_with_model(
    *,
    date: str,
    model: StrategyModel,
    ordered_tickers: list[str],
    rank_by_ticker: dict[str, float],
    liquidity_caps: dict[str, float],
    ticker_bars: dict[str, list[dict]],
    index_bars: dict[str, list[dict]],
    cash: float,
    buy_fee: float,
    sell_fee: float,
    daily_target: float | None,
) -> tuple[list[BacktestTrade], float, bool]:
    master = index_bars.get("SPY") or next(iter(ticker_bars.values()), [])
    if not master:
        return [], cash, False

    trades: list[BacktestTrade] = []
    day_net = 0.0
    day_hit_target = False
    n = len(master)
    queue = list(ordered_tickers)
    position = None
    fees_rt = round_trip_fees(buy_fee, sell_fee)

    for i in range(n):
        if daily_target is not None and day_net >= daily_target:
            day_hit_target = True
            break

        if position is not None:
            tbars = ticker_bars.get(position["ticker"], [])
            if i >= len(tbars):
                continue
            px, reason = _bar_exit_price(
                target=position["target"],
                stop=position["stop"],
                bar=tbars[i],
            )
            if px is None:
                continue
            exit_ts = tbars[i]["ts"]
            proceeds = position["shares"] * px - sell_fee
            gross = position["shares"] * (px - position["entry_price"])
            fees = position["buy_fee"] + sell_fee
            net = gross - fees
            cash += proceeds
            day_net += net
            closed = position["ticker"]
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=closed,
                    rank_score=position["rank_score"],
                    entry_ts=position["entry_ts"],
                    exit_ts=exit_ts,
                    entry_price=round(position["entry_price"], 4),
                    exit_price=round(px, 4),
                    shares=position["shares"],
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason=reason,
                    balance_after=round(cash, 2),
                )
            )
            position = None

            if model.stop_day_after_stop and reason == "stop":
                break
            if len(trades) >= model.max_trades_per_day:
                break
            if daily_target is not None and day_net >= daily_target:
                day_hit_target = True
                break
            if closed in queue:
                queue.remove(closed)
                queue.append(closed)
            continue

        if i < model.entry_bar_delay:
            continue
        if _regime_blocks(index_bars, i):
            continue
        if len(trades) >= model.max_trades_per_day:
            break

        for ticker in queue:
            tbars = ticker_bars.get(ticker, [])
            if i >= len(tbars):
                continue
            entry_price = float(tbars[i]["open"])
            if entry_price <= 0:
                continue
            cap = liquidity_caps.get(ticker, cash)
            deploy = min(cap, cash - buy_fee)
            if deploy <= 0:
                continue
            shares = int(deploy / entry_price)
            if shares <= 0:
                continue
            cost = shares * entry_price + buy_fee
            if cost > cash:
                continue

            if model.target_pct is not None:
                tgt_pct = model.target_pct
            else:
                remaining = (daily_target or 0) - day_net
                if remaining <= 0:
                    day_hit_target = True
                    break
                pct = target_pct_for_dollars(
                    net_needed=remaining,
                    deploy_dollar=shares * entry_price,
                    fees=fees_rt,
                    min_pct=model.min_dynamic_target_pct,
                    max_pct=model.max_dynamic_target_pct,
                )
                if pct is None:
                    continue
                tgt_pct = pct

            cash -= cost
            position = {
                "ticker": ticker,
                "rank_score": rank_by_ticker.get(ticker, 0),
                "entry_ts": tbars[i]["ts"],
                "entry_price": entry_price,
                "shares": float(shares),
                "target": entry_price * (1 + tgt_pct / 100),
                "stop": entry_price * (1 - model.stop_pct / 100),
                "buy_fee": buy_fee,
            }
            break

    if position is not None:
        tbars = ticker_bars.get(position["ticker"], [])
        if tbars:
            last = tbars[-1]
            px = float(last["close"])
            proceeds = position["shares"] * px - sell_fee
            gross = position["shares"] * (px - position["entry_price"])
            fees = position["buy_fee"] + sell_fee
            net = gross - fees
            cash += proceeds
            day_net += net
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=position["ticker"],
                    rank_score=position["rank_score"],
                    entry_ts=position["entry_ts"],
                    exit_ts=last["ts"],
                    entry_price=round(position["entry_price"], 4),
                    exit_price=round(px, 4),
                    shares=position["shares"],
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason="eod",
                    balance_after=round(cash, 2),
                )
            )

    if daily_target is not None and day_net >= daily_target:
        day_hit_target = True
    return trades, cash, day_hit_target


def run_strategy_backtest(
    conn: sqlite3.Connection,
    model: StrategyModel,
    *,
    lookback_days: int = 60,
    top_n: int = 20,
    starting_capital: float = ORIGINAL_BASIS,
    bar_interval: str = "5m",
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    intraday_cache: dict[str, list[dict]] | None = None,
) -> StrategyBacktestResult:
    start_date, end_date = date_range_for_period(lookback_days, conn=conn)
    top_rows = _top_ranked_tickers(conn, period_days=lookback_days, top_n=top_n)
    top_tickers = {r["ticker"] for r in top_rows}
    rank_by_ticker = {r["ticker"]: float(r.get("score") or 0) for r in top_rows}

    errors: list[str] = []
    cache = dict(intraday_cache or {})
    for sym in sorted(top_tickers | set(REGIME_INDICES)):
        if sym not in cache:
            try:
                cache[sym] = get_intraday_bars(sym, lookback_days=lookback_days, interval=bar_interval)
            except Exception as exc:
                errors.append(f"{sym}: {exc}")
                cache[sym] = []

    ticker_by_date = {sym: _group_bars_by_date(cache.get(sym, [])) for sym in top_tickers}
    index_by_date = {sym: _group_bars_by_date(cache.get(sym, [])) for sym in REGIME_INDICES}

    trading_dates = sorted(
        {
            d
            for sym in top_tickers
            for d in ticker_by_date.get(sym, {})
            if start_date <= d <= end_date
        }
    )

    cash = starting_capital
    all_trades: list[BacktestTrade] = []
    day_summaries: list[BacktestDaySummary] = []
    month_summaries: list[MonthSummary] = []
    month_net: dict[str, float] = {}
    total_swept = 0.0
    daily_targets_used: list[float] = []
    days_hit_target = 0
    peak = starting_capital
    max_dd = 0.0

    for idx, date in enumerate(trading_dates):
        month_key = date[:7]
        month_net.setdefault(month_key, 0.0)

        day_start_cash = cash
        daily_target = None
        if model.target_pct is None:
            daily_target = daily_profit_target(
                day_start_cash,
                base=model.daily_base_target,
                step=model.daily_step,
                every=model.daily_step_every,
            )
            daily_targets_used.append(daily_target)

        qualifiers = _qualifiers_for_day(conn, date, top_tickers, tradable_cash=cash)
        ordered = sorted(qualifiers.keys(), key=lambda t: (-rank_by_ticker.get(t, 0), t))
        index_bars = {sym: index_by_date[sym].get(date, []) for sym in REGIME_INDICES}
        regime_blocked = bool(index_bars.get("SPY")) and _regime_blocks(index_bars, 0)

        day_trades: list[BacktestTrade] = []
        hit = False
        if ordered and not regime_blocked:
            ticker_bars = {
                t: ticker_by_date[t].get(date, [])
                for t in ordered
                if ticker_by_date.get(t, {}).get(date)
            }
            caps = {t: float(qualifiers[t].get("liquidity_cap") or cash) for t in ordered}
            day_trades, cash, hit = _simulate_day_with_model(
                date=date,
                model=model,
                ordered_tickers=ordered,
                rank_by_ticker=rank_by_ticker,
                liquidity_caps=caps,
                ticker_bars=ticker_bars,
                index_bars=index_bars,
                cash=cash,
                buy_fee=buy_fee,
                sell_fee=sell_fee,
                daily_target=daily_target,
            )
            all_trades.extend(day_trades)
            if hit:
                days_hit_target += 1

        day_pnl = sum(t.net_pnl for t in day_trades)
        month_net[month_key] += day_pnl

        peak = max(peak, cash)
        max_dd = max(max_dd, (peak - cash) / peak * 100 if peak > 0 else 0)

        day_summaries.append(
            BacktestDaySummary(
                date=date,
                regime_blocked=regime_blocked,
                qualifiers=ordered,
                trades=day_trades,
                day_pnl=round(day_pnl, 2),
            )
        )

        next_month = trading_dates[idx + 1][:7] if idx + 1 < len(trading_dates) else None
        if model.apply_monthly_sweeps and (next_month is None or next_month != month_key):
            sweep = compute_month_end_sweep(month_net[month_key])
            if sweep.applies:
                cash -= sweep.total_sweep
                total_swept += sweep.total_sweep
            month_summaries.append(
                MonthSummary(
                    month=month_key,
                    trading_days=sum(1 for d in day_summaries if d.date.startswith(month_key)),
                    gross_net=round(month_net[month_key], 2),
                    management_sweep=round(sweep.management_sweep, 2),
                    tax_sweep=round(sweep.tax_sweep, 2),
                    total_sweep=round(sweep.total_sweep, 2),
                    balance_after_sweep=round(cash, 2),
                )
            )

    wins = sum(1 for t in all_trades if t.net_pnl > 0)
    total_fees = sum(t.fees for t in all_trades)
    total_net = cash - starting_capital

    assumptions = [
        f"Model: {model.name} — {model.description}",
        f"Top {top_n} ranked tickers; Yahoo {bar_interval} bars.",
        f"Stop −{model.stop_pct}%; max {model.max_trades_per_day} trades/day; "
        f"entry after {model.entry_bar_delay * 5} min; "
        + ("stop day after stop-out." if model.stop_day_after_stop else "re-entry allowed."),
    ]
    if model.target_pct is not None:
        assumptions.append(f"Fixed target +{model.target_pct}%.")
    else:
        assumptions.append(
            f"Daily net target ${model.daily_base_target} + ${model.daily_step} per ${model.daily_step_every:,.0f} "
            f"above ${ORIGINAL_BASIS:,.0f}; dynamic per-trade target {model.min_dynamic_target_pct}–"
            f"{model.max_dynamic_target_pct}%."
        )
    if model.apply_monthly_sweeps:
        assumptions.append("Month-end: 10% management + 25% tax on positive monthly net, removed from tradable balance.")
    assumptions.append(f"Fees: ${buy_fee:.0f} buy + ${sell_fee:.0f} sell per round trip.")

    return StrategyBacktestResult(
        start_date=start_date,
        end_date=end_date,
        starting_capital=starting_capital,
        ending_capital=round(cash, 2),
        total_return_pct=round(total_net / starting_capital * 100, 2),
        total_trades=len(all_trades),
        wins=wins,
        losses=len(all_trades) - wins,
        win_rate_pct=round(100.0 * wins / max(len(all_trades), 1), 1),
        total_fees=round(total_fees, 2),
        total_net_pnl=round(total_net, 2),
        max_drawdown_pct=round(max_dd, 2),
        top_tickers=[r["ticker"] for r in top_rows],
        bar_interval=bar_interval,
        days=day_summaries,
        trades=all_trades,
        spy_return_pct=_spy_return(conn, start_date, end_date),
        assumptions=assumptions,
        errors=errors,
        model_name=model.name,
        months=month_summaries,
        total_swept=round(total_swept, 2),
        avg_daily_target=round(sum(daily_targets_used) / max(len(daily_targets_used), 1), 2),
        days_hit_target=days_hit_target,
    )
```


---

<a id="src-investment_agent-cio-py"></a>
## `src/investment_agent/cio.py`

```python
"""CIO managing agent — rule-based dashboard summary (Phase 5, no Claude)."""

from __future__ import annotations

import sqlite3

from investment_agent.account import build_dashboard_summary, summary_to_dict
from investment_agent.learning import generate_learning_report
from investment_agent.monitor import list_active_alerts
from investment_agent.stock_team import list_queue, screen_candidates


def build_cio_summary(conn: sqlite3.Connection) -> dict:
    """Aggregate sub-agent outputs into a single CIO panel (rule-based until Claude)."""
    dash = build_dashboard_summary(conn)
    dash_dict = summary_to_dict(dash)
    learning = generate_learning_report(conn)
    queue = list_queue(conn)
    alerts = list_active_alerts(conn)
    candidates = screen_candidates(conn)

    state_counts: dict[str, int] = {}
    for item in queue:
        state_counts[item["state"]] = state_counts.get(item["state"], 0) + 1

    in_trade = state_counts.get("in_trade", 0) + state_counts.get("eod", 0)
    action_items: list[str] = []

    if dash.block_new_longs:
        action_items.append("Regime blocks new longs — manage open positions only.")
    elif candidates:
        action_items.append(
            f"{len(candidates)} screener candidate(s) — sync queue if you want fresh ideas."
        )

    if alerts:
        action_items.append(f"{len(alerts)} active price alert(s) — review intraday panel.")
    if in_trade:
        action_items.append(f"{in_trade} position(s) in trade/EOD — confirm flat by close or log exit.")
    if learning["eod_open_positions"]:
        action_items.append("Learning flagged open positions near EOD — verify overnight hold policy.")
    if dash.monthly_realized_net <= 0 and dash.total_fees_paid > 0:
        action_items.append(
            f"Month net ${dash.monthly_realized_net:.2f} after ${dash.total_fees_paid:.2f} fees — "
            "fees matter at $7/$7; aim for +1.5% targets."
        )
    if not action_items:
        action_items.append("No urgent actions — run ingest + monitor to stay current.")

    headline_parts: list[str] = []
    if dash.block_new_longs:
        headline_parts.append("Caution: triple-index down")
    else:
        headline_parts.append("Regime OK for new longs")
    headline_parts.append(f"${dash.tradable_cash:,.0f} tradable")
    headline_parts.append(f"goal {dash.goal_pct:.4f}%")
    headline = " · ".join(headline_parts)

    narrative_parts = [
        f"CIO summary (rule-based, no Claude). {headline}.",
        dash.market_brief.split(".")[0] + "." if dash.market_brief else "",
        f"Queue: {len(queue)} item(s)"
        + (f" ({in_trade} live)" if in_trade else "")
        + f"; {len(alerts)} alert(s); month P&L ${dash.monthly_realized_net:+.2f}.",
    ]
    if learning["highlights"]:
        narrative_parts.append(learning["highlights"][0])
    narrative = " ".join(p for p in narrative_parts if p)

    return {
        "headline": headline,
        "narrative": narrative,
        "action_items": action_items[:6],
        "sub_agents": {
            "research": dash.market_brief.split(". Rule-based")[0],
            "regime": (
                dash.regime["summary"]
                if dash.regime
                else "No regime data — run ingest."
            ),
            "stock_team": f"{len(candidates)} qualified candidate(s) on screener",
            "monitor": f"{len(alerts)} active alert(s); {in_trade} in-trade queue item(s)",
            "learning": (
                learning["highlights"][0]
                if learning["highlights"]
                else "No journal activity to analyze yet."
            ),
        },
        "queue_summary": {
            "total": len(queue),
            "by_state": state_counts,
        },
        "goal_pct": dash.goal_pct,
        "tradable_cash": dash.tradable_cash,
        "monthly_realized_net": dash.monthly_realized_net,
        "block_new_longs": dash.block_new_longs,
        "claude_ready": False,
        "dashboard": dash_dict,
    }
```


---

<a id="src-investment_agent-close_report-py"></a>
## `src/investment_agent/close_report.py`

```python
"""Daily Close and Weekly Close — retrospective Growth Plan attribution.

Shows which top-20 ranked tickers would have hit today's dollar goal from:
- **Open entry** (daily bar open)
- **10:00 ET entry** (first 5m bar at/after 30-minute gate)

Compares journal trades, system #1 pick, and best achievable name on the list.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary
from investment_agent.dollar_target import (
    net_at_high_from_open,
    shares_for_deploy,
    simulate_dollar_outcome,
    target_sell_price,
)
from investment_agent.finance import ORIGINAL_BASIS, daily_profit_target
from investment_agent.historical import evaluate_trading_day
from investment_agent.journal import get_completed_round_trips
from investment_agent.period_screener import (
    date_range_for_period,
    list_trading_dates,
    run_period_screener,
)
from investment_agent.strategy_models import RECOMMENDED_MODEL

ET = ZoneInfo("America/New_York")
ENTRY_BAR_DELAY = RECOMMENDED_MODEL.entry_bar_delay  # 6 → 10:00 ET on 5m bars
TOP_N = 20


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def price_at_10_et_from_day_bars(day_bars: list[dict]) -> float | None:
    """Return 10:00 ET entry proxy (open of bar index 6 after 9:30 open)."""
    if len(day_bars) <= ENTRY_BAR_DELAY:
        return None
    bar = day_bars[ENTRY_BAR_DELAY]
    open_px = float(bar.get("open") or 0)
    return round(open_px, 4) if open_px > 0 else None


def fetch_price_at_10_et(
    ticker: str,
    report_date: str,
    *,
    intraday_cache: dict[str, Any] | None = None,
) -> float | None:
    """Fetch 5m bars and return 10:00 ET open for ``report_date``."""
    cache = intraday_cache if intraday_cache is not None else {}
    key = f"{ticker}:{report_date}"
    if key in cache:
        return cache[key]

    try:
        from investment_agent.backtest import _group_bars_by_date
        from investment_agent.providers.yfinance_bars import get_intraday_bars

        bars_key = f"_bars:{ticker}"
        if bars_key not in cache:
            cache[bars_key] = get_intraday_bars(ticker, lookback_days=14, interval="5m")
        by_date = _group_bars_by_date(cache[bars_key])
        px = price_at_10_et_from_day_bars(by_date.get(report_date, []))
        cache[key] = px
        return px
    except Exception:
        cache[key] = None
        return None


def save_rank_snapshot(
    conn: sqlite3.Connection,
    snapshot_date: str,
    ranked: list[dict],
    *,
    top_n: int = TOP_N,
) -> None:
    payload = ranked[:top_n]
    conn.execute(
        """
        INSERT INTO rank_snapshots (snapshot_date, created_at, ranked_json, top_n)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(snapshot_date) DO UPDATE SET
          created_at = excluded.created_at,
          ranked_json = excluded.ranked_json,
          top_n = excluded.top_n
        """,
        (snapshot_date, _utc_now(), json.dumps(payload), top_n),
    )


def get_rank_snapshot(conn: sqlite3.Connection, snapshot_date: str) -> list[dict] | None:
    row = conn.execute(
        "SELECT ranked_json FROM rank_snapshots WHERE snapshot_date = ?",
        (snapshot_date,),
    ).fetchone()
    if not row:
        return None
    return json.loads(row["ranked_json"])


def build_ranked_top20_for_date(
    conn: sqlite3.Connection,
    report_date: str,
    *,
    period_days: int = 14,
) -> list[dict]:
    """Reconstruct top-20 rank as of ``report_date`` (no hindsight re-rank)."""
    stored = get_rank_snapshot(conn, report_date)
    if stored:
        return stored[:TOP_N]

    start, end = date_range_for_period(period_days, end_date=report_date, conn=conn)
    trading_dates = list_trading_dates(conn, count=period_days, end_date=report_date)
    period = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        min_days_screened=1,
        trading_dates=trading_dates or None,
        requested_trading_days=period_days,
    )
    day_eval = evaluate_trading_day(conn, report_date)
    screened = {m["ticker"]: m for m in day_eval.get("screened_matches") or []}

    candidates: list[dict] = []
    for c in period.get("candidates") or []:
        ticker = c["ticker"]
        row = dict(c)
        row["live_pass_today"] = ticker in screened
        row["rank_date"] = report_date
        candidates.append(row)

    candidates.sort(
        key=lambda r: (-float(r.get("score") or 0), -int(r.get("days_screened") or 0), r["ticker"])
    )
    top = candidates[:TOP_N]

    if not top:
        from investment_agent.db import get_active_watchlist

        fallback: list[dict] = []
        for ticker in get_active_watchlist(conn):
            if _day_bar(conn, ticker, report_date) is None:
                continue
            m = conn.execute(
                """
                SELECT avg_range_pct, meets_liquidity_min, near_swing_target
                FROM ticker_metrics WHERE ticker = ?
                ORDER BY computed_at DESC LIMIT 1
                """,
                (ticker,),
            ).fetchone()
            fallback.append(
                {
                    "ticker": ticker,
                    "score": 0.5,
                    "days_screened": 0,
                    "hit_rate_pct": 0.0,
                    "dollar_hit_rate_pct": 0.0,
                    "live_pass_today": ticker in screened,
                    "avg_range_pct": float(m["avg_range_pct"]) if m and m["avg_range_pct"] else 3.0,
                }
            )
        fallback.sort(key=lambda r: r["ticker"])
        top = fallback[:TOP_N]

    if top:
        save_rank_snapshot(conn, report_date, top)
    return top


def _day_bar(conn: sqlite3.Connection, ticker: str, report_date: str) -> dict | None:
    from investment_agent.db import get_ohlcv_bars

    rows = get_ohlcv_bars(conn, ticker, start_date=report_date, end_date=report_date)
    if not rows:
        return None
    r = rows[0]
    return {
        "open": float(r["open"]),
        "high": float(r["high"]),
        "low": float(r["low"]),
        "close": float(r["close"]),
    }


def _simulate_entry_close(
    *,
    entry_price: float | None,
    day_bar: dict,
    deploy: float,
    net_target: float,
    entry_label: str,
) -> dict:
    if entry_price is None or entry_price <= 0 or not day_bar:
        return {
            "entry_label": entry_label,
            "entry_price": entry_price,
            "available": False,
        }

    open_px = day_bar["open"]
    high = day_bar["high"]
    low = day_bar["low"]
    shares = shares_for_deploy(entry_price, deploy)
    target_px = target_sell_price(
        entry_price=entry_price,
        deploy_dollar=deploy,
        net_target=net_target,
    )
    outcome = simulate_dollar_outcome(
        entry_price,
        high,
        low,
        deploy_dollar=deploy,
        net_target=net_target,
    )
    net_at_high = net_at_high_from_open(entry_price, high, deploy_dollar=deploy)
    hit_goal = net_at_high >= net_target * 0.98

    return {
        "entry_label": entry_label,
        "entry_price": round(entry_price, 2),
        "available": True,
        "shares": shares,
        "target_sell_price": round(target_px, 2) if target_px else None,
        "net_at_high": net_at_high,
        "hit_goal": hit_goal,
        "outcome": outcome,
        "day_high": round(high, 2),
        "day_low": round(low, 2),
    }


def _evaluate_ticker_close_row(
    conn: sqlite3.Connection,
    row: dict,
    report_date: str,
    *,
    deploy: float,
    net_target: float,
    intraday_cache: dict[str, Any] | None = None,
) -> dict | None:
    ticker = row["ticker"]
    bar = _day_bar(conn, ticker, report_date)
    if not bar:
        return None

    entry_open = bar["open"]
    entry_10 = fetch_price_at_10_et(ticker, report_date, intraday_cache=intraday_cache)

    open_sim = _simulate_entry_close(
        entry_price=entry_open,
        day_bar=bar,
        deploy=deploy,
        net_target=net_target,
        entry_label="open",
    )
    sim_10 = _simulate_entry_close(
        entry_price=entry_10,
        day_bar=bar,
        deploy=deploy,
        net_target=net_target,
        entry_label="10:00_et",
    )

    return {
        "rank": None,  # filled by caller
        "ticker": ticker,
        "score": row.get("score"),
        "live_pass_today": bool(row.get("live_pass_today")),
        "dollar_hit_rate_pct": row.get("dollar_hit_rate_pct"),
        "hit_rate_pct": row.get("hit_rate_pct"),
        "avg_range_pct": row.get("avg_range_pct"),
        "day_open": round(bar["open"], 2),
        "day_high": round(bar["high"], 2),
        "day_low": round(bar["low"], 2),
        "day_close": round(bar["close"], 2),
        "open_entry": open_sim,
        "entry_10_et": sim_10,
        "best_net_at_high": max(
            open_sim.get("net_at_high") or 0,
            sim_10.get("net_at_high") or 0,
        ),
        "hit_goal_either": bool(open_sim.get("hit_goal") or sim_10.get("hit_goal")),
    }


def _journal_for_date(conn: sqlite3.Connection, report_date: str) -> dict:
    legs = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, notes
        FROM trade_journal
        WHERE substr(executed_at, 1, 10) = ?
        ORDER BY executed_at ASC, id ASC
        """,
        (report_date,),
    ).fetchall()
    journal_legs = [
        {
            "id": r["id"],
            "ticker": r["ticker"],
            "side": r["side"],
            "shares": r["shares"],
            "price": r["price"],
            "fee": r["fee"],
            "executed_at": r["executed_at"],
            "notes": r["notes"],
        }
        for r in legs
    ]

    round_trips = []
    for trip in get_completed_round_trips(conn, limit=100):
        sell_day = trip["sell_at"][:10]
        buy_day = trip["buy_at"][:10]
        if sell_day != report_date and buy_day != report_date:
            continue
        round_trips.append(
            {
                "ticker": trip["ticker"],
                "shares": trip["shares"],
                "buy_price": trip["buy_price"],
                "sell_price": trip["sell_price"],
                "buy_at": trip["buy_at"],
                "sell_at": trip["sell_at"],
                "net_pnl": trip["net_pnl"],
                "same_day": trip["same_day"],
            }
        )

    journal_net = round(sum(t["net_pnl"] for t in round_trips if t["sell_at"][:10] == report_date), 2)
    return {
        "legs": journal_legs,
        "round_trips": round_trips,
        "realized_net": journal_net,
        "traded_today": len(journal_legs) > 0,
    }


def _pick_best_hit(rows: list[dict], *, use_10_et: bool) -> dict | None:
    key = "entry_10_et" if use_10_et else "open_entry"
    hits = [r for r in rows if r.get(key, {}).get("hit_goal")]
    if not hits:
        candidates = [r for r in rows if r.get(key, {}).get("available")]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r[key].get("net_at_high") or 0)
    return max(hits, key=lambda r: r[key].get("net_at_high") or 0)


def _summary_for_rows(
    rows: list[dict],
    *,
    net_target: float,
    deploy: float,
    rank1_ticker: str | None,
    journal: dict,
) -> dict:
    rank1_row = next((r for r in rows if r["ticker"] == rank1_ticker), None) if rank1_ticker else None

    best_open = _pick_best_hit(rows, use_10_et=False)
    best_10 = _pick_best_hit(rows, use_10_et=True)

    def _net(row: dict | None, key: str) -> float | None:
        if not row:
            return None
        return row.get(key, {}).get("net_at_high")

    counter_open = _net(best_open, "open_entry")
    counter_10 = _net(best_10, "entry_10_et")

    return {
        "net_target": net_target,
        "deploy": deploy,
        "rank1_ticker": rank1_ticker,
        "rank1_net_at_high_open": _net(rank1_row, "open_entry"),
        "rank1_net_at_high_10et": _net(rank1_row, "entry_10_et"),
        "rank1_hit_open": bool(rank1_row and rank1_row.get("open_entry", {}).get("hit_goal")),
        "rank1_hit_10et": bool(rank1_row and rank1_row.get("entry_10_et", {}).get("hit_goal")),
        "best_hit_ticker_open": best_open["ticker"] if best_open else None,
        "best_hit_ticker_10et": best_10["ticker"] if best_10 else None,
        "best_net_at_high_open": counter_open,
        "best_net_at_high_10et": counter_10,
        "counterfactual_if_best_open": round(deploy + (counter_open or 0), 2) if counter_open else None,
        "counterfactual_if_best_10et": round(deploy + (counter_10 or 0), 2) if counter_10 else None,
        "counterfactual_if_rank1_open": round(deploy + (_net(rank1_row, "open_entry") or 0), 2)
        if rank1_row
        else None,
        "counterfactual_if_rank1_10et": round(deploy + (_net(rank1_row, "entry_10_et") or 0), 2)
        if rank1_row
        else None,
        "journal_realized_net": journal.get("realized_net", 0),
        "journal_traded": journal.get("traded_today", False),
        "tickers_hit_goal_open": sum(1 for r in rows if r.get("open_entry", {}).get("hit_goal")),
        "tickers_hit_goal_10et": sum(1 for r in rows if r.get("entry_10_et", {}).get("hit_goal")),
        "tickers_evaluated": len(rows),
    }


def generate_daily_close_report(
    conn: sqlite3.Connection,
    report_date: str | None = None,
    *,
    fetch_10_et: bool = True,
    intraday_cache: dict[str, Any] | None = None,
) -> dict:
    """Build Daily Close report for ``report_date`` (default: latest stored OHLCV day)."""
    day = report_date or _latest_ohlcv_date(conn) or _today_et()
    summary_acct = build_dashboard_summary(conn)
    deploy = float(summary_acct.tradable_cash or ORIGINAL_BASIS)
    net_target = float(summary_acct.daily_target or daily_profit_target(deploy))

    ranked = build_ranked_top20_for_date(conn, day)
    cache = intraday_cache if intraday_cache is not None else ({} if fetch_10_et else {"_skip": True})

    full_rows: list[dict] = []
    for i, r in enumerate(ranked):
        row = _evaluate_ticker_close_row(
            conn,
            r,
            day,
            deploy=deploy,
            net_target=net_target,
            intraday_cache=cache if not cache.get("_skip") else None,
        )
        if row:
            row["rank"] = i + 1
            full_rows.append(row)

    step3_rows = [r for r in full_rows if r.get("live_pass_today")]

    journal = _journal_for_date(conn, day)
    rank1 = ranked[0]["ticker"] if ranked else None

    highlights: list[str] = []
    if journal["traded_today"]:
        highlights.append(
            f"Journal: ${journal['realized_net']:+.2f} realized on {day}"
            + (f" ({journal['round_trips'][0]['ticker']})" if journal["round_trips"] else "")
        )
    else:
        highlights.append(f"No journal trades logged for {day}.")

    full_summary = _summary_for_rows(
        full_rows, net_target=net_target, deploy=deploy, rank1_ticker=rank1, journal=journal,
    )
    step3_summary = _summary_for_rows(
        step3_rows, net_target=net_target, deploy=deploy, rank1_ticker=rank1, journal=journal,
    )

    if full_summary["best_hit_ticker_open"]:
        highlights.append(
            f"Best on full top 20 (open): {full_summary['best_hit_ticker_open']} "
            f"→ ~${full_summary['best_net_at_high_open']:.0f} net at high "
            f"({'hit' if full_summary['best_net_at_high_open'] and full_summary['best_net_at_high_open'] >= net_target else 'miss'})"
        )
    if rank1:
        highlights.append(
            f"Ranked #1 was {rank1}: "
            f"open ~${full_summary['rank1_net_at_high_open'] or 0:.0f} / "
            f"10:00 ~${full_summary['rank1_net_at_high_10et'] or 0:.0f} net at high "
            f"(goal ${net_target:.0f})"
        )

    return {
        "report_type": "daily",
        "report_date": day,
        "generated_at": _utc_now(),
        "net_target": net_target,
        "deploy": deploy,
        "highlights": highlights,
        "journal": journal,
        "rank1_ticker": rank1,
        "tabs": {
            "step3_pass": {
                "label": "Step 3 pass only",
                "summary": step3_summary,
                "rows": step3_rows,
            },
            "full_top20": {
                "label": "Full top 20",
                "summary": full_summary,
                "rows": full_rows,
            },
        },
        "assumptions": [
            f"Top {TOP_N} ranked as of {day} (frozen snapshot when saved, else reconstructed from {day} screener).",
            "Open entry = daily bar open; 10:00 ET entry = 5m bar index 6 open (30 min after 9:30).",
            f"One trade per day counterfactual; deploy ${deploy:,.0f}; goal ${net_target:.0f} net.",
            "Exit proxy: sell at day high if it reaches Growth Plan target; else stop/neither from daily bar.",
            "Journal compared by trade date (executed_at date prefix).",
        ],
    }


def _latest_ohlcv_date(conn: sqlite3.Connection, before: str | None = None) -> str | None:
    clause = "WHERE date < ?" if before else ""
    params: tuple[Any, ...] = (before,) if before else ()
    row = conn.execute(
        f"SELECT MAX(date) AS d FROM ohlcv_daily {clause}",
        params,
    ).fetchone()
    return row["d"] if row and row["d"] else None


def _trading_days_in_range(conn: sqlite3.Connection, start: str, end: str) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT date FROM ohlcv_daily
        WHERE date >= ? AND date <= ?
        ORDER BY date ASC
        """,
        (start, end),
    ).fetchall()
    return [r["date"] for r in rows]


def generate_weekly_close_report(
    conn: sqlite3.Connection,
    end_date: str | None = None,
    *,
    fetch_10_et: bool = False,
) -> dict:
    """Weekly Close — aggregate daily close for the last 5 trading days in window."""
    end = end_date or _latest_ohlcv_date(conn) or _today_et()
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    start = (end_dt - timedelta(days=7)).strftime("%Y-%m-%d")
    trading_days = _trading_days_in_range(conn, start, end)[-5:]

    daily_reports: list[dict] = []
    cache: dict[str, Any] = {}
    total_journal = 0.0
    total_best_open = 0.0
    total_best_10 = 0.0
    total_rank1_open = 0.0
    rank1_hits_open = 0
    best_hits_open = 0

    for day in trading_days:
        report = generate_daily_close_report(
            conn, day, fetch_10_et=fetch_10_et, intraday_cache=cache,
        )
        fs = report["tabs"]["full_top20"]["summary"]
        total_journal += fs.get("journal_realized_net") or 0
        if fs.get("best_net_at_high_open"):
            total_best_open += fs["best_net_at_high_open"]
        if fs.get("best_net_at_high_10et"):
            total_best_10 += fs["best_net_at_high_10et"]
        if fs.get("rank1_net_at_high_open"):
            total_rank1_open += fs["rank1_net_at_high_open"]
        if fs.get("rank1_hit_open"):
            rank1_hits_open += 1
        if fs.get("best_hit_ticker_open") and fs.get("best_net_at_high_open", 0) >= report["net_target"]:
            best_hits_open += 1

        daily_reports.append(
            {
                "date": day,
                "highlights": report["highlights"][:2],
                "journal_net": fs.get("journal_realized_net"),
                "rank1": fs.get("rank1_ticker"),
                "rank1_hit_open": fs.get("rank1_hit_open"),
                "best_open": fs.get("best_hit_ticker_open"),
                "best_net_open": fs.get("best_net_at_high_open"),
                "net_target": report["net_target"],
            }
        )

    summary_acct = build_dashboard_summary(conn)
    deploy = float(summary_acct.tradable_cash or ORIGINAL_BASIS)

    return {
        "report_type": "weekly",
        "report_date": end,
        "week_start": trading_days[0] if trading_days else start,
        "week_end": end,
        "trading_days": trading_days,
        "generated_at": _utc_now(),
        "net_target_per_day": daily_reports[0]["net_target"] if daily_reports else daily_profit_target(deploy),
        "summary": {
            "days": len(trading_days),
            "journal_total_net": round(total_journal, 2),
            "counterfactual_best_open_total": round(total_best_open, 2),
            "counterfactual_best_10et_total": round(total_best_10, 2),
            "counterfactual_rank1_open_total": round(total_rank1_open, 2),
            "rank1_hit_days_open": rank1_hits_open,
            "best_hit_days_open": best_hits_open,
            "missed_vs_best_open": round(total_best_open - total_journal, 2),
            "missed_vs_rank1_open": round(total_rank1_open - total_journal, 2),
        },
        "daily_reports": daily_reports,
        "assumptions": [
            "Rolling last 5 trading days with OHLCV in 7-calendar-day window ending on report_date.",
            "Weekly totals sum daily counterfactual 'best on list' nets (one pick per day).",
            "10:00 ET entries fetched only when fetch_10_et=True (slower).",
        ],
    }


def save_close_report(conn: sqlite3.Connection, report: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO close_reports (report_date, report_type, generated_at, payload_json)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(report_date, report_type) DO UPDATE SET
          generated_at = excluded.generated_at,
          payload_json = excluded.payload_json
        """,
        (
            report["report_date"],
            report["report_type"],
            report["generated_at"],
            json.dumps(report),
        ),
    )
    return int(cur.lastrowid)


def get_close_report(
    conn: sqlite3.Connection,
    report_date: str,
    report_type: str = "daily",
) -> dict | None:
    row = conn.execute(
        """
        SELECT payload_json FROM close_reports
        WHERE report_date = ? AND report_type = ?
        """,
        (report_date, report_type),
    ).fetchone()
    if not row:
        return None
    return json.loads(row["payload_json"])


def get_or_generate_daily_close(
    conn: sqlite3.Connection,
    report_date: str | None = None,
    *,
    regenerate: bool = False,
    fetch_10_et: bool = True,
) -> dict:
    day = report_date or _latest_ohlcv_date(conn) or _today_et()
    if not regenerate:
        cached = get_close_report(conn, day, "daily")
        if cached:
            return cached
    report = generate_daily_close_report(conn, day, fetch_10_et=fetch_10_et)
    save_close_report(conn, report)
    return report


def get_or_generate_weekly_close(
    conn: sqlite3.Connection,
    end_date: str | None = None,
    *,
    regenerate: bool = False,
    fetch_10_et: bool = False,
) -> dict:
    end = end_date or _latest_ohlcv_date(conn) or _today_et()
    if not regenerate:
        cached = get_close_report(conn, end, "weekly")
        if cached:
            return cached
    report = generate_weekly_close_report(conn, end, fetch_10_et=fetch_10_et)
    save_close_report(conn, report)
    return report


def list_close_report_dates(conn: sqlite3.Connection, report_type: str = "daily", limit: int = 30) -> list[str]:
    rows = conn.execute(
        """
        SELECT report_date FROM close_reports
        WHERE report_type = ?
        ORDER BY report_date DESC
        LIMIT ?
        """,
        (report_type, limit),
    ).fetchall()
    return [r["report_date"] for r in rows]
```


---

<a id="src-investment_agent-config-py"></a>
## `src/investment_agent/config.py`

```python
"""Environment configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def load_env(env_file: str | None = None) -> None:
    """Load .env from project root if present."""
    if env_file:
        load_dotenv(env_file)
        return
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    fred_api_key: str
    finnhub_api_key: str
    massive_api_key: str | None
    verify_test_ticker: str
    app_api_key: str
    # Optional Alpaca (data only — not required v3)
    alpaca_api_key: str | None
    alpaca_secret_key: str | None

    @classmethod
    def from_env(cls) -> Settings:
        load_env()
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            fred_api_key=os.getenv("FRED_API_KEY", ""),
            finnhub_api_key=os.getenv("FINNHUB_API_KEY", ""),
            massive_api_key=os.getenv("MASSIVE_API_KEY") or None,
            verify_test_ticker=os.getenv("VERIFY_TEST_TICKER", "SPY"),
            app_api_key=os.getenv("APP_API_KEY", ""),
            alpaca_api_key=os.getenv("ALPACA_API_KEY") or None,
            alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY") or None,
        )


def missing_required_keys(
    settings: Settings,
    *,
    require_anthropic: bool = True,
) -> list[str]:
    """Return names of required env vars that are empty (v3: no Alpaca)."""
    required = {
        "FRED_API_KEY": settings.fred_api_key,
        "FINNHUB_API_KEY": settings.finnhub_api_key,
    }
    if require_anthropic:
        required["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    return [name for name, value in required.items() if not value.strip()]
```


---

<a id="src-investment_agent-daily_rhythm-py"></a>
## `src/investment_agent/daily_rhythm.py`

```python
"""Three-step daily trading rhythm — status for dashboard."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary
from investment_agent.db import DEFAULT_DB_PATH
from investment_agent.monitor import get_latest_quotes
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.screen_actions import (
    ACTION_DAILY_INGEST,
    ACTION_PERIOD_SCREENER,
    get_screen_action_status,
)
from investment_agent.stock_team import build_analysis_card, _latest_metrics
from investment_agent.pullback_entry import compute_pullback_trade_plan
from investment_agent.trading_day import compute_trade_plan
from investment_agent.watchlist import compute_data_freshness

ET = ZoneInfo("America/New_York")
PT = ZoneInfo("America/Los_Angeles")
INGEST_LAST_RUN = DEFAULT_DB_PATH.parent / "ingest_last_run.json"
SCHEDULE_PLIST = Path.home() / "Library/LaunchAgents/com.investment-agent.ingest.plist"


def _parse_iso(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        ts = iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _same_calendar_day_pt(a: datetime | None, b: datetime | None) -> bool:
    if not a or not b:
        return False
    return a.astimezone(PT).date() == b.astimezone(PT).date()


def _read_last_ingest() -> dict | None:
    if not INGEST_LAST_RUN.is_file():
        return None
    try:
        return json.loads(INGEST_LAST_RUN.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def ingest_schedule_installed() -> bool:
    return SCHEDULE_PLIST.is_file()


def build_trading_candidates(
    conn: sqlite3.Connection,
    *,
    limit: int = 15,
    period_days: int = 14,
) -> list[dict]:
    """Top ranked names with buy size, sell target, and stop for pre-market review."""
    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or 0)
    net_target = float(summary.daily_target or 150)
    quotes = get_latest_quotes(conn)
    metrics = {r["ticker"]: r for r in _latest_metrics(conn)}
    ranked = build_ranked_candidates(conn, period_days=period_days).get("ranked", [])[:limit]

    rows: list[dict] = []
    for item in ranked:
        sym = item["ticker"]
        m = metrics.get(sym)
        session_open = (
            float(m["last_quote"] if m else 0)
            or float(m["last_close"] if m else 0)
            or float(quotes.get(sym) or 0)
        )
        avg_range = float(item.get("avg_range_pct") or (m["avg_range_pct"] if m else 0) or 0)
        card = build_analysis_card(m, deploy) if m else None
        size = float(card.suggested_size) if card else deploy
        if session_open and avg_range > 0:
            plan = compute_pullback_trade_plan(
                session_open=session_open,
                avg_range_pct=avg_range,
                deploy_dollar=size,
                net_target=net_target,
            )
        elif session_open:
            plan = compute_trade_plan(
                entry_price=session_open,
                deploy_dollar=size,
                net_target=net_target,
            )
        else:
            plan = {}
        rows.append(
            {
                "ticker": sym,
                "score": item.get("score"),
                "hit_rate_pct": item.get("hit_rate_pct"),
                "dollar_hit_rate_pct": item.get("dollar_hit_rate_pct"),
                "live_pass_today": item.get("live_pass_today"),
                "session_open": plan.get("session_open"),
                "limit_buy_price": plan.get("limit_buy_price"),
                "limit_sell_price": plan.get("limit_sell_price") or plan.get("target_price"),
                "limit_fill_deadline_et": plan.get("limit_fill_deadline_et"),
                "entry_price": plan.get("limit_buy_price") or plan.get("entry_price"),
                "recommended_shares": plan.get("shares"),
                "suggested_size": round(size, 0),
                "target_price": plan.get("target_price"),
                "stop_price": plan.get("stop_price"),
                "net_target": plan.get("net_target"),
                "pullback_pct": plan.get("pullback_pct"),
                "step3_pass": card is not None,
            }
        )
    return rows


def get_daily_rhythm_status(conn: sqlite3.Connection) -> dict:
    """Status for the 3-step daily workflow shown on Trade / Screen tabs."""
    now = datetime.now(timezone.utc)
    fresh = compute_data_freshness(conn)
    actions = get_screen_action_status(conn)
    last_ingest = _read_last_ingest() or {}

    ingest_action = actions.get(ACTION_DAILY_INGEST, {})
    screener_action = actions.get(ACTION_PERIOD_SCREENER, {})

    ingest_at = _parse_iso(last_ingest.get("finished_at")) or _parse_iso(
        ingest_action.get("completed_at")
    )
    screener_at = _parse_iso(screener_action.get("completed_at"))
    quote_age = fresh.get("quotes_max_age_hours")
    metric_age = fresh.get("metrics_max_age_hours")

    # Step 1 — after close: quotes fresh enough for overnight / next morning
    step1_state = "needed"
    if quote_age is not None and quote_age <= 8 and (metric_age or 999) <= 36:
        step1_state = "ready"
    elif quote_age is not None and quote_age <= 16:
        step1_state = "ok"

    step1_detail = "Pulls Range, ADV, and Step 3 metrics for your watchlist."
    if ingest_schedule_installed():
        step1_detail += " Auto-refresh runs at 4:30 PM and 6:30 AM (Mac local time)."
    else:
        step1_detail += " Enable auto-refresh once in Setup, or double-click Run After-Close Ingest.command."

    # Step 2 — pre-market: screener run today with fresh data
    step2_state = "needed"
    if screener_at and _same_calendar_day_pt(screener_at, now):
        if step1_state in ("ready", "ok") or (ingest_at and screener_at >= ingest_at):
            step2_state = "ready"
        else:
            step2_state = "ok"
    elif screener_at:
        step2_state = "stale"

    # Step 3 — intraday: always available via Refresh live
    step3_state = "ready"
    step3_detail = "Right before you buy in E*TRADE, refresh live prices and validate the symbol."

    return {
        "schedule_installed": ingest_schedule_installed(),
        "freshness": fresh,
        "last_ingest": {
            "finished_at": last_ingest.get("finished_at"),
            "mode": last_ingest.get("mode"),
            "quotes_refreshed": last_ingest.get("quotes_refreshed"),
            "bars_refreshed": last_ingest.get("bars_refreshed"),
        },
        "steps": [
            {
                "id": "after_close",
                "number": 1,
                "title": "After market close",
                "subtitle": "Refresh stock metrics",
                "state": step1_state,
                "last_at": ingest_at.isoformat() if ingest_at else None,
                "detail": step1_detail,
                "manual": "Double-click: scripts/Run After-Close Ingest.command",
            },
            {
                "id": "pre_market",
                "number": 2,
                "title": "Before trading starts",
                "subtitle": "Rank candidates · size · sell · stop",
                "state": step2_state,
                "last_at": screener_at.isoformat() if screener_at else None,
                "detail": "Runs the 14-day screener and fills in buy size, sell target, and stop loss per stock on the Trade tab.",
                "browser_action": "prepare_morning",
            },
            {
                "id": "before_buy",
                "number": 3,
                "title": "Right before you buy",
                "subtitle": "Confirm live prices",
                "state": step3_state,
                "last_at": None,
                "detail": step3_detail,
                "browser_action": "refresh_live",
            },
        ],
    }
```


---

<a id="src-investment_agent-dashboard-__init__-py"></a>
## `src/investment_agent/dashboard/__init__.py`

```python
"""Dashboard package."""
```


---

<a id="src-investment_agent-dashboard-app-py"></a>
## `src/investment_agent/dashboard/app.py`

```python
"""FastAPI dashboard — Phase 3–6 (queue, journal, goal, sweeps, monitor, learning, CIO, scenario)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from investment_agent.account import (
    apply_month_end_sweep,
    build_dashboard_summary,
    format_journal_notes,
    get_tax_rate,
    get_trading_mode,
    set_setting,
    set_trading_mode,
    summary_to_dict,
)
from investment_agent.cio import build_cio_summary
from investment_agent.config import Settings
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.historical import (
    build_historical_summary,
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    pull_historical_data,
)
from investment_agent.learning import (
    generate_learning_report,
    get_learning_report,
    get_or_generate_learning_report,
    list_learning_report_dates,
    save_learning_report,
)
from investment_agent.close_report import (
    generate_daily_close_report,
    generate_weekly_close_report,
    get_or_generate_daily_close,
    get_or_generate_weekly_close,
    list_close_report_dates,
    save_close_report,
    save_rank_snapshot,
)
from investment_agent.period_screener import (
    build_ranked_candidates,
    get_latest_screener_run,
    list_trading_dates,
    promote_ticker_to_queue,
    run_period_screener,
    save_screener_run,
    date_range_for_period,
)
from investment_agent.db import connect, init_db, get_active_watchlist
from investment_agent.db_maintenance import (
    assert_db_available_for_writes,
    ingest_lock_active,
    ingest_lock_message,
    repair_database,
)
from investment_agent.journal import (
    clear_all_trades,
    insert_trade,
    list_trades,
    resolve_executed_at,
    trade_to_dict,
)
from investment_agent.scenario import build_scenario_visualizer
from investment_agent.watchlist import (
    add_special_watch_ticker,
    build_special_watch_report,
    compute_universe_stats,
    deactivate_ticker,
    get_active_watchlist_details,
    import_tickers,
    list_presets,
    load_preset_into_watchlist,
)
from investment_agent.monitor import (
    acknowledge_alert,
    enrich_queue_item,
    get_latest_quotes,
    list_active_alerts,
    run_monitor_cycle,
)
from investment_agent.stock_team import (
    advance_queue_state,
    card_to_dict,
    list_queue,
    screen_candidates,
    set_queue_state,
    sync_queue_from_screener,
)
from investment_agent.ingest import run_ingest
from investment_agent.screen_actions import (
    ACTION_PERIOD_SCREENER,
    ACTION_REFRESH_RANKED,
    get_screen_action_status,
    record_screen_action,
)
from investment_agent.trading_day import (
    build_trading_day_status,
    clear_pinned_pick,
    pin_top_pick,
    refresh_live_quotes,
    validate_planned_trade,
)
from investment_agent.daily_rhythm import (
    build_trading_candidates,
    get_daily_rhythm_status,
    ingest_schedule_installed,
)

DASHBOARD_DIR = Path(__file__).resolve().parent
REPO_ROOT = DASHBOARD_DIR.parents[2]
ONE_PAGER_PDF = REPO_ROOT / "docs" / "DASHBOARD_ONE_PAGER.pdf"
templates = Jinja2Templates(directory=str(DASHBOARD_DIR / "templates"))

app = FastAPI(title="AI Investment Agent Dashboard", version="0.8.0")


@app.exception_handler(sqlite3.OperationalError)
def sqlite_operational_error_handler(_request: Request, exc: sqlite3.OperationalError) -> JSONResponse:
    msg = str(exc).lower()
    if "locked" in msg:
        detail = (
            "Database is locked — pause the dashboard and run ingest from Terminal: "
            "./scripts/run_ingest_mac.sh"
        )
        status = 503
    elif "no such column" in msg:
        detail = "Database schema out of date — run: ./scripts/repair_dashboard_mac.sh"
        status = 500
    else:
        detail = f"Database error: {exc}"
        status = 500
    return JSONResponse(status_code=status, content={"detail": detail})


class NoCacheDashboardMiddleware(BaseHTTPMiddleware):
    """Avoid stale dashboard HTML/JS/CSS in the browser during active development."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response


app.add_middleware(NoCacheDashboardMiddleware)
app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR / "static")), name="static")


class TradeCreate(BaseModel):
    ticker: str
    side: str
    shares: float = Field(gt=0)
    price: float = Field(gt=0)
    fee: float | None = None
    executed_at: str | None = None
    executed_date: str | None = None
    executed_time_pt: str | None = None
    notes: str | None = None
    queue_id: int | None = None


class TaxRateUpdate(BaseModel):
    tax_rate: float = Field(ge=0, le=1)


class TradingModeUpdate(BaseModel):
    mode: str


class QueueStateUpdate(BaseModel):
    state: str


class WatchlistImportBody(BaseModel):
    tickers: list[str]


class LoadPresetBody(BaseModel):
    preset: str
    replace: bool = False


class SpecialWatchAddBody(BaseModel):
    preset: str = "datacenter_us"
    ticker: str


class PeriodScreenerBody(BaseModel):
    period_days: int = 14
    min_days_screened: int = 1
    min_hit_rate_pct: float | None = None
    save: bool = True


class PinPickBody(BaseModel):
    ticker: str


class ValidateTradeBody(BaseModel):
    ticker: str
    price: float = Field(gt=0)
    shares: float | None = Field(default=None, gt=0)


class IngestRunBody(BaseModel):
    incremental: bool = False
    lookback_days: int = 60
    stale_hours: float = 20.0


class ScreenActionRecordBody(BaseModel):
    action: str = ACTION_REFRESH_RANKED


# Browser ingest is unreliable with large watchlists (DB lock, Finnhub rate limits, timeouts).
BROWSER_INGEST_MAX_TICKERS = 150


def _db():
    init_db()
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


def _require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    if not key or key == "change-me-to-a-random-secret":
        return
    if x_api_key != key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/one-pager.pdf")
def one_pager_pdf() -> FileResponse:
    if not ONE_PAGER_PDF.is_file():
        raise HTTPException(status_code=404, detail="One-pager PDF not found")
    return FileResponse(
        ONE_PAGER_PDF,
        media_type="application/pdf",
        filename="AI-Investment-Agent-Daily-One-Pager.pdf",
    )


@app.get("/api/config")
def api_config() -> dict[str, bool]:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    return {
        "api_key_required": bool(key and key != "change-me-to-a-random-secret"),
    }


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "api_key_required": bool(key and key != "change-me-to-a-random-secret"),
        },
    )


@app.get("/api/scenario/visualizer")
def api_scenario_visualizer(
    conn=Depends(_db),
    projection_months: int = 120,
) -> dict[str, Any]:
    return build_scenario_visualizer(conn, projection_horizon=projection_months)


@app.get("/api/cio/summary")
def api_cio_summary(conn=Depends(_db)) -> dict[str, Any]:
    return build_cio_summary(conn)


@app.get("/api/learning/report")
def api_learning_report(
    conn=Depends(_db),
    date: str | None = None,
) -> dict[str, Any]:
    return get_or_generate_learning_report(conn, report_date=date)


@app.get("/api/learning/history")
def api_learning_history(conn=Depends(_db), limit: int = 30) -> dict[str, Any]:
    return {"dates": list_learning_report_dates(conn, limit=limit)}


@app.post("/api/learning/generate")
def api_learning_generate(
    conn=Depends(_db),
    date: str | None = None,
    _: None = Depends(_require_api_key),
) -> dict:
    report = generate_learning_report(conn, report_date=date)
    report_id = save_learning_report(conn, report)
    conn.commit()
    return {"ok": True, "id": report_id, "report": report}


@app.get("/api/close/daily")
def api_close_daily(
    conn=Depends(_db),
    date: str | None = None,
    refresh: bool = False,
    fetch_10_et: bool = True,
) -> dict[str, Any]:
    report = get_or_generate_daily_close(
        conn,
        report_date=date,
        regenerate=refresh,
        fetch_10_et=fetch_10_et,
    )
    conn.commit()
    return report


@app.get("/api/close/weekly")
def api_close_weekly(
    conn=Depends(_db),
    end: str | None = None,
    refresh: bool = False,
    fetch_10_et: bool = False,
) -> dict[str, Any]:
    report = get_or_generate_weekly_close(
        conn,
        end_date=end,
        regenerate=refresh,
        fetch_10_et=fetch_10_et,
    )
    conn.commit()
    return report


@app.get("/api/close/history")
def api_close_history(
    conn=Depends(_db),
    report_type: str = "daily",
    limit: int = 30,
) -> dict[str, Any]:
    return {"dates": list_close_report_dates(conn, report_type=report_type, limit=limit)}


@app.post("/api/close/daily/generate")
def api_close_daily_generate(
    conn=Depends(_db),
    date: str | None = None,
    fetch_10_et: bool = True,
    _: None = Depends(_require_api_key),
) -> dict:
    report = generate_daily_close_report(conn, date, fetch_10_et=fetch_10_et)
    report_id = save_close_report(conn, report)
    conn.commit()
    return {"ok": True, "id": report_id, "report": report}


@app.post("/api/close/snapshot-rank")
def api_close_snapshot_rank(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    """Freeze current top-20 rank for today's date (call after 10:00 ET)."""
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"][:20]
    from investment_agent.trading_day import today_et_str

    day = today_et_str()
    save_rank_snapshot(conn, day, ranked)
    conn.commit()
    return {"ok": True, "snapshot_date": day, "count": len(ranked)}


@app.get("/api/historical/summary")
def api_historical_summary(conn=Depends(_db)) -> dict[str, Any]:
    return build_historical_summary(conn)


@app.get("/api/historical/evaluate")
def api_historical_evaluate(
    conn=Depends(_db),
    date: str | None = None,
) -> dict[str, Any]:
    if date:
        return evaluate_trading_day(conn, date)
    result = evaluate_prior_day(conn)
    if result is None:
        raise HTTPException(status_code=404, detail="No historical bars — run historical pull first")
    return result


@app.get("/api/historical/period")
def api_historical_period(
    start_date: str,
    end_date: str,
    conn=Depends(_db),
) -> dict[str, Any]:
    return evaluate_period(conn, start_date, end_date)


@app.post("/api/historical/pull")
def api_historical_pull(
    conn=Depends(_db),
    lookback_days: int = 60,
    _: None = Depends(_require_api_key),
) -> dict:
    settings = Settings.from_env()
    result = pull_historical_data(settings, db_path=None, lookback_days=lookback_days)
    conn.commit()
    return result


@app.get("/api/summary")
def api_summary(conn=Depends(_db)) -> dict[str, Any]:
    summary = build_dashboard_summary(conn)
    return summary_to_dict(summary)


@app.get("/api/trading-day/status")
def api_trading_day_status(conn=Depends(_db)) -> dict[str, Any]:
    return build_trading_day_status(conn)


@app.get("/api/daily-rhythm/status")
def api_daily_rhythm_status(conn=Depends(_db)) -> dict[str, Any]:
    return get_daily_rhythm_status(conn)


@app.get("/api/daily-rhythm/candidates")
def api_daily_rhythm_candidates(
    conn=Depends(_db),
    limit: int = 15,
    period_days: int = 14,
) -> dict[str, Any]:
    return {
        "candidates": build_trading_candidates(
            conn, limit=min(max(limit, 1), 30), period_days=period_days
        ),
        "period_days": period_days,
    }


@app.post("/api/daily-rhythm/prepare-morning")
def api_prepare_morning(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    """Step 2 — run screener and return trade candidates with size / sell / stop."""
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    start, end = date_range_for_period(14, conn=conn)
    trading_dates = list_trading_dates(conn, count=14)
    from investment_agent.account import build_dashboard_summary

    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or ORIGINAL_BASIS)
    result = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        tradable_cash=deploy,
        min_days_screened=1,
        min_hit_rate_pct=None,
        trading_dates=trading_dates or None,
        requested_trading_days=14,
    )
    run_id = save_screener_run(conn, result)
    record_screen_action(
        conn,
        ACTION_PERIOD_SCREENER,
        detail=f"{len(result.get('candidates', []))} candidates · 14 trading days",
    )
    conn.commit()
    candidates = build_trading_candidates(conn, limit=15, period_days=14)
    status = build_trading_day_status(conn)
    rhythm = get_daily_rhythm_status(conn)
    return {
        "ok": True,
        "saved_run_id": run_id,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "trading_day": status,
        "rhythm": rhythm,
    }


@app.get("/api/health/db")
def api_health_db(conn=Depends(_db)) -> dict[str, Any]:
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        return {
            "ok": integrity == "ok",
            "integrity": integrity,
            "ingest_running": ingest_lock_active(),
        }
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail=f"Database error: {exc}") from exc


@app.post("/api/trading-day/refresh")
def api_trading_day_refresh(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    settings = Settings.from_env()
    try:
        refresh = refresh_live_quotes(conn, settings)
        if refresh.get("ok"):
            conn.commit()
        status = build_trading_day_status(conn)
        return {"refresh": refresh, "status": status}
    except sqlite3.OperationalError as exc:
        conn.rollback()
        msg = str(exc).lower()
        if "locked" in msg:
            detail = (
                "Database is locked — stop Terminal ingest or close duplicate dashboard "
                "windows, then run ./scripts/repair_dashboard_mac.sh"
            )
        else:
            detail = f"Database error: {exc} — run ./scripts/repair_dashboard_mac.sh"
        raise HTTPException(status_code=503, detail=detail) from exc
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Refresh live failed: {exc}") from exc


@app.post("/api/trading-day/validate")
def api_trading_day_validate(
    body: ValidateTradeBody,
    conn=Depends(_db),
) -> dict:
    return validate_planned_trade(
        conn,
        ticker=body.ticker,
        planned_price=body.price,
        shares=body.shares,
    )


@app.post("/api/trading-day/pin-pick")
def api_trading_day_pin(
    body: PinPickBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = pin_top_pick(conn, body.ticker)
    conn.commit()
    return {**result, "status": build_trading_day_status(conn)}


@app.post("/api/trading-day/clear-pin")
def api_trading_day_clear_pin(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = clear_pinned_pick(conn)
    conn.commit()
    return {**result, "status": build_trading_day_status(conn)}


@app.get("/api/queue")
def api_queue(conn=Depends(_db)) -> list[dict]:
    quotes = get_latest_quotes(conn)
    items = list_queue(conn)
    return [enrich_queue_item(conn, item, quotes) for item in items]


@app.get("/api/alerts")
def api_alerts(conn=Depends(_db)) -> list[dict]:
    return list_active_alerts(conn)


@app.post("/api/monitor/run")
def api_monitor_run(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = run_monitor_cycle(conn)
    conn.commit()
    return result


@app.post("/api/alerts/{alert_id}/acknowledge")
def api_ack_alert(
    alert_id: int,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = acknowledge_alert(conn, alert_id)
    if result.get("ok"):
        conn.commit()
    return result


@app.get("/api/candidates")
def api_candidates(conn=Depends(_db)) -> list[dict]:
    return [card_to_dict(c) for c in screen_candidates(conn)]


@app.post("/api/queue/sync")
def api_queue_sync(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = sync_queue_from_screener(conn)
    conn.commit()
    return result


@app.post("/api/queue/{item_id}/advance")
def api_queue_advance(
    item_id: int,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = advance_queue_state(conn, item_id)
    if result.get("ok"):
        conn.commit()
    return result


@app.post("/api/queue/{item_id}/state")
def api_queue_set_state(
    item_id: int,
    body: QueueStateUpdate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = set_queue_state(conn, item_id, body.state)
    if result.get("ok"):
        conn.commit()
    return result


@app.get("/api/journal")
def api_journal(conn=Depends(_db)) -> list[dict]:
    return [trade_to_dict(t) for t in list_trades(conn)]


@app.post("/api/journal")
def api_journal_create(
    body: TradeCreate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    mode = get_trading_mode(conn)
    try:
        executed_at = resolve_executed_at(
            executed_at=body.executed_at,
            executed_date=body.executed_date,
            executed_time_pt=body.executed_time_pt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    trade_id = insert_trade(
        conn,
        ticker=body.ticker,
        side=body.side,
        shares=body.shares,
        price=body.price,
        fee=body.fee,
        executed_at=executed_at,
        notes=format_journal_notes(body.notes, mode),
        queue_id=body.queue_id,
    )
    conn.commit()
    return {"ok": True, "id": trade_id, "trading_mode": mode}


@app.post("/api/journal/clear")
def api_journal_clear(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    removed = clear_all_trades(conn)
    conn.commit()
    return {"ok": True, "removed": removed}


@app.get("/api/settings/trading-mode")
def api_get_trading_mode(conn=Depends(_db)) -> dict:
    return {"mode": get_trading_mode(conn)}


@app.put("/api/settings/trading-mode")
def api_set_trading_mode(
    body: TradingModeUpdate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    try:
        mode = set_trading_mode(conn, body.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    conn.commit()
    return {"ok": True, "mode": mode}


@app.put("/api/settings/tax-rate")
def api_tax_rate(
    body: TaxRateUpdate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    set_setting(conn, "tax_reserve_rate", str(body.tax_rate))
    conn.commit()
    return {"ok": True, "tax_rate": get_tax_rate(conn)}


@app.post("/api/sweeps/apply")
def api_apply_sweep(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = apply_month_end_sweep(conn)
    if result.get("ok"):
        conn.commit()
    return result


@app.get("/api/watchlist")
def api_watchlist(conn=Depends(_db)) -> dict[str, Any]:
    return {
        "tickers": get_active_watchlist_details(conn),
        "count": len(get_active_watchlist_details(conn)),
    }


@app.get("/api/watchlist/presets")
def api_watchlist_presets() -> list[dict[str, Any]]:
    return [
        {"name": p.name, "description": p.description, "ticker_count": p.ticker_count}
        for p in list_presets()
    ]


@app.get("/api/watchlist/stats")
def api_watchlist_stats(conn=Depends(_db)) -> dict[str, Any]:
    return compute_universe_stats(conn)


@app.get("/api/screen/actions")
def api_screen_actions(conn=Depends(_db)) -> dict[str, Any]:
    return {"actions": get_screen_action_status(conn)}


@app.post("/api/screen/actions/record")
def api_screen_action_record(
    body: ScreenActionRecordBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    try:
        record_screen_action(conn, body.action, detail="Dashboard refresh")
        conn.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    status = get_screen_action_status(conn).get(body.action, {})
    return {"ok": True, "action": status}


@app.get("/api/watchlist/special-watch")
def api_special_watch(
    conn=Depends(_db),
    preset: str = "datacenter_us",
) -> dict[str, Any]:
    try:
        return build_special_watch_report(conn, preset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/watchlist/special-watch/add")
def api_special_watch_add(
    body: SpecialWatchAddBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    try:
        result = add_special_watch_ticker(conn, body.preset, body.ticker)
        conn.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/watchlist/load-preset")
def api_load_preset(
    body: LoadPresetBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    try:
        result = load_preset_into_watchlist(conn, body.preset, replace=body.replace)
        conn.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/ingest/preflight")
def api_ingest_preflight(conn=Depends(_db)) -> dict[str, Any]:
    if ingest_lock_active():
        return {
            "ticker_count": len(get_active_watchlist(conn)),
            "missing_api_keys": False,
            "browser_ok": False,
            "recommend_terminal": True,
            "ingest_running": True,
            "message": ingest_lock_message(),
            "terminal_command": "./scripts/run_ingest_mac.sh --incremental",
            "terminal_command_full": "./scripts/run_ingest_mac.sh",
        }
    symbols = get_active_watchlist(conn)
    settings = Settings.from_env()
    missing_keys = not (settings.fred_api_key and settings.finnhub_api_key)
    count = len(symbols)
    return {
        "ticker_count": count,
        "missing_api_keys": missing_keys,
        "browser_ok": count <= BROWSER_INGEST_MAX_TICKERS and not missing_keys,
        "recommend_terminal": count > BROWSER_INGEST_MAX_TICKERS,
        "ingest_running": False,
        "terminal_command": "./scripts/run_ingest_mac.sh --incremental",
        "terminal_command_full": "./scripts/run_ingest_mac.sh",
    }


@app.post("/api/ingest/run")
def api_ingest_run(
    body: IngestRunBody | None = None,
    _: None = Depends(_require_api_key),
) -> dict:
    settings = Settings.from_env()
    if not settings.fred_api_key or not settings.finnhub_api_key:
        raise HTTPException(
            status_code=503,
            detail="FRED_API_KEY and FINNHUB_API_KEY required in .env — restart dashboard after editing .env",
        )
    opts = body or IngestRunBody()
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    try:
        assert_db_available_for_writes()
        check_conn = connect(init_db())
        try:
            ticker_count = len(get_active_watchlist(check_conn))
        finally:
            check_conn.close()
        if ticker_count > BROWSER_INGEST_MAX_TICKERS:
            mode = " --incremental" if opts.incremental else ""
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Watchlist has {ticker_count} tickers — browser ingest supports up to "
                    f"{BROWSER_INGEST_MAX_TICKERS}. In Terminal run: "
                    f"cd ~/Home-Repository && ./scripts/run_ingest_mac.sh{mode}"
                ),
            )
        return run_ingest(
            settings,
            incremental=opts.incremental,
            lookback_days=opts.lookback_days,
            stale_hours=opts.stale_hours,
        )
    except HTTPException:
        raise
    except sqlite3.OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database is locked — use Terminal instead (pauses background service): "
                "./scripts/run_ingest_mac.sh --incremental"
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc


@app.post("/api/watchlist/import")
def api_watchlist_import(
    body: WatchlistImportBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = import_tickers(conn, body.tickers)
    conn.commit()
    return result


@app.delete("/api/watchlist/{ticker}")
def api_watchlist_remove(
    ticker: str,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = deactivate_ticker(conn, ticker)
    conn.commit()
    return result


@app.get("/api/screener/ranked")
def api_screener_ranked(
    conn=Depends(_db),
    period_days: int = 14,
) -> dict[str, Any]:
    return build_ranked_candidates(conn, period_days=period_days)


@app.post("/api/screener/period")
def api_screener_period(
    body: PeriodScreenerBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    start, end = date_range_for_period(body.period_days, conn=conn)
    trading_dates = list_trading_dates(conn, count=body.period_days)
    result = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        min_days_screened=body.min_days_screened,
        min_hit_rate_pct=body.min_hit_rate_pct,
        trading_dates=trading_dates or None,
        requested_trading_days=body.period_days,
    )
    if body.save:
        run_id = save_screener_run(conn, result)
        record_screen_action(
            conn,
            ACTION_PERIOD_SCREENER,
            detail=f"{len(result.get('candidates', []))} candidates · {body.period_days} trading days",
        )
        conn.commit()
        result["saved_run_id"] = run_id
    return result


@app.get("/api/screener/period/latest")
def api_screener_period_latest(conn=Depends(_db)) -> dict[str, Any]:
    result = get_latest_screener_run(conn)
    if result is None:
        return {"candidates": [], "summary": {}}
    return result


@app.post("/api/screener/promote/{ticker}")
def api_screener_promote(
    ticker: str,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = promote_ticker_to_queue(conn, ticker)
    if result.get("ok"):
        conn.commit()
    return result
```


---

<a id="src-investment_agent-dashboard-static-style-css"></a>
## `src/investment_agent/dashboard/static/style.css`

```css
/* AI Investment Agent Dashboard — Phase 3 */

:root {
  --bg: #0f1419;
  --surface: #1a2332;
  --surface2: #243044;
  --border: #2d3a4f;
  --text: #e8edf4;
  --muted: #8b9cb3;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --green: #22c55e;
  --red: #ef4444;
  --amber: #f59e0b;
  --radius: 10px;
  --font: "Segoe UI", system-ui, -apple-system, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  min-height: 100vh;
}

header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 1rem 1.5rem;
}

header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.35rem;
  font-weight: 600;
}

header .subtitle {
  color: var(--muted);
  font-size: 0.875rem;
}

.api-key-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  margin-top: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.875rem;
}

.api-key-bar label {
  color: var(--muted);
}

.api-key-bar input {
  flex: 1 1 220px;
  min-width: 180px;
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
}

.api-key-hint {
  flex: 1 1 100%;
  font-size: 0.78rem;
  color: var(--muted);
}

.screener-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  align-items: center;
  margin-top: 0.75rem;
  font-size: 0.875rem;
}

.screener-filters label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--muted);
}

.screener-filters input[type="text"],
.screener-filters input[type="number"],
.screener-filters select {
  padding: 0.3rem 0.45rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
}

.screener-filters .inline-check {
  color: var(--text);
}

.sortable-table th.sortable {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.sortable-table th.sortable:hover {
  color: var(--accent);
}

.sortable-table th.sortable.sorted-asc::after {
  content: " ▲";
  font-size: 0.7em;
  color: var(--accent);
}

.sortable-table th.sortable.sorted-desc::after {
  content: " ▼";
  font-size: 0.7em;
  color: var(--accent);
}

.prior-screened-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
  margin: 0.5rem 0 0.75rem;
}

.prior-screened-toolbar input[type="search"],
.prior-screened-toolbar select {
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  min-width: 8rem;
}

.prior-screened-summary {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.outcome-badge {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.outcome-badge.outcome-target {
  background: rgba(34, 197, 94, 0.18);
  color: var(--green);
}

.outcome-badge.outcome-stop {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
}

.outcome-badge.outcome-neither {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
}

.outcome-badge.outcome-dollar-target {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
}

.range-delta.positive { color: var(--green); }
.range-delta.negative { color: #fca5a5; }
.range-delta.warn { font-weight: 600; }

.table-wrap {
  overflow-x: auto;
  max-height: 28rem;
  overflow-y: auto;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 3rem;
}

.banner {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.banner.ok {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.35);
  color: #86efac;
}

.banner.block {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #fca5a5;
}

.grid {
  display: grid;
  gap: 1rem;
}

.banner.wait {
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.35);
  color: #93c5fd;
}

.banner.caution {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #fcd34d;
}

.banner.paper {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.45);
  color: #bfdbfe;
  font-weight: 600;
}

.banner.live {
  background: rgba(239, 68, 68, 0.18);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fecaca;
  font-weight: 600;
}

.journal-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}

.journal-mode-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
}

.journal-mode-row label {
  color: var(--muted);
  font-size: 0.875rem;
}

.journal-mode-row select {
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
}

.trading-day-section {
  margin-top: 1rem;
}

.trading-day-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.trading-day-header h2 {
  margin: 0;
  font-size: 1rem;
}

.trading-day-panel {
  border-width: 2px;
}

.trading-day-panel.verdict-go {
  border-color: rgba(34, 197, 94, 0.55);
}

.trading-day-panel.verdict-wait {
  border-color: rgba(59, 130, 246, 0.55);
}

.trading-day-panel.verdict-caution {
  border-color: rgba(245, 158, 11, 0.55);
}

.trading-day-panel.verdict-no_go {
  border-color: rgba(239, 68, 68, 0.55);
}

.trading-verdict {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.verdict-badge {
  flex: 0 0 auto;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.45rem 0.65rem;
  border-radius: 8px;
  background: var(--surface2);
}

.verdict-badge.go { background: rgba(34, 197, 94, 0.2); color: var(--green); }
.verdict-badge.wait { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
.verdict-badge.caution { background: rgba(245, 158, 11, 0.2); color: #fcd34d; }
.verdict-badge.no_go { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }

.verdict-headline {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.tradability-badge {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  margin: 0.35rem 0;
}

.tradability-badge.trad-tradable {
  background: rgba(34, 197, 94, 0.18);
  color: var(--green);
}

.tradability-badge.trad-caution,
.tradability-badge.trad-unknown {
  background: rgba(245, 158, 11, 0.18);
  color: #fcd34d;
}

.tradability-badge.trad-not-tradable {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
}

.tradability-detail {
  margin-bottom: 0.35rem;
  color: var(--muted);
}

.special-watch-panel {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--surface2);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}

.special-watch-panel h3 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
}

.special-watch-add {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
  margin: 0.75rem 0 1rem;
  padding: 0.65rem 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.special-watch-add label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
}

.special-watch-add input[type="text"] {
  width: 5.5rem;
  text-transform: uppercase;
}

.special-watch-add-hint {
  flex: 1 1 12rem;
  min-width: 10rem;
}

/* ── Daily rhythm (3-step workflow) ── */
.daily-rhythm {
  margin-bottom: 1.25rem;
}

.daily-rhythm-title {
  margin: 0 0 1rem;
  font-size: 1.05rem;
}

.rhythm-steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rhythm-step {
  padding: 0.85rem 1rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.rhythm-step.rhythm-state-ready {
  border-color: rgba(34, 197, 94, 0.35);
}

.rhythm-step.rhythm-state-needed,
.rhythm-step.rhythm-state-stale {
  border-color: rgba(251, 191, 36, 0.35);
}

.rhythm-step-head {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.rhythm-num {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 999px;
  background: var(--accent, #6366f1);
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rhythm-step-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.rhythm-sub {
  font-size: 0.82rem;
  color: var(--muted);
}

.rhythm-badge {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--muted);
}

.rhythm-state-ready .rhythm-badge {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.rhythm-detail,
.rhythm-last {
  margin: 0.5rem 0 0 2.5rem;
  font-size: 0.82rem;
}

.rhythm-action-btn {
  margin: 0.5rem 0 0 2.5rem;
}

.rhythm-manual {
  display: block;
  margin: 0.5rem 0 0 2.5rem;
  font-size: 0.78rem;
}

.rhythm-step3-panel {
  border-color: rgba(99, 102, 241, 0.35);
}

.setup-onboarding h3 {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
}

.setup-terminal-label {
  margin: 0.85rem 0 0.25rem;
  font-size: 0.82rem;
  color: var(--muted);
}

.setup-workflow-list {
  margin: 0.35rem 0 0.75rem 1.1rem;
  padding: 0;
}

.setup-workflow-list li {
  margin: 0.25rem 0;
}

.setup-terminal-note {
  margin: 0.5rem 0 1rem;
  max-width: 52rem;
}

.setup-terminal {
  margin: 0.25rem 0 0.5rem;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.25);
  color: #e2e8f0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.78rem;
  line-height: 1.45;
  white-space: pre-wrap;
  overflow-x: auto;
  user-select: all;
  cursor: text;
}

.setup-terminal-compact {
  margin-top: 0.35rem;
}

.setup-terminal:focus {
  outline: 2px solid rgba(99, 102, 241, 0.55);
  outline-offset: 2px;
}

.confidence-badge {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.confidence-badge.conf-high {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.confidence-badge.conf-medium {
  background: rgba(234, 179, 8, 0.2);
  color: #fde047;
}

.confidence-badge.conf-low {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
}

.screener-actions-compact {
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
}

.step3-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.step3-badge.step3-step3-pass {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.step3-badge.step3-too-quiet {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
}

.step3-badge.step3-too-wild {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
}

.step3-badge.step3-low-liquidity {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
}

.step3-badge.step3-missing-metrics {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
}

.top-pick-card h3 {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}

.top-pick-ticker {
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.entry-highlight {
  margin: 0.5rem 0;
  padding: 0.5rem 0.65rem;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.35);
  border-radius: 8px;
  font-size: 0.95rem;
}

.trade-math-panel {
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.trade-math-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.65rem;
}

.trade-math-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

@media (max-width: 800px) {
  .trade-math-grid {
    grid-template-columns: 1fr;
  }
}

.trade-math-box {
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
}

.trade-math-box.buy {
  border-color: rgba(59, 130, 246, 0.45);
}

.trade-math-box.stop {
  border-color: rgba(239, 68, 68, 0.4);
}

.trade-math-box.sell {
  border-color: rgba(34, 197, 94, 0.45);
}

.trade-math-label {
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.25rem;
}

.trade-math-value {
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.2;
}

.trade-math-sub {
  font-size: 0.78rem;
  color: var(--muted);
  margin-top: 0.25rem;
}

.second-pick-block {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--border);
}

.second-pick-block h3 {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: var(--muted);
}

.planned-trade-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  align-items: flex-end;
  margin-bottom: 0.5rem;
}

.planned-trade-form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--muted);
}

.planned-trade-form input {
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  min-width: 100px;
}

.planned-trade-result {
  margin-top: 0.5rem;
}

.validate-verdict {
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.validate-verdict.go { background: rgba(34, 197, 94, 0.15); color: var(--green); }
.validate-verdict.caution { background: rgba(245, 158, 11, 0.15); color: #fcd34d; }
.validate-verdict.no_go { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }

.check-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.check-list li {
  padding: 0.35rem 0;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--border);
}

.check-list li:last-child {
  border-bottom: none;
}

.check-icon {
  display: inline-block;
  width: 1.1rem;
}

.check-ok { color: var(--green); }
.check-bad { color: var(--red); }
.check-wait { color: #93c5fd; }

.grid-4 {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.grid-2 {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.card-daily-target .progress-fill.daily-fill {
  background: linear-gradient(90deg, var(--green), #16a34a);
}

.strategy-rules {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--text);
}

.growth-table td,
.growth-table th {
  text-align: left;
  padding: 0.45rem 0.5rem;
}

.growth-table tr.growth-active {
  background: rgba(34, 197, 94, 0.08);
}

.growth-table tr.growth-active td:last-child {
  color: var(--green);
  font-weight: 600;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.15rem;
}

.card h2 {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
  font-weight: 600;
}

.metric {
  font-size: 1.5rem;
  font-weight: 700;
}

.metric.small {
  font-size: 1.1rem;
}

.metric.positive {
  color: var(--green);
}

.metric.negative {
  color: var(--red);
}

.progress-wrap {
  margin-top: 0.75rem;
}

.progress-bar {
  height: 8px;
  background: var(--surface2);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #6366f1);
  border-radius: 999px;
  transition: width 0.4s ease;
}

.progress-label {
  font-size: 0.8rem;
  color: var(--muted);
  margin-top: 0.35rem;
}

section {
  margin-top: 1.5rem;
}

section > h2 {
  font-size: 1rem;
  margin: 0 0 0.75rem;
  font-weight: 600;
}

.brief {
  font-size: 0.95rem;
  color: var(--muted);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

th,
td {
  text-align: left;
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--border);
}

th {
  color: var(--muted);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
}

tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  background: var(--surface2);
  color: var(--muted);
}

.badge.in_trade,
.badge.alert {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.badge.alert-target_hit,
.badge.alert-near_target {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.badge.alert-stop_hit,
.badge.alert-near_stop {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}

.badge.alert-eod_flatten {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
}

.badge.approved,
.badge.armed {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
}

.btn {
  appearance: none;
  border: none;
  border-radius: 6px;
  padding: 0.45rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--accent);
  color: white;
}

.btn:hover {
  background: var(--accent-hover);
}

.btn.secondary {
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn.secondary:hover {
  background: var(--border);
}

.btn-sm {
  padding: 0.25rem 0.55rem;
  font-size: 0.72rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

label {
  display: block;
  font-size: 0.72rem;
  color: var(--muted);
  margin-bottom: 0.25rem;
}

input,
select,
textarea {
  width: 100%;
  padding: 0.45rem 0.55rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 0.875rem;
}

.thesis {
  font-size: 0.8rem;
  color: var(--muted);
  max-width: 420px;
}

.empty {
  color: var(--muted);
  font-size: 0.875rem;
  padding: 1rem 0;
}

.toast {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.2s, transform 0.2s;
  pointer-events: none;
  z-index: 100;
}

.toast.show {
  opacity: 1;
  transform: translateY(0);
}

.learning-grid {
  display: grid;
  gap: 1rem;
  margin-top: 0.75rem;
}

.learning-block h3 {
  margin: 0 0 0.35rem;
  font-size: 0.85rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.learning-block ul {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.875rem;
  color: var(--muted);
}

.cio-headline {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.cio-actions {
  margin: 0.5rem 0 0;
  padding-left: 1.1rem;
  color: var(--muted);
  font-size: 0.9rem;
}

.cio-actions li {
  margin-bottom: 0.25rem;
}

.cio-panel {
  border-color: rgba(59, 130, 246, 0.35);
}

.scenario-chart-wrap {
  margin-top: 1rem;
  background: var(--bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 0.5rem;
}

#scenario-chart {
  width: 100%;
  height: auto;
  display: block;
}

.scenario-legend {
  display: flex;
  gap: 1.25rem;
  margin-top: 0.65rem;
  font-size: 0.8rem;
  color: var(--muted);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.swatch {
  width: 14px;
  height: 3px;
  border-radius: 2px;
  display: inline-block;
}

.swatch.actual { background: #22c55e; }
.swatch.pace { background: #3b82f6; }
.swatch.strategy { background: #f59e0b; }

.scenario-stats .metric {
  font-size: 1rem;
}

/* ── App shell (UI refresh) ── */
.app-header {
  padding: 0.85rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.app-header-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  max-width: 1280px;
  margin: 0 auto;
}

.app-brand h1 {
  margin: 0;
  font-size: 1.2rem;
}

.ui-version {
  display: inline-block;
  margin-left: 0.35rem;
  padding: 0.12rem 0.45rem;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  vertical-align: middle;
  color: #93c5fd;
  background: rgba(59, 130, 246, 0.18);
  border: 1px solid rgba(59, 130, 246, 0.45);
  border-radius: 999px;
}

.app-header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.app-banner-compact {
  max-width: 1280px;
  margin: 0.5rem auto 0;
  padding: 0.45rem 1rem;
  font-size: 0.82rem;
  border-radius: 8px;
}

.status-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-width: 1280px;
  margin: 0.75rem auto 0;
  padding: 0 1.5rem;
}

.status-chip {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.4rem 0.75rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  min-width: 5.5rem;
}

.status-chip-accent {
  border-color: rgba(59, 130, 246, 0.45);
  background: rgba(59, 130, 246, 0.08);
}

.status-chip.status-go { border-color: rgba(34, 197, 94, 0.5); }
.status-chip.status-nogo { border-color: rgba(239, 68, 68, 0.5); }

.status-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}

.app-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.65rem 1.5rem;
  background: var(--surface);
  border-bottom: 2px solid var(--border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.app-nav-btn {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--surface2);
  color: var(--text);
  padding: 0.55rem 1rem;
  border-radius: 999px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.nav-icon {
  opacity: 0.75;
  font-size: 0.85em;
}

.app-nav-btn:hover {
  color: var(--text);
  background: var(--bg);
  border-color: rgba(59, 130, 246, 0.45);
}

.app-nav-btn.active {
  color: #fff;
  background: var(--accent);
  border-color: var(--accent);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
}

.app-nav-btn.active .nav-icon {
  opacity: 1;
}

.app-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1rem 1.5rem 3rem;
}

.app-view {
  display: none;
  animation: viewIn 0.2s ease;
}

.app-view.active {
  display: block;
}

@keyframes viewIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.view-section {
  margin-bottom: 1.75rem;
}

.view-head h2 {
  margin: 0 0 0.25rem;
  font-size: 1.05rem;
}

.view-head p {
  margin: 0 0 0.65rem;
}

.actions-wrap {
  flex-wrap: wrap;
}

.screener-actions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 0.85rem;
  margin-bottom: 0.85rem;
}

.screener-action-item {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.25rem;
  min-width: 7.5rem;
}

.screener-action-item .btn {
  width: 100%;
}

.screener-action-ts {
  font-size: 0.72rem;
  line-height: 1.3;
  color: var(--muted);
  text-align: center;
  min-height: 1.25rem;
}

.screener-action-ts .ts-label {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.62rem;
  color: var(--accent);
  margin-right: 0.15rem;
}

.screener-workflow {
  margin-bottom: 0.85rem;
  padding: 0.65rem 0.85rem;
}

.screener-workflow-summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
}

.screener-workflow-body p {
  margin: 0.35rem 0;
  font-size: 0.84rem;
  line-height: 1.45;
}

.screener-workflow-note {
  margin-top: 0.5rem !important;
  color: var(--accent);
  font-size: 0.8rem !important;
}

.screener-action-ts.inferred {
  font-style: italic;
}

.screener-action-ts.empty {
  opacity: 0.65;
}

.table-card {
  padding: 0;
  overflow-x: auto;
}

/* ── Trade view ── */
.trade-page-head {
  margin-bottom: 0.75rem;
}

.trade-page-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.pick-why {
  margin: 0.65rem 0;
  padding: 0.6rem 0.75rem;
  background: var(--surface2);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.pick-why-label {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  margin-bottom: 0.25rem;
}

.pick-why p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.45;
  color: var(--text);
}

.trade-verdict-row {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.picks-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1rem 0;
}

.pick-empty {
  padding: 1.25rem 0.75rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.88rem;
  line-height: 1.45;
  border: 1px dashed var(--border);
  border-radius: 8px;
  background: rgba(15, 20, 25, 0.35);
}

@media (max-width: 900px) {
  .picks-grid {
    grid-template-columns: 1fr;
  }
}

.pick-card {
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--surface);
  overflow: hidden;
}

.pick-card-primary {
  border-color: rgba(59, 130, 246, 0.45);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.12);
}

.pick-card-secondary {
  border-color: rgba(148, 163, 184, 0.35);
}

.pick-card-head {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 0.85rem 1rem;
  background: var(--surface2);
  border-bottom: 1px solid var(--border);
}

.pick-num {
  flex: 0 0 auto;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-weight: 800;
  font-size: 1rem;
}

.pick-num-alt {
  background: var(--surface);
  color: var(--muted);
  border: 1px solid var(--border);
}

.pick-title {
  margin: 0;
  font-size: 1rem;
}

.pick-sub {
  margin: 0.15rem 0 0;
  font-size: 0.8rem;
}

.pick-card-body {
  padding: 1rem;
  font-size: 0.9rem;
}

.pick-symbol-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}

.pick-symbol {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.pick-stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin: 0.75rem 0;
}

.pick-stat {
  padding: 0.45rem 0.55rem;
  background: var(--bg);
  border-radius: 6px;
  border: 1px solid var(--border);
  font-size: 0.82rem;
}

.pick-stat-label {
  display: block;
  font-size: 0.68rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.pick-forecast {
  padding: 0.55rem 0.65rem;
  margin-bottom: 0.65rem;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 6px;
  border-left: 3px solid var(--accent);
  font-size: 0.85rem;
}

.pick-prices-head {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--green);
  margin-bottom: 0.35rem;
}

.pick-prices {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.pick-price-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid rgba(45, 58, 79, 0.5);
}

.pick-price-row.highlight {
  font-size: 1.05rem;
}

.pick-price-row.highlight .pick-price {
  font-size: 1.35rem;
  color: var(--green);
}

.pick-price-row.target strong:last-of-type {
  color: var(--green);
}

.pick-price-row.stop strong {
  color: #fca5a5;
}

.pick-change.up { color: var(--green); }
.pick-change.down { color: #fca5a5; }

.pick-note.warn {
  padding: 0.4rem 0.55rem;
  margin-bottom: 0.5rem;
  background: rgba(245, 158, 11, 0.12);
  border-radius: 6px;
  font-size: 0.82rem;
  color: #fcd34d;
}

.pick-tradability-detail {
  font-size: 0.85rem;
  color: var(--muted);
  margin-bottom: 0.5rem;
}

.validate-panel {
  margin-top: 1rem;
}

.panel-head h2 {
  margin: 0 0 0.25rem;
  font-size: 1.05rem;
}

.planned-trade-form-hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  align-items: end;
  margin-top: 0.75rem;
}

.plan-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.82rem;
  color: var(--muted);
}

.plan-field input {
  padding: 0.5rem 0.6rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 1rem;
}

.plan-submit {
  min-height: 2.65rem;
}

.planned-trade-result {
  margin-top: 0.75rem;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  background: var(--bg);
  border: 1px solid var(--border);
}

.checks-panel {
  margin-top: 1rem;
}

.checks-summary {
  cursor: pointer;
  font-weight: 600;
  padding: 0.25rem 0;
}

.checks-summary::-webkit-details-marker {
  color: var(--accent);
}

.kpi-grid {
  margin-bottom: 1rem;
}

.kpi-card h2 {
  font-size: 0.85rem;
  color: var(--muted);
}

.setup-hints code {
  font-size: 0.85rem;
}

@media (max-width: 640px) {
  main, .app-main {
    padding: 1rem;
  }

  .app-nav, .status-bar {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .pick-stats-row {
    grid-template-columns: 1fr;
  }
}
```


---

<a id="src-investment_agent-dashboard-templates-dashboard-html"></a>
## `src/investment_agent/dashboard/templates/dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Investment Agent</title>
  <link rel="stylesheet" href="/static/style.css?v=20260812a" />
</head>
<body>
  <header class="app-header">
    <div class="app-header-inner">
      <div class="app-brand">
        <h1>AI Investment Agent <span class="ui-version">UI v2</span></h1>
        <p class="subtitle">E*TRADE manual · Growth Plan · $5M goal</p>
      </div>
      <div class="app-header-actions">
        <button class="btn btn-sm" type="button" id="refresh-trading-day" title="Step 3 — refresh live prices before you buy">Refresh live before buy</button>
        <button class="btn secondary btn-sm" type="button" id="pin-top-pick">Pin #1</button>
        <button class="btn secondary btn-sm" type="button" id="refresh-all">Refresh all</button>
      </div>
    </div>
    {% if api_key_required %}
    <div class="api-key-bar" id="api-key-bar">
      <label for="app-api-key">Dashboard password</label>
      <input type="password" id="app-api-key" placeholder="APP_API_KEY from .env" autocomplete="off" />
      <button class="btn secondary btn-sm" type="button" id="save-api-key">Save</button>
      <button class="btn secondary btn-sm" type="button" id="clear-api-key">Clear</button>
      <span class="brief" id="api-key-status"></span>
    </div>
    {% endif %}
  </header>

  <div id="trading-mode-banner" class="banner paper app-banner-compact">Loading trading mode…</div>
  <div id="regime-banner" class="banner ok app-banner-compact">Loading regime…</div>

  <div class="status-bar" id="status-bar">
    <div class="status-chip" id="status-verdict-chip"><span class="status-label">Session</span><span id="status-verdict-text">—</span></div>
    <div class="status-chip status-chip-accent"><span class="status-label">Today</span><span id="status-daily-text">—</span></div>
    <div class="status-chip"><span class="status-label">Cash</span><span id="status-cash-text">—</span></div>
    <div class="status-chip"><span class="status-label">Goal</span><span id="status-goal-text">—</span></div>
  </div>

  <nav class="app-nav" aria-label="Dashboard views">
    <button type="button" class="app-nav-btn active" data-view="trade"><span class="nav-icon">◎</span> Trade</button>
    <button type="button" class="app-nav-btn" data-view="screen"><span class="nav-icon">▦</span> Screen</button>
    <button type="button" class="app-nav-btn" data-view="review"><span class="nav-icon">▤</span> Review</button>
    <button type="button" class="app-nav-btn" data-view="account"><span class="nav-icon">◫</span> Account</button>
    <button type="button" class="app-nav-btn" data-view="setup"><span class="nav-icon">⚙</span> Setup</button>
  </nav>

  <main class="app-main">

    <!-- ═══ TRADE — primary view ═══ -->
    <div id="view-trade" class="app-view active">

      <header class="trade-page-head">
        <h2 class="trade-page-title">What to trade today</h2>
        <p class="brief">Three steps each day — metrics after close, picks before open, live check before you buy.</p>
      </header>

      <section class="daily-rhythm card" id="daily-rhythm-panel">
        <h2 class="daily-rhythm-title">Daily rhythm</h2>
        <ol class="rhythm-steps" id="rhythm-steps"></ol>
      </section>

      <section class="card" id="candidates-panel">
        <header class="panel-head">
          <h2>Today&apos;s candidates</h2>
          <p class="brief">After Step 2 — buy size, sell target, and stop per symbol (Growth Plan).</p>
        </header>
        <div class="table-wrap">
          <table class="data-table" id="candidates-table">
            <thead><tr>
              <th>#</th><th>Ticker</th><th>Hit%</th><th>Limit buy</th><th>Shares</th><th>Size</th>
              <th>Limit sell</th><th>Stop</th><th>Live S3</th>
            </tr></thead>
            <tbody id="candidates-body"><tr><td colspan="9" class="empty">Run Step 2 to populate.</td></tr></tbody>
          </table>
        </div>
      </section>

      <div class="card trading-day-panel verdict-neutral" id="trading-day-panel">
        <div class="trade-verdict-row">
          <div class="verdict-badge" id="verdict-badge">—</div>
          <div class="trade-verdict-copy">
            <div class="verdict-headline" id="verdict-headline">Loading…</div>
            <div class="brief" id="verdict-detail"></div>
            <div class="brief" id="verdict-asof"></div>
          </div>
        </div>
      </div>

      <div class="picks-grid">
        <article class="pick-card pick-card-primary">
          <header class="pick-card-head">
            <span class="pick-num">1</span>
            <div>
              <h2 class="pick-title">Top pick — buy this first</h2>
              <p class="pick-sub brief">Limit buy in the expected pullback · TRADABLE for today&apos;s $ goal only</p>
            </div>
          </header>
          <div class="pick-card-body" id="top-pick-body">Loading…</div>
        </article>

        <article class="pick-card pick-card-secondary" id="second-pick-block">
          <header class="pick-card-head">
            <span class="pick-num pick-num-alt">2</span>
            <div>
              <h2 class="pick-title">Backup pick</h2>
              <p class="pick-sub brief">If #1 fails or for optional 2nd trade after a win</p>
            </div>
          </header>
          <div class="pick-card-body" id="second-pick-body"><div class="pick-empty">Loading backup pick…</div></div>
        </article>
      </div>

      <div class="trade-math-panel card" id="trade-math-panel" hidden>
        <div class="trade-math-title">Trade math <span class="brief" id="trade-math-goal"></span></div>
        <div class="trade-math-grid">
          <div class="trade-math-box buy">
            <div class="trade-math-label">Limit buy</div>
            <div class="trade-math-value" id="math-buy">—</div>
            <div class="trade-math-sub" id="math-shares">—</div>
            <div class="trade-math-sub" id="math-limit-note">—</div>
          </div>
          <div class="trade-math-box stop">
            <div class="trade-math-label">Stop (−0.75%)</div>
            <div class="trade-math-value" id="math-stop">—</div>
            <div class="trade-math-sub" id="math-stop-net">—</div>
          </div>
          <div class="trade-math-box sell">
            <div class="trade-math-label">Sell for goal</div>
            <div class="trade-math-value" id="math-sell">—</div>
            <div class="trade-math-sub" id="math-sell-net">—</div>
          </div>
        </div>
      </div>

      <section class="validate-panel card rhythm-step3-panel">
        <header class="panel-head">
          <h2>Step 3 — Confirm before you buy</h2>
          <p class="brief">Click <strong>Refresh live before buy</strong> above, then place the <strong>limit buy</strong> in E*TRADE (not market).</p>
        </header>
        <form id="planned-trade-form" class="planned-trade-form planned-trade-form-hero">
          <label class="plan-field"><span>Ticker</span><input type="text" id="plan-ticker" placeholder="NFLX" /></label>
          <label class="plan-field"><span>Limit buy ($)</span><input type="number" id="plan-price" step="0.01" min="0.01" placeholder="Pullback limit" /></label>
          <label class="plan-field"><span>Shares</span><input type="number" id="plan-shares" step="1" min="1" placeholder="Auto" /></label>
          <button class="btn plan-submit" type="submit">Validate trade</button>
        </form>
        <div id="planned-trade-result" class="planned-trade-result"></div>
      </section>

      <details class="checks-panel card">
        <summary class="checks-summary">Go / no-go checks &amp; rotation hints</summary>
        <ul class="check-list" id="trading-checks"></ul>
        <p class="brief rotation-hint" id="rotation-hint"></p>
      </details>
    </div>

    <!-- ═══ SCREEN ═══ -->
    <div id="view-screen" class="app-view">
      <section class="view-section">
        <header class="view-head"><h2>Trade queue</h2><p class="brief">Active names you are working — sync adds live Step 3 passers.</p></header>
        <div class="actions">
          <button class="btn" id="sync-queue">Sync from screener</button>
        </div>
        <div class="card table-card">
          <table>
            <thead><tr>
              <th>Ticker</th><th>State</th><th>Live</th><th>P&amp;L</th><th>Entry</th>
              <th>Target</th><th>Stop</th><th>Size</th><th>Thesis</th><th></th>
            </tr></thead>
            <tbody id="queue-body"><tr><td colspan="10" class="empty">Loading…</td></tr></tbody>
          </table>
        </div>
      </section>

      <section class="view-section">
        <header class="view-head"><h2>Intraday alerts</h2></header>
        <div class="actions">
          <button class="btn" id="run-monitor">Run monitor</button>
          <button class="btn secondary" id="refresh-alerts">Refresh alerts</button>
        </div>
        <div class="card table-card">
          <table>
            <thead><tr>
              <th>Time</th><th>Ticker</th><th>Alert</th><th>Price</th><th>P&amp;L</th><th>Message</th><th></th>
            </tr></thead>
            <tbody id="alerts-body"><tr><td colspan="7" class="empty">Loading…</td></tr></tbody>
          </table>
        </div>
      </section>

      <section class="view-section">
        <header class="view-head">
          <h2>Ranked universe</h2>
          <p class="brief">Ranked by $-goal history (≥40% hit rate, avg net ≥90% of today's goal) · use <strong>Trade</strong> tab for Step 2 picks</p>
        </header>
        <div class="card rhythm-screen-note brief" id="rhythm-screen-note">Loading daily rhythm…</div>
        <details class="screener-workflow card">
          <summary class="screener-workflow-summary">Advanced — load watchlists &amp; one-time setup</summary>
          <div class="screener-workflow-body brief">
            <div class="screener-actions-grid screener-actions-compact">
              <div class="screener-action-item" data-action="sp500">
                <button class="btn secondary btn-sm" id="load-sp500">Load S&amp;P 500</button>
              </div>
              <div class="screener-action-item" data-action="datacenter_us">
                <button class="btn secondary btn-sm" id="load-datacenter-us">DC US watch</button>
              </div>
              <div class="screener-action-item" data-action="refresh_ranked">
                <button class="btn secondary btn-sm" id="refresh-ranked">Reload table</button>
              </div>
            </div>
            <p class="screener-workflow-note">First time: Setup tab → Enable Auto Refresh · Load S&amp;P 500 once.</p>
          </div>
        </details>
        <div class="card">
          <div id="watchlist-stats" class="brief">Loading…</div>
          <div class="screener-filters">
            <label>Ticker <input type="text" id="screener-filter-ticker" placeholder="Filter…" /></label>
            <label>Min hit % <input type="number" id="screener-min-hit" min="0" max="100" style="width:70px" /></label>
            <label>Min days <input type="number" id="screener-min-days" min="0" max="30" style="width:70px" /></label>
            <label class="inline-check"><input type="checkbox" id="screener-live-only" /> Live only</label>
            <label>Period <select id="screener-period-days">
              <option value="7">7 trading days</option><option value="14" selected>14 trading days</option><option value="30">30 trading days</option>
            </select></label>
            <span id="screener-row-count" class="brief"></span>
          </div>
          <div class="table-wrap">
            <table class="sortable-table" id="ranked-screener-table">
              <thead><tr>
                <th data-sort="score" class="sortable sorted-desc">Score</th>
                <th data-sort="ticker" class="sortable">Ticker</th>
                <th data-sort="avg_range_pct" class="sortable">Range</th>
                <th data-sort="adv_dollar_m" class="sortable">ADV</th>
                <th data-sort="dollar_hit_rate_pct" class="sortable" title="Historical % of Step 3 days hitting today's net goal">$ Hit%</th>
                <th data-sort="avg_net_at_high" class="sortable" title="Average net at day high on Step 3 days">Avg $</th>
                <th data-sort="days_screened" class="sortable" title="Step 3 hits out of selected trading days (excludes weekends and market holidays)">Days</th>
                <th data-sort="simulated_targets" class="sortable" title="Target hits on Step 3 days in the period">Tgt</th>
                <th data-sort="simulated_stops" class="sortable" title="Stop hits on Step 3 days in the period">Stp</th>
                <th data-sort="hit_rate_pct" class="sortable">Hit%</th>
                <th data-sort="live_pass_today" class="sortable">Live</th><th></th>
              </tr></thead>
              <tbody id="period-screener-body"><tr><td colspan="12" class="empty">Run screener after ingest.</td></tr></tbody>
            </table>
          </div>
          <div class="card special-watch-panel" id="special-watch-panel">
            <h3>Special Watch — US AI Data Centers</h3>
            <div id="special-watch-stats" class="brief">Loading…</div>
            <div class="special-watch-add">
              <label>Add ticker
                <input type="text" id="special-watch-add-ticker" placeholder="e.g. NBIS" maxlength="6" autocapitalize="characters" />
              </label>
              <button type="button" class="btn btn-sm secondary" id="special-watch-add-btn">Add to Special Watch</button>
              <span class="brief special-watch-add-hint">Added tickers join the active watchlist; Range/ADV fill in after Daily ingest.</span>
            </div>
            <div class="screener-filters">
              <label>Ticker <input type="text" id="special-watch-filter-ticker" placeholder="Filter…" /></label>
              <label>Step 3 <select id="special-watch-filter-status">
                <option value="">All</option>
                <option value="step3_pass">Pass</option>
                <option value="too_quiet">Too quiet</option>
                <option value="too_wild">Too wild</option>
                <option value="low_liquidity">Low liq</option>
                <option value="missing_metrics">Missing</option>
              </select></label>
              <label class="inline-check"><input type="checkbox" id="special-watch-active-only" /> Active only</label>
              <span id="special-watch-row-count" class="brief"></span>
            </div>
            <div class="table-wrap">
              <table class="sortable-table special-watch-table">
                <thead><tr>
                  <th data-sort="ticker" class="sortable sorted-asc">Ticker</th>
                  <th data-sort="step3_status" class="sortable">Step 3</th>
                  <th data-sort="avg_range_pct" class="sortable">Range</th>
                  <th data-sort="adv_dollar_m" class="sortable">ADV</th>
                  <th data-sort="in_active_watchlist" class="sortable">List</th>
                </tr></thead>
                <tbody id="special-watch-body"><tr><td colspan="5" class="empty">Loading…</td></tr></tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- ═══ REVIEW ═══ -->
    <div id="view-review" class="app-view">
      <section class="view-section">
        <header class="view-head"><h2>Daily &amp; weekly close</h2><p class="brief">Which ranked names would have hit the Growth Plan goal?</p></header>
        <div class="actions">
          <label for="close-date" class="brief">Date</label>
          <input type="date" id="close-date" />
          <button class="btn" id="load-daily-close">Daily close</button>
          <button class="btn secondary" id="load-weekly-close">Weekly</button>
          <button class="btn secondary" id="refresh-close">Refresh</button>
        </div>
        <div class="card" id="close-panel">
          <div id="close-highlights" class="brief">Load a daily close report.</div>
          <div id="close-summary"></div>
          <div class="close-tab-bar">
            <button type="button" class="btn btn-sm close-tab active" data-tab="step3_pass">Step 3</button>
            <button type="button" class="btn btn-sm secondary close-tab" data-tab="full_top20">Top 20</button>
          </div>
          <div class="table-wrap">
            <table class="data-table" id="close-table">
              <thead><tr><th>#</th><th>Ticker</th><th>Open→net</th><th>10:00→net</th><th>Hit?</th><th>S3</th></tr></thead>
              <tbody id="close-table-body"></tbody>
            </table>
          </div>
          <div id="close-journal" class="brief" style="margin-top:1rem"></div>
        </div>
      </section>

      <section class="view-section">
        <header class="view-head"><h2>Learning report</h2></header>
        <div class="actions">
          <label for="learning-date" class="brief">Date</label>
          <input type="date" id="learning-date" />
          <button class="btn" id="generate-learning">Generate</button>
        </div>
        <div class="card" id="learning-panel">
          <div id="learning-highlights" class="brief">Loading…</div>
          <div id="continual-learning" class="brief"></div>
          <div id="learning-prior-screened" class="learning-prior-block" hidden>
            <h3>Prior day screened <span id="learning-prior-date" class="brief"></span></h3>
            <p class="brief" id="learning-prior-summary"></p>
            <div class="prior-screened-toolbar">
              <input type="search" id="learning-prior-search" placeholder="Search ticker…" />
              <select id="learning-prior-outcome">
                <option value="">All outcomes</option>
                <option value="target">Target</option>
                <option value="stop">Stop</option>
                <option value="neither">No exit</option>
              </select>
              <span id="learning-prior-count" class="brief"></span>
            </div>
            <div class="table-wrap">
              <table class="sortable-table prior-screened-table learning-prior-table">
                <thead><tr>
                  <th data-sort="ticker" class="sortable sorted-asc">Ticker</th>
                  <th data-sort="predicted_avg_range_pct" class="sortable">Typical</th>
                  <th data-sort="actual_range_pct" class="sortable">Actual</th>
                  <th data-sort="range_delta_pct" class="sortable">Δ</th>
                  <th data-sort="simulated_outcome" class="sortable">+1.5%</th>
                  <th data-sort="dollar_outcome" class="sortable">$ goal</th>
                </tr></thead>
                <tbody id="learning-prior-table"></tbody>
              </table>
            </div>
          </div>
          <div class="learning-grid" id="learning-details"></div>
        </div>
      </section>

      <section class="view-section">
        <header class="view-head"><h2>Historical — prior day</h2></header>
        <div class="actions">
          <button class="btn secondary" id="pull-historical">Pull 60d history</button>
          <button class="btn secondary" id="refresh-historical">Refresh</button>
        </div>
        <div class="card" id="historical-panel">
          <div id="historical-summary" class="brief">Loading…</div>
          <div class="grid grid-4" id="historical-stats"></div>
          <div id="prior-day-eval" class="prior-screened-summary brief"></div>
          <div class="prior-screened-toolbar">
            <input type="search" id="historical-prior-search" placeholder="Search ticker…" />
            <select id="historical-prior-outcome">
              <option value="">All outcomes</option>
              <option value="target">Target</option>
              <option value="stop">Stop</option>
              <option value="neither">No exit</option>
            </select>
            <span id="historical-prior-count" class="brief"></span>
          </div>
          <div class="table-wrap">
            <table class="sortable-table prior-screened-table" id="prior-day-table-wrap">
              <thead><tr>
                <th data-sort="ticker" class="sortable sorted-asc">Ticker</th>
                <th data-sort="predicted_avg_range_pct" class="sortable">Typical</th>
                <th data-sort="actual_range_pct" class="sortable">Actual</th>
                <th data-sort="range_delta_pct" class="sortable">Δ</th>
                <th data-sort="simulated_outcome" class="sortable">+1.5%</th>
                <th data-sort="dollar_outcome" class="sortable">$ goal</th>
              </tr></thead>
              <tbody id="prior-day-table"></tbody>
            </table>
          </div>
        </div>
      </section>

      <section class="view-section">
        <header class="view-head"><h2>CIO summary</h2></header>
        <div class="card cio-panel" id="cio-panel">
          <div class="cio-headline" id="cio-headline">Loading…</div>
          <p class="brief" id="cio-narrative"></p>
          <ul id="cio-actions" class="cio-actions"></ul>
          <div class="grid grid-4" id="cio-subagents"></div>
        </div>
      </section>

      <section class="view-section">
        <header class="view-head"><h2>Market brief</h2></header>
        <div class="card brief" id="market-brief">Loading…</div>
      </section>
    </div>

    <!-- ═══ ACCOUNT ═══ -->
    <div id="view-account" class="app-view">
      <div class="grid grid-4 kpi-grid">
        <div class="card kpi-card"><h2>$5M goal</h2><div class="metric" id="goal-pct">—</div>
          <div class="progress-wrap"><div class="progress-bar"><div class="progress-fill" id="goal-bar"></div></div>
          <div class="progress-label" id="goal-label">—</div></div></div>
        <div class="card kpi-card card-daily-target"><h2>Daily target</h2><div class="metric" id="daily-target">—</div>
          <div class="progress-wrap"><div class="progress-bar"><div class="progress-fill daily-fill" id="daily-bar"></div></div>
          <div class="progress-label" id="daily-progress-label">—</div></div>
          <div class="progress-label brief" id="next-tier-label">—</div></div>
        <div class="card kpi-card"><h2>Tradable cash</h2><div class="metric" id="tradable-cash">—</div>
          <div class="progress-label brief">Basis <span id="original-basis">—</span></div></div>
        <div class="card kpi-card"><h2>Month P&amp;L</h2><div class="metric" id="month-pnl">—</div>
          <div class="progress-label brief"><span id="month-key">—</span> · fees <span id="total-fees">—</span></div></div>
      </div>
      <div class="grid grid-2">
        <div class="card"><h2>Jars</h2><div class="metric small">Mgmt <span id="mgmt-jar">—</span></div>
          <div class="metric small">Tax <span id="tax-jar">—</span></div></div>
        <div class="card"><h2>Operating rules</h2><div class="strategy-rules brief" id="strategy-rules">Loading…</div></div>
      </div>
      <section class="view-section">
        <header class="view-head"><h2>Growth plan tiers</h2></header>
        <div class="card">
          <div id="growth-tier-summary" class="brief">Loading…</div>
          <table class="growth-table"><thead><tr><th>Balance</th><th>Daily target</th><th>Status</th></tr></thead>
          <tbody id="growth-plan-body"><tr><td colspan="3" class="empty">Loading…</td></tr></tbody></table>
        </div>
      </section>
      <section class="view-section">
        <header class="view-head"><h2>$5M scenario</h2></header>
        <div class="card" id="scenario-panel">
          <div id="scenario-summary" class="brief"></div>
          <div class="scenario-stats grid grid-4" id="scenario-stats"></div>
          <div class="scenario-chart-wrap"><svg id="scenario-chart" viewBox="0 0 800 220"></svg></div>
          <div class="scenario-legend" id="scenario-legend"></div>
          <div class="table-wrap"><table><thead><tr><th>Month</th><th>Tradable</th><th>Goal%</th><th>P&amp;L</th><th>Sweep</th></tr></thead>
          <tbody id="scenario-table"></tbody></table></div>
        </div>
      </section>
      <section class="view-section">
        <header class="view-head"><h2>Trade journal</h2></header>
        <div class="card journal-toolbar">
          <div class="journal-mode-row">
            <label for="trading-mode">Mode</label>
            <select id="trading-mode"><option value="paper">PAPER</option><option value="live">LIVE</option></select>
            <button class="btn secondary btn-sm" type="button" id="save-trading-mode">Save</button>
            <span class="brief" id="trading-mode-status"></span>
          </div>
          <button class="btn secondary btn-sm" type="button" id="clear-journal">Clear journal</button>
        </div>
        <div class="card">
          <form id="trade-form"><div class="form-row">
            <div><label for="t-ticker">Ticker</label><input id="t-ticker" required /></div>
            <div><label for="t-side">Side</label><select id="t-side"><option value="BUY">BUY</option><option value="SELL">SELL</option></select></div>
            <div><label for="t-shares">Shares</label><input id="t-shares" type="number" step="any" min="0.0001" required /></div>
            <div><label for="t-price">Price</label><input id="t-price" type="number" step="any" min="0.01" required /></div>
            <div><label for="t-fee">Fee</label><input id="t-fee" type="number" step="0.01" min="0" placeholder="7" /></div>
            <div><label for="t-date">Date (PT)</label><input id="t-date" type="date" required /></div>
            <div><label for="t-time" id="t-time-label">Time (PT)</label><input id="t-time" type="time" step="1" required /></div>
            <div><label for="t-notes">Notes</label><input id="t-notes" placeholder="E*TRADE fill" /></div>
          </div><button class="btn" type="submit">Log trade</button></form>
        </div>
        <div class="card table-card"><table><thead><tr>
          <th>Date</th><th>Time</th><th>Ticker</th><th>Side</th><th>Shares</th><th>Price</th><th>Fee</th><th>Notes</th>
        </tr></thead><tbody id="journal-body"><tr><td colspan="8" class="empty">Loading…</td></tr></tbody></table></div>
      </section>
      <section class="view-section">
        <header class="view-head"><h2>Month-end sweep</h2></header>
        <div class="card">
          <div id="sweep-preview">Loading…</div>
          <div class="actions" style="margin-top:0.75rem">
            <label>Tax rate <input type="number" id="tax-rate" min="0" max="100" style="width:70px" />%</label>
            <button class="btn secondary btn-sm" id="save-tax">Save</button>
            <button class="btn btn-sm" id="apply-sweep">Apply sweep</button>
          </div>
        </div>
      </section>
    </div>

    <!-- ═══ SETUP ═══ -->
    <div id="view-setup" class="app-view">
      <section class="view-section">
        <header class="view-head"><h2>Setup</h2><p class="brief">One-time — then the daily rhythm runs automatically.</p></header>
        <div class="card setup-onboarding">
          <h3>1. Enable automatic data refresh (recommended)</h3>
          <p class="brief">Updates metrics after close (4:30 PM) and before open (6:30 AM).</p>
          <p>In Finder, open <code>Home-Repository/scripts/</code> and double-click <strong>Enable Auto Refresh.command</strong>.</p>
          <p class="brief">If double-click does not launch, paste in Terminal:</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
./scripts/install_ingest_schedule_mac.sh</pre>
          <p class="brief" id="setup-schedule-status">Checking schedule…</p>

          <h3 style="margin-top:1.25rem">2. Load your stock universe (once)</h3>
          <p class="brief">Screen tab → Advanced → <strong>Load S&amp;P 500</strong>, or run in Terminal:</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
PYTHONPATH=src python3 scripts/manage_watchlist.py load-preset sp500</pre>
          <p class="brief">Smaller list (SP100): <code>load-preset sp100</code> · Special Watch: <code>load-preset datacenter_us</code></p>

          <h3 style="margin-top:1.25rem">3. Daily workflow (recommended)</h3>
          <p class="brief">In Finder, open <code>Home-Repository/scripts/</code> and double-click:</p>
          <ul class="setup-workflow-list brief">
            <li><strong>Run End of Day.command</strong> — after close: ingest + screener + close report</li>
            <li><strong>Run Morning Prep.command</strong> — before open: screener + today&apos;s candidates</li>
            <li><strong>Run Refresh Live.command</strong> — right before you buy or sell (limit orders)</li>
          </ul>
          <p class="brief">Or paste in Terminal (replace <code>~/Home-Repository</code> with your clone path):</p>

          <p class="setup-terminal-label"><strong>End of day</strong> — ingest + screener + close report (~15–30 min)</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
./scripts/run_end_of_day_mac.sh</pre>

          <p class="setup-terminal-label"><strong>Morning precheck</strong> — candidates for Trade tab</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
./scripts/run_morning_prep_mac.sh</pre>

          <p class="setup-terminal-label"><strong>Before buy/sell</strong> — live Finnhub quotes (Step 3)</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
./scripts/run_refresh_live_mac.sh</pre>

          <p class="setup-terminal-label"><strong>Check data freshness</strong></p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
PYTHONPATH=src python3 scripts/manage_watchlist.py stats</pre>

          <h3 style="margin-top:1.25rem">4. Individual steps (advanced)</h3>
          <p class="brief">Use when you only need one piece. S&amp;P 500 ingest takes ~15–25 minutes.</p>

          <p class="setup-terminal-label"><strong>After market close</strong> — quotes + today&apos;s bars only</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
./scripts/run_ingest_mac.sh --after-close</pre>

          <p class="setup-terminal-label"><strong>Before open</strong> — incremental ingest only</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
./scripts/run_ingest_mac.sh --incremental</pre>

          <p class="setup-terminal-label"><strong>Screener only</strong> (14 trading days)</p>
          <pre class="setup-terminal" tabindex="0">cd ~/Home-Repository
PYTHONPATH=src python3 scripts/run_period_screener.py --days 14 --save</pre>
        </div>
        <div class="actions actions-wrap">
          <button class="btn secondary" id="setup-daily-ingest">Daily ingest (small lists only)</button>
          <button class="btn secondary" id="setup-pull-historical">Pull 60d OHLCV</button>
        </div>
        <p class="brief setup-terminal-note">Large watchlists (100+ tickers): browser ingest is blocked — use Terminal commands above.</p>
        <div class="card brief setup-hints">
          <p id="setup-freshness">Loading data freshness…</p>
          <p><strong>Repair dashboard:</strong></p>
          <pre class="setup-terminal setup-terminal-compact" tabindex="0">cd ~/Home-Repository
./scripts/repair_dashboard_mac.sh</pre>
        </div>
      </section>
    </div>

  </main>

  <div class="toast" id="toast"></div>

  <script>
    const fmt = (n) => n == null ? "—" : Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const fmtPct = (n) => n == null ? "—" : Number(n).toFixed(4) + "%";
    const PT = "America/Los_Angeles";

    function parseIsoDate(iso) {
      if (!iso) return null;
      if (/[zZ]$|[+-]\d{2}:?\d{2}$/.test(iso)) return new Date(iso);
      const m = iso.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}(?::\d{2})?)/);
      if (m) {
        const month = parseInt(m[1].slice(5, 7), 10);
        const offset = (month >= 4 && month <= 10) ? "-07:00" : "-08:00";
        return new Date(`${m[1]}T${m[2]}${offset}`);
      }
      return new Date(iso);
    }

    function fmtDatePT(iso) {
      if (!iso) return "—";
      const d = parseIsoDate(iso);
      return d.toLocaleString("en-US", {
        timeZone: PT,
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    }

    function fmtTimePT(iso) {
      if (!iso) return "—";
      const d = parseIsoDate(iso);
      return d.toLocaleString("en-US", {
        timeZone: PT,
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
        timeZoneName: "short",
      });
    }

    function fmtDateTimePT(iso) {
      if (!iso) return "—";
      return `${fmtDatePT(iso)} · ${fmtTimePT(iso)}`;
    }

    function fmtSessionPhase(phase) {
      const labels = {
        weekend: "Weekend",
        pre_market: "Pre-market",
        opening_wait: "Opening wait (30 min gate)",
        trade_window: "Trade window",
        late_day: "Late day (manage only)",
        after_hours: "After hours",
      };
      return labels[phase] || (phase || "—").replace(/_/g, " ");
    }

    function todayPtDateInput() {
      return new Intl.DateTimeFormat("en-CA", { timeZone: PT }).format(new Date());
    }

    function initJournalForm() {
      document.getElementById("t-date").value = todayPtDateInput();
      updateTradeTimeLabel();
    }

    function updateTradeTimeLabel() {
      const side = document.getElementById("t-side").value;
      document.getElementById("t-time-label").textContent =
        side === "SELL" ? "Time of sell (Pacific)" : "Time of purchase (Pacific)";
    }

    function toast(msg, ms = 3200) {
      const el = document.getElementById("toast");
      el.textContent = msg;
      el.classList.add("show");
      setTimeout(() => el.classList.remove("show"), ms);
    }

    const API_KEY_STORAGE = "investment_agent_api_key";
    let apiKeyRequired = false;

    function getApiKey() {
      if (!apiKeyRequired) return "";
      return localStorage.getItem(API_KEY_STORAGE) || "";
    }

    function apiHeaders(extra = {}) {
      const headers = { "Content-Type": "application/json", ...extra };
      const key = getApiKey();
      if (key) headers["X-API-Key"] = key;
      return headers;
    }

    async function api(path, opts = {}) {
      const timeoutMs = opts.timeoutMs ?? 30000;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const res = await fetch(path, {
          ...opts,
          signal: controller.signal,
          headers: apiHeaders(opts.headers || {}),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          if (res.status === 401) {
            localStorage.removeItem(API_KEY_STORAGE);
            const input = document.getElementById("app-api-key");
            if (input) input.value = "";
            throw new Error(
              "Invalid dashboard password — it must match APP_API_KEY in your .env exactly. "
              + "Saved password cleared; re-enter and click Save, or leave APP_API_KEY blank in .env for local-only use."
            );
          }
          throw new Error(data.detail || data.error || res.statusText);
        }
        return data;
      } catch (err) {
        if (err.name === "AbortError") {
          throw new Error("Request timed out — the server may still be refreshing quotes. Wait 15s and click Refresh again.");
        }
        if (err instanceof TypeError) {
          throw new Error(
            "Cannot reach the dashboard server (connection failed). "
            + "If using 127.0.0.1, start run_dashboard.py on this machine. "
            + "If using a cloud link, ask for a new tunnel URL — they expire."
          );
        }
        throw err;
      } finally {
        clearTimeout(timer);
      }
    }

    function initApiKeyBar() {
      const input = document.getElementById("app-api-key");
      if (!input) return;
      const saved = getApiKey();
      if (saved) {
        input.value = saved;
        document.getElementById("api-key-status").textContent = "Password saved in this browser.";
      }
      document.getElementById("save-api-key").addEventListener("click", () => {
        const key = input.value.trim();
        if (!key) {
          localStorage.removeItem(API_KEY_STORAGE);
          document.getElementById("api-key-status").textContent = "Password cleared.";
          return;
        }
        localStorage.setItem(API_KEY_STORAGE, key);
        document.getElementById("api-key-status").textContent = "Password saved — retry your action.";
        toast("Dashboard password saved in this browser");
      });
      document.getElementById("clear-api-key")?.addEventListener("click", () => {
        localStorage.removeItem(API_KEY_STORAGE);
        input.value = "";
        document.getElementById("api-key-status").textContent = "Password cleared.";
      });
    }

    async function initDashboard() {
      const cfg = await fetch("/api/config").then((r) => r.json()).catch(() => ({ api_key_required: false }));
      apiKeyRequired = !!cfg.api_key_required;
      if (!apiKeyRequired) {
        localStorage.removeItem(API_KEY_STORAGE);
      } else {
        initApiKeyBar();
      }
      initAppNav();
      await refreshAll();
      initJournalForm();
    }

    function formatWhyOnly(thesis) {
      if (!thesis) return "";
      // Thesis includes entry/sell from last screener ingest — strip so we don't duplicate live prices.
      return thesis
        .replace(/Entry ~\$[\d.]+ → sell \$[\d.]+ \([^)]+\), stop −[\d.]+% \$[\d.]+\.\s*/i, "")
        .replace(/\s*Execute in E\*TRADE; log fill in journal\./i, "")
        .trim();
    }

    function renderPickBlock(pick, td) {
      if (!pick) return "<div class='pick-empty'>No live pick — run ingest and refresh ranked screener.</div>";
      const limitBuy = pick.limit_buy_price ?? pick.recommended_entry ?? pick.entry_price;
      const limitSell = pick.limit_sell_price ?? pick.target_price;
      const netGoal = pick.net_target ?? td.daily_target;
      const trad = pick.tradability || {};
      const tradClass = (trad.verdict || "unknown").toLowerCase().replace("_", "-");
      const conf = pick.dollar_confidence || "";
      const rankedNote = td.ranked_first && pick.ticker !== td.ranked_first
        ? `<div class="pick-note warn">Ranked #1 was ${td.ranked_first} — skipped (not tradable for $${fmt(netGoal)})</div>`
        : "";
      const livePx = pick.quote_price;
      const changeHtml = pick.intraday_change_pct != null
        ? `<span class="pick-change ${pick.intraday_change_pct >= 0 ? "up" : "down"}">${fmtPctLive(pick.intraday_change_pct)} from open</span>`
        : "";
      return `
        <div class="pick-symbol-row">
          <span class="pick-symbol">${pick.ticker}</span>
          <span class="pick-source brief">${pick.source || ""}</span>
          ${conf ? `<span class="confidence-badge conf-${conf}">${conf} $ confidence</span>` : ""}
          ${trad.verdict ? `<span class="tradability-badge trad-${tradClass}">${trad.verdict.replace(/_/g, " ")}</span>` : ""}
        </div>
        ${rankedNote}
        ${trad.detail ? `<div class="pick-tradability-detail">${trad.detail}</div>` : ""}
        ${pick.thesis_summary ? `<div class="pick-why"><span class="pick-why-label">Why ranked</span><p>${formatWhyOnly(pick.thesis_summary)}</p></div>` : ""}
        <div class="pick-stats-row">
          <div class="pick-stat"><span class="pick-stat-label">Rank score</span><strong>${pick.rank_score != null ? Number(pick.rank_score).toFixed(3) : "—"}</strong></div>
          <div class="pick-stat"><span class="pick-stat-label">$ goal hit</span><strong>${pick.dollar_hit_rate_pct ?? "—"}%</strong></div>
          <div class="pick-stat"><span class="pick-stat-label">1.5% hit</span><strong>${pick.hit_rate_pct ?? "—"}%</strong></div>
        </div>
        ${pick.expected_net_at_typical_high != null ? `
        <div class="pick-forecast">
          Est. high from limit → <strong>$${fmt(pick.expected_net_at_typical_high)}</strong> net
          ${pick.historical_avg_net_at_high != null ? `<span class="brief">(14d avg $${fmt(pick.historical_avg_net_at_high)})</span>` : ""}
          · need <strong>$${fmt(netGoal)}</strong>
        </div>` : ""}
        <div class="pick-prices">
          <div class="pick-prices-head">Pullback limit plan · cancel unfilled by ${pick.limit_fill_deadline_et || "11:30 ET"}</div>
          ${pick.session_open != null ? `<div class="pick-price-row brief"><span>Today&apos;s open</span><strong>$${fmt(pick.session_open)}</strong>${pick.pullback_pct != null ? `<span class="brief">−${pick.pullback_pct}% limit zone</span>` : ""}</div>` : ""}
          <div class="pick-price-row highlight">
            <span>Limit buy</span><strong class="pick-price">$${fmt(limitBuy)}</strong>
          </div>
          <div class="pick-price-row brief">
            <span>Live now</span><strong>$${fmt(livePx)}</strong>${changeHtml}
          </div>
          <div class="pick-price-row">
            <span>${pick.recommended_shares ?? "—"} shares</span>
            <span class="brief">$${fmt(pick.notional)} notional</span>
          </div>
          <div class="pick-price-row stop">
            <span>Stop −0.75%</span><strong>$${fmt(pick.stop_price)}</strong>
            <span class="brief">net ~$${fmt(pick.net_at_stop)}</span>
          </div>
          <div class="pick-price-row target">
            <span>Limit sell $${fmt(netGoal)} net</span><strong>$${fmt(limitSell)}</strong>
            <span class="brief">+${pick.target_pct != null ? Number(pick.target_pct).toFixed(2) : "—"}% · +$${fmt(pick.net_at_target)}</span>
          </div>
        </div>
        ${trad.max_net_at_day_high != null ? `<div class="pick-day-high brief">Day high so far → ~$${fmt(trad.max_net_at_day_high)} net from limit entry</div>` : ""}
        ${pick.quote_as_of ? `<div class="pick-asof brief">Quote ${fmtDateTimePT(pick.quote_as_of)}</div>` : ""}
      `;
    }

    function updateStatusBar(td, summary) {
      const verdictEl = document.getElementById("status-verdict-text");
      const dailyEl = document.getElementById("status-daily-text");
      const cashEl = document.getElementById("status-cash-text");
      const goalEl = document.getElementById("status-goal-text");
      if (td && verdictEl) {
        verdictEl.textContent = (td.verdict || "—").replace("_", " ");
        document.getElementById("status-verdict-chip")?.classList.toggle("status-go", td.verdict === "GO");
        document.getElementById("status-verdict-chip")?.classList.toggle("status-nogo", td.verdict === "NO_GO");
      }
      if (summary && dailyEl) {
        const todayNet = summary.today_realized_net ?? 0;
        const target = summary.daily_target ?? 150;
        dailyEl.textContent = `$${fmt(todayNet)} / $${fmt(target)}`;
        if (cashEl) cashEl.textContent = "$" + fmt(summary.tradable_cash);
        if (goalEl) goalEl.textContent = fmtPct(summary.goal_pct);
      }
    }

    function initAppNav() {
      const saved = localStorage.getItem("dashboard-view") || "trade";
      document.querySelectorAll(".app-nav-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const view = btn.dataset.view;
          localStorage.setItem("dashboard-view", view);
          document.querySelectorAll(".app-nav-btn").forEach((b) => b.classList.toggle("active", b === btn));
          document.querySelectorAll(".app-view").forEach((v) => {
            v.classList.toggle("active", v.id === "view-" + view);
          });
        });
      });
      const btn = document.querySelector(`.app-nav-btn[data-view="${saved}"]`);
      if (btn) btn.click();
      else document.querySelector('.app-nav-btn[data-view="trade"]')?.click();
    }

    function renderTradeMath(pick, td) {
      const panel = document.getElementById("trade-math-panel");
      if (!pick) {
        panel.hidden = true;
        return;
      }
      panel.hidden = false;
      const limitBuy = pick.limit_buy_price ?? pick.recommended_entry ?? pick.entry_price;
      const limitSell = pick.limit_sell_price ?? pick.target_price;
      const netGoal = pick.net_target ?? td.daily_target;
      document.getElementById("trade-math-goal").textContent =
        `(Limit entry · $${fmt(netGoal)} net after $14 fees · cancel if not filled by ${pick.limit_fill_deadline_et || "11:30 ET"})`;
      document.getElementById("math-buy").textContent = "$" + fmt(limitBuy);
      document.getElementById("math-shares").textContent =
        `${pick.recommended_shares ?? "—"} shares · deploy $${fmt(pick.suggested_size)}`;
      const limitNote = document.getElementById("math-limit-note");
      if (limitNote) {
        limitNote.textContent = pick.session_open != null
          ? `Open $${fmt(pick.session_open)} · pullback −${pick.pullback_pct ?? "—"}%`
          : "Place as limit order in E*TRADE";
      }
      document.getElementById("math-stop").textContent = "$" + fmt(pick.stop_price);
      document.getElementById("math-stop-net").textContent =
        `net ~$${fmt(pick.net_at_stop)} if stopped`;
      document.getElementById("math-sell").textContent = "$" + fmt(limitSell);
      document.getElementById("math-sell-net").textContent =
        `+${pick.target_pct != null ? Number(pick.target_pct).toFixed(2) : "—"}% · net ~+$${fmt(pick.net_at_target)}`;
    }

    async function loadTradingDay() {
      const td = await api("/api/trading-day/status");
      const badge = document.getElementById("verdict-badge");
      const panel = document.getElementById("trading-day-panel");
      badge.textContent = td.verdict.replace("_", " ");
      badge.className = "verdict-badge " + (td.verdict || "").toLowerCase();
      panel.className = "card trading-day-panel verdict-" + (td.verdict || "").toLowerCase();
      document.getElementById("verdict-headline").textContent = td.headline || "—";
      document.getElementById("verdict-detail").textContent = td.detail || "";
      document.getElementById("verdict-asof").textContent =
        `Session: ${fmtSessionPhase(td.session_phase)} · ${fmtDateTimePT(td.as_of_et)}`;

      const pick = td.top_pick;
      const pickEl = document.getElementById("top-pick-body");
      renderTradeMath(pick, td);
      if (!pick) {
        pickEl.innerHTML = "<div class='pick-empty'>No live pick — run ingest + ranked screener, then Refresh live.</div>";
        document.getElementById("second-pick-body").innerHTML =
          "<div class='pick-empty'>Backup pick appears after #1 is ranked and tradable.</div>";
      } else {
        pickEl.innerHTML = renderPickBlock(pick, td);
        const planTicker = document.getElementById("plan-ticker");
        const planPrice = document.getElementById("plan-price");
        const planShares = document.getElementById("plan-shares");
        const entry = pick.limit_buy_price ?? pick.recommended_entry ?? pick.entry_price;
        if (planTicker && !planTicker.dataset.userEdited) planTicker.value = pick.ticker;
        if (planPrice && !planPrice.dataset.userEdited) planPrice.value = entry != null ? Number(entry).toFixed(2) : "";
        if (planShares && !planShares.dataset.userEdited && pick.recommended_shares) planShares.value = pick.recommended_shares;

        const second = td.second_pick;
        const secondEl = document.getElementById("second-pick-body");
        if (second) {
          secondEl.innerHTML = renderPickBlock(second, td);
        } else {
          secondEl.innerHTML = "<div class='pick-empty'>No second tradable name on the ranked list yet. Refresh live after ingest.</div>";
        }
      }

      const checks = document.getElementById("trading-checks");
      checks.innerHTML = (td.checks || []).map((c) => {
        const icon = c.ok === true ? "✓" : c.ok === false ? "✗" : "◐";
        const cls = c.ok === true ? "ok" : c.ok === false ? "bad" : "wait";
        return `<li class="check-${cls}"><span class="check-icon">${icon}</span> <strong>${c.name}</strong>: ${c.message}</li>`;
      }).join("");

      const hint = document.getElementById("rotation-hint");
      const next = td.next_ranked || [];
      let hintText = "";
      if (td.stopped_out_today) hintText = "Stop-out logged — done for the day per plan.";
      else if (td.daily_target_met) hintText = "Daily target reached — protect gains, no new entries.";
      else if (td.can_second_trade) hintText = "Win logged — optional 2nd trade: use #2 pick below before 2:30 PM ET.";
      else if (td.second_pick) hintText = "If #1 fails before target: watch #" + td.second_pick.ticker + " (shown below).";
      else if ((td.skipped_not_tradable || []).length)
        hintText = "Skipped not tradable: " + td.skipped_not_tradable.map((s) => s.ticker).join(", ");
      else if (next.length) hintText = "If top pick fails: " + next.map((n) => n.ticker).join(" → ");
      hint.textContent = hintText;

      const banner = document.getElementById("regime-banner");
      if (td.verdict === "NO_GO") {
        banner.className = "banner block app-banner-compact";
        banner.textContent = td.headline + " — " + (td.detail || "");
      } else if (td.verdict === "WAIT") {
        banner.className = "banner wait app-banner-compact";
        banner.textContent = td.headline + " — " + (td.detail || "");
      } else if (td.verdict === "CAUTION") {
        banner.className = "banner caution app-banner-compact";
        banner.textContent = td.headline + " — " + (td.detail || "");
      } else {
        banner.className = "banner ok app-banner-compact";
        banner.textContent = td.headline + " — " + (td.detail || "");
      }
      updateStatusBar(td, null);
    }

    function updateTradingModeBanner(mode) {
      const banner = document.getElementById("trading-mode-banner");
      if (mode === "live") {
        banner.className = "banner live app-banner-compact";
        banner.textContent =
          "LIVE TRADING — journal entries are treated as real E*TRADE fills. Only switch here when you are ready.";
      } else {
        banner.className = "banner paper app-banner-compact";
        banner.textContent =
          "PAPER TRADING — journal entries are practice data for testing the dashboard and process. Not real money.";
      }
    }

    async function loadSummary() {
      const s = await api("/api/summary");
      updateTradingModeBanner(s.trading_mode || "paper");
      document.getElementById("trading-mode").value = s.trading_mode || "paper";
      document.getElementById("goal-pct").textContent = fmtPct(s.goal_pct);
      document.getElementById("goal-bar").style.width = Math.min(100, s.goal_pct) + "%";
      document.getElementById("goal-label").textContent =
        `$${fmt(s.tradable_cash)} of $${fmt(s.goal_target)} goal`;
      document.getElementById("tradable-cash").textContent = "$" + fmt(s.tradable_cash);
      document.getElementById("original-basis").textContent = "$" + fmt(s.original_basis);

      const dailyTarget = s.daily_target ?? 150;
      document.getElementById("daily-target").textContent = "$" + fmt(dailyTarget) + "/day";
      const todayNet = s.today_realized_net ?? 0;
      const dailyPct = Math.min(100, Math.max(0, s.today_target_progress_pct ?? 0));
      document.getElementById("daily-bar").style.width = dailyPct + "%";
      const todaySign = todayNet >= 0 ? "+" : "";
      document.getElementById("daily-progress-label").textContent =
        `Today ${todaySign}$${fmt(todayNet)} of $${fmt(dailyTarget)} (${dailyPct.toFixed(0)}%)`;

      const tier = s.growth_tier || {};
      const nextAmt = tier.amount_to_next_tier ?? 0;
      document.getElementById("next-tier-label").textContent = nextAmt > 0
        ? `$${fmt(nextAmt)} to $${fmt(tier.next_balance)} → $${fmt(tier.next_daily_target)}/day`
        : "At top growth tier shown";

      const st = s.strategy || {};
      const dailyNet = st.daily_net_target ?? s.daily_target ?? 150;
      document.getElementById("strategy-rules").innerHTML = [
        `Sell for <strong>$${fmt(dailyNet)} net/day</strong> (Growth Plan — scales +$50 per $5K)`,
        `Stop <strong>−${st.stop_pct ?? 0.75}%</strong> · Max <strong>${st.max_trades_per_day ?? 2}</strong> trades/day`,
        `<strong>${st.entry_delay_minutes ?? 30}m</strong> entry delay · Window <strong>${st.entry_window_et ?? "10:00–14:30"}</strong> ET`,
        `Stop day after stop-out · Trade #2 only after a win on #1`,
      ].join("<br>");

      const plan = s.growth_plan || [];
      const balance = s.tradable_cash ?? 0;
      document.getElementById("growth-tier-summary").textContent =
        `Current balance $${fmt(balance)} → daily goal $${fmt(dailyTarget)}/day. `
        + (tier.milestone_daily_350_at
          ? `$350/day milestone at $${fmt(tier.milestone_daily_350_at)}+.`
          : "");
      document.getElementById("growth-plan-body").innerHTML = plan.length
        ? plan.map((row, i) => {
            const nextBalance = i < plan.length - 1 ? plan[i + 1].balance_at_least : Infinity;
            const active = balance >= row.balance_at_least && balance < nextBalance;
            const reached = balance >= row.balance_at_least;
            const status = active ? "Current tier" : reached ? "Reached" : "Upcoming";
            return `<tr class="${active ? "growth-active" : ""}"><td>$${fmt(row.balance_at_least)}</td>`
              + `<td>$${fmt(row.daily_target)}/day</td><td>${status}</td></tr>`;
          }).join("")
        : "<tr><td colspan='3' class='empty'>No growth tiers</td></tr>";

      const pnlEl = document.getElementById("month-pnl");
      pnlEl.textContent = (s.monthly_realized_net >= 0 ? "+" : "") + "$" + fmt(s.monthly_realized_net);
      pnlEl.className = "metric " + (s.monthly_realized_net >= 0 ? "positive" : s.monthly_realized_net < 0 ? "negative" : "");

      document.getElementById("month-key").textContent = s.month_key;
      document.getElementById("total-fees").textContent = "$" + fmt(s.total_fees_paid);
      document.getElementById("mgmt-jar").textContent = "$" + fmt(s.management_jar);
      document.getElementById("tax-jar").textContent = "$" + fmt(s.tax_jar);
      document.getElementById("market-brief").textContent = s.market_brief;
      document.getElementById("tax-rate").value = Math.round(s.tax_rate * 100);

      const sp = s.sweep_preview;
      let sweepHtml = sp.applies
        ? `Realized net $${fmt(sp.monthly_realized_net)} → sweep $${fmt(sp.total_sweep)} `
          + `(mgmt $${fmt(sp.management_sweep)} + tax $${fmt(sp.tax_sweep)})`
        : `No sweep this month (realized net $${fmt(sp.monthly_realized_net)} ≤ 0)`;
      if (s.sweep_already_applied) sweepHtml += " · <strong>Already applied</strong>";
      document.getElementById("sweep-preview").innerHTML = sweepHtml;
      updateStatusBar(null, s);
    }

    const fmtPctLive = (n) => n == null ? "—" : (Number(n) >= 0 ? "+" : "") + Number(n).toFixed(2) + "%";

    async function loadAlerts() {
      const alerts = await api("/api/alerts");
      const body = document.getElementById("alerts-body");
      if (!alerts.length) {
        body.innerHTML = '<tr><td colspan="7" class="empty">No active alerts — run monitor on in-trade positions</td></tr>';
        return;
      }
      body.innerHTML = alerts.map((a) => `
        <tr>
          <td>${fmtDateTimePT(a.created_at)}</td>
          <td><strong>${a.ticker}</strong></td>
          <td><span class="badge alert-${(a.alert_type || '').toLowerCase()}">${a.alert_type}</span></td>
          <td>$${fmt(a.current_price)}</td>
          <td>${fmtPctLive(a.pnl_pct)}</td>
          <td class="thesis">${a.message || ""}</td>
          <td><button class="btn secondary btn-sm" data-ack="${a.id}">Ack</button></td>
        </tr>
      `).join("");
      body.querySelectorAll("[data-ack]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            await api(`/api/alerts/${btn.dataset.ack}/acknowledge`, { method: "POST" });
            toast("Alert acknowledged");
            await loadAlerts();
          } catch (e) { toast(e.message); }
        });
      });
    }

    async function loadQueue() {
      const items = await api("/api/queue");
      const body = document.getElementById("queue-body");
      if (!items.length) {
        body.innerHTML = '<tr><td colspan="10" class="empty">Queue empty — run ingest then Sync from screener</td></tr>';
        return;
      }
      body.innerHTML = items.map((q) => `
        <tr>
          <td><strong>${q.ticker}</strong></td>
          <td><span class="badge ${q.state}">${q.state}</span></td>
          <td>${q.current_price != null ? "$" + fmt(q.current_price) : "—"}</td>
          <td>${q.pnl_pct != null ? fmtPctLive(q.pnl_pct) : "—"}</td>
          <td>$${fmt(q.entry_price)}</td>
          <td>$${fmt(q.target_price)}</td>
          <td>$${fmt(q.stop_price)}</td>
          <td>$${fmt(q.suggested_size)}</td>
          <td class="thesis">${q.thesis_summary || ""}</td>
          <td><button class="btn secondary btn-sm" data-advance="${q.id}">Advance</button></td>
        </tr>
      `).join("");
      body.querySelectorAll("[data-advance]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            const r = await api(`/api/queue/${btn.dataset.advance}/advance`, { method: "POST" });
            toast(`${r.from_state} → ${r.to_state}`);
            await refreshAll();
          } catch (e) { toast(e.message); }
        });
      });
    }

    async function loadJournal() {
      const trades = await api("/api/journal");
      const body = document.getElementById("journal-body");
      if (!trades.length) {
        body.innerHTML = '<tr><td colspan="8" class="empty">No trades logged yet</td></tr>';
        return;
      }
      body.innerHTML = trades.map((t) => `
        <tr>
          <td>${fmtDatePT(t.executed_at)}</td>
          <td><strong>${fmtTimePT(t.executed_at)}</strong></td>
          <td><strong>${t.ticker}</strong></td>
          <td>${t.side}</td>
          <td>${t.shares}</td>
          <td>$${fmt(t.price)}</td>
          <td>$${fmt(t.fee)}</td>
          <td>${t.notes || ""}</td>
        </tr>
      `).join("");
    }

    async function loadCio() {
      const cio = await api("/api/cio/summary");
      document.getElementById("cio-headline").textContent = cio.headline || "—";
      document.getElementById("cio-narrative").textContent = cio.narrative || "";
      const actions = document.getElementById("cio-actions");
      actions.innerHTML = (cio.action_items || []).map((a) => `<li>${a}</li>`).join("") || "<li>No urgent actions</li>";
      const subs = document.getElementById("cio-subagents");
      const sa = cio.sub_agents || {};
      subs.innerHTML = Object.entries(sa).map(([k, v]) => `
        <div class="card" style="padding:0.65rem">
          <h2 style="margin-bottom:0.35rem">${k.replace("_", " ")}</h2>
          <div class="brief" style="font-size:0.82rem">${v}</div>
        </div>
      `).join("");
    }

    function rhythmStateLabel(state) {
      const map = { ready: "Ready", ok: "OK", needed: "Do this", stale: "Re-run" };
      return map[state] || state || "—";
    }

    function renderCandidatesTable(candidates) {
      const body = document.getElementById("candidates-body");
      if (!body) return;
      if (!candidates?.length) {
        body.innerHTML = '<tr><td colspan="9" class="empty">Run Step 2 — Prepare today&apos;s trades — to fill this table.</td></tr>';
        return;
      }
      body.innerHTML = candidates.map((c, i) => `
        <tr>
          <td>${i + 1}</td>
          <td><strong>${c.ticker}</strong></td>
          <td>${c.dollar_hit_rate_pct ?? c.hit_rate_pct ?? "—"}%</td>
          <td>${c.limit_buy_price != null ? "$" + fmt(c.limit_buy_price) : (c.entry_price != null ? "$" + fmt(c.entry_price) : "—")}</td>
          <td>${c.recommended_shares ?? "—"}</td>
          <td>${c.suggested_size != null ? "$" + fmt(c.suggested_size) : "—"}</td>
          <td>${c.limit_sell_price != null ? "$" + fmt(c.limit_sell_price) : (c.target_price != null ? "$" + fmt(c.target_price) : "—")}</td>
          <td>${c.stop_price != null ? "$" + fmt(c.stop_price) : "—"}</td>
          <td>${c.step3_pass ? "Yes" : "No"}</td>
        </tr>
      `).join("");
    }

    async function loadCandidates() {
      try {
        const data = await api("/api/daily-rhythm/candidates?limit=15");
        renderCandidatesTable(data.candidates || []);
      } catch (_) {
        renderCandidatesTable([]);
      }
    }

    function renderDailyRhythm(rhythm) {
      const list = document.getElementById("rhythm-steps");
      if (!list || !rhythm?.steps) return;
      list.innerHTML = rhythm.steps.map((step) => {
        const last = step.last_at ? `Last: ${fmtDateTimePT(step.last_at)}` : "Not run yet today";
        let actionBtn = "";
        if (step.id === "pre_market") {
          actionBtn = `<button type="button" class="btn btn-sm rhythm-action-btn" data-rhythm-action="prepare">Prepare today&apos;s trades</button>`;
        } else if (step.id === "before_buy") {
          actionBtn = `<button type="button" class="btn btn-sm rhythm-action-btn" data-rhythm-action="refresh">Refresh live before buy</button>`;
        } else if (step.id === "after_close") {
          actionBtn = `<span class="brief rhythm-manual">${step.manual || ""}</span>`;
        }
        return `
          <li class="rhythm-step rhythm-state-${step.state}">
            <div class="rhythm-step-head">
              <span class="rhythm-num">${step.number}</span>
              <div class="rhythm-step-copy">
                <strong>${step.title}</strong>
                <span class="rhythm-sub">${step.subtitle}</span>
              </div>
              <span class="rhythm-badge">${rhythmStateLabel(step.state)}</span>
            </div>
            <p class="brief rhythm-detail">${step.detail}</p>
            <p class="brief rhythm-last">${last}</p>
            ${actionBtn}
          </li>`;
      }).join("");
      list.querySelectorAll("[data-rhythm-action=prepare]").forEach((btn) => {
        btn.addEventListener("click", () => prepareMorningTrades().catch((e) => toast(e.message)));
      });
      list.querySelectorAll("[data-rhythm-action=refresh]").forEach((btn) => {
        btn.addEventListener("click", () => refreshLiveBeforeBuy().catch((e) => toast(e.message)));
      });
      const sched = document.getElementById("setup-schedule-status");
      if (sched) {
        sched.textContent = rhythm.schedule_installed
          ? "Auto refresh is ON (6:30 AM + 4:30 PM)."
          : "Auto refresh is OFF — double-click Enable Auto Refresh.command in scripts/.";
      }
      const screenNote = document.getElementById("rhythm-screen-note");
      if (screenNote && rhythm.steps?.[1]) {
        const s2 = rhythm.steps[1];
        screenNote.textContent =
          `Step 2 last run: ${s2.last_at ? fmtDateTimePT(s2.last_at) : "not yet today"} — `
          + `use Trade tab → Prepare today's trades for buy / sell / stop columns.`;
      }
    }

    async function loadDailyRhythm() {
      const rhythm = await api("/api/daily-rhythm/status");
      renderDailyRhythm(rhythm);
      return rhythm;
    }

    async function prepareMorningTrades() {
      toast("Step 2 — running screener and building trade plan…");
      const r = await api("/api/daily-rhythm/prepare-morning", { method: "POST", timeoutMs: 300000 });
      renderCandidatesTable(r.candidates || []);
      if (r.trading_day) {
        const td = r.trading_day;
        updateStatusBar(td, null);
        const pick = td.top_pick;
        document.getElementById("top-pick-body").innerHTML = pick
          ? renderPickBlock(pick, td)
          : "<div class='pick-empty'>No tradable pick for today's dollar goal.</div>";
        renderTradeMath(pick, td);
        document.getElementById("second-pick-body").innerHTML = td.second_pick
          ? renderPickBlock(td.second_pick, td)
          : "<div class='pick-empty'>No backup pick yet.</div>";
        document.getElementById("verdict-headline").textContent = td.headline || "—";
        document.getElementById("verdict-detail").textContent = td.detail || "";
      }
      if (r.rhythm) renderDailyRhythm(r.rhythm);
      await loadPeriodScreener();
      await loadWatchlistStats();
      toast(`Step 2 done — ${r.candidate_count || 0} candidates with buy / sell / stop on Trade tab.`);
    }

    async function refreshLiveBeforeBuy() {
      const btn = document.getElementById("refresh-trading-day");
      try {
        if (btn) btn.disabled = true;
        toast("Step 3 — refreshing live quotes for picks…", 8000);
        const r = await api("/api/trading-day/refresh", { method: "POST", timeoutMs: 90000 });
        if (!r.refresh?.ok) {
          toast(r.refresh?.error || "Refresh failed — check FINNHUB_API_KEY in .env", 6000);
        } else {
          toast(`Live refresh done (${(r.refresh.updated || []).length} symbols). Validate below.`);
        }
        if (r.status) {
          await loadTradingDay();
          await loadSummary();
        }
        document.getElementById("plan-ticker")?.removeAttribute("data-user-edited");
        document.getElementById("plan-price")?.removeAttribute("data-user-edited");
        document.getElementById("plan-shares")?.removeAttribute("data-user-edited");
        await loadTradingDay();
        document.querySelector(".validate-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    async function loadWatchlistStats() {
      const s = await api("/api/watchlist/stats");
      const f = s.freshness || {};
      let freshLine = "";
      if (f.quotes_max_age_hours != null) {
        freshLine = ` · Quotes oldest: ${f.quotes_max_age_hours}h ago`;
        if (f.stale_quote_count > 0) {
          freshLine += ` (${f.stale_quote_count} stale)`;
        }
      }
      if (f.metrics_max_age_hours != null) {
        freshLine += ` · Metrics oldest: ${f.metrics_max_age_hours}h ago`;
      }
      document.getElementById("watchlist-stats").textContent =
        `Universe: ${s.universe_size} tickers (${s.tradeable_universe} tradeable) · `
        + `Step 3 pass: ${s.pass_both_step3} (${s.pass_pct}%) · `
        + `Filtered out: ${s.filtered_out} (${s.filter_pct_out}%) · `
        + `Missing metrics: ${s.missing_metrics}${freshLine}`;
      const setupFresh = document.getElementById("setup-freshness");
      if (setupFresh) {
        if (f.quotes_newest_at) {
          setupFresh.textContent =
            `Data freshness — newest quote: ${fmtDateTimePT(f.quotes_newest_at)} · `
            + `newest metrics: ${f.metrics_newest_at ? fmtDateTimePT(f.metrics_newest_at) : "—"} · `
            + `If quotes are >4h old, run After-Close Ingest or install the auto schedule (above).`;
        } else {
          setupFresh.textContent = "No quote data yet — run ingest once.";
        }
      }
    }

    function renderScreenActionTimes(actions) {
      document.querySelectorAll(".screener-action-item[data-action]").forEach((item) => {
        const id = item.dataset.action;
        const info = actions[id];
        const el = item.querySelector(".screener-action-ts");
        if (!el) return;
        el.classList.remove("inferred", "empty");
        if (!info?.completed_at) {
          el.innerHTML = '<span class="ts-label">Last:</span> Not run yet';
          el.classList.add("empty");
          return;
        }
        let label = fmtDateTimePT(info.completed_at);
        if (info.source === "inferred") {
          label += " · est.";
          el.classList.add("inferred");
        }
        el.innerHTML = `<span class="ts-label">Last:</span> ${label}`;
        el.title = info.detail || label;
      });
    }

    async function loadScreenActionTimes() {
      const data = await api("/api/screen/actions");
      renderScreenActionTimes(data.actions || {});
    }

    let screenerRows = [];
    let screenerSortKey = "score";
    let screenerSortAsc = false;
    let screenerRequestedTradingDays = 14;
    let screenerTradingDaysInPeriod = 14;
    let screenerNetTarget = 150;
    let screenerExcludedCount = 0;

    function screenerNumeric(val) {
      if (val === true) return 1;
      if (val === false) return 0;
      const n = Number(val);
      return Number.isFinite(n) ? n : -Infinity;
    }

    const priorScreenedState = {
      historical: { rows: [], sortKey: "ticker", sortAsc: true },
      learning: { rows: [], sortKey: "ticker", sortAsc: true },
    };

    const OUTCOME_LABELS = {
      target: "Hit +1.5% target",
      stop: "Hit stop (−0.75%)",
      neither: "No target or stop",
    };

    const DOLLAR_OUTCOME_LABELS = {
      target: "Hit $ goal",
      stop: "Hit stop",
      neither: "Missed $ goal",
    };

    function outcomeBadge(outcome, kind) {
      if (!outcome) return "<span class='brief'>—</span>";
      const labels = kind === "dollar" ? DOLLAR_OUTCOME_LABELS : OUTCOME_LABELS;
      const label = labels[outcome] || outcome;
      const cls = kind === "dollar" && outcome === "target"
        ? "outcome-dollar-target"
        : `outcome-${outcome}`;
      return `<span class="outcome-badge ${cls}">${label}</span>`;
    }

    function formatRangeDelta(delta) {
      if (delta == null || Number.isNaN(Number(delta))) return "—";
      const n = Number(delta);
      const sign = n >= 0 ? "+" : "";
      const warn = Math.abs(n) > 1 ? " warn" : "";
      const dir = n >= 0 ? "positive" : "negative";
      return `<span class="range-delta ${dir}${warn}">${sign}${n.toFixed(2)}%</span>`;
    }

    function applyPriorScreenedFilters(rows, searchId, outcomeId) {
      const q = (document.getElementById(searchId)?.value || "").trim().toUpperCase();
      const outcome = document.getElementById(outcomeId)?.value || "";
      return rows.filter((r) => {
        if (q && !String(r.ticker || "").includes(q)) return false;
        if (outcome && r.simulated_outcome !== outcome) return false;
        return true;
      });
    }

    function sortPriorScreenedRows(rows, sortKey, sortAsc) {
      const outcomeOrder = { target: 0, neither: 1, stop: 2 };
      return [...rows].sort((a, b) => {
        let av = a[sortKey];
        let bv = b[sortKey];
        if (sortKey === "ticker") {
          return sortAsc
            ? String(av).localeCompare(String(bv))
            : String(bv).localeCompare(String(av));
        }
        if (sortKey === "simulated_outcome" || sortKey === "dollar_outcome") {
          av = outcomeOrder[av] ?? 99;
          bv = outcomeOrder[bv] ?? 99;
        } else {
          av = screenerNumeric(av);
          bv = screenerNumeric(bv);
        }
        if (av === bv) return a.ticker.localeCompare(b.ticker);
        return sortAsc ? av - bv : bv - av;
      });
    }

    function priorScreenedRowHtml(m) {
      return `<tr>
        <td><strong>${m.ticker}</strong></td>
        <td>${m.predicted_avg_range_pct != null ? Number(m.predicted_avg_range_pct).toFixed(2) + "%" : "—"}</td>
        <td>${m.actual_range_pct != null ? Number(m.actual_range_pct).toFixed(2) + "%" : "—"}</td>
        <td>${formatRangeDelta(m.range_delta_pct)}</td>
        <td>${outcomeBadge(m.simulated_outcome, "pct")}</td>
        <td>${outcomeBadge(m.dollar_outcome, "dollar")}</td>
      </tr>`;
    }

    function renderPriorScreenedTable(instance, tbodyId, countId, searchId, outcomeId) {
      const st = priorScreenedState[instance];
      const filtered = sortPriorScreenedRows(
        applyPriorScreenedFilters(st.rows, searchId, outcomeId),
        st.sortKey,
        st.sortAsc,
      );
      const tbody = document.getElementById(tbodyId);
      if (!tbody) return;
      tbody.innerHTML = filtered.length
        ? filtered.map(priorScreenedRowHtml).join("")
        : "<tr><td colspan='6' class='empty'>No matches — try clearing filters</td></tr>";
      const countEl = document.getElementById(countId);
      if (countEl) {
        countEl.textContent = filtered.length === st.rows.length
          ? `${filtered.length} ticker(s)`
          : `${filtered.length} of ${st.rows.length} shown`;
      }
    }

    function updatePriorScreenedSortHeaders(tableSelector, instance) {
      const st = priorScreenedState[instance];
      document.querySelectorAll(`${tableSelector} th.sortable`).forEach((th) => {
        th.classList.remove("sorted-asc", "sorted-desc");
        if (th.dataset.sort === st.sortKey) {
          th.classList.add(st.sortAsc ? "sorted-asc" : "sorted-desc");
        }
      });
    }

    function setPriorScreenedData(instance, rows, meta) {
      priorScreenedState[instance].rows = rows || [];
      if (instance === "historical") {
        renderPriorScreenedTable(
          "historical",
          "prior-day-table",
          "historical-prior-count",
          "historical-prior-search",
          "historical-prior-outcome",
        );
        updatePriorScreenedSortHeaders("#prior-day-table-wrap", "historical");
        if (meta) {
          const s = meta.summary || {};
          document.getElementById("prior-day-eval").innerHTML =
            `<strong>${meta.eval_date}</strong> — `
            + `${s.screened_count || 0} Step 3 match(es): `
            + `<span class="outcome-badge outcome-target">${s.simulated_targets || 0} targets</span> `
            + `<span class="outcome-badge outcome-stop">${s.simulated_stops || 0} stops</span> `
            + `<span class="outcome-badge outcome-neither">${s.simulated_neither || 0} flat</span>`
            + (s.dollar_targets != null
              ? ` · $ goal: ${s.dollar_targets} hit / ${s.dollar_stops || 0} stop / ${s.dollar_neither || 0} miss`
              : "");
        }
      } else if (instance === "learning") {
        const block = document.getElementById("learning-prior-screened");
        if (!rows || !rows.length) {
          block.hidden = true;
          return;
        }
        block.hidden = false;
        if (meta) {
          document.getElementById("learning-prior-date").textContent = meta.eval_date ? `(${meta.eval_date})` : "";
          const s = meta.summary || {};
          document.getElementById("learning-prior-summary").textContent =
            `${s.screened_count || rows.length} names passed Step 3 — `
            + `${s.simulated_targets || 0} would hit +1.5%, `
            + `${s.simulated_stops || 0} hit stop, `
            + `${s.simulated_neither || 0} no clean exit. `
            + "Sort columns or search by ticker.";
        }
        renderPriorScreenedTable(
          "learning",
          "learning-prior-table",
          "learning-prior-count",
          "learning-prior-search",
          "learning-prior-outcome",
        );
        updatePriorScreenedSortHeaders(".learning-prior-table", "learning");
      }
    }

    function applyScreenerFilters(rows) {
      const q = (document.getElementById("screener-filter-ticker").value || "").trim().toUpperCase();
      const minHit = document.getElementById("screener-min-hit").value;
      const minDays = document.getElementById("screener-min-days").value;
      const liveOnly = document.getElementById("screener-live-only").checked;
      return rows.filter((r) => {
        if (q && !r.ticker.includes(q)) return false;
        if (minHit !== "" && (r.hit_rate_pct ?? 0) < Number(minHit)) return false;
        if (minDays !== "" && (r.days_screened ?? 0) < Number(minDays)) return false;
        if (liveOnly && !r.live_pass_today) return false;
        return true;
      });
    }

    function sortScreenerRows(rows) {
      const key = screenerSortKey;
      const asc = screenerSortAsc;
      return [...rows].sort((a, b) => {
        const av = key === "ticker" ? a.ticker : screenerNumeric(a[key]);
        const bv = key === "ticker" ? b.ticker : screenerNumeric(b[key]);
        if (key === "ticker") {
          return asc ? av.localeCompare(bv) : bv.localeCompare(av);
        }
        if (av === bv) return a.ticker.localeCompare(b.ticker);
        return asc ? av - bv : bv - av;
      });
    }

    function formatScreenerDays(row) {
      const hit = row.days_screened ?? 0;
      const total = row.requested_trading_days ?? screenerRequestedTradingDays;
      return `${hit}/${total}`;
    }

    function renderScreenerTable() {
      const body = document.getElementById("period-screener-body");
      const filtered = sortScreenerRows(applyScreenerFilters(screenerRows));
      document.getElementById("screener-row-count").textContent =
        `${filtered.length} of ${screenerRows.length} shown · ${screenerRequestedTradingDays} trading-day window · $${screenerNetTarget} goal${screenerExcludedCount ? ` · ${screenerExcludedCount} excluded (weak $ history)` : ""} · sorted by ${screenerSortKey} (${screenerSortAsc ? "asc" : "desc"})`;

      if (!filtered.length) {
        body.innerHTML = `<tr><td colspan="12" class="empty">${screenerRows.length ? "No rows match filters." : "Run period screener after pulling history."}</td></tr>`;
        return;
      }

      body.innerHTML = filtered.map((r) => `
        <tr>
          <td><strong>${r.score != null ? Number(r.score).toFixed(3) : "—"}</strong></td>
          <td>${r.ticker}</td>
          <td>${r.avg_range_pct != null ? r.avg_range_pct + "%" : "—"}</td>
          <td>${r.adv_dollar_m != null ? r.adv_dollar_m : "—"}</td>
          <td>${r.dollar_hit_rate_pct != null ? r.dollar_hit_rate_pct + "%" : "—"}</td>
          <td>${r.avg_net_at_high != null ? "$" + Math.round(r.avg_net_at_high) : "—"}</td>
          <td>${formatScreenerDays(r)}</td>
          <td>${r.simulated_targets ?? "—"}</td>
          <td>${r.simulated_stops ?? "—"}</td>
          <td>${r.hit_rate_pct != null ? r.hit_rate_pct + "%" : "—"}</td>
          <td>${r.live_pass_today ? "Yes" : "—"}</td>
          <td><button class="btn btn-sm secondary promote-btn" data-ticker="${r.ticker}">Add to queue</button></td>
        </tr>
      `).join("");

      body.querySelectorAll(".promote-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            const res = await api(`/api/screener/promote/${btn.dataset.ticker}`, { method: "POST" });
            toast(res.message || "Promoted");
            await loadQueue();
          } catch (e) { toast(e.message); }
        });
      });
    }

    function updateScreenerSortHeaders() {
      document.querySelectorAll("#ranked-screener-table th.sortable").forEach((th) => {
        th.classList.remove("sorted-asc", "sorted-desc");
        if (th.dataset.sort === screenerSortKey) {
          th.classList.add(screenerSortAsc ? "sorted-asc" : "sorted-desc");
        }
      });
    }

    async function loadPeriodScreener() {
      const days = document.getElementById("screener-period-days").value || "14";
      const data = await api(`/api/screener/ranked?period_days=${days}`);
      screenerRows = data.ranked || [];
      screenerRequestedTradingDays = data.period_days ?? Number(days);
      screenerTradingDaysInPeriod = data.trading_days_in_period ?? screenerRequestedTradingDays;
      screenerNetTarget = data.net_target ?? 150;
      screenerExcludedCount = data.excluded_count ?? 0;
      renderScreenerTable();
      updateScreenerSortHeaders();
    }

    async function loadRankedAndStats() {
      await loadWatchlistStats();
      await loadScreenActionTimes();
      await loadSpecialWatch();
      await loadPeriodScreener();
    }

    let specialWatchRows = [];
    let specialWatchSortKey = "ticker";
    let specialWatchSortAsc = true;

    function step3BadgeClass(status) {
      return `step3-badge step3-${(status || "missing").replace(/_/g, "-")}`;
    }

    function applySpecialWatchFilters(rows) {
      const q = (document.getElementById("special-watch-filter-ticker").value || "").trim().toUpperCase();
      const status = document.getElementById("special-watch-filter-status").value;
      const activeOnly = document.getElementById("special-watch-active-only").checked;
      return rows.filter((r) => {
        if (q && !r.ticker.includes(q)) return false;
        if (status && r.step3_status !== status) return false;
        if (activeOnly && !r.in_active_watchlist) return false;
        return true;
      });
    }

    function sortSpecialWatchRows(rows) {
      const key = specialWatchSortKey;
      const asc = specialWatchSortAsc;
      return [...rows].sort((a, b) => {
        let av = a[key];
        let bv = b[key];
        if (key === "ticker" || key === "step3_status") {
          av = String(av || "");
          bv = String(bv || "");
          return asc ? av.localeCompare(bv) : bv.localeCompare(av);
        }
        av = screenerNumeric(av);
        bv = screenerNumeric(bv);
        if (av === bv) return a.ticker.localeCompare(b.ticker);
        return asc ? av - bv : bv - av;
      });
    }

    function renderSpecialWatchTable() {
      const body = document.getElementById("special-watch-body");
      const filtered = sortSpecialWatchRows(applySpecialWatchFilters(specialWatchRows));
      document.getElementById("special-watch-row-count").textContent =
        `${filtered.length} of ${specialWatchRows.length} shown`;

      if (!filtered.length) {
        body.innerHTML = `<tr><td colspan="5" class="empty">${specialWatchRows.length ? "No rows match filters." : "No Special Watch data."}</td></tr>`;
        return;
      }

      body.innerHTML = filtered.map((r) => `
        <tr>
          <td><strong>${r.ticker}</strong></td>
          <td><span class="${step3BadgeClass(r.step3_status)}" title="${r.step3_label || ""}">${r.step3_label || "—"}</span></td>
          <td>${r.avg_range_pct != null ? r.avg_range_pct + "%" : "—"}</td>
          <td>${r.adv_dollar_m != null ? r.adv_dollar_m : "—"}</td>
          <td>${r.in_active_watchlist ? "Yes" : "—"}</td>
        </tr>
      `).join("");
    }

    function updateSpecialWatchSortHeaders() {
      document.querySelectorAll(".special-watch-table th.sortable").forEach((th) => {
        th.classList.remove("sorted-asc", "sorted-desc");
        if (th.dataset.sort === specialWatchSortKey) {
          th.classList.add(specialWatchSortAsc ? "sorted-asc" : "sorted-desc");
        }
      });
    }

    async function loadSpecialWatch() {
      const data = await api("/api/watchlist/special-watch?preset=datacenter_us");
      const band = data.swing_band_pct || {};
      const manualNote = data.manual_ticker_count
        ? ` · ${data.manual_ticker_count} manual add(s)`
        : "";
      document.getElementById("special-watch-stats").textContent =
        `Universe: ${data.ticker_count} tickers${manualNote} · Step 3 pass: ${data.step3_pass} · `
        + `Too quiet: ${data.too_quiet} · Too wild: ${data.too_wild} · `
        + `Low liquidity: ${data.low_liquidity} · Missing metrics: ${data.missing_metrics} · `
        + `Band ${band.low}–${band.high}% (target ${band.target}%)`;
      specialWatchRows = data.tickers || [];
      renderSpecialWatchTable();
      updateSpecialWatchSortHeaders();
    }

    async function addSpecialWatchTicker() {
      const input = document.getElementById("special-watch-add-ticker");
      const ticker = (input.value || "").trim().toUpperCase();
      if (!ticker) {
        toast("Enter a ticker symbol (e.g. NBIS)");
        return;
      }
      try {
        const r = await api("/api/watchlist/special-watch/add", {
          method: "POST",
          body: JSON.stringify({ preset: "datacenter_us", ticker }),
        });
        input.value = "";
        const msg = r.already_in_preset && !r.added_to_extras
          ? `${ticker} is already on the Special Watch list — activated on watchlist for ingest.`
          : `${ticker} added to Special Watch. Run Daily ingest (or Refresh live) for Range/ADV.`;
        toast(msg);
        await loadSpecialWatch();
        await loadRankedAndStats();
      } catch (e) {
        toast(e.message);
      }
    }

    async function loadHistorical() {
      const summary = await api("/api/historical/summary");
      const el = document.getElementById("historical-summary");
      if (!summary.has_data) {
        el.textContent = "No historical bars stored — click Pull history or run scripts/run_historical.py pull.";
        document.getElementById("historical-stats").innerHTML = "";
        document.getElementById("prior-day-eval").textContent = "—";
        document.getElementById("prior-day-table").innerHTML = "<tr><td colspan='6' class='empty'>No data</td></tr>";
        document.getElementById("historical-prior-count").textContent = "";
        priorScreenedState.historical.rows = [];
        return;
      }
      el.textContent = `${summary.ticker_count} ticker(s), ${summary.total_bars} bars (${summary.earliest_date} → ${summary.latest_date})`;
      document.getElementById("historical-stats").innerHTML = `
        <div class="card"><h2>Tickers</h2><div class="metric small">${summary.ticker_count}</div></div>
        <div class="card"><h2>Total bars</h2><div class="metric small">${summary.total_bars}</div></div>
        <div class="card"><h2>From</h2><div class="metric small">${summary.earliest_date}</div></div>
        <div class="card"><h2>Through</h2><div class="metric small">${summary.latest_date}</div></div>
      `;
      const prior = await api("/api/historical/evaluate");
      const matches = prior.screened_matches || [];
      setPriorScreenedData("historical", matches, prior);
    }

    let closeReportCache = null;
    let closeActiveTab = "step3_pass";

    function renderCloseTable(tabKey) {
      const tbody = document.getElementById("close-table-body");
      if (!closeReportCache || !closeReportCache.tabs) {
        tbody.innerHTML = "<tr><td colspan='6' class='empty'>Load a Daily Close report</td></tr>";
        return;
      }
      const tab = closeReportCache.tabs[tabKey] || closeReportCache.tabs.full_top20;
      const rows = tab.rows || [];
      tbody.innerHTML = rows.length ? rows.map((r) => {
        const o = r.open_entry || {};
        const t = r.entry_10_et || {};
        const hit = r.hit_goal_either ? "✓" : "—";
        return `<tr>
          <td>${r.rank}</td>
          <td><strong>${r.ticker}</strong></td>
          <td>$${fmt(o.entry_price)} → <strong>$${fmt(o.net_at_high)}</strong></td>
          <td>${t.available ? `$${fmt(t.entry_price)} → <strong>$${fmt(t.net_at_high)}</strong>` : "—"}</td>
          <td>${hit}</td>
          <td>${r.live_pass_today ? "pass" : "—"}</td>
        </tr>`;
      }).join("") : "<tr><td colspan='6' class='empty'>No rows for this tab</td></tr>";
    }

    function renderCloseSummary(report, tabKey) {
      const el = document.getElementById("close-summary");
      if (!report || report.report_type === "weekly") {
        if (report && report.report_type === "weekly") {
          const s = report.summary || {};
          el.innerHTML = `
            <div><strong>Week ${report.week_start} → ${report.week_end}</strong> (${s.days} sessions)</div>
            <div>Journal total: <strong>$${fmt(s.journal_total_net)}</strong>
              · Best-on-list (open): <strong>$${fmt(s.counterfactual_best_open_total)}</strong>
              · Ranked #1 (open): <strong>$${fmt(s.counterfactual_rank1_open_total)}</strong></div>
            <div class="brief">Missed vs best: $${fmt(s.missed_vs_best_open)} · #1 hit ${s.rank1_hit_days_open}/${s.days} days</div>`;
        }
        return;
      }
      const tab = report.tabs[tabKey] || report.tabs.full_top20;
      const s = tab.summary || {};
      el.innerHTML = `
        <div>Goal <strong>$${fmt(report.net_target)}</strong> net · Deploy $${fmt(report.deploy)} · Ranked #1: <strong>${report.rank1_ticker || "—"}</strong></div>
        <div>#1 net@high: open <strong>$${fmt(s.rank1_net_at_high_open)}</strong>
          · 10:00 <strong>$${fmt(s.rank1_net_at_high_10et)}</strong>
          · Best on list: <strong>${s.best_hit_ticker_open || "—"}</strong> ($${fmt(s.best_net_at_high_open)})</div>
        <div class="brief">Journal: $${fmt(s.journal_realized_net)} realized
          · Counterfactual if #1 (open): $${fmt(s.counterfactual_if_rank1_open)}
          · if best (open): $${fmt(s.counterfactual_if_best_open)}</div>`;
    }

    async function loadDailyClose(refresh) {
      const dateInput = document.getElementById("close-date");
      const q = new URLSearchParams();
      if (dateInput.value) q.set("date", dateInput.value);
      if (refresh) q.set("refresh", "true");
      const r = await api(`/api/close/daily?${q}`);
      if (!dateInput.value && r.report_date) dateInput.value = r.report_date;
      closeReportCache = r;
      document.getElementById("close-highlights").innerHTML = (r.highlights || [])
        .map((h) => `<div>${h}</div>`).join("") || "<span class='empty'>No data</span>";
      renderCloseSummary(r, closeActiveTab);
      renderCloseTable(closeActiveTab);
      const j = r.journal || {};
      document.getElementById("close-journal").innerHTML = j.traded_today
        ? `<strong>Journal:</strong> ${(j.round_trips || []).map((t) =>
            `${t.ticker} $${fmt(t.buy_price)}→$${fmt(t.sell_price)} net $${fmt(t.net_pnl)}`).join(" · ")}`
        : "<span class='brief'>No journal trades on this date.</span>";
    }

    async function loadWeeklyClose(refresh) {
      const dateInput = document.getElementById("close-date");
      const q = new URLSearchParams();
      if (dateInput.value) q.set("end", dateInput.value);
      if (refresh) q.set("refresh", "true");
      const r = await api(`/api/close/weekly?${q}`);
      closeReportCache = null;
      document.getElementById("close-highlights").innerHTML = (r.daily_reports || [])
        .map((d) => `<div>${d.date}: journal $${fmt(d.journal_net)} · best ${d.best_open || "—"} $${fmt(d.best_net_open)}</div>`).join("")
        || "<span class='empty'>No weekly data</span>";
      renderCloseSummary(r, closeActiveTab);
      document.getElementById("close-table-body").innerHTML =
        "<tr><td colspan='6' class='empty'>Weekly view — see summary above; load Daily Close for ticker table.</td></tr>";
      document.getElementById("close-journal").innerHTML = "";
    }

    async function loadLearning() {
      const dateInput = document.getElementById("learning-date");
      const q = dateInput.value ? `?date=${dateInput.value}` : "";
      const r = await api(`/api/learning/report${q}`);
      if (!dateInput.value && r.report_date) dateInput.value = r.report_date;
      const hl = document.getElementById("learning-highlights");
      hl.innerHTML = (r.highlights || []).length
        ? `<ul>${r.highlights.map((h) => `<li>${h}</li>`).join("")}</ul>`
        : "<span class='empty'>No highlights yet — log trades and run ingest.</span>";
      const cl = r.continual_learning || {};
      const j = cl.journal || {};
      document.getElementById("continual-learning").innerHTML = cl.note
        ? `<strong>Continual learning (${cl.lookback_days || 30}d):</strong> `
          + `${j.round_trips_closed || 0} closed trips, ${j.win_rate_pct ?? "—"}% win rate, `
          + `net $${fmt(j.total_net_pnl || 0)}; `
          + `${cl.reports_saved || 0} saved report(s).`
        : "";
      const details = document.getElementById("learning-details");
      const prior = r.prior_day_evaluation;
      const priorRows = prior && prior.screened_matches ? prior.screened_matches : [];
      setPriorScreenedData("learning", priorRows, prior);
      const sections = [
        ["Today's journal", r.today_journal, (p) => `${p.side} ${p.shares} ${p.ticker} @ $${p.price}`],
        ["Today's round trips", r.today_round_trips, (p) => `${p.ticker}: ${p.note}`],
        ["Active positions", r.active_positions, (p) => `${p.ticker}: ${p.note}`],
        ["Recent round trips", r.round_trips, (p) => `${p.ticker}: ${p.note}`],
        ["Watchlist", r.watchlist_insights, (p) => `${p.ticker}: ${p.note}`],
      ];
      details.innerHTML = sections.map(([title, rows, fmt]) => {
        if (!rows || !rows.length) return `<div class="learning-block"><h3>${title}</h3><p class="empty">None</p></div>`;
        return `<div class="learning-block"><h3>${title}</h3><ul>${rows.map((x) => `<li>${fmt(x)}</li>`).join("")}</ul></div>`;
      }).join("");
    }

    async function loadScenario() {
      const s = await api("/api/scenario/visualizer?projection_months=120");
      document.getElementById("scenario-summary").textContent = s.summary || "";
      const stats = document.getElementById("scenario-stats");
      stats.innerHTML = `
        <div class="card"><h2>Current</h2><div class="metric small">$${fmt(s.current_balance)}</div></div>
        <div class="card"><h2>Goal %</h2><div class="metric small">${fmtPct(s.current_goal_pct)}</div></div>
        <div class="card"><h2>Journal pace</h2><div class="metric small">${s.scenarios?.journal_pace?.months_to_goal != null ? s.scenarios.journal_pace.months_to_goal.toFixed(0) + " mo" : "—"}</div></div>
        <div class="card"><h2>10yr required</h2><div class="metric small">${s.scenarios?.required_10yr?.monthly_return_pct?.toFixed(2) || "—"}%/mo</div></div>
      `;
      renderScenarioChart(s);
      const tbody = document.getElementById("scenario-table");
      tbody.innerHTML = (s.actual_timeline || []).map((p) => `
        <tr>
          <td>${p.label || p.month_key}</td>
          <td>$${fmt(p.tradable_balance)}</td>
          <td>${fmtPct(p.goal_pct)}</td>
          <td>${p.monthly_realized_net ? ((p.monthly_realized_net >= 0 ? "+" : "") + "$" + fmt(p.monthly_realized_net)) : "—"}</td>
          <td>${p.sweep_total ? "$" + fmt(p.sweep_total) : "—"}</td>
        </tr>
      `).join("");
      const leg = document.getElementById("scenario-legend");
      leg.innerHTML = `
        <span class="legend-item"><span class="swatch actual"></span> Actual (journal)</span>
        <span class="legend-item"><span class="swatch pace"></span> Journal pace</span>
        <span class="legend-item"><span class="swatch strategy"></span> Strategy reference</span>
      `;
    }

    function renderScenarioChart(s) {
      const svg = document.getElementById("scenario-chart");
      const W = 800, H = 220, pad = { l: 55, r: 20, t: 20, b: 35 };
      const actual = s.actual_timeline || [];
      const pace = s.scenarios?.journal_pace?.points || [];
      const allY = [
        ...actual.map((p) => p.tradable_balance),
        ...pace.map((p) => p.balance),
        s.goal,
      ].filter((v) => v != null && v > 0);
      const minY = Math.min(...allY, s.original_basis) * 0.95;
      const maxY = Math.max(...allY) * 1.05;
      const xScale = (i, n) => pad.l + (i / Math.max(n - 1, 1)) * (W - pad.l - pad.r);
      const yScale = (v) => pad.t + (1 - (v - minY) / (maxY - minY)) * (H - pad.t - pad.b);
      const line = (pts, key) => {
        if (!pts.length) return "";
        return pts.map((p, i) => {
          const x = xScale(i, pts.length);
          const y = yScale(p.tradable_balance ?? p.balance);
          return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(" ");
      };
      const goalY = yScale(s.goal);
      svg.innerHTML = `
        <line x1="${pad.l}" y1="${goalY}" x2="${W - pad.r}" y2="${goalY}" stroke="#6366f1" stroke-dasharray="4 4" opacity="0.5"/>
        <text x="${W - pad.r}" y="${goalY - 4}" fill="#8b9cb3" font-size="10" text-anchor="end">$5M goal</text>
        <path d="${line(actual.map((p) => ({ balance: p.tradable_balance })), "balance")}" fill="none" stroke="#22c55e" stroke-width="2.5"/>
        <path d="${line(pace, "balance")}" fill="none" stroke="#3b82f6" stroke-width="2" stroke-dasharray="6 4" opacity="0.85"/>
        <text x="${pad.l}" y="${H - 8}" fill="#8b9cb3" font-size="10">Months →</text>
        <text x="8" y="${pad.t + 10}" fill="#8b9cb3" font-size="10" transform="rotate(-90 8,${pad.t + 10})">Balance</text>
      `;
    }

    async function refreshAll() {
      await Promise.all([
        loadTradingDay(),
        loadSummary(),
        loadScenario(),
        loadCio(),
        loadDailyRhythm(),
        loadCandidates(),
        loadRankedAndStats(),
        loadHistorical(),
        loadDailyClose(),
        loadLearning(),
        loadAlerts(),
        loadQueue(),
        loadJournal(),
      ]);
    }

    document.getElementById("load-sp500")?.addEventListener("click", async () => {
      if (!confirm("Load ~500 S&P 500 tickers into the watchlist? Existing tickers stay active.")) return;
      try {
        const r = await api("/api/watchlist/load-preset", {
          method: "POST",
          body: JSON.stringify({ preset: "sp500", replace: false }),
          timeoutMs: 120000,
        });
        toast(`Loaded ${r.tickers_loaded} tickers. Enable Auto Refresh in Setup, then wait for ingest or run After-Close Ingest.command.`);
        await loadRankedAndStats();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("load-datacenter-us")?.addEventListener("click", async () => {
      try {
        const r = await api("/api/watchlist/load-preset", {
          method: "POST",
          body: JSON.stringify({ preset: "datacenter_us", replace: false }),
          timeoutMs: 120000,
        });
        toast(`Special Watch: added ${r.tickers_loaded} tickers (${r.tickers_activated} activated). Run ingest for metrics.`);
        await loadRankedAndStats();
      } catch (e) { toast(e.message); }
    });
    async function runIngest(incremental) {
      const label = incremental ? "Daily incremental ingest" : "Full ingest";
      let pf;
      try {
        pf = await api("/api/ingest/preflight");
      } catch (e) {
        toast(e.message, 8000);
        return;
      }
      if (pf.ingest_running) {
        toast(pf.message || "Ingest running in Terminal — wait for it to finish.", 10000);
        return;
      }
      if (pf.missing_api_keys) {
        toast("Add FRED_API_KEY and FINNHUB_API_KEY to .env, then restart the dashboard.", 9000);
        return;
      }
      if (pf.recommend_terminal) {
        const cmd = incremental ? pf.terminal_command : pf.terminal_command_full;
        toast(
          `Watchlist has ${pf.ticker_count} tickers — use Mac Terminal or double-click `
          + `scripts/Run Daily Ingest.command in Finder. Command: ${cmd}. `
          + `Refresh the browser after it finishes.`,
          14000,
        );
        return;
      }
      toast(`${label} started — this may take several minutes…`);
      const r = await api("/api/ingest/run", {
        method: "POST",
        body: JSON.stringify({ incremental, lookback_days: 60, stale_hours: 20 }),
        timeoutMs: incremental ? 600000 : 900000,
      });
      const q = r.quotes_refreshed ?? 0;
      const qs = r.quotes_skipped ?? 0;
      const b = r.bars_refreshed ?? 0;
      const bs = r.bars_skipped ?? 0;
      toast(`${label} done: ${q} quotes refreshed (${qs} skipped), ${b} bars refreshed (${bs} skipped)`);
      await refreshAll();
    }
    document.getElementById("refresh-ranked")?.addEventListener("click", async () => {
      try {
        await loadRankedAndStats();
        await api("/api/screen/actions/record", {
          method: "POST",
          body: JSON.stringify({ action: "refresh_ranked" }),
        });
        await loadScreenActionTimes();
        toast("Ranked list refreshed");
      } catch (e) { toast(e.message); }
    });

    ["special-watch-filter-ticker", "special-watch-filter-status"].forEach((id) => {
      document.getElementById(id).addEventListener("input", () => renderSpecialWatchTable());
      document.getElementById(id).addEventListener("change", () => renderSpecialWatchTable());
    });
    document.getElementById("special-watch-active-only").addEventListener("change", () => renderSpecialWatchTable());
    document.getElementById("special-watch-add-btn").addEventListener("click", () => addSpecialWatchTicker());
    document.getElementById("special-watch-add-ticker").addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        addSpecialWatchTicker();
      }
    });
    document.querySelectorAll(".special-watch-table th.sortable").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.sort;
        if (specialWatchSortKey === key) {
          specialWatchSortAsc = !specialWatchSortAsc;
        } else {
          specialWatchSortKey = key;
          specialWatchSortAsc = key === "ticker" || key === "step3_status";
        }
        renderSpecialWatchTable();
        updateSpecialWatchSortHeaders();
      });
    });

    ["screener-filter-ticker", "screener-min-hit", "screener-min-days"].forEach((id) => {
      document.getElementById(id).addEventListener("input", () => renderScreenerTable());
    });
    document.getElementById("screener-live-only").addEventListener("change", () => renderScreenerTable());
    document.getElementById("screener-period-days").addEventListener("change", () => {
      loadPeriodScreener().catch((e) => toast(e.message));
    });
    document.querySelectorAll("#ranked-screener-table th.sortable").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.sort;
        if (screenerSortKey === key) {
          screenerSortAsc = !screenerSortAsc;
        } else {
          screenerSortKey = key;
          screenerSortAsc = key === "ticker";
        }
        updateScreenerSortHeaders();
        renderScreenerTable();
      });
    });

    function wirePriorScreenedTable(instance, tableSelector, searchId, outcomeId, tbodyId, countId) {
      const searchEl = document.getElementById(searchId);
      const outcomeEl = document.getElementById(outcomeId);
      if (searchEl) {
        searchEl.addEventListener("input", () => renderPriorScreenedTable(instance, tbodyId, countId, searchId, outcomeId));
      }
      if (outcomeEl) {
        outcomeEl.addEventListener("change", () => renderPriorScreenedTable(instance, tbodyId, countId, searchId, outcomeId));
      }
      document.querySelectorAll(`${tableSelector} th.sortable`).forEach((th) => {
        th.addEventListener("click", () => {
          const st = priorScreenedState[instance];
          const key = th.dataset.sort;
          if (st.sortKey === key) {
            st.sortAsc = !st.sortAsc;
          } else {
            st.sortKey = key;
            st.sortAsc = key === "ticker";
          }
          renderPriorScreenedTable(instance, tbodyId, countId, searchId, outcomeId);
          updatePriorScreenedSortHeaders(tableSelector, instance);
        });
      });
    }
    wirePriorScreenedTable(
      "historical",
      "#prior-day-table-wrap",
      "historical-prior-search",
      "historical-prior-outcome",
      "prior-day-table",
      "historical-prior-count",
    );
    wirePriorScreenedTable(
      "learning",
      ".learning-prior-table",
      "learning-prior-search",
      "learning-prior-outcome",
      "learning-prior-table",
      "learning-prior-count",
    );

    document.getElementById("pull-historical").addEventListener("click", async () => {
      try {
        const r = await api("/api/historical/pull?lookback_days=60", { method: "POST" });
        toast(`Pulled ${r.bars_inserted || 0} bar(s)`);
        await loadHistorical();
        await loadLearning();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("refresh-historical").addEventListener("click", () => loadHistorical().catch((e) => toast(e.message)));
    document.getElementById("learning-date").addEventListener("change", () => loadLearning().catch((e) => toast(e.message)));

    document.getElementById("load-daily-close").addEventListener("click", () => loadDailyClose(false).catch((e) => toast(e.message)));
    document.getElementById("load-weekly-close").addEventListener("click", () => loadWeeklyClose(false).catch((e) => toast(e.message)));
    document.getElementById("refresh-close").addEventListener("click", () => loadDailyClose(true).catch((e) => toast(e.message)));
    document.getElementById("close-date").addEventListener("change", () => loadDailyClose(false).catch((e) => toast(e.message)));
    document.querySelectorAll(".close-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        closeActiveTab = btn.dataset.tab;
        document.querySelectorAll(".close-tab").forEach((b) => {
          b.classList.toggle("active", b === btn);
          b.classList.toggle("secondary", b !== btn);
        });
        if (closeReportCache) {
          renderCloseSummary(closeReportCache, closeActiveTab);
          renderCloseTable(closeActiveTab);
        }
      });
    });

    document.getElementById("generate-learning").addEventListener("click", async () => {
      try {
        const dateInput = document.getElementById("learning-date");
        const q = dateInput.value ? `?date=${dateInput.value}` : "";
        await api(`/api/learning/generate${q}`, { method: "POST" });
        toast("Learning report saved");
        await loadLearning();
        await loadCio();
      } catch (e) { toast(e.message); }
    });

    document.getElementById("run-monitor").addEventListener("click", async () => {
      try {
        const r = await api("/api/monitor/run", { method: "POST" });
        toast(`Monitor: ${r.new_alerts} new alert(s)`);
        await refreshAll();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("refresh-alerts").addEventListener("click", () => loadAlerts().catch((e) => toast(e.message)));

    document.getElementById("refresh-trading-day").addEventListener("click", () => {
      refreshLiveBeforeBuy().catch((e) => toast(e.message, 8000));
    });

    ["plan-ticker", "plan-price", "plan-shares"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", (e) => {
        e.target.dataset.userEdited = "1";
      });
    });

    document.getElementById("planned-trade-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const ticker = document.getElementById("plan-ticker").value.trim();
      const price = Number(document.getElementById("plan-price").value);
      const sharesRaw = document.getElementById("plan-shares").value;
      const payload = { ticker, price };
      if (sharesRaw) payload.shares = Number(sharesRaw);
      try {
        toast("Validating planned trade…");
        const r = await api("/api/trading-day/validate", { method: "POST", body: JSON.stringify(payload), timeoutMs: 60000 });
        const el = document.getElementById("planned-trade-result");
        const p = r.plan || {};
        el.innerHTML = `
          <div class="validate-verdict ${r.verdict.toLowerCase()}"><strong>${r.verdict}</strong> — ${r.headline}</div>
          <ul class="check-list">${(r.checks || []).map((c) => {
            const icon = c.ok === true ? "✓" : c.ok === false ? "✗" : "◐";
            const cls = c.ok === true ? "ok" : c.ok === false ? "bad" : "wait";
            return `<li class="check-${cls}"><span class="check-icon">${icon}</span> ${c.message}</li>`;
          }).join("")}</ul>
          ${p.shares ? `<div style="margin-top:0.5rem">At $${fmt(price)} × ${p.shares} sh → sell $${fmt(p.target_price)} (${p.target_pct != null ? Number(p.target_pct).toFixed(2) + "%" : "—"} / $${fmt(p.net_target)} net) · stop $${fmt(p.stop_price)}</div>` : ""}
        `;
        toast(r.headline, 5000);
      } catch (err) { toast(err.message, 6000); }
    });

    document.getElementById("pin-top-pick").addEventListener("click", async () => {
      try {
        const td = await api("/api/trading-day/status");
        const ticker = td.top_pick?.ticker;
        if (!ticker) { toast("No top pick to pin"); return; }
        await api("/api/trading-day/pin-pick", { method: "POST", body: JSON.stringify({ ticker }) });
        const pr = await api(`/api/screener/promote/${ticker}`, { method: "POST" });
        toast(pr.message || `Pinned ${ticker} and added to queue`);
        await refreshAll();
      } catch (e) { toast(e.message); }
    });

    document.getElementById("refresh-all").addEventListener("click", () => refreshAll().catch((e) => toast(e.message)));
    document.getElementById("setup-daily-ingest")?.addEventListener("click", () => {
      runIngest(true).catch((e) => toast(e.message));
    });
    document.getElementById("setup-pull-historical")?.addEventListener("click", () => {
      document.getElementById("pull-historical")?.click();
    });
    document.getElementById("sync-queue").addEventListener("click", async () => {
      try {
        const r = await api("/api/queue/sync", { method: "POST" });
        const msg = r.message || (r.added ? `Added ${r.added} ticker(s)` : "Sync complete — no new tickers");
        toast(msg, msg.length > 60 ? 6000 : 3200);
        await loadQueue();
        await loadCio();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("save-tax").addEventListener("click", async () => {
      try {
        const rate = Number(document.getElementById("tax-rate").value) / 100;
        await api("/api/settings/tax-rate", { method: "PUT", body: JSON.stringify({ tax_rate: rate }) });
        toast("Tax rate saved");
        await loadSummary();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("save-trading-mode").addEventListener("click", async () => {
      const select = document.getElementById("trading-mode");
      const mode = select.value;
      const status = document.getElementById("trading-mode-status");
      if (mode === "live") {
        const ok = window.confirm(
          "Switch to LIVE mode? New journal entries will be tagged as real E*TRADE fills. Continue?"
        );
        if (!ok) {
          await loadSummary();
          return;
        }
      }
      try {
        const r = await api("/api/settings/trading-mode", { method: "PUT", body: JSON.stringify({ mode }) });
        status.textContent = r.mode === "live" ? "LIVE mode saved." : "PAPER mode saved.";
        toast(r.mode === "live" ? "LIVE trading mode enabled" : "PAPER trading mode enabled");
        await refreshAll();
      } catch (e) {
        status.textContent = "";
        toast(e.message);
      }
    });
    document.getElementById("clear-journal").addEventListener("click", async () => {
      const ok = window.confirm(
        "Clear ALL journal entries? This resets cash/P&L to the $10K basis and cannot be undone."
      );
      if (!ok) return;
      try {
        const r = await api("/api/journal/clear", { method: "POST" });
        toast(`Cleared ${r.removed} journal entr${r.removed === 1 ? "y" : "ies"}`);
        await refreshAll();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("apply-sweep").addEventListener("click", async () => {
      try {
        const r = await api("/api/sweeps/apply", { method: "POST" });
        if (!r.ok) { toast(r.error || "Sweep not applied"); return; }
        toast(`Sweep applied: $${fmt(r.total_sweep)}`);
        await refreshAll();
      } catch (e) { toast(e.message); }
    });
    document.getElementById("t-side").addEventListener("change", updateTradeTimeLabel);
    document.getElementById("trade-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const feeVal = document.getElementById("t-fee").value;
      const payload = {
        ticker: document.getElementById("t-ticker").value.trim(),
        side: document.getElementById("t-side").value,
        shares: Number(document.getElementById("t-shares").value),
        price: Number(document.getElementById("t-price").value),
        executed_date: document.getElementById("t-date").value,
        executed_time_pt: document.getElementById("t-time").value,
        notes: document.getElementById("t-notes").value || null,
      };
      if (feeVal) payload.fee = Number(feeVal);
      try {
        await api("/api/journal", { method: "POST", body: JSON.stringify(payload) });
        toast("Trade logged");
        e.target.reset();
        initJournalForm();
        await refreshAll();
      } catch (err) { toast(err.message); }
    });

    initDashboard().catch((e) => toast(e.message));
  </script>
</body>
</html>
```


---

<a id="src-investment_agent-db-py"></a>
## `src/investment_agent/db.py`

```python
"""SQLite database schema and helpers (Phase 1 — no Claude)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "agent.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS watchlist (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL UNIQUE,
  sector TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  source TEXT DEFAULT 'manual',
  added_via TEXT DEFAULT 'manual',
  added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ohlcv_daily (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  date TEXT NOT NULL,
  open REAL NOT NULL,
  high REAL NOT NULL,
  low REAL NOT NULL,
  close REAL NOT NULL,
  volume INTEGER NOT NULL,
  source TEXT NOT NULL DEFAULT 'finnhub',
  UNIQUE(ticker, date, source)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_daily_ticker_date
  ON ohlcv_daily(ticker, date);

CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  price REAL NOT NULL,
  open REAL,
  high REAL,
  low REAL,
  prev_close REAL,
  source TEXT NOT NULL DEFAULT 'finnhub'
);

CREATE INDEX IF NOT EXISTS idx_quotes_ticker_time
  ON quotes(ticker, captured_at);

CREATE TABLE IF NOT EXISTS macro_snapshots (
  id INTEGER PRIMARY KEY,
  captured_at TEXT NOT NULL,
  series_id TEXT NOT NULL,
  value REAL NOT NULL,
  observation_date TEXT NOT NULL,
  UNIQUE(series_id, observation_date)
);

CREATE TABLE IF NOT EXISTS ticker_metrics (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  computed_at TEXT NOT NULL,
  adv_dollar REAL,
  avg_range_pct REAL,
  liquidity_cap REAL,
  last_close REAL,
  last_quote REAL,
  meets_liquidity_min INTEGER NOT NULL DEFAULT 0,
  near_swing_target INTEGER NOT NULL DEFAULT 0,
  UNIQUE(ticker, computed_at)
);

CREATE TABLE IF NOT EXISTS ingest_log (
  id INTEGER PRIMARY KEY,
  run_at TEXT NOT NULL DEFAULT (datetime('now')),
  component TEXT NOT NULL,
  status TEXT NOT NULL,
  detail TEXT
);

CREATE TABLE IF NOT EXISTS regime_snapshots (
  id INTEGER PRIMARY KEY,
  captured_at TEXT NOT NULL UNIQUE,
  spy_change_pct REAL NOT NULL,
  dia_change_pct REAL NOT NULL,
  qqq_change_pct REAL NOT NULL,
  all_indices_down INTEGER NOT NULL DEFAULT 0,
  block_new_longs INTEGER NOT NULL DEFAULT 0,
  summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS jar_balances (
  jar_type TEXT PRIMARY KEY,
  balance REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sweep_history (
  id INTEGER PRIMARY KEY,
  month_key TEXT NOT NULL UNIQUE,
  realized_net REAL NOT NULL,
  management_amount REAL NOT NULL,
  tax_amount REAL NOT NULL,
  tax_rate REAL NOT NULL,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS queue_items (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'watching',
  suggested_size REAL,
  entry_price REAL,
  target_price REAL,
  stop_price REAL,
  avg_range_pct REAL,
  liquidity_cap REAL,
  thesis_summary TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_queue_items_ticker_state
  ON queue_items(ticker, state);

CREATE TABLE IF NOT EXISTS trade_journal (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
  shares REAL NOT NULL,
  price REAL NOT NULL,
  fee REAL NOT NULL DEFAULT 7.0,
  executed_at TEXT NOT NULL,
  notes TEXT,
  queue_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (queue_id) REFERENCES queue_items(id)
);

CREATE INDEX IF NOT EXISTS idx_trade_journal_executed
  ON trade_journal(executed_at);

CREATE TABLE IF NOT EXISTS price_alerts (
  id INTEGER PRIMARY KEY,
  queue_id INTEGER,
  ticker TEXT NOT NULL,
  alert_type TEXT NOT NULL,
  entry_price REAL,
  current_price REAL,
  target_price REAL,
  stop_price REAL,
  pnl_pct REAL,
  message TEXT NOT NULL,
  acknowledged INTEGER NOT NULL DEFAULT 0,
  alert_date TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (queue_id) REFERENCES queue_items(id)
);

CREATE INDEX IF NOT EXISTS idx_price_alerts_active
  ON price_alerts(acknowledged, alert_date, ticker);

CREATE TABLE IF NOT EXISTS learning_reports (
  id INTEGER PRIMARY KEY,
  report_date TEXT NOT NULL UNIQUE,
  generated_at TEXT NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screener_runs (
  id INTEGER PRIMARY KEY,
  run_type TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  params_json TEXT NOT NULL,
  summary_json TEXT,
  status TEXT NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS period_screener_hits (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  ticker TEXT NOT NULL,
  hit_date TEXT NOT NULL,
  predicted_range_pct REAL,
  actual_range_pct REAL,
  simulated_outcome TEXT,
  would_screen INTEGER NOT NULL DEFAULT 1,
  days_screened INTEGER NOT NULL DEFAULT 0,
  hit_rate_pct REAL,
  score REAL,
  FOREIGN KEY (run_id) REFERENCES screener_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_period_hits_run
  ON period_screener_hits(run_id, score DESC);

CREATE TABLE IF NOT EXISTS rank_snapshots (
  id INTEGER PRIMARY KEY,
  snapshot_date TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  ranked_json TEXT NOT NULL,
  top_n INTEGER NOT NULL DEFAULT 20
);

CREATE TABLE IF NOT EXISTS close_reports (
  id INTEGER PRIMARY KEY,
  report_date TEXT NOT NULL,
  report_type TEXT NOT NULL CHECK(report_type IN ('daily', 'weekly')),
  generated_at TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  UNIQUE(report_date, report_type)
);
"""

MIGRATION_SQL = """
-- Phase 7 watchlist columns (idempotent via try/ignore in Python)
"""


def _apply_migrations(conn: sqlite3.Connection) -> None:
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='watchlist'"
        )
    }
    if "watchlist" not in tables:
        return
    cols = {row[1] for row in conn.execute("PRAGMA table_info(watchlist)")}
    if "source" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN source TEXT DEFAULT 'manual'")
    if "added_via" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN added_via TEXT DEFAULT 'manual'")


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    _apply_migrations(conn)
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or DEFAULT_DB_PATH
    with connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        _apply_migrations(conn)
        conn.commit()
    return path


def upsert_watchlist(conn: sqlite3.Connection, tickers: list[str]) -> None:
    from investment_agent.watchlist import upsert_tickers

    upsert_tickers(conn, tickers, source="ingest", added_via="run_ingest")


def insert_ohlcv_rows(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        conn.execute(
            """
            INSERT OR REPLACE INTO ohlcv_daily
              (ticker, date, open, high, low, close, volume, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["ticker"],
                row["date"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
                row.get("source", "finnhub"),
            ),
        )
        count += 1
    return count


def get_max_ohlcv_date(conn: sqlite3.Connection, ticker: str) -> str | None:
    row = conn.execute(
        "SELECT MAX(date) AS d FROM ohlcv_daily WHERE ticker = ?",
        (ticker.upper(),),
    ).fetchone()
    return row["d"] if row and row["d"] else None


def insert_quote(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO quotes
          (ticker, captured_at, price, open, high, low, prev_close, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["ticker"],
            row["captured_at"],
            row["price"],
            row.get("open"),
            row.get("high"),
            row.get("low"),
            row.get("prev_close"),
            row.get("source", "finnhub"),
        ),
    )


def insert_macro(
    conn: sqlite3.Connection,
    series_id: str,
    observation_date: str,
    value: float,
    captured_at: str,
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO macro_snapshots
          (captured_at, series_id, value, observation_date)
        VALUES (?, ?, ?, ?)
        """,
        (captured_at, series_id, value, observation_date),
    )


def insert_ticker_metrics(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO ticker_metrics
          (ticker, computed_at, adv_dollar, avg_range_pct, liquidity_cap,
           last_close, last_quote, meets_liquidity_min, near_swing_target)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["ticker"],
            row["computed_at"],
            row["adv_dollar"],
            row["avg_range_pct"],
            row["liquidity_cap"],
            row["last_close"],
            row["last_quote"],
            1 if row["meets_liquidity_min"] else 0,
            1 if row["near_swing_target"] else 0,
        ),
    )


def get_active_watchlist(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT ticker FROM watchlist WHERE active = 1 ORDER BY ticker"
    ).fetchall()
    return [row["ticker"] for row in rows]


def get_ohlcv_bars(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
) -> list[sqlite3.Row]:
    """Daily OHLCV rows for a ticker, sorted ascending by date."""
    clauses = ["ticker = ?"]
    params: list[Any] = [ticker.upper()]
    if start_date:
        clauses.append("date >= ?")
        params.append(start_date)
    if end_date:
        clauses.append("date <= ?")
        params.append(end_date)
    sql = f"""
        SELECT ticker, date, open, high, low, close, volume, source
        FROM ohlcv_daily
        WHERE {' AND '.join(clauses)}
        ORDER BY date ASC
    """
    if limit is not None:
        sql = f"""
            SELECT * FROM (
                SELECT ticker, date, open, high, low, close, volume, source
                FROM ohlcv_daily
                WHERE {' AND '.join(clauses)}
                ORDER BY date DESC
                LIMIT ?
            ) sub ORDER BY date ASC
        """
        params.append(limit)
    return conn.execute(sql, params).fetchall()


def get_ohlcv_coverage(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT ticker,
               MIN(date) AS first_date,
               MAX(date) AS last_date,
               COUNT(*) AS bar_count
        FROM ohlcv_daily
        GROUP BY ticker
        ORDER BY ticker
        """
    ).fetchall()
    return [dict(row) for row in rows]


def log_ingest(
    conn: sqlite3.Connection, component: str, status: str, detail: str = ""
) -> None:
    conn.execute(
        "INSERT INTO ingest_log (component, status, detail) VALUES (?, ?, ?)",
        (component, status, detail),
    )


def insert_regime_snapshot(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO regime_snapshots
          (captured_at, spy_change_pct, dia_change_pct, qqq_change_pct,
           all_indices_down, block_new_longs, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["captured_at"],
            row["spy_change_pct"],
            row["dia_change_pct"],
            row["qqq_change_pct"],
            1 if row["all_indices_down"] else 0,
            1 if row["block_new_longs"] else 0,
            row["summary"],
        ),
    )
```


---

<a id="src-investment_agent-db_maintenance-py"></a>
## `src/investment_agent/db_maintenance.py`

```python
"""Database health checks and ingest lock (avoid concurrent writes)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from investment_agent.db import DEFAULT_DB_PATH, connect, init_db

INGEST_LOCK_PATH = DEFAULT_DB_PATH.parent / "ingest.lock"

REQUIRED_TABLES = (
    "watchlist",
    "ohlcv_daily",
    "quotes",
    "ticker_metrics",
    "app_settings",
    "screener_runs",
    "rank_snapshots",
    "close_reports",
    "trade_journal",
)


def ingest_lock_active() -> bool:
    return INGEST_LOCK_PATH.is_file()


def ingest_lock_message() -> str:
    return (
        "Ingest is running in Terminal (database busy). "
        "Wait for ./scripts/run_ingest_mac.sh to finish, then try again."
    )


def acquire_ingest_lock(*, detail: str = "ingest") -> None:
    INGEST_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INGEST_LOCK_PATH.exists():
        raise RuntimeError(ingest_lock_message())
    INGEST_LOCK_PATH.write_text(
        f"{detail}\n{datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )


def release_ingest_lock() -> None:
    INGEST_LOCK_PATH.unlink(missing_ok=True)


def repair_database(db_path: Path | None = None) -> dict:
    """Apply schema and verify database integrity."""
    path = init_db(db_path)
    conn = connect(path)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        missing = [t for t in REQUIRED_TABLES if t not in tables]
        if missing:
            raise RuntimeError(f"Missing tables after init: {', '.join(missing)}")

        cols = {row[1] for row in conn.execute("PRAGMA table_info(watchlist)")}
        if "source" not in cols or "added_via" not in cols:
            raise RuntimeError("watchlist schema out of date — missing source/added_via columns")

        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"integrity_check failed: {integrity}")

        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=60000")
        conn.commit()
        return {
            "ok": True,
            "db_path": str(path),
            "tables": len(tables),
            "integrity": integrity,
        }
    finally:
        conn.close()


def assert_db_available_for_writes() -> None:
    if ingest_lock_active():
        raise RuntimeError(ingest_lock_message())
```


---

<a id="src-investment_agent-demo_seed-py"></a>
## `src/investment_agent/demo_seed.py`

```python
"""Deterministic demo/test dataset for dashboard verification."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from investment_agent.db import (
    init_db,
    insert_macro,
    insert_ohlcv_rows,
    insert_quote,
    insert_regime_snapshot,
    insert_ticker_metrics,
    upsert_watchlist,
)
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.journal import insert_trade
from investment_agent.strategy import STOP_PCT, TARGET_PCT

NOW = datetime.now(timezone.utc).replace(microsecond=0)
NOW_ISO = NOW.isoformat()
MONTH_KEY = NOW.strftime("%Y-%m")
TRADE_TIME = NOW.replace(hour=14, minute=30).isoformat()


def _target(entry: float) -> float:
    return round(entry * (1 + TARGET_PCT / 100), 2)


def _stop(entry: float) -> float:
    return round(entry * (1 - STOP_PCT / 100), 2)


def _seed_ohlcv_history(conn: sqlite3.Connection, tickers: list[str], end: datetime) -> None:
    """~25 trading days of synthetic daily bars ending the day before `end`."""
    tradeables = [t for t in tickers if t not in ("SPY", "DIA", "QQQ")]
    base_prices = {
        "AAPL": 100.0,
        "MSFT": 420.0,
        "NVDA": 100.0,
        "META": 500.0,
        "AMD": 160.0,
        "TSLA": 250.0,
        "IWM": 220.0,
    }
    prior_day = (end - timedelta(days=1)).strftime("%Y-%m-%d")

    for ticker in tickers:
        base = base_prices.get(ticker, 100.0)
        rows: list[dict] = []
        for offset in range(25, 0, -1):
            day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
            close = base * (1 + 0.002 * ((25 - offset) % 5 - 2))
            if ticker in tradeables and day == prior_day:
                open_px = close
                high = open_px * 1.018
                low = open_px * 0.992
            elif ticker in tradeables:
                open_px = close * 0.998
                swing = 0.025 if ticker in ("AAPL", "NVDA", "AMD", "META") else 0.015
                high = open_px * (1 + swing / 2)
                low = open_px * (1 - swing / 2)
            else:
                open_px = close * 0.999
                high = close * 1.004
                low = close * 0.996
            rows.append(
                {
                    "ticker": ticker,
                    "date": day,
                    "open": round(open_px, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": 5_000_000,
                    "source": "demo",
                }
            )
        insert_ohlcv_rows(conn, rows)


def seed_demo_db(db_path: Path | None = None) -> Path:
    """Populate a database with realistic test data covering every dashboard section.

    Scenario:
    - Regime OK, VIX 18.25
    - Completed AAPL round trip (+profit) this month
    - Open NVDA in_trade at +1.13% target (quote at target)
    - MSFT armed, META alert (approaching stop)
    - Queue + journal + metrics for screener
    """
    path = init_db(db_path)

    tickers = ["SPY", "DIA", "QQQ", "AAPL", "MSFT", "NVDA", "AMD", "META", "TSLA", "IWM"]

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row

        # Clear mutable demo tables for idempotent re-seed
        for table in (
            "learning_reports",
            "price_alerts",
            "trade_journal",
            "queue_items",
            "sweep_history",
            "jar_balances",
            "app_settings",
            "quotes",
            "ticker_metrics",
            "ohlcv_daily",
            "macro_snapshots",
            "regime_snapshots",
            "ingest_log",
        ):
            conn.execute(f"DELETE FROM {table}")

        upsert_watchlist(conn, tickers)
        _seed_ohlcv_history(conn, tickers, end=NOW)

        insert_macro(conn, "VIXCLS", NOW.strftime("%Y-%m-%d"), 18.25, NOW_ISO)
        insert_regime_snapshot(
            conn,
            {
                "captured_at": NOW_ISO,
                "spy_change_pct": 0.35,
                "dia_change_pct": 0.12,
                "qqq_change_pct": -0.18,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "Regime OK — SPY +0.35%, DIA +0.12%, QQQ -0.18%",
            },
        )

        metrics_rows = [
            ("AAPL", 100.0, 3.1),
            ("MSFT", 420.0, 2.9),
            ("NVDA", 100.0, 3.0),
            ("META", 500.0, 3.2),
            ("AMD", 160.0, 3.0),
            ("TSLA", 250.0, 4.1),
            ("SPY", 745.0, 1.2),
            ("DIA", 440.0, 1.0),
            ("QQQ", 480.0, 1.5),
            ("IWM", 220.0, 2.0),
        ]
        for ticker, price, avg_range in metrics_rows:
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": NOW_ISO,
                    "adv_dollar": 80_000_000,
                    "avg_range_pct": avg_range,
                    "liquidity_cap": 640_000,
                    "last_close": price,
                    "last_quote": price,
                    "meets_liquidity_min": ticker not in ("SPY", "DIA", "QQQ"),
                    "near_swing_target": avg_range >= 2.0 and avg_range <= 4.0,
                },
            )

        # Quotes — NVDA at target, META near stop, MSFT mid-range
        quote_prices = {
            "SPY": 745.0,
            "DIA": 440.0,
            "QQQ": 480.0,
            "AAPL": 101.5,
            "MSFT": 420.0,
            "NVDA": _target(100.0) + 0.05,  # above target
            "META": _stop(500.0) + 1.0,  # above stop but close
            "AMD": 160.0,
            "TSLA": 250.0,
            "IWM": 220.0,
        }
        for ticker, price in quote_prices.items():
            insert_quote(
                conn,
                {
                    "ticker": ticker,
                    "captured_at": NOW_ISO,
                    "price": price,
                    "open": price * 0.998,
                    "high": price * 1.005,
                    "low": price * 0.995,
                    "prev_close": price * 0.99,
                },
            )

        # Queue items in multiple states
        queue_specs = [
            # closed winner (already traded)
            (
                "AAPL",
                "closed",
                100.0,
                10_000,
                "Completed round trip — journal below.",
            ),
            # in_trade — NVDA at target
            (
                "NVDA",
                "in_trade",
                100.0,
                10_000,
                "Demo in-trade position — monitor should fire TARGET_HIT.",
            ),
            ("MSFT", "armed", 420.0, 10_000, "Armed — waiting for entry trigger."),
            ("META", "alert", 500.0, 10_000, "Alert state — price near stop."),
            ("AMD", "watching", 160.0, 10_000, "Watching — screener candidate."),
        ]

        queue_ids: dict[str, int] = {}
        for ticker, state, entry, size, thesis in queue_specs:
            cur = conn.execute(
                """
                INSERT INTO queue_items
                  (ticker, state, suggested_size, entry_price, target_price, stop_price,
                   avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 3.0, 640000, ?, ?, ?)
                """,
                (
                    ticker,
                    state,
                    size,
                    entry,
                    _target(entry),
                    _stop(entry),
                    thesis,
                    NOW_ISO,
                    NOW_ISO,
                ),
            )
            queue_ids[ticker] = int(cur.lastrowid)

        # Journal — multi-month history for scenario visualizer + current month
        # June 2026: strong MSFT round trip
        insert_trade(
            conn,
            ticker="MSFT",
            side="BUY",
            shares=10,
            price=400.0,
            fee=7.0,
            executed_at="2026-06-15T14:00:00+00:00",
            notes="Demo Jun buy",
        )
        insert_trade(
            conn,
            ticker="MSFT",
            side="SELL",
            shares=10,
            price=404.52,
            fee=7.0,
            executed_at="2026-06-15T15:00:00+00:00",
            notes="Demo Jun sell at +1.13%",
        )
        # July 2026: smaller AMD round trip
        insert_trade(
            conn,
            ticker="AMD",
            side="BUY",
            shares=20,
            price=150.0,
            fee=7.0,
            executed_at="2026-07-20T14:00:00+00:00",
            notes="Demo Jul buy",
        )
        insert_trade(
            conn,
            ticker="AMD",
            side="SELL",
            shares=20,
            price=151.70,
            fee=7.0,
            executed_at="2026-07-20T15:00:00+00:00",
            notes="Demo Jul sell",
        )
        # August 2026: AAPL round trip + NVDA open
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100.0,
            fee=7.0,
            executed_at=TRADE_TIME,
            notes="Demo buy",
            queue_id=queue_ids["AAPL"],
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=101.13,
            fee=7.0,
            executed_at=TRADE_TIME,
            notes="Demo sell at target",
            queue_id=queue_ids["AAPL"],
        )
        insert_trade(
            conn,
            ticker="NVDA",
            side="BUY",
            shares=50,
            price=100.0,
            fee=7.0,
            executed_at=TRADE_TIME,
            notes="Demo NVDA entry",
            queue_id=queue_ids["NVDA"],
        )

        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES ('tax_reserve_rate', '0.25')"
        )

        conn.commit()

    return path


def expected_demo_summary() -> dict:
    """Known values after seed — used by verification tests."""
    # AAPL: gross 11.3 - fees 14 = -2.7
    aapl_pnl = (101.13 - 100.0) * 10 - 14.0
    # Cash: 10000 - 1007 (AAPL buy) + 1004.3 (AAPL sell) - 5007 (NVDA buy) = 4990.3
    nvda_cost = 50 * 100 + 7
    msft_jun = (10 * 400 + 7) - (10 * 404.52 - 7)
    amd_jul = (20 * 150 + 7) - (20 * 151.70 - 7)
    cash = (
        ORIGINAL_BASIS
        - msft_jun
        - amd_jul
        - (10 * 100 + 7)
        + (10 * 101.13 - 7)
        - nvda_cost
    )
    # After Jun+Jul round trips (before Aug): MSFT net ~31.2, AMD net ~20.0
    jun_net = (404.52 - 400.0) * 10 - 14.0
    jul_net = (151.70 - 150.0) * 20 - 14.0
    return {
        "month_key": MONTH_KEY,
        "monthly_realized_net": aapl_pnl,
        "tradable_cash": cash,
        "queue_count": 5,
        "journal_count": 7,
        "regime_ok": True,
        "vix": 18.25,
        "timeline_months": 4,  # start + Jun + Jul + Aug
        "jun_realized_net": jun_net,
        "jul_realized_net": jul_net,
    }
```


---

<a id="src-investment_agent-dollar_target-py"></a>
## `src/investment_agent/dollar_target.py`

```python
"""Dollar-target prediction — Growth Plan $ net goal from historical open→high.

Uses daily OHLCV bars with **open as entry proxy** (same as period screener and
intraday backtest). Deploy size and net target follow ``daily_profit_target()``.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
)
from investment_agent.strategy import STOP_PCT

# Minimum historical open→high hit rate to treat as reliably reachable (tradability caution)
MIN_DOLLAR_HIT_RATE_PCT = 40.0
# Expected net at typical day-high must reach this fraction of today's goal for GO
MIN_EXPECTED_NET_RATIO = 0.95
DEFAULT_LOOKBACK_DAYS = 14

# Stricter gates for period ranking — smaller pool, stronger $-goal alignment
MIN_RANK_DOLLAR_HIT_RATE_PCT = 40.0
MIN_RANK_AVG_NET_RATIO = 0.90
MIN_RANK_DOLLAR_DAYS = 2


def passes_dollar_rank_gate(
    *,
    dollar_hit_rate_pct: float,
    avg_net_at_high: float,
    net_target: float,
    days_screened: int,
    min_hit_rate_pct: float = MIN_RANK_DOLLAR_HIT_RATE_PCT,
    min_avg_ratio: float = MIN_RANK_AVG_NET_RATIO,
    min_days: int = MIN_RANK_DOLLAR_DAYS,
) -> bool:
    """True when historical Step 3 days support today's scaled Growth Plan net goal."""
    if net_target <= 0 or days_screened < min_days:
        return False
    if dollar_hit_rate_pct < min_hit_rate_pct:
        return False
    return avg_net_at_high >= net_target * min_avg_ratio


@dataclass(frozen=True)
class DollarDayBar:
    open: float
    high: float
    low: float


def shares_for_deploy(
    entry_price: float,
    deploy_dollar: float,
    *,
    buy_fee: float = DEFAULT_BUY_FEE,
) -> int:
    if entry_price <= 0 or deploy_dollar <= buy_fee:
        return 0
    return int((deploy_dollar - buy_fee) / entry_price)


def net_pnl_at_price(
    *,
    entry_price: float,
    exit_price: float,
    shares: int,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    if shares <= 0 or entry_price <= 0:
        return 0.0
    return round(shares * (exit_price - entry_price) - buy_fee - sell_fee, 2)


def target_sell_price(
    *,
    entry_price: float,
    deploy_dollar: float,
    net_target: float | None = None,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float | None:
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    shares = shares_for_deploy(entry_price, deploy_dollar, buy_fee=buy_fee)
    if shares <= 0 or goal <= 0:
        return None
    return sell_price_for_net_target(
        entry_price=entry_price,
        shares=shares,
        net_target=goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )


def simulate_dollar_outcome(
    open_px: float,
    high: float,
    low: float,
    *,
    deploy_dollar: float,
    net_target: float | None = None,
    stop_pct: float = STOP_PCT,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> str:
    """Daily-bar approximation: did open→high reach the Growth Plan sell price?"""
    if open_px <= 0:
        return "invalid"
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    shares = shares_for_deploy(open_px, deploy_dollar, buy_fee=buy_fee)
    if shares <= 0:
        return "invalid"
    target_px = sell_price_for_net_target(
        entry_price=open_px,
        shares=shares,
        net_target=goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )
    stop_px = open_px * (1 - stop_pct / 100)
    if high >= target_px:
        return "target"
    if low <= stop_px:
        return "stop"
    return "neither"


def net_at_high_from_open(
    open_px: float,
    high: float,
    *,
    deploy_dollar: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    shares = shares_for_deploy(open_px, deploy_dollar, buy_fee=buy_fee)
    return net_pnl_at_price(
        entry_price=open_px,
        exit_price=high,
        shares=shares,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )


def estimate_net_at_typical_high(
    entry_price: float,
    avg_range_pct: float,
    *,
    deploy_dollar: float,
    net_target: float | None = None,
) -> float:
    """Estimate net if price reaches open + half the typical daily range (upside leg)."""
    if entry_price <= 0 or avg_range_pct <= 0:
        return 0.0
    est_high = entry_price * (1 + (avg_range_pct / 2) / 100)
    return net_at_high_from_open(
        entry_price,
        est_high,
        deploy_dollar=deploy_dollar,
    )


@dataclass
class DollarHistoryStats:
    days_evaluated: int
    dollar_targets: int
    dollar_stops: int
    dollar_neither: int
    dollar_hit_rate_pct: float
    avg_net_at_high: float
    median_net_at_high: float
    max_net_at_high: float
    min_net_at_high: float

    def to_dict(self) -> dict:
        return {
            "days_evaluated": self.days_evaluated,
            "dollar_targets": self.dollar_targets,
            "dollar_stops": self.dollar_stops,
            "dollar_neither": self.dollar_neither,
            "dollar_hit_rate_pct": self.dollar_hit_rate_pct,
            "avg_net_at_high": self.avg_net_at_high,
            "median_net_at_high": self.median_net_at_high,
            "max_net_at_high": self.max_net_at_high,
            "min_net_at_high": self.min_net_at_high,
        }


def evaluate_dollar_history(
    bars: list[DollarDayBar],
    *,
    deploy_dollar: float,
    net_target: float | None = None,
    avg_range_pct: float | None = None,
) -> DollarHistoryStats:
    """Simulate Growth Plan outcomes (pullback limit entry when avg_range_pct set)."""
    from investment_agent.pullback_entry import (
        net_at_high_after_pullback_fill,
        simulate_pullback_dollar_outcome,
    )

    targets = stops = neither = 0
    nets: list[float] = []

    for bar in bars:
        if bar.open <= 0:
            continue
        if avg_range_pct is not None and avg_range_pct > 0:
            outcome = simulate_pullback_dollar_outcome(
                bar.open,
                bar.high,
                bar.low,
                deploy_dollar=deploy_dollar,
                avg_range_pct=avg_range_pct,
                net_target=net_target,
            )
            net_high = net_at_high_after_pullback_fill(
                bar.open,
                bar.high,
                bar.low,
                deploy_dollar=deploy_dollar,
                avg_range_pct=avg_range_pct,
            )
        else:
            outcome = simulate_dollar_outcome(
                bar.open,
                bar.high,
                bar.low,
                deploy_dollar=deploy_dollar,
                net_target=net_target,
            )
            net_high = net_at_high_from_open(bar.open, bar.high, deploy_dollar=deploy_dollar)
        if outcome == "target":
            targets += 1
        elif outcome == "stop":
            stops += 1
        elif outcome in ("neither", "no_fill"):
            neither += 1
        else:
            continue
        if net_high > 0:
            nets.append(net_high)

    days = targets + stops + neither
    decided = targets + stops
    hit_rate = round(100.0 * targets / max(decided, 1), 1) if decided else 0.0

    if nets:
        sorted_nets = sorted(nets)
        mid = len(sorted_nets) // 2
        median = (
            sorted_nets[mid]
            if len(sorted_nets) % 2
            else (sorted_nets[mid - 1] + sorted_nets[mid]) / 2
        )
        return DollarHistoryStats(
            days_evaluated=days,
            dollar_targets=targets,
            dollar_stops=stops,
            dollar_neither=neither,
            dollar_hit_rate_pct=hit_rate,
            avg_net_at_high=round(sum(nets) / len(nets), 2) if nets else 0.0,
            median_net_at_high=round(median, 2),
            max_net_at_high=round(max(nets), 2),
            min_net_at_high=round(min(nets), 2),
        )

    return DollarHistoryStats(
        days_evaluated=0,
        dollar_targets=0,
        dollar_stops=0,
        dollar_neither=0,
        dollar_hit_rate_pct=0.0,
        avg_net_at_high=0.0,
        median_net_at_high=0.0,
        max_net_at_high=0.0,
        min_net_at_high=0.0,
    )


def assess_dollar_reachability(
    *,
    entry_price: float,
    deploy_dollar: float,
    net_target: float | None = None,
    avg_range_pct: float | None = None,
    history: DollarHistoryStats | None = None,
) -> dict:
    """Predict whether today's $ goal is reachable from this entry using history."""
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    fees = round_trip_fees()
    shares = shares_for_deploy(entry_price, deploy_dollar)
    target_px = target_sell_price(
        entry_price=entry_price,
        deploy_dollar=deploy_dollar,
        net_target=goal,
    )

    expected_net = None
    if avg_range_pct is not None and avg_range_pct > 0:
        expected_net = estimate_net_at_typical_high(
            entry_price,
            avg_range_pct,
            deploy_dollar=deploy_dollar,
            net_target=goal,
        )

    hist_avg = history.avg_net_at_high if history and history.days_evaluated else None
    hist_hit = history.dollar_hit_rate_pct if history and history.days_evaluated else None

    blockers: list[str] = []
    cautions: list[str] = []
    checks: list[dict] = []

    def add(name: str, ok: bool | None, message: str) -> None:
        checks.append({"name": name, "ok": ok, "message": message})

    if expected_net is not None:
        ratio = expected_net / goal if goal > 0 else 0.0
        if ratio < MIN_EXPECTED_NET_RATIO:
            blockers.append(
                f"Typical day high nets ~${expected_net:.0f} from this entry "
                f"(need ${goal:.0f}) — range too tight for Growth Plan"
            )
            add(
                "Expected net at typical high",
                False,
                f"~${expected_net:.0f} at avg swing high vs ${goal:.0f} goal ({ratio:.0%})",
            )
        elif ratio < 1.0:
            cautions.append(
                f"Typical high only ~${expected_net:.0f} net — marginal for ${goal:.0f}"
            )
            add(
                "Expected net at typical high",
                None,
                f"~${expected_net:.0f} at avg swing high vs ${goal:.0f} goal",
            )
        else:
            add(
                "Expected net at typical high",
                True,
                f"~${expected_net:.0f} at avg swing high vs ${goal:.0f} goal",
            )

    if hist_avg is not None and hist_hit is not None:
        add(
            "Historical net at high",
            True if hist_avg >= goal * MIN_EXPECTED_NET_RATIO else None,
            f"Avg ${hist_avg:.0f} net at day high over {history.days_evaluated}d "
            f"({hist_hit:.0f}% hit ${goal:.0f})",
        )
        if hist_hit < MIN_DOLLAR_HIT_RATE_PCT and hist_avg < goal * MIN_EXPECTED_NET_RATIO:
            blockers.append(
                f"Historical open→high hit ${goal:.0f} only {hist_hit:.0f}% of days "
                f"(avg net ${hist_avg:.0f} at high)"
            )
            checks[-1]["ok"] = False
        elif hist_hit < MIN_DOLLAR_HIT_RATE_PCT:
            cautions.append(
                f"Historical ${goal:.0f} hit rate only {hist_hit:.0f}% — lower confidence"
            )

    if blockers:
        verdict = "NOT_REACHABLE"
        headline = f"Unlikely to reach ${goal:.0f} net from this entry"
        detail = blockers[0]
    elif cautions:
        verdict = "MARGINAL"
        headline = f"Marginal for ${goal:.0f} net — history suggests tight upside"
        detail = cautions[0]
    else:
        verdict = "REACHABLE"
        headline = f"Historical range supports ${goal:.0f} net goal"
        detail = (
            f"Typical high ~${expected_net:.0f} net"
            if expected_net is not None
            else f"{hist_hit:.0f}% historical hit rate" if hist_hit is not None else "OK"
        )

    return {
        "verdict": verdict,
        "headline": headline,
        "detail": detail,
        "checks": checks,
        "blockers": blockers,
        "cautions": cautions,
        "net_target": goal,
        "expected_net_at_typical_high": expected_net,
        "historical_avg_net_at_high": hist_avg,
        "dollar_hit_rate_pct": hist_hit,
        "dollar_history_days": history.days_evaluated if history else 0,
        "target_sell_price": round(target_px, 2) if target_px else None,
        "shares": shares,
        "fees_round_trip": fees,
    }


def load_dollar_history(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    deploy_dollar: float,
    net_target: float | None = None,
    avg_range_pct: float | None = None,
) -> DollarHistoryStats:
    """Load recent daily bars and evaluate pullback limit dollar outcomes."""
    from investment_agent.db import get_ohlcv_bars

    end = end_date or datetime.now().strftime("%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    start = (end_dt - timedelta(days=lookback_days * 2)).strftime("%Y-%m-%d")
    rows = get_ohlcv_bars(conn, ticker.upper(), start_date=start, end_date=end)
    if not rows:
        return evaluate_dollar_history(
            [],
            deploy_dollar=deploy_dollar,
            net_target=net_target,
            avg_range_pct=avg_range_pct,
        )

    history_rows = [r for r in rows if r["date"] < end][-lookback_days:]
    bars = [
        DollarDayBar(
            open=float(r["open"]),
            high=float(r["high"]),
            low=float(r["low"]),
        )
        for r in history_rows
        if r["open"] and r["high"] and r["low"]
    ]
    return evaluate_dollar_history(
        bars,
        deploy_dollar=deploy_dollar,
        net_target=net_target,
        avg_range_pct=avg_range_pct,
    )
```


---

<a id="src-investment_agent-finance-py"></a>
## `src/investment_agent/finance.py`

```python
"""Financial model: fees, goal progress, month-end sweeps (v3)."""

from __future__ import annotations

from dataclasses import dataclass

# Defaults from approved product spec v3
ORIGINAL_BASIS = 10_000.0
GOAL_ACCOUNT_VALUE = 5_000_000.0
DEFAULT_BUY_FEE = 7.0
DEFAULT_SELL_FEE = 7.0
DEFAULT_TAX_RESERVE_RATE = 0.25
DEFAULT_MGMT_SWEEP_RATE = 0.10

# Scalable daily net profit target (v3.1 operating plan)
DAILY_TARGET_BASE = 150.0  # at $10K basis
DAILY_TARGET_STEP = 50.0  # added per tier
DAILY_TARGET_EVERY = 5_000.0  # balance step between tiers
DAILY_TARGET_MILESTONE_GOAL = 350.0  # full daily goal at $20K+
DAILY_TARGET_MILESTONE_AT = 20_000.0


@dataclass(frozen=True)
class MonthEndSweep:
    """Sweeps applied only when monthly realized net profit is positive."""

    monthly_realized_net: float
    management_sweep: float
    tax_sweep: float
    total_sweep: float

    @property
    def applies(self) -> bool:
        return self.monthly_realized_net > 0


def round_trip_fees(
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    return buy_fee + sell_fee


def sell_price_for_net_target(
    *,
    entry_price: float,
    shares: int,
    net_target: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    """Limit price where selling ``shares`` nets ``net_target`` after round-trip fees."""
    if entry_price <= 0 or shares <= 0 or net_target <= 0:
        return entry_price
    gross_needed = net_target + buy_fee + sell_fee
    return entry_price + gross_needed / shares


def target_move_pct(entry_price: float, target_price: float) -> float:
    if entry_price <= 0:
        return 0.0
    return ((target_price - entry_price) / entry_price) * 100.0


def goal_progress_pct(
    tradable_balance: float,
    goal: float = GOAL_ACCOUNT_VALUE,
) -> float:
    if goal <= 0:
        return 0.0
    return (tradable_balance / goal) * 100.0


def compute_month_end_sweep(
    monthly_realized_net: float,
    tax_rate: float = DEFAULT_TAX_RESERVE_RATE,
    mgmt_rate: float = DEFAULT_MGMT_SWEEP_RATE,
) -> MonthEndSweep:
    """
    10% management + tax reserve on positive monthly realized net only.
    During the month, tradable cash is unchanged by this calculation;
    sweeps are applied at month-end on the trading account.
    """
    if monthly_realized_net <= 0:
        return MonthEndSweep(
            monthly_realized_net=monthly_realized_net,
            management_sweep=0.0,
            tax_sweep=0.0,
            total_sweep=0.0,
        )
    mgmt = monthly_realized_net * mgmt_rate
    tax = monthly_realized_net * tax_rate
    return MonthEndSweep(
        monthly_realized_net=monthly_realized_net,
        management_sweep=mgmt,
        tax_sweep=tax,
        total_sweep=mgmt + tax,
    )


def tradable_after_sweep(
    tradable_balance_before_sweep: float,
    sweep: MonthEndSweep,
) -> float:
    return tradable_balance_before_sweep - sweep.total_sweep


def daily_profit_target(
    tradable_balance: float,
    *,
    base: float = DAILY_TARGET_BASE,
    step: float = DAILY_TARGET_STEP,
    every: float = DAILY_TARGET_EVERY,
    basis: float = ORIGINAL_BASIS,
) -> float:
    """
    Daily net profit goal: $150 at $10K, +$50 for each additional $5K balance.
    $10K→$150, $15K→$200, $20K→$250, … reaching $350/day at $20K in the scaling example
    (use milestone note when marketing the $350 tier at $20K).
    """
    tiers = max(int((tradable_balance - basis) // every), 0)
    return base + tiers * step


def growth_plan_milestones(
    *,
    basis: float = ORIGINAL_BASIS,
    step_balance: float = DAILY_TARGET_EVERY,
    max_balance: float = 50_000.0,
) -> list[dict]:
    """Balance tiers and daily targets for dashboard growth table."""
    rows: list[dict] = []
    balance = basis
    while balance <= max_balance:
        rows.append(
            {
                "balance_at_least": balance,
                "daily_target": daily_profit_target(balance),
            }
        )
        balance += step_balance
    return rows


def next_growth_tier(tradable_balance: float) -> dict:
    """Current daily target and the next balance milestone."""
    tiers = max(int((tradable_balance - ORIGINAL_BASIS) // DAILY_TARGET_EVERY), 0)
    next_balance = ORIGINAL_BASIS + (tiers + 1) * DAILY_TARGET_EVERY
    return {
        "current_daily_target": daily_profit_target(tradable_balance),
        "current_tier_balance": ORIGINAL_BASIS + tiers * DAILY_TARGET_EVERY,
        "next_balance": next_balance,
        "next_daily_target": daily_profit_target(next_balance),
        "amount_to_next_tier": max(round(next_balance - tradable_balance, 2), 0.0),
        "milestone_daily_350_at": DAILY_TARGET_MILESTONE_AT,
    }
```


---

<a id="src-investment_agent-historical-py"></a>
## `src/investment_agent/historical.py`

```python
"""Historical OHLCV analysis — limited backfill, prior-day evaluation, period screening."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from typing import Any

from investment_agent.config import Settings
from investment_agent.db import (
    connect,
    get_active_watchlist,
    get_ohlcv_bars,
    get_ohlcv_coverage,
    init_db,
    insert_ohlcv_rows,
    log_ingest,
    upsert_watchlist,
)
from investment_agent.dollar_target import net_at_high_from_open, simulate_dollar_outcome
from investment_agent.finance import ORIGINAL_BASIS, daily_profit_target
from investment_agent.pullback_entry import (
    net_at_high_after_pullback_fill,
    simulate_pullback_dollar_outcome,
)
from investment_agent.liquidity import DailyBar, compute_liquidity_metrics
from investment_agent.providers.yfinance_bars import get_daily_bars
from investment_agent.strategy import REGIME_ONLY_TICKERS, STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")
MIN_HISTORY_BARS = 5


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _prior_calendar_day(day: str) -> str:
    dt = datetime.strptime(day, "%Y-%m-%d")
    return (dt - timedelta(days=1)).strftime("%Y-%m-%d")


def open_based_range_pct(open_px: float, high: float, low: float) -> float:
    if open_px <= 0:
        return 0.0
    return ((high - low) / open_px) * 100.0


def _rows_to_daily_bars(rows: list[sqlite3.Row]) -> list[DailyBar]:
    return [
        DailyBar(
            high=float(r["high"]),
            low=float(r["low"]),
            close=float(r["close"]),
            volume=int(r["volume"]),
        )
        for r in rows
    ]


def simulate_intraday_outcome(
    open_px: float,
    high: float,
    low: float,
    *,
    target_pct: float = TARGET_PCT,
    stop_pct: float = STOP_PCT,
) -> str:
    """Daily-bar approximation: target if high reached, else stop if low breached."""
    if open_px <= 0:
        return "invalid"
    target = open_px * (1 + target_pct / 100)
    stop = open_px * (1 - stop_pct / 100)
    if high >= target:
        return "target"
    if low <= stop:
        return "stop"
    return "neither"


def _latest_stored_trading_date(conn: sqlite3.Connection, before: str | None = None) -> str | None:
    clause = "WHERE date < ?" if before else ""
    params: tuple[Any, ...] = (before,) if before else ()
    row = conn.execute(
        f"SELECT MAX(date) AS d FROM ohlcv_daily {clause}",
        params,
    ).fetchone()
    return row["d"] if row and row["d"] else None


def evaluate_trading_day(
    conn: sqlite3.Connection,
    eval_date: str,
    *,
    tradable_cash: float = ORIGINAL_BASIS,
) -> dict:
    """Compare predicted metrics (bars before eval_date) vs actual bar on eval_date."""
    net_target = daily_profit_target(tradable_cash)
    tickers = [t for t in get_active_watchlist(conn) if t not in REGIME_ONLY_TICKERS]
    ticker_rows: list[dict] = []
    screened: list[dict] = []

    for ticker in tickers:
        bars = get_ohlcv_bars(conn, ticker, end_date=eval_date)
        if not bars:
            continue
        day_row = next((b for b in bars if b["date"] == eval_date), None)
        if day_row is None:
            continue
        history = [b for b in bars if b["date"] < eval_date]
        if len(history) < MIN_HISTORY_BARS:
            continue

        metrics = compute_liquidity_metrics(
            _rows_to_daily_bars(history),
            tradable_cash=tradable_cash,
        )
        open_px = float(day_row["open"])
        high = float(day_row["high"])
        low = float(day_row["low"])
        close = float(day_row["close"])
        actual_range = open_based_range_pct(open_px, high, low)
        would_screen = metrics.meets_liquidity_min and metrics.near_swing_target
        outcome = (
            simulate_intraday_outcome(open_px, high, low)
            if would_screen
            else None
        )
        dollar_outcome = (
            simulate_pullback_dollar_outcome(
                open_px,
                high,
                low,
                deploy_dollar=tradable_cash,
                avg_range_pct=metrics.avg_range_pct,
                net_target=net_target,
            )
            if would_screen
            else None
        )
        net_at_high = (
            net_at_high_after_pullback_fill(
                open_px,
                high,
                low,
                deploy_dollar=tradable_cash,
                avg_range_pct=metrics.avg_range_pct,
            )
            if would_screen
            else None
        )

        row = {
            "ticker": ticker,
            "eval_date": eval_date,
            "open": open_px,
            "high": high,
            "low": low,
            "close": close,
            "predicted_avg_range_pct": round(metrics.avg_range_pct, 2),
            "actual_range_pct": round(actual_range, 2),
            "range_delta_pct": round(actual_range - metrics.avg_range_pct, 2),
            "meets_liquidity": metrics.meets_liquidity_min,
            "near_swing_target": metrics.near_swing_target,
            "would_screen": would_screen,
            "simulated_outcome": outcome,
            "dollar_outcome": dollar_outcome,
            "net_at_high": round(net_at_high, 2) if net_at_high is not None else None,
            "liquidity_cap": round(metrics.liquidity_cap, 2),
        }
        ticker_rows.append(row)
        if would_screen:
            screened.append(row)

    targets = sum(1 for r in screened if r["simulated_outcome"] == "target")
    stops = sum(1 for r in screened if r["simulated_outcome"] == "stop")
    neither = sum(1 for r in screened if r["simulated_outcome"] == "neither")
    dollar_targets = sum(1 for r in screened if r["dollar_outcome"] == "target")
    dollar_stops = sum(1 for r in screened if r["dollar_outcome"] == "stop")
    dollar_neither = sum(
        1 for r in screened if r["dollar_outcome"] in ("neither", "no_fill")
    )
    dollar_no_fill = sum(1 for r in screened if r["dollar_outcome"] == "no_fill")

    return {
        "eval_date": eval_date,
        "tickers_evaluated": len(ticker_rows),
        "screened_matches": screened,
        "all_tickers": ticker_rows,
        "summary": {
            "screened_count": len(screened),
            "simulated_targets": targets,
            "simulated_stops": stops,
            "simulated_neither": neither,
            "dollar_targets": dollar_targets,
            "dollar_stops": dollar_stops,
            "dollar_neither": dollar_neither,
            "dollar_no_fill": dollar_no_fill,
            "dollar_hit_rate_pct": round(
                100.0 * dollar_targets / max(dollar_targets + dollar_stops, 1),
                1,
            ),
            "avg_range_delta_pct": round(
                sum(r["range_delta_pct"] for r in ticker_rows) / len(ticker_rows),
                2,
            )
            if ticker_rows
            else None,
        },
    }


def evaluate_prior_day(
    conn: sqlite3.Connection,
    *,
    tradable_cash: float = ORIGINAL_BASIS,
    reference_date: str | None = None,
) -> dict | None:
    """Evaluate the most recent complete trading day before reference_date (default: today ET)."""
    ref = reference_date or _today_et()
    eval_date = _latest_stored_trading_date(conn, before=ref)
    if not eval_date:
        eval_date = _prior_calendar_day(ref)
    if not eval_date:
        return None
    sample = conn.execute(
        "SELECT 1 FROM ohlcv_daily WHERE date = ? LIMIT 1",
        (eval_date,),
    ).fetchone()
    if not sample:
        return None
    result = evaluate_trading_day(conn, eval_date, tradable_cash=tradable_cash)
    result["reference_date"] = ref
    result["is_prior_day"] = eval_date == _prior_calendar_day(ref)
    return result


def build_historical_summary(conn: sqlite3.Connection) -> dict:
    coverage = get_ohlcv_coverage(conn)
    if not coverage:
        return {
            "has_data": False,
            "ticker_count": 0,
            "coverage": [],
            "earliest_date": None,
            "latest_date": None,
            "total_bars": 0,
        }
    earliest = min(c["first_date"] for c in coverage)
    latest = max(c["last_date"] for c in coverage)
    total = sum(c["bar_count"] for c in coverage)
    return {
        "has_data": True,
        "ticker_count": len(coverage),
        "coverage": coverage,
        "earliest_date": earliest,
        "latest_date": latest,
        "total_bars": total,
    }


def pull_historical_data(
    settings: Settings | None,
    *,
    tickers: list[str] | None = None,
    db_path=None,
    lookback_days: int = 60,
    use_active_watchlist: bool = True,
) -> dict:
    """Fetch limited daily OHLCV history into ohlcv_daily (yfinance, free tier)."""
    path = init_db(db_path)
    summary: dict = {
        "db_path": str(path),
        "lookback_days": lookback_days,
        "bars_inserted": 0,
        "errors": [],
        "tickers_processed": 0,
    }

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row

        if tickers is not None:
            symbols = [t.upper() for t in tickers]
            upsert_watchlist(conn, symbols)
        elif use_active_watchlist:
            symbols = get_active_watchlist(conn)
            if not symbols:
                from investment_agent.ingest import DEFAULT_TICKERS

                symbols = [t.upper() for t in DEFAULT_TICKERS]
                upsert_watchlist(conn, symbols)
        else:
            from investment_agent.ingest import DEFAULT_TICKERS

            symbols = [t.upper() for t in DEFAULT_TICKERS]
            upsert_watchlist(conn, symbols)

        summary["tickers"] = symbols

        for symbol in symbols:
            summary["tickers_processed"] += 1
            try:
                candles = get_daily_bars(symbol, lookback_days=lookback_days)
                count = insert_ohlcv_rows(conn, candles)
                summary["bars_inserted"] += count
                log_ingest(conn, "historical", "ok", f"{symbol}: {count} bars")
            except Exception as exc:
                log_ingest(conn, "historical", "error", f"{symbol}: {exc}")
                summary["errors"].append(f"{symbol}: {exc}")

        conn.commit()

    summary["error_count"] = len(summary["errors"])
    summary["ok"] = summary["error_count"] == 0
    with connect(path) as conn:
        summary["coverage"] = build_historical_summary(conn)
        from investment_agent.watchlist import compute_universe_stats

        summary["universe_stats"] = compute_universe_stats(conn)
    return summary


def evaluate_period(
    conn: sqlite3.Connection,
    start_date: str,
    end_date: str,
    *,
    tradable_cash: float = ORIGINAL_BASIS,
    trading_dates: list[str] | None = None,
) -> dict:
    """Evaluate each trading day in range that has OHLCV data."""
    if trading_dates is not None:
        dates = sorted(trading_dates)
    else:
        dates = [
            row["date"]
            for row in conn.execute(
                """
                SELECT DISTINCT date FROM ohlcv_daily
                WHERE date >= ? AND date <= ?
                ORDER BY date ASC
                """,
                (start_date, end_date),
            ).fetchall()
        ]
    days: list[dict] = []
    total_dollar_targets = 0
    total_dollar_stops = 0
    for date in dates:
        day_eval = evaluate_trading_day(conn, date, tradable_cash=tradable_cash)
        total_dollar_targets += day_eval["summary"]["dollar_targets"]
        total_dollar_stops += day_eval["summary"]["dollar_stops"]
        days.append(
            {
                "date": date,
                "screened_count": day_eval["summary"]["screened_count"],
                "simulated_targets": day_eval["summary"]["simulated_targets"],
                "simulated_stops": day_eval["summary"]["simulated_stops"],
                "dollar_targets": day_eval["summary"]["dollar_targets"],
                "dollar_stops": day_eval["summary"]["dollar_stops"],
                "matches": [
                    {
                        "ticker": m["ticker"],
                        "outcome": m["simulated_outcome"],
                        "dollar_outcome": m.get("dollar_outcome"),
                        "net_at_high": m.get("net_at_high"),
                        "actual_range_pct": m["actual_range_pct"],
                    }
                    for m in day_eval["screened_matches"]
                ],
            }
        )

    total_targets = sum(d["simulated_targets"] for d in days)
    total_stops = sum(d["simulated_stops"] for d in days)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "days_evaluated": len(days),
        "days": days,
        "summary": {
            "total_screened_setups": sum(d["screened_count"] for d in days),
            "total_simulated_targets": total_targets,
            "total_simulated_stops": total_stops,
            "total_dollar_targets": total_dollar_targets,
            "total_dollar_stops": total_dollar_stops,
            "target_rate_pct": round(
                100.0 * total_targets / max(total_targets + total_stops, 1),
                1,
            ),
            "dollar_target_rate_pct": round(
                100.0 * total_dollar_targets / max(total_dollar_targets + total_dollar_stops, 1),
                1,
            ),
        },
    }
```


---

<a id="src-investment_agent-ingest-py"></a>
## `src/investment_agent/ingest.py`

```python
"""Phase 1 ingestion orchestration — FRED + Finnhub quotes + yfinance bars, no Claude."""

from __future__ import annotations

import gc
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from investment_agent.config import Settings
from investment_agent.db import (
    connect,
    get_active_watchlist,
    init_db,
    insert_macro,
    insert_ohlcv_rows,
    insert_quote,
    insert_regime_snapshot,
    insert_ticker_metrics,
    log_ingest,
    upsert_watchlist,
)
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.liquidity import DailyBar, compute_liquidity_metrics
from investment_agent.providers.fred import fetch_vix, utc_now_iso as fred_now
from investment_agent.providers.finnhub import FinnhubClient, utc_now_iso as fh_now
from investment_agent.providers.yfinance_bars import get_daily_bars
from investment_agent.regime import (
    REGIME_SYMBOLS,
    evaluate_regime,
    index_quote_from_finnhub,
)
from investment_agent.screen_actions import (
    ACTION_DAILY_INGEST,
    ACTION_FULL_INGEST,
    record_screen_action,
)

# Commit + GC every N symbols during large watchlist ingests (S&P 500 ~537 tickers).
_BARS_BATCH_SIZE = 25

# Regime indices + starter watchlist (expand in Phase 2 screener)
DEFAULT_TICKERS = [
    "SPY",
    "DIA",
    "QQQ",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "META",
    "TSLA",
    "IWM",
]

MACRO_SERIES = ["VIXCLS"]


def _parse_iso_age_hours(iso_ts: str | None) -> float | None:
    if not iso_ts:
        return None
    try:
        ts = iso_ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return age.total_seconds() / 3600.0
    except ValueError:
        return None


def _needs_quote_refresh(
    conn: sqlite3.Connection,
    symbol: str,
    *,
    stale_hours: float,
    force_symbols: set[str] | None = None,
) -> bool:
    if force_symbols and symbol in force_symbols:
        return True
    row = conn.execute(
        """
        SELECT captured_at FROM quotes
        WHERE ticker = ?
        ORDER BY captured_at DESC
        LIMIT 1
        """,
        (symbol,),
    ).fetchone()
    age = _parse_iso_age_hours(row["captured_at"] if row else None)
    return age is None or age >= stale_hours


def _needs_bars_refresh(
    conn: sqlite3.Connection,
    symbol: str,
    *,
    stale_hours: float,
    force_symbols: set[str] | None = None,
) -> bool:
    if force_symbols and symbol in force_symbols:
        return True
    metrics = conn.execute(
        """
        SELECT computed_at FROM ticker_metrics
        WHERE ticker = ?
        ORDER BY computed_at DESC
        LIMIT 1
        """,
        (symbol,),
    ).fetchone()
    age = _parse_iso_age_hours(metrics["computed_at"] if metrics else None)
    return age is None or age >= stale_hours


def run_ingest(
    settings: Settings,
    tickers: list[str] | None = None,
    db_path: Path | None = None,
    lookback_days: int = 60,
    tradable_cash: float = ORIGINAL_BASIS,
    incremental: bool = False,
    stale_hours: float = 20.0,
    quote_stale_hours: float | None = None,
    bar_stale_hours: float | None = None,
) -> dict:
    """Fetch macro + quotes + daily bars; compute liquidity/range metrics + regime."""
    from investment_agent.db_maintenance import acquire_ingest_lock, release_ingest_lock

    acquire_ingest_lock(detail="run_ingest")
    try:
        return _run_ingest_body(
            settings,
            tickers=tickers,
            db_path=db_path,
            lookback_days=lookback_days,
            tradable_cash=tradable_cash,
            incremental=incremental,
            stale_hours=stale_hours,
            quote_stale_hours=quote_stale_hours,
            bar_stale_hours=bar_stale_hours,
        )
    finally:
        release_ingest_lock()


def _run_ingest_body(
    settings: Settings,
    tickers: list[str] | None = None,
    db_path: Path | None = None,
    lookback_days: int = 60,
    tradable_cash: float = ORIGINAL_BASIS,
    incremental: bool = False,
    stale_hours: float = 20.0,
    quote_stale_hours: float | None = None,
    bar_stale_hours: float | None = None,
) -> dict:
    """Internal ingest implementation."""
    q_stale = stale_hours if quote_stale_hours is None else quote_stale_hours
    b_stale = stale_hours if bar_stale_hours is None else bar_stale_hours
    path = init_db(db_path)
    if tickers is not None:
        symbols = [t.upper() for t in tickers]
    else:
        with connect(path) as conn:
            symbols = get_active_watchlist(conn)
        if not symbols:
            symbols = [t.upper() for t in DEFAULT_TICKERS]
    summary: dict = {
        "db_path": str(path),
        "tickers": symbols,
        "errors": [],
        "incremental": incremental,
        "stale_hours": stale_hours,
        "quote_stale_hours": q_stale,
        "bar_stale_hours": b_stale,
        "quotes_refreshed": 0,
        "quotes_skipped": 0,
        "bars_refreshed": 0,
        "bars_skipped": 0,
    }
    index_quotes: dict = {}
    force = set(REGIME_SYMBOLS)

    with connect(path) as conn:
        upsert_watchlist(conn, symbols)

        # --- FRED macro ---
        try:
            captured = fred_now()
            obs_date, vix = fetch_vix(settings.fred_api_key)
            insert_macro(conn, "VIXCLS", obs_date, vix, captured)
            log_ingest(conn, "fred", "ok", f"VIXCLS={vix} on {obs_date}")
            summary["vix"] = vix
        except Exception as exc:
            log_ingest(conn, "fred", "error", str(exc))
            summary["errors"].append(f"fred: {exc}")

        # --- Finnhub live quotes ---
        fh = FinnhubClient(settings.finnhub_api_key)
        try:
            for symbol in symbols:
                if incremental and not _needs_quote_refresh(
                    conn, symbol, stale_hours=q_stale, force_symbols=force
                ):
                    summary["quotes_skipped"] += 1
                    if symbol in REGIME_SYMBOLS:
                        row = conn.execute(
                            """
                            SELECT price, open, prev_close FROM quotes
                            WHERE ticker = ?
                            ORDER BY captured_at DESC
                            LIMIT 1
                            """,
                            (symbol,),
                        ).fetchone()
                        if row:
                            index_quotes[symbol] = index_quote_from_finnhub(
                                symbol,
                                {
                                    "c": row["price"],
                                    "o": row["open"] or row["price"],
                                    "pc": row["prev_close"] or row["price"],
                                },
                            )
                    continue
                try:
                    q = fh.get_quote(symbol)
                    insert_quote(
                        conn,
                        {
                            "ticker": symbol,
                            "captured_at": fh_now(),
                            "price": float(q["c"]),
                            "open": float(q.get("o") or 0) or None,
                            "high": float(q.get("h") or 0) or None,
                            "low": float(q.get("l") or 0) or None,
                            "prev_close": float(q.get("pc") or 0) or None,
                        },
                    )
                    summary["quotes_refreshed"] += 1
                    if symbol in REGIME_SYMBOLS:
                        index_quotes[symbol] = index_quote_from_finnhub(symbol, q)
                    log_ingest(conn, "finnhub", "ok", f"quote {symbol}")
                except Exception as exc:
                    log_ingest(conn, "finnhub", "error", f"quote {symbol}: {exc}")
                    summary["errors"].append(f"quote {symbol}: {exc}")
        finally:
            fh.close()

        # --- yfinance daily bars (Finnhub /stock/candle requires paid tier) ---
        bars_pending_commit = 0
        total_symbols = len(symbols)
        for idx, symbol in enumerate(symbols, start=1):
            if incremental and not _needs_bars_refresh(
                conn, symbol, stale_hours=b_stale, force_symbols=force
            ):
                summary["bars_skipped"] += 1
                continue
            try:
                candles = get_daily_bars(symbol, lookback_days=lookback_days)
                insert_ohlcv_rows(conn, candles)

                bars = [
                    DailyBar(
                        high=r["high"],
                        low=r["low"],
                        close=r["close"],
                        volume=r["volume"],
                    )
                    for r in sorted(candles, key=lambda x: x["date"])
                ]
                metrics = compute_liquidity_metrics(
                    bars, tradable_cash=tradable_cash
                )
                last_close = bars[-1].close if bars else 0.0
                last_quote_row = conn.execute(
                    """
                    SELECT price FROM quotes
                    WHERE ticker = ?
                    ORDER BY captured_at DESC
                    LIMIT 1
                    """,
                    (symbol,),
                ).fetchone()
                last_quote = (
                    float(last_quote_row["price"]) if last_quote_row else last_close
                )
                insert_ticker_metrics(
                    conn,
                    {
                        "ticker": symbol,
                        "computed_at": datetime.now(timezone.utc)
                        .replace(microsecond=0)
                        .isoformat(),
                        "adv_dollar": metrics.adv_dollar,
                        "avg_range_pct": metrics.avg_range_pct,
                        "liquidity_cap": metrics.liquidity_cap,
                        "last_close": last_close,
                        "last_quote": last_quote,
                        "meets_liquidity_min": metrics.meets_liquidity_min,
                        "near_swing_target": metrics.near_swing_target,
                    },
                )
                log_ingest(conn, "yfinance", "ok", symbol)
                summary["bars_refreshed"] += 1
                bars_pending_commit += 1
                if bars_pending_commit >= _BARS_BATCH_SIZE:
                    conn.commit()
                    bars_pending_commit = 0
                    gc.collect()
                if idx % 50 == 0 or idx == total_symbols:
                    print(
                        f"  bars progress: {idx}/{total_symbols} "
                        f"({summary['bars_refreshed']} refreshed, "
                        f"{summary['bars_skipped']} skipped, "
                        f"{len(summary['errors'])} errors)",
                        flush=True,
                    )
            except Exception as exc:
                log_ingest(conn, "yfinance", "error", f"{symbol}: {exc}")
                summary["errors"].append(f"bars {symbol}: {exc}")

        # --- Regime gate (requires SPY/DIA/QQQ quotes) ---
        if all(sym in index_quotes for sym in REGIME_SYMBOLS):
            try:
                regime = evaluate_regime(index_quotes, fh_now())
                insert_regime_snapshot(
                    conn,
                    {
                        "captured_at": regime.captured_at,
                        "spy_change_pct": regime.spy_change_pct,
                        "dia_change_pct": regime.dia_change_pct,
                        "qqq_change_pct": regime.qqq_change_pct,
                        "all_indices_down": regime.all_indices_down,
                        "block_new_longs": regime.block_new_longs,
                        "summary": regime.summary,
                    },
                )
                log_ingest(conn, "regime", "ok", regime.summary)
                summary["regime"] = {
                    "block_new_longs": regime.block_new_longs,
                    "summary": regime.summary,
                    "spy_change_pct": regime.spy_change_pct,
                    "dia_change_pct": regime.dia_change_pct,
                    "qqq_change_pct": regime.qqq_change_pct,
                }
            except Exception as exc:
                log_ingest(conn, "regime", "error", str(exc))
                summary["errors"].append(f"regime: {exc}")
        else:
            missing = [s for s in REGIME_SYMBOLS if s not in index_quotes]
            summary["errors"].append(
                f"regime: missing index quotes for {', '.join(missing)}"
            )

        conn.commit()

        action_id = ACTION_DAILY_INGEST if incremental else ACTION_FULL_INGEST
        record_screen_action(
            conn,
            action_id,
            detail=(
                f"{summary['quotes_refreshed']} quotes, {summary['bars_refreshed']} bars refreshed"
            ),
        )
        conn.commit()

    summary["error_count"] = len(summary["errors"])
    summary["ok"] = summary["error_count"] == 0
    summary["partial"] = (
        not summary["ok"]
        and (summary["bars_refreshed"] > 0 or summary["quotes_refreshed"] > 0)
    )
    return summary
```


---

<a id="src-investment_agent-journal-py"></a>
## `src/investment_agent/journal.py`

```python
"""Trade journal — manual E*TRADE fills (source of truth for cash and P&L)."""

from __future__ import annotations

import sqlite3
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE, ORIGINAL_BASIS

PT = ZoneInfo("America/Los_Angeles")


def today_pt_str() -> str:
    return datetime.now(PT).strftime("%Y-%m-%d")


def _parse_executed_at(executed_at: str) -> datetime:
    ts = executed_at.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=PT)
    return dt


def _executed_date_pt(executed_at: str) -> str:
    try:
        return _parse_executed_at(executed_at).astimezone(PT).strftime("%Y-%m-%d")
    except ValueError:
        return executed_at[:10]


def build_executed_at_pt(date_key: str, time_hm: str) -> str:
    """Combine YYYY-MM-DD and HH:MM as Pacific Time (E*TRADE audit log times)."""
    parts = time_hm.strip().split(":")
    if len(parts) < 2:
        raise ValueError("time must be HH:MM")
    hour, minute = int(parts[0]), int(parts[1])
    second = int(parts[2]) if len(parts) > 2 else 0
    y, m, d = map(int, date_key.split("-"))
    dt = datetime(y, m, d, hour, minute, second, tzinfo=PT)
    return dt.replace(microsecond=0).isoformat()


def normalize_executed_at(executed_at: str) -> str:
    """Store timezone-aware ISO; naive values are interpreted as Pacific Time."""
    return _parse_executed_at(executed_at).replace(microsecond=0).isoformat()


def resolve_executed_at(
    *,
    executed_at: str | None = None,
    executed_date: str | None = None,
    executed_time_pt: str | None = None,
) -> str | None:
    if executed_date and executed_time_pt:
        return build_executed_at_pt(executed_date, executed_time_pt)
    if executed_at:
        return normalize_executed_at(executed_at)
    return None


@dataclass(frozen=True)
class JournalEntry:
    id: int
    ticker: str
    side: str
    shares: float
    price: float
    fee: float
    executed_at: str
    notes: str | None
    queue_id: int | None


def _normalize_side(side: str) -> str:
    s = side.upper()
    if s not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    return s


def insert_trade(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    side: str,
    shares: float,
    price: float,
    fee: float | None = None,
    executed_at: str | None = None,
    notes: str | None = None,
    queue_id: int | None = None,
) -> int:
    if shares <= 0 or price <= 0:
        raise ValueError("shares and price must be positive")
    side_n = _normalize_side(side)
    default_fee = DEFAULT_BUY_FEE if side_n == "BUY" else DEFAULT_SELL_FEE
    when = (
        normalize_executed_at(executed_at)
        if executed_at
        else datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    cur = conn.execute(
        """
        INSERT INTO trade_journal
          (ticker, side, shares, price, fee, executed_at, notes, queue_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticker.upper(),
            side_n,
            shares,
            price,
            fee if fee is not None else default_fee,
            when,
            notes,
            queue_id,
        ),
    )
    return int(cur.lastrowid)


def list_trades(conn: sqlite3.Connection, limit: int = 100) -> list[JournalEntry]:
    rows = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, notes, queue_id
        FROM trade_journal
        ORDER BY executed_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [
        JournalEntry(
            id=row["id"],
            ticker=row["ticker"],
            side=row["side"],
            shares=row["shares"],
            price=row["price"],
            fee=row["fee"],
            executed_at=row["executed_at"],
            notes=row["notes"],
            queue_id=row["queue_id"],
        )
        for row in rows
    ]


def journal_cash_balance(conn: sqlite3.Connection) -> float:
    """Cash available from journal activity starting at ORIGINAL_BASIS."""
    cash = ORIGINAL_BASIS
    rows = conn.execute(
        """
        SELECT side, shares, price, fee
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()
    for row in rows:
        notional = row["shares"] * row["price"]
        if row["side"] == "BUY":
            cash -= notional + row["fee"]
        else:
            cash += notional - row["fee"]
    return cash


def compute_total_fees(conn: sqlite3.Connection) -> float:
    row = conn.execute("SELECT COALESCE(SUM(fee), 0) AS total FROM trade_journal").fetchone()
    return float(row["total"]) if row else 0.0


def compute_today_realized_net(conn: sqlite3.Connection, date_key: str | None = None) -> float:
    """FIFO matched round-trip P&L for closed trades on YYYY-MM-DD (Pacific Time)."""
    when = date_key or today_pt_str()
    rows = conn.execute(
        """
        SELECT ticker, side, shares, price, fee, executed_at
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()

    buys: dict[str, deque] = {}
    realized = 0.0

    for row in rows:
        if _executed_date_pt(row["executed_at"]) != when:
            continue
        ticker = row["ticker"]
        if row["side"] == "BUY":
            buys.setdefault(ticker, deque()).append(
                {"shares": float(row["shares"]), "price": float(row["price"]), "fee": float(row["fee"])}
            )
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        queue = buys.setdefault(ticker, deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            realized += (sell_price - buy["price"]) * matched - buy_fee - sell_fee
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    return realized


def compute_monthly_realized_net(conn: sqlite3.Connection, month_key: str) -> float:
    """FIFO matched round-trip P&L for closed trades in YYYY-MM."""
    rows = conn.execute(
        """
        SELECT ticker, side, shares, price, fee, executed_at
        FROM trade_journal
        WHERE strftime('%Y-%m', executed_at) = ?
        ORDER BY executed_at ASC, id ASC
        """,
        (month_key,),
    ).fetchall()

    buys: dict[str, deque] = {}
    realized = 0.0

    for row in rows:
        ticker = row["ticker"]
        if row["side"] == "BUY":
            buys.setdefault(ticker, deque()).append(
                {"shares": float(row["shares"]), "price": float(row["price"]), "fee": float(row["fee"])}
            )
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        queue = buys.setdefault(ticker, deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            realized += (sell_price - buy["price"]) * matched - buy_fee - sell_fee
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    return realized


def trade_to_dict(entry: JournalEntry) -> dict:
    notional = entry.shares * entry.price
    return {
        "id": entry.id,
        "ticker": entry.ticker,
        "side": entry.side,
        "shares": entry.shares,
        "price": entry.price,
        "fee": entry.fee,
        "notional": notional,
        "executed_at": entry.executed_at,
        "notes": entry.notes,
        "queue_id": entry.queue_id,
    }


def _fifo_ledger(conn: sqlite3.Connection) -> tuple[list[dict], list[dict]]:
    """Return (open_lots, completed_round_trips) via FIFO matching."""
    rows = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, queue_id
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()

    open_lots: dict[str, deque] = {}
    completed: list[dict] = []

    for row in rows:
        ticker = row["ticker"]
        if row["side"] == "BUY":
            open_lots.setdefault(ticker, deque()).append(
                {
                    "buy_id": row["id"],
                    "shares": float(row["shares"]),
                    "price": float(row["price"]),
                    "fee": float(row["fee"]),
                    "executed_at": row["executed_at"],
                    "queue_id": row["queue_id"],
                }
            )
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        sell_at = row["executed_at"]
        sell_id = row["id"]
        sell_queue_id = row["queue_id"]
        queue = open_lots.setdefault(ticker, deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            gross = (sell_price - buy["price"]) * matched
            net = gross - buy_fee - sell_fee
            completed.append(
                {
                    "ticker": ticker,
                    "shares": matched,
                    "buy_price": buy["price"],
                    "sell_price": sell_price,
                    "buy_at": buy["executed_at"],
                    "sell_at": sell_at,
                    "buy_id": buy["buy_id"],
                    "sell_id": sell_id,
                    "queue_id": buy["queue_id"] or sell_queue_id,
                    "gross_pnl": gross,
                    "net_pnl": net,
                    "buy_fee": buy_fee,
                    "sell_fee": sell_fee,
                    "same_day": buy["executed_at"][:10] == sell_at[:10],
                }
            )
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    open_positions: list[dict] = []
    for ticker, lots in open_lots.items():
        for lot in lots:
            if lot["shares"] <= 1e-9:
                continue
            open_positions.append(
                {
                    "ticker": ticker,
                    "shares": lot["shares"],
                    "avg_cost": lot["price"],
                    "cost_basis": lot["shares"] * lot["price"] + lot["fee"],
                    "buy_at": lot["executed_at"],
                    "buy_id": lot["buy_id"],
                    "queue_id": lot["queue_id"],
                }
            )
    return open_positions, completed


def get_open_positions(conn: sqlite3.Connection) -> list[dict]:
    open_positions, _ = _fifo_ledger(conn)
    return open_positions


def get_completed_round_trips(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    _, completed = _fifo_ledger(conn)
    completed.sort(key=lambda r: r["sell_at"], reverse=True)
    return completed[:limit]


def clear_all_trades(conn: sqlite3.Connection) -> int:
    """Delete every row in trade_journal. Returns number of rows removed."""
    row = conn.execute("SELECT COUNT(*) AS c FROM trade_journal").fetchone()
    count = int(row["c"]) if row else 0
    conn.execute("DELETE FROM trade_journal")
    return count
```


---

<a id="src-investment_agent-learning-py"></a>
## `src/investment_agent/learning.py`

```python
"""Learning agent — daily feedback on trades and watchlist (Phase 5, no Claude)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from investment_agent.historical import evaluate_prior_day
from investment_agent.journal import get_completed_round_trips, get_open_positions
from investment_agent.liquidity import SWING_TARGET_PCT
from investment_agent.monitor import get_latest_quotes, pnl_pct
from investment_agent.strategy import STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _intraday_range_pct(open_px: float, high: float, low: float) -> float:
    if open_px <= 0:
        return 0.0
    return ((high - low) / open_px) * 100.0


def _queue_for(conn: sqlite3.Connection, queue_id: int | None) -> sqlite3.Row | None:
    if queue_id is None:
        return None
    return conn.execute(
        """
        SELECT id, ticker, state, entry_price, target_price, stop_price, avg_range_pct
        FROM queue_items WHERE id = ?
        """,
        (queue_id,),
    ).fetchone()


def _analyze_active_positions(conn: sqlite3.Connection, quotes: dict[str, float]) -> list[dict]:
    items: list[dict] = []
    for pos in get_open_positions(conn):
        ticker = pos["ticker"]
        current = quotes.get(ticker)
        entry = pos["avg_cost"]
        q = _queue_for(conn, pos.get("queue_id"))
        target = float(q["target_price"]) if q and q["target_price"] else entry * (1 + TARGET_PCT / 100)
        stop = float(q["stop_price"]) if q and q["stop_price"] else entry * (1 - STOP_PCT / 100)
        unrealized = None
        if current is not None:
            unrealized = (current - entry) * pos["shares"]
        items.append(
            {
                "ticker": ticker,
                "shares": pos["shares"],
                "entry_price": entry,
                "current_price": current,
                "unrealized_pnl": unrealized,
                "pnl_pct": pnl_pct(entry, current) if current else None,
                "target_price": target,
                "stop_price": stop,
                "queue_state": q["state"] if q else None,
                "eod_status": "open" if (q and q["state"] in ("in_trade", "eod")) else "unknown",
                "note": (
                    f"Open {pos['shares']:.0f} sh @ ${entry:.2f}"
                    + (f", unrealized ${unrealized:+.2f}" if unrealized is not None else "")
                ),
            }
        )
    return items


def _analyze_round_trips(conn: sqlite3.Connection, report_date: str | None = None) -> list[dict]:
    items: list[dict] = []
    for trip in get_completed_round_trips(conn, limit=50):
        if report_date and trip["sell_at"][:10] != report_date:
            continue
        q = _queue_for(conn, trip.get("queue_id"))
        rec_entry = float(q["entry_price"]) if q and q["entry_price"] else trip["buy_price"]
        target = float(q["target_price"]) if q and q["target_price"] else rec_entry * (1 + TARGET_PCT / 100)
        stop = float(q["stop_price"]) if q and q["stop_price"] else rec_entry * (1 - STOP_PCT / 100)
        entry_delta_pct = pnl_pct(rec_entry, trip["buy_price"])
        hit_target = trip["sell_price"] >= target - 0.001
        hit_stop = trip["sell_price"] <= stop + 0.001
        exit_vs_target = pnl_pct(target, trip["sell_price"])

        items.append(
            {
                "ticker": trip["ticker"],
                "shares": trip["shares"],
                "buy_price": trip["buy_price"],
                "sell_price": trip["sell_price"],
                "net_pnl": trip["net_pnl"],
                "same_day": trip["same_day"],
                "sell_date": trip["sell_at"][:10],
                "recommended_entry": rec_entry,
                "entry_delta_pct": entry_delta_pct,
                "target_price": target,
                "stop_price": stop,
                "hit_target": hit_target,
                "hit_stop": hit_stop,
                "exit_vs_target_pct": exit_vs_target,
                "note": (
                    f"{'Same-day' if trip['same_day'] else 'Multi-day'} round trip: "
                    f"net ${trip['net_pnl']:+.2f}, "
                    f"{'hit target' if hit_target else 'hit stop' if hit_stop else 'mid exit'}"
                ),
            }
        )
        if len(items) >= 30:
            break
    return items


def _journal_legs_for_date(conn: sqlite3.Connection, report_date: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, notes
        FROM trade_journal
        WHERE substr(executed_at, 1, 10) = ?
        ORDER BY executed_at ASC, id ASC
        """,
        (report_date,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "ticker": row["ticker"],
            "side": row["side"],
            "shares": row["shares"],
            "price": row["price"],
            "fee": row["fee"],
            "executed_at": row["executed_at"],
            "notes": row["notes"],
        }
        for row in rows
    ]


def _build_continual_learning(conn: sqlite3.Connection, *, lookback_days: int = 30) -> dict:
    """Aggregate journal + saved reports across recent days."""
    cutoff = (datetime.now(ET) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    trips = get_completed_round_trips(conn, limit=200)
    recent_trips = [t for t in trips if t["sell_at"][:10] >= cutoff]
    wins = sum(1 for t in recent_trips if t["net_pnl"] > 0)
    total_net = sum(t["net_pnl"] for t in recent_trips)
    same_day = sum(1 for t in recent_trips if t["same_day"])

    report_rows = conn.execute(
        """
        SELECT report_date, payload_json
        FROM learning_reports
        WHERE report_date >= ?
        ORDER BY report_date DESC
        """,
        (cutoff,),
    ).fetchall()

    range_errors: list[float] = []
    prior_screened = 0
    prior_targets = 0
    for row in report_rows:
        payload = json.loads(row["payload_json"])
        prior = payload.get("prior_day_evaluation")
        if not prior:
            continue
        summary = prior.get("summary") or {}
        prior_screened += summary.get("screened_count", 0)
        prior_targets += summary.get("simulated_targets", 0)
        for t in prior.get("all_tickers") or []:
            if t.get("range_delta_pct") is not None:
                range_errors.append(abs(float(t["range_delta_pct"])))

    saved_dates = [row["report_date"] for row in report_rows]
    return {
        "lookback_days": lookback_days,
        "cutoff_date": cutoff,
        "reports_saved": len(saved_dates),
        "saved_report_dates": saved_dates[:10],
        "journal": {
            "round_trips_closed": len(recent_trips),
            "win_rate_pct": round(100.0 * wins / max(len(recent_trips), 1), 1),
            "total_net_pnl": round(total_net, 2),
            "same_day_pct": round(100.0 * same_day / max(len(recent_trips), 1), 1),
        },
        "historical_accuracy": {
            "avg_range_error_pct": round(sum(range_errors) / len(range_errors), 2)
            if range_errors
            else None,
            "prior_day_screened_setups": prior_screened,
            "prior_day_simulated_targets": prior_targets,
        },
        "note": (
            f"Last {lookback_days}d: {len(recent_trips)} closed round trip(s), "
            f"{len(saved_dates)} saved learning report(s)."
        ),
    }


def list_learning_report_dates(conn: sqlite3.Connection, limit: int = 30) -> list[str]:
    rows = conn.execute(
        """
        SELECT report_date FROM learning_reports
        ORDER BY report_date DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [row["report_date"] for row in rows]


def _analyze_watchlist(conn: sqlite3.Connection, quotes: dict[str, float]) -> list[dict]:
    rows = conn.execute(
        """
        SELECT m.ticker, m.avg_range_pct, m.near_swing_target, m.last_quote,
               m.meets_liquidity_min, w.active
        FROM ticker_metrics m
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        LEFT JOIN watchlist w ON w.ticker = m.ticker
        WHERE COALESCE(w.active, 1) = 1
        ORDER BY ABS(m.avg_range_pct - ?) ASC
        LIMIT 15
        """,
        (SWING_TARGET_PCT,),
    ).fetchall()

    active_tickers = {
        r["ticker"]
        for r in conn.execute(
            """
            SELECT DISTINCT ticker FROM queue_items
            WHERE state IN ('in_trade','alert','armed','eod')
            """
        ).fetchall()
    }

    items: list[dict] = []
    for row in rows:
        ticker = row["ticker"]
        if ticker in active_tickers:
            continue
        quote_row = conn.execute(
            """
            SELECT open, high, low, price FROM quotes q
            INNER JOIN (
              SELECT ticker, MAX(captured_at) AS max_at FROM quotes GROUP BY ticker
            ) l ON q.ticker = l.ticker AND q.captured_at = l.max_at
            WHERE q.ticker = ?
            """,
            (ticker,),
        ).fetchone()
        actual_range = None
        if quote_row and quote_row["open"]:
            actual_range = _intraday_range_pct(
                float(quote_row["open"]),
                float(quote_row["high"] or quote_row["price"]),
                float(quote_row["low"] or quote_row["price"]),
            )
        predicted = float(row["avg_range_pct"] or 0)
        items.append(
            {
                "ticker": ticker,
                "predicted_range_pct": predicted,
                "actual_range_pct": actual_range,
                "range_delta_pct": (
                    actual_range - predicted if actual_range is not None else None
                ),
                "near_swing_target": bool(row["near_swing_target"]),
                "meets_liquidity": bool(row["meets_liquidity_min"]),
                "last_quote": quotes.get(ticker, row["last_quote"]),
                "note": (
                    f"Avg range {predicted:.1f}% vs ~{SWING_TARGET_PCT}% target"
                    + (
                        f"; today ~{actual_range:.1f}%"
                        if actual_range is not None
                        else ""
                    )
                ),
            }
        )
    return items[:8]


def _regime_stats(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        """
        SELECT captured_at, block_new_longs
        FROM regime_snapshots
        ORDER BY captured_at DESC
        LIMIT 30
        """
    ).fetchall()
    blocked = sum(1 for r in rows if r["block_new_longs"])
    return {
        "snapshots_reviewed": len(rows),
        "blocked_days_recent": blocked,
        "latest_blocked": bool(rows[0]["block_new_longs"]) if rows else False,
    }


def _multi_round_same_day(conn: sqlite3.Connection, report_date: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT ticker, COUNT(*) AS legs
        FROM trade_journal
        WHERE substr(executed_at, 1, 10) = ?
        GROUP BY ticker
        HAVING legs >= 2
        ORDER BY legs DESC
        """,
        (report_date,),
    ).fetchall()
    return [{"ticker": r["ticker"], "legs": r["legs"]} for r in rows]


def generate_learning_report(
    conn: sqlite3.Connection,
    report_date: str | None = None,
) -> dict:
    """Build daily learning report from journal, queue, metrics, regime, and history."""
    day = report_date or _today_et()
    quotes = get_latest_quotes(conn)

    active = _analyze_active_positions(conn, quotes)
    today_round_trips = _analyze_round_trips(conn, report_date=day)
    recent_round_trips = _analyze_round_trips(conn)
    watchlist = _analyze_watchlist(conn, quotes)
    regime = _regime_stats(conn)
    multi_round = _multi_round_same_day(conn, day)
    today_journal = _journal_legs_for_date(conn, day)
    prior_day = evaluate_prior_day(conn, reference_date=day)
    continual = _build_continual_learning(conn)

    eod_open = [a for a in active if a.get("queue_state") in ("in_trade", "eod")]

    highlights: list[str] = []
    if today_round_trips:
        wins = sum(1 for r in today_round_trips if r["net_pnl"] > 0)
        highlights.append(
            f"Today: {len(today_round_trips)} round trip(s) closed; {wins} profitable after fees."
        )
    elif recent_round_trips:
        wins = sum(1 for r in recent_round_trips if r["net_pnl"] > 0)
        highlights.append(
            f"Recent: {len(recent_round_trips)} round trip(s) logged; {wins} profitable after fees."
        )
    if today_journal:
        highlights.append(f"Today: {len(today_journal)} journal leg(s) logged.")
    if prior_day and prior_day.get("summary"):
        s = prior_day["summary"]
        highlights.append(
            f"Prior day ({prior_day['eval_date']}): {s['screened_count']} screener match(es), "
            f"{s['simulated_targets']} simulated target(s), {s['simulated_stops']} stop(s)."
        )
    if continual["journal"]["round_trips_closed"]:
        highlights.append(
            f"Continual ({continual['lookback_days']}d): "
            f"{continual['journal']['win_rate_pct']}% win rate, "
            f"net ${continual['journal']['total_net_pnl']:+.2f}."
        )
    if active:
        highlights.append(f"{len(active)} open position(s) — review target/stop and EOD flat rule.")
    if eod_open:
        highlights.append(f"{len(eod_open)} position(s) still open near session end — confirm flat or overnight approval.")
    if multi_round:
        names = ", ".join(f"{m['ticker']}({m['legs']} legs)" for m in multi_round)
        highlights.append(f"Multi-leg same-day activity: {names}.")
    if regime["blocked_days_recent"]:
        highlights.append(
            f"Regime blocked new longs on {regime['blocked_days_recent']} of last "
            f"{regime['snapshots_reviewed']} snapshots."
        )
    if watchlist:
        near = [w["ticker"] for w in watchlist if w["near_swing_target"]][:3]
        if near:
            highlights.append(f"Watchlist near ~3% swing: {', '.join(near)}.")

    return {
        "report_date": day,
        "generated_at": _utc_now_iso(),
        "highlights": highlights,
        "active_positions": active,
        "round_trips": recent_round_trips,
        "today_round_trips": today_round_trips,
        "today_journal": today_journal,
        "watchlist_insights": watchlist,
        "regime_stats": regime,
        "multi_round_same_day": multi_round,
        "eod_open_positions": eod_open,
        "prior_day_evaluation": prior_day,
        "continual_learning": continual,
        "claude_ready": False,
    }


def save_learning_report(conn: sqlite3.Connection, report: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO learning_reports (report_date, generated_at, payload_json)
        VALUES (?, ?, ?)
        ON CONFLICT(report_date) DO UPDATE SET
          generated_at = excluded.generated_at,
          payload_json = excluded.payload_json
        """,
        (report["report_date"], report["generated_at"], json.dumps(report)),
    )
    row = conn.execute(
        "SELECT id FROM learning_reports WHERE report_date = ?",
        (report["report_date"],),
    ).fetchone()
    return int(row["id"]) if row else int(cur.lastrowid)


def get_learning_report(conn: sqlite3.Connection, report_date: str | None = None) -> dict | None:
    day = report_date or _today_et()
    row = conn.execute(
        "SELECT payload_json FROM learning_reports WHERE report_date = ?",
        (day,),
    ).fetchone()
    if row:
        return json.loads(row["payload_json"])
    return None


def get_or_generate_learning_report(
    conn: sqlite3.Connection,
    report_date: str | None = None,
) -> dict:
    day = report_date or _today_et()
    cached = get_learning_report(conn, day)
    if cached:
        return cached
    return generate_learning_report(conn, report_date=day)
```


---

<a id="src-investment_agent-liquidity-py"></a>
## `src/investment_agent/liquidity.py`

```python
"""Liquidity cap and daily range metrics (Product Spec v3 / strategy doc §7)."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

# Strategy defaults
MIN_ADV_DOLLAR = 2_000_000.0
PARTICIPATION_RATE = 0.01
LIQUIDITY_BUFFER = 0.80
SWING_TARGET_PCT = 3.0
SWING_TOLERANCE_PCT = 1.0  # 2–4% band around 3%


@dataclass(frozen=True)
class DailyBar:
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class LiquidityMetrics:
    adv_dollar: float
    avg_range_pct: float
    liquidity_cap: float
    meets_liquidity_min: bool
    near_swing_target: bool


def daily_range_pct(bar: DailyBar) -> float:
    if bar.close <= 0:
        return 0.0
    return ((bar.high - bar.low) / bar.close) * 100.0


def compute_adv_dollar(bars: list[DailyBar], window: int = 20) -> float:
    if not bars:
        return 0.0
    recent = bars[-window:]
    dollars = [b.close * b.volume for b in recent if b.close > 0 and b.volume > 0]
    return mean(dollars) if dollars else 0.0


def compute_avg_range_pct(bars: list[DailyBar], window: int = 20) -> float:
    if not bars:
        return 0.0
    recent = bars[-window:]
    ranges = [daily_range_pct(b) for b in recent if b.close > 0]
    return mean(ranges) if ranges else 0.0


def liquidity_cap_from_adv(
    adv_dollar: float,
    participation_rate: float = PARTICIPATION_RATE,
    buffer: float = LIQUIDITY_BUFFER,
) -> float:
    return adv_dollar * participation_rate * buffer


def compute_liquidity_metrics(
    bars: list[DailyBar],
    tradable_cash: float | None = None,
    window: int = 20,
) -> LiquidityMetrics:
    adv = compute_adv_dollar(bars, window=window)
    avg_range = compute_avg_range_pct(bars, window=window)
    cap = liquidity_cap_from_adv(adv)
    if tradable_cash is not None:
        cap = min(cap, tradable_cash)
    meets_liq = adv >= MIN_ADV_DOLLAR
    near_swing = abs(avg_range - SWING_TARGET_PCT) <= SWING_TOLERANCE_PCT
    return LiquidityMetrics(
        adv_dollar=adv,
        avg_range_pct=avg_range,
        liquidity_cap=cap,
        meets_liquidity_min=meets_liq,
        near_swing_target=near_swing,
    )
```


---

<a id="src-investment_agent-monitor-py"></a>
## `src/investment_agent/monitor.py`

```python
"""Intraday monitor — +1.13% target / −0.50% stop alerts (Phase 4, no Claude)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from investment_agent.strategy import ALERT_TYPES, MONITORED_STATES, STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")

NEAR_TARGET_BUFFER_PCT = 0.25  # alert when within 0.25% of target
NEAR_STOP_BUFFER_PCT = 0.10


@dataclass(frozen=True)
class MonitorEvaluation:
    queue_id: int
    ticker: str
    state: str
    entry_price: float
    current_price: float
    target_price: float
    stop_price: float
    pnl_pct: float
    alert_type: str | None
    message: str | None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def is_eod_window(when: datetime | None = None) -> bool:
    """After 3:45 PM ET on a weekday — remind to flatten intraday positions."""
    now = when or datetime.now(ET)
    if now.weekday() >= 5:
        return False
    return (now.hour, now.minute) >= (15, 45)


def pnl_pct(entry: float, current: float) -> float:
    if entry <= 0:
        return 0.0
    return ((current - entry) / entry) * 100.0


def target_stop_prices(entry: float) -> tuple[float, float]:
    target = entry * (1 + TARGET_PCT / 100)
    stop = entry * (1 - STOP_PCT / 100)
    return target, stop


def effective_entry_price(conn: sqlite3.Connection, queue_id: int, fallback: float) -> float:
    row = conn.execute(
        """
        SELECT price FROM trade_journal
        WHERE queue_id = ? AND side = 'BUY'
        ORDER BY executed_at DESC
        LIMIT 1
        """,
        (queue_id,),
    ).fetchone()
    if row and row["price"]:
        return float(row["price"])
    return fallback


def get_latest_quotes(conn: sqlite3.Connection) -> dict[str, float]:
    rows = conn.execute(
        """
        SELECT q.ticker, q.price
        FROM quotes q
        INNER JOIN (
          SELECT ticker, MAX(captured_at) AS max_at
          FROM quotes GROUP BY ticker
        ) latest ON q.ticker = latest.ticker AND q.captured_at = latest.max_at
        """
    ).fetchall()
    return {row["ticker"]: float(row["price"]) for row in rows}


def _classify_price_alert(
    *,
    state: str,
    entry: float,
    current: float,
    target: float,
    stop: float,
    eod: bool,
) -> tuple[str | None, str | None]:
    pct = pnl_pct(entry, current)

    if state in ("in_trade", "alert", "eod") and current >= target:
        return (
            "TARGET_HIT",
            f"Target +{TARGET_PCT}% hit — ${current:.2f} ≥ ${target:.2f} "
            f"(P&L {pct:+.2f}%). Consider taking profit in E*TRADE.",
        )

    if state in ("in_trade", "alert", "eod") and current <= stop:
        return (
            "STOP_HIT",
            f"Stop −{STOP_PCT}% hit — ${current:.2f} ≤ ${stop:.2f} "
            f"(P&L {pct:+.2f}%). Review exit in E*TRADE.",
        )

    if state == "in_trade" and eod:
        return (
            "EOD_FLATTEN",
            f"EOD reminder — {state} position open at ${current:.2f} "
            f"(P&L {pct:+.2f}%). Default rule: flat by close unless approved overnight.",
        )

    if state in ("armed", "alert", "in_trade"):
        if pct >= TARGET_PCT - NEAR_TARGET_BUFFER_PCT and current < target:
            return (
                "NEAR_TARGET",
                f"Approaching target — ${current:.2f}, P&L {pct:+.2f}% "
                f"(target ${target:.2f}).",
            )
        if pct <= -(STOP_PCT - NEAR_STOP_BUFFER_PCT) and current > stop:
            return (
                "NEAR_STOP",
                f"Approaching stop — ${current:.2f}, P&L {pct:+.2f}% "
                f"(stop ${stop:.2f}).",
            )

    return None, None


def evaluate_queue_item(
    conn: sqlite3.Connection,
    row: sqlite3.Row,
    quotes: dict[str, float],
    *,
    eod: bool | None = None,
) -> MonitorEvaluation | None:
    state = row["state"]
    if state not in MONITORED_STATES:
        return None

    ticker = row["ticker"]
    current = quotes.get(ticker)
    if current is None:
        return None

    fallback_entry = float(row["entry_price"] or current)
    entry = effective_entry_price(conn, int(row["id"]), fallback_entry)
    stored_target = float(row["target_price"]) if row["target_price"] else None
    stored_stop = float(row["stop_price"]) if row["stop_price"] else None
    target, stop = target_stop_prices(entry)
    if stored_target:
        target = stored_target
    if stored_stop:
        stop = stored_stop

    eod_flag = is_eod_window() if eod is None else eod
    alert_type, message = _classify_price_alert(
        state=state,
        entry=entry,
        current=current,
        target=target,
        stop=stop,
        eod=eod_flag,
    )

    return MonitorEvaluation(
        queue_id=int(row["id"]),
        ticker=ticker,
        state=state,
        entry_price=entry,
        current_price=current,
        target_price=target,
        stop_price=stop,
        pnl_pct=pnl_pct(entry, current),
        alert_type=alert_type,
        message=message,
    )


def _alert_exists_today(
    conn: sqlite3.Connection,
    queue_id: int | None,
    ticker: str,
    alert_type: str,
    alert_date: str,
) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM price_alerts
        WHERE alert_type = ?
          AND alert_date = ?
          AND acknowledged = 0
          AND (
            (queue_id IS NOT NULL AND queue_id = ?)
            OR (queue_id IS NULL AND ticker = ?)
          )
        LIMIT 1
        """,
        (alert_type, alert_date, queue_id, ticker),
    ).fetchone()
    return row is not None


def insert_alert(conn: sqlite3.Connection, ev: MonitorEvaluation, alert_date: str) -> int | None:
    if not ev.alert_type or not ev.message:
        return None
    if ev.alert_type not in ALERT_TYPES:
        return None
    if _alert_exists_today(conn, ev.queue_id, ev.ticker, ev.alert_type, alert_date):
        return None

    cur = conn.execute(
        """
        INSERT INTO price_alerts
          (queue_id, ticker, alert_type, entry_price, current_price,
           target_price, stop_price, pnl_pct, message, alert_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ev.queue_id,
            ev.ticker,
            ev.alert_type,
            ev.entry_price,
            ev.current_price,
            ev.target_price,
            ev.stop_price,
            ev.pnl_pct,
            ev.message,
            alert_date,
        ),
    )
    return int(cur.lastrowid)


def run_monitor_cycle(
    conn: sqlite3.Connection,
    quotes: dict[str, float] | None = None,
    *,
    eod: bool | None = None,
) -> dict:
    """Evaluate monitored queue items; persist new alerts."""
    quote_map = quotes if quotes is not None else get_latest_quotes(conn)
    alert_date = today_et()

    placeholders = ",".join("?" for _ in MONITORED_STATES)
    rows = conn.execute(
        f"""
        SELECT id, ticker, state, entry_price, target_price, stop_price
        FROM queue_items
        WHERE state IN ({placeholders})
        ORDER BY updated_at DESC
        """,
        MONITORED_STATES,
    ).fetchall()

    evaluations: list[MonitorEvaluation] = []
    new_alerts: list[int] = []
    missing_quotes: list[str] = []

    for row in rows:
        ticker = row["ticker"]
        if ticker not in quote_map:
            missing_quotes.append(ticker)
            continue
        ev = evaluate_queue_item(conn, row, quote_map, eod=eod)
        if ev:
            evaluations.append(ev)
            alert_id = insert_alert(conn, ev, alert_date)
            if alert_id:
                new_alerts.append(alert_id)

    return {
        "ok": True,
        "evaluated": len(evaluations),
        "new_alerts": len(new_alerts),
        "alert_ids": new_alerts,
        "missing_quotes": missing_quotes,
        "evaluations": [evaluation_to_dict(e) for e in evaluations],
    }


def list_active_alerts(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, queue_id, ticker, alert_type, entry_price, current_price,
               target_price, stop_price, pnl_pct, message, acknowledged,
               alert_date, created_at
        FROM price_alerts
        WHERE acknowledged = 0
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_all_alerts(conn: sqlite3.Connection, limit: int = 100) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, queue_id, ticker, alert_type, entry_price, current_price,
               target_price, stop_price, pnl_pct, message, acknowledged,
               alert_date, created_at
        FROM price_alerts
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def acknowledge_alert(conn: sqlite3.Connection, alert_id: int) -> dict:
    cur = conn.execute(
        "UPDATE price_alerts SET acknowledged = 1 WHERE id = ? AND acknowledged = 0",
        (alert_id,),
    )
    if cur.rowcount == 0:
        return {"ok": False, "error": "Alert not found or already acknowledged"}
    return {"ok": True, "id": alert_id}


def enrich_queue_item(
    conn: sqlite3.Connection,
    item: dict,
    quotes: dict[str, float] | None = None,
) -> dict:
    """Add live price + P&L fields for dashboard display."""
    quote_map = quotes if quotes is not None else get_latest_quotes(conn)
    out = dict(item)
    ticker = item["ticker"]
    current = quote_map.get(ticker)
    out["current_price"] = current
    if current is None:
        out["pnl_pct"] = None
        out["monitor_status"] = "no_quote"
        return out

    entry = effective_entry_price(
        conn, int(item["id"]), float(item.get("entry_price") or current)
    )
    out["entry_price_effective"] = entry
    out["pnl_pct"] = pnl_pct(entry, current)
    target = float(item.get("target_price") or target_stop_prices(entry)[0])
    stop = float(item.get("stop_price") or target_stop_prices(entry)[1])
    out["distance_to_target_pct"] = pnl_pct(entry, target)
    out["distance_to_stop_pct"] = pnl_pct(entry, stop)

    if item["state"] in MONITORED_STATES:
        ev = evaluate_queue_item(
            conn,
            conn.execute(
                "SELECT id, ticker, state, entry_price, target_price, stop_price FROM queue_items WHERE id = ?",
                (item["id"],),
            ).fetchone(),
            quote_map,
            eod=False,
        )
        out["monitor_status"] = ev.alert_type.lower() if ev and ev.alert_type else "watching"
    else:
        out["monitor_status"] = "idle"
    return out


def evaluation_to_dict(ev: MonitorEvaluation) -> dict:
    return {
        "queue_id": ev.queue_id,
        "ticker": ev.ticker,
        "state": ev.state,
        "entry_price": ev.entry_price,
        "current_price": ev.current_price,
        "target_price": ev.target_price,
        "stop_price": ev.stop_price,
        "pnl_pct": ev.pnl_pct,
        "alert_type": ev.alert_type,
        "message": ev.message,
    }
```


---

<a id="src-investment_agent-period_screener-py"></a>
## `src/investment_agent/period_screener.py`

```python
"""Period screener — aggregate historical Step 3 matches over days/weeks (Phase 7)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from investment_agent.finance import ORIGINAL_BASIS, daily_profit_target
from investment_agent.historical import evaluate_period
from investment_agent.liquidity import MIN_ADV_DOLLAR, SWING_TARGET_PCT
from investment_agent.dollar_target import (
    MIN_RANK_AVG_NET_RATIO,
    MIN_RANK_DOLLAR_DAYS,
    MIN_RANK_DOLLAR_HIT_RATE_PCT,
    passes_dollar_rank_gate,
)
from investment_agent.stock_team import _latest_metrics, screen_candidates
from investment_agent.strategy import REGIME_ONLY_TICKERS

# Rank weights — dollar-goal reachability first (pool is smaller but stronger)
RANK_WEIGHTS = {
    "live_pass": 0.12,
    "dollar_hit_rate": 0.32,
    "dollar_avg_net": 0.22,
    "consistency": 0.10,
    "hit_rate": 0.06,
    "swing_proximity": 0.08,
    "liquidity": 0.06,
    "near_swing": 0.04,
}


def _metrics_map(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    return {row["ticker"]: row for row in _latest_metrics(conn)}


def _swing_proximity(avg_range_pct: float) -> float:
    return max(0.0, 1.0 - abs(avg_range_pct - SWING_TARGET_PCT) / SWING_TARGET_PCT)


def _liquidity_score(adv_dollar: float, meets_liquidity: bool) -> float:
    if not meets_liquidity or adv_dollar <= 0:
        return 0.0
    return min(1.0, adv_dollar / (MIN_ADV_DOLLAR * 5))


def _criteria_likelihood_score(
    *,
    live_pass: bool,
    hit_rate_pct: float,
    dollar_hit_rate_pct: float = 0.0,
    avg_net_at_high: float = 0.0,
    net_target: float = 150.0,
    days_screened: int,
    avg_range_pct: float,
    adv_dollar: float = 0.0,
    meets_liquidity: bool = False,
    near_swing: bool = False,
    period_days: int = 14,
) -> dict:
    swing_px = _swing_proximity(avg_range_pct)
    liq = _liquidity_score(adv_dollar, meets_liquidity)
    consistency = min(days_screened / max(period_days * 0.5, 1), 1.0)
    hit = hit_rate_pct / 100.0
    dollar_hit = dollar_hit_rate_pct / 100.0
    dollar_avg = (
        min(avg_net_at_high / net_target, 1.0) if net_target > 0 and avg_net_at_high > 0 else 0.0
    )
    score = (
        RANK_WEIGHTS["live_pass"] * (1.0 if live_pass else 0.0)
        + RANK_WEIGHTS["hit_rate"] * hit
        + RANK_WEIGHTS["dollar_hit_rate"] * dollar_hit
        + RANK_WEIGHTS["dollar_avg_net"] * dollar_avg
        + RANK_WEIGHTS["consistency"] * consistency
        + RANK_WEIGHTS["swing_proximity"] * swing_px
        + RANK_WEIGHTS["liquidity"] * liq
        + RANK_WEIGHTS["near_swing"] * (1.0 if near_swing else 0.0)
    )
    return {
        "score": round(score, 4),
        "swing_proximity": round(swing_px, 3),
        "liquidity_score": round(liq, 3),
        "consistency_score": round(consistency, 3),
        "hit_rate_component": round(hit, 3),
        "dollar_hit_rate_component": round(dollar_hit, 3),
        "dollar_avg_net_component": round(dollar_avg, 3),
    }


def _enrich_row(
    row: dict,
    metrics: sqlite3.Row | None,
    *,
    period_days: int,
    net_target: float,
) -> dict:
    adv = float(metrics["adv_dollar"] or 0) if metrics else 0.0
    avg_range = float(row.get("avg_range_pct") or (metrics["avg_range_pct"] if metrics else 0) or 0)
    meets_liq = bool(metrics["meets_liquidity_min"]) if metrics else False
    near_swing = bool(metrics["near_swing_target"]) if metrics else False
    if metrics and avg_range == 0:
        avg_range = float(metrics["avg_range_pct"] or 0)

    parts = _criteria_likelihood_score(
        live_pass=bool(row.get("live_pass_today")),
        hit_rate_pct=float(row.get("hit_rate_pct") or 0),
        dollar_hit_rate_pct=float(row.get("dollar_hit_rate_pct") or 0),
        avg_net_at_high=float(row.get("avg_net_at_high") or 0),
        net_target=net_target,
        days_screened=int(row.get("days_screened") or 0),
        avg_range_pct=avg_range,
        adv_dollar=adv,
        meets_liquidity=meets_liq,
        near_swing=near_swing,
        period_days=period_days,
    )
    out = {**row, **parts}
    out["net_target"] = net_target
    out["passes_dollar_rank_gate"] = passes_dollar_rank_gate(
        dollar_hit_rate_pct=float(row.get("dollar_hit_rate_pct") or 0),
        avg_net_at_high=float(row.get("avg_net_at_high") or 0),
        net_target=net_target,
        days_screened=int(row.get("days_screened") or 0),
    )
    out["avg_range_pct"] = round(avg_range, 2)
    out["adv_dollar"] = round(adv, 0)
    out["adv_dollar_m"] = round(adv / 1_000_000, 1) if adv else 0.0
    out["liquidity_cap"] = round(float(metrics["liquidity_cap"] or 0), 0) if metrics else None
    out["meets_liquidity"] = meets_liq
    out["near_swing_target"] = near_swing
    return out

ET = ZoneInfo("America/New_York")


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


MARKET_CALENDAR_TICKER = "SPY"


def list_trading_dates(
    conn: sqlite3.Connection,
    *,
    count: int,
    end_date: str | None = None,
) -> list[str]:
    """Last ``count`` US market sessions from OHLCV (SPY calendar, excludes weekends/holidays)."""
    end = end_date or _today_et()
    rows = conn.execute(
        """
        SELECT DISTINCT date FROM ohlcv_daily
        WHERE ticker = ? AND date <= ?
        ORDER BY date DESC
        LIMIT ?
        """,
        (MARKET_CALENDAR_TICKER, end, count),
    ).fetchall()
    if len(rows) < count:
        rows = conn.execute(
            """
            SELECT DISTINCT date FROM ohlcv_daily
            WHERE date <= ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (end, count),
        ).fetchall()
    return sorted(row[0] for row in rows)


def date_range_for_period(
    period_days: int,
    end_date: str | None = None,
    *,
    conn: sqlite3.Connection | None = None,
) -> tuple[str, str]:
    """Return [start, end] spanning the last ``period_days`` trading sessions."""
    if conn is not None:
        dates = list_trading_dates(conn, count=period_days, end_date=end_date)
        if dates:
            return dates[0], dates[-1]
    end = end_date or _today_et()
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    # Calendar fallback when no OHLCV (tests): widen window to approximate sessions.
    start_dt = end_dt - timedelta(days=max(int(period_days * 2), period_days))
    return start_dt.strftime("%Y-%m-%d"), end


def _rank_score(
    *,
    live_pass: bool,
    hit_rate_pct: float,
    dollar_hit_rate_pct: float = 0.0,
    avg_net_at_high: float = 0.0,
    net_target: float = 150.0,
    days_screened: int,
    avg_range_pct: float,
    adv_dollar: float = 0.0,
    meets_liquidity: bool = False,
    near_swing: bool = False,
    period_days: int = 14,
) -> float:
    return _criteria_likelihood_score(
        live_pass=live_pass,
        hit_rate_pct=hit_rate_pct,
        dollar_hit_rate_pct=dollar_hit_rate_pct,
        avg_net_at_high=avg_net_at_high,
        net_target=net_target,
        days_screened=days_screened,
        avg_range_pct=avg_range_pct,
        adv_dollar=adv_dollar,
        meets_liquidity=meets_liquidity,
        near_swing=near_swing,
        period_days=period_days,
    )["score"]


def run_period_screener(
    conn: sqlite3.Connection,
    *,
    start_date: str,
    end_date: str,
    tradable_cash: float = ORIGINAL_BASIS,
    min_days_screened: int = 1,
    min_hit_rate_pct: float | None = None,
    min_dollar_hit_rate_pct: float | None = None,
    trading_dates: list[str] | None = None,
    requested_trading_days: int | None = None,
) -> dict:
    """Aggregate period evaluation by ticker and rank candidates."""
    net_target = daily_profit_target(tradable_cash)
    period = evaluate_period(
        conn,
        start_date,
        end_date,
        tradable_cash=tradable_cash,
        trading_dates=trading_dates,
    )
    live_tickers = {c.ticker for c in screen_candidates(conn)}
    metrics_by_ticker = _metrics_map(conn)
    trading_days_in_period = period["days_evaluated"]
    score_period_days = requested_trading_days or trading_days_in_period

    agg: dict[str, dict] = {}
    for day in period["days"]:
        for match in day["matches"]:
            ticker = match["ticker"]
            bucket = agg.setdefault(
                ticker,
                {
                    "ticker": ticker,
                    "days_screened": 0,
                    "simulated_targets": 0,
                    "simulated_stops": 0,
                    "simulated_neither": 0,
                    "dollar_targets": 0,
                    "dollar_stops": 0,
                    "dollar_neither": 0,
                    "dollar_no_fill": 0,
                    "last_screened_date": None,
                    "avg_range_pct": 0.0,
                    "_range_sum": 0.0,
                    "_net_at_high_sum": 0.0,
                },
            )
            bucket["days_screened"] += 1
            outcome = match.get("outcome") or "neither"
            dollar_outcome = match.get("dollar_outcome") or "neither"
            if outcome == "target":
                bucket["simulated_targets"] += 1
            elif outcome == "stop":
                bucket["simulated_stops"] += 1
            else:
                bucket["simulated_neither"] += 1
            if dollar_outcome == "target":
                bucket["dollar_targets"] += 1
            elif dollar_outcome == "stop":
                bucket["dollar_stops"] += 1
            elif dollar_outcome == "no_fill":
                bucket["dollar_no_fill"] += 1
                bucket["dollar_neither"] += 1
            else:
                bucket["dollar_neither"] += 1
            bucket["last_screened_date"] = day["date"]
            bucket["_range_sum"] += float(match.get("actual_range_pct") or 0)
            bucket["_net_at_high_sum"] += float(match.get("net_at_high") or 0)

    candidates: list[dict] = []
    for ticker, b in agg.items():
        if b["days_screened"] < min_days_screened:
            continue
        decided = b["simulated_targets"] + b["simulated_stops"]
        hit_rate = round(100.0 * b["simulated_targets"] / max(decided, 1), 1)
        dollar_decided = b["dollar_targets"] + b["dollar_stops"]
        dollar_hit_rate = round(100.0 * b["dollar_targets"] / max(dollar_decided, 1), 1)
        if min_hit_rate_pct is not None and hit_rate < min_hit_rate_pct:
            continue
        if min_dollar_hit_rate_pct is not None and dollar_hit_rate < min_dollar_hit_rate_pct:
            continue
        avg_range = round(b["_range_sum"] / max(b["days_screened"], 1), 2)
        avg_net_at_high = round(b["_net_at_high_sum"] / max(b["days_screened"], 1), 2)
        live_pass = ticker in live_tickers
        m = metrics_by_ticker.get(ticker)
        base = {
            "ticker": ticker,
            "days_screened": b["days_screened"],
            "simulated_targets": b["simulated_targets"],
            "simulated_stops": b["simulated_stops"],
            "simulated_neither": b["simulated_neither"],
            "dollar_targets": b["dollar_targets"],
            "dollar_stops": b["dollar_stops"],
            "dollar_neither": b["dollar_neither"],
            "hit_rate_pct": hit_rate,
            "dollar_hit_rate_pct": dollar_hit_rate,
            "avg_net_at_high": avg_net_at_high,
            "avg_range_pct": avg_range,
            "last_screened_date": b["last_screened_date"],
            "live_pass_today": live_pass,
            "period_trading_days": trading_days_in_period,
            "requested_trading_days": score_period_days,
        }
        row = _enrich_row(base, m, period_days=score_period_days, net_target=net_target)
        candidates.append(row)

    candidates.sort(
        key=lambda r: (-r["score"], -r["days_screened"], -r.get("adv_dollar", 0), r["ticker"])
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "period_days": score_period_days,
        "trading_days_in_period": trading_days_in_period,
        "requested_trading_days": score_period_days,
        "net_target": net_target,
        "deploy": tradable_cash,
        "days_evaluated": period["days_evaluated"],
        "candidates": candidates,
        "summary": {
            **period["summary"],
            "unique_tickers_screened": len(candidates),
        },
    }


def save_screener_run(conn: sqlite3.Connection, result: dict, *, run_type: str = "period") -> int:
    started = _utc_now()
    params = {
        "start_date": result["start_date"],
        "end_date": result["end_date"],
        "run_type": run_type,
    }
    summary_payload = {
        **result.get("summary", {}),
        "candidates": result.get("candidates", []),
    }
    cur = conn.execute(
        """
        INSERT INTO screener_runs (run_type, started_at, finished_at, params_json, summary_json, status)
        VALUES (?, ?, ?, ?, ?, 'completed')
        """,
        (
            run_type,
            started,
            _utc_now(),
            json.dumps(params),
            json.dumps(summary_payload),
        ),
    )
    run_id = int(cur.lastrowid)

    for c in result.get("candidates", []):
        conn.execute(
            """
            INSERT INTO period_screener_hits
              (run_id, ticker, hit_date, predicted_range_pct, actual_range_pct,
               simulated_outcome, would_screen, days_screened, hit_rate_pct, score)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (
                run_id,
                c["ticker"],
                c.get("last_screened_date") or result["end_date"],
                c.get("avg_range_pct"),
                c.get("avg_range_pct"),
                f"targets={c['simulated_targets']},stops={c['simulated_stops']}",
                c["days_screened"],
                c["hit_rate_pct"],
                c["score"],
            ),
        )
    return run_id


def get_latest_screener_run(conn: sqlite3.Connection, run_type: str = "period") -> dict | None:
    row = conn.execute(
        """
        SELECT id, run_type, started_at, finished_at, params_json, summary_json, status
        FROM screener_runs
        WHERE run_type = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (run_type,),
    ).fetchone()
    if not row:
        return None
    summary = json.loads(row["summary_json"])
    candidates = summary.pop("candidates", [])
    params = json.loads(row["params_json"])
    return {
        "id": row["id"],
        "run_type": row["run_type"],
        "started_at": row["started_at"],
        "params": params,
        "summary": summary,
        "candidates": candidates,
        "start_date": params.get("start_date"),
        "end_date": params.get("end_date"),
    }


def build_ranked_candidates(
    conn: sqlite3.Connection,
    *,
    period_days: int = 14,
    min_days_screened: int = 1,
    end_date: str | None = None,
    tradable_cash: float | None = None,
    net_target: float | None = None,
    require_dollar_rank_gate: bool = True,
) -> dict:
    from investment_agent.account import build_dashboard_summary

    summary = build_dashboard_summary(conn)
    deploy = float(tradable_cash if tradable_cash is not None else summary.tradable_cash or ORIGINAL_BASIS)
    goal = float(net_target if net_target is not None else summary.daily_target or daily_profit_target(deploy))

    trading_dates = list_trading_dates(conn, count=period_days, end_date=end_date)
    start, end = date_range_for_period(period_days, end_date=end_date, conn=conn)
    period = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        tradable_cash=deploy,
        min_days_screened=min_days_screened,
        trading_dates=trading_dates or None,
        requested_trading_days=period_days,
    )
    live = screen_candidates(conn)
    live_map = {c.ticker: c for c in live}
    metrics_by_ticker = _metrics_map(conn)
    score_period = period_days

    ranked: list[dict] = []
    excluded: list[dict] = []
    seen: set[str] = set()

    for c in period["candidates"]:
        card = live_map.get(c["ticker"])
        row = _enrich_row(c, metrics_by_ticker.get(c["ticker"]), period_days=score_period, net_target=goal)
        enriched = {
            **row,
            "entry_price": card.entry_price if card else None,
            "target_price": card.target_price if card else None,
            "stop_price": card.stop_price if card else None,
            "suggested_size": card.suggested_size if card else row.get("liquidity_cap"),
            "thesis_summary": card.thesis_summary if card else None,
        }
        if require_dollar_rank_gate and not row.get("passes_dollar_rank_gate"):
            excluded.append(enriched)
        else:
            ranked.append(enriched)
        seen.add(c["ticker"])

    for card in live:
        if card.ticker in seen:
            continue
        m = metrics_by_ticker.get(card.ticker)
        base = {
            "ticker": card.ticker,
            "days_screened": 0,
            "simulated_targets": 0,
            "simulated_stops": 0,
            "simulated_neither": 0,
            "dollar_targets": 0,
            "dollar_stops": 0,
            "dollar_neither": 0,
            "hit_rate_pct": 0.0,
            "dollar_hit_rate_pct": 0.0,
            "avg_net_at_high": 0.0,
            "avg_range_pct": card.avg_range_pct,
            "last_screened_date": None,
            "live_pass_today": True,
            "period_trading_days": period.get("trading_days_in_period", period["days_evaluated"]),
            "requested_trading_days": score_period,
        }
        row = _enrich_row(base, m, period_days=score_period, net_target=goal)
        enriched = {
            **row,
            "entry_price": card.entry_price,
            "target_price": card.target_price,
            "stop_price": card.stop_price,
            "suggested_size": card.suggested_size,
            "thesis_summary": card.thesis_summary,
            "liquidity_cap": card.liquidity_cap,
        }
        if require_dollar_rank_gate and not row.get("passes_dollar_rank_gate"):
            excluded.append(enriched)
        else:
            ranked.append(enriched)

    ranked.sort(
        key=lambda r: (-r["score"], -r["days_screened"], -r.get("adv_dollar", 0), r["ticker"])
    )
    return {
        "period_days": period_days,
        "trading_days_in_period": period.get("trading_days_in_period", period["days_evaluated"]),
        "start_date": start,
        "end_date": end,
        "trading_dates": trading_dates,
        "ranked": ranked,
        "excluded": excluded,
        "excluded_count": len(excluded),
        "live_count": len(live),
        "period_unique": len(period["candidates"]),
        "net_target": goal,
        "deploy": deploy,
        "rank_filters": {
            "min_dollar_hit_rate_pct": MIN_RANK_DOLLAR_HIT_RATE_PCT,
            "min_avg_net_ratio": MIN_RANK_AVG_NET_RATIO,
            "min_dollar_days": MIN_RANK_DOLLAR_DAYS,
            "require_dollar_rank_gate": require_dollar_rank_gate,
        },
        "rank_weights": RANK_WEIGHTS,
    }


def promote_ticker_to_queue(conn: sqlite3.Connection, ticker: str) -> dict:
    """Add a single ticker to queue as watching if not already active."""
    from investment_agent.account import build_dashboard_summary
    from investment_agent.stock_team import _active_queue_tickers, build_analysis_card, _latest_metrics

    summary = build_dashboard_summary(conn)
    if summary.block_new_longs:
        return {"ok": False, "message": "Regime blocks new longs."}

    sym = ticker.upper()
    if sym in REGIME_ONLY_TICKERS:
        return {"ok": False, "message": f"{sym} is regime-only."}

    if sym in _active_queue_tickers(conn):
        return {"ok": False, "message": f"{sym} already in active queue."}

    from investment_agent.journal import journal_cash_balance

    sweeps_row = conn.execute(
        "SELECT COALESCE(SUM(management_amount + tax_amount), 0) AS t FROM sweep_history"
    ).fetchone()
    sweeps = float(sweeps_row["t"]) if sweeps_row else 0.0
    tradable = journal_cash_balance(conn) - sweeps

    row = next((r for r in _latest_metrics(conn) if r["ticker"] == sym), None)
    if row is None:
        return {"ok": False, "message": f"No metrics for {sym} — run ingest first."}

    card = build_analysis_card(row, tradable)
    if card is None:
        return {"ok": False, "message": f"{sym} does not pass Step 3 filters today."}

    now = _utc_now()
    conn.execute(
        """
        INSERT INTO queue_items
          (ticker, state, suggested_size, entry_price, target_price, stop_price,
           avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
        VALUES (?, 'watching', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            card.ticker,
            card.suggested_size,
            card.entry_price,
            card.target_price,
            card.stop_price,
            card.avg_range_pct,
            card.liquidity_cap,
            card.thesis_summary,
            now,
            now,
        ),
    )
    return {"ok": True, "message": f"Added {sym} to queue as watching.", "ticker": sym}
```


---

<a id="src-investment_agent-providers-__init__-py"></a>
## `src/investment_agent/providers/__init__.py`

```python

```


---

<a id="src-investment_agent-providers-finnhub-py"></a>
## `src/investment_agent/providers/finnhub.py`

```python
"""Finnhub API client (quotes + daily candles — Phase 1)."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import httpx

FINNHUB_BASE = "https://finnhub.io/api/v1"


class FinnhubClient:
    def __init__(
        self,
        api_key: str,
        min_interval_sec: float = 1.05,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.min_interval_sec = min_interval_sec
        self._client = client or httpx.Client(timeout=30.0)
        self._owns_client = client is None
        self._last_call = 0.0

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_call
        if elapsed < self.min_interval_sec:
            time.sleep(self.min_interval_sec - elapsed)
        self._last_call = time.monotonic()

    def get_quote(self, symbol: str) -> dict:
        self._throttle()
        resp = self._client.get(
            f"{FINNHUB_BASE}/quote",
            params={"symbol": symbol.upper(), "token": self.api_key},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("c") in (None, 0):
            raise ValueError(f"Invalid quote for {symbol}: {data}")
        return data

    def get_daily_candles(
        self,
        symbol: str,
        from_ts: int,
        to_ts: int,
    ) -> list[dict]:
        self._throttle()
        resp = self._client.get(
            f"{FINNHUB_BASE}/stock/candle",
            params={
                "symbol": symbol.upper(),
                "resolution": "D",
                "from": from_ts,
                "to": to_ts,
                "token": self.api_key,
            },
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("s") != "ok":
            raise ValueError(f"Candle fetch failed for {symbol}: {payload}")
        rows = []
        for i, ts in enumerate(payload["t"]):
            rows.append(
                {
                    "ticker": symbol.upper(),
                    "date": datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
                        "%Y-%m-%d"
                    ),
                    "open": float(payload["o"][i]),
                    "high": float(payload["h"][i]),
                    "low": float(payload["l"][i]),
                    "close": float(payload["c"][i]),
                    "volume": int(payload["v"][i]),
                    "source": "finnhub",
                }
            )
        return rows


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
```


---

<a id="src-investment_agent-providers-fred-py"></a>
## `src/investment_agent/providers/fred.py`

```python
"""FRED API client (macro — Phase 1)."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def fetch_latest_observation(
    api_key: str,
    series_id: str,
    client: httpx.Client | None = None,
) -> tuple[str, float]:
    """Return (observation_date, value) for the latest observation."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    own_client = client is None
    if own_client:
        client = httpx.Client(timeout=30.0)
    try:
        resp = client.get(FRED_BASE, params=params)
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        if not obs:
            raise ValueError(f"No observations for {series_id}")
        row = obs[0]
        value = float(row["value"])
        return row["date"], value
    finally:
        if own_client:
            client.close()


def fetch_vix(api_key: str, client: httpx.Client | None = None) -> tuple[str, float]:
    return fetch_latest_observation(api_key, "VIXCLS", client=client)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
```


---

<a id="src-investment_agent-providers-yfinance_bars-py"></a>
## `src/investment_agent/providers/yfinance_bars.py`

```python
"""Daily and intraday OHLCV via yfinance (free fallback — Finnhub /stock/candle is paid-only)."""

from __future__ import annotations

import gc
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

REGIME_INDICES = ("SPY", "DIA", "QQQ")
ET = ZoneInfo("America/New_York")

_MIN_INTERVAL_SEC = float(os.environ.get("YFINANCE_MIN_INTERVAL_SEC", "0.15"))
_MAX_RETRIES = int(os.environ.get("YFINANCE_MAX_RETRIES", "3"))
_RETRY_BASE_SEC = float(os.environ.get("YFINANCE_RETRY_BASE_SEC", "1.0"))
_last_fetch_at = 0.0
_cache_configured = False


def _configure_yfinance_cache() -> None:
    global _cache_configured
    if _cache_configured:
        return
    cache_dir = os.environ.get("YFINANCE_CACHE_DIR")
    if cache_dir:
        path = Path(cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        try:
            yf.set_tz_cache_location(str(path))
        except Exception:
            pass
    _cache_configured = True


def _throttle() -> None:
    global _last_fetch_at
    now = time.monotonic()
    wait = _MIN_INTERVAL_SEC - (now - _last_fetch_at)
    if wait > 0:
        time.sleep(wait)
    _last_fetch_at = time.monotonic()


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        out = df.copy()
        out.columns = out.columns.get_level_values(0)
        return out
    return df


def _safe_float(val) -> float:
    return float(val) if val is not None and not pd.isna(val) else 0.0


def _fetch_history(
    sym: str,
    *,
    period: str,
    interval: str | None = None,
) -> pd.DataFrame:
    """Fetch OHLCV with retries; one Ticker at a time to limit open FDs."""
    _configure_yfinance_cache()
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        ticker = None
        try:
            _throttle()
            ticker = yf.Ticker(sym)
            if interval:
                df = ticker.history(
                    period=period, interval=interval, auto_adjust=False
                )
            else:
                df = ticker.history(period=period, auto_adjust=False)
            if df is None or df.empty:
                raise ValueError(f"No bars returned for {sym}")
            return _flatten_columns(df)
        except Exception as exc:
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BASE_SEC * (2**attempt))
        finally:
            if ticker is not None:
                del ticker
            gc.collect()
    assert last_exc is not None
    raise last_exc


def _rows_from_daily_df(df: pd.DataFrame, sym: str) -> list[dict]:
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Unexpected yfinance columns for {sym}: {list(df.columns)}")

    rows: list[dict] = []
    for ts, row in df.iterrows():
        close = _safe_float(row["Close"])
        if close <= 0:
            continue
        date_str = ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts)[:10]
        volume = int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
        rows.append(
            {
                "ticker": sym,
                "date": date_str,
                "open": _safe_float(row["Open"]),
                "high": _safe_float(row["High"]),
                "low": _safe_float(row["Low"]),
                "close": close,
                "volume": volume,
                "source": "yfinance",
            }
        )
    if not rows:
        raise ValueError(f"No valid daily bars for {sym}")
    return rows


def get_daily_bars(symbol: str, lookback_days: int = 60) -> list[dict]:
    """Fetch daily OHLCV bars for a US ticker/ETF."""
    sym = symbol.upper()
    period = f"{max(lookback_days, 5)}d"
    df = _fetch_history(sym, period=period)
    return _rows_from_daily_df(df, sym)


def get_intraday_bars(
    symbol: str,
    *,
    lookback_days: int = 60,
    interval: str = "5m",
) -> list[dict]:
    """Fetch intraday OHLCV bars (default 5m — supports ~60d on Yahoo free tier)."""
    sym = symbol.upper()
    # Yahoo free tier: 1m limited to ~7 calendar days per request
    if interval == "1m":
        period = f"{min(max(lookback_days, 1), 7)}d"
    else:
        period = f"{max(lookback_days, 5)}d"
    df = _fetch_history(sym, period=period, interval=interval)

    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Unexpected yfinance columns for {sym}: {list(df.columns)}")

    rows: list[dict] = []
    for ts, row in df.iterrows():
        close = _safe_float(row["Close"])
        if close <= 0:
            continue
        if hasattr(ts, "tz_convert"):
            ts_et = ts.tz_convert(ET)
        elif hasattr(ts, "tz_localize"):
            ts_et = ts.tz_localize(ET)
        else:
            ts_et = ts
        date_str = ts_et.strftime("%Y-%m-%d")
        rows.append(
            {
                "ticker": sym,
                "ts": ts_et.isoformat(),
                "date": date_str,
                "open": _safe_float(row["Open"]),
                "high": _safe_float(row["High"]),
                "low": _safe_float(row["Low"]),
                "close": close,
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
                "source": "yfinance",
                "interval": interval,
            }
        )
    if not rows:
        raise ValueError(f"No valid intraday bars for {sym}")
    return rows


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
```


---

<a id="src-investment_agent-pullback_entry-py"></a>
## `src/investment_agent/pullback_entry.py`

```python
"""Pullback limit entry — buy in lower half of expected daily swing, sell at Growth Plan target."""

from __future__ import annotations

from datetime import time

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.strategy import STOP_PCT

# Limit buy ≈ open minus this fraction of the 20d avg daily range (2–4% band).
PULLBACK_RANGE_FRACTION = 0.35
PULLBACK_MIN_PCT = 0.25
PULLBACK_MAX_PCT = 1.20
LIMIT_FILL_DEADLINE = time(11, 30)
LIMIT_FILL_DEADLINE_LABEL = "11:30 ET"


def pullback_pct_from_open(avg_range_pct: float) -> float:
    """Percent below session open for the limit buy."""
    if avg_range_pct <= 0:
        return PULLBACK_MIN_PCT
    raw = avg_range_pct * PULLBACK_RANGE_FRACTION
    return max(PULLBACK_MIN_PCT, min(raw, PULLBACK_MAX_PCT))


def limit_buy_price(session_open: float, avg_range_pct: float) -> float:
    if session_open <= 0:
        return 0.0
    pct = pullback_pct_from_open(avg_range_pct)
    return round(session_open * (1 - pct / 100), 2)


def dollar_confidence(dollar_hit_rate_pct: float) -> str:
    if dollar_hit_rate_pct >= 50.0:
        return "high"
    if dollar_hit_rate_pct >= 40.0:
        return "medium"
    return "low"


def compute_pullback_trade_plan(
    *,
    session_open: float,
    avg_range_pct: float,
    deploy_dollar: float,
    net_target: float | None = None,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    stop_pct: float = STOP_PCT,
) -> dict:
    """Limit-buy entry in the lower part of the expected swing + Growth Plan sell/stop."""
    if session_open <= 0 or deploy_dollar <= 0:
        return {}
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    pullback_pct = pullback_pct_from_open(avg_range_pct)
    entry = limit_buy_price(session_open, avg_range_pct)
    if entry <= 0:
        return {}
    shares = int((deploy_dollar - buy_fee) / entry)
    if shares <= 0:
        return {}
    stop_px = round(entry * (1 - stop_pct / 100), 2)
    target_px = round(
        sell_price_for_net_target(
            entry_price=entry,
            shares=shares,
            net_target=goal,
            buy_fee=buy_fee,
            sell_fee=sell_fee,
        ),
        2,
    )
    notional = round(shares * entry, 2)
    total_cost = round(notional + buy_fee, 2)
    net_at_target = round(shares * (target_px - entry) - buy_fee - sell_fee, 2)
    net_at_stop = round(shares * (stop_px - entry) - buy_fee - sell_fee, 2)
    est_high = session_open * (1 + (avg_range_pct / 2) / 100) if avg_range_pct > 0 else session_open * 1.015
    net_at_est_high = round(shares * (est_high - entry) - buy_fee - sell_fee, 2)
    return {
        "entry_mode": "pullback_limit",
        "session_open": round(session_open, 2),
        "pullback_pct": round(pullback_pct, 2),
        "limit_buy_price": entry,
        "entry_price": entry,
        "recommended_entry": entry,
        "limit_sell_price": target_px,
        "target_price": target_px,
        "stop_price": stop_px,
        "shares": shares,
        "recommended_shares": shares,
        "notional": notional,
        "total_cost": total_cost,
        "target_pct": round(target_move_pct(entry, target_px), 2),
        "stop_pct": stop_pct,
        "net_target": round(goal, 2),
        "net_at_target": net_at_target,
        "net_at_stop": net_at_stop,
        "estimated_net_at_typical_high": net_at_est_high,
        "fees_round_trip": round_trip_fees(buy_fee, sell_fee),
        "limit_fill_deadline_et": LIMIT_FILL_DEADLINE_LABEL,
        "skip_if_not_filled_by": LIMIT_FILL_DEADLINE_LABEL,
        "avg_range_pct": round(avg_range_pct, 2),
    }


def simulate_pullback_dollar_outcome(
    open_px: float,
    high: float,
    low: float,
    *,
    deploy_dollar: float,
    avg_range_pct: float,
    net_target: float | None = None,
    stop_pct: float = STOP_PCT,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> str:
    """Daily-bar sim: limit buy in pullback zone, then target/stop from fill price."""
    if open_px <= 0:
        return "invalid"
    entry = limit_buy_price(open_px, avg_range_pct)
    if entry <= 0:
        return "invalid"
    if low > entry:
        return "no_fill"
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    shares = int((deploy_dollar - buy_fee) / entry)
    if shares <= 0:
        return "invalid"
    target_px = sell_price_for_net_target(
        entry_price=entry,
        shares=shares,
        net_target=goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )
    stop_px = entry * (1 - stop_pct / 100)
    if high >= target_px:
        return "target"
    if low <= stop_px:
        return "stop"
    return "neither"


def net_at_high_after_pullback_fill(
    open_px: float,
    high: float,
    low: float,
    *,
    deploy_dollar: float,
    avg_range_pct: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    """Net at day high if limit filled; else 0."""
    if open_px <= 0 or low <= 0:
        return 0.0
    entry = limit_buy_price(open_px, avg_range_pct)
    if low > entry:
        return 0.0
    shares = int((deploy_dollar - buy_fee) / entry)
    if shares <= 0:
        return 0.0
    return round(shares * (high - entry) - buy_fee - sell_fee, 2)


def limit_fill_missed(
    *,
    limit_buy_price: float,
    session_low: float | None,
    as_of_time: time,
) -> bool:
    """True after the fill deadline if the session low never reached the limit buy."""
    if as_of_time <= LIMIT_FILL_DEADLINE:
        return False
    if limit_buy_price <= 0 or session_low is None:
        return False
    return session_low > limit_buy_price
```


---

<a id="src-investment_agent-regime-py"></a>
## `src/investment_agent/regime.py`

```python
"""Regime gate — triple-index intraday down blocks new longs (Product Spec v3)."""

from __future__ import annotations

from dataclasses import dataclass

REGIME_SYMBOLS = ("SPY", "DIA", "QQQ")


@dataclass(frozen=True)
class IndexQuote:
    symbol: str
    price: float
    open: float | None
    prev_close: float | None
    intraday_change_pct: float


@dataclass(frozen=True)
class RegimeSnapshot:
    captured_at: str
    spy_change_pct: float
    dia_change_pct: float
    qqq_change_pct: float
    all_indices_down: bool
    block_new_longs: bool
    summary: str


def intraday_change_pct(
    price: float,
    open_price: float | None = None,
    prev_close: float | None = None,
) -> float:
    """Percent change vs session open; fall back to prior close if open missing."""
    if open_price and open_price > 0:
        return ((price - open_price) / open_price) * 100.0
    if prev_close and prev_close > 0:
        return ((price - prev_close) / prev_close) * 100.0
    return 0.0


def index_quote_from_finnhub(symbol: str, quote: dict) -> IndexQuote:
    price = float(quote["c"])
    open_px = float(quote["o"]) if quote.get("o") else None
    prev = float(quote["pc"]) if quote.get("pc") else None
    change = intraday_change_pct(price, open_px, prev)
    return IndexQuote(
        symbol=symbol.upper(),
        price=price,
        open=open_px,
        prev_close=prev,
        intraday_change_pct=change,
    )


def evaluate_regime(
    index_quotes: dict[str, IndexQuote],
    captured_at: str,
) -> RegimeSnapshot:
    """True when SPY, DIA, and QQQ are all down intraday."""
    changes: dict[str, float] = {}
    for sym in REGIME_SYMBOLS:
        q = index_quotes.get(sym)
        if q is None:
            raise ValueError(f"Missing regime quote for {sym}")
        changes[sym] = q.intraday_change_pct

    all_down = all(changes[sym] < 0 for sym in REGIME_SYMBOLS)
    block = all_down
    if block:
        summary = (
            "Regime: SPY, DIA, QQQ all down intraday — "
            "no new longs until indices recover."
        )
    else:
        parts = ", ".join(f"{s} {changes[s]:+.2f}%" for s in REGIME_SYMBOLS)
        summary = f"Regime OK — {parts}"

    return RegimeSnapshot(
        captured_at=captured_at,
        spy_change_pct=changes["SPY"],
        dia_change_pct=changes["DIA"],
        qqq_change_pct=changes["QQQ"],
        all_indices_down=all_down,
        block_new_longs=block,
        summary=summary,
    )
```


---

<a id="src-investment_agent-scenario-py"></a>
## `src/investment_agent/scenario.py`

```python
"""$5M goal scenario visualizer — journal-fed actuals + projections (Phase 6)."""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.account import get_tax_rate
from investment_agent.finance import (
    GOAL_ACCOUNT_VALUE,
    ORIGINAL_BASIS,
    compute_month_end_sweep,
    goal_progress_pct,
)
from investment_agent.journal import compute_monthly_realized_net

MAX_PROJECTION_MONTHS = 360
DEFAULT_PROJECTION_HORIZON = 120


@dataclass(frozen=True)
class TimelinePoint:
    month_key: str
    tradable_balance: float
    goal_pct: float
    monthly_realized_net: float
    sweep_total: float
    fees_in_month: float
    label: str


def _month_keys_from_journal(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT strftime('%Y-%m', executed_at) AS mk
        FROM trade_journal
        ORDER BY mk ASC
        """
    ).fetchall()
    return [row["mk"] for row in rows]


def _journal_cash_through(conn: sqlite3.Connection, month_key: str) -> float:
    cash = ORIGINAL_BASIS
    rows = conn.execute(
        """
        SELECT side, shares, price, fee
        FROM trade_journal
        WHERE strftime('%Y-%m', executed_at) <= ?
        ORDER BY executed_at ASC, id ASC
        """,
        (month_key,),
    ).fetchall()
    for row in rows:
        notional = row["shares"] * row["price"]
        if row["side"] == "BUY":
            cash -= notional + row["fee"]
        else:
            cash += notional - row["fee"]
    return cash


def _fees_in_month(conn: sqlite3.Connection, month_key: str) -> float:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(fee), 0) AS total
        FROM trade_journal
        WHERE strftime('%Y-%m', executed_at) = ?
        """,
        (month_key,),
    ).fetchone()
    return float(row["total"]) if row else 0.0


def _cumulative_sweeps_through(
    conn: sqlite3.Connection,
    through_month: str,
    tax_rate: float,
    months: list[str],
) -> float:
    total = 0.0
    for mk in months:
        if mk > through_month:
            break
        realized = compute_monthly_realized_net(conn, mk)
        sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
        total += sweep.total_sweep
    return total


def replay_actual_timeline(conn: sqlite3.Connection) -> list[TimelinePoint]:
    """Month-by-month tradable balance from journal + computed month-end sweeps."""
    tax_rate = get_tax_rate(conn)
    months = _month_keys_from_journal(conn)
    points: list[TimelinePoint] = [
        TimelinePoint(
            month_key="start",
            tradable_balance=ORIGINAL_BASIS,
            goal_pct=goal_progress_pct(ORIGINAL_BASIS),
            monthly_realized_net=0.0,
            sweep_total=0.0,
            fees_in_month=0.0,
            label="Start ($10K basis)",
        )
    ]

    for mk in months:
        cash = _journal_cash_through(conn, mk)
        sweeps = _cumulative_sweeps_through(conn, mk, tax_rate, months)
        tradable = cash - sweeps
        realized = compute_monthly_realized_net(conn, mk)
        sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
        points.append(
            TimelinePoint(
                month_key=mk,
                tradable_balance=tradable,
                goal_pct=goal_progress_pct(tradable),
                monthly_realized_net=realized,
                sweep_total=sweep.total_sweep,
                fees_in_month=_fees_in_month(conn, mk),
                label=mk,
            )
        )
    return points


def _tradable_at_month_end(
    conn: sqlite3.Connection,
    month_key: str,
    months: list[str],
    tax_rate: float,
) -> float:
    cash = _journal_cash_through(conn, month_key)
    sweeps = _cumulative_sweeps_through(conn, month_key, tax_rate, months)
    return cash - sweeps


def _journal_pace_monthly_return(
    conn: sqlite3.Connection,
    months: list[str],
    tax_rate: float,
) -> float | None:
    """
    Average monthly return from realized P&L / tradable balance at month start.
    Avoids distortion when cash moves into open positions mid-month.
    """
    if not months:
        return None
    returns: list[float] = []
    prior_tradable = ORIGINAL_BASIS
    for mk in months:
        realized = compute_monthly_realized_net(conn, mk)
        if prior_tradable > 0:
            returns.append(realized / prior_tradable)
        prior_tradable = _tradable_at_month_end(conn, mk, months, tax_rate)
    if not returns:
        return None
    if all(r <= 0 for r in returns):
        return None
    geo = 1.0
    for r in returns:
        geo *= max(1.0 + r, 0.001)
    return geo ** (1.0 / len(returns)) - 1.0


def _avg_monthly_return_pct(
    conn: sqlite3.Connection,
    months: list[str],
    tax_rate: float,
) -> float | None:
    return _journal_pace_monthly_return(conn, months, tax_rate)


def _months_to_goal(balance: float, goal: float, monthly_return: float) -> float | None:
    if balance <= 0 or goal <= balance:
        return 0.0 if goal <= balance else None
    if monthly_return <= 0:
        return None
    growth = 1.0 + monthly_return
    if growth <= 1.0:
        return None
    return math.log(goal / balance) / math.log(growth)


def _project_balance(
    start_balance: float,
    monthly_return: float,
    months: int,
) -> list[dict]:
    pts: list[dict] = []
    bal = start_balance
    for offset in range(months + 1):
        pts.append(
            {
                "month_offset": offset,
                "balance": bal,
                "goal_pct": goal_progress_pct(bal),
            }
        )
        bal *= 1.0 + monthly_return
    return pts


def build_scenario_visualizer(
    conn: sqlite3.Connection,
    *,
    projection_horizon: int = DEFAULT_PROJECTION_HORIZON,
) -> dict:
    horizon = min(max(projection_horizon, 12), MAX_PROJECTION_MONTHS)
    actual = replay_actual_timeline(conn)
    current = actual[-1] if actual else None
    current_balance = current.tradable_balance if current else ORIGINAL_BASIS
    current_goal_pct = current.goal_pct if current else goal_progress_pct(ORIGINAL_BASIS)

    tax_rate = get_tax_rate(conn)
    month_list = _month_keys_from_journal(conn)
    avg_return = _avg_monthly_return_pct(conn, month_list, tax_rate)
    journal_months = [p for p in actual if p.month_key != "start"]

    # Include mark-to-market for open positions in current account value
    from investment_agent.journal import get_open_positions
    from investment_agent.monitor import get_latest_quotes

    quotes = get_latest_quotes(conn)
    account_value = current_balance
    for pos in get_open_positions(conn):
        px = quotes.get(pos["ticker"], pos["avg_cost"])
        account_value += pos["shares"] * px

    scenarios: dict[str, dict] = {}

    # Journal pace — compound at observed avg monthly return
    if avg_return is not None and avg_return > 0:
        months_to = _months_to_goal(account_value, GOAL_ACCOUNT_VALUE, avg_return)
        scenarios["journal_pace"] = {
            "name": "Journal pace",
            "description": (
                f"Compound at {avg_return * 100:.2f}% avg monthly realized return "
                f"from {len(journal_months)} logged month(s)."
            ),
            "monthly_return_pct": avg_return * 100,
            "months_to_goal": months_to,
            "reachable": months_to is not None and months_to <= horizon * 2,
            "points": _project_balance(account_value, avg_return, horizon),
        }
    else:
        scenarios["journal_pace"] = {
            "name": "Journal pace",
            "description": "Not enough positive journal history to project (need 2+ months with gains).",
            "monthly_return_pct": (avg_return or 0) * 100,
            "months_to_goal": None,
            "reachable": False,
            "points": _project_balance(account_value, 0.0, min(horizon, 24)),
        }

    # Strategy reference — uses account value including open positions
    trades_per_month = 0.0
    if journal_months:
        round_trips = sum(
            1
            for p in journal_months
            if p.monthly_realized_net != 0
        ) or len(journal_months)
        trades_per_month = max(round_trips, 1.0)
    # ~3-4 trades/day * ~16 days = ~56 trades/mo is max cadence; scale from journal
    strategy_monthly = (1.013**max(trades_per_month, 4)) - 1.0 if trades_per_month else 0.013
    strategy_monthly = min(strategy_monthly, 0.50)  # cap unrealistic projection
    scenarios["strategy_reference"] = {
        "name": "Strategy reference",
        "description": (
            f"If ~{max(int(trades_per_month), 4)} round trips/month at +1.13% target "
            f"(fees not modeled in projection)."
        ),
        "monthly_return_pct": strategy_monthly * 100,
        "months_to_goal": _months_to_goal(account_value, GOAL_ACCOUNT_VALUE, strategy_monthly),
        "reachable": True,
        "points": _project_balance(account_value, strategy_monthly, horizon),
    }

    # Required return to hit $5M in 10 years (120 months)
    required_10y = None
    if account_value > 0 and account_value < GOAL_ACCOUNT_VALUE:
        g = (GOAL_ACCOUNT_VALUE / account_value) ** (1.0 / 120) - 1.0
        required_10y = g
    scenarios["required_10yr"] = {
        "name": "Required (10 yr)",
        "description": "Monthly return needed to reach $5M in 120 months from today.",
        "monthly_return_pct": (required_10y or 0) * 100,
        "months_to_goal": 120.0 if required_10y else None,
        "reachable": required_10y is not None,
        "points": _project_balance(account_value, required_10y or 0, 120) if required_10y else [],
    }

    total_realized = sum(p.monthly_realized_net for p in journal_months)
    total_fees = sum(p.fees_in_month for p in journal_months)
    total_sweeps = sum(p.sweep_total for p in journal_months)

    summary_parts = [
        f"Tradable cash ${current_balance:,.2f}; account value ${account_value:,.2f} "
        f"({goal_progress_pct(account_value):.4f}% of $5M incl. open positions).",
        f"Journal spans {len(journal_months)} month(s); "
        f"realized net ${total_realized:+,.2f}, fees ${total_fees:,.2f}, sweeps ${total_sweeps:,.2f}.",
    ]
    jp = scenarios["journal_pace"]
    if jp.get("months_to_goal"):
        summary_parts.append(
            f"At journal pace ({jp['monthly_return_pct']:.2f}%/mo), "
            f"~{jp['months_to_goal']:.0f} months to $5M."
        )
    else:
        summary_parts.append("Journal pace cannot reach $5M — improve edge or cadence.")

    return {
        "goal": GOAL_ACCOUNT_VALUE,
        "original_basis": ORIGINAL_BASIS,
        "current_balance": current_balance,
        "account_value": account_value,
        "current_goal_pct": goal_progress_pct(account_value),
        "actual_timeline": [_point_to_dict(p) for p in actual],
        "scenarios": scenarios,
        "summary": " ".join(summary_parts),
        "projection_horizon_months": horizon,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def _point_to_dict(p: TimelinePoint) -> dict:
    return {
        "month_key": p.month_key,
        "tradable_balance": p.tradable_balance,
        "goal_pct": p.goal_pct,
        "monthly_realized_net": p.monthly_realized_net,
        "sweep_total": p.sweep_total,
        "fees_in_month": p.fees_in_month,
        "label": p.label,
    }
```


---

<a id="src-investment_agent-screen_actions-py"></a>
## `src/investment_agent/screen_actions.py`

```python
"""Last-completed timestamps for Ranked screener dashboard actions."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from investment_agent.account import get_setting, set_setting

ACTION_SP100 = "sp100"
ACTION_SP500 = "sp500"
ACTION_DATACENTER_US = "datacenter_us"
ACTION_DAILY_INGEST = "daily_ingest"
ACTION_FULL_INGEST = "full_ingest"
ACTION_PERIOD_SCREENER = "period_screener"
ACTION_REFRESH_RANKED = "refresh_ranked"

PRESET_ACTIONS: dict[str, str] = {
    "sp100": ACTION_SP100,
    "sp500": ACTION_SP500,
    "datacenter_us": ACTION_DATACENTER_US,
}

SCREEN_ACTIONS: dict[str, str] = {
    ACTION_SP100: "SP100 load",
    ACTION_SP500: "S&P 500 load",
    ACTION_DATACENTER_US: "DC US watch load",
    ACTION_DAILY_INGEST: "Daily ingest",
    ACTION_FULL_INGEST: "Full ingest",
    ACTION_PERIOD_SCREENER: "Run screener",
    ACTION_REFRESH_RANKED: "Refresh ranked",
}

_SETTING_PREFIX = "screen_action_"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _setting_key(action_id: str) -> str:
    return f"{_SETTING_PREFIX}{action_id}"


def record_screen_action(
    conn: sqlite3.Connection,
    action_id: str,
    *,
    detail: str = "",
) -> None:
    if action_id not in SCREEN_ACTIONS:
        raise ValueError(f"Unknown screen action: {action_id}")
    payload = json.dumps(
        {
            "completed_at": _utc_now_iso(),
            "detail": detail,
        }
    )
    set_setting(conn, _setting_key(action_id), payload)


def _parse_action_payload(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("completed_at"):
            return data
    except json.JSONDecodeError:
        pass
    if raw:
        return {"completed_at": raw, "detail": ""}
    return None


def _fallback_period_screener(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        """
        SELECT finished_at FROM screener_runs
        WHERE status = 'completed'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    if not row or not row["finished_at"]:
        return None
    return {"completed_at": row["finished_at"], "detail": "From saved screener run"}


def _fallback_ingest(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        "SELECT MAX(computed_at) AS last_at FROM ticker_metrics"
    ).fetchone()
    if not row or not row["last_at"]:
        return None
    return {"completed_at": row["last_at"], "detail": "From latest ticker metrics"}


def get_screen_action_status(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return last completion time per Ranked screener action."""
    out: dict[str, dict] = {}
    for action_id, label in SCREEN_ACTIONS.items():
        raw = get_setting(conn, _setting_key(action_id), "")
        payload = _parse_action_payload(raw)
        source = "recorded"
        if payload is None:
            if action_id == ACTION_PERIOD_SCREENER:
                payload = _fallback_period_screener(conn)
            elif action_id in (ACTION_DAILY_INGEST, ACTION_FULL_INGEST):
                payload = _fallback_ingest(conn)
            source = "inferred" if payload else "none"
        out[action_id] = {
            "id": action_id,
            "label": label,
            "completed_at": payload.get("completed_at") if payload else None,
            "detail": payload.get("detail", "") if payload else "",
            "source": source,
        }
    return out
```


---

<a id="src-investment_agent-step3_status-py"></a>
## `src/investment_agent/step3_status.py`

```python
"""Step 3 eligibility labels for watchlist / Special Watch reporting."""

from __future__ import annotations

from investment_agent.liquidity import SWING_TARGET_PCT, SWING_TOLERANCE_PCT

STEP3_PASS = "step3_pass"
TOO_QUIET = "too_quiet"
TOO_WILD = "too_wild"
LOW_LIQUIDITY = "low_liquidity"
MISSING_METRICS = "missing_metrics"
REGIME_ONLY = "regime_only"

STEP3_STATUS_LABELS: dict[str, str] = {
    STEP3_PASS: "Step 3 pass",
    TOO_QUIET: "Too quiet",
    TOO_WILD: "Too wild",
    LOW_LIQUIDITY: "Low liquidity",
    MISSING_METRICS: "Missing metrics",
    REGIME_ONLY: "Regime only",
}


def swing_band_low() -> float:
    return SWING_TARGET_PCT - SWING_TOLERANCE_PCT


def swing_band_high() -> float:
    return SWING_TARGET_PCT + SWING_TOLERANCE_PCT


def classify_step3_status(
    *,
    ticker: str = "",
    meets_liquidity: bool | None = None,
    near_swing: bool | None = None,
    avg_range_pct: float | None = None,
    regime_only: bool = False,
) -> str:
    if regime_only:
        return REGIME_ONLY
    if meets_liquidity is None and avg_range_pct is None:
        return MISSING_METRICS
    if meets_liquidity is False:
        return LOW_LIQUIDITY
    if near_swing:
        return STEP3_PASS
    if avg_range_pct is not None:
        if avg_range_pct < swing_band_low():
            return TOO_QUIET
        if avg_range_pct > swing_band_high():
            return TOO_WILD
    return TOO_QUIET
```


---

<a id="src-investment_agent-stock_team-py"></a>
## `src/investment_agent/stock_team.py`

```python
"""Stock team screener + rule-based analysis cards (Phase 2, no Claude)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.account import build_dashboard_summary
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    daily_profit_target,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.journal import journal_cash_balance
from investment_agent.strategy import (
    ACTIVE_QUEUE_STATES,
    REGIME_ONLY_TICKERS,
    STOP_PCT,
)


@dataclass(frozen=True)
class AnalysisCard:
    ticker: str
    last_quote: float
    avg_range_pct: float
    liquidity_cap: float
    suggested_size: float
    entry_price: float
    target_price: float
    stop_price: float
    thesis_summary: str


def _latest_metrics(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT m.*
        FROM ticker_metrics m
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at
          FROM ticker_metrics
          GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        """
    ).fetchall()


def _active_queue_tickers(conn: sqlite3.Connection) -> set[str]:
    placeholders = ",".join("?" for _ in ACTIVE_QUEUE_STATES)
    rows = conn.execute(
        f"""
        SELECT DISTINCT ticker FROM queue_items
        WHERE state IN ({placeholders})
        """,
        ACTIVE_QUEUE_STATES,
    ).fetchall()
    return {row["ticker"] for row in rows}


def build_analysis_card(
    row: sqlite3.Row,
    tradable_cash: float,
) -> AnalysisCard | None:
    ticker = row["ticker"]
    if ticker in REGIME_ONLY_TICKERS:
        return None
    if not row["meets_liquidity_min"]:
        return None
    if not row["near_swing_target"]:
        return None

    last_quote = float(row["last_quote"] or row["last_close"] or 0)
    if last_quote <= 0:
        return None

    liquidity_cap = float(row["liquidity_cap"] or 0)
    suggested_size = min(liquidity_cap, tradable_cash)
    if suggested_size <= 0:
        return None

    target_net = daily_profit_target(tradable_cash)
    shares = int((suggested_size - DEFAULT_BUY_FEE) / last_quote) if last_quote > 0 else 0
    if shares <= 0:
        return None
    target = sell_price_for_net_target(
        entry_price=last_quote,
        shares=shares,
        net_target=target_net,
    )
    target = round(target, 2)
    target_pct = target_move_pct(last_quote, target)
    stop = last_quote * (1 - STOP_PCT / 100)
    avg_range = float(row["avg_range_pct"] or 0)
    swing_note = (
        "near ~3% swing target"
        if row["near_swing_target"]
        else f"avg range {avg_range:.1f}% (watch ~3%)"
    )

    thesis = (
        f"{ticker}: {swing_note}. Liquidity cap ${liquidity_cap:,.0f}. "
        f"Entry ~${last_quote:.2f} → sell ${target:.2f} (+{target_pct:.2f}% / ${target_net:.0f} net/day), "
        f"stop −{STOP_PCT}% ${stop:.2f}. "
        f"Size ${suggested_size:,.0f} (min of cap and tradable cash). "
        f"Execute in E*TRADE; log fill in journal."
    )

    return AnalysisCard(
        ticker=ticker,
        last_quote=last_quote,
        avg_range_pct=avg_range,
        liquidity_cap=liquidity_cap,
        suggested_size=suggested_size,
        entry_price=last_quote,
        target_price=target,
        stop_price=round(stop, 2),
        thesis_summary=thesis,
    )


def screen_candidates(conn: sqlite3.Connection) -> list[AnalysisCard]:
    """Return qualified tickers sorted by avg range proximity to 3%."""
    sweeps_row = conn.execute(
        "SELECT COALESCE(SUM(management_amount + tax_amount), 0) AS t FROM sweep_history"
    ).fetchone()
    sweeps = float(sweeps_row["t"]) if sweeps_row else 0.0
    tradable = journal_cash_balance(conn) - sweeps

    cards: list[AnalysisCard] = []
    for row in _latest_metrics(conn):
        card = build_analysis_card(row, tradable)
        if card:
            cards.append(card)

    cards.sort(key=lambda c: abs(c.avg_range_pct - 3.0))
    return cards


def sync_queue_from_screener(conn: sqlite3.Connection, *, max_items: int = 5) -> dict:
    """
    Add top ranked live Step 3 passers to queue as 'watching' if not already active.
    Uses 14d period rank score (not range proximity alone).
    Respects regime block (returns message, does not add when blocked).
    """
    summary = build_dashboard_summary(conn)
    if summary.block_new_longs:
        return {
            "ok": False,
            "added": 0,
            "live_count": 0,
            "already_in_queue": 0,
            "message": "Regime blocks new longs — SPY/DIA/QQQ all down intraday.",
        }

    active = _active_queue_tickers(conn)
    from investment_agent.period_screener import build_ranked_candidates

    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live_ranked = [r for r in ranked if r.get("live_pass_today")]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    added_tickers: list[str] = []

    if live_ranked:
        live_count = len(live_ranked)
        pending = [r for r in live_ranked if r["ticker"] not in active]
        for row in pending[:max_items]:
            conn.execute(
                """
                INSERT INTO queue_items
                  (ticker, state, suggested_size, entry_price, target_price, stop_price,
                   avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
                VALUES (?, 'watching', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["ticker"],
                    row.get("suggested_size") or row.get("liquidity_cap") or 0,
                    row.get("entry_price"),
                    row.get("target_price"),
                    row.get("stop_price"),
                    row.get("avg_range_pct"),
                    row.get("liquidity_cap"),
                    row.get("thesis_summary") or "",
                    now,
                    now,
                ),
            )
            added_tickers.append(row["ticker"])
        live_names_source = live_ranked
    else:
        # No period history yet — fall back to live screener sorted by ~3% range
        live_cards = screen_candidates(conn)
        live_count = len(live_cards)
        pending = [c for c in live_cards if c.ticker not in active]
        for card in pending[:max_items]:
            conn.execute(
                """
                INSERT INTO queue_items
                  (ticker, state, suggested_size, entry_price, target_price, stop_price,
                   avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
                VALUES (?, 'watching', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card.ticker,
                    card.suggested_size,
                    card.entry_price,
                    card.target_price,
                    card.stop_price,
                    card.avg_range_pct,
                    card.liquidity_cap,
                    card.thesis_summary,
                    now,
                    now,
                ),
            )
            added_tickers.append(card.ticker)
        live_names_source = live_cards

    added = len(added_tickers)
    already = live_count - len(pending)

    if added:
        message = (
            f"Added {added} ticker(s) by 14d rank score: {', '.join(added_tickers)}."
        )
    elif not live_count:
        message = "No tickers pass Step 3 today — run ingest after loading your watchlist."
    elif already >= live_count:
        live_names = ", ".join(
            (r["ticker"] if isinstance(r, dict) else r.ticker)
            for r in live_names_source[:8]
        )
        suffix = f" ({live_names})" if live_names else ""
        message = (
            f"Nothing to add — all {live_count} live ranked candidate(s) "
            f"are already in the queue{suffix}."
        )
    else:
        message = "No new tickers to add (queue already has active picks)."

    return {
        "ok": True,
        "added": added,
        "live_count": live_count,
        "already_in_queue": already,
        "added_tickers": added_tickers,
        "message": message,
    }


def list_queue(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, ticker, state, suggested_size, entry_price, target_price,
               stop_price, avg_range_pct, liquidity_cap, thesis_summary,
               created_at, updated_at
        FROM queue_items
        ORDER BY
          CASE state
            WHEN 'in_trade' THEN 0
            WHEN 'alert' THEN 1
            WHEN 'armed' THEN 2
            WHEN 'approved' THEN 3
            WHEN 'watching' THEN 4
            WHEN 'eod' THEN 5
            WHEN 'runner' THEN 6
            ELSE 7
          END,
          updated_at DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def advance_queue_state(conn: sqlite3.Connection, item_id: int) -> dict:
    from investment_agent.strategy import NEXT_STATE, QUEUE_STATES

    row = conn.execute(
        "SELECT id, ticker, state FROM queue_items WHERE id = ?", (item_id,)
    ).fetchone()
    if not row:
        return {"ok": False, "error": "Queue item not found"}

    current = row["state"]
    nxt = NEXT_STATE.get(current)
    if nxt is None:
        return {"ok": False, "error": f"No next state after '{current}'"}

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn.execute(
        "UPDATE queue_items SET state = ?, updated_at = ? WHERE id = ?",
        (nxt, now, item_id),
    )
    return {"ok": True, "id": item_id, "from_state": current, "to_state": nxt}


def set_queue_state(conn: sqlite3.Connection, item_id: int, state: str) -> dict:
    if state not in QUEUE_STATES:
        return {"ok": False, "error": f"Invalid state: {state}"}
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    cur = conn.execute(
        "UPDATE queue_items SET state = ?, updated_at = ? WHERE id = ?",
        (state, now, item_id),
    )
    if cur.rowcount == 0:
        return {"ok": False, "error": "Queue item not found"}
    return {"ok": True, "id": item_id, "state": state}


def card_to_dict(card: AnalysisCard) -> dict:
    return {
        "ticker": card.ticker,
        "last_quote": card.last_quote,
        "avg_range_pct": card.avg_range_pct,
        "liquidity_cap": card.liquidity_cap,
        "suggested_size": card.suggested_size,
        "entry_price": card.entry_price,
        "target_price": card.target_price,
        "stop_price": card.stop_price,
        "thesis_summary": card.thesis_summary,
    }
```


---

<a id="src-investment_agent-strategy-py"></a>
## `src/investment_agent/strategy.py`

```python
"""Trading strategy constants (Product Spec v3)."""

from __future__ import annotations

TARGET_PCT = 1.50
STOP_PCT = 0.75
MAX_TRADES_PER_DAY = 2
ENTRY_DELAY_MINUTES = 30
STOP_DAY_AFTER_STOP = True
ENTRY_WINDOW_ET = "10:00–14:30"

QUEUE_STATES = (
    "watching",
    "approved",
    "armed",
    "alert",
    "in_trade",
    "eod",
    "closed",
    "runner",
)

ACTIVE_QUEUE_STATES = ("watching", "approved", "armed", "alert", "in_trade", "eod", "runner")

# Queue states polled by intraday monitor (Phase 4)
MONITORED_STATES = ("armed", "alert", "in_trade", "eod")

ALERT_TYPES = (
    "TARGET_HIT",
    "STOP_HIT",
    "EOD_FLATTEN",
    "NEAR_TARGET",
    "NEAR_STOP",
)

# Indices used for regime — not primary trade candidates
REGIME_ONLY_TICKERS = frozenset({"SPY", "DIA", "QQQ"})

NEXT_STATE: dict[str, str | None] = {
    "watching": "approved",
    "approved": "armed",
    "armed": "alert",
    "alert": "in_trade",
    "in_trade": "eod",
    "eod": "closed",
    "closed": "runner",
    "runner": None,
}
```


---

<a id="src-investment_agent-strategy_models-py"></a>
## `src/investment_agent/strategy_models.py`

```python
"""Strategy presets and scalable daily profit targets for backtesting."""

from __future__ import annotations

from dataclasses import dataclass

from investment_agent.finance import (
    DAILY_TARGET_BASE,
    daily_profit_target,
    ORIGINAL_BASIS,
)

__all__ = [
    "daily_profit_target",
    "target_pct_for_dollars",
    "StrategyModel",
    "RECOMMENDED_MODEL",
    "DAILY_TARGET_MODEL",
    "ORIGINAL_MODEL",
    "PRESETS",
]


def target_pct_for_dollars(
    *,
    net_needed: float,
    deploy_dollar: float,
    fees: float,
    min_pct: float = 1.0,
    max_pct: float = 4.0,
) -> float | None:
    """Percent move required on deploy_dollar to net net_needed after round-trip fees."""
    if deploy_dollar <= 0 or net_needed <= 0:
        return None
    gross_needed = net_needed + fees
    pct = 100.0 * gross_needed / deploy_dollar
    if pct < min_pct or pct > max_pct:
        return None
    return pct


@dataclass(frozen=True)
class StrategyModel:
    name: str
    description: str
    stop_pct: float
    max_trades_per_day: int
    entry_bar_delay: int  # 5m bars to skip after open (6 ≈ 30 min)
    stop_day_after_stop: bool
    target_pct: float | None = None  # fixed exit; None = dynamic dollar target
    daily_base_target: float = 150.0
    daily_step: float = 50.0
    daily_step_every: float = 5_000.0
    min_dynamic_target_pct: float = 1.0
    max_dynamic_target_pct: float = 4.0
    apply_monthly_sweeps: bool = True


RECOMMENDED_MODEL = StrategyModel(
    name="recommended",
    description="Wider stop, fewer trades, no re-entry after stop, 30m entry delay",
    target_pct=1.50,
    stop_pct=0.75,
    max_trades_per_day=2,
    entry_bar_delay=6,
    stop_day_after_stop=True,
    apply_monthly_sweeps=True,
)

DAILY_TARGET_MODEL = StrategyModel(
    name="daily_target",
    description="$150/day net at $10K (scales +$50 per $5K), dynamic per-trade target",
    target_pct=None,
    stop_pct=0.75,
    max_trades_per_day=2,
    entry_bar_delay=6,
    stop_day_after_stop=True,
    daily_base_target=DAILY_TARGET_BASE,
    apply_monthly_sweeps=True,
)

ORIGINAL_MODEL = StrategyModel(
    name="original",
    description="Original plan: +1.13% / −0.50%, unlimited re-entries",
    target_pct=1.13,
    stop_pct=0.50,
    max_trades_per_day=999,
    entry_bar_delay=0,
    stop_day_after_stop=False,
    apply_monthly_sweeps=False,
)

PRESETS: dict[str, StrategyModel] = {
    m.name: m for m in (ORIGINAL_MODEL, RECOMMENDED_MODEL, DAILY_TARGET_MODEL)
}
```


---

<a id="src-investment_agent-tradability-py"></a>
## `src/investment_agent/tradability.py`

```python
"""Intraday tradability — can we reach the Growth Plan $ target from *this* entry?

Uses Finnhub live quote fields already stored in ``quotes`` (price, open, high, low,
prev_close). No intraday candles or paid APIs required.
"""

from __future__ import annotations

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.dollar_target import DollarHistoryStats, assess_dollar_reachability
from investment_agent.strategy import STOP_PCT

# Gap-and-chase filters (from Aug 2026 week review — NFLX Wed gap)
MAX_GAP_UP_PCT = 1.0
MAX_GAP_DOWN_PCT = 1.5
MAX_CHASE_ABOVE_OPEN_PCT = 0.50
MIN_SESSION_RANGE_PCT = 0.40
MIN_NET_AT_DAY_HIGH_RATIO = 0.95
TARGET_RETRACE_TOLERANCE = 0.998


def _gap_at_open_pct(quote: dict) -> float | None:
    open_px = quote.get("open")
    prev = quote.get("prev_close")
    if not open_px or not prev or prev <= 0:
        return None
    return ((open_px - prev) / prev) * 100.0


def _pct(from_px: float, to_px: float) -> float:
    if from_px <= 0:
        return 0.0
    return ((to_px - from_px) / from_px) * 100.0


def _trade_plan(
    entry_price: float,
    deploy_dollar: float,
    net_target: float,
) -> dict:
    if entry_price <= 0 or deploy_dollar <= 0:
        return {}
    shares = int((deploy_dollar - DEFAULT_BUY_FEE) / entry_price)
    if shares <= 0:
        return {}
    stop_px = entry_price * (1 - STOP_PCT / 100)
    target_px = round(
        sell_price_for_net_target(
            entry_price=entry_price,
            shares=shares,
            net_target=net_target,
        ),
        2,
    )
    fees = round_trip_fees()
    return {
        "entry_price": round(entry_price, 2),
        "shares": shares,
        "target_price": target_px,
        "stop_price": round(stop_px, 2),
        "target_pct": round(target_move_pct(entry_price, target_px), 2),
        "fees_round_trip": fees,
    }


def assess_entry_tradability(
    *,
    quote: dict | None,
    entry_price: float,
    deploy_dollar: float,
    net_target: float | None = None,
    avg_range_pct: float | None = None,
    dollar_history: DollarHistoryStats | None = None,
) -> dict:
    """Return tradability verdict for entering at ``entry_price`` right now."""
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    plan = _trade_plan(entry_price=entry_price, deploy_dollar=deploy_dollar, net_target=goal)
    if not plan or not quote:
        return {
            "verdict": "UNKNOWN",
            "headline": "Cannot assess — missing quote or invalid entry",
            "detail": "Refresh live data and confirm entry price.",
            "checks": [],
            "plan": plan or {},
        }

    price = float(quote.get("price") or entry_price)
    open_px = quote.get("open")
    high = quote.get("high")
    low = quote.get("low")
    target_px = float(plan["target_price"])
    stop_px = float(plan["stop_price"])
    shares = int(plan["shares"])
    target_pct = float(plan["target_pct"])

    checks: list[dict] = []
    blockers: list[str] = []
    cautions: list[str] = []

    def add(name: str, ok: bool | None, message: str) -> None:
        checks.append({"name": name, "ok": ok, "message": message})

    gap_pct = _gap_at_open_pct(quote)
    if gap_pct is not None:
        if gap_pct > MAX_GAP_UP_PCT:
            blockers.append(f"Gap up {gap_pct:.2f}% at open — chasing, little upside room")
            add("Gap at open", False, f"+{gap_pct:.2f}% vs prior close (max {MAX_GAP_UP_PCT}%)")
        elif gap_pct < -MAX_GAP_DOWN_PCT:
            cautions.append(f"Gap down {gap_pct:.2f}% — weak open")
            add("Gap at open", None, f"{gap_pct:.2f}% vs prior close")
        else:
            add("Gap at open", True, f"{gap_pct:+.2f}% vs prior close")

    if open_px and open_px > 0 and entry_price > open_px:
        chase = _pct(open_px, entry_price)
        if chase > MAX_CHASE_ABOVE_OPEN_PCT:
            blockers.append(f"Entry {chase:.2f}% above open — need extra upside for ${goal:.0f}")
            add("Chase above open", False, f"+{chase:.2f}% above today's open")
        elif chase > 0.15:
            cautions.append(f"Buying {chase:.2f}% above open")
            add("Chase above open", None, f"+{chase:.2f}% above open")
        else:
            add("Chase above open", True, f"{chase:+.2f}% vs open")

    remaining_pct = _pct(entry_price, target_px)
    add(
        "Room to target",
        True if remaining_pct >= target_pct * 0.9 else None,
        f"Need +{remaining_pct:.2f}% to ${target_px:.2f} sell ({target_pct:.2f}% move)",
    )

    max_net_at_high: float | None = None
    if high is not None and high > 0:
        max_net_at_high = round(shares * (high - entry_price) - plan["fees_round_trip"], 2)
        required_move = target_px - entry_price
        move_so_far = high - entry_price
        move_ratio = (move_so_far / required_move) if required_move > 0 else 0.0

        if move_ratio >= 0.85 and max_net_at_high < goal * MIN_NET_AT_DAY_HIGH_RATIO:
            blockers.append(
                f"Day high ${high:.2f} only nets ~${max_net_at_high:.0f} from this entry "
                f"(need ${goal:.0f})"
            )
            add(
                "Day-high P&L",
                False,
                f"High ${high:.2f} → ~${max_net_at_high:.0f} net (need ${goal:.0f})",
            )
        elif max_net_at_high >= goal * MIN_NET_AT_DAY_HIGH_RATIO:
            add(
                "Day-high P&L",
                True,
                f"High ${high:.2f} could net ~${max_net_at_high:.0f}",
            )
        else:
            add(
                "Day-high P&L",
                None,
                f"High ${high:.2f} so far — session may still develop (need ${goal:.0f})",
            )

        if high >= target_px:
            if price < target_px * TARGET_RETRACE_TOLERANCE:
                blockers.append(
                    f"Target ${target_px:.2f} already touched — price now ${price:.2f} (missed window)"
                )
                add("Target window", False, f"High reached ${high:.2f}; current ${price:.2f}")
            else:
                add("Target window", True, f"At/above target ${target_px:.2f}")
        else:
            shortfall = target_px - high
            add(
                "Target window",
                None if shortfall / entry_price * 100 < 0.15 else True,
                f"High ${high:.2f} is ${shortfall:.2f} below sell target",
            )

    if low is not None and low <= stop_px:
        blockers.append(f"Session low ${low:.2f} already at/below stop ${stop_px:.2f}")
        add("Stop zone", False, f"Low ${low:.2f} ≤ stop ${stop_px:.2f}")
    else:
        add("Stop zone", True, f"Low ${float(low):.2f} above stop ${stop_px:.2f}" if low is not None else "Low not available")

    if open_px and high is not None and low is not None and open_px > 0:
        session_range = ((high - low) / open_px) * 100.0
        if session_range < MIN_SESSION_RANGE_PCT and remaining_pct > 1.0:
            cautions.append(f"Tight session range {session_range:.2f}% — chop risk")
            add("Session range", None, f"{session_range:.2f}% intraday range (tight)")
        else:
            add("Session range", True, f"{session_range:.2f}% intraday range")

    if avg_range_pct is not None and remaining_pct > avg_range_pct * 0.6:
        cautions.append(
            f"Need +{remaining_pct:.2f}% but typical range ~{avg_range_pct:.1f}%/day"
        )
        add(
            "Vs avg swing",
            None,
            f"Need +{remaining_pct:.2f}% · 20d avg range ~{avg_range_pct:.1f}%",
        )
    elif avg_range_pct is not None:
        add(
            "Vs avg swing",
            True,
            f"Need +{remaining_pct:.2f}% · avg range ~{avg_range_pct:.1f}%",
        )

    dollar_pred = assess_dollar_reachability(
        entry_price=entry_price,
        deploy_dollar=deploy_dollar,
        net_target=goal,
        avg_range_pct=avg_range_pct,
        history=dollar_history,
    )
    for check in dollar_pred.get("checks", []):
        add(check["name"], check["ok"], check["message"])
    if dollar_pred.get("verdict") == "NOT_REACHABLE":
        blockers.append(dollar_pred.get("detail") or "Historical range unlikely to reach $ goal")
    elif dollar_pred.get("verdict") == "MARGINAL":
        cautions.append(dollar_pred.get("detail") or "Marginal historical $ reachability")

    if blockers:
        verdict = "NOT_TRADABLE"
        headline = "Not tradable for today's $ goal"
        detail = blockers[0]
    elif cautions:
        verdict = "CAUTION"
        headline = "Marginal — tight room for $ goal"
        detail = cautions[0]
    else:
        verdict = "TRADABLE"
        headline = "Tradable from this entry"
        detail = f"Room to ${target_px:.2f} sell for ~${goal:.0f} net after fees"

    return {
        "verdict": verdict,
        "headline": headline,
        "detail": detail,
        "checks": checks,
        "blockers": blockers,
        "cautions": cautions,
        "gap_at_open_pct": round(gap_pct, 3) if gap_pct is not None else None,
        "remaining_to_target_pct": round(remaining_pct, 3),
        "target_pct_required": target_pct,
        "max_net_at_day_high": max_net_at_high if high is not None else None,
        "net_target": goal,
        "plan": plan,
        "dollar_prediction": dollar_pred,
        "expected_net_at_typical_high": dollar_pred.get("expected_net_at_typical_high"),
        "historical_avg_net_at_high": dollar_pred.get("historical_avg_net_at_high"),
        "dollar_hit_rate_pct": dollar_pred.get("dollar_hit_rate_pct"),
    }
```


---

<a id="src-investment_agent-trading_day-py"></a>
## `src/investment_agent/trading_day.py`

```python
"""Intraday trading day status — go/no-go gate, top pick, live refresh."""

from __future__ import annotations

import sqlite3
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary, get_setting, set_setting
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.journal import (
    compute_today_realized_net,
    get_completed_round_trips,
    get_open_positions,
)
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.regime import REGIME_SYMBOLS
from investment_agent.strategy import ENTRY_DELAY_MINUTES, ENTRY_WINDOW_ET, STOP_PCT
from investment_agent.dollar_target import load_dollar_history
from investment_agent.pullback_entry import (
    LIMIT_FILL_DEADLINE,
    compute_pullback_trade_plan,
    dollar_confidence,
    limit_fill_missed,
)
from investment_agent.tradability import assess_entry_tradability

ET = ZoneInfo("America/New_York")
MARKET_OPEN = time(9, 30)
ENTRY_READY = time(10, 0)  # 30 min after open
ENTRY_CUTOFF = time(14, 30)
MARKET_CLOSE = time(16, 0)
QUOTE_STALE_MINUTES = 20
TOP_PICK_MAX_DROP_PCT = 0.50  # down more than 0.5% from open → caution
TOP_PICK_NO_GO_DROP_PCT = 0.75  # aligns with stop width
ACTIONABLE_PICK_SCAN = 10  # walk top N live ranked for tradability


def _session_open_from_quote(quote: dict | None, fallback: float | None = None) -> float | None:
    if not quote:
        return fallback
    open_px = quote.get("open")
    if open_px and open_px > 0:
        return float(open_px)
    return fallback


def _pullback_plan_for_row(
    row: dict,
    quote: dict | None,
    *,
    deploy: float,
    net_target: float,
) -> dict:
    avg_range = float(row.get("avg_range_pct") or 0)
    session_open = _session_open_from_quote(
        quote,
        fallback=float(row.get("entry_price") or row.get("last_quote") or 0) or None,
    )
    if not session_open or session_open <= 0:
        return {}
    return compute_pullback_trade_plan(
        session_open=session_open,
        avg_range_pct=avg_range,
        deploy_dollar=deploy,
        net_target=net_target,
    )


def _assess_pick_tradability(
    row: dict,
    quote: dict | None,
    *,
    deploy: float,
    net_target: float,
    conn: sqlite3.Connection,
) -> tuple[dict, dict, dict]:
    """Return (pullback_plan, tradability, dollar_history dict)."""
    avg_range = float(row.get("avg_range_pct") or 0) or None
    plan = _pullback_plan_for_row(row, quote, deploy=deploy, net_target=net_target)
    limit_entry = plan.get("limit_buy_price") or plan.get("entry_price")
    hist = load_dollar_history(
        conn,
        row["ticker"],
        end_date=today_et_str(),
        deploy_dollar=deploy,
        net_target=net_target,
        avg_range_pct=avg_range,
    )
    tradability = assess_entry_tradability(
        quote=quote,
        entry_price=limit_entry or float(row.get("last_quote") or 0),
        deploy_dollar=deploy,
        net_target=net_target,
        avg_range_pct=avg_range,
        dollar_history=hist,
    ) if limit_entry and quote else {
        "verdict": "UNKNOWN",
        "headline": "No live quote",
        "detail": "Refresh live data for tradability check",
        "checks": [],
    }
    return plan, tradability, hist.to_dict()


def now_et() -> datetime:
    return datetime.now(ET)


def today_et_str() -> str:
    return now_et().strftime("%Y-%m-%d")


def session_phase(when: datetime | None = None) -> str:
    now = when or now_et()
    if now.weekday() >= 5:
        return "weekend"
    t = now.time()
    if t < MARKET_OPEN:
        return "pre_market"
    if t < ENTRY_READY:
        return "opening_wait"
    if t < ENTRY_CUTOFF:
        return "trade_window"
    if t < MARKET_CLOSE:
        return "late_day"
    return "after_hours"


def _latest_quote_rows(conn: sqlite3.Connection, tickers: list[str]) -> dict[str, dict]:
    if not tickers:
        return {}
    placeholders = ",".join("?" for _ in tickers)
    rows = conn.execute(
        f"""
        SELECT q.ticker, q.price, q.open, q.high, q.low, q.prev_close, q.captured_at
        FROM quotes q
        INNER JOIN (
          SELECT ticker, MAX(captured_at) AS max_at
          FROM quotes
          WHERE ticker IN ({placeholders})
          GROUP BY ticker
        ) latest ON q.ticker = latest.ticker AND q.captured_at = latest.max_at
        """,
        tickers,
    ).fetchall()
    return {
        row["ticker"]: {
            "price": float(row["price"]),
            "open": float(row["open"]) if row["open"] else None,
            "high": float(row["high"]) if row["high"] else None,
            "low": float(row["low"]) if row["low"] else None,
            "prev_close": float(row["prev_close"]) if row["prev_close"] else None,
            "captured_at": row["captured_at"],
        }
        for row in rows
    }


def _quote_age_minutes(captured_at: str | None) -> float | None:
    if not captured_at:
        return None
    try:
        ts = captured_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return age.total_seconds() / 60.0
    except ValueError:
        return None


def _intraday_change_pct(quote: dict) -> float | None:
    price = quote.get("price")
    open_px = quote.get("open")
    prev = quote.get("prev_close")
    if price is None:
        return None
    if open_px and open_px > 0:
        return ((price - open_px) / open_px) * 100.0
    if prev and prev > 0:
        return ((price - prev) / prev) * 100.0
    return None


def _opening_range_pct(quote: dict) -> float | None:
    """Approximate session range vs open using quote high/low."""
    open_px = quote.get("open")
    high = quote.get("high")
    low = quote.get("low")
    if not open_px or open_px <= 0 or high is None or low is None:
        return None
    return ((high - low) / open_px) * 100.0


def get_top_pick(conn: sqlite3.Connection) -> dict | None:
    """Highest ranked live candidate that passes the dollar-goal rank gate."""
    pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live = [
        r for r in ranked
        if r.get("live_pass_today") and r.get("passes_dollar_rank_gate", True)
    ]

    if pinned:
        match = next((r for r in live if r["ticker"] == pinned), None)
        if match:
            return {**match, "source": "pinned"}
        row = next((r for r in ranked if r["ticker"] == pinned), None)
        if row:
            return {**row, "source": "pinned_not_live", "live_pass_today": False}

    if not live:
        return None
    return {**live[0], "source": "ranked_#1"}


def _live_ranked_candidates(conn: sqlite3.Connection, limit: int = ACTIONABLE_PICK_SCAN) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live = [
        r for r in ranked
        if r.get("live_pass_today") and r.get("passes_dollar_rank_gate", True)
    ]
    pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
    if pinned:
        pin_row = next((r for r in ranked if r["ticker"] == pinned), None)
        if pin_row:
            live = [pin_row] + [r for r in live if r["ticker"] != pinned]
    return live[:limit]


def resolve_actionable_pick(
    conn: sqlite3.Connection,
    *,
    quotes: dict[str, dict],
    deploy: float,
    net_target: float,
) -> tuple[dict | None, list[dict]]:
    """Pick first live ranked name that passes intraday tradability for today's $ goal."""
    skipped: list[dict] = []
    candidates = _live_ranked_candidates(conn)

    for row in candidates:
        sym = row["ticker"]
        quote = quotes.get(sym)
        if not quote or not quote.get("price"):
            skipped.append({
                "ticker": sym,
                "rank_score": row.get("score"),
                "reason": "No live quote",
                "verdict": "UNKNOWN",
            })
            continue

        plan, tradability, hist_dict = _assess_pick_tradability(
            row, quote, deploy=deploy, net_target=net_target, conn=conn
        )
        pick = {
            **row,
            **plan,
            "tradability": tradability,
            "dollar_history": hist_dict,
            "dollar_confidence": dollar_confidence(float(row.get("dollar_hit_rate_pct") or 0)),
        }
        if row.get("source") != "pinned" and sym == get_setting(conn, "pinned_pick_ticker", "").strip().upper():
            pick["source"] = "pinned"

        verdict = tradability.get("verdict")
        if verdict in ("NOT_TRADABLE", "CAUTION"):
            skipped.append({
                "ticker": sym,
                "rank_score": row.get("score"),
                "reason": tradability.get("detail"),
                "verdict": verdict,
                "dollar_hit_rate_pct": row.get("dollar_hit_rate_pct"),
                "expected_net_at_typical_high": tradability.get("expected_net_at_typical_high"),
                "limit_buy_price": plan.get("limit_buy_price"),
            })
            continue

        source = pick.get("source")
        if not source:
            pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
            source = "pinned" if sym == pinned else f"ranked_#{len(skipped) + 1}"
        pick["source"] = source
        return pick, skipped

    return None, skipped


def stopped_out_today(conn: sqlite3.Connection, date_key: str | None = None) -> bool:
    """True if any closed round trip today lost money (stop-out day)."""
    day = date_key or today_et_str()
    for trip in get_completed_round_trips(conn, limit=200):
        sell_day = trip["sell_at"][:10]
        try:
            dt = datetime.fromisoformat(trip["sell_at"].replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            sell_day = dt.astimezone(ET).strftime("%Y-%m-%d")
        except ValueError:
            pass
        if sell_day != day:
            continue
        if trip["net_pnl"] < -20:
            return True
    return False


def refresh_live_quotes(conn: sqlite3.Connection, settings) -> dict:
    """Fetch fresh Finnhub quotes for regime indices, top pick, queue, and open positions."""
    from investment_agent.db import insert_quote, insert_regime_snapshot, log_ingest
    from investment_agent.providers.finnhub import FinnhubClient, utc_now_iso as fh_now
    from investment_agent.regime import evaluate_regime, index_quote_from_finnhub

    symbols: set[str] = set(REGIME_SYMBOLS)
    for row in _live_ranked_candidates(conn, limit=ACTIONABLE_PICK_SCAN):
        symbols.add(row["ticker"])

    pick = get_top_pick(conn)
    if pick:
        symbols.add(pick["ticker"])

    rows = conn.execute(
        "SELECT DISTINCT ticker FROM queue_items WHERE state NOT IN ('closed')"
    ).fetchall()
    symbols.update(row["ticker"] for row in rows)
    for pos in get_open_positions(conn):
        symbols.add(pos["ticker"])

    errors: list[str] = []
    updated: list[str] = []
    index_quotes = {}

    if not settings.finnhub_api_key:
        return {
            "ok": False,
            "error": "FINNHUB_API_KEY not set — add to .env to refresh live quotes",
            "symbols_requested": sorted(symbols),
        }

    fh = FinnhubClient(settings.finnhub_api_key)
    try:
        for symbol in sorted(symbols):
            try:
                q = fh.get_quote(symbol)
                insert_quote(
                    conn,
                    {
                        "ticker": symbol,
                        "captured_at": fh_now(),
                        "price": float(q["c"]),
                        "open": float(q.get("o") or 0) or None,
                        "high": float(q.get("h") or 0) or None,
                        "low": float(q.get("l") or 0) or None,
                        "prev_close": float(q.get("pc") or 0) or None,
                    },
                )
                updated.append(symbol)
                if symbol in REGIME_SYMBOLS:
                    index_quotes[symbol] = index_quote_from_finnhub(symbol, q)
            except Exception as exc:
                errors.append(f"{symbol}: {exc}")
                log_ingest(conn, "finnhub", "error", f"refresh {symbol}: {exc}")

        if len(index_quotes) == len(REGIME_SYMBOLS):
            snap = evaluate_regime(index_quotes, fh_now())
            insert_regime_snapshot(
                conn,
                {
                    "captured_at": snap.captured_at,
                    "spy_change_pct": snap.spy_change_pct,
                    "dia_change_pct": snap.dia_change_pct,
                    "qqq_change_pct": snap.qqq_change_pct,
                    "all_indices_down": snap.all_indices_down,
                    "block_new_longs": snap.block_new_longs,
                    "summary": snap.summary,
                },
            )
    finally:
        fh.close()

    return {
        "ok": len(updated) > 0,
        "updated": updated,
        "errors": errors,
        "symbols_requested": sorted(symbols),
    }


TOP_PICK_NO_GO_DROP_PCT = 0.75  # aligns with stop width
MAX_ENTRY_SLIPPAGE_PCT = 0.35  # planned buy vs live — warn above this


def compute_trade_plan(
    *,
    entry_price: float,
    deploy_dollar: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    net_target: float | None = None,
    stop_pct: float = STOP_PCT,
) -> dict:
    """Shares, Growth-Plan sell price, stop price, and net P&L at each exit."""
    if entry_price <= 0 or deploy_dollar <= 0:
        return {}
    shares = int((deploy_dollar - buy_fee) / entry_price)
    if shares <= 0:
        return {}
    daily_goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    stop_px = entry_price * (1 - stop_pct / 100)
    target_px = sell_price_for_net_target(
        entry_price=entry_price,
        shares=shares,
        net_target=daily_goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )
    target_px = round(target_px, 2)
    notional = shares * entry_price
    total_cost = notional + buy_fee
    net_at_target = round(shares * (target_px - entry_price) - buy_fee - sell_fee, 2)
    net_at_stop = round(shares * (stop_px - entry_price) - buy_fee - sell_fee, 2)
    return {
        "entry_price": round(entry_price, 2),
        "shares": shares,
        "notional": round(notional, 2),
        "total_cost": round(total_cost, 2),
        "target_price": target_px,
        "stop_price": round(stop_px, 2),
        "target_pct": round(target_move_pct(entry_price, target_px), 2),
        "stop_pct": stop_pct,
        "net_target": round(daily_goal, 2),
        "net_at_target": net_at_target,
        "net_at_stop": net_at_stop,
        "fees_round_trip": round_trip_fees(buy_fee, sell_fee),
    }


def validate_planned_trade(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    planned_price: float,
    shares: float | None = None,
) -> dict:
    """Check whether a planned entry still matches live price and strategy rules."""
    sym = ticker.upper().strip()
    day_status = build_trading_day_status(conn)
    quotes = _latest_quote_rows(conn, [sym])
    live_q = quotes.get(sym)
    live_price = float(live_q["price"]) if live_q else None

    tradable = day_status.get("top_pick", {})  # for deploy hint
    pick = get_top_pick(conn)
    deploy = float(pick.get("suggested_size") or 0) if pick and pick.get("ticker") == sym else 0
    if deploy <= 0:
        from investment_agent.account import build_dashboard_summary

        deploy = build_dashboard_summary(conn).tradable_cash

    if shares is not None and shares > 0:
        remaining = max(day_status["daily_target"] - day_status.get("today_realized_net", 0), 0)
        plan = compute_trade_plan(
            entry_price=planned_price,
            deploy_dollar=planned_price * shares + DEFAULT_BUY_FEE,
            net_target=remaining or day_status["daily_target"],
        )
        plan["shares"] = int(shares)
        plan["notional"] = round(planned_price * shares, 2)
        plan["total_cost"] = round(plan["notional"] + DEFAULT_BUY_FEE, 2)
        stop_px = planned_price * (1 - STOP_PCT / 100)
        s = int(shares)
        daily_goal = remaining or day_status["daily_target"]
        target_px = sell_price_for_net_target(
            entry_price=planned_price,
            shares=s,
            net_target=daily_goal,
        )
        plan["target_price"] = round(target_px, 2)
        plan["stop_price"] = round(stop_px, 2)
        plan["target_pct"] = round(target_move_pct(planned_price, target_px), 2)
        plan["net_at_target"] = round(s * (target_px - planned_price) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
        plan["net_at_stop"] = round(s * (stop_px - planned_price) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
    else:
        remaining = max(day_status["daily_target"] - day_status.get("today_realized_net", 0), 0)
        plan = compute_trade_plan(
            entry_price=planned_price,
            deploy_dollar=deploy,
            net_target=remaining or day_status["daily_target"],
        )

    checks: list[dict] = []
    verdict = "GO"
    messages: list[str] = []

    if not live_price:
        verdict = "CAUTION"
        messages.append("No live quote — refresh live data before buying.")
        checks.append({"name": "Live quote", "ok": False, "message": "Missing — click Refresh live data"})
    else:
        slippage = ((planned_price - live_price) / live_price) * 100.0
        if slippage > MAX_ENTRY_SLIPPAGE_PCT:
            verdict = "NO_GO"
            messages.append(f"Planned price ${planned_price:.2f} is {slippage:.2f}% above live ${live_price:.2f}.")
            checks.append({"name": "Price vs live", "ok": False, "message": f"+{slippage:.2f}% above live (max {MAX_ENTRY_SLIPPAGE_PCT}%)"})
        elif slippage < -MAX_ENTRY_SLIPPAGE_PCT:
            checks.append({"name": "Price vs live", "ok": True, "message": f"{slippage:+.2f}% vs live ${live_price:.2f}"})
        else:
            checks.append({"name": "Price vs live", "ok": True, "message": f"Within {slippage:+.2f}% of live ${live_price:.2f}"})

        remaining = max(day_status["daily_target"] - day_status.get("today_realized_net", 0), 0)
        goal = remaining or day_status["daily_target"]
        metrics_row = conn.execute(
            """
            SELECT avg_range_pct FROM ticker_metrics
            WHERE ticker = ?
            ORDER BY computed_at DESC LIMIT 1
            """,
            (sym,),
        ).fetchone()
        avg_range = float(metrics_row["avg_range_pct"]) if metrics_row and metrics_row["avg_range_pct"] else None
        hist = load_dollar_history(
            conn,
            sym,
            end_date=today_et_str(),
            deploy_dollar=deploy,
            net_target=goal,
        )
        trad = assess_entry_tradability(
            quote=live_q,
            entry_price=planned_price,
            deploy_dollar=deploy,
            net_target=goal,
            avg_range_pct=avg_range,
            dollar_history=hist,
        )
        if trad.get("verdict") == "NOT_TRADABLE":
            verdict = "NO_GO"
            messages.append(trad.get("detail") or "Not tradable for today's dollar target")
            checks.append({"name": "Tradability", "ok": False, "message": trad.get("detail", "Not tradable")})
        elif trad.get("verdict") == "CAUTION":
            if verdict == "GO":
                verdict = "CAUTION"
            checks.append({"name": "Tradability", "ok": None, "message": trad.get("detail", "Marginal")})
        elif trad.get("verdict") == "TRADABLE":
            checks.append({"name": "Tradability", "ok": True, "message": trad.get("detail", "Tradable for $ goal")})
        else:
            checks.append({"name": "Tradability", "ok": None, "message": trad.get("detail", "Unknown — refresh live data")})

    if pick and pick.get("ticker") != sym:
        if verdict == "GO":
            verdict = "CAUTION"
        messages.append(f"{sym} is not today's #1 pick ({pick.get('ticker')} is).")
        checks.append({"name": "Rank", "ok": False, "message": f"Not #1 — top pick is {pick.get('ticker')}"})
    elif pick:
        checks.append({"name": "Rank", "ok": True, "message": f"{sym} is today's ranked #1"})

    if day_status["verdict"] == "NO_GO":
        verdict = "NO_GO"
        messages.append(day_status["headline"])
        checks.append({"name": "Day status", "ok": False, "message": day_status["headline"]})
    elif day_status["verdict"] in ("CAUTION", "WAIT"):
        if verdict == "GO":
            verdict = "CAUTION"
        checks.append({"name": "Day status", "ok": None, "message": day_status["headline"]})
    else:
        checks.append({"name": "Day status", "ok": True, "message": day_status["headline"]})

    daily_target = day_status["daily_target"]
    if plan.get("net_at_target") is not None:
        goal = plan.get("net_target") or daily_target
        if plan["net_at_target"] >= goal * 0.98:
            checks.append({"name": "Target P&L", "ok": True, "message": f"Sell nets ~${plan['net_at_target']:.2f} (Growth Plan ${goal:.0f}/day)"})
        else:
            if verdict == "GO":
                verdict = "CAUTION"
            checks.append({"name": "Target P&L", "ok": None, "message": f"Sell nets ~${plan['net_at_target']:.2f} — below ${goal:.0f} day goal on this size"})

    if not plan:
        verdict = "NO_GO"
        messages.append("Could not size trade — check price and deploy amount.")

    headline = "Recommended — proceed in E*TRADE" if verdict == "GO" else (
        "Caution — review before buying" if verdict == "CAUTION" else "Not recommended — do not buy"
    )

    return {
        "verdict": verdict,
        "headline": headline,
        "messages": messages,
        "checks": checks,
        "ticker": sym,
        "planned_price": round(planned_price, 2),
        "live_price": round(live_price, 2) if live_price else None,
        "plan": plan,
        "day_status_verdict": day_status["verdict"],
    }


def _build_pick_detail(
    pick: dict,
    *,
    quote: dict | None,
    deploy: float,
    net_target: float,
) -> dict:
    avg_range = float(pick.get("avg_range_pct") or 0)
    session_open = _session_open_from_quote(
        quote,
        fallback=float(pick.get("session_open") or pick.get("entry_price") or 0) or None,
    )
    plan = pick if pick.get("limit_buy_price") else (
        compute_pullback_trade_plan(
            session_open=session_open or 0,
            avg_range_pct=avg_range,
            deploy_dollar=deploy,
            net_target=net_target,
        )
        if session_open
        else {}
    )
    if not plan and session_open:
        plan = compute_trade_plan(
            entry_price=session_open,
            deploy_dollar=deploy,
            net_target=net_target,
        )

    tradability = pick.get("tradability")
    limit_entry = plan.get("limit_buy_price") or plan.get("entry_price")
    if tradability is None and quote and limit_entry:
        hist = pick.get("dollar_history")
        tradability = assess_entry_tradability(
            quote=quote,
            entry_price=limit_entry,
            deploy_dollar=deploy,
            net_target=net_target,
            avg_range_pct=avg_range or None,
        )

    live_price = float(quote["price"]) if quote and quote.get("price") else None
    detail = {
        "ticker": pick["ticker"],
        "rank_score": pick.get("score"),
        "hit_rate_pct": pick.get("hit_rate_pct"),
        "source": pick.get("source"),
        "live_pass_today": bool(pick.get("live_pass_today")),
        "entry_mode": plan.get("entry_mode", "pullback_limit"),
        "session_open": plan.get("session_open"),
        "pullback_pct": plan.get("pullback_pct"),
        "limit_buy_price": plan.get("limit_buy_price"),
        "limit_sell_price": plan.get("limit_sell_price") or plan.get("target_price"),
        "limit_fill_deadline_et": plan.get("limit_fill_deadline_et"),
        "skip_if_not_filled_by": plan.get("skip_if_not_filled_by"),
        "recommended_entry": plan.get("limit_buy_price") or plan.get("entry_price"),
        "entry_price": plan.get("limit_buy_price") or plan.get("entry_price"),
        "target_price": plan.get("target_price"),
        "stop_price": plan.get("stop_price"),
        "target_pct": plan.get("target_pct"),
        "recommended_shares": plan.get("shares"),
        "notional": plan.get("notional"),
        "total_cost": plan.get("total_cost"),
        "net_target": plan.get("net_target"),
        "net_at_target": plan.get("net_at_target"),
        "net_at_stop": plan.get("net_at_stop"),
        "suggested_size": deploy,
        "quote_price": live_price,
        "quote_as_of": quote.get("captured_at") if quote else None,
        "thesis_summary": pick.get("thesis_summary"),
        "tradability": tradability,
        "dollar_hit_rate_pct": pick.get("dollar_hit_rate_pct")
        or (tradability or {}).get("dollar_hit_rate_pct"),
        "dollar_confidence": pick.get("dollar_confidence")
        or dollar_confidence(float(pick.get("dollar_hit_rate_pct") or 0)),
        "expected_net_at_typical_high": plan.get("estimated_net_at_typical_high")
        or (tradability or {}).get("expected_net_at_typical_high"),
        "historical_avg_net_at_high": (tradability or {}).get("historical_avg_net_at_high"),
        "dollar_history": pick.get("dollar_history"),
        "dollar_prediction": (tradability or {}).get("dollar_prediction"),
    }
    return detail


def build_trading_day_status(conn: sqlite3.Connection) -> dict:
    """Go/no-go panel for intraday manual trading."""
    now = now_et()
    phase = session_phase(now)
    summary = build_dashboard_summary(conn)
    day = today_et_str()
    today_net = compute_today_realized_net(conn, day)
    daily_target = summary.daily_target
    target_met = today_net >= daily_target
    stopped = stopped_out_today(conn, day)
    open_positions = get_open_positions(conn)
    remaining_net = max(daily_target - today_net, 0)
    net_for_plan = remaining_net or daily_target

    watch: list[str] = list(REGIME_SYMBOLS)
    for row in _live_ranked_candidates(conn, limit=ACTIONABLE_PICK_SCAN):
        watch.append(row["ticker"])
    quotes = _latest_quote_rows(conn, watch)

    pick, skipped_picks = resolve_actionable_pick(
        conn,
        quotes=quotes,
        deploy=summary.tradable_cash,
        net_target=net_for_plan,
    )
    ranked_first = get_top_pick(conn)

    regime_quote_ages = [
        _quote_age_minutes(quotes[s]["captured_at"])
        for s in REGIME_SYMBOLS
        if s in quotes
    ]
    max_age = max(regime_quote_ages) if regime_quote_ages else None
    quotes_stale = max_age is None or max_age > QUOTE_STALE_MINUTES

    pick_quote = quotes.get(pick["ticker"]) if pick else None
    pick_change = _intraday_change_pct(pick_quote) if pick_quote else None
    pick_range = _opening_range_pct(pick_quote) if pick_quote else None

    checks: list[dict] = []
    verdict = "GO"
    headline = "Good to trade"
    detail = "Conditions favor taking the top ranked setup after the 30-minute gate."

    def add_check(name: str, ok: bool | None, message: str, *, blocking: bool = False):
        checks.append({"name": name, "ok": ok, "message": message, "blocking": blocking})

    if phase == "weekend":
        verdict = "NO_GO"
        headline = "Market closed (weekend)"
        detail = "No intraday session — review ranked list for Monday."
        add_check("Session", False, "Weekend — market closed", blocking=True)
    elif phase == "pre_market":
        verdict = "WAIT"
        headline = "Pre-market — wait for open"
        detail = f"Market opens 9:30 AM ET. First entry window after {ENTRY_READY.strftime('%H:%M')} ET ({ENTRY_DELAY_MINUTES} min delay)."
        add_check("Session", None, "Pre-market", blocking=True)
    elif phase == "opening_wait":
        verdict = "WAIT"
        headline = "Opening period — wait for 30-minute gate"
        mins_left = int(
            (
                datetime.combine(now.date(), ENTRY_READY, tzinfo=ET) - now
            ).total_seconds()
            // 60
        )
        detail = f"Let the opening chop settle. Entry gate opens in ~{max(mins_left, 0)} min (10:00 AM ET)."
        add_check("30-minute gate", None, f"Wait until {ENTRY_READY.strftime('%H:%M')} ET", blocking=True)
    elif phase in ("late_day", "after_hours"):
        verdict = "NO_GO"
        headline = "Too late for new entries"
        detail = f"Entry window was {ENTRY_WINDOW_ET} ET. Manage open positions only."
        add_check("Entry window", False, "Past 2:30 PM ET cutoff", blocking=True)
    else:
        add_check(
            "30-minute gate",
            True,
            f"Past {ENTRY_READY.strftime('%H:%M')} ET — opening period complete",
        )
        add_check("Entry window", True, f"Within {ENTRY_WINDOW_ET} ET window")

    if summary.block_new_longs:
        verdict = "NO_GO"
        headline = "Regime blocks new longs"
        detail = summary.regime["summary"] if summary.regime else "SPY/DIA/QQQ all down intraday."
        add_check("Regime", False, detail, blocking=True)
    elif phase in ("trade_window", "opening_wait", "pre_market"):
        regime_msg = summary.regime["summary"] if summary.regime else "Run refresh for live regime"
        add_check("Regime", True, regime_msg)

    if quotes_stale:
        if verdict == "GO":
            verdict = "CAUTION"
        headline = headline if verdict != "GO" else "Refresh live data"
        detail = "Quote data is stale — click Refresh live before deciding."
        add_check(
            "Live quotes",
            False,
            f"Last quote {max_age:.0f} min ago (refresh needed)" if max_age else "No quotes — run refresh",
            blocking=False,
        )
    else:
        add_check("Live quotes", True, f"Updated within {max_age:.0f} min")

    if target_met:
        verdict = "NO_GO"
        headline = "Daily target hit — stop trading"
        detail = f"Today net ${today_net:,.2f} ≥ ${daily_target:,.0f} goal. Protect the green day."
        add_check("Daily target", True, f"${today_net:,.2f} / ${daily_target:,.0f}", blocking=True)
    else:
        remaining = daily_target - today_net
        add_check(
            "Daily target",
            None,
            f"${today_net:,.2f} of ${daily_target:,.2f} (${remaining:,.2f} to go)",
        )

    if stopped:
        verdict = "NO_GO"
        headline = "Stop-out day — done for today"
        detail = "A losing round trip was logged today. No revenge trades."
        add_check("Stop-out rule", False, "Loss logged today — no more entries", blocking=True)
    else:
        add_check("Stop-out rule", True, "No stop-out logged today")

    if open_positions:
        if verdict == "GO":
            verdict = "CAUTION"
        pos = open_positions[0]
        detail = f"Open position in {pos['ticker']} — finish before a new full-size entry."
        add_check(
            "Open position",
            None,
            f"{pos['ticker']}: {pos['shares']:.0f} sh @ ${pos['avg_cost']:.2f}",
        )
    else:
        add_check("Open position", True, "Flat — ready for one full-size entry")

    if pick is None:
        if verdict in ("GO", "CAUTION"):
            verdict = "NO_GO"
        if skipped_picks:
            skipped_names = ", ".join(s["ticker"] for s in skipped_picks[:5])
            headline = "No tradable setup for today's $ goal"
            detail = (
                f"Step 3 passers fail live tradability for ${net_for_plan:.0f} net: "
                f"{skipped_names}"
                + (f" +{len(skipped_picks) - 5} more" if len(skipped_picks) > 5 else "")
            )
            add_check("Top pick", False, detail, blocking=True)
        else:
            headline = "No live top pick"
            detail = "No ticker passes Step 3 today — run ingest and refresh ranked screener."
            add_check("Top pick", False, "No live Step 3 candidates today", blocking=True)
    else:
        pick_ok = True
        pick_msg = (
            f"{pick['ticker']} (score {pick.get('score', 0):.3f}, "
            f"${pick.get('dollar_hit_rate_pct', 0):.0f}% $ hit, "
            f"{pick.get('hit_rate_pct', 0):.0f}% 1.5% hit)"
        )
        if not pick.get("live_pass_today"):
            pick_ok = False
            pick_msg += " — not live Step 3 today"
        if pick_change is not None:
            pick_msg += f" · {pick_change:+.2f}% from open"
            if pick_change <= -TOP_PICK_NO_GO_DROP_PCT:
                pick_ok = False
                if verdict == "GO":
                    verdict = "NO_GO"
                headline = f"{pick['ticker']} weak at open"
                detail = f"Top pick down {pick_change:.2f}% from open — skip or wait for next ranked name."
            elif pick_change <= -TOP_PICK_MAX_DROP_PCT:
                pick_ok = False
                if verdict == "GO":
                    verdict = "CAUTION"
                detail = f"{pick['ticker']} slightly weak ({pick_change:+.2f}%) — extra caution."
        if pick_range is not None and pick_range < 0.4 and phase == "trade_window":
            pick_msg += f" · tight {pick_range:.2f}% range (chop)"

        trad = (pick.get("tradability") or {}) if pick else {}
        trad_verdict = trad.get("verdict")
        if trad_verdict == "NOT_TRADABLE":
            pick_ok = False
            if verdict == "GO":
                verdict = "NO_GO"
            headline = f"{pick['ticker']} — not tradable for ${net_for_plan:.0f}"
            detail = trad.get("detail") or "Insufficient room from entry to Growth Plan sell target."
            pick_msg += f" · NOT TRADABLE: {trad.get('detail', '')[:80]}"
        elif trad_verdict == "CAUTION":
            pick_ok = False
            if verdict == "GO":
                verdict = "CAUTION"
            detail = trad.get("detail") or detail
            pick_msg += f" · CAUTION: {trad.get('detail', '')[:80]}"
        elif trad_verdict == "TRADABLE":
            pick_msg += " · limit entry tradable for $ goal"

        add_check("Top pick", pick_ok if pick_ok else False, pick_msg, blocking=not pick_ok and pick_change is not None and pick_change <= -TOP_PICK_NO_GO_DROP_PCT)

    if skipped_picks:
        skipped_names = ", ".join(s["ticker"] for s in skipped_picks[:3])
        add_check(
            "Skipped (not tradable)",
            None,
            f"{skipped_names}" + (f" +{len(skipped_picks) - 3} more" if len(skipped_picks) > 3 else ""),
        )

    if summary.vix is not None and summary.vix >= 22:
        if verdict == "GO":
            verdict = "CAUTION"
        add_check("VIX", False, f"VIX {summary.vix:.1f} — elevated volatility")
    elif summary.vix is not None:
        add_check("VIX", True, f"VIX {summary.vix:.1f}")

    # Second trade only if target not met and no stop
    can_second_trade = (
        not target_met
        and not stopped
        and not summary.block_new_longs
        and phase == "trade_window"
        and today_net > 0
        and not open_positions
    )

    pick_detail = None
    second_pick_detail = None
    if pick:
        pick_quote = quotes.get(pick["ticker"])
        pick_detail = _build_pick_detail(
            pick,
            quote=pick_quote,
            deploy=float(pick.get("suggested_size") or summary.tradable_cash),
            net_target=net_for_plan,
        )
        if pick_change is not None:
            pick_detail["intraday_change_pct"] = round(pick_change, 3)
        if pick_range is not None:
            pick_detail["opening_range_pct"] = round(pick_range, 3)
        if pick_detail and pick_quote:
            limit_px = pick_detail.get("limit_buy_price")
            day_low = pick_quote.get("low")
            if limit_fill_missed(
                limit_buy_price=float(limit_px or 0),
                session_low=float(day_low) if day_low is not None else None,
                as_of_time=now.time(),
            ):
                verdict = "NO_GO"
                headline = f"{pick['ticker']} — pullback limit not filled"
                detail = (
                    f"Limit buy ${limit_px:.2f} was not reached by {LIMIT_FILL_DEADLINE.strftime('%H:%M')} ET "
                    "— skip today, do not chase with a market order."
                )
                add_check(
                    "Limit fill",
                    False,
                    detail,
                    blocking=True,
                )
            elif limit_px and day_low is not None and day_low <= limit_px:
                add_check(
                    "Limit fill",
                    True,
                    f"Session low ${day_low:.2f} touched limit ${limit_px:.2f} — limit may have filled",
                )
            elif limit_px:
                add_check(
                    "Limit fill",
                    None,
                    f"Place limit buy ${limit_px:.2f} · cancel if not filled by 11:30 ET",
                )

    # Second pick: next tradable live name after actionable #1
    second_candidates = _live_ranked_candidates(conn, limit=ACTIONABLE_PICK_SCAN)
    if pick:
        second_candidates = [r for r in second_candidates if r["ticker"] != pick["ticker"]]
    second_row = None
    for row in second_candidates:
        sym = row["ticker"]
        quote = quotes.get(sym)
        if not quote or not quote.get("price"):
            continue
        plan, t, hist_dict = _assess_pick_tradability(
            row,
            quote,
            deploy=float(row.get("suggested_size") or summary.tradable_cash),
            net_target=net_for_plan,
            conn=conn,
        )
        if t.get("verdict") == "TRADABLE":
            second_row = {
                **row,
                **plan,
                "tradability": t,
                "dollar_history": hist_dict,
                "source": "ranked_#2",
            }
            break

    if second_row:
        second_quote = quotes.get(second_row["ticker"])
        second_pick_detail = _build_pick_detail(
            second_row,
            quote=second_quote,
            deploy=float(second_row.get("suggested_size") or summary.tradable_cash),
            net_target=net_for_plan,
        )

    return {
        "as_of_et": now.replace(microsecond=0).isoformat(),
        "date_et": day,
        "session_phase": phase,
        "verdict": verdict,
        "headline": headline,
        "detail": detail,
        "checks": checks,
        "today_realized_net": round(today_net, 2),
        "daily_target": daily_target,
        "daily_target_met": target_met,
        "stopped_out_today": stopped,
        "can_enter_new": verdict == "GO" and not open_positions and not target_met and not stopped,
        "can_second_trade": can_second_trade,
        "open_positions": open_positions,
        "top_pick": pick_detail,
        "second_pick": second_pick_detail,
        "ranked_first": ranked_first["ticker"] if ranked_first else None,
        "skipped_not_tradable": skipped_picks,
        "next_ranked": _next_ranked(conn, pick["ticker"] if pick else None),
        "remaining_daily_net": round(remaining_net, 2),
        "strategy": {
            "daily_net_target": daily_target,
            "stop_pct": STOP_PCT,
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "entry_window_et": ENTRY_WINDOW_ET,
        },
    }


def _next_ranked(conn: sqlite3.Connection, after_ticker: str | None) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live = [r for r in ranked if r.get("live_pass_today")]
    if after_ticker:
        live = [r for r in live if r["ticker"] != after_ticker]
    return [
        {
            "ticker": r["ticker"],
            "rank_score": r.get("score"),
            "hit_rate_pct": r.get("hit_rate_pct"),
            "dollar_hit_rate_pct": r.get("dollar_hit_rate_pct"),
        }
        for r in live[:5]
    ]


def pin_top_pick(conn: sqlite3.Connection, ticker: str) -> dict:
    sym = ticker.upper().strip()
    set_setting(conn, "pinned_pick_ticker", sym)
    return {"ok": True, "pinned_pick_ticker": sym}


def clear_pinned_pick(conn: sqlite3.Connection) -> dict:
    set_setting(conn, "pinned_pick_ticker", "")
    return {"ok": True, "pinned_pick_ticker": ""}
```


---

<a id="src-investment_agent-watchlist-py"></a>
## `src/investment_agent/watchlist.py`

```python
"""Watchlist management — presets, import, universe stats (Phase 7)."""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from investment_agent.account import set_setting
from investment_agent.db import get_active_watchlist
from investment_agent.ingest import DEFAULT_TICKERS
from investment_agent.liquidity import SWING_TARGET_PCT
from investment_agent.step3_status import (
    STEP3_STATUS_LABELS,
    classify_step3_status,
    swing_band_high,
    swing_band_low,
)
from investment_agent.strategy import REGIME_ONLY_TICKERS

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_DIR = REPO_ROOT / "universe"

PRESETS: dict[str, str] = {
    "starter10": "Starter 10 (default ingest list)",
    "sp100": "S&P 100 liquid subset (~100 tickers)",
    "sp500": "S&P 500 full index (~500 tickers + regime ETFs)",
    "datacenter_us": "US AI data center buildout & maintenance (~96 tickers)",
}

SPECIAL_WATCH_EXTRAS_PREFIX = "special_watch_extras:"
_TICKER_RE = re.compile(r"^[A-Z]{1,6}$")


@dataclass(frozen=True)
class PresetInfo:
    name: str
    description: str
    ticker_count: int
    path: Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_presets() -> list[PresetInfo]:
    items: list[PresetInfo] = []
    for name, desc in PRESETS.items():
        path = UNIVERSE_DIR / f"{name}.txt"
        tickers = load_tickers_from_file(path) if path.is_file() else []
        items.append(PresetInfo(name=name, description=desc, ticker_count=len(tickers), path=path))
    return items


def load_tickers_from_file(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Universe file not found: {path}")
    tickers: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tickers.append(line.upper())
    # preserve order, dedupe
    seen: set[str] = set()
    out: list[str] = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def load_preset_tickers(preset_name: str) -> list[str]:
    name = preset_name.lower().strip()
    if name not in PRESETS:
        known = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset {preset_name!r}. Choose one of: {known}")
    if name == "starter10" and not (UNIVERSE_DIR / "starter10.txt").is_file():
        return [t.upper() for t in DEFAULT_TICKERS]
    path = UNIVERSE_DIR / f"{name}.txt"
    return load_tickers_from_file(path)


def _special_watch_extras_key(preset_name: str) -> str:
    return f"{SPECIAL_WATCH_EXTRAS_PREFIX}{preset_name.lower().strip()}"


def get_special_watch_extras(conn: sqlite3.Connection, preset_name: str) -> list[str]:
    """Manually added tickers for a Special Watch preset (stored in app_settings)."""
    key = _special_watch_extras_key(preset_name)
    row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    if not row:
        return []
    try:
        data = json.loads(row["value"])
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    seen: set[str] = set()
    out: list[str] = []
    for item in data:
        t = str(item).strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _save_special_watch_extras(
    conn: sqlite3.Connection, preset_name: str, tickers: list[str]
) -> None:
    set_setting(conn, _special_watch_extras_key(preset_name), json.dumps(tickers))


def merge_special_watch_tickers(preset_name: str, extras: list[str]) -> list[str]:
    """Preset file tickers plus manual extras (deduped, preset order first)."""
    base = load_preset_tickers(preset_name)
    seen = set(base)
    out = list(base)
    for ticker in extras:
        t = ticker.upper()
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def add_special_watch_ticker(
    conn: sqlite3.Connection,
    preset_name: str,
    ticker: str,
) -> dict:
    """Add a ticker to Special Watch and the active watchlist (metrics on next ingest)."""
    name = preset_name.lower().strip()
    if name not in PRESETS:
        known = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset {preset_name!r}. Choose one of: {known}")

    t = ticker.strip().upper()
    if not t or not _TICKER_RE.match(t):
        raise ValueError(f"Invalid ticker symbol {ticker!r} — use 1–6 letters (e.g. NBIS)")

    preset_tickers = set(load_preset_tickers(name))
    extras = get_special_watch_extras(conn, name)
    added_to_extras = False
    if t not in preset_tickers and t not in extras:
        extras.append(t)
        _save_special_watch_extras(conn, name, extras)
        added_to_extras = True

    upsert_tickers(conn, [t], source="special_watch", added_via=f"{name}_manual")
    return {
        "ok": True,
        "preset": name,
        "ticker": t,
        "added_to_extras": added_to_extras,
        "already_in_preset": t in preset_tickers,
        "tickers_activated": 1,
    }


def get_active_watchlist_details(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT ticker, sector, active, source, added_via, added_at
        FROM watchlist
        WHERE active = 1
        ORDER BY ticker
        """
    ).fetchall()
    return [dict(row) for row in rows]


def load_preset_into_watchlist(
    conn: sqlite3.Connection,
    preset_name: str,
    *,
    replace: bool = False,
) -> dict:
    tickers = load_preset_tickers(preset_name)
    if replace:
        conn.execute("UPDATE watchlist SET active = 0")
    added = upsert_tickers(conn, tickers, source="preset", added_via=preset_name)
    from investment_agent.screen_actions import PRESET_ACTIONS, record_screen_action

    action_id = PRESET_ACTIONS.get(preset_name.lower().strip())
    if action_id:
        record_screen_action(
            conn,
            action_id,
            detail=f"{len(tickers)} tickers loaded, {added} activated",
        )
    return {
        "ok": True,
        "preset": preset_name,
        "tickers_loaded": len(tickers),
        "tickers_activated": added,
        "replace": replace,
    }


def import_tickers(
    conn: sqlite3.Connection,
    tickers: list[str],
    *,
    source: str = "import",
    added_via: str = "manual",
) -> dict:
    normalized = [t.strip().upper() for t in tickers if t.strip()]
    added = upsert_tickers(conn, normalized, source=source, added_via=added_via)
    return {"ok": True, "tickers_received": len(normalized), "tickers_activated": added}


def deactivate_ticker(conn: sqlite3.Connection, ticker: str) -> dict:
    cur = conn.execute(
        "UPDATE watchlist SET active = 0 WHERE ticker = ?",
        (ticker.upper(),),
    )
    return {"ok": cur.rowcount > 0, "ticker": ticker.upper()}


def upsert_tickers(
    conn: sqlite3.Connection,
    tickers: list[str],
    *,
    source: str = "manual",
    added_via: str = "manual",
) -> int:
    now = _utc_now()
    count = 0
    for ticker in tickers:
        t = ticker.upper()
        conn.execute(
            """
            INSERT INTO watchlist (ticker, active, source, added_via, added_at)
            VALUES (?, 1, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
              active = 1,
              source = excluded.source,
              added_via = excluded.added_via
            """,
            (t, source, added_via, now),
        )
        count += 1
    return count


def _parse_iso_age_hours(iso_ts: str | None) -> float | None:
    if not iso_ts:
        return None
    try:
        from datetime import datetime, timezone

        ts = iso_ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return age.total_seconds() / 3600.0
    except ValueError:
        return None


def compute_data_freshness(conn: sqlite3.Connection) -> dict:
    """How old quotes and metrics are for the active watchlist."""
    active = get_active_watchlist(conn)
    if not active:
        return {
            "quotes_newest_at": None,
            "quotes_oldest_at": None,
            "quotes_max_age_hours": None,
            "metrics_newest_at": None,
            "metrics_max_age_hours": None,
            "stale_quote_count": 0,
            "stale_metrics_count": 0,
        }

    placeholders = ",".join("?" for _ in active)
    quote_rows = conn.execute(
        f"""
        SELECT ticker, MAX(captured_at) AS last_at
        FROM quotes
        WHERE ticker IN ({placeholders})
        GROUP BY ticker
        """,
        active,
    ).fetchall()
    metric_rows = conn.execute(
        f"""
        SELECT ticker, MAX(computed_at) AS last_at
        FROM ticker_metrics
        WHERE ticker IN ({placeholders})
        GROUP BY ticker
        """,
        active,
    ).fetchall()

    quote_times = [r["last_at"] for r in quote_rows if r["last_at"]]
    metric_times = [r["last_at"] for r in metric_rows if r["last_at"]]
    quote_ages = [_parse_iso_age_hours(t) for t in quote_times]
    metric_ages = [_parse_iso_age_hours(t) for t in metric_times]
    quote_ages_valid = [a for a in quote_ages if a is not None]
    metric_ages_valid = [a for a in metric_ages if a is not None]

    newest_quote = max(quote_times) if quote_times else None
    oldest_quote = min(quote_times) if quote_times else None
    newest_metric = max(metric_times) if metric_times else None

    return {
        "quotes_newest_at": newest_quote,
        "quotes_oldest_at": oldest_quote,
        "quotes_max_age_hours": round(max(quote_ages_valid), 1) if quote_ages_valid else None,
        "metrics_newest_at": newest_metric,
        "metrics_max_age_hours": round(max(metric_ages_valid), 1) if metric_ages_valid else None,
        "stale_quote_count": sum(1 for a in quote_ages_valid if a >= 4.0),
        "stale_metrics_count": sum(1 for a in metric_ages_valid if a >= 24.0),
        "tickers_with_quotes": len(quote_times),
        "tickers_with_metrics": len(metric_times),
    }


def compute_universe_stats(conn: sqlite3.Connection) -> dict:
    """Step 3 pass/filter counts from latest ticker_metrics per active ticker."""
    rows = conn.execute(
        """
        SELECT m.ticker, m.meets_liquidity_min, m.near_swing_target, m.avg_range_pct
        FROM ticker_metrics m
        INNER JOIN watchlist w ON w.ticker = m.ticker AND w.active = 1
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        ORDER BY m.ticker
        """
    ).fetchall()

    active = get_active_watchlist(conn)
    universe_size = len(active)
    with_metrics = len(rows)
    pass_liq = sum(1 for r in rows if r["meets_liquidity_min"])
    pass_swing = sum(1 for r in rows if r["near_swing_target"])
    pass_both = sum(
        1
        for r in rows
        if r["meets_liquidity_min"]
        and r["near_swing_target"]
        and r["ticker"] not in REGIME_ONLY_TICKERS
    )
    tradeable = sum(1 for t in active if t not in REGIME_ONLY_TICKERS)
    filtered_out = max(tradeable - pass_both, 0)

    return {
        "universe_size": universe_size,
        "tradeable_universe": tradeable,
        "with_metrics": with_metrics,
        "pass_liquidity": pass_liq,
        "pass_swing": pass_swing,
        "pass_both_step3": pass_both,
        "filtered_out": filtered_out,
        "filter_pct_out": round(100.0 * filtered_out / max(tradeable, 1), 1),
        "pass_pct": round(100.0 * pass_both / max(tradeable, 1), 1),
        "missing_metrics": max(universe_size - with_metrics, 0),
        "freshness": compute_data_freshness(conn),
    }


def _latest_metrics_by_ticker(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT m.*
        FROM ticker_metrics m
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        """
    ).fetchall()
    return {row["ticker"]: row for row in rows}


def build_special_watch_report(
    conn: sqlite3.Connection,
    preset_name: str = "datacenter_us",
) -> dict:
    """Status for every ticker in a thematic preset — Step 3 pass / too quiet / too wild / etc."""
    name = preset_name.lower().strip()
    extras = get_special_watch_extras(conn, name)
    tickers = merge_special_watch_tickers(name, extras)
    active = set(get_active_watchlist(conn))
    metrics = _latest_metrics_by_ticker(conn)

    rows: list[dict] = []
    counts: dict[str, int] = {k: 0 for k in STEP3_STATUS_LABELS}

    for ticker in tickers:
        regime_only = ticker in REGIME_ONLY_TICKERS
        m = metrics.get(ticker)
        if m is None:
            status = classify_step3_status(ticker=ticker, regime_only=regime_only)
            row = {
                "ticker": ticker,
                "step3_status": status,
                "step3_label": STEP3_STATUS_LABELS[status],
                "avg_range_pct": None,
                "adv_dollar": None,
                "adv_dollar_m": None,
                "meets_liquidity": None,
                "near_swing_target": None,
                "in_active_watchlist": ticker in active,
            }
        else:
            avg_range = float(m["avg_range_pct"] or 0)
            adv = float(m["adv_dollar"] or 0)
            meets_liq = bool(m["meets_liquidity_min"])
            near_swing = bool(m["near_swing_target"])
            status = classify_step3_status(
                ticker=ticker,
                meets_liquidity=meets_liq,
                near_swing=near_swing,
                avg_range_pct=avg_range,
                regime_only=regime_only,
            )
            row = {
                "ticker": ticker,
                "step3_status": status,
                "step3_label": STEP3_STATUS_LABELS[status],
                "avg_range_pct": round(avg_range, 2),
                "adv_dollar": round(adv, 0),
                "adv_dollar_m": round(adv / 1_000_000, 1) if adv else 0.0,
                "meets_liquidity": meets_liq,
                "near_swing_target": near_swing,
                "in_active_watchlist": ticker in active,
            }
        counts[status] = counts.get(status, 0) + 1
        rows.append(row)

    with_metrics = sum(1 for r in rows if r["step3_status"] != "missing_metrics")
    return {
        "preset": name,
        "description": PRESETS.get(name, name),
        "ticker_count": len(tickers),
        "preset_ticker_count": len(load_preset_tickers(name)),
        "manual_ticker_count": len(extras),
        "with_metrics": with_metrics,
        "missing_metrics": len(tickers) - with_metrics,
        "step3_pass": counts.get("step3_pass", 0),
        "too_quiet": counts.get("too_quiet", 0),
        "too_wild": counts.get("too_wild", 0),
        "low_liquidity": counts.get("low_liquidity", 0),
        "status_counts": counts,
        "swing_band_pct": {
            "target": SWING_TARGET_PCT,
            "low": swing_band_low(),
            "high": swing_band_high(),
        },
        "tickers": rows,
    }
```


---

<a id="tests-test_account-py"></a>
## `tests/test_account.py`

```python
"""Tests for account summary and sweeps."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import (
    apply_month_end_sweep,
    build_dashboard_summary,
    format_journal_notes,
    get_trading_mode,
    set_trading_mode,
    set_setting,
)
from investment_agent.db import init_db, insert_regime_snapshot
from investment_agent.journal import insert_trade


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def test_apply_sweep_on_gain_month():
    conn, path = _conn()
    try:
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-07-31T10:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=110,
            fee=7,
            executed_at="2026-07-31T11:00:00+00:00",
        )
        conn.commit()
        result = apply_month_end_sweep(conn, "2026-07")
        assert result["ok"] is True
        assert result["total_sweep"] > 0
        conn.commit()
        summary = build_dashboard_summary(conn)
        assert summary.management_jar > 0
        assert summary.tax_jar > 0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_dashboard_summary_regime_and_tax_rate():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-07-31T12:00:00+00:00",
                "spy_change_pct": -0.5,
                "dia_change_pct": -0.3,
                "qqq_change_pct": -0.1,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "All down",
            },
        )
        set_setting(conn, "tax_reserve_rate", "0.30")
        conn.commit()
        summary = build_dashboard_summary(conn)
        assert summary.block_new_longs is True
        assert summary.tax_rate == 0.30
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_trading_mode_defaults_to_paper():
    conn, path = _conn()
    try:
        assert get_trading_mode(conn) == "paper"
        summary = build_dashboard_summary(conn)
        assert summary.trading_mode == "paper"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_set_trading_mode_and_journal_note_tagging():
    conn, path = _conn()
    try:
        assert set_trading_mode(conn, "live") == "live"
        assert format_journal_notes("E*TRADE fill", "live") == "[LIVE] E*TRADE fill"
        assert format_journal_notes("[PAPER] already tagged", "live") == "[PAPER] already tagged"
        assert format_journal_notes(None, "paper") == "[PAPER]"
    finally:
        conn.close()
        path.unlink(missing_ok=True)
```


---

<a id="tests-test_backtest-py"></a>
## `tests/test_backtest.py`

```python
"""Tests for intraday backtest engine."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import (
    _bar_exit_price,
    _regime_blocks,
    _simulate_trading_day,
)


def test_bar_exit_target():
    px, reason = _bar_exit_price(target=101.13, stop=99.5, bar={"open": 100, "high": 102, "low": 99.8})
    assert reason == "target"
    assert px == 101.13


def test_bar_exit_stop_when_both_hit():
    px, reason = _bar_exit_price(target=101.13, stop=99.5, bar={"open": 100, "high": 102, "low": 99})
    assert reason == "stop"
    assert px == 99.5


def test_regime_blocks_when_all_indices_down():
    index_bars = {
        "SPY": [{"open": 100, "close": 99, "high": 100, "low": 98}],
        "DIA": [{"open": 100, "close": 99, "high": 100, "low": 98}],
        "QQQ": [{"open": 100, "close": 99, "high": 100, "low": 98}],
    }
    assert _regime_blocks(index_bars, 0) is True


def test_simulate_day_single_target_trade():
    spy = [
        {"ts": "2026-07-01T09:30:00-04:00", "open": 100, "high": 100, "low": 100, "close": 100},
        {"ts": "2026-07-01T09:35:00-04:00", "open": 100, "high": 102, "low": 99.9, "close": 101.5},
    ]
    aapl = [
        {"ts": "2026-07-01T09:30:00-04:00", "open": 100, "high": 100.5, "low": 99.9, "close": 100},
        {"ts": "2026-07-01T09:35:00-04:00", "open": 100, "high": 102, "low": 99.9, "close": 101.5},
    ]
    index_bars = {"SPY": spy, "DIA": spy, "QQQ": spy}
    trades, cash = _simulate_trading_day(
        date="2026-07-01",
        ordered_tickers=["AAPL"],
        rank_by_ticker={"AAPL": 0.9},
        liquidity_caps={"AAPL": 10_000},
        ticker_bars={"AAPL": aapl},
        index_bars=index_bars,
        cash=10_000,
        buy_fee=7,
        sell_fee=7,
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "target"
    assert cash > 10_000
```


---

<a id="tests-test_cio-py"></a>
## `tests/test_cio.py`

```python
"""Tests for CIO summary (Phase 5)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.cio import build_cio_summary
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db


def test_cio_summary_on_demo_data():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cio.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cio = build_cio_summary(conn)
        assert cio["headline"]
        assert cio["narrative"]
        assert cio["action_items"]
        assert "research" in cio["sub_agents"]
        assert "learning" in cio["sub_agents"]
        assert cio["tradable_cash"] == expected["tradable_cash"] or abs(
            cio["tradable_cash"] - expected["tradable_cash"]
        ) < 0.02
        assert cio["claude_ready"] is False
        assert cio["block_new_longs"] is False
        conn.close()
```


---

<a id="tests-test_close_report-py"></a>
## `tests/test_close_report.py`

```python
"""Tests for Daily Close / Weekly Close reports."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.close_report import (
    generate_daily_close_report,
    generate_weekly_close_report,
    price_at_10_et_from_day_bars,
    save_close_report,
    save_rank_snapshot,
)
from investment_agent.db import init_db, insert_ohlcv_rows, insert_ticker_metrics, upsert_watchlist


def _seed(conn, eval_date: str):
    upsert_watchlist(conn, ["AAPL", "MSFT"])
    for ticker in ("AAPL", "MSFT"):
        insert_ticker_metrics(
            conn,
            {
                "ticker": ticker,
                "computed_at": "2026-08-01T12:00:00+00:00",
                "adv_dollar": 50_000_000,
                "avg_range_pct": 3.0,
                "liquidity_cap": 400_000,
                "last_close": 100.0,
                "last_quote": 100.0,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )

    end = datetime.strptime(eval_date, "%Y-%m-%d")
    rows = []
    for ticker in ("AAPL", "MSFT"):
        for offset in range(10, -1, -1):
            day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
            open_px = 100.0
            high = round(open_px * (1.015 if day == eval_date and ticker == "AAPL" else 1.012), 2)
            low = round(open_px * 0.988, 2)
            rows.append(
                {
                    "ticker": ticker,
                    "date": day,
                    "open": open_px,
                    "high": round(high, 2),
                    "low": round(open_px * 0.995, 2),
                    "close": round(open_px * 1.005, 2),
                    "volume": 10_000_000,
                    "source": "test",
                }
            )
    insert_ohlcv_rows(conn, rows)


def test_price_at_10_et_bar_index():
    bars = [{"open": 100 + i * 0.1, "ts": f"2026-08-07T{9 + i // 12}:{i % 12}:00"} for i in range(10)]
    assert price_at_10_et_from_day_bars(bars) == bars[6]["open"]


def test_daily_close_report_tabs():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "close.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        eval_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        _seed(conn, eval_date)
        conn.commit()

        report = generate_daily_close_report(conn, eval_date, fetch_10_et=False)
        assert report["report_type"] == "daily"
        assert "tabs" in report
        assert "step3_pass" in report["tabs"]
        assert "full_top20" in report["tabs"]
        full = report["tabs"]["full_top20"]["rows"]
        assert len(full) >= 1
        aapl = next(r for r in full if r["ticker"] == "AAPL")
        assert aapl["open_entry"]["net_at_high"] > 0
        assert "journal" in report

        save_close_report(conn, report)
        conn.commit()
        conn.close()


def test_weekly_close_report():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "close.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        eval_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        _seed(conn, eval_date)
        conn.commit()

        report = generate_weekly_close_report(conn, eval_date, fetch_10_et=False)
        assert report["report_type"] == "weekly"
        assert "summary" in report
        assert report["summary"]["days"] >= 1
        conn.close()


def test_rank_snapshot_saved():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "close.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        save_rank_snapshot(conn, "2026-08-07", [{"ticker": "AAPL", "score": 0.9}])
        conn.commit()
        row = conn.execute("SELECT ranked_json FROM rank_snapshots WHERE snapshot_date = '2026-08-07'").fetchone()
        assert row is not None
        conn.close()
```


---

<a id="tests-test_daily_rhythm-py"></a>
## `tests/test_daily_rhythm.py`

```python
"""Tests for daily rhythm status and trading candidates."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.daily_rhythm import get_daily_rhythm_status, ingest_schedule_installed
from investment_agent.db import init_db


def test_get_daily_rhythm_status_has_three_steps():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "rhythm.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        status = get_daily_rhythm_status(conn)
        conn.close()
        assert len(status["steps"]) == 3
        assert status["steps"][0]["id"] == "after_close"
        assert status["steps"][1]["id"] == "pre_market"
        assert status["steps"][2]["id"] == "before_buy"
        assert isinstance(status["schedule_installed"], bool)


def test_ingest_schedule_installed_is_bool():
    assert isinstance(ingest_schedule_installed(), bool)
```


---

<a id="tests-test_dashboard-py"></a>
## `tests/test_dashboard.py`

```python
"""Tests for FastAPI dashboard routes."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app
from investment_agent.db import init_db


def test_dashboard_homepage():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/")
                assert resp.status_code == 200
                assert "AI Investment Agent" in resp.text


def test_api_summary_empty_db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/api/summary")
                assert resp.status_code == 200
                data = resp.json()
                assert data["tradable_cash"] == 10000.0
                assert "goal_pct" in data
```


---

<a id="tests-test_dashboard_integration-py"></a>
## `tests/test_dashboard_integration.py`

```python
"""Full dashboard integration tests with seeded demo data."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app, _require_api_key
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db


class DashboardIntegration:
    """Context manager wrapping patched TestClient with auth bypass for POST routes."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._patches = []

    def __enter__(self) -> TestClient:
        def fake_connect():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

        self._patches = [
            patch("investment_agent.dashboard.app.connect", fake_connect),
            patch("investment_agent.dashboard.app.init_db", lambda: self.db_path),
        ]
        for p in self._patches:
            p.start()
        app.dependency_overrides[_require_api_key] = lambda: None
        return TestClient(app)

    def __exit__(self, *args) -> None:
        app.dependency_overrides.pop(_require_api_key, None)
        for p in self._patches:
            p.stop()


def test_full_dashboard_flow_with_demo_data():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "integration.db"
        seed_demo_db(db_path)
        expected = expected_demo_summary()

        with DashboardIntegration(db_path) as client:
            # Page loads
            home = client.get("/")
            assert home.status_code == 200
            for section_id in (
                "regime-banner", "scenario-panel", "cio-headline", "learning-panel",
            ):
                assert section_id in home.text or section_id.replace("-", "_") in home.text

            # Summary
            summary = client.get("/api/summary").json()
            assert summary["trading_mode"] == "paper"
            assert abs(summary["tradable_cash"] - expected["tradable_cash"]) < 0.02
            assert summary["vix"] == expected["vix"]
            assert summary["regime"]["summary"].startswith("Regime OK")
            assert summary["market_brief"]
            assert "sweep_preview" in summary

            # Queue with live fields
            queue = client.get("/api/queue").json()
            assert len(queue) == expected["queue_count"]
            nvda = next(q for q in queue if q["ticker"] == "NVDA")
            assert nvda["state"] == "in_trade"
            assert nvda["current_price"] is not None
            assert nvda["pnl_pct"] is not None

            # Journal
            journal = client.get("/api/journal").json()
            assert len(journal) == expected["journal_count"]

            # Phase 6 — Scenario visualizer
            scenario = client.get("/api/scenario/visualizer").json()
            assert scenario["goal"] == 5_000_000
            assert len(scenario["actual_timeline"]) >= 3
            assert scenario["scenarios"]["journal_pace"]["months_to_goal"] is not None
            assert "scenario-panel" in home.text or "Scenario Visualizer" in home.text

            # Candidates from metrics
            candidates = client.get("/api/candidates").json()
            assert isinstance(candidates, list)
            assert len(candidates) >= 1

            # Monitor + alerts
            mon = client.post("/api/monitor/run").json()
            assert mon["ok"] is True
            assert mon["new_alerts"] >= 1

            alerts = client.get("/api/alerts").json()
            assert len(alerts) >= 1
            assert any(a["alert_type"] == "TARGET_HIT" for a in alerts)

            # Acknowledge
            alert_id = alerts[0]["id"]
            ack = client.post(f"/api/alerts/{alert_id}/acknowledge").json()
            assert ack["ok"] is True
            remaining = client.get("/api/alerts").json()
            assert all(a["id"] != alert_id for a in remaining)

            # Queue advance
            amd = next(q for q in queue if q["ticker"] == "AMD")
            adv = client.post(f"/api/queue/{amd['id']}/advance").json()
            assert adv["ok"] is True
            assert adv["to_state"] == "approved"

            # Log trade
            trade = client.post(
                "/api/journal",
                json={"ticker": "AMD", "side": "BUY", "shares": 5, "price": 160.0},
            ).json()
            assert trade["ok"] is True
            assert trade["trading_mode"] == "paper"

            journal_after = client.get("/api/journal").json()
            latest = journal_after[0]
            assert latest["notes"].startswith("[PAPER]")

            # Tax rate
            tax = client.put("/api/settings/tax-rate", json={"tax_rate": 0.28}).json()
            assert tax["tax_rate"] == 0.28

            # Sync queue
            sync = client.post("/api/queue/sync").json()
            assert "added" in sync or "message" in sync

            # Static
            assert client.get("/static/style.css").status_code == 200

            # Phase 5 — CIO + Learning
            cio = client.get("/api/cio/summary").json()
            assert cio["headline"]
            assert len(cio["action_items"]) >= 1
            assert cio["sub_agents"]["regime"].startswith("Regime OK")

            learning = client.get("/api/learning/report").json()
            assert learning["active_positions"]
            assert learning["round_trips"]

            gen = client.post("/api/learning/generate").json()
            assert gen["ok"] is True
            assert gen["report"]["highlights"]

            cleared = client.post("/api/journal/clear").json()
            assert cleared["ok"] is True
            assert cleared["removed"] >= 1
            assert client.get("/api/journal").json() == []

            mode = client.put("/api/settings/trading-mode", json={"mode": "live"}).json()
            assert mode["mode"] == "live"


def test_verify_dashboard_script_matches_integration():
    """Ensure verify_dashboard.py checks align with integration expectations."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "verify.db"
        seed_demo_db(db_path)

        import importlib.util

        script = ROOT / "scripts" / "verify_dashboard.py"
        spec = importlib.util.spec_from_file_location("verify_dashboard", script)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        report = mod.verify(db_path)
        assert report["failed"] == 0, report["results"]
```


---

<a id="tests-test_data_freshness-py"></a>
## `tests/test_data_freshness.py`

```python
"""Tests for data freshness reporting."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.db import init_db, insert_quote, insert_ticker_metrics, upsert_watchlist
from investment_agent.watchlist import compute_data_freshness


def test_compute_data_freshness_reports_ages():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fresh.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        upsert_watchlist(conn, ["AAPL", "MSFT"])
        insert_quote(
            conn,
            {
                "ticker": "AAPL",
                "captured_at": "2026-08-10T10:00:00+00:00",
                "price": 100.0,
                "open": 99.0,
                "high": 101.0,
                "low": 98.0,
                "prev_close": 99.5,
            },
        )
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
                "computed_at": "2026-08-10T10:00:00+00:00",
                "adv_dollar": 1e9,
                "avg_range_pct": 3.0,
                "liquidity_cap": 1e6,
                "last_close": 100,
                "last_quote": 100,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        conn.commit()
        fresh = compute_data_freshness(conn)
        conn.close()
        assert fresh["tickers_with_quotes"] == 1
        assert fresh["tickers_with_metrics"] == 1
        assert fresh["quotes_max_age_hours"] is not None
        assert fresh["quotes_max_age_hours"] > 0
```


---

<a id="tests-test_db-py"></a>
## `tests/test_db.py`

```python
"""Tests for database init."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, upsert_watchlist


def test_init_db_creates_tables():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.db"
        init_db(path)
        conn = sqlite3.connect(path)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        conn.close()
        assert "watchlist" in tables
        assert "ohlcv_daily" in tables
        assert "ticker_metrics" in tables
        assert "regime_snapshots" in tables
        assert "queue_items" in tables
        assert "trade_journal" in tables
        assert "price_alerts" in tables
        assert "learning_reports" in tables


def test_upsert_watchlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.db"
        init_db(path)
        conn = sqlite3.connect(path)
        upsert_watchlist(conn, ["SPY", "AAPL"])
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
        conn.close()
        assert count == 2
```


---

<a id="tests-test_db_maintenance-py"></a>
## `tests/test_db_maintenance.py`

```python
"""Tests for database maintenance helpers."""

from __future__ import annotations

from investment_agent.db import connect, init_db
from investment_agent.db_maintenance import (
    acquire_ingest_lock,
    ingest_lock_active,
    release_ingest_lock,
    repair_database,
)


def test_ingest_lock(tmp_path):
    lock = tmp_path / "ingest.lock"
    import investment_agent.db_maintenance as dm

    dm.INGEST_LOCK_PATH = lock
    acquire_ingest_lock(detail="test")
    assert ingest_lock_active()
    release_ingest_lock()
    assert not ingest_lock_active()


def test_repair_database(tmp_path):
    path = init_db(tmp_path / "t.db")
    result = repair_database(path)
    assert result["ok"]
    assert result["integrity"] == "ok"
```


---

<a id="tests-test_demo_seed-py"></a>
## `tests/test_demo_seed.py`

```python
"""Tests for demo seed data."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import build_dashboard_summary
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.monitor import run_monitor_cycle


def test_seed_demo_db_populates_all_sections():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo.db"
        seed_demo_db(path)
        expected = expected_demo_summary()

        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        assert conn.execute("SELECT COUNT(*) FROM queue_items").fetchone()[0] == expected["queue_count"]
        assert conn.execute("SELECT COUNT(*) FROM trade_journal").fetchone()[0] == expected["journal_count"]
        assert conn.execute("SELECT value FROM macro_snapshots WHERE series_id='VIXCLS'").fetchone()[0] == expected["vix"]

        summary = build_dashboard_summary(conn)
        assert abs(summary.tradable_cash - expected["tradable_cash"]) < 0.02
        assert abs(summary.monthly_realized_net - expected["monthly_realized_net"]) < 0.02
        assert summary.block_new_longs is False

        mon = run_monitor_cycle(conn)
        assert mon["new_alerts"] >= 1

        conn.close()


def test_seed_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo.db"
        seed_demo_db(path)
        seed_demo_db(path)
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM queue_items").fetchone()[0]
        conn.close()
        assert count == expected_demo_summary()["queue_count"]
```


---

<a id="tests-test_dollar_backtest-py"></a>
## `tests/test_dollar_backtest.py`

```python
"""Tests for daily dollar backtest."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import run_dollar_daily_backtest
from investment_agent.db import init_db, insert_ohlcv_rows, insert_ticker_metrics, upsert_watchlist


def _seed(conn, eval_date: str):
    upsert_watchlist(conn, ["AAPL"])
    insert_ticker_metrics(
        conn,
        {
            "ticker": "AAPL",
            "computed_at": "2026-08-01T12:00:00+00:00",
            "adv_dollar": 50_000_000,
            "avg_range_pct": 3.0,
            "liquidity_cap": 400_000,
            "last_close": 100.0,
            "last_quote": 100.0,
            "meets_liquidity_min": True,
            "near_swing_target": True,
        },
    )
    end = datetime.strptime(eval_date, "%Y-%m-%d")
    rows = []
    for offset in range(10, 0, -1):
        day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
        close = 100.0
        open_px = 100.0
        high = 102.5 if day == eval_date else 101.2
        low = 99.2
        rows.append(
            {
                "ticker": "AAPL",
                "date": day,
                "open": open_px,
                "high": high,
                "low": low,
                "close": close,
                "volume": 10_000_000,
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def test_dollar_daily_backtest_runs():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bt.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        eval_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _seed(conn, eval_date)
        conn.commit()
        result = run_dollar_daily_backtest(conn, lookback_days=14, starting_capital=10_000)
        conn.close()
        assert result["total_trades"] >= 0
        assert "dollar_hit_rate_pct" in result
        assert result["assumptions"]
```


---

<a id="tests-test_dollar_rank_gate-py"></a>
## `tests/test_dollar_rank_gate.py`

```python
"""Tests for dollar-goal rank gate and tightened scoring weights."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.dollar_target import (
    MIN_RANK_AVG_NET_RATIO,
    MIN_RANK_DOLLAR_HIT_RATE_PCT,
    passes_dollar_rank_gate,
)
from investment_agent.period_screener import RANK_WEIGHTS, _criteria_likelihood_score


def test_rank_weights_sum_to_one():
    assert abs(sum(RANK_WEIGHTS.values()) - 1.0) < 1e-9


def test_passes_dollar_rank_gate_requires_hit_rate_and_avg_net():
    assert passes_dollar_rank_gate(
        dollar_hit_rate_pct=50.0,
        avg_net_at_high=140.0,
        net_target=150.0,
        days_screened=5,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=30.0,
        avg_net_at_high=160.0,
        net_target=150.0,
        days_screened=5,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=50.0,
        avg_net_at_high=120.0,
        net_target=150.0,
        days_screened=5,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=50.0,
        avg_net_at_high=200.0,
        net_target=200.0,
        days_screened=1,
    )


def test_scoring_prefers_strong_dollar_history():
    strong = _criteria_likelihood_score(
        live_pass=True,
        hit_rate_pct=60.0,
        dollar_hit_rate_pct=70.0,
        avg_net_at_high=170.0,
        net_target=150.0,
        days_screened=10,
        avg_range_pct=3.0,
        adv_dollar=10_000_000,
        meets_liquidity=True,
        near_swing=True,
        period_days=14,
    )
    weak = _criteria_likelihood_score(
        live_pass=True,
        hit_rate_pct=80.0,
        dollar_hit_rate_pct=20.0,
        avg_net_at_high=80.0,
        net_target=150.0,
        days_screened=10,
        avg_range_pct=3.0,
        adv_dollar=10_000_000,
        meets_liquidity=True,
        near_swing=True,
        period_days=14,
    )
    assert strong["score"] > weak["score"]
    assert strong["dollar_avg_net_component"] > weak["dollar_avg_net_component"]


def test_net_target_scales_gate_threshold():
    net_target = 200.0
    min_avg = net_target * MIN_RANK_AVG_NET_RATIO
    assert passes_dollar_rank_gate(
        dollar_hit_rate_pct=MIN_RANK_DOLLAR_HIT_RATE_PCT,
        avg_net_at_high=min_avg,
        net_target=net_target,
        days_screened=3,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=MIN_RANK_DOLLAR_HIT_RATE_PCT,
        avg_net_at_high=min_avg - 1,
        net_target=net_target,
        days_screened=3,
    )
```


---

<a id="tests-test_dollar_target-py"></a>
## `tests/test_dollar_target.py`

```python
"""Tests for dollar-target prediction and historical simulation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.dollar_target import (
    DollarDayBar,
    assess_dollar_reachability,
    evaluate_dollar_history,
    estimate_net_at_typical_high,
    net_at_high_from_open,
    simulate_dollar_outcome,
)
from investment_agent.finance import ORIGINAL_BASIS


def test_adp_aug7_not_reachable_from_open():
    """ADP 2026-08-07 — high ~+0.85% could not deliver $150 net from open."""
    open_px = 272.95
    high = 275.27
    low = 271.50
    deploy = ORIGINAL_BASIS
    outcome = simulate_dollar_outcome(open_px, high, low, deploy_dollar=deploy, net_target=150.0)
    assert outcome == "neither"
    net_high = net_at_high_from_open(open_px, high, deploy_dollar=deploy)
    assert net_high < 150.0
    assert net_high == 69.52

    pred = assess_dollar_reachability(
        entry_price=open_px,
        deploy_dollar=deploy,
        net_target=150.0,
        avg_range_pct=2.4,
    )
    assert pred["verdict"] == "NOT_REACHABLE"
    assert pred["expected_net_at_typical_high"] is not None
    assert pred["expected_net_at_typical_high"] < 150.0


def test_dollar_history_hit_rate():
    """Three days: one hits $150 from open, one stops, one neither."""
    bars = [
        DollarDayBar(open=100.0, high=103.0, low=99.5),   # likely target at ~101.5+
        DollarDayBar(open=100.0, high=100.5, low=99.0),   # stop
        DollarDayBar(open=50.0, high=50.4, low=49.9),     # neither on $10K
    ]
    stats = evaluate_dollar_history(bars, deploy_dollar=ORIGINAL_BASIS, net_target=150.0)
    assert stats.days_evaluated == 3
    assert stats.dollar_targets >= 1
    assert stats.dollar_hit_rate_pct >= 0


def test_estimate_net_at_typical_high():
    net = estimate_net_at_typical_high(
        100.0,
        avg_range_pct=3.0,
        deploy_dollar=ORIGINAL_BASIS,
    )
    assert net > 0
    assert net == 134.5


def test_high_enough_reaches_target():
    open_px = 100.0
    high = 102.5
    low = 99.5
    outcome = simulate_dollar_outcome(
        open_px, high, low, deploy_dollar=ORIGINAL_BASIS, net_target=150.0,
    )
    assert outcome == "target"
```


---

<a id="tests-test_finance-py"></a>
## `tests/test_finance.py`

```python
"""Tests for v3 financial model."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import (
    GOAL_ACCOUNT_VALUE,
    compute_month_end_sweep,
    goal_progress_pct,
    round_trip_fees,
    tradable_after_sweep,
)


def test_round_trip_fees():
    assert round_trip_fees() == 14.0


def test_goal_progress_pct():
    assert goal_progress_pct(10_700) == (10_700 / GOAL_ACCOUNT_VALUE) * 100


def test_sweep_zero_on_loss_month():
    sweep = compute_month_end_sweep(-500.0)
    assert not sweep.applies
    assert sweep.total_sweep == 0.0


def test_sweep_on_gain_month():
    sweep = compute_month_end_sweep(1000.0)
    assert sweep.management_sweep == 100.0
    assert sweep.tax_sweep == 250.0
    assert sweep.total_sweep == 350.0


def test_tradable_after_sweep():
    sweep = compute_month_end_sweep(1000.0)
    assert tradable_after_sweep(11_000.0, sweep) == 10_650.0


def test_editable_tax_rate():
    sweep = compute_month_end_sweep(1000.0, tax_rate=0.30)
    assert sweep.tax_sweep == 300.0
```


---

<a id="tests-test_historical-py"></a>
## `tests/test_historical.py`

```python
"""Tests for historical analysis and prior-day evaluation."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows, upsert_watchlist
from investment_agent.historical import (
    build_historical_summary,
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    open_based_range_pct,
    simulate_intraday_outcome,
)
from investment_agent.learning import generate_learning_report


def _seed_minimal_history(path: Path) -> tuple[str, str]:
    end = datetime.now(timezone.utc)
    eval_date = (end - timedelta(days=1)).strftime("%Y-%m-%d")
    history_start = (end - timedelta(days=10)).strftime("%Y-%m-%d")

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row
        upsert_watchlist(conn, ["AAPL", "SPY"])

        rows = []
        for offset in range(10, 0, -1):
            day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
            close = 100.0 + offset * 0.1
            if day == eval_date:
                open_px = close
                high = open_px * 1.012
                low = open_px * 0.996
            else:
                open_px = close * 0.998
                high = open_px * 1.015
                low = open_px * 0.985
            rows.append(
                {
                    "ticker": "AAPL",
                    "date": day,
                    "open": round(open_px, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": 10_000_000,
                    "source": "test",
                }
            )
        insert_ohlcv_rows(conn, rows)
        conn.commit()

    return eval_date, history_start


def test_open_based_range_and_simulation():
    assert open_based_range_pct(100, 103, 97) == 6.0
    assert simulate_intraday_outcome(100, 102, 99) == "target"
    assert simulate_intraday_outcome(100, 101, 99.2) == "stop"
    assert simulate_intraday_outcome(100, 100.5, 99.8) == "neither"


def test_evaluate_trading_day_finds_screened_matches():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hist.db"
        init_db(path)
        eval_date, _ = _seed_minimal_history(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        result = evaluate_trading_day(conn, eval_date)
        conn.close()
        assert result["tickers_evaluated"] == 1
        assert result["summary"]["screened_count"] >= 1
        match = result["screened_matches"][0]
        assert match["ticker"] == "AAPL"
        assert match["would_screen"] is True


def test_evaluate_prior_day_and_period():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hist.db"
        init_db(path)
        eval_date, history_start = _seed_minimal_history(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        prior = evaluate_prior_day(conn, reference_date=(datetime.strptime(eval_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"))
        assert prior is not None
        assert prior["eval_date"] == eval_date
        period = evaluate_period(conn, history_start, eval_date)
        assert period["days_evaluated"] >= 1
        summary = build_historical_summary(conn)
        assert summary["has_data"] is True
        conn.close()


def test_learning_report_includes_historical_sections():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hist.db"
        init_db(path)
        eval_date, _ = _seed_minimal_history(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        report = generate_learning_report(conn, report_date=eval_date)
        conn.close()
        assert "prior_day_evaluation" in report
        assert "continual_learning" in report
        assert "today_journal" in report
        assert report["continual_learning"]["lookback_days"] == 30
```


---

<a id="tests-test_ingest-py"></a>
## `tests/test_ingest.py`

```python
"""Tests for ingest orchestration and incremental refresh logic."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import init_db, insert_quote, insert_ticker_metrics
from investment_agent.ingest import (
    _needs_bars_refresh,
    _needs_quote_refresh,
    run_ingest,
)
from investment_agent.watchlist import load_preset_into_watchlist, load_preset_tickers


def _recent_iso(hours_ago: float = 1.0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return dt.replace(microsecond=0).isoformat()


def test_load_sp500_preset_has_many_tickers():
    tickers = load_preset_tickers("sp500")
    assert len(tickers) >= 500
    assert "AAPL" in tickers
    assert "SPY" in tickers


def test_load_sp500_preset_into_watchlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sp500.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        result = load_preset_into_watchlist(conn, "sp500")
        conn.commit()
        assert result["tickers_loaded"] >= 500
        count = conn.execute("SELECT COUNT(*) AS c FROM watchlist WHERE active = 1").fetchone()["c"]
        assert count >= 500
        conn.close()


def test_needs_quote_refresh_skips_fresh_data():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "q.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        insert_quote(
            conn,
            {
                "ticker": "AAPL",
                "captured_at": _recent_iso(1.0),
                "price": 100.0,
                "open": 99.0,
                "high": 101.0,
                "low": 98.0,
                "prev_close": 99.5,
            },
        )
        conn.commit()
        assert _needs_quote_refresh(conn, "AAPL", stale_hours=20.0) is False
        assert _needs_quote_refresh(conn, "MSFT", stale_hours=20.0) is True
        conn.close()


def test_needs_bars_refresh_skips_fresh_metrics():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "b.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
                "computed_at": _recent_iso(2.0),
                "adv_dollar": 50_000_000,
                "avg_range_pct": 3.0,
                "liquidity_cap": 400_000,
                "last_close": 100,
                "last_quote": 100,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        conn.commit()
        assert _needs_bars_refresh(conn, "AAPL", stale_hours=20.0) is False
        assert _needs_bars_refresh(conn, "NVDA", stale_hours=20.0) is True
        conn.close()


def test_run_ingest_incremental_skips_fresh_symbols():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "inc.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        now = _recent_iso(1.0)
        for ticker in ("AAPL", "MSFT", "NVDA"):
            insert_quote(
                conn,
                {
                    "ticker": ticker,
                    "captured_at": now,
                    "price": 100.0,
                    "open": 99.0,
                    "high": 101.0,
                    "low": 98.0,
                    "prev_close": 99.5,
                },
            )
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now,
                    "adv_dollar": 50_000_000,
                    "avg_range_pct": 3.0,
                    "liquidity_cap": 400_000,
                    "last_close": 100,
                    "last_quote": 100,
                    "meets_liquidity_min": True,
                    "near_swing_target": True,
                },
            )
        conn.commit()
        conn.close()

        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="test-fred",
            finnhub_api_key="test-finnhub",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        mock_fh = MagicMock()
        mock_fh.get_quote.return_value = {"c": 100, "o": 99, "h": 101, "l": 98, "pc": 99}

        with (
            patch("investment_agent.ingest.fetch_vix", return_value=("2026-01-01", 15.0)),
            patch("investment_agent.ingest.FinnhubClient", return_value=mock_fh),
            patch("investment_agent.ingest.get_daily_bars", return_value=[]),
        ):
            summary = run_ingest(
                settings,
                db_path=path,
                incremental=True,
                stale_hours=20.0,
            )

        assert summary["incremental"] is True
        assert summary["quotes_skipped"] >= 3
        assert summary["bars_skipped"] >= 3
        assert mock_fh.get_quote.call_count < len(summary["tickers"])


def test_run_ingest_after_close_uses_shorter_quote_stale_window():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ac.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        now = _recent_iso(3.0)  # 3 hours ago — fresh for 20h, stale for 2h quotes
        for ticker in ("AAPL",):
            insert_quote(
                conn,
                {
                    "ticker": ticker,
                    "captured_at": now,
                    "price": 100.0,
                    "open": 99.0,
                    "high": 101.0,
                    "low": 98.0,
                    "prev_close": 99.5,
                },
            )
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now,
                    "adv_dollar": 50_000_000,
                    "avg_range_pct": 3.0,
                    "liquidity_cap": 400_000,
                    "last_close": 100,
                    "last_quote": 100,
                    "meets_liquidity_min": True,
                    "near_swing_target": True,
                },
            )
        conn.commit()
        conn.close()

        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="test-fred",
            finnhub_api_key="test-finnhub",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        mock_fh = MagicMock()
        mock_fh.get_quote.return_value = {"c": 100, "o": 99, "h": 101, "l": 98, "pc": 99}

        with (
            patch("investment_agent.ingest.fetch_vix", return_value=("2026-01-01", 15.0)),
            patch("investment_agent.ingest.FinnhubClient", return_value=mock_fh),
            patch("investment_agent.ingest.get_daily_bars", return_value=[]),
        ):
            summary = run_ingest(
                settings,
                db_path=path,
                incremental=True,
                stale_hours=20.0,
                quote_stale_hours=2.0,
                bar_stale_hours=12.0,
            )

        assert summary["quote_stale_hours"] == 2.0
        assert summary["quotes_refreshed"] >= 1
        assert summary["bars_skipped"] >= 1
```


---

<a id="tests-test_journal-py"></a>
## `tests/test_journal.py`

```python
"""Tests for trade journal and P&L."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.journal import (
    build_executed_at_pt,
    clear_all_trades,
    compute_monthly_realized_net,
    insert_trade,
    journal_cash_balance,
    list_trades,
    resolve_executed_at,
)


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    return sqlite3.connect(path), path


def test_journal_cash_balance_after_round_trip():
    conn, path = _conn()
    try:
        conn.row_factory = sqlite3.Row
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-07-31T14:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=101.13,
            fee=7,
            executed_at="2026-07-31T15:00:00+00:00",
        )
        conn.commit()
        cash = journal_cash_balance(conn)
        # Buy 1007, sell proceeds 1004.3 → net cash −2.7 vs basis
        assert abs(cash - (ORIGINAL_BASIS - 2.7)) < 0.01
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_monthly_realized_net_includes_fees():
    conn, path = _conn()
    try:
        conn.row_factory = sqlite3.Row
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-07-31T14:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=101.13,
            fee=7,
            executed_at="2026-07-31T15:00:00+00:00",
        )
        conn.commit()
        net = compute_monthly_realized_net(conn, "2026-07")
        # Gross +11.3, fees 14 → net −2.7
        assert abs(net - (-2.7)) < 0.01
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_clear_all_trades_resets_cash_to_basis():
    conn, path = _conn()
    try:
        conn.row_factory = sqlite3.Row
        insert_trade(conn, ticker="AAPL", side="BUY", shares=10, price=100, fee=7)
        insert_trade(conn, ticker="AAPL", side="SELL", shares=10, price=110, fee=7)
        conn.commit()
        assert journal_cash_balance(conn) != ORIGINAL_BASIS
        removed = clear_all_trades(conn)
        conn.commit()
        assert removed == 2
        assert list_trades(conn) == []
        assert journal_cash_balance(conn) == ORIGINAL_BASIS
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_executed_at_pt_combines_date_and_time():
    iso = build_executed_at_pt("2026-08-03", "10:15")
    assert iso.startswith("2026-08-03T10:15:00")
    assert "-07:00" in iso or "-08:00" in iso


def test_resolve_executed_at_prefers_audit_fields():
    resolved = resolve_executed_at(
        executed_date="2026-08-03",
        executed_time_pt="14:30",
    )
    assert resolved is not None
    assert "2026-08-03T14:30:00" in resolved
```


---

<a id="tests-test_learning-py"></a>
## `tests/test_learning.py`

```python
"""Tests for learning report generation."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.demo_seed import seed_demo_db
from investment_agent.journal import get_completed_round_trips, get_open_positions
from investment_agent.learning import generate_learning_report, save_learning_report


def test_fifo_open_and_round_trips_on_demo():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "learn.db"
        seed_demo_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        open_pos = get_open_positions(conn)
        trips = get_completed_round_trips(conn)
        assert len(open_pos) == 1
        assert open_pos[0]["ticker"] == "NVDA"
        assert len(trips) == 3
        assert trips[0]["ticker"] in ("AAPL", "AMD", "MSFT")
        assert trips[0]["same_day"] is True
        conn.close()


def test_learning_report_covers_sections():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "learn.db"
        seed_demo_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        report = generate_learning_report(conn)
        assert report["active_positions"]
        assert report["round_trips"]
        assert report["highlights"]
        assert report["claude_ready"] is False
        assert any("NVDA" in h or "round trip" in h.lower() for h in report["highlights"])
        rid = save_learning_report(conn, report)
        conn.commit()
        assert rid >= 1
        conn.close()
```


---

<a id="tests-test_liquidity-py"></a>
## `tests/test_liquidity.py`

```python
"""Tests for liquidity metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.liquidity import DailyBar, compute_liquidity_metrics, daily_range_pct


def _bars(range_pct: float, days: int = 20) -> list[DailyBar]:
    close = 100.0
    half = (range_pct / 100.0) * close / 2.0
    return [
        DailyBar(high=close + half, low=close - half, close=close, volume=500_000)
        for _ in range(days)
    ]


def test_daily_range_pct():
    bar = DailyBar(high=103.0, low=97.0, close=100.0, volume=1)
    assert abs(daily_range_pct(bar) - 6.0) < 0.01


def test_near_swing_target_at_three_percent():
    metrics = compute_liquidity_metrics(_bars(3.0), tradable_cash=10_000)
    assert metrics.near_swing_target is True
    assert metrics.avg_range_pct == 3.0


def test_liquidity_cap_respects_tradable_cash():
    metrics = compute_liquidity_metrics(_bars(3.0), tradable_cash=5_000)
    assert metrics.liquidity_cap <= 5_000


def test_meets_liquidity_min():
    # 500k shares * $100 = $50M ADV
    metrics = compute_liquidity_metrics(_bars(3.0), tradable_cash=10_000)
    assert metrics.meets_liquidity_min is True
```


---

<a id="tests-test_monitor-py"></a>
## `tests/test_monitor.py`

```python
"""Tests for intraday monitor (Phase 4)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_quote
from investment_agent.monitor import (
    evaluate_queue_item,
    pnl_pct,
    run_monitor_cycle,
    target_stop_prices,
)
from investment_agent.strategy import STOP_PCT, TARGET_PCT


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _queue_row(conn, ticker: str, state: str, entry: float, qid: int = 1):
    target, stop = target_stop_prices(entry)
    conn.execute(
        """
        INSERT INTO queue_items
          (id, ticker, state, entry_price, target_price, stop_price, suggested_size)
        VALUES (?, ?, ?, ?, ?, ?, 10000)
        """,
        (qid, ticker, state, entry, target, stop),
    )
    conn.commit()
    return conn.execute(
        "SELECT id, ticker, state, entry_price, target_price, stop_price FROM queue_items WHERE id = ?",
        (qid,),
    ).fetchone()


def test_target_stop_prices():
    entry = 100.0
    target, stop = target_stop_prices(entry)
    assert abs(target - entry * (1 + TARGET_PCT / 100)) < 0.01
    assert abs(stop - entry * (1 - STOP_PCT / 100)) < 0.01


def test_pnl_pct():
    assert abs(pnl_pct(100, 101.5) - 1.5) < 0.01


def test_target_hit_creates_alert():
    conn, path = _conn()
    try:
        entry = 100.0
        target, stop = target_stop_prices(entry)
        row = _queue_row(conn, "NVDA", "in_trade", entry)
        quotes = {"NVDA": target + 0.10}
        ev = evaluate_queue_item(conn, row, quotes, eod=False)
        assert ev is not None
        assert ev.alert_type == "TARGET_HIT"

        result = run_monitor_cycle(conn, quotes)
        assert result["new_alerts"] == 1
        alert = conn.execute("SELECT alert_type, ticker FROM price_alerts").fetchone()
        assert alert["alert_type"] == "TARGET_HIT"
        assert alert["ticker"] == "NVDA"

        # Idempotent same day
        result2 = run_monitor_cycle(conn, quotes)
        assert result2["new_alerts"] == 0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_stop_hit_creates_alert():
    conn, path = _conn()
    try:
        entry = 500.0
        _, stop = target_stop_prices(entry)
        row = _queue_row(conn, "META", "in_trade", entry)
        quotes = {"META": stop - 0.05}
        ev = evaluate_queue_item(conn, row, quotes, eod=False)
        assert ev is not None
        assert ev.alert_type == "STOP_HIT"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_eod_flatten_alert():
    conn, path = _conn()
    try:
        row = _queue_row(conn, "MSFT", "in_trade", 420.0)
        quotes = {"MSFT": 421.0}
        ev = evaluate_queue_item(conn, row, quotes, eod=True)
        assert ev is not None
        assert ev.alert_type == "EOD_FLATTEN"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_missing_quote_skipped():
    conn, path = _conn()
    try:
        _queue_row(conn, "AMD", "armed", 160.0)
        result = run_monitor_cycle(conn, {})
        assert "AMD" in result["missing_quotes"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)
```


---

<a id="tests-test_phase7-py"></a>
## `tests/test_phase7.py`

```python
"""Tests for Phase 7 watchlist and period screener."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows, insert_ticker_metrics
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.period_screener import (
    RANK_WEIGHTS,
    _criteria_likelihood_score,
    build_ranked_candidates,
    date_range_for_period,
    run_period_screener,
    save_screener_run,
)
from investment_agent.watchlist import (
    compute_universe_stats,
    load_preset_into_watchlist,
    load_preset_tickers,
)


def test_load_sp100_preset_has_many_tickers():
    tickers = load_preset_tickers("sp100")
    assert len(tickers) >= 90
    assert "AAPL" in tickers
    assert "SPY" in tickers


def test_load_preset_into_watchlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        result = load_preset_into_watchlist(conn, "starter10")
        conn.commit()
        assert result["tickers_loaded"] == 10
        count = conn.execute("SELECT COUNT(*) AS c FROM watchlist WHERE active = 1").fetchone()["c"]
        assert count == 10
        conn.close()


def test_period_screener_on_seeded_history():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "NVDA", "AMD", "META", "SPY", "DIA", "QQQ"], end=now)
        conn.commit()

        start, end = date_range_for_period(14, end_date=(now.replace(day=max(now.day - 1, 1))).strftime("%Y-%m-%d"), conn=conn)
        result = run_period_screener(
            conn,
            start_date=start,
            end_date=end,
            min_days_screened=1,
            requested_trading_days=14,
        )
        assert "candidates" in result
        assert result["days_evaluated"] >= 1

        run_id = save_screener_run(conn, result)
        conn.commit()
        assert run_id >= 1
        conn.close()


def test_criteria_likelihood_score_prefers_live_and_swing():
    high = _criteria_likelihood_score(
        live_pass=True,
        hit_rate_pct=80.0,
        dollar_hit_rate_pct=65.0,
        avg_net_at_high=160.0,
        net_target=150.0,
        days_screened=10,
        avg_range_pct=3.0,
        adv_dollar=10_000_000,
        meets_liquidity=True,
        near_swing=True,
        period_days=14,
    )
    low = _criteria_likelihood_score(
        live_pass=False,
        hit_rate_pct=20.0,
        dollar_hit_rate_pct=10.0,
        avg_net_at_high=50.0,
        net_target=150.0,
        days_screened=2,
        avg_range_pct=1.5,
        adv_dollar=500_000,
        meets_liquidity=False,
        near_swing=False,
        period_days=14,
    )
    assert high["score"] > low["score"]
    assert high["swing_proximity"] == 1.0
    assert low["liquidity_score"] == 0.0


def test_build_ranked_candidates_includes_enriched_fields():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
                "computed_at": now,
                "adv_dollar": 50_000_000,
                "avg_range_pct": 3.0,
                "liquidity_cap": 400_000,
                "last_close": 100,
                "last_quote": 100,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        now_dt = datetime.now(timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "NVDA"], end=now_dt)
        conn.commit()

        result = build_ranked_candidates(conn, period_days=14, require_dollar_rank_gate=False)
        assert "ranked" in result
        assert result["rank_weights"] == RANK_WEIGHTS
        assert len(result["ranked"]) >= 1
        top = result["ranked"][0]
        for field in (
            "score",
            "swing_proximity",
            "liquidity_score",
            "consistency_score",
            "adv_dollar_m",
            "meets_liquidity",
            "near_swing_target",
        ):
            assert field in top
        scores = [r["score"] for r in result["ranked"]]
        assert scores == sorted(scores, reverse=True)
        conn.close()


def test_universe_stats_with_metrics():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for ticker, swing in [("AAPL", 3.1), ("MSFT", 2.9), ("SPY", 1.2)]:
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now,
                    "adv_dollar": 50_000_000,
                    "avg_range_pct": swing,
                    "liquidity_cap": 400_000,
                    "last_close": 100,
                    "last_quote": 100,
                    "meets_liquidity_min": True,
                    "near_swing_target": 2.0 <= swing <= 4.0,
                },
            )
        conn.commit()
        stats = compute_universe_stats(conn)
        assert stats["universe_size"] == 10
        assert stats["pass_both_step3"] >= 1
        conn.close()
```


---

<a id="tests-test_pullback_entry-py"></a>
## `tests/test_pullback_entry.py`

```python
"""Tests for pullback limit entry planning."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.pullback_entry import (
    compute_pullback_trade_plan,
    limit_buy_price,
    limit_fill_missed,
    simulate_pullback_dollar_outcome,
)
from datetime import time


def test_limit_buy_below_open():
    px = limit_buy_price(100.0, avg_range_pct=3.0)
    assert px < 100.0
    assert px == 98.95  # 100 * (1 - 1.05/100) with 35% of 3% = 1.05%


def test_pullback_plan_needs_smaller_upside_move():
    from investment_agent.trading_day import compute_trade_plan

    session_open = 100.0
    plan = compute_pullback_trade_plan(
        session_open=session_open,
        avg_range_pct=3.0,
        deploy_dollar=10_000,
        net_target=150.0,
    )
    at_open = compute_trade_plan(entry_price=session_open, deploy_dollar=10_000, net_target=150.0)
    move_from_open_pct = ((plan["limit_sell_price"] - session_open) / session_open) * 100
    assert plan["limit_buy_price"] < session_open
    assert plan["limit_sell_price"] < at_open["target_price"]
    assert move_from_open_pct < at_open["target_pct"]
    assert plan["estimated_net_at_typical_high"] > at_open["net_at_target"]
    assert plan["net_at_target"] >= 149.0


def test_simulate_pullback_no_fill_when_low_stays_above_limit():
    outcome = simulate_pullback_dollar_outcome(
        100.0,
        high=101.0,
        low=99.5,
        deploy_dollar=10_000,
        avg_range_pct=3.0,
        net_target=150.0,
    )
    assert outcome == "no_fill"


def test_simulate_pullback_target_when_dip_then_rally():
    limit = limit_buy_price(100.0, 3.0)
    outcome = simulate_pullback_dollar_outcome(
        100.0,
        high=100.0 + (100.0 - limit) + 2.0,
        low=limit - 0.01,
        deploy_dollar=10_000,
        avg_range_pct=3.0,
        net_target=150.0,
    )
    assert outcome == "target"


def test_limit_fill_missed_after_deadline():
    limit = limit_buy_price(100.0, 3.0)
    assert limit_fill_missed(
        limit_buy_price=limit,
        session_low=limit + 0.05,
        as_of_time=time(12, 0),
    )
    assert not limit_fill_missed(
        limit_buy_price=limit,
        session_low=limit - 0.01,
        as_of_time=time(12, 0),
    )
```


---

<a id="tests-test_regime-py"></a>
## `tests/test_regime.py`

```python
"""Tests for regime gate logic."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.regime import (
    IndexQuote,
    evaluate_regime,
    index_quote_from_finnhub,
    intraday_change_pct,
)


def test_intraday_change_vs_open():
    assert abs(intraday_change_pct(101.0, open_price=100.0) - 1.0) < 0.001


def test_intraday_change_falls_back_to_prev_close():
    assert abs(intraday_change_pct(99.0, prev_close=100.0) - (-1.0)) < 0.001


def test_all_indices_down_blocks_new_longs():
    quotes = {
        "SPY": IndexQuote("SPY", 100, 101, 100, -0.99),
        "DIA": IndexQuote("DIA", 100, 101, 100, -0.50),
        "QQQ": IndexQuote("QQQ", 100, 101, 100, -0.10),
    }
    snap = evaluate_regime(quotes, "2026-07-31T12:00:00+00:00")
    assert snap.all_indices_down is True
    assert snap.block_new_longs is True


def test_mixed_indices_allows_longs():
    quotes = {
        "SPY": IndexQuote("SPY", 101, 100, 100, 1.0),
        "DIA": IndexQuote("DIA", 99, 100, 100, -1.0),
        "QQQ": IndexQuote("QQQ", 99, 100, 100, -1.0),
    }
    snap = evaluate_regime(quotes, "2026-07-31T12:00:00+00:00")
    assert snap.block_new_longs is False


def test_index_quote_from_finnhub():
    q = index_quote_from_finnhub("SPY", {"c": 100.0, "o": 99.0, "pc": 98.0})
    assert q.symbol == "SPY"
    assert abs(q.intraday_change_pct - ((100 - 99) / 99 * 100)) < 0.01
```


---

<a id="tests-test_scenario-py"></a>
## `tests/test_scenario.py`

```python
"""Tests for $5M scenario visualizer (Phase 6)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.scenario import build_scenario_visualizer, replay_actual_timeline


def test_replay_timeline_includes_start_and_months():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sc.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        timeline = replay_actual_timeline(conn)
        assert timeline[0].month_key == "start"
        assert timeline[0].tradable_balance == ORIGINAL_BASIS
        assert len(timeline) == expected["timeline_months"]
        month_keys = [p.month_key for p in timeline if p.month_key != "start"]
        assert "2026-06" in month_keys
        assert "2026-07" in month_keys
        assert expected["month_key"] in month_keys
        conn.close()


def test_june_sweep_applied_in_timeline():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sc.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        timeline = replay_actual_timeline(conn)
        jun = next(p for p in timeline if p.month_key == "2026-06")
        assert abs(jun.monthly_realized_net - expected["jun_realized_net"]) < 0.02
        assert jun.sweep_total > 0
        conn.close()


def test_scenario_visualizer_structure():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sc.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        viz = build_scenario_visualizer(conn)
        assert viz["goal"] == 5_000_000
        assert len(viz["actual_timeline"]) >= 3
        assert "journal_pace" in viz["scenarios"]
        assert "required_10yr" in viz["scenarios"]
        assert viz["summary"]
        assert viz["scenarios"]["journal_pace"]["months_to_goal"] is not None
        assert viz["account_value"] > ORIGINAL_BASIS
        conn.close()


def test_empty_journal_still_returns_start_point():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "empty.db"
        from investment_agent.db import init_db

        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        viz = build_scenario_visualizer(conn)
        assert len(viz["actual_timeline"]) == 1
        assert viz["current_balance"] == ORIGINAL_BASIS
        conn.close()
```


---

<a id="tests-test_screen_actions-py"></a>
## `tests/test_screen_actions.py`

```python
"""Tests for screen action timestamps."""

from __future__ import annotations

from investment_agent.db import connect, init_db
from investment_agent.screen_actions import (
    ACTION_DAILY_INGEST,
    ACTION_SP500,
    get_screen_action_status,
    record_screen_action,
)


def test_record_and_fetch_screen_action(tmp_path):
    path = init_db(tmp_path / "t.db")
    conn = connect(path)
    try:
        record_screen_action(conn, ACTION_SP500, detail="503 tickers")
        conn.commit()
        status = get_screen_action_status(conn)
        assert status[ACTION_SP500]["completed_at"]
        assert status[ACTION_SP500]["detail"] == "503 tickers"
        assert status[ACTION_SP500]["source"] == "recorded"
        assert status[ACTION_DAILY_INGEST]["completed_at"] is None or status[ACTION_DAILY_INGEST]["source"] == "none"
    finally:
        conn.close()
```


---

<a id="tests-test_special_watch-py"></a>
## `tests/test_special_watch.py`

```python
"""Tests for Step 3 status labels and Special Watch reporting."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.db import init_db, insert_ticker_metrics
from investment_agent.step3_status import (
    LOW_LIQUIDITY,
    MISSING_METRICS,
    STEP3_PASS,
    TOO_QUIET,
    TOO_WILD,
    classify_step3_status,
)
from investment_agent.watchlist import (
    build_special_watch_report,
    load_preset_tickers,
)


def test_classify_step3_status_bands():
    assert classify_step3_status(meets_liquidity=True, near_swing=True, avg_range_pct=3.0) == STEP3_PASS
    assert classify_step3_status(meets_liquidity=True, near_swing=False, avg_range_pct=1.5) == TOO_QUIET
    assert classify_step3_status(meets_liquidity=True, near_swing=False, avg_range_pct=6.0) == TOO_WILD
    assert classify_step3_status(meets_liquidity=False, near_swing=False, avg_range_pct=3.0) == LOW_LIQUIDITY
    assert classify_step3_status(ticker="X") == MISSING_METRICS


def test_datacenter_us_preset_loads():
    tickers = load_preset_tickers("datacenter_us")
    assert len(tickers) >= 90
    assert "VRT" in tickers
    assert "ACM" in tickers
    assert "ASML" in tickers
    assert "NBIS" in tickers
    assert "DRAM" in tickers
    assert len(tickers) == len(set(tickers))


def test_add_special_watch_ticker_manual_extra():
    from investment_agent.watchlist import (
        add_special_watch_ticker,
        get_special_watch_extras,
        merge_special_watch_tickers,
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sw2.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        result = add_special_watch_ticker(conn, "datacenter_us", "TESTX")
        conn.commit()
        assert result["ok"] is True
        assert result["added_to_extras"] is True
        assert get_special_watch_extras(conn, "datacenter_us") == ["TESTX"]

        merged = merge_special_watch_tickers("datacenter_us", ["TESTX"])
        assert "TESTX" in merged
        assert "VRT" in merged

        # Preset ticker does not duplicate in extras
        result2 = add_special_watch_ticker(conn, "datacenter_us", "VRT")
        conn.commit()
        assert result2["already_in_preset"] is True
        assert get_special_watch_extras(conn, "datacenter_us") == ["TESTX"]

        report = build_special_watch_report(conn, "datacenter_us")
        by_ticker = {r["ticker"]: r for r in report["tickers"]}
        assert "TESTX" in by_ticker
        assert by_ticker["TESTX"]["step3_status"] == MISSING_METRICS
        conn.close()


def test_build_special_watch_report_counts():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sw.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        insert_ticker_metrics(
            conn,
            {
                "ticker": "VRT",
                "computed_at": "2026-08-01T12:00:00+00:00",
                "adv_dollar": 1_000_000_000.0,
                "avg_range_pct": 3.0,
                "liquidity_cap": 8_000_000.0,
                "last_close": 100.0,
                "last_quote": 100.0,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        insert_ticker_metrics(
            conn,
            {
                "ticker": "FIX",
                "computed_at": "2026-08-01T12:00:00+00:00",
                "adv_dollar": 500_000_000.0,
                "avg_range_pct": 6.0,
                "liquidity_cap": 4_000_000.0,
                "last_close": 50.0,
                "last_quote": 50.0,
                "meets_liquidity_min": True,
                "near_swing_target": False,
            },
        )
        conn.commit()

        report = build_special_watch_report(conn, "datacenter_us")
        conn.close()

        assert report["preset"] == "datacenter_us"
        assert report["ticker_count"] >= 90
        assert report["step3_pass"] >= 1
        assert report["too_wild"] >= 1

        by_ticker = {r["ticker"]: r for r in report["tickers"]}
        assert by_ticker["VRT"]["step3_status"] == STEP3_PASS
        assert by_ticker["FIX"]["step3_status"] == TOO_WILD
        assert by_ticker["VRT"]["step3_label"] == "Step 3 pass"
```


---

<a id="tests-test_stock_team-py"></a>
## `tests/test_stock_team.py`

```python
"""Tests for stock team screener and queue."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ticker_metrics
from investment_agent.stock_team import (
    advance_queue_state,
    build_analysis_card,
    sync_queue_from_screener,
)


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _insert_metric(conn, ticker: str, *, near_swing: bool = True):
    insert_ticker_metrics(
        conn,
        {
            "ticker": ticker,
            "computed_at": "2026-07-31T12:00:00+00:00",
            "adv_dollar": 50_000_000,
            "avg_range_pct": 3.0 if near_swing else 1.0,
            "liquidity_cap": 400_000,
            "last_close": 100.0,
            "last_quote": 100.0,
            "meets_liquidity_min": True,
            "near_swing_target": near_swing,
        },
    )


def test_build_analysis_card_excludes_spy():
    conn, path = _conn()
    try:
        _insert_metric(conn, "SPY")
        conn.commit()
        row = conn.execute("SELECT * FROM ticker_metrics LIMIT 1").fetchone()
        assert build_analysis_card(row, 10_000) is None
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_sync_queue_adds_candidates():
    conn, path = _conn()
    try:
        _insert_metric(conn, "AAPL")
        _insert_metric(conn, "MSFT", near_swing=False)
        conn.commit()
        result = sync_queue_from_screener(conn, max_items=3)
        assert result["ok"] is True
        assert result["added"] == 1
        assert result["added_tickers"] == ["AAPL"]
        row = conn.execute("SELECT ticker, state FROM queue_items").fetchone()
        assert row["ticker"] == "AAPL"
        assert row["state"] == "watching"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_sync_queue_skips_when_all_live_already_active():
    conn, path = _conn()
    try:
        _insert_metric(conn, "AAPL")
        conn.commit()
        first = sync_queue_from_screener(conn, max_items=3)
        assert first["added"] == 1
        second = sync_queue_from_screener(conn, max_items=3)
        assert second["added"] == 0
        assert second["already_in_queue"] == 1
        assert "already in the queue" in second["message"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_advance_queue_state():
    conn, path = _conn()
    try:
        conn.execute(
            """
            INSERT INTO queue_items (ticker, state, entry_price, target_price, stop_price)
            VALUES ('AAPL', 'watching', 100, 101.13, 99.5)
            """
        )
        conn.commit()
        result = advance_queue_state(conn, 1)
        assert result["ok"] is True
        assert result["to_state"] == "approved"
    finally:
        conn.close()
        path.unlink(missing_ok=True)
```


---

<a id="tests-test_strategy_models-py"></a>
## `tests/test_strategy_models.py`

```python
"""Tests for strategy models and daily profit targets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import daily_profit_target, growth_plan_milestones, next_growth_tier
from investment_agent.strategy_models import target_pct_for_dollars


def test_daily_profit_target_scales_every_5k():
    assert daily_profit_target(10_000) == 150
    assert daily_profit_target(14_999) == 150
    assert daily_profit_target(15_000) == 200
    assert daily_profit_target(20_000) == 250
    assert daily_profit_target(25_000) == 300


def test_growth_plan_milestones():
    rows = growth_plan_milestones(max_balance=25_000)
    assert rows[0] == {"balance_at_least": 10_000.0, "daily_target": 150.0}
    assert rows[2] == {"balance_at_least": 20_000.0, "daily_target": 250.0}


def test_next_growth_tier():
    tier = next_growth_tier(12_500)
    assert tier["current_daily_target"] == 150
    assert tier["next_balance"] == 15_000
    assert tier["next_daily_target"] == 200
    assert tier["amount_to_next_tier"] == 2_500


def test_target_pct_for_dollars_on_10k():
    # need $150 net + $14 fees on ~$10k deploy ≈ 1.64%
    pct = target_pct_for_dollars(net_needed=150, deploy_dollar=10_000, fees=14)
    assert pct is not None
    assert 1.6 < pct < 1.7
```


---

<a id="tests-test_tradability-py"></a>
## `tests/test_tradability.py`

```python
"""Tests for intraday tradability assessment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.tradability import assess_entry_tradability


def _assess(entry: float, quote: dict, **kwargs):
    return assess_entry_tradability(
        quote=quote,
        entry_price=entry,
        deploy_dollar=ORIGINAL_BASIS,
        net_target=150.0,
        **kwargs,
    )


def test_nflx_mon_aug3_open_entry_not_tradable():
    """Mon 8/3 — high $73.95 missed ~$73.97 target from open."""
    quote = {
        "price": 72.77,
        "open": 72.77,
        "high": 73.95,
        "low": 72.18,
        "prev_close": 72.39,
    }
    result = _assess(72.77, quote, avg_range_pct=3.0)
    assert result["verdict"] == "NOT_TRADABLE"
    assert result["max_net_at_day_high"] is not None
    assert result["max_net_at_day_high"] < 150.0


def test_nflx_wed_aug5_gap_up_not_tradable():
    """Wed 8/5 — gap up ~2.1%, little upside from open."""
    quote = {
        "price": 75.11,
        "open": 75.11,
        "high": 75.30,
        "low": 73.16,
        "prev_close": 73.57,
    }
    result = _assess(75.11, quote, avg_range_pct=3.0)
    assert result["verdict"] == "NOT_TRADABLE"
    assert any("Gap up" in b for b in result["blockers"])


def test_nflx_tue_aug4_missed_window_if_target_already_touched():
    """Tue 8/4 — if high already hit target but price retraced, not tradable NOW."""
    quote = {
        "price": 72.51,
        "open": 72.51,
        "high": 73.75,
        "low": 72.30,
        "prev_close": 73.33,
    }
    result = _assess(72.51, quote, avg_range_pct=3.0)
    assert result["verdict"] == "NOT_TRADABLE"
    assert any("missed window" in b.lower() for b in result["blockers"])


def test_room_to_target_early_session_caution():
    """Early session — high hasn't developed enough yet; marginal, not blocked."""
    quote = {
        "price": 100.0,
        "open": 100.0,
        "high": 100.25,
        "low": 99.85,
        "prev_close": 99.8,
    }
    result = _assess(100.0, quote, avg_range_pct=4.0)
    assert result["verdict"] in ("CAUTION", "TRADABLE")


def test_chase_above_open_blocks_entry():
    quote = {
        "price": 101.0,
        "open": 100.0,
        "high": 102.0,
        "low": 99.5,
        "prev_close": 99.0,
    }
    result = _assess(101.0, quote)
    assert result["verdict"] == "NOT_TRADABLE"
    assert any("above open" in b.lower() for b in result["blockers"])


def test_target_already_hit_and_retraced():
    quote = {
        "price": 99.5,
        "open": 98.0,
        "high": 101.5,
        "low": 97.5,
        "prev_close": 97.0,
    }
    result = _assess(100.0, quote)
    assert result["verdict"] in ("NOT_TRADABLE", "CAUTION")
```


---

<a id="tests-test_trade_plan-py"></a>
## `tests/test_trade_plan.py`

```python
"""Tests for trade plan and planned trade validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import sell_price_for_net_target
from investment_agent.trading_day import compute_trade_plan


def test_compute_trade_plan_growth_plan_150_net_at_10k():
    plan = compute_trade_plan(entry_price=100.0, deploy_dollar=10_000, net_target=150)
    assert plan["shares"] == 99
    assert plan["stop_price"] == 99.25
    assert plan["net_target"] == 150
    assert plan["net_at_target"] >= 149
    assert plan["net_at_target"] <= 151
    assert plan["target_pct"] > 1.6
    assert plan["net_at_stop"] < -80


def test_compute_trade_plan_scales_down_pct_at_15k():
    plan_10 = compute_trade_plan(entry_price=100.0, deploy_dollar=10_000, net_target=150)
    plan_15 = compute_trade_plan(entry_price=100.0, deploy_dollar=15_000, net_target=200)
    assert plan_15["target_pct"] < plan_10["target_pct"]
    assert plan_15["net_target"] == 200


def test_compute_trade_plan_updates_with_price():
    low = compute_trade_plan(entry_price=50.0, deploy_dollar=10_000, net_target=150)
    high = compute_trade_plan(entry_price=55.0, deploy_dollar=10_000, net_target=150)
    assert high["target_price"] > low["target_price"]
    assert high["shares"] < low["shares"]


def test_sell_price_for_net_target():
    px = sell_price_for_net_target(entry_price=72.79, shares=137, net_target=150)
    net = 137 * (px - 72.79) - 14
    assert abs(net - 150) < 0.05
```


---

<a id="tests-test_trading_day-py"></a>
## `tests/test_trading_day.py`

```python
"""Tests for intraday trading day go/no-go panel."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_regime_snapshot, insert_ticker_metrics
from investment_agent.trading_day import build_trading_day_status, session_phase, stopped_out_today

ET = ZoneInfo("America/New_York")


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _metric(conn, ticker: str):
    insert_ticker_metrics(
        conn,
        {
            "ticker": ticker,
            "computed_at": "2026-08-01T12:00:00+00:00",
            "adv_dollar": 50_000_000,
            "avg_range_pct": 3.0,
            "liquidity_cap": 400_000,
            "last_close": 100.0,
            "last_quote": 100.0,
            "meets_liquidity_min": True,
            "near_swing_target": True,
        },
    )


def test_session_phase_opening_wait():
    dt = datetime(2026, 8, 3, 9, 45, tzinfo=ET)
    assert session_phase(dt) == "opening_wait"


def test_session_phase_trade_window():
    dt = datetime(2026, 8, 3, 11, 0, tzinfo=ET)
    assert session_phase(dt) == "trade_window"


def test_trading_day_status_wait_during_opening():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": 0.2,
                "dia_change_pct": 0.1,
                "qqq_change_pct": 0.3,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "Regime OK",
            },
        )
        conn.commit()
        from unittest.mock import patch

        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 9, 50, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert status["verdict"] == "WAIT"
        assert status["session_phase"] == "opening_wait"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_trading_day_no_go_when_regime_blocks():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": -0.5,
                "dia_change_pct": -0.3,
                "qqq_change_pct": -0.1,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "All down",
            },
        )
        conn.commit()
        from unittest.mock import patch

        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert status["verdict"] == "NO_GO"
        assert status["can_enter_new"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)
```


---

<a id="tests-test_trading_days_period-py"></a>
## `tests/test_trading_days_period.py`

```python
"""Tests for trading-day period windows in period screener."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.period_screener import (
    build_ranked_candidates,
    list_trading_dates,
    date_range_for_period,
    run_period_screener,
)
from investment_agent.watchlist import load_preset_into_watchlist


def _insert_spy_week(conn: sqlite3.Connection, start: datetime, sessions: int) -> list[str]:
    """Insert SPY bars on weekdays only (no weekends)."""
    dates: list[str] = []
    d = start
    while len(dates) < sessions:
        if d.weekday() < 5:
            ds = d.strftime("%Y-%m-%d")
            insert_ohlcv_rows(
                conn,
                [
                    {
                        "ticker": "SPY",
                        "date": ds,
                        "open": 100.0,
                        "high": 103.0,
                        "low": 99.0,
                        "close": 101.0,
                        "volume": 1_000_000,
                        "source": "test",
                    }
                ],
            )
            dates.append(ds)
        d += timedelta(days=1)
    return dates


def test_list_trading_dates_excludes_weekends():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "td.db"
        init_db(path)
        conn = sqlite3.connect(path)
        end = datetime(2026, 8, 10, tzinfo=timezone.utc)  # Monday
        dates = _insert_spy_week(conn, end - timedelta(days=20), sessions=14)
        conn.commit()
        listed = list_trading_dates(conn, count=14, end_date=end.strftime("%Y-%m-%d"))
        conn.close()
        assert len(listed) == 14
        for ds in listed:
            wd = datetime.strptime(ds, "%Y-%m-%d").weekday()
            assert wd < 5, f"{ds} should be a weekday"
        assert listed[-1] <= end.strftime("%Y-%m-%d")


def test_period_screener_uses_trading_day_window():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "td2.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        end = datetime(2026, 8, 10, tzinfo=timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "SPY", "DIA", "QQQ"], end=end)
        conn.commit()

        trading_dates = list_trading_dates(conn, count=14, end_date=end.strftime("%Y-%m-%d"))
        start, end_str = date_range_for_period(14, end_date=end.strftime("%Y-%m-%d"), conn=conn)
        result = run_period_screener(
            conn,
            start_date=start,
            end_date=end_str,
            trading_dates=trading_dates,
            requested_trading_days=14,
            min_days_screened=1,
        )
        ranked = build_ranked_candidates(conn, period_days=14, end_date=end.strftime("%Y-%m-%d"))
        conn.close()

        assert result["requested_trading_days"] == 14
        assert result["days_evaluated"] <= 14
        assert ranked["trading_days_in_period"] <= 14
        if ranked["ranked"]:
            row = ranked["ranked"][0]
            assert row.get("requested_trading_days") == 14
            assert row["days_screened"] <= 14
```


---

<a id="tests-test_verify_access-py"></a>
## `tests/test_verify_access.py`

```python
"""Tests for Gate 0 verification helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings, missing_required_keys


def test_missing_required_keys_detects_empty_values():
    settings = Settings(
        anthropic_api_key="sk-test",
        fred_api_key="",
        finnhub_api_key="fh-test",
        massive_api_key=None,
        verify_test_ticker="SPY",
        app_api_key="",
        alpaca_api_key=None,
        alpaca_secret_key=None,
    )
    missing = missing_required_keys(settings)
    assert "FRED_API_KEY" in missing
    assert "ANTHROPIC_API_KEY" not in missing


def test_missing_required_keys_passes_when_all_set():
    settings = Settings(
        anthropic_api_key="sk-test",
        fred_api_key="fred-key",
        finnhub_api_key="fh-test",
        massive_api_key=None,
        verify_test_ticker="SPY",
        app_api_key="x",
        alpaca_api_key=None,
        alpaca_secret_key=None,
    )
    assert missing_required_keys(settings) == []


def test_missing_required_keys_skips_anthropic_when_disabled():
    settings = Settings(
        anthropic_api_key="",
        fred_api_key="fred-key",
        finnhub_api_key="fh-test",
        massive_api_key=None,
        verify_test_ticker="SPY",
        app_api_key="x",
        alpaca_api_key=None,
        alpaca_secret_key=None,
    )
    assert missing_required_keys(settings, require_anthropic=False) == []


def test_verify_access_module_imports():
    """Ensure verify_access script is importable."""
    import importlib.util
    import sys

    script = ROOT / "scripts" / "verify_access.py"
    spec = importlib.util.spec_from_file_location("verify_access", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_access"] = module
    spec.loader.exec_module(module)
    assert "CHECKS" in dir(module)
    assert set(module.REQUIRED_CHECKS) == {"anthropic", "fred", "finnhub"}
    assert set(module.REQUIRED_CHECKS_NO_CLAUDE) == {"fred", "finnhub"}
```


---

<a id="tests-test_yfinance_bars-py"></a>
## `tests/test_yfinance_bars.py`

```python
"""Tests for yfinance daily bar provider."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.providers import yfinance_bars


def _sample_df() -> pd.DataFrame:
    idx = pd.to_datetime(["2026-07-29", "2026-07-30"])
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1_000_000, 1_100_000],
        },
        index=idx,
    )


def _mock_ticker(df: pd.DataFrame) -> MagicMock:
    ticker = MagicMock()
    ticker.history.return_value = df
    return ticker


@patch("investment_agent.providers.yfinance_bars.yf.Ticker")
def test_get_daily_bars_parses_flat_columns(mock_ticker_cls):
    mock_ticker_cls.return_value = _mock_ticker(_sample_df())
    rows = yfinance_bars.get_daily_bars("SPY", lookback_days=30)
    assert len(rows) == 2
    assert rows[0]["ticker"] == "SPY"
    assert rows[0]["source"] == "yfinance"
    assert rows[-1]["close"] == 102.0
    mock_ticker_cls.assert_called_once_with("SPY")


@patch("investment_agent.providers.yfinance_bars.yf.Ticker")
def test_get_daily_bars_handles_multiindex_columns(mock_ticker_cls):
    flat = _sample_df()
    flat.columns = pd.MultiIndex.from_product([flat.columns, ["SPY"]])
    mock_ticker_cls.return_value = _mock_ticker(flat)
    rows = yfinance_bars.get_daily_bars("SPY", lookback_days=30)
    assert rows[0]["open"] == 100.0


@patch("investment_agent.providers.yfinance_bars.time.sleep")
@patch("investment_agent.providers.yfinance_bars.yf.Ticker")
def test_get_daily_bars_retries_on_failure(mock_ticker_cls, _mock_sleep):
    ticker = MagicMock()
    ticker.history.side_effect = [RuntimeError("DNS"), _sample_df()]
    mock_ticker_cls.return_value = ticker
    rows = yfinance_bars.get_daily_bars("SPY", lookback_days=30)
    assert len(rows) == 2
    assert ticker.history.call_count == 2
```


---

<a id="universe-datacenter_us-txt"></a>
## `universe/datacenter_us.txt`

```text
# US AI / data center buildout & maintenance — Special Watch preset
# Same Step 3 rules as all other tickers; thematic list only (no ranking boost).
# Design / engineering / EPC
ACM
J
FLR
TTEK
# Site, civil, grid construction
STRL
MTZ
PWR
MYRG
DY
ROAD
PRIM
ACA
AGX
URI
# MEP construction & facilities service
FIX
EME
IESC
APG
# Power & electrical equipment
VRT
ETN
POWL
NVT
HUBB
EMR
HON
ROK
# Cooling / HVAC
TT
CARR
MOD
JCI
AAON
LII
# Fiber, cable, networking
GLW
APH
ANET
CIEN
LITE
COHR
CRDO
MRVL
# Structural materials
NUE
STLD
VMC
MLM
EXP
# Water
XYL
PNR
# Backup / on-site generation
CAT
CMI
GNRC
GEV
BE
# Power to campus
CEG
VST
TLN
NEE
NRG
AES
OKLO
SMR
DUK
SO
AEP
EXC
XEL
EIX
WEC
ES
PEG
SRE
ED
D
PCG
FE
CMS
AEE
LNT
EVRG
NI
CNP
# Facility operators (colo / landlord)
EQIX
DLR
IRM
AMT
# Finance / development capital
BX
STWD
# Build + operate AI campuses
APLD
CORZ
WULF
HUT
IREN
CRWV
# In-rack IT hardware
SMCI
DELL
HPE
NTAP
# Semiconductor / AI infra (manual adds — metrics on ingest)
DRAM
ASML
NBIS
```


---

<a id="universe-sp100-txt"></a>
## `universe/sp100.txt`

```text
# S&P 100 subset — liquid large caps for Phase 7 screener
SPY
DIA
QQQ
AAPL
MSFT
NVDA
GOOGL
GOOG
AMZN
META
TSLA
BRK-B
UNH
JNJ
V
XOM
JPM
WMT
MA
PG
HD
CVX
MRK
ABBV
KO
PEP
COST
AVGO
LLY
TMO
MCD
CSCO
ACN
ABT
DHR
WFC
DIS
VZ
ADBE
NFLX
CRM
AMD
INTC
QCOM
TXN
AMAT
INTU
ISRG
BKNG
GILD
MDT
LOW
CAT
BA
GE
SBUX
PYPL
MU
PANW
NKE
ORCL
IBM
GS
MS
C
BAC
AXP
BLK
SCHW
DE
RTX
HON
UNP
UPS
LMT
AMGN
BMY
PFE
T
CMCSA
PM
MO
ELV
CI
CB
MMC
PLD
SO
DUK
NEE
IWM
```


---

<a id="universe-sp500-txt"></a>
## `universe/sp500.txt`

```text
# S&P 500 constituents + regime ETFs (SPY/DIA/QQQ)
# Source: https://github.com/datasets/s-and-p-500-companies (updated periodically)
SPY
DIA
QQQ
MMM
AOS
ABT
ABBV
ACN
ADBE
AMD
AES
AFL
A
APD
ABNB
AKAM
ALB
ARE
ALGN
ALLE
LNT
ALL
GOOGL
GOOG
MO
AMZN
AMCR
AEE
AEP
AXP
AIG
AMT
AWK
AMP
AME
AMGN
APH
ADI
AON
APA
APO
AAPL
AMAT
APP
APTV
ACGL
ADM
ARES
ANET
AJG
AIZ
T
ATO
ADSK
ADP
AZO
AVB
AVY
AXON
BKR
BALL
BAC
BAX
BDX
BRK-B
BBY
TECH
BIIB
BLK
BX
XYZ
BNY
BA
BKNG
BSX
BMY
AVGO
BR
BRO
BF-B
BLDR
BG
BXP
CHRW
CDNS
CPT
COF
CAH
CCL
CARR
CVNA
CASY
CAT
CBOE
CBRE
CDW
COR
CNC
CNP
CF
CRL
SCHW
CHTR
CVX
CMG
CB
CHD
CIEN
CI
CINF
CTAS
CSCO
C
CFG
CLX
CME
CMS
KO
CTSH
COHR
COIN
CL
CMCSA
FIX
COP
ED
STZ
CEG
COO
CPRT
GLW
CPAY
CTVA
CSGP
COST
CRH
CRWD
CCI
CSX
CMI
CVS
DHR
DRI
DDOG
DVA
DECK
DE
DELL
DAL
DVN
DXCM
FANG
DLR
DG
DLTR
D
DPZ
DASH
DOV
DOW
DHI
DTE
DUK
DD
ETN
EBAY
ECHO
ECL
EIX
EW
EA
ELV
EME
EMR
ETR
EOG
EQT
EFX
EQIX
EQR
ERIE
ESS
EL
EG
EVRG
ES
EXC
EXE
EXPE
EXPD
EXR
XOM
FFIV
FDS
FICO
FAST
FRT
FDX
FDXF
FIS
FITB
FSLR
FE
FISV
FLEX
F
FTNT
FTV
FOXA
FOX
BEN
FCX
GRMN
IT
GE
GEHC
GEV
GEN
GNRC
GD
GIS
GM
GPC
GILD
GPN
GL
GDDY
GS
HAL
HIG
HAS
HCA
DOC
HSIC
HSY
HPE
HLT
HD
HONA
HON
HRL
HST
HWM
HPQ
HUBB
HUM
HBAN
HII
IBM
IEX
IDXX
ITW
INCY
IR
PODD
INTC
IBKR
ICE
IFF
IP
INTU
ISRG
IVZ
INVH
IQV
IRM
JBHT
JBL
JKHY
J
JNJ
JCI
JPM
KVUE
KDP
KEY
KEYS
KMB
KIM
KMI
KKR
KLAC
KHC
KR
LHX
LH
LRCX
LVS
LDOS
LEN
LII
LLY
LIN
LYV
LMT
L
LOW
LULU
LITE
LYB
MTB
MPC
MAR
MRSH
MLM
MRVL
MAS
MA
MKC
MCD
MCK
MDT
MRK
META
MET
MTD
MGM
MCHP
MU
MSFT
MAA
MRNA
TAP
MDLZ
MPWR
MNST
MCO
MS
MOS
MSI
MSCI
NDAQ
NTAP
NFLX
NEM
NWSA
NWS
NEE
NKE
NI
NDSN
NSC
NTRS
NOC
NCLH
NRG
NUE
NVDA
NVR
NXPI
ORLY
OXY
ODFL
OMC
ON
OKE
ORCL
OTIS
PCAR
PKG
PLTR
PANW
PSKY
PH
PAYX
PYPL
PNR
PEP
PFE
PCG
PM
PSX
PNW
PNC
PPG
PPL
PFG
PG
PGR
PLD
PRU
PEG
PTC
PSA
PHM
PWR
QCOM
DGX
Q
RL
RJF
RTX
O
REG
REGN
RF
RSG
RMD
RVTY
HOOD
ROK
ROL
ROP
ROST
RCL
SPGI
CRM
SNDK
SBAC
SLB
STX
SRE
NOW
SHW
SPG
SWKS
SJM
SW
SNA
SOLV
SO
LUV
SWK
SBUX
STT
STLD
STE
SYK
SMCI
SYF
SNPS
SYY
TMUS
TROW
TTWO
TPR
TRGP
TGT
TEL
TDY
TER
TSLA
TXN
TPL
TXT
TMO
TJX
TKO
TTD
TSCO
TT
TDG
TRV
TRMB
TFC
TYL
TSN
USB
UBER
UDR
ULTA
UNP
UAL
UPS
URI
UNH
UHS
VLO
VEEV
VTR
VLTO
VRSN
VRSK
VZ
VRTX
VRT
VTRS
VICI
V
VST
VMC
WRB
GWW
WAB
WMT
DIS
WBD
WM
WAT
WEC
WFC
WELL
WST
WDC
WY
WSM
WMB
WTW
WDAY
WYNN
XEL
XYL
YUM
ZBRA
ZBH
ZTS
```


---

<a id="universe-starter10-txt"></a>
## `universe/starter10.txt`

```text
# Starter watchlist (Product Spec v3 default)
SPY
DIA
QQQ
AAPL
MSFT
NVDA
AMD
META
TSLA
IWM
```


---
