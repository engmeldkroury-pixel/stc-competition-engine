"""Bounded, authenticated-inbox research report. No write operations."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib

from .approval import timeframe_duration_minutes
from .cloud_approval import _validate_record
from .outcome_attribution import (VERSION, build_outcome_seed, canonical, evaluate_outcome,
                                 iso, summarize_outcomes, utc, validate_seed)


def report_from_inbox(inbox: dict, *, as_of: datetime, horizon_bars: int = 32,
                      cost_r: float = 0.02, requested_limit: int | None = None) -> dict:
    """Existing immutable envelope is used; never re-run historical live scoring.

    Legacy geometry is explicitly reconstructed under today's frozen v1 rule.
    Unknown historical gate diagnostics remain UNKNOWN. Bounded inbox coverage
    is not a complete historical export, even when the server returns < limit.
    """
    if inbox.get("ok") is not True or not isinstance(inbox.get("events"), list):
        raise ValueError("invalid_inbox_contract")
    as_of = utc(as_of)
    errors = Counter()
    records, market_bars, outcomes = [], [], []
    ids = defaultdict(list)
    for row in inbox["events"]:
        if not isinstance(row, dict):
            errors["invalid_row"] += 1
        else:
            ids[str(row.get("event_id", ""))].append(row)
    duplicates = 0
    for _, versions in sorted(ids.items()):
        if len({canonical(v) for v in versions}) > 1:
            errors["conflicting_event_duplicates"] += len(versions)
            continue
        duplicates += len(versions) - 1
        row = versions[0]
        try:
            result, receipt, payload = _validate_record(row)
            decision = result["decision"]
            if decision.get("action") != "signal_created":
                continue
            minutes = timeframe_duration_minutes(str(payload.get("timeframe", "")))
            if not minutes:
                raise ValueError("unsupported_timeframe")
            opened = utc(payload["time"])
            if opened + timedelta(minutes=minutes) > as_of:
                errors["future_or_unclosed_source_bar"] += 1
                continue
            signal, envelope = decision["signal"], decision["approval_envelope"]
            expected_id = "bridge-" + hashlib.sha256(row["event_id"].encode()).hexdigest()[:32]
            if signal.get("signal_id") != expected_id or receipt.get("signal_id") != expected_id:
                raise ValueError("signal_identity_mismatch")
            for evidence in (signal, envelope):
                if any(evidence.get(k) != payload.get(k) for k in ("competition_id", "symbol")):
                    raise ValueError("target_identity_mismatch")
            market_bars.append({"competition_id": payload["competition_id"], "symbol": payload["symbol"],
                                "timeframe_minutes": minutes, "time": payload["time"],
                                **{k: payload[k] for k in ("open", "high", "low", "close")}})
            seed = decision.get("research_outcome_seed")
            if seed is not None:
                validate_seed(seed)
                if seed["event_id"] != row["event_id"] or any(seed[k] != payload[k] for k in ("competition_id", "symbol")) or utc(seed["source_open"]) != opened or seed["timeframe_minutes"] != minutes:
                    raise ValueError("seed_source_identity_mismatch")
                records.append(seed)
            else:
                seed = build_outcome_seed(row["event_id"], payload, signal, envelope,
                                          provenance="LEGACY_RECONSTRUCTED_GEOMETRY")
                if seed:
                    records.append(seed)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            # Never include raw upstream response bodies or credentials in logs.
            reason = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
            errors[reason[:100]] += 1
    for seed in sorted(records, key=lambda x: (x["available_at"], x["event_id"])):
        try:
            outcomes.append(evaluate_outcome(seed, market_bars, as_of=as_of,
                                             horizon_bars=horizon_bars, cost_r=cost_r))
        except (ValueError, KeyError, TypeError) as exc:
            reason = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
            errors[reason[:100]] += 1
    coverage = {}
    for bar in market_bars:
        key = f'{bar["competition_id"]}|{bar["symbol"]}|{bar["timeframe_minutes"]}m'
        coverage.setdefault(key, set()).add(iso(utc(bar["time"])))
    return {
        "version": VERSION, "as_of": iso(as_of), "research_only": True,
        "execution": "none", "live_authorized": False,
        "source_scope": "BOUNDED_INBOX_NOT_COMPLETE_HISTORY", "requested_limit": requested_limit,
        "source_rows": len(inbox["events"]), "exact_duplicate_rows_ignored": duplicates,
        "quarantine_counts": dict(sorted(errors.items())),
        "coverage": {key: {"unique_bars": len(times), "first_open": min(times), "last_open": max(times)} for key, times in sorted(coverage.items())},
        "input_sha256": hashlib.sha256(canonical(inbox).encode()).hexdigest(),
        "summary": summarize_outcomes(outcomes), "outcomes": outcomes,
    }
