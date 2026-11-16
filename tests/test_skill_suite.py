"""Contract tests for the portable OpenCode workflow skill suite."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED = {
    "specification",
    "implementation-planning",
    "autonomous-execution",
    "systematic-debugging",
    "test-driven-development",
    "code-review",
    "delivery",
    "clean-code",
    "skill-authoring",
    "orchestration",
}

DOCS_WITH_TEST_REFERENCES = (
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "docs" / "opencode-orchestration.md",
    ROOT / "docs" / "release-process.md",
    ROOT / "docs" / "repository-settings.md",
)

TRIGGER_MATRIX = {
    "specification": {
        "positive": "turn this vague request into a testable specification; define non-goals and acceptance",
        "positive_terms": ("specification", "non-goals", "acceptance"),
        "negative": "fix this tiny, obvious CSS typo; the requirement is concrete",
        "negative_terms": ("tiny", "obvious", "concrete"),
    },
    "implementation-planning": {
        "positive": "produce an execution plan with small tasks and dependencies",
        "positive_terms": ("execution plan", "small tasks", "dependencies"),
        "negative": "make this trivial one-step edit",
        "negative_terms": ("trivial", "one-step"),
    },
    "autonomous-execution": {
        "positive": "execute the approved implementation plan and keep a ledger",
        "positive_terms": ("approved implementation plan", "ledger"),
        "negative": "do planning, spec discovery, or debugging an unknown cause",
        "negative_terms": ("planning", "spec discovery", "debugging"),
    },
    "systematic-debugging": {
        "positive": "find the root-cause and add a regression test",
        "positive_terms": ("root-cause", "regression test"),
        "negative": "do feature work or start guessing at symptoms",
        "negative_terms": ("feature work", "guessing"),
    },
    "test-driven-development": {
        "positive": "use red-green-refactor and watch the failing test",
        "positive_terms": ("red-green-refactor", "failing test"),
        "negative": "make a documentation-only or purely visual change",
        "negative_terms": ("documentation-only", "purely visual"),
    },
    "code-review": {
        "positive": "request a fresh-context review with P0/P1/P2 findings",
        "positive_terms": ("fresh-context review", "p0/p1/p2"),
        "negative": "give performative agreement or review your own work",
        "negative_terms": ("performative agreement", "own work"),
    },
    "delivery": {
        "positive": "merge the PR after cleanup with evidence",
        "positive_terms": ("pr", "merge", "cleanup"),
        "negative": "starting implementation or merging unverified work",
        "negative_terms": ("starting implementation", "unverified"),
    },
    "clean-code": {
        "positive": "refactor for readability and remove duplication",
        "positive_terms": ("refactor", "readability", "duplication"),
        "negative": "implement a new feature, review correctness, or do cosmetic rewrites",
        "negative_terms": ("new feature", "correctness", "cosmetic"),
    },
    "skill-authoring": {
        "positive": "write an OpenCode skill with a trigger description and baseline-vs-skill test",
        "positive_terms": ("opencode skill", "trigger description", "baseline-vs-skill"),
        "negative": "write application documentation or general agent rules",
        "negative_terms": ("application documentation", "general agent rules"),
    },
    "orchestration": {
        "positive": "route complex work; delegate and run parallel read-only investigation",
        "positive_terms": ("complex", "delegate", "parallel read-only"),
        "negative": "make a small sequential edit to a single obvious file",
        "negative_terms": ("small sequential", "single obvious file"),
    },
}


def skill_text(skill_id: str) -> str:
    return (SKILLS / skill_id / "SKILL.md").read_text(encoding="utf-8")


def skill_body(text: str) -> str:
    end = text.find("\n---\n", 4)
    return text[end + 5 :] if text.startswith("---\n") and end != -1 else text


def frontmatter(text: str) -> dict:
    assert text.startswith("---\n")
    end = text.find("\n---\n", 4)
    assert end != -1
    data = yaml.safe_load(text[4:end])
    assert isinstance(data, dict)
    return data


def test_suite_skills_and_frontmatter() -> None:
    assert {path.name for path in SKILLS.iterdir() if path.is_dir()} >= EXPECTED
    for skill_id in EXPECTED:
        data = frontmatter(skill_text(skill_id))
        assert data["compatibility"] == "opencode"
        assert data["license"] == "MIT"
        description = data["description"]
        assert 40 <= len(description) <= 1024
        assert any(
            phrase in description for phrase in ("Use when", "Use before", "Use after", "Use to", "Use for")
        )


def test_suite_has_workflow_and_handoff() -> None:
    for skill_id in EXPECTED:
        text = skill_text(skill_id)
        assert re.search(r"^## (Workflow|Process|The cycle|Design before prose|Decision order|Two modes|Evidence before claims|The task loop|Phase 1|Routing matrix)", text, re.M)
        assert (
            re.search(r"^## (Handoff|Output|Final gate|Delivery)", text, re.M)
            or skill_id == "delivery"
        )


def workflow_body(text: str) -> str:
    match = re.search(
        r"^## (Workflow|Process|The cycle|Design before prose|Decision order|Two modes|"
        r"Evidence before claims|The task loop|Phase 1|Routing matrix).*$",
        text,
        re.M,
    )
    assert match
    start = match.end()
    following = re.search(r"^## ", text[start:], re.M)
    return (text[start : start + following.start()] if following else text[start:]).strip()


def assert_workflow_content(skill_id: str, text: str) -> None:
    assert len(workflow_body(text)) >= 120, f"{skill_id} workflow is too thin"


def test_suite_workflow_sections_have_content() -> None:
    for skill_id in EXPECTED:
        assert_workflow_content(skill_id, skill_text(skill_id))


def test_empty_workflow_body_is_rejected() -> None:
    text = skill_text("orchestration")
    match = re.search(
        r"^## (Workflow|Process|The cycle|Design before prose|Decision order|Two modes|"
        r"Evidence before claims|The task loop|Phase 1|Routing matrix).*$",
        text,
        re.M,
    )
    assert match
    start = match.end()
    following = re.search(r"^## ", text[start:], re.M)
    end = start + following.start() if following else len(text)
    mutated = text[:start] + "\n\n" + text[end:]
    with pytest.raises(AssertionError):
        assert_workflow_content("orchestration", mutated)


def test_suite_is_portable_markdown() -> None:
    forbidden = ("plugin install", "bootstrap", "session-start", "opencode.json", "hooks/", "~/.claude")
    for skill_id in EXPECTED:
        text = skill_text(skill_id)
        for phrase in forbidden:
            assert phrase not in text, f"{skill_id} contains {phrase}"
        assert "Not for" in frontmatter(text)["description"]


def test_suite_tabletop_trigger_matrix() -> None:
    for skill_id, matrix in TRIGGER_MATRIX.items():
        description = frontmatter(skill_text(skill_id))["description"].casefold()
        positive_prompt = matrix["positive"].casefold()
        negative_prompt = matrix["negative"].casefold()
        for term in matrix["positive_terms"]:
            assert term in positive_prompt, (skill_id, "positive prompt", term)
            assert term in description, (skill_id, "positive trigger", term)
        not_for = description.split("not for", 1)[1]
        for term in matrix["negative_terms"]:
            assert term in negative_prompt, (skill_id, "negative prompt", term)
            assert term in not_for, (skill_id, "negative trigger", term)


def test_orchestration_hands_off_approved_plan() -> None:
    text = skill_text("orchestration")
    description = frontmatter(text)["description"].casefold()
    not_for = description.split("not for", 1)[1]
    assert "executing an approved implementation plan" in not_for
    assert "autonomous-execution" in description
    assert "autonomous-execution" in skill_body(text)


def test_suite_handoff_targets_exist() -> None:
    handoffs = {
        "specification": "implementation-planning",
        "implementation-planning": "autonomous-execution",
        "autonomous-execution": "code-review",
        "systematic-debugging": "test-driven-development",
        "test-driven-development": "clean-code",
        "code-review": "delivery",
        "clean-code": "test-driven-development",
    }
    for source, target in handoffs.items():
        assert (SKILLS / target / "SKILL.md").is_file()
        assert f"`{target}`" in skill_text(source)


def test_suite_is_listed_in_readme_and_agents() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    actual = {
        path.name
        for path in SKILLS.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    listed = set(
        re.findall(r"\[`([a-z0-9-]+)`\]\(skills/\1/SKILL\.md\)", readme)
    )
    assert listed == actual
    assert f"{len(actual)} portable skills" in readme
    for skill_id in actual:
        assert skill_id in agents


def test_v2_planning_and_execution_contracts() -> None:
    required = {
        "specification": ("Approaches:", "Review focus:"),
        "implementation-planning": (
            "Global constraints:",
            "Review focus:",
            "Interfaces:",
            "Consumes:",
            "Produces:",
            "docs/plans/",
            "Expected:",
            "Checkpoint",
        ),
        "autonomous-execution": (
            "progress.md",
            "Task briefs",
            "Ruling:",
            "3-strike",
            "whole-branch",
            "BASE",
        ),
        "orchestration": (
            "Independent failure dispatch",
            "One brief, not the whole plan",
        ),
        "code-review": (
            "Tests first",
            "Five axes",
            "Mutation check",
            "Structural remedies",
            "Change size",
        ),
        "delivery": (
            "Evidence required",
            "Post-merge verification",
            "Change summary",
        ),
        "clean-code": ("Scope discipline", "Simplicity check"),
        "skill-authoring": (
            "Trigger mining",
            "Record each evaluation",
            "Version a material",
        ),
    }
    for skill_id, phrases in required.items():
        text = skill_text(skill_id)
        for phrase in phrases:
            assert phrase in text, (skill_id, phrase)


def test_v2_state_is_project_local() -> None:
    assert "docs/plans/" in skill_text("implementation-planning")
    assert "docs/plans/" in skill_text("autonomous-execution")
    assert "progress.md" in skill_text("autonomous-execution")
    assert "hooks:" not in skill_text("autonomous-execution")


def test_docs_test_paths_exist() -> None:
    for path in DOCS_WITH_TEST_REFERENCES:
        text = path.read_text(encoding="utf-8")
        for relative in set(re.findall(r"`(tests/[^`\s]+\.py)`", text)):
            assert (ROOT / relative).is_file(), (path.relative_to(ROOT), relative)
