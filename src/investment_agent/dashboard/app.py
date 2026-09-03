"""FastAPI dashboard — Phase 3–6 (queue, journal, goal, sweeps, monitor, learning, CIO, scenario)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from investment_agent.account import (
    apply_period_sweep,
    build_dashboard_summary,
    format_journal_notes,
    get_tax_rate,
    get_trading_mode,
    set_setting,
    set_trading_mode,
    summary_to_dict,
)
from investment_agent.cio import build_cio_summary
from investment_agent.config import Settings
from investment_agent.version import version_info
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.historical import (
    build_historical_summary,
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    pull_historical_data,
)
from investment_agent.operator_day_log import (
    OUTCOME_ATTENDED_ONLY,
    OUTCOME_PASS_NO_SETUP,
    build_attendance_summary,
    get_operator_day,
    list_operator_days,
    record_operator_day_from_journal,
    record_operator_day_manual,
    today_et_str,
)
from investment_agent.learning import (
    generate_learning_report,
    get_learning_report,
    get_or_generate_learning_report,
    list_learning_report_dates,
    save_learning_report,
)
from investment_agent.close_report import (
    generate_daily_close_report,
    generate_weekly_close_report,
    get_or_generate_daily_close,
    get_or_generate_weekly_close,
    list_close_report_dates,
    save_close_report,
    save_rank_snapshot,
)
from investment_agent.period_screener import (
    build_ranked_candidates,
    get_latest_screener_run,
    list_trading_dates,
    promote_ticker_to_queue,
    run_period_screener,
    save_screener_run,
    date_range_for_period,
)
from investment_agent.db import connect, init_db, get_active_watchlist
from investment_agent.db_maintenance import (
    assert_db_available_for_writes,
    ingest_lock_active,
    ingest_lock_message,
    repair_database,
)
from investment_agent.journal import (
    clear_all_trades,
    insert_trade,
    list_trades,
    resolve_executed_at,
    trade_to_dict,
)
from investment_agent.growth_projection import build_ten_year_growth_plan
from investment_agent.scenario import build_scenario_visualizer
from investment_agent.watchlist import (
    add_special_watch_ticker,
    build_special_watch_report,
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
from investment_agent.ingest import run_ingest
from investment_agent.screen_actions import (
    ACTION_PERIOD_SCREENER,
    ACTION_REFRESH_RANKED,
    get_screen_action_status,
    record_screen_action,
)
from investment_agent.trading_day import (
    build_trading_day_status,
    clear_pinned_pick,
    pin_top_pick,
    refresh_live_quotes,
    today_et_str,
    validate_planned_trade,
)
from investment_agent.ai_service import ai_service_status
from investment_agent.capital_builder import (
    build_capital_builder_progress,
    progress_to_dict,
)
from investment_agent.risk_engine import (
    build_portfolio_snapshot,
    is_kill_switch_active,
    portfolio_status_dict,
    set_kill_switch,
    auto_engaged_kill_switch,
)
from investment_agent.trade_proposal import (
    REJECTION_REASONS,
    approve_proposal,
    generate_proposals,
    get_proposal,
    list_proposals_for_session,
    mark_proposal_executed,
    reject_proposal,
    validate_journal_buy_proposal,
)
from investment_agent.daily_rhythm import (
    build_trading_candidates,
    get_daily_rhythm_status,
    ingest_schedule_installed,
)

DASHBOARD_DIR = Path(__file__).resolve().parent
REPO_ROOT = DASHBOARD_DIR.parents[2]
ONE_PAGER_PDF = REPO_ROOT / "docs" / "DASHBOARD_ONE_PAGER.pdf"
OPERATOR_CHECKLIST_PDF = REPO_ROOT / "docs" / "DAILY_OPERATOR_CHECKLIST.pdf"
templates = Jinja2Templates(directory=str(DASHBOARD_DIR / "templates"))

app = FastAPI(title="AI Investment Agent Dashboard", version=version_info()["version"])


@app.exception_handler(sqlite3.OperationalError)
def sqlite_operational_error_handler(_request: Request, exc: sqlite3.OperationalError) -> JSONResponse:
    msg = str(exc).lower()
    if "locked" in msg:
        detail = (
            "Database is locked — pause the dashboard and run ingest from Terminal: "
            "./scripts/run_ingest_mac.sh"
        )
        status = 503
    elif "no such column" in msg:
        detail = "Database schema out of date — run: ./scripts/repair_dashboard_mac.sh"
        status = 500
    else:
        detail = f"Database error: {exc}"
        status = 500
    return JSONResponse(status_code=status, content={"detail": detail})


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
    executed_date: str | None = None
    executed_time_pt: str | None = None
    notes: str | None = None
    queue_id: int | None = None
    proposal_id: int | None = None


class TaxRateUpdate(BaseModel):
    tax_rate: float = Field(ge=0, le=1)


class TradingModeUpdate(BaseModel):
    mode: str


class QueueStateUpdate(BaseModel):
    state: str


class WatchlistImportBody(BaseModel):
    tickers: list[str]


class LoadPresetBody(BaseModel):
    preset: str
    replace: bool = False


class SpecialWatchAddBody(BaseModel):
    preset: str = "datacenter_us"
    ticker: str


class PeriodScreenerBody(BaseModel):
    period_days: int = 14
    min_days_screened: int = 1
    min_hit_rate_pct: float | None = None
    save: bool = True


class PinPickBody(BaseModel):
    ticker: str


class KillSwitchBody(BaseModel):
    active: bool


class ProposalRejectBody(BaseModel):
    reason_code: str
    reason_text: str | None = None


class ProposalGenerateBody(BaseModel):
    replace_existing: bool = False
    max_proposals: int = Field(default=5, ge=1, le=5)


class ValidateTradeBody(BaseModel):
    ticker: str
    price: float = Field(gt=0)
    shares: float | None = Field(default=None, gt=0)


class IngestRunBody(BaseModel):
    incremental: bool = False
    lookback_days: int = 60
    stale_hours: float = 20.0


class ScreenActionRecordBody(BaseModel):
    action: str = ACTION_REFRESH_RANKED


class OperatorDayLogBody(BaseModel):
    outcome: str
    session_date_et: str | None = None
    notes: str | None = None


class OperatorDayNoTradeBody(BaseModel):
    session_date_et: str | None = None
    notes: str | None = None


# Browser ingest is unreliable with large watchlists (DB lock, Finnhub rate limits, timeouts).
BROWSER_INGEST_MAX_TICKERS = 150


def _db():
    init_db()
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


_LOCAL_API_HOSTS = frozenset({"127.0.0.1", "::1", "localhost", "testclient"})


def _require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    if not key or key == "change-me-to-a-random-secret":
        return
    client_host = (request.client.host if request.client else "") or ""
    if client_host in _LOCAL_API_HOSTS:
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


@app.get("/operator-checklist.pdf")
def operator_checklist_pdf() -> FileResponse:
    if not OPERATOR_CHECKLIST_PDF.is_file():
        raise HTTPException(status_code=404, detail="Operator checklist PDF not found")
    return FileResponse(
        OPERATOR_CHECKLIST_PDF,
        media_type="application/pdf",
        filename="AI-Investment-Agent-Daily-Operator-Checklist.pdf",
    )


@app.get("/api/config")
def api_config() -> dict[str, bool]:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    return {
        "api_key_required": bool(key and key != "change-me-to-a-random-secret"),
    }


@app.get("/api/version")
def api_version() -> dict[str, str]:
    return version_info()


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    settings = Settings.from_env()
    key = settings.app_api_key.strip()
    info = version_info()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "api_key_required": bool(key and key != "change-me-to-a-random-secret"),
            "app_version": info["version"],
            "app_version_label": info["label"],
            "app_release": info["release"],
            "app_release_tag": info["tag"],
        },
    )


@app.get("/api/scenario/visualizer")
def api_scenario_visualizer(
    conn=Depends(_db),
    projection_months: int = 120,
) -> dict[str, Any]:
    return build_scenario_visualizer(conn, projection_horizon=projection_months)


@app.get("/api/growth-plan/ten-year")
def api_growth_plan_ten_year() -> dict[str, Any]:
    """Year 1–10 projection: $15K base vs +$10K injection at ~month 6."""
    return build_ten_year_growth_plan()


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


@app.get("/api/close/daily")
def api_close_daily(
    conn=Depends(_db),
    date: str | None = None,
    refresh: bool = False,
    fetch_10_et: bool = True,
) -> dict[str, Any]:
    report = get_or_generate_daily_close(
        conn,
        report_date=date,
        regenerate=refresh,
        fetch_10_et=fetch_10_et,
    )
    conn.commit()
    return report


@app.get("/api/close/weekly")
def api_close_weekly(
    conn=Depends(_db),
    end: str | None = None,
    refresh: bool = False,
    fetch_10_et: bool = False,
) -> dict[str, Any]:
    report = get_or_generate_weekly_close(
        conn,
        end_date=end,
        regenerate=refresh,
        fetch_10_et=fetch_10_et,
    )
    conn.commit()
    return report


@app.get("/api/close/history")
def api_close_history(
    conn=Depends(_db),
    report_type: str = "daily",
    limit: int = 30,
) -> dict[str, Any]:
    return {"dates": list_close_report_dates(conn, report_type=report_type, limit=limit)}


@app.post("/api/close/daily/generate")
def api_close_daily_generate(
    conn=Depends(_db),
    date: str | None = None,
    fetch_10_et: bool = True,
    _: None = Depends(_require_api_key),
) -> dict:
    report = generate_daily_close_report(conn, date, fetch_10_et=fetch_10_et)
    report_id = save_close_report(conn, report)
    conn.commit()
    return {"ok": True, "id": report_id, "report": report}


@app.post("/api/close/snapshot-rank")
def api_close_snapshot_rank(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    """Freeze current top-20 rank for today's date (call after 10:00 ET)."""
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"][:20]
    from investment_agent.trading_day import today_et_str

    day = today_et_str()
    save_rank_snapshot(conn, day, ranked)
    conn.commit()
    return {"ok": True, "snapshot_date": day, "count": len(ranked)}


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


