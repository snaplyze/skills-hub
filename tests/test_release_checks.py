"""Tests for required check-run validation."""

from __future__ import annotations

from scripts.release_checks import EXPECTED_WORKFLOWS, check_run_errors

COMMIT = "a" * 40


def run(name: str, run_id: int, **overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "name": name,
        "id": run_id,
        "head_sha": COMMIT,
        "status": "completed",
        "conclusion": "success",
        "app": {"slug": "github-actions"},
        "details_url": f"https://github.com/o/r/actions/runs/{run_id}/job/1",
    }
    data.update(overrides)
    return data


def paths(run_id: str) -> str:
    return ".github/workflows/ci.yml" if run_id == "1" else ".github/workflows/codeql.yml"


def valid_runs() -> list[dict[str, object]]:
    return [run("validate", 1), run("Analyze (python)", 2)]


def test_valid_runs_pass() -> None:
    assert check_run_errors(valid_runs(), COMMIT, EXPECTED_WORKFLOWS, paths) == []


def test_missing_failed_or_spoofed_runs_fail() -> None:
    assert "missing" in " ".join(
        check_run_errors([run("validate", 1)], COMMIT, EXPECTED_WORKFLOWS, paths)
    )
    failed = [run("validate", 1, conclusion="failure"), run("Analyze (python)", 2)]
    assert any(
        "not successful" in error
        for error in check_run_errors(failed, COMMIT, EXPECTED_WORKFLOWS, paths)
    )
    spoofed = [run("validate", 1, app={"slug": "evil"}), run("Analyze (python)", 2)]
    assert any(
        "not created by GitHub Actions" in error
        for error in check_run_errors(spoofed, COMMIT, EXPECTED_WORKFLOWS, paths)
    )


def test_wrong_commit_or_workflow_fails() -> None:
    wrong_commit = [run("validate", 1, head_sha="b" * 40), run("Analyze (python)", 2)]
    assert any(
        "ran on" in error
        for error in check_run_errors(wrong_commit, COMMIT, EXPECTED_WORKFLOWS, paths)
    )
    wrong_path = check_run_errors(
        valid_runs(), COMMIT, EXPECTED_WORKFLOWS, lambda _run_id: "other.yml"
    )
    assert any("expected" in error for error in wrong_path)
