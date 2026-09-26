from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .competition_profiles import (
    COMPETITION_MODE_IDS,
    COMPETITION_OPPORTUNITY_QUALITY_FLOOR,
    STRICT_QUALITY_FLOOR,
    get_profile,
)


UTC = timezone.utc


@dataclass(frozen=True)
class CompetitionPace:
    competition_id: str
    phase: str
    hours_remaining: float
    time_remaining_fraction: float
    qualifying_days_done: int
    qualifying_days_required: int
    qualifying_days_remaining: int
    current_rank: int | None
    prize_cutoff_rank: int | None
    size_band: str
    scan_mode: str
    quality_floor: str
    note: str


def competition_pace(
    competition_id: str,
    *,
    now_utc: datetime,
    qualifying_days_done: int,
    realized_pnl: float,
    current_rank: int | None = None,
    prize_cutoff_rank: int | None = None,
) -> CompetitionPace:
    profile = get_profile(competition_id)
    now = now_utc.astimezone(UTC)
    total_seconds = max(1.0, (profile.end_utc - profile.start_utc).total_seconds())
    remaining_seconds = max(0.0, (profile.end_utc - now).total_seconds())
    fraction = min(1.0, remaining_seconds / total_seconds)
    hours = remaining_seconds / 3600.0
    q_remaining = max(0, profile.min_trading_days - qualifying_days_done)

    in_prize_zone = (
        current_rank is not None
        and prize_cutoff_rank is not None
        and current_rank <= prize_cutoff_rank
    )

    if remaining_seconds <= 0:
        phase = "ENDED"
        size_band = "NONE"
        scan_mode = "STOP"
        note = "Competition window has ended."
    elif q_remaining > 0 and fraction <= 0.40:
        phase = "QUALIFICATION_URGENT"
        size_band = "LOW_TO_NORMAL"
        scan_mode = "BROADEN_UNIVERSE_KEEP_QUALITY"
        note = "Qualification days are still missing; do not lower the active competition quality floor."
    elif in_prize_zone and fraction <= 0.25:
        phase = "PROTECT_SCORE"
        size_band = "LOW"
        scan_mode = "TOP_SETUPS_ONLY"
        note = "Protect realized score late in the competition; avoid unnecessary turnover."
    elif (
        current_rank is not None
        and prize_cutoff_rank is not None
        and current_rank > prize_cutoff_rank
        and fraction <= 0.35
    ):
        phase = "CATCH_UP"
        size_band = "NORMAL_TO_UPPER_ALLOWED"
        scan_mode = "BROADEN_UNIVERSE_KEEP_QUALITY"
        note = (
            "Behind the target zone late in the event: scan more symbols and sessions, "
            "but keep the same active competition quality floor and all official/risk caps."
        )
    elif realized_pnl > 0 and fraction <= 0.15:
        phase = "FINAL_WINDOW"
        size_band = "LOW_TO_NORMAL"
        scan_mode = "TOP_SETUPS_ONLY"
        note = "Final window: prioritize score preservation and only exceptional qualified setups."
    else:
        phase = "BUILD_SCORE"
        size_band = "NORMAL"
        scan_mode = "NORMAL_UNIVERSE"
        note = "Build realized score with qualified setups while preserving qualification and risk limits."

    quality_floor = (
        f"COMPETITION_OPPORTUNITY_{COMPETITION_OPPORTUNITY_QUALITY_FLOOR}"
        if competition_id in COMPETITION_MODE_IDS
        else f"A_PLUS_{STRICT_QUALITY_FLOOR}"
    )

    return CompetitionPace(
        competition_id=competition_id,
        phase=phase,
        hours_remaining=hours,
        time_remaining_fraction=fraction,
        qualifying_days_done=qualifying_days_done,
        qualifying_days_required=profile.min_trading_days,
        qualifying_days_remaining=q_remaining,
        current_rank=current_rank,
        prize_cutoff_rank=prize_cutoff_rank,
        size_band=size_band,
        scan_mode=scan_mode,
        quality_floor=quality_floor,
        note=note,
    )
