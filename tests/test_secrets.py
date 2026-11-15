"""Tests for secret-related .gitignore coverage in a temporary repository."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_IGNORED = [
    ".env",
    ".env.local",
    ".env.production",
    "config/.env",
    "private.pem",
    "server.key",
    "certificate.p12",
    "secrets/database.env",
    "credentials",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
    ".opencode/config.json",
    ".claude/settings.json",
    ".agents/skills/example.md",
]

EXISTING_IGNORED = [
    "node_modules/package/index.js",
    ".venv/bin/python",
    ".ruff_cache/data",
    ".pytest_cache/state",
    ".playwright-cli/trace.zip",
    "__pycache__/module.pyc",
]


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    """Create a throwaway repository with this project's .gitignore."""
    shutil.copyfile(ROOT / ".gitignore", tmp_path / ".gitignore")
    subprocess.run(
        ["git", "init", "--quiet", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return tmp_path


def check_ignore(repo: Path, path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "--no-index", "--quiet", "--", path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise AssertionError(f"git check-ignore failed for {path}: {result.stderr}")
    return result.returncode == 0


def create_placeholder(repo: Path, path: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("placeholder\n", encoding="utf-8")


@pytest.mark.parametrize("path", REQUIRED_IGNORED)
def test_secret_path_is_ignored(temp_repo: Path, path: str) -> None:
    create_placeholder(temp_repo, path)

    assert check_ignore(temp_repo, path)


@pytest.mark.parametrize("path", EXISTING_IGNORED)
def test_existing_ignore_patterns_are_kept(temp_repo: Path, path: str) -> None:
    create_placeholder(temp_repo, path)

    assert check_ignore(temp_repo, path)


def test_env_example_is_allowed(temp_repo: Path) -> None:
    create_placeholder(temp_repo, ".env.example")

    assert not check_ignore(temp_repo, ".env.example")


def test_git_add_does_not_stage_secret_files(temp_repo: Path) -> None:
    for path in REQUIRED_IGNORED:
        create_placeholder(temp_repo, path)
    create_placeholder(temp_repo, ".env.example")
    create_placeholder(temp_repo, "safe.txt")

    subprocess.run(
        ["git", "-C", str(temp_repo), "add", "--all"],
        check=True,
        capture_output=True,
        text=True,
    )
    staged = set(
        subprocess.run(
            ["git", "-C", str(temp_repo), "diff", "--cached", "--name-only"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )

    assert {".env.example", "safe.txt"} <= staged
    assert not staged.intersection(REQUIRED_IGNORED)


def test_secret_scan_pins_rules_and_disables_inline_allow() -> None:
    workflow = (ROOT / ".github" / "workflows" / "secret-scan.yml").read_text(
        encoding="utf-8"
    )
    assert "--config" in workflow
    assert "--gitleaks-ignore-path" in workflow
    assert "--ignore-gitleaks-allow" in workflow
