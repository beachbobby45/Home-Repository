# Robinhood EOD flatten & go-live sequence

> **Status:** Locked decision (2026-11-14) — implement after Nov + Dec paper sample  
> **Owner:** Tony + Cursor agent  
> **Execution broker:** Robinhood (MCP / agent adapter) — **not** E\*TRADE  
> **Related:** `docs/ROBINHOOD_AUTOMATION_PLAN.md` Phase D (broker-side exits)

---

## 1. Why this exists

Dashboard / monitor `EOD_FLATTEN` alerts are insufficient: Tony is not watching the board all day. Exit protection must not depend on Cursor chat or a human acknowledging an alert before the close.

Paper November–December 2026 is for measuring real win rate / cadence. Automation build for unattended execution follows that sample.

---

## 2. Locked exit method (Phase D acceptance)

After a Robinhood **limit buy fill**, the execution worker must immediately arm broker-side exits:

| Leg | Action | Where it lives |
|-----|--------|----------------|
| Target | Limit sell at Growth Plan target | Resting on **Robinhood** (OCO/bracket if MCP supports; else linked orders + worker cancel) |
| Stop | Stop at Growth Plan stop | Resting on **Robinhood** (same OCO/link rule) |
| **EOD flatten** | If still long after **~15:50 ET** → **market sell** (or best available exit); cancel leftover target/stop; journal from RH fill | Worker-enforced via Robinhood MCP (unless RH exposes a native time trigger) |

**Default:** same-day flat. Overnight only if `overnight_approved=true` for that session.

**Chaos bar (must pass):** kill dashboard / Cursor mid-day → target+stop still rest on RH. Unprotected overnight caused by tool failure = Phase D fail.

**Non-goals for this control:** dashboard-only reminders, phone push as primary sell, manual “remember to flatten.”

---

## 3. Post–Nov/Dec go-live sequence (Tony + agent)

After November and December paper results are reviewed:

1. **Tony** connects Robinhood account access for the agent (MCP / approved auth path).
2. **Tony** funds the account with the agreed **seed principal** (ladder start, typically $5,000 book).
3. **Agent** runs the locked plan **fully automated** under existing safeguards:
   - Local Mac execution worker (LaunchAgent)
   - PDT caps (3 day trades/week while equity &lt; $25k; 5 at/above)
   - Day gate / armed plan / kill switch (`TRADING_PAUSED`)
   - Fill → resting target+stop → **15:50 EOD market flatten** if still open
   - Robinhood remains ledger of truth; dashboard mirrors

Until that handoff, continue paper / operator observation only — no live auto-submit.

---

## 4. Implementation notes (when building)

- Prefer extending **Phase D** in `ROBINHOOD_AUTOMATION_PLAN.md` so EOD market flatten is an explicit build bullet and exit criterion, not a later add-on.
- Worker module already sketched as: arm → buy → attach exits → **EOD flatten check**.
- Keep Cursor for morning prep / ranking / oversight; it is **not** the sole sell trigger.

---

## 5. Decision log

| Date (ET) | Decision |
|-----------|----------|
| 2026-11-14 | Reaffirm RH MCP as execution path; lock resting target+stop + ~15:50 market flatten; defer build until after Nov+Dec paper; go-live = RH access + seed fund + full automation. |
