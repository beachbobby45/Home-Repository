#!/bin/bash
# Shared Python resolution for Mac rhythm scripts.
# Usage (after cd to repo root):
#   ROOT="$PWD"
#   source "$ROOT/scripts/_resolve_python_env.sh"
[[ -n "${ROOT:-}" ]] || {
  echo "ERROR: set ROOT before sourcing _resolve_python_env.sh" >&2
  exit 1
}
export PYTHONNOUSERSITE=1
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/fix_ingest_python_mac.sh" 2>/dev/null || true
if ! PY="$("$ROOT/scripts/resolve_python.sh")"; then
  echo "" >&2
  echo "Trying automatic Python repair…" >&2
  if "$ROOT/scripts/fix_ingest_python_mac.sh" >&2 && PY="$("$ROOT/scripts/resolve_python.sh")"; then
    echo "Python repaired: $PY" >&2
  else
    echo "ERROR: Could not set up Python (.venv)." >&2
    echo "Double-click: scripts/Repair Dashboard.command" >&2
    echo "Or Terminal: cd \"$ROOT\" && ./scripts/fix_ingest_python_mac.sh" >&2
    exit 1
  fi
fi
export PYTHONPATH="$ROOT/src"
export PY
