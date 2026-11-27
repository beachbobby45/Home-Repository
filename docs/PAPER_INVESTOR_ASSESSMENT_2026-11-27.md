# Paper investor assessment — 2026-11-27

> **Verdict:** **YES — provisional**  
> **As of:** Fri Nov 27, 2026 18:39 ET  
> **Source:** `data/agent.db` via `scripts/paper_investor_assessment.py`  
> **Books:** `gate_approved` (primary), `all_signals` (shadow)  
> **Basis:** $5,000 paper · equity now **$5,186.74** (**+$186.74 / +3.73%**)

Interactive briefing: Cursor canvas “Paper Investor Assessment — Nov 27 2026”.

---

## Executive answer

| Question | Answer |
|----------|--------|
| Does the model work? | **Yes, provisionally** — net positive primary book, positive expectancy/fill, gate improved vs shadow |
| Why? | See §Why it works |
| Why not “proven”? | Only **4** primary fills; paper ≠ live; soft-tape regime dominated sample |
| What to update? | Planning rates only (wins/week + loss rate). **No** entry/stop/target changes yet |

---

## Headline facts (30d = same fills as 60d)

### Primary `gate_approved`
- **4 fills** on 4 days: **3 wins / 1 loss** · win rate on fills **75%**
- Net **+$186.74** · expectancy/fill **+$46.69** · expectancy/session-row **+$6.22** (30d)
- Avg win **$75.13** (~**1.503%** of $5k) · avg loss **−$38.64** · win/loss magnitude **~1.94×**
- Non-fills (30d): gate_blocked **12**, no_fill **2**, propose_failed **10**, other_flat **2**

| Date | Ticker | Net | Scenario |
|------|--------|----:|----------|
| 2026-11-02 | TYL | +$75.00 | exit_target_same_bar_as_fill |
| 2026-11-13 | TTEK | +$75.40 | exit_target |
| 2026-11-16 | SWK | +$74.98 | exit_target_same_bar_as_fill |
| 2026-11-17 | SWK | −$38.64 | exit_stop_same_bar_as_fill |

### Shadow `all_signals`
- **5 fills**: 3W / 2L · **60%** win rate · net **+$142.31** · expectancy/fill **+$28.46**
- Extra activity primary skipped: GPN +73.44; FDS −35.85; HUM −36.63; SNPS +68.75; TGT +72.60
- **Primary beat shadow by +$44.43** in this window

### Market activity
| Window | Allow | Block | Score avg (min–max) | Bands |
|--------|------:|------:|---------------------|-------|
| 30d | 13 | 17 | 46.5 (27–63) | below_avg 20 · avg 2 · neg 8 |
| 60d | 17 | 43 | 48.2 (27–63) | below_avg 50 · avg 2 · neg 8 |

---

## Why it works (provisional)

1. **Positive expectancy** on the risked fills (+$46.69/fill), not just one lucky week.
2. **Designed win size held** — avg win ≈ 1.50% of $5k basis (matches Growth Plan / Nov-pace sizing).
3. **Asymmetric outcomes** — average winner roughly **1.94×** average loser.
4. **Gate is real and helpful here** — 17/30 days blocked; primary still finished ahead of ungated shadow (shadow took two stops primary avoided).
5. **60d cross-check** shows the same 4 fills / same net — no earlier primary drawdown hiding in this DB window.

## Why it is not yet proven

1. **n = 4 primary fills** — directional, not statistical.
2. **Paper bars** — not Robinhood queue/slippage.
3. **Frequency risk** — measured **0.70 wins/week** over 30d; **0.35**/week over 60d (October had no primary fills). Target 1’s unbroken 1.0/week was optimistic.
4. **Losses exist** — 25% of fills were stops; “no loss” projection sheets are invalid going forward.

---

## Plan vs measured (update these; not the trade rules)

| Assumption | Plan | Measured 30d | Update |
|------------|------|--------------|--------|
| Wins/week | 1.0 | **0.70** | Yes — use 0.70 until Dec sample |
| Win % of $5k | 1.504% | **1.503%** | Keep |
| Loss rate on fills | 0% | **25% (1/4)** | Yes — include in projections |
| 30d naive plan net | ~$322 | Actual **$186.74** | Gap = fewer wins + one stop |
| Entry/stop/target | — | — | **No change** (sample too small) |

---

## Investor-safe claim (approved language)

> In a ~30-day paper window on a $5,000 gated book, the system produced **+$186.74 (+3.7%)** across **4 fills (3 winners / 1 stop)**, with **positive expectancy per fill** and a day gate that **blocked 17 of 30 sessions** while **outperforming an ungated shadow book**. Sample size is small; **December paper is required before live capital**.

---

## Next evidence bar

- Continue paper through **December 2026**
- Re-run `python3 scripts/paper_investor_assessment.py` after month-end
- Raise confidence only if fill count grows and expectancy stays positive — not by loosening the gate without a blocked-day P&L study
