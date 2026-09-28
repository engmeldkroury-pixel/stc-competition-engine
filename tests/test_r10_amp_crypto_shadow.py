import pytest
from app.r10_amp_crypto_shadow import FROZEN_AMP_CRYPTO, protocol_sha256, shadow_decision


def snap(**u):
    x={"source_open_utc":"2026-09-28T04:15:00Z","open":100.0,"close":100.2,"ema20":100.0,"ema50":99.0,"ema200":98.0,"atr14":1.0,"adx14":31.0,"rsi14":55.0,"range_atr":1.0}
    x.update(u);return x


def test_boundary_and_research_authority_are_frozen():
    assert FROZEN_AMP_CRYPTO.not_before_utc=="2026-09-28T04:15:00Z"
    assert FROZEN_AMP_CRYPTO.live_authorized is False
    assert protocol_sha256()==protocol_sha256()


def test_only_frozen_crypto_symbols_are_accepted():
    with pytest.raises(ValueError,match="symbol_not"):
        shadow_decision("CME_MINI:MNQ1!",snap())


def test_long_short_symmetry_and_geometry_metadata():
    a=shadow_decision("CME:MBT1!",snap())
    b=shadow_decision("CME:MET1!",snap(open=100,close=99.8,ema20=100,ema50=101,ema200=102,rsi14=45))
    assert a["decision"]=="LONG" and b["decision"]=="SHORT"
    for x in (a,b):
        assert x["initial_stop_atr_multiple"]==2.0 and x["single_target_r"]==2.0
        assert x["research_only"] is True and x["live_authorized"] is False and x["execution"]=="none"
        assert "quantity" not in x and "approval" not in x


def test_low_adx_or_chasing_is_wait():
    assert shadow_decision("CME:MBT1!",snap(adx14=25))["decision"]=="WAIT"
    assert shadow_decision("CME:MBT1!",snap(close=101.0))["decision"]=="WAIT"


def test_pre_freeze_signal_is_not_forward_eligible():
    x=shadow_decision("CME:MBT1!",snap(source_open_utc="2026-09-28T04:00:00Z"))
    assert x["decision"]=="LONG" and x["forward_eligible"] is False