@app.get("/api/trading-day/snapshots")
def api_trading_day_snapshots(
    conn=Depends(_db),
    session_date_et: str | None = None,
) -> dict[str, Any]:
    from investment_agent.quote_snapshots import get_session_snapshot_status

    return get_session_snapshot_status(conn, session_date_et)


@app.get("/api/trading-day/market-activity")
def api_trading_day_market_activity(
    conn=Depends(_db),
    session_date_et: str | None = None,
) -> dict[str, Any]:
    from investment_agent.market_activity import (
        evaluate_market_activity,
        list_recent_evaluations,
        market_activity_to_dict,
    )
    from investment_agent.trading_day import today_et_str

    day = session_date_et or today_et_str()
    result = market_activity_to_dict(evaluate_market_activity(conn, persist=False))
    result["recent_evaluations"] = list_recent_evaluations(conn, day, limit=5)
    return result


@app.get("/api/market-activity/daily-breakdown")
def api_market_activity_daily_breakdown(
    conn=Depends(_db),
    days: int = 14,
    since: str | None = None,
) -> dict[str, Any]:
    from investment_agent.market_activity import TRADE_MIN, list_daily_breakdowns

    rows = list_daily_breakdowns(conn, days=days, since=since)
    return {
        "days": rows,
        "trade_min": TRADE_MIN,
        "count": len(rows),
    }


