"""Causal, long-only Crypto Spot research and fail-closed manual Paper decision gate.

No exchange/TradingView API order code, secrets, notifier, or production side effects.
All values are historical hypotheses until external Paper fills are verified.
"""
from __future__ import annotations

import bisect
import gzip
import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PERIOD_MS={"15m":900000,"1h":3600000,"4h":14400000,"1d":86400000}
FAMILIES=("MTF_TREND_PULLBACK","MTF_BOUNDED_BREAKOUT","MTF_RANGE_RECOVERY")
COST_BPS=(5,15,30)
BAR_ENTRY="NEXT_CLOSED_SIGNAL_BAR_OPEN"
STOP_ATR=1.8
MAX_HOLD=48
WARMUP_15M=240
RESEARCH_SPLIT=0.60
EMBARGO_BARS=48

@dataclass(frozen=True)
class Bar:
    open_ms:int
    close_ms:int
    o:float
    h:float
    l:float
    c:float
    v:float

def bars_from_binance(rows:list[list[Any]],interval:str)->list[Bar]:
    step=PERIOD_MS[interval]
    out=[]
    prev=None
    for row in rows:
        if not isinstance(row,list) or len(row)<7:raise ValueError("RAW_KLINE_SCHEMA_INVALID")
        t=int(row[0]);close=int(row[6]);values=[float(row[x]) for x in (1,2,3,4,5)]
        if t%step or close!=t+step-1:raise ValueError("INVALID_KLINE_PERIOD")
        if prev is not None and (t<=prev or t-prev!=step):
            raise ValueError("GAPPED_OR_DUPLICATED_SPOT_BARS")
        if not all(math.isfinite(x) for x in values):
            raise ValueError("NONFINITE_BARS")
        o,h,l,c,v=values
        if min(o,h,l,c)<=0 or v<0 or h<max(o,c) or l>min(o,c) or h<l:
            raise ValueError("BAD_OHLCV")
        out.append(Bar(t,close,o,h,l,c,v))
        prev=t
    return out

def load_verified_symbol(manifest_path:str|Path,pair:str)->dict[str,list[Bar]]:
    path=Path(manifest_path)
    meta=json.loads(path.read_text(encoding="utf-8"))
    if meta.get("execution")!="NONE" or meta.get("real_money_authorized") is not False:
        raise ValueError("RESEARCH_MANIFEST_POLICY_VIOLATION")
    found=[x for x in meta["pairs"] if x["pair"]==pair]
    if len(found)!=1 or found[0].get("data_gate")!="HISTORY_QUALITY_PASS":
        raise ValueError("SPOT_DATA_NOT_QUALIFIED")
    record=found[0]
    result={}
    for item in record["series"]:
        name=item["interval"]
        if name not in PERIOD_MS or item["closed_bars"]<900 or not item.get("data_valid"):
            raise ValueError("TIMEFRAME_RESEARCH_NOT_QUALIFIED")
        payload=(path.parent/item["filename"]).read_bytes()
        if hashlib.sha256(payload).hexdigest()!=item["sha256"]:
            raise ValueError("MARKET_DATA_HASH_MISMATCH")
        body=json.loads(gzip.decompress(payload))
        if body.get("source")!="BINANCE_SPOT_PUBLIC" or body.get("pair")!=pair or body.get("interval")!=name:
            raise ValueError("WRONG_MARKET_SOURCE")
        series=bars_from_binance(body["rows"],name)
        if len(series)!=item["closed_bars"]:
            raise ValueError("MARKET_DATA_COUNT_MISMATCH")
        result[name]=series
    if set(result)!=set(PERIOD_MS):
        raise ValueError("MISSING_QUALIFIED_TIMEFRAMES")
    return result

