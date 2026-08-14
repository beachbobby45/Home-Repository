# Phase 1 — Capital Builder Technical Specification

> **Status:** Draft for review — **no implementation authorized by this document alone**  
> **Date:** August 14, 2026  
> **Baseline:** [PHASE1_TECHNICAL_AUDIT.md](./PHASE1_TECHNICAL_AUDIT.md)  
> **Supersedes for Phase 1 scope:** Daily-only Growth Plan UX where this spec explicitly differs  
> **Authoritative long-term product rules:** [PRODUCT_SPEC_V3.md](./PRODUCT_SPEC_V3.md) (preserved where not contradicted below)

---

## 1. Purpose

Define **Phase 1 — Capital Builder**: evolve the existing AI Investment Agent from a daily intraday copilot into a **human-approved capital growth system** targeting **$10,000 → $30,000** with a **soft weekly goal of ~$1,000**, without rebuilding the repository or enabling automated broker execution.

This spec is the **second artifact** in the controlled workflow:

```text
Phase 0 audit (done) → Phase 1 spec (this doc) → review → Increment N Cursor prompt → code → tests → review
```

---

## 2. Business Objectives

### 2.1 Primary milestone

| Parameter | Value | Notes |
|-----------|-------|-------|
| Starting capital | **$10,000** | Maps to `ORIGINAL_BASIS` / tradable cash |
| Target capital | **$30,000** | **New** Phase 1 milestone (alongside existing $5M long-term display) |
| Weekly target | **~$1,000** | **Soft target** — guidance only, not a quota |
| Time horizon | Open-ended | No forced calendar deadline |

**Critical rule:** The system must **never manufacture trades** to hit the weekly number. If no proposal passes Opportunity Score + Risk Engine + human judgment, the correct output is **no trade**.

### 2.2 Trading style (Phase 1)

| Parameter | Value |
|-----------|-------|
| Style | Short-term / swing; intraday entries allowed |
| Overnight holds | **Allowed** when proposal + risk + human approve |
| Day trading | Allowed within broker rules and risk limits |
| Leverage | **None** (Phase 1) |
| Human approval | **Required** before every entry |
| Automated execution | **Out of scope** Phase 1 |
| Broker | **E*TRADE manual** (existing workflow) — no IB/API orders |

### 2.3 Relationship to existing Growth Plan

The codebase today optimizes for **daily net profit** ($150 at $10K deploy, scaling with balance). Phase 1 **adds** weekly and milestone tracking without removing daily metrics:

| Metric | Keep | Add |
|--------|------|-----|
| Daily net goal | Yes (`daily_profit_target()`) | — |
| Weekly net progress | — | Yes (~$1K soft band) |
| Account milestone | $5M long-term | **$30K Phase 1 gate** |
| Pullback limit entry | Yes | Extend to proposals |
| 14d period screener | Yes | Feed Opportunity Score |

---

## 3. Architectural Principles

1. **Evolve, don't rebuild** — extend `src/investment_agent/` modules per [PHASE1_TECHNICAL_AUDIT.md](./PHASE1_TECHNICAL_AUDIT.md).
2. **Risk Engine is sovereign** — LLM may recommend; Risk Engine **approves or rejects**. LLM output cannot bypass risk.
3. **Trade Proposal is the unit of work** — not a bare ticker rank.
4. **Journal remains source of truth** for fills and P&L until Execution Service exists.
5. **One increment per Cursor build** — each increment has acceptance tests before the next.
6. **Live broker API stays disabled** until strategy, risk, backtest, and journal evidence support it.

---

