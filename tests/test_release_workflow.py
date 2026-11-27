"""Structural YAML contract tests for the release workflow ordering and safe trigger."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from tests._helpers import active_shell_text as _active_shell_text
from tests._helpers import active_shell_tokens as _active_shell_tokens

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def load_workflow() -> dict:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


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

    validate_run = _active_shell_text(
        str(_step_by_name(data, "Validate tag format").get("run", ""))
    )
    assert "^v(0|[1-9][0-9]*)\\." in validate_run
    assert "+" not in validate_run

    tag_checkout = _step_by_name(data, "Checkout full history")
    assert str(tag_checkout.get("uses", "")).startswith("actions/checkout@")
    assert tag_checkout.get("with", {}).get("ref") == "refs/tags/${{ inputs.tag }}"
    assert tag_checkout.get("with", {}).get("fetch-depth") == 0
    assert tag_checkout.get("with", {}).get("persist-credentials") is False

    gate_checkout = _step_by_name(data, "Checkout release gate from main")
    assert str(gate_checkout.get("uses", "")).startswith("actions/checkout@")
    assert gate_checkout.get("with", {}).get("ref") == "${{ github.sha }}"
    assert gate_checkout.get("with", {}).get("path") == "gate"
    assert gate_checkout.get("with", {}).get("persist-credentials") is False

    sig_run = _active_shell_text(str(_step_by_name(data, "Verify signed tag").get("run", "")))
    assert "gate/docs/release-signing/allowed_signers" in sig_run
    assert 'verify-tag -- "refs/tags/$TAG"' in sig_run
    assert "--format='%(tag)'" in sig_run
    assert '"$signed_tag" != "$TAG"' in sig_run
    assert 'target_type="$(git cat-file tag "refs/tags/$TAG"' in sig_run
    assert '$0==""' in sig_run
    assert '"$target_type" != "commit"' in sig_run
    assert "python3 -I -" in sig_run

    ancestry_run = _active_shell_text(
        str(_step_by_name(data, "Verify tag commit is on main").get("run", ""))
    )
    ancestry_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Verify tag commit is on main").get("run", ""))
    )
    assert '"$head_commit" != "$tag_commit"' in ancestry_run
    assert "merge-base" in ancestry_tokens
    assert "--is-ancestor" in ancestry_tokens

    checks_run = _active_shell_text(
        str(_step_by_name(data, "Verify required check-runs").get("run", ""))
    )
    checks_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Verify required check-runs").get("run", ""))
    )
    assert "python3 -I gate/scripts/release_checks.py" in checks_run
    assert "gate/scripts/release_checks.py" in checks_tokens

    notes_run = _active_shell_text(
        str(_step_by_name(data, "Validate tag and extract release notes").get("run", ""))
    )
    notes_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Validate tag and extract release notes").get("run", ""))
    )
    assert 'git show "${TAG_COMMIT}:CHANGELOG.md"' in notes_run
    assert "python3 -I gate/scripts/release_notes.py" in notes_run
    assert "gate/scripts/release_notes.py" in notes_tokens

    archive_tokens = _active_shell_tokens(
        str(_step_by_name(data, "Build source archive and SHA-256 checksum").get("run", ""))
    )
    assert "archive" in archive_tokens
    assert "sha256sum" in archive_tokens
    assert "dist/SHA256SUMS" in archive_tokens

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
    assert "dist/skills-hub-${TAG}.tar.gz" in create_tokens
    assert "dist/SHA256SUMS" in create_tokens
    assert any(token.endswith(".sigstore.json") for token in create_tokens)
    assert "args+=(--prerelease --latest=false)" in create_run
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
        "python3 -I gate/scripts/release_notes.py \\",
        "python3 -I scripts/release_notes.py # gate/scripts/release_notes.py",
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

    # 5. Dropping -I from any python3 invocation must fail.
    for step_name, old, new in [
        ("Verify signed tag", "python3 -I -", "python3 -"),
        (
            "Verify required check-runs",
            "python3 -I gate/scripts/release_checks.py",
            "python3 gate/scripts/release_checks.py",
        ),
        (
            "Validate tag and extract release notes",
            "python3 -I gate/scripts/release_notes.py",
            "python3 gate/scripts/release_notes.py",
        ),
    ]:
        no_isolated = copy.deepcopy(base)
        step = _step_by_name(no_isolated, step_name)
        assert old in step["run"]
        step["run"] = step["run"].replace(old, new, 1)
        with pytest.raises(AssertionError):
            assert_release_workflow_contract(no_isolated)

    # 6. Commenting out merge-base --is-ancestor or dist/SHA256SUMS must fail.
    no_ancestry = copy.deepcopy(base)
    ancestry_step = _step_by_name(no_ancestry, "Verify tag commit is on main")
    ancestry_step["run"] = ancestry_step["run"].replace(
        'if ! git merge-base --is-ancestor "$tag_commit" refs/remotes/origin/main; then',
        'if false; then # git merge-base --is-ancestor "$tag_commit" refs/remotes/origin/main',
    )
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(no_ancestry)

    no_sums = copy.deepcopy(base)
    release_step = _step_by_name(no_sums, "Create draft release with assets")
    release_step["run"] = release_step["run"].replace(
        "  dist/SHA256SUMS \\\n",
        "  # dist/SHA256SUMS\n",
    )
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(no_sums)

    # 7. Moving gate checkout back to branch ref: main or dropping %(tag) binding must fail.
    moving_gate = copy.deepcopy(base)
    _step_by_name(moving_gate, "Checkout release gate from main")["with"]["ref"] = "main"
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(moving_gate)

    no_tag_binding = copy.deepcopy(base)
    sig_step = _step_by_name(no_tag_binding, "Verify signed tag")
    sig_step["run"] = sig_step["run"].replace(
        'if [[ "$signed_tag" != "$TAG" ]]; then', "if false; then"
    )
    with pytest.raises(AssertionError):
        assert_release_workflow_contract(no_tag_binding)

    # 8. Re-allowing +build metadata in tag format regex (via \+ or [+]) must fail.
    for variant in (r")?(\+[0-9A-Za-z-]+)?$ ]]", r")?([+][0-9A-Za-z-]+)?$ ]]"):
        allow_build = copy.deepcopy(base)
        val_step = _step_by_name(allow_build, "Validate tag format")
        val_step["run"] = val_step["run"].replace(")?$ ]]", variant)
        with pytest.raises(AssertionError):
            assert_release_workflow_contract(allow_build)
