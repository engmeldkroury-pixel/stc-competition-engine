from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from .models import ExecutionEvidence

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "stc.db"
_LOCK = Lock()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_utc TEXT NOT NULL,
                event_type TEXT NOT NULL,
                competition_id TEXT,
                symbol TEXT,
                payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                ts_utc TEXT NOT NULL,
                competition_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                composite_score REAL NOT NULL,
                approved INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL
            );
            """
        )


def log_event(event_type: str, payload: dict, competition_id: str | None = None, symbol: str | None = None) -> None:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO audit_events(ts_utc,event_type,competition_id,symbol,payload_json) VALUES (?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(),
                event_type,
                competition_id,
                symbol,
                json.dumps(payload, separators=(",", ":"), default=str),
            ),
        )


def save_signal(signal: dict) -> None:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO signals
               (signal_id,ts_utc,competition_id,symbol,recommendation,composite_score,approved,payload_json)
               VALUES (?,?,?,?,?,?,COALESCE((SELECT approved FROM signals WHERE signal_id=?),0),?)""",
            (
                signal["signal_id"],
                datetime.now(timezone.utc).isoformat(),
                signal["competition_id"],
                signal["symbol"],
                signal["recommendation"],
                signal["composite_score"],
                signal["signal_id"],
                json.dumps(signal, separators=(",", ":"), default=str),
            ),
        )


def approve_signal(signal_id: str) -> bool:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("UPDATE signals SET approved=1 WHERE signal_id=?", (signal_id,))
        return cur.rowcount == 1


def summary() -> dict:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        audit_count = conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
        signal_count = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
        approved = conn.execute("SELECT COUNT(*) FROM signals WHERE approved=1").fetchone()[0]
    return {"audit_events": audit_count, "signals": signal_count, "approved_signals": approved}


def _ensure_trade_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS trade_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id TEXT NOT NULL,
            competition_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            event TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            event_time TEXT NOT NULL,
            realized_pnl_delta REAL NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_trade_events_comp ON trade_events(competition_id);
        CREATE INDEX IF NOT EXISTS idx_trade_events_trade ON trade_events(trade_id);
        """
    )


def record_trade_event(event: dict) -> dict:
    import uuid

    init_db()
    trade_id = event.get("trade_id") or str(uuid.uuid4())
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_trade_tables(conn)
        conn.execute(
            """INSERT INTO trade_events
               (trade_id,competition_id,symbol,event,side,quantity,price,event_time,realized_pnl_delta)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                trade_id,
                event["competition_id"],
                event["symbol"],
                event["event"],
                event["side"],
                event["quantity"],
                event["price"],
                str(event["event_time"]),
                event.get("realized_pnl_delta", 0.0),
            ),
        )
        realized = conn.execute(
            "SELECT COALESCE(SUM(realized_pnl_delta),0) FROM trade_events WHERE competition_id=?",
            (event["competition_id"],),
        ).fetchone()[0]
        days = conn.execute(
            """SELECT COUNT(DISTINCT substr(event_time,1,10))
               FROM trade_events
               WHERE competition_id=? AND event IN ('OPEN','CLOSE')""",
            (event["competition_id"],),
        ).fetchone()[0]
    return {
        "trade_id": trade_id,
        "status": "CLOSED" if event["event"] == "CLOSE" else "OPEN",
        "realized_pnl_total": float(realized),
        "qualifying_trading_days": int(days),
    }


def competition_trade_summary(competition_id: str) -> dict:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_trade_tables(conn)
        realized = conn.execute(
            "SELECT COALESCE(SUM(realized_pnl_delta),0) FROM trade_events WHERE competition_id=?",
            (competition_id,),
        ).fetchone()[0]
        days = conn.execute(
            """SELECT COUNT(DISTINCT substr(event_time,1,10))
               FROM trade_events
               WHERE competition_id=? AND event IN ('OPEN','CLOSE')""",
            (competition_id,),
        ).fetchone()[0]
        events = conn.execute(
            "SELECT COUNT(*) FROM trade_events WHERE competition_id=?",
            (competition_id,),
        ).fetchone()[0]
    return {
        "competition_id": competition_id,
        "realized_pnl": float(realized),
        "qualifying_trading_days": int(days),
        "trade_events": int(events),
    }



