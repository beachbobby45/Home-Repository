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
  echo "Setup failed — need Python 3.9 or newer."
  echo ""
  echo "Your Mac's /usr/bin/python3 is 3.8 (too old for numpy 1.26)."
  echo ""
  echo "Option A — double-click: scripts/Install Python.command"
  echo "Option B — Terminal:"
  echo "  brew install python@3.12"
  echo "  ./scripts/fix_ingest_python_mac.sh"
  echo ""
  echo "Option C — if you already have /usr/local/bin/python3 3.14, just re-run:"
  echo "  ./scripts/fix_ingest_python_mac.sh"
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
