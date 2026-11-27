"""Tests for the release tag and CHANGELOG note extractor."""

from __future__ import annotations

import io
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import release_notes

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_notes.py"


def make_changelog(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "CHANGELOG.md"
    path.write_text(body, encoding="utf-8")
    return path


def run_cli_subprocess(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def run_cli(*args: str) -> SimpleNamespace:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = release_notes.main(list(args))
    return SimpleNamespace(returncode=rc, stdout=out.getvalue(), stderr=err.getvalue())


@pytest.mark.parametrize(
    "tag",
    [
        "v0.0.0",
        "v1.2.3",
        "v10.20.30",
        "v1.2.3-rc.1",
        "v1.2.3-alpha.1",
        "v1.2.3-0.3.7",
        "v1.2.3-x.7.z.92",
        "v1.2.3+20130313144700",
        "v1.2.3-beta+exp.sha.5114f85",
    ],
)
def test_accepts_semver_tags(tag: str) -> None:
    parsed = release_notes.parse_tag(tag)
    assert parsed.tag == tag
    assert parsed.version == tag[1:]


@pytest.mark.parametrize(
    ("tag", "prerelease"),
    [
        ("v1.2.3", False),
        ("v1.2.3+build.5", False),
        ("v1.2.3-rc.1", True),
        ("v1.2.3-rc.1+build.5", True),
        ("v1.2.3-0", True),
    ],
)
def test_prerelease_detection(tag: str, prerelease: bool) -> None:
    assert release_notes.parse_tag(tag).prerelease is prerelease


@pytest.mark.parametrize(
    "tag",
    [
        "",
        "1.2.3",
        "v1.2",
        "v1.2.3.4",
        "v01.2.3",
        "v1.02.3",
        "v1.2.03",
        "v1.2.3-",
        "v1.2.3-01",
        "v1.2.3-rc..1",
        "v1.2.3+",
        "v1.2.3+foo..bar",
        "V1.2.3",
        "v1.2.3 ",
        "v1.2.3\n",
        "v١.٢.٣",
        "release-v1.2.3",
    ],
)
def test_rejects_invalid_tags(tag: str) -> None:
    with pytest.raises(ValueError, match="invalid release tag"):
        release_notes.parse_tag(tag)


def test_extracts_matching_section_only(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [Unreleased]

### Added

- Next change.

## [1.2.3] - 2026-11-15

### Fixed

- A real fix.

## [1.2.2] - 2026-11-14

### Fixed

- An older fix.
""",
    )

    notes = release_notes.extract_section(changelog, "1.2.3")
    assert notes == "### Fixed\n\n- A real fix."
    assert "older fix" not in notes
    assert "Next change" not in notes


def test_extracts_prerelease_section(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3-rc.1] - 2026-11-15

### Added

- Release candidate.
""",
    )

    assert "Release candidate." in release_notes.extract_section(changelog, "1.2.3-rc.1")


def test_extracts_build_metadata_section(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3+build.5] - 2026-11-15

- Build-specific note.
""",
    )

    assert "Build-specific note." in release_notes.extract_section(changelog, "1.2.3+build.5")


def test_does_not_match_a_prefix_version(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.30] - 2026-11-15

- Wrong version.

## [1.2.3-rc.1] - 2026-11-14

- Wrong prerelease.
""",
    )

    with pytest.raises(ValueError, match="missing"):
        release_notes.extract_section(changelog, "1.2.3")


def test_stops_at_link_references(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3] - 2026-11-15

- Release note.

[Unreleased]: https://example.test/compare/v1.2.2...v1.2.3
[1.2.3]: https://example.test/releases/tag/v1.2.3
""",
    )

    notes = release_notes.extract_section(changelog, "1.2.3")
    assert notes == "- Release note."


def test_ignores_h2_inside_fenced_code(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3] - 2026-11-15

```text
## [9.9.9] not a heading
```

- Still part of 1.2.3.
""",
    )

    notes = release_notes.extract_section(changelog, "1.2.3")
    assert "Still part of 1.2.3." in notes


def test_missing_section_fails(tmp_path: Path) -> None:
    changelog = make_changelog(tmp_path, "# Changelog\n\n## [1.2.2]\n\n- Old.\n")

    with pytest.raises(ValueError, match="missing"):
        release_notes.extract_section(changelog, "1.2.3")


def test_empty_section_fails(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3] - 2026-11-15

## [1.2.2] - 2026-11-14

- Old.
""",
    )

    with pytest.raises(ValueError, match="empty"):
        release_notes.extract_section(changelog, "1.2.3")


def test_duplicate_section_fails(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3] - 2026-11-15

- First.

## [1.2.3] - 2026-11-16

- Second.
""",
    )

    with pytest.raises(ValueError, match="duplicate"):
        release_notes.extract_section(changelog, "1.2.3")


def test_cli_writes_notes_and_github_output(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3] - 2026-11-15

