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
