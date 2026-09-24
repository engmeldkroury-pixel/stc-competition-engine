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
    assert 'id="record-panel"' in source
    assert "function submitPositionModal()" in source
    assert "EXECUTION TICKET" in source
    assert "TradingView size mode: Units / Contracts — NOT % balance" in source
    assert "Advanced details / why STC selected this setup" in source
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
    assert 'placeholder="Current TradingView price — decimal or exchange quote"' in source


def test_console_keeps_recovery_path_when_signal_refreshes_after_manual_fill() -> None:
    source = _source()
    assert "function latestLockedPlanContextHtml(c)" in source
    assert "function isLockedPlanVisible(c)" in source
    assert "RECOVERY ONLY" in source
    assert "LOCKED PLAN PRESERVED" in source
    assert "approval_compatible_with_locked_plan" in source
    assert "Already filled on platform? Record position" in source
    assert "If you already filled the trade and the signal card disappeared after a refresh, DO NOT enter the trade again." in source
    assert "newer_signal_not_aligned" in source


def test_record_trade_competition_is_selected_from_allowed_values_and_capital_symbol_is_normalized() -> None:
    source = _source()
    assert 'id="pos-competition"' in source
    assert '<option value="capital-africa-sep-2026">Capital.com Africa</option>' in source
    assert '<option value="amp-futures-sep-2026">AMP Futures</option>' in source
    assert "function normalizePositionSymbolForCompetition" in source
    assert "return 'CAPITALCOM:'+raw" in source
    assert "Select the competition first." in source
    assert "Position target is not valid. Select the competition and use the supported symbol" in source


def test_record_trade_blank_open_time_uses_server_time() -> None:
    source = _source()
    assert "Leave blank to use the STC server time automatically." in source
    assert "const openedAt=openedText?new Date(openedText):null;" in source
    assert "const openedUtc=openedAt?openedAt.toISOString():null;" in source
    assert "opened_at_utc:openedUtc" in source
    assert "manual_position_open_time_outside_competition_window" in source
    assert "opened_at_out_of_range" in source


def test_competition_tabs_expose_trade_inventory_open_pnl_and_recent_completed_trades():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "'open_unrealized_pnl_usd' => 0.0" in snapshot
    assert "'open_unrealized_known_positions' => 0" in snapshot
    assert "'open_unrealized_unknown_positions' => 0" in snapshot
    assert "'closed_positions_recent' => $closedPositions" in snapshot
    assert "WHERE status = 'CLOSED'" in snapshot
    for label in (
        "TRADE INVENTORY — THIS COMPETITION",
        "Open trades",
        "Completed trades",
        "Open P/L estimate",
        "Tracked P/L",
        "Completed trades — recent",
        "CLOSED • RECORDED",
        "Latest market check — STC bar mark",
        "not a broker live quote",
    ):
        assert label in ui
