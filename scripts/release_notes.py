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
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHANGELOG = ROOT / "CHANGELOG.md"

# Semantic Versioning 2.0.0 with a required leading "v".
SEMVER_TAG_RE = re.compile(
    r"^v(?P<major>0|[1-9][0-9]*)\.(?P<minor>0|[1-9][0-9]*)\.(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
SECTION_RE = re.compile(r"^##[ \t]+\[(?P<version>[^\]]+)\](?:[ \t]+-[ \t]+.*)?[ \t]*$")
H2_RE = re.compile(r"^##(?:[ \t]|$)")
REFERENCE_RE = re.compile(r"^\[[^\]]+\]:[ \t]*\S")
FENCE_RE = re.compile(r"^[ \t]*(?P<fence>```|~~~)")


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


def _section_bounds(lines: Sequence[str], version: str) -> tuple[int, int]:
    """Return the start and end line indexes of the matching changelog section."""
    start: int | None = None
    start_heading = ""
    in_fence = False
    fence = ""

    for index, line in enumerate(lines):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group("fence")
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
            continue
        if in_fence:
            continue
        match = SECTION_RE.match(line)
        if match and match.group("version") == version:
            if start is not None:
                raise ValueError(
                    f"CHANGELOG.md has duplicate sections for {version!r}: "
                    f"{start_heading!r} and {line.strip()!r}"
                )
            start = index + 1
            start_heading = line.strip()

    if start is None:
        raise ValueError(f"CHANGELOG.md is missing a '## [{version}]' section")

    end = len(lines)
    in_fence = False
    fence = ""
    for index in range(start, len(lines)):
        line = lines[index]
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group("fence")
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
            continue
        if in_fence:
            continue
        if H2_RE.match(line) or REFERENCE_RE.match(line):
            end = index
            break

    return start, end


def extract_section(changelog: Path, version: str) -> str:
    """Extract a non-empty changelog section for ``version``."""
    try:
        text = changelog.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"changelog not found: {changelog}") from None

    lines = text.splitlines()
    start, end = _section_bounds(lines, version)
    block = lines[start:end]
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
        "--output",
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
