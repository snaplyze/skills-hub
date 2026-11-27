from __future__ import annotations

import atexit
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts import validate

REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORE = shutil.ignore_patterns(
    ".git",
    ".ruff_cache",
    "__pycache__",
    ".pytest_cache",
    ".playwright-cli",
    ".mypy_cache",
    ".venv",
    "venv",
    "node_modules",
    ".gemini",
    ".agents",
    ".opencode",
    ".claude",
    ".env",
    ".env.*",
    "secrets",
    "*.pyc",
    "tests",
)
_TEMPLATE_DIR: Path | None = None
_FRONTEND_SKILL_TEMPLATE: Path | None = None
_CONTRAST_MODULE: object | None = None


def _clean_template() -> Path:
    global _TEMPLATE_DIR
    if _TEMPLATE_DIR is None:
        base = Path(tempfile.mkdtemp(prefix="skills-hub-val-tpl-"))
        atexit.register(shutil.rmtree, base, True)
        dest = base / "repo"
        shutil.copytree(REPO_ROOT, dest, ignore=IGNORE)
        _TEMPLATE_DIR = dest
    return _TEMPLATE_DIR


def _frontend_skill_template() -> Path:
    global _FRONTEND_SKILL_TEMPLATE
    if _FRONTEND_SKILL_TEMPLATE is None:
        base = Path(tempfile.mkdtemp(prefix="skills-hub-fe-tpl-"))
        atexit.register(shutil.rmtree, base, True)
        dest = base / "frontend-design"
        shutil.copytree(REPO_ROOT / "skills" / "frontend-design", dest, ignore=IGNORE)
        _FRONTEND_SKILL_TEMPLATE = dest
    return _FRONTEND_SKILL_TEMPLATE


def _contrast_module():
    global _CONTRAST_MODULE
    if _CONTRAST_MODULE is None:
        _CONTRAST_MODULE = validate.load_contrast_module(
            REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py"
        )
    return _CONTRAST_MODULE


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(_clean_template(), destination)
    return destination


