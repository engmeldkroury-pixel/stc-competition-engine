"""Expired analysis remains research history, never a revived order."""
import pytest
from tests.test_r9_data_exit_audit import dataset
from tests.test_outcome_attribution import stored_row, stamp
from app.exit_policy_audit import audit_exit_policies


@pytest.mark.parametrize('issued', [60, 120])
def test_late_decision_retains_real_candle_but_never_regains_entry_authority(issued):
    from app.outcome_attribution import build_outcome_seed
    a=stored_row();d=a['result']['decision'];d['approval_envelope']['issued_at']=stamp(issued)
    d['research_outcome_seed']=build_outcome_seed(a['event_id'],a['payload'],d['signal'],d['approval_envelope'])
    result=dataset([a]);assert len(result['bars'])==1
    assert result['late_decision_rows_retained']==1 and not result['quarantine_counts']
    frozen=result['seeds'][0]
    assert frozen['expires_at']==stamp(60).replace('+00:00','Z')
    audit=audit_exit_policies(result,horizon_bars=1)
    assert audit['outcomes'][0]['status']=='NO_ENTRY' and audit['entered']==0
    assert audit['outcomes'][0]['entry'] is None


def test_expiry_before_source_close_remains_invalid_and_error_stage_is_safe():
    a=stored_row();a['result']['decision']['approval_envelope']['valid_until']=stamp(10)
    result=dataset([a]);assert not result['bars']
    assert result['invalid_record_stage_counts']=={'envelope':1}
    assert 'r8-test-1' not in str(result['invalid_record_stage_counts'])