@app.get("/api/trading-day/confirmation")
def api_trading_day_confirmation(
    conn=Depends(_db),
    session_date_et: str | None = None,
) -> dict[str, Any]:
    from investment_agent.confirmation import (
        confirmations_to_dict,
        evaluate_session_confirmations,
        list_recent_confirmations,
    )
    from investment_agent.market_activity import evaluate_market_activity, market_activity_to_dict
    from investment_agent.trading_day import today_et_str

    day = session_date_et or today_et_str()
    market_activity = market_activity_to_dict(evaluate_market_activity(conn, persist=False))
    confirmations = confirmations_to_dict(
        evaluate_session_confirmations(conn, market_activity=market_activity)
    )
    return {
        "session_date_et": day,
        "market_activity": market_activity,
        "confirmations": confirmations,
        "recent_evaluations": list_recent_confirmations(conn, day, limit=9),
    }


@app.get("/api/daily-rhythm/status")
def api_daily_rhythm_status(conn=Depends(_db)) -> dict[str, Any]:
    return get_daily_rhythm_status(conn)


@app.get("/api/daily-rhythm/candidates")
def api_daily_rhythm_candidates(
    conn=Depends(_db),
    limit: int = 15,
    period_days: int = 14,
) -> dict[str, Any]:
    return {
        "candidates": build_trading_candidates(
            conn, limit=min(max(limit, 1), 30), period_days=period_days
        ),
        "period_days": period_days,
    }


