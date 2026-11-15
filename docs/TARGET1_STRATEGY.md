# Target 1 strategy (locked planning baseline)

> **Status:** Saved 2026-11-15 — evaluate against **November + December 2026** paper results  
> **Owner:** Tony + Cursor agent  
> **Purpose:** Short-term lifestyle gate + path check before Robinhood full automation / seed funding  
> **Related:** `docs/ROBINHOOD_EOD_FLATTEN_AND_GOLIVE.md`, Nov-pace projection canvases

---

## 1. Goals

| Horizon | Goal | Definition |
|---------|------|------------|
| **Target 1 (short-term)** | Lifestyle production | **$10,500 net / month** after **25% federal** tax reserve (FL state = $0): pull **$8,500**, retain **$2,000** in principal |
| **Long-term** | Principal ceiling | **$5,000,000** account value — **not** reachable on +$2k/mo retain alone (see §5) |

RH trading fees treated as ≈ $0 (model ~$5/win dust only).

---

## 2. Starting point & win model

| Input | Value |
|-------|------:|
| Planning start | **Jan 1, 2027** open = **$15,000** (first compound week Mon **Jan 4, 2027**) |
| Observed Nov 2026 paper pace (TYL + TTEK) | **1 win / week**, avg **$75.20** net on $5k → **1.504% of equity per win** |
| Compounding during build-up | Wins compound; **no losses**, **no $8.5k pulls** until Target 1 principal is reached |
| Effective weekly rates used | **1.0** win/wk → 1.504%/wk · **1.4** → 2.112%/wk · **1.7** → 2.570%/wk |

---

## 3. Principal required for $10.5k net / month (25% federal)

| Income rule after arrival | Principal (Target 1 book size) | Notes |
|---------------------------|-------------------------------:|-------|
| **A. ~1 win / week continues** | **~$209,931** | Aligns with Nov sample frequency |
| **B. Only 1 win / month must fund $10.5k** | **~$931,294** | Conservative “single monthly winner” sizing — **primary Target 1 number used in month-by-month table** |

Gross needed ≈ **$14.0k** before 25% tax so **$10.5k** remains after tax.

---

## 4. Month-by-month path — $15k → ~$931k (Target 1 primary)

Opening **$15,000** on Jan 1, 2027. Table stops when each pace first reaches **≥ ~$931k**.

| Pace | Hits ~$931k | Also crosses ~$210k (weekly lifestyle) |
|------|-------------|----------------------------------------|
| **1.0** win/wk | **Apr 2032** (~W277) | May 2030 |
| **1.4** wins/wk | **Oct 2030** (~W198) | Jun 2029 |
| **1.7** wins/wk | **Feb 2030** (~W163) | Dec 2028 |

### Checkpoint snapshot (ending principal)

| Month | 1.0 /wk | 1.4 /wk | 1.7 /wk |
|-------|--------:|--------:|--------:|
| Dec 2027 | $32,600 | $44,470 | $56,131 |
| Dec 2028 | $70,850 | $131,838 | $210,046 |
| Jun 2029 | $104,448 | $227,000 | $406,321 |
| Dec 2029 | $153,980 | $390,853 | $786,004 |
| Hit | Apr 2032 ~$937k | Oct 2030 ~$940k | Feb 2030 ~$939k |

Full month-by-month series was generated in-session (canvas: “$15k → $931k Month-by-Month”). Recompute with the same rules if numbers need refresh after Nov–Dec measurement.

### What must be true for Dec 2028 / Jun 2029 (weekly ~$210k path)

If the deadline is lifestyle at **~$210k** (not $931k):

| Deadline | Seed @ Nov 1.0/wk | Or from $15k seed |
|----------|------------------:|-------------------|
| Dec 2028 | start ≈ **$45k** | ≈ **1.7** wins/wk sustained |
| Jun 2029 | start ≈ **$30k** | ≈ **1.4** wins/wk sustained |

---

## 5. After Target 1 — conflict with $5M

Once the **$8.5k pull / $2k retain** regime is on, book growth is capped at **+$2,000 / month** even if trading could earn more.

| From | To $5M at +$2k/mo |
|------|-------------------|
| ~$931k | **~2,035 months (~170 years)** |
| ~$210k | even longer |

**Implication:** Target 1 lifestyle and the $5M ceiling are compatible only if retain rate rises later, pulls pause some months, or production above $10.5k is left in the book.

---

## 6. Nov–Dec 2026 evaluation checklist

Use paper (and any live journal) results to accept, revise, or reject Target 1 assumptions:

- [ ] **Win frequency:** measured wins / trading week (vs 1.0 / 1.4 / 1.7 planning bands)
- [ ] **Win size:** average net % of deployed principal per win (vs **1.504%**)
- [ ] **Loss / stop rate:** weeks with stops or scratches (Target 1 sheets assumed **zero**)
- [ ] **No-fill / gated weeks:** share of weeks with $0 (expected some; sheets assumed a win every week at the stated pace)
- [ ] **Net after fees:** confirm RH/friction still negligible vs model
- [ ] **Which Target 1 book size to keep:** ~$210k (weekly income) vs ~$931k (single monthly win)

### Decision guide (after Dec 2026 close)

| If Nov–Dec shows… | Then |
|-------------------|------|
| ≈ 1.0 win/wk @ ~1.5% net, few stops | Target 1 **1.0** column is the baseline plan |
| Sustained ≥ 1.4 wins/wk with acceptable stops | Faster columns become plausible; revisit Dec 2028 / Jun 2029 |
| << 1 win/wk or stops dominate | Do **not** treat $931k / $5M dates as plan — revise rate or seed |
| Clear edge but thin sample | Extend paper / small live; keep Target 1 as hypothesis |

---

## 7. Explicitly not claimed

- Not a guarantee of returns  
- Not gate-ON multi-year backtest proof  
- Not authorization to auto-trade; RH MCP go-live remains after Tony funds + grants access (`ROBINHOOD_EOD_FLATTEN_AND_GOLIVE.md`)

---

## 8. Decision log

| Date (ET) | Decision |
|-----------|----------|
| 2026-11-15 | Lock Target 1: $15k Jan 2027 planning start; $8.5k+$2k=$10.5k net/mo @ 25% fed; primary book size ~$931k with 1.0/1.4/1.7 win/wk paths; defer accept/reject until Nov+Dec 2026 paper evaluation. |
