"""Tests for required check-run validation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import release_checks
from scripts.release_checks import EXPECTED_WORKFLOWS, check_run_errors

COMMIT = "a" * 40
REPO = "o/r"


def run(name: str, run_id: int | None, **overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "name": name,
        "id": run_id,
        "head_sha": COMMIT,
        "status": "completed",
        "conclusion": "success",
        "completed_at": "2026-11-26T00:00:10Z",
        "started_at": "2026-11-26T00:00:00Z",
        "app": {"slug": "github-actions"},
        "details_url": f"https://github.com/{REPO}/actions/runs/{run_id}/job/1",
    }
    data.update(overrides)
    return data


def paths(run_id: str) -> tuple[str | None, str | None]:
    mapping = {
        "1": (".github/workflows/ci.yml", COMMIT),
        "2": (".github/workflows/codeql.yml", COMMIT),
        "3": (".github/workflows/secret-scan.yml", COMMIT),
    }
    return mapping.get(run_id, (None, None))


def valid_runs() -> list[dict[str, object]]:
    return [
        run("validate", 1),
        run("Analyze (python)", 2),
        run("Analyze (actions)", 2),
        run("gitleaks", 3),
    ]


def test_valid_runs_pass() -> None:
    assert check_run_errors(valid_runs(), COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO) == []


def test_missing_failed_or_spoofed_runs_fail() -> None:
    assert "missing" in " ".join(
        check_run_errors([run("validate", 1)], COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    )
    failed = [
        run("validate", 1, conclusion="failure"),
        run("Analyze (python)", 2),
        run("gitleaks", 3),
    ]
    assert any(
        "not successful" in error
        for error in check_run_errors(failed, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    )
    in_progress = [
        run("validate", 1, status="in_progress", conclusion=None),
        run("Analyze (python)", 2),
        run("gitleaks", 3),
    ]
    assert any(
        "not successful" in error
        for error in check_run_errors(in_progress, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    )
    spoofed = [
        run("validate", 1, app={"slug": "evil"}),
        run("Analyze (python)", 2),
        run("gitleaks", 3),
    ]
    assert any(
        "not created by GitHub Actions" in error
        for error in check_run_errors(spoofed, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    )
    app_none = [run("validate", 1, app=None), run("Analyze (python)", 2), run("gitleaks", 3)]
    assert any(
        "not created by GitHub Actions" in error
        for error in check_run_errors(app_none, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    )


def test_wrong_commit_url_or_workflow_fails() -> None:
    wrong_commit = [
        run("validate", 1, head_sha="b" * 40),
        run("Analyze (python)", 2),
        run("gitleaks", 3),
    ]
    called: list[str] = []

    def tracking_paths(run_id: str) -> tuple[str | None, str | None]:
        called.append(run_id)
        return paths(run_id)

    errors = check_run_errors(wrong_commit, COMMIT, EXPECTED_WORKFLOWS, tracking_paths, repo=REPO)
    assert any("ran on" in error for error in errors)
    # Must NOT query workflow API for a run that already failed head_sha.
    assert "1" not in called

    wrong_repo_url = [
        run("validate", 1, details_url="https://github.com/other/repo/actions/runs/1/job/1"),
        run("Analyze (python)", 2),
        run("gitleaks", 3),
    ]
    assert any(
        "no Actions run URL" in error
        for error in check_run_errors(wrong_repo_url, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    )

    wrong_wf_sha = check_run_errors(
        valid_runs(),
        COMMIT,
        EXPECTED_WORKFLOWS,
        lambda rid: (".github/workflows/ci.yml", "b" * 40) if rid == "1" else paths(rid),
        repo=REPO,
    )
    assert any("workflow run targeted" in error for error in wrong_wf_sha)

    wrong_path = check_run_errors(
        valid_runs(), COMMIT, EXPECTED_WORKFLOWS, lambda _run_id: "other.yml", repo=REPO
    )
    assert any("expected" in error for error in wrong_path)

    unreadable = check_run_errors(
        valid_runs(), COMMIT, EXPECTED_WORKFLOWS, lambda _run_id: None, repo=REPO
    )
    assert any("unreadable workflow" in error for error in unreadable)


def test_third_party_or_cancelled_run_does_not_shadow_valid_check() -> None:
    runs = [
        *valid_runs(),
        # Higher ID third-party app with same name must not shadow valid run 1.
        run("validate", 999, app={"slug": "third-party-bot"}, conclusion="failure"),
        # Higher ID run from a different workflow must not shadow valid run 1.
        run(
            "validate",
            1000,
            details_url=f"https://github.com/{REPO}/actions/runs/1000/job/1",
            conclusion="failure",
        ),
        # Newer cancelled re-dispatch from ci.yml must not mask earlier completed pass.
        run(
            "validate",
            1001,
            completed_at="2026-11-26T01:00:00Z",
            conclusion="cancelled",
            details_url=f"https://github.com/{REPO}/actions/runs/1001/job/1",
        ),
        # Unrelated check-run and null id must be handled cleanly.
        run("other-check", None),
    ]

    def lookup(run_id: str) -> tuple[str | None, str | None]:
        if run_id == "1000":
            return (".github/workflows/other.yml", COMMIT)
        if run_id == "1001":
            return (".github/workflows/ci.yml", COMMIT)
        return paths(run_id)

    assert check_run_errors(runs, COMMIT, EXPECTED_WORKFLOWS, lookup, repo=REPO) == []


def test_newer_failed_in_progress_or_unreadable_run_fails_closed() -> None:
    # Newer completed failure with missing completed_at must NOT be masked by older success.
    failed_no_ts = [
        *valid_runs(),
        run(
            "validate",
            10,
            completed_at=None,
            started_at="2026-11-26T02:00:00Z",
            conclusion="failure",
            details_url=f"https://github.com/{REPO}/actions/runs/10/job/1",
        ),
    ]

    def lookup_10(run_id: str) -> tuple[str | None, str | None]:
        if run_id == "10":
            return (".github/workflows/ci.yml", COMMIT)
        return paths(run_id)

    assert any(
        "validate is not successful" in e
        for e in check_run_errors(failed_no_ts, COMMIT, EXPECTED_WORKFLOWS, lookup_10, repo=REPO)
    )

    # Newer in_progress or queued run must NOT be masked by an older success.
    in_progress_newer = [
        *valid_runs(),
        run(
            "validate",
            11,
            status="in_progress",
            conclusion=None,
            completed_at=None,
            started_at="2026-11-26T02:00:00Z",
            details_url=f"https://github.com/{REPO}/actions/runs/11/job/1",
        ),
    ]
    assert any(
        "validate is not successful" in e
        for e in check_run_errors(
            in_progress_newer,
            COMMIT,
            EXPECTED_WORKFLOWS,
            lambda rid: (".github/workflows/ci.yml", COMMIT) if rid == "11" else paths(rid),
            repo=REPO,
        )
    )

    # API failure (None, None) on newer failing run must fail closed instead of falling back to id=1.
    assert any(
        "unreadable workflow" in e
        for e in check_run_errors(
            failed_no_ts,
            COMMIT,
            EXPECTED_WORKFLOWS,
            lambda rid: (None, None) if rid == "10" else paths(rid),
            repo=REPO,
        )
    )

    # Missing head_sha (expected_path, None) from tuple lookup must fail closed.
    assert any(
        "workflow run targeted None" in e
        for e in check_run_errors(
            valid_runs(),
            COMMIT,
            EXPECTED_WORKFLOWS,
            lambda rid: (".github/workflows/ci.yml", None) if rid == "1" else paths(rid),
            repo=REPO,
        )
    )


def test_main_jsonl_handling_and_gh_workflow_info(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Malformed JSONL exits 1 with ::error:: (no traceback).
    bad_json = tmp_path / "bad.jsonl"
    bad_json.write_text("{not-json\n", encoding="utf-8")
    assert (
        release_checks.main(["--runs-file", str(bad_json), "--commit", COMMIT, "--repo", REPO]) == 1
    )
    assert "::error::" in capsys.readouterr().out

    # Non-object JSON line exits 1 cleanly.
    non_obj = tmp_path / "list.jsonl"
    non_obj.write_text("[1, 2]\n", encoding="utf-8")
    assert (
        release_checks.main(["--runs-file", str(non_obj), "--commit", COMMIT, "--repo", REPO]) == 1
    )
    assert "expected JSON object" in capsys.readouterr().out

    # Valid JSONL passes when gh_workflow_info returns matching workflows.
    good = tmp_path / "good.jsonl"
    good.write_text("\n".join(json.dumps(r) for r in valid_runs()) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        release_checks,
        "gh_workflow_info",
        lambda _repo, run_id: paths(run_id),
    )
    assert release_checks.main(["--runs-file", str(good), "--commit", COMMIT, "--repo", REPO]) == 0
    assert "required check-runs OK" in capsys.readouterr().out


def test_gh_workflow_info_handles_success_failure_and_timeout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_kw: SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"path": ".github/workflows/ci.yml", "head_sha": COMMIT}) + "\n",
            stderr="",
        ),
    )
    assert release_checks.gh_workflow_info(REPO, "1") == (".github/workflows/ci.yml", COMMIT)

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_kw: SimpleNamespace(returncode=1, stdout="", stderr="rate limited"),
    )
    assert release_checks.gh_workflow_info(REPO, "1") == (None, None)
    assert "rate limited" in capsys.readouterr().err

    def raise_timeout(*_a: object, **_kw: object) -> None:
        raise subprocess.TimeoutExpired(cmd="gh", timeout=30)

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    assert release_checks.gh_workflow_info(REPO, "1") == (None, None)
    assert "gh api failed" in capsys.readouterr().err
