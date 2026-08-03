"""FastAPI dashboard — Phase 3–6 (queue, journal, goal, sweeps, monitor, learning, CIO, scenario)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from investment_agent.account import (
    apply_month_end_sweep,
    build_dashboard_summary,
    get_tax_rate,
    set_setting,
    summary_to_dict,
)
from investment_agent.cio import build_cio_summary
from investment_agent.config import Settings
from investment_agent.historical import (
    build_historical_summary,
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    pull_historical_data,
)
from investment_agent.learning import (
    generate_learning_report,
    get_learning_report,
    get_or_generate_learning_report,
    list_learning_report_dates,
    save_learning_report,
)
from investment_agent.period_screener import (
    build_ranked_candidates,
    get_latest_screener_run,
    promote_ticker_to_queue,
    run_period_screener,
    save_screener_run,
    date_range_for_period,
)
from investment_agent.db import connect, init_db
from investment_agent.journal import insert_trade, list_trades, trade_to_dict
from investment_agent.scenario import build_scenario_visualizer
from investment_agent.watchlist import (
    compute_universe_stats,
    deactivate_ticker,
    get_active_watchlist_details,
    import_tickers,
    list_presets,
    load_preset_into_watchlist,
)
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
from investment_agent.trading_day import (
    build_trading_day_status,
    clear_pinned_pick,
    pin_top_pick,
    refresh_live_quotes,
    validate_planned_trade,
)

DASHBOARD_DIR = Path(__file__).resolve().parent
REPO_ROOT = DASHBOARD_DIR.parents[2]
ONE_PAGER_PDF = REPO_ROOT / "docs" / "DASHBOARD_ONE_PAGER.pdf"
templates = Jinja2Templates(directory=str(DASHBOARD_DIR / "templates"))

app = FastAPI(title="AI Investment Agent Dashboard", version="0.8.0")


class NoCacheDashboardMiddleware(BaseHTTPMiddleware):
    """Avoid stale dashboard HTML/JS/CSS in the browser during active development."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response


app.add_middleware(NoCacheDashboardMiddleware)
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


class WatchlistImportBody(BaseModel):
    tickers: list[str]


class LoadPresetBody(BaseModel):
    preset: str
    replace: bool = False


class PeriodScreenerBody(BaseModel):
    period_days: int = 14
    min_days_screened: int = 1
    min_hit_rate_pct: float | None = None
    save: bool = True


class PinPickBody(BaseModel):
    ticker: str


class ValidateTradeBody(BaseModel):
    ticker: str
    price: float = Field(gt=0)
    shares: float | None = Field(default=None, gt=0)


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


@app.get("/one-pager.pdf")
def one_pager_pdf() -> FileResponse:
    if not ONE_PAGER_PDF.is_file():
        raise HTTPException(status_code=404, detail="One-pager PDF not found")
    return FileResponse(
        ONE_PAGER_PDF,
        media_type="application/pdf",
        filename="AI-Investment-Agent-Daily-One-Pager.pdf",
    )


@app.get("/api/config")
def api_config() -> dict[str, bool]:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    return {
        "api_key_required": bool(key and key != "change-me-to-a-random-secret"),
    }


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "api_key_required": bool(key and key != "change-me-to-a-random-secret"),
        },
    )


@app.get("/api/scenario/visualizer")
def api_scenario_visualizer(
    conn=Depends(_db),
    projection_months: int = 120,
) -> dict[str, Any]:
    return build_scenario_visualizer(conn, projection_horizon=projection_months)


@app.get("/api/cio/summary")
def api_cio_summary(conn=Depends(_db)) -> dict[str, Any]:
    return build_cio_summary(conn)


@app.get("/api/learning/report")
def api_learning_report(
    conn=Depends(_db),
    date: str | None = None,
) -> dict[str, Any]:
    return get_or_generate_learning_report(conn, report_date=date)


@app.get("/api/learning/history")
def api_learning_history(conn=Depends(_db), limit: int = 30) -> dict[str, Any]:
    return {"dates": list_learning_report_dates(conn, limit=limit)}


@app.post("/api/learning/generate")
def api_learning_generate(
    conn=Depends(_db),
    date: str | None = None,
    _: None = Depends(_require_api_key),
) -> dict:
    report = generate_learning_report(conn, report_date=date)
    report_id = save_learning_report(conn, report)
    conn.commit()
    return {"ok": True, "id": report_id, "report": report}


@app.get("/api/historical/summary")
def api_historical_summary(conn=Depends(_db)) -> dict[str, Any]:
    return build_historical_summary(conn)


