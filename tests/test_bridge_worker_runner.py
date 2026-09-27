from __future__ import annotations

import httpx

from app.bridge_client import BridgeClientError
from run_bridge_worker_once import is_transient_bridge_failure


def test_transient_bridge_failure_classifies_network_transport():
    exc = httpx.ConnectError("network unreachable")
    assert is_transient_bridge_failure(exc) is True


def test_transient_bridge_failure_classifies_html_edge_403_and_5xx():
    assert is_transient_bridge_failure(
        BridgeClientError("claim_failed:403:<!DOCTYPE html><html>")
    ) is True
    assert is_transient_bridge_failure(
        BridgeClientError("claim_failed:503:temporary upstream failure")
    ) is True


def test_transient_bridge_failure_does_not_hide_auth_or_contract_errors():
    assert is_transient_bridge_failure(
        BridgeClientError('claim_failed:403:{"error":"invalid_worker_token"}')
    ) is False
    assert is_transient_bridge_failure(
        BridgeClientError("claim_rejected:{'ok': False}")
    ) is False
