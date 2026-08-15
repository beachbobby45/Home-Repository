# Phase 1B — Market Activity & Confirmation (Spec v0)

> **Status:** Market Activity v0 implemented (Inc 12); Confirmation Inc 13 pending  
> **Assumptions:** [PHASE1B_ASSUMPTIONS_AND_DEFINITIONS.md](./PHASE1B_ASSUMPTIONS_AND_DEFINITIONS.md)

---

## 1. Three layers

```text
Opportunity Engine (EOD)     → ranked #1, #2, #3
Market Activity Engine (AM)    → TRADE / NO TRADE today
Confirmation Engine (AM)       → which names confirm
Risk Engine                    → approve / reject size
Human                          → execute E*TRADE + journal
```

---

## 2. Market Activity Score (0–100)

### Weights (hypothesis — validate via learning)

| Component | Weight | Free-tier v0 |
|-----------|-------:|--------------|
| Market direction | 20% | SPY, QQQ, DIA vs open |
| Market volume | 15% | Snapshot proxy vs 20d avg |
| Market breadth | 15% | **n/a** — renormalize |
| Volatility | 10% | VIX level/change |
| Momentum | 15% | Index 5–20d from daily bars |
| Sector participation | 10% | Sector ETF RS vs SPY |
| VWAP/trend confirmation | 10% | **n/a** — open+time proxy |
| News/catalysts | 5% | Macro headline flag |

### Bands → authorization

| Score | Label | Action |
|------:|-------|--------|
| ≥90 | Exceptional | Trade; multiple names if confirm |
| 75–89 | Above average | Trade; #1 primary |
| 60–74 | Average | **NO TRADE** |
| 40–59 | Below average | **NO TRADE** |
| <40 | Negative | **NO TRADE**; exit if holding |

**Bull gate:** SPY 20-day return > 0 required for any TRADE band.

---

## 3. Candidate Confirmation Score (0–100)

Per ranked ticker at same timestamps as market activity.

| Component | Weight |
|-----------|-------:|
| Relative volume | 20% |
| Volume acceleration | 15% |
| Price momentum | 15% |
| Relative strength | 15% |
| VWAP | 10% |
| Breakout/technical | 10% |
| Sector confirmation | 5% |
| News/catalyst | 10% |

**Rule:** Confirmation never overrides NO TRADE day.

**Pass threshold (hypothesis):** ≥75 with day ≥ Above average.

---

## 4. Intraday flip

Two consecutive refreshes below Above Average **or** single refresh in Negative → **NO TRADE** + **EXIT MARKET** if position open.

---

## 5. Modules (planned)

- `market_activity.py` (Inc 12)
- `confirmation.py` (Inc 13)
- `quote_snapshots` table (Inc 11)