@app.post("/api/daily-rhythm/prepare-morning")
def api_prepare_morning(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    """Step 2 — run screener and return trade candidates with size / sell / stop."""
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    start, end = date_range_for_period(14, conn=conn)
    trading_dates = list_trading_dates(conn, count=14)
    from investment_agent.account import build_dashboard_summary

    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or ORIGINAL_BASIS)
    result = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        tradable_cash=deploy,
        min_days_screened=1,
        min_hit_rate_pct=None,
        trading_dates=trading_dates or None,
        requested_trading_days=14,
    )
    run_id = save_screener_run(conn, result)
    record_screen_action(
        conn,
        ACTION_PERIOD_SCREENER,
        detail=f"{len(result.get('candidates', []))} candidates · 14 trading days",
    )
    conn.commit()
    candidates = build_trading_candidates(conn, limit=15, period_days=14)
    status = build_trading_day_status(conn)
    rhythm = get_daily_rhythm_status(conn)
    return {
        "ok": True,
        "saved_run_id": run_id,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "trading_day": status,
        "rhythm": rhythm,
    }


@app.get("/api/health/db")
def api_health_db(conn=Depends(_db)) -> dict[str, Any]:
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        return {
            "ok": integrity == "ok",
            "integrity": integrity,
            "ingest_running": ingest_lock_active(),
        }
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail=f"Database error: {exc}") from exc