def indicators(bars:list[Bar])->dict[str,list[float|None]]:
    n=len(bars)
    c=[b.c for b in bars]
    obj={key:[None]*n for key in ("ema20","ema50","ema200","atr","adx","rsi","bblo","bbhi")}
    if not n:return obj
    for name,length in (("ema20",20),("ema50",50),("ema200",200)):
        obj[name][0]=c[0]
        alpha=2./(length+1)
        for i in range(1,n):
            obj[name][i]=obj[name][i-1]+alpha*(c[i]-obj[name][i-1])
    if n<=29:return obj
    trs=[bars[0].h-bars[0].l]
    pds=[0.];mds=[0.];gains=[0.];losses=[0.]
    for i in range(1,n):
        now,prior=bars[i],bars[i-1]
        trs.append(max(now.h-now.l,abs(now.h-prior.c),abs(now.l-prior.c)))
        up=now.h-prior.h;down=prior.l-now.l
        pds.append(up if up>down and up>0 else 0.)
        mds.append(down if down>up and down>0 else 0.)
        dif=now.c-prior.c
        gains.append(max(0,dif));losses.append(max(0,-dif))
    obj["atr"][13]=sum(trs[:14])/14
    for i in range(14,n):
        obj["atr"][i]=(obj["atr"][i-1]*13+trs[i])/14
    trs_sm=sum(trs[1:15]);p_sm=sum(pds[1:15]);m_sm=sum(mds[1:15])
    avg_g=sum(gains[1:15])/14;avg_l=sum(losses[1:15])/14
    dx=[None]*n
    for i in range(14,n):
        if i>14:
            trs_sm=trs_sm-trs_sm/14+trs[i]
            p_sm=p_sm-p_sm/14+pds[i]
            m_sm=m_sm-m_sm/14+mds[i]
            avg_g=(avg_g*13+gains[i])/14
            avg_l=(avg_l*13+losses[i])/14
        rsi=100 if avg_l==0 else 100-100/(1+avg_g/avg_l)
        obj["rsi"][i]=rsi
        plus=100*p_sm/trs_sm if trs_sm>0 else 0
        minus=100*m_sm/trs_sm if trs_sm>0 else 0
        dx[i]=100*abs(plus-minus)/(plus+minus) if plus+minus else 0
        if i==27:obj["adx"][i]=sum(dx[14:28])/14
        elif i>27:obj["adx"][i]=(obj["adx"][i-1]*13+dx[i])/14
    for i in range(19,n):
        x=c[i-19:i+1];mean=sum(x)/20
        sd=math.sqrt(sum((a-mean)**2 for a in x)/20)
        obj["bblo"][i]=mean-2*sd;obj["bbhi"][i]=mean+2*sd
    return obj

def closed_asof_index(bars:list[Bar],utc_ms:int)->int:
    """Return last strictly completed higher-timeframe bar at a 15m signal close."""
    return bisect.bisect_right(bars, utc_ms, key=lambda b: b.close_ms)-1

def signal_family(
    family:str,bars:dict[str,list[Bar]],f:dict[str,dict[str,list]],
    i:int
)->bool:
    if family not in FAMILIES:raise ValueError("UNREGISTERED_STRATEGY")
    s=bars["15m"]
    if i<max(WARMUP_15M,21) or i>=len(s):return False
    indexes={x:closed_asof_index(bars[x],s[i].close_ms) for x in ("1d","4h","1h")}
    if indexes["1d"]<210 or indexes["4h"]<60 or indexes["1h"]<60:
        return False
    # As-of alone may silently substitute days-old missing hourly/daily bars.
    # SPOT trades 24/7. Missing most-recent completed HTF candle => fail closed.
    for frame,last_index in indexes.items():
        elapsed_ms=s[i].close_ms-bars[frame][last_index].close_ms
        if elapsed_ms<0 or elapsed_ms>=PERIOD_MS[frame]:
            return False
    d=bars["1d"][indexes["1d"]]
    fd=f["1d"];i_d=indexes["1d"]
    fh=f["4h"];i4=indexes["4h"];four=bars["4h"][i4]
    f1=f["1h"];i1=indexes["1h"];hour=bars["1h"][i1]
    fs=f["15m"];now=s[i];prior=s[i-1]
    atr=fs["atr"][i]
    adx_hour=f1["adx"][i1]
    if atr is None or atr<=0 or adx_hour is None:
        return False
    bullish_day=d.c>fd["ema200"][i_d]
    bullish_4h=four.c>fh["ema50"][i4]
    volume_median=statistics.median(x.v for x in s[i-20:i])
    if volume_median<=0:return False
    if family=="MTF_TREND_PULLBACK":
        return bool(
            bullish_day and fd["ema50"][i_d]>fd["ema200"][i_d] and
            bullish_4h and fh["ema20"][i4]>fh["ema50"][i4] and
            hour.c>f1["ema50"][i1] and adx_hour>=18 and
            now.l<=fs["ema20"][i] and fs["ema20"][i]<now.c<=fs["ema20"][i]+0.8*atr and
            now.c>now.o and now.v>volume_median
        )
    if family=="MTF_BOUNDED_BREAKOUT":
        highest=max(x.h for x in s[i-20:i])
        prev_high=max(x.h for x in s[i-21:i-1])
        return bool(
            bullish_day and fd["ema50"][i_d]>fd["ema200"][i_d] and
            bullish_4h and fh["ema20"][i4]>fh["ema50"][i4] and
            hour.c>f1["ema20"][i1] and adx_hour>=18 and
            now.c>highest and prior.c<=prev_high and
            now.v>=1.2*volume_median and
            now.c<=fs["ema20"][i]+1.5*atr
        )
    return bool(
       bullish_day and bullish_4h and adx_hour<=18 and now.c>now.o and
       fs["bblo"][i-1] is not None and
       prior.c<fs["bblo"][i-1] and now.c>fs["bblo"][i] and
       fs["rsi"][i] is not None and fs["rsi"][i]<48 and
       now.v>volume_median
    )

