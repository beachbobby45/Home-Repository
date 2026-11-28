# Paper → Live written go checklist

Use this at the **Dec 2026 30/60/90 paper review** (target close **2026-12-31**).  
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
- [ ] Repo on branch with Dec $15k paper scale (or `main` after merge)
- [ ] `./scripts/scale_paper_to_15k_mac.sh` applied once (books ~$15k; Oct–Nov history kept)
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
Sizing for Dec = **$15,000** (~**$225** net target / trade at 1.50%).

| # | Criterion | Pass? | Evidence |
|---|-----------|-------|----------|
| 1 | ≥ **30 filled** paper trades (prefer trade-through fills) | ☐ | Scoreboard / session log |
| 2 | **Positive expectancy** after fees on gate book | ☐ | Scoreboard / export |
| 3 | Gate book **beats random-pick control** (same entry/exit/fees) | ☐ | `scripts/run_random_pick_control.py` |
| 4 | Max drawdown on $15k paper book **≤ 10%** ($1,500) | ☐ | Risk / equity high-water |
| 5 | Ops clean: ≤5 sessions/week; T+1 settled redeploy modeled | ☐ | Day-trade log / skips |

**Fail → do not deposit live $15k.** Fix tooling or extend paper; do not “hope live is different.”

---

## C. Written go for live seed (RH CASH $15,000)

Earliest sketch: **2027-01-04**. Still requires B = pass.  
Fresh seed — **not** a roll of paper equity. Mode stays **Paper** until this go.

- [ ] Section B all checked **Pass** (Dec 30/60/90 review)
- [ ] Dual-arm review done (gate vs all-signals) — gate remains primary
- [ ] STOP PROCESS re-tested after any code pull
- [ ] RH account type confirmed: **CASH / unlevered** (no borrow)
- [ ] Hard stop rule accepted: **−10% ($1,500)** → pause new arms + written review
- [ ] Same-day **EOD flatten** accepted (alert ~15:45 ET / RH ~15:50)
- [ ] SMTP paper trade emails off when live (`NOTIFY_PAPER_TRADES=0`) — use RH app for fills
- [ ] RH API/MCP creds provided and dry-run sync OK
- [ ] Operator statement (fill in):

> I reviewed the Dec paper evidence on ________ (date). Gate book meets §5.2 at $15k sizing.  
> I authorize live seed of **$15,000 CASH** on/after **2027-01-04** (or ________).  
> Signature / initials: ________

---

## D. Later capital — not automatic

No staged auto-ladder. Any add after the $15k seed needs:

- [ ] Evidence + written go for that amount
- [ ] Live expectancy still positive after costs
- [ ] No unresolved hard-stop breach
- [ ] RH ↔ dashboard reconcile clean

---

## E. Mode reminder

Dashboard mode dropdown: keep **Paper** through December. Flip to **Live** only on/after the written go in section C.