@app.post("/api/trading-day/refresh")
def api_trading_day_refresh(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    settings = Settings.from_env()
    try:
        refresh = refresh_live_quotes(conn, settings)
        if refresh.get("ok"):
            conn.commit()
        status = build_trading_day_status(conn)
        return {"refresh": refresh, "status": status}
    except sqlite3.OperationalError as exc:
        conn.rollback()
        msg = str(exc).lower()
        if "locked" in msg:
            detail = (
                "Database is locked — stop Terminal ingest or close duplicate dashboard "
                "windows, then run ./scripts/repair_dashboard_mac.sh"
            )
        else:
            detail = f"Database error: {exc} — run ./scripts/repair_dashboard_mac.sh"
        raise HTTPException(status_code=503, detail=detail) from exc
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Refresh live failed: {exc}") from exc


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


@app.get("/api/risk/status")
def api_risk_status(conn=Depends(_db)) -> dict[str, Any]:
    snapshot = build_portfolio_snapshot(conn)
    auto_engaged = auto_engaged_kill_switch(conn, snapshot)
    if auto_engaged:
        conn.commit()
        snapshot = build_portfolio_snapshot(conn)
    status = portfolio_status_dict(snapshot)
    status["auto_kill_switch_engaged"] = auto_engaged
    return status


@app.post("/api/risk/kill-switch")
def api_risk_kill_switch(
    body: KillSwitchBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    set_kill_switch(conn, body.active)
    conn.commit()
    snapshot = build_portfolio_snapshot(conn)
    return {
        "ok": True,
        "kill_switch_active": is_kill_switch_active(conn),
        "status": portfolio_status_dict(snapshot),
    }


@app.get("/api/capital-builder/progress")
def api_capital_builder_progress(conn=Depends(_db)) -> dict[str, Any]:
    progress = build_capital_builder_progress(conn)
    return progress_to_dict(progress)


@app.get("/api/ai/status")
def api_ai_status(conn=Depends(_db)) -> dict[str, Any]:
    return ai_service_status(conn, today_et_str())


@app.get("/api/proposals/today")
def api_proposals_today(conn=Depends(_db)) -> dict[str, Any]:
    proposals = list_proposals_for_session(conn)
    return {
        "proposals": proposals,
        "rejection_reasons": REJECTION_REASONS,
        "count": len(proposals),
        "ai_status": ai_service_status(conn, today_et_str()),
    }


@app.get("/api/proposals/{proposal_id}")
def api_proposal_detail(proposal_id: int, conn=Depends(_db)) -> dict[str, Any]:
    proposal = get_proposal(conn, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@app.post("/api/proposals/generate")
def api_proposals_generate(
    body: ProposalGenerateBody | None = None,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    opts = body or ProposalGenerateBody()
    settings = Settings.from_env()
    try:
        result = generate_proposals(
            conn,
            max_proposals=opts.max_proposals,
            replace_existing=opts.replace_existing,
            settings=settings,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Proposal generate failed: {exc}",
        ) from exc
    if not result.get("ok", True):
        raise HTTPException(status_code=409, detail=result.get("error") or "Proposal generate blocked")
    conn.commit()
    return result


@app.post("/api/proposals/{proposal_id}/approve")
def api_proposal_approve(
    proposal_id: int,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    settings = Settings.from_env()
    result = approve_proposal(conn, proposal_id, settings=settings)
    if result.get("ok"):
        conn.commit()
    elif result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/proposals/{proposal_id}/reject")
def api_proposal_reject(
    proposal_id: int,
    body: ProposalRejectBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    result = reject_proposal(
        conn,
        proposal_id,
        reason_code=body.reason_code,
        reason_text=body.reason_text,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Reject failed"))
    conn.commit()
    return result


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
    mode = get_trading_mode(conn)
    try:
        executed_at = resolve_executed_at(
            executed_at=body.executed_at,
            executed_date=body.executed_date,
            executed_time_pt=body.executed_time_pt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if body.proposal_id is not None:
        check = validate_journal_buy_proposal(
            conn,
            proposal_id=body.proposal_id,
            ticker=body.ticker,
            side=body.side,
        )
        if not check.get("ok"):
            raise HTTPException(status_code=400, detail=check.get("error", "Invalid proposal"))

    exceptional_snapshot = None
    if body.side.upper() == "BUY":
        from investment_agent.trading_day import build_trading_day_status

        exceptional_snapshot = build_trading_day_status(conn)

    trade_id = insert_trade(
        conn,
        ticker=body.ticker,
        side=body.side,
        shares=body.shares,
        price=body.price,
        fee=body.fee,
        executed_at=executed_at,
        notes=format_journal_notes(body.notes, mode),
        queue_id=body.queue_id,
        proposal_id=body.proposal_id,
    )
    if body.proposal_id is not None and body.side.upper() == "BUY":
        mark_proposal_executed(conn, body.proposal_id, trade_id)
    if exceptional_snapshot and body.side.upper() == "BUY":
        exc = exceptional_snapshot.get("exceptional_trade") or {}
        if exc.get("active"):
            from investment_agent.exceptional_trade import log_exceptional_trade_consumed
            from investment_agent.quote_snapshots import today_et_str

            log_exceptional_trade_consumed(
                conn,
                session_date_et=today_et_str(),
                ticker=body.ticker,
                journal_buy_id=trade_id,
                market_activity=exceptional_snapshot.get("market_activity") or {},
                confirmation_score=exc.get("confirmation_score"),
                notes="Exceptional override consumed on journal BUY",
            )
    from investment_agent.operator_day_log import (
        record_operator_day_from_journal,
        session_date_et_from_executed_at,
    )

    session_day = (
        session_date_et_from_executed_at(executed_at)
        if executed_at
        else today_et_str()
    )
    operator_day_result = record_operator_day_from_journal(conn, session_day)
    conn.commit()
    return {
        "ok": True,
        "id": trade_id,
        "trading_mode": mode,
        "proposal_id": body.proposal_id,
        "operator_day": operator_day_result.get("entry"),
    }


@app.get("/api/operator-day-log")
def api_operator_day_log_list(
    conn=Depends(_db),
    limit: int = 60,
    since: str | None = None,
) -> dict[str, Any]:
    return {
        "entries": list_operator_days(conn, limit=min(max(limit, 1), 365), since=since),
    }


@app.get("/api/operator-day-log/summary")
def api_operator_day_log_summary(
    conn=Depends(_db),
    since: str | None = None,
) -> dict[str, Any]:
    return build_attendance_summary(conn, since=since)


@app.get("/api/operator-day-log/{session_date_et}")
def api_operator_day_log_get(session_date_et: str, conn=Depends(_db)) -> dict[str, Any]:
    entry = get_operator_day(conn, session_date_et)
    if not entry:
        raise HTTPException(status_code=404, detail="No operator day log for this date")
    return entry


@app.post("/api/operator-day-log")
def api_operator_day_log_create(
    body: OperatorDayLogBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    try:
        result = record_operator_day_manual(
            conn,
            outcome=body.outcome,
            session_date_et=body.session_date_et,
            notes=body.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    conn.commit()
    return result


@app.post("/api/operator-day-log/no-trade")
def api_operator_day_log_no_trade(
    body: OperatorDayNoTradeBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    result = record_operator_day_manual(
        conn,
        outcome="NO_TRADE",
        session_date_et=body.session_date_et,
        notes=body.notes,
    )
    conn.commit()
    return result


@app.post("/api/operator-day-log/check-in")
def api_operator_day_log_check_in(
    body: OperatorDayNoTradeBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    result = record_operator_day_manual(
        conn,
        outcome=OUTCOME_ATTENDED_ONLY,
        session_date_et=body.session_date_et,
        notes=body.notes,
    )
    conn.commit()
    return result


@app.post("/api/operator-day-log/pass")
def api_operator_day_log_pass(
    body: OperatorDayNoTradeBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    result = record_operator_day_manual(
        conn,
        outcome=OUTCOME_PASS_NO_SETUP,
        session_date_et=body.session_date_et,
        notes=body.notes,
    )
    conn.commit()
    return result


@app.post("/api/journal/clear")
def api_journal_clear(
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    removed = clear_all_trades(conn)
    conn.commit()
    return {"ok": True, "removed": removed}


@app.get("/api/settings/trading-mode")
def api_get_trading_mode(conn=Depends(_db)) -> dict:
    return {"mode": get_trading_mode(conn)}


@app.put("/api/settings/trading-mode")
def api_set_trading_mode(
    body: TradingModeUpdate,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    try:
        mode = set_trading_mode(conn, body.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    conn.commit()
    return {"ok": True, "mode": mode}


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
    result = apply_period_sweep(conn)
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


@app.get("/api/screen/actions")
def api_screen_actions(conn=Depends(_db)) -> dict[str, Any]:
    return {"actions": get_screen_action_status(conn)}


@app.post("/api/screen/actions/record")
def api_screen_action_record(
    body: ScreenActionRecordBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    try:
        record_screen_action(conn, body.action, detail="Dashboard refresh")
        conn.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    status = get_screen_action_status(conn).get(body.action, {})
    return {"ok": True, "action": status}


@app.get("/api/watchlist/special-watch")
def api_special_watch(
    conn=Depends(_db),
    preset: str = "datacenter_us",
) -> dict[str, Any]:
    try:
        return build_special_watch_report(conn, preset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/watchlist/special-watch/add")
def api_special_watch_add(
    body: SpecialWatchAddBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict[str, Any]:
    try:
        result = add_special_watch_ticker(conn, body.preset, body.ticker)
        conn.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/watchlist/load-preset")
def api_load_preset(
    body: LoadPresetBody,
    conn=Depends(_db),
    _: None = Depends(_require_api_key),
) -> dict:
    try:
        result = load_preset_into_watchlist(conn, body.preset, replace=body.replace)
        conn.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/ingest/preflight")
def api_ingest_preflight(conn=Depends(_db)) -> dict[str, Any]:
    if ingest_lock_active():
        return {
            "ticker_count": len(get_active_watchlist(conn)),
            "missing_api_keys": False,
            "browser_ok": False,
            "recommend_terminal": True,
            "ingest_running": True,
            "message": ingest_lock_message(),
            "terminal_command": "./scripts/run_ingest_mac.sh --incremental",
            "terminal_command_full": "./scripts/run_ingest_mac.sh",
        }
    symbols = get_active_watchlist(conn)
    settings = Settings.from_env()
    missing_keys = not (settings.fred_api_key and settings.finnhub_api_key)
    count = len(symbols)
    return {
        "ticker_count": count,
        "missing_api_keys": missing_keys,
        "browser_ok": count <= BROWSER_INGEST_MAX_TICKERS and not missing_keys,
        "recommend_terminal": count > BROWSER_INGEST_MAX_TICKERS,
        "ingest_running": False,
        "terminal_command": "./scripts/run_ingest_mac.sh --incremental",
        "terminal_command_full": "./scripts/run_ingest_mac.sh",
    }


@app.post("/api/ingest/run")
def api_ingest_run(
    body: IngestRunBody | None = None,
    _: None = Depends(_require_api_key),
) -> dict:
    settings = Settings.from_env()
    if not settings.fred_api_key or not settings.finnhub_api_key:
        raise HTTPException(
            status_code=503,
            detail="FRED_API_KEY and FINNHUB_API_KEY required in .env — restart dashboard after editing .env",
        )
    opts = body or IngestRunBody()
    if ingest_lock_active():
        raise HTTPException(status_code=503, detail=ingest_lock_message())
    try:
        assert_db_available_for_writes()
        check_conn = connect(init_db())
        try:
            ticker_count = len(get_active_watchlist(check_conn))
        finally:
            check_conn.close()
        if ticker_count > BROWSER_INGEST_MAX_TICKERS:
            mode = " --incremental" if opts.incremental else ""
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Watchlist has {ticker_count} tickers — browser ingest supports up to "
                    f"{BROWSER_INGEST_MAX_TICKERS}. In Terminal run: "
                    f"cd ~/Home-Repository && ./scripts/run_ingest_mac.sh{mode}"
                ),
            )
        return run_ingest(
            settings,
            incremental=opts.incremental,
            lookback_days=opts.lookback_days,
            stale_hours=opts.stale_hours,
        )
    except HTTPException:
        raise
    except sqlite3.OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database is locked — use Terminal instead (pauses background service): "
                "./scripts/run_ingest_mac.sh --incremental"
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc


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
    start, end = date_range_for_period(body.period_days, conn=conn)
    trading_dates = list_trading_dates(conn, count=body.period_days)
    result = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        min_days_screened=body.min_days_screened,
        min_hit_rate_pct=body.min_hit_rate_pct,
        trading_dates=trading_dates or None,
        requested_trading_days=body.period_days,
    )
    if body.save:
        run_id = save_screener_run(conn, result)
        record_screen_action(
            conn,
            ACTION_PERIOD_SCREENER,
            detail=f"{len(result.get('candidates', []))} candidates · {body.period_days} trading days",
        )
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
