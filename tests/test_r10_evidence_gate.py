import pytest
from app.r10_evidence_gate import assess_forward_evidence

SHA="a"*64

def row(i,r=0.5,status="SETTLED",sym=None,day=None):
    return {"protocol_sha256":SHA,"symbol":sym or f"S{i%4}","source_open_utc":f"2026-09-{20+i:02d}T12:00:00Z","cost_bps":2,"status":status,"net_r":r,"day":day or f"2026-09-{20+i%6:02d}"}

def test_fails_closed_on_protocol_mismatch_and_duplicates():
    x=row(0);x["protocol_sha256"]="bad"
    with pytest.raises(ValueError,match="protocol_sha"):
        assess_forward_evidence([x],expected_protocol_sha256=SHA,min_settled=1,min_days=1,min_symbols=1)
    x=row(0)
    with pytest.raises(ValueError,match="duplicate"):
        assess_forward_evidence([x,x],expected_protocol_sha256=SHA,min_settled=1,min_days=1,min_symbols=1)

def test_censored_rows_do_not_become_wins_or_losses():
    x=row(0,status="CENSORED");x.pop("net_r")
    got=assess_forward_evidence([x],expected_protocol_sha256=SHA,min_settled=1,min_days=1,min_symbols=1)
    assert got["settled"]==0 and got["status"]=="INSUFFICIENT_EVIDENCE"

def test_small_positive_sample_is_still_insufficient():
    got=assess_forward_evidence([row(i,1.0) for i in range(4)],expected_protocol_sha256=SHA,min_settled=20,min_days=5,min_symbols=2)
    assert got["status"]=="INSUFFICIENT_EVIDENCE" and got["auto_promotion"] is False

def test_clustered_positive_result_is_not_automatically_promoted():
    rows=[]
    for i in range(30):
        d=f"2026-09-{20+i%5:02d}"
        r=2.0 if i%5==0 else (-0.2 if i%3==0 else 0.1)
        rows.append(row(i,r,sym=f"S{i%4}",day=d))
    got=assess_forward_evidence(rows,expected_protocol_sha256=SHA,min_settled=30,min_days=5,min_symbols=4)
    assert got["settled"]==30 and got["cluster_ci95"][0] is not None
    assert got["live_authorized"] is False and got["auto_promotion"] is False
