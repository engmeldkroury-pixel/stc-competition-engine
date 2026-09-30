from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.crypto_spot_registry import CryptoSpotRegistry, load_crypto_spot_registry


@dataclass(frozen=True)
class CryptoResearchJob:
    asset: str
    pair: str
    intervals: tuple[str, ...]
    closed_bars_only: bool
    provider: str


def build_crypto_research_job(
    asset: str,
    registry: CryptoSpotRegistry | None = None,
) -> CryptoResearchJob:
    registry = registry or load_crypto_spot_registry()
    item = registry.by_asset(asset)
    policy: dict[str, Any] = registry.data_policy

    return CryptoResearchJob(
        asset=item.asset,
        pair=item.pair,
        intervals=tuple(policy["required_intervals"]),
        closed_bars_only=bool(policy["closed_bars_only"]),
        provider=str(policy["primary_provider"]),
    )
