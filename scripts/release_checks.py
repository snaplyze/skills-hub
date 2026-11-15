#!/usr/bin/env python3
"""Validate required GitHub Actions check-runs for a release tag."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Callable, Iterable
from typing import Any

EXPECTED_WORKFLOWS = {
    "validate": ".github/workflows/ci.yml",
    "Analyze (python)": ".github/workflows/codeql.yml",
}
RUN_ID_RE = re.compile(r"/actions/runs/(\d+)")


def check_run_errors(
    runs: Iterable[dict[str, Any]],
    commit: str,
    expected_workflows: dict[str, str],
    workflow_path: Callable[[str], str | None],
) -> list[str]:
    """Return human-readable errors for the latest required check-runs."""
    latest: dict[str, dict[str, Any]] = {}
    for run in runs:
        name = run.get("name")
        if name not in expected_workflows:
            continue
        current = latest.get(name)
        if current is None or int(run.get("id", 0)) > int(current.get("id", 0)):
            latest[name] = run

    errors: list[str] = []
    for name, expected in expected_workflows.items():
        run = latest.get(name)
        if run is None:
            errors.append(f"missing required check-run: {name}")
            continue
        if run.get("head_sha") != commit:
            errors.append(f"{name} ran on {run.get('head_sha')}, not {commit}")
        if (run.get("app") or {}).get("slug") != "github-actions":
            errors.append(f"{name} was not created by GitHub Actions")
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            errors.append(
                f"{name} is not successful "
                f"(status={run.get('status')}, conclusion={run.get('conclusion')})"
            )
            continue
        details = run.get("details_url") or ""
        match = RUN_ID_RE.search(details)
        if match is None:
            errors.append(f"{name} has no Actions run URL")
            continue
        path = workflow_path(match.group(1))
        if path != expected:
            errors.append(
                f"{name} came from {path or 'an unreadable workflow'}, expected {expected}"
            )
    return errors


def gh_workflow_path(repo: str, run_id: str) -> str | None:
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/runs/{run_id}", "--jq", ".path"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-file", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args(argv)

    runs = []
    with open(args.runs_file, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                runs.append(json.loads(line))

    errors = check_run_errors(
        runs,
        args.commit,
        EXPECTED_WORKFLOWS,
        lambda run_id: gh_workflow_path(args.repo, run_id),
    )
    if errors:
        for error in errors:
            print(f"::error::{error}")
        return 1
    print(f"required check-runs OK for {args.commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
