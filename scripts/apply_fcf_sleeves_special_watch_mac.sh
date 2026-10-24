#!/bin/bash
# Pull latest Special Watch (datacenter_us) list — including FCF Sleeve A/B adds —
# onto the active watchlist without deactivating other names. Then remind to ingest.
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/apply_fcf_sleeves_special_watch_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

echo "=== Sync Special Watch (datacenter_us + extras) onto active watchlist ==="
"$PY" - <<'PY'
from investment_agent.db import connect, get_active_watchlist, init_db
from investment_agent.watchlist import (
    get_special_watch_extras,
    load_preset_tickers,
    merge_special_watch_tickers,
    upsert_tickers,
)

conn = connect(init_db())
preset = "datacenter_us"
extras = get_special_watch_extras(conn, preset)
merged = merge_special_watch_tickers(preset, extras)
before = set(get_active_watchlist(conn))
activated = upsert_tickers(
    conn, merged, source="special_watch", added_via="fcf_sleeves_sync"
)
conn.commit()
after = set(get_active_watchlist(conn))
new_active = sorted(after - before)
preset_n = len(load_preset_tickers(preset))
print(f"special_watch_merged={len(merged)} (preset={preset_n}, extras={len(extras)})")
print(f"upserted={activated}")
print(f"newly_activated_count={len(new_active)}")
print(f"newly_activated_sample={new_active[:30]}")
print(f"active_watchlist_count={len(after)}")
conn.close()
PY

echo ""
echo "Special Watch table updates from universe/datacenter_us.txt after dashboard restart."
echo "Run Daily ingest (or ./scripts/run_ingest_mac.sh) so Range/ADV fill for new names."
echo "Optional: ./scripts/hard_restart_dashboard_mac.sh"
echo "=== Done ==="