## 4. Target Logical Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│ MARKET DATA SERVICE          ingest.py, providers/*     [EXTEND] │
│ NEWS SERVICE                 news_service.py            [NEW]    │
│ SENTIMENT / AI SERVICE       ai_service.py              [NEW]    │
│ OPPORTUNITY ENGINE           opportunity_score.py       [NEW]    │
│ STRATEGY ENGINE              pullback_entry, strategy   [EXTEND]│
│ RISK ENGINE                  risk_engine.py             [NEW]    │
│ PORTFOLIO MANAGER            account.py, journal.py     [EXTEND]│
│ TRADE PROPOSAL SERVICE       trade_proposal.py          [NEW]    │
│ HUMAN APPROVAL UI            dashboard                  [EXTEND] │
│ EXECUTION SERVICE            execution/ (stub)          [STUB]   │
│ POSITION MONITOR             monitor.py                 [EXTEND] │
│ TRADE JOURNAL                journal.py                 [EXTEND] │
│ PERFORMANCE ANALYTICS        learning.py                [EXTEND] │
│ BACKTESTING ENGINE           backtest.py                [EXTEND] │
└──────────────────────────────────────────────────────────────────┘
```

### 4.1 Phase 1 trading flow

```text
[EOD]     ingest (+ news) → screener → close report
[Morning] prepare proposals → Opportunity Score → Strategy plan → Risk Engine
[Human]   review Proposal card → APPROVE / REJECT (with reason)
[Pre-buy] refresh live → re-run Risk Engine on live quote
[Execute] manual limit orders in E*TRADE
[Log]     journal entry linked to proposal_id
[Monitor] target / stop / EOD alerts
[Close]   journal SELL → learning attributes outcome to factors
```

---

## 5. Core Domain Objects

### 5.1 Trade Proposal

A **Trade Proposal** is the primary decision artifact. It replaces "top pick card only" as the persisted record of intent.

#### 5.1.1 Lifecycle states

```text
draft → risk_rejected | proposed → human_rejected | human_approved
     → executed (journal BUY logged) → closed (journal SELL logged)
     → expired (no fill / session end)
```

| State | Meaning |
|-------|---------|
| `draft` | Generated internally, not yet risk-checked |
| `risk_rejected` | Failed Risk Engine — not shown as actionable |
| `proposed` | Passed risk — awaiting human |
| `human_rejected` | Operator declined — reason required |
| `human_approved` | Operator approved — ready for E*TRADE |
| `executed` | BUY logged in journal with `proposal_id` |
| `closed` | Round trip complete |
| `expired` | Limit not filled by deadline or session rules |

#### 5.1.2 JSON schema (logical)

```json
{
  "id": "uuid-or-int",
  "strategy_version": "phase1-capital-builder-v1",
  "model_version": "rule-based-v1 | claude-sonnet-v1",
  "created_at": "ISO-8601",
  "valid_until": "ISO-8601",
  "session_date_et": "YYYY-MM-DD",

  "ticker": "NVDA",
  "direction": "long",

  "opportunity_score": 87,
  "factor_scores": {
    "market_regime": 81,
    "technical_setup": 91,
    "momentum": 94,
    "relative_strength": 0,
    "volume": 88,
    "volatility": 76,
    "news_sentiment": 84,
    "news_significance": 80,
    "earnings_events": 100,
    "fundamental_quality": 0,
    "risk_reward": 85,
    "ai_confidence": 89,
    "dollar_history": 82
  },

  "entry_mode": "pullback_limit",
  "session_open": 100.00,
  "limit_buy_price": 98.95,
  "limit_sell_price": 100.59,
  "stop_price": 98.21,
  "shares": 100,
  "notional": 9895.00,
  "max_risk_dollars": 75.00,
  "expected_rr": 2.4,
  "net_target": 150.00,

  "risk_verdict": "approved | rejected",
  "risk_checks": [
    {"name": "daily_loss_limit", "ok": true, "message": "..."}
  ],
  "risk_rejection_reason": null,

  "human_verdict": null,
  "human_rejection_reason": null,
  "human_approved_at": null,
  "human_approved_by": "operator",

  "explanation": "Human-readable summary (rule-based or Claude)",
  "explanation_short": "One-line headline",

  "journal_buy_id": null,
  "journal_sell_id": null,
  "outcome_net_pnl": null,
  "outcome_exit_reason": null
}
```

**Note:** Factors scored `0` mean **not yet implemented** (weight excluded from composite until Increment 3+).

#### 5.1.3 Database table (proposed)

```sql
CREATE TABLE trade_proposals (
  id INTEGER PRIMARY KEY,
  proposal_uuid TEXT NOT NULL UNIQUE,
  strategy_version TEXT NOT NULL,
  model_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  valid_until TEXT,
  session_date_et TEXT NOT NULL,
  ticker TEXT NOT NULL,
  direction TEXT NOT NULL DEFAULT 'long',
  opportunity_score REAL NOT NULL,
  factor_scores_json TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  risk_verdict TEXT NOT NULL,
  risk_checks_json TEXT NOT NULL,
  risk_rejection_reason TEXT,
  human_verdict TEXT,
  human_rejection_reason TEXT,
  human_approved_at TEXT,
  explanation TEXT,
  explanation_short TEXT,
  status TEXT NOT NULL,
  journal_buy_id INTEGER,
  journal_sell_id INTEGER,
  outcome_net_pnl REAL,
  outcome_exit_reason TEXT,
  FOREIGN KEY (journal_buy_id) REFERENCES trade_journal(id),
  FOREIGN KEY (journal_sell_id) REFERENCES trade_journal(id)
);
```

Extend `trade_journal`:

```sql
ALTER TABLE trade_journal ADD COLUMN proposal_id INTEGER
  REFERENCES trade_proposals(id);
