#!/usr/bin/env python3
"""Check GitHub Actions workflows for pinned actions and least privilege.

Policy enforced for every file in ``.github/workflows/``:

* valid YAML mapping with no duplicate mapping keys (case-insensitive),
  ``<<`` merge keys, or cyclic YAML aliases;
* explicit top-level ``name``, ``on``, ``permissions``, and non-empty ``jobs``;
* every ``uses:`` reference is pinned to a full 40-character commit SHA with
  valid owner/repo/subpath segments (no ``.`` or ``..``);
* every standard job declares a pinned GitHub-hosted ``runs-on`` runner (no
  ``self-hosted`` or ``*-latest``), a bounded unquoted base-10 integer
  ``timeout-minutes`` (1..360), and non-empty ``steps`` without ``${{ ... }}``
  in ``run:``;
* every ``actions/checkout`` step (case-insensitive, including any subpath)
  sets ``persist-credentials: false``;
* ``pull_request_target`` is not used;
* top-level permissions are an explicit read-only mapping (no ``write-all``
  or ``read-all``);
* write permissions live only at job scope for approved scopes
  (``attestations``, ``contents``, ``security-events``, ``id-token``,
  ``pull-requests``), and untrusted-input workflows (``pull_request``,
  ``pull_request_review``, ``pull_request_review_comment``, ``issue_comment``,
  ``issues``, ``discussion``, ``discussion_comment``, ``fork``, ``watch``,
  ``workflow_run``) cannot grant ``contents: write``, ``id-token: write``, or
  ``attestations: write``.

Usage:
    python3 scripts/check_workflows.py [--root PATH] [--strict]

Exit codes:
    0  all workflows satisfy the policy
    1  policy violations
    2  missing development dependency
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
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
OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$")
ACTION_SHA_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*@[0-9a-f]{40}$")
PINNED_HOSTED_RUNNER_RE = re.compile(r"^(?:ubuntu|macos|windows)-[0-9][A-Za-z0-9.-]*$")
BASE10_POS_INT_RE = re.compile(r"^[1-9][0-9]*$")
EXPRESSION_RE = re.compile(r"\$\{\{")
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
UNTRUSTED_WRITE_RESTRICTED_EVENTS = frozenset(
    {
        "pull_request",
        "pull_request_review",
        "pull_request_review_comment",
        "issue_comment",
        "issues",
        "discussion",
        "discussion_comment",
        "fork",
        "watch",
        "workflow_run",
    }
)
PR_FORBIDDEN_WRITE_SCOPES = frozenset({"attestations", "contents", "id-token"})
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
    """Return the mapping entry named *key* (case-insensitive for fail-closed checks)."""
    target = key.lower()
    for key_node, value_node in mapping_items(node):
        if key_node.value.lower() == target:
            return key_node, value_node
    return None


def scalar_value(node: object) -> str | None:
    """Return a scalar value for a YAML node, otherwise ``None``."""
    if isinstance(node, yaml.ScalarNode):
        return node.value
    return None


def is_null_node(node: object) -> bool:
    """Return True when *node* is a YAML null scalar."""
    return isinstance(node, yaml.ScalarNode) and node.tag == "tag:yaml.org,2002:null"


def line_of(node: yaml.Node) -> int:
    """Return the 1-based line where *node* starts."""
    return node.start_mark.line + 1


def add(errors: list[Error], relative: str, node: yaml.Node, message: str) -> None:
    errors.append((relative, line_of(node), message))


def check_ast_integrity(
    errors: list[Error],
    relative: str,
    node: yaml.Node,
    active: set[int] | None = None,
    visited: set[int] | None = None,
) -> None:
    """Reject duplicate YAML mapping keys (case-insensitive), ``<<`` merges, and cyclic aliases."""
    if active is None:
        active = set()
    if visited is None:
        visited = set()

    node_id = id(node)
    if node_id in active:
        add(errors, relative, node, "cyclic YAML alias is not allowed")
        return
    if node_id in visited:
        return

    active.add(node_id)
    try:
        if isinstance(node, yaml.MappingNode):
            seen: set[str] = set()
            for key_node, value_node in node.value:
                if isinstance(key_node, yaml.ScalarNode):
                    normalized = key_node.value.lower()
                    if key_node.tag == "tag:yaml.org,2002:merge" or key_node.value == "<<":
                        add(errors, relative, key_node, "YAML merge key '<<' is not allowed")
                    elif normalized in seen:
                        add(errors, relative, key_node, f"duplicate YAML key '{key_node.value}'")
                    else:
                        seen.add(normalized)
                else:
                    add(errors, relative, key_node, "mapping key must be a scalar")
                check_ast_integrity(errors, relative, value_node, active, visited)
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                check_ast_integrity(errors, relative, item, active, visited)
    finally:
        active.remove(node_id)
        visited.add(node_id)


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
        return

    action_path = value.partition("@")[0]
    segments = action_path.split("/")
    if not OWNER_RE.fullmatch(segments[0]) or any(seg in {".", ".."} for seg in segments):
        add(
            errors,
            relative,
            node,
            f"action '{value}' has an invalid owner or path segment",
        )


def check_checkout_credentials(errors: list[Error], relative: str, step: yaml.MappingNode) -> None:
    uses = find(step, "uses")
    if uses is None:
        return
    action_segments = (scalar_value(uses[1]) or "").partition("@")[0].lower().split("/")
    if action_segments[:2] != ["actions", "checkout"]:
        return

    with_entry = find(step, "with")
    if with_entry is not None and not isinstance(with_entry[1], yaml.MappingNode):
        add(errors, relative, with_entry[1], "actions/checkout 'with' must be a mapping")
        return
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


def check_permissions(
    errors: list[Error],
    relative: str,
    node: yaml.Node,
    scope: str,
    *,
    events: set[str] | None = None,
) -> None:
    value = scalar_value(node)
    if value is not None:
        if value == "write-all":
            add(errors, relative, node, "permissions must not use write-all")
            return
        if value == "read-all":
            add(
                errors,
                relative,
                node,
                "permissions must not use read-all; declare explicit minimal scopes or {}",
            )
            return
        add(errors, relative, node, f"unsupported {scope} permissions value '{value}'")
        return

    if not isinstance(node, yaml.MappingNode):
        add(errors, relative, node, f"{scope} permissions must be a mapping")
        return

    restricted = sorted((events or set()) & UNTRUSTED_WRITE_RESTRICTED_EVENTS)
    for key_node, value_node in mapping_items(node):
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
            elif restricted and name in PR_FORBIDDEN_WRITE_SCOPES:
                add(
                    errors,
                    relative,
                    value_node,
                    f"job-level permission '{name}: write' is not allowed on "
                    f"{', '.join(restricted)} workflows",
                )
            continue
        add(
            errors,
            relative,
            value_node,
            f"permission '{name}' must be read, none, or write",
        )


def check_triggers(errors: list[Error], relative: str, workflow: yaml.MappingNode) -> set[str]:
    trigger = find(workflow, "on")
    if trigger is None:
        add(errors, relative, workflow, "workflow must define 'on'")
        return set()

    node = trigger[1]
    names: list[tuple[str, yaml.Node]] = []
    if isinstance(node, yaml.ScalarNode):
        if is_null_node(node) or not node.value.strip():
            add(errors, relative, node, "workflow 'on' must not be empty")
            return set()
        names.append((node.value, node))
    elif isinstance(node, yaml.SequenceNode):
        if not node.value:
            add(errors, relative, node, "workflow 'on' must not be empty")
            return set()
        for item in node.value:
            if isinstance(item, yaml.ScalarNode) and not is_null_node(item):
                names.append((item.value, item))
            else:
                add(errors, relative, item, "workflow event name must be a scalar")
    elif isinstance(node, yaml.MappingNode):
        if not node.value:
            add(errors, relative, node, "workflow 'on' must not be empty")
            return set()
        names.extend((key.value, key) for key, _ in mapping_items(node))
    else:
        add(errors, relative, node, "workflow 'on' must be a scalar, sequence, or mapping")
        return set()

    seen_events: set[str] = set()
    for name, name_node in names:
        seen_events.add(name)
        if name not in VALID_EVENTS:
            add(errors, relative, name_node, f"unsupported workflow event '{name}'")
        if name == "pull_request_target":
            add(errors, relative, name_node, "pull_request_target is not allowed")
    return seen_events


def check_timeout(
    errors: list[Error], relative: str, job: yaml.MappingNode, job_node: yaml.Node
) -> None:
    timeout = find(job, "timeout-minutes")
    if timeout is None:
        add(errors, relative, job_node, "job must set timeout-minutes")
        return
    timeout_node = timeout[1]
    raw = scalar_value(timeout_node)
    if (
        raw is None
        or timeout_node.tag != "tag:yaml.org,2002:int"
        or not BASE10_POS_INT_RE.fullmatch(raw)
    ):
        add(errors, relative, timeout_node, "timeout-minutes must be an integer from 1 to 360")
        return
    minutes = int(raw)
    if not 1 <= minutes <= 360:
        add(errors, relative, timeout_node, "timeout-minutes must be an integer from 1 to 360")


def check_runs_on(
    errors: list[Error], relative: str, job: yaml.MappingNode, job_node: yaml.Node
) -> None:
    runs_on = find(job, "runs-on")
    if runs_on is None:
        add(errors, relative, job_node, "job must set runs-on")
        return
    value = scalar_value(runs_on[1])
    if value is None or is_null_node(runs_on[1]):
        add(
            errors,
            relative,
            runs_on[1],
            "runs-on must be a pinned GitHub-hosted runner (for example ubuntu-24.04)",
        )
        return
    lower = value.lower()
    if "self-hosted" in lower:
        add(errors, relative, runs_on[1], "self-hosted runners are not allowed by current policy")
        return
    if not PINNED_HOSTED_RUNNER_RE.fullmatch(lower) or lower.endswith("-latest"):
        add(
            errors,
            relative,
            runs_on[1],
            f"runs-on '{value}' must be a pinned GitHub-hosted runner (for example ubuntu-24.04)",
        )


def check_steps(errors: list[Error], relative: str, job: yaml.MappingNode) -> None:
    steps = find(job, "steps")
    if steps is None:
        add(errors, relative, job, "job must define steps")
        return
    if not isinstance(steps[1], yaml.SequenceNode):
        add(errors, relative, steps[1], "steps must be a sequence")
        return
    if not steps[1].value:
        add(errors, relative, steps[1], "steps must not be empty")
        return

    for step in steps[1].value:
        if not isinstance(step, yaml.MappingNode):
            add(errors, relative, step, "step must be a mapping")
            continue
        uses = find(step, "uses")
        run_entry = find(step, "run")
        if uses is None and run_entry is None:
            add(errors, relative, step, "step must define either 'uses' or 'run'")
            continue
        if uses is not None and run_entry is not None:
            add(errors, relative, step, "step cannot define both 'uses' and 'run'")
        if uses is not None:
            check_action_ref(errors, relative, uses[1])
            check_checkout_credentials(errors, relative, step)
        if run_entry is not None:
            script = scalar_value(run_entry[1])
            if script is None or is_null_node(run_entry[1]):
                add(errors, relative, run_entry[1], "step 'run' must be a scalar")
            elif EXPRESSION_RE.search(script):
                add(
                    errors,
                    relative,
                    run_entry[1],
                    "do not interpolate ${{ ... }} directly in run:; pass values via env:",
                )


def check_jobs(
    errors: list[Error], relative: str, workflow: yaml.MappingNode, *, events: set[str]
) -> None:
    jobs = find(workflow, "jobs")
    if jobs is None:
        add(errors, relative, workflow, "workflow must define jobs")
        return
    if not isinstance(jobs[1], yaml.MappingNode):
        add(errors, relative, jobs[1], "jobs must be a mapping")
        return
    job_items = mapping_items(jobs[1])
    if not job_items:
        add(errors, relative, jobs[1], "jobs must not be empty")
        return

    for job_key, job in job_items:
        if not isinstance(job, yaml.MappingNode):
            add(errors, relative, job_key, f"job '{job_key.value}' must be a mapping")
            continue

        permissions = find(job, "permissions")
        if permissions is not None:
            check_permissions(errors, relative, permissions[1], "job", events=events)

        job_uses = find(job, "uses")
        job_steps = find(job, "steps")
        if job_uses is not None:
            check_action_ref(errors, relative, job_uses[1])
            if job_steps is not None:
                add(
                    errors,
                    relative,
                    job_steps[0],
                    f"reusable workflow job '{job_key.value}' cannot define steps",
                )
        else:
            check_runs_on(errors, relative, job, job_key)
            check_timeout(errors, relative, job, job_key)
            check_steps(errors, relative, job)


def _has_symlink_component(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return path.is_symlink()
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def check_workflow(path: Path, root: Path) -> list[Error]:
    relative = path.relative_to(root).as_posix()
    if _has_symlink_component(path, root) or not path.resolve().is_relative_to(root.resolve()):
        return [(relative, 1, "symlinked workflow file is not allowed")]
    try:
        workflow = yaml.compose(path.read_text(encoding="utf-8"), Loader=yaml.SafeLoader)
    except yaml.YAMLError as error:
        return [(relative, 1, f"invalid YAML: {error}")]

    errors: list[Error] = []
    if not isinstance(workflow, yaml.MappingNode):
        return [(relative, 1, "workflow must be a mapping")]

    check_ast_integrity(errors, relative, workflow)

    name_entry = find(workflow, "name")
    if (
        name_entry is None
        or is_null_node(name_entry[1])
        or not (scalar_value(name_entry[1]) or "").strip()
    ):
        add(errors, relative, workflow, "workflow must define a non-empty 'name'")

    permissions = find(workflow, "permissions")
    if permissions is None:
        add(errors, relative, workflow, "workflow must declare top-level permissions")
    else:
        check_permissions(errors, relative, permissions[1], "workflow")

    events = check_triggers(errors, relative, workflow)
    check_jobs(errors, relative, workflow, events=events)
    return errors


def workflow_paths(root: Path) -> list[Path]:
    github_dir = root / ".github"
    directory = root / WORKFLOW_DIR
    if github_dir.is_symlink() or directory.is_symlink() or not directory.is_dir():
        return []
    return sorted(
        [
            p
            for p in directory.iterdir()
            if p.suffix.lower() in (".yml", ".yaml") and (p.is_symlink() or p.is_file())
        ],
        key=lambda path: path.name,
    )


def main(argv: Sequence[str] | None = None) -> int:
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
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors: list[Error] = []
    if (root / ".github").is_symlink():
        errors.append((".github", 1, "symlinked .github directory is not allowed"))
    elif (root / WORKFLOW_DIR).is_symlink():
        errors.append((WORKFLOW_DIR.as_posix(), 1, "symlinked workflows directory is not allowed"))

    if errors:
        print(f"Workflow policy failed with {len(errors)} error(s):\n", file=sys.stderr)
        for relative, line, message in sorted(errors):
            print(f"  {relative}:{line}: {message}", file=sys.stderr)
        return 1

    paths = workflow_paths(root)
    if not paths:
        print(f"error: no workflows found under {root / WORKFLOW_DIR}", file=sys.stderr)
        return 1

    if args.strict:
        present = {path.name for path in paths if not path.is_symlink()}
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