def simulate_exit(s:list[Bar], entry_i:int,hi:int,stop:float,target:float)->dict:
    if not 0<=entry_i<hi<=len(s):raise ValueError("INVALID_WINDOW")
    until=min(entry_i+MAX_HOLD,hi)
    for j in range(entry_i,until):
        bar=s[j]
        if j>entry_i and bar.open_ms-s[j-1].open_ms!=PERIOD_MS["15m"]:
            return {"exit_index":j,"exit_price":None,"reason":"UNOBSERVED_GAP"}
        if bar.l<=stop:
            return {"exit_index":j,"exit_price":min(bar.o,stop),"reason":"STOP"}
        if bar.h>=target:
            return {"exit_index":j,"exit_price":target,"reason":"TARGET"}
    if until<entry_i+MAX_HOLD:
        return {"exit_index":until-1,"exit_price":None,"reason":"INCOMPLETE_FORWARD_WINDOW"}
    return {"exit_index":until-1,"exit_price":s[until-1].c,"reason":"TIME_STOP"}

def backtest_family(bars:dict[str,list[Bar]],family:str,lo:int,hi:int)->list[dict]:
    f={interval:indicators(rows) for interval,rows in bars.items()}
    s=bars["15m"]
    rows=[];i=max(lo,WARMUP_15M)
    while i<hi-1:
        if not signal_family(family,bars,f,i):
            i+=1;continue
        entry_i=i+1
        # Continuity is checked when simulating the hypothetical next-open fill,
        # NOT by peeking at the bar from inside the signal-time predicate.
        if s[entry_i].open_ms-s[i].open_ms!=PERIOD_MS["15m"]:
            i+=1
            continue
        entry=s[entry_i].o
        risk=STOP_ATR*f["15m"]["atr"][i]
        stop=entry-risk
        target=entry+(1.5 if family=="MTF_RANGE_RECOVERY" else 2)*risk
        if risk<=0 or stop<=0 or entry<=0:
            i+=1;continue
        exit=simulate_exit(s,entry_i,hi,stop,target)
        j=exit["exit_index"]
        row={"family":family,"signal_ms":s[i].close_ms,"entry_ms":s[entry_i].open_ms,
             "exit_ms":s[j].close_ms,"signal_i":i,"entry_i":entry_i,"exit_i":j,
             "direction":"LONG","hypothetical_only":True,
             "entry":entry,"stop":stop,"target":target,"risk_price":risk,
             "reason":exit["reason"],"exit":exit["exit_price"],
             "cost_net_R":{}}
        if exit["exit_price"] is not None:
            gross=(exit["exit_price"]-entry)/risk
            row["gross_R"]=round(gross,8)
            for bps in COST_BPS:
                modeled_cost=(bps/10000)*(entry+exit["exit_price"])/risk
                row["cost_net_R"][str(bps)]=round(gross-modeled_cost,8)
        else:
            row["gross_R"]=None
            row["cost_net_R"]={str(x):None for x in COST_BPS}
        if row["entry_ms"]<=row["signal_ms"]:
            raise RuntimeError("CAUSALITY_VIOLATION")
        rows.append(row)
        i=j+1
    return rows