```

---

### 5.2 Opportunity Score (0–100)

Multi-factor composite replacing single `period_screener` rank as the **primary proposal sort key**. Period rank remains available as a sub-factor (`dollar_history`).

#### 5.2.1 Factor weights (Phase 1 initial)

| Factor | Weight | Source (increment) | v1 data |
|--------|--------|--------------------|---------|
| Market regime | 10% | `regime.py` | **EXISTING** |
| Technical setup | 15% | range + Step 3 pass | **EXISTING** |
| Momentum | 10% | 5/10/20d return vs SPY | **NEW** Inc 3 |
| Relative strength | 10% | ticker vs SPY same window | **NEW** Inc 3 |
| Volume | 10% | vs 20d avg volume | **NEW** Inc 3 |
| Volatility | 8% | avg_range_pct band fit | **EXISTING** |
| News sentiment | 12% | `ai_service.py` | **NEW** Inc 6 |
| News significance | 8% | headline count + recency | **NEW** Inc 2 |
| Earnings/events | 5% | Finnhub calendar / flags | **NEW** Inc 2 |
| Fundamental quality | 0% | deferred | — |
| Risk/reward | 12% | expected R:R from plan | **NEW** Inc 4 |
| AI confidence | 0% → 10% | Claude gated | **NEW** Inc 6 |
| Dollar history | 10% | existing $ hit rate | **EXISTING** |

**Rollout:** Increments 3–4 use **deterministic factors only** (news/sentiment weights redistributed to technical + dollar_history until Inc 6).

#### 5.2.2 Composite formula

```text
opportunity_score = round(100 * Σ (weight_i * score_i / 100))
```

Each `score_i` is 0–100. Missing factors: weight renormalized across available factors (document in code comments).

#### 5.2.3 Minimum gates (before scoring)

Same as today plus Phase 1 additions:

| Gate | Rule |
|------|------|
| Step 3 pass | liquidity + swing band |
| Dollar rank gate | ≥40% $ hit, avg net ≥90% goal, ≥2 days |
| Regime | not `block_new_longs` for new proposals |
| Opportunity floor | `opportunity_score ≥ 65` to create proposal |

---

### 5.3 Risk Engine

**Independent module:** `src/investment_agent/risk_engine.py`

#### 5.3.1 Interface

```python
def evaluate_proposal(
    *,
    proposal: TradeProposalPlan,
    portfolio: PortfolioSnapshot,
    market: MarketSnapshot,
    config: RiskConfig,
) -> RiskDecision:
    """Returns APPROVE or REJECT with checks[]. LLM cannot call this."""
