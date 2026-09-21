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
.bar{padding:14px;margin-bottom:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:14px}.card{padding:15px}
h1{margin:0 0 4px}.muted,.small{color:#94a3b8}.small{font-size:12px}.row{display:grid;grid-template-columns:minmax(105px,0.72fr) minmax(0,1.28fr);gap:12px;align-items:start;margin:7px 0}.value{font-weight:700;text-align:left;overflow-wrap:anywhere}.statusline{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}.badge{display:inline-block;border:1px solid #334155;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:700}.badge.active{border-color:#166534;background:#052e16;color:#86efac}.badge.expired{border-color:#991b1b;background:#450a0a;color:#fca5a5}.badge.blocked{border-color:#854d0e;background:#422006;color:#fde047}.orderbox{background:#0b1220;border:1px solid #334155;border-radius:10px;padding:10px;margin:10px 0}.orderbox .ordername{font-size:16px;font-weight:800}.countdown{font-variant-numeric:tabular-nums}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.tab{background:#0b1220;border:1px solid #334155;border-radius:10px;padding:10px 14px;color:#cbd5e1;cursor:pointer}.tab.active{background:#1d4ed8;border-color:#1d4ed8;color:#fff}.tabcount{font-size:11px;opacity:.8;margin-left:5px}
.hidden{display:none!important}.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}.summary .card{min-height:90px}.big{font-size:24px;font-weight:800}.sectiontitle{font-weight:800;margin:0 0 8px}.generalbox{display:grid;grid-template-columns:1fr 1fr;gap:10px}.generalbox textarea{width:100%;min-height:90px;background:#0b1220;color:#e5e7eb;border:1px solid #334155;border-radius:9px;padding:9px;font:inherit}
@media(max-width:700px){.generalbox{grid-template-columns:1fr}}
input,button,select{font:inherit;border:1px solid #334155;border-radius:9px;padding:9px;background:#0b1220;color:#e5e7eb}
input{width:100%}button{cursor:pointer}.primary{background:#1d4ed8}.danger{background:#991b1b}.safe{background:#166534}
.long,.ok{color:#22c55e}.short,.bad{color:#f87171}.wait{color:#facc15}.pill{display:inline-block;border:1px solid #334155;border-radius:999px;padding:3px 7px;margin:2px;font-size:11px}
.controls{display:grid;grid-template-columns:1fr auto auto auto;gap:8px}.approve{display:grid;grid-template-columns:1fr auto auto;gap:8px;margin-top:10px}
@media(max-width:700px){.controls,.approve{grid-template-columns:1fr}.row{grid-template-columns:1fr;gap:3px}.grid{grid-template-columns:1fr}}
</style>
</head>
<body><div class="wrap">
<h1>STC Owner Console</h1>
<p class="muted">Human approval + manual order entry only. This page never places an order.</p>

<div class="tabs" id="tabs">
<button class="tab active" data-tab="overview">Overview</button>
<button class="tab" data-tab="capital">Capital.com Africa <span class="tabcount" id="count-capital">0</span></button>
<button class="tab" data-tab="amp">AMP Futures <span class="tabcount" id="count-amp">0</span></button>
<button class="tab" data-tab="general">General Lab</button>
<button class="tab" data-tab="notifications">Notifications</button>
</div>

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

<div id="overview-panel">
  <div id="overview-summary" class="summary"></div>
  <div class="bar" style="margin-top:14px"><div class="sectiontitle">Latest opportunities across both competitions</div><div id="overview-cards" class="grid"></div></div>
</div>

<div id="capital-panel" class="hidden">
  <div class="bar"><div class="sectiontitle">Capital.com Africa</div><div class="small">Independent competition lane. Capital.com symbols, account rules, risk and position limits stay separate from AMP Futures.</div></div>
  <div id="capital-account" class="bar"></div>
  <div class="bar"><div class="sectiontitle">Open positions / Portfolio Supervisor</div><div class="small">Executed trades stay here until you record a manual close. New signals on the same symbol do not replace them.</div><button style="margin-top:10px" onclick="recordExistingPosition('capital-africa-sep-2026')">Record an existing manual position</button><div id="capital-positions" class="grid" style="margin-top:10px"></div></div>
  <div class="bar"><div class="sectiontitle">Latest signals</div><div id="capital-cards" class="grid"></div></div>
</div>

<div id="amp-panel" class="hidden">
  <div class="bar"><div class="sectiontitle">AMP Futures</div><div class="small">Independent futures lane. Futures symbols, contract limits, risk and position state stay separate from Capital.com Africa.</div></div>
  <div id="amp-account" class="bar"></div>
  <div class="bar"><div class="sectiontitle">Open positions / Portfolio Supervisor</div><div class="small">Executed trades stay here until you record a manual close. New signals on the same symbol do not replace them.</div><button style="margin-top:10px" onclick="recordExistingPosition('amp-futures-sep-2026')">Record an existing manual position</button><div id="amp-positions" class="grid" style="margin-top:10px"></div></div>
  <div class="bar"><div class="sectiontitle">Latest signals</div><div id="amp-cards" class="grid"></div></div>
</div>

<div id="general-panel" class="hidden">
  <div class="bar">
    <div class="sectiontitle">General Lab</div>
    <div class="small">Separate research/sandbox area. It does not affect either competition account.</div>
    <div class="generalbox" style="margin-top:12px">
      <div><label class="small">Research capital</label><input id="general-capital" type="number" min="0" step="any" placeholder="Example: 10000"></div>
      <div><label class="small">Preferred base currency</label><select id="general-currency"><option>USD</option><option>EUR</option><option>GBP</option><option>EGP</option></select></div>
      <div style="grid-column:1/-1"><label class="small">Watch symbols / ideas</label><textarea id="general-symbols" placeholder="Examples: EURUSD, XAUUSD, BTCUSD ..."></textarea></div>
    </div>
    <button class="primary" id="save-general" style="margin-top:10px">Save General Lab settings on this device</button>
    <div id="general-status" class="small" style="margin-top:8px">The General Lab engine is intentionally separate from competition execution.</div>
  </div>
</div>

<div id="notifications-panel" class="hidden">
  <div class="bar">
    <div class="sectiontitle">Notification Center</div>
    <div class="row"><span>Browser / laptop</span><span class="value" id="browser-notify-status">Not enabled</span></div>
    <div class="row"><span>Telegram mobile</span><span class="value" id="telegram-notify-status">Not configured</span></div>
    <div class="row"><span>Email backup</span><span class="value" id="email-notify-status">Not configured</span></div>
    <div class="row"><span>Recent server notification events</span><span class="value" id="server-notify-count">-</span></div>
    <button id="test-server-notify" style="margin-top:10px">Send notification test</button>
    <div id="server-notify-note" class="small" style="margin-top:8px">Server notification status not loaded yet.</div>
    <div class="small" style="margin-top:10px">Raw 15-minute feed bars do not generate user notifications. Server notifications are reserved for new locked plans and non-HOLD position-management changes.</div>
  </div>
</div>
</div>
<script>
const $=id=>document.getElementById(id);
let snapshot=null;
let activeTab='overview';
let notificationStatus=null;
let autoTimer=null;
let autoCountdown=null;
let secondsToRefresh=30;
let initializedSignals=false;
function loadSeenSet(key){
 try{
   const value=JSON.parse(localStorage.getItem(key)||'[]');
   return new Set(Array.isArray(value)?value:[]);
 }catch(e){
   return new Set();
 }
}
const seenSignalPlans=loadSeenSet('stc_seen_signal_plans');
const seenManagement=loadSeenSet('stc_seen_management');

function esc(s){
 return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}
function num(x,d=4){
 const n=Number(x);
 return Number.isFinite(n)?n.toFixed(d):'-';
}
function auth(){
 const t=$('token').value.trim();
 return {'Authorization':'Bearer '+t,'Content-Type':'application/json'};
}
async function api(path,opts={}){
 const r=await fetch(path,{cache:'no-store',...opts,headers:{...auth(),...(opts.headers||{})}});
 const j=await r.json().catch(()=>({}));
 if(!r.ok)throw new Error((j&&j.error)||('HTTP '+r.status));
 return j;
}

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

function formatLocalTime(value){
 if(!value)return '-';
 const d=new Date(value);
 if(Number.isNaN(d.getTime()))return String(value);
 return new Intl.DateTimeFormat(undefined,{day:'2-digit',month:'short',hour:'numeric',minute:'2-digit'}).format(d);
}
function formatAgeSeconds(seconds){
 const s=Math.max(0,Math.floor(Number(seconds)||0));
 if(s<60)return s+'s ago';
 const m=Math.floor(s/60);
 if(m<60)return m+'m ago';
 const h=Math.floor(m/60);
 return h+'h '+(m%60)+'m ago';
}
function secondsUntil(value){
 const t=Date.parse(value||'');
 if(!Number.isFinite(t))return null;
 return Math.floor((t-Date.now())/1000);
}
function formatCountdown(seconds){
 if(seconds==null)return '-';
 if(seconds<=0)return 'expired';
 const m=Math.floor(seconds/60), s=seconds%60;
 if(m>=60){const h=Math.floor(m/60);return h+'h '+(m%60)+'m';}
 return m+'m '+String(s).padStart(2,'0')+'s';
}
function isOpportunityActive(c){
 if(!c||c.has_open_position||!c.locked_trade_plan||!(c.recommendation==='LONG'||c.recommendation==='SHORT'))return false;
 const left=secondsUntil(c.locked_trade_plan.valid_until);
 return left!==null && left>0;
}
function deriveOrderInstruction(c,price){
 const p=c&&c.locked_trade_plan;
 const direction=c&&c.recommendation;
 const current=Number(price);
 if(!p||!(direction==='LONG'||direction==='SHORT')||!Number.isFinite(current)||current<=0)return null;
 const low=Number(p.entry_min), high=Number(p.entry_max), mid=(low+high)/2;
 if(current>=low&&current<=high)return {order_type:'MARKET',side:direction==='LONG'?'BUY':'SELL',status:'inside_entry_zone',trigger_price:null,limit_price:null,explanation:'Live price is inside the locked entry zone.'};
 if(direction==='LONG'&&current>high)return {order_type:'BUY LIMIT',side:'BUY',status:'wait_pullback',trigger_price:null,limit_price:mid,explanation:'Price is above the zone. Wait for a pullback; use a BUY LIMIT inside the zone.'};
 if(direction==='LONG')return {order_type:'BUY STOP-LIMIT',side:'BUY',status:'wait_breakout_into_zone',trigger_price:low,limit_price:high,explanation:'Price is below the zone. Enter only if price rises into it.'};
 if(current<low)return {order_type:'SELL LIMIT',side:'SELL',status:'wait_rebound',trigger_price:null,limit_price:mid,explanation:'Price is below the zone. Wait for a rebound; use a SELL LIMIT inside the zone.'};
 return {order_type:'SELL STOP-LIMIT',side:'SELL',status:'wait_breakdown_into_zone',trigger_price:high,limit_price:low,explanation:'Price is above the zone. Enter only if price falls into it.'};
}
function orderHtml(c,i){
 const live=(c.order_instruction||deriveOrderInstruction(c,c.current_price));
 if(!live)return '';
 const trigger=live.trigger_price==null?'':' • trigger '+num(live.trigger_price);
 const limit=live.limit_price==null?'':' • limit '+num(live.limit_price);
 return '<div class="orderbox"><div class="small">Planned order type • based on latest confirmed 15m close</div>'
  +'<div class="ordername">'+esc((live.side?live.side+' ':'')+(live.order_type||'UNKNOWN'))+'</div>'
  +'<div class="small">'+esc(live.explanation||'')+esc(trigger)+esc(limit)+'</div>'
  +'<div id="order-hint-'+i+'" class="small" style="margin-top:6px">Enter the current TradingView price below to recalculate the order type before approval.</div></div>';
}
function updateOrderHint(i){
 const c=snapshot&&snapshot.cards?snapshot.cards[i]:null;
 const price=Number($('price-'+i)?.value);
 const h=$('order-hint-'+i);
 if(!h||!c)return;
 if(!Number.isFinite(price)||price<=0){h.textContent='Enter the current TradingView price to recalculate the order type before approval.';return;}
 const o=deriveOrderInstruction(c,price);
 if(!o){h.textContent='Order type unavailable.';return;}
 const parts=[(o.side?o.side+' ':'')+o.order_type,o.explanation];
 if(o.trigger_price!=null)parts.push('Trigger '+num(o.trigger_price));
 if(o.limit_price!=null)parts.push('Limit '+num(o.limit_price));
 h.textContent='LIVE PRICE CHECK: '+parts.join(' • ');
}
function planHtml(p){
 if(!p)return '<div class="row"><span>Locked plan</span><span class="value">None</span></div>';
 const left=secondsUntil(p.valid_until);
 return '<div class="row"><span>Direction</span><span class="value">'+esc(p.direction||'-')+'</span></div>'
  +'<div class="row"><span>Decision timeframe</span><span class="value">'+esc(p.decision_timeframe||'15')+' min</span></div>'
  +'<div class="row"><span>Entry zone</span><span class="value">'+num(p.entry_min)+' → '+num(p.entry_max)+'</span></div>'
  +'<div class="row"><span>Stop loss</span><span class="value">'+num(p.initial_stop)+'</span></div>'
  +'<div class="row"><span>Management checkpoint</span><span class="value">'+num(p.target1)+' • no partial TP order</span></div>'
  +'<div class="row"><span>Final take profit</span><span class="value">'+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Expires</span><span class="value">'+formatLocalTime(p.valid_until)+' • <span class="countdown" data-valid-until="'+esc(p.valid_until)+'">'+formatCountdown(left)+'</span></span></div>';
}

function sizingHtml(s,c){
 if(!s)return '';
 const limited=(s.risk_budget_limited_by||[]).join(', ');
 const riskPct=Number(s.equity_usd)>0?Number(s.risk_amount_usd)/Number(s.equity_usd)*100:0;
 const p=c&&c.locked_trade_plan?c.locked_trade_plan:null;
 return '<div class="orderbox"><div class="small">STC POSITION SIZE • use this quantity unless the competition platform forces a smaller valid amount</div>'
  +'<div class="ordername">'+num(s.proposed_quantity,6)+' units/contracts</div>'
  +'<div class="row"><span>Risk on this trade</span><span class="value">

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing,c)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function progressHtml(competitionId){
 const p=snapshot&&snapshot.competition_progress?snapshot.competition_progress[competitionId]:null;
 if(!p)return '';
 const cls=p.eligible_by_days?'ok':'wait';
 return '<div class="orderbox"><div class="small">COMPETITION PROGRESS</div>'
  +'<div class="row"><span>Qualifying trading days</span><span class="value '+cls+'">'+esc(p.qualifying_trading_days)+' / '+esc(p.required_trading_days)+'</span></div>'
  +'<div class="row"><span>Days remaining</span><span class="value">'+esc(p.days_remaining)+'</span></div>'
  +'<div class="row"><span>Trades entered</span><span class="value">'+esc(p.total_entries)+'</span></div>'
  +'<div class="row"><span>Open / closed</span><span class="value">'+esc(p.open_positions)+' / '+esc(p.closed_positions)+'</span></div>'
  +'<div class="row"><span>Recorded trade actions</span><span class="value">'+esc(p.position_actions)+'</span></div>'
  +'<div class="row"><span>Realized competition P/L</span><span class="value">
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return progressHtml(competitionId)
  +'<div class="row"><span>Owner-synced equity</span><span class="value">
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_amount_usd,2)+' • '+num(riskPct,3)+'%</span></div>'
  +'<div class="row"><span>Configured risk budget</span><span class="value">

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_budget_usd,2)+' • '+num(Number(s.risk_fraction)*100,3)+'%</span></div>'
  +'<div class="row"><span>Official max open position</span><span class="value">'+num(s.max_position,6)+'</span></div>'
  +'<div class="row"><span>Open before this trade</span><span class="value">'+num(s.current_open_quantity,6)+'</span></div>'
  +'<div class="row"><span>Projected open after</span><span class="value">'+num(s.projected_open_quantity,6)+'</span></div>'
  +(p?'<div class="row"><span>Stop loss</span><span class="value">'+num(p.initial_stop)+'</span></div>':'')
  +(p?'<div class="row"><span>Final take profit</span><span class="value">'+num(p.target2)+'</span></div>':'')
  +'<div class="small">Single-TP mode: TP1 is an internal management checkpoint only; do not place a separate TP1 order.</div>'
  +(limited?'<div class="small wait">Sizing reduced by: '+esc(limited)+'</div>':'')
  +'</div>';
}

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(p.realized_pnl_usd,2)+'</span></div>'
  +'<div class="small">Qualification-day tracking is based on recorded opening/closing activity. Keep STC updated after every manual platform action.</div></div>';
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_amount_usd,2)+' • '+num(riskPct,3)+'%</span></div>'
  +'<div class="row"><span>Configured risk budget</span><span class="value">

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_budget_usd,2)+' • '+num(Number(s.risk_fraction)*100,3)+'%</span></div>'
  +'<div class="row"><span>Official max open position</span><span class="value">'+num(s.max_position,6)+'</span></div>'
  +'<div class="row"><span>Open before this trade</span><span class="value">'+num(s.current_open_quantity,6)+'</span></div>'
  +'<div class="row"><span>Projected open after</span><span class="value">'+num(s.projected_open_quantity,6)+'</span></div>'
  +(p?'<div class="row"><span>Stop loss</span><span class="value">'+num(p.initial_stop)+'</span></div>':'')
  +(p?'<div class="row"><span>Final take profit</span><span class="value">'+num(p.target2)+'</span></div>':'')
  +'<div class="small">Single-TP mode: TP1 is an internal management checkpoint only; do not place a separate TP1 order.</div>'
  +(limited?'<div class="small wait">Sizing reduced by: '+esc(limited)+'</div>':'')
  +'</div>';
}

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_amount_usd,2)+' • '+num(riskPct,3)+'%</span></div>'
  +'<div class="row"><span>Configured risk budget</span><span class="value">

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_budget_usd,2)+' • '+num(Number(s.risk_fraction)*100,3)+'%</span></div>'
  +'<div class="row"><span>Official max open position</span><span class="value">'+num(s.max_position,6)+'</span></div>'
  +'<div class="row"><span>Open before this trade</span><span class="value">'+num(s.current_open_quantity,6)+'</span></div>'
  +'<div class="row"><span>Projected open after</span><span class="value">'+num(s.projected_open_quantity,6)+'</span></div>'
  +(p?'<div class="row"><span>Stop loss</span><span class="value">'+num(p.initial_stop)+'</span></div>':'')
  +(p?'<div class="row"><span>Final take profit</span><span class="value">'+num(p.target2)+'</span></div>':'')
  +'<div class="small">Single-TP mode: TP1 is an internal management checkpoint only; do not place a separate TP1 order.</div>'
  +(limited?'<div class="small wait">Sizing reduced by: '+esc(limited)+'</div>':'')
  +'</div>';
}

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(p.realized_pnl_usd,2)+'</span></div>'
  +'<div class="small">Qualification-day tracking is based on recorded opening/closing activity. Keep STC updated after every manual platform action.</div></div>';
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_amount_usd,2)+' • '+num(riskPct,3)+'%</span></div>'
  +'<div class="row"><span>Configured risk budget</span><span class="value">

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
+num(s.risk_budget_usd,2)+' • '+num(Number(s.risk_fraction)*100,3)+'%</span></div>'
  +'<div class="row"><span>Official max open position</span><span class="value">'+num(s.max_position,6)+'</span></div>'
  +'<div class="row"><span>Open before this trade</span><span class="value">'+num(s.current_open_quantity,6)+'</span></div>'
  +'<div class="row"><span>Projected open after</span><span class="value">'+num(s.projected_open_quantity,6)+'</span></div>'
  +(p?'<div class="row"><span>Stop loss</span><span class="value">'+num(p.initial_stop)+'</span></div>':'')
  +(p?'<div class="row"><span>Final take profit</span><span class="value">'+num(p.target2)+'</span></div>':'')
  +'<div class="small">Single-TP mode: TP1 is an internal management checkpoint only; do not place a separate TP1 order.</div>'
  +(limited?'<div class="small wait">Sizing reduced by: '+esc(limited)+'</div>':'')
  +'</div>';
}

