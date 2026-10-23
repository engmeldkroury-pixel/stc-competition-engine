"""Read-only offline research runner. No real or Paper order authority."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
STC=REPO.parents[1]
OUT=STC/"Verification"/"Spot16_Binance_20261015"
MANIFEST=OUT/"SPOT16_MANIFEST_20261015.json"
RESULT=OUT/"STC_SPOT16_FIXED_SCREEN_RESEARCH_V2.json"
LEDGER=OUT/"STC_SPOT16_HYPOTHETICAL_LEDGER_V2.json.gz"
sys.path.insert(0,str(REPO))
from app.spot16_manual_paper_strategy import FAMILIES,COST_BPS,run_fixed_screen
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    results,ledger=run_fixed_screen(MANIFEST)
    if results["execution"]!="NONE" or not results["no_strategy_promoted"] or len(results["result_rows"])<50:
        raise RuntimeError("UNEXPECTED_SPOT_EXECUTION_OR_RESEARCH_SCOPE")
    results["screen_source_code_sha256"]=sha((REPO/"app"/"spot16_manual_paper_strategy.py").read_bytes())
    results["runtime_manifest_sha256"]=sha(MANIFEST.read_bytes())
    outputs={
        RESULT:(json.dumps(results,sort_keys=True,ensure_ascii=True,indent=2)+"\n").encode(),
        LEDGER:gzip.compress((json.dumps(ledger,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode(),mtime=0)
    }
    for path,blob in outputs.items():
        if path.exists() and path.read_bytes()!=blob:
            raise RuntimeError("RESEARCH_OUTCOME_DIFFERENT_ON_REPRODUCTION_"+path.name)
        if not path.exists():path.write_bytes(blob)
    groups={}
    for family in FAMILIES:
        for bps in COST_BPS:
            r=[x for x in results["result_rows"] if x.get("family")==family
               and x.get("segment")=="HISTORICAL_RESEARCH_HOLDOUT"
               and x.get("assumed_friction_bps_per_side")==bps]
            groups[f"{family}_{bps}bps"]={
              "eligible_pairs":len(r),"trades":sum(x["trades"] for x in r),
              "pairs_with_20_or_more_trades":sum(x["trades"]>=20 for x in r),
              "positive_series":sum(x["positive_mean"] for x in r),
              "sum_independent_R_not_portfolio":round(sum(x["net_R_sum"] for x in r),5)}
    print("SPOT16_RESEARCH_SUMMARY "+json.dumps({
     "source_manifest_sha256":sha(MANIFEST.read_bytes()),
     "results_sha256":sha(RESULT.read_bytes()),
     "ledger_sha256":sha(LEDGER.read_bytes()),
     "research_only":True,"no_orders":True,
     "pairs":results["symbols_registered"],"qualified":results["symbols_historical_qa_pass"],
     "blocked":results["blocked_symbols"],"hypothetical_ledger_rows":len(ledger),
     "summary":groups},sort_keys=True),flush=True)
if __name__=="__main__":main()