```

#### 5.3.2 RiskConfig defaults (Phase 1)

| Rule | Default | Config key |
|------|---------|------------|
| Max risk per trade | **1.0%** of tradable capital | `RISK_MAX_PCT_PER_TRADE` |
| Min risk per trade floor | 0.5% (warning only) | `RISK_MIN_PCT_PER_TRADE` |
| Max position size | `min(liquidity_cap, tradable_cash)` | existing |
| Max portfolio exposure | **100%** long (single strategy, no margin) | `RISK_MAX_EXPOSURE_PCT` |
| Max open positions | **2** (1 primary + 1 optional after win) | `RISK_MAX_OPEN_POSITIONS` |
| Daily loss limit | **2.0%** of tradable capital | `RISK_DAILY_LOSS_LIMIT_PCT` |
| Weekly loss limit | **5.0%** of tradable capital | `RISK_WEEKLY_LOSS_LIMIT_PCT` |
| Max drawdown halt | **10%** from Phase 1 high-water mark | `RISK_MAX_DRAWDOWN_PCT` |
| Mandatory stop | Required on every proposal | existing `STOP_PCT` |
| Kill switch | Manual + auto on drawdown halt | `app_settings.kill_switch` |
| Max trades per day | **2** | enforce `MAX_TRADES_PER_DAY` |
| Min R:R | **1.5 : 1** net of fees | `RISK_MIN_RR` |

#### 5.3.3 RiskDecision output

```json
{
  "verdict": "approved | rejected",
  "headline": "Approved — $75 max risk within 1% cap",
  "checks": [
    {"name": "kill_switch", "ok": true, "blocking": true, "message": "..."},
    {"name": "daily_loss_limit", "ok": true, "blocking": true, "message": "..."},
    {"name": "weekly_loss_limit", "ok": true, "blocking": true, "message": "..."},
    {"name": "max_risk_per_trade", "ok": true, "blocking": true, "message": "..."},
    {"name": "max_open_positions", "ok": true, "blocking": true, "message": "..."},
    {"name": "max_trades_today", "ok": true, "blocking": true, "message": "..."},
    {"name": "regime", "ok": true, "blocking": true, "message": "..."},
    {"name": "mandatory_stop", "ok": true, "blocking": true, "message": "..."},
    {"name": "min_rr", "ok": true, "blocking": true, "message": "..."},
    {"name": "gap_chase", "ok": true, "blocking": true, "message": "..."}
  ],
  "blockers": [],
  "max_risk_dollars": 75.00,
  "recommended_shares": 100
}
```

#### 5.3.4 Migration from `tradability.py`

| Current (`tradability.py`) | Risk Engine |
|----------------------------|-------------|
| Gap/chase filters | `gap_chase` check |
| Day-high room | `reachability` check |
| Dollar history reachability | `dollar_history` check |
| Session range | `session_range` check (caution → blocker if tight + low RR) |
| — | daily/weekly loss, kill switch, max trades |

`tradability.py` becomes a **thin wrapper** calling Risk Engine for backward compatibility during migration.

---

### 5.4 News Service

**Module:** `src/investment_agent/news_service.py`

#### 5.4.1 Provider

- **Primary:** Finnhub `/company-news` (already licensed in product spec)
- **Storage:** `news_headlines` table

```sql
CREATE TABLE news_headlines (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  headline_hash TEXT NOT NULL,
  published_at TEXT NOT NULL,
  headline TEXT NOT NULL,
  summary TEXT,
  source TEXT,
  url TEXT,
  ingested_at TEXT NOT NULL,
  UNIQUE(ticker, headline_hash)
);
CREATE INDEX idx_news_ticker_time ON news_headlines(ticker, published_at);
```

#### 5.4.2 Ingest rules

- Run after quote ingest for **proposal candidates only** (top 50 ranked) + any open positions
- Dedupe: SHA256 normalized headline per ticker
- Retention: 30 days rolling
- Rate limit: respect Finnhub 60/min with existing throttle pattern

#### 5.4.3 Scoring (deterministic v1)

| Signal | Score logic |
|--------|-------------|
| News significance | Headlines in last 24h: 0→20, 1→60, 2+→80+, major keyword boost |
| Earnings/events | Flag if headline matches earnings regex or Finnhub calendar |

Sentiment numeric score deferred to AI Service (Increment 6).

---

### 5.5 AI / Sentiment Service

**Module:** `src/investment_agent/ai_service.py`

#### 5.5.1 Scope (Increment 6 only)

- **Input:** ticker, top 3 headlines, factor scores, trade plan summary
- **Output:** `explanation`, `explanation_short`, `ai_confidence` (0–100), optional `news_sentiment` (0–100)
- **Model:** Claude Sonnet (configurable); **Haiku** for batch/off-hours
- **Gating:** Max **10 proposals/day** sent to Claude; cache by `(ticker, session_date, headline_hash)` for 24h

#### 5.5.2 Hard rules

- Claude **never** sets `risk_verdict` or `human_verdict`
- Claude **never** triggers execution
- On API failure: fall back to rule-based explanation; `ai_confidence = 0`, weight excluded

---

## 6. Strategy Engine (Phase 1)

### 6.1 Entry

Preserve **pullback limit entry** as default Phase 1 entry mode:

| Field | Source |
|-------|--------|
| `limit_buy_price` | `pullback_entry.limit_buy_price()` |
| `limit_sell_price` | Growth Plan net target via `sell_price_for_net_target()` |
| `stop_price` | `STOP_PCT` below fill price |
| Fill deadline | 11:30 ET |
| Overnight | If not closed EOD and human approves hold, monitor transitions queue to `runner` state (existing) |

### 6.2 Position sizing (dynamic)

```text
base_deploy = min(liquidity_cap, tradable_cash)
max_risk_dollars = tradable_cash * RISK_MAX_PCT_PER_TRADE
shares_from_risk = floor(max_risk_dollars / (entry - stop))
shares_from_capital = floor((base_deploy - buy_fee) / entry)
shares = min(shares_from_risk, shares_from_capital)
```

This implements **0.5–1.0% risk per trade** with capital cap.

### 6.3 Exit

| Exit | Rule |
|------|------|
| Target | Limit sell at `limit_sell_price` |
| Stop | `-STOP_PCT` from entry (mandatory) |
| EOD | Alert at 3:45 PM ET; overnight requires explicit human path |
| Weekly loss halt | Risk Engine rejects new proposals |

### 6.4 Constants alignment (fix DEBT D1)

Phase 1 spec **standardizes on code values** until backtest comparison completes:

| Constant | Phase 1 value |
|----------|---------------|
| `STOP_PCT` | **0.75%** |
| `TARGET_PCT` (legacy sim) | **1.50%** |
| Growth Plan daily net | **$150 @ $10K** (unchanged) |

Update docs in Increment 1 README pass — not blocking code.

---

## 7. Human Approval Interface

### 7.1 Trade tab changes

Replace/enhance top pick card with **Proposal Card**:

```text
┌─────────────────────────────────────────────────────────┐
│ NVDA  ·  Opportunity 87/100  ·  PROPOSED              │
├─────────────────────────────────────────────────────────┤
│ Limit buy $XXX  ·  Sell $XXX  ·  Stop $XXX  ·  100 sh  │
│ Max risk $75 (0.75%)  ·  R:R 2.4:1  ·  Cancel 11:30 ET│
├─────────────────────────────────────────────────────────┤
│ Factors: Tech 91 · Mom 94 · News 84 · Regime 81 · ...  │
├─────────────────────────────────────────────────────────┤
│ Risk: ✓ APPROVED — daily loss OK, weekly loss OK        │
├─────────────────────────────────────────────────────────┤
│ Why: [explanation_short]                              │
│ [Expand full explanation]                             │
├─────────────────────────────────────────────────────────┤
│ [ APPROVE ]  [ REJECT ▼ reason required ]               │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Account tab additions

