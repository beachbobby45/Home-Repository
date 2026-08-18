#!/bin/bash
# Fix ingest End-of-Day failures from wrong Python / NumPy architecture (Mac).
# Installs deps with native Homebrew Python when possible, pins ingest-python.path.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
PINNED="$HOME/.investment_agent/ingest-python.path"
mkdir -p "$(dirname "$PINNED")"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "=== Fix ingest Python (Mac) ==="
echo "Repo: $ROOT"
echo ""

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script is for Mac. Use: python3 -m pip install -r requirements.txt pandas numpy"
  exit 1
fi

pick_python() {
  if [[ -x /opt/homebrew/bin/python3 ]]; then
    echo /opt/homebrew/bin/python3
    return
  fi
  if [[ -x /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 ]]; then
    echo /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
    return
  fi
  command -v python3
}

PY="$(pick_python)"
if [[ -z "$PY" || ! -x "$PY" ]]; then
  echo "ERROR: python3 not found."
  echo "Install: brew install python@3.12   (Apple Silicon Mac)"
  echo "Or download from https://www.python.org/downloads/macos/"
  exit 1
fi

echo "Using: $PY"
"$PY" -c "import platform, struct; print('  Version:', platform.python_version()); print('  Machine:', platform.machine(), struct.calcsize('P')*8, 'bit')"
echo ""

echo "Installing project dependencies (includes pandas/numpy for ingest)…"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r "$ROOT/requirements.txt" "pandas>=2.0" "numpy>=1.26"
echo ""

echo "Verifying pandas/numpy…"
PYTHONPATH="$ROOT/src" "$PY" -c "
import pandas as pd
import numpy as np
print('  pandas', pd.__version__)
print('  numpy', np.__version__)
"

echo "$PY" > "$PINNED"
echo ""
echo "Pinned ingest Python → $PINNED"
echo ""
echo "Next: quit and reopen the Desktop app, then retry End of Day."
echo "Or test: ./scripts/doctor_ingest_mac.sh"
