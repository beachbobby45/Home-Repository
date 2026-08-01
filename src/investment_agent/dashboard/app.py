"""FastAPI dashboard — Phase 3–5 (queue, journal, goal, sweeps, monitor, learning, CIO)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from investment_agent.account import (
    apply_month_end_sweep,
    build_dashboard_summary,
    get_tax_rate,
    set_setting,
    summary_to_dict,
)
from investment_agent.cio import build_cio_summary
from investment_agent.config import Settings
from investment_agent.learning import (
    generate_learning_report,
    get_learning_report,
    get_or_generate_learning_report,
    save_learning_report,
)
from investment_agent.db import connect, init_db
from investment_agent.journal import insert_trade, list_trades, trade_to_dict
from investment_agent.monitor import (
    acknowledge_alert,
    enrich_queue_item,
    get_latest_quotes,
    list_active_alerts,
    run_monitor_cycle,
)
from investment_agent.stock_team import (
    advance_queue_state,
    card_to_dict,
    list_queue,
    screen_candidates,
    set_queue_state,
    sync_queue_from_screener,
)

DASHBOARD_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(DASHBOARD_DIR / "templates"))

app = FastAPI(title="AI Investment Agent Dashboard", version="0.5.0")
app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR / "static")), name="static")


class TradeCreate(BaseModel):
    ticker: str
    side: str
    shares: float = Field(gt=0)
    price: float = Field(gt=0)
    fee: float | None = None
    executed_at: str | None = None
    notes: str | None = None
    queue_id: int | None = None


class TaxRateUpdate(BaseModel):
    tax_rate: float = Field(ge=0, le=1)


class QueueStateUpdate(BaseModel):
    state: str


def _db():
    init_db()
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


def _require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    if not key or key == "change-me-to-a-random-secret":
        return
    if x_api_key != key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request},
    )


@app.get("/api/cio/summary")
def api_cio_summary(conn=Depends(_db)) -> dict[str, Any]:
    return build_cio_summary(conn)


@app.get("/api/learning/report")
def api_learning_report(conn=Depends(_db)) -> dict[str, Any]:
    report = get_or_generate_learning_report(conn)
    return report


@app.post("/api/learning/generate")
def api_learning_generate(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    report = generate_learning_report(conn)
    report_id = save_learning_report(conn, report)
    conn.commit()
    return {"ok": True, "id": report_id, "report": report}


@app.get("/api/summary")
def api_summary(conn=Depends(_db)) -> dict[str, Any]:
    summary = build_dashboard_summary(conn)
    return summary_to_dict(summary)


@app.get("/api/queue")
def api_queue(conn=Depends(_db)) -> list[dict]:
    quotes = get_latest_quotes(conn)
    items = list_queue(conn)
    return [enrich_queue_item(conn, item, quotes) for item in items]


@app.get("/api/alerts")
def api_alerts(conn=Depends(_db)) -> list[dict]:
    return list_active_alerts(conn)


@app.post("/api/monitor/run")
def api_monitor_run(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = run_monitor_cycle(conn)
    conn.commit()
    return result


@app.post("/api/alerts/{alert_id}/acknowledge")
def api_ack_alert(
    alert_id: int,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = acknowledge_alert(conn, alert_id)
    if result.get("ok"):
        conn.commit()
    return result


@app.get("/api/candidates")
def api_candidates(conn=Depends(_db)) -> list[dict]:
    return [card_to_dict(c) for c in screen_candidates(conn)]


@app.post("/api/queue/sync")
def api_queue_sync(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = sync_queue_from_screener(conn)
    conn.commit()
    return result


@app.post("/api/queue/{item_id}/advance")
def api_queue_advance(
    item_id: int,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = advance_queue_state(conn, item_id)
    if result.get("ok"):
        conn.commit()
    return result


@app.post("/api/queue/{item_id}/state")
def api_queue_set_state(
    item_id: int,
    body: QueueStateUpdate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = set_queue_state(conn, item_id, body.state)
    if result.get("ok"):
        conn.commit()
    return result


@app.get("/api/journal")
def api_journal(conn=Depends(_db)) -> list[dict]:
    return [trade_to_dict(t) for t in list_trades(conn)]


@app.post("/api/journal")
def api_journal_create(
    body: TradeCreate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    trade_id = insert_trade(
        conn,
        ticker=body.ticker,
        side=body.side,
        shares=body.shares,
        price=body.price,
        fee=body.fee,
        executed_at=body.executed_at,
        notes=body.notes,
        queue_id=body.queue_id,
    )
    conn.commit()
    return {"ok": True, "id": trade_id}


@app.put("/api/settings/tax-rate")
def api_tax_rate(
    body: TaxRateUpdate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    set_setting(conn, "tax_reserve_rate", str(body.tax_rate))
    conn.commit()
    return {"ok": True, "tax_rate": get_tax_rate(conn)}


@app.post("/api/sweeps/apply")
def api_apply_sweep(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = apply_month_end_sweep(conn)
    if result.get("ok"):
        conn.commit()
    return result
