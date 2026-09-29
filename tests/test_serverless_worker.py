from app.bridge_client import ClaimBatch, ClaimedEvent
from app.serverless_worker import run_serverless_drain, run_serverless_once


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.acks = []

    def claim(self, worker_id, limit):
        return ClaimBatch(
            claim_token="claim-serverless",
            events=[
                ClaimedEvent(
                    event_id="evt-serverless-1",
                    payload=self.payload,
                    status="claimed",
                    process_attempts=1,
                )
            ],
        )

    def ack(self, event_id, claim_token, status, note="", result=None):
        self.acks.append({
            "event_id": event_id,
            "claim_token": claim_token,
            "status": status,
            "note": note,
            "result": result,
        })
        return {"ok": True, "event_id": event_id, "status": status}


def test_serverless_worker_archives_test_event_and_returns_result_to_bridge():
    client = FakeClient({"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"})
    result = run_serverless_once(client, worker_id="vercel-1", limit=5)
    assert result.claimed == 1
    assert result.ingested == 1
    assert client.acks[0]["status"] == "ingested"
    assert client.acks[0]["result"]["status"] == "ingested_context"


def test_serverless_worker_rejects_unknown_competition():
    client = FakeClient({"competition_id": "nope", "symbol": "X", "time": "2026-09-20T07:00:00Z"})
    result = run_serverless_once(client)
    assert result.rejected == 1
    assert client.acks[0]["status"] == "rejected"
    assert client.acks[0]["result"]["decision"]["reason"] == "unknown_competition"


class DrainFakeClient:
    def __init__(self, batches):
        self.batches = list(batches)
        self.acks = []

    def claim(self, worker_id, limit):
        items = self.batches.pop(0) if self.batches else []
        return ClaimBatch(
            claim_token="claim-drain" if items else None,
            events=[
                ClaimedEvent(
                    event_id=f"evt-{i}",
                    payload={"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"},
                    status="claimed",
                    process_attempts=1,
                )
                for i in items
            ],
        )

    def ack(self, event_id, claim_token, status, note="", result=None):
        self.acks.append((event_id, status))
        return {"ok": True}


def test_drain_processes_multiple_full_batches_in_one_invocation():
    client = DrainFakeClient([list(range(20)), list(range(20, 26)), []])
    result = run_serverless_drain(client, worker_id="drain", limit=20, max_batches=5)
    assert result.claimed == 26
    assert result.ingested == 26
    assert result.failed == 0
    assert len(client.acks) == 26


class NotificationFakeClient(FakeClient):
    def __init__(self, payload):
        super().__init__(payload)
        self.signal_notifications = []
        self.portfolio_notifications = 0

    def notify_signal(self, event_id):
        self.signal_notifications.append(event_id)
        return {
            "ok": True,
            "skipped": False,
            "dispatch": {"delivered_any": True},
        }

    def notify_portfolio(self):
        self.portfolio_notifications += 1
        return {"ok": True}


def _actionable_payload():
    return {
        "event_id": "evt-actionable-notify",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 4300,
        "high": 4332,
        "low": 4312,
        "close": 4325,
        "volume": 2000,
        "ema20": 4310,
        "ema50": 4280,
        "rsi14": 72,
        "atr14": 12,
        "macd": 8,
        "macd_signal": 3,
        "volume_ratio": 2.0,
        "confirm_timeframe": "60",
        "confirm_time": "2026-09-21T17:00:00Z",
        "confirm_close": 4320,
        "confirm_ema20": 4300,
        "confirm_ema50": 4260,
        "confirm_ema200": 4100,
        "confirm_rsi14": 60,
        "confirm_atr14": 20,
        "confirm_macd": 9,
        "confirm_macd_signal": 4,
        "confirm_volume_ratio": 1.5,
        "trend_2h_time": "2026-09-21T16:00:00Z",
        "trend_2h_score": 0.88,
        "trend_4h_time": "2026-09-21T16:00:00Z",
        "trend_4h_score": 0.84,
        "trend_1m_time": "2026-09-01T00:00:00Z",
        "trend_1m_score": 0.74,
        "family_trend": 0.85,
        "family_momentum": 0.78,
        "family_volatility": 0.65,
        "family_volume": 0.72,
        "family_vwap": 0.70,
        "family_market_structure": 0.88,
        "family_smc_liquidity": 0.86,
        "family_price_action": 0.75,
        "family_microstructure": 0.68,
        "history_timeframe": "1D",
        "history_time": "2026-09-20T00:00:00Z",
        "history_close": 4325,
        "history_ema50": 4200,
        "history_ema200": 3900,
        "history_rsi14": 62,
        "history_atr14": 90,
        "history_high_252": 4350,
        "history_low_252": 3000,
        "history_momentum_20": 0.08,
        "history_momentum_63": 0.15,
        "history_momentum_126": 0.22,
        "history_momentum_252": 0.40,
        "history_volatility_20": 0.02,
    }


def test_actionable_locked_plan_triggers_fail_soft_signal_notification():
    client = NotificationFakeClient(_actionable_payload())
    result = run_serverless_once(client, worker_id="notify", limit=5)
    assert result.ingested == 1
    assert client.signal_notifications == ["evt-serverless-1"]
    assert result.signal_notification_attempted == 1
    assert result.signal_notification_delivered == 1
    assert result.signal_notification_skipped == 0
    assert result.signal_notification_errors == 0


class DrainNotificationClient(DrainFakeClient):
    def __init__(self, batches):
        super().__init__(batches)
        self.portfolio_notifications = 0

    def notify_portfolio(self):
        self.portfolio_notifications += 1
        return {"ok": True}


def test_drain_triggers_one_portfolio_notification_evaluation_after_batching():
    client = DrainNotificationClient([list(range(20)), list(range(20, 26)), []])
    result = run_serverless_drain(client, worker_id="notify-drain", limit=20, max_batches=5)
    assert result.ingested == 26
    assert client.portfolio_notifications == 1


class SkippedNotificationClient(NotificationFakeClient):
    def notify_signal(self, event_id):
        self.signal_notifications.append(event_id)
        return {
            "ok": True,
            "skipped": True,
            "reason": "quality_gate_not_passed",
        }


def test_signal_notification_skip_reason_is_visible_without_failing_ingestion():
    client = SkippedNotificationClient(_actionable_payload())
    result = run_serverless_once(client, worker_id="notify-skip", limit=5)
    assert result.ingested == 1
    assert result.failed == 0
    assert result.signal_notification_attempted == 1
    assert result.signal_notification_skipped == 1
    assert result.signal_notification_skip_reasons == {"quality_gate_not_passed": 1}


class FailedNotificationClient(NotificationFakeClient):
    def notify_signal(self, event_id):
        self.signal_notifications.append(event_id)
        raise RuntimeError("notification transport failed")


def test_signal_notification_failure_is_counted_but_remains_fail_soft():
    client = FailedNotificationClient(_actionable_payload())
    result = run_serverless_once(client, worker_id="notify-fail", limit=5)
    assert result.ingested == 1
    assert result.failed == 0
    assert result.signal_notification_attempted == 1
    assert result.signal_notification_errors == 1
