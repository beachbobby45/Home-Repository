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
chmod +x "$ROOT/scripts/find_desktop_python.sh" 2>/dev/null || true
PY="$("$ROOT/scripts/find_desktop_python.sh" 2>/dev/null || true)"
if [[ -n "$PY" ]]; then
  ok "Python with tkinter: $PY ($("$PY" --version 2>&1))"
else
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
  if [[ -f "$DESKTOP_APP/Contents/Resources/python.path" ]]; then
    PP="$(tr -d '\r\n' < "$DESKTOP_APP/Contents/Resources/python.path")"
    if [[ -x "$PP" ]] && "$PP" -c "import tkinter" 2>/dev/null; then
      ok "python.path pinned: $PP"
    else
      bad "python.path invalid: $PP — reinstall: ./scripts/build_mac_desktop_app.sh --desktop"
    fi
  else
    warn "python.path missing (old build) — reinstall: ./scripts/build_mac_desktop_app.sh --desktop"
  fi
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
