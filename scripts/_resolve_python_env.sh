#!/bin/bash
# Shared Python resolution for Mac rhythm scripts.
# Usage (after cd to repo root):
#   ROOT="$PWD"
#   source "$ROOT/scripts/_resolve_python_env.sh"
[[ -n "${ROOT:-}" ]] || {
  echo "ERROR: set ROOT before sourcing _resolve_python_env.sh" >&2
  exit 1
}
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/fix_ingest_python_mac.sh" 2>/dev/null || true
if ! PY="$("$ROOT/scripts/resolve_python.sh")"; then
  echo "" >&2
  echo "ERROR: Could not set up Python (.venv)." >&2
  echo "Run: cd \"$ROOT\" && ./scripts/fix_ingest_python_mac.sh" >&2
  echo "Or double-click: scripts/Fix Ingest Python.command" >&2
  exit 1
fi
export PYTHONPATH="$ROOT/src"
