# Fees at a Glance — AI Investment Agent

> **Last verified:** July 23, 2026  
> **Purpose:** One-page reference for every key, fee, and billing surprise before you start building.  
> **Related:** [Full Architecture Spec](./AI_Investment_Agent_Spec.md)

---

## Step 1 Required Keys (Phase 0)

These four keys are required before any feature code. **Only Anthropic has ongoing usage fees** for this project.

| # | Service | Key cost | Usage fees | Typical v1 monthly cost | Credit card required? |
|---|---------|----------|------------|---------------------------|----------------------|
| 1 | **Alpaca (paper)** | $0 | $0 for paper trading | $0 | No (for paper account) |
| 2 | **Anthropic (Claude API)** | $0 | **Pay-per-token** after free credits | **$0 during trial, then ~$5–25/mo** | No to start; **yes before credits run out** |
| 3 | **FRED (St. Louis Fed)** | $0 | $0 | $0 | No |
| 4 | **Finnhub** | $0 | $0 on free personal tier | $0 | No |

**Daily OHLCV note:** Finnhub **free tier does not include** `/stock/candle` (403). Phase 1 uses **yfinance** for daily bars (free) and **Finnhub** for live quotes only. Upgrade Finnhub or add Massive/Polygon later if you want a single vendor.

**Minimum cash to start building:** **$0** if Anthropic free credits are available on your account.  
**Minimum cash to finish building + paper trade:** plan **~$5–25/month** for Claude API (with signal gating).

---

## Anthropic Trial Credits — Verified Facts

