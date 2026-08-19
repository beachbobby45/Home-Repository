#!/bin/bash
# Pick ingest/dashboard Python — ONLY Home-Repository/.venv (never system python3).
# Creates/repairs .venv automatically. Ignores ~/Library/Python user packages.
set -u

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONNOUSERSITE=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"
VENV_PY="$VENV/bin/python3"
PINNED="$HOME/.investment_agent/ingest-python.path"

_python_ok() {
  local py="$1"
  [[ -n "$py" && -x "$py" ]] || return 1
  PYTHONNOUSERSITE=1 PYTHONPATH="$ROOT/src" "$py" -c "
import pandas
import numpy
from investment_agent.providers import yfinance_bars
" 2>/dev/null
}

_python_err() {
  local py="$1"
  PYTHONNOUSERSITE=1 PYTHONPATH="$ROOT/src" "$py" -c "import pandas, numpy" 2>&1 | head -3 | tr '\n' ' '
}

_arch_label() {
  local py="$1"
  PYTHONNOUSERSITE=1 "$py" -c "import platform, struct; print(f'{platform.python_version()} {platform.machine()} ({struct.calcsize(\"P\")*8}-bit)')" 2>/dev/null || echo "unknown"
}

_pin() {
  mkdir -p "$(dirname "$PINNED")"
  echo "$VENV_PY" > "$PINNED"
  echo "$VENV_PY"
  exit 0
}

_pick_base_python() {
  local c
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
  PYTHONNOUSERSITE=1 "$VENV_PY" -m pip install --upgrade pip >&2
  PYTHONNOUSERSITE=1 "$VENV_PY" -m pip install -r "$ROOT/requirements.txt" "pandas>=2.0" "numpy>=1.26" >&2
}

_bootstrap_venv() {
  local base="$1"
  [[ -n "$base" && -x "$base" ]] || return 1
  local base_arch host_arch
  host_arch="$(uname -m)"
  base_arch="$(PYTHONNOUSERSITE=1 "$base" -c "import platform; print(platform.machine())" 2>/dev/null || echo unknown)"

  echo "" >&2
  echo "Setting up Home-Repository/.venv (one-time, ~1–2 min)…" >&2
  echo "  Base: $base ($(_arch_label "$base"))" >&2
  echo "  (Ignores ~/Library/Python packages that cause NumPy arch errors.)" >&2

  rm -rf "$VENV"
  if [[ "$host_arch" == "arm64" && "$base_arch" == "x86_64" ]]; then
    echo "  Using Rosetta (x86_64) venv — normal on some Mac setups." >&2
    arch -x86_64 "$base" -m venv "$VENV" >&2 || return 1
  else
    "$base" -m venv "$VENV" >&2 || return 1
  fi

  _pip_install_venv || return 1
  _python_ok "$VENV_PY"
}

# Use existing .venv if healthy.
if [[ -x "$VENV_PY" ]] && _python_ok "$VENV_PY"; then
  _pin
fi

# Repair broken .venv (or create new).
BASE="$(_pick_base_python)"
if [[ -n "$BASE" ]] && _bootstrap_venv "$BASE"; then
  echo "  .venv ready: $VENV_PY ($(_arch_label "$VENV_PY"))" >&2
  _pin
fi

echo "ERROR: Could not create a working .venv for ingest/dashboard." >&2
echo "  Run: cd \"$ROOT\" && ./scripts/fix_ingest_python_mac.sh" >&2
echo "  Or:  brew install python@3.12  then run fix again." >&2
if [[ -x "$VENV_PY" ]]; then
  echo "  .venv broken: $(_python_err "$VENV_PY")" >&2
fi
exit 1
