import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_research_cli_can_run_directly_from_repo_root():
    result = subprocess.run(
        [sys.executable, "scripts/run_strategy_research.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Run STC no-lookahead strategy research" in result.stdout


def test_calibration_registry_cli_can_run_directly_from_repo_root():
    result = subprocess.run(
        [sys.executable, "scripts/update_calibration_registry.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Promote a validated STC research output" in result.stdout
