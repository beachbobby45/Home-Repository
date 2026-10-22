# Intraday Ranked-Pick Capital Builder  
## Strategy Brief for External Review

| Field | Detail |
|-------|--------|
| **Document type** | Investment strategy & operating plan (for diligence) |
| **Prepared** | October 17, 2026 |
| **Last updated** | October 18, 2026 (**post–PDT + evidence-gate refresh**) |
| **Operator** | Tony (individual account; self-directed) |
| **Status** | Published for external diligence; **paper-first** before live capital; historical simulation is exploratory only |
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
5. **Paper-trades 40–60 sessions** (Oct–Nov 2026) with pre-registered pass/fail **before** any live deposit; proposed **RH CASH live $5k on 2026-12-01**, then **+$5k every ~30 trading sessions** to **$20k invested** — dates are earliest sketches; deposits stay **evidence-gated (never automatic)**.  
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
Robinhood has **no stock paper account** (Simulated Returns = options scenarios only), so forward paper stays on the **internal ledger**; written go checklist: `docs/PAPER_GO_CHECKLIST.md`.

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
| Capital plan | Paper first → live **$5k** → scale to **$20k** only under §5 evidence gates |
| Horizon (plan) | P0/P1 immediately; live $5k only after paper pass |

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

## 5. Evidence-gated capital plan (revised after external diligence)

**External review takeaway (accepted):** treating “one profitable ~30-session cycle → next $5k” as *proof of edge* is weak — a no-edge process can still print a green cycle by luck. Structure stays: **~$5k every ~30 sessions on the calendar**, but unlocks require **evidence + written go** (never automatic).

### 5.0 Binding sequence (do in order)

| Phase | What | Capital at risk | Gate to proceed |
|-------|------|-----------------|-----------------|
| **P0 — Controls** | Re-run history with (a) **gate ON**, (b) **gate OFF / all signals**, (c) **random-pick control** using identical entry/exit/fees | $0 | Scripts complete; results logged in brief appendix |
| **P1 — Forward paper** | **40–60 sessions**, up to 5 days/week; **log every signal** + gate verdict; run two arms from same log: *all signals* vs *gate-approved only* | $0 | Pre-registered pass criteria in §5.2 |
| **P2 — Live $5k** | First deposit only after P1 pass; **CASH / unlevered**; settled cash; hard drawdown stop; earliest sketch **2026-12-01** | **$5,000** | Written go after paper pass |
| **P3 — Scale** | Further **+$5k every ~30 sessions** (calendar in §5.6) | up to **$20,000** invested | §5.4 — evidence + written go; **not automatic** |

Illustrative growth math from the old all-fill sim (~$5.4k → ~$26k) remains a **planning sketch only** if live edge appears; it is **not** a deposit schedule and is **not** evidence of edge.

### 5.1 Why “$5k for 30 days, then +$5k if green” is incomplete

| Issue | Why it matters |
|-------|----------------|
| Gate was bypassed in the only backtest | Live default should respect the gate; we don’t know if the gate helps or just cuts trades |
| ~15 fills / 30 sessions | Cycle P&L is mostly noise; profit ≠ proven expectancy |
| No random control | Ranking may not beat chance under the same pullback/target/stop rules |
| One green cycle unlock | No-edge paths still reach $20k some fraction of the time |

**Chosen path:** keep the **$5k first tranche** and **+$5k ~every 30 sessions** calendar, but put **paper + controls in front of live #1**, and require **written go + ongoing evidence** before each later deposit.

### 5.2 Pre-registered paper pass/fail (write before session 1)

**Pass (all required):**
1. ≥ **30 filled** paper trades (trade-through fills preferred: price must **trade through** the limit, not only touch).  
2. **Positive expectancy** after fees on the primary arm (default: gate-approved; also report all-signals).  
3. Primary arm **beats random-pick control** under identical entry/exit/fee rules over the same sessions.  
4. Max drawdown on the $5k notional paper book **≤ 10%** ($500) without a rule breach that would have been ignored live.  
5. Ops clean: ≤5 day-trades/week policy respected; settlement rules modeled (T+1 redeploy).

**Fail → do not deposit live $5k:** any of the above missed, or tooling cannot log gate + signal daily.

### 5.3 Live $5k (only after paper pass)

- Treat as **tuition to find out**, not an investment thesis proven.  
- **Hard stop:** −**10%** ($500) peak-to-trough on the live book → pause all new arms; written review before any resume.  
- Unlevered; settled cash; broker-side target/stop; kill switch.  
- Continue logging **every** signal + gate verdict (even on NO-TRADE days).

### 5.4 Deposit #2 and beyond (evidence-gated cadence)

**Planning cadence:** +$5,000 about every **~30 trading sessions** after the prior deposit (≈6 calendar weeks at ≤5 sessions/week). Calendar dates in §5.6 are **earliest sketches**, not autopay.

| Unlock | Requirement |
|--------|-------------|
| Deposit #2 (+$5k → $10k invested) | Earliest ~**30 sessions after #1**; live expectancy still positive after costs; drawdown within hard-stop history; RH/dashboard reconcile clean; **operator written go** |
| Deposit #3 / #4 | Same bar: ~30 sessions after prior; expectancy still positive; no unresolved hard-stop breach; written go |

