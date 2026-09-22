import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    assert '"research_inputs/**"' in text
    assert "run_strategy_research_dir.py" in text
    assert "actions/upload-artifact@v4" in text
    assert "print_calibration_candidate.py" in text
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