**Capital Builder panel:**

```text
Phase 1: $10,000 → $30,000
Current: $12,450 (41.5% of milestone)
This week: +$320 / ~$1,000 target (soft)
High water: $12,800 · Drawdown: -2.7%
Kill switch: OFF [Activate]
```

### 7.3 Rejection reasons (required enum + optional text)

| Code | Label |
|------|-------|
| `NO_CONVICTION` | Don't agree with setup |
| `NEWS_RISK` | News/event too risky |
| `MARKET_RISK` | Market conditions |
| `SIZE_TOO_LARGE` | Position too big |
| `ALREADY_EXPOSED` | Already have exposure |
| `TIMING` | Bad timing / missed entry |
| `OTHER` | Free text required |

Stored on `trade_proposals.human_rejection_reason`.

---

## 8. API Additions (proposed)

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/proposals/today` | List session proposals |
| GET | `/api/proposals/{id}` | Proposal detail |
| POST | `/api/proposals/generate` | Run screener → proposals (morning) |
| POST | `/api/proposals/{id}/approve` | Human approve |
| POST | `/api/proposals/{id}/reject` | Human reject + reason |
| GET | `/api/risk/status` | Portfolio risk snapshot |
| POST | `/api/risk/kill-switch` | Toggle kill switch |
| GET | `/api/capital-builder/progress` | $10K→$30K + weekly band |

Existing routes **remain** during migration; `trading-day/status` delegates to proposal + risk internally.

---

## 9. Learning Loop (Phase 1 v2)

Every proposal stores factor scores at creation. On close:

```text
proposal_id → entry factors + plan
journal round trip → outcome_net_pnl, holding_hours, overnight flag
nightly job → aggregate:
  - win rate by opportunity_score bucket (65–75, 75–85, 85+)
  - win rate by news_sentiment bucket (when live)
  - avg P&L by regime state
  - rejection reason counts vs later hypothetical outcome (close report)
