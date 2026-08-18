#!/bin/bash
# Pick a Python that can import pandas/numpy (ingest/yfinance).
# Prefers repo .venv (same Python for Terminal + Desktop app), then pinned path.
# Creates .venv automatically on first use if needed.
set -u

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"
VENV_PY="$VENV/bin/python3"
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

_pick_base_python() {
  local c arch
  if [[ "$(uname -m)" == "arm64" ]]; then
    for c in \
      /opt/homebrew/bin/python3 \
      /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
      /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
      /usr/bin/python3 \
      /usr/local/bin/python3
    do
      [[ -x "$c" ]] || continue
      echo "$c"
      return 0
    done
  else
    for c in /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /usr/bin/python3; do
      [[ -x "$c" ]] || continue
      echo "$c"
      return 0
    done
  fi
  command -v python3 2>/dev/null || true
}

_pip_install_venv() {
  "$VENV_PY" -m pip install --upgrade pip >&2
  "$VENV_PY" -m pip install -r "$ROOT/requirements.txt" "pandas>=2.0" "numpy>=1.26" >&2
}

_bootstrap_venv() {
  local base="$1"
  [[ -n "$base" && -x "$base" ]] || return 1
  local base_arch host_arch
  host_arch="$(uname -m)"
  base_arch="$("$base" -c "import platform; print(platform.machine())" 2>/dev/null || echo unknown)"

  echo "" >&2
  echo "Setting up Home-Repository/.venv (one-time, ~1–2 min)…" >&2
  echo "  Base: $base ($(_arch_label "$base"))" >&2

  rm -rf "$VENV"
  if [[ "$host_arch" == "arm64" && "$base_arch" == "x86_64" ]]; then
    echo "  Using Rosetta (x86_64) Python — normal on some Mac setups." >&2
    arch -x86_64 "$base" -m venv "$VENV" >&2 || return 1
  else
    "$base" -m venv "$VENV" >&2 || return 1
  fi

  _pip_install_venv || return 1
  _python_ok "$VENV_PY"
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
  echo "WARN: pinned Python failed pandas/numpy: $PY" >&2
  echo "      $(_python_err "$PY")" >&2
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

# Auto-create .venv (Desktop app + Terminal share this; avoids /usr/local arch mismatch).
BASE="$(_pick_base_python)"
if [[ -n "$BASE" ]] && _bootstrap_venv "$BASE"; then
  echo "  .venv ready: $VENV_PY ($(_arch_label "$VENV_PY"))" >&2
  _pin "$VENV_PY"
fi

echo "ERROR: No Python found with working pandas/numpy for ingest." >&2
echo "  Run in Terminal: cd \"$ROOT\" && ./scripts/fix_ingest_python_mac.sh" >&2
echo "  Or install: brew install python@3.12" >&2
if [[ -f "$PINNED" ]]; then
  PY="$(tr -d '\r\n' < "$PINNED")"
  echo "  Last pinned: $PY — $(_arch_label "$PY") — $(_python_err "$PY")" >&2
fi
exit 1
