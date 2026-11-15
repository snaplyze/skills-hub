#!/usr/bin/env python3
"""Check GitHub Actions workflows for pinned actions and least privilege.

Policy enforced for every file in ``.github/workflows/``:

* every ``uses:`` reference is pinned to a full 40-character commit SHA;
* every job declares a bounded ``timeout-minutes``;
* every ``actions/checkout`` step sets ``persist-credentials: false``;
* ``pull_request_target`` is not used;
* top-level permissions are explicit and read-only, and ``write-all`` is
  never used;
* write permissions live only at job scope and only for the approved scopes
  (``attestations``, ``contents``, ``security-events``, ``id-token``,
  ``pull-requests``).

Usage:
    python3 scripts/check_workflows.py [--root PATH]

Exit codes:
    0  all workflows satisfy the policy
    1  policy violations
    2  missing development dependency
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "error: PyYAML is required. Install development dependencies with "
        "`python3 -m pip install -r requirements-dev.txt`.",
        file=sys.stderr,
    )
    raise SystemExit(2) from None

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = Path(".github") / "workflows"
REQUIRED_WORKFLOWS = frozenset(
    {
        "ci.yml",
        "codeql.yml",
        "dependency-review.yml",
        "release.yml",
        "scorecard.yml",
        "secret-scan.yml",
    }
)
ACTION_SHA_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-f]{40}$")
VALID_PERMISSIONS = frozenset(
    {
        "actions",
        "attestations",
        "checks",
        "contents",
        "deployments",
        "discussions",
        "id-token",
        "issues",
        "models",
        "packages",
        "pages",
        "pull-requests",
        "security-events",
        "statuses",
    }
)
JOB_WRITE_SCOPES = frozenset(
    {"attestations", "contents", "security-events", "id-token", "pull-requests"}
)
VALID_EVENTS = frozenset(
    {
        "branch_protection_rule",
        "check_run",
        "check_suite",
        "create",
        "delete",
        "deployment",
        "deployment_status",
        "discussion",
        "discussion_comment",
        "fork",
        "gollum",
        "issue_comment",
        "issues",
        "label",
        "merge_group",
        "milestone",
        "page_build",
        "public",
        "pull_request",
        "pull_request_review",
        "pull_request_review_comment",
        "pull_request_target",
        "push",
        "registry_package",
        "release",
        "repository_dispatch",
        "schedule",
        "status",
        "watch",
        "workflow_call",
        "workflow_dispatch",
        "workflow_run",
    }
)
READ_VALUES = frozenset({"read", "none"})

Error = tuple[str, int, str]


def mapping_items(node: object) -> list[tuple[yaml.ScalarNode, yaml.Node]]:
    """Return mapping entries when *node* is a YAML mapping."""
    if not isinstance(node, yaml.MappingNode):
        return []
    return [(key, value) for key, value in node.value if isinstance(key, yaml.ScalarNode)]


def find(node: object, key: str) -> tuple[yaml.ScalarNode, yaml.Node] | None:
    """Return the first mapping entry named *key*."""
    for key_node, value_node in mapping_items(node):
        if key_node.value == key:
            return key_node, value_node
    return None


def scalar_value(node: object) -> str | None:
    """Return a scalar value for a YAML node, otherwise ``None``."""
    if isinstance(node, yaml.ScalarNode):
        return node.value
    return None


def line_of(node: yaml.Node) -> int:
    """Return the 1-based line where *node* starts."""
    return node.start_mark.line + 1


def add(errors: list[Error], relative: str, node: yaml.Node, message: str) -> None:
    errors.append((relative, line_of(node), message))


def check_action_ref(errors: list[Error], relative: str, node: yaml.Node) -> None:
    value = scalar_value(node)
    if value is None or not ACTION_SHA_RE.fullmatch(value):
        shown = value if value is not None else "<non-scalar>"
        add(
            errors,
            relative,
            node,
            f"action '{shown}' must be pinned to a full 40-character commit SHA",
        )


def check_checkout_credentials(errors: list[Error], relative: str, step: yaml.MappingNode) -> None:
    uses = find(step, "uses")
    if uses is None:
        return
    action = (scalar_value(uses[1]) or "").partition("@")[0]
    if action != "actions/checkout":
        return

    with_entry = find(step, "with")
    persist = find(with_entry[1], "persist-credentials") if with_entry else None
    if persist is None:
        add(
            errors,
            relative,
            uses[1],
            "actions/checkout must set persist-credentials: false",
        )
        return
    if (scalar_value(persist[1]) or "").lower() != "false":
        add(
            errors,
            relative,
            persist[1],
            "actions/checkout must set persist-credentials: false",
        )


def check_permissions(errors: list[Error], relative: str, node: yaml.Node, scope: str) -> None:
    value = scalar_value(node)
    if value is not None:
        if value == "read-all":
            return
        if value == "write-all":
            add(errors, relative, node, "permissions must not use write-all")
            return
        add(errors, relative, node, f"unsupported {scope} permissions value '{value}'")
        return

    items = mapping_items(node)
    if not items:
        return
    for key_node, value_node in items:
        name = key_node.value
        permission = scalar_value(value_node) or ""
        if name not in VALID_PERMISSIONS:
            add(errors, relative, key_node, f"unknown permission scope '{name}'")
            continue
        if permission in READ_VALUES:
            continue
        if permission == "write":
            if scope == "workflow":
                add(
                    errors,
                    relative,
                    value_node,
                    f"workflow-level permission '{name}: write' is not allowed; "
                    "move write permissions to job scope",
                )
            elif name not in JOB_WRITE_SCOPES:
                add(
                    errors,
                    relative,
                    value_node,
                    f"job-level permission '{name}: write' is not allowed",
                )
            continue
        add(
            errors,
            relative,
            value_node,
            f"permission '{name}' must be read, none, or write",
        )


def check_triggers(errors: list[Error], relative: str, workflow: yaml.MappingNode) -> None:
    trigger = find(workflow, "on")
    if trigger is None:
        add(errors, relative, workflow, "workflow must define 'on'")
        return

    node = trigger[1]
    names: list[tuple[str, yaml.Node]] = []
    if isinstance(node, yaml.ScalarNode):
        names.append((node.value, node))
    elif isinstance(node, yaml.SequenceNode):
        names.extend((item.value, item) for item in node.value if isinstance(item, yaml.ScalarNode))
    else:
        names.extend((key.value, key) for key, _ in mapping_items(node))

    for name, name_node in names:
        if name not in VALID_EVENTS:
            add(errors, relative, name_node, f"unsupported workflow event '{name}'")
        if name == "pull_request_target":
            add(errors, relative, name_node, "pull_request_target is not allowed")


def check_timeout(
    errors: list[Error], relative: str, job: yaml.MappingNode, job_node: yaml.Node
) -> None:
    timeout = find(job, "timeout-minutes")
    if timeout is None:
        add(errors, relative, job_node, "job must set timeout-minutes")
        return
    raw = scalar_value(timeout[1])
    try:
        minutes = int(raw) if raw is not None else 0
    except ValueError:
        minutes = 0
    if not 1 <= minutes <= 360:
        add(errors, relative, timeout[1], "timeout-minutes must be an integer from 1 to 360")


def check_steps(errors: list[Error], relative: str, job: yaml.MappingNode) -> None:
    steps = find(job, "steps")
    if steps is None:
        add(errors, relative, job, "job must define steps")
        return
    if not isinstance(steps[1], yaml.SequenceNode):
        add(errors, relative, steps[1], "steps must be a sequence")
        return

    for step in steps[1].value:
        if not isinstance(step, yaml.MappingNode):
            add(errors, relative, step, "step must be a mapping")
            continue
        uses = find(step, "uses")
        if uses is not None:
            check_action_ref(errors, relative, uses[1])
            check_checkout_credentials(errors, relative, step)


def check_jobs(errors: list[Error], relative: str, workflow: yaml.MappingNode) -> None:
    jobs = find(workflow, "jobs")
    if jobs is None:
        add(errors, relative, workflow, "workflow must define jobs")
        return
    if not isinstance(jobs[1], yaml.MappingNode):
        add(errors, relative, jobs[1], "jobs must be a mapping")
        return

    for job_key, job in mapping_items(jobs[1]):
        if not isinstance(job, yaml.MappingNode):
            add(errors, relative, job_key, f"job '{job_key.value}' must be a mapping")
            continue
        check_timeout(errors, relative, job, job_key)

        permissions = find(job, "permissions")
        if permissions is not None:
            check_permissions(errors, relative, permissions[1], "job")

        job_uses = find(job, "uses")
        if job_uses is not None:
            check_action_ref(errors, relative, job_uses[1])
        else:
            check_steps(errors, relative, job)


def check_workflow(path: Path, root: Path) -> list[Error]:
    relative = path.relative_to(root).as_posix()
    try:
        workflow = yaml.compose(path.read_text(encoding="utf-8"), Loader=yaml.SafeLoader)
    except yaml.YAMLError as error:
        return [(relative, 1, f"invalid YAML: {error}")]

    errors: list[Error] = []
    if not isinstance(workflow, yaml.MappingNode):
        return [(relative, 1, "workflow must be a mapping")]

    permissions = find(workflow, "permissions")
    if permissions is None:
        add(errors, relative, workflow, "workflow must declare top-level permissions")
    else:
        check_permissions(errors, relative, permissions[1], "workflow")

    check_triggers(errors, relative, workflow)
    check_jobs(errors, relative, workflow)
    return errors


def workflow_paths(root: Path) -> list[Path]:
    directory = root / WORKFLOW_DIR
    if not directory.is_dir():
        return []
    return sorted(
        [*directory.glob("*.yml"), *directory.glob("*.yaml")],
        key=lambda path: path.name,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root containing .github/workflows (default: repository root)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="require the repository's mandatory workflow files to exist",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    paths = workflow_paths(root)
    if not paths:
        print(f"error: no workflows found under {root / WORKFLOW_DIR}", file=sys.stderr)
        return 1

    errors: list[Error] = []
    if args.strict:
        present = {path.name for path in paths}
        for name in sorted(REQUIRED_WORKFLOWS - present):
            errors.append((str(WORKFLOW_DIR / name), 1, "required workflow file is missing"))
    for path in paths:
        errors.extend(check_workflow(path, root))

    if errors:
        print(f"Workflow policy failed with {len(errors)} error(s):\n", file=sys.stderr)
        for relative, line, message in sorted(errors):
            print(f"  {relative}:{line}: {message}", file=sys.stderr)
        return 1

    print(f"Checked {len(paths)} workflow file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