def paper_manual_intent(
    *,pair:str,entry:float,stop:float,now_ms:int,signal_ms:int,
    quote_observed_ms:int|None,quote_from_exact_verified_venue:bool,
    strategy_review_state:str,equity_usdt:float|None=None,
    spot_step_size:float|None=None,minimum_notional:float|None=None,
    owner_ack:bool=False,actual_quote_price:float|None=None,
    verified_available_cash_usdt:float|None=None,
    verified_existing_open_stop_risk_usdt:float|None=None,
    paper_account_identity_verified:bool=False,
)->dict[str,Any]:
    """Return hypothetical sizing for independent OWNER MANUAL Paper checks ONLY.

    No order API integration is present. This function must never silently
    treat an STC-generated plan as actual broker entry, fill or protective stop.
    """
    base={"pair":pair,"mode":"SPOT_ONLY","side":"LONG_ONLY",
          "broker_order_sent":False,"paper_order_sent":False,
          "automatic_execution":False,"no_email":True}
    # A caller-chosen text pair can never authorize new symbols outside owner registry.
    # This is still a PURE paper preview, not an authenticated order approval.
    from app.crypto_spot_registry import load_crypto_spot_registry
    try:
        registered=load_crypto_spot_registry().by_pair(pair)
    except (KeyError,ValueError,OSError):
        return {**base,"decision":"HOLD","reason":"UNREGISTERED_OWNER_SPOT_PAIR"}
    if registered.pair!=pair:
        return {**base,"decision":"HOLD","reason":"UNREGISTERED_OWNER_SPOT_PAIR"}
    if strategy_review_state!="APPROVED_FOR_MANUAL_PAPER":
        return {**base,"decision":"HOLD","reason":"STRATEGY_NOT_PROMOTED"}
    if not paper_account_identity_verified:
        return {**base,"decision":"HOLD","reason":"PAPER_ACCOUNT_UNVERIFIED"}
    if not quote_from_exact_verified_venue or quote_observed_ms is None or not 0<=now_ms-quote_observed_ms<=60_000:
        return {**base,"decision":"HOLD","reason":"VERIFIED_FRESH_QUOTE_REQUIRED"}
    if not isinstance(signal_ms,int) or now_ms<signal_ms or now_ms-signal_ms>300_000:
        return {**base,"decision":"HOLD","reason":"SIGNAL_EXPIRED_REQUIRE_NEW_PLAN"}
    if not owner_ack:
        return {**base,"decision":"HOLD","reason":"OWNER_MANUAL_ACK_REQUIRED"}
    numeric=(entry,stop,actual_quote_price,equity_usdt,
             verified_available_cash_usdt,verified_existing_open_stop_risk_usdt,
             spot_step_size,minimum_notional)
    if any(x is None or not isinstance(x,(float,int)) or not math.isfinite(x) for x in numeric):
        return {**base,"decision":"HOLD","reason":"MISSING_VERIFIED_QUOTE_ACCOUNT_OR_MARKET_RULE"}
    quote=float(actual_quote_price)
    if (entry<=0 or quote<=0 or equity_usdt<=0 or
        verified_available_cash_usdt<=0 or
        verified_existing_open_stop_risk_usdt<0 or
        spot_step_size<=0 or minimum_notional<=0 or not 0<stop<min(entry,quote)):
        return {**base,"decision":"HOLD","reason":"INVALID_ACCOUNT_STOP_OR_VENUE"}
    if abs(quote-entry)/entry>0.002:
        return {**base,"decision":"HOLD","reason":"PRICE_CHANGED_REVALIDATE_NO_CHASE"}
    remaining_risk=0.02*equity_usdt-verified_existing_open_stop_risk_usdt
    if remaining_risk<=0:
        return {**base,"decision":"HOLD","reason":"PORTFOLIO_RISK_CAP_REACHED"}
    single_trade_stop_risk=min(0.005*equity_usdt,remaining_risk)
    # Conservative modeled 30 bps EACH side, in addition to price-to-stop risk.
    # Even this cannot bound slippage past SL / gaps; no guaranteed stop execution.
    fee_bps_per_side=max(COST_BPS)
    modeled_roundtrip_cost_per_unit=(fee_bps_per_side/10_000)*(quote+stop)
    stop_risk_per_unit=(quote-stop)+modeled_roundtrip_cost_per_unit
    cap=min(0.05*equity_usdt/quote,
            verified_available_cash_usdt/quote,
            single_trade_stop_risk/stop_risk_per_unit)
    steps=math.floor((cap+1e-15)/spot_step_size)
    qty=steps*spot_step_size
    if qty<=0 or qty*quote<minimum_notional:
        return {**base,"decision":"HOLD","reason":"BELOW_VENUE_MIN_NOTIONAL"}
    # Budget check after venue step-size rounding; never round risk upward.
    if (qty*stop_risk_per_unit>single_trade_stop_risk+1e-9
        or verified_existing_open_stop_risk_usdt+qty*stop_risk_per_unit>0.02*equity_usdt+1e-9):
        return {**base,"decision":"HOLD","reason":"FEE_INCLUSIVE_RISK_BUDGET_EXCEEDED"}
    return {**base,"decision":"OWNER_MANUAL_PAPER_RECHECK_ONLY",
            "hypothetical_max_quantity":qty,
            "quoted_reference_price":quote,
            "estimated_max_stop_risk_usdt":qty*stop_risk_per_unit,
            "stop_price_only_risk_usdt":qty*(quote-stop),
            "modeled_friction_bps_per_side":fee_bps_per_side,
            "modeled_roundtrip_cost_buffer_usdt":qty*modeled_roundtrip_cost_per_unit,
            "fee_inclusive_verified_open_stop_risk_required":True,
            "max_notional_usdt":qty*quote,
            "expires_at_ms":signal_ms+300_000,
            "stop_reference":stop,
            "note":"Only a hypothetical OWNER manual Paper preview. Fills, fee tier, gaps, account identity and protection must be verified externally; NOT A GUARANTEED LOSS CAP. NO ORDER SENT."}

