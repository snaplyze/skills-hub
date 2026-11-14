#!/usr/bin/env python3
"""Validate skills-hub skills, documentation, and deterministic checks.

Run from anywhere:
    python3 scripts/validate.py

Exit codes:
    0  all checks pass
    1  validation errors
    2  missing development dependency or environment problem
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    print(
        "error: PyYAML is required. Install development dependencies with "
        "`python3 -m pip install -r requirements-dev.txt`.",
        file=sys.stderr,
    )
    raise SystemExit(2) from None

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_REF_RE = re.compile(r"`((?:references|assets|scripts)/[^`\s]+)`")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
PLACEHOLDER_MARKERS = ("TODO", "TBD", "FIXME")


def slug(text: str) -> str:
    """Approximate GitHub's heading anchor slug for simple headings."""
    text = text.strip().lower()
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("file does not start with YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter is not closed with ---")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def markdown_headings(text: str) -> set[str]:
    headings: set[str] = set()
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.add(slug(match.group(2)))
    return headings


def check_markdown_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    headings = markdown_headings(text)

    for target in MD_LINK_RE.findall(text):
        target = target.strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "/")):
            continue
        clean = unquote(target.split("#", 1)[0])
        anchor = target.split("#", 1)[1] if "#" in target else None
        if clean:
            candidate = (path.parent / clean).resolve()
            if not candidate.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link -> {target}")
                continue
        if anchor and clean in ("", str(path.name)) and anchor not in headings:
            errors.append(f"{path.relative_to(ROOT)}: missing anchor -> #{anchor}")


def check_skill(skill_dir: Path, errors: list[str]) -> None:
    skill_file = skill_dir / "SKILL.md"
    rel = skill_file.relative_to(ROOT)

    if not skill_file.is_file():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
        return

    if not SKILL_ID_RE.fullmatch(skill_dir.name):
        errors.append(f"{rel}: directory name must be lowercase kebab-case")
    if len(skill_dir.name) > 64:
        errors.append(f"{rel}: directory name must be 64 characters or fewer")

    try:
        frontmatter = parse_frontmatter(skill_file)
    except (ValueError, yaml.YAMLError) as error:
        errors.append(f"{rel}: invalid frontmatter: {error}")
        return

    for key in ("name", "description", "license"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{rel}: frontmatter needs a non-empty '{key}'")

    description = frontmatter.get("description", "")
    if isinstance(description, str):
        if len(description.strip()) < 40:
            errors.append(f"{rel}: description is too short to advertise clearly")
        if len(description) > 1024:
            errors.append(f"{rel}: description exceeds 1024 characters")

    text = skill_file.read_text(encoding="utf-8")

    for target in LOCAL_REF_RE.findall(text):
        if not (skill_dir / target).exists():
            errors.append(f"{rel}: missing referenced file -> {target}")

    for reference in sorted((skill_dir / "references").glob("*.md")):
        if reference.name not in text:
            errors.append(f"{rel}: reference not mentioned in routing -> {reference.name}")

    for md in sorted(skill_dir.rglob("*.md")):
        if md.name == "SKILL.md":
            continue
        if md.stat().st_size == 0:
            errors.append(f"{md.relative_to(ROOT)}: empty markdown file")
        check_markdown_links(md, errors)

    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and path.suffix in (".md", ".css", ".json", ".py", ".sh"):
            content = path.read_text(encoding="utf-8")
            for marker in PLACEHOLDER_MARKERS:
                if marker in content:
                    errors.append(f"{path.relative_to(ROOT)}: contains placeholder marker {marker}")


def check_installer(errors: list[str]) -> None:
    installer = ROOT / "install" / "opencode.sh"
    if not installer.is_file():
        errors.append("install/opencode.sh: missing")
        return
    if not installer.stat().st_mode & 0o111:
        errors.append("install/opencode.sh: not executable")
    result = subprocess.run(
        ["bash", "-n", str(installer)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append(f"install/opencode.sh: bash syntax error: {result.stderr.strip()}")


def check_contrast(errors: list[str]) -> None:
    script = SKILLS_DIR / "frontend-design" / "scripts" / "contrast.py"
    fixture = SKILLS_DIR / "frontend-design" / "assets" / "token-contrast-pairs.json"
    if not script.is_file():
        return
    for args, label in (
        ([sys.executable, str(script), "--self-test"], "contrast self-test"),
        (
            [sys.executable, str(script), "--pairs", str(fixture), "--check"],
            "token contrast fixture",
        ),
    ):
        if "--pairs" in args and not fixture.is_file():
            errors.append(f"{fixture.relative_to(ROOT)}: missing contrast fixture")
            continue
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"{label}: failed\n{result.stdout}{result.stderr}".strip())


def check_root_docs(errors: list[str]) -> None:
    for name in (
        "README.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "GOVERNANCE.md",
    ):
        path = ROOT / name
        if not path.is_file():
            errors.append(f"{name}: missing")
            continue
        check_markdown_links(path, errors)


def check_yaml(errors: list[str]) -> None:
    paths = sorted((ROOT / ".github").rglob("*.yml"))
    paths.extend(sorted((ROOT / ".github").rglob("*.yaml")))
    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {error}")
            continue
        if path.parent.name == "workflows":
            if not isinstance(data, dict):
                errors.append(f"{path.relative_to(ROOT)}: workflow must be a mapping")
                continue
            for key in ("name", "jobs"):
                if key not in data:
                    errors.append(f"{path.relative_to(ROOT)}: workflow missing '{key}'")
            # PyYAML implements YAML 1.1, where the unquoted key `on` becomes True.
            if "on" not in data and True not in data:
                errors.append(f"{path.relative_to(ROOT)}: workflow missing 'on'")


def main() -> int:
    errors: list[str] = []

    if not SKILLS_DIR.is_dir():
        print("error: skills/ directory not found", file=sys.stderr)
        return 2

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        print("error: no skills found", file=sys.stderr)
        return 2

    for skill_dir in skill_dirs:
        check_skill(skill_dir, errors)

    check_installer(errors)
    check_contrast(errors)
    check_root_docs(errors)
    check_yaml(errors)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill(s):")
    for skill_dir in skill_dirs:
        print(f"  - {skill_dir.name}")
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