- Release note.
""",
    )
    notes_file = tmp_path / "notes.md"
    github_output = tmp_path / "github-output"

    result = run_cli_subprocess(
        "--tag",
        "v1.2.3",
        "--changelog",
        str(changelog),
        "--notes-file",
        str(notes_file),
        "--github-output",
        str(github_output),
    )

    assert result.returncode == 0, result.stderr
    assert notes_file.read_text(encoding="utf-8") == "- Release note.\n"
    output = github_output.read_text(encoding="utf-8")
    assert "version=1.2.3" in output
    assert "prerelease=false" in output


def test_cli_marks_prerelease_in_github_output(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.2.3-rc.1] - 2026-11-15

- Release candidate.
""",
    )
    github_output = tmp_path / "github-output"

    result = run_cli(
        "--tag",
        "v1.2.3-rc.1",
        "--changelog",
        str(changelog),
        "--check",
        "--github-output",
        str(github_output),
    )

    assert result.returncode == 0, result.stderr
    assert "version=1.2.3-rc.1" in github_output.read_text(encoding="utf-8")
    assert "prerelease=true" in github_output.read_text(encoding="utf-8")


def test_cli_fails_for_invalid_tag(tmp_path: Path) -> None:
    changelog = make_changelog(tmp_path, "# Changelog\n")

    result = run_cli("--tag", "v1.2", "--changelog", str(changelog))

    assert result.returncode == 1
    assert "invalid release tag" in result.stderr


def test_cli_fails_for_missing_section(tmp_path: Path) -> None:
    changelog = make_changelog(tmp_path, "# Changelog\n\n## [1.2.2]\n\n- Old.\n")

    result = run_cli("--tag", "v1.2.3", "--changelog", str(changelog))

    assert result.returncode == 1
    assert "missing" in result.stderr


def test_cli_fails_for_missing_changelog(tmp_path: Path) -> None:
    changelog = tmp_path / "missing.md"

    result = run_cli("--tag", "v1.2.3", "--changelog", str(changelog))

    assert result.returncode == 1
    assert "changelog not found" in result.stderr


def test_extracts_four_backtick_fences_footnotes_and_linked_heading(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

## [1.3.0](https://github.com/snaplyze/skills-hub/releases/tag/v1.3.0) - 2026-11-26

- Supports footnotes[^1] and nested code examples:

````markdown
```text
## [1.2.0] - 2026-11-15
```
````

[^1]: Footnote stays inside the section.

~~~text
## [9.9.9] - ignored inside tilde fence
~~~

- Final bullet.

[1.3.0]: https://github.com/snaplyze/skills-hub/releases/tag/v1.3.0
""",
    )
    notes = release_notes.extract_section(changelog, "1.3.0")
    assert "[^1]: Footnote stays inside the section." in notes
    assert "- Final bullet." in notes
    assert "[1.3.0]: https://" not in notes


def test_cli_default_stdout_and_live_changelog(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path, "# Changelog\n\n## [1.2.3] - 2026-11-26\n\n- Stdout note.\n"
    )
    result = run_cli("--tag", "v1.2.3", "--changelog", str(changelog))
    assert result.returncode == 0, result.stderr
    assert result.stdout == "- Stdout note.\n"

    # Live repository CHANGELOG.md must cleanly extract v1.2.0.
    live = release_notes.extract_section(ROOT / "CHANGELOG.md", "1.2.0")
    assert "orchestration" in live

    # Duplicate version appearing after an intervening section must still be rejected.
    dup_after = make_changelog(
        tmp_path,
        "# Changelog\n\n## [1.2.3]\n\n- First.\n\n## [1.2.2]\n\n- Mid.\n\n## [1.2.3]\n\n- Second.\n",
    )
    with pytest.raises(ValueError, match="duplicate"):
        release_notes.extract_section(dup_after, "1.2.3")


def test_aud49_html_comments_indented_h2_and_isolated_python_mode(tmp_path: Path) -> None:
    changelog = make_changelog(
        tmp_path,
        """# Changelog

<!--
## [1.2.3] - commented duplicate must be ignored
-->

  ## [1.2.3] - 2026-11-27

- Leading item.

<!--
## [9.9.9] - commented heading must not truncate 1.2.3
-->

    ## [8.8.8] - 4-space indented code block is not an H2

- Trailing item.

   ## [1.2.2] - 2026-11-26

- Older item.
""",
    )
    notes = release_notes.extract_section(changelog, "1.2.3")
    assert "- Leading item." in notes
    assert "- Trailing item." in notes
    assert "Older item." not in notes

    # Section ending with a fenced code block at EOF + 3-char inline code before "##"
    # must neither drop the closing fence nor falsely truncate.
    eof_changelog = tmp_path / "eof.md"
    eof_changelog.write_text(
        "# Changelog\n\n## [1.2.4]\n\n`a`## [9.9.9] not a heading\n\n```text\nhello\n```\n",
        encoding="utf-8",
    )
    eof_notes = release_notes.extract_section(eof_changelog, "1.2.4")
    assert "`a`## [9.9.9] not a heading" in eof_notes
    assert eof_notes.endswith("```")

    # Running under `python3 -I` (isolated mode) must load sibling _markdown.py cleanly.
    isolated = subprocess.run(
        [
            sys.executable,
            "-I",
            str(SCRIPT),
            "--tag",
            "v1.2.3",
            "--changelog",
            str(changelog),
            "--check",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert isolated.returncode == 0, isolated.stderr
