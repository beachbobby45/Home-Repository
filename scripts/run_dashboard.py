#!/usr/bin/env python3
"""Start the Phase 3 dashboard (FastAPI + uvicorn)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run investment agent dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--reload", action="store_true", help="Dev auto-reload")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn not installed — run: pip install -r requirements.txt")
        sys.exit(2)

    uvicorn.run(
        "investment_agent.dashboard.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
