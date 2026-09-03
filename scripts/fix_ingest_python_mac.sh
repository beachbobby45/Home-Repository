#!/bin/bash
# Fix NumPy architecture errors — rebuilds Home-Repository/.venv from scratch.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
PINNED="$HOME/.investment_agent/ingest-python.path"
PLIST_LABEL="com.investment-agent.dashboard"
LOG_DIR="$HOME/Library/Logs/investment-agent"
mkdir -p "$(dirname "$PINNED")"
export PYTHONNOUSERSITE=1
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/install_dashboard_service_mac.sh" 2>/dev/null || true

echo "=== Fix Python (.venv) ==="
echo "Repo: $ROOT"
echo "Host: $(uname -m) · $(sw_vers -productVersion 2>/dev/null || echo macOS)"
echo ""

# Stop background dashboard so it cannot hold a broken .venv or stale plist.
launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
  sleep 1
fi

echo "Removing old .venv and rebuilding (ignores ~/Library/Python packages)…"
rm -rf "$ROOT/.venv"

PY="$("$ROOT/scripts/resolve_python.sh")" || {
  echo ""
  echo "No working .venv yet — checking for Python 3.9+…"
  if [[ -x "$ROOT/scripts/install_python_mac.sh" ]]; then
    echo ""
    echo "Attempting to install Python via Homebrew (if missing)…"
    if INSTALL_PYTHON_AUTO_FIX=1 "$ROOT/scripts/install_python_mac.sh" --fix; then
      exit 0
    fi
  fi
  echo ""
  echo "Setup failed — need Python 3.9 or newer."
  echo ""
  echo "── Do this ──"
  echo "  Finder → Home-Repository/scripts → Install Python.command"
  echo "  (installs Python + builds .venv + starts dashboard)"
  echo ""
  echo "  Or Terminal:"
  echo "    brew install python@3.12"
  echo "    ./scripts/fix_ingest_python_mac.sh"
  echo ""
  exit 1
}

echo ""
echo "Python: $PY ($("$PY" --version 2>&1))"
echo "Arch:   $("$PY" -c "import platform; print(platform.machine())" 2>/dev/null || echo unknown)"
echo ""
echo "Verifying pandas, numpy, yfinance, dashboard…"
PYTHONNOUSERSITE=1 PYTHONPATH="$ROOT/src" "$PY" -c "
import pandas as pd
import numpy as np
from investment_agent.providers import yfinance_bars
from investment_agent.dashboard.app import app
print('OK · pandas', pd.__version__, '· numpy', np.__version__, '· dashboard import')
"
echo "$PY" > "$PINNED"

echo ""
echo "Reinstalling dashboard LaunchAgent with this Python…"
if "$ROOT/scripts/install_dashboard_service_mac.sh"; then
  echo ""
  echo "Done. Dashboard is at http://127.0.0.1:8080"
  echo "Test: ./scripts/doctor_dashboard_mac.sh"
  exit 0
fi

echo ""
echo "WARN: .venv is healthy but the LaunchAgent did not pass the health check yet."
echo "      Python repair succeeded — try:"
echo "        ./scripts/install_dashboard_service_mac.sh"
echo "        ./scripts/ensure_dashboard_mac.sh"
echo "      Or wait 30s and open http://127.0.0.1:8080"
echo ""
echo "If it still fails, send: ~/Library/Logs/investment-agent/dashboard.err.log"
exit 0
