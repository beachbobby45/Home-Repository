#!/bin/bash
# Morning / mid-morning health ping: LaunchAgents + paper equity + optional email.
#
# Usage:
#   ./scripts/run_morning_health_mac.sh
#   ./scripts/run_morning_health_mac.sh --force-notify   # email even when OK
#   ./scripts/run_morning_health_mac.sh --no-notify      # checks only (API-style)

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

FORCE_NOTIFY=0
NO_NOTIFY=0
for arg in "$@"; do
  case "$arg" in
    --force-notify) FORCE_NOTIFY=1 ;;
    --no-notify) NO_NOTIFY=1 ;;
    -h|--help)
      echo "Usage: $0 [--force-notify|--no-notify]"
      exit 0
      ;;
  esac
done

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1
if [[ "$FORCE_NOTIFY" -eq 1 ]]; then
  export NOTIFY_ON_SUCCESS=1
fi

echo ""
echo "  AI Investment Agent — morning health"
echo "  Folder: $ROOT"
echo "  Python: $PY ($("$PY" --version 2>&1))"
echo ""

SEND_NOTIFY=1
if [[ "$NO_NOTIFY" -eq 1 ]]; then
  SEND_NOTIFY=0
fi

"$PY" - <<PY
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))
from investment_agent.db import connect, init_db
from investment_agent.execution.health_check import run_health_check

conn = connect(init_db())
try:
    result = run_health_check(conn, send_notify=bool(${SEND_NOTIFY}))
    print(result["body"])
    print("")
    if result.get("notify"):
        n = result["notify"]
        print(f"Notify: ok={n.get('ok')} emailed={n.get('emailed')} banner={n.get('banner')}")
        print(f"  detail: {n.get('detail')}")
        print(f"  log: {n.get('logged')}")
    else:
        print("Notify: skipped (OK and NOTIFY_ON_SUCCESS!=1, or --no-notify)")
    sys.exit(0 if result.get("ok") else 1)
finally:
    conn.close()
PY
