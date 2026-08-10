#!/bin/bash
# Start dashboard for Cursor Cloud / dev VM (port 8080).
set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
mkdir -p "$ROOT/data"

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env" 2>/dev/null || true
fi

if [[ ! -f "$ROOT/data/agent.db" ]]; then
  PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.demo_seed import seed_demo_db; seed_demo_db()" 2>/dev/null || true
fi

pip install -q -r "$ROOT/requirements.txt" 2>/dev/null || true

export PYTHONPATH="$ROOT/src"
echo "Dashboard: http://127.0.0.1:8080 (use Cursor Ports tab if remote)"
exec python3 "$ROOT/scripts/run_dashboard.py" --host 0.0.0.0 --port 8080
