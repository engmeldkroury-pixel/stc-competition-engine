"""The production reader must honor the existing 1..100 inbox contract."""
from pathlib import Path
import subprocess
import sys

import pytest

@pytest.mark.parametrize('limit', ['0', '101', '1000'])
def test_cli_rejects_out_of_contract_limit_before_any_network(tmp_path,limit):
    out = subprocess.run([sys.executable, 'scripts/run_outcome_attribution.py',
                          '--bridge-url', 'https://stc.feama.site', '--limit', limit,
                          '--output', str(tmp_path/'unused.json')],capture_output=True,text=True)
    assert out.returncode == 2
    assert '1..100' in out.stderr
    assert not (tmp_path/'unused.json').exists()

def test_workflow_reader_must_never_claim_ack_or_export_raw_inbox():
    source = Path('scripts/run_outcome_attribution.py').read_text()
    assert 'default=100)' in source
    assert '.inbox(status="ingested"' in source
    assert '.claim(' not in source and '.ack(' not in source
    assert 'response body withheld' in source
