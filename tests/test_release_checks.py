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


def with_run_override(name: str, **overrides: object) -> list[dict[str, object]]:
    return [
        {**entry, **overrides} if entry["name"] == name else dict(entry) for entry in valid_runs()
    ]


def test_expected_workflows_contract() -> None:
    assert EXPECTED_WORKFLOWS == {
        "validate": ".github/workflows/ci.yml",
        "Analyze (python)": ".github/workflows/codeql.yml",
        "Analyze (actions)": ".github/workflows/codeql.yml",
        "gitleaks": ".github/workflows/secret-scan.yml",
    }


def test_valid_runs_pass() -> None:
    assert check_run_errors(valid_runs(), COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO) == []


def test_missing_failed_or_spoofed_runs_fail() -> None:
    missing_errors = check_run_errors(
        [run("validate", 1)], COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO
    )
    assert len(missing_errors) == 3
    for name in ("Analyze (python)", "Analyze (actions)", "gitleaks"):
        assert any(f"missing required check-run: {name}" in err for err in missing_errors)

    failed = with_run_override("validate", conclusion="failure")
    failed_errors = check_run_errors(failed, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    assert len(failed_errors) == 1
    assert "not successful" in failed_errors[0]

    in_progress = with_run_override("validate", status="in_progress", conclusion=None)
    in_progress_errors = check_run_errors(in_progress, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    assert len(in_progress_errors) == 1
    assert "not successful" in in_progress_errors[0]

    spoofed = with_run_override("validate", app={"slug": "evil"})
    spoofed_errors = check_run_errors(spoofed, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    assert len(spoofed_errors) == 1
    assert "not created by GitHub Actions" in spoofed_errors[0]

    app_none = with_run_override("validate", app=None)
    app_none_errors = check_run_errors(app_none, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    assert len(app_none_errors) == 1
    assert "not created by GitHub Actions" in app_none_errors[0]


def test_wrong_commit_url_or_workflow_fails() -> None:
    wrong_commit = with_run_override("validate", head_sha="b" * 40)
    called: list[str] = []

    def tracking_paths(run_id: str) -> tuple[str | None, str | None]:
        called.append(run_id)
        return paths(run_id)

    errors = check_run_errors(wrong_commit, COMMIT, EXPECTED_WORKFLOWS, tracking_paths, repo=REPO)
    assert len(errors) == 1
    assert "ran on" in errors[0]
    # Must NOT query workflow API for a run that already failed head_sha.
    assert "1" not in called

    wrong_repo_url = with_run_override(
        "validate", details_url="https://github.com/other/repo/actions/runs/1/job/1"
    )
    wrong_url_errors = check_run_errors(
        wrong_repo_url, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO
    )
    assert len(wrong_url_errors) == 1
    assert "no Actions run URL" in wrong_url_errors[0]

    wrong_wf_sha = check_run_errors(
        valid_runs(),
        COMMIT,
        EXPECTED_WORKFLOWS,
        lambda rid: (".github/workflows/ci.yml", "b" * 40) if rid == "1" else paths(rid),
        repo=REPO,
    )
    assert len(wrong_wf_sha) == 1
    assert "workflow run targeted" in wrong_wf_sha[0]

    wrong_single_path = check_run_errors(
        valid_runs(),
        COMMIT,
        EXPECTED_WORKFLOWS,
        lambda rid: (".github/workflows/other.yml", COMMIT) if rid == "1" else paths(rid),
        repo=REPO,
    )
    assert len(wrong_single_path) == 1
    assert "expected" in wrong_single_path[0]

    wrong_path = check_run_errors(
        valid_runs(), COMMIT, EXPECTED_WORKFLOWS, lambda _run_id: "other.yml", repo=REPO
    )
    assert len(wrong_path) == 4
    assert all("expected" in error for error in wrong_path)

    unreadable = check_run_errors(
        valid_runs(), COMMIT, EXPECTED_WORKFLOWS, lambda _run_id: None, repo=REPO
    )
    assert len(unreadable) == 4
    assert all("unreadable workflow" in error for error in unreadable)


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

    # Missing head_sha (expected_path, None) from tuple lookup must fail closed,
    # even when an older passing run id=1 exists alongside newer run id=10.
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
    assert any(
        "workflow run targeted None" in e
        for e in check_run_errors(
            failed_no_ts,
            COMMIT,
            EXPECTED_WORKFLOWS,
            lambda rid: (".github/workflows/ci.yml", None) if rid == "10" else paths(rid),
            repo=REPO,
        )
    )

    # Malformed id (None, 0, -1, True, "abc") on a candidate from the expected workflow must
    # fail closed instead of sorting behind an older passing id=1 — even if conclusion="success".
    for bad_id, conclusion in [
        (None, "failure"),
        (None, "success"),
        (0, "failure"),
        (-1, "success"),
        (True, "failure"),
        ("abc", "success"),
    ]:
        bad_id_runs = [
            *valid_runs(),
            run(
                "validate",
                bad_id,
                conclusion=conclusion,
                details_url=f"https://github.com/{REPO}/actions/runs/10/job/1",
            ),
        ]
        assert any(
            "invalid check-run id" in e
            for e in check_run_errors(bad_id_runs, COMMIT, EXPECTED_WORKFLOWS, lookup_10, repo=REPO)
        )

    # Spoofed or unrelated-workflow runs with id=None must still be ignored cleanly.
    unrelated_null_id = [
        *valid_runs(),
        run("validate", None, app={"slug": "third-party-bot"}, conclusion="failure"),
        run(
            "validate",
            None,
            conclusion="failure",
            details_url=f"https://github.com/{REPO}/actions/runs/99/job/1",
        ),
    ]
    assert (
        check_run_errors(
            unrelated_null_id,
            COMMIT,
            EXPECTED_WORKFLOWS,
            lambda rid: (".github/workflows/other.yml", COMMIT) if rid == "99" else paths(rid),
            repo=REPO,
        )
        == []
    )


def test_repo_url_matching_is_case_insensitive_and_dead_helper_removed() -> None:
    mixed_case = [
        run(
            "validate",
            1,
            details_url="https://github.com/O/R/actions/runs/1/job/1",
        ),
        *valid_runs()[1:],
    ]
    assert check_run_errors(mixed_case, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO) == []
    assert check_run_errors(valid_runs(), COMMIT, EXPECTED_WORKFLOWS, paths, repo="O/R") == []
    assert not hasattr(release_checks, "gh_workflow_path")


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

    # Valid JSONL with failing check_run_errors exits 1 and reports ::error::.
    missing_checks = tmp_path / "missing.jsonl"
    missing_checks.write_text(json.dumps(run("validate", 1)) + "\n", encoding="utf-8")
    assert (
        release_checks.main(
            ["--runs-file", str(missing_checks), "--commit", COMMIT, "--repo", REPO]
        )
        == 1
    )
    out = capsys.readouterr().out
    assert "::error::missing required check-run: Analyze (actions)" in out


def test_fallback_cancelled_and_wf_cache() -> None:
    # Only a cancelled run exists for validate -> fails closed as not successful.
    only_cancelled = with_run_override("validate", conclusion="cancelled")
    errors = check_run_errors(only_cancelled, COMMIT, EXPECTED_WORKFLOWS, paths, repo=REPO)
    assert len(errors) == 1
    assert "validate is not successful" in errors[0]
    assert "conclusion=cancelled" in errors[0]

    # Shared workflow run_id ("2" for Analyze python + actions) is looked up only once via wf_cache.
    lookups: list[str] = []

    def counting_paths(run_id: str) -> tuple[str | None, str | None]:
        lookups.append(run_id)
        return paths(run_id)

    assert (
        check_run_errors(valid_runs(), COMMIT, EXPECTED_WORKFLOWS, counting_paths, repo=REPO) == []
    )
    assert lookups.count("2") == 1
    assert sorted(lookups) == ["1", "2", "3"]


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

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_kw: SimpleNamespace(returncode=0, stdout="{bad-json\n", stderr=""),
    )
    assert release_checks.gh_workflow_info(REPO, "1") == (None, None)
    assert "invalid JSON" in capsys.readouterr().err

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_kw: SimpleNamespace(returncode=0, stdout="[1, 2]\n", stderr=""),
    )
    assert release_checks.gh_workflow_info(REPO, "1") == (None, None)

    def raise_oserror(*_a: object, **_kw: object) -> None:
        raise OSError("gh binary not found")

    monkeypatch.setattr(subprocess, "run", raise_oserror)
    assert release_checks.gh_workflow_info(REPO, "1") == (None, None)
    assert "gh api failed" in capsys.readouterr().err

    def raise_timeout(*_a: object, **_kw: object) -> None:
        raise subprocess.TimeoutExpired(cmd="gh", timeout=30)

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    assert release_checks.gh_workflow_info(REPO, "1") == (None, None)
    assert "gh api failed" in capsys.readouterr().err
