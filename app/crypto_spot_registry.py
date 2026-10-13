"""Fail-closed, immutable registry for paper-only Binance Spot research.

The registry is research metadata, not trading authorization. Runtime callers
must never infer leveraged, futures, short, or real-money permissions from it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1] / "research_inputs" / "CRYPTO_SPOT_ASSET_REGISTRY.json"
)


@dataclass(frozen=True)
class CryptoSpotAsset:
    asset: str
    pair: str
    tier: str
    status: str
    priority: int


@dataclass(frozen=True)
class CryptoSpotRegistry:
    version: int
    mode: str
    quote_asset: str
    constraints: dict[str, bool]
    research_order: tuple[str, ...]
    assets: tuple[CryptoSpotAsset, ...]
    data_policy: dict[str, Any]

    @property
    def research_assets(self) -> tuple[CryptoSpotAsset, ...]:
        return tuple(self.by_asset(name) for name in self.research_order)

    def by_asset(self, asset: str) -> CryptoSpotAsset:
        for item in self.assets:
            if item.asset == asset:
                return item
        raise KeyError(f"Asset not registered for Spot research: {asset!r}")

    def by_pair(self, pair: str) -> CryptoSpotAsset:
        for item in self.assets:
            if item.pair == pair:
                return item
        raise KeyError(f"Pair not registered for Spot research: {pair!r}")


def load_crypto_spot_registry(path: str | Path | None = None) -> CryptoSpotRegistry:
    source = Path(path) if path is not None else _DEFAULT_REGISTRY_PATH
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Spot registry must be a JSON object")

    if data.get("mode") != "SPOT_ONLY":
        raise ValueError("Spot registry cannot authorize other instrument modes")
    constraints = data.get("constraints")
    if not isinstance(constraints, dict) or any(
        constraints.get(key) is not False
        for key in ("futures", "leverage", "shorting", "real_money_authorized")
    ):
        raise ValueError("Spot research must forbid futures, leverage, shorting and real money")

    quote = data.get("quote_asset")
    if quote != "USDT":
        raise ValueError("Unexpected or unverified Spot quote currency")

    raw_assets = data.get("assets")
    if not isinstance(raw_assets, list) or not raw_assets:
        raise ValueError("Spot asset registry is empty or malformed")
    assets: list[CryptoSpotAsset] = []
    names: set[str] = set()
    pairs: set[str] = set()
    priorities: set[int] = set()
    for raw in raw_assets:
        if not isinstance(raw, dict):
            raise ValueError("Malformed Spot asset record")
        asset = raw.get("asset")
        pair = raw.get("pair")
        status = raw.get("status")
        tier = raw.get("tier")
        priority = raw.get("priority")
        if (
            not isinstance(asset, str)
            or not asset.isascii()
            or not asset.isalnum()
            or asset != asset.upper()
            or pair != asset + quote
            or status not in ("RESEARCH", "QUEUED")
            or tier not in ("CORE", "HIGH_VOLATILITY")
            or type(priority) is not int
            or priority < 1
            or asset in names
            or pair in pairs
            or priority in priorities
        ):
            raise ValueError(f"Invalid, duplicate or unauthorized Spot asset: {asset!r}")
        names.add(asset)
        pairs.add(pair)
        priorities.add(priority)
        assets.append(CryptoSpotAsset(asset, pair, tier, status, priority))

    raw_order = data.get("research_order")
    if not isinstance(raw_order, list) or any(not isinstance(item, str) for item in raw_order):
        raise ValueError("Spot research_order must be a list of asset codes")
    if len(raw_order) != len(set(raw_order)):
        raise ValueError("Duplicate asset in Spot research_order")
    expected = {item.asset for item in assets if item.status == "RESEARCH"}
    if set(raw_order) != expected:
        raise ValueError("Spot research_order differs from registered RESEARCH assets")

    policy = data.get("data_policy")
    if not isinstance(policy, dict):
        raise ValueError("Missing Spot market-data policy")
    if policy.get("closed_bars_only") is not True or policy.get("exact_pair_required") is not True:
        raise ValueError("Spot data validation requires exact closed bars and pairs")
    if policy.get("primary_provider") != "BINANCE_SPOT_PUBLIC":
        raise ValueError("Unexpected Spot data provider")
    intervals = policy.get("required_intervals")
    if not isinstance(intervals, list) or not intervals or not all(
        isinstance(value, str) and value in {"15m", "1h", "4h", "1d"}
        for value in intervals
    ):
        raise ValueError("Invalid mandatory Spot intervals")
    if type(policy.get("min_bars_per_interval")) is not int or policy["min_bars_per_interval"] < 900:
        raise ValueError("Insufficient minimum Spot data-history requirement")

    version = data.get("version")
    if type(version) is not int or version < 1:
        raise ValueError("Invalid Spot registry version")
    return CryptoSpotRegistry(
        version=version,
        mode="SPOT_ONLY",
        quote_asset=quote,
        constraints=dict(constraints),
        research_order=tuple(raw_order),
        assets=tuple(assets),
        data_policy=dict(policy),
    )
