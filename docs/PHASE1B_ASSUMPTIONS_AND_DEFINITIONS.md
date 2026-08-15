# Phase 1B — Assumptions & Definitions

> **Status:** Approved for implementation (Inc 9)  
> **Baseline:** `v0.8-pre-phase1b`  
> **Supersedes:** Fixed ~$1K/week band and linear +$50/$5K daily ladder for Capital Builder UI

---

## 1. Weekly production objective

At **$10,000** principal:

- **Weekly guidance** = **3 × $150 = $450** net realized growth
- **Not** three calendar days — **three successful production opportunities**
- Wins may occur on **one day**, **two days**, or **spread across the week**

When weekly guidance is met → **default stop** (no new trades).

**Exceptional override (max 1/week):** all Market Activity + Confirmation signals GO → one additional trade targeting **one daily production unit** at current tier.

---

## 2. Split-lot tier model

Virtual lots (accounting buckets — one E*TRADE account).

| Lot size | Daily rate per lot |
|---------:|-------------------:|
| $10,000 | $150 |
| $15,000 | $200 |
| $20,000 | $250 |
| $25,000 | $300 |
| $30,000 | $350 |

Formula: `$150 + ($lot − $10,000) / $5,000 × $50`

### Account structure by equity tier

| Equity ≥ | Structure | Daily total | Weekly (3×) |
|---------:|-----------|------------:|------------:|
| $10,000 | 1× $10K | $150 | $450 |
| $15,000 | 1× $15K | $200 | $600 |
| $20,000 | $10K + $10K | $300 | $900 |
| $25,000 | $10K + $15K | $350 | $1,050 |
| $30,000 | $15K + $15K | $400 | $1,200 |
| $35,000 | $15K + $20K | $450 | $1,350 |
| $40,000 | $20K + $20K | $500 | $1,500 |
| $45,000 | $20K + $25K | $550 | $1,650 |
| $50,000 | $25K + $25K | $600 | $1,800 |
| $55,000 | $25K + $30K | $650 | $1,950 |
| $60,000 | $30K + $30K | $700 | $2,100 |

**Tier selection:** highest threshold ≤ current equity (step function — no interpolation).

**Phase 1 sizing:** one trade targets **full daily total** for the tier (not separate E*TRADE orders per lot).

---

## 3. Day authorization (strict)

| Market Activity band | New entries |
|---------------------|-------------|
| Exceptional (≥90) | Yes — #1–#3 if each confirms |
| Above average (≥75) | Yes — #1 primary |
| Average and below (<75) | **NO TRADE** |
| Not bull (SPY 20d ≤ 0 + weak session) | **NO TRADE** |

Ranked list **always visible**; red **DO NOT TRADE TODAY** banner when blocked.

---

## 4. Evaluation schedule (ET)

| Time | Purpose |
|------|---------|
| Pre-open | Preliminary market read |
| 9:30 | Open — match/improve pre-market |
| 9:45 | Authoritative day type |
| Each refresh | Detect flip → exit alert if holding |

---

## 5. Exit policy

When day flips to **NO TRADE** while holding a position:

- Dashboard: **sell at market** to exit
- Human executes in E*TRADE; journal the SELL

Every BUY retains a **stop loss** (measured loss cap).

---

## 6. Opportunity counting (journal)

| Event | Counts toward weekly 3× |
|-------|-------------------------|
| Closed round trip, net ≥ 67% of daily target | **Yes — 1 opportunity** |
| Stopped out | **Yes — 1 opportunity** |
| Limit not filled | **No** |
| Intraday exit on day flip | **Yes — 1 opportunity** |

Weekly progress = **sum of realized net** vs tier weekly guidance.

---

## 7. Free tier (v0)

Breadth and VWAP marked **n/a**; weights renormalize. See [PHASE1B_MARKET_ACTIVITY.md](./PHASE1B_MARKET_ACTIVITY.md).

---

## 8. Implementation increments

| Inc | Deliverable |
|-----|-------------|
| 9 | This doc + market activity spec |
| 10 | Split-lot tier in `finance.py` + Capital Builder UI |
| 11–18 | Snapshots, engines, dashboard banner, learning |
