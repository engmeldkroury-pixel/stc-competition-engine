from copy import deepcopy
from datetime import timedelta
import pytest
from app.outcome_dataset import digest
from app.outcome_attribution import utc,iso
from scripts.r9_reviewed_supplement import overlay_reviewed_research_bars
from tests.test_r9_data_exit_audit import dataset
from tests.test_outcome_attribution import stored_row


def source():
    d=dataset([stored_row(event_id=str(i),minute=15*i) for i in range(22)])
    candidate=deepcopy(d['bars']);missing=candidate.pop(10)
    d['bars']=candidate[:];d['dataset_sha256']=digest({k:v for k,v in d.items() if k!='dataset_sha256'})
    candidate=candidate+[missing]
    review={'scope':'research_prices_only','decision':'ACCEPT_EXACT_HASHED_SNAPSHOT','candidate_sha256':digest(candidate),
            'source_reference':'synthetic-test-only','series_key':['capital-africa-sep-2026','CAPITALCOM:BTCUSD',15]}
    return d,candidate,review


def test_overlay_preserves_seed_and_original_prices_and_hashes():
    d,c,r=source();original=deepcopy(d);x=overlay_reviewed_research_bars(d,c,review=r)
    assert d==original and x['seeds']==d['seeds'] and len(x['bars'])==len(d['bars'])+1
    assert x['reviewed_research_supplements'][0]['added_bars']==1
    assert not x['live_authorized'] and x['execution']=='none'


def test_unreviewed_changed_cross_source_and_conflicting_candidates_blocked():
    d,c,r=source()
    with pytest.raises(ValueError):overlay_reviewed_research_bars(d,c,review={})
    c[0]['close']=101
    with pytest.raises(ValueError):overlay_reviewed_research_bars(d,c,review=r)
    r['candidate_sha256']=digest(c)
    with pytest.raises(ValueError):overlay_reviewed_research_bars(d,c,review=r)
    d,c,r=source();c[0]['symbol']='BITSTAMP:BTCUSD';r['candidate_sha256']=digest(c)
    with pytest.raises(ValueError):overlay_reviewed_research_bars(d,c,review=r)


def test_mutable_tail_is_never_imported_even_in_reviewed_snapshot():
    d,c,r=source();future=deepcopy(c[-1]);future['time']=d['as_of'];c.append(future);r['candidate_sha256']=digest(c)
    x=overlay_reviewed_research_bars(d,c,review=r)
    assert len(x['bars'])==22 and future not in x['bars']
