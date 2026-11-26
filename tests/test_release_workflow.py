"""Structural YAML contract tests for the release workflow ordering and safe trigger."""

from __future__ import annotations

import copy
import shlex
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def load_workflow() -> dict:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _strip_shell_comments(line: str) -> str:
    """Remove full-line and inline shell comments while respecting single/double quotes."""
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and not in_single:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif (
            ch == "#" and not in_single and not in_double and (idx == 0 or line[idx - 1].isspace())
        ):
            return line[:idx].rstrip()
    return line.rstrip()


def _active_shell_text(script: str) -> str:
    """Return active (comment-stripped) shell text joined across backslash continuations."""
    logical_lines: list[str] = []
    current = ""
    for raw_line in script.splitlines():
        cleaned = _strip_shell_comments(raw_line).strip()
        if not cleaned:
            if current:
                logical_lines.append(current)
                current = ""
            continue
        if cleaned.endswith("\\"):
            current += cleaned[:-1].rstrip() + " "
        else:
            current += cleaned
            logical_lines.append(current)
            current = ""
    if current:
        logical_lines.append(current)
    return "\n".join(logical_lines)


def _active_shell_tokens(script: str) -> list[str]:
    tokens: list[str] = []
    for line in _active_shell_text(script).splitlines():
        try:
            tokens.extend(shlex.split(line, comments=True))
        except ValueError:
            tokens.extend(line.split())
    return tokens


def _step_by_name(data: dict, name: str) -> dict:
    for step in data["jobs"]["release"]["steps"]:
        if isinstance(step, dict) and step.get("name") == name:
            return step
    raise AssertionError(f"release workflow is missing step {name!r}")


def assert_release_workflow_contract(data: dict) -> None:
    triggers = data.get("on", data.get(True))
    assert isinstance(triggers, dict) and set(triggers) == {"workflow_dispatch"}
    assert "tag" in triggers["workflow_dispatch"]["inputs"]

    assert data["concurrency"]["cancel-in-progress"] is False

    job = data["jobs"]["release"]
    assert job["if"] == "github.ref == 'refs/heads/main'"
    assert job["environment"]["name"] == "release"

    perms = job.get("permissions", {})
    assert perms.get("actions") == "read"
    assert perms.get("attestations") == "write"
    assert perms.get("checks") == "read"
    assert perms.get("contents") == "write"
    assert perms.get("id-token") == "write"

    names = [step.get("name", "") for step in job["steps"]]
    expected_order = [
        "Validate tag format",
        "Checkout full history",
        "Checkout release gate from main",
        "Verify signed tag",
        "Verify tag commit is on main",
        "Verify required check-runs",
        "Validate tag and extract release notes",
        "Build source archive and SHA-256 checksum",
        "Attest build provenance",
        "Stage Sigstore provenance bundle asset",
        "Create draft release with assets",
    ]
    positions = [names.index(step_name) for step_name in expected_order]
    assert positions == sorted(positions), f"unexpected step ordering: {names}"

    tag_checkout = _step_by_name(data, "Checkout full history")
    assert str(tag_checkout.get("uses", "")).startswith("actions/checkout@")
    assert tag_checkout.get("with", {}).get("ref") == "refs/tags/${{ inputs.tag }}"
    assert tag_checkout.get("with", {}).get("fetch-depth") == 0
    assert tag_checkout.get("with", {}).get("persist-credentials") is False

    gate_checkout = _step_by_name(data, "Checkout release gate from main")
    assert str(gate_checkout.get("uses", "")).startswith("actions/checkout@")
    assert gate_checkout.get("with", {}).get("ref") == "main"
    assert gate_checkout.get("with", {}).get("path") == "gate"
    assert gate_checkout.get("with", {}).get("persist-credentials") is False

    sig_run = _active_shell_text(str(_step_by_name(data, "Verify signed tag").get("run", "")))
    assert "gate/docs/release-signing/allowed_signers" in sig_run
    assert 'verify-tag -- "refs/tags/$TAG"' in sig_run

    checks_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Verify required check-runs").get("run", ""))
    )
    assert "gate/scripts/release_checks.py" in checks_tokens

    notes_run = _active_shell_text(
        str(_step_by_name(data, "Validate tag and extract release notes").get("run", ""))
    )
    notes_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Validate tag and extract release notes").get("run", ""))
    )
    assert 'git show "${TAG_COMMIT}:CHANGELOG.md"' in notes_run
    assert "gate/scripts/release_notes.py" in notes_tokens

    attest_step = _step_by_name(data, "Attest build provenance")
    assert str(attest_step.get("uses", "")).startswith("actions/attest-build-provenance@")
    assert (
        attest_step.get("with", {}).get("subject-path")
        == "dist/skills-hub-${{ inputs.tag }}.tar.gz"
    )

    bundle_run = _active_shell_text(
        str(_step_by_name(data, "Stage Sigstore provenance bundle asset").get("run", ""))
    )
    assert ".sigstore.json" in bundle_run

    create_run = _active_shell_text(
        str(_step_by_name(data, "Create draft release with assets").get("run", ""))
    )
    create_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Create draft release with assets").get("run", ""))
    )
    assert "--draft" in create_tokens
    assert "--verify-tag" in create_tokens
    assert any(token.endswith(".sigstore.json") for token in create_tokens)
    assert "args+=(--latest)" not in create_run


def test_release_workflow_structural_contract() -> None:
    assert_release_workflow_contract(load_workflow())


def test_comment_only_and_inline_comment_mutations_fail_contract() -> None:
    base = load_workflow()

    # 1. Full-line commenting out --draft must fail.
    no_draft = copy.deepcopy(base)
    create_step = _step_by_name(no_draft, "Create draft release with assets")
    create_step["run"] = create_step["run"].replace("--draft", "# --draft")
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(no_draft)

    # 2. Inline-commenting gate/scripts/release_notes.py must fail.
    inline_notes = copy.deepcopy(base)
    notes_step = _step_by_name(inline_notes, "Validate tag and extract release notes")
    notes_step["run"] = notes_step["run"].replace(
        "python3 gate/scripts/release_notes.py \\",
        "python3 scripts/release_notes.py # gate/scripts/release_notes.py",
    )
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(inline_notes)

    # 3. Inline-commenting --draft on the gh release create line must fail.
    inline_draft = copy.deepcopy(base)
    c_step = _step_by_name(inline_draft, "Create draft release with assets")
    c_step["run"] = (
        c_step["run"]
        .replace("--draft\n", "")
        .replace('gh release create "$TAG"', 'gh release create "$TAG" # --draft')
    )
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(inline_draft)

    # 4. Dropping attest-build-provenance uses: must fail even if mentioned in comments.
    no_attest = copy.deepcopy(base)
    attest_step = _step_by_name(no_attest, "Attest build provenance")
    attest_step.pop("uses")
    attest_step["run"] = "# actions/attest-build-provenance@deadbeef\necho skipped"
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(no_attest)
