# Intraday Ranked-Pick Capital Builder  
## Strategy Brief for External Review

| Field | Detail |
|-------|--------|
| **Document type** | Investment strategy & operating plan (for diligence) |
| **Prepared** | October 17, 2026 |
| **Last updated** | October 18, 2026 |
| **Operator** | Tony (individual account; self-directed) |
| **Status** | Published for external diligence; pre-live / systems build; historical simulation complete for a limited window |
| **Canonical copy** | https://github.com/beachbobby45/Home-Repository/blob/main/docs/INVESTMENT_STRATEGY_BRIEF.md |
| **Not** | A solicitation, prospectus, or guarantee of returns |

> **Important:** This document is for informational and diligence purposes. It is **not** financial, legal, or tax advice. Past simulated or live performance does **not** predict future results. Equity trading can result in **partial or total loss** of capital. Pattern Day Trader (PDT) and broker rules apply. Any third party considering involvement should perform independent due diligence and consult licensed advisors as appropriate.

---

## 1. Executive summary

### What this is
A **rules-based, same-day long-only** trading program that:

1. Ranks liquid U.S. equities using a local research stack (screener, dollar-goal fit, market activity, confirmation).  
2. Selects primarily the **#1 ranked name** each session.  
3. Enters with a **pullback limit buy**, exits at a **dollar profit target** or **stop**, with an **11:30 ET** entry deadline.  
4. Respects **FINRA Pattern Day Trader** limits while account equity is under **$25,000** (max **3** day trades per week).  
5. Funds capital in **staged $5,000 deposits** only after each ~30-session cycle shows profit.  
6. Executes via **Robinhood** as the ledger of record, with a local always-on worker for travel-safe **broker-side** target/stop orders—not discretionary “AI guessing” each minute.

### What this is not
- Not a hedge fund, pooled vehicle, or managed account offering.  
- Not high-frequency market making.  
- Not a promise of ~$450 every week or of compounding to large wealth on a fixed schedule.  
- Not fully unattended AI discretion; automation is **rule-bound** with kill switches and staged go-lives.

### Ask of a reviewer
Judge whether the **edge hypothesis**, **risk controls**, **capital ladder**, and **evidence quality** are coherent enough to justify the operator deploying **up to $20,000** of personal capital over ~4–6 months under the rules below—and optionally whether a third party would want any economic participation (separate legal structure required if so; none is defined here).

---

## 2. Investment thesis

**Hypothesis:** A systematically ranked “top pick” with a pullback entry and a modest daily dollar target can produce positive expectancy over time, even on many days the system’s own “market activity” gate would have said “no trade”—provided fills are proven on intraday data and day-trade frequency stays PDT-compliant.

**Supporting observations (historical simulation only):**

| Window | Rules | Result (simulated) |
|--------|--------|---------------------|
| 30 sessions | $10k deploy, ignore day-gate, 5-minute fill proof | ≈ **+$1,271** (**+12.7%**) |
| 60 sessions | $10k compound path, same | ≈ **+$1,968** (**+19.7%**) |
| 60 sessions | **$5k** fixed deploy, same | ≈ **+$933** (**+18.7%**) |
| 60 sessions | **$5k** + **≤3 day trades/week** (PDT-style) | ≈ **+$951** (**+19.0%**) |

Source: operator’s local SQLite history + Yahoo 5-minute bars; scripted counterfactual on ranked #1. **Not** live broker fills.

**Why a reviewer might care:** The edge, if real, is process + selectivity (many no-fills) + asymmetric target vs stop design—not “pick every winner.” Weekly $450 (3 × $150) is a **design goal**, rarely achieved as a *minimum* in the sample.

**Why a reviewer might reject it:** Short sample (~60 trading days), concentration in repeated names (e.g. PLTR stretches), counterfactual ignored the system’s own NO-TRADE gate, and live slippage/halts/API risk are unproven.

---

## 3. Scope

