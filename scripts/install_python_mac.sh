#!/bin/bash
# Install Python 3.12+ via Homebrew (Mac) — required for numpy 1.26 / pandas 2.
set -euo pipefail

echo "=== Install Python for AI Investment Agent ==="
echo ""

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Use Python 3.9+ from your package manager."
  exit 1
fi

export PATH="/opt/homebrew/bin:/opt/homebrew/opt/python@3.12/bin:/usr/local/bin:$PATH"

_have_python39() {
  local py="$1"
  [[ -x "$py" ]] && "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null
}

for py in \
  /opt/homebrew/bin/python3 \
  /opt/homebrew/opt/python@3.12/bin/python3 \
  /usr/local/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
do
  if _have_python39 "$py"; then
    echo "OK: usable Python already installed:"
    "$py" --version
    echo "  $py"
    echo ""
    echo "Next: cd ~/Home-Repository && ./scripts/fix_ingest_python_mac.sh"
    exit 0
  fi
done

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is not installed."
  echo ""
  echo "Option A — install Homebrew (recommended), then re-run this script:"
  echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  echo ""
  echo "Option B — install Python from python.org (3.12+), then run:"
  echo "  cd ~/Home-Repository && ./scripts/fix_ingest_python_mac.sh"
  exit 1
fi

echo "Installing python@3.12 (one time, ~2 min)…"
brew install python@3.12
echo ""
echo "Adding Homebrew Python to PATH for this session…"
export PATH="/opt/homebrew/opt/python@3.12/bin:/opt/homebrew/bin:$PATH"
/opt/homebrew/bin/python3 --version || python3 --version
echo ""
echo "Next steps:"
echo "  cd ~/Home-Repository"
echo "  ./scripts/fix_ingest_python_mac.sh"
echo "  ./scripts/doctor_ingest_mac.sh"
