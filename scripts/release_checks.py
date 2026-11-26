#!/usr/bin/env python3
"""Validate required GitHub Actions check-runs for a release tag."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Iterable
from typing import Any

EXPECTED_WORKFLOWS = {
    "validate": ".github/workflows/ci.yml",
    "Analyze (python)": ".github/workflows/codeql.yml",
    "gitleaks": ".github/workflows/secret-scan.yml",
}
GENERIC_RUN_URL_RE = re.compile(
    r"^https://github\.com/[^/\s]+/[^/\s]+/actions/runs/(\d+)(?:/|\?|#|\Z)"
)
GH_API_TIMEOUT_SECONDS = 30

WorkflowLookup = Callable[[str], str | tuple[str | None, str | None] | None]


def _safe_int(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _extract_run_id(details_url: str, repo: str | None) -> str | None:
    if repo:
        pattern = re.compile(
            rf"^https://github\.com/{re.escape(repo)}/actions/runs/(\d+)(?:/|\?|#|\Z)"
        )
    else:
        pattern = GENERIC_RUN_URL_RE
    match = pattern.match(details_url)
    return match.group(1) if match else None


def _run_sort_key(run: dict[str, Any]) -> tuple[int, str, str]:
    completed = run.get("completed_at")
    started = run.get("started_at")
    return (
        _safe_int(run.get("id")),
        completed if isinstance(completed, str) else "",
        started if isinstance(started, str) else "",
    )


def _resolve_workflow_info(
    run_id: str,
    workflow_lookup: WorkflowLookup,
    cache: dict[str, tuple[str | None, str | None, bool]],
) -> tuple[str | None, str | None, bool]:
    if run_id in cache:
        return cache[run_id]
    raw = workflow_lookup(run_id)
    info = (raw[0], raw[1], True) if isinstance(raw, tuple) else (raw, None, False)
    cache[run_id] = info
    return info


def check_run_errors(
    runs: Iterable[dict[str, Any]],
    commit: str,
    expected_workflows: dict[str, str],
    workflow_path: WorkflowLookup,
    *,
    repo: str | None = None,
) -> list[str]:
    """Return human-readable errors for required GitHub Actions check-runs.

    Candidates are sorted newest-first by check-run ``id`` and filtered by
    ``head_sha``, ``app.slug == "github-actions"``, repository-scoped Actions
    URL, and originating workflow path BEFORE selecting a decisive run.
    Cancelled re-dispatches are skipped in favor of the latest non-cancelled
    run from the expected workflow; unread/unverifiable newer runs and active
    ``in_progress``/``queued`` runs fail closed.
    """
    by_name: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if not isinstance(run, dict):
            continue
        name = run.get("name")
        if isinstance(name, str) and name in expected_workflows:
            by_name.setdefault(name, []).append(run)

    wf_cache: dict[str, tuple[str | None, str | None, bool]] = {}
    errors: list[str] = []

    for name, expected in expected_workflows.items():
        candidates = by_name.get(name, [])
        if not candidates:
            errors.append(f"missing required check-run: {name}")
            continue

        decisive: dict[str, Any] | None = None
        fallback_cancelled: dict[str, Any] | None = None
        lookup_failed: str | None = None
        diagnostics: list[str] = []

        for run in sorted(candidates, key=_run_sort_key, reverse=True):
            if run.get("head_sha") != commit:
                diagnostics.append(f"{name} ran on {run.get('head_sha')}, not {commit}")
                continue
            app = run.get("app")
            if not isinstance(app, dict) or app.get("slug") != "github-actions":
                diagnostics.append(f"{name} was not created by GitHub Actions")
                continue
            details = run.get("details_url")
            run_id = _extract_run_id(details, repo) if isinstance(details, str) else None
            if run_id is None:
                diagnostics.append(f"{name} has no Actions run URL")
                continue
            path, wf_sha, has_sha = _resolve_workflow_info(run_id, workflow_path, wf_cache)
            if path is None:
                lookup_failed = (
                    f"{name} came from an unreadable workflow (run {run_id}), expected {expected}"
                )
                break
            if path != expected:
                diagnostics.append(f"{name} came from {path}, expected {expected}")
                continue
            if has_sha and wf_sha != commit:
                diagnostics.append(f"{name} workflow run targeted {wf_sha}, not {commit}")
                continue
            if run.get("status") == "completed" and run.get("conclusion") == "cancelled":
                if fallback_cancelled is None:
                    fallback_cancelled = run
                continue
            decisive = run
            break

        if lookup_failed is not None:
            errors.append(lookup_failed)
            continue

        chosen = decisive if decisive is not None else fallback_cancelled
        if chosen is None:
            errors.append(diagnostics[0] if diagnostics else f"missing required check-run: {name}")
            continue

        if chosen.get("status") != "completed" or chosen.get("conclusion") != "success":
            errors.append(
                f"{name} is not successful "
                f"(status={chosen.get('status')}, conclusion={chosen.get('conclusion')})"
            )

    return errors


def gh_workflow_info(repo: str, run_id: str) -> tuple[str | None, str | None]:
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}/actions/runs/{run_id}",
                "--jq",
                "{path: .path, head_sha: .head_sha}",
            ],
            capture_output=True,
            text=True,
            timeout=GH_API_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"warning: gh api failed for run {run_id}: {error}", file=sys.stderr)
        return None, None

    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit {result.returncode}"
        print(f"warning: gh api failed for run {run_id}: {detail}", file=sys.stderr)
        return None, None

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        print(f"warning: gh api returned invalid JSON for run {run_id}: {error}", file=sys.stderr)
        return None, None
    if not isinstance(payload, dict):
        return None, None
    raw_path = payload.get("path")
    raw_sha = payload.get("head_sha")
    path = raw_path.strip() if isinstance(raw_path, str) and raw_path.strip() else None
    head_sha = raw_sha.strip() if isinstance(raw_sha, str) and raw_sha.strip() else None
    return path, head_sha


def gh_workflow_path(repo: str, run_id: str) -> str | None:
    return gh_workflow_info(repo, run_id)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-file", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args(argv)

    runs: list[dict[str, Any]] = []
    try:
        with open(args.runs_file, encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                entry = json.loads(stripped)
                if not isinstance(entry, dict):
                    print(
                        f"::error::{args.runs_file}:{line_no}: expected JSON object in check-runs",
                    )
                    return 1
                runs.append(entry)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"::error::failed to read check-runs file {args.runs_file}: {error}")
        return 1

    errors = check_run_errors(
        runs,
        args.commit,
        EXPECTED_WORKFLOWS,
        lambda run_id: gh_workflow_info(args.repo, run_id),
        repo=args.repo,
    )
    if errors:
        for error in errors:
            print(f"::error::{error}")
        return 1
    print(f"required check-runs OK for {args.commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
