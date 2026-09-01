#!/bin/bash
# Git pull + hard restart dashboard + open browser (Mac).
# Usage:
#   ./scripts/update_and_open_dashboard_mac.sh           # pull + restart + open browser
#   ./scripts/update_and_open_dashboard_mac.sh --no-open # pull + restart (Desktop app opens browser)
set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

EXTRA_ARGS=()
for arg in "$@"; do
  EXTRA_ARGS+=("$arg")
done

echo "=== Update and open dashboard ==="
echo "Repo: $ROOT"
echo ""

echo "── git pull origin main ──"
if git pull --ff-only origin main; then
  echo ""
else
  PULL_CODE=$?
  echo ""
  echo "WARN: git pull failed (exit $PULL_CODE) — restarting with local code."
  echo "      If you have local edits or are on a branch, that is OK."
  echo ""
fi

exec "$ROOT/scripts/hard_restart_dashboard_mac.sh" "${EXTRA_ARGS[@]}"
