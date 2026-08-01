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
