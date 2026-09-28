from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from app.r10_amp_crypto_evaluator import snapshots

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)
SYMBOL = "CME:MBT1!"


def rows(n=260):
    out=[]; price=100.0
    for i in range(n):
        drift=0.03 + (0.02 if i % 7 < 4 else -0.01)
        o=price; c=price+drift; h=max(o,c)+0.20; l=min(o,c)-0.20
        out.append({"symbol":SYMBOL,"timeframe_minutes":15,"time":(BASE+timedelta(minutes=15*i)).isoformat(),"open":o,"high":h,"low":l,"close":c})
        price=c
    return out


def test_amp_evaluator_is_causal_under_future_mutation():
    base=rows(); first=snapshots(base,symbol=SYMBOL); target=first[0]
    changed=deepcopy(base)
    for i in range(target["bar_index"]+1,len(changed)):
        for key in ("open","high","low","close"):
            changed[i][key]*=1.5
    second={x["bar_index"]:x for x in snapshots(changed,symbol=SYMBOL)}[target["bar_index"]]
    assert second["snapshot"]==target["snapshot"]
    assert second["decision"]==target["decision"]


def test_amp_evaluator_rejects_non_frozen_symbol():
    with pytest.raises(ValueError,match="symbol_not"):
        snapshots(rows(),symbol="CME_MINI:MNQ1!")
