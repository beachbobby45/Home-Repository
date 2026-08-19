#!/bin/bash
# Fix NumPy architecture errors — rebuilds Home-Repository/.venv from scratch.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
PINNED="$HOME/.investment_agent/ingest-python.path"
mkdir -p "$(dirname "$PINNED")"
export PYTHONNOUSERSITE=1
chmod +x "$ROOT/scripts/resolve_python.sh" 2>/dev/null || true

echo "=== Fix Python (.venv) ==="
echo "Repo: $ROOT"
echo ""
echo "Removing old .venv and rebuilding (ignores ~/Library/Python packages)…"
rm -rf "$ROOT/.venv"

PY="$("$ROOT/scripts/resolve_python.sh")" || {
  echo ""
  echo "Setup failed. Try: brew install python@3.12"
  echo "Then run this script again."
  exit 1
}

echo ""
echo "Ingest Python: $PY ($("$PY" --version 2>&1))"
PYTHONNOUSERSITE=1 PYTHONPATH="$ROOT/src" "$PY" -c "
import pandas as pd
import numpy as np
from investment_agent.providers import yfinance_bars
print('pandas', pd.__version__, '· numpy', np.__version__, '· yfinance OK')
"
echo "$PY" > "$PINNED"
echo ""
echo "Done. Quit the Desktop app (Cmd+Q), reopen it, then retry Morning Prep."
echo "Test: ./scripts/doctor_ingest_mac.sh"
if [[ -f "$HOME/Library/LaunchAgents/com.investment-agent.dashboard.plist" ]]; then
  echo ""
  echo "Updating background dashboard…"
  "$ROOT/scripts/install_dashboard_service_mac.sh" || true
fi
