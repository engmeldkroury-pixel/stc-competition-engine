from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from app.r10_forward_evaluator import normalize_bars, snapshots

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)
SYMBOL = "CAPITALCOM:TEST"


def rows(n=260):
    out=[]; price=100.0
    for i in range(n):
        drift=0.03 + (0.02 if i % 7 < 4 else -0.01)
        o=price; c=price+drift; h=max(o,c)+0.20; l=min(o,c)-0.20
        out.append({"symbol":SYMBOL,"timeframe_minutes":15,"time":(BASE+timedelta(minutes=15*i)).isoformat(),"open":o,"high":h,"low":l,"close":c})
        price=c
    return out


def test_normalize_requires_contiguous_exact_series_and_rejects_conflicts():
    x=rows(3); assert len(normalize_bars(x,symbol=SYMBOL))==3
    gap=rows(3); gap[2]["time"]=(BASE+timedelta(minutes=60)).isoformat()
    with pytest.raises(ValueError,match="noncontiguous"):
        normalize_bars(gap,symbol=SYMBOL)
    dup=rows(3); bad=deepcopy(dup[1]);bad["close"]+=1;bad["high"]+=1;dup.append(bad)
    with pytest.raises(ValueError,match="conflicting"):
        normalize_bars(dup,symbol=SYMBOL)


def test_snapshot_at_index_is_unchanged_by_future_mutation():
    base=rows(); first=snapshots(base,symbol=SYMBOL)
    target=first[0]
    changed=deepcopy(base)
    for i in range(target["bar_index"]+1,len(changed)):
        changed[i]["open"]*=1.5;changed[i]["high"]*=1.5;changed[i]["low"]*=1.5;changed[i]["close"]*=1.5
    second={x["bar_index"]:x for x in snapshots(changed,symbol=SYMBOL)}[target["bar_index"]]
    assert second["snapshot"]==target["snapshot"]
    assert second["decision"]==target["decision"]


def test_no_snapshot_exists_before_causal_history_is_available():
    x=snapshots(rows(),symbol=SYMBOL)
    assert x and min(z["bar_index"] for z in x)>=199
