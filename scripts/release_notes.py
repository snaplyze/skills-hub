#!/usr/bin/env python3
"""Validate a release tag and extract its section from CHANGELOG.md.

The release workflow uses this script as the single source of release notes:

    python3 scripts/release_notes.py --tag v1.2.3 --notes-file release-notes.md

The tag must be SemVer with a ``v`` prefix (``vX.Y.Z``, optionally with a
prerelease suffix such as ``v1.2.3-rc.1``). The changelog must contain exactly
one matching ``## [X.Y.Z]`` section with non-empty content.

Exit codes:
    0  tag and release notes are valid
    1  invalid tag, missing/empty/duplicate changelog section, or I/O error
    2  command-line usage error
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHANGELOG = ROOT / "CHANGELOG.md"


def _load_markdown_module():
    if __package__ == "scripts":
        from . import _markdown

        return _markdown
    sibling = Path(__file__).resolve().with_name("_markdown.py")
    spec = importlib.util.spec_from_file_location("_skills_hub_markdown", sibling)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {sibling}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_markdown = _load_markdown_module()

# Semantic Versioning 2.0.0 with a required leading "v".
SEMVER_TAG_RE = re.compile(
    r"^v(?P<major>0|[1-9][0-9]*)\.(?P<minor>0|[1-9][0-9]*)\.(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
SECTION_RE = re.compile(
    r"^ {0,3}##[ \t]+\[(?P<version>[^\]]+)\](?:\([^)\n]+\))?(?:[ \t]+-[ \t]+.*)?[ \t]*$"
)
H2_RE = re.compile(r"^ {0,3}##(?:[ \t]|$)")
# Match Markdown link reference definitions, excluding footnotes such as [^1]:.
REFERENCE_RE = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:[ \t]*\S")


class ReleaseTag(NamedTuple):
    """Parsed release tag metadata."""

    tag: str
    version: str
    prerelease: bool


def parse_tag(tag: str) -> ReleaseTag:
    """Validate a tag and return its version metadata."""
    if not tag:
        raise ValueError("invalid release tag: tag is empty")
    match = SEMVER_TAG_RE.fullmatch(tag)
    if match is None:
        raise ValueError(
            f"invalid release tag {tag!r}: expected vX.Y.Z with an optional "
            "SemVer prerelease suffix (for example v1.2.3 or v1.2.3-rc.1)"
        )
    return ReleaseTag(
        tag=tag,
        version=tag[1:],
        prerelease=match.group("prerelease") is not None,
    )


def _section_bounds(
    masked_lines: Sequence[str], raw_lines: Sequence[str], version: str
) -> tuple[int, int]:
    """Return the start and end line indexes of the matching changelog section in one pass."""
    start: int | None = None
    end: int | None = None
    start_heading = ""

    for index, (masked_line, raw_line) in enumerate(zip(masked_lines, raw_lines, strict=True)):
        section_match = SECTION_RE.match(masked_line)
        if section_match and H2_RE.match(raw_line) and section_match.group("version") == version:
            if start is not None:
                raise ValueError(
                    f"CHANGELOG.md has duplicate sections for {version!r}: "
                    f"{start_heading!r} and {raw_line.strip()!r}"
                )
            start = index + 1
            start_heading = raw_line.strip()
            continue

        if (
            start is not None
            and end is None
            and (
                (H2_RE.match(masked_line) and H2_RE.match(raw_line))
                or (REFERENCE_RE.match(masked_line) and REFERENCE_RE.match(raw_line))
            )
        ):
            end = index

    if start is None:
        raise ValueError(f"CHANGELOG.md is missing a '## [{version}]' section")

    return start, len(masked_lines) if end is None else end


def extract_section(changelog: Path, version: str) -> str:
    """Extract a non-empty changelog section for ``version``."""
    try:
        text = changelog.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"changelog not found: {changelog}") from None

    normalized = _markdown.normalize_newlines(text)
    raw_lines = normalized.splitlines()
    masked = _markdown.mask_code_and_comments(_markdown.strip_fenced_code(normalized))
    masked_lines = masked.split("\n") if raw_lines else []
    start, end = _section_bounds(masked_lines, raw_lines, version)
    block = raw_lines[start:end]
    while block and not block[0].strip():
        block.pop(0)
    while block and not block[-1].strip():
        block.pop()
    notes = "\n".join(block)
    if not notes.strip():
        raise ValueError(f"CHANGELOG.md section for {version!r} is empty")
    return notes


def write_github_output(path: Path, release: ReleaseTag) -> None:
    """Append release metadata for the workflow's ``id`` output."""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"version={release.version}\n")
        handle.write(f"prerelease={'true' if release.prerelease else 'false'}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a vX.Y.Z release tag and extract the matching "
            "## [X.Y.Z] section from CHANGELOG.md."
        ),
        epilog=(
            "The release workflow passes the extracted notes to `gh release create --notes-file`."
        ),
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="release tag to validate, for example v1.2.3 or v1.2.3-rc.1",
    )
    parser.add_argument(
        "--changelog",
        type=Path,
        default=DEFAULT_CHANGELOG,
        help=f"changelog path (default: {DEFAULT_CHANGELOG})",
    )
    parser.add_argument(
        "--notes-file",
        dest="notes_file",
        type=Path,
        help="write release notes to this file instead of standard output",
    )
    parser.add_argument(
        "--github-output",
        type=Path,
        help="append version and prerelease values to a GitHub Actions output file",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the tag and changelog section without writing notes",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        release = parse_tag(args.tag)
        notes = extract_section(args.changelog, release.version)
        if args.github_output is not None:
            write_github_output(args.github_output, release)
        if not args.check:
            if args.notes_file is not None:
                args.notes_file.write_text(notes + "\n", encoding="utf-8")
            else:
                sys.stdout.write(notes + "\n")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    kind = "prerelease" if release.prerelease else "stable release"
    action = "validated" if args.check else "extracted"
    print(f"{release.tag}: {action} {kind} notes from {args.changelog}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
