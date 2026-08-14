# Phase 0 — Technical Audit (Existing Trading System)

> **Status:** Read-only audit — no code modified  
> **Date:** August 14, 2026  
> **Branch audited:** `cursor/patch-investment-agent-spec-cd1d`  
> **Baseline:** Home-Repository / AI Investment Agent (Product Spec v3)  
> **Purpose:** Inventory the existing system before Phase 1 Capital Builder ($10K → $30K) integration

---

## Executive Summary

The repository is a **mature Python monolith** with a **FastAPI dashboard**, **SQLite database**, and **Mac-local scheduling**. Phases 0–7 are marked complete in `README.md` under **Option A (no Claude in production)**.

**Strengths to preserve:** data ingest (FRED + Finnhub + yfinance), expandable watchlist (S&P 500), 14-trading-day period screener with dollar-goal ranking, pullback limit entry, intraday tradability gates, manual trade journal, learning/close reports, backtesting, and 124 automated tests.

**Major gaps vs Phase 1 Capital Builder:** no news/sentiment pipeline, no independent Risk Engine module, no Trade Proposal object, no broker API (E*TRADE manual only), no enforced daily/weekly loss limits or kill switch, no weekly $1K / $30K milestone tracking, and no production Claude/LLM integration.

**Recommendation:** Evolve the monolith module-by-module; do **not** rebuild. First implementation increment should be **Risk Engine extraction**; second should be **News Service**; third **Opportunity Score** refactor.

---

## Tag Legend

| Tag | Meaning |
|-----|---------|
| **EXISTING** | Implemented and used in production workflow |
| **PARTIAL** | Exists but incomplete, inconsistent, or not wired end-to-end |
| **MISSING** | Not present in codebase |
| **DEBT** | Present but should be fixed before relying on it |

---

## 1. Project Structure

### 1.1 Repository layout