def _ensure_webhook_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS webhook_events (
            event_id TEXT PRIMARY KEY,
            first_received_utc TEXT NOT NULL,
            last_received_utc TEXT NOT NULL,
            duplicate_count INTEGER NOT NULL DEFAULT 0,
            competition_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_webhook_events_comp ON webhook_events(competition_id);
        """
    )


def record_webhook_once(event_id: str, payload: dict, competition_id: str, symbol: str) -> dict:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_webhook_tables(conn)
        row = conn.execute(
            "SELECT duplicate_count FROM webhook_events WHERE event_id=?",
            (event_id,),
        ).fetchone()
        if row is not None:
            duplicate_count = int(row[0]) + 1
            conn.execute(
                "UPDATE webhook_events SET last_received_utc=?, duplicate_count=? WHERE event_id=?",
                (now, duplicate_count, event_id),
            )
            return {"is_new": False, "duplicate_count": duplicate_count}
        conn.execute(
            """INSERT INTO webhook_events
               (event_id,first_received_utc,last_received_utc,duplicate_count,competition_id,symbol,payload_json)
               VALUES (?,?,?,?,?,?,?)""",
            (
                event_id,
                now,
                now,
                0,
                competition_id,
                symbol,
                json.dumps(payload, separators=(",", ":"), default=str),
            ),
        )
        return {"is_new": True, "duplicate_count": 0}


def recent_signals(limit: int = 20) -> list[dict]:
    init_db()
    limit = max(1, min(limit, 100))
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """SELECT signal_id,ts_utc,competition_id,symbol,recommendation,composite_score,approved
               FROM signals ORDER BY ts_utc DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [
        {
            "signal_id": r[0],
            "ts_utc": r[1],
            "competition_id": r[2],
            "symbol": r[3],
            "recommendation": r[4],
            "composite_score": r[5],
            "approved": bool(r[6]),
        }
        for r in rows
    ]


def _ensure_bridge_inbox_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS bridge_inbox (
            event_id TEXT PRIMARY KEY,
            first_seen_utc TEXT NOT NULL,
            updated_utc TEXT NOT NULL,
            competition_id TEXT,
            symbol TEXT,
            status TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            decision_json TEXT,
            note TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_bridge_inbox_status ON bridge_inbox(status, first_seen_utc);
        """
    )


def bridge_event_get(event_id: str) -> dict | None:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_bridge_inbox_tables(conn)
        row = conn.execute(
            """SELECT event_id,first_seen_utc,updated_utc,competition_id,symbol,status,payload_json,decision_json,note
               FROM bridge_inbox WHERE event_id=?""",
            (event_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "event_id": row[0],
        "first_seen_utc": row[1],
        "updated_utc": row[2],
        "competition_id": row[3],
        "symbol": row[4],
        "status": row[5],
        "payload": json.loads(row[6]),
        "decision": json.loads(row[7]) if row[7] else None,
        "note": row[8],
    }


def bridge_event_start(event_id: str, payload: dict) -> dict:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    competition_id = payload.get("competition_id")
    symbol = payload.get("symbol")
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_bridge_inbox_tables(conn)
        existing = conn.execute(
            "SELECT status,decision_json,note FROM bridge_inbox WHERE event_id=?",
            (event_id,),
        ).fetchone()
        if existing is not None:
            return {
                "is_new": False,
                "status": existing[0],
                "decision": json.loads(existing[1]) if existing[1] else None,
                "note": existing[2],
            }
        conn.execute(
            """INSERT INTO bridge_inbox
               (event_id,first_seen_utc,updated_utc,competition_id,symbol,status,payload_json)
               VALUES (?,?,?,?,?,'processing',?)""",
            (
                event_id,
                now,
                now,
                competition_id,
                symbol,
                json.dumps(payload, separators=(",", ":"), default=str),
            ),
        )
    return {"is_new": True, "status": "processing", "decision": None, "note": None}


def bridge_event_finish(event_id: str, status: str, decision: dict | None = None, note: str | None = None) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_bridge_inbox_tables(conn)
        conn.execute(
            """UPDATE bridge_inbox SET updated_utc=?, status=?, decision_json=?, note=? WHERE event_id=?""",
            (
                now,
                status,
                json.dumps(decision, separators=(",", ":"), default=str) if decision is not None else None,
                note,
                event_id,
            ),
        )


def bridge_inbox_summary() -> dict:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_bridge_inbox_tables(conn)
        total = conn.execute("SELECT COUNT(*) FROM bridge_inbox").fetchone()[0]
        rows = conn.execute("SELECT status,COUNT(*) FROM bridge_inbox GROUP BY status").fetchall()
    return {"total": int(total), "by_status": {str(status): int(count) for status, count in rows}}


def _ensure_approval_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS signal_approvals (
            signal_id TEXT PRIMARY KEY,
            envelope_json TEXT NOT NULL,
            approval_status TEXT NOT NULL DEFAULT 'pending',
            approved_at_utc TEXT,
            last_revalidated_at_utc TEXT,
            last_revalidation_json TEXT
        );
        CREATE TABLE IF NOT EXISTS runtime_control (
            id INTEGER PRIMARY KEY CHECK (id=1),
            safe_mode INTEGER NOT NULL DEFAULT 0,
            kill_switch INTEGER NOT NULL DEFAULT 0,
            reason TEXT,
            updated_utc TEXT NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO runtime_control(id,safe_mode,kill_switch,reason,updated_utc) VALUES (1,0,0,NULL,?)",
        (datetime.now(timezone.utc).isoformat(),),
    )


def save_approval_envelope(signal_id: str, envelope: dict) -> None:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_approval_tables(conn)
        conn.execute(
            """INSERT INTO signal_approvals(signal_id,envelope_json,approval_status)
               VALUES (?,?, 'pending')
               ON CONFLICT(signal_id) DO UPDATE SET envelope_json=excluded.envelope_json""",
            (signal_id, json.dumps(envelope, separators=(",", ":"), default=str)),
        )


def get_approval_envelope(signal_id: str) -> dict | None:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_approval_tables(conn)
        row = conn.execute(
            "SELECT envelope_json,approval_status,approved_at_utc,last_revalidated_at_utc,last_revalidation_json FROM signal_approvals WHERE signal_id=?",
            (signal_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "signal_id": signal_id,
        "envelope": json.loads(row[0]),
        "approval_status": row[1],
        "approved_at_utc": row[2],
        "last_revalidated_at_utc": row[3],
        "last_revalidation": json.loads(row[4]) if row[4] else None,
    }


def record_revalidation(signal_id: str, result: dict) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_approval_tables(conn)
        status = "approved_fresh" if result.get("valid") else "stale_or_blocked"
        conn.execute(
            """UPDATE signal_approvals
               SET approval_status=?, approved_at_utc=CASE WHEN ? THEN COALESCE(approved_at_utc,?) ELSE approved_at_utc END,
                   last_revalidated_at_utc=?, last_revalidation_json=?
               WHERE signal_id=?""",
            (status, bool(result.get("valid")), now, now, json.dumps(result, separators=(",", ":")), signal_id),
        )
        if result.get("valid"):
            conn.execute("UPDATE signals SET approved=1 WHERE signal_id=?", (signal_id,))


def get_runtime_control() -> dict:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_approval_tables(conn)
        row = conn.execute("SELECT safe_mode,kill_switch,reason,updated_utc FROM runtime_control WHERE id=1").fetchone()
    return {"safe_mode": bool(row[0]), "kill_switch": bool(row[1]), "reason": row[2], "updated_utc": row[3]}


def set_runtime_control(safe_mode: bool | None = None, kill_switch: bool | None = None, reason: str | None = None) -> dict:
    current = get_runtime_control()
    new_safe = current["safe_mode"] if safe_mode is None else bool(safe_mode)
    new_kill = current["kill_switch"] if kill_switch is None else bool(kill_switch)
    now = datetime.now(timezone.utc).isoformat()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_approval_tables(conn)
        conn.execute("UPDATE runtime_control SET safe_mode=?,kill_switch=?,reason=?,updated_utc=? WHERE id=1",
                     (int(new_safe), int(new_kill), reason, now))
    return get_runtime_control()


def _ensure_execution_evidence_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS execution_evidence (
            evidence_id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            competition_id TEXT,
            symbol TEXT NOT NULL,
            provider TEXT NOT NULL,
            observed_at_utc TEXT NOT NULL,
            quote_price REAL,
            update_mode TEXT,
            market_status TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            stored_at_utc TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_execution_evidence_symbol ON execution_evidence(symbol, observed_at_utc);
        """
    )


def save_execution_evidence(evidence: dict) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    validated = ExecutionEvidence.model_validate(evidence)
    payload = validated.model_dump()
    observed = payload.get("observed_at_utc")
    if hasattr(observed, "isoformat"):
        observed = observed.isoformat()
        payload["observed_at_utc"] = observed
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_execution_evidence_tables(conn)
        conn.execute(
            """INSERT OR REPLACE INTO execution_evidence
               (evidence_id,source,competition_id,symbol,provider,observed_at_utc,quote_price,update_mode,market_status,payload_json,stored_at_utc)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                payload["evidence_id"], payload["source"], payload.get("competition_id"),
                payload["symbol"], payload["provider"], observed, payload.get("quote_price"),
                payload.get("update_mode"), payload.get("market_status", "unknown"),
                json.dumps(payload, separators=(",", ":"), default=str), now,
            ),
        )


def get_execution_evidence(evidence_id: str) -> dict | None:
    init_db()
    with _LOCK, sqlite3.connect(DB_PATH) as conn:
        _ensure_execution_evidence_tables(conn)
        row = conn.execute(
            "SELECT payload_json FROM execution_evidence WHERE evidence_id=?",
            (evidence_id,),
        ).fetchone()
    return json.loads(row[0]) if row else None
