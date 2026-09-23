from pathlib import Path


OPERATOR = Path("hostinger_patch/operator.php")


def _source() -> str:
    return OPERATOR.read_text(encoding="utf-8")


def test_operator_supports_treasury_exchange_quotes_and_tick_aligned_decimals() -> None:
    source = _source()
    assert "'CBOT:ZN1!':{tick:1/64,style:'treasury32'}" in source
    assert "'CBOT:ZB1!':{tick:1/32,style:'treasury32'}" in source
    assert "function parsePlatformPrice(symbol,raw)" in source
    assert "105'12'5" in source
    assert "Values such as 105.13 are rejected for ZN" in source


def test_existing_position_uses_single_inline_form_instead_of_prompt_chain() -> None:
    source = _source()
    assert 'id="position-modal"' in source
    assert "function submitPositionModal()" in source
    assert "Already filled on platform? Record position" in source
    manual_start = source.index("function recordExistingPosition(")
    manual_end = source.index("function recordFilledPosition(", manual_start)
    assert "prompt(" not in source[manual_start:manual_end]
    assert "confirm(" not in source[manual_start:manual_end]


def test_approval_preserves_block_reasons_instead_of_only_http_409() -> None:
    source = _source()
    assert "err.payload=j" in source
    assert "price_outside_envelope:'Current price is outside the locked entry zone.'" in source
    assert "Approval blocked: '+text" in source
    assert 'type="text" autocomplete="off" placeholder="Current TradingView price — decimal or exchange quote"' in source
