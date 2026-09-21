<?php
declare(strict_types=1);
header('Cache-Control: no-store, private');
header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STC Owner Console</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#070b14;color:#e5e7eb;font-family:Arial,sans-serif}
.wrap{max-width:1320px;margin:auto;padding:18px}.bar,.card{background:#101827;border:1px solid #263247;border-radius:14px}
.bar{padding:14px;margin-bottom:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}.card{padding:15px}
h1{margin:0 0 4px}.muted,.small{color:#94a3b8}.small{font-size:12px}.row{display:flex;justify-content:space-between;gap:10px;margin:7px 0}.value{font-weight:700;text-align:right}
input,button,select{font:inherit;border:1px solid #334155;border-radius:9px;padding:9px;background:#0b1220;color:#e5e7eb}
input{width:100%}button{cursor:pointer}.primary{background:#1d4ed8}.danger{background:#991b1b}.safe{background:#166534}
.long,.ok{color:#22c55e}.short,.bad{color:#f87171}.wait{color:#facc15}.pill{display:inline-block;border:1px solid #334155;border-radius:999px;padding:3px 7px;margin:2px;font-size:11px}
.controls{display:grid;grid-template-columns:1fr auto auto;gap:8px}.approve{display:grid;grid-template-columns:1fr auto auto;gap:8px;margin-top:10px}
@media(max-width:700px){.controls,.approve{grid-template-columns:1fr}}
</style>
</head>
<body><div class="wrap">
<h1>STC Owner Console</h1>
<p class="muted">Human approval + manual order entry only. This page never places an order.</p>

<div class="bar">
<div class="controls">
<input id="token" type="password" autocomplete="off" placeholder="Owner token — kept only in page memory">
<button class="primary" id="refresh">Refresh</button>
<button id="notify">Enable browser alerts</button>
<button id="logout">Clear token</button>
</div>
<div id="status" class="small" style="margin-top:8px">Not connected</div>
<div id="autostatus" class="small" style="margin-top:4px">Auto refresh: OFF</div>
</div>

<div id="runtime" class="bar">Runtime controls not loaded.</div>
<div id="cards" class="grid"></div>
</div>
<script>
const $=id=>document.getElementById(id);
let snapshot=null;
let autoTimer=null;
let autoCountdown=null;
let secondsToRefresh=30;
let initializedSignals=false;
const seenSignalPlans=new Set();
function esc(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function num(x,d=4){const n=Number(x);return Number.isFinite(n)?n.toFixed(d):'-'}
function auth(){const t=$('token').value.trim();return {'Authorization':'Bearer '+t,'Content-Type':'application/json'}}
async function api(path,opts={}){const r=await fetch(path,{cache:'no-store',...opts,headers:{...auth(),...(opts.headers||{})}});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error((j&&j.error)||('HTTP '+r.status));return j}
function runtimeHtml(r){
 return '<div class="row"><span>Decision timeframe</span><span class="value">15m</span></div>'
 +'<div class="row"><span>Historical context</span><span class="value">1D / 252 trading days</span></div>'
 +'<div class="row"><span>Safe Mode</span><span class="value '+(r.safe_mode?'bad':'ok')+'">'+esc(r.safe_mode)+'</span></div>'
 +'<div class="row"><span>Kill Switch</span><span class="value '+(r.kill_switch?'bad':'ok')+'">'+esc(r.kill_switch)+'</span></div>'
 +'<div class="row"><span>Version</span><span class="value">'+esc(r.version)+'</span></div>'
 +'<div class="controls" style="margin-top:10px"><input id="reason" placeholder="Reason for control change">'
 +'<button class="safe" onclick="setControls(false,false)">Enable manual approval mode</button>'
 +'<button class="danger" onclick="setControls(true,true)">SAFE + KILL ON</button></div>'
 +'<div class="small" style="margin-top:8px">Changing controls does not execute any trade.</div>';
}
function planHtml(p){
 if(!p)return '<div class="row"><span>Locked plan</span><span class="value">None</span></div>';
 return '<div class="row"><span>Direction</span><span class="value">'+esc(p.direction||'-')+'</span></div>'
 +'<div class="row"><span>Decision TF</span><span class="value">'+esc(p.decision_timeframe||'15')+'</span></div>'
 +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_min)+' - '+num(p.entry_max)+'</span></div>'
 +'<div class="row"><span>Stop</span><span class="value">'+num(p.initial_stop)+'</span></div>'
 +'<div class="row"><span>TP1</span><span class="value">'+num(p.target1)+'</span></div>'
 +'<div class="row"><span>TP2</span><span class="value">'+num(p.target2)+'</span></div>'
 +'<div class="row"><span>Risk / unit</span><span class="value">'+num(p.risk_per_unit)+'</span></div>'
 +'<div class="row"><span>Valid until</span><span class="value">'+esc(p.valid_until||'-')+'</span></div>'
 +'<div class="small">Plan: '+esc(p.plan_id)+'</div>';
}
function cardHtml(c,i){
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,8).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const canApprove=(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan;
 return '<div class="card"><div class="row"><span>'+esc(c.symbol)+'</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
 +'<div class="row"><span>Source</span><span class="value">'+esc(c.source_time)+'</span></div>'
 +planHtml(c.locked_trade_plan)
 +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'none')+'</span></div>'
 +'<div class="row"><span>Manual ready</span><span class="value '+(c.manual_execution_ready?'ok':'bad')+'">'+esc(c.manual_execution_ready)+'</span></div>'
 +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
 +(canApprove?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current price from TradingView">'
 +'<button class="safe" onclick="approve('+i+',\'approve\')">Approve</button><button class="danger" onclick="approve('+i+',\'reject\')">Reject</button></div>'
 :'<div class="small">WAIT signals cannot be approved as orders.</div>')
 +'</div>';
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>(c.recommendation==='LONG'||c.recommendation==='SHORT')&&c.locked_trade_plan);
 if(!initializedSignals){
   for(const c of actionable){seenSignalPlans.add(String(c.locked_trade_plan.plan_id||c.signal_id))}
   initializedSignals=true;
   return;
 }
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   seenSignalPlans.add(key);
   const body=c.symbol+' • '+c.recommendation+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1);
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW LOCKED TRADE PLAN',{body,tag:key,requireInteraction:true});
   }
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
 }
}
function render(){
 const r=snapshot.runtime_control||{};
 $('runtime').innerHTML=runtimeHtml(r);
 const cards=snapshot.cards||[];
 $('cards').innerHTML=cards.map(cardHtml).join('')||'<div class="card">No analyzed signals found.</div>';
 maybeNotify(cards);
}
async function refresh(){
 if(!$('token').value.trim()){return}
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   secondsToRefresh=30;
   $('status').textContent='Connected • '+new Date().toLocaleTimeString();
   startAutoRefresh();
 }catch(e){
   $('status').textContent='Failed: '+e.message;
 }
}
function updateAutoStatus(){
 $('autostatus').textContent='Auto refresh: ON • next check in '+secondsToRefresh+'s';
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null}
 $('autostatus').textContent='Auto refresh: OFF';
}
async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if(p==='granted')new Notification('STC browser alerts enabled',{body:'You will be notified here when a new LONG/SHORT locked trade plan appears while this console is running.'});
}
async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh()}
 catch(e){alert('Control change failed: '+e.message)}
}
async function approve(i,decision){
 const c=snapshot.cards[i];
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});alert('Decision: '+r.decision);await refresh()}
 catch(e){alert('Approval failed/blocked: '+e.message);await refresh()}
}
$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('logout').onclick=()=>{stopAutoRefresh();$('token').value='';snapshot=null;initializedSignals=false;seenSignalPlans.clear();$('cards').innerHTML='';$('runtime').textContent='Runtime controls not loaded.';$('status').textContent='Token cleared';document.title='STC Owner Console'};
</script></body></html>
