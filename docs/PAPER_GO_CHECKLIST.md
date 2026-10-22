# Paper → Live written go checklist

Use this at the **~2026-11-28 paper review** (or earlier if evidence is clear).  
Nothing auto-deposits. Live RH requires **your written go** after the checks below.

---

## A. Daily Mac readiness (before each paper week)

**Before leaving the Mac unattended**, run one script until it prints `READY_UNATTENDED`:

```bash
cd ~/Home-Repository
./scripts/arm_unattended_mac.sh
```

Operator bar (no SMTP required): paper-worker + morning_prep loaded, sleep=0, macOS **banner** notifications, dashboard shows ranked list / #1 / paper trade log.

Manual checklist (same bar):

- [ ] `./scripts/arm_unattended_mac.sh` → `RESULT: READY_UNATTENDED`
- [ ] Repo on `cursor/post-pdt-strategy-refresh-cd1d` (or `main` after merge)
- [ ] `./scripts/doctor_paper_ready_mac.sh` — no FAIL items
- [ ] Dashboard LaunchAgent loaded → http://127.0.0.1:8080 opens
- [ ] Paper worker LaunchAgent loaded (`com.investment-agent.paper-worker`)
- [ ] Morning health LaunchAgent loaded (`com.investment-agent.health.morning`)
- [ ] Mac on AC with `sleep=0` (calendar jobs miss if the Mac sleeps)
- [ ] `.env` has `NOTIFY_*` + working `SMTP_*` (health + PAPER buy/sell emails)
- [ ] Smoke: forced health email reached inbox
- [ ] **STOP PROCESS** tested once: Stop → no new paper arms → Resume → arms resume

---

## B. Paper pass criteria (§5.2) — all required

Primary book = **gate_approved**. Also review **all_signals** for comparison.

| # | Criterion | Pass? | Evidence |
|---|-----------|-------|----------|
| 1 | ≥ **30 filled** paper trades (prefer trade-through fills) | ☐ | Scoreboard / session log |
| 2 | **Positive expectancy** after fees on gate book | ☐ | Scoreboard / export |
| 3 | Gate book **beats random-pick control** (same entry/exit/fees) | ☐ | `scripts/run_random_pick_control.py` |
| 4 | Max drawdown on $5k paper book **≤ 10%** ($500) | ☐ | Risk / equity high-water |
| 5 | Ops clean: ≤5 sessions/week; T+1 settled redeploy modeled | ☐ | Day-trade log / skips |

**Fail → do not deposit live $5k.** Fix tooling or extend paper; do not “hope live is different.”

---

## C. Written go for live Deposit #1 (RH CASH $5,000)

Earliest sketch: **2026-12-01**. Still requires B = pass.

- [ ] Section B all checked **Pass**
- [ ] Dual-arm review done (gate vs all-signals) — gate remains primary
- [ ] STOP PROCESS re-tested after any code pull
- [ ] RH account type confirmed: **CASH / unlevered** (no borrow)
- [ ] Hard stop rule accepted: **−10% ($500)** → pause new arms + written review
- [ ] SMTP paper trade emails off when live (`NOTIFY_PAPER_TRADES=0`) — use RH app for fills
- [ ] RH API/MCP creds provided and dry-run sync OK
- [ ] Operator statement (fill in):

> I reviewed the paper evidence on ________ (date). Gate book meets §5.2.  
> I authorize live Deposit #1 of **$5,000 CASH** on/after ________.  
> Signature / initials: ________

---

## D. Later deposits (#2–#4) — not automatic

Cadence sketch: +$5k ~every **30 sessions** (2027-01-13 / 02-25 / 04-09).  
Each tranche needs:

- [ ] ~30 sessions since prior deposit (or explicit waiver)
- [ ] Live expectancy still positive after costs
- [ ] No unresolved hard-stop breach
- [ ] RH ↔ dashboard reconcile clean
- [ ] New **written go** for that tranche

---

## E. Robinhood paper trading note (research — Oct 2026)

**Robinhood does not offer a stock paper / demo brokerage account** (no virtual cash, no simulated stock fills, no practice portfolio). Official U.S. help has no “open a paper account” path.

Closest official tool: **[Simulated Returns](https://robinhood.com/us/en/support/articles/simulated-returns/)** — options *scenario analysis only* (price/time/IV what-if). RH states it shows hypothetical options outcomes, not actual returns, and it is not a paper brokerage ledger for equities.

**Worth building RH paper into this plan?** **No.** There is nothing to integrate for stock fills. Keep the **internal paper ledger + Yahoo 5m bars** through the Nov evidence window. Do **not** delay paper for an RH sandbox that does not exist. After written go, prove fill quality with **small real CASH** under the −10% hard stop; RH then becomes ledger of record.

Optional later (not required for P1): richer live quotes already in stack (e.g. Finnhub) for limits — still not RH paper. Fractional shares are live money at $1+, not a substitute for the paper gate.

---

## F. Quick links

| Item | Where |
|------|--------|
| Strategy / gates | `docs/INVESTMENT_STRATEGY_BRIEF.md` §5 |
| Automation plan | `docs/ROBINHOOD_AUTOMATION_PLAN.md` |
| Funding dates | Account tab → Funding plan / `funding_plan.py` |
| Paper status API | `GET /api/paper/status` |
| Health API | `GET /api/ops/health?notify=1` |
