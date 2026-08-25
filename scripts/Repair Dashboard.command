#!/bin/bash
# One-click repair: Python .venv + dashboard service + start (Mac).
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
echo "=== Repair dashboard ==="
chmod +x "$ROOT/scripts/"*.sh "$ROOT/scripts/"*.command 2>/dev/null || true
"$ROOT/scripts/fix_ingest_python_mac.sh" || exit 1
"$ROOT/scripts/install_dashboard_service_mac.sh" || true
"$ROOT/scripts/ensure_dashboard_mac.sh" || exit 1
echo ""
echo "Done. Open http://127.0.0.1:8080"
read -r -p "Press Enter to close…"