**Not automatic:** reaching a calendar date or finishing ~30 sessions does **not** auto-deposit. Skip or delay any tranche if edge is absent.

### 5.5 Frequency after PDT drop

Up to **5 sessions/week** is allowed as ops policy (FINRA/RH no longer impose 3-under-$25k). Binding live constraint remains **settled cash (T+1)** for unlevered accounts — see §0.

### 5.6 Funding calendar (earliest sketches — evidence-gated)

Assumption: ~30 trading sessions ≈ ~6 calendar weeks when markets are open (skips weekends + US holidays: Christmas, New Year’s, MLK, Presidents Day).

| Step | Earliest date | Cash in | Invested after | Mode / note |
|------|---------------|---------|----------------|-------------|
| Paper P1 | 2026-10-20 → ~2026-11-28 | $0 | $0 | Must pass §5.2 |
| **Deposit #1** (RH live) | **2026-12-01** | **$5,000** | **$5,000** | **CASH / unlevered**; hard −10% stop |
| **Deposit #2** | **2027-01-13** | **$5,000** | **$10,000** | ~30 sessions after #1 |
| **Deposit #3** | **2027-02-25** | **$5,000** | **$15,000** | ~30 sessions after #2 |
| **Deposit #4** | **2027-04-09** | **$5,000** | **$20,000** | ~30 sessions after #3; optional |

Old extrapolated end-state (~$25–26k on $20k invested) is retained only as a **what-if** if expectancy survives paper and live — not a promise.

---

## 6. Evidence quality

| Evidence | Strength | Caveat |
|----------|----------|--------|
| 60-session 5m fill-path on #1 (gate off) | Exploratory | Counterfactual; gate bypassed |
| $5k all-fill path ≈ +18.7% / 60d | Planning sketch | Not a forecast; not deposit proof |
| Weekly ≥$450 as a floor | **Weak** | Design goal, not history |
| Random-pick control | **Not yet run** | Required before trusting rank edge |
| Gate ON vs OFF dual arm | **Not yet logged forward** | Required in paper |
| Live automated RH execution | **Not yet proven** | Build in progress |

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
| Paper pass before live $5k | §5.2 pre-registered criteria |
| Hard −10% live drawdown stop | Pause and review |
| Scale gate | +$5k ~every 30 sessions (calendar §5.6); still evidence + written go — not automatic |
| Unlevered policy | No borrowed buying power |
| Default `#1` only | Avoid untested dual-name complexity |
| Dual-arm logging | Every signal + gate verdict (all vs gate-approved) |

Technical plan: `docs/ROBINHOOD_AUTOMATION_PLAN.md`.

---

## 9. Use of proceeds

| Tranche | Amount | Purpose |
|---------|--------|---------|
| Paper | $0 | Prove process + beat control (§5.2) |
| 1 | $5,000 | Live tuition after paper pass; hard −10% stop |
| 2–4 | $5,000 each | ~every 30 sessions (dates §5.6); §5.4 evidence + written go → max **$20,000** invested |

---

## 10. Alternatives

1. Cash / do nothing  
2. Buy-and-hold index ETF  
3. **Paper 40–60 first, then live $5k only** (chosen path)  
4. Live $5k forever, never scale  
5. Auto-deposit on calendar date with no written go (rejected — must stay gated)  
6. Margin with borrow (rejected)

---

## 11. Diligence checklist

- [ ] I understand cited returns are mostly **simulated** and gate-off.  
- [ ] I understand **PDT $25k / 3-trade rules are replaced** (FINRA/RH, Jun 2026) but **settlement and intraday margin** still matter.  
- [ ] I will confirm in-app: **Settings → Investing → Day trade settings**.  
- [ ] I understand this plan is **unlevered** and uses **T+1 settled** funds in cash mode.  
- [ ] I understand **$450/week is a design target**, not a historical minimum.  
- [ ] I understand **paper must pass §5.2 before any live $5k**.  
- [ ] I understand deposits follow the **§5.6 calendar (~30 sessions)** but still need **§5.4 evidence + written go** (never automatic).  
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
| Next milestone | Paper worker live on Mac (Oct–Nov); scoreboard at `/api/paper/scoreboard`; then live $5k only if pass |

---

## 13. One-page verdict frame

| Question | Reading of *this* plan |
|----------|-------------------------|
| Clear strategy? | **Yes** — #1, pullback, target/stop, ≤5 sessions/week, settled cash. |
| Empirical support for edge? | **Not yet** — exploratory sim only; controls + paper still required. |
| PDT still blocking 3/week? | **No** (as of Jun 4, 2026 per FINRA/RH) — settlement is the pacing item. |
| Outside capital today? | **No** — reviewers correctly declined; evidence incomplete. |
| Live first $5k today? | **No** — paper + controls first. |
| Live first $5k after clean paper pass? | **Reasonable as tuition** if loss of $5k is personally acceptable. |
| Scale past $5k on calendar alone? | **No** — use §5.4 evidence + written go (~30-session cadence is the sketch only). |

---

*End of strategy brief. Simulated figures from Oct 2026 analysis runs; post-PDT + evidence-gate refresh Oct 18, 2026.*
