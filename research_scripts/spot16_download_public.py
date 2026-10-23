"""Read-only public Binance Spot OHLCV for owner-approved 16 pairs; no orders."""
from __future__ import annotations
import gzip, hashlib, json, math, time, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
STC=Path(__file__).resolve().parents[3]
REPO=Path(__file__).resolve().parents[1]
PROTOCOL=STC/"Work"/"STC_CRYPTO_SPOT16_RESEARCH_PROTOCOL_V2_20261015.md"
REGISTRY=REPO/"research_inputs"/"CRYPTO_SPOT_ASSET_REGISTRY.json"
OUT=STC/"Verification"/"Spot16_Binance_20261015"
HOST="https://api.binance.com"
PERIOD={"15m":900000,"1h":3600000,"4h":14400000,"1d":86400000}
COUNTS={"15m":4000,"1h":1000,"4h":1000,"1d":1000}
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(path,params):
    assert path in ("/api/v3/exchangeInfo","/api/v3/klines")
    url=HOST+path+"?"+urllib.parse.urlencode(params)
    for n in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"STC-Spot-Public-History-QA/2"})
            with urllib.request.urlopen(req,timeout=18) as stream:
                raw=stream.read(1_700_000)
                if len(raw)>=1_700_000:raise ValueError("RESPONSE_TOO_LARGE")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code not in (429,500,502,503,504) or n==2:raise
            time.sleep(1.0+n*2)
        except (urllib.error.URLError,TimeoutError):
            if n==2:raise
            time.sleep(1+n)
    raise RuntimeError("RATE_RETRIES_EXHAUSTED")
def validate(symbol,interval,rows,cutoff):
    period=PERIOD[interval];old=None;gaps=0
    for b in rows:
        if len(b)<7:raise ValueError("SHORT_RAW_KLINE")
        t=int(b[0]);ct=int(b[6])
        if t%period!=0 or ct!=t+period-1 or ct>=cutoff:raise ValueError("UNVERIFIED_FINALITY")
        if old is not None:
            if t<=old:raise ValueError("DUPLICATE_OR_UNORDERED_KLINE")
            if t-old>period:gaps+=1
        o,h,l,c,v=[float(b[i]) for i in (1,2,3,4,5)]
        if not all(math.isfinite(z) for z in (o,h,l,c,v)):raise ValueError("NONFINITE")
        if min(o,h,l,c)<=0 or v<0 or h<max(o,c) or l>min(o,c) or h<l:raise ValueError("BAD_OHLCV")
        old=t
    return gaps
def download(symbol,interval,asof):
    end=(asof//PERIOD[interval])*PERIOD[interval]-1
    result=[]
    while len(result)<COUNTS[interval]:
        limit=min(1000,COUNTS[interval]-len(result))
        chunk=fetch("/api/v3/klines",{"symbol":symbol,"interval":interval,"endTime":end,"limit":limit})
        if not isinstance(chunk,list) or not chunk:break
        result=chunk+result
        end=int(chunk[0][0])-1
        if len(chunk)<limit:break
        time.sleep(.08)
    return result,validate(symbol,interval,result,asof)
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry["mode"]!="SPOT_ONLY" or registry["constraints"]["real_money_authorized"] is not False:raise ValueError("RESEARCH_POLICY_VIOLATION")
    pairs=[a["pair"] for a in registry["assets"]]
    if len(pairs)!=16 or len(set(pairs))!=16 or any(not p.endswith("USDT") for p in pairs):raise ValueError("PAIR_REGISTRY_MISMATCH")
    utc_ms=int(time.time()*1000)
    info_raw=fetch("/api/v3/exchangeInfo",{"symbols":json.dumps(pairs,separators=(",",":"))})
    info={s["symbol"]:s for s in info_raw.get("symbols",[])}
    if not info:raise ValueError("EXCHANGEINFO_EMPTY")
    result=[]
    for pair in pairs:
        meta=info.get(pair,{})
        allowed=meta.get("status")=="TRADING" and meta.get("isSpotTradingAllowed") is True
        filters={f.get("filterType"):f for f in meta.get("filters",[])}
        record={"pair":pair,"is_spot_trading":allowed,"exchange_status":meta.get("status"),"series":[],
                "lot_size":filters.get("LOT_SIZE"),"min_notional":filters.get("NOTIONAL",filters.get("MIN_NOTIONAL"))}
        if not allowed:
            record["data_gate"]="UNAVAILABLE_SPOT"
        else:
            ready=True
            for interval in PERIOD:
                try:
                    rows,gaps=download(pair,interval,utc_ms)
                    file=f"{pair}_{interval}.json.gz"; dest=OUT/file
                    content={"source":"BINANCE_SPOT_PUBLIC","pair":pair,"interval":interval,
                             "asof_utc":datetime.fromtimestamp(utc_ms/1000,timezone.utc).isoformat(),"rows":rows}
                    blob=gzip.compress(json.dumps(content,ensure_ascii=True,separators=(",",":")).encode(),mtime=0)
                    if dest.exists() and dest.read_bytes()!=blob:raise ValueError("IMMUTABLE_DATA_COLLISION")
                    if not dest.exists():dest.write_bytes(blob)
                    one={"interval":interval,"filename":file,"sha256":sha(blob),"closed_bars":len(rows),
                         "gap_boundaries":gaps,"first_open_ms":int(rows[0][0]) if rows else None,
                         "last_close_ms":int(rows[-1][6]) if rows else None,
                         "data_valid":len(rows)>=900 and gaps==0}
                    if not one["data_valid"]:ready=False
                    record["series"].append(one)
                    print("SPOT16_PAIR "+pair+" "+interval+" CLOSED="+str(len(rows))+" GAPS="+str(gaps)+" PASS="+str(one["data_valid"]),flush=True)
                except Exception as exc:
                    ready=False
                    record["series"].append({"interval":interval,"error":type(exc).__name__,
                                              "reason":str(exc)[:100]})
                    print("SPOT16_PAIR "+pair+" "+interval+" FAILED="+type(exc).__name__,flush=True)
            record["data_gate"]="HISTORY_QUALITY_PASS" if ready else "HISTORY_QUALITY_FAIL"
        result.append(record)
        print("SPOT16_DATA_GATE "+pair+" "+record["data_gate"],flush=True)
        time.sleep(.2)
    manifest={"mode":"RESEARCH_ONLY","provider":"BINANCE_SPOT_PUBLIC","execution":"NONE",
              "asof_utc":datetime.fromtimestamp(utc_ms/1000,timezone.utc).isoformat(),
              "registry_sha256":sha(REGISTRY.read_bytes()),"protocol_sha256":sha(PROTOCOL.read_bytes()),
              "pair_count":len(result),"all_16_covered":len(result)==16,
              "no_order_activity":True,"real_money_authorized":False,"pairs":result}
    dest=OUT/"SPOT16_MANIFEST_20261015.json"
    encoded=(json.dumps(manifest,indent=2,ensure_ascii=True,sort_keys=True)+"\n").encode()
    if dest.exists() and dest.read_bytes()!=encoded:raise RuntimeError("IMMUTABLE_MANIFEST_COLLISION")
    if not dest.exists():dest.write_bytes(encoded)
    print("SPOT16_COMPLETE "+json.dumps({"manifest_sha256":sha(encoded),"pairs":len(result),
       "history_ready":sum(r["data_gate"]=="HISTORY_QUALITY_PASS" for r in result),
       "not_ready":[r["pair"] for r in result if r["data_gate"]!="HISTORY_QUALITY_PASS"],
       "no_orders":True}),flush=True)
if __name__=="__main__":main()