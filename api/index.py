from __future__ import annotations

import os
import secrets

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from app.bridge_client import BridgeClient, BridgeClientError
from app.cloud_approval import CloudSnapshotError, cloud_readiness, read_cloud_snapshot, read_operator_snapshot
from app.competition_profiles import PROFILES
from app.community_research_plan import community_research_plan_summary
from app.research_runner import run_symbol_research
from app.shadow_promotion_registry import public_shadow_record, shadow_candidates
from app.serverless_worker import run_serverless_drain

app = FastAPI(title="STC Serverless Processor", version="0.9.0")


def _require_trigger(auth: str | None) -> None:
    expected = os.getenv("STC_TRIGGER_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="STC_TRIGGER_TOKEN is not configured")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    provided = auth.split(" ", 1)[1].strip()
    if not provided or not secrets.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.9.0",
        "runtime": "serverless",
        "execution": "manual_only",
    }


@app.post("/process")
def process_pending(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    bridge_url = os.getenv("STC_BRIDGE_URL", "").strip()
    worker_token = os.getenv("STC_WORKER_TOKEN", "").strip()
    if not bridge_url or not worker_token:
        raise HTTPException(status_code=503, detail="Bridge environment is not configured")
    worker_id = os.getenv("STC_WORKER_ID", "stc-vercel-worker")
    try:
        limit = int(os.getenv("STC_WORKER_BATCH_LIMIT", "5"))
    except ValueError:
        limit = 5
    limit = max(1, min(limit, 20))
    client = BridgeClient(bridge_url, worker_token, timeout_seconds=8.0)
    result = run_serverless_drain(
        client,
        worker_id=worker_id,
        limit=limit,
        max_batches=3,
    )
    return {"ok": True, **result.to_dict(), "execution": "manual_only"}


@app.post("/research/general-lab/plan")
def serverless_general_lab_plan(
    payload: dict,
    authorization: str | None = Header(default=None),
):
    _require_trigger(authorization)
    raw_symbols = payload.get("symbols") or []
    if not isinstance(raw_symbols, list):
        raise HTTPException(status_code=400, detail="symbols must be a list")
    symbols = tuple(dict.fromkeys(str(x).strip() for x in raw_symbols if str(x).strip()))
    if not symbols:
        raise HTTPException(status_code=400, detail="At least one General Lab symbol is required")
    if len(symbols) > 50:
        raise HTTPException(status_code=400, detail="General Lab plan supports at most 50 symbols per request")
    result = community_research_plan_summary(lab_symbols=symbols)
    result["symbols_requested"] = list(symbols)
    result["execution"] = "research_only"
    result["live_authority"] = False
    return result


@app.post("/research/general-lab/evaluate")
def serverless_general_lab_evaluate(
    payload: dict,
    authorization: str | None = Header(default=None),
):
    _require_trigger(authorization)
    symbol = str(payload.get("symbol") or "").strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="General Lab payload requires symbol")
    if not isinstance(payload.get("series"), dict):
        raise HTTPException(status_code=400, detail="General Lab payload requires exact-provider series")
    try:
        result = run_symbol_research(payload)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result["general_lab"] = True
    result["execution"] = "research_only"
    result["live_authority"] = False
    result["promotion_required"] = True
    return result


@app.get("/research/shadow-candidates")
def serverless_shadow_candidates(
    symbol: str | None = None,
    state: str | None = None,
    authorization: str | None = Header(default=None),
):
    _require_trigger(authorization)
    try:
        rows = shadow_candidates(symbol=symbol, state=state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "records": [public_shadow_record(row) for row in rows],
        "count": len(rows),
        "execution": "research_only",
        "live_authority": False,
    }


