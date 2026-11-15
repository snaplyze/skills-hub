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
            phrase in description for phrase in ("Use when", "Use before", "Use after", "Use to")
        )


def test_suite_has_workflow_and_handoff() -> None:
    for skill_id in EXPECTED:
        text = skill_text(skill_id)
        assert re.search(r"^## (Workflow|Process|The cycle|Design before prose|Decision order|Two modes|Evidence before claims|The task loop|Phase 1)", text, re.M)
        assert (
            re.search(r"^## (Handoff|Output|Final gate|Delivery)", text, re.M)
            or skill_id == "delivery"
        )


def test_suite_is_portable_markdown() -> None:
    for skill_id in EXPECTED:
        text = skill_text(skill_id)
        assert "hooks/" not in text
        assert "opencode.json" not in text
        assert "~/.claude" not in text


def test_suite_is_listed_in_readme_and_agents() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for skill_id in EXPECTED:
        assert f"skills/{skill_id}/SKILL.md" in readme
        assert skill_id in agents
