"""Tests for the GitHub Actions workflow policy checker."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import check_workflows

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


def run_checker_cli(root: Path, *, strict: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(CHECKER), "--root", str(root)]
    if strict:
        command.append("--strict")
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def run_checker(root: Path, *, strict: bool = False) -> SimpleNamespace:
    args = ["--root", str(root)]
    if strict:
        args.append("--strict")
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = check_workflows.main(args)
    return SimpleNamespace(returncode=rc, stdout=out.getvalue(), stderr=err.getvalue())


def write_workflow(root: Path, text: str, name: str = "ci.yml") -> SimpleNamespace:
    directory = root / ".github" / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(text, encoding="utf-8")
    return run_checker(root)


def test_repository_workflows_pass() -> None:
    result = run_checker_cli(ROOT, strict=True)

    assert result.returncode == 0, result.stderr
    assert "workflow file" in result.stdout


def test_cli_exits_one_on_policy_violation(tmp_path: Path) -> None:
    directory = tmp_path / ".github" / "workflows"
    directory.mkdir(parents=True)
    (directory / "bad.yml").write_text(
        VALID_WORKFLOW.replace(f"actions/checkout@{CHECKOUT_SHA}", "actions/checkout@v7"),
        encoding="utf-8",
    )
    result = run_checker_cli(tmp_path)
    assert result.returncode == 1
    assert "40-character commit SHA" in result.stderr


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


def test_yaml_workflow_extension_is_checked(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(f"actions/checkout@{CHECKOUT_SHA}", "actions/checkout@main")
    assert text != VALID_WORKFLOW

    result = write_workflow(tmp_path, text, name="ci.yaml")

    assert result.returncode == 1


def check_in_process(tmp_path: Path, text: str, name: str = "ci.yml") -> list[tuple[str, int, str]]:
    from scripts import check_workflows

    directory = tmp_path / ".github" / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return check_workflows.check_workflow(path, tmp_path)


def test_empty_permissions_mapping_passes(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("permissions:\n  contents: read", "permissions: {}")
    assert text != VALID_WORKFLOW
    assert check_in_process(tmp_path, text) == []


def test_read_all_permissions_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("permissions:\n  contents: read", "permissions: read-all")
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("read-all" in msg for _, _, msg in errors)


def test_job_read_all_and_sequence_permissions_fail(tmp_path: Path) -> None:
    for bad, needle in (("read-all", "read-all"), ("[write-all]", "must be a mapping")):
        text = VALID_WORKFLOW.replace(
            "    timeout-minutes: 5\n", f"    timeout-minutes: 5\n    permissions: {bad}\n"
        )
        assert text != VALID_WORKFLOW
        errors = check_in_process(tmp_path, text)
        assert any(needle in msg for _, _, msg in errors)


def test_sequence_permissions_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("permissions:\n  contents: read", "permissions: [write-all]")
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("must be a mapping" in msg for _, _, msg in errors)


def test_duplicate_yaml_keys_fail(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "permissions:\n  contents: read\n",
        "permissions:\n  contents: read\npermissions: write-all\n",
    )
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("duplicate YAML key 'permissions'" in msg for _, _, msg in errors)


def test_case_insensitive_duplicate_yaml_keys_fail(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "          persist-credentials: false\n",
        "          persist-credentials: false\n          Persist-Credentials: true\n",
    )
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("duplicate YAML key 'Persist-Credentials'" in msg for _, _, msg in errors)


def test_yaml_merge_key_fails(tmp_path: Path) -> None:
    text = (
        "name: Merge\n"
        "on: push\n"
        "permissions: {}\n"
        "x-bad: &bad\n"
        "  uses: evil/action@main\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-24.04\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - <<: *bad\n"
    )
    errors = check_in_process(tmp_path, text)
    assert any("merge key '<<'" in msg for _, _, msg in errors)


def test_cyclic_yaml_alias_fails_without_recursion_error(tmp_path: Path) -> None:
    text = (
        "name: Cycle\n"
        "on: push\n"
        "permissions: {}\n"
        "x-loop: &loop\n"
        "  self: *loop\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-24.04\n"
        "    timeout-minutes: 5\n"
        "    steps:\n"
        "      - run: echo ok\n"
    )
    errors = check_in_process(tmp_path, text)
    assert any("cyclic YAML alias" in msg for _, _, msg in errors)


def test_deep_alias_dag_completes_linearly(tmp_path: Path) -> None:
    lines = ["name: Dag", "on: push", "permissions: {}", "x-0: &a0 [1, 2]"]
    for i in range(1, 25):
        lines.append(f"x-{i}: &a{i} [*a{i - 1}, *a{i - 1}]")
    lines.extend(
        [
            "jobs:",
            "  test:",
            "    runs-on: ubuntu-24.04",
            "    timeout-minutes: 5",
            "    steps:",
            "      - run: echo ok",
        ]
    )
    assert check_in_process(tmp_path, "\n".join(lines) + "\n") == []


def test_case_insensitive_checkout_requires_persist_credentials(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace("actions/checkout@", "Actions/Checkout@").replace(
        "        with:\n          persist-credentials: false\n", ""
    )
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("persist-credentials: false" in msg for _, _, msg in errors)


def test_checkout_dot_subpath_and_invalid_segments_fail(tmp_path: Path) -> None:
    dot_checkout = VALID_WORKFLOW.replace(
        f"actions/checkout@{CHECKOUT_SHA}", f"actions/checkout/.@{CHECKOUT_SHA}"
    ).replace("        with:\n          persist-credentials: false\n", "")
    assert dot_checkout != VALID_WORKFLOW
    errors = check_in_process(tmp_path, dot_checkout)
    assert any("invalid owner or path segment" in msg for _, _, msg in errors)
    assert any("persist-credentials: false" in msg for _, _, msg in errors)

    rel_action = VALID_WORKFLOW.replace(
        f"actions/checkout@{CHECKOUT_SHA}", f"./local@{CHECKOUT_SHA}"
    )
    assert rel_action != VALID_WORKFLOW
    errors = check_in_process(tmp_path, rel_action)
    assert any("invalid owner or path segment" in msg for _, _, msg in errors)


def test_checkout_non_mapping_with_fails(tmp_path: Path) -> None:
    text = VALID_WORKFLOW.replace(
        "        with:\n          persist-credentials: false\n",
        "        with: [persist-credentials]\n",
    )
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("'with' must be a mapping" in msg for _, _, msg in errors)


@pytest.mark.parametrize("bad_name", ["", "name: null\n\n", "name: ~\n\n"])
def test_missing_or_null_workflow_name_fails(tmp_path: Path, bad_name: str) -> None:
    text = VALID_WORKFLOW.replace("name: Test\n\n", bad_name)
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("non-empty 'name'" in msg for _, _, msg in errors)


@pytest.mark.parametrize(
    ("bad_on", "needle"),
    [
        ("on: []\n", "must not be empty"),
        ("on: {}\n", "must not be empty"),
        ("on: null\n", "must not be empty"),
        ("on:\n  - [push]\n", "must be a scalar"),
    ],
)
def test_invalid_triggers_fail(tmp_path: Path, bad_on: str, needle: str) -> None:
    text = VALID_WORKFLOW.replace("on:\n  push:\n    branches:\n      - main\n", bad_on)
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any(needle in msg for _, _, msg in errors)


def test_empty_jobs_and_empty_steps_fail(tmp_path: Path) -> None:
    empty_jobs = "name: Empty\non: push\npermissions: {}\njobs: {}\n"
    assert any(
        "jobs must not be empty" in msg for _, _, msg in check_in_process(tmp_path, empty_jobs)
    )

    empty_steps = (
        "name: EmptySteps\non: push\npermissions: {}\njobs:\n  test:\n"
        "    runs-on: ubuntu-24.04\n    timeout-minutes: 5\n    steps: []\n"
    )
    assert any(
        "steps must not be empty" in msg for _, _, msg in check_in_process(tmp_path, empty_steps)
    )


@pytest.mark.parametrize("bad_timeout", ["1_0", "0", "361", '"10"', "010"])
def test_invalid_or_quoted_timeout_fails(tmp_path: Path, bad_timeout: str) -> None:
    text = VALID_WORKFLOW.replace("timeout-minutes: 5", f"timeout-minutes: {bad_timeout}")
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any("timeout-minutes" in msg for _, _, msg in errors)


@pytest.mark.parametrize(
    ("runner", "needle"),
    [
        ("self-hosted", "self-hosted"),
        ("ubuntu-latest", "pinned GitHub-hosted runner"),
        ("[self-hosted, linux]", "pinned GitHub-hosted runner"),
        ('"ubuntu-24.04 "', "pinned GitHub-hosted runner"),
    ],
)
def test_unpinned_or_self_hosted_runner_fails(tmp_path: Path, runner: str, needle: str) -> None:
    text = VALID_WORKFLOW.replace("runs-on: ubuntu-24.04", f"runs-on: {runner}")
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any(needle in msg for _, _, msg in errors)


def test_expression_or_non_scalar_run_fails_but_env_passes(tmp_path: Path) -> None:
    bad = VALID_WORKFLOW.replace("run: echo ok", "run: echo ${{ github.head_ref }}")
    assert bad != VALID_WORKFLOW
    errors = check_in_process(tmp_path, bad)
    assert any("${{ ... }}" in msg for _, _, msg in errors)

    non_scalar = VALID_WORKFLOW.replace("run: echo ok", "run: [echo, '${{ github.head_ref }}']")
    assert non_scalar != VALID_WORKFLOW
    errors = check_in_process(tmp_path, non_scalar)
    assert any("step 'run' must be a scalar" in msg for _, _, msg in errors)

    good = VALID_WORKFLOW.replace(
        "        run: echo ok",
        "        env:\n          REF: ${{ github.head_ref }}\n        run: printf '%s\\n' \"$REF\"",
    )
    assert good != VALID_WORKFLOW
    assert check_in_process(tmp_path, good) == []


def test_reusable_workflow_job_rules(tmp_path: Path) -> None:
    valid_reusable = (
        "name: Caller\n"
        "on: workflow_dispatch\n"
        "permissions: {}\n"
        "jobs:\n"
        "  call:\n"
        f"    uses: octo/repo/.github/workflows/ci.yml@{CHECKOUT_SHA}\n"
    )
    assert check_in_process(tmp_path, valid_reusable) == []

    unpinned = valid_reusable.replace(f"@{CHECKOUT_SHA}", "@main")
    assert any(
        "40-character commit SHA" in msg for _, _, msg in check_in_process(tmp_path, unpinned)
    )

    both = valid_reusable + "    steps:\n      - run: echo bad\n"
    assert any("cannot define steps" in msg for _, _, msg in check_in_process(tmp_path, both))

    pr_write = (
        valid_reusable.replace("on: workflow_dispatch", "on: pull_request")
        + "    permissions:\n      contents: write\n"
    )
    assert any(
        "pull_request workflows" in msg for _, _, msg in check_in_process(tmp_path, pr_write)
    )


@pytest.mark.parametrize(
    "event",
    [
        "pull_request",
        "pull_request_review",
        "pull_request_review_comment",
        "issue_comment",
        "workflow_run",
    ],
)
@pytest.mark.parametrize("scope", ["contents", "id-token", "attestations"])
def test_untrusted_events_forbid_dangerous_write_scopes(
    tmp_path: Path, event: str, scope: str
) -> None:
    text = VALID_WORKFLOW.replace(
        "on:\n  push:\n    branches:\n      - main\n", f"on: {event}\n"
    ).replace(
        "    timeout-minutes: 5\n",
        f"    timeout-minutes: 5\n    permissions:\n      {scope}: write\n",
    )
    assert text != VALID_WORKFLOW
    errors = check_in_process(tmp_path, text)
    assert any(f"{event} workflows" in msg for _, _, msg in errors)


@pytest.mark.parametrize("scope", ["pull-requests", "security-events"])
def test_pull_request_allows_safe_review_write_scopes(tmp_path: Path, scope: str) -> None:
    text = VALID_WORKFLOW.replace("  push:\n", "  pull_request:\n").replace(
        "    timeout-minutes: 5\n",
        f"    timeout-minutes: 5\n    permissions:\n      {scope}: write\n",
    )
    assert text != VALID_WORKFLOW
    assert check_in_process(tmp_path, text) == []


def test_ci_workflow_has_no_unhashed_pip_upgrade() -> None:
    ci_text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pip install --upgrade" not in ci_text
    assert "--require-hashes -r requirements-dev.txt" in ci_text
