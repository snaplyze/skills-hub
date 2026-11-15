"""Tests for the GitHub Actions workflow policy checker."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_workflows.py"
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"

VALID_WORKFLOW = f"""\
name: Test

on:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  test:
    name: test
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - name: Checkout
        uses: actions/checkout@{CHECKOUT_SHA} # v7.0.1
        with:
          persist-credentials: false
      - name: Run
        run: echo ok
"""


def run_checker(root: Path, *, strict: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(CHECKER), "--root", str(root)]
    if strict:
        command.append("--strict")
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def write_workflow(root: Path, text: str, name: str = "ci.yml") -> subprocess.CompletedProcess[str]:
    directory = root / ".github" / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(text, encoding="utf-8")
    return run_checker(root)


def test_repository_workflows_pass() -> None:
    result = run_checker(ROOT, strict=True)

    assert result.returncode == 0, result.stderr
    assert "workflow file" in result.stdout


def test_valid_workflow_passes(tmp_path: Path) -> None:
    result = write_workflow(tmp_path, VALID_WORKFLOW)

    assert result.returncode == 0, result.stderr


def test_unpinned_action_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(f"actions/checkout@{CHECKOUT_SHA}", "actions/checkout@v7")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "40-character commit SHA" in result.stderr


def test_missing_job_timeout_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("    timeout-minutes: 5\n", "")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "timeout-minutes" in result.stderr


def test_invalid_timeout_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("timeout-minutes: 5", 'timeout-minutes: "forever"')
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "timeout-minutes" in result.stderr


def test_checkout_persist_credentials_true_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("persist-credentials: false", "persist-credentials: true")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "persist-credentials: false" in result.stderr


def test_checkout_missing_persist_credentials_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("        with:\n          persist-credentials: false\n", "")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "persist-credentials: false" in result.stderr


def test_unknown_workflow_event_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "on:\n  push:\n    branches:\n      - main\n",
        "on:\n  push:\n    branches:\n      - main\n  repository_ruleset:\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "unsupported workflow event" in result.stderr


def test_pull_request_target_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "on:\n  push:\n    branches:\n      - main\n",
        "on:\n  push:\n    branches:\n      - main\n  pull_request_target:\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "pull_request_target" in result.stderr


def test_write_all_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("permissions:\n  contents: read", "permissions: write-all")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "write-all" in result.stderr


def test_missing_workflow_permissions_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("permissions:\n  contents: read\n\n", "")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "top-level permissions" in result.stderr


def test_workflow_level_pull_requests_write_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "permissions:\n  contents: read\n",
        "permissions:\n  contents: read\n  pull-requests: write\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "job scope" in result.stderr


def test_job_level_pull_requests_write_passes(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "    timeout-minutes: 5\n",
        "    timeout-minutes: 5\n"
        "    permissions:\n"
        "      contents: read\n"
        "      pull-requests: write\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 0, result.stderr


def test_job_level_attestations_write_passes(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "    timeout-minutes: 5\n",
        "    timeout-minutes: 5\n"
        "    permissions:\n"
        "      contents: read\n"
        "      attestations: write\n"
        "      id-token: write\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 0, result.stderr


def test_workflow_level_attestations_write_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "permissions:\n  contents: read\n",
        "permissions:\n  contents: read\n  attestations: write\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "job scope" in result.stderr


def test_unapproved_job_write_scope_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "    timeout-minutes: 5\n",
        "    timeout-minutes: 5\n    permissions:\n      packages: write\n",
    )
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text)

    assert result.returncode == 1
    assert "packages: write" in result.stderr


def test_invalid_yaml_fails(tmp_path: Path) -> None:
    result = write_workflow(tmp_path, "name: [unterminated\n")

    assert result.returncode == 1
    assert "invalid YAML" in result.stderr


def test_no_workflows_fails(tmp_path: Path) -> None:
    result = run_checker(tmp_path)

    assert result.returncode == 1
    assert "no workflows found" in result.stderr


def test_missing_required_workflow_fails(tmp_path: Path) -> None:
    destination = tmp_path / ".github" / "workflows"
    shutil.copytree(ROOT / ".github" / "workflows", destination)
    (destination / "ci.yml").unlink()

    result = run_checker(tmp_path, strict=True)

    assert result.returncode == 1
    assert "required workflow file is missing" in result.stderr


@pytest.mark.parametrize("suffix", [".yml", ".yaml"])
def test_both_workflow_extensions_are_checked(tmp_path: Path, suffix: str) -> None:
    text = VALID_WORKFLOW.replace(f"actions/checkout@{CHECKOUT_SHA}", "actions/checkout@main")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text, name=f"ci{suffix}")

    assert result.returncode == 1
