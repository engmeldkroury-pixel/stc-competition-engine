import json
from pathlib import Path


def test_crypto_spot_adaptive_strategy_config_is_spot_only():
    path = Path('research_inputs/CRYPTO_SPOT_ADAPTIVE_STRATEGY_CONFIG_v1.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['execution'] == 'PAPER_TRADING_ONLY'
    assert data['risk']['spot_only'] is True
    assert data['risk']['leverage'] is False
    assert data['risk']['short'] is False
    assert data['adaptive_rules']['weights_must_be_data_derived'] is True
    assert data['adaptive_rules']['walk_forward_required'] is True
