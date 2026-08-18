#!/bin/bash
# Fix ingest End-of-Day failures from wrong Python / NumPy architecture (Mac).
# Creates Home-Repository/.venv so Terminal and Desktop app use the same Python.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
VENV="$ROOT/.venv"
PINNED="$HOME/.investment_agent/ingest-python.path"
mkdir -p "$(dirname "$PINNED")"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "=== Fix ingest Python (Mac) ==="
echo "Repo: $ROOT"
echo ""

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script is for Mac. Use: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pandas numpy"
  exit 1
fi

pick_base_python() {
  # Apple Silicon: avoid Intel-only /usr/local Python (NumPy arch mismatch with Desktop app).
  if [[ "$(uname -m)" == "arm64" ]]; then
    for candidate in \
      /opt/homebrew/bin/python3 \
      /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
      /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
      /usr/bin/python3
    do
      if [[ -x "$candidate" ]]; then
        echo "$candidate"
        return
      fi
    done
  else
    for candidate in \
      /usr/local/bin/python3 \
      /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
      /usr/bin/python3
    do
      if [[ -x "$candidate" ]]; then
        echo "$candidate"
        return
      fi
    done
  fi
  command -v python3 || true
}

BASE="$(pick_base_python)"
if [[ -z "$BASE" || ! -x "$BASE" ]]; then
  echo "ERROR: python3 not found."
  echo "Install (Apple Silicon): brew install python@3.12"
  echo "Or download from https://www.python.org/downloads/macos/"
  exit 1
fi

echo "Base Python: $BASE"
"$BASE" -c "import platform, struct; print('  Version:', platform.python_version()); print('  Machine:', platform.machine(), struct.calcsize('P')*8, 'bit')"
if [[ "$(uname -m)" == "arm64" && "$BASE" == /usr/local/bin/python3* ]]; then
  echo ""
  echo "WARN: /usr/local/bin/python3 is often Intel/Rosetta on Apple Silicon."
  echo "      Prefer: brew install python@3.12  then re-run this script."
fi
echo ""

if [[ ! -x "$VENV/bin/python3" ]]; then
  echo "Creating project venv: $VENV"
  "$BASE" -m venv "$VENV"
else
  echo "Using existing project venv: $VENV"
fi

PY="$VENV/bin/python3"
echo "Ingest Python: $PY ($("$PY" --version 2>&1))"
echo ""

echo "Installing project dependencies into .venv (pandas/numpy for ingest)…"
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
echo "Project venv → $VENV"
echo ""
echo "Next: quit and reopen the Desktop app, then retry End of Day."
echo "Test: ./scripts/doctor_ingest_mac.sh"
