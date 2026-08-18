#!/bin/bash
# Pick a Python that can import pandas/numpy (ingest/yfinance).
# Prefers native Apple Silicon (/opt/homebrew) over Rosetta /usr/local.
# Prints full path to stdout; exit 1 if none found.
set -u

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PINNED="$HOME/.investment_agent/ingest-python.path"

_python_ok() {
  local py="$1"
  [[ -n "$py" && -x "$py" ]] || return 1
  PYTHONPATH="$ROOT/src" "$py" -c "
import pandas
import numpy
" 2>/dev/null
}

_arch_label() {
  local py="$1"
  "$py" -c "import platform, struct; print(f'{platform.python_version()} {platform.machine()} ({struct.calcsize(\"P\")*8}-bit)')" 2>/dev/null || echo "unknown"
}

if [[ -f "$PINNED" ]]; then
  PY="$(tr -d '\r\n' < "$PINNED")"
  if _python_ok "$PY"; then
    echo "$PY"
    exit 0
  fi
fi

for candidate in \
  /opt/homebrew/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
  /usr/local/bin/python3 \
  /usr/bin/python3 \
  python3
do
  if [[ -x "$candidate" ]] || command -v "$candidate" >/dev/null 2>&1; then
    cmd="$candidate"
    [[ -x "$candidate" ]] || cmd="$(command -v "$candidate")"
    if _python_ok "$cmd"; then
      mkdir -p "$(dirname "$PINNED")"
      echo "$cmd" > "$PINNED"
      echo "$cmd"
      exit 0
    fi
  fi
done

echo "ERROR: No Python found with working pandas/numpy for ingest." >&2
echo "  Default python3: $(command -v python3 2>/dev/null || echo missing) — $(_arch_label "$(command -v python3 2>/dev/null || echo /usr/bin/false)")" >&2
echo "  Fix: ./scripts/fix_ingest_python_mac.sh" >&2
exit 1