def summary(trades:list[dict],bps:int)->dict:
    amounts=[r["cost_net_R"][str(bps)] for r in trades if r["cost_net_R"][str(bps)] is not None]
    censored=len(trades)-len(amounts)
    if not amounts:
        return {"trades":0,"censored":censored,"mean_R":None,"net_R_sum":0.,"profit_factor":None,
                "max_drawdown_R":0.,"positive_mean":False}
    equity=peak=maxdd=0.;grosswin=grossloss=0.
    for x in amounts:
        equity+=x
        peak=max(peak,equity)
        maxdd=max(maxdd,peak-equity)
        if x>0:grosswin+=x
        else:grossloss-=x
    return {"trades":len(amounts),"censored":censored,
            "mean_R":round(statistics.mean(amounts),7),
            "net_R_sum":round(sum(amounts),6),
            "profit_factor":round(grosswin/grossloss,5) if grossloss else None,
            "max_drawdown_R":round(maxdd,6),
            "positive_mean":statistics.mean(amounts)>0}

def run_fixed_screen(manifest_path:Path)->tuple[dict,list[dict]]:
    meta=json.loads(manifest_path.read_text(encoding="utf-8"))
    results=[];ledger=[]
    if meta["pair_count"]!=16 or meta["execution"]!="NONE":raise ValueError("BAD_RESEARCH_SCOPE")
    for asset in meta["pairs"]:
        pair=asset["pair"]
        if asset["data_gate"]!="HISTORY_QUALITY_PASS":
            results.append({"pair":pair,"status":"DATA_BLOCKED_NO_SIGNAL","reason":asset["data_gate"]})
            continue
        bars=load_verified_symbol(manifest_path,pair)
        n=len(bars["15m"]);pivot=int(RESEARCH_SPLIT*n)
        for segment,lo,hi in (("TRAIN",0,pivot),("HISTORICAL_RESEARCH_HOLDOUT",pivot+EMBARGO_BARS,n)):
            for family in FAMILIES:
                t=backtest_family(bars,family,lo,hi)
                for x in t:
                    ledger.append({"pair":pair,"segment":segment,**x})
                for bps in COST_BPS:
                    results.append({"pair":pair,"segment":segment,"family":family,
                                    "side":"LONG","assumed_friction_bps_per_side":bps,
                                    "no_live_order_authorization":True,
                                    **summary(t,bps)})
    info={
      "status":"RESEARCH_ONLY_UNPROMOTED",
      "source_manifest_sha256":hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
      "symbols_registered":16,
      "symbols_historical_qa_pass":sum(x["data_gate"]=="HISTORY_QUALITY_PASS" for x in meta["pairs"]),
      "blocked_symbols":[x["pair"] for x in meta["pairs"] if x["data_gate"]!="HISTORY_QUALITY_PASS"],
      "assumed_friction_bps_per_side":COST_BPS,
      "train_fraction":RESEARCH_SPLIT,"embargo_15m_bars":EMBARGO_BARS,
      "result_rows":results,
      "no_strategy_promoted":True,"execution":"NONE",
      "no_paper_account_fills_verified":True,
      "no_real_money_or_automated_orders":True,
      "historical_research_only":True,
      "notes":[
        "Previous observed bars and retrospectively split holdout are NOT genuinely new prospective forward evidence.",
        "No selected symbols/families can be promoted without clean prospective and actual owner Paper fill tests.",
        "No trade-specific 5/10/15-minute delay execution paths are simulated using this 15m-only entry model.",
        "Correlated family-level simulated R sums are not an executable portfolio equity curve.",
      ]
    }
    return info,ledger
