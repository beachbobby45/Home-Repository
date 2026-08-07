#!/bin/bash
# Repair dashboard database and restart background service (Mac).
# Fixes schema migrations, WAL mode, and stale locks.
# Usage: ./scripts/repair_dashboard_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
DB="$ROOT/data/agent.db"

echo "=== Repair Investment Agent Dashboard ==="

# Stop dashboard to release DB lock
if launchctl print "gui/$(id -u)/$PLIST_LABEL" &>/dev/null; then
  echo "Stopping background dashboard…"
  launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 2
fi
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill -9 $PIDS 2>/dev/null || true
  sleep 1
fi

# Remove stale WAL locks if present
if [[ -f "$DB-wal" || -f "$DB-shm" ]]; then
  echo "Clearing WAL sidecar files…"
  rm -f "$DB-wal" "$DB-shm" 2>/dev/null || true
fi

echo "Applying database schema + migrations…"
export PYTHONPATH="$ROOT/src"
python3 - <<'PY'
from investment_agent.db import init_db, connect
from investment_agent.watchlist import load_preset_into_watchlist, compute_universe_stats

path = init_db()
conn = connect(path)
cols = {r[1] for r in conn.execute("PRAGMA table_info(watchlist)")}
print("watchlist columns:", sorted(cols))
if "source" not in cols or "added_via" not in cols:
    raise SystemExit("Migration failed — missing watchlist columns")
load_preset_into_watchlist(conn, "starter10")
conn.commit()
stats = compute_universe_stats(conn)
conn.close()
print("stats:", stats)
PY

echo ""
echo "Repair OK. Restarting dashboard…"
if [[ -f "$PLIST_PATH" ]]; then
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
  launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 3
fi

if curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:8080/ | grep -q 200; then
  echo "Dashboard UP: http://127.0.0.1:8080"
  echo ""
  echo "Next: ./scripts/run_ingest_mac.sh   (loads metrics — 15–25 min for S&P 500)"
else
  echo "Dashboard not responding — run: ./scripts/install_dashboard_service_mac.sh"
  exit 1
fi