```
Home-Repository/
├── src/investment_agent/          # Core Python package (31 modules + dashboard)
│   ├── providers/                 # finnhub.py, fred.py, yfinance_bars.py
│   └── dashboard/                 # app.py, templates/, static/
├── scripts/                       # CLI runners + Mac .command + .sh wrappers
├── tests/                         # 35 test files, 124 tests
├── docs/                          # Product specs (v3 authoritative)
├── universe/                      # sp100, sp500, starter10, datacenter_us presets
├── data/                          # agent.db (runtime, gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

There are **no separate microservices**, **no message queues**, and **no cloud deployment manifests**. Architecture is a **modular monolith** with scheduled shell scripts on macOS.

### 1.2 Applications and entry points

| Component | Entry point | Tag |
|-----------|-------------|-----|
| Dashboard API + UI | `scripts/run_dashboard.py` → `dashboard/app.py` | **EXISTING** |
| Data ingest | `scripts/run_ingest.py` → `ingest.py` | **EXISTING** |
| Period screener | `scripts/run_period_screener.py` → `period_screener.py` | **EXISTING** |
| Intraday monitor | `scripts/run_monitor.py` → `monitor.py` | **EXISTING** |
| Learning report | `scripts/run_learning.py` → `learning.py` | **EXISTING** |
| Daily/weekly close | `scripts/run_daily_close.py` → `close_report.py` | **EXISTING** |
| Backtest | `scripts/run_backtest.py` → `backtest.py` | **EXISTING** |
| Gate 0 verify | `scripts/verify_access.py` | **EXISTING** |
| Live refresh (Step 3) | `scripts/run_refresh_live.py` → `trading_day.py` | **EXISTING** |
| EOD / morning Mac pipelines | `run_end_of_day_mac.sh`, `run_morning_prep_mac.sh` | **EXISTING** |

### 1.3 Logical modules (agent roles)

| Spec role | Module(s) | Tag |
|-----------|-----------|-----|
| Market data | `ingest.py`, `providers/*`, `historical.py`, `watchlist.py` | **EXISTING** |
| Regime | `regime.py` | **EXISTING** |
| Stock team / screener | `stock_team.py`, `step3_status.py`, `liquidity.py` | **EXISTING** |
| Ranking / selection | `period_screener.py`, `dollar_target.py` | **EXISTING** |
| Strategy / entry | `pullback_entry.py`, `trading_day.py`, `strategy.py` | **EXISTING** |
| Tradability (pre-trade) | `tradability.py` | **PARTIAL** (not a standalone Risk Engine) |
| Monitor | `monitor.py` | **EXISTING** |
| Journal | `journal.py` | **EXISTING** |
| Learning | `learning.py` | **PARTIAL** (no factor attribution at proposal time) |
| CIO | `cio.py` | **PARTIAL** (rule-based only) |
| Research / macro brief | `account.py` (market_brief), `ingest.py` (FRED) | **PARTIAL** |
| News | — | **MISSING** |
| Sentiment / AI | — | **MISSING** (Anthropic verify-only) |
| Execution / broker | — | **MISSING** (manual E*TRADE) |
| Risk Engine (independent) | — | **MISSING** (controls scattered) |

### 1.4 Configuration and infrastructure

| Item | Location | Tag |
|------|----------|-----|
| Environment | `.env` / `config.py` | **EXISTING** |
| DB path | `data/agent.db` via `db.py` | **EXISTING** |
| Mac LaunchAgents | `install_ingest_schedule_mac.sh`, `install_dashboard_service_mac.sh` | **EXISTING** |
| Cloud dashboard | `start_dashboard_cloud.sh` | **PARTIAL** (dev only) |
| Docker / K8s / Terraform | — | **MISSING** |

---

## 2. Technology Stack

| Layer | Technology | Tag |
|-------|------------|-----|
| Language | Python 3.12+ | **EXISTING** |
| Web framework | FastAPI 0.115+ | **EXISTING** |
| Server | Uvicorn | **EXISTING** |
| Templates | Jinja2 (`dashboard/templates/dashboard.html`) | **EXISTING** |
| Database | SQLite (WAL mode, busy timeout 60s) | **EXISTING** |
| HTTP client | httpx (FRED, Finnhub) | **EXISTING** |
| Market data | yfinance, Finnhub, FRED | **EXISTING** |
| AI | anthropic SDK (verify script only) | **PARTIAL** |
| Testing | pytest (124 tests) | **EXISTING** |
| PDF export | fpdf2 (one-pager) | **EXISTING** |
| Message queue | — | **MISSING** |
| Cache | yfinance file cache (`YFINANCE_CACHE_DIR`) | **PARTIAL** |
| Cloud services | None in production path | **MISSING** |

### Key dependencies (`requirements.txt`)

```
python-dotenv, httpx, pydantic, yfinance, fastapi, uvicorn, jinja2,
anthropic, pytest, fpdf2
```

**Not in requirements:** Alpaca SDK, Redis, Celery, PostgreSQL, IBKR API.

---

## 3. Market Data

### 3.1 Providers

| Provider | Module | Data | Tag |
|----------|--------|------|-----|
| **FRED** | `providers/fred.py` | VIXCLS, macro series | **EXISTING** |
| **Finnhub** | `providers/finnhub.py` | Live quotes (`/quote`); candle API implemented but unused in ingest | **EXISTING** / **DEBT** |
| **yfinance** | `providers/yfinance_bars.py` | Daily OHLCV (60d default), intraday 5m/1m | **EXISTING** |
| Massive/Polygon | `verify_access.py` only | Optional Gate 0 check | **PARTIAL** |
| Alpaca | `verify_access.py` only | Skipped in v3 | **MISSING** in pipeline |

### 3.2 Ingest flow (`ingest.py`)

1. FRED macro snapshots → `macro_snapshots`
2. Finnhub quotes for watchlist + regime indices → `quotes`
3. yfinance daily bars → `ohlcv_daily` (source written as `yfinance`; schema default says `finnhub` — **DEBT**)
4. Compute `ticker_metrics` (ADV, avg range, liquidity cap, swing flags)
5. Regime evaluation → `regime_snapshots`

**Modes:** full, `--incremental`, `--after-close` (via `scripts/run_ingest.py`).

**Scale:** S&P 500 (~537 tickers) documented as 15–25 minutes via Terminal; browser ingest capped at 150 tickers (`app.py`).

### 3.3 Storage

| Table | Contents |
|-------|----------|
| `ohlcv_daily` | Daily OHLCV per ticker |
| `quotes` | Timestamped price/open/high/low/prev_close |
| `ticker_metrics` | ADV, range %, liquidity cap, Step 3 flags |
| `macro_snapshots` | FRED observations |
| `regime_snapshots` | SPY/DIA/QQQ intraday state |
| `ingest_log` | Component status audit |

### 3.4 Real-time vs historical

| Type | Source | Tag |
|------|--------|-----|
| Live quotes (Step 3) | Finnhub via `trading_day.refresh_live_quotes()` | **EXISTING** |
| Daily history | yfinance → SQLite | **EXISTING** |
| Intraday 5m (backtest/close) | yfinance on demand | **PARTIAL** (not stored persistently) |
| Corporate actions | — | **MISSING** |
| Fundamentals (full) | — | **MISSING** (liquidity/range only) |

### 3.5 Rate limits and tuning

- Finnhub: 1.05s min interval in client
- yfinance: `YFINANCE_MIN_INTERVAL_SEC`, `YFINANCE_MAX_RETRIES`, `YFINANCE_CACHE_DIR` (env, not in `.env.example` — **DEBT**)

---

## 4. News and Sentiment

| Capability | Status | Tag |
|------------|--------|-----|
| News provider integration | Not implemented | **MISSING** |
| News ingestion pipeline | Not implemented | **MISSING** |
| `news_headlines` table (described in v2 spec) | Not in `db.py` schema | **MISSING** |
| Sentiment scoring | Not implemented | **MISSING** |
| LLM thesis generation | Gate 0 verify only | **MISSING** in production |
| Prompt architecture | Described in `AI_Investment_Agent_Spec.md` only | **MISSING** in code |
| News deduplication | Described in v2 spec only | **MISSING** |
| News relevance filtering | — | **MISSING** |
| Earnings/corporate events | — | **MISSING** |

**Note:** Finnhub free tier supports company news; client not built. Product Spec v3 lists Finnhub for "quotes, news, bars" but only quotes/bars path exists.

---

## 5. Stock Selection

### 5.1 Universe selection

| Mechanism | File | Tag |
|-----------|------|-----|
| Presets (sp100, sp500, datacenter_us, starter10) | `watchlist.py`, `universe/*.txt` | **EXISTING** |
| Manual import / special watch | `watchlist.py`, dashboard API | **EXISTING** |
| Active watchlist filter | `watchlist.active = 1` | **EXISTING** |

### 5.2 Screening (Step 3)

**File:** `stock_team.py`, `liquidity.py`, `step3_status.py`

| Filter | Rule | Tag |
|--------|------|-----|
| Liquidity | ADV ≥ $2M (`MIN_ADV_DOLLAR`) | **EXISTING** |
| Swing proof | Avg daily range ~3% ±1% (`SWING_TARGET_PCT`) | **EXISTING** |
| Regime-only exclusion | SPY, DIA, QQQ not trade candidates | **EXISTING** |
| Liquidity cap sizing | 1% participation × 0.80 buffer | **EXISTING** |

### 5.3 Period ranking (14 trading days)

**File:** `period_screener.py`

**Weights (`RANK_WEIGHTS`):**

| Factor | Weight |
|--------|--------|
| Dollar hit rate | 0.32 |
| Dollar avg net at high | 0.22 |
| Consistency (days screened) | 0.10 |
| Live pass today | 0.12 |
| Hit rate (1.5% target sim) | 0.06 |
| Swing proximity | 0.08 |
| Liquidity score | 0.06 |
| Near swing flag | 0.04 |

**Dollar rank gate** (`dollar_target.py`): ≥40% $ hit rate, avg net ≥90% of daily goal, ≥2 days.

**Pullback simulation** (`pullback_entry.py`): limit buy ≈ open − 35% of avg range; 11:30 ET fill deadline.

### 5.4 Missing Phase 1 factors

| Factor (Capital Builder spec) | Status |
|-------------------------------|--------|
| Momentum | **MISSING** |
| Relative strength | **MISSING** |
| Volume (beyond ADV gate) | **PARTIAL** (ADV only) |
| Volatility (scoring factor) | **PARTIAL** (range % only) |
| News sentiment | **MISSING** |
| News significance | **MISSING** |
| Earnings/events | **MISSING** |
| Fundamental quality | **MISSING** |
| Risk/reward score | **PARTIAL** (tradability checks) |
| AI confidence | **MISSING** |
| Multi-factor Opportunity Score (0–100) | **MISSING** |

### 5.5 Current decision flow

```text
Watchlist (537 tickers)
    → Ingest (quotes + daily bars + metrics)
    → Step 3 filter (liquidity + ~3% range)
    → Period screener (14 trading days, pullback $ sim)
    → Weighted rank score + dollar rank gate
    → live_pass_today (currently in Step 3 set)
    → Top pick resolution (trading_day.resolve_actionable_pick)
    → Tradability assessment (gap, chase, day-high room)
    → Go/no-go verdict
    → Human: limit buy/sell in E*TRADE
    → Manual journal entry
    → Learning + close report (post hoc)
```

This is a **single-score rank + tradability gate**, not a **multi-factor Opportunity Score decision object**.

---

## 6. Trading Strategy

### 6.1 Constants (`strategy.py`)

| Parameter | Code value | Docs (v3/v2) | Tag |
|-----------|------------|--------------|-----|
| Target | `TARGET_PCT = 1.50` | +1.13% in older docs | **DEBT** (doc/code drift) |
| Stop | `STOP_PCT = 0.75` | −0.50% in older docs | **DEBT** |
| Max trades/day | `MAX_TRADES_PER_DAY = 2` | Documented | **PARTIAL** (not enforced) |
| Entry delay | 30 min after open | **EXISTING** | |
| Entry window | 10:00–14:30 ET | **EXISTING** | |
| Stop-out day | No re-entry after loss | **EXISTING** | |

**Growth Plan dollar target** (`finance.py`): $150 net/day at $10K deploy, scales +$50 per $5K balance tier up to $350 at $20K+.

**Pullback entry** (`pullback_entry.py`): limit buy in lower part of expected swing; limit sell at Growth Plan net target.

### 6.2 Entry conditions

| Condition | Implementation | Tag |
|-----------|----------------|-----|
| Ranked + live Step 3 | `period_screener.py`, `trading_day.py` | **EXISTING** |
| Regime not blocking | `regime.py` | **EXISTING** |
| Tradability GO | `tradability.py` | **EXISTING** |
| Pullback limit fill | `pullback_entry.py`, 11:30 ET deadline | **EXISTING** |
| 30-min opening gate | `trading_day.session_phase()` | **EXISTING** |
| Human validate | `/api/trading-day/validate` | **EXISTING** |

### 6.3 Exit conditions

| Exit | Implementation | Tag |
|------|----------------|-----|
| Target (+1.5% or $ goal sell) | Monitor alert, trade plan | **EXISTING** |
| Stop (−0.75%) | Monitor alert, trade plan | **EXISTING** |
| EOD flatten alert | `monitor.py` after 3:45 PM ET | **EXISTIAL** |
| Overnight hold | Mentioned in monitor copy; not full strategy path | **PARTIAL** |

### 6.4 Position sizing

| Rule | File | Tag |
|------|------|-----|
| `min(liquidity_cap, tradable_cash)` | `liquidity.py`, `stock_team.py` | **EXISTING** |
| Share rounding with $7 fees | `finance.py`, trade plans | **EXISTING** |
| Risk per trade (0.5–1.0% of capital) | — | **MISSING** |
| Dynamic sizing from Opportunity Score | — | **MISSING** |

### 6.5 Phase 1 Capital Builder alignment

| Phase 1 parameter | Current system | Tag |
|-------------------|----------------|-----|
| $10K start | `ORIGINAL_BASIS = 10_000` | **EXISTING** |
| $30K target | — (only $5M long-term goal) | **MISSING** |
| $1K/week target (soft) | — (daily $150 focus) | **MISSING** |
| Overnight positions | Partial alert copy | **PARTIAL** |
| Mandatory stop | Yes (0.75%) | **EXISTING** |
| Human approval | Yes (manual execution) | **EXISTING** |
| Automated execution | Explicitly out of scope v3 | **MISSING** (by design) |

---

## 7. Broker / Execution

| Capability | Status | Tag |
|------------|--------|-----|
| Broker integration | None — E*TRADE manual | **MISSING** |
| Interactive Brokers | Not referenced in code | **MISSING** |
| Alpaca paper/live | Config keys + verify skip only | **MISSING** in pipeline |
| API authentication | — | **MISSING** |
| Paper trading (broker-simulated) | — | **MISSING** |
| Paper trading (journal tags) | `[PAPER]` / `[LIVE]` in `account.py` | **PARTIAL** |
| Order types | Limit buy/sell recommended in UI; no API orders | **PARTIAL** |
| Order status handling | — | **MISSING** |
| Position reconciliation | Manual journal FIFO in `journal.py` | **PARTIAL** |
| Live trading enabled | User toggles LIVE mode; still manual fills | **PARTIAL** |

**Execution path today:**

```text
Dashboard pick → Refresh live → Validate → User places orders in E*TRADE → POST /api/journal
```

---

## 8. Risk Management

Controls are **distributed** across modules; there is **no independent Risk Engine** that can APPROVE/REJECT proposals.

### 8.1 Existing controls

| Control | Location | Tag |
|---------|----------|-----|
| Regime gate (triple index down) | `regime.py`, enforced in screener/sync/trading day | **EXISTING** |
| Mandatory stop price | All trade plans | **EXISTING** |
| Stop-out day (no revenge trades) | `trading_day.stopped_out_today()` | **EXISTING** |
| Daily target met → stop trading | `trading_day.build_trading_day_status()` | **EXISTING** |
| Gap-up / chase filters | `tradability.py` | **EXISTING** |
| Day-high room for $ goal | `tradability.py` | **EXISTING** |
| Dollar rank gate | `dollar_target.passes_dollar_rank_gate()` | **EXISTING** |
| Liquidity cap | `liquidity.py` | **EXISTING** |
| Open position caution | `trading_day.py` | **EXISTING** |
| EOD flatten alert | `monitor.py` | **EXISTING** |
| Month-end sweeps (gains only) | `finance.py`, `account.py` | **EXISTING** |
| Ingest lock (DB safety) | `db_maintenance.py` | **EXISTING** |

### 8.2 Phase 1 requirements — gap analysis

| Requirement | Status | Tag |
|-------------|--------|-----|
| Max risk per trade (0.5–1.0%) | Not enforced | **MISSING** |
| Max position size | Liquidity cap only | **PARTIAL** |
| Max portfolio exposure | Not tracked | **MISSING** |
| Daily loss limit | Not implemented | **MISSING** |
| Weekly loss limit | Not implemented | **MISSING** |
| Max drawdown halt | Not implemented | **MISSING** |
| Max open positions | Implicit (one full-size entry messaging) | **PARTIAL** |
| Stop-loss enforcement | Alerts only; no auto-sell | **PARTIAL** |
| Kill switch | Not implemented | **MISSING** |
| LLM cannot override risk | N/A (no LLM in loop) | **MISSING** architecture |

---

## 9. Backtesting

| Capability | File | Tag |
|------------|------|-----|
| Intraday 5m replay | `backtest.py` | **EXISTING** |
| Daily dollar backtest | `backtest.py` | **EXISTING** |
| Strategy model comparison | `backtest_strategy.py` (1.13/0.50 vs 1.50/0.75) | **EXISTING** |
| Historical period evaluation | `historical.py` | **EXISTING** |
| Pullback limit sim | `pullback_entry.py` | **EXISTING** |
| Transaction costs ($7/$7) | Yes | **EXISTING** |
| Regime block in backtest | Yes | **EXISTING** |
| Slippage model | No | **MISSING** |
| Walk-forward testing | No | **MISSING** |
| Out-of-sample testing | No | **MISSING** |
| Overnight hold simulation | No dedicated path | **MISSING** |
| Weekly P&L aggregation | No | **MISSING** |

**CLI:** `scripts/run_backtest.py`, `run_strategy_models.py`, `compare_backtest_intervals.py`

**Data source:** yfinance only (not Massive/Alpaca in backtest path).

---

## 10. Analytics

### 10.1 What is recorded today

| Data | Storage | Tag |
|------|---------|-----|
| Trade fills (manual) | `trade_journal` | **EXISTING** |
| Queue state / thesis text | `queue_items.thesis_summary` | **EXISTING** (rule-based) |
| Period screener hits | `period_screener_hits`, `screener_runs` | **EXISTING** |
| Rank snapshots | `rank_snapshots` | **EXISTING** |
| Close reports | `close_reports` (JSON) | **EXISTING** |
| Learning reports | `learning_reports` (JSON) | **EXISTING** |
| Price alerts | `price_alerts` | **EXISTING** |
| Ingest audit | `ingest_log` | **EXISTING** |

### 10.2 Phase 1 learning loop — gaps

| Requirement | Status | Tag |
|-------------|--------|-----|
| Trade decisions (proposal object) | Not stored | **MISSING** |
| AI scores at decision time | Not stored | **MISSING** |
| Factor scores (multi-factor) | Not stored | **MISSING** |
| Entry / exit linked to proposal | Partial via `queue_id` on journal | **PARTIAL** |
| P&L / holding time | `journal.get_completed_round_trips()` | **EXISTING** |
| Market conditions at entry | Regime in snapshots; not linked per trade | **PARTIAL** |
| Strategy version | Not versioned | **MISSING** |
| Model version | Not tracked | **MISSING** |
| Reason for trade | Rule-based thesis string only | **PARTIAL** |
| Reason for rejection | Not logged | **MISSING** |
| Performance by factor bucket | Not implemented | **MISSING** |
| Parameter optimization | Not implemented | **MISSING** |

### 10.3 Dashboard / UI

**File:** `dashboard/templates/dashboard.html` (~2,300 lines), `dashboard/static/style.css`

| Tab | Purpose | Tag |
|-----|---------|-----|
| Trade | Daily rhythm, candidates, top pick, validate, go/no-go | **EXISTING** |
| Screen | Queue, alerts, ranked universe, special watch | **EXISTING** |
| Review | Close reports, learning | **EXISTING** |
| Account | Journal, jars, sweeps, paper/live mode, $5M scenario | **EXISTING** |
| Setup | Auto refresh, Terminal commands, EOD/morning/refresh scripts | **EXISTING** |

**API surface:** 50+ routes in `dashboard/app.py` (v0.8.0).

---

## Current Architecture

### Component diagram (as-built)

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Mac LaunchAgents (optional)                  │
│   6:30 AM incremental ingest  |  4:30 PM after-close + screener │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  scripts/          CLI wrappers (ingest, screener, monitor, …)   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  src/investment_agent/          Python monolith                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ ingest   │ │ screener │ │ trading  │ │ journal  │          │
│  │ regime   │ │ dollar   │ │ day      │ │ learning │          │
│  │ liquidity│ │ pullback │ │ tradabil │ │ close    │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       └────────────┴────────────┴────────────┘                  │
│                         │                                        │
│                  dashboard/app.py (FastAPI)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    SQLite (data/agent.db)
                             │
              External: FRED, Finnhub, yfinance
                             │
                    Human: E*TRADE (manual)
```

### Current data flow

```text
FRED ──────────► macro_snapshots
Finnhub ───────► quotes (live + ingest)
yfinance ──────► ohlcv_daily
                    │
                    ▼
              ticker_metrics (ADV, range, Step 3 flags)
                    │
                    ▼
         period_screener (14 trading days, pullback $ sim)
                    │
                    ▼
              ranked candidates (weighted score)
                    │
                    ▼
         trading_day (tradability + go/no-go)
                    │
                    ▼
              Dashboard → Human → E*TRADE → trade_journal
                    │
                    ▼
         learning_reports + close_reports (nightly/EOD)
```

### Current trading flow

```text
[After close]  ingest → screener → close report
[Before open]  prepare morning → candidates table
[Before buy]   refresh live → validate → limit orders in E*TRADE
[After fill]   log journal (PAPER or LIVE tag)
[Intraday]     monitor alerts (target/stop/EOD)
[Review]       daily close, learning, scenario
```

---

## Capability Matrix (EXISTING / PARTIAL / MISSING / DEBT)

### EXISTING (functional, keep)

- SQLite schema with 18 tables (`db.py`)
- FRED + Finnhub + yfinance ingest pipeline
- S&P 500 / SP100 / special watch presets
- Step 3 liquidity + swing screener
- 14-trading-day period screener with persistence
- Dollar-goal ranking and rank gate
- Pullback limit entry simulation
- Regime gate (SPY/DIA/QQQ)
- Intraday tradability checks
- Go/no-go trading day panel
- Trade journal (FIFO, fees, round trips)
- Paper/LIVE journal tagging
- Intraday monitor (target/stop/EOD alerts)
- Queue state machine
- Learning + CIO panels (rule-based)
- Daily/weekly close reports
- $5M scenario visualizer
- Backtest (5m + daily dollar)
- Mac EOD / morning / refresh live scripts
- 124 pytest tests
- Dashboard (5 tabs, 50+ API routes)

### PARTIAL (modify for Phase 1)

- **Scoring** — single weighted rank; needs multi-factor Opportunity Score
- **Risk** — checks exist but not centralized; no loss limits or kill switch
- **AI** — Anthropic in Gate 0 only; agents rule-based
- **Paper trading** — journal tags only; no broker simulation
- **Overnight holds** — alert copy exists; strategy/backtest don't fully support
- **Analytics** — post-trade learning; no proposal-level attribution
- **Position sizing** — liquidity cap only; no %-of-capital risk sizing
- **Target/stop constants** — code 1.50/0.75 vs docs 1.13/0.50
- **MAX_TRADES_PER_DAY** — constant exists, not enforced
- **Finnhub candles** — client exists, bypassed for yfinance
- **Cloud deployment** — cloud dev script only; production is Mac-local

### MISSING (add for Phase 1)

- News Service (ingest, store, dedupe)
- Sentiment / AI Service (Claude, gated)
- Opportunity Score (0–100, multi-factor)
- Trade Proposal / Decision Object (DB + API + UI)
- Independent Risk Engine (approve/reject)
- Weekly $1K / $30K capital milestone tracking
- Daily and weekly loss limits
- Kill switch
- Per-trade risk % (0.5–1.0%)
- Portfolio exposure tracking
- Rejection reason logging
- Strategy/model versioning
- Broker API (IB or other) — defer execution to later increment
- Momentum, relative strength, fundamentals, earnings factors

### TECHNICAL DEBT (fix before relying)

| ID | Issue | Files |
|----|-------|-------|
| D1 | Target/stop % mismatch code vs docs | `strategy.py`, `monitor.py`, docs |
| D2 | `MAX_TRADES_PER_DAY` not enforced | `strategy.py`, `trading_day.py`, `journal.py` |
| D3 | Duplicate `TOP_PICK_NO_GO_DROP_PCT` | `trading_day.py:42, :399` |
| D4 | `ohlcv_daily.source` default `finnhub` but writes `yfinance` | `db.py`, `ingest.py` |
| D5 | Dead Finnhub candle path | `providers/finnhub.py`, `ingest.py` |
| D6 | Mac-only scheduling (no Linux/cloud cron) | `install_ingest_schedule_mac.sh` |
| D7 | SQLite concurrency at S&P 500 scale | `db_maintenance.py`, ingest lock |
| D8 | v2 spec (`AI_Investment_Agent_Spec.md`) describes Alpaca auto-orders | docs |
| D9 | yfinance tuning env vars not in `.env.example` | `yfinance_bars.py` |
| D10 | No tests for `backtest_strategy.py`, auth middleware | tests/ |
| D11 | Growth Plan is daily $150; Phase 1 wants weekly $1K soft target | product alignment |
| D12 | Bundled `AI_Investment_Agent_PROJECT_PACKAGE.md` may stale | root |

---

## Recommended Target Architecture (Phase 1)

Evolve monolith into **logical services as Python modules** (not microservices yet):

```text
┌─────────────────────────────────────────────────────────────────┐
│ 1. Market Data Service     │ ingest.py, providers/*  [EXTEND]  │
│ 2. News Service            │ news_service.py         [NEW]     │
│ 3. Sentiment/AI Service    │ ai_service.py           [NEW]     │
│ 4. Opportunity Engine      │ opportunity_score.py    [NEW]     │
│                            │ period_screener.py      [REFACTOR]│
│ 5. Strategy Engine         │ pullback_entry.py       [EXTEND]  │
│                            │ strategy.py             [EXTEND]  │
│ 6. Risk Engine             │ risk_engine.py          [NEW]     │
│ 7. Portfolio Manager       │ account.py, journal.py  [EXTEND] │
│ 8. Trade Proposal Service  │ trade_proposal.py       [NEW]     │
│ 9. Human Approval UI       │ dashboard               [EXTEND]  │
│ 10. Execution Service      │ execution/ (stub)       [STUB]    │
│ 11. Position Monitor       │ monitor.py              [EXTEND]  │
│ 12. Trade Journal          │ journal.py              [EXTEND] │
│ 13. Performance Analytics  │ learning.py             [EXTEND] │
│ 14. Backtesting Engine     │ backtest.py             [EXTEND] │
└─────────────────────────────────────────────────────────────────┘

Flow:
  Market Data + News
       → Opportunity Engine (multi-factor score)
       → Strategy Engine (entry/stop/target/size)
       → Trade Proposal
       → Risk Engine (APPROVE / REJECT — LLM cannot override)
       → Human Approval UI
       → Manual Execution (Phase 1) → Journal
       → Performance Analytics → Learning Loop
```

### Risk Engine placement (critical)

```text
        AI / Opportunity Engine
                 │
                 ▼
          Trade Proposal
                 │
                 ▼
        ┌─────────────────┐
        │   RISK ENGINE   │  ← NEW independent module
        └────────┬────────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
 Position     Daily       Weekly
  Risk         Loss         Loss
     │           │           │
     └───────────┼───────────┘
                 ▼
          APPROVE / REJECT
                 │
                 ▼
         Human Approval (Phase 1)
                 │
                 ▼
         Manual E*TRADE → Journal
```

---

## Recommended Implementation Sequence

**Do not implement all at once.** Controlled increments after this audit is reviewed:

| Step | Deliverable | Reuse | New/Modify |
|------|-------------|-------|------------|
| **0** | This audit doc | — | **DONE** |
| **1** | `docs/PHASE1_CAPITAL_BUILDER_SPEC.md` | Business params from Capital Builder plan | Review + approve |
| **2** | **Increment 1: Risk Engine** | Extract from `tradability.py`, `regime.py`, `trading_day.py` | `risk_engine.py`, daily/weekly loss, kill switch, tests |
| **3** | **Increment 2: News Service** | Finnhub client pattern | `news_service.py`, DB table, ingest hook |
| **4** | **Increment 3: Opportunity Score** | `period_screener.py` weights | `opportunity_score.py`; deterministic factors first |
| **5** | **Increment 4: Trade Proposal** | Top pick UI | `trade_proposal.py`, schema, API, UI card |
| **6** | **Increment 5: Capital milestones** | `finance.py`, Account tab | $10K→$30K, soft $1K/week tracker |
| **7** | **Increment 6: AI sentiment** | Gate 0 Anthropic | `ai_service.py`, gated Claude, `ai_confidence` factor |
| **8** | **Increment 7: Learning v2** | `learning.py`, `close_report.py` | Proposal linkage, rejection logs, factor buckets |
| **9** | **Increment 8: Backtest extend** | `backtest.py` | Overnight, weekly P&L, slippage stub |
| **10** | **Increment 9: Execution design** | — | IB vs E*TRADE decision doc only |
| **11** | **Increment 10: Paper broker** | — | After spec approval; not before risk + proposals validated |

---

## Files / Modules Likely to Change (Phase 1)

### Do NOT rewrite (explicit preserve list)

| Module | Reason |
|--------|--------|
| `journal.py` | Source of truth; extend only |
| `providers/finnhub.py`, `providers/fred.py` | Stable integrations |
| `db.py` | Extend schema via migrations only |
| `ingest.py` | Extend for news; keep core pipeline |
| Mac shell scripts | Operational workflow in use |
| `tests/` | Extend; do not delete passing tests |

### Modify

| File | Change |
|------|--------|
| `period_screener.py` | Delegate scoring to Opportunity Engine |
| `trading_day.py` | Consume Trade Proposal + Risk Engine verdict |
| `tradability.py` | Move hard gates into Risk Engine |
| `dashboard/app.py` | Proposal API, risk status, weekly capital widget |
| `dashboard/templates/dashboard.html` | Proposal card, rejection reasons |
| `learning.py` | Link proposals, factor attribution |
| `finance.py` | Phase 1 milestones alongside $5M goal |
| `strategy.py` | Align constants with spec; enforce max trades |
| `ingest.py` | Hook news ingest after quotes |

### Add (new files)

| File | Purpose |
|------|---------|
| `risk_engine.py` | Independent approve/reject |
| `news_service.py` | Headlines ingest + dedupe |
| `opportunity_score.py` | Multi-factor 0–100 score |
| `trade_proposal.py` | Decision object lifecycle |
| `ai_service.py` | Claude sentiment + explanation (gated) |
| `tests/test_risk_engine.py` | Risk unit tests |
| `tests/test_opportunity_score.py` | Scoring tests |
| `tests/test_trade_proposal.py` | Proposal lifecycle tests |

### Database additions (proposed, not implemented)

| Table | Purpose |
|-------|---------|
| `news_headlines` | Stored news events |
| `trade_proposals` | Decision objects with factor scores |
| `risk_decisions` | Approve/reject audit trail |
| `strategy_versions` | Version tracking |

---

## Risks and Dependencies

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rebuilding instead of evolving | Lose 124 tests + working ingest | Follow increment plan; preserve list above |
| LLM cost / latency | Claude on 500 tickers unusable | Gate AI to top-N proposals only; cache |
| Finnhub news rate limits | News ingest may throttle | Batch + dedupe; store locally |
| SQLite at scale | Lock contention during S&P 500 ingest | Keep ingest lock; consider Postgres later |
| Broker pivot (IB vs E*TRADE) | Execution module rework | Phase 1 stays manual; defer API |
| Weekly $1K quota pressure | Over-trading | Spec says target not requirement; enforce in Risk Engine |
| Doc/code drift (target %) | Wrong backtest expectations | Fix D1 in Increment 1 or 2 |
| Mac-only ops | User off-machine misses ingest | Document EOD scripts; future cloud scheduler |
| No rejection logging | Can't train learning loop | Increment 4 (proposals) blocks Increment 7 |

### Dependencies for Phase 1 start

1. `.env` with `FINNHUB_API_KEY`, `FRED_API_KEY` (required today)
2. `ANTHROPIC_API_KEY` (required for Increment 6 only)
3. Approved `PHASE1_CAPITAL_BUILDER_SPEC.md`
4. Decision: keep E*TRADE manual for Phase 1 execution (recommended)

---

## Tests

| Metric | Value |
|--------|-------|
| Total tests | **124** |
| Test files | **35** |
| Framework | pytest |
| CI | Not configured in repo (local `pytest` only) |

**Well covered:** ingest, regime, tradability, journal, finance, period screener, pullback, dollar gate, dashboard integration.

**Gaps:** `backtest_strategy.py`, proposal/risk modules (don't exist yet), dashboard auth middleware, news pipeline.

---

## Environment Variables

| Variable | Required today | Phase 1 use |
|----------|----------------|-------------|
| `FRED_API_KEY` | Yes | Unchanged |
| `FINNHUB_API_KEY` | Yes | Quotes + news (Increment 2) |
| `ANTHROPIC_API_KEY` | Gate 0 only | Increment 6 (sentiment) |
| `APP_API_KEY` | Optional | Dashboard auth |
| `MASSIVE_API_KEY` | Optional | Still optional |
| `ALPACA_*` | Optional/unused | Not Phase 1 |
| `YFINANCE_*` | Optional tuning | Document in `.env.example` (DEBT) |

---

## Alignment with Business Objectives

### Phase 1 — Capital Building ($10K → $30K)

| Requirement | Audit result |
|-------------|--------------|
| Starting capital $10K | **EXISTING** (`ORIGINAL_BASIS`) |
| Target $30K | **MISSING** milestone tracker |
| Weekly $1K (soft) | **MISSING** |
| Overnight positions | **PARTIAL** |
| Human approval | **EXISTING** |
| Automated execution later | **MISSING** (by design) |
| Risk per trade 0.5–1.0% | **MISSING** |
| Mandatory stop | **EXISTING** |
| Daily/weekly loss limits | **MISSING** |
| Kill switch | **MISSING** |
| Trade journal | **EXISTING** |
| AI news | **MISSING** |
| AI sentiment | **MISSING** |
| Technical analysis | **PARTIAL** (range, tradability) |
| Market regime | **EXISTING** |
| Dynamic position sizing | **PARTIAL** |
| Multi-factor opportunity score | **MISSING** |

### Phase 2 — Active/automated (do not implement yet)

No code paths exist for automated broker execution. **Correct per instructions.**

---

## Explicit Do-Not-Change List (until spec approved)

1. Manual E*TRADE execution workflow
2. Journal as P&L source of truth
3. Core ingest pipeline (FRED + Finnhub quotes + yfinance bars)
4. Watchlist preset files and load mechanism
5. Existing pytest suite (extend only)
6. Mac EOD / morning / refresh live scripts
7. Live trading broker API (remain disabled)

---

## Next Steps (after audit review)

1. **You review this document** — mark sections REUSE / MODIFY / ADD / DEFER
2. **Draft `docs/PHASE1_CAPITAL_BUILDER_SPEC.md`** — Trade Proposal schema, risk rule numbers, UI wireframes
3. **Authorize Increment 1 only** — Risk Engine (`risk_engine.py`) with daily/weekly loss + kill switch
4. **Controlled Cursor prompt** — one increment per review cycle

---

## Document History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-14 | Cursor Phase 0 audit | Initial read-only inventory |

---

*End of Phase 0 Technical Audit. No repository code was modified to produce this document.*