function macroHtml(m){
 if(!m)return '';
 const status=String(m.status||'unknown');
 const cls=status==='safe'?'ok':status==='blackout'?'short':'wait';
 const next=m.next_high_impact;
 const nearby=(m.nearby_high_impact||[]);
 let html='<div class="row"><span>Macro event risk</span><span class="value '+cls+'">'+esc(status.toUpperCase())+'</span></div>';
 if(nearby.length){
   const e=nearby[0];
   html+='<div class="small bad">High-impact blackout: '+esc(e.currency)+' • '+esc(e.title)+' • '+num(e.minutes_from_now,0)+' min</div>';
 }else if(next){
   html+='<div class="small">Next high-impact: '+esc(next.currency)+' • '+esc(next.title)+' • '+num(next.minutes_from_now,0)+' min</div>';
 }
 if(m.block_new_approval)html+='<div class="small bad">New approval blocked by macro-risk gate.</div>';
 return html;
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&controlOpen;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';
 return '<div class="card" data-card-index="'+i+'">'
  +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Signal</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
  +planHtml(c.locked_trade_plan)
  +orderHtml(c,i)
  +sizingHtml(c.position_sizing)
  +macroHtml(c.macro_context)
  +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
  +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
  +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
  +'<div class="small" style="margin:8px 0">'+reasons+'</div>'
  +(active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')
    ?'<div class="approve"><input id="price-'+i+'" type="number" step="any" placeholder="Current TradingView price" oninput="updateOrderHint('+i+')">'
      +(canApprove?'<button class="safe" onclick="approveCard('+i+',\'approve\')">Approve</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button>':'')
      +'</div>'
    :'')
  +(active && c.locked_trade_plan && a.decision==='approved'?'<button style="margin-top:8px" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
  +'</div>';
}

function persistSeenSet(key,set){
 try{localStorage.setItem(key,JSON.stringify([...set].slice(-250)))}catch(e){}
}
function maybeNotify(cards){
 const actionable=(cards||[]).filter(c=>isOpportunityActive(c));
 initializedSignals=true;
 for(const c of actionable){
   const key=String(c.locked_trade_plan.plan_id||c.signal_id);
   if(seenSignalPlans.has(key))continue;
   const oi=c.order_instruction||{};
   const body=c.symbol+' • '+c.recommendation+' • '+(oi.order_type||'ENTRY')+' • Entry '+num(c.locked_trade_plan.entry_min)+' - '+num(c.locked_trade_plan.entry_max)+' • SL '+num(c.locked_trade_plan.initial_stop)+' • TP1 '+num(c.locked_trade_plan.target1)+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='NEW '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC NEW ACTIVE TRADE PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(c=>c.recommendation==='WAIT'||isOpportunityActive(c));
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function accountHtml(account,competitionId){
 if(!account)return '<div class="small">Account state unavailable.</div>';
 const s=riskSummaryFor(competitionId);
 const tradeRisk=Number(account.equity_usd)*Number(account.risk_fraction);
 const portfolioCap=tradeRisk*6;
 const clusterCap=tradeRisk*3;
 const clusters=Object.entries(s.clusters||{}).sort((a,b)=>Number(b[1].initial_risk_usd)-Number(a[1].initial_risk_usd));
 const clusterHtml=clusters.length
   ?clusters.map(([name,v])=>'<span class="pill">'+esc(name)+': $'+num(v.initial_risk_usd,2)+'</span>').join('')
   :'<span class="small">No open risk clusters.</span>';
 return '<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
  +'<div class="row"><span>STC risk budget / trade</span><span class="value">'+num(Number(account.risk_fraction)*100,2)+'% • $'+num(tradeRisk,2)+'</span></div>'
  +'<div class="row"><span>Open initial risk</span><span class="value">$'+num(s.initial_risk_usd,2)+' / $'+num(portfolioCap,2)+'</span></div>'
  +'<div class="row"><span>Correlation-cluster cap</span><span class="value">$'+num(clusterCap,2)+'</span></div>'
  +'<div class="row"><span>Account state source</span><span class="value">'+esc(account.source)+'</span></div>'
  +'<div style="margin:8px 0">'+clusterHtml+'</div>'
  +'<div class="small">Risk caps are STC controls, not official competition limits. Equity is owner-maintained because broker-account read access is unavailable.</div>'
  +'<button style="margin-top:8px" onclick="updateAccountState(\''+competitionId+'\')">Update equity / risk setting</button>';
}

function managementClass(a){
 return a==='EXIT_NOW'?'short':a==='HOLD'?'ok':'wait';
}
function positionHtml(p){
 const m=p.management||{};
 const rotation=p.rotation_candidate;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<button onclick="recordPartial(\''+esc(p.position_id)+'\')">After manual partial close: record</button>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="row"><span>'+esc(p.symbol)+'</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+num(p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+num(p.current_stop)+'</span></div>'
  +'<div class="row"><span>TP1 / TP2</span><span class="value">'+num(p.target1)+' / '+num(p.target2)+'</span></div>'
  +'<div class="row"><span>Supervisor</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+num(m.r_multiple,2)+'</span></div>'
  +'<div class="row"><span>Unrealized P/L</span><span class="value">'+(m.unrealized_pnl_usd==null?'-':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}

function renderOverview(cards){
 const capital=cards.filter(c=>competitionOf(c)==='capital');
 const amp=cards.filter(c=>competitionOf(c)==='amp');
 const actionable=cards.filter(c=>isOpportunityActive(c));
 const ready=cards.filter(c=>c.manual_execution_ready);
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 $('count-capital').textContent=capital.length;
 $('count-amp').textContent=amp.length;
 $('overview-summary').innerHTML=
   '<div class="card"><div class="small">Capital symbols monitored</div><div class="big">'+capital.length+'</div></div>'
  +'<div class="card"><div class="small">AMP symbols monitored</div><div class="big">'+amp.length+'</div></div>'
  +'<div class="card"><div class="small">ACTIVE opportunities now</div><div class="big">'+actionable.length+'</div></div>'
  +'<div class="card"><div class="small">Manual-ready now</div><div class="big">'+ready.length+'</div></div>'
  +'<div class="card"><div class="small">Open positions tracked</div><div class="big">'+positions.length+'</div></div>';
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
}

function render(){
 const r=snapshot.runtime_control||{};
 const mc=snapshot.macro_calendar_status||{};
 $('runtime').innerHTML=runtimeHtml(r)
  +'<div class="row"><span>Macro calendar</span><span class="value '+(mc.ok?'ok':'bad')+'">'+(mc.ok?'CONNECTED':'UNAVAILABLE')+'</span></div>'
  +(!mc.ok&&mc.error?'<div class="small bad">Macro gate error: '+esc(mc.error)+'</div>':'');
 const cards=snapshot.cards||[];
 const accounts=snapshot.account_states||[];
 const positions=(snapshot.portfolio&&snapshot.portfolio.positions)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   if($('server-notify-note'))$('server-notify-note').textContent='Actionable server notification audit loaded.';
 }catch(e){
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification endpoint not available yet: '+e.message;
 }
}

async function refresh(){
 if(!$('token').value.trim())return;
 $('status').textContent='Loading...';
 try{
   snapshot=await api('operator_snapshot.php');
   render();
   refreshNotificationStatus();
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
function updateLiveCountdowns(){
 let expiredVisible=false;
 for(const el of document.querySelectorAll('[data-valid-until]')){
   const left=secondsUntil(el.dataset.validUntil);
   el.textContent=formatCountdown(left);
   if(left!==null&&left<=0)expiredVisible=true;
 }
 if(expiredVisible&&snapshot)render();
}
function startAutoRefresh(){
 if(autoTimer)return;
 updateAutoStatus();
 autoCountdown=setInterval(()=>{secondsToRefresh=Math.max(0,secondsToRefresh-1);updateAutoStatus();updateLiveCountdowns()},1000);
 autoTimer=setInterval(()=>{secondsToRefresh=30;refresh()},30000);
}
function stopAutoRefresh(){
 if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
 if(autoCountdown){clearInterval(autoCountdown);autoCountdown=null;}
 $('autostatus').textContent='Auto refresh: OFF';
}

async function enableNotifications(){
 if(!('Notification' in window)){alert('Browser notifications are not supported in this browser.');return;}
 const p=await Notification.requestPermission();
 $('notify').textContent=p==='granted'?'Browser alerts ON':'Enable browser alerts';
 if($('browser-notify-status'))$('browser-notify-status').textContent=p==='granted'?'Enabled':'Not enabled';
 if(p==='granted'){
   new Notification('STC browser alerts enabled',{body:'Active opportunities will now notify even if they already appeared before this permission was enabled.'});
   if(snapshot)maybeNotify(snapshot.cards||[]);
 }
}
function maybeNotifyManagement(positions){
 for(const p of positions||[]){
   const m=p.management||{};
   if(!m.action || m.action==='HOLD')continue;
   const key=p.position_id+'|'+m.action+'|'+num(m.suggested_stop||0,4);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC POSITION: '+m.action,{body:p.symbol+' • '+p.side+' • R '+num(m.r_multiple,2)+' • '+(m.reasons||[]).join(', '),tag:key,requireInteraction:m.action==='EXIT_NOW'});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
 }
}

async function updateAccountState(competitionId){
 const account=(snapshot.account_states||[]).find(a=>a.competition_id===competitionId);
 const equity=Number(prompt('Current competition equity in USD',account?account.equity_usd:''));
 if(!Number.isFinite(equity)||equity<=0)return;
 const pct=Number(prompt('STC risk budget per new trade (%)',account?Number(account.risk_fraction)*100:0.5));
 if(!Number.isFinite(pct)||pct<=0||pct>2){alert('Risk setting must be above 0% and at most 2%.');return;}
 try{
   await api('account_state.php',{method:'POST',body:JSON.stringify({competition_id:competitionId,equity_usd:equity,risk_fraction:pct/100})});
   await refresh();
 }catch(e){alert('Account state update failed: '+e.message);}
}

async function recordFilledPosition(i){
 const c=snapshot.cards[i];
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){alert('An approved locked plan is required.');return;}
 if(!isOpportunityActive(c)){alert('This locked plan has expired. Do not enter it; wait for a new active plan.');await refresh();return;}
 if(c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('STC position limit or portfolio risk capacity currently blocks a new entry.');return;}
 const suggested=c.position_sizing?c.position_sizing.proposed_quantity:'';
 const qty=Number(prompt('Quantity actually filled manually in the competition platform',suggested));
 if(!Number.isFinite(qty)||qty<=0)return;
 const entry=Number(prompt('Actual average fill price',c.current_price||c.locked_trade_plan.entry_mid));
 if(!Number.isFinite(entry)||entry<=0)return;
 if(!confirm('Confirm the order was already entered manually in the competition platform. STC will only record it.'))return;
 const p=c.locked_trade_plan;
 const body={action:'OPEN',origin:'stc_plan',competition_id:c.competition_id,symbol:c.symbol,side:p.direction,quantity:qty,entry_price:entry,initial_stop:p.initial_stop,current_stop:p.initial_stop,target1:p.target1,target2:p.target2,source_plan_id:p.plan_id,opened_at_utc:new Date().toISOString(),note:'Owner-confirmed manual fill'};
 try{await api('position.php',{method:'POST',body:JSON.stringify(body)});await refresh();}
 catch(e){alert('Position record failed: '+e.message);}
}
async function recordStopUpdate(positionId,suggested){
 const stop=Number(prompt('Stop price already changed manually in the platform',suggested));
 if(!Number.isFinite(stop)||stop<=0)return;
 if(!confirm('Confirm you already changed the stop manually. This only updates the STC ledger.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'UPDATE_STOP',position_id:positionId,current_stop:stop,note:'Owner-confirmed manual stop change'})});await refresh();}
 catch(e){alert('Stop record failed: '+e.message);}
}
async function recordPartial(positionId){
 const qty=Number(prompt('Quantity already closed manually'));
 const price=Number(prompt('Actual partial exit fill price'));
 if(!Number.isFinite(qty)||qty<=0||!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm this partial close already happened in the platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'PARTIAL',position_id:positionId,quantity_closed:qty,exit_price:price,note:'Owner-confirmed manual partial close'})});await refresh();}
 catch(e){alert('Partial-close record failed: '+e.message);}
}
async function recordClose(positionId){
 const price=Number(prompt('Actual final exit fill price'));
 if(!Number.isFinite(price)||price<=0)return;
 if(!confirm('Confirm the position is already closed manually in the competition platform.'))return;
 try{await api('position.php',{method:'POST',body:JSON.stringify({action:'CLOSE',position_id:positionId,exit_price:price,note:'Owner-confirmed manual close'})});await refresh();}
 catch(e){alert('Close record failed: '+e.message);}
}

async function setControls(safe,kill){
 if(!confirm('Confirm runtime control change? This changes approval availability but never places an order.'))return;
 try{await api('runtime_control.php',{method:'POST',body:JSON.stringify({safe_mode:safe,kill_switch:kill,reason:$('reason').value.trim()||null})});await refresh();}
 catch(e){alert('Control change failed: '+e.message);}
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 if(decision==='approve'&&!isOpportunityActive(c)){alert('This opportunity has expired and was removed from the active set. Wait for a new locked plan.');await refresh();return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){alert('Approval blocked by competition position limit or STC portfolio/cluster risk capacity.');return;}
 if(decision==='approve'&&!confirm('Approve this signal for MANUAL order entry only? No order will be sent.'))return;
 const price=Number($('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(!Number.isFinite(price)||price<=0){alert('Enter the current TradingView price first.');return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   alert('Decision: '+r.decision);
   await refresh();
 }catch(e){alert('Approval failed/blocked: '+e.message);await refresh();}
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>showTab(el.dataset.tab));

function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=()=>{
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 $('general-status').textContent='Saved on this device. General Lab analysis remains isolated from both competition accounts.';
};

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=refresh;
$('notify').onclick=enableNotifications;
$('test-server-notify').onclick=async()=>{
 if(!confirm('Send one harmless STC notification test through configured server channels?'))return;
 try{
   await api('notification.php',{method:'POST',body:JSON.stringify({action:'test'})});
   alert('Test dispatched. Check Telegram/email and the delivery audit.');
   await refreshNotificationStatus();
 }catch(e){alert('Notification test failed: '+e.message);}
};
$('logout').onclick=()=>{
 stopAutoRefresh();
 $('token').value='';
 snapshot=null;
 initializedSignals=false;
 seenSignalPlans.clear();
 seenManagement.clear();
 $('runtime').textContent='Runtime controls not loaded.';
 $('status').textContent='Token cleared';
 document.title='STC Owner Console';
};
</script></body></html>
