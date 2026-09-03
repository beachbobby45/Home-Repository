#!/bin/bash
# Full dashboard repair: rebuild .venv + reinstall LaunchAgent + verify (Mac).
# Used by Repair Dashboard.command and the Desktop app.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
chmod +x "$ROOT/scripts/"*.sh "$ROOT/scripts/"*.command 2>/dev/null || true

echo "=== Repair dashboard service ==="
echo "Repo: $ROOT"
echo ""

"$ROOT/scripts/fix_ingest_python_mac.sh"
"$ROOT/scripts/install_dashboard_service_mac.sh"
"$ROOT/scripts/ensure_dashboard_mac.sh"

echo ""
echo "Dashboard service is running at http://127.0.0.1:8080"
