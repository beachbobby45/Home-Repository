# Robinhood Automation Build Plan

> **Status:** Approved to build — Phase A/B in progress; **PDT + evidence gates refreshed Oct 18, 2026**  
> **Owner:** Tony + Cursor agent  
> **Supersedes for execution path:** Product Spec v3 “manual E*TRADE only” *when Tony explicitly enables this track*  
> **Does not replace:** ranking, Market Activity, pullback entry, Growth Plan targets, Produce/Preserve day gate

---

## 1. Goal

Build a **travel-safe, settlement-aware** system where:

1. **Robinhood is the source of truth** for cash, positions, fills, and P&L.  
2. The **dashboard is a mirror** (ingested copy), not the ledger.  
3. A **local always-on Mac worker** (LaunchAgent) enforces ops caps and **settled buying power** checks.  
4. **Exits (target + stop) live on Robinhood** as resting orders after fill — not dependent on Cursor chat or Tony being at a keyboard.  
5. Cursor continues **Morning Prep / ranking / confirmation / oversight**; it is **not** the sole sell trigger.  
6. Capital ladder: **$5k → +$5k each profitable ~30-session cycle → $20k invested**, deposits only if the cycle grew.

**Regulatory note (Jun 4, 2026):** FINRA replaced PDT with intraday margin standards ([Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10)); Robinhood removed day-trade count restrictions ([Day trading](https://robinhood.com/us/en/support/articles/day-trading/)). Binding ops constraint is now **settled cash (T+1)** for unlevered accounts ([Settlement](https://robinhood.com/us/en/support/articles/settlement-and-buying-power/)), not 3 trades/week under $25k.

**Reference backtest (planning only, not a promise):**  
$5k all-fill path over 60 sessions ≈ +18.7%; staged plan Nov 2026 → ~Apr 2027 toward ~$25–26k account with $20k invested (~+26–30% on invested) if live rhymes with history.

---

## 1b. Decided: frequency, settlement & allocation (updated 2026-10-18)

| Setting | Rule |
|---------|------|
| `max_day_trades_per_week` | **5** (ops policy — one filled round-trip per weekday max). **No** regulatory 3-under-$25k cap. |
| Settlement | **Cash / unlevered:** arm only if **settled** buying power ≥ deploy; after a same-day sale, next buy waits **T+1** |
| Leverage | **Off** — never borrow; avoid intraday margin deficit path |
| `allocation_mode` (default) | **`single_top1`** — one name/day, full deploy to #1 |
| `allocation_mode` (later) | **`dual_lot_top2`** — only after Top2 backtest + Tony OK |

### 2027 year sketch (proposed, not guaranteed)

| Period | Mode | Account band (sketch) |
|--------|------|------------------------|
| Nov 2026 – Apr 2027 | Up to **5** sessions/week; ladder to $20k invested | → **~$25–26k** |
| May – Dec 2027 | Up to **5** sessions/week; `#1` only initially | **~$32–50k** planning band |

---

## 2. Non-goals (this track)

- Unattended strategy changes or “AI discretion” beyond the locked rules.  
- More than **5** filled day trades/week without an explicit settings override.  
- Borrowed margin / leverage.  
- Enabling `dual_lot_top2` without a completed Top2 backtest.  
- Dashboard-authored balances that disagree with Robinhood.  
- Relying on Cursor Cloud chat as a 9:30–16:00 watchdog.

---

## 3. Locked trading rules (automation must enforce)

| Rule | Value |
|------|--------|
| Deploy / sizing | Growth Plan pullback limit; start **$5,000** book |
| Names per day | **1** under `single_top1` (default); dual only if mode enabled |
| Day-trade cap (ops) | **5**/week max filled round-trips |
| Settled funds | Required before arm (cash / unlevered) |
| Entry | Limit buy from pullback plan; **fill by 11:30 ET** or cancel |
| Exit | Growth Plan **limit sell** + **stop**; same-bar ambiguity → stop (backtest convention) |
| Day gate | Configurable Preserve / Produce; default **do not arm** if `allow_trade` false unless Tony enables “counterfactual arm” flag (off by default for live) |
| Confirmation | #1 (or live-confirmed alternate from top list) must pass confirmation checks before arm |
| Kill switch | File/env/API flag: `TRADING_PAUSED=1` → cancel working buys, leave protective exits |

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Cursor (async)     Morning prep, rank, review, kill switch │
└────────────────────────────┬────────────────────────────────┘
                             │ writes plan JSON / DB row
┌────────────────────────────▼────────────────────────────────┐
│  Local worker (LaunchAgent)   Always-on on Tony’s Mac       │
│  - Read today’s ArmedPlan                                   │
│  - Weekly ops slot + settled BP check                       │
│  - Place/cancel RH orders                                   │
│  - Sync RH → SQLite mirror                                  │
└───────────────┬────────────────────────────▲────────────────┘
                │ orders / fills               │ account sync
┌───────────────▼────────────────────────────┴────────────────┐
│  Robinhood (ledger)   Cash, positions, orders, fills = truth│
└─────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│  Dashboard (mirror)   Display + audit from ingested RH data │
└─────────────────────────────────────────────────────────────┘
```

**New modules (proposed):**

| Module | Responsibility |
|--------|----------------|
| `src/investment_agent/broker/robinhood_client.py` | Auth, account, orders, positions (MCP/API adapter) |
| `src/investment_agent/broker/sync.py` | Pull RH → `broker_*` tables; never overwrite RH with journal guesses |
| `src/investment_agent/execution/armed_plan.py` | Immutable day’s plan: ticker, buy, target, stop, shares, deadlines |
| `src/investment_agent/execution/pdt_guard.py` | Count day trades in week; block 6th (ops cap 5) |
| `src/investment_agent/execution/worker.py` | Session loop: arm → buy → attach exits → EOD flatten check |
| `scripts/run_execution_worker_mac.sh` + LaunchAgent plist | KeepAlive worker separate from dashboard if needed |
| Dashboard: **Broker** tab | Equity, buying power, open orders, fills (read-only from sync) |

---

## 5. Phased build

### Phase A — Foundations & reliability (before any live orders)

**Build**
- Harden dashboard KeepAlive (health check, log truncation, restart already partially done).  
- Separate **execution worker** process from UI server so UI blips ≠ missed exits.  
- Schema: `broker_accounts`, `broker_balances`, `broker_positions`, `broker_orders`, `broker_fills`, `armed_plans`, `pdt_day_trades`.  
- Config: `.env.robinhood.paper` / `.env.robinhood.live` (never mixed).

**Test**
- Unit: weekly ops counter (week boundaries, no-fill ≠ day trade).  
- Integration: worker survives dashboard restart.  
- Manual: `dashboard_service_status_mac.sh` green 7 consecutive mornings.

**Exit criteria:** 7 days local uptime with zero “connection failed” during market hours (or documented root-cause fixes).

---

### Phase B — Robinhood sync (ledger → mirror)

**Build**
- Connect via Robinhood **Agent / MCP / official API** (use whatever Tony’s account exposes; adapter interface so the rest of the app is stable).  
- Sync job every N seconds in market hours + on demand: equity, cash, positions, open orders, fills.  
- Dashboard Account/Trade panels show **RH equity/cash**; journal becomes optional annotation, not balance source.  
- Reconciliation report: RH fills vs local `trade_journal` (flag orphans).

**Test**
- Fixture replay of sample RH payloads → DB rows.  
- Idempotent sync (re-pull same fill ≠ duplicates).  
- Balance widget matches RH within $0.01 after sync.

**Exit criteria:** Tony confirms dashboard cash/equity matches Robinhood app on 5 consecutive sessions.

---

### Phase C — Armed plan + propose-only (no auto submit)

**Build**
- After Morning Prep / ranked #1 + confirmation: write `ArmedPlan` (status=`proposed`).  
- Push notification / dashboard banner: “Approve to arm” (mobile-friendly).  
- **Travel mode:** if no veto by `arm_deadline_et` (e.g. 9:25 ET) **and** `travel_auto_arm=true`, status → `armed`. Default `travel_auto_arm=false` until Phase D exit.  
- Dry-run order preview (shares, buy, target, stop, weekly slots left, settled BP) — **no broker submit**.

**Test / backtest**
- Re-run `analyze_blocked_day_top1_pnl.py --days 60 --deploy 5000` with weekly ops-cap report (script extension).  
- Unit: plan builder matches pullback + Growth Plan math at $5k/$10k.  
- Simulation: given historical #1 days, generate ArmedPlans and assert ≤5/week.

**Exit criteria:** 10 consecutive mornings produce a correct proposed plan Tony can approve on phone.

---

### Phase D — Broker-side exits (auto after fill) + manual/armed buy

**Build**
- On approved/armed day: worker places **limit buy** (or Tony taps Approve → submit).  
- On fill: **immediately** place target limit sell + stop (OCO/bracket if RH supports; else two linked orders + monitor).  
- Cancel unfilled buy at **11:30 ET**.  
- Ops guard blocks submit if weekly day-trade count ≥ **5**.  
- Settled buying power required before submit.  
- Kill switch cancels entry; does **not** cancel protective stop unless flattening.

**Test**
- Paper/agent sandbox: full day lifecycle (no fill / fill→target / fill→stop / 11:30 cancel).  
- Chaos: kill dashboard during open order → exits still rest at RH.  
- Chaos: kill worker after fill+exits placed → RH still holds exits.  
- Ops: 6th submit attempt in a week rejected.

**Exit criteria:** 15 paper (or RH agent approval) sessions with **zero** unprotected long overnight positions caused by tool failure.

---

### Phase E — Travel-safe limited auto-buy (still rule-bound)

**Build**
- Enable `travel_auto_arm` + auto-submit buy when: weekly slot free, settled BP OK, plan armed, day-gate policy satisfied, kill switch clear.  
- Enforce `max_day_trades_per_week` = **5**; notify Tony after each submit/fill/exit.  
- Daily EOD email/push: RH P&L, slots used, whether deposit ladder checkpoint is due.

**Test**
- 30-session paper/live-small run matching ladder Cycle 1 ($5k).  
- Compare to backtest band (not required to match; track fill rate, target rate, max DD).  
- Ops/settlement compliance audit: 0 freeriding / over-cap events.

**Exit criteria:** Cycle 1 complete with **profit ≥ $0** and Tony’s written OK to Deposit #2 — **or** pause and revise rules.

---

### Phase F — Ladder operations (Cycles 2–4)

**Build**
- Dashboard “Capital ladder” widget: invested, RH equity, cycle P&L, next deposit eligibility, weekly slots + settled BP.  
- After each ~30 trading sessions: compute cycle P&L from **RH fills only**.  
- Prompt Tony for +$5k only if cycle profit &gt; 0.  
- Ops cap remains **5**/week at all equity levels (post-PDT).  
- Enforce **settled buying power** before arm.  
- Gate `dual_lot_top2` behind Top2 backtest + setting.

**Test**
- Ladder state machine unit tests (deposit gates).  
- Replay Jul–Oct history through ladder simulator (already sketched in chat; encode as `tests/test_capital_ladder_sim.py`).

**Exit criteria:** Invested = $20k only via real deposits; mirror matches RH; settlement/ops clean.

---

## 6. Backtest & test matrix (thorough)

| ID | Type | What | Pass bar |
|----|------|------|----------|
| BT-1 | Backtest | 60d #1, $5k, 5m fills, all fill days | Script reproduces ~+$933 path (±$1) |
| BT-2 | Backtest | 60d #1, $10k compound / fixed | Matches prior published summary |
| BT-3 | Backtest | Ladder sim Nov schedule (post-PDT) | Stage dates/growth table reproducible |
| UT-1 | Unit | `pdt_guard` week boundaries + holidays | Golden cases |
| UT-2 | Unit | Pullback plan $5k vs $10k targets | Sell % widens at $5k |
| UT-3 | Unit | Sync idempotency | No duplicate fills |
| IT-1 | Integration | Paper buy → bracket → target | Fill+flatten recorded in RH+DB |
| IT-2 | Integration | Paper buy → stop | Stop preferred on same-bar conflict |
| IT-3 | Integration | 11:30 cancel | No late entry |
| IT-4 | Chaos | Dashboard down, worker up | Exits remain |
| IT-5 | Chaos | Worker down after brackets | RH still protects |
| AT-1 | Acceptance | 7-day uptime | No morning “connection failed” |
| AT-2 | Acceptance | Balance match | RH vs dashboard $0.01 |
| AT-3 | Acceptance | 30-session Cycle 1 | Settlement/ops clean; Tony go/no-go |

---

## 7. Suggested calendar (evidence-gated — see strategy brief §5)

| When | Focus |
|------|--------|
| **Now** | Confirm RH day-trade settings in-app; Phase A + B reliability + RH sync |
| **Now (parallel)** | **P0 controls:** gate ON vs OFF + random-pick control on historical window |
| **Next ~40–60 sessions** | **P1 forward paper** with pre-registered pass/fail; log every signal + gate verdict; dual arms |
| **After paper pass** | Live **$5k** only (Phase C/D exits proven); hard −10% drawdown stop |
| **After §5.4 scale gate** | Deposit #2 (+$5k) — **not** after one green 30-session cycle alone |
| **Later** | Deposits #3–#4 only under continued evidence; Top2 study before any split |

Slip phases rather than skip exit criteria. Old “Nov→Apr $20k ladder on cycle profit” is superseded by brief §5.

---

## 8. Risk controls (must ship before Phase E)

- Kill switch (`TRADING_PAUSED`) from dashboard + local file.  
- Max loss/day (cancel new arms; flatten optional).  
- No new arms if RH sync older than N minutes.  
- No new arms if worker cannot confirm open-order readback.  
- Separate RH **agent/dedicated** account funding (per RH product guidance).  
- Approvals on until Phase E exit criteria met.

---

## 9. Open decisions (Tony)

1. **Day gate live policy:** Preserve / Produce / or allow arms on NO GO (backtest mode)? Default recommendation: **Produce** for paper, **Preserve** for first live cash.  
2. **Robinhood access path:** in-app Agents + MCP vs other API — confirm what the funded account enables.  
3. **Travel auto-arm default time:** e.g. veto window until 9:20 ET.  
4. **Fee model on RH:** keep $7/$7 planning fees or switch to RH actual commissions for P&L.

**Decided:** ops day-trade cap **5**/week at all equity (post-PDT); default `single_top1`; dual lots only after Top2 study; unlevered + settled cash required.

---

## 10. Definition of “done” for this program

- [ ] RH is sole balance/P&L source; dashboard mirrors it.  
- [ ] Local worker places/cancels entries; **exits rest at RH**.  
- [ ] Day-trade ops cap enforced in code (**5**/week) + settled-BP gate + audited.  
- [ ] Travel does not leave an unprotected position.  
- [ ] Cycle 1 live/paper complete with written go/no-go for Deposit #2.  
- [ ] BT/UT/IT/AT matrix above green or waived in writing.

---

## 11. Implementation status

1. ✅ Plan decisions documented (frequency + allocation + 2027 sketch).  
2. ✅ PDT guard module + unit tests.  
3. ✅ `broker_*` / `armed_plans` / `pdt_day_trades` schema + migration.  
4. ✅ ArmedPlan dataclass + persistence helpers.  
5. ✅ Broker sync stub (`StubBrokerClient` + `/api/broker/sync/fixture`).  
6. ✅ Propose/arm APIs + `/api/broker/status` + `/api/execution/pdt`.  
7. ✅ Execution worker dry-run + `install_execution_worker_mac.sh`.  
8. ⏳ Live Robinhood client (waiting on Tony’s account credentials).  
9. ⏳ Dashboard Broker tab UI banner; `--pdt-weekly-cap` analysis report.  
10. ⏳ P0: random-pick control + gate ON/OFF report on same historical window.  
11. ⏳ P1: forward paper dual-arm logger (signal + gate verdict every session).

---

*This plan keeps automation for travel safety without giving up broker-truth, settlement/ops safety, or exit protection when you’re offline.*