### In scope
| Area | Description |
|------|-------------|
| Universe | Liquid U.S. equities from the operator’s watchlist / screener |
| Direction | Long only; flat by end of day in normal operation |
| Sizing | Growth Plan pullback sizing; start **$5,000** book |
| Frequency | **≤3** day trades/week if equity **&lt; $25k**; **≤5**/week if **≥ $25k** |
| Selection | Default **#1 only** (`single_top1`); dual #1+#2 lots only after a future study |
| Broker | Robinhood (dedicated/agent account intended); RH = source of truth for cash/P&L |
| Software | Local Mac dashboard + LaunchAgent worker; Cursor for research/oversight |
| Capital plan | Four × $5k deposits → **$20k invested**, gated on cycle profit |
| Horizon (plan) | Cycle 1 target start **~Nov 2, 2026**; ladder through **~Apr 2027**; 2027 remainder at higher frequency if ≥$25k |

### Out of scope (near term)
- Short selling, options, leverage products, crypto  
- Pooling outside capital without a separate legal entity  
- Trading more than the PDT/week caps above  
- Splitting capital across #1 and #2 until backtested  
- Guaranteed weekly income or fixed “salary” from trading  

---

## 4. Strategy mechanics (rules a reviewer can audit)

### 4.1 Daily process
1. **Morning prep** — refresh data, rank candidates, market activity score, confirmation on #1.  
2. **Arm plan** — ticker, limit buy, target sell, stop, share count, PDT slots remaining.  
3. **Entry** — limit buy; if not filled by **11:30 ET**, cancel (no chase).  
4. **Exit** — resting **target** and **stop** at the broker after fill (travel-safe).  
5. **EOD** — reconcile Robinhood fills into the dashboard mirror; update PDT counter and cycle P&L.

### 4.2 Profit target model (Growth Plan)
At a **$10,000** notional tier, the design daily net target is about **$150** per successful target hit (fees assumed in planning; live RH fees may differ).  
Weekly design at that tier ≈ **3 × $150 = $450**—aligned with “up to 3 production days,” not “profit every day.”

At **$5,000**, the code still aims for ~**$150** net per target, which implies a **larger % move**—historically fewer full target hits than at $10k.

At **$25,000** tier, design daily/weekly production rises (on the order of **~$350 / ~$1,050** per the internal tier table)—still modeled around a small number of quality wins per week.

### 4.3 Risk per trade
- Stop defined in the pullback plan (percentage stop from entry).  
- Same 5-minute bar hitting stop and target counted as **stop** (conservative in backtests).  
- Kill switch: pause new arms; protective exits remain.  
- One name per day under default mode (settlement / operational simplicity).

### 4.4 Pattern Day Trader compliance
| Equity | Max day trades / calendar week |
|--------|--------------------------------|
| &lt; $25,000 | **3** |
| ≥ $25,000 | **5** (operator policy; still subject to broker rules) |

No-fill days do **not** consume a day-trade slot.  
Cash settlement and Robinhood product specifics must be verified in the live account before automation.

---

## 5. Capital plan & proposed outcomes

### 5.1 Funding ladder (operator’s personal capital)

| Stage | Approx. date* | Operator cash in | Simulated / sketched account | Growth on cash invested* |
|-------|---------------|------------------|------------------------------|---------------------------|
| Start | Mon **Nov 2, 2026** | $5,000 | $5,000 | 0% |
| End cycle 1 | Mon **Dec 14, 2026** | $5,000 | ~$5,471 | **~+9.4%** |
| Deposit #2 | Dec 14, 2026 | $10,000 | ~$10,471 | ~+4.7% |
| End cycle 2 | Thu **Jan 28, 2027** | $10,000 | ~$11,676 | **~+16.8%** |
| Deposit #3 | Jan 28, 2027 | $15,000 | ~$16,676 | ~+11.2% |
| End cycle 3 | Fri **Mar 12, 2027** | $15,000 | ~$18,421† | **~+22.8%**† |
| Deposit #4 ($20k in) | Mar 12, 2027 | $20,000 | ~$23,421† | ~+17.1%† |
| End cycle 4 | Mon **Apr 26, 2027** | $20,000 | ~$25,872† | **~+29.4%**† |

\*Trading-day calendar from Nov 2, 2026 (Nov 1 was a Sunday), excluding major U.S. market holidays.  
†Cycles 3–4 **extrapolate** ~9–11% per 30-session block from cycles 1–2 history—**not** measured forward markets.  
Deposits occur **only if** the prior cycle’s live (or paper) P&L is positive.

