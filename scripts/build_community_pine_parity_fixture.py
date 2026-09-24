#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.community_indicator_signals import indicator_signal_series
from app.research_dataset import bars_from_tradingview_ohlcv


PROFILES: dict[str, dict[str, dict]] = {
    "CAPITALCOM:BTCUSD": {
        "rsi_kernel_optimized_flux": {
            "rsi_period": 21,
            "pivot_length": 12,
            "bandwidth": 6.0,
            "min_samples": 12,
            "dominance_ratio": 1.35,
        },
    },
    "CAPITALCOM:DOGEUSD": {
        "range_filter_guikroth": {
            "sampling_period": 100,
            "range_multiplier": 3.0,
        },
        "schaff_trend_cycle": {
            "cycle_length": 12,
            "fast_length": 26,
            "slow_length": 50,
            "smoothing": 0.5,
        },
    },
    "CAPITALCOM:ETHUSD": {
        "ssl_hybrid": {
            "baseline_length": 60,
            "ssl_length": 15,
        },
    },
    "CAPITALCOM:EURUSD": {
        "trendilo": {
            "smoothing": 1,
            "lookback": 50,
            "alma_offset": 0.85,
            "alma_sigma": 6.0,
            "band_multiplier": 1.0,
        },
    },
    "CAPITALCOM:NAS100": {
        "halftrend_everget": {
            "amplitude": 5,
        },
    },
    "CAPITALCOM:USDZAR": {
        "lorentzian_classification": {},
        "nadaraya_watson_endpoint_nonrepaint": {
            "window": 500,
            "bandwidth": 8.0,
            "multiplier": 3.0,
            "deviation_length": 499,
        },
        "alphatrend": {
            "period": 20,
            "coefficient": 1.0,
        },
        "supertrend_kivanc": {
            "atr_period": 14,
            "multiplier": 3.0,
        },
        "ut_bot_alerts": {
            "atr_period": 14,
            "key_value": 1.5,
        },
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    meta_path = args.input_dir / "meta.json"
    bars_path = args.input_dir / "15m.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    raw = bars_path.read_bytes()
    payload = json.loads(raw)
    symbol = str(meta["symbol"])
    profile = PROFILES.get(symbol)
    if not profile:
        raise SystemExit(f"no parity profile for {symbol}")

    bars = bars_from_tradingview_ohlcv(payload)
    components = {}
    for component_id, parameters in profile.items():
        signals = indicator_signal_series(component_id, bars, parameters=parameters)
        events = [
            {
                "index": int(index),
                "time": bars[index].timestamp.isoformat().replace("+00:00", "Z"),
                "value": float(value),
            }
            for index, value in sorted(signals.items())
        ]
        components[component_id] = {
            "parameters": parameters,
            "event_count": len(events),
            "events": events,
        }

    result = {
        "schema": "stc-community-pine-parity-fixture-v1",
        "symbol": symbol,
        "timeframe": "15",
        "bar_count": len(bars),
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "first_bar_utc": bars[0].timestamp.isoformat().replace("+00:00", "Z"),
        "last_bar_utc": bars[-1].timestamp.isoformat().replace("+00:00", "Z"),
        "components": components,
        "live_authority": False,
        "purpose": "Python reference stream for Pine parity verification before any live weight promotion.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "STC_PARITY_FIXTURE="
        + json.dumps(
            {
                "symbol": symbol,
                "bar_count": len(bars),
                "dataset_sha256": result["dataset_sha256"],
                "component_event_counts": {
                    key: value["event_count"] for key, value in components.items()
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
