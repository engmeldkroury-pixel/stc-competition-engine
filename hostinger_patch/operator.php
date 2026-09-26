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
.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.formgrid .full{grid-column:1/-1}.fieldnote{font-size:11px;color:#94a3b8;margin-top:4px}.inlineerror{border:1px solid #7f1d1d;background:#450a0a;color:#fecaca;border-radius:9px;padding:9px;margin-top:10px}.inlinesuccess{border:1px solid #166534;background:#052e16;color:#bbf7d0;border-radius:9px;padding:9px;margin-top:10px}.buttonrow{display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;margin-top:14px}
.ticket{border:2px solid #334155;border-radius:14px;padding:14px;margin:10px 0;background:#0b1220}.ticket.actionable{border-color:#166534}.ticket.blockedticket{border-color:#854d0e}.ticket-title{font-size:13px;font-weight:800;letter-spacing:.04em;color:#cbd5e1}.ticket-action{font-size:28px;font-weight:900;line-height:1.15;margin:7px 0}.ticket-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}.ticket-cell{border:1px solid #334155;border-radius:10px;padding:10px;background:#0f172a;min-width:0}.ticket-label{font-size:11px;color:#94a3b8;margin-bottom:4px}.ticket-value{font-size:18px;font-weight:800;overflow-wrap:anywhere}.ticket-note{font-size:12px;color:#cbd5e1;margin-top:8px}.ticket-input{margin-top:12px}.advanced{margin-top:12px;border-top:1px solid #334155;padding-top:10px}.advanced summary{cursor:pointer;font-weight:700;color:#cbd5e1}.advanced-body{margin-top:10px}.record-page{max-width:900px}.record-page h2{margin:0 0 6px}.record-guide{border:1px solid #334155;border-radius:10px;padding:10px;margin:10px 0;background:#0b1220}
@media(max-width:700px){.formgrid,.ticket-grid{grid-template-columns:1fr}}
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
<button class="tab" data-tab="record">Record Trade</button>
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
  <div class="bar" style="margin-top:14px"><div class="sectiontitle">Competition Watchlist — strongest blocked candidates</div><div class="small">These are NOT trade approvals. They show the strongest current directional evidence that is still blocked by the A+ gate, so the operator can see whether the market is close to becoming actionable and exactly which confirmations are missing.</div><div id="watchlist-cards" class="grid" style="margin-top:10px"></div></div>
</div>

<div id="capital-panel" class="hidden">
  <div class="bar"><div class="sectiontitle">Capital.com Africa</div><div class="small">Independent competition lane. Capital.com symbols, account rules, risk and position limits stay separate from AMP Futures.</div></div>
  <div id="capital-account" class="bar"></div>
  <div class="bar"><div class="sectiontitle">Open positions / Portfolio Supervisor</div><div class="small">Executed trades stay here until you record a manual close. New signals on the same symbol do not replace them.</div><button style="margin-top:10px" onclick="recordExistingPosition('capital-africa-sep-2026')">Record an existing manual position</button> <button style="margin-top:10px" onclick="recordClosedTradeHistory('capital-africa-sep-2026')">Import a past closed trade</button><div id="capital-positions" class="grid" style="margin-top:10px"></div></div>
  <div class="bar"><div class="sectiontitle">Completed trades — recent</div><div class="small">Closed trades remain visible here with realized P/L so the competition record is easy to audit.</div><div id="capital-closed-positions" class="grid" style="margin-top:10px"></div></div>
  <div class="bar"><div class="sectiontitle">Latest signals</div><div id="capital-cards" class="grid"></div></div>
</div>

<div id="amp-panel" class="hidden">
  <div class="bar"><div class="sectiontitle">AMP Futures</div><div class="small">Independent futures lane. Futures symbols, contract limits, risk and position state stay separate from Capital.com Africa.</div></div>
  <div id="amp-account" class="bar"></div>
  <div class="bar"><div class="sectiontitle">Open positions / Portfolio Supervisor</div><div class="small">Executed trades stay here until you record a manual close. New signals on the same symbol do not replace them.</div><button style="margin-top:10px" onclick="recordExistingPosition('amp-futures-sep-2026')">Record an existing manual position</button> <button style="margin-top:10px" onclick="recordClosedTradeHistory('amp-futures-sep-2026')">Import a past closed trade</button><div id="amp-positions" class="grid" style="margin-top:10px"></div></div>
  <div class="bar"><div class="sectiontitle">Completed trades — recent</div><div class="small">Closed trades remain visible here with realized P/L so the competition record is easy to audit.</div><div id="amp-closed-positions" class="grid" style="margin-top:10px"></div></div>
  <div class="bar"><div class="sectiontitle">Latest signals</div><div id="amp-cards" class="grid"></div></div>
</div>

<div id="general-panel" class="hidden">
  <div class="bar">
    <div class="sectiontitle">General Lab</div>
    <div class="small">Separate research/sandbox area. Adding a symbol creates a research-only STC request and does not affect either competition account.</div>
    <div class="generalbox" style="margin-top:12px">
      <div><label class="small">Research capital</label><input id="general-capital" type="number" min="0" step="any" placeholder="Example: 10000"></div>
      <div><label class="small">Preferred base currency</label><select id="general-currency"><option>USD</option><option>EUR</option><option>GBP</option><option>EGP</option></select></div>
      <div style="grid-column:1/-1"><label class="small">Symbols to research — one per line or comma-separated</label><textarea id="general-symbols" placeholder="Examples: CAPITALCOM:EURUSD, CAPITALCOM:XAUUSD, CBOT:ZN1!&#10;Bare symbols such as EURUSD are accepted but must be resolved to the exact TradingView provider symbol before history can be evaluated."></textarea></div>
    </div>
    <div class="buttonrow" style="justify-content:flex-start">
      <button class="primary" id="save-general">Save + queue research</button>
      <button id="refresh-general">Refresh research status</button>
    </div>
    <div id="general-status" class="small" style="margin-top:8px">Research is isolated from competition execution. Exact-provider history is mandatory; no substitute data provider is used silently.</div>
  </div>
  <div class="bar">
    <div class="sectiontitle">General Lab research queue</div>
    <div class="small">Every queued symbol follows the same STC process: asset classification → native strategies → community/composite indicators → train-only tuning → OOS/forward → frozen holdout → research/shadow status. Weights are symbol/timeframe-specific.</div>
    <div id="general-research-summary" class="summary" style="margin-top:10px"></div>
    <div id="general-research-cards" class="grid" style="margin-top:10px"></div>
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
    <div class="sectiontitle" style="margin-top:16px">Recent Telegram / server events</div>
    <div class="small">This audit mirrors what the server sent. If a Telegram message is delivered, it remains visible here even when the related symbol already has an open position and is therefore not a new-entry opportunity.</div>
    <div id="server-notify-events" class="grid" style="margin-top:10px"></div>
  </div>
</div>

<div id="record-panel" class="hidden">
  <div class="bar record-page">
    <h2>Record an already-executed position</h2>
    <div class="small">Use this only after the trade is ALREADY OPEN in the competition platform. STC will record and monitor it; no order will be sent.</div>
    <div class="record-guide"><b>If you already filled the trade and the signal card disappeared after a refresh, DO NOT enter the trade again.</b> Record the existing position here using the actual platform fill details.</div>
    <div class="record-guide"><b>One form only.</b> Fill everything here at once. Auto-refresh will not erase these fields while this page is open.</div>
    <input id="pos-origin" type="hidden"><input id="pos-card-index" type="hidden">
    <div class="formgrid" style="margin-top:14px">
      <div><label class="small">Competition</label><select id="pos-competition" onchange="normalizePositionTargetInputs()"><option value="">Select competition</option><option value="capital-africa-sep-2026">Capital.com Africa</option><option value="amp-futures-sep-2026">AMP Futures</option></select><div class="fieldnote">Choose from the allowed competitions. Free-text competition names are not accepted.</div></div>
      <div><label class="small">Symbol</label><input id="pos-symbol" type="text" autocomplete="off" placeholder="Example: CBOT:ZN1!" oninput="updatePositionPricePreviews()"></div>
      <div><label class="small">Side</label><select id="pos-side"><option>LONG</option><option>SHORT</option></select></div>
      <div><label class="small">Quantity actually filled</label><input id="pos-qty" type="number" min="0" step="any"><div id="pos-qty-note" class="fieldnote"></div></div>
      <div><label class="small">Actual average fill price</label><input id="pos-entry" type="text" autocomplete="off" oninput="updatePositionPricePreviews()"><div id="pos-entry-preview" class="fieldnote"></div></div>
      <div><label class="small">Current stop price</label><input id="pos-stop" type="text" autocomplete="off" oninput="updatePositionPricePreviews()"><div id="pos-stop-preview" class="fieldnote"></div></div>
      <div><label class="small">Final take-profit price (one TP only)</label><input id="pos-tp" type="text" autocomplete="off" oninput="updatePositionPricePreviews()"><div id="pos-tp-preview" class="fieldnote"></div></div>
      <div><label class="small">Original open time if known</label><input id="pos-opened" type="datetime-local"><div class="fieldnote">Leave blank to use the STC server time automatically. This avoids browser/time-zone clock mismatch.</div></div>
    </div>
    <div class="small" style="margin-top:10px">Treasury futures fields accept the exact TradingView quote, for example 105'12'5, or a tick-aligned decimal such as 105.390625. Values such as 105.13 are rejected for ZN because they are not valid ticks.</div>
    <div id="position-modal-message" class="hidden"></div>
    <div class="buttonrow"><button onclick="closePositionModal()">Back without saving</button><button class="safe" id="position-submit" onclick="submitPositionModal()">Record open position</button></div>
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
let recordReturnTab='overview';
const livePriceDrafts={};
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
const PRICE_RULES={
 'CBOT:ZN1!':{tick:1/64,style:'treasury32'},
 'CBOT:ZB1!':{tick:1/32,style:'treasury32'}
};
function priceRule(symbol){return PRICE_RULES[String(symbol||'').toUpperCase()]||null;}
function tickRound(symbol,price,mode='nearest'){
 const n=Number(price), rule=priceRule(symbol);
 if(!Number.isFinite(n)||!rule)return n;
 const scaled=n/rule.tick;
 const units=mode==='floor'?Math.floor(scaled+1e-9):mode==='ceil'?Math.ceil(scaled-1e-9):Math.round(scaled);
 return units*rule.tick;
}
function treasury32Quote(price){
 let n=Number(price);
 if(!Number.isFinite(n))return '-';
 let whole=Math.floor(n);
 let half32=Math.round((n-whole)*64);
 if(half32>=64){whole+=1;half32-=64;}
 if(half32<0){whole-=1;half32+=64;}
 const thirtySeconds=Math.floor(half32/2);
 const half=(half32%2)?5:0;
 return whole+"'"+String(thirtySeconds).padStart(2,'0')+"'"+half;
}
function formatPlatformPrice(symbol,price,mode='nearest'){
 const n=Number(price), rule=priceRule(symbol);
 if(!Number.isFinite(n))return '-';
 const normalized=tickRound(symbol,n,mode);
 if(rule&&rule.style==='treasury32')return treasury32Quote(normalized)+' ('+normalized.toFixed(6)+')';
 return num(n,4);
}
function formatPlatformInput(symbol,price,mode='nearest'){
 const n=Number(price), rule=priceRule(symbol);
 if(!Number.isFinite(n))return '';
 const normalized=tickRound(symbol,n,mode);
 if(rule&&rule.style==='treasury32')return treasury32Quote(normalized);
 return String(Number(n.toFixed(6)));
}
function parsePlatformPrice(symbol,raw){
 const text=String(raw??'').trim();
 if(!text)return null;
 const rule=priceRule(symbol);
 if(rule&&rule.style==='treasury32'){
   const m=text.replace(/[’′]/g,"'").match(/^([0-9]+)\s*'\s*([0-9]{1,2})(?:\s*'\s*([05]))?$/);
   if(m){
     const whole=Number(m[1]), thirtySeconds=Number(m[2]), half=m[3]==='5'?0.5:0;
     if(thirtySeconds<0||thirtySeconds>31)return null;
     return whole+(thirtySeconds+half)/32;
   }
 }
 const n=Number(text);
 if(!Number.isFinite(n)||n<=0)return null;
 if(rule){
   const units=n/rule.tick;
   if(Math.abs(units-Math.round(units))>1e-7)return null;
 }
 return n;
}
function planTickMode(direction,kind){
 if(kind==='stop')return direction==='LONG'?'ceil':'floor';
 if(kind==='target')return direction==='LONG'?'floor':'ceil';
 return 'nearest';
}
function planPriceText(c,price,kind='generic'){
 if(!c)return num(price);
 return formatPlatformPrice(c.symbol,price,planTickMode(c.recommendation||c.locked_trade_plan?.direction,kind));
}
function auth(){
 const t=$('token').value.trim();
 return {'Authorization':'Bearer '+t,'Content-Type':'application/json'};
}
async function api(path,opts={}){
 const r=await fetch(path,{cache:'no-store',...opts,headers:{...auth(),...(opts.headers||{})}});
 const j=await r.json().catch(()=>({}));
 if(!r.ok){
   const reasons=Array.isArray(j&&j.reasons)?j.reasons:[];
   const message=reasons.length?reasons.join(', '):((j&&j.error)||('HTTP '+r.status));
   const err=new Error(message);
   err.status=r.status;
   err.payload=j;
   throw err;
 }
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
function isLockedPlanVisible(c){
 if(!c||c.has_open_position||!c.locked_trade_plan||!(c.recommendation==='LONG'||c.recommendation==='SHORT'))return false;
 const left=secondsUntil(c.locked_trade_plan.valid_until);
 return left!==null && left>0;
}
function isOpportunityActive(c){
 if(!isLockedPlanVisible(c))return false;
 if(c.latest_signal_context&&c.latest_signal_context.approval_compatible_with_locked_plan===false)return false;
 return c.opportunity_active!==false;
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
function sizeModeText(c){
 const approved=c&&c.approval&&c.approval.execution_ticket?Number(c.approval.execution_ticket.max_quantity):NaN;
 const proposed=c&&c.position_sizing?Number(c.position_sizing.proposed_quantity):NaN;
 const q=Number.isFinite(approved)&&approved>0?approved:proposed;
 const qty=Number.isFinite(q)?num(q,6):'-';
 if(c&&c.competition_id==='amp-futures-sep-2026')return {qty,unit:'contracts',mode:'TradingView size mode: Units / Contracts — NOT % balance. MAX STC QUANTITY — NEVER use % balance, trade value, or margin.'};
 return {qty,unit:'units',mode:'MAX STC QUANTITY — enter this number in the platform Units field. NEVER use % balance, trade value, or margin.'};
}
function savePriceDraft(i){
 const c=snapshot&&snapshot.cards?snapshot.cards[i]:null;
 if(!c)return;
 const el=$('price-'+i);
 if(el)livePriceDrafts[c.signal_id]=el.value;
}
function orderHtml(c,i){
 const live=(c.order_instruction||deriveOrderInstruction(c,c.current_price));
 if(!live)return '';
 const trigger=live.trigger_price==null?'':' • trigger '+formatPlatformPrice(c.symbol,live.trigger_price);
 const limit=live.limit_price==null?'':' • limit '+formatPlatformPrice(c.symbol,live.limit_price);
 return '<div class="orderbox"><div class="small">Planned order type • based on latest confirmed 15m close</div>'
  +'<div class="ordername">'+esc((live.side?live.side+' ':'')+(live.order_type||'UNKNOWN'))+'</div>'
  +'<div class="small">'+esc(live.explanation||'')+esc(trigger)+esc(limit)+'</div>'
  +'<div id="order-hint-'+i+'" class="small" style="margin-top:6px">Enter the current TradingView price below to recalculate the order type before approval.</div></div>';
}
function updateOrderHint(i){
 const c=snapshot&&snapshot.cards?snapshot.cards[i]:null;
 const price=parsePlatformPrice(c.symbol,$('price-'+i)?.value);
 const h=$('order-hint-'+i);
 if(!h||!c)return;
 if(!Number.isFinite(price)||price<=0){h.textContent='Enter the current TradingView price to recalculate the order type before approval.';return;}
 const o=deriveOrderInstruction(c,price);
 if(!o){h.textContent='Order type unavailable.';return;}
 const ticket=$('ticket-order-'+i);
 if(ticket)ticket.textContent=(o.side?o.side+' ':'')+o.order_type;
 const parts=[(o.side?o.side+' ':'')+o.order_type,o.explanation];
 if(o.trigger_price!=null)parts.push('Trigger '+formatPlatformPrice(c.symbol,o.trigger_price));
 if(o.limit_price!=null)parts.push('Limit '+formatPlatformPrice(c.symbol,o.limit_price));
 h.textContent='LIVE PRICE CHECK: '+parts.join(' • ');
}
function planHtml(p,c){
 if(!p)return '<div class="row"><span>Locked plan</span><span class="value">None</span></div>';
 const left=secondsUntil(p.valid_until);
 return '<div class="row"><span>Direction</span><span class="value">'+esc(p.direction||'-')+'</span></div>'
  +'<div class="row"><span>Decision timeframe</span><span class="value">'+esc(p.decision_timeframe||'15')+' min</span></div>'
  +'<div class="row"><span>Entry zone</span><span class="value">'+formatPlatformPrice(c&&c.symbol,p.entry_min,'floor')+' → '+formatPlatformPrice(c&&c.symbol,p.entry_max,'ceil')+'</span></div>'
  +'<div class="row"><span>Stop loss</span><span class="value">'+planPriceText(c,p.initial_stop,'stop')+'</span></div>'
  +'<div class="row"><span>Management checkpoint</span><span class="value">'+planPriceText(c,p.target1,'target')+' • no partial TP order</span></div>'
  +'<div class="row"><span>Final take profit</span><span class="value">'+planPriceText(c,p.target2,'target')+'</span></div>'
  +'<div class="row"><span>Expires</span><span class="value">'+formatLocalTime(p.valid_until)+' • <span class="countdown" data-valid-until="'+esc(p.valid_until)+'">'+formatCountdown(left)+'</span></span></div>';
}

function sizingHtml(s,c){
 if(!s)return '';
 const limited=(s.risk_budget_limited_by||[]).join(', ');
 const riskPct=Number(s.equity_usd)>0?Number(s.risk_amount_usd)/Number(s.equity_usd)*100:0;
 const p=c&&c.locked_trade_plan?c.locked_trade_plan:null;
 return '<div class="orderbox"><div class="small">STC POSITION SIZE • use this quantity unless the competition platform forces a smaller valid amount • MAX STC QUANTITY • DO NOT EXCEED</div>'
  +'<div class="ordername">'+num(s.proposed_quantity,6)+' units/contracts</div>'
  +'<div class="small bad"><b>Enter this as Units / Contracts only.</b> Never copy trade value, margin, leverage value, or % balance into the quantity field.</div>'
  +'<div class="row"><span>Risk on this trade</span><span class="value">$'+num(s.risk_amount_usd,2)+' • '+num(riskPct,3)+'%</span></div>'
  +'<div class="row"><span>Configured risk budget</span><span class="value">$'+num(s.risk_budget_usd,2)+' • '+num(Number(s.risk_fraction)*100,3)+'%</span></div>'
  +'<div class="row"><span>Official max open position</span><span class="value">'+num(s.max_position,6)+'</span></div>'
  +'<div class="row"><span>Projected open after</span><span class="value">'+num(s.projected_open_quantity,6)+'</span></div>'
  +(p?'<div class="row"><span>Stop loss</span><span class="value">'+planPriceText(c,p.initial_stop,'stop')+'</span></div>':'')
  +(p?'<div class="row"><span>Final take profit</span><span class="value">'+planPriceText(c,p.target2,'target')+'</span></div>':'')
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

function convictionHtml(c){
 const q=Number(c.setup_quality_score);
 const qText=Number.isFinite(q)?Math.round(q)+'/100':'not scored';
 const p=c.empirical_win_probability||{};
 let pText='NOT CALIBRATED';
 if(p.estimated_probability!==null&&p.estimated_probability!==undefined&&Number.isFinite(Number(p.estimated_probability))){
   pText=num(Number(p.estimated_probability)*100,1)+'% • n='+esc(p.sample_size||0);
   if(Number.isFinite(Number(p.confidence_low))&&Number.isFinite(Number(p.confidence_high))){
     pText+=' • CI '+num(Number(p.confidence_low)*100,1)+'–'+num(Number(p.confidence_high)*100,1)+'%';
   }
 }else if(p.sample_size){
   pText='NOT CALIBRATED • n='+esc(p.sample_size);
 }

 const rc=c.research_calibration||{};
 let calibrationText='No matching live-timeframe calibration';
 let featureHtml='';
 if(rc.status==='AVAILABLE_INFORMATIONAL'||rc.strategy_id){
   calibrationText=esc(rc.strategy_id||'-')+' @ '+esc(rc.timeframe||'-')
     +' • robust '+num(rc.robust_score,2)
     +' • data '+(rc.data_end_utc?formatLocalTime(rc.data_end_utc):'-');
   const fw=rc.feature_weights||{};
   const features=Object.entries(fw)
     .filter(([,v])=>Number.isFinite(Number(v))&&Number(v)>0)
     .sort((a,b)=>Number(b[1])-Number(a[1]))
     .slice(0,8)
     .map(([k,v])=>'<span class="pill">'+esc(k)+' '+num(Number(v)*100,1)+'%</span>')
     .join('');
   if(features){
     featureHtml='<div class="small" style="margin-top:6px"><b>Validated feature participation:</b> '+features+'</div>';
   }
 }

 const t=c.timeframe_confirmation||{};
 function tf(label,key){
   const v=t[key];
   return '<span class="pill">'+esc(label)+' '+(v===null||v===undefined?'-':(Number(v)>=0?'+':'')+num(v,2))+'</span>';
 }
 const mtf=tf(String(t.entry_timeframe||'15')+'m','entry_score')
   +tf('1H','1h_score')+tf('2H','2h_score')+tf('4H','4h_score')+tf('1D','1d_score')+tf('1M','1m_score');

 const f=c.live_family_evidence||null;
 let familyHtml='<div class="small wait" style="margin-top:6px">Family evidence: unavailable — candidate cannot pass the A+ breadth gate.</div>';
 if(f){
   const fs=f.family_scores||{};
   const fw=f.family_weights_used||{};
   function fam(label,key){
     const v=fs[key];
     const w=fw[key];
     const scoreText=v===null||v===undefined?'-':(Number(v)>=0?'+':'')+num(v,2);
     const weightText=Number.isFinite(Number(w))?' • w '+num(Number(w)*100,1)+'%':'';
     return '<span class="pill">'+esc(label)+' '+scoreText+weightText+'</span>';
   }
   const familyPills=fam('Trend','trend')+fam('Momentum','momentum')+fam('Volatility','volatility')
     +fam('Volume','volume')+fam('VWAP','vwap')+fam('Structure','market_structure')
     +fam('SMC','smc_liquidity')+fam('Price Action','price_action')+fam('Micro','microstructure');
   familyHtml='<div class="row"><span>Independent evidence families</span><span class="value">'
     +(Number(f.score)>=0?'+':'')+num(f.score,2)+' • agreement '+num(Number(f.agreement_ratio)*100,0)
     +'% • aligned '+esc(f.aligned_families||0)+'/9 • conflicts '+esc(f.conflicting_families||0)+'</span></div>'
     +'<div class="small" style="margin-top:6px">'+familyPills+'</div>';
 }

 return '<div class="orderbox"><div class="small">CONVICTION / VALIDATION</div>'
   +'<div class="row"><span>Setup quality</span><span class="value">'+esc(qText)+' • '+esc(c.setup_grade||'MONITOR_ONLY')+'</span></div>'
   +'<div class="row"><span>Empirical win probability</span><span class="value">'+esc(pText)+'</span></div>'
   +'<div class="row"><span>Research strategy</span><span class="value">'+calibrationText+'</span></div>'
   +'<div class="small">Setup Quality is not win probability. Probability is shown only after out-of-sample + forward calibration on the same live entry timeframe.</div>'
   +featureHtml
   +'<div class="small" style="margin-top:6px">'+mtf+'</div>'
   +familyHtml+'</div>';
}

function latestLockedPlanContextHtml(c){
 const x=c&&c.latest_signal_context;
 if(!x||x.same_event)return '';
 const compatible=x.approval_compatible_with_locked_plan!==false;
 const failures=Array.isArray(x.quality_gate_failures)&&x.quality_gate_failures.length
   ?x.quality_gate_failures.map(esc).join(', ')
   :'none';
 const cls=compatible?'ok':'wait';
 const headline=compatible
   ?'LOCKED PLAN PRESERVED • latest bar remains same-direction'
   :'LOCKED PLAN PRESERVED FOR RECOVERY • latest bar no longer aligned for a new approval';
 return '<div class="record-guide '+cls+'" style="margin-top:10px"><b>'+headline+'</b>'
   +'<div class="small" style="margin-top:4px">Latest context: '
   +esc(x.pre_gate_recommendation||x.recommendation||'WAIT')
   +' • quality '+esc(x.setup_quality_score==null?'-':x.setup_quality_score+'/100')
   +' • '+esc(x.setup_grade||'MONITOR_ONLY')
   +' • failures: '+failures+'</div></div>';
}

function approvedExecutionTicketHtml(c){
 const t=c&&c.approval&&c.approval.execution_ticket;
 if(!t)return '';
 const oi=t.order_instruction||{};
 const order=(oi.side?oi.side+' ':'')+(oi.order_type||'ENTRY');
 return '<div class="orderbox"><div class="small ok"><b>APPROVED EXECUTION TICKET</b> • valid only while the 60-second approval remains fresh</div>'
  +'<div class="row"><span>MAX STC QUANTITY</span><span class="value ok">'+num(t.max_quantity,6)+'</span></div>'
  +'<div class="row"><span>Order</span><span class="value">'+esc(order)+'</span></div>'
  +'<div class="row"><span>Approved quote</span><span class="value">'+formatPlatformPrice(c.symbol,t.approved_quote_price)+'</span></div>'
  +'<div class="row"><span>Stop loss</span><span class="value">'+formatPlatformPrice(c.symbol,t.initial_stop)+'</span></div>'
  +'<div class="row"><span>Final take profit</span><span class="value">'+formatPlatformPrice(c.symbol,t.final_take_profit)+'</span></div>'
  +'<div class="small bad"><b>Never exceed MAX STC QUANTITY.</b> Enter the number in Units / Contracts only. Smaller is allowed. If price/order conditions change, reconfirm instead of improvising.</div>'
  +'</div>';
}

function cardHtml(c,i){
 const active=isOpportunityActive(c);
 const cls=c.recommendation==='LONG'?'long':c.recommendation==='SHORT'?'short':'wait';
 const a=c.approval||{};
 const reasons=(c.reasons||[]).slice(0,12).map(x=>'<span class="pill">'+esc(x)+'</span>').join('');
 const sizingAllowed=!c.position_sizing || (c.position_sizing.allowed_by_position_limit!==false && c.position_sizing.allowed_by_risk_policy!==false);
 const macroAllowed=!(c.macro_context&&c.macro_context.block_new_approval);
 const cooldownActive=!!(c.loss_cooldown&&c.loss_cooldown.active);
 const controlOpen=!!(snapshot&&snapshot.runtime_control&&!snapshot.runtime_control.safe_mode&&!snapshot.runtime_control.kill_switch);
 const latestCompatible=!c.latest_signal_context||c.latest_signal_context.same_event||c.latest_signal_context.approval_compatible_with_locked_plan!==false;
 const canApprove=active&&(c.recommendation==='LONG'||c.recommendation==='SHORT')&&!!c.locked_trade_plan&&sizingAllowed&&macroAllowed&&!cooldownActive&&controlOpen&&latestCompatible;
 const competitionLabel=c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa';
 const recoveryOnly=isLockedPlanVisible(c)&&!active;
 const statusBadge=c.recommendation==='WAIT'
   ?'<span class="badge blocked">WAIT</span>'
   :(active?'<span class="badge active">ACTIVE NOW</span>':recoveryOnly?'<span class="badge blocked">RECOVERY ONLY</span>':'<span class="badge expired">EXPIRED</span>');
 let blockReason='';
 if(c.has_open_position)blockReason='An executed position is already tracked for this symbol. New signals are used to manage that position, not to create a replacement trade.';
 else if(c.quality_gate_passed===false&&c.pre_gate_recommendation&&c.pre_gate_recommendation!=='WAIT')blockReason='MONITOR ONLY: this directional candidate failed its required quality gate and cannot be approved or notified as a trade.';
 else if(!active&&c.recommendation!=='WAIT')blockReason='Expired opportunities are removed automatically from opportunity lists.';
 else if(active&&!latestCompatible)blockReason='The locked plan is still shown so an already-filled trade can be recorded, but the newest confirmed bar is no longer aligned. Do not create a new entry from this plan.';
 else if(!controlOpen)blockReason='SAFE MODE / KILL SWITCH is ON. Enable manual approval mode before approving.';
 else if(cooldownActive)blockReason='ANTI-CHURN COOLDOWN: a recent losing trade in the same symbol/direction is too recent. Wait for a fresh setup after the cooldown.';
 else if(!sizingAllowed)blockReason='New entry blocked by sizing / risk capacity.';
 else if(!macroAllowed)blockReason='New entry blocked by macro-risk gate.';

 const p=c.locked_trade_plan;
 const live=(c.order_instruction||deriveOrderInstruction(c,c.current_price));
 const actionText=(live&&live.side?live.side+' ':'')+(live&&live.order_type?live.order_type:(c.recommendation==='LONG'?'BUY':c.recommendation==='SHORT'?'SELL':'WAIT'));
 const s=sizeModeText(c);
 const riskPct=c.position_sizing&&Number(c.position_sizing.equity_usd)>0
   ?Number(c.position_sizing.risk_amount_usd)/Number(c.position_sizing.equity_usd)*100:null;
 const draft=livePriceDrafts[c.signal_id]||'';
 const ticketClass=active?'ticket actionable':'ticket blockedticket';

 let ticket='';
 if(c.has_open_position){
   ticket='<div class="ticket blockedticket"><div class="ticket-title">POSITION CONTEXT — NO NEW ENTRY</div>'
     +'<div class="ticket-action '+cls+'">'+esc(c.recommendation)+' SIGNAL • '+esc(c.symbol)+'</div>'
     +'<div class="ticket-note">Telegram/server signal received, but STC already tracks an open position for this symbol. Use the Portfolio Supervisor; do not add a new trade from this signal.</div></div>';
 }else{
   ticket='<div class="'+ticketClass+'"><div class="ticket-title">EXECUTION TICKET</div>'
     +'<div class="ticket-action '+cls+'">'+esc(c.recommendation==='LONG'?'BUY / LONG':c.recommendation==='SHORT'?'SELL / SHORT':'DO NOT ENTER')+' • '+esc(c.symbol)+'</div>';
 }
 if(!c.has_open_position&&p){
   ticket+='<div class="ticket-grid">'
     +'<div class="ticket-cell"><div class="ticket-label">ORDER TO PLACE</div><div class="ticket-value" id="ticket-order-'+i+'">'+esc(actionText)+'</div></div>'
     +'<div class="ticket-cell"><div class="ticket-label">QUANTITY</div><div class="ticket-value">'+esc(s.qty)+' '+esc(s.unit)+'</div><div class="ticket-note">'+esc(s.mode)+'</div></div>'
     +'<div class="ticket-cell"><div class="ticket-label">ENTRY ZONE</div><div class="ticket-value">'+formatPlatformPrice(c.symbol,p.entry_min,'floor')+' → '+formatPlatformPrice(c.symbol,p.entry_max,'ceil')+'</div></div>'
     +'<div class="ticket-cell"><div class="ticket-label">STOP LOSS</div><div class="ticket-value">'+planPriceText(c,p.initial_stop,'stop')+'</div></div>'
     +'<div class="ticket-cell"><div class="ticket-label">FINAL TAKE PROFIT</div><div class="ticket-value">'+planPriceText(c,p.target2,'target')+'</div><div class="ticket-note">One final TP only. Do not place a separate TP1 order.</div></div>'
     +'<div class="ticket-cell"><div class="ticket-label">RISK</div><div class="ticket-value">'+(c.position_sizing?'$'+num(c.position_sizing.risk_amount_usd,2):'-')+(riskPct!==null?' • '+num(riskPct,3)+'%':'')+'</div></div>'
     +'</div>'
     +latestLockedPlanContextHtml(c)
     +'<div class="ticket-input"><label class="small"><b>LIVE PRICE BEFORE APPROVAL</b> — copy the current TradingView price here</label>'
     +'<input id="price-'+i+'" type="text" autocomplete="off" value="'+esc(draft)+'" placeholder="Current TradingView price — decimal or exchange quote" oninput="updateOrderHint('+i+');savePriceDraft('+i+')">'
     +'<div id="order-hint-'+i+'" class="ticket-note">Enter the live price. STC will tell you MARKET / LIMIT / STOP-LIMIT before approval.</div></div>';
   if(canApprove){
     ticket+='<div class="buttonrow"><button class="safe" onclick="approveCard('+i+',\'approve\')">Approve this plan</button><button class="danger" onclick="approveCard('+i+',\'reject\')">Reject</button></div>';
   }
   ticket+='<div id="approval-feedback-'+i+'" class="small" style="margin-top:6px"></div>'
     +'<div class="buttonrow"><button onclick="recordExistingPositionFromCard('+i+')">Already filled on platform? Record position</button>'
     +(active&&a.decision==='approved'?'<button class="primary" onclick="recordFilledPosition('+i+')">After manual fill: record open position</button>':'')
     +'</div>';
 } else if(!c.has_open_position) {
   ticket+='<div class="ticket-note">No locked executable plan. Do not place a trade from this card.</div>';
 }
 if(!c.has_open_position)ticket+='</div>';

 const advanced='<details class="advanced"><summary>Advanced details / why STC selected this setup</summary><div class="advanced-body">'
   +'<div class="statusline">'+statusBadge+'<span class="pill">'+esc(competitionLabel)+'</span><span class="pill">'+esc(c.setup_grade||'MONITOR_ONLY')+'</span></div>'
   +'<div class="row"><span>Signal score</span><span class="value '+cls+'">'+esc(c.recommendation)+' '+num(c.composite_score,2)+'</span></div>'
   +'<div class="row"><span>Latest confirmed bar</span><span class="value">'+formatLocalTime(c.source_close_time||c.source_time)+' • '+formatAgeSeconds(c.source_age_seconds)+'</span></div>'
   +convictionHtml(c)+planHtml(p,c)+sizingHtml(c.position_sizing,c)+approvedExecutionTicketHtml(c)+macroHtml(c.macro_context)
   +'<div class="row"><span>Approval</span><span class="value">'+esc(a.decision||'not approved yet')+'</span></div>'
   +'<div class="row"><span>Ready to execute</span><span class="value '+(c.manual_execution_ready?'ok':'wait')+'">'+(c.manual_execution_ready?'YES':'NO')+'</span></div>'
   +(blockReason?'<div class="small wait" style="margin:8px 0">'+esc(blockReason)+'</div>':'')
   +'<div class="small" style="margin:8px 0">'+reasons+'</div></div></details>';

 return '<div class="card" data-card-index="'+i+'">'+ticket+advanced+'</div>';
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
   const body=c.symbol+' • A+ '+c.recommendation+' • Quality '+(Number.isFinite(Number(c.setup_quality_score))?Math.round(Number(c.setup_quality_score))+'/100':'-')+' • '+(oi.order_type||'ENTRY')+' • Entry '+formatPlatformPrice(c.symbol,c.locked_trade_plan.entry_min,'floor')+' - '+formatPlatformPrice(c.symbol,c.locked_trade_plan.entry_max,'ceil')+' • SL '+planPriceText(c,c.locked_trade_plan.initial_stop,'stop')+' • Final TP '+planPriceText(c,c.locked_trade_plan.target2,'target')+' • Expires '+formatLocalTime(c.locked_trade_plan.valid_until);
   document.title='A+ '+c.recommendation+' • '+c.symbol+' • STC';
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC QUALIFIED PLAN',{body,tag:key,requireInteraction:true});
     seenSignalPlans.add(key);
     persistSeenSet('stc_seen_signal_plans',seenSignalPlans);
   }
 }
}

function competitionOf(c){
 return c.competition_id==='amp-futures-sep-2026'?'amp':c.competition_id==='capital-africa-sep-2026'?'capital':'other';
}
function shouldShowSignalCard(c){
 if(!c)return false;
 if(c.recommendation==='WAIT')return true;
 if(!(c.recommendation==='LONG'||c.recommendation==='SHORT'))return false;
 if(c.has_open_position)return true;
 return isLockedPlanVisible(c);
}
function renderCards(target,cards){
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 const visible=(cards||[]).filter(shouldShowSignalCard);
 $(target).innerHTML=visible.map(c=>cardHtml(c,all.indexOf(c))).join('')||'<div class="card">No current signals or active opportunities.</div>';
 for(const card of visible){
   const i=all.indexOf(card);
   if(livePriceDrafts[card.signal_id])updateOrderHint(i);
 }
}

function riskSummaryFor(competitionId){
 const s=snapshot&&snapshot.portfolio&&snapshot.portfolio.summary?snapshot.portfolio.summary[competitionId]:null;
 return s||{open_positions:0,initial_risk_usd:0,clusters:{}};
}
function rulesHtml(competitionId){
 const r=snapshot&&snapshot.competition_rules?snapshot.competition_rules[competitionId]:null;
 if(!r)return '';
 const leverage=Object.entries(r.leverage||{}).map(([k,v])=>esc(k)+' '+num(v,0)+':1').join(' • ');
 const scoring=r.scoring_basis==='realized_pnl_closed_positions'?'Realized P/L on closed positions':esc(r.scoring_basis||'-');
 return '<div class="orderbox"><div class="small">COMPETITION RULES</div>'
  +'<div class="row"><span>Competition</span><span class="value">'+esc(r.name||competitionId)+'</span></div>'
  +'<div class="row"><span>Initial balance</span><span class="value">$'+num(r.initial_balance_usd,2)+'</span></div>'
  +'<div class="row"><span>First prize</span><span class="value">$'+num(r.first_prize_usd,2)+'</span></div>'
  +'<div class="row"><span>Competition window</span><span class="value">'+esc(formatLocalTime(r.start_utc))+' → '+esc(formatLocalTime(r.end_utc))+'</span></div>'
  +'<div class="row"><span>Minimum trading days</span><span class="value">'+esc(r.min_trading_days)+'</span></div>'
  +'<div class="row"><span>Scoring</span><span class="value">'+scoring+'</span></div>'
  +'<div class="row"><span>Leverage</span><span class="value">'+esc(leverage||'-')+'</span></div>'
  +'<div class="row"><span>Commission</span><span class="value">'+num(Number(r.commission_rate||0)*100,3)+'%</span></div>'
  +'<div class="row"><span>STC production feed</span><span class="value">'+esc(r.production_feed_symbols)+' symbols currently configured</span></div>'
  +(r.verified_feed_symbols_after_24x7_crypto_alert?'<div class="row"><span>Verified coverage after 24x7 crypto alert</span><span class="value">'+esc(r.verified_feed_symbols_after_24x7_crypto_alert)+' unique symbols</span></div>':'')
  +(r.official_allowed_symbols?'<div class="row"><span>Official competition universe</span><span class="value">'+esc(r.official_allowed_symbols)+' allowed symbols</span></div>':'')
  +'<div class="small"><a href="'+esc(r.official_rules_url||'#')+'" target="_blank" rel="noopener">Open official competition rules</a></div>'
  +'</div>';
}

function progressHtml(competitionId){
 const p=snapshot&&snapshot.competition_progress?snapshot.competition_progress[competitionId]:null;
 if(!p)return '';
 const urgency=String(p.qualification_urgency||'ON_TRACK');
 const urgencyClass=urgency==='QUALIFIED'?'ok':urgency==='ON_TRACK'?'wait':'bad';
 const urgencyText=urgency==='MUST_TRADE_TODAY'
   ?'CRITICAL: today must count as a trading day to preserve qualification eligibility'
   :urgency==='INSUFFICIENT_REMAINING_UTC_DATES'
   ?'Qualification is no longer possible from STC-recorded days unless prior activity is missing from the ledger'
   :urgency==='QUALIFIED'
   ?'Minimum trading-day requirement satisfied'
   :'Qualification pace is currently on track';
 return '<div class="orderbox"><div class="small">COMPETITION PROGRESS</div>'
  +'<div class="row"><span>Qualifying trading days</span><span class="value">'+esc(p.qualifying_trading_days)+' / '+esc(p.required_trading_days)+'</span></div>'
  +'<div class="row"><span>Qualification days still needed</span><span class="value">'+esc(p.qualifying_days_remaining??p.days_remaining)+'</span></div>'
  +'<div class="row"><span>UTC calendar dates left incl. today</span><span class="value">'+esc(p.utc_calendar_dates_remaining_including_today??'-')+'</span></div>'
  +'<div class="row"><span>Qualification status</span><span class="value '+urgencyClass+'">'+esc(urgencyText)+'</span></div>'
  +'<div class="row"><span>Trades entered</span><span class="value">'+esc(p.total_entries)+'</span></div>'
  +'<div class="row"><span>Open / closed</span><span class="value">'+esc(p.open_positions)+' / '+esc(p.closed_positions)+'</span></div>'
  +'<div class="row"><span>Recorded trade actions</span><span class="value">'+esc(p.position_actions)+'</span></div>'
  +'<div class="row"><span>Realized competition P/L</span><span class="value">function tradeInventoryHtml(competitionId){
 const p=snapshot&&snapshot.competition_progress?snapshot.competition_progress[competitionId]:null;
 const s=riskSummaryFor(competitionId);
 if(!p)return '';
 const openCount=Number(p.open_positions||0);
 const closedCount=Number(p.closed_positions||0);
 const known=Number(s.open_unrealized_known_positions||0);
 const unknown=Number(s.open_unrealized_unknown_positions||0);
 const openPnl=Number(s.open_unrealized_pnl_usd||0);
 const realized=Number(p.realized_pnl_usd||0);
 let openPnlText='$0.00';
 if(openCount>0){
   openPnlText=known>0
     ?'$'+num(openPnl,2)+(unknown>0?' • PARTIAL; '+unknown+' open trade(s) waiting for an STC mark':'')
     :'Unavailable • waiting for an STC market mark';
 }
 const trackedPnl=unknown===0?realized+openPnl:null;
 return '<div class="orderbox"><div class="small">TRADE INVENTORY — THIS COMPETITION</div>'
  +'<div class="row"><span>Open trades</span><span class="value">'+openCount+'</span></div>'
  +'<div class="row"><span>Completed trades</span><span class="value">'+closedCount+'</span></div>'
  +'<div class="row"><span>Open P/L estimate</span><span class="value '+(known>0?(openPnl>=0?'ok':'bad'):'')+'">'+esc(openPnlText)+'</span></div>'
  +'<div class="row"><span>Realized P/L</span><span class="value '+(realized>=0?'ok':'bad')+'">$'+num(realized,2)+'</span></div>'
  +'<div class="row"><span>Tracked P/L</span><span class="value '+(trackedPnl==null?'wait':trackedPnl>=0?'ok':'bad')+'">'+(trackedPnl==null?'Incomplete — one or more open marks unavailable':'$'+num(trackedPnl,2))+'</span></div>'
  +'<div class="small">Open P/L is an STC estimate using the latest confirmed STC bar close available for each tracked position. It is not a broker live quote and does not change official competition scoring, which uses realized P/L.</div>'
  +'</div>';
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
 return rulesHtml(competitionId)
  +progressHtml(competitionId)
  +tradeInventoryHtml(competitionId)
  +'<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
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
 const latest=(p.latest_signal_history||[]).slice(-1)[0]||null;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<div class="small wait">Partial take-profit is disabled in single-TP mode. Keep the full quantity unless another management rule says EXIT_NOW.</div>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="statusline"><span class="badge active">EXECUTED • TRACKING</span><span class="pill">'+esc(p.origin==='manual_external'?'Imported manual trade':'STC plan fill')+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(p.symbol)+'</span></div>'
  +'<div class="row"><span>Position</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Opened</span><span class="value">'+formatLocalTime(p.opened_at_utc)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+formatPlatformPrice(p.symbol,p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+formatPlatformPrice(p.symbol,p.current_stop)+'</span></div>'
  +'<div class="row"><span>Management checkpoint</span><span class="value">'+formatPlatformPrice(p.symbol,p.target1)+' • no partial close</span></div>'
  +'<div class="row"><span>Final take profit</span><span class="value">'+formatPlatformPrice(p.symbol,p.target2)+'</span></div>'
  +(latest?'<div class="row"><span>Latest market check — STC bar mark</span><span class="value">'+formatLocalTime(latest.time)+' • '+esc(latest.recommendation)+' '+num(latest.composite_score,2)+' @ '+formatPlatformPrice(p.symbol,latest.close)+'</span></div>':'<div class="small wait">No STC market mark is available yet for this open position.</div>')
  +'<div class="row"><span>What to do now</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+(m.r_multiple==null?'-':num(m.r_multiple,2))+'</span></div>'
  +'<div class="row"><span>Unrealized P/L estimate</span><span class="value '+(m.unrealized_pnl_usd==null?'wait':Number(m.unrealized_pnl_usd)>=0?'ok':'bad')+'">'+(m.unrealized_pnl_usd==null?'Unavailable':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +'<div class="small">The mark and open P/L above use STC confirmed bar data, not a broker live quote. Use the competition platform for the exact live P/L.</div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}
function closedPositionHtml(p){
 return '<div class="card">'
  +'<div class="statusline"><span class="badge">CLOSED • RECORDED</span><span class="pill">'+esc(p.origin==='manual_external'?'Imported manual trade':'STC plan fill')+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(p.symbol)+'</span></div>'
  +'<div class="row"><span>Position</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.initial_quantity,6)+'</span></div>'
  +'<div class="row"><span>Opened</span><span class="value">'+formatLocalTime(p.opened_at_utc)+'</span></div>'
  +'<div class="row"><span>Closed</span><span class="value">'+formatLocalTime(p.closed_at_utc)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+formatPlatformPrice(p.symbol,p.entry_price)+'</span></div>'
  +'<div class="row"><span>Exit</span><span class="value">'+(p.exit_price==null?'-':formatPlatformPrice(p.symbol,p.exit_price))+'</span></div>'
  +'<div class="row"><span>Realized P/L</span><span class="value '+(Number(p.realized_pnl_usd||0)>=0?'ok':'bad')+'">$'+num(p.realized_pnl_usd,2)+'</span></div>'
  +'</div>';
}
function renderClosedPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(closedPositionHtml).join('')||'<div class="card">No completed trades recorded in STC for this competition yet.</div>';
}

function watchlistHtml(c){
 const direction=Number(c.composite_score||0)>0?'LONG BIAS':Number(c.composite_score||0)<0?'SHORT BIAS':'NEUTRAL';
 const failures=(c.quality_gate_failures||[]).length
   ?(c.quality_gate_failures||[]).slice(0,8)
   :(c.reasons||[]).filter(x=>String(x).startsWith('gate_block=')).slice(0,8);
 const missing=(c.reasons||[]).filter(x=>/unavailable|gate_block=.*present|gate_block=.*alignment|family_/i.test(String(x))).slice(0,10);
 return '<div class="card">'
  +'<div class="statusline"><span class="badge blocked">WATCH ONLY</span><span class="pill">'+esc(c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa')+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Current bias</span><span class="value '+(direction==='LONG BIAS'?'long':direction==='SHORT BIAS'?'short':'wait')+'">'+esc(direction)+' • '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Confidence</span><span class="value">'+num(Number(c.confidence||0)*100,1)+'%</span></div>'
  +(Number.isFinite(Number(c.setup_quality_score))?'<div class="row"><span>Setup quality</span><span class="value">'+Math.round(Number(c.setup_quality_score))+'/100</span></div>':'')
  +'<div class="row"><span>Latest confirmed price</span><span class="value">'+num(c.current_price,6)+'</span></div>'
  +'<div class="small wait" style="margin-top:8px">NOT ACTIONABLE — no locked plan. Do not enter from this card.</div>'
  +(failures.length?'<div class="small" style="margin-top:8px"><b>Gate blockers:</b> '+failures.map(x=>esc(String(x).replace('gate_block=',''))).join(' • ')+'</div>':'')
  +(missing.length?'<div class="small" style="margin-top:6px"><b>Missing/unaligned evidence:</b> '+missing.map(x=>esc(String(x))).join(' • ')+'</div>':'')
  +'</div>';
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
 const missingMtf=cards.filter(c=>(c.reasons||[]).some(x=>/confirmation_1h=unavailable|trend_2h=unavailable|trend_4h=unavailable|family_evidence=unavailable/i.test(String(x)))).length;
 if(missingMtf){
   $('overview-summary').innerHTML+='<div class="card"><div class="small bad">MTF LIVE CONFIRMATION</div><div class="big bad">OFFLINE</div><div class="small">'+missingMtf+'/'+cards.length+' cards are missing higher-timeframe/family evidence. A+ opportunities can remain blocked until the v1.1 MTF production feeds are activated.</div></div>';
 }
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
 const watch=[...cards]
   .filter(c=>!isOpportunityActive(c)&&c.recommendation==='WAIT'&&Math.abs(Number(c.composite_score||0))>0)
   .sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)))
   .slice(0,8);
 $('watchlist-cards').innerHTML=watch.length
   ?watch.map(watchlistHtml).join('')
   :'<div class="card">No directional watchlist candidates at the moment.</div>';
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
 const closedPositions=(snapshot.portfolio&&snapshot.portfolio.closed_positions_recent)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotifyQualification();
 renderClosedPositions('capital-closed-positions',closedPositions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderClosedPositions('amp-closed-positions',closedPositions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

function notificationEventHtml(e){
 const cls=e.event_type==='NEW_LOCKED_PLAN'?'active':e.event_type==='POSITION_MANAGEMENT'?'blocked':'';
 return '<div class="card">'
   +'<div class="statusline"><span class="badge '+cls+'">'+esc(e.event_type||'EVENT')+'</span>'
   +(e.symbol?'<span class="pill">'+esc(e.symbol)+'</span>':'')+'</div>'
   +'<div class="row"><span>Sent</span><span class="value">'+formatLocalTime(e.created_at_utc)+'</span></div>'
   +'<div class="row"><span>Title</span><span class="value">'+esc(e.title||'-')+'</span></div>'
   +'<details class="advanced"><summary>Message body</summary><div class="advanced-body small" style="white-space:pre-wrap">'+esc(e.body_text||'')+'</div></details>'
   +'</div>';
}
function renderNotificationEvents(events){
 const recent=(events||[]).slice(0,20);
 if($('server-notify-events'))$('server-notify-events').innerHTML=recent.map(notificationEventHtml).join('')
   ||'<div class="card">No server notification events recorded yet.</div>';
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   renderNotificationEvents(notificationStatus.events||[]);
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification audit loaded. Recent Telegram/server events are shown below.';
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
function maybeNotifyQualification(){
 if(!snapshot || !snapshot.competition_progress)return;
 for(const [cid,p] of Object.entries(snapshot.competition_progress)){
   if(!p || p.qualification_urgency!=='MUST_TRADE_TODAY')continue;
   const key='qualification|'+cid+'|'+new Date().toISOString().slice(0,10);
   if(seenManagement.has(key))continue;
   if('Notification' in window && Notification.permission==='granted'){
     new Notification('STC QUALIFICATION URGENT',{body:(cid==='amp-futures-sep-2026'?'AMP Futures':'Competition')+' • today must contain an opening or closing action to preserve minimum trading-day eligibility.',tag:key,requireInteraction:true});
     seenManagement.add(key);
     persistSeenSet('stc_seen_management',seenManagement);
   }
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

async function recordClosedTradeHistory(competitionId){
 const symbol=String(prompt('Historical symbol exactly as shown in STC / TradingView','')||'').trim();
 if(!symbol)return;
 const side=String(prompt('Historical side: LONG or SHORT','LONG')||'').trim().toUpperCase();
 if(!(side==='LONG'||side==='SHORT')){alert('Side must be LONG or SHORT.');return;}
 const qty=Number(prompt('Historical filled quantity',''));
 const entry=Number(prompt('Historical average entry price',''));
 const exit=Number(prompt('Historical average/final exit price',''));
 if(![qty,entry,exit].every(x=>Number.isFinite(x)&&x>0)){alert('Enter valid positive quantity, entry and exit prices.');return;}
 const openedText=String(prompt('Original open date/time (example 2026-09-20 14:35)','')||'').trim();
 const closedText=String(prompt('Original close date/time (example 2026-09-20 16:10)','')||'').trim();
 const opened=new Date(openedText);
 const closed=new Date(closedText);
 if(Number.isNaN(opened.getTime())||Number.isNaN(closed.getTime())||closed<opened){alert('Historical open/close times are invalid.');return;}
 const pnlText=String(prompt('Actual realized P/L in USD from the competition platform. Leave blank if unknown; STC will estimate it.','')||'').trim();
 let realized=null;
 if(pnlText!==''){
   realized=Number(pnlText);
   if(!Number.isFinite(realized)){alert('Realized P/L must be a valid number or left blank.');return;}
 }
 if(!confirm('Import this trade as ALREADY CLOSED historical competition activity? This only updates STC progress/audit and sends no order.'))return;
 const body={action:'IMPORT_CLOSED',competition_id:competitionId,symbol,side,quantity:qty,entry_price:entry,exit_price:exit,opened_at_utc:opened.toISOString(),closed_at_utc:closed.toISOString(),realized_pnl_usd:realized,note:'Owner-confirmed historical trade import'};
 try{
   await api('position.php',{method:'POST',body:JSON.stringify(body)});
   alert('Historical closed trade imported. Qualification progress and trade counts will refresh now.');
   await refresh();
 }catch(e){alert('Historical trade import failed: '+e.message);}
}

function setPositionModalMessage(message,kind='error'){
 const el=$('position-modal-message');
 if(!el)return;
 if(!message){el.className='hidden';el.textContent='';return;}
 el.className=kind==='success'?'inlinesuccess':'inlineerror';
 el.textContent=message;
}
function closePositionModal(){
 setPositionModalMessage('');
 showTab(recordReturnTab||'overview');
}
function updatePositionPricePreviews(){
 const symbol=$('pos-symbol').value.trim();
 for(const key of ['entry','stop','tp']){
   const raw=$('pos-'+key).value;
   const parsed=parsePlatformPrice(symbol,raw);
   const preview=$('pos-'+key+'-preview');
   if(!preview)continue;
   if(!raw.trim()){preview.textContent='';continue;}
   if(parsed===null){
     preview.textContent=priceRule(symbol)?"Invalid tick. Use TradingView form such as 105'12'5 or an exact tick-aligned decimal.":'Enter a valid positive price.';
     preview.className='fieldnote bad';
   }else{
     preview.textContent='Parsed: '+formatPlatformPrice(symbol,parsed);
     preview.className='fieldnote ok';
   }
 }
}
function recordExistingPosition(competitionId){
 // Compatibility/safety contract: ALREADY OPEN in the competition platform; no order will be sent.
 return openExistingPositionForm(competitionId,null);
}
function recordExistingPositionFromCard(cardIndex){
 const c=snapshot&&snapshot.cards?snapshot.cards[cardIndex]:null;
 if(!c)return;
 return openExistingPositionForm(c.competition_id,cardIndex);
}
function normalizePositionSymbolForCompetition(competitionId,symbol){
 const raw=String(symbol||'').trim().toUpperCase();
 if(!raw)return '';
 if(competitionId==='capital-africa-sep-2026'&&!raw.includes(':')){
   const allowed=new Set(['BTCUSD','ETHUSD','DOGEUSD','EURUSD','AUDUSD','USDZAR','XAUUSD','XAGUSD','SPX500','NAS100']);
   if(allowed.has(raw))return 'CAPITALCOM:'+raw;
 }
 return raw;
}
function normalizePositionTargetInputs(){
 const competitionId=$('pos-competition').value;
 const symbolInput=$('pos-symbol');
 if(symbolInput){
   symbolInput.value=normalizePositionSymbolForCompetition(competitionId,symbolInput.value);
 }
 updatePositionPricePreviews();
}

function openExistingPositionForm(competitionId,cardIndex=null){
 recordReturnTab=activeTab;
 const c=cardIndex!==null&&snapshot&&snapshot.cards?snapshot.cards[cardIndex]:null;
 const p=c&&c.locked_trade_plan?c.locked_trade_plan:null;
 $('pos-origin').value='manual_external';
 $('pos-competition').value=competitionId;
 $('pos-card-index').value=cardIndex===null?'':String(cardIndex);
 $('pos-symbol').value=c?c.symbol:'';
 $('pos-symbol').value=normalizePositionSymbolForCompetition(competitionId,$('pos-symbol').value);
 $('pos-side').value=p&&p.direction?p.direction:'LONG';
 $('pos-qty').value=c&&c.position_sizing&&c.position_sizing.proposed_quantity?c.position_sizing.proposed_quantity:'';
 $('pos-entry').value=c&&Number.isFinite(Number(c.current_price))?formatPlatformInput(c.symbol,c.current_price):'';
 $('pos-stop').value=p?formatPlatformInput(c.symbol,p.initial_stop,planTickMode(p.direction,'stop')):'';
 $('pos-tp').value=p?formatPlatformInput(c.symbol,p.target2,planTickMode(p.direction,'target')):'';
 $('pos-opened').value='';
 $('position-submit').textContent='Record open position';
 $('pos-qty-note').textContent=competitionId==='amp-futures-sep-2026'?'Enter contracts / units. Do NOT use % balance.':'Enter platform units. Do NOT use % balance.';
 setPositionModalMessage('');
 showTab('record');
 updatePositionPricePreviews();
}
function recordFilledPosition(i){
 const c=snapshot&&snapshot.cards?snapshot.cards[i]:null;
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){
   const feedback=$('approval-feedback-'+i); if(feedback)feedback.textContent='An approved locked plan is required before using the STC-plan fill workflow.';
   return;
 }
 if(!isOpportunityActive(c)){
   const feedback=$('approval-feedback-'+i); if(feedback)feedback.textContent='This locked plan expired. If the order is already open on the platform, use “Already filled on platform? Record position”.';
   return;
 }
 const p=c.locked_trade_plan;
 recordReturnTab=activeTab;
 $('pos-origin').value='stc_plan';
 $('pos-competition').value=c.competition_id;
 $('pos-card-index').value=String(i);
 $('pos-symbol').value=normalizePositionSymbolForCompetition(c.competition_id,c.symbol);
 $('pos-side').value=p.direction;
 const approvedMax=c.approval&&c.approval.execution_ticket?Number(c.approval.execution_ticket.max_quantity):NaN;
 $('pos-qty').value=Number.isFinite(approvedMax)&&approvedMax>0
   ?approvedMax
   :(c.position_sizing&&c.position_sizing.proposed_quantity?c.position_sizing.proposed_quantity:'');
 $('pos-entry').value=Number.isFinite(Number(c.current_price))?formatPlatformInput(c.symbol,c.current_price):formatPlatformInput(c.symbol,p.entry_mid);
 $('pos-stop').value=formatPlatformInput(c.symbol,p.initial_stop,planTickMode(p.direction,'stop'));
 $('pos-tp').value=formatPlatformInput(c.symbol,p.target2,planTickMode(p.direction,'target'));
 $('pos-opened').value='';
 $('position-submit').textContent='Record approved plan fill';
 $('pos-qty-note').textContent=c.competition_id==='amp-futures-sep-2026'?'Enter contracts / units. Do NOT use % balance.':'Enter platform units. Do NOT use % balance.';
 setPositionModalMessage('');
 showTab('record');
 updatePositionPricePreviews();
}
async function submitPositionModal(){
 const competitionId=$('pos-competition').value;
 const origin=$('pos-origin').value||'manual_external';
 const cardIndex=$('pos-card-index').value===''?null:Number($('pos-card-index').value);
 const symbol=normalizePositionSymbolForCompetition(competitionId,$('pos-symbol').value);
 $('pos-symbol').value=symbol;
 const side=$('pos-side').value.trim().toUpperCase();
 const qty=Number($('pos-qty').value);
 const entry=parsePlatformPrice(symbol,$('pos-entry').value);
 const stop=parsePlatformPrice(symbol,$('pos-stop').value);
 const finalTp=parsePlatformPrice(symbol,$('pos-tp').value);
 if(!(competitionId==='capital-africa-sep-2026'||competitionId==='amp-futures-sep-2026')){setPositionModalMessage('Select the competition first.');return;}
 if(!symbol){setPositionModalMessage('Symbol is required.');return;}
 if(!(side==='LONG'||side==='SHORT')){setPositionModalMessage('Side must be LONG or SHORT.');return;}
 if(!Number.isFinite(qty)||qty<=0){setPositionModalMessage('Enter the quantity actually filled.');return;}
 if(entry===null||stop===null||finalTp===null){setPositionModalMessage('One or more prices are invalid for this contract tick size. Use the TradingView quote format shown in the green preview.');return;}
 const geometryOk=side==='LONG'?(stop<entry&&finalTp>entry):(stop>entry&&finalTp<entry);
 if(!geometryOk){setPositionModalMessage('Stop / take-profit geometry does not match '+side+'.');return;}
 const openedText=$('pos-opened').value.trim();
 const openedAt=openedText?new Date(openedText):null;
 if(openedAt&&Number.isNaN(openedAt.getTime())){setPositionModalMessage('Open time is invalid.');return;}
 const openedUtc=openedAt?openedAt.toISOString():null;
 let body;
 if(origin==='stc_plan'){
   const c=cardIndex!==null&&snapshot&&snapshot.cards?snapshot.cards[cardIndex]:null;
   const p=c&&c.locked_trade_plan?c.locked_trade_plan:null;
   if(!c||!p||!c.approval||c.approval.decision!=='approved'){setPositionModalMessage('The approved STC plan is no longer available. Use the existing-manual-position workflow instead.');return;}
   const approvedTicket=c.approval.execution_ticket||null;
   const approvedMax=approvedTicket?Number(approvedTicket.max_quantity):NaN;
   if(Number.isFinite(approvedMax)&&approvedMax>0&&qty>approvedMax+Math.max(1e-9,approvedMax*1e-8)){
     setPositionModalMessage('BLOCKED: filled quantity exceeds the approved STC risk ticket. Maximum approved quantity is '+num(approvedMax,6)+'. If an oversized fill already happened on the platform, record it as an existing manual position for supervision; do not label it as an STC-compliant fill.');
     return;
   }
   body={action:'OPEN',origin:'stc_plan',competition_id:competitionId,symbol,side,quantity:qty,entry_price:entry,initial_stop:stop,current_stop:stop,target1:p.target1,target2:finalTp,source_plan_id:p.plan_id,opened_at_utc:openedUtc,note:'Owner-confirmed manual fill via inline form'};
 }else{
   const checkpoint=(entry+finalTp)/2;
   body={action:'OPEN',origin:'manual_external',competition_id:competitionId,symbol,side,quantity:qty,entry_price:entry,initial_stop:stop,current_stop:stop,target1:checkpoint,target2:finalTp,opened_at_utc:openedUtc,note:'Backfilled existing manual position via inline form; single final TP'};
 }
 $('position-submit').disabled=true;
 setPositionModalMessage('Saving position…','success');
 try{
   await api('position.php',{method:'POST',body:JSON.stringify(body)});
   setPositionModalMessage('Position recorded in STC. Portfolio Supervisor will track it now.','success');
   await refresh();
   setTimeout(()=>closePositionModal(),900);
 }catch(e){
   const raw=String(e&&e.message?e.message:e);
   const friendly=raw.includes('invalid_position_target')
     ?'Position target is not valid. Select the competition and use the supported symbol (for example CAPITALCOM:EURUSD).'
     :raw.includes('symbol_not_allowed')
       ?'That symbol is not enabled for the selected competition.'
       :raw.includes('manual_position_open_time_outside_competition_window')
         ?'The entered open time is before the configured competition start. Leave the field blank to use STC server time, or enter the real platform fill time.'
         :raw.includes('opened_at_out_of_range')
           ?'The entered open time is outside the allowed range. Leave it blank to use STC server time automatically.'
           :raw.includes('filled_quantity_exceeds_stc_risk_ticket')
             ?'BLOCKED: the filled quantity is larger than the approved STC maximum. Record an already-executed oversized trade as an existing manual position for supervision, not as an STC-compliant fill.'
             :raw.includes('stc_risk_capacity_unavailable_at_fill_record')
               ?'STC risk capacity changed or is unavailable. Do not add risk. If the platform fill already happened, use the existing-manual-position recovery workflow.'
               :raw;
   setPositionModalMessage('Position record failed: '+friendly);
 }finally{
   $('position-submit').disabled=false;
 }
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
function approvalReasonText(reason){
 const labels={
   price_outside_envelope:'Current price is outside the locked entry zone.',
   newer_signal_exists:'A newer confirmed signal already exists; refresh and use the newest plan.',
   newer_signal_not_aligned:'The newest confirmed bar is no longer aligned with this locked plan. Do not create a new entry; if the trade is already open, record the existing position instead.',
   latest_signal_unavailable:'The latest signal context could not be verified, so approval fails closed.',
   signal_expired:'The locked plan has expired.',
   evidence_stale:'The price confirmation became stale; enter the current price again.',
   safe_mode_active:'Safe Mode is active.',
   kill_switch_active:'Kill Switch is active.',
   quality_gate_not_passed:'The required setup quality gate is no longer passed.',
   macro_high_impact_blackout:'A high-impact macro blackout is active.',
   macro_calendar_unavailable_fail_closed:'Macro calendar is unavailable, so approval fails closed.',
   existing_open_position:'An open position already exists for this symbol. Manage it instead of opening another trade.',
   same_direction_loss_cooldown:'A recent losing trade in the same symbol/direction is still inside the anti-churn cooldown. Wait for fresh confirmation.',
   risk_capacity_unavailable:'Current STC portfolio/risk capacity does not permit a new fill.',
   locked_plan_unavailable:'The locked plan is unavailable or no longer executable.',
   invalid_quote_price:'The entered price is invalid.',
   market_not_open:'The market is not open.'
 };
 return labels[reason]||String(reason).replaceAll('_',' ');
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 const feedback=$('approval-feedback-'+i);
 if(decision==='approve'&&!isOpportunityActive(c)){if(feedback)feedback.textContent='This opportunity expired. Refresh and wait for a new locked plan.';return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){if(feedback)feedback.textContent='Approval blocked by position limit or STC portfolio risk capacity.';return;}
 const price=parsePlatformPrice(c.symbol,$('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(price===null){if(feedback)feedback.textContent=priceRule(c.symbol)?"Invalid contract price. Use TradingView format such as 105'12'5 or an exact tick-aligned decimal.":'Enter a valid current TradingView price first.';return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 if(feedback)feedback.textContent='Submitting '+decision+'…';
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   if(feedback){
     const t=r.execution_ticket||null;
     if(r.decision==='approved'&&t){
       const oi=t.order_instruction||{};
       feedback.textContent='APPROVED FOR 60s • MAX QTY '+num(t.max_quantity,6)+' • '+(oi.side?oi.side+' ':'')+(oi.order_type||'ENTRY')+' • SL '+formatPlatformPrice(c.symbol,t.initial_stop)+' • FINAL TP '+formatPlatformPrice(c.symbol,t.final_take_profit)+' • DO NOT EXCEED QUANTITY.';
     }else{
       feedback.textContent='Decision: '+r.decision;
     }
   }
   await refresh();
 }catch(e){
   const reasons=e.payload&&Array.isArray(e.payload.reasons)?e.payload.reasons:[];
   const text=reasons.length?reasons.map(approvalReasonText).join(' '):e.message;
   if(feedback)feedback.textContent='Approval blocked: '+text;
 }
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications','record'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>{
 showTab(el.dataset.tab);
 if(el.dataset.tab==='general')refreshGeneralLabResearch();
});

function generalLabSymbols(){
 const raw=$('general-symbols').value||'';
 return [...new Set(raw.split(/[\n,;]+/).map(x=>x.trim().toUpperCase()).filter(Boolean))].slice(0,50);
}
function generalStatusLabel(status){
 const labels={
   WAITING_FOR_SYMBOL_RESOLUTION:'Waiting for exact TradingView symbol',
   WAITING_FOR_EXACT_HISTORY:'Waiting for exact TradingView history',
   RUNNING:'Research running',
   EVALUATED:'Research evaluated',
   FAILED:'Research failed',
   CANCELLED:'Cancelled'
 };
 return labels[status]||status||'Unknown';
}
function generalStatusClass(status){
 if(status==='EVALUATED')return 'ok';
 if(status==='FAILED'||status==='CANCELLED')return 'bad';
 return 'wait';
}
function generalResultSummary(r){
 if(!r||typeof r!=='object')return null;
 const report=r.research_report||{};
 const entry=r.live_entry_research_report||{};
 const community=r.community_ensemble_profiles||{};
 const candidates=[];
 for(const [tf,p] of Object.entries(community)){
   if(!p||!Array.isArray(p.components)||!p.components.length)continue;
   const top=p.components[0]||{};
   candidates.push({tf,component:top.component_id||'-',weight:Number(top.normalized_weight||0),status:p.status||'-'});
 }
 candidates.sort((a,b)=>b.weight-a.weight);
 return {
   nativeStatus:report.status||entry.status||'-',
   nativeStrategy:report.selected_strategy||entry.selected_strategy||'-',
   nativeTf:report.selected_timeframe||r.live_entry_timeframe||'-',
   community:candidates[0]||null,
   shadowCount:Array.isArray(r.existing_shadow_records)?r.existing_shadow_records.length:0,
   liveAuthority:r.live_authority===true
 };
}
function generalRequestCard(req){
 const status=String(req.status||'');
 const resolved=req.resolved_symbol||req.requested_symbol||'-';
 const result=generalResultSummary(req.result);
 let detail='';
 if(status==='WAITING_FOR_SYMBOL_RESOLUTION'){
   detail='An authorized exact-data worker must resolve the provider-qualified TradingView ticker first.';
 }else if(status==='WAITING_FOR_EXACT_HISTORY'){
   detail='The full STC research matrix is queued but exact-provider historical bars have not arrived yet.';
 }else if(status==='RUNNING'){
   detail='Exact history has been claimed and the native + community research matrix is being evaluated.';
 }else if(status==='EVALUATED'){
   detail='Research completed. Result remains research-only and cannot affect competition execution without a separate promotion decision.';
 }else{
   detail=req.note||'Research request is not active.';
 }
 let resultHtml='';
 if(result){
   resultHtml='<div class="row"><span>Native research</span><span class="value">'+esc(result.nativeStatus)+' • '+esc(result.nativeStrategy)+' • '+esc(result.nativeTf)+'</span></div>'
    +(result.community?'<div class="row"><span>Top community research</span><span class="value">'+esc(result.community.component)+' • '+esc(result.community.tf)+' • '+num(result.community.weight*100,1)+'%</span></div>':'')
    +'<div class="row"><span>Existing SHADOW records</span><span class="value">'+result.shadowCount+'</span></div>'
    +'<div class="row"><span>Live authority</span><span class="value '+(result.liveAuthority?'bad':'ok')+'">'+(result.liveAuthority?'UNEXPECTED TRUE':'FALSE • research only')+'</span></div>';
 }
 return '<div class="card">'
   +'<div class="statusline"><span class="badge '+(status==='EVALUATED'?'active':status==='FAILED'||status==='CANCELLED'?'expired':'blocked')+'">'+esc(generalStatusLabel(status))+'</span><span class="pill">RESEARCH ONLY</span></div>'
   +'<div class="row"><span>Requested symbol</span><span class="value">'+esc(req.requested_symbol||'-')+'</span></div>'
   +'<div class="row"><span>Resolved symbol</span><span class="value">'+esc(resolved)+'</span></div>'
   +'<div class="row"><span>Request</span><span class="value">'+esc(req.request_id||'-')+'</span></div>'
   +'<div class="row"><span>Updated</span><span class="value">'+formatLocalTime(req.updated_at_utc)+'</span></div>'
   +'<div class="small '+generalStatusClass(status)+'">'+esc(detail)+'</div>'
   +resultHtml
   +'</div>';
}
function renderGeneralResearch(requests){
 const rows=Array.isArray(requests)?requests:[];
 const counts={waiting:0,running:0,evaluated:0,failed:0};
 for(const r of rows){
   if(r.status==='RUNNING')counts.running++;
   else if(r.status==='EVALUATED')counts.evaluated++;
   else if(r.status==='FAILED'||r.status==='CANCELLED')counts.failed++;
   else counts.waiting++;
 }
 $('general-research-summary').innerHTML=
   '<div class="card"><div class="small">Queued / waiting</div><div class="big">'+counts.waiting+'</div></div>'
  +'<div class="card"><div class="small">Running</div><div class="big">'+counts.running+'</div></div>'
  +'<div class="card"><div class="small">Evaluated</div><div class="big">'+counts.evaluated+'</div></div>'
  +'<div class="card"><div class="small">Failed / cancelled</div><div class="big">'+counts.failed+'</div></div>';
 $('general-research-cards').innerHTML=rows.map(generalRequestCard).join('')||'<div class="card">No General Lab research requests yet.</div>';
}
async function refreshGeneralLabResearch(){
 if(!$('token').value.trim()){
   $('general-status').textContent='Enter the owner token first to load the durable General Lab research queue.';
   return;
 }
 try{
   const r=await api('general_lab.php?limit=100');
   renderGeneralResearch(r.requests||[]);
   $('general-status').textContent='General Lab queue loaded. Exact-provider history is mandatory; research has no live authority.';
 }catch(e){
   $('general-status').textContent='General Lab queue unavailable: '+e.message;
 }
}
async function queueGeneralLabResearch(){
 const symbols=generalLabSymbols();
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 if(!symbols.length){
   $('general-status').textContent='Saved locally. Add at least one symbol to queue STC research.';
   renderGeneralResearch([]);
   return;
 }
 if(!$('token').value.trim()){
   $('general-status').textContent='Saved locally. Enter the owner token, then press Save + queue research again.';
   return;
 }
 $('general-status').textContent='Queuing '+symbols.length+' symbol(s) for STC research…';
 let ok=0,failed=[];
 for(const symbol of symbols){
   try{
     await api('general_lab.php',{method:'POST',body:JSON.stringify({action:'REQUEST',symbol})});
     ok++;
   }catch(e){
     failed.push(symbol+': '+e.message);
   }
 }
 await refreshGeneralLabResearch();
 $('general-status').textContent='Queued/confirmed '+ok+'/'+symbols.length+' symbol(s).'
   +(failed.length?' Failed: '+failed.join(' | '):' Exact-provider history will be required before evaluation.');
}
function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=queueGeneralLabResearch;
$('refresh-general').onclick=refreshGeneralLabResearch;

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=async()=>{await refresh();if(activeTab==='general')await refreshGeneralLabResearch();};
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
+num(p.realized_pnl_usd,2)+'</span></div></div>';
}
function tradeInventoryHtml(competitionId){
 const p=snapshot&&snapshot.competition_progress?snapshot.competition_progress[competitionId]:null;
 const s=riskSummaryFor(competitionId);
 if(!p)return '';
 const openCount=Number(p.open_positions||0);
 const closedCount=Number(p.closed_positions||0);
 const known=Number(s.open_unrealized_known_positions||0);
 const unknown=Number(s.open_unrealized_unknown_positions||0);
 const openPnl=Number(s.open_unrealized_pnl_usd||0);
 const realized=Number(p.realized_pnl_usd||0);
 let openPnlText='$0.00';
 if(openCount>0){
   openPnlText=known>0
     ?'$'+num(openPnl,2)+(unknown>0?' • PARTIAL; '+unknown+' open trade(s) waiting for an STC mark':'')
     :'Unavailable • waiting for an STC market mark';
 }
 const trackedPnl=unknown===0?realized+openPnl:null;
 return '<div class="orderbox"><div class="small">TRADE INVENTORY — THIS COMPETITION</div>'
  +'<div class="row"><span>Open trades</span><span class="value">'+openCount+'</span></div>'
  +'<div class="row"><span>Completed trades</span><span class="value">'+closedCount+'</span></div>'
  +'<div class="row"><span>Open P/L estimate</span><span class="value '+(known>0?(openPnl>=0?'ok':'bad'):'')+'">'+esc(openPnlText)+'</span></div>'
  +'<div class="row"><span>Realized P/L</span><span class="value '+(realized>=0?'ok':'bad')+'">$'+num(realized,2)+'</span></div>'
  +'<div class="row"><span>Tracked P/L</span><span class="value '+(trackedPnl==null?'wait':trackedPnl>=0?'ok':'bad')+'">'+(trackedPnl==null?'Incomplete — one or more open marks unavailable':'$'+num(trackedPnl,2))+'</span></div>'
  +'<div class="small">Open P/L is an STC estimate using the latest confirmed STC bar close available for each tracked position. It is not a broker live quote and does not change official competition scoring, which uses realized P/L.</div>'
  +'</div>';
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
 return rulesHtml(competitionId)
  +progressHtml(competitionId)
  +tradeInventoryHtml(competitionId)
  +'<div class="row"><span>Owner-synced equity</span><span class="value">$'+num(account.equity_usd,2)+'</span></div>'
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
 const latest=(p.latest_signal_history||[]).slice(-1)[0]||null;
 let buttons='';
 if(m.action==='PROTECT' && m.suggested_stop)buttons='<button onclick="recordStopUpdate(\''+esc(p.position_id)+'\','+Number(m.suggested_stop)+')">After manual stop change: record</button>';
 if(m.action==='PARTIAL_TAKE_PROFIT')buttons='<div class="small wait">Partial take-profit is disabled in single-TP mode. Keep the full quantity unless another management rule says EXIT_NOW.</div>';
 if(m.action==='EXIT_NOW')buttons='<button class="danger" onclick="recordClose(\''+esc(p.position_id)+'\')">After manual close: record</button>';
 return '<div class="card">'
  +'<div class="statusline"><span class="badge active">EXECUTED • TRACKING</span><span class="pill">'+esc(p.origin==='manual_external'?'Imported manual trade':'STC plan fill')+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(p.symbol)+'</span></div>'
  +'<div class="row"><span>Position</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.quantity,6)+'</span></div>'
  +'<div class="row"><span>Opened</span><span class="value">'+formatLocalTime(p.opened_at_utc)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+formatPlatformPrice(p.symbol,p.entry_price)+'</span></div>'
  +'<div class="row"><span>Active stop</span><span class="value">'+formatPlatformPrice(p.symbol,p.current_stop)+'</span></div>'
  +'<div class="row"><span>Management checkpoint</span><span class="value">'+formatPlatformPrice(p.symbol,p.target1)+' • no partial close</span></div>'
  +'<div class="row"><span>Final take profit</span><span class="value">'+formatPlatformPrice(p.symbol,p.target2)+'</span></div>'
  +(latest?'<div class="row"><span>Latest market check — STC bar mark</span><span class="value">'+formatLocalTime(latest.time)+' • '+esc(latest.recommendation)+' '+num(latest.composite_score,2)+' @ '+formatPlatformPrice(p.symbol,latest.close)+'</span></div>':'<div class="small wait">No STC market mark is available yet for this open position.</div>')
  +'<div class="row"><span>What to do now</span><span class="value '+managementClass(m.action)+'">'+esc(m.action||'HOLD')+'</span></div>'
  +'<div class="row"><span>R multiple</span><span class="value">'+(m.r_multiple==null?'-':num(m.r_multiple,2))+'</span></div>'
  +'<div class="row"><span>Unrealized P/L estimate</span><span class="value '+(m.unrealized_pnl_usd==null?'wait':Number(m.unrealized_pnl_usd)>=0?'ok':'bad')+'">'+(m.unrealized_pnl_usd==null?'Unavailable':'$'+num(m.unrealized_pnl_usd,2))+'</span></div>'
  +'<div class="small">The mark and open P/L above use STC confirmed bar data, not a broker live quote. Use the competition platform for the exact live P/L.</div>'
  +(m.suggested_stop?'<div class="row"><span>Suggested stop</span><span class="value">'+num(m.suggested_stop)+'</span></div>':'')
  +(rotation?'<div class="small">Rotation candidate: '+esc(rotation.to_symbol)+' '+esc(rotation.to_direction)+' • only after current thesis degradation.</div>':'')
  +'<div class="small" style="margin:8px 0">'+(m.reasons||[]).map(x=>'<span class="pill">'+esc(x)+'</span>').join('')+'</div>'
  +buttons+'</div>';
}
function renderPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(positionHtml).join('')||'<div class="card">No open positions recorded in STC for this competition.</div>';
}
function closedPositionHtml(p){
 return '<div class="card">'
  +'<div class="statusline"><span class="badge">CLOSED • RECORDED</span><span class="pill">'+esc(p.origin==='manual_external'?'Imported manual trade':'STC plan fill')+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(p.symbol)+'</span></div>'
  +'<div class="row"><span>Position</span><span class="value '+(p.side==='LONG'?'long':'short')+'">'+esc(p.side)+' × '+num(p.initial_quantity,6)+'</span></div>'
  +'<div class="row"><span>Opened</span><span class="value">'+formatLocalTime(p.opened_at_utc)+'</span></div>'
  +'<div class="row"><span>Closed</span><span class="value">'+formatLocalTime(p.closed_at_utc)+'</span></div>'
  +'<div class="row"><span>Entry</span><span class="value">'+formatPlatformPrice(p.symbol,p.entry_price)+'</span></div>'
  +'<div class="row"><span>Exit</span><span class="value">'+(p.exit_price==null?'-':formatPlatformPrice(p.symbol,p.exit_price))+'</span></div>'
  +'<div class="row"><span>Realized P/L</span><span class="value '+(Number(p.realized_pnl_usd||0)>=0?'ok':'bad')+'">$'+num(p.realized_pnl_usd,2)+'</span></div>'
  +'</div>';
}
function renderClosedPositions(target,positions){
 $(target).innerHTML=(positions||[]).map(closedPositionHtml).join('')||'<div class="card">No completed trades recorded in STC for this competition yet.</div>';
}

function watchlistHtml(c){
 const direction=Number(c.composite_score||0)>0?'LONG BIAS':Number(c.composite_score||0)<0?'SHORT BIAS':'NEUTRAL';
 const failures=(c.quality_gate_failures||[]).length
   ?(c.quality_gate_failures||[]).slice(0,8)
   :(c.reasons||[]).filter(x=>String(x).startsWith('gate_block=')).slice(0,8);
 const missing=(c.reasons||[]).filter(x=>/unavailable|gate_block=.*present|gate_block=.*alignment|family_/i.test(String(x))).slice(0,10);
 return '<div class="card">'
  +'<div class="statusline"><span class="badge blocked">WATCH ONLY</span><span class="pill">'+esc(c.competition_id==='amp-futures-sep-2026'?'AMP Futures':'Capital.com Africa')+'</span></div>'
  +'<div class="row"><span>Symbol</span><span class="value">'+esc(c.symbol)+'</span></div>'
  +'<div class="row"><span>Current bias</span><span class="value '+(direction==='LONG BIAS'?'long':direction==='SHORT BIAS'?'short':'wait')+'">'+esc(direction)+' • '+num(c.composite_score,2)+'</span></div>'
  +'<div class="row"><span>Confidence</span><span class="value">'+num(Number(c.confidence||0)*100,1)+'%</span></div>'
  +(Number.isFinite(Number(c.setup_quality_score))?'<div class="row"><span>Setup quality</span><span class="value">'+Math.round(Number(c.setup_quality_score))+'/100</span></div>':'')
  +'<div class="row"><span>Latest confirmed price</span><span class="value">'+num(c.current_price,6)+'</span></div>'
  +'<div class="small wait" style="margin-top:8px">NOT ACTIONABLE — no locked plan. Do not enter from this card.</div>'
  +(failures.length?'<div class="small" style="margin-top:8px"><b>Gate blockers:</b> '+failures.map(x=>esc(String(x).replace('gate_block=',''))).join(' • ')+'</div>':'')
  +(missing.length?'<div class="small" style="margin-top:6px"><b>Missing/unaligned evidence:</b> '+missing.map(x=>esc(String(x))).join(' • ')+'</div>':'')
  +'</div>';
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
 const missingMtf=cards.filter(c=>(c.reasons||[]).some(x=>/confirmation_1h=unavailable|trend_2h=unavailable|trend_4h=unavailable|family_evidence=unavailable/i.test(String(x)))).length;
 if(missingMtf){
   $('overview-summary').innerHTML+='<div class="card"><div class="small bad">MTF LIVE CONFIRMATION</div><div class="big bad">OFFLINE</div><div class="small">'+missingMtf+'/'+cards.length+' cards are missing higher-timeframe/family evidence. A+ opportunities can remain blocked until the v1.1 MTF production feeds are activated.</div></div>';
 }
 const ranked=[...actionable].sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)));
 const all=snapshot&&snapshot.cards?snapshot.cards:[];
 $('overview-cards').innerHTML=ranked.length
   ?ranked.slice(0,8).map(c=>cardHtml(c,all.indexOf(c))).join('')
   :'<div class="card">No ACTIVE opportunity right now. Expired plans are removed automatically; WAIT signals remain visible inside each competition tab.</div>';
 const watch=[...cards]
   .filter(c=>!isOpportunityActive(c)&&c.recommendation==='WAIT'&&Math.abs(Number(c.composite_score||0))>0)
   .sort((a,b)=>Math.abs(Number(b.composite_score||0))-Math.abs(Number(a.composite_score||0)))
   .slice(0,8);
 $('watchlist-cards').innerHTML=watch.length
   ?watch.map(watchlistHtml).join('')
   :'<div class="card">No directional watchlist candidates at the moment.</div>';
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
 const closedPositions=(snapshot.portfolio&&snapshot.portfolio.closed_positions_recent)||[];
 renderOverview(cards);
 renderCards('capital-cards',cards.filter(c=>competitionOf(c)==='capital'));
 renderCards('amp-cards',cards.filter(c=>competitionOf(c)==='amp'));
 $('capital-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='capital-africa-sep-2026'),'capital-africa-sep-2026');
 $('amp-account').innerHTML=accountHtml(accounts.find(a=>a.competition_id==='amp-futures-sep-2026'),'amp-futures-sep-2026');
 renderPositions('capital-positions',positions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderPositions('amp-positions',positions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 renderClosedPositions('capital-closed-positions',closedPositions.filter(p=>p.competition_id==='capital-africa-sep-2026'));
 renderClosedPositions('amp-closed-positions',closedPositions.filter(p=>p.competition_id==='amp-futures-sep-2026'));
 maybeNotify(cards);
 maybeNotifyManagement(positions);
}

function notificationEventHtml(e){
 const cls=e.event_type==='NEW_LOCKED_PLAN'?'active':e.event_type==='POSITION_MANAGEMENT'?'blocked':'';
 return '<div class="card">'
   +'<div class="statusline"><span class="badge '+cls+'">'+esc(e.event_type||'EVENT')+'</span>'
   +(e.symbol?'<span class="pill">'+esc(e.symbol)+'</span>':'')+'</div>'
   +'<div class="row"><span>Sent</span><span class="value">'+formatLocalTime(e.created_at_utc)+'</span></div>'
   +'<div class="row"><span>Title</span><span class="value">'+esc(e.title||'-')+'</span></div>'
   +'<details class="advanced"><summary>Message body</summary><div class="advanced-body small" style="white-space:pre-wrap">'+esc(e.body_text||'')+'</div></details>'
   +'</div>';
}
function renderNotificationEvents(events){
 const recent=(events||[]).slice(0,20);
 if($('server-notify-events'))$('server-notify-events').innerHTML=recent.map(notificationEventHtml).join('')
   ||'<div class="card">No server notification events recorded yet.</div>';
}

async function refreshNotificationStatus(){
 if(!$('token').value.trim())return;
 try{
   notificationStatus=await api('notification.php');
   const cfg=notificationStatus.config||{};
   if($('telegram-notify-status'))$('telegram-notify-status').textContent=cfg.telegram_configured?'Configured':'Not configured';
   if($('email-notify-status'))$('email-notify-status').textContent=cfg.email_configured?'Configured':'Not configured';
   if($('server-notify-count'))$('server-notify-count').textContent=(notificationStatus.events||[]).length;
   renderNotificationEvents(notificationStatus.events||[]);
   if($('server-notify-note'))$('server-notify-note').textContent='Server notification audit loaded. Recent Telegram/server events are shown below.';
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

async function recordClosedTradeHistory(competitionId){
 const symbol=String(prompt('Historical symbol exactly as shown in STC / TradingView','')||'').trim();
 if(!symbol)return;
 const side=String(prompt('Historical side: LONG or SHORT','LONG')||'').trim().toUpperCase();
 if(!(side==='LONG'||side==='SHORT')){alert('Side must be LONG or SHORT.');return;}
 const qty=Number(prompt('Historical filled quantity',''));
 const entry=Number(prompt('Historical average entry price',''));
 const exit=Number(prompt('Historical average/final exit price',''));
 if(![qty,entry,exit].every(x=>Number.isFinite(x)&&x>0)){alert('Enter valid positive quantity, entry and exit prices.');return;}
 const openedText=String(prompt('Original open date/time (example 2026-09-20 14:35)','')||'').trim();
 const closedText=String(prompt('Original close date/time (example 2026-09-20 16:10)','')||'').trim();
 const opened=new Date(openedText);
 const closed=new Date(closedText);
 if(Number.isNaN(opened.getTime())||Number.isNaN(closed.getTime())||closed<opened){alert('Historical open/close times are invalid.');return;}
 const pnlText=String(prompt('Actual realized P/L in USD from the competition platform. Leave blank if unknown; STC will estimate it.','')||'').trim();
 let realized=null;
 if(pnlText!==''){
   realized=Number(pnlText);
   if(!Number.isFinite(realized)){alert('Realized P/L must be a valid number or left blank.');return;}
 }
 if(!confirm('Import this trade as ALREADY CLOSED historical competition activity? This only updates STC progress/audit and sends no order.'))return;
 const body={action:'IMPORT_CLOSED',competition_id:competitionId,symbol,side,quantity:qty,entry_price:entry,exit_price:exit,opened_at_utc:opened.toISOString(),closed_at_utc:closed.toISOString(),realized_pnl_usd:realized,note:'Owner-confirmed historical trade import'};
 try{
   await api('position.php',{method:'POST',body:JSON.stringify(body)});
   alert('Historical closed trade imported. Qualification progress and trade counts will refresh now.');
   await refresh();
 }catch(e){alert('Historical trade import failed: '+e.message);}
}

function setPositionModalMessage(message,kind='error'){
 const el=$('position-modal-message');
 if(!el)return;
 if(!message){el.className='hidden';el.textContent='';return;}
 el.className=kind==='success'?'inlinesuccess':'inlineerror';
 el.textContent=message;
}
function closePositionModal(){
 setPositionModalMessage('');
 showTab(recordReturnTab||'overview');
}
function updatePositionPricePreviews(){
 const symbol=$('pos-symbol').value.trim();
 for(const key of ['entry','stop','tp']){
   const raw=$('pos-'+key).value;
   const parsed=parsePlatformPrice(symbol,raw);
   const preview=$('pos-'+key+'-preview');
   if(!preview)continue;
   if(!raw.trim()){preview.textContent='';continue;}
   if(parsed===null){
     preview.textContent=priceRule(symbol)?"Invalid tick. Use TradingView form such as 105'12'5 or an exact tick-aligned decimal.":'Enter a valid positive price.';
     preview.className='fieldnote bad';
   }else{
     preview.textContent='Parsed: '+formatPlatformPrice(symbol,parsed);
     preview.className='fieldnote ok';
   }
 }
}
function recordExistingPosition(competitionId){
 // Compatibility/safety contract: ALREADY OPEN in the competition platform; no order will be sent.
 return openExistingPositionForm(competitionId,null);
}
function recordExistingPositionFromCard(cardIndex){
 const c=snapshot&&snapshot.cards?snapshot.cards[cardIndex]:null;
 if(!c)return;
 return openExistingPositionForm(c.competition_id,cardIndex);
}
function normalizePositionSymbolForCompetition(competitionId,symbol){
 const raw=String(symbol||'').trim().toUpperCase();
 if(!raw)return '';
 if(competitionId==='capital-africa-sep-2026'&&!raw.includes(':')){
   const allowed=new Set(['BTCUSD','ETHUSD','DOGEUSD','EURUSD','AUDUSD','USDZAR','XAUUSD','XAGUSD','SPX500','NAS100']);
   if(allowed.has(raw))return 'CAPITALCOM:'+raw;
 }
 return raw;
}
function normalizePositionTargetInputs(){
 const competitionId=$('pos-competition').value;
 const symbolInput=$('pos-symbol');
 if(symbolInput){
   symbolInput.value=normalizePositionSymbolForCompetition(competitionId,symbolInput.value);
 }
 updatePositionPricePreviews();
}

function openExistingPositionForm(competitionId,cardIndex=null){
 recordReturnTab=activeTab;
 const c=cardIndex!==null&&snapshot&&snapshot.cards?snapshot.cards[cardIndex]:null;
 const p=c&&c.locked_trade_plan?c.locked_trade_plan:null;
 $('pos-origin').value='manual_external';
 $('pos-competition').value=competitionId;
 $('pos-card-index').value=cardIndex===null?'':String(cardIndex);
 $('pos-symbol').value=c?c.symbol:'';
 $('pos-symbol').value=normalizePositionSymbolForCompetition(competitionId,$('pos-symbol').value);
 $('pos-side').value=p&&p.direction?p.direction:'LONG';
 $('pos-qty').value=c&&c.position_sizing&&c.position_sizing.proposed_quantity?c.position_sizing.proposed_quantity:'';
 $('pos-entry').value=c&&Number.isFinite(Number(c.current_price))?formatPlatformInput(c.symbol,c.current_price):'';
 $('pos-stop').value=p?formatPlatformInput(c.symbol,p.initial_stop,planTickMode(p.direction,'stop')):'';
 $('pos-tp').value=p?formatPlatformInput(c.symbol,p.target2,planTickMode(p.direction,'target')):'';
 $('pos-opened').value='';
 $('position-submit').textContent='Record open position';
 $('pos-qty-note').textContent=competitionId==='amp-futures-sep-2026'?'Enter contracts / units. Do NOT use % balance.':'Enter platform units. Do NOT use % balance.';
 setPositionModalMessage('');
 showTab('record');
 updatePositionPricePreviews();
}
function recordFilledPosition(i){
 const c=snapshot&&snapshot.cards?snapshot.cards[i]:null;
 if(!c||!c.locked_trade_plan||!c.approval||c.approval.decision!=='approved'){
   const feedback=$('approval-feedback-'+i); if(feedback)feedback.textContent='An approved locked plan is required before using the STC-plan fill workflow.';
   return;
 }
 if(!isOpportunityActive(c)){
   const feedback=$('approval-feedback-'+i); if(feedback)feedback.textContent='This locked plan expired. If the order is already open on the platform, use “Already filled on platform? Record position”.';
   return;
 }
 const p=c.locked_trade_plan;
 recordReturnTab=activeTab;
 $('pos-origin').value='stc_plan';
 $('pos-competition').value=c.competition_id;
 $('pos-card-index').value=String(i);
 $('pos-symbol').value=normalizePositionSymbolForCompetition(c.competition_id,c.symbol);
 $('pos-side').value=p.direction;
 const approvedMax=c.approval&&c.approval.execution_ticket?Number(c.approval.execution_ticket.max_quantity):NaN;
 $('pos-qty').value=Number.isFinite(approvedMax)&&approvedMax>0
   ?approvedMax
   :(c.position_sizing&&c.position_sizing.proposed_quantity?c.position_sizing.proposed_quantity:'');
 $('pos-entry').value=Number.isFinite(Number(c.current_price))?formatPlatformInput(c.symbol,c.current_price):formatPlatformInput(c.symbol,p.entry_mid);
 $('pos-stop').value=formatPlatformInput(c.symbol,p.initial_stop,planTickMode(p.direction,'stop'));
 $('pos-tp').value=formatPlatformInput(c.symbol,p.target2,planTickMode(p.direction,'target'));
 $('pos-opened').value='';
 $('position-submit').textContent='Record approved plan fill';
 $('pos-qty-note').textContent=c.competition_id==='amp-futures-sep-2026'?'Enter contracts / units. Do NOT use % balance.':'Enter platform units. Do NOT use % balance.';
 setPositionModalMessage('');
 showTab('record');
 updatePositionPricePreviews();
}
async function submitPositionModal(){
 const competitionId=$('pos-competition').value;
 const origin=$('pos-origin').value||'manual_external';
 const cardIndex=$('pos-card-index').value===''?null:Number($('pos-card-index').value);
 const symbol=normalizePositionSymbolForCompetition(competitionId,$('pos-symbol').value);
 $('pos-symbol').value=symbol;
 const side=$('pos-side').value.trim().toUpperCase();
 const qty=Number($('pos-qty').value);
 const entry=parsePlatformPrice(symbol,$('pos-entry').value);
 const stop=parsePlatformPrice(symbol,$('pos-stop').value);
 const finalTp=parsePlatformPrice(symbol,$('pos-tp').value);
 if(!(competitionId==='capital-africa-sep-2026'||competitionId==='amp-futures-sep-2026')){setPositionModalMessage('Select the competition first.');return;}
 if(!symbol){setPositionModalMessage('Symbol is required.');return;}
 if(!(side==='LONG'||side==='SHORT')){setPositionModalMessage('Side must be LONG or SHORT.');return;}
 if(!Number.isFinite(qty)||qty<=0){setPositionModalMessage('Enter the quantity actually filled.');return;}
 if(entry===null||stop===null||finalTp===null){setPositionModalMessage('One or more prices are invalid for this contract tick size. Use the TradingView quote format shown in the green preview.');return;}
 const geometryOk=side==='LONG'?(stop<entry&&finalTp>entry):(stop>entry&&finalTp<entry);
 if(!geometryOk){setPositionModalMessage('Stop / take-profit geometry does not match '+side+'.');return;}
 const openedText=$('pos-opened').value.trim();
 const openedAt=openedText?new Date(openedText):null;
 if(openedAt&&Number.isNaN(openedAt.getTime())){setPositionModalMessage('Open time is invalid.');return;}
 const openedUtc=openedAt?openedAt.toISOString():null;
 let body;
 if(origin==='stc_plan'){
   const c=cardIndex!==null&&snapshot&&snapshot.cards?snapshot.cards[cardIndex]:null;
   const p=c&&c.locked_trade_plan?c.locked_trade_plan:null;
   if(!c||!p||!c.approval||c.approval.decision!=='approved'){setPositionModalMessage('The approved STC plan is no longer available. Use the existing-manual-position workflow instead.');return;}
   const approvedTicket=c.approval.execution_ticket||null;
   const approvedMax=approvedTicket?Number(approvedTicket.max_quantity):NaN;
   if(Number.isFinite(approvedMax)&&approvedMax>0&&qty>approvedMax+Math.max(1e-9,approvedMax*1e-8)){
     setPositionModalMessage('BLOCKED: filled quantity exceeds the approved STC risk ticket. Maximum approved quantity is '+num(approvedMax,6)+'. If an oversized fill already happened on the platform, record it as an existing manual position for supervision; do not label it as an STC-compliant fill.');
     return;
   }
   body={action:'OPEN',origin:'stc_plan',competition_id:competitionId,symbol,side,quantity:qty,entry_price:entry,initial_stop:stop,current_stop:stop,target1:p.target1,target2:finalTp,source_plan_id:p.plan_id,opened_at_utc:openedUtc,note:'Owner-confirmed manual fill via inline form'};
 }else{
   const checkpoint=(entry+finalTp)/2;
   body={action:'OPEN',origin:'manual_external',competition_id:competitionId,symbol,side,quantity:qty,entry_price:entry,initial_stop:stop,current_stop:stop,target1:checkpoint,target2:finalTp,opened_at_utc:openedUtc,note:'Backfilled existing manual position via inline form; single final TP'};
 }
 $('position-submit').disabled=true;
 setPositionModalMessage('Saving position…','success');
 try{
   await api('position.php',{method:'POST',body:JSON.stringify(body)});
   setPositionModalMessage('Position recorded in STC. Portfolio Supervisor will track it now.','success');
   await refresh();
   setTimeout(()=>closePositionModal(),900);
 }catch(e){
   const raw=String(e&&e.message?e.message:e);
   const friendly=raw.includes('invalid_position_target')
     ?'Position target is not valid. Select the competition and use the supported symbol (for example CAPITALCOM:EURUSD).'
     :raw.includes('symbol_not_allowed')
       ?'That symbol is not enabled for the selected competition.'
       :raw.includes('manual_position_open_time_outside_competition_window')
         ?'The entered open time is before the configured competition start. Leave the field blank to use STC server time, or enter the real platform fill time.'
         :raw.includes('opened_at_out_of_range')
           ?'The entered open time is outside the allowed range. Leave it blank to use STC server time automatically.'
           :raw.includes('filled_quantity_exceeds_stc_risk_ticket')
             ?'BLOCKED: the filled quantity is larger than the approved STC maximum. Record an already-executed oversized trade as an existing manual position for supervision, not as an STC-compliant fill.'
             :raw.includes('stc_risk_capacity_unavailable_at_fill_record')
               ?'STC risk capacity changed or is unavailable. Do not add risk. If the platform fill already happened, use the existing-manual-position recovery workflow.'
               :raw;
   setPositionModalMessage('Position record failed: '+friendly);
 }finally{
   $('position-submit').disabled=false;
 }
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
function approvalReasonText(reason){
 const labels={
   price_outside_envelope:'Current price is outside the locked entry zone.',
   newer_signal_exists:'A newer confirmed signal already exists; refresh and use the newest plan.',
   newer_signal_not_aligned:'The newest confirmed bar is no longer aligned with this locked plan. Do not create a new entry; if the trade is already open, record the existing position instead.',
   latest_signal_unavailable:'The latest signal context could not be verified, so approval fails closed.',
   signal_expired:'The locked plan has expired.',
   evidence_stale:'The price confirmation became stale; enter the current price again.',
   safe_mode_active:'Safe Mode is active.',
   kill_switch_active:'Kill Switch is active.',
   quality_gate_not_passed:'The required setup quality gate is no longer passed.',
   macro_high_impact_blackout:'A high-impact macro blackout is active.',
   macro_calendar_unavailable_fail_closed:'Macro calendar is unavailable, so approval fails closed.',
   existing_open_position:'An open position already exists for this symbol. Manage it instead of opening another trade.',
   same_direction_loss_cooldown:'A recent losing trade in the same symbol/direction is still inside the anti-churn cooldown. Wait for fresh confirmation.',
   risk_capacity_unavailable:'Current STC portfolio/risk capacity does not permit a new fill.',
   locked_plan_unavailable:'The locked plan is unavailable or no longer executable.',
   invalid_quote_price:'The entered price is invalid.',
   market_not_open:'The market is not open.'
 };
 return labels[reason]||String(reason).replaceAll('_',' ');
}
async function approveCard(i,decision){
 const c=snapshot.cards[i];
 if(!c)return;
 const feedback=$('approval-feedback-'+i);
 if(decision==='approve'&&!isOpportunityActive(c)){if(feedback)feedback.textContent='This opportunity expired. Refresh and wait for a new locked plan.';return;}
 if(decision==='approve' && c.position_sizing && (c.position_sizing.allowed_by_position_limit===false || c.position_sizing.allowed_by_risk_policy===false)){if(feedback)feedback.textContent='Approval blocked by position limit or STC portfolio risk capacity.';return;}
 const price=parsePlatformPrice(c.symbol,$('price-'+i)?.value);
 const body={signal_id:c.signal_id,decision,note:'STC owner console'};
 if(decision==='approve'){
   if(price===null){if(feedback)feedback.textContent=priceRule(c.symbol)?"Invalid contract price. Use TradingView format such as 105'12'5 or an exact tick-aligned decimal.":'Enter a valid current TradingView price first.';return;}
   body.confirmation={observed_at_utc:new Date().toISOString(),quote_price:price,market_status:'open'};
 }
 if(feedback)feedback.textContent='Submitting '+decision+'…';
 try{
   const r=await api('approval.php',{method:'POST',body:JSON.stringify(body)});
   if(feedback){
     const t=r.execution_ticket||null;
     if(r.decision==='approved'&&t){
       const oi=t.order_instruction||{};
       feedback.textContent='APPROVED FOR 60s • MAX QTY '+num(t.max_quantity,6)+' • '+(oi.side?oi.side+' ':'')+(oi.order_type||'ENTRY')+' • SL '+formatPlatformPrice(c.symbol,t.initial_stop)+' • FINAL TP '+formatPlatformPrice(c.symbol,t.final_take_profit)+' • DO NOT EXCEED QUANTITY.';
     }else{
       feedback.textContent='Decision: '+r.decision;
     }
   }
   await refresh();
 }catch(e){
   const reasons=e.payload&&Array.isArray(e.payload.reasons)?e.payload.reasons:[];
   const text=reasons.length?reasons.map(approvalReasonText).join(' '):e.message;
   if(feedback)feedback.textContent='Approval blocked: '+text;
 }
}

function showTab(name){
 activeTab=name;
 for(const el of document.querySelectorAll('.tab'))el.classList.toggle('active',el.dataset.tab===name);
 for(const id of ['overview','capital','amp','general','notifications','record'])$(id+'-panel').classList.toggle('hidden',id!==name);
 localStorage.setItem('stc_active_tab',name);
}
for(const el of document.querySelectorAll('.tab'))el.addEventListener('click',()=>{
 showTab(el.dataset.tab);
 if(el.dataset.tab==='general')refreshGeneralLabResearch();
});

function generalLabSymbols(){
 const raw=$('general-symbols').value||'';
 return [...new Set(raw.split(/[\n,;]+/).map(x=>x.trim().toUpperCase()).filter(Boolean))].slice(0,50);
}
function generalStatusLabel(status){
 const labels={
   WAITING_FOR_SYMBOL_RESOLUTION:'Waiting for exact TradingView symbol',
   WAITING_FOR_EXACT_HISTORY:'Waiting for exact TradingView history',
   RUNNING:'Research running',
   EVALUATED:'Research evaluated',
   FAILED:'Research failed',
   CANCELLED:'Cancelled'
 };
 return labels[status]||status||'Unknown';
}
function generalStatusClass(status){
 if(status==='EVALUATED')return 'ok';
 if(status==='FAILED'||status==='CANCELLED')return 'bad';
 return 'wait';
}
function generalResultSummary(r){
 if(!r||typeof r!=='object')return null;
 const report=r.research_report||{};
 const entry=r.live_entry_research_report||{};
 const community=r.community_ensemble_profiles||{};
 const candidates=[];
 for(const [tf,p] of Object.entries(community)){
   if(!p||!Array.isArray(p.components)||!p.components.length)continue;
   const top=p.components[0]||{};
   candidates.push({tf,component:top.component_id||'-',weight:Number(top.normalized_weight||0),status:p.status||'-'});
 }
 candidates.sort((a,b)=>b.weight-a.weight);
 return {
   nativeStatus:report.status||entry.status||'-',
   nativeStrategy:report.selected_strategy||entry.selected_strategy||'-',
   nativeTf:report.selected_timeframe||r.live_entry_timeframe||'-',
   community:candidates[0]||null,
   shadowCount:Array.isArray(r.existing_shadow_records)?r.existing_shadow_records.length:0,
   liveAuthority:r.live_authority===true
 };
}
function generalRequestCard(req){
 const status=String(req.status||'');
 const resolved=req.resolved_symbol||req.requested_symbol||'-';
 const result=generalResultSummary(req.result);
 let detail='';
 if(status==='WAITING_FOR_SYMBOL_RESOLUTION'){
   detail='An authorized exact-data worker must resolve the provider-qualified TradingView ticker first.';
 }else if(status==='WAITING_FOR_EXACT_HISTORY'){
   detail='The full STC research matrix is queued but exact-provider historical bars have not arrived yet.';
 }else if(status==='RUNNING'){
   detail='Exact history has been claimed and the native + community research matrix is being evaluated.';
 }else if(status==='EVALUATED'){
   detail='Research completed. Result remains research-only and cannot affect competition execution without a separate promotion decision.';
 }else{
   detail=req.note||'Research request is not active.';
 }
 let resultHtml='';
 if(result){
   resultHtml='<div class="row"><span>Native research</span><span class="value">'+esc(result.nativeStatus)+' • '+esc(result.nativeStrategy)+' • '+esc(result.nativeTf)+'</span></div>'
    +(result.community?'<div class="row"><span>Top community research</span><span class="value">'+esc(result.community.component)+' • '+esc(result.community.tf)+' • '+num(result.community.weight*100,1)+'%</span></div>':'')
    +'<div class="row"><span>Existing SHADOW records</span><span class="value">'+result.shadowCount+'</span></div>'
    +'<div class="row"><span>Live authority</span><span class="value '+(result.liveAuthority?'bad':'ok')+'">'+(result.liveAuthority?'UNEXPECTED TRUE':'FALSE • research only')+'</span></div>';
 }
 return '<div class="card">'
   +'<div class="statusline"><span class="badge '+(status==='EVALUATED'?'active':status==='FAILED'||status==='CANCELLED'?'expired':'blocked')+'">'+esc(generalStatusLabel(status))+'</span><span class="pill">RESEARCH ONLY</span></div>'
   +'<div class="row"><span>Requested symbol</span><span class="value">'+esc(req.requested_symbol||'-')+'</span></div>'
   +'<div class="row"><span>Resolved symbol</span><span class="value">'+esc(resolved)+'</span></div>'
   +'<div class="row"><span>Request</span><span class="value">'+esc(req.request_id||'-')+'</span></div>'
   +'<div class="row"><span>Updated</span><span class="value">'+formatLocalTime(req.updated_at_utc)+'</span></div>'
   +'<div class="small '+generalStatusClass(status)+'">'+esc(detail)+'</div>'
   +resultHtml
   +'</div>';
}
function renderGeneralResearch(requests){
 const rows=Array.isArray(requests)?requests:[];
 const counts={waiting:0,running:0,evaluated:0,failed:0};
 for(const r of rows){
   if(r.status==='RUNNING')counts.running++;
   else if(r.status==='EVALUATED')counts.evaluated++;
   else if(r.status==='FAILED'||r.status==='CANCELLED')counts.failed++;
   else counts.waiting++;
 }
 $('general-research-summary').innerHTML=
   '<div class="card"><div class="small">Queued / waiting</div><div class="big">'+counts.waiting+'</div></div>'
  +'<div class="card"><div class="small">Running</div><div class="big">'+counts.running+'</div></div>'
  +'<div class="card"><div class="small">Evaluated</div><div class="big">'+counts.evaluated+'</div></div>'
  +'<div class="card"><div class="small">Failed / cancelled</div><div class="big">'+counts.failed+'</div></div>';
 $('general-research-cards').innerHTML=rows.map(generalRequestCard).join('')||'<div class="card">No General Lab research requests yet.</div>';
}
async function refreshGeneralLabResearch(){
 if(!$('token').value.trim()){
   $('general-status').textContent='Enter the owner token first to load the durable General Lab research queue.';
   return;
 }
 try{
   const r=await api('general_lab.php?limit=100');
   renderGeneralResearch(r.requests||[]);
   $('general-status').textContent='General Lab queue loaded. Exact-provider history is mandatory; research has no live authority.';
 }catch(e){
   $('general-status').textContent='General Lab queue unavailable: '+e.message;
 }
}
async function queueGeneralLabResearch(){
 const symbols=generalLabSymbols();
 const g={capital:$('general-capital').value,currency:$('general-currency').value,symbols:$('general-symbols').value};
 localStorage.setItem('stc_general_lab',JSON.stringify(g));
 if(!symbols.length){
   $('general-status').textContent='Saved locally. Add at least one symbol to queue STC research.';
   renderGeneralResearch([]);
   return;
 }
 if(!$('token').value.trim()){
   $('general-status').textContent='Saved locally. Enter the owner token, then press Save + queue research again.';
   return;
 }
 $('general-status').textContent='Queuing '+symbols.length+' symbol(s) for STC research…';
 let ok=0,failed=[];
 for(const symbol of symbols){
   try{
     await api('general_lab.php',{method:'POST',body:JSON.stringify({action:'REQUEST',symbol})});
     ok++;
   }catch(e){
     failed.push(symbol+': '+e.message);
   }
 }
 await refreshGeneralLabResearch();
 $('general-status').textContent='Queued/confirmed '+ok+'/'+symbols.length+' symbol(s).'
   +(failed.length?' Failed: '+failed.join(' | '):' Exact-provider history will be required before evaluation.');
}
function loadGeneralSettings(){
 try{
   const g=JSON.parse(localStorage.getItem('stc_general_lab')||'{}');
   $('general-capital').value=g.capital??'';
   $('general-currency').value=g.currency||'USD';
   $('general-symbols').value=g.symbols||'';
 }catch(e){}
}
$('save-general').onclick=queueGeneralLabResearch;
$('refresh-general').onclick=refreshGeneralLabResearch;

loadGeneralSettings();
showTab(localStorage.getItem('stc_active_tab')||'overview');
if('Notification' in window && $('browser-notify-status'))$('browser-notify-status').textContent=Notification.permission==='granted'?'Enabled':'Not enabled';

$('refresh').onclick=async()=>{await refresh();if(activeTab==='general')await refreshGeneralLabResearch();};
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
