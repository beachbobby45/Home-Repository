#!/bin/bash
# Diagnose why AI Investment Agent.app flashes and does not open (Mac).
set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
LOG="$HOME/.investment_agent/desktop-app.log"

echo "=== Desktop app doctor ==="
echo "Repo: $ROOT"
echo ""

fail=0
ok() { echo "OK:   $*"; }
bad() { echo "FAIL: $*"; fail=1; }
warn() { echo "WARN: $*"; }

# Python + tkinter
PY=""
for candidate in /usr/bin/pythonw /usr/bin/python3 pythonw3 pythonw python3; do
  if [[ -x "$candidate" ]] || command -v "$candidate" >/dev/null 2>&1; then
    cmd="$candidate"
    [[ -x "$candidate" ]] || cmd="$(command -v "$candidate")"
    if "$cmd" -c "import tkinter" 2>/dev/null; then
      ok "Python with tkinter: $cmd ($("$cmd" --version 2>&1))"
      PY="$cmd"
      break
    fi
  fi
done
if [[ -z "$PY" ]]; then
  bad "No Python with tkinter — install: brew install python-tk@3.12"
fi

# Project import
if [[ -n "$PY" ]]; then
  if PYTHONPATH="$ROOT/src" "$PY" -c "from investment_agent.desktop_status import format_last_run" 2>/dev/null; then
    ok "investment_agent imports"
  else
    bad "investment_agent import failed:"
    PYTHONPATH="$ROOT/src" "$PY" -c "from investment_agent.desktop_status import format_last_run" 2>&1 | tail -3
  fi
fi

# Desktop app bundle
DESKTOP_APP="$HOME/Desktop/AI Investment Agent.app"
REPO_APP="$ROOT/desktop/AI Investment Agent.app"
if [[ -d "$DESKTOP_APP" ]]; then
  ok "Desktop app exists: $DESKTOP_APP"
  if [[ -f "$DESKTOP_APP/Contents/Resources/repo.path" ]]; then
    RP="$(tr -d '\r\n' < "$DESKTOP_APP/Contents/Resources/repo.path")"
    if [[ -f "$RP/scripts/run_dashboard.py" ]]; then
      ok "repo.path points to valid repo: $RP"
    else
      bad "repo.path invalid: $RP — reinstall: ./scripts/build_mac_desktop_app.sh --desktop"
    fi
  else
    bad "repo.path missing inside app — reinstall"
  fi
elif [[ -d "$REPO_APP" ]]; then
  warn "App not on Desktop; built at $REPO_APP"
  echo "      Install: ./scripts/build_mac_desktop_app.sh --desktop"
else
  warn "App not built — run: ./scripts/build_mac_desktop_app.sh --desktop"
fi

# Launch test
if [[ -n "$PY" ]]; then
  if PYTHONPATH="$ROOT/src" "$PY" -m py_compile "$ROOT/scripts/desktop_helper.py" 2>/dev/null; then
    ok "desktop_helper.py syntax OK"
  else
    bad "desktop_helper.py has syntax errors"
  fi
fi

echo ""
if [[ -f "$LOG" ]]; then
  echo "Last lines of $LOG:"
  tail -15 "$LOG"
else
  echo "No log yet at $LOG (app has not been launched since logging was added)"
fi

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Doctor: all checks passed. Try opening the Desktop app again."
  echo "If it still fails, run: open -a \"AI Investment Agent\"  then check the log above."
else
  echo "Doctor: fix the FAIL items above, then reinstall:"
  echo "  ./scripts/build_mac_desktop_app.sh --desktop"
fi
exit "$fail"