Sources checked:
- [Anthropic official pricing FAQ](https://platform.claude.com/docs/en/about-claude/pricing) (July 2026)
- [Anthropic Help Center — How do I pay for API usage?](https://support.anthropic.com/en/articles/8977456-how-do-i-pay-for-my-api-usage)

### What Anthropic officially states

| Claim | Official source | Verdict |
|-------|----------------|---------|
| New users get free credits to test | Pricing FAQ: *"New users receive a **small amount of free credits** to test the API"* | **Confirmed** |
| Exact dollar amount of free credits | Not published in official docs | **Unknown — do not assume $5** |
| Permanent free API tier | Not offered | **No permanent free tier** |
| Billing model after credits | Prepaid usage credits; API stops when balance is $0 | **Confirmed** |
| Credit expiry | Purchased credits expire **1 year** from purchase date | **Confirmed** (paid credits) |
| Failed API calls charged? | Failed requests are **not charged** | **Confirmed** |

### What community reports (not guaranteed)

Third-party guides often report **~$5** after phone verification, sometimes with a "Claim" banner in Console. Treat this as **anecdotal** until you confirm on your own account under **Settings → Billing → Credit Balance**.

### How to verify on YOUR account (do this in Step 1)

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Complete email + phone verification
3. Open **Settings → Billing** (or Plans & Billing)
4. Check **Credit Balance** — note exact amount and any expiry shown
5. Run `python scripts/verify_access.py --check anthropic` (minimal test call)
6. Re-check credit balance to see cost of one test call

**Gate 0 rule:** Document your actual starting credit balance in `.env.local notes` or a personal log. Do not proceed assuming unlimited free usage.

### Estimated burn rate during build (with signal gating)

| Phase | Estimated Claude calls | Est. cost (Sonnet 4.6) |
|-------|------------------------|-------------------------|
| Gate 0 — access test | 1–3 calls | ~$0.01–0.05 |
| Gate 2 — thesis engine dev | 20–50 test calls | ~$0.50–2.00 |
| Gate 4 — dashboard integration | 10–30 test calls | ~$0.20–1.00 |
| Paper trading (60 days, gated) | ~120–480 theses | ~$5–25 total |

**Without signal gating:** costs can exceed **$150/month** — do not disable the gate.

### Cost controls built into the project

- **Signal gate (Layer 1.5):** only send triggered tickers to Claude
- **`temperature=0`:** consistent outputs, fewer retries
- **Prompt caching:** ~90% savings on repeated system prompt
- **`scripts/verify_access.py`:** uses Haiku or minimal Sonnet call for Gate 0 (cheapest possible test)
- **Validation retry limit:** max 1 retry per thesis (prevents runaway spend on bad outputs)

### When you must add payment

Add a credit card and purchase credits when:
- Free credits are exhausted (API returns billing error), OR
- You want auto-reload enabled for uninterrupted paper trading

Recommended: set a **monthly spend cap** in Console Billing before enabling auto-reload.

---

## Optional Keys (Not Required for Step 1)

| Service | Key cost | Usage fees | When needed | Skip if |
|---------|----------|------------|-------------|---------|
| **Massive (Polygon)** | $0 | $0 free tier; $29+/mo paid | Historical backfill | Using Alpaca history only |
| **Benzinga Basic** (AWS) | $0 | $0 free tier | Extra news headlines | Finnhub news is enough |
| **NewsAPI.org** | $0 dev key | **$449/mo** for production | General news (dev only) | Not using in v1 |
| **SiftingIO calendar** | $0 free tier | Paid tiers exist | Structured economic calendar | FRED release dates suffice |
| **VPS (DigitalOcean etc.)** | N/A | ~$5–12/mo | 24/5 scheduling away from PC | Running on your PC |

---

## Services Removed from v1 (Would Cost Money or Require Approval)

| Service | Why not in v1 | Cost if you insist |
|---------|---------------|-------------------|
| **Reddit API** | Manual approval; commercial use likely paid | ~$0.24/1K calls + contract |
| **StockTwits official API** | Not open to new developers | Enterprise sales |
| **Alpha Vantage free** | 25 requests/day — unusable | $49.99+/mo paid |
| **NewsAPI production** | Dev tier not for live use | $449/mo |
| **Finnhub commercial** | Free = personal use only | $50+/mo |

---

## Live Trading Fees (Phase 6 Only — Not Now)

| Item | Paper (now) | Live (later) |
|------|-------------|--------------|
| Alpaca stock/ETF commissions | $0 | $0 (commission-free) |
| Alpaca account minimum | $0 | $0 |
| SEC/FINRA fees | Simulated | Small per-trade regulatory fees |
| Pattern Day Trader rule | N/A in paper | Applies if account < $25K + day trading |
| Real-time market data | IEX on free paper | Paid data plans optional (~$9–99/mo) |

---

## Total Monthly Cost Summary

| Scenario | Monthly cost |
|----------|-------------|
| **Building + paper trading (v1, gated)** | **$0–25** (Anthropic only; rest free) |
| **Building without signal gating** | **$150–400** (avoid this) |
| **+ VPS hosting** | +$5–12 |
| **+ Massive paid tier** | +$29 |
| **+ Finnhub paid tier** | +$50+ |

---

## Quick Checklist Before You Spend Anything

- [ ] Alpaca paper account created — **$0**
- [ ] FRED API key obtained — **$0**
- [ ] Finnhub API key obtained — **$0**
- [ ] Anthropic Console account created — **$0**
- [ ] Anthropic **Credit Balance checked** — note exact amount
- [ ] Gate 0 test call run — note cost of one call
- [ ] Monthly spend cap set in Anthropic Console (recommended before adding card)

---

## Official Links

- Alpaca: [alpaca.markets](https://alpaca.markets)
- Anthropic pricing: [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Anthropic billing help: [support.anthropic.com/en/articles/8977456](https://support.anthropic.com/en/articles/8977456-how-do-i-pay-for-my-api-usage)
- FRED API keys: [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org/useraccount/apikey)
- Finnhub: [finnhub.io/pricing](https://finnhub.io/pricing)

---

*This page is updated when provider pricing or access terms change. Re-verify before Phase 6 (live trading).*