```

**New learning questions enabled:**

- Does positive news sentiment improve return? (after Inc 6)
- Which factor correlates with wins? (after Inc 7)
- Overnight vs same-day flat performance? (after Inc 8 backtest)

---

## 10. Implementation Increments

Each increment: **one Cursor prompt → PR → tests → your review**.

### Increment 1 — Risk Engine ⭐ first

**Files:** `risk_engine.py`, `tests/test_risk_engine.py`; modify `tradability.py`, `trading_day.py`

**Deliverables:**
- `RiskConfig` defaults as §5.3.2
- Daily/weekly realized loss from journal
- Kill switch in `app_settings`
- Enforce `MAX_TRADES_PER_DAY`
- High-water drawdown tracking

**Acceptance:**
- [ ] Rejects proposal when daily loss ≥ 2%
- [ ] Rejects when weekly loss ≥ 5%
- [ ] Kill switch blocks all new proposals
- [ ] Max 2 open positions enforced
- [ ] All 124 existing tests pass + ≥15 new risk tests

---

### Increment 2 — News Service

**Files:** `news_service.py`, DB migration, `ingest.py` hook

**Acceptance:**
- [ ] Headlines stored with dedupe
- [ ] Top-50 ranked tickers get news on ingest
- [ ] `news_significance` factor computable

---

### Increment 3 — Opportunity Score (deterministic)

**Files:** `opportunity_score.py`, refactor `period_screener.py`

**Acceptance:**
- [ ] Composite 0–100 with regime, technical, momentum, RS, volume, volatility, dollar_history
- [ ] Weights renormalize when factors missing
- [ ] Proposals only for score ≥ 65

---

### Increment 4 — Trade Proposal Service + UI

**Files:** `trade_proposal.py`, DB tables, API routes, dashboard Proposal card

**Acceptance:**
- [ ] Morning generate creates ≤5 proposals sorted by score
- [ ] Human approve/reject persisted with reason
- [ ] Journal BUY accepts optional `proposal_id`
- [ ] Risk re-run on live refresh before approve

---

### Increment 5 — Capital Builder progress UI

**Files:** `finance.py` or `capital_builder.py`, Account tab widget

**Acceptance:**
- [ ] Shows $10K→$30K progress bar
- [ ] Shows weekly net vs ~$1K soft band (no "must trade" messaging)
- [ ] High-water + drawdown visible

---

### Increment 6 — AI Sentiment Service

**Files:** `ai_service.py`, wire into proposals

**Acceptance:**
- [ ] Claude explanation on top proposals only (≤10/day)
- [ ] Cache prevents duplicate calls
- [ ] Failure falls back to rule-based text
- [ ] `ai_confidence` and `news_sentiment` factors live

---

### Increment 7 — Learning v2

**Files:** `learning.py`, nightly aggregation

**Acceptance:**
- [ ] Proposal outcomes linked in learning report
- [ ] Factor bucket stats in Review tab
- [ ] Rejection reasons summarized

---

### Increment 8 — Backtest extensions

**Files:** `backtest.py`

**Acceptance:**
- [ ] Overnight hold mode flag
- [ ] Weekly P&L aggregation
- [ ] Slippage stub (configurable bps)

---

### Increment 9 — Execution design doc only

**Deliverable:** `docs/EXECUTION_SERVICE_DESIGN.md` — IB vs E*TRADE, paper sim, order types. **No code.**

---

### Increment 10 — Paper broker (deferred until Inc 1–7 validated)

**Not authorized in initial Phase 1 batch.**

---

## 11. Explicit Preserve List

Do **not** remove or rewrite in Phase 1:

| Asset | Reason |
|-------|--------|
| `journal.py` FIFO logic | P&L source of truth |
| Ingest pipeline | Production data path |
| Mac EOD / morning / refresh scripts | Operator workflow |
| Watchlist presets | Universe management |
| Pullback entry math | Validated strategy component |
| 124-test baseline | Regression safety |
| Manual E*TRADE execution | Phase 1 broker model |

---

## 12. Non-Goals (Phase 1)

- Interactive Brokers or any broker API orders
- Automated approval or execution
- Cloud deployment / multi-tenant SaaS
- Phase 2 active intraday automation
- Fundamental quality scoring
- Parameter auto-optimization (manual review only)
- Replacing SQLite with Postgres (defer)

---

## 13. Success Criteria (Phase 1 complete)

Phase 1 is **complete** when:

1. Operator can run EOD → morning → generate **Trade Proposals** with Opportunity Score
2. **Risk Engine** blocks unsafe proposals (loss limits, kill switch demonstrated)
3. Human can **approve/reject** with reasons; journal links to proposals
4. **Capital Builder** panel shows $10K→$30K and weekly soft progress
5. News ingested for candidates; sentiment live or gracefully degraded
6. Learning report answers at least **3 factor-correlation questions** from historical proposals
7. All baseline tests pass; ≥40 new tests across increments
8. **No automated broker orders** shipped

Transition to Phase 2 ($30K reached + evidence review) is a **business gate**, not automatic.

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Weekly $1K pressure causes overtrading | UI labels "soft target"; Risk Engine + "no proposal" is valid |
| Scope creep to IB integration | Increment 9 design only; execution stub |
| Claude cost | Gate to top-N; cache; Haiku fallback |
| SQLite migrations | Additive tables only; migration in `db.py` |
| Breaking daily Growth Plan users | Keep daily metrics; add weekly/milestone in parallel |

---

## 15. Review Checklist (for operator)

Before authorizing **Increment 1** Cursor prompt, confirm:

- [ ] $10K→$30K milestone and ~$1K/week soft target approved
- [ ] Risk limits (§5.3.2) approved or adjusted
- [ ] E*TRADE manual execution remains Phase 1 broker
- [ ] Opportunity Score weights (§5.2.1) directionally OK
- [ ] Trade Proposal schema (§5.1) sufficient for journal linkage
- [ ] Increment order (§10) acceptable
- [ ] Explicit non-goals (§12) acceptable

---

## 16. Next Step

When review checklist is approved, authorize:

> **"Implement Increment 1 — Risk Engine"**

Cursor will receive a **single-increment prompt** referencing this spec §5.3 and §10 Increment 1 only.

---

## Document History

| Date | Version | Change |
|------|---------|--------|
| 2026-08-14 | 0.1 | Initial Phase 1 Capital Builder spec |

---

*This document defines requirements only. No implementation code is authorized until increment prompts are explicitly approved.*