**Conservative extrapolated end cycle 4:** ~$25.4k account, ~**+27%** on $20k invested.

### 5.2 Full-year 2027 sketch (proposed, not guaranteed)

| Period | Operating mode | Illustrative account band |
|--------|----------------|---------------------------|
| Nov 2026 – Apr 2027 | ≤3 day trades/week; ladder to $20k in | → **~$25–26k** |
| May – Dec 2027 | Up to 5 day trades/week; #1 only initially | **~$32–50k** (conservative→base planning band) |

Optimistic paths exist on paper if weekly production often hits design; they should **not** be used as the base case for diligence.

### 5.3 What “success” means for Cycle 1
- PDT violations: **zero**  
- No unprotected overnight longs caused by tooling failure  
- Robinhood vs dashboard cash match within **$0.01** after sync  
- Cycle P&L **≥ $0** before Deposit #2  
- Operator written go/no-go after ~30 sessions  

Failure of Cycle 1 → **pause deposits**, revise rules; do not “double down” blindly.

---

## 6. Evidence quality (how strong is the proof?)

| Evidence | Strength | Caveat |
|----------|----------|--------|
| 60-session 5m fill-path on #1 | Medium for a personal experiment | One regime window (Jul–Oct 2026 sample in DB); Yahoo 5m ≠ RH fills |
| PDT-capped $5k path ≈ +19% | Useful for under-$25k planning | Does not prove next 60 days |
| Weekly ≥$450 as a floor | **Weak** | 0/13 weeks strictly ≥$450 under first-3-fills; ~2 weeks ≈$449.6 at $10k path |
| Single name making $450 in 1–2 trades | **Not observed** | Cap ~$150/target; best same-name 2-trade week ≈$300 |
| Live automated RH execution | **Not yet proven** | Build in progress; stub sync only until credentials |
| Ignoring NO-TRADE gate in backtest | Material | Live default should prefer Preserve/Produce gates unless explicitly overridden |

**Bottom line for a skeptic:** There is a coherent, tested *process* and a short positive *simulation*. There is **not** yet multi-year live audited performance or out-of-sample robustness across regimes.

---

## 7. Risk factors

### Market & strategy risk
- **Loss of capital** — stops can hit; EOD exits can lose; streaks of stops occurred in the sample (e.g. clustered IDXX/CRM/PTC-type days).  
- **Regime change** — rankings that worked in one period may fail in another.  
- **Concentration** — repeated #1 names increase idiosyncratic risk.  
- **Fill risk** — ~half of days in the 60-day sample never filled by 11:30; opportunity set is thinner than “trade every day.”  
- **Target inflation at $5k** — $150 goal on $5k needs larger % moves → fewer clean targets historically.

### Regulatory & broker risk
- **PDT** — exceeding 3 day trades in 5 business days under $25k can restrict the account.  
- **Broker policy** — Robinhood agentic/API features, approvals, and order types may change.  
- **Settlement / buying power** — same-day reuse of proceeds depends on account type; operator assumes one primary round-trip structure.

### Operational & technology risk
- **Automation failure** — dashboard/worker outages (already experienced in development) could miss entries or, worse, exits—mitigated by **broker-resting** target/stop and kill switch, not by chat-only control.  
- **Data risk** — bad quotes, halted symbols, sync lag → wrong arms if sync freshness checks fail.  
- **Model risk** — AI/Cursor assists research; it must not become unsupervised discretion.  
- **Key-person / travel** — mitigated by local KeepAlive worker + RH orders; not eliminated.

### Capital & liquidity risk
- Staged deposits still put **up to $20k** at risk if later cycles fail.  
- No claim the account reaches $25k on profits alone without deposits.  
- Opportunity cost vs broad index ETFs over the same period is unproven.

### Conflicts & structure
- Operator builds and runs the system (development bias).  
- No independent administrator, auditor, or third-party risk manager in the current personal setup.  
- If others invest, **this brief alone is insufficient**—securities law, custody, and agreements would be required.

---

## 8. Governance & controls

