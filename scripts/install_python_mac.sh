#!/bin/bash
# Install Python 3.12+ via Homebrew (Mac) — required for numpy 1.26 / pandas 2.
# Usage: ./scripts/install_python_mac.sh [--fix]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUTO_FIX=0
for arg in "$@"; do
  case "$arg" in
    --fix) AUTO_FIX=1 ;;
  esac
done

echo "=== Install Python for AI Investment Agent ==="
echo "Repo: $ROOT"
echo ""

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Use Python 3.9+ from your package manager."
  exit 1
fi

export PATH="/opt/homebrew/bin:/opt/homebrew/opt/python@3.12/bin:/opt/homebrew/opt/python@3.13/bin:/usr/local/bin:$PATH"

_have_python39() {
  local py="$1"
  [[ -x "$py" ]] && "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null
}

FOUND=""
for py in \
  /opt/homebrew/bin/python3 \
  /opt/homebrew/opt/python@3.12/bin/python3 \
  /opt/homebrew/opt/python@3.13/bin/python3 \
  /usr/local/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
do
  if _have_python39 "$py"; then
    FOUND="$py"
    break
  fi
done

if [[ -n "$FOUND" ]]; then
  echo "OK: usable Python already installed:"
  "$FOUND" --version
  echo "  $FOUND"
  echo ""
else
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is not installed."
    echo ""
    echo "Option A — install Homebrew (recommended), then re-run this script:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "Option B — install Python from https://www.python.org/downloads/macos/"
    echo "  Then run: cd ~/Home-Repository && ./scripts/fix_ingest_python_mac.sh"
    exit 1
  fi

  echo "Installing python@3.12 via Homebrew (one time, ~2–5 min)…"
  brew install python@3.12
  echo ""
  export PATH="/opt/homebrew/opt/python@3.12/bin:/opt/homebrew/bin:$PATH"
  FOUND="/opt/homebrew/bin/python3"
  if [[ ! -x "$FOUND" ]]; then
    FOUND="$(command -v python3)"
  fi
  "$FOUND" --version
  echo "  $FOUND"
  echo ""
fi

if [[ "$AUTO_FIX" -eq 1 || "${INSTALL_PYTHON_AUTO_FIX:-0}" == "1" ]]; then
  echo "── Building Home-Repository/.venv and dashboard service ──"
  "$ROOT/scripts/fix_ingest_python_mac.sh"
  echo ""
  echo "All set. Open http://127.0.0.1:8080"
  exit 0
fi

echo "Next step — build project .venv and start dashboard:"
echo "  cd \"$ROOT\""
echo "  ./scripts/fix_ingest_python_mac.sh"
echo ""
echo "Or double-click: Repair Dashboard.command"