def copy_frontend_skill(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(_frontend_skill_template(), repo / "skills" / "frontend-design")
    return repo


def copy_contrast_assets(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    assets = repo / "skills" / "frontend-design" / "assets"
    assets.mkdir(parents=True)
    src = REPO_ROOT / "skills" / "frontend-design" / "assets"
    shutil.copy2(src / "token-contrast-pairs.json", assets / "token-contrast-pairs.json")
    shutil.copy2(src / "tokens.css", assets / "tokens.css")
    return repo


def run_validate(repo: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate.py", *extra_args],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def assert_skill_passes(repo: Path, skill_id: str = "frontend-design") -> None:
    errors: list[str] = []
    validate.check_skill(repo / "skills" / skill_id, errors, root=repo)
    assert not errors, "\n".join(errors)


def assert_skill_fails(repo: Path, *needles: str, skill_id: str = "frontend-design") -> None:
    errors: list[str] = []
    validate.check_skill(repo / "skills" / skill_id, errors, root=repo)
    assert errors, f"expected skill validation failure matching {needles!r}, got 0 errors"
    joined = "\n".join(errors)
    for needle in needles:
        assert needle in joined, joined


def assert_contrast_fixture_passes(repo: Path) -> None:
    errors: list[str] = []
    validate.check_contrast_fixture(
        fixture_path(repo),
        repo / "skills" / "frontend-design" / "assets" / "tokens.css",
        _contrast_module(),
        errors,
        root=repo,
    )
    assert not errors, "\n".join(errors)


def assert_contrast_fixture_fails(repo: Path, *needles: str) -> None:
    errors: list[str] = []
    validate.check_contrast_fixture(
        fixture_path(repo),
        repo / "skills" / "frontend-design" / "assets" / "tokens.css",
        _contrast_module(),
        errors,
        root=repo,
    )
    assert errors, f"expected contrast fixture failure matching {needles!r}, got 0 errors"
    joined = "\n".join(errors)
    for needle in needles:
        assert needle in joined, joined


def append_to_skill(repo: Path, text: str) -> None:
    path = repo / "skills" / "frontend-design" / "SKILL.md"
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


def fixture_path(repo: Path) -> Path:
    return repo / "skills" / "frontend-design" / "assets" / "token-contrast-pairs.json"


def load_fixture(repo: Path) -> dict:
    return json.loads(fixture_path(repo).read_text(encoding="utf-8"))


def save_fixture(repo: Path, data: dict) -> None:
    fixture_path(repo).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_reading_sets(repo: Path, data: dict) -> Path:
    path = repo / "skills" / "frontend-design" / "assets" / "reading-sets.json"
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def load_reading_sets(repo: Path) -> dict:
    path = repo / "skills" / "frontend-design" / "assets" / "reading-sets.json"
    return json.loads(path.read_text(encoding="utf-8"))


def relax_reading_budget(repo: Path) -> None:
    skill = repo / "skills" / "frontend-design"
    excluded = {}
    for path in sorted(skill.rglob("*.md")):
        relative = path.relative_to(skill).as_posix()
        if relative != "SKILL.md":
            excluded[relative] = "test fixture"
    write_reading_sets(
        repo,
        {
            "sets": {
                "new-page": ["SKILL.md"],
                "component-state": ["SKILL.md"],
            },
            "excluded": excluded,
        },
    )


def test_repository_validates_on_current_interpreter(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    result = run_validate(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed." in result.stdout


def test_cli_exits_one_on_validation_error(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(repo, "\n\n[broken](references/does-not-exist.md)\n")
    result = run_validate(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "broken link" in result.stderr


def test_skill_link_formats_pass(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(
        repo,
        '\n\n[local](references/accessibility.md "Accessibility reference")\n'
        "[full][accessibility]\n"
        "[collapsed][]\n"
        "[![badge](https://example.invalid/badge.svg)](references/accessibility.md)\n"
        "\n[accessibility]: references/accessibility.md#testing-protocol\n"
        "[collapsed]: references/accessibility.md\n",
    )
    assert_skill_passes(repo)

    readme = repo / "README.md"
    readme.write_text("# Root\n\n[root](/README.md)\n", encoding="utf-8")
    errs: list[str] = []
    validate.check_markdown_links(readme, errs, root=repo)
    assert not errs, errs


@pytest.mark.parametrize(
    ("text", "needle"),
    [
        ("\n\n[broken](references/does-not-exist.md)\n", "broken link"),
        ("\n\n[broken](#does-not-exist)\n", "missing anchor"),
        (
            "\n\n[broken](references/accessibility.md#does-not-exist)\n",
            "missing anchor",
        ),
        ("\n\n[escape](/README.md)\n", "escapes skill directory"),
        ("\n\n[escape](../../README.md)\n", "escapes skill directory"),
        (
            '\n\n[broken](references/does-not-exist.md "A title")\n',
            "broken link",
        ),
        (
            '\n\n[broken][missing]\n\n[missing]: references/does-not-exist.md "A title"\n',
            "broken link",
        ),
        (
            "\n\n[unused]: references/does-not-exist.md\n",
            "broken link",
        ),
        (
            "\n\n[![badge](https://example.invalid/x.svg)](references/does-not-exist.md)\n",
            "broken link",
        ),
    ],
)
def test_skill_link_mutations_fail(tmp_path: Path, text: str, needle: str) -> None:
    repo = copy_frontend_skill(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(repo, text)
    assert_skill_fails(repo, needle)


def test_duplicate_and_setext_heading_slugs(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(
        repo,
        "\n\n## Duplicate Check\n"
        "[first](#duplicate-check)\n"
        "## Duplicate Check\n"
        "[second](#duplicate-check-1)\n"
        "\nSetext Heading\n"
        "--------------\n"
        "[setext](#setext-heading)\n",
    )
    assert_skill_passes(repo)

    append_to_skill(repo, "\n[bad duplicate](#duplicate-check-2)\n")
    assert_skill_fails(repo, "missing anchor")


def test_empty_skill_body_fails(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "frontend-design"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: frontend-design\n"
        "description: A deliberately long description for the empty-body mutation.\n"
        "license: MIT\n"
        "---\n",
        encoding="utf-8",
    )
    assert_skill_fails(tmp_path, "body is empty")


@pytest.mark.parametrize(
    ("mutation", "needle"),
    [
        (
            lambda text: text.replace("name: frontend-design", "name: [unterminated", 1),
            "invalid frontmatter",
        ),
        (
            lambda text: text.replace("name: frontend-design", "name: Frontend Design", 1),
            "must be lowercase kebab-case",
        ),
        (
            lambda text: text.replace("name: frontend-design", "name: wrong-id", 1),
            "must match directory name",
        ),
        (
            lambda text: text.replace("name: frontend-design", f"name: {'a' * 65}", 1),
            "must be lowercase kebab-case (1-64 chars)",
        ),
        (
            lambda text: text.replace("\n---\n", "\n", 1),
            "invalid frontmatter",
        ),
        (
            lambda text: text.replace("license: MIT\n", "license: MIT\nunexpected: true\n", 1),
            "unknown frontmatter key",
        ),
    ],
)
def test_frontmatter_mutations_fail(
    tmp_path: Path,
    mutation,
    needle: str,
) -> None:
    repo = copy_frontend_skill(tmp_path)
    skill = repo / "skills" / "frontend-design" / "SKILL.md"
    skill.write_text(mutation(skill.read_text(encoding="utf-8")), encoding="utf-8")
    assert_skill_fails(repo, needle)


def test_agents_and_pull_request_template_links_are_checked(tmp_path: Path) -> None:
    agents_repo = tmp_path / "agents"
    agents_repo.mkdir()
    for name in (
        "README.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "GOVERNANCE.md",
        "THIRD_PARTY_NOTICES.md",
    ):
        (agents_repo / name).write_text("# Doc\n", encoding="utf-8")
    agents_file = agents_repo / "AGENTS.md"
    agents_file.write_text(
        (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        + "\n[broken](/docs/does-not-exist.md)\n",
        encoding="utf-8",
    )
    root_errs: list[str] = []
    validate.check_root_docs(root_errs, root=agents_repo)
    assert any("AGENTS.md: broken link -> /docs/does-not-exist.md" in e for e in root_errs), (
        root_errs
    )

    template_repo = tmp_path / "template"
    (template_repo / ".github").mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "CONTRIBUTING.md", template_repo / "CONTRIBUTING.md")
    template = template_repo / ".github" / "PULL_REQUEST_TEMPLATE.md"
    shutil.copy2(REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md", template)
    ok_errs: list[str] = []
    validate.check_github_docs(ok_errs, root=template_repo)
    assert ok_errs == []

    template.write_text(
        template.read_text(encoding="utf-8").replace("../CONTRIBUTING.md", "../DOES_NOT_EXIST.md"),
        encoding="utf-8",
    )
    gh_errs: list[str] = []
    validate.check_github_docs(gh_errs, root=template_repo)
    assert any("broken link" in e for e in gh_errs), gh_errs


def test_external_links_are_skipped(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(
        repo,
        "\n\n[external](https://example.invalid/this-page-does-not-exist)\n",
    )
    assert_skill_passes(repo)


def test_fixture_shrink_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data["pairs"].pop()
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "expected 64 pairs")


def test_fixture_theme_counts_fail(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data["pairs"][0]["label"] = "dark: theme count probe"
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "expected 32 light pairs")


def test_fixture_duplicate_label_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data["pairs"][1]["label"] = data["pairs"][0]["label"]
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "duplicates label")


@pytest.mark.parametrize(
    ("mutation", "needle"),
    [
        (lambda pair: pair.pop("fg"), "missing field(s): fg"),
        (lambda pair: pair.update({"bg": "#zzzzzz"}), "invalid bg color"),
    ],
)
def test_fixture_shape_mutations_fail(
    tmp_path: Path,
    mutation,
    needle: str,
) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    mutation(data["pairs"][0])
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, needle)


def test_missing_contrast_script_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    errs: list[str] = []
    validate.check_contrast(errs, root=repo)
    assert any("missing contrast checker" in e for e in errs), errs


def test_new_semantic_token_without_coverage_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    tokens.write_text(
        tokens.read_text(encoding="utf-8") + "\n:root {\n  --color-mystery: var(--brand-500);\n}\n",
        encoding="utf-8",
    )
    assert_contrast_fixture_fails(repo, "--color-mystery", "without contrast coverage")


@pytest.mark.parametrize(
    ("old", "new", "needle"),
    [
        (
            "--neutral-500: #6a6459;",
            "--neutral-500: #6f695e;",
            "light: text-subtle / warning-surface",
        ),
        (
            "--brand-600: #227164;",
            "--brand-600: #237366;",
            "light: accent / warning-surface",
        ),
        (
            "--neutral-450: #817b70;",
            "--neutral-450: #8a8478;",
            "light: border-strong / warning-surface (ui)",
        ),
        (
            "--neutral-400: #a29c8e;",
            "--neutral-400: #9b9587;",
            "dark: text-subtle / success-surface",
        ),
    ],
)
def test_semantic_combination_regressions_fail(
    tmp_path: Path,
    old: str,
    new: str,
    needle: str,
) -> None:
    repo = copy_contrast_assets(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    original = tokens.read_text(encoding="utf-8")
    assert old in original
    tokens.write_text(original.replace(old, new, 1), encoding="utf-8")
    assert_contrast_fixture_fails(repo, needle)


def test_new_semantic_token_with_coverage_passes(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    tokens.write_text(
        tokens.read_text(encoding="utf-8")
        + '\n:root {\n  --color-mystery: var(--neutral-900);\n}\n[data-theme="dark"] {\n  --color-mystery: var(--neutral-50);\n}\n',
        encoding="utf-8",
    )
    data = load_fixture(repo)
    data["combinations"].extend(
        [
            {
                "label": "light: mystery / canvas",
                "theme": "light",
                "fg": "--color-mystery",
                "bg": "--color-canvas",
                "size": "normal",
            },
            {
                "label": "dark: mystery / canvas",
                "theme": "dark",
                "fg": "--color-mystery",
                "bg": "--color-canvas",
                "size": "normal",
            },
        ]
    )
    data["coverage"]["--color-mystery"] = [
        "light: mystery / canvas",
        "dark: mystery / canvas",
    ]
    save_fixture(repo, data)
    assert_contrast_fixture_passes(repo)


def test_single_theme_coverage_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data["coverage"]["--color-surface-raised"] = ["dark: text / surface-raised"]
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "missing light theme coverage")


def test_string_aware_css_parser_and_var_fallback() -> None:
    css = (
        ':root, [data-theme="light"] {\n'
        '  --font-note: "a { ; } /* not comment */";\n'
        "  --base: #111111;\n"
        "  --color-a: var(--base);\n"
        "  --color-b: var(--missing, #222222);\n"
        "}\n"
        ':root[data-theme="dark"] {\n'
        "  --color-a: #eeeeee;\n"
        "}\n"
        "@media (prefers-color-scheme: dark) {\n"
        "  :root { --color-media-only: #333333; }\n"
        "}\n"
    )
    decls = validate.css_declarations(css)
    tokens = validate.semantic_tokens_from_declarations(decls)
    assert tokens == {"--color-a", "--color-b"}
    resolved = validate.resolve_theme_tokens_from_declarations(decls)
    assert resolved["light"]["--color-a"] == "#111111"
    assert resolved["light"]["--color-b"] == "#222222"
    assert resolved["dark"]["--color-a"] == "#eeeeee"


def test_token_literal_parity_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    original = tokens.read_text(encoding="utf-8")
    assert "--neutral-50: #f7f6f2;" in original
    tokens.write_text(
        original.replace("--neutral-50: #f7f6f2;", "--neutral-50: #000000;", 1),
        encoding="utf-8",
    )
    assert_contrast_fixture_fails(repo, "does not match --color-canvas")


def test_new_semantic_token_with_unrelated_coverage_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    tokens.write_text(
        tokens.read_text(encoding="utf-8")
        + "\n:root {\n  --color-mystery: var(--neutral-900);\n}\n",
        encoding="utf-8",
    )
    data = load_fixture(repo)
    data["coverage"]["--color-mystery"] = ["light: text / canvas"]
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "does not test --color-mystery")


def test_missing_coverage_mapping_fails(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data.pop("coverage")
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "needs a 'coverage' mapping")


def write_simple_skill(
    repo: Path,
    skill_id: str = "simple-skill",
    body: str = "# Simple\n\nKeep this skill small.\n",
) -> Path:
    skill = repo / "skills" / skill_id
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {skill_id}\n"
        "description: Use when a small test skill needs a deterministic validator contract.\n"
        "license: MIT\n"
        "compatibility: agentskills\n"
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return skill


def test_simple_skill_without_manifest_passes(tmp_path: Path) -> None:
    write_simple_skill(tmp_path)
    assert_skill_passes(tmp_path, "simple-skill")


def test_simple_skill_oversize_fails(tmp_path: Path) -> None:
    write_simple_skill(tmp_path, body="#" + ("x" * 32769))
    assert_skill_fails(tmp_path, "hard limit is 32768 B", skill_id="simple-skill")


def test_simple_skill_references_without_manifest_fails(tmp_path: Path) -> None:
    skill = write_simple_skill(tmp_path, body="# Simple\n\nRead `references/extra.md`.\n")
    references = skill / "references"
    references.mkdir()
    (references / "extra.md").write_text("# Extra\n", encoding="utf-8")
    assert_skill_fails(tmp_path, "missing reading-set manifest", skill_id="simple-skill")


def test_reading_sets_missing_manifest_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    (repo / "skills" / "frontend-design" / "assets" / "reading-sets.json").unlink()
    assert_skill_fails(repo, "missing reading-set manifest")


def test_reading_sets_object_shape_manifest_passes(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    relax_reading_budget(repo)
    data = load_reading_sets(repo)
    data["sets"] = {
        "new-page": {"limit_bytes": 32768, "files": ["SKILL.md"]},
        "component-state": {"limit_bytes": 16384, "files": ["SKILL.md"]},
    }
    write_reading_sets(repo, data)
    assert_skill_passes(repo)


def test_reading_sets_missing_path_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    write_reading_sets(
        repo,
        {
            "sets": {
                "new-page": ["SKILL.md"],
                "broken": ["assets/does-not-exist.json"],
            }
        },
    )
    assert_skill_fails(repo, "path does not exist")


def test_nested_markdown_not_covered_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    nested = repo / "skills" / "frontend-design" / "references" / "nested"
    nested.mkdir()
    (nested / "extra.md").write_text("# Extra\n", encoding="utf-8")
    assert_skill_fails(repo, "not covered by a set or excluded")


def test_pair_token_fields_must_be_strings(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data["pairs"][0]["theme"] = None
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "must be non-empty strings")


def test_pair_theme_must_match_label(tmp_path: Path) -> None:
    repo = copy_contrast_assets(tmp_path)
    data = load_fixture(repo)
    data["pairs"][0]["theme"] = "dark"
    save_fixture(repo, data)
    assert_contrast_fixture_fails(repo, "does not match label theme")


def test_reading_sets_unrouted_markdown_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    extra = repo / "skills" / "frontend-design" / "assets" / "unrouted.md"
    extra.write_text("# Unrouted\n", encoding="utf-8")
    write_reading_sets(
        repo,
        {
            "sets": {
                "new-page": ["SKILL.md"],
                "extra": ["assets/unrouted.md"],
            }
        },
    )
    assert_skill_fails(repo, "not mentioned in SKILL routing")


def test_reading_sets_hard_limit_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    oversized = repo / "skills" / "frontend-design" / "assets" / "oversized.bin"
    oversized.write_bytes(b"x" * 32769)
    write_reading_sets(
        repo,
        {
            "sets": {
                "new-page": ["SKILL.md"],
                "oversized": ["assets/oversized.bin"],
            }
        },
    )
    assert_skill_fails(repo, "hard limit is 32768 B")


def test_reading_sets_new_page_hard_limit_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    skill = repo / "skills" / "frontend-design" / "SKILL.md"
    skill_size = skill.stat().st_size
    padding = repo / "skills" / "frontend-design" / "assets" / "new-page-padding.bin"
    padding.write_bytes(b"x" * (32768 - skill_size + 1))
    write_reading_sets(repo, {"sets": {"new-page": ["SKILL.md", "assets/new-page-padding.bin"]}})
    assert_skill_fails(repo, "hard limit is 32768 B")


def test_reading_sets_missing_new_page_set_fails(tmp_path: Path) -> None:
    repo = copy_frontend_skill(tmp_path)
    write_reading_sets(repo, {"sets": {"component-state": ["SKILL.md"]}})
    assert_skill_fails(repo, "missing new-page set")


def test_v2_frontmatter_metadata_and_autoinvoke_pass(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "v2-meta-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\r\n"
        "name: v2-meta-skill\r\n"
        "description: Use when testing Antigravity and OpenCode V2 frontmatter metadata and invocation controls.\r\n"
        "license: MIT\r\n"
        "compatibility: agentskills\r\n"
        "allowed-tools: read_file grep_search\r\n"
        "disable-model-invocation: true\r\n"
        "metadata:\r\n"
        "  version: '1.0.0'\r\n"
        "  opencode/autoinvoke: false\r\n"
        "---\r\n\r\n"
        "# V2 Meta Skill\r\n\r\nWorkflow body.\r\n",
        encoding="utf-8",
    )
    assert_skill_passes(tmp_path, "v2-meta-skill")

    # Exact 500-char compatibility boundary must pass.
    boundary = tmp_path / "skills" / "compat-boundary"
    boundary.mkdir()
    (boundary / "SKILL.md").write_text(
        "---\n"
        "name: compat-boundary\n"
        "description: Use when testing exact 500-character compatibility boundary passes validation.\n"
        "license: MIT\n"
        f"compatibility: {'a' * 500}\n"
        "---\n\n"
        "# Boundary\n",
        encoding="utf-8",
    )
    assert_skill_passes(tmp_path, "compat-boundary")


@pytest.mark.parametrize(
    ("extra", "needle"),
    [
        ("compatibility: null\n", "'compatibility' must be a non-empty string"),
        ("compatibility: '   '\n", "'compatibility' must be a non-empty string"),
        (
            f"compatibility: {'a' * 501}\n",
            "'compatibility' exceeds 500 characters",
        ),
        ("allowed-tools: ''\n", "'allowed-tools' must be a non-empty string"),
        ("allowed-tools: '   '\n", "'allowed-tools' must be a non-empty string"),
        ("allowed-tools: []\n", "'allowed-tools' must be a non-empty string"),
        ("disable-model-invocation: 'yes'\n", "'disable-model-invocation' must be a boolean"),
        ("metadata: []\n", "'metadata' must be a mapping"),
        ("metadata:\n  1: bad\n", "'metadata' keys must be non-empty strings"),
        ("metadata:\n  '   ': bad\n", "'metadata' keys must be non-empty strings"),
        ("metadata:\n  version: null\n", "'metadata.version' must be a string"),
        ("metadata:\n  version: 1.0\n", "'metadata.version' must be a string"),
        ("metadata:\n  tags: [a]\n", "'metadata.tags' must be a string"),
        (
            "metadata:\n  opencode/autoinvoke: 'false'\n",
            "'metadata.opencode/autoinvoke' must be a boolean",
        ),
        (
            "disable-model-invocation: true\nmetadata:\n  opencode/autoinvoke: true\n",
            "conflicting 'disable-model-invocation'",
        ),
        ("license: Apache-2.0\n", "duplicate key 'license'"),
    ],
)
def test_v2_frontmatter_invalid_fields_fail(tmp_path: Path, extra: str, needle: str) -> None:
    skill = tmp_path / "skills" / "v2-bad-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: v2-bad-skill\n"
        "description: Use when testing invalid V2 frontmatter fields fail validation cleanly.\n"
        "license: MIT\n"
        f"{extra}"
        "---\n\n"
        "# V2 Bad Skill\n",
        encoding="utf-8",
    )
    assert_skill_fails(tmp_path, needle, skill_id="v2-bad-skill")


def test_second_skill_with_references_does_not_require_new_page_set(tmp_path: Path) -> None:
    skill = write_simple_skill(
        tmp_path,
        skill_id="modular-skill",
        body="# Modular\n\nRead `references/extra.md` when needed.\n",
    )
    (skill / "references").mkdir()
    (skill / "references" / "extra.md").write_text("# Extra\n\nDetails.\n", encoding="utf-8")
    (skill / "assets").mkdir()
    (skill / "assets" / "reading-sets.json").write_text(
        json.dumps(
            {"sets": {"core": {"limit_bytes": 16384, "files": ["SKILL.md", "references/extra.md"]}}}
        ),
        encoding="utf-8",
    )
    assert_skill_passes(tmp_path, "modular-skill")


def test_reading_sets_path_containment_and_per_set_limit_enforced(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "probe"
    (skill / "assets").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: probe\ndescription: A sufficiently long probe skill description for testing.\n"
        "license: MIT\n---\n# Probe\n" + ("a" * 200) + "\n",
        encoding="utf-8",
    )
    manifest = skill / "assets" / "reading-sets.json"

    manifest.write_text(json.dumps({"sets": {"s": ["SKILL.md", "/etc/hosts"]}}), encoding="utf-8")
    errs: list[str] = []
    validate.check_reading_sets(skill, "# Probe\n", errs, root=tmp_path)
    assert any("must be relative" in e for e in errs)

    manifest.write_text(
        json.dumps({"sets": {"s": ["SKILL.md", "../../README.md"]}}), encoding="utf-8"
    )
    errs = []
    validate.check_reading_sets(skill, "# Probe\n", errs, root=tmp_path)
    assert any("escapes skill directory" in e for e in errs)

    manifest.write_text(
        json.dumps({"sets": {"s": {"limit_bytes": 100, "files": ["SKILL.md"]}}}),
        encoding="utf-8",
    )
    errs = []
    validate.check_reading_sets(skill, "# Probe\n", errs, root=tmp_path)
    assert any("limit is 100 B" in e for e in errs)

    manifest.write_text(
        json.dumps({"sets": {"s": {"limit_bytes": True, "files": ["SKILL.md"]}}}),
        encoding="utf-8",
    )
    errs = []
    validate.check_reading_sets(skill, "# Probe\n", errs, root=tmp_path)
    assert any("invalid manifest" in e for e in errs)

    manifest.write_text(
        json.dumps({"sets": {"s": ["SKILL.md"]}, "excluded": {"SKILL.md": "nope"}}),
        encoding="utf-8",
    )
    errs = []
    validate.check_reading_sets(skill, "# Probe\n", errs, root=tmp_path)
    assert any("SKILL.md cannot be excluded" in e for e in errs)


def test_nested_docs_and_relative_repo_escape_fail(tmp_path: Path) -> None:
    (tmp_path / "docs" / "nested").mkdir(parents=True)
    nested_doc = tmp_path / "docs" / "nested" / "broken.md"
    nested_doc.write_text("# Nested\n\n[escape](../../../../etc/hosts)\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "README.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "GOVERNANCE.md",
        "THIRD_PARTY_NOTICES.md",
    ):
        (tmp_path / name).write_text("# Doc\n", encoding="utf-8")

    errs: list[str] = []
    validate.check_root_docs(errs, root=tmp_path)
    assert any("escapes repository root" in e for e in errs)


def test_symlink_inside_skill_fails(tmp_path: Path) -> None:
    # Symlink to directory named leak.md must not crash with IsADirectoryError.
    skill = tmp_path / "skills" / "sym-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sym-skill\ndescription: A sufficiently long test description for symlink rejection.\n"
        "license: MIT\n---\n# Sym\n",
        encoding="utf-8",
    )
    (skill / "leak.md").symlink_to(tmp_path)
    errs: list[str] = []
    validate.check_skill(skill, errs, root=tmp_path)
    assert any("symlink inside skill directory" in e for e in errs)

    # Broken *.md symlink must not crash with FileNotFoundError.
    skill2 = tmp_path / "skills" / "broken-sym"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text(
        "---\nname: broken-sym\ndescription: A sufficiently long test description for broken symlink.\n"
        "license: MIT\n---\n# Sym2\n",
        encoding="utf-8",
    )
    (skill2 / "dangling.md").symlink_to(tmp_path / "does-not-exist")
    errs = []
    validate.check_skill(skill2, errs, root=tmp_path)
    assert any("symlink inside skill directory" in e for e in errs)

    # Symlinked skill directory itself.
    link_dir = tmp_path / "skills" / "sym-dir"
    link_dir.symlink_to(skill)
    errs = []
    validate.check_skill(link_dir, errs, root=tmp_path)
    assert any("symlinked skill directory" in e for e in errs)


def test_top_level_file_symlink_and_aggregate_description_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validate, "AGGREGATE_DESCRIPTION_LIMIT", 50)
    skills_dir = tmp_path / "skills"
    skill = skills_dir / "tiny-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: tiny-skill\ndescription: A sufficiently long description exceeding fifty bytes total.\n"
        "license: MIT\n---\n# Tiny\n",
        encoding="utf-8",
    )
    (skills_dir / "stray-link").symlink_to(tmp_path / "does-not-exist")

    buf = io.StringIO()
    with redirect_stderr(buf):
        rc = validate.main(["--root", str(tmp_path)])
    assert rc == 1
    err_text = buf.getvalue()
    assert "symlink inside skills/ is not allowed" in err_text
    assert "aggregate description bytes" in err_text


def test_frontmatter_edge_cases_unit(tmp_path: Path) -> None:
    def check_raw(name: str, raw: str) -> list[str]:
        skill = tmp_path / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(raw, encoding="utf-8")
        errs: list[str] = []
        validate.check_skill(skill, errs, root=tmp_path)
        return errs

    # Closing --- at EOF without trailing newline parses frontmatter cleanly (then reports empty body).
    errs = check_raw(
        "eof-fm",
        "---\nname: eof-fm\ndescription: A sufficiently long description for EOF frontmatter test.\n"
        "license: MIT\n---",
    )
    assert any("body is empty" in e for e in errs)

    # Empty frontmatter ---\n--- must not swallow body until next horizontal rule.
    empty_fm_doc = "---\n---\n# Title\n\n[broken](missing.md)\n\n---\n\nAfter\n"
    assert "missing.md" in validate.extract_markdown_links(empty_fm_doc)
    errs = check_raw("empty-fm", empty_fm_doc)
    assert any("invalid frontmatter" in e for e in errs)

    # Unhashable key, merge key <<, nested duplicate key, non-string key, and false/false conflict.
    assert any("unhashable key" in e for e in check_raw("unhashable", "---\n[a, b]: 1\n---\n# X\n"))
    assert any(
        "merge key '<<'" in e
        for e in check_raw("merge-key", "---\nbase: &b\n  k: v\n<<: *b\n---\n# X\n")
    )
    assert any(
        "duplicate key 'v'" in e
        for e in check_raw(
            "nested-dup",
            "---\nname: nested-dup\ndescription: A sufficiently long description for nested duplicate key.\n"
            "license: MIT\nmetadata:\n  v: '1'\n  v: '2'\n---\n# X\n",
        )
    )
    assert any(
        "frontmatter keys must be strings" in e
        for e in check_raw(
            "non-str-key",
            "---\nname: non-str-key\ndescription: A sufficiently long description for non string key test.\n"
            "license: MIT\n1: bad\n---\n# X\n",
        )
    )
    assert any(
        "conflicting 'disable-model-invocation'" in e
        for e in check_raw(
            "false-conflict",
            "---\nname: false-conflict\ndescription: A sufficiently long description for false conflict test.\n"
            "license: MIT\ndisable-model-invocation: false\nmetadata:\n  opencode/autoinvoke: false\n---\n# X\n",
        )
    )


def test_reading_sets_and_local_ref_edge_cases_unit(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "edge-skill"
    (skill / "references").mkdir(parents=True)
    (skill / "assets").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: edge-skill\ndescription: A sufficiently long description for edge reading-set tests.\n"
        "license: MIT\n---\n# Edge\n\nSee extra.md (bare basename only).\n",
        encoding="utf-8",
    )
    (skill / "references" / "extra.md").write_text(
        "# Extra\n\nBad ref `references/../../README.md` and [pct](%2e%2e/%2e%2e/README.md) "
        "and [nul](foo%00bar.md).\n",
        encoding="utf-8",
    )
    manifest = skill / "assets" / "reading-sets.json"
    manifest.write_text(
        json.dumps(
            {
                "budget_bytes": 50,
                "sets": {"no-skill": ["references/extra.md"]},
                "excluded": {"../../README.md": "escape"},
            }
        ),
        encoding="utf-8",
    )
    errs: list[str] = []
    validate.check_skill(skill, errs, root=tmp_path)
    routing_errors = [
        e for e in errs if "not mentioned in SKILL routing -> references/extra.md" in e
    ]
    assert len(routing_errors) == 1
    assert any("must include SKILL.md" in e for e in errs)
    assert any("limit is 50 B" in e for e in errs)
    assert any("excluded path escapes skill directory" in e for e in errs)
    assert any("local reference escapes skill directory" in e for e in errs)
    assert any("skill link escapes skill directory" in e for e in errs)
    assert any("broken link -> foo%00bar.md" in e for e in errs)


def test_gfm_slug_and_commonmark_parser_unit(tmp_path: Path) -> None:
    assert validate.slug("foo_bar") == "foo_bar"
    assert validate.slug("`__init__`") == "__init__"
    assert validate.slug("A & B") == "a--b"
    assert validate.slug("_em_ and `code_id`") == "em-and-code_id"

    headings = validate.markdown_headings(
        "# Foo\n## Foo 1\n## Foo\n<a id='custom-id'></a>\n<a data-id='ignored'></a>\n"
    )
    assert {"foo", "foo-1", "foo-2", "custom-id"} <= headings
    assert "ignored" not in headings

    links = validate.extract_markdown_links(
        "```inline``` text\n\n"
        r"Use \` [escaped-ok](esc.md) \`"
        "\n\n<!-- note ` [hidden-comment](hidden.md) --> [after-comment](comment.md) "
        "`[hidden-inline](inline.md)`\n\n"
        "```md\n[hidden-fence](fence.md)\n```\n\n"
        "`<!--` [kept](a.md) `-->`\n\n"
        "[![alt](img.svg)](target.md)\n\n"
        "[dup]: broken-first.md\n[dup]: second.md\n[dup][]\n"
    )
    for expected in (
        "esc.md",
        "comment.md",
        "a.md",
        "img.svg",
        "target.md",
        "broken-first.md",
        "second.md",
    ):
        assert expected in links
    for masked_out in ("hidden.md", "inline.md", "fence.md"):
        assert masked_out not in links

    deep = "[" * 1500 + "x" + "](deep.md)" * 1500
    assert "deep.md" in validate.extract_markdown_links(deep)

    doc = tmp_path / "doc.md"
    doc.write_text("[proto](<//example.com/foo>)\n", encoding="utf-8")
    errs: list[str] = []
    validate.check_markdown_links(doc, errs, root=tmp_path)
    assert errs == []


def test_validate_repo_in_process_does_not_mutate_root_and_catches_aa_failure(
    tmp_path: Path,
) -> None:
    from scripts import validate

    orig_root = validate.ROOT
    names, errors = validate.validate_repo(REPO_ROOT)
    assert errors == []
    assert len(names) == 11
    assert orig_root == validate.ROOT

    # Verify merged pairs loop catches an AA failure in-process (without contrast subprocesses).
    contrast = validate.load_contrast_module(
        REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py"
    )
    fixture_data = json.loads(
        (
            REPO_ROOT / "skills" / "frontend-design" / "assets" / "token-contrast-pairs.json"
        ).read_text(encoding="utf-8")
    )
    fixture_data["pairs"][0]["fg"] = fixture_data["pairs"][0]["bg"]
    bad_fixture = tmp_path / "pairs.json"
    bad_fixture.write_text(json.dumps(fixture_data), encoding="utf-8")
    errs: list[str] = []
    validate.check_contrast_fixture(
        bad_fixture,
        REPO_ROOT / "skills" / "frontend-design" / "assets" / "tokens.css",
        contrast,
        errs,
        root=tmp_path,
    )
    assert any("fails AA" in e for e in errs)


def test_check_installer_validates_both_harnesses_and_lib(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "install", repo / "install")

    def check_install() -> list[str]:
        errs: list[str] = []
        validate.check_installer(errs, root=repo)
        return errs

    assert check_install() == []

    # Missing, symlinked, and non-executable entrypoints fail for both harnesses.
    for name in ("antigravity.sh", "opencode.sh"):
        script = repo / "install" / name
        other = repo / "install" / ("opencode.sh" if name == "antigravity.sh" else "antigravity.sh")
        script.unlink()
        assert any(f"install/{name}: missing" in e for e in check_install())

        script.symlink_to(other)
        assert any(f"install/{name}: symlinked installer script" in e for e in check_install())

        script.unlink()
        shutil.copy2(REPO_ROOT / "install" / name, script)
        script.chmod(0o644)
        assert any(f"install/{name}: not executable" in e for e in check_install())
        script.chmod(0o755)

    # Missing, symlinked, and syntax-broken install/lib.sh fail.
    lib = repo / "install" / "lib.sh"
    lib_text = lib.read_text(encoding="utf-8")
    lib.write_text(lib_text + "\nif then\n", encoding="utf-8")
    assert any("install/lib.sh: bash syntax error" in e for e in check_install())

    lib.unlink()
    assert any("install/lib.sh: missing" in e for e in check_install())

    lib.symlink_to(repo / "install" / "opencode.sh")
    assert any("install/lib.sh: symlinked installer script" in e for e in check_install())

    # Symlinked install/ directory itself fails.
    real_install = tmp_path / "real-install"
    shutil.copytree(REPO_ROOT / "install", real_install)
    shutil.rmtree(repo / "install")
    (repo / "install").symlink_to(real_install)
    assert any("install: symlinked installer directory" in e for e in check_install())


def test_aud46_css_tokens_fail_closed_nested_var_and_no_duplicate_missing_error(
    tmp_path: Path,
) -> None:
    contrast = validate.load_contrast_module(
        REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py"
    )
    fixture_src = REPO_ROOT / "skills" / "frontend-design" / "assets" / "token-contrast-pairs.json"
    tokens_src = REPO_ROOT / "skills" / "frontend-design" / "assets" / "tokens.css"

    fixture = tmp_path / "pairs.json"
    fixture.write_text(fixture_src.read_text(encoding="utf-8"), encoding="utf-8")
    base_css = tokens_src.read_text(encoding="utf-8")

    # 1. Pair-only token mutated to invalid color or oklch() must fail closed (never silently skipped).
    for old, bad_val, needle in (
        (
            "--color-canvas: var(--neutral-50);",
            "--color-canvas: oklch(0.95 0.01 90);",
            "does not resolve to a valid color",
        ),
        (
            "--color-focus: var(--brand-500);",
            "--color-focus: not-a-color;",
            "does not resolve to a valid color",
        ),
        (
            "--color-accent-hover: var(--brand-700);",
            "--color-accent-hover: var(--missing-var);",
            "failed to resolve",
        ),
    ):
        assert old in base_css
        tokens = tmp_path / "tokens.css"
        tokens.write_text(base_css.replace(old, bad_val, 1), encoding="utf-8")
        errs: list[str] = []
        validate.check_contrast_fixture(fixture, tokens, contrast, errs, root=tmp_path)
        assert any(needle in e for e in errs), (bad_val, errs)

    # 2. Opted-out tokens (--color-border, --color-accent-subtle, --color-overlay) must fail closed
    #    on unresolved var() or unparseable colors.
    for old, bad_val, needle in (
        (
            "--color-border: var(--neutral-200);",
            "--color-border: var(--nonexistent);",
            "failed to resolve",
        ),
        (
            "--color-accent-subtle: var(--brand-50);",
            "--color-accent-subtle: oklch(0.9 0.05 180);",
            "does not resolve to a valid color",
        ),
        (
            "--color-overlay: var(--overlay-light);",
            "--color-overlay: not-a-color;",
            "does not resolve to a valid color",
        ),
    ):
        assert old in base_css
        tokens = tmp_path / "tokens.css"
        tokens.write_text(base_css.replace(old, bad_val, 1), encoding="utf-8")
        errs = []
        validate.check_contrast_fixture(fixture, tokens, contrast, errs, root=tmp_path)
        assert any(needle in e for e in errs), errs

    # 3. Nested var(--a, var(--b, #123456)) resolves recursively; cycles (even with fallback!)
    #    and malformed multi-var fail closed.
    nested_css = (
        ":root {\n"
        "  --real: #123456;\n"
        "  --color-nested: var(--missing-a, var(--real));\n"
        "  --color-deep: var(--missing-a, var(--missing-b, #654321));\n"
        "  --color-self-cycle: var(--color-self-cycle, #444444);\n"
        "  --color-cycle-a: var(--color-cycle-b, #444444);\n"
        "  --color-cycle-b: var(--color-cycle-a);\n"
        "  --color-junk: var(--real, #fff) var(--real);\n"
        "}\n"
    )
    resolved = validate.resolve_theme_tokens_from_declarations(
        validate.css_declarations(nested_css)
    )
    assert resolved["light"]["--color-nested"] == "#123456"
    assert resolved["light"]["--color-deep"] == "#654321"
    assert "--color-self-cycle" not in resolved["light"]
    assert "--color-cycle-a" not in resolved["light"]
    assert "--color-cycle-b" not in resolved["light"]
    assert resolved["light"]["--color-junk"] == "var(--real, #fff) var(--real)"

    # 4. Missing tokens.css produces exactly one "missing token source" error via check_contrast.
    mini = tmp_path / "missing-tokens-root"
    (mini / "skills" / "frontend-design" / "scripts").mkdir(parents=True)
    (mini / "skills" / "frontend-design" / "assets").mkdir(parents=True)
    shutil.copy2(
        REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py",
        mini / "skills" / "frontend-design" / "scripts" / "contrast.py",
    )
    shutil.copy2(
        fixture_src,
        mini / "skills" / "frontend-design" / "assets" / "token-contrast-pairs.json",
    )
    errs = []
    validate.check_contrast(errs, root=mini)
    missing_msgs = [e for e in errs if "missing token source" in e]
    assert len(missing_msgs) == 1, errs


def test_aud46_symlink_containment_blocks_contrast_exec_and_repo_entries(tmp_path: Path) -> None:
    # 1. Symlinked contrast.py and symlinked parent dir must NEVER execute exec_module.
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "executed.marker"
    evil_script = outside / "contrast.py"
    evil_script.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('pwned', encoding='utf-8')\n"
        "def self_test(): return 0\n",
        encoding="utf-8",
    )

    repo_a = tmp_path / "repo_a"
    (repo_a / "skills" / "frontend-design" / "scripts").mkdir(parents=True)
    (repo_a / "skills" / "frontend-design" / "assets").mkdir(parents=True)
    (repo_a / "skills" / "frontend-design" / "scripts" / "contrast.py").symlink_to(evil_script)
    errs: list[str] = []
    validate.check_contrast(errs, root=repo_a)
    assert any("symlinked contrast checker" in e for e in errs), errs
    assert not marker.exists()

    repo_b = tmp_path / "repo_b"
    (repo_b / "skills" / "frontend-design" / "assets").mkdir(parents=True)
    (repo_b / "skills" / "frontend-design" / "scripts").symlink_to(outside)
    errs = []
    validate.check_contrast(errs, root=repo_b)
    assert any("symlinked contrast checker" in e for e in errs), errs
    assert not marker.exists()

    # 2. Symlinked skills/ directory fails cleanly in validate_repo.
    repo_c = tmp_path / "repo_c"
    repo_c.mkdir()
    real_skills = tmp_path / "real_skills"
    real_skills.mkdir()
    (repo_c / "skills").symlink_to(real_skills)
    names, errs = validate.validate_repo(repo_c)
    assert names == []
    assert any("symlinked skills directory" in e for e in errs), errs

    # Symlinked fixture and tokens.css also fail closed in check_contrast.
    repo_assets = tmp_path / "repo_assets"
    (repo_assets / "skills" / "frontend-design" / "scripts").mkdir(parents=True)
    (repo_assets / "skills" / "frontend-design" / "assets").mkdir(parents=True)
    shutil.copy2(
        REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py",
        repo_assets / "skills" / "frontend-design" / "scripts" / "contrast.py",
    )
    (
        repo_assets / "skills" / "frontend-design" / "assets" / "token-contrast-pairs.json"
    ).symlink_to(REPO_ROOT / "skills" / "frontend-design" / "assets" / "token-contrast-pairs.json")
    (repo_assets / "skills" / "frontend-design" / "assets" / "tokens.css").symlink_to(
        REPO_ROOT / "skills" / "frontend-design" / "assets" / "tokens.css"
    )
    asset_errs: list[str] = []
    validate.check_contrast(asset_errs, root=repo_assets)
    assert any("symlinked contrast fixture" in e for e in asset_errs), asset_errs
    assert any("symlinked token source" in e for e in asset_errs), asset_errs

    # 3. Symlinked root doc, docs/ dir, docs/ file, .github/ dir, .github/ doc/dangling/YAML fail.
    repo_d = tmp_path / "repo_d"
    (repo_d / "docs").mkdir(parents=True)
    (repo_d / ".github").mkdir(parents=True)
    ext_md = outside / "ext.md"
    ext_md.write_text("# Ext\n", encoding="utf-8")
    ext_yml = outside / "ext.yml"
    ext_yml.write_text("version: 2\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "GOVERNANCE.md",
        "THIRD_PARTY_NOTICES.md",
    ):
        (repo_d / name).write_text("# Doc\n", encoding="utf-8")
    (repo_d / "README.md").symlink_to(ext_md)
    (repo_d / "docs" / "linked.md").symlink_to(ext_md)
    (repo_d / ".github" / "linked.md").symlink_to(ext_md)
    (repo_d / ".github" / "CODEOWNERS").symlink_to(outside / "missing-codeowners")
    (repo_d / ".github" / "linked.yml").symlink_to(ext_yml)
    (repo_d / ".github" / "linked-dir").symlink_to(outside)

    root_errs: list[str] = []
    validate.check_root_docs(root_errs, root=repo_d)
    assert any("README.md: symlinked documentation file" in e for e in root_errs), root_errs
    assert any("docs/linked.md: symlink inside docs/" in e for e in root_errs), root_errs

    gh_errs: list[str] = []
    validate.check_github_docs(gh_errs, root=repo_d)
    assert any(".github/linked.md: symlink inside .github/" in e for e in gh_errs), gh_errs
    assert any(".github/CODEOWNERS: symlink inside .github/" in e for e in gh_errs), gh_errs

    yml_errs: list[str] = []
    validate.check_yaml(yml_errs, root=repo_d)
    assert any(".github/linked.yml: symlinked YAML file" in e for e in yml_errs), yml_errs
    assert any(".github/linked-dir: symlink inside .github/" in e for e in yml_errs), yml_errs

    # Symlinked docs/ and .github/ directories themselves fail closed.
    repo_e = tmp_path / "repo_e"
    repo_e.mkdir()
    for name in (
        "AGENTS.md",
        "README.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "GOVERNANCE.md",
        "THIRD_PARTY_NOTICES.md",
    ):
        (repo_e / name).write_text("# Doc\n", encoding="utf-8")
    (repo_e / "docs").symlink_to(outside)
    (repo_e / ".github").symlink_to(outside)
    dir_errs: list[str] = []
    validate.check_root_docs(dir_errs, root=repo_e)
    validate.check_github_docs(dir_errs, root=repo_e)
    validate.check_yaml(dir_errs, root=repo_e)
    assert any("docs: symlinked docs directory" in e for e in dir_errs), dir_errs
    assert any(".github: symlinked .github directory" in e for e in dir_errs), dir_errs


def test_aud46_markdown_links_footnotes_multiline_and_yaml12_rules(tmp_path: Path) -> None:
    import yaml

    # 1. Single-newline wrapping in links is extracted; blank line breaks it; footnotes excluded;
    #    brackets inside link titles are ignored.
    sample = (
        "[multi\nline](references/missing.md)\n\n"
        "[wrapped-dest](\nreferences/wrapped.md\n)\n\n"
        "[not a link\n\nstill not](references/blank-line.md)\n\n"
        "[^1]: not-a-file.md\n"
        "[real-ref]: references/real-ref.md\n\n"
        '[titled](references/ok.md "[fake](references/fake.md)")\n'
    )
    links = validate.extract_markdown_links(sample)
    assert "references/missing.md" in links
    assert "references/wrapped.md" in links
    assert "references/real-ref.md" in links
    assert "references/ok.md" in links
    assert "references/blank-line.md" not in links
    assert "not-a-file.md" not in links
    assert "references/fake.md" not in links

    # 2. parse_frontmatter_text preserves trailing newline for literal block scalars.
    fm, body = validate.parse_frontmatter_text("---\nname: x\ndescription: |\n  line1\n---\nBody\n")
    assert fm["description"] == "line1\n"
    assert body == "Body\n"

    # 3. YAML 1.2 booleans: yes/no/on/off are strings (not booleans) without mutating yaml.SafeLoader.
    assert yaml.safe_load("yes") is True
    for raw_bool in ("yes", "no", "on", "off"):
        parsed, _ = validate.parse_frontmatter_text(f"---\nflag: {raw_bool}\n---\nBody\n")
        assert parsed["flag"] == raw_bool and isinstance(parsed["flag"], str)
    for raw_bool, expected in (("true", True), ("false", False), ("True", True), ("FALSE", False)):
        parsed, _ = validate.parse_frontmatter_text(f"---\nflag: {raw_bool}\n---\nBody\n")
        assert parsed["flag"] is expected

    # 4. allowed-tools rejects commas, newlines, and control chars; .markdown files are validated;
    #    reading-sets rejects sets ∩ excluded overlap, unknown set keys, and wrong base.
    skill = tmp_path / "skills" / "strict-skill"
    (skill / "references").mkdir(parents=True)
    (skill / "assets").mkdir(parents=True)
    (skill / "references" / "extra.markdown").write_text(
        "# Extra\n\n[broken](does-not-exist.md)\n", encoding="utf-8"
    )
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: strict-skill\n"
        "description: A sufficiently long description for strict AUD-46 validation checks.\n"
        "license: MIT\n"
        "disable-model-invocation: yes\n"
        'allowed-tools: "read_file, grep_search"\n'
        "metadata:\n"
        "  country: NO\n"
        "---\n\n"
        "# Strict\n\nSee `references/extra.markdown`.\n",
        encoding="utf-8",
    )
    (skill / "assets" / "reading-sets.json").write_text(
        json.dumps(
            {
                "base": "skills/wrong-skill",
                "sets": {
                    "core": {
                        "files": ["SKILL.md", "references/extra.markdown"],
                        "limit_bytes": 16384,
                    }
                },
                "excluded": {"references/extra.markdown": "overlap"},
            }
        ),
        encoding="utf-8",
    )
    errs: list[str] = []
    validate.check_skill(skill, errs, root=tmp_path)
    joined = "\n".join(errs)
    assert "'disable-model-invocation' must be a boolean" in joined
    assert "'allowed-tools' must be space-delimited without commas or control characters" in joined
    assert "'metadata.country'" not in joined  # NO parsed as string, not bool
    assert "'base' ('skills/wrong-skill') does not match skill directory" in joined
    assert "cannot be in both sets and excluded: references/extra.markdown" in joined
    assert "references/extra.markdown: broken link -> does-not-exist.md" in joined

    # Newlines and control characters in allowed-tools are also rejected.
    for bad_tools in ('"read_file\\ngrep_search"', '"read_file\\tgrep_search"'):
        ctrl_skill = tmp_path / "skills" / "ctrl-skill"
        ctrl_skill.mkdir(parents=True, exist_ok=True)
        (ctrl_skill / "SKILL.md").write_text(
            "---\n"
            "name: ctrl-skill\n"
            "description: A sufficiently long description for allowed-tools control char check.\n"
            "license: MIT\n"
            f"allowed-tools: {bad_tools}\n"
            "---\n\n# Ctrl\n",
            encoding="utf-8",
        )
        ctrl_errs: list[str] = []
        validate.check_skill(ctrl_skill, ctrl_errs, root=tmp_path)
        assert any(
            "'allowed-tools' must be space-delimited without commas or control characters" in e
            for e in ctrl_errs
        ), (bad_tools, ctrl_errs)

    # Unknown key in reading-sets set object fails.
    with pytest.raises(ValueError, match="unknown key"):
        validate.reading_set_entries(
            {"sets": {"core": {"files": ["SKILL.md"], "unexpected": True}}}
        )

    # check_yaml rejects duplicate keys in .github/*.yml via UniqueKeySafeLoader.
    gh_root = tmp_path / "yaml_dup"
    (gh_root / ".github").mkdir(parents=True)
    (gh_root / ".github" / "dependabot.yml").write_text(
        "version: 2\nversion: 3\n", encoding="utf-8"
    )
    yml_errs: list[str] = []
    validate.check_yaml(yml_errs, root=gh_root)
    assert any("duplicate key 'version'" in e for e in yml_errs), yml_errs

    # Dead symbols are removed.
    for dead in (
        "HTML_COMMENT_RE",
        "REF_LINK_RE",
        "CSS_COMMENT_RE",
        "mask_inline_code",
        "mask_html_comments",
        "normalize_reference_label",
        "parse_frontmatter",
        "semantic_tokens",
        "resolve_theme_tokens",
    ):
        assert not hasattr(validate, dead), f"dead symbol {dead} still exists"


def test_aud49_markdownlint_ignores_private_dirs_and_shared_blockquote_fence(
    tmp_path: Path,
) -> None:
    # 1. Shared _markdown closes blockquote fence on blockquote exit.
    links = validate.extract_markdown_links(
        "> ```text\n> [ignored](ignored.md)\n\n[real](real.md)\n"
    )
    assert "real.md" in links
    assert "ignored.md" not in links

    # 2. .markdownlint-cli2.jsonc ignores private/ignored dirs while still linting real files.
    cfg_raw = (REPO_ROOT / ".markdownlint-cli2.jsonc").read_text(encoding="utf-8")
    cfg_json = re.sub(r"(?m)^\s*//.*$", "", cfg_raw)
    cfg = json.loads(cfg_json)
    expected_ignores = {
        "**/node_modules",
        "**/.venv",
        "**/venv",
        "**/.playwright-cli",
        "**/.gemini",
        "**/.opencode",
        "**/.claude",
        "**/.agents",
        "**/secrets",
    }
    assert expected_ignores <= set(cfg.get("ignores", []))

    mdlint_local = REPO_ROOT / "node_modules" / ".bin" / "markdownlint-cli2"
    mdlint_bin = str(mdlint_local) if mdlint_local.is_file() else shutil.which("markdownlint-cli2")
    if mdlint_bin is None:
        if os.environ.get("CI") or (REPO_ROOT / "node_modules").is_dir():
            pytest.fail("markdownlint-cli2 binary is required")
        return

    shutil.copy2(REPO_ROOT / ".markdownlint-cli2.jsonc", tmp_path / ".markdownlint-cli2.jsonc")
    (tmp_path / "good.md").write_text("# Good\n", encoding="utf-8")
    for ignored_dir in (
        "node_modules",
        ".venv",
        "venv",
        ".playwright-cli",
        ".gemini",
        ".opencode",
        ".claude",
        ".agents",
        "secrets",
        "nested/.gemini",
    ):
        d = tmp_path / ignored_dir
        d.mkdir(parents=True)
        # Trailing spaces + missing newline + bad heading trigger markdownlint if not ignored.
        (d / "bad.md").write_text("#Bad   \n\n\n\n* a\n+ b", encoding="utf-8")

    ok = subprocess.run(
        [mdlint_bin, "**/*.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr

    # Confirm a real violation at root is still caught.
    (tmp_path / "bad.md").write_text("* a\n+ b\n", encoding="utf-8")
    bad = subprocess.run(
        [mdlint_bin, "**/*.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert bad.returncode != 0


def test_aud47_cli_root_exit_two_placeholders_and_invalid_yaml(tmp_path: Path) -> None:
    # 1. --root CLI flag validates repository root and returns exit 2 on missing/empty skills/.
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc_ok = validate.main(["--root", str(REPO_ROOT)])
    assert rc_ok == 0, err.getvalue()
    assert "All checks passed." in out.getvalue()

    missing_skills = tmp_path / "no-skills"
    missing_skills.mkdir()
    res_missing = run_validate(REPO_ROOT, "--root", str(missing_skills))
    assert res_missing.returncode == 2
    assert "skills/ directory not found" in res_missing.stderr

    empty_skills = tmp_path / "empty-skills"
    (empty_skills / "skills").mkdir(parents=True)
    err = io.StringIO()
    with redirect_stderr(err):
        rc_empty = validate.main(["--root", str(empty_skills)])
    assert rc_empty == 2
    assert "no skills found" in err.getvalue()

    # 2. Placeholder markers (TODO, TBD, FIXME) are caught in SKILL.md and skill assets/scripts.
    skill = write_simple_skill(
        tmp_path,
        skill_id="placeholder-skill",
        body="# Placeholder\n\nTODO: replace this text.\n",
    )
    (skill / "assets").mkdir()
    (skill / "assets" / "sample.css").write_text("/* TBD */\n", encoding="utf-8")
    (skill / "scripts").mkdir()
    (skill / "scripts" / "tool.py").write_text("# FIXME: remove\n", encoding="utf-8")
    assert_skill_fails(
        tmp_path,
        "contains placeholder marker TODO",
        "contains placeholder marker TBD",
        "contains placeholder marker FIXME",
        skill_id="placeholder-skill",
    )

    # 3. check_yaml reports invalid YAML syntax cleanly.
    bad_yaml_root = tmp_path / "bad-yaml"
    (bad_yaml_root / ".github").mkdir(parents=True)
    (bad_yaml_root / ".github" / "dependabot.yml").write_text(
        "version: [unterminated\n", encoding="utf-8"
    )
    yml_errs: list[str] = []
    validate.check_yaml(yml_errs, root=bad_yaml_root)
    assert any("invalid YAML" in e for e in yml_errs), yml_errs
