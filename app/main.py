from __future__ import annotations

from contextlib import asynccontextmanager
import hashlib
import json
from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .analysis import analyze
from .approval import revalidate_envelope
from .execution_context import derive_execution_context
from .data_capabilities import get_capability, validate_provider_mapping
from .competition_profiles import PROFILES, get_profile
from .models import (
    CompetitionEligibilityRequest,
    FactorScores,
    OrderValidationRequest,
    ProviderMappingCheckRequest,
    SignalEvaluationRequest,
    TechnicalAnalysisRequest,
    TradingViewWebhook,
    TradeEvent,
    TradeEventResult,
    ApprovalRevalidationRequest,
)
from .risk import competition_eligibility, validate_order
from .readiness import build_readiness
from .signals import evaluate, factors_from_tradingview
from .storage import (
    competition_trade_summary,
    init_db,
    log_event,
    recent_signals,
    record_webhook_once,
    record_trade_event,
    save_signal,
    summary,
    bridge_inbox_summary,
    get_approval_envelope,
    record_revalidation,
    get_runtime_control,
    set_runtime_control,
    get_execution_evidence,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="STC Competition Engine", version="0.9.0", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html><head><title>STC v0.9</title></head>
    <body style='font-family:Arial;max-width:900px;margin:40px auto;line-height:1.5'>
    <h1>STC Competition Engine v0.9</h1>
    <p>Rule-aware paper-trading competition assistant. Recommendations require human approval.</p>
    <ul>
      <li><a href='/docs'>Interactive API</a></li>
      <li><a href='/competitions'>Competition profiles</a></li>
      <li><a href='/state/summary'>Local audit summary</a></li>
    </ul>
    <p><strong>No real-money execution is implemented.</strong></p>
    </body></html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.9.0", "human_approval_required": True}


@app.get("/competitions")
def competitions():
    return {
        k: {
            "competition_id": v.competition_id,
            "name": v.name,
            "start_utc": v.start_utc,
            "end_utc": v.end_utc,
            "registration_close_utc": v.registration_close_utc,
            "initial_balance_usd": v.initial_balance_usd,
            "min_trading_days": v.min_trading_days,
            "first_prize_usd": v.first_prize_usd,
            "scoring_basis": v.scoring_basis,
            "allowed_symbols_count": len(v.allowed_symbols),
            "source_url": v.source_url,
        }
        for k, v in PROFILES.items()
    }


@app.get("/competitions/{competition_id}")
def competition(competition_id: str):
    try:
        p = get_profile(competition_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    result = asdict(p)
    result["allowed_symbols"] = list(p.allowed_symbols)
    return result


@app.get("/data/capabilities/{symbol:path}")
def data_capabilities(symbol: str):
    return get_capability(symbol).to_dict()


@app.post("/data/provider-check")
def provider_check(req: ProviderMappingCheckRequest):
    allowed, reason = validate_provider_mapping(
        req.requested_symbol, req.candidate_symbol, req.allow_cross_provider
    )
    return {
        "allowed": allowed,
        "requested_symbol": req.requested_symbol,
        "candidate_symbol": req.candidate_symbol,
        "reason": reason,
    }


@app.post("/analysis/technical")
def technical(req: TechnicalAnalysisRequest):
    result = analyze(req.symbol, req.bars)
    log_event("technical_analysis", result.model_dump(), symbol=req.symbol)
    return result


@app.post("/signals/evaluate")
def evaluate_signal(req: SignalEvaluationRequest):
    try:
        result = evaluate(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    save_signal(result.model_dump())
    log_event("signal_created", result.model_dump(), req.competition_id, req.symbol)
    return result


@app.get("/signals/{signal_id}/approval-card")
def approval_card(signal_id: str):
    card = get_approval_envelope(signal_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Approval envelope not found")
    card["runtime_control"] = get_runtime_control()
    card["execution"] = "manual_only"
    return card


@app.post("/signals/{signal_id}/approve")
def approve(signal_id: str, req: ApprovalRevalidationRequest):
    card = get_approval_envelope(signal_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Approval envelope not found")
    control = get_runtime_control()
    quote_evidence = get_execution_evidence(req.quote_evidence_id)
    market_evidence = get_execution_evidence(req.market_evidence_id)
    derived = derive_execution_context(card["envelope"], quote_evidence, market_evidence)
    current = req.model_dump(exclude={"quote_evidence_id", "market_evidence_id"})
    current.update(derived)
    current["safe_mode"] = current["safe_mode"] or control["safe_mode"]
    current["kill_switch"] = current["kill_switch"] or control["kill_switch"]
    result = revalidate_envelope(card["envelope"], current)
    result["execution_context"] = derived
    record_revalidation(signal_id, result)
    log_event("signal_approval_revalidation", {"signal_id": signal_id, "result": result})
    return {"signal_id": signal_id, "approved": bool(result["valid"]), "revalidation": result, "execution": "manual_only"}


@app.get("/readiness")
def readiness():
    return build_readiness(get_runtime_control())


@app.get("/runtime-control")
def runtime_control():
    return get_runtime_control()


@app.post("/runtime-control")
def update_runtime_control(payload: dict):
    allowed = {"safe_mode", "kill_switch", "reason"}
    if any(k not in allowed for k in payload):
        raise HTTPException(status_code=400, detail="Unsupported runtime-control field")
    result = set_runtime_control(payload.get("safe_mode"), payload.get("kill_switch"), payload.get("reason"))
    log_event("runtime_control_changed", result)
    return result


@app.post("/rules/validate-order")
def validate(req: OrderValidationRequest):
    try:
        result = validate_order(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    log_event("order_validation", {"request": req.model_dump(), "result": result.model_dump()}, req.competition_id, req.symbol)
    return result


@app.post("/competition/eligibility")
def eligibility(req: CompetitionEligibilityRequest):
    try:
        result = competition_eligibility(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result


@app.post("/webhooks/tradingview")
def tradingview_webhook(payload: TradingViewWebhook):
    try:
        p = get_profile(payload.competition_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if payload.symbol not in p.max_open_position:
        raise HTTPException(status_code=400, detail="Symbol is not allowed in this competition")

    payload_dict = payload.model_dump(mode="json")
    event_id = payload.event_id
    if not event_id:
        canonical = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"), default=str)
        event_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    receipt = record_webhook_once(event_id, payload_dict, payload.competition_id, payload.symbol)
    if not receipt["is_new"]:
        log_event(
            "tradingview_webhook_duplicate",
            {"event_id": event_id, "duplicate_count": receipt["duplicate_count"]},
            payload.competition_id,
            payload.symbol,
        )
        return {
            "received": True,
            "duplicate": True,
            "event_id": event_id,
            "duplicate_count": receipt["duplicate_count"],
            "execution": "no_duplicate_processing",
        }

    technical = factors_from_tradingview(payload)
    req = SignalEvaluationRequest(
        competition_id=payload.competition_id,
        symbol=payload.symbol,
        factors=FactorScores(technical=technical),
    )
    result = evaluate(req)
    save_signal(result.model_dump())
    log_event(
        "tradingview_webhook",
        {"event_id": event_id, "payload": payload_dict},
        payload.competition_id,
        payload.symbol,
    )
    return {
        "received": True,
        "duplicate": False,
        "event_id": event_id,
        "signal": result,
        "execution": "manual_approval_required",
    }



@app.get("/signals")
def list_signals(limit: int = 20):
    return {"signals": recent_signals(limit)}


@app.post("/trade-events", response_model=TradeEventResult)
def trade_event(event: TradeEvent):
    try:
        profile = get_profile(event.competition_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if event.symbol not in profile.max_open_position:
        raise HTTPException(status_code=400, detail="Symbol is not allowed in this competition")
    data = event.model_dump()
    result = record_trade_event(data)
    log_event("trade_event", data, event.competition_id, event.symbol)
    return TradeEventResult(
        trade_id=result["trade_id"],
        recorded=True,
        status=result["status"],
        competition_id=event.competition_id,
        symbol=event.symbol,
        realized_pnl_total=result["realized_pnl_total"],
        qualifying_trading_days=result["qualifying_trading_days"],
    )


@app.get("/competition/{competition_id}/trade-summary")
def trade_summary(competition_id: str):
    try:
        profile = get_profile(competition_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    result = competition_trade_summary(competition_id)
    result["minimum_days_required"] = profile.min_trading_days
    result["eligible_by_days"] = result["qualifying_trading_days"] >= profile.min_trading_days
    result["days_remaining"] = max(0, profile.min_trading_days - result["qualifying_trading_days"])
    return result


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>STC Dashboard</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f5f6f8;color:#111827}.wrap{max-width:1100px;margin:0 auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px}h1,h2{margin-top:0}.muted{color:#6b7280}.pill{display:inline-block;padding:4px 9px;border-radius:999px;background:#eef2ff}input,select,button{font:inherit;padding:10px;border:1px solid #d1d5db;border-radius:8px;margin:4px 0;width:100%;box-sizing:border-box}button{cursor:pointer;background:#111827;color:white}.ok{color:#047857}.bad{color:#b91c1c}pre{white-space:pre-wrap;word-break:break-word;background:#f9fafb;padding:10px;border-radius:8px}</style>
</head><body><div class='wrap'>
<h1>STC Competition Dashboard <span class='pill'>v0.9</span></h1>
<p class='muted'>Competition-rule engine, signals, audit trail, and human approval. No real-money execution.</p>
<div class='grid'><div class='card'><h2>Competitions</h2><div id='competitions'>Loading...</div></div>
<div class='card'><h2>Order rule check</h2>
<select id='comp'><option value='capital-africa-sep-2026'>Capital.com Africa</option><option value='amp-futures-sep-2026'>AMP Futures</option></select>
<input id='symbol' value='CAPITALCOM:XAUUSD' placeholder='Symbol'>
<input id='qty' type='number' value='1' step='any' placeholder='Quantity'>
<input id='current' type='number' value='0' step='any' placeholder='Current open quantity'>
<input id='tx' type='number' value='0' placeholder='Transactions last 60 sec'>
<input id='equity' type='number' value='100000' placeholder='Equity'>
<input id='risk' type='number' value='500' placeholder='Risk amount'>
<button id='check'>Validate proposal</button><pre id='orderResult'></pre></div>
<div class='card'><h2>Recent signals</h2><div id='signals'>No signals yet.</div></div></div>
</div><script>
async function load(){
 const c=await fetch('/competitions').then(r=>r.json());
 document.getElementById('competitions').innerHTML=Object.values(c).map(x=>`<p><b>${x.name}</b><br>Balance: $${x.initial_balance_usd.toLocaleString()}<br>Min days: ${x.min_trading_days}<br>Symbols: ${x.allowed_symbols_count}<br>First prize: $${x.first_prize_usd.toLocaleString()}</p>`).join('');
 const s=await fetch('/signals').then(r=>r.json());
 document.getElementById('signals').innerHTML=s.signals.length?s.signals.map(x=>`<p><b>${x.symbol}</b> — ${x.recommendation} (${Number(x.composite_score).toFixed(2)}) ${x.approved?'APPROVED':'PENDING'}</p>`).join(''):'No signals yet.';
}
document.getElementById('check').addEventListener('click',async()=>{
 const body={competition_id:comp.value,symbol:symbol.value,side:'BUY',requested_quantity:Number(qty.value),current_open_quantity:Number(current.value),transactions_last_60s:Number(tx.value),account_equity:Number(equity.value),risk_amount:Number(risk.value),max_risk_fraction:0.02};
 const r=await fetch('/rules/validate-order',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
 const j=await r.json(); orderResult.textContent=JSON.stringify(j,null,2); orderResult.className=j.allowed?'ok':'bad';
}); load();
</script></body></html>
    """


@app.get("/state/summary")
def state_summary():
    return {**summary(), "bridge_inbox": bridge_inbox_summary()}