| Control | Intent |
|---------|--------|
| Robinhood as ledger | Prevent “dashboard fiction” balances |
| Dashboard as mirror | Audit trail and ops UI only |
| PDT guard in code | Hard-block 4th (or 6th) day trade |
| Approvals-first go-live | Propose → arm → later limited auto-buy |
| Kill switch | Halt new risk immediately |
| Cycle deposit gate | Do not add $5k after a losing cycle |
| Paper / small live phases | Prove exits before travel auto-buy |
| Default `#1` only | Avoid untested dual-name complexity |
| Separate paper vs live env files | Prevent key mix-ups |

Technical roadmap: `docs/ROBINHOOD_AUTOMATION_PLAN.md` in the Home-Repository project.

---

## 9. Use of proceeds (operator capital)

| Tranche | Amount | Purpose |
|---------|--------|---------|
| 1 | $5,000 | Cycle 1 trading capital (prove process live/paper) |
| 2 | +$5,000 | Only if Cycle 1 profitable |
| 3 | +$5,000 | Only if Cycle 2 profitable |
| 4 | +$5,000 | Only if Cycle 3 profitable → **$20,000 invested** |

Funds are for **securities trading** in the operator’s brokerage account—not for software R&D budgets, salaries, or unrelated expenses (engineering time is separate/sweat equity).

---

## 10. Alternatives a reviewer should weigh

1. **Do nothing / cash** — zero trading risk; zero strategy upside.  
2. **Buy & hold index ETF** — historically strong long-term expectancy; different risk profile; no PDT complexity.  
3. **This plan as paper-only for 60+ sessions** — lowest capital risk way to validate automation.  
4. **This plan with live $5k only, no further deposits** — caps downside at first tranche.  
5. **Wait for ≥$25k funded upfront** — removes PDT 3/week constraint earlier; larger capital at risk immediately.

---

## 11. Diligence checklist (for the reader)

- [ ] I understand returns cited are **mostly simulated**, not multi-year live audited results.  
- [ ] I understand **$450/week is a design target**, not a historical minimum.  
- [ ] I understand **total loss of trading capital is possible**.  
- [ ] I understand PDT and broker rules can halt the strategy.  
- [ ] I understand automation and travel features are **under construction**.  
- [ ] I have read Section 7 (Risks) and Section 6 (Evidence quality).  
- [ ] If I am a third party: I will not fund based on this PDF/MD alone without legal counsel.  

---

## 12. Document control & contacts

| Item | Value |
|------|--------|
| **Final document (GitHub `main`)** | https://github.com/beachbobby45/Home-Repository/blob/main/docs/INVESTMENT_STRATEGY_BRIEF.md |
| **Raw markdown** | https://raw.githubusercontent.com/beachbobby45/Home-Repository/main/docs/INVESTMENT_STRATEGY_BRIEF.md |
| Related technical plan | [`docs/ROBINHOOD_AUTOMATION_PLAN.md`](https://github.com/beachbobby45/Home-Repository/blob/main/docs/ROBINHOOD_AUTOMATION_PLAN.md) |
| Product / finance model | Internal Growth Plan / Phase 1B specs in repository |
| Simulation tools | `scripts/analyze_blocked_day_top1_pnl.py` (5m proven fills; optional compound) |
| Operator | Tony — self-directed retail account |
| Next milestone | Complete Robinhood connectivity; Phase B sync from live ledger; Cycle 1 start target ~Nov 2, 2026 |

---

## 13. One-page verdict frame (for the reader)

| Question | Suggested reading of *this* plan |
|----------|----------------------------------|
| Is there a clear strategy? | **Yes** — ranked #1, pullback, target/stop, PDT caps, staged capital. |
| Is there empirical support? | **Limited but real** — ~60 sessions, positive under strict fill rules; not a long track record. |
| Are risks disclosed? | **Yes** — market, PDT, ops, concentration, extrapolation. |
| Are projected 2027 outcomes guaranteed? | **No** — sketches only; cycles 3–4 extrapolated. |
| Is this ready for outside passive investors? | **Not as presented** — personal operator plan; no fund structure. |
| Is this a reasonable *personal* experiment at $5k→$20k with gates? | **Possibly**, if the operator accepts loss risk and sticks to cycle gates and PDT rules. |

---

*End of strategy brief. Reproduce freely for diligence; do not alter simulated figures without citing a new run date and script version.*
