from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.crypto_spot_registry import CryptoSpotRegistry


@dataclass(frozen=True)
class BenchmarkRequest:
    pair: str
    intervals: tuple[str, ...] = ("15m", "1h", "4h", "1d")
    closed_bars_only: bool = True


@dataclass(frozen=True)
class BenchmarkResult:
    pair: str
    status: str
    metrics: dict[str, Any]


def validate_request(registry: CryptoSpotRegistry, request: BenchmarkRequest) -> None:
    registry.by_pair(request.pair)
    if not request.closed_bars_only:
        raise ValueError("Benchmark requires closed bars only")


def run_benchmark(
    registry: CryptoSpotRegistry,
    request: BenchmarkRequest,
    bars: list[dict[str, Any]],
) -> BenchmarkResult:
    validate_request(registry, request)
    return BenchmarkResult(
        pair=request.pair.upper(),
        status="DATA_READY",
        metrics={"bars": len(bars), "intervals": list(request.intervals)},
    )
