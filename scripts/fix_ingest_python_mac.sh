#!/bin/bash
# Fix ingest End-of-Day failures from wrong Python / NumPy architecture (Mac).
# Creates Home-Repository/.venv so Terminal and Desktop app use the same Python.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
chmod +x "$ROOT/scripts/resolve_python.sh" 2>/dev/null || true

echo "=== Fix ingest Python (Mac) ==="
echo "Repo: $ROOT"
echo ""

# resolve_python.sh creates/repairs .venv when needed.
PY="$("$ROOT/scripts/resolve_python.sh")" || {
  echo ""
  echo "Setup failed. On Apple Silicon without Homebrew Python, run:"
  echo "  brew install python@3.12"
  echo "Then run this script again."
  exit 1
}

echo "Ingest Python: $PY ($("$PY" --version 2>&1))"
echo ""
PYTHONPATH="$ROOT/src" "$PY" -c "
import pandas as pd
import numpy as np
print('pandas', pd.__version__, '· numpy', np.__version__)
"
echo ""
echo "Done. Quit and reopen the Desktop app, then retry End of Day."
echo "Test: ./scripts/doctor_ingest_mac.sh"
