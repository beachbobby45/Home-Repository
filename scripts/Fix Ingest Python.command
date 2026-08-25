#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
exec ./scripts/fix_ingest_python_mac.sh