@app.get("/api/historical/evaluate")
def api_historical_evaluate(
    conn=Depends(_db),
    date: str | None = None,
) -> dict[str, Any]:
    if date:
        return evaluate_trading_day(conn, date)
    result = evaluate_prior_day(conn)
    if result is None:
        raise HTTPException(status_code=404, detail="No historical bars — run historical pull first")
    return result


@app.get("/api/historical/period")
def api_historical_period(
    start_date: str,
    end_date: str,
    conn=Depends(_db),
) -> dict[str, Any]:
    return evaluate_period(conn, start_date, end_date)


@app.post("/api/historical/pull")
def api_historical_pull(
    conn=Depends(_db),
    lookback_days: int = 60,
    _: None = Depends(_require_api_key),
) -> dict:
    settings = Settings.from_env()
    result = pull_historical_data(settings, db_path=None, lookback_days=lookback_days)
    conn.commit()
    return result


@app.get("/api/summary")
def api_summary(conn=Depends(_db)) -> dict[str, Any]:
    summary = build_dashboard_summary(conn)
    return summary_to_dict(summary)


@app.get("/api/trading-day/status")
def api_trading_day_status(conn=Depends(_db)) -> dict[str, Any]:
    return build_trading_day_status(conn)


@app.post("/api/trading-day/refresh")
def api_trading_day_refresh(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    settings = Settings.from_env()
    refresh = refresh_live_quotes(conn, settings)
    if refresh.get("ok"):
        conn.commit()
    status = build_trading_day_status(conn)
    return {"refresh": refresh, "status": status}


@app.post("/api/trading-day/validate")
def api_trading_day_validate(
    body: ValidateTradeBody,
    conn=Depends(_db),
) -> dict:
    return validate_planned_trade(
        conn,
        ticker=body.ticker,
        planned_price=body.price,
        shares=body.shares,
    )


@app.post("/api/trading-day/pin-pick")
def api_trading_day_pin(
    body: PinPickBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = pin_top_pick(conn, body.ticker)
    conn.commit()
    return {**result, "status": build_trading_day_status(conn)}


@app.post("/api/trading-day/clear-pin")
def api_trading_day_clear_pin(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = clear_pinned_pick(conn)
    conn.commit()
    return {**result, "status": build_trading_day_status(conn)}


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


@app.get("/api/watchlist")
def api_watchlist(conn=Depends(_db)) -> dict[str, Any]:
    return {
        "tickers": get_active_watchlist_details(conn),
        "count": len(get_active_watchlist_details(conn)),
    }


@app.get("/api/watchlist/presets")
def api_watchlist_presets() -> list[dict[str, Any]]:
    return [
        {"name": p.name, "description": p.description, "ticker_count": p.ticker_count}
        for p in list_presets()
    ]


@app.get("/api/watchlist/stats")
def api_watchlist_stats(conn=Depends(_db)) -> dict[str, Any]:
    return compute_universe_stats(conn)


@app.post("/api/watchlist/load-preset")
def api_load_preset(
    body: LoadPresetBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = load_preset_into_watchlist(conn, body.preset, replace=body.replace)
    conn.commit()
    return result


@app.post("/api/watchlist/import")
def api_watchlist_import(
    body: WatchlistImportBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = import_tickers(conn, body.tickers)
    conn.commit()
    return result


@app.delete("/api/watchlist/{ticker}")
def api_watchlist_remove(
    ticker: str,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = deactivate_ticker(conn, ticker)
    conn.commit()
    return result


@app.get("/api/screener/ranked")
def api_screener_ranked(
    conn=Depends(_db),
    period_days: int = 14,
) -> dict[str, Any]:
    return build_ranked_candidates(conn, period_days=period_days)


@app.post("/api/screener/period")
def api_screener_period(
    body: PeriodScreenerBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    start, end = date_range_for_period(body.period_days)
    result = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        min_days_screened=body.min_days_screened,
        min_hit_rate_pct=body.min_hit_rate_pct,
    )
    if body.save:
        run_id = save_screener_run(conn, result)
        conn.commit()
        result["saved_run_id"] = run_id
    return result


@app.get("/api/screener/period/latest")
def api_screener_period_latest(conn=Depends(_db)) -> dict[str, Any]:
    result = get_latest_screener_run(conn)
    if result is None:
        return {"candidates": [], "summary": {}}
    return result


@app.post("/api/screener/promote/{ticker}")
def api_screener_promote(
    ticker: str,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    result = promote_ticker_to_queue(conn, ticker)
    if result.get("ok"):
        conn.commit()
    return result
