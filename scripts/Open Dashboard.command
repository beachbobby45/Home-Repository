#!/bin/bash
# Double-click in Finder to start http://127.0.0.1:8080 (Mac).
# Runs Python/.venv setup automatically if needed.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — open dashboard"
echo "  Folder: $ROOT"
echo ""

for s in fix_ingest_python_mac.sh resolve_python.sh ensure_dashboard_mac.sh \
         hard_restart_dashboard_mac.sh doctor_dashboard_mac.sh; do
  chmod +x "$ROOT/scripts/$s" 2>/dev/null || true
done

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Checking for updates on GitHub…"
  git -C "$ROOT" pull --ff-only origin main 2>/dev/null || echo "(Could not auto-update — OK to continue)"
  echo ""
fi

# Ensure .venv exists (same Python Terminal + Desktop app use).
if [[ ! -x "$ROOT/.venv/bin/python3" ]] || ! "$ROOT/.venv/bin/python3" -c "import pandas, numpy, uvicorn" 2>/dev/null; then
  echo "── One-time Python setup (~1–2 min) ──"
  if ! "$ROOT/scripts/fix_ingest_python_mac.sh"; then
    echo ""
    echo "Python setup failed."
    echo "Try in Terminal: brew install python@3.12"
    echo "Then run this file again."
    read -r -p "Press Enter to close…"
    exit 1
  fi
  echo ""
fi

echo "── Starting dashboard ──"
STATUS=0
if ! "$ROOT/scripts/ensure_dashboard_mac.sh"; then
  echo ""
  echo "Quick start failed — trying full restart…"
  if ! "$ROOT/scripts/hard_restart_dashboard_mac.sh"; then
    STATUS=1
  fi
fi

echo ""
if [[ "$STATUS" -ne 0 ]]; then
  echo "── Dashboard doctor ──"
  "$ROOT/scripts/doctor_dashboard_mac.sh" || true
  echo ""
  if [[ -f "$ROOT/data/dashboard.log" ]]; then
    echo "── Last lines of data/dashboard.log ──"
    tail -25 "$ROOT/data/dashboard.log" 2>/dev/null || true
    echo ""
  fi
  echo "Copy ALL text above and send for help."
  echo "Or try: ./scripts/fix_ingest_python_mac.sh in Terminal"
else
  echo "Dashboard should be open at http://127.0.0.1:8080"
  echo "Header: v0.9.0 · Phase 1B  (Cmd+Shift+R if old version shows)"
fi

read -r -p "Press Enter to close this window…"
exit "$STATUS"
