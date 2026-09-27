"""Offline tests: PHP projection is not market performance evidence."""
import json, os, subprocess
from pathlib import Path
from tests.test_outcome_attribution import stored_row
from app.cloud_approval import _validate_record

PHP=Path('scripts/export_outcome_history.php')

def test_php_history_reader_lints():
    assert subprocess.run(['php','-l',str(PHP)],capture_output=True).returncode == 0

def test_php_projection_retains_receipt_integrity_and_removes_unneeded_fields():
    row=stored_row(); row['payload']['test_float']=1.0
    from app.pipeline_receipt import build_pipeline_receipt
    row['result']['receipt']=build_pipeline_receipt(row['event_id'],row['payload'],status='analyzed',action='signal_created',signal_id=row['result']['decision']['signal']['signal_id'])
    row['result']['unrelated_private_field']='MUST_NOT_LEAVE_SERVER'
    raw={'event_id':row['event_id'],'status':row['status'],'payload_json':json.dumps(row['payload']),'result_json':json.dumps(row['result'])}
    process=subprocess.run(['php',str(PHP)],env={**os.environ,'STC_R8_PROJECTION_TEST':'1'},input=json.dumps(raw),capture_output=True,text=True)
    assert process.returncode == 0, process.stderr
    assert 'MUST_NOT_LEAVE_SERVER' not in process.stdout
    projected=json.loads(process.stdout)
    assert type(projected['payload']['test_float']) is float
    _validate_record(projected)
    assert projected['result']['decision']['research_outcome_seed'] == row['result']['decision']['research_outcome_seed']

def test_exporter_is_cli_read_only_bounded_and_no_account_tables():
    source=PHP.read_text()
    assert "PHP_SAPI !== 'cli'" in source
    assert 'WITH CONSISTENT SNAPSHOT, READ ONLY' in source
    assert 'ORDER BY id DESC LIMIT 5000' in source
    for forbidden in ['INSERT INTO','DELETE FROM','UPDATE stc_','DROP TABLE','stc_positions','stc_account_state','file_put_contents']:
        assert forbidden not in source
