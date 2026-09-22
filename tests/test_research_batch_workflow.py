import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_candidate_printer():
    path = ROOT / "scripts" / "print_calibration_candidate.py"
    spec = importlib.util.spec_from_file_location("stc_candidate_printer", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_runner():
    path = ROOT / "scripts" / "run_strategy_research_dir.py"
    spec = importlib.util.spec_from_file_location("stc_research_dir_runner", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _series():
    return {
        "bars": [
            {"t": 1700000000, "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 10}
        ]
    }


def test_split_directory_loader_requires_all_exact_provider_series(tmp_path):
    runner = _load_runner()
    target = tmp_path / "xau"
    target.mkdir()
    (target / "meta.json").write_text(
        json.dumps({"symbol": "CAPITALCOM:XAUUSD"}),
        encoding="utf-8",
    )
    for filename in ("15m.json", "1h.json", "4h.json", "1D.json"):
        (target / filename).write_text(json.dumps(_series()), encoding="utf-8")

    payload = runner.load_series_dir(target)
    assert payload["symbol"] == "CAPITALCOM:XAUUSD"
    assert set(payload["series"]) == {"15m", "1h", "4h", "1D"}


def test_research_workflow_is_isolated_to_research_branches_and_inputs():
    text = (ROOT / ".github" / "workflows" / "stc-research.yml").read_text(encoding="utf-8")
    assert '"research/**"' in text
    assert '"research_inputs/READY"' in text
    assert "run_strategy_research_dir.py" in text
    assert "actions/upload-artifact@v4" in text
    assert "print_calibration_candidate.py" in text
    assert "STC_TIMEFRAME_DIAGNOSTIC=" in text
    assert "timeout-minutes: 30" in text
    assert "contents: read" in text
    assert "STC_OWNER_TOKEN" not in text
    assert "HOSTINGER" not in text.upper()



def test_research_scripts_are_directly_invocable_from_repo_root():
    import subprocess
    import sys

    for script in (
        "scripts/run_strategy_research_dir.py",
        "scripts/run_strategy_research.py",
        "scripts/update_calibration_registry.py",
    ):
        proc = subprocess.run(
            [sys.executable, script, "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr



def test_split_directory_loader_reads_optional_short_timeframes(tmp_path):
    runner = _load_runner()
    target = tmp_path / "xau-short"
    target.mkdir()
    (target / "meta.json").write_text(
        json.dumps({"symbol": "CAPITALCOM:XAUUSD"}),
        encoding="utf-8",
    )
    for filename in ("15m.json", "1h.json", "4h.json", "1D.json", "5m.json", "30m.json"):
        (target / filename).write_text(json.dumps(_series()), encoding="utf-8")

    payload = runner.load_series_dir(target)
    assert set(payload["series"]) == {"5m", "15m", "30m", "1h", "4h", "1D"}



def test_calibration_candidate_defaults_to_live_entry_report():
    printer = _load_candidate_printer()
    base = {
        "status": "VALIDATED",
        "robust_score": 60.0,
        "setup_probability": {
            "status": "CALIBRATED",
            "sample_size": 60,
            "estimated_win_probability": 0.60,
            "confidence_low": 0.50,
            "confidence_high": 0.70,
        },
        "test_expectancy_r": 0.20,
        "forward_expectancy_r": 0.10,
        "test_profit_factor": 1.40,
        "forward_profit_factor": 1.20,
        "feature_participation_pct": {"bos": 60.0, "relative_volume": 40.0},
    }
    result = {
        "symbol": "CAPITALCOM:XAUUSD",
        "derived_timeframe_end_utc": {
            "15": "2026-09-22T05:00:00Z",
            "240": "2026-09-22T04:00:00Z",
        },
        "research_report": {
            **base,
            "selected_strategy": "breakout_expansion",
            "selected_timeframe": "240",
        },
        "live_entry_research_report": {
            **base,
            "selected_strategy": "trend_pullback",
            "selected_timeframe": "15",
        },
    }
    candidate = printer.build_candidate(result)
    assert candidate["timeframe"] == "15"
    assert candidate["strategy_id"] == "trend_pullback"



def test_split_directory_loader_supports_matrix_only_screening_mode(tmp_path):
    runner = _load_runner()
    target = tmp_path / "screen"
    target.mkdir()
    (target / "meta.json").write_text(
        json.dumps({
            "symbol": "CAPITALCOM:EURUSD",
            "research_mode": "matrix_only",
        }),
        encoding="utf-8",
    )
    for filename in ("15m.json", "1h.json", "4h.json", "1D.json"):
        (target / filename).write_text(json.dumps(_series()), encoding="utf-8")
    payload = runner.load_series_dir(target)
    assert payload["research_mode"] == "matrix_only"



def test_research_workflow_prints_feature_participation():
    text = (ROOT / ".github" / "workflows" / "stc-research.yml").read_text(encoding="utf-8")
    assert "STC_FEATURE_PARTICIPATION=" in text
    assert "feature_participation_pct" in text
    assert '"live_entry_research_report"' in text
    assert '"research_report"' in text



def test_research_workflow_waits_for_explicit_ready_marker():
    text = (ROOT / ".github" / "workflows" / "stc-research.yml").read_text(encoding="utf-8")
    assert '"research_inputs/READY"' in text
    assert '"research_inputs/**"' not in text



def test_research_runner_records_engine_commit_provenance():
    text = (ROOT / "scripts" / "run_strategy_research_dir.py").read_text(encoding="utf-8")
    assert 'result["research_engine_git_sha"] = os.getenv("GITHUB_SHA")' in text
    assert 'result["research_engine_ref"] = os.getenv("GITHUB_REF_NAME")' in text
