#!/bin/bash
# Pick a Python that can import pandas/numpy (ingest/yfinance).
# Prefers repo .venv (same Python for Terminal + Desktop app), then pinned path.
set -u

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$ROOT/.venv/bin/python3"
PINNED="$HOME/.investment_agent/ingest-python.path"

_python_ok() {
  local py="$1"
  [[ -n "$py" && -x "$py" ]] || return 1
  PYTHONPATH="$ROOT/src" "$py" -c "import pandas, numpy" 2>/dev/null
}

_python_err() {
  local py="$1"
  PYTHONPATH="$ROOT/src" "$py" -c "import pandas, numpy" 2>&1 | head -2 | tr '\n' ' '
}

_arch_label() {
  local py="$1"
  "$py" -c "import platform, struct; print(f'{platform.python_version()} {platform.machine()} ({struct.calcsize(\"P\")*8}-bit)')" 2>/dev/null || echo "unknown"
}

_pin() {
  local py="$1"
  mkdir -p "$(dirname "$PINNED")"
  echo "$py" > "$PINNED"
  echo "$py"
  exit 0
}

if [[ -x "$VENV_PY" ]] && _python_ok "$VENV_PY"; then
  _pin "$VENV_PY"
fi

if [[ -f "$PINNED" ]]; then
  PY="$(tr -d '\r\n' < "$PINNED")"
  if [[ -x "$PY" ]] && _python_ok "$PY"; then
    echo "$PY"
    exit 0
  fi
  echo "WARN: pinned Python failed pandas/numpy check: $PY" >&2
  echo "      $(_python_err "$PY")" >&2
  echo "      Re-run: ./scripts/fix_ingest_python_mac.sh" >&2
fi

for candidate in \
  /opt/homebrew/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
  /usr/bin/python3 \
  /usr/local/bin/python3 \
  python3
do
  if [[ -x "$candidate" ]] || command -v "$candidate" >/dev/null 2>&1; then
    cmd="$candidate"
    [[ -x "$candidate" ]] || cmd="$(command -v "$candidate")"
    if _python_ok "$cmd"; then
      _pin "$cmd"
    fi
  fi
done

echo "ERROR: No Python found with working pandas/numpy for ingest." >&2
echo "  Try: ./scripts/fix_ingest_python_mac.sh  (creates Home-Repository/.venv)" >&2
if [[ -x "$VENV_PY" ]]; then
  echo "  .venv exists but failed: $(_python_err "$VENV_PY")" >&2
fi
if [[ -f "$PINNED" ]]; then
  PY="$(tr -d '\r\n' < "$PINNED")"
  echo "  Pinned: $PY — $(_arch_label "$PY") — $(_python_err "$PY")" >&2
fi
exit 1
