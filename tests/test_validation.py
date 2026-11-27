from __future__ import annotations

import atexit
import json
import shutil
import subprocess
import sys
import tempfile
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
    "*.pyc",
    "tests",
)
_TEMPLATE_DIR: Path | None = None


def _clean_template() -> Path:
    global _TEMPLATE_DIR
    if _TEMPLATE_DIR is None:
        base = Path(tempfile.mkdtemp(prefix="skills-hub-val-tpl-"))
        atexit.register(shutil.rmtree, base, True)
        dest = base / "repo"
        shutil.copytree(REPO_ROOT, dest, ignore=IGNORE)
        _TEMPLATE_DIR = dest
    return _TEMPLATE_DIR


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(_clean_template(), destination)
    return destination


def run_validate(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def assert_validation_passes(repo: Path) -> None:
    _, errors = validate.validate_repo(repo)
    assert not errors, "\n".join(errors)


def assert_validation_fails(repo: Path, *needles: str) -> None:
    _, errors = validate.validate_repo(repo)
    assert errors, f"expected validation failure matching {needles!r}, got 0 errors"
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
    repo = copy_repo(tmp_path)
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
    readme = repo / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\n[root](/README.md)\n", encoding="utf-8"
    )
    assert_validation_passes(repo)


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
    repo = copy_repo(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(repo, text)
    assert_validation_fails(repo, needle)


def test_duplicate_and_setext_heading_slugs(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
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
    assert_validation_passes(repo)

    append_to_skill(repo, "\n[bad duplicate](#duplicate-check-2)\n")
    assert_validation_fails(repo, "missing anchor")


def test_empty_skill_body_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    skill = repo / "skills" / "frontend-design" / "SKILL.md"
    skill.write_text(
        "---\n"
        "name: frontend-design\n"
        "description: A deliberately long description for the empty-body mutation.\n"
        "license: MIT\n"
        "---\n",
        encoding="utf-8",
    )
    assert_validation_fails(repo, "body is empty")


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
    repo = copy_repo(tmp_path)
    skill = repo / "skills" / "frontend-design" / "SKILL.md"
    skill.write_text(mutation(skill.read_text(encoding="utf-8")), encoding="utf-8")
    assert_validation_fails(repo, needle)


def test_agents_and_pull_request_template_links_are_checked(tmp_path: Path) -> None:
    agents_repo = copy_repo(tmp_path / "agents")
    agents_file = agents_repo / "AGENTS.md"
    agents_file.write_text(
        agents_file.read_text(encoding="utf-8") + "\n[broken](/docs/does-not-exist.md)\n",
        encoding="utf-8",
    )
    assert_validation_fails(agents_repo, "broken link")

    template_repo = copy_repo(tmp_path / "template")
    template = template_repo / ".github" / "PULL_REQUEST_TEMPLATE.md"
    template.write_text(
        template.read_text(encoding="utf-8").replace("../CONTRIBUTING.md", "../DOES_NOT_EXIST.md"),
        encoding="utf-8",
    )
    assert_validation_fails(template_repo, "broken link")


def test_external_links_are_skipped(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(
        repo,
        "\n\n[external](https://example.invalid/this-page-does-not-exist)\n",
    )
    assert_validation_passes(repo)


def test_fixture_shrink_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data["pairs"].pop()
    save_fixture(repo, data)
    assert_validation_fails(repo, "expected 64 pairs")


def test_fixture_theme_counts_fail(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data["pairs"][0]["label"] = "dark: theme count probe"
    save_fixture(repo, data)
    assert_validation_fails(repo, "expected 32 light pairs")


def test_fixture_duplicate_label_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data["pairs"][1]["label"] = data["pairs"][0]["label"]
    save_fixture(repo, data)
    assert_validation_fails(repo, "duplicates label")


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
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    mutation(data["pairs"][0])
    save_fixture(repo, data)
    assert_validation_fails(repo, needle)


def test_missing_contrast_script_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    (repo / "skills" / "frontend-design" / "scripts" / "contrast.py").unlink()
    assert_validation_fails(repo, "missing contrast checker")


def test_new_semantic_token_without_coverage_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    tokens.write_text(
        tokens.read_text(encoding="utf-8") + "\n:root {\n  --color-mystery: var(--brand-500);\n}\n",
        encoding="utf-8",
    )
    assert_validation_fails(repo, "--color-mystery", "without contrast coverage")


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
    repo = copy_repo(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    original = tokens.read_text(encoding="utf-8")
    assert old in original
    tokens.write_text(original.replace(old, new, 1), encoding="utf-8")
    assert_validation_fails(repo, needle)


def test_new_semantic_token_with_coverage_passes(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
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
    assert_validation_passes(repo)


def test_single_theme_coverage_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data["coverage"]["--color-surface-raised"] = ["dark: text / surface-raised"]
    save_fixture(repo, data)
    assert_validation_fails(repo, "missing light theme coverage")


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
    repo = copy_repo(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    original = tokens.read_text(encoding="utf-8")
    assert "--neutral-50: #f7f6f2;" in original
    tokens.write_text(
        original.replace("--neutral-50: #f7f6f2;", "--neutral-50: #000000;", 1),
        encoding="utf-8",
    )
    assert_validation_fails(repo, "does not match --color-canvas")


def test_new_semantic_token_with_unrelated_coverage_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    tokens = repo / "skills" / "frontend-design" / "assets" / "tokens.css"
    tokens.write_text(
        tokens.read_text(encoding="utf-8")
        + "\n:root {\n  --color-mystery: var(--neutral-900);\n}\n",
        encoding="utf-8",
    )
    data = load_fixture(repo)
    data["coverage"]["--color-mystery"] = ["light: text / canvas"]
    save_fixture(repo, data)
    assert_validation_fails(repo, "does not test --color-mystery")


def test_missing_coverage_mapping_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data.pop("coverage")
    save_fixture(repo, data)
    assert_validation_fails(repo, "needs a 'coverage' mapping")


def write_simple_skill(
    repo: Path,
    skill_id: str = "simple-skill",
    body: str = "# Simple\n\nKeep this skill small.\n",
) -> Path:
    skill = repo / "skills" / skill_id
    skill.mkdir()
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
    repo = copy_repo(tmp_path)
    write_simple_skill(repo)
    assert_validation_passes(repo)


def test_simple_skill_oversize_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    write_simple_skill(repo, body="#" + ("x" * 32769))
    assert_validation_fails(repo, "hard limit is 32768 B")


def test_simple_skill_references_without_manifest_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    skill = write_simple_skill(repo, body="# Simple\n\nRead `references/extra.md`.\n")
    references = skill / "references"
    references.mkdir()
    (references / "extra.md").write_text("# Extra\n", encoding="utf-8")
    assert_validation_fails(repo, "missing reading-set manifest")


def test_reading_sets_missing_manifest_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    (repo / "skills" / "frontend-design" / "assets" / "reading-sets.json").unlink()
    assert_validation_fails(repo, "missing reading-set manifest")


def test_reading_sets_object_shape_manifest_passes(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    relax_reading_budget(repo)
    data = load_reading_sets(repo)
    data["sets"] = {
        "new-page": {"limit_bytes": 32768, "files": ["SKILL.md"]},
        "component-state": {"limit_bytes": 16384, "files": ["SKILL.md"]},
    }
    write_reading_sets(repo, data)
    assert_validation_passes(repo)


def test_reading_sets_missing_path_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    write_reading_sets(
        repo,
        {
            "sets": {
                "new-page": ["SKILL.md"],
                "broken": ["assets/does-not-exist.json"],
            }
        },
    )
    assert_validation_fails(repo, "path does not exist")


def test_nested_markdown_not_covered_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    nested = repo / "skills" / "frontend-design" / "references" / "nested"
    nested.mkdir()
    (nested / "extra.md").write_text("# Extra\n", encoding="utf-8")
    assert_validation_fails(repo, "not covered by a set or excluded")


def test_pair_token_fields_must_be_strings(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data["pairs"][0]["theme"] = None
    save_fixture(repo, data)
    assert_validation_fails(repo, "must be non-empty strings")


def test_pair_theme_must_match_label(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    data = load_fixture(repo)
    data["pairs"][0]["theme"] = "dark"
    save_fixture(repo, data)
    assert_validation_fails(repo, "does not match label theme")


def test_reading_sets_unrouted_markdown_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
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
    assert_validation_fails(repo, "not mentioned in SKILL routing")


def test_reading_sets_hard_limit_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
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
    assert_validation_fails(repo, "hard limit is 32768 B")


def test_reading_sets_new_page_hard_limit_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    skill = repo / "skills" / "frontend-design" / "SKILL.md"
    skill_size = skill.stat().st_size
    padding = repo / "skills" / "frontend-design" / "assets" / "new-page-padding.bin"
    padding.write_bytes(b"x" * (32768 - skill_size + 1))
    write_reading_sets(repo, {"sets": {"new-page": ["SKILL.md", "assets/new-page-padding.bin"]}})
    assert_validation_fails(repo, "hard limit is 32768 B")


def test_reading_sets_missing_new_page_set_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    write_reading_sets(repo, {"sets": {"component-state": ["SKILL.md"]}})
    assert_validation_fails(repo, "missing new-page set")


def test_v2_frontmatter_metadata_and_autoinvoke_pass(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    skill = repo / "skills" / "v2-meta-skill"
    skill.mkdir()
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
    # Exact 500-char compatibility boundary must pass.
    boundary = repo / "skills" / "compat-boundary"
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
    assert_validation_passes(repo)


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
    repo = copy_repo(tmp_path)
    skill = repo / "skills" / "frontend-design" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    mutated = text.replace("compatibility: agentskills\n", extra, 1)
    assert mutated != text
    skill.write_text(mutated, encoding="utf-8")
    assert_validation_fails(repo, needle)


def test_second_skill_with_references_does_not_require_new_page_set(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    skill = write_simple_skill(
        repo,
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
    assert_validation_passes(repo)


def test_reading_sets_path_containment_and_per_set_limit_enforced(tmp_path: Path) -> None:
    from scripts import validate

    skill = tmp_path / "skills" / "probe"
    (skill / "assets").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: probe\ndescription: A sufficiently long probe skill description for testing.\n"
        "license: MIT\n---\n# Probe\n" + ("a" * 200) + "\n",
        encoding="utf-8",
    )
    orig_root = validate.ROOT
    try:
        validate.ROOT = tmp_path
        manifest = skill / "assets" / "reading-sets.json"

        manifest.write_text(
            json.dumps({"sets": {"s": ["SKILL.md", "/etc/hosts"]}}), encoding="utf-8"
        )
        errs: list[str] = []
        validate.check_reading_sets(skill, "# Probe\n", errs)
        assert any("must be relative" in e for e in errs)

        manifest.write_text(
            json.dumps({"sets": {"s": ["SKILL.md", "../../README.md"]}}), encoding="utf-8"
        )
        errs = []
        validate.check_reading_sets(skill, "# Probe\n", errs)
        assert any("escapes skill directory" in e for e in errs)

        manifest.write_text(
            json.dumps({"sets": {"s": {"limit_bytes": 100, "files": ["SKILL.md"]}}}),
            encoding="utf-8",
        )
        errs = []
        validate.check_reading_sets(skill, "# Probe\n", errs)
        assert any("limit is 100 B" in e for e in errs)

        manifest.write_text(
            json.dumps({"sets": {"s": {"limit_bytes": True, "files": ["SKILL.md"]}}}),
            encoding="utf-8",
        )
        errs = []
        validate.check_reading_sets(skill, "# Probe\n", errs)
        assert any("invalid manifest" in e for e in errs)

        manifest.write_text(
            json.dumps({"sets": {"s": ["SKILL.md"]}, "excluded": {"SKILL.md": "nope"}}),
            encoding="utf-8",
        )
        errs = []
        validate.check_reading_sets(skill, "# Probe\n", errs)
        assert any("SKILL.md cannot be excluded" in e for e in errs)
    finally:
        validate.ROOT = orig_root


def test_nested_docs_and_relative_repo_escape_fail(tmp_path: Path) -> None:
    from scripts import validate

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

    orig_root = validate.ROOT
    try:
        validate.ROOT = tmp_path
        errs: list[str] = []
        validate.check_root_docs(errs)
        assert any("escapes repository root" in e for e in errs)
    finally:
        validate.ROOT = orig_root


def test_symlink_inside_skill_fails(tmp_path: Path) -> None:
    from scripts import validate

    orig_root = validate.ROOT
    try:
        validate.ROOT = tmp_path

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
        validate.check_skill(skill, errs)
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
        validate.check_skill(skill2, errs)
        assert any("symlink inside skill directory" in e for e in errs)

        # Symlinked skill directory itself.
        link_dir = tmp_path / "skills" / "sym-dir"
        link_dir.symlink_to(skill)
        errs = []
        validate.check_skill(link_dir, errs)
        assert any("symlinked skill directory" in e for e in errs)
    finally:
        validate.ROOT = orig_root


def test_top_level_file_symlink_and_aggregate_description_limit(tmp_path: Path) -> None:
    from scripts import validate

    orig_root, orig_skills, orig_limit = (
        validate.ROOT,
        validate.SKILLS_DIR,
        validate.AGGREGATE_DESCRIPTION_LIMIT,
    )
    try:
        validate.ROOT = tmp_path
        validate.SKILLS_DIR = tmp_path / "skills"
        validate.AGGREGATE_DESCRIPTION_LIMIT = 50
        skill = validate.SKILLS_DIR / "tiny-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: tiny-skill\ndescription: A sufficiently long description exceeding fifty bytes total.\n"
            "license: MIT\n---\n# Tiny\n",
            encoding="utf-8",
        )
        (validate.SKILLS_DIR / "stray-link").symlink_to(tmp_path / "does-not-exist")
        import io
        from contextlib import redirect_stderr

        buf = io.StringIO()
        with redirect_stderr(buf):
            rc = validate.main()
        assert rc == 1
        err_text = buf.getvalue()
        assert "symlink inside skills/ is not allowed" in err_text
        assert "aggregate description bytes" in err_text
    finally:
        validate.ROOT = orig_root
        validate.SKILLS_DIR = orig_skills
        validate.AGGREGATE_DESCRIPTION_LIMIT = orig_limit


def test_frontmatter_edge_cases_unit(tmp_path: Path) -> None:
    from scripts import validate

    orig_root = validate.ROOT
    try:
        validate.ROOT = tmp_path

        def check_raw(name: str, raw: str) -> list[str]:
            skill = tmp_path / "skills" / name
            skill.mkdir(parents=True, exist_ok=True)
            (skill / "SKILL.md").write_text(raw, encoding="utf-8")
            errs: list[str] = []
            validate.check_skill(skill, errs)
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
        assert any(
            "unhashable key" in e for e in check_raw("unhashable", "---\n[a, b]: 1\n---\n# X\n")
        )
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
    finally:
        validate.ROOT = orig_root


def test_reading_sets_and_local_ref_edge_cases_unit(tmp_path: Path) -> None:
    from scripts import validate

    orig_root = validate.ROOT
    try:
        validate.ROOT = tmp_path
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
        validate.check_skill(skill, errs)
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
    finally:
        validate.ROOT = orig_root


def test_gfm_slug_and_commonmark_parser_unit(tmp_path: Path) -> None:
    from scripts import validate

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
        "\n\n<!-- note ` --> [after-comment](comment.md) `code`\n\n"
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

    deep = "[" * 1500 + "x" + "](deep.md)" * 1500
    assert "deep.md" in validate.extract_markdown_links(deep)

    orig_root = validate.ROOT
    try:
        validate.ROOT = tmp_path
        doc = tmp_path / "doc.md"
        doc.write_text("[proto](<//example.com/foo>)\n", encoding="utf-8")
        errs: list[str] = []
        validate.check_markdown_links(doc, errs)
        assert errs == []
    finally:
        validate.ROOT = orig_root


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
    repo = copy_repo(tmp_path)
    assert_validation_passes(repo)

    # Missing install/antigravity.sh fails.
    agy = repo / "install" / "antigravity.sh"
    agy.unlink()
    assert_validation_fails(repo, "install/antigravity.sh: missing")

    # Symlinked install/antigravity.sh fails.
    agy.symlink_to(repo / "install" / "opencode.sh")
    assert_validation_fails(repo, "install/antigravity.sh: symlinked installer script")

    # Non-executable install/antigravity.sh fails.
    agy.unlink()
    shutil.copy2(REPO_ROOT / "install" / "antigravity.sh", agy)
    agy.chmod(0o644)
    assert_validation_fails(repo, "install/antigravity.sh: not executable")
    agy.chmod(0o755)

    # Missing install/lib.sh fails.
    lib = repo / "install" / "lib.sh"
    lib.unlink()
    assert_validation_fails(repo, "install/lib.sh: missing")
