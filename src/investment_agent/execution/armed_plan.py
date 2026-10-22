"""Day's armed trade plan (propose → arm → submit → filled → flat)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


class AllocationMode(str, Enum):
    SINGLE_TOP1 = "single_top1"
    BEST_TRADABLE_TOP3 = "best_tradable_top3"
    DUAL_LOT_TOP2 = "dual_lot_top2"


class PlanStatus(str, Enum):
    PROPOSED = "proposed"
    ARMED = "armed"
    SUBMITTED = "submitted"
    FILLED = "filled"
    FLAT = "flat"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REJECTED = "rejected"


@dataclass
class ArmedLeg:
    """One lot leg (#1 or #2)."""

    rank: int
    ticker: str
    limit_buy: float
    limit_sell: float
    stop: float
    shares: int
    deploy: float
    avg_range_pct: float | None = None


@dataclass
class ArmedPlan:
    session_date_et: str
    allocation_mode: AllocationMode
    status: PlanStatus
    legs: list[ArmedLeg]
    plan_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    day_gate_mode: str | None = None
    allow_trade: bool | None = None
    ma_score: int | None = None
    equity_snapshot: float | None = None
    pdt_cap: int | None = None
    pdt_used: int | None = None
    arm_deadline_et: str | None = None
    fill_deadline_et: str = "11:30"
    notes: str | None = None
    selection_audit: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None
    id: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "plan_uuid": self.plan_uuid,
            "session_date_et": self.session_date_et,
            "allocation_mode": self.allocation_mode.value
            if isinstance(self.allocation_mode, AllocationMode)
            else self.allocation_mode,
            "status": self.status.value if isinstance(self.status, PlanStatus) else self.status,
            "legs": [asdict(leg) for leg in self.legs],
            "day_gate_mode": self.day_gate_mode,
            "allow_trade": self.allow_trade,
            "ma_score": self.ma_score,
            "equity_snapshot": self.equity_snapshot,
            "pdt_cap": self.pdt_cap,
            "pdt_used": self.pdt_used,
            "arm_deadline_et": self.arm_deadline_et,
            "fill_deadline_et": self.fill_deadline_et,
            "notes": self.notes,
        }
        if self.selection_audit is not None:
            payload["selection_audit"] = self.selection_audit
        return payload

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict) -> ArmedPlan:
        d = dict(row)
        payload = json.loads(d["payload_json"])
        legs = [ArmedLeg(**leg) for leg in payload.get("legs") or []]
        return cls(
            id=d.get("id"),
            plan_uuid=d["plan_uuid"],
            session_date_et=d["session_date_et"],
            allocation_mode=AllocationMode(d["allocation_mode"]),
            status=PlanStatus(d["status"]),
            legs=legs,
            day_gate_mode=d.get("day_gate_mode"),
            allow_trade=bool(d["allow_trade"]) if d.get("allow_trade") is not None else None,
            ma_score=d.get("ma_score"),
            equity_snapshot=d.get("equity_snapshot"),
            pdt_cap=d.get("pdt_cap"),
            pdt_used=d.get("pdt_used"),
            arm_deadline_et=d.get("arm_deadline_et"),
            fill_deadline_et=d.get("fill_deadline_et") or "11:30",
            notes=d.get("notes"),
            selection_audit=payload.get("selection_audit"),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )


def _now_et() -> str:
    return datetime.now(ET).replace(microsecond=0).isoformat()


def save_armed_plan(conn: sqlite3.Connection, plan: ArmedPlan) -> int:
    now = _now_et()
    plan.created_at = plan.created_at or now
    plan.updated_at = now
    payload = json.dumps(plan.to_payload())
    mode = (
        plan.allocation_mode.value
        if isinstance(plan.allocation_mode, AllocationMode)
        else plan.allocation_mode
    )
    status = plan.status.value if isinstance(plan.status, PlanStatus) else plan.status
    cur = conn.execute(
        """
        INSERT INTO armed_plans (
          plan_uuid, session_date_et, allocation_mode, status,
          day_gate_mode, allow_trade, ma_score, equity_snapshot,
          pdt_cap, pdt_used, arm_deadline_et, fill_deadline_et,
          payload_json, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(plan_uuid) DO UPDATE SET
          status = excluded.status,
          allow_trade = excluded.allow_trade,
          ma_score = excluded.ma_score,
          equity_snapshot = excluded.equity_snapshot,
          pdt_cap = excluded.pdt_cap,
          pdt_used = excluded.pdt_used,
          arm_deadline_et = excluded.arm_deadline_et,
          fill_deadline_et = excluded.fill_deadline_et,
          payload_json = excluded.payload_json,
          notes = excluded.notes,
          updated_at = excluded.updated_at
        """,
        (
            plan.plan_uuid,
            plan.session_date_et,
            mode,
            status,
            plan.day_gate_mode,
            None if plan.allow_trade is None else (1 if plan.allow_trade else 0),
            plan.ma_score,
            plan.equity_snapshot,
            plan.pdt_cap,
            plan.pdt_used,
            plan.arm_deadline_et,
            plan.fill_deadline_et,
            payload,
            plan.notes,
            plan.created_at,
            plan.updated_at,
        ),
    )
    if plan.id is None:
        row = conn.execute(
            "SELECT id FROM armed_plans WHERE plan_uuid = ?",
            (plan.plan_uuid,),
        ).fetchone()
        plan.id = int(row["id"]) if row else int(cur.lastrowid)
    return int(plan.id)


def get_armed_plan_for_session(
    conn: sqlite3.Connection,
    session_date_et: str,
) -> ArmedPlan | None:
    row = conn.execute(
        """
        SELECT * FROM armed_plans
        WHERE session_date_et = ?
        ORDER BY updated_at DESC, id DESC
        LIMIT 1
        """,
        (session_date_et,),
    ).fetchone()
    return ArmedPlan.from_row(row) if row else None


def set_armed_plan_status(
    conn: sqlite3.Connection,
    plan_uuid: str,
    status: PlanStatus | str,
) -> None:
    st = status.value if isinstance(status, PlanStatus) else status
    conn.execute(
        """
        UPDATE armed_plans
        SET status = ?, updated_at = ?
        WHERE plan_uuid = ?
        """,
        (st, _now_et(), plan_uuid),
    )