@app.get("/cloud/readiness")
def cloud_status(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    return JSONResponse(cloud_readiness(), headers={"Cache-Control": "no-store"})


@app.get("/cloud/signals")
def cloud_signals(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    bridge_url = os.getenv("STC_BRIDGE_URL", "").strip()
    worker_token = os.getenv("STC_WORKER_TOKEN", "").strip()
    if not bridge_url or not worker_token:
        raise HTTPException(status_code=503, detail="Bridge environment is not configured")
    allowed = {key: profile.allowed_symbols for key, profile in PROFILES.items()}
    try:
        snapshot = read_cloud_snapshot(
            BridgeClient(bridge_url, worker_token, timeout_seconds=8.0),
            allowed,
        )
    except (BridgeClientError, CloudSnapshotError, httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Cloud bridge readback unavailable",
            headers={"Cache-Control": "no-store"},
        ) from None
    return JSONResponse(snapshot, headers={"Cache-Control": "no-store"})


@app.get("/cloud/operator")
def cloud_operator(authorization: str | None = Header(default=None)):
    _require_trigger(authorization)
    bridge_url = os.getenv("STC_BRIDGE_URL", "").strip()
    worker_token = os.getenv("STC_WORKER_TOKEN", "").strip()
    if not bridge_url or not worker_token:
        raise HTTPException(status_code=503, detail="Bridge environment is not configured")
    allowed = {key: profile.allowed_symbols for key, profile in PROFILES.items()}
    try:
        snapshot = read_operator_snapshot(
            BridgeClient(bridge_url, worker_token, timeout_seconds=8.0),
            allowed,
        )
    except (BridgeClientError, CloudSnapshotError, httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Cloud operator readback unavailable",
            headers={"Cache-Control": "no-store"},
        ) from None
    return JSONResponse(snapshot, headers={"Cache-Control": "no-store"})


@app.get("/operator", response_class=HTMLResponse)
def operator_dashboard():
    return HTMLResponse(
        """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STC Competition Operator</title>
<style>
:root{color-scheme:dark}body{margin:0;background:#0b1020;color:#e5e7eb;font-family:Inter,Arial,sans-serif}
.wrap{max-width:1280px;margin:0 auto;padding:20px}.top{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
h1{margin:0 0 4px}.sub{color:#94a3b8;margin:0 0 18px}.panel,.card{background:#111827;border:1px solid #253047;border-radius:14px}
.panel{padding:14px;margin-bottom:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:14px}
.card{padding:16px}.row{display:flex;justify-content:space-between;gap:12px;margin:7px 0}.k{color:#94a3b8}.v{font-weight:700;text-align:right}
.long{color:#22c55e}.short{color:#f87171}.wait{color:#facc15}.ok{color:#22c55e}.bad{color:#f87171}
input,button{font:inherit;border-radius:9px;border:1px solid #334155;padding:10px;background:#0f172a;color:#e5e7eb}
input{min-width:320px;flex:1}button{cursor:pointer;background:#1d4ed8;border-color:#1d4ed8}
.small{font-size:12px;color:#94a3b8}.pill{display:inline-block;padding:3px 8px;border:1px solid #334155;border-radius:999px;margin-right:6px}
pre{white-space:pre-wrap;word-break:break-word;background:#0b1220;padding:10px;border-radius:8px;font-size:12px}
</style>
</head>
<body><div class="wrap">
<h1>STC Competition Operator</h1>
<p class="sub">Read-only authoritative cloud state. Manual approval and manual order entry only.</p>
<div class="panel">
<div class="top">
<input id="token" type="password" autocomplete="off" placeholder="Read token for this session only">
<button id="load">Refresh</button>
<span id="status" class="small">Not connected</span>
</div>
<div class="small" style="margin-top:8px">The token stays only in this page memory and is not stored by the dashboard.</div>
</div>
<div id="runtime" class="panel">Runtime state not loaded.</div>
<div id="cards" class="grid"></div>
</div>
<script>
const q=(id)=>document.getElementById(id);
function fmt(x,d=5){if(x===null||x===undefined)return "-";const n=Number(x);return Number.isFinite(n)?n.toFixed(d):String(x)}
function planRows(p){
 if(!p)return '<div class="row"><span class="k">Locked plan</span><span class="v">None</span></div>';
 return [
 ['Entry',fmt(p.entry_min)+' - '+fmt(p.entry_max)],
 ['Stop',fmt(p.initial_stop)],
 ['TP1',fmt(p.target1)],
 ['TP2',fmt(p.target2)],
 ['Plan ID',p.plan_id||'-']
 ].map(([k,v])=>'<div class="row"><span class="k">'+k+'</span><span class="v">'+v+'</span></div>').join('');
}
function render(data){
 const r=data.runtime_control||{};
 q('runtime').innerHTML='<div class="row"><span class="k">Safe Mode</span><span class="v '+(r.safe_mode?'bad':'ok')+'">'+String(r.safe_mode)+'</span></div>'
 +'<div class="row"><span class="k">Kill Switch</span><span class="v '+(r.kill_switch?'bad':'ok')+'">'+String(r.kill_switch)+'</span></div>'
 +'<div class="row"><span class="k">Runtime version</span><span class="v">'+(r.version??'-')+'</span></div>'
 +'<div class="row"><span class="k">Manual-ready cards</span><span class="v">'+(data.actionable_manual_count??0)+'</span></div>'
 +'<div class="row"><span class="k">Blocked cards</span><span class="v">'+(data.blocked_count??0)+'</span></div>';
 const newest={};
 for(const c of (data.cards||[])){ if(!newest[c.symbol] || c.source_time>newest[c.symbol].source_time)newest[c.symbol]=c; }
 q('cards').innerHTML=Object.values(newest).sort((a,b)=>a.symbol.localeCompare(b.symbol)).map(c=>{
   const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
   const blockers=(c.operational_blockers||[]).map(x=>'<span class="pill">'+x+'</span>').join(' ');
   return '<div class="card"><div class="row"><span class="k">'+c.symbol+'</span><span class="v '+cls+'">'+c.recommendation+' '+fmt(c.composite_score,2)+'</span></div>'
    +'<div class="row"><span class="k">Source time</span><span class="v">'+c.source_time+'</span></div>'
    +planRows(c.locked_trade_plan)
    +'<div class="row"><span class="k">Approval</span><span class="v">'+c.durable_approval_decision+'</span></div>'
    +'<div class="row"><span class="k">Manual execution ready</span><span class="v '+(c.manual_execution_ready?'ok':'bad')+'">'+String(c.manual_execution_ready)+'</span></div>'
    +'<div class="small" style="margin-top:10px">'+(blockers||'No operational blockers')+'</div></div>';
 }).join('');
}
async function load(){
 q('status').textContent='Loading...';
 try{
  const token=q('token').value.trim();
  const r=await fetch('/cloud/operator',{headers:{Authorization:'Bearer '+token},cache:'no-store'});
  if(!r.ok)throw new Error('HTTP '+r.status);
  const data=await r.json(); render(data); q('status').textContent='Connected • '+new Date().toLocaleTimeString();
 }catch(e){q('status').textContent='Failed: '+e.message;}
}
q('load').addEventListener('click',load);
</script></body></html>""",
        headers={"Cache-Control": "no-store"},
    )
