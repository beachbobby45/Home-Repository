# AI Investment Agent

AI-powered stock analysis and trading signal agent with human-in-the-loop approval.

## Documentation

- **[Architecture Spec (v2)](docs/AI_Investment_Agent_Spec.md)** — full system design
- **[Fees at a Glance](docs/FEES_AT_A_GLANCE.md)** — costs, trial credits, and billing surprises

## Quick Start (Phase 0)

### 1. Get your API keys

See [docs/FEES_AT_A_GLANCE.md](docs/FEES_AT_A_GLANCE.md) for signup links and costs.

Required (all free to obtain; Anthropic has usage fees after trial credits):
- Alpaca paper account
- Anthropic Claude API key
- FRED API key
- Finnhub API key

### 2. Set up environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
```

### 3. Run Gate 0 verification

```bash
python scripts/verify_access.py
```

All required checks must pass before proceeding to Phase 1.

### 4. Run tests

```bash
pytest tests/ -v
```

## Project Status

| Phase | Status |
|-------|--------|
| Phase 0 — Access & foundation | In progress |
| Phase 1 — Data pipeline | Not started |
| Phase 1.5 — Signal gate + backtest | Not started |
| Phase 2 — Reasoning engine | Not started |
| Phase 3 — Risk engine | Not started |
| Phase 4 — Dashboard | Not started |
| Phase 5 — Paper trading | Not started |

## Important

- This system does **not** auto-trade. Human approval is required for every order.
- Paper trade for 60–90 days minimum before considering live trading.
- See the legal disclaimer in the architecture spec.
