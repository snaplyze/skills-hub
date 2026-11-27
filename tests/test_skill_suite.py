"""Contract tests for the portable Antigravity and OpenCode skill suite."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

WORKFLOW_SKILLS = frozenset(
    {
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
)

ALL_SKILLS = tuple(
    sorted(
        path.name for path in SKILLS.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    )
)

WORKFLOW_HEADING_RE = re.compile(
    r"^## (Workflow|Process|The cycle|Design before prose|Decision order|Two modes|"
    r"Evidence before claims|The task loop|Phase 1|Routing matrix).*$",
    re.M,
)
HANDOFF_HEADING_RE = re.compile(r"^## (Handoff|Output|Final gate)", re.M)

DOCS_WITH_TEST_REFERENCES = (
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "docs" / "antigravity-orchestration.md",
    ROOT / "docs" / "opencode-orchestration.md",
    ROOT / "docs" / "release-process.md",
    ROOT / "docs" / "repository-settings.md",
)

TRIGGER_MATRIX = {
    "frontend-design": {
        "positive": "design a distinctive accessible web UI landing page with responsive typography, color tokens, and motion",
        "negative_terms": ("backend-only",),
    },
    "specification": {
        "positive": "turn this ambiguous feature request into a testable specification with outcomes, non-goals, and acceptance criteria",
        "negative_terms": ("tiny", "obvious", "concrete"),
    },
    "implementation-planning": {
        "positive": "produce an execution plan after specification with small tasks, exact files, interfaces, and dependencies",
        "negative_terms": ("trivial", "one-step"),
    },
    "autonomous-execution": {
        "positive": "execute the approved implementation plan autonomously with small commits, a visible ledger, and stop conditions",
        "negative_terms": ("planning", "spec discovery", "debugging"),
    },
    "systematic-debugging": {
        "positive": "debug this crash and test failure to isolate root cause with a falsifiable hypothesis and regression test",
        "negative_terms": ("feature work", "guessing"),
    },
    "test-driven-development": {
        "positive": "implement this behavior change with red-green-refactor, a failing behavioral test first, and minimal implementation",
        "negative_terms": ("documentation-only", "purely visual"),
    },
    "code-review": {
        "positive": "request a fresh-context review before merging with P0/P1/P2 findings covering correctness, security, and edge cases",
        "negative_terms": ("performative agreement", "own work"),
    },
    "delivery": {
        "positive": "deliver this verified work through a PR, required checks, no-bypass merge, cleanup, and completion report",
        "negative_terms": ("starting implementation", "unverified"),
    },
    "clean-code": {
        "positive": "refactor existing code for readability, boundaries, duplication, and coupling while preserving behavior",
        "negative_terms": ("new feature", "correctness", "cosmetic"),
    },
    "skill-authoring": {
        "positive": "create a portable agent skill for Antigravity with trigger description, progressive disclosure, baseline-vs-skill evaluation, and pressure tests",
        "negative_terms": ("application documentation", "general agent rules"),
    },
    "orchestration": {
        "positive": "route complex cross-cutting coding work by deciding whether to delegate bounded subagents, run a dynamic workflow, or recommend a built-in Antigravity orchestrator",
        "negative_terms": ("small sequential", "single obvious file"),
    },
}

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "do",
        "for",
        "from",
        "in",
        "into",
        "is",
        "it",
        "its",
        "not",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "use",
        "when",
        "where",
        "whether",
        "with",
    }
)


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


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]*", text.casefold())
        if len(token) >= 2 and token not in STOPWORDS
    }


def _route_score(prompt: str, description: str) -> float:
    lower = description.casefold()
    positive_part, _, negative_part = lower.partition("not for")
    prompt_tokens = _tokens(prompt)
    pos_hits = len(prompt_tokens & _tokens(positive_part))
    neg_hits = len(prompt_tokens & _tokens(negative_part))
    return pos_hits - 1.5 * neg_hits


def test_suite_skills_and_frontmatter() -> None:
    skill_dirs = sorted(path.name for path in SKILLS.iterdir() if path.is_dir())
    assert skill_dirs == list(ALL_SKILLS), "every directory under skills/ must contain SKILL.md"
    discovered = set(ALL_SKILLS)
    assert discovered >= WORKFLOW_SKILLS | {"frontend-design"}
    for skill_id in ALL_SKILLS:
        data = frontmatter(skill_text(skill_id))
        assert data["name"] == skill_id
        assert data["compatibility"] == "agentskills"
        assert data["license"] == "MIT"
        description = data["description"]
        assert 40 <= len(description) <= 1024
        if skill_id in WORKFLOW_SKILLS:
            assert any(
                phrase in description
                for phrase in ("Use when", "Use before", "Use after", "Use to", "Use for")
            ), skill_id


def test_suite_has_workflow_and_handoff() -> None:
    for skill_id in ALL_SKILLS:
        text = skill_text(skill_id)
        assert WORKFLOW_HEADING_RE.search(text), f"{skill_id} missing workflow heading"
        assert HANDOFF_HEADING_RE.search(text), f"{skill_id} missing handoff/output heading"


def workflow_body(text: str) -> str:
    match = WORKFLOW_HEADING_RE.search(text)
    assert match
    start = match.end()
    following = re.search(r"^## ", text[start:], re.M)
    return (text[start : start + following.start()] if following else text[start:]).strip()


def assert_workflow_content(skill_id: str, text: str) -> None:
    assert len(workflow_body(text)) >= 120, f"{skill_id} workflow is too thin"


def test_suite_workflow_sections_have_content() -> None:
    for skill_id in ALL_SKILLS:
        assert_workflow_content(skill_id, skill_text(skill_id))


def test_empty_workflow_body_is_rejected() -> None:
    text = skill_text("orchestration")
    match = WORKFLOW_HEADING_RE.search(text)
    assert match
    start = match.end()
    following = re.search(r"^## ", text[start:], re.M)
    end = start + following.start() if following else len(text)
    mutated = text[:start] + "\n\n" + text[end:]
    with pytest.raises(AssertionError):
        assert_workflow_content("orchestration", mutated)


def test_suite_is_portable_markdown() -> None:
    forbidden = (
        "opencode",
        "sessionid",
        "session.move",
        "worktree_remove",
        "<background-result>",
        "`explore`",
        "`general`",
        "plugin install",
        "bootstrap",
        "session-start",
        "hooks/",
        "~/.claude",
        ".superpowers",
        "docs/superpowers",
    )
    for skill_id in ALL_SKILLS:
        skill_root = SKILLS / skill_id
        assert "Not for" in frontmatter(skill_text(skill_id))["description"], skill_id
        for md_file in sorted(skill_root.rglob("*.md")):
            lowered = md_file.read_text(encoding="utf-8").casefold()
            rel = md_file.relative_to(ROOT)
            for phrase in forbidden:
                assert phrase not in lowered, f"{rel} contains forbidden phrase {phrase!r}"


def test_antigravity_orchestration_contract() -> None:
    text = skill_text("orchestration")
    for required in (
        "invoke_subagent",
        "define_subagent",
        "send_message",
        "manage_subagents",
        "run_workflow",
        "`research`",
        "`browser`",
        "`self`",
        "/swarm",
        "/boost",
        "/teamwork",
    ):
        assert required in text, f"orchestration missing Antigravity primitive {required!r}"
    for legacy_agent in ("`explore`", "`general`"):
        assert legacy_agent not in text, f"orchestration still names {legacy_agent}"


def test_suite_trigger_matrix_and_cross_skill_isolation() -> None:
    assert set(TRIGGER_MATRIX) == set(ALL_SKILLS)
    descriptions = {
        skill_id: frontmatter(skill_text(skill_id))["description"] for skill_id in ALL_SKILLS
    }
    for skill_id, matrix in TRIGGER_MATRIX.items():
        description_cf = descriptions[skill_id].casefold()
        assert "not for" in description_cf, skill_id
        not_for = description_cf.split("not for", 1)[1]
        for term in matrix["negative_terms"]:
            assert term in not_for, (skill_id, "missing negative trigger", term)

        # Cross-skill isolation: skill_id must uniquely rank #1 for its positive prompt.
        scores = {
            candidate: _route_score(matrix["positive"], desc)
            for candidate, desc in descriptions.items()
        }
        best_score = max(scores.values())
        winners = [candidate for candidate, score in scores.items() if score == best_score]
        assert winners == [skill_id], (
            f"prompt for {skill_id!r} routed to {winners!r} instead (scores={scores})"
        )

    # Adversarial boundary routing: verify Not-for penalties isolate competing skills.
    adversarial_cases = (
        (
            "UI visual design audit for responsive color tokens and layout contrast",
            "frontend-design",
            ("code-review", "clean-code"),
        ),
        (
            "diagnose an unknown-cause crash and locate root cause before fixing",
            "systematic-debugging",
            ("test-driven-development", "autonomous-execution"),
        ),
        (
            "execute an approved implementation plan with small commits and a ledger",
            "autonomous-execution",
            ("orchestration", "implementation-planning"),
        ),
    )
    for prompt, expected_winner, competitors in adversarial_cases:
        winner_score = _route_score(prompt, descriptions[expected_winner])
        for competitor in competitors:
            comp_score = _route_score(prompt, descriptions[competitor])
            assert winner_score > comp_score, (
                f"adversarial prompt routed {competitor!r} ({comp_score}) >= "
                f"{expected_winner!r} ({winner_score})"
            )


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
    actual = set(ALL_SKILLS)
    listed = set(re.findall(r"\[`([a-z0-9-]+)`\]\(skills/\1/SKILL\.md\)", readme))
    assert listed == actual
    assert f"{len(actual)} portable skills" in readme
    for skill_id in actual:
        assert skill_id in agents


V2_REQUIRED = {
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


def v2_contract_errors(skill_id: str, text: str) -> list[str]:
    return [phrase for phrase in V2_REQUIRED[skill_id] if phrase not in text]


def test_v2_planning_and_execution_contracts() -> None:
    for skill_id in V2_REQUIRED:
        errors = v2_contract_errors(skill_id, skill_text(skill_id))
        assert not errors, (skill_id, errors)


def test_v2_contract_mutation_is_detected() -> None:
    text = skill_text("implementation-planning")
    mutated = text.replace("Global constraints:", "")
    assert mutated != text
    assert "Global constraints:" in v2_contract_errors("implementation-planning", mutated)


def test_v2_state_is_project_local() -> None:
    """Verify plan and ledger paths stay project-local at document level (wrap-independent)."""
    for skill_id in ("implementation-planning", "autonomous-execution", "orchestration"):
        text = skill_text(skill_id)
        assert "docs/plans/" in text, skill_id
    for skill_id in ("autonomous-execution", "orchestration"):
        text = skill_text(skill_id)
        assert "docs/plans/<plan-basename>.progress.md" in text, skill_id
    assert "hooks:" not in skill_text("autonomous-execution")
    assert "Never hide it in a tool-owned directory" in skill_text("autonomous-execution")


def test_docs_test_paths_exist() -> None:
    for path in DOCS_WITH_TEST_REFERENCES:
        text = path.read_text(encoding="utf-8")
        for relative in set(re.findall(r"`(tests/[^`\s]+\.py)`", text)):
            assert (ROOT / relative).is_file(), (path.relative_to(ROOT), relative)


def test_aud51_skills_paths_tokens_guardrails_and_portability() -> None:
    # 1. No skill markdown may use `../` backtick paths that bypass LOCAL_REF_RE.
    for md_file in sorted(SKILLS.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        assert not re.search(r"`\.\./", text), f"{md_file.relative_to(ROOT)} uses `../` path"

    # 2. design-system.md layout tokens and contrast summary must match assets/tokens.css.
    tokens_css = (SKILLS / "frontend-design" / "assets" / "tokens.css").read_text(encoding="utf-8")
    design_sys = (SKILLS / "frontend-design" / "references" / "design-system.md").read_text(
        encoding="utf-8"
    )
    for prop in ("--container-2xl", "--gutter", "--measure", "--header-height"):
        css_match = re.search(rf"{re.escape(prop)}:\s*([^;]+);", tokens_css)
        assert css_match, f"missing {prop} in tokens.css"
        expected_val = css_match.group(1).strip()
        doc_matches = re.findall(rf"{re.escape(prop)}:\s*([^;]+);", design_sys)
        assert doc_matches, f"missing {prop} in design-system.md"
        for found in doc_matches:
            assert found.strip() == expected_val, (prop, found.strip(), expected_val)
    assert "64 light/dark pairs and 27 semantic combinations" in design_sys

    # 3. responsive-mobile.md TOC includes Mobile checklist.
    mobile_doc = (SKILLS / "frontend-design" / "references" / "responsive-mobile.md").read_text(
        encoding="utf-8"
    )
    assert "- [Mobile checklist](#mobile-checklist)" in mobile_doc

    # 4. Untrusted-data guardrails & code-review secret-redaction rule.
    for skill_id in ("frontend-design", "orchestration", "code-review"):
        assert "untrusted data" in skill_text(skill_id).casefold(), skill_id
    review_text = skill_text("code-review")
    review_order = review_text.split("## Review order", 1)[1].split("## Five axes", 1)[0]
    receiving_fb = review_text.split("## Receiving feedback", 1)[1].split("## Red flags", 1)[0]
    assert "untrusted data" in review_order.casefold()
    assert "untrusted data" in receiving_fb.casefold()
    assert "`file:line`" in review_order
    assert "without echoing secret values" in review_order

    # 5. Portable orchestration wording & autonomous-execution field sync.
    orch_text = skill_text("orchestration")
    assert "user-global harness configuration" in orch_text
    assert "user-global Antigravity configuration" not in orch_text
    assert "native equivalents" in orch_text

    auto_text = skill_text("autonomous-execution")
    isolation_sec = auto_text.split("## Isolation", 1)[1].split("## Review gate", 1)[0]
    subagents_sec = auto_text.split("## Subagents and parallelism", 1)[1].split(
        "## Stop conditions", 1
    )[0]
    assert "native equivalents" in isolation_sec
    assert "native equivalents" in subagents_sec
    assert "owner/session" in auto_text
    assert "deferred items" in auto_text
    assert "workspace mode (`inherit` | `share` | `branch`)" in auto_text
