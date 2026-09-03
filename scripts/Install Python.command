#!/bin/bash
# Double-click: install Python 3.12 (if needed) + build .venv + start dashboard.
cd "$(dirname "$0")/.." || exit 1
export INSTALL_PYTHON_AUTO_FIX=1
exec ./scripts/install_python_mac.sh --fix
