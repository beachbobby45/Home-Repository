# AI Investment Agent — Full Architecture & Build Spec (v2)

> **Purpose:** Complete handoff document for building an AI-powered stock market analysis and trading signal agent. Designed to be given to a coding agent or developer on a PC with full development environment access.
>
> **Version:** 2.0 (patched July 23, 2026)
> **Changes from v1:** Added pre-build access checklist, verified external dependency matrix, Layer 1.5 signal gate, complete risk engine spec, formal thesis schema, anti-hallucination validation, order lifecycle, expanded database schema, gate-based testing plan, realistic cost model, and removed/replaced data sources that are unavailable or impractical on free tiers.

---

## Table of Contents

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
| 2 | **Anthropic Claude API** | API key from [console.anthropic.com](https://console.anthropic.com) | ~$15–80/mo usage (see cost section) | Self-serve. Phone verification required. **No permanent free tier** — new accounts may get ~$5 one-time trial credits; ongoing use requires prepaid credits + payment method. | Cannot generate theses |
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

Create `scripts/verify_access.py` and confirm each check passes:

```python
CHECKS = [
    ("alpaca_trading", "GET /v2/account on paper endpoint → 200"),
    ("alpaca_bars", "Fetch 1 bar for SPY → non-empty"),
    ("anthropic", "Minimal messages API call → 200"),
    ("fred", "Fetch VIXCLS series → non-empty"),
    ("finnhub", "Fetch AAPL quote → non-empty"),
    ("massive_optional", "Fetch 1 agg for SPY → 200 or skip if not configured"),
]
```

**Gate rule:** If any **required** check fails, stop and resolve before proceeding to the next phase.

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
| Claude API (2–8 theses/day, cached) | **$5–25** | ~60–240 theses/month |
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
*Patched: July 23, 2026 (v2)*
*Ready for handoff to development agent or PC environment*
