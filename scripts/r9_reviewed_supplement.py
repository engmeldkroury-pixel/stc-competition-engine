"""Research overlay only, after explicit exact-source consistency review.

Never changes the original archive, original seed, real account or live strategy.
All new prices are actual observed candles; gaps and market sessions are not
invented. A recorded review permits only the exact hashed candidate snapshot.
"""
from copy import deepcopy
from datetime import timedelta
from app.outcome_attribution import utc
from app.outcome_dataset import (validate_dataset,clean_bar,series_key,digest,reconcile_candidate_bars)


def overlay_reviewed_research_bars(dataset, candidate, *, review):
    validate_dataset(dataset)
    if review.get('scope')!='research_prices_only' or review.get('decision')!='ACCEPT_EXACT_HASHED_SNAPSHOT':
        raise ValueError('explicit_research_review_required')
    if review.get('candidate_sha256')!=digest(candidate) or not review.get('source_reference'):
        raise ValueError('candidate_review_mismatch')
    expected_key=tuple(review['series_key'])
    if len(expected_key)!=3 or any(series_key(row)!=expected_key for row in candidate):
        raise ValueError('cross_series_overlay_blocked')
    cutoff=utc(dataset['as_of'])
    base=[b for b in dataset['bars'] if series_key(b)==expected_key]
    comparison=reconcile_candidate_bars(base,candidate,as_of=cutoff,tolerance=0.,min_overlap=20)
    if not comparison['by_series'] or any(not x['price_consistency_passed'] for x in comparison['by_series'].values()):
        raise ValueError('exact_price_reconciliation_failed')
    indexed={(*series_key(b),b['time']):b for b in dataset['bars']}
    added=[]
    for raw in candidate:
        b=clean_bar(raw)
        if utc(b['time'])+timedelta(minutes=b['timeframe_minutes'])>cutoff:
            continue
        key=(*series_key(b),b['time'])
        if key not in indexed:
            indexed[key]=b;added.append(b['time'])
    result=deepcopy(dataset)
    result['parent_dataset_sha256']=dataset['dataset_sha256']
    result['bars']=sorted(indexed.values(),key=lambda b:(series_key(b),b['time']))
    result.setdefault('reviewed_research_supplements',[]).append({
        'review':review,'comparison':comparison,'added_bars':len(added),
        'added_open_times':added,'no_original_seed_change':True,
        'not_live_approval_evidence':True,'not_assumed_session_closure':True})
    result['dataset_sha256']=digest({k:v for k,v in result.items() if k!='dataset_sha256'})
    return result
