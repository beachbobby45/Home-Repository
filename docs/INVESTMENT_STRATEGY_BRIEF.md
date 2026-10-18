# Intraday Ranked-Pick Capital Builder  
## Strategy Brief for External Review

| Field | Detail |
|-------|--------|
| **Document type** | Investment strategy & operating plan (for diligence) |
| **Prepared** | October 17, 2026 |
| **Last updated** | October 18, 2026 (**post–PDT rule change refresh**) |
| **Operator** | Tony (individual account; self-directed) |
| **Status** | Published for external diligence; pre-live / systems build; historical simulation complete for a limited window |
| **Canonical copy** | https://github.com/beachbobby45/Home-Repository/blob/main/docs/INVESTMENT_STRATEGY_BRIEF.md |
| **Not** | A solicitation, prospectus, or guarantee of returns |

> **Important:** This document is for informational and diligence purposes. It is **not** financial, legal, or tax advice. Past simulated or live performance does **not** predict future results. Equity trading can result in **partial or total loss** of capital. Broker and FINRA margin rules still apply. Any third party considering involvement should perform independent due diligence and consult licensed advisors as appropriate.

---

## 0. Regulatory update (October 2026) — PDT replaced

### Confirmed: Pattern Day Trader (PDT) framework replaced

**FINRA** replaced the old day-trading margin / PDT rules (including the **4 trades in 5 days** count test and the **$25,000** PDT equity minimum) with **intraday margin standards**.

