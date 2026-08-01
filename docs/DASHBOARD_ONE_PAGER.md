# AI Investment Agent — Daily One-Pager

**You trade in E\*TRADE. This board screens, alerts, and records. No auto-orders.**

| Strategy | +1.13% target · −0.50% stop · ~3% swing · $7 buy + $7 sell · $10K → $5M goal |
|----------|--------------------------------------------------------------------------------|

---

## Before you start (once per session)

- [ ] Dashboard open · `APP_API_KEY` pasted → **Save**
- [ ] Regime banner **green** (if red = SPY+DIA+QQQ all down → **no new longs**)

---

## Morning (pre-market / open)

- [ ] Refresh data: `run_ingest.py` **or** **Pull history** + **Sync from screener**
- [ ] Read **Market Brief** (VIX + regime)
- [ ] Review **Trade Queue** — advance only names you agree with  
  `watching → approved → armed → alert → in_trade → eod → closed`
- [ ] Note **Target +1.13%** · **Stop −0.50%** · **Size** on each row

---

## During market hours

- [ ] **Run monitor** every 15–30 min (or on alert)
- [ ] On **TARGET_HIT** / **STOP_HIT** / **EOD_FLATTEN**:
  1. Execute in **E\*TRADE**
  2. **Log fill** in Trade Journal (BUY or SELL)
  3. **Acknowledge** alert on board
- [ ] Same-day flat default — close before close unless overnight approved

---

## End of day

- [ ] Final **Run monitor**
- [ ] All open positions closed in E\*TRADE (or overnight exception documented)
- [ ] Every fill logged in **Trade Journal** (buy **and** sell)
- [ ] **Generate report** (Learning) · skim **CIO Summary**
- [ ] Glance **Historical Analysis** — prior-day screener vs actual

---

## End of month (if month P&L > 0)

- [ ] Check **Month-end Sweep Preview** (10% mgmt + tax %)
- [ ] Adjust tax rate if needed → **Save rate**
- [ ] **Apply month-end sweep**

---

## Quick reference

| Section | Why |
|---------|-----|
| Regime banner | Gate for new longs |
| Goal / Cash / Month P&L | Account health |
| Trade Queue | What to watch / trade |
| Intraday Alerts | Target · stop · EOD |
| Trade Journal | Source of truth — log every fill |
| Learning + CIO | Daily feedback + actions |

**Needs API key:** Sync queue · Run monitor · Pull history · Generate report · Log trade · Apply sweep

**CLI:** `run_ingest.py` · `run_monitor.py` · `run_dashboard.py` · `run_learning.py`

---

*v3 · E\*TRADE manual · Option A (no Claude) · Product Spec v3*
