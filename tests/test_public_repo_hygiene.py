from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DISALLOWED_TRACKED_NAMES = {
    ".env",
    "config.php",
}

DISALLOWED_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
    ".db",
    ".sqlite",
    ".sqlite3",
}

SECRET_PATTERNS = {
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    "github_fine_grained": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "telegram_bot_token": re.compile(r"\b\d{7,12}:[A-Za-z0-9_-]{25,}\b"),
}


def _iter_public_text_files():
    skip_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.name == Path(__file__).name:
            continue
        yield path


def test_public_repository_excludes_private_runtime_files():
    violations = []
    for path in _iter_public_text_files():
        rel = path.relative_to(ROOT)
        if path.name in DISALLOWED_TRACKED_NAMES or path.suffix.lower() in DISALLOWED_SUFFIXES:
            violations.append(str(rel))
        if any(part.lower() in {"private", "secrets", "credentials"} for part in rel.parts):
            violations.append(str(rel))
    assert not violations, f"Private/runtime files must not be tracked: {sorted(set(violations))}"


def test_public_repository_has_no_common_hardcoded_secret_shapes():
    findings = []
    for path in _iter_public_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}:{label}")
    assert not findings, f"Potential hard-coded secrets detected: {findings}"