| Source | What it says |
|--------|----------------|
| [FINRA Regulatory Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10) | Published Apr 20, 2026; **effective June 4, 2026**. Adopts new intraday margin standards that **replace in their entirety** the outdated day trading margin requirements, including PDT designation by trade count and the **$25,000** PDT minimum equity. Members may phase in through **Oct 20, 2027**. |
| [FINRA investor explainer](https://www.finra.org/investors/insights/intraday-margin-requirements) | No $25,000 minimum for day trading; no PDT designation by counting trades; firms monitor equity vs open exposure; repeated intraday margin deficits can lead to up to a **90-day** restriction. |
| [Robinhood — Day trading](https://robinhood.com/us/en/support/articles/day-trading/) | Starting **June 4, 2026**: **no more day trade restrictions or day trade calls** on Robinhood margin accounts; PDT flags removed; **no $25,000** portfolio minimum to day trade; **$2,000 margin minimum equity** still applies if using margin. |

**Operator policy after this change:** trade **up to 5 sessions per week** (one primary round-trip per day when a setup fills). The old **3 trades/week under $25k** regulatory cap is **no longer the binding constraint**.

### Confirmed: settlement / settled funds (cash vs margin)

| Source | What it says |
|--------|----------------|
| [Robinhood — Settlement and buying power](https://robinhood.com/us/en/support/articles/settlement-and-buying-power/) | Stocks and options take **1 trading day (T+1)** to settle. **Margin accounts** can trade instantly with funds from unsettled stock/option sales. **Cash accounts can’t trade with unsettled funds** — wait **1 trading day** to trade with proceeds from equity/options sales. |
| [Robinhood — T+1 settlements](https://robinhood.com/us/en/support/articles/T1-settlements/) | Industry T+1 since May 28, 2024: sale proceeds settle **one trading day** after trade date. |
| [Robinhood — Investing accounts](https://robinhood.com/us/en/support/articles/robinhood-accounts/) | Cash: unlimited day trades historically, but **no trading with unsettled** sale proceeds. Margin: can use unsettled sale proceeds. |

**Practical meaning for this plan (unlevered):**

1. Prefer **cash account**, **or** margin enabled with **borrow = $0** (never use leverage).  
2. Same-day buy → sell is fine when the **buy** is funded with **settled** cash.  
3. After a same-day sale, in a **cash** account those proceeds are available for a **new** purchase on the **next trading day** (overnight / T+1)—matching “funds settle before we redeploy.”  
4. Do **not** rely on borrowing or on spending unsettled proceeds if the goal is an unlevered $5k experiment.

**Caution:** Some Robinhood pages may still show legacy PDT language in places; the dedicated [Day trading](https://robinhood.com/us/en/support/articles/day-trading/) article above is the current PDT-replacement statement. Operator should also confirm in-app: **Settings → Investing → Day trade settings**.

---

## 1. Executive summary

### What this is
A **rules-based, same-day long-only** trading program that:

1. Ranks liquid U.S. equities using a local research stack (screener, dollar-goal fit, market activity, confirmation).  
2. Selects primarily the **#1 ranked name** each session.  
3. Enters with a **pullback limit buy**, exits at a **dollar profit target** or **stop**, with an **11:30 ET** entry deadline.  
4. Trades **up to 5 weekdays per week** when a setup fills (post–PDT rules); **one name per day**; redeploy only with **settled** buying power (cash / unlevered).  
5. Funds capital in **staged $5,000 deposits** only after each ~30-session cycle shows profit.  
6. Executes via **Robinhood** as the ledger of record, with a local always-on worker for travel-safe **broker-side** target/stop orders—not discretionary “AI guessing” each minute.

### What this is not
- Not a hedge fund, pooled vehicle, or managed account offering.  
- Not high-frequency market making.  
- Not a promise of ~$450 every week or of compounding to large wealth on a fixed schedule.  
- Not leveraged / borrowed buying power (operator policy).  
- Not fully unattended AI discretion; automation is **rule-bound** with kill switches and staged go-lives.

### Ask of a reviewer
Judge whether the **edge hypothesis**, **risk controls**, **capital ladder**, and **evidence quality** are coherent enough to justify the operator deploying **up to $20,000** of personal capital over ~4–6 months under the rules below—and optionally whether a third party would want any economic participation (separate legal structure required if so; none is defined here).

---

## 2. Investment thesis

**Hypothesis:** A systematically ranked “top pick” with a pullback entry and a modest daily dollar target can produce positive expectancy over time—even on many days the system’s own “market activity” gate would have said “no trade”—provided fills are proven on intraday data and capital is only redeployed when **settled**.

**Supporting observations (historical simulation only):**

| Window | Rules | Result (simulated) |
|--------|--------|---------------------|
| 30 sessions | $10k deploy, ignore day-gate, 5-minute fill proof | ≈ **+$1,271** (**+12.7%**) |
| 60 sessions | $10k compound path, same | ≈ **+$1,968** (**+19.7%**) |
| 60 sessions | **$5k** fixed deploy, trade every fill day (≤5/week capable) | ≈ **+$933** (**+18.7%**) |
| 60 sessions | $5k with old **≤3/week PDT cap** (superseded) | ≈ **+$951** (**+19.0%**) — similar; cap barely changed totals |

Source: operator’s local SQLite history + Yahoo 5-minute bars; scripted counterfactual on ranked #1. **Not** live broker fills.

**Why a reviewer might care:** Edge, if real, is process + selectivity (many no-fills) + asymmetric target vs stop—not “win every day.” Weekly $450 (3 × $150) remains a **design goal**, not a historical minimum.

**Why a reviewer might reject it:** Short sample (~60 trading days), name concentration, counterfactual ignored the NO-TRADE gate, live RH automation unproven, and **intraday margin** risk if the account ever uses borrowed buying power.

---

## 3. Scope

### In scope
| Area | Description |
|------|-------------|
| Universe | Liquid U.S. equities from the operator’s watchlist / screener |
| Direction | Long only; flat by end of day in normal operation |
| Sizing | Growth Plan pullback sizing; start **$5,000** book |
| Frequency | **Up to 5** trading sessions/week when filled (one round-trip/day) |
| Settlement | **Cash / unlevered:** redeploy with **settled** funds (T+1 after a sale) |
| Selection | Default **#1 only** (`single_top1`); dual #1+#2 only after a future study |
| Broker | Robinhood; RH = source of truth for cash/P&L |
| Software | Local Mac dashboard + LaunchAgent worker; Cursor for research/oversight |
| Capital plan | Four × $5k deposits → **$20k invested**, gated on cycle profit |
| Horizon (plan) | Cycle 1 target start **~Nov 2, 2026**; ladder through **~Apr 2027** |

### Out of scope (near term)
- Short selling, options, crypto, **borrowed margin / leverage**  
- Pooling outside capital without a separate legal entity  
- Splitting capital across #1 and #2 until backtested  
- Guaranteed weekly income  

---

## 4. Strategy mechanics

### 4.1 Daily process
1. **Morning prep** — data, rank, market activity, confirmation on #1.  
2. **Arm plan** — ticker, limit buy, target, stop, shares; confirm **settled** buying power ≥ deploy.  
3. **Entry** — limit buy; cancel if not filled by **11:30 ET**.  
4. **Exit** — resting **target** and **stop** at the broker after fill.  
5. **EOD / next morning** — RH sync; sale proceeds settle **T+1** in cash mode before next deploy.

### 4.2 Profit target model (Growth Plan)
At ~**$10,000** notional, design daily net ≈ **$150** per clean target hit.  
Weekly design ≈ **3 × $150 = $450** (quality wins, not five mandatory wins).  
At **$5,000**, aiming for ~$150 still requires a larger % move → fewer full targets historically.  
At **$25,000** tier, internal design daily/weekly rises (on the order of **~$350 / ~$1,050**).

### 4.3 Risk per trade
- Plan stop from entry; same 5m bar stop+target → **stop** (conservative in sims).  
- Kill switch pauses new arms; protective exits remain.  
- One name/day under default mode.  
- **No borrowed funds** — loss capped near cash at risk (still can lose most/all of trading cash).

### 4.4 Frequency & settlement (binding constraints)

| Constraint | Rule |
|------------|------|
| Sessions/week | Up to **5** (Mon–Fri) when a setup fills |
| Names/day | **1** (`single_top1`) |
| Settled cash | Required before arming a buy in cash / unlevered mode |
| After a same-day sale | Next deploy on **next trading day** once proceeds settle (T+1) |
| Leverage | **Off** — do not borrow; avoid intraday margin deficit path |

---

## 5. Capital plan & proposed outcomes (revised — 5 sessions/week capable)

Assumptions for the ladder sketch:

- Historical block returns use the **all-fill** (no 3/week cap) $5k simulation for Cycle 1 and $10k-path nets for Cycle 2.  
- Cycles 3–4 **extrapolate** average cycle return — not guaranteed.  
- Deposits only if prior cycle profit &gt; 0.  
- Dates = trading-day calendar from **Mon Nov 2, 2026**.

### 5.1 Funding ladder

| Stage | Approx. date | Operator cash in | Account (sketch) | Growth on cash invested |
|-------|--------------|------------------|------------------|-------------------------|
| Start | Mon **Nov 2, 2026** | $5,000 | $5,000 | 0% |
| End cycle 1 | Mon **Dec 14, 2026** | $5,000 | **~$5,422** | **~+8.4%** |
| Deposit #2 | Dec 14, 2026 | $10,000 | ~$10,422 | ~+4.2% |
| End cycle 2 | Thu **Jan 28, 2027** | $10,000 | **~$11,756** | **~+17.6%** |
| Deposit #3 | Jan 28, 2027 | $15,000 | ~$16,756 | ~+11.7% |
| End cycle 3† | Fri **Mar 12, 2027** | $15,000 | **~$18,536** | **~+23.6%** |
| Deposit #4 ($20k in)† | Mar 12, 2027 | $20,000 | ~$23,536 | ~+17.7% |
| End cycle 4† | Mon **Apr 26, 2027** | $20,000 | **~$26,036** | **~+30.2%** |

†Cycles 3–4 extrapolated at ~**10.6%** per 30-session block (average of observed Cycle 1 & 2).  
**Conservative** extrapolation (~8.4%/block): end Cycle 4 ≈ **$25,128** (~**+25.6%** on $20k invested).

### 5.2 vs prior (PDT-capped) ladder
Removing the 3/week cap does **not** radically change the sketch: many days never filled anyway. End Cycle 4 base case moves from ~**$25.9k / +29%** (old PDT-capped path) to ~**$26.0k / +30%** (all-fill path)—same order of magnitude. The strategic win is **operational**: no need to skip valid Monday–Friday setups solely for an obsolete PDT count.

### 5.3 Full-year 2027 sketch (proposed, not guaranteed)

| Period | Mode | Illustrative account band |
|--------|------|---------------------------|
| Nov 2026 – Apr 2027 | Up to 5 sessions/week; ladder to $20k in | → **~$25–26k** |
| May – Dec 2027 | Same frequency; #1 only; scale with equity | **~$32–50k** planning band (conservative→base) |

### 5.4 Cycle 1 success criteria
- Zero freeriding / unsettled-cash violations (cash mode)  
- No unprotected overnight longs from tooling failure  
- RH vs dashboard cash match within **$0.01** after sync  
- Cycle P&L **≥ $0** before Deposit #2  
- Operator written go/no-go  

---

## 6. Evidence quality

| Evidence | Strength | Caveat |
|----------|----------|--------|
| 60-session 5m fill-path on #1 | Medium for a personal experiment | One window; Yahoo ≠ RH fills |
| $5k all-fill path ≈ +18.7% / 60d | Useful for under-$25k planning | Not a forecast |
| Weekly ≥$450 as a floor | **Weak** | Rare even with more trade slots |
| Live automated RH execution | **Not yet proven** | Build in progress |
| Ignoring NO-TRADE gate in backtest | Material | Live should prefer day-gate unless overridden |

---

## 7. Risk factors

### Market & strategy
- Loss of capital; stop clusters; regime change; name concentration; ~50% no-fill days in sample.  

### Regulatory & broker (post-PDT)
- **Intraday margin deficits** if margin/borrow is used — can lead to restrictions (see FINRA/RH sources in §0).  
- **Cash freeriding / good-faith violations** if trading on unsettled proceeds.  
- Broker house rules may be stricter than FINRA minimums.  

### Operational
- Automation/dashboard outages; data lag; key-person risk — mitigated by broker-resting exits + kill switch.  

### Leverage (explicitly rejected)
- Borrowing can turn a $5k experiment into losses **beyond** $5k; **not allowed** under this plan.

---

## 8. Governance & controls

| Control | Intent |
|---------|--------|
| Robinhood as ledger | True cash/P&L |
| Dashboard as mirror | Ops/audit only |
| Settled-cash check before arm | Prevent freeriding |
| Weekly session tracker (ops) | Cap **5** filled day trades/week by policy |
| Kill switch | Halt new risk |
| Cycle deposit gate | No +$5k after a losing cycle |
| Unlevered policy | No borrowed buying power |
| Default `#1` only | Avoid untested dual-name complexity |

Technical plan: `docs/ROBINHOOD_AUTOMATION_PLAN.md`.

---

## 9. Use of proceeds

| Tranche | Amount | Purpose |
|---------|--------|---------|
| 1–4 | $5,000 each | Trading capital only; next tranche only if prior cycle profitable → **$20,000** invested |

---

## 10. Alternatives

1. Cash / do nothing  
2. Buy-and-hold index ETF  
3. Paper-trade 60+ sessions first  
4. Live $5k only, no further deposits  
5. Margin with borrow (rejected here)

---

## 11. Diligence checklist

- [ ] I understand cited returns are mostly **simulated**.  
- [ ] I understand **PDT $25k / 3-trade rules are replaced** (FINRA/RH, Jun 2026) but **settlement and intraday margin** still matter.  
- [ ] I understand this plan is **unlevered** and uses **T+1 settled** funds in cash mode.  
- [ ] I understand **$450/week is a design target**, not a historical minimum.  
- [ ] I understand **total loss of trading capital is possible**.  
- [ ] I have read §0 (sources) and §7 (risks).  

---

## 12. Document control & contacts

| Item | Value |
|------|--------|
| **Final document** | https://github.com/beachbobby45/Home-Repository/blob/main/docs/INVESTMENT_STRATEGY_BRIEF.md |
| **Raw markdown** | https://raw.githubusercontent.com/beachbobby45/Home-Repository/main/docs/INVESTMENT_STRATEGY_BRIEF.md |
| FINRA Notice 26-10 | https://www.finra.org/rules-guidance/notices/26-10 |
| FINRA intraday margin explainer | https://www.finra.org/investors/insights/intraday-margin-requirements |
| Robinhood day trading | https://robinhood.com/us/en/support/articles/day-trading/ |
| Robinhood settlement | https://robinhood.com/us/en/support/articles/settlement-and-buying-power/ |
| Related technical plan | [`docs/ROBINHOOD_AUTOMATION_PLAN.md`](https://github.com/beachbobby45/Home-Repository/blob/main/docs/ROBINHOOD_AUTOMATION_PLAN.md) |
| Operator | Tony — self-directed retail account |
| Next milestone | RH connectivity; settled-cash arm checks; Cycle 1 ~Nov 2, 2026 |

---

## 13. One-page verdict frame

| Question | Reading of *this* plan |
|----------|-------------------------|
| Clear strategy? | **Yes** — #1, pullback, target/stop, ≤5 sessions/week, settled cash, staged capital. |
| Empirical support? | **Limited but real** — ~60 sessions positive under 5m rules. |
| PDT still blocking 3/week? | **No** (as of Jun 4, 2026 per FINRA/RH) — settlement is the pacing item. |
| 2027 outcomes guaranteed? | **No**. |
| Ready for outside passive investors? | **Not as presented**. |
| Reasonable personal $5k→$20k experiment? | **Possibly**, if unlevered, cycle-gated, and loss-tolerant. |

---

*End of strategy brief. Simulated figures from Oct 2026 analysis runs; post-PDT refresh Oct 18, 2026.*
