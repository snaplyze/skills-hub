"""Contract tests for the portable OpenCode workflow skill suite."""

from __future__ import annotations

import re
from pathlib import Path

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


def skill_text(skill_id: str) -> str:
    return (SKILLS / skill_id / "SKILL.md").read_text(encoding="utf-8")


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


def test_suite_is_portable_markdown() -> None:
    forbidden = ("plugin install", "bootstrap", "session-start", "opencode.json", "hooks/", "~/.claude")
    for skill_id in EXPECTED:
        text = skill_text(skill_id)
        for phrase in forbidden:
            assert phrase not in text, f"{skill_id} contains {phrase}"
        assert "Not for" in frontmatter(text)["description"]


def test_suite_tabletop_trigger_matrix() -> None:
    triggers = {
        "specification": ("request", "specification"),
        "implementation-planning": ("plan", "tasks"),
        "autonomous-execution": ("execute", "plan"),
        "systematic-debugging": ("bug", "root-cause"),
        "test-driven-development": ("test", "red-green-refactor"),
        "code-review": ("review", "feedback"),
        "delivery": ("deliver", "merge"),
        "clean-code": ("refactor", "readability"),
        "skill-authoring": ("skill", "trigger"),
        "orchestration": ("complex", "native"),
    }
    for skill_id, words in triggers.items():
        description = frontmatter(skill_text(skill_id))["description"].lower()
        assert all(word in description for word in words), (skill_id, words)


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
    for skill_id in EXPECTED:
        assert f"skills/{skill_id}/SKILL.md" in readme
        assert skill_id in agents
