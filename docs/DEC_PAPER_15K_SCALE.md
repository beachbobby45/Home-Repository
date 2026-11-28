# December 2026 paper at $15k (Jan 4 2027 live seed)

## Decision

- Continue **paper** through December 2026 at **$15,000** deploy (matches planned RH seed).
- Net target **~1.50%** → **~$225 / trade** at $15k.
- Keep all **Oct–Nov** fills and session logs (top-up credit only — never wipe).
- **Do not** flip Paper→Live until **2027-01-04** written go after Dec 30/60/90 review.
- Live seed is **fresh $15k** (not a paper roll). Same-day EOD flatten on live.

## Mac apply (after pulling this branch)

```bash
cd ~/Home-Repository
git fetch origin
git checkout cursor/dec-paper-15k-cd1d   # or main after merge
git pull
./scripts/scale_paper_to_15k_mac.sh
# then restart dashboard / paper-worker if LaunchAgents are running
```

Confirm Account tab shows ~$15k equity on both books and daily target ~$225.
Mode dropdown stays **Paper**.

## What changed in code

| Area | Change |
|------|--------|
| `PAPER_STARTING_CASH` | $5k → **$15k** |
| `lot_daily_production` | **1.50%** of lot ($15k → **$225**) |
| Funding / PLAN | RH live earliest **2027-01-04** · $15k seed |
| `top_up_paper_books_to_target` | Credits cash; preserves fills |

## Do not

- Run `repair_paper_cash_mac.sh --force` on books with fills (refuses / wrong tool).
- Flip ledger to Robinhood before Jan 4 written go.
- Expect Dec paper to “become” the live balance — live is a separate seed.
