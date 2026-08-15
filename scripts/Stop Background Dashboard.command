#!/bin/bash
# Double-click to stop the old background dashboard service (Mac).
# Then double-click Open Dashboard.command to run the latest version.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  Stopping background dashboard service (if installed)…"
echo ""

if [[ -f "$ROOT/scripts/uninstall_dashboard_service_mac.sh" ]]; then
  chmod +x "$ROOT/scripts/uninstall_dashboard_service_mac.sh" 2>/dev/null || true
  "$ROOT/scripts/uninstall_dashboard_service_mac.sh"
else
  echo "Uninstall script not found."
fi

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    echo "Stopping process on port 8080: $PIDS"
    kill $PIDS 2>/dev/null || true
  fi
fi

echo ""
echo "Done. Now double-click Open Dashboard.command"
echo ""
read -r -p "Press Enter to close…"
