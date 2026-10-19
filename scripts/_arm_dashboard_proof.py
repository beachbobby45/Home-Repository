"""Dashboard proof for arm_unattended_mac.sh — ranks / #1 / paper log APIs."""

from __future__ import annotations

import json
import os
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def get(path: str) -> dict:
    with urllib.request.urlopen(f"http://127.0.0.1:8080{path}", timeout=20) as r:
        return json.loads(r.read().decode())


def main() -> int:
    day = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    ok_all = True
    notes: list[str] = []
    pick = None
    ranked_n = 0

    try:
        paper = get("/api/paper/status")
        eq = (paper.get("balances") or {}).get("gate_approved", {}).get("equity")
        notes.append(f"paper_status ok equity={eq}")
    except Exception as e:  # noqa: BLE001
        ok_all = False
        notes.append(f"paper_status FAIL: {e}")

    try:
        sessions = get("/api/paper/sessions?limit=5")
        notes.append(f"paper_sessions ok count={sessions.get('count')}")
    except Exception as e:  # noqa: BLE001
        ok_all = False
        notes.append(f"paper_sessions FAIL: {e}")

    try:
        td = get("/api/trading-day/status")
        if isinstance(td.get("pick"), dict):
            pick = td["pick"].get("ticker")
        pick = pick or td.get("ranked_first")
        if pick:
            notes.append(f"trading_day #1={pick}")
        else:
            notes.append("trading_day has no #1 yet (ranks may still be loading)")
    except Exception as e:  # noqa: BLE001
        notes.append(f"trading_day/status unavailable: {e}")

    try:
        ranked = get("/api/screener/ranked")
        rows = ranked.get("rows") or ranked.get("ranked") or ranked.get("items") or []
        if isinstance(rows, list) and rows:
            ranked_n = len(rows)
            notes.append(f"screener/ranked rows={ranked_n}")
            if not pick and isinstance(rows[0], dict):
                pick = rows[0].get("ticker")
        else:
            notes.append("screener/ranked returned no rows (will check DB snapshot)")
    except Exception as e:  # noqa: BLE001
        notes.append(f"screener/ranked unavailable: {e}")

    try:
        db = os.environ.get("DB_PATH") or str(Path("data") / "agent.db")
        if Path(db).is_file():
            conn = sqlite3.connect(db)
            n = conn.execute(
                "SELECT COUNT(*) AS n FROM rank_snapshots WHERE snapshot_date = ?",
                (day,),
            ).fetchone()[0]
            conn.close()
            ranked_n = max(ranked_n, int(n or 0))
            if n > 0:
                notes.append(f"rank_snapshots today={n}")
            else:
                notes.append("rank_snapshots today=0")
        else:
            ok_all = False
            notes.append(f"db missing: {db}")
    except Exception as e:  # noqa: BLE001
        ok_all = False
        notes.append(f"rank check FAIL: {e}")

    if ranked_n <= 0:
        ok_all = False

    print("PROOF_OK" if ok_all else "PROOF_FAIL")
    for line in notes:
        print(line)
    if pick:
        print(f"NUMBER_ONE={pick}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
