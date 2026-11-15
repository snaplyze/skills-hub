from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORE = shutil.ignore_patterns(
    ".git",
    ".ruff_cache",
    "__pycache__",
    ".pytest_cache",
    ".playwright-cli",
    "tests",
)


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, destination, ignore=IGNORE)
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
    result = run_validate(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed." in result.stdout


def assert_validation_fails(repo: Path, needle: str) -> None:
    result = run_validate(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert needle in result.stderr, result.stdout + result.stderr


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
    assert_validation_passes(copy_repo(tmp_path))


def test_skill_link_formats_pass(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    relax_reading_budget(repo)
    append_to_skill(
        repo,
        '\n\n[local](references/accessibility.md "Accessibility reference")\n'
        "[root](/README.md)\n"
        "[full][accessibility]\n"
        "[collapsed][]\n"
        "\n[accessibility]: references/accessibility.md#testing-protocol\n"
        "[collapsed]: references/accessibility.md\n",
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
        ("\n\n[broken](/docs/does-not-exist.md)\n", "broken link"),
        (
            '\n\n[broken](references/does-not-exist.md "A title")\n',
            "broken link",
        ),
        (
            '\n\n[broken][missing]\n\n[missing]: references/does-not-exist.md "A title"\n',
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
        "name: Frontend Design\n"
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
            lambda text: text.replace("name: Frontend Design", "name: [unterminated", 1),
            "invalid frontmatter",
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
    assert_validation_fails(repo, "--color-mystery")
    assert_validation_fails(repo, "without contrast coverage")


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
        + "\n:root {\n  --color-mystery: var(--neutral-900);\n}\n",
        encoding="utf-8",
    )
    data = load_fixture(repo)
    data["combinations"].append(
        {
            "label": "light: mystery / canvas",
            "theme": "light",
            "fg": "--color-mystery",
            "bg": "--color-canvas",
            "size": "normal",
        }
    )
    data["coverage"]["--color-mystery"] = ["light: mystery / canvas"]
    save_fixture(repo, data)
    assert_validation_passes(repo)


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


def test_reading_sets_missing_manifest_fails(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    (repo / "skills" / "frontend-design" / "assets" / "reading-sets.json").unlink()
    assert_validation_fails(repo, "missing reading-set manifest")


def test_reading_sets_valid_manifest_passes(tmp_path: Path) -> None:
    repo = copy_repo(tmp_path)
    relax_reading_budget(repo)
    data = load_reading_sets(repo)
    data["sets"]["component-state"] = data["sets"]["new-page"]
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
