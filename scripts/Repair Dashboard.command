#!/bin/bash
# One-click repair: Python .venv + dashboard service + start (Mac).
# Use when Update & Open Dashboard fails with "Dashboard failed to load".
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
echo ""
echo "  Repair Dashboard — fixes Python (.venv) and restarts the server"
echo "  Repo: $ROOT"
echo ""
echo "  This takes about 1–2 minutes. Do not close the window."
echo ""
chmod +x "$ROOT/scripts/"*.sh "$ROOT/scripts/"*.command 2>/dev/null || true
"$ROOT/scripts/fix_ingest_python_mac.sh" || exit 1
"$ROOT/scripts/install_dashboard_service_mac.sh" || true
"$ROOT/scripts/ensure_dashboard_mac.sh" || exit 1
echo ""
echo "Done. Opening http://127.0.0.1:8080 …"
if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:8080"
fi
echo ""
read -r -p "Press Enter to close…"
