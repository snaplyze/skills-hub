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

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

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
LOCAL_REF_RE = re.compile(r"`((?:references|assets|scripts)/[^`\s*?\[\]{}]+)`")
PLACEHOLDER_MARKERS = ("TODO", "TBD", "FIXME")

CONTRAST_PAIR_COUNT = 64
CONTRAST_THEME_PAIR_COUNT = 32
CONTRAST_SIZES = frozenset({"normal", "large", "ui"})
ALLOWED_FRONTMATTER_KEYS = frozenset({"name", "description", "license", "compatibility"})
READING_SET_HARD_LIMIT = 32768
READING_SET_NEW_PAGE_LIMIT = 32768

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
CLOSING_HASHES_RE = re.compile(r"[ \t]+#+[ \t]*$")
SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.*?)\1")
REF_DEF_RE = re.compile(
    r"^ {0,3}\[([^\]\n]+)\]:[ \t]*(<[^>\n]*>|[^\s]+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?[ \t]*$"
)
INLINE_LINK_RE = re.compile(
    # Possessive repetition avoids exponential backtracking on escaped brackets.
    r"!?\[(?:[^\[\]\n]|\\.)*+\]\("
    r"[ \t]*(?P<dest><[^>\n]*>|(?:[^\s()\\]|\\.|\([^()\n]*\))+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?"
    r"[ \t]*\)"
)
REF_LINK_RE = re.compile(r"!?\[([^\]\n]*)\](?:\[([^\]\n]*)\])?")
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
VAR_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*(?:,\s*(.*))?\)", re.DOTALL)


def slug(text: str) -> str:
    """Approximate GitHub's heading anchor slug for simple headings."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = text.strip().lower()
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :]
    return text


def strip_fenced_code(text: str) -> str:
    """Blank fenced code blocks while keeping line numbers stable."""
    lines: list[str] = []
    fence_char = ""
    fence_length = 0
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if fence_char:
            if match and match.group(1)[0] == fence_char and len(match.group(1)) >= fence_length:
                fence_char = ""
                fence_length = 0
            lines.append("")
        elif match:
            fence_char = match.group(1)[0]
            fence_length = len(match.group(1))
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def mask_inline_code(text: str) -> str:
    return INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), text)


def mask_html_comments(text: str) -> str:
    return HTML_COMMENT_RE.sub(
        lambda match: re.sub(r"[^\n]", " ", match.group(0)),
        text,
    )


def normalize_reference_label(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def markdown_headings(text: str) -> set[str]:
    text = mask_html_comments(strip_fenced_code(strip_frontmatter(text)))
    lines = text.splitlines()
    anchors: set[str] = set()
    seen: dict[str, int] = {}

    def add(raw: str) -> None:
        base = slug(raw)
        if not base:
            return
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")

    index = 0
    while index < len(lines):
        line = lines[index]
        heading = ATX_HEADING_RE.match(line)
        if heading:
            raw = CLOSING_HASHES_RE.sub("", heading.group(2) or "")
            add(raw)
            index += 1
            continue
        if (
            line.strip()
            and not line.lstrip().startswith(("-", "*", ">", "|"))
            and index + 1 < len(lines)
            and SETEXT_UNDERLINE_RE.match(lines[index + 1])
        ):
            add(line)
            index += 2
            continue
        index += 1
    return anchors


def extract_markdown_links(text: str) -> list[str]:
    text = mask_html_comments(strip_fenced_code(strip_frontmatter(text)))
    definitions: dict[str, str] = {}
    lines: list[str] = []
    for line in text.splitlines():
        definition = REF_DEF_RE.match(line)
        if definition:
            definitions[normalize_reference_label(definition.group(1))] = definition.group(2)
            lines.append("")
        else:
            lines.append(line)
    scan = mask_inline_code("\n".join(lines))

    targets = [match.group("dest") for match in INLINE_LINK_RE.finditer(scan)]
    without_inline = INLINE_LINK_RE.sub(lambda match: " " * len(match.group(0)), scan)
    for match in REF_LINK_RE.finditer(without_inline):
        text_label, reference_label = match.group(1), match.group(2)
        label = reference_label if reference_label else text_label
        target = definitions.get(normalize_reference_label(label))
        if target is not None:
            targets.append(target)
    return targets


def check_markdown_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    headings = markdown_headings(text)

    for raw_target in extract_markdown_links(text):
        target = raw_target.strip()
        if not target or target.startswith("//"):
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            # http(s), mailto, tel, and other external schemes are skipped.
            continue

        parsed = urlsplit(target)
        path_part = unquote(parsed.path)
        anchor = unquote(parsed.fragment)
        if path_part.startswith("/"):
            candidate = (ROOT / path_part.lstrip("/")).resolve()
            if not candidate.is_relative_to(ROOT):
                errors.append(f"{path.relative_to(ROOT)}: broken link -> {target}")
                continue
        elif path_part:
            candidate = (path.parent / path_part).resolve()
        else:
            candidate = path.resolve()

        if not candidate.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link -> {target}")
            continue
        if not anchor or candidate.is_dir():
            continue
        if candidate.suffix.lower() not in (".md", ".markdown"):
            continue

        if candidate == path.resolve():
            target_headings = headings
        else:
            target_headings = markdown_headings(candidate.read_text(encoding="utf-8"))
        if anchor not in target_headings:
            errors.append(f"{path.relative_to(ROOT)}: missing anchor -> {target}")


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("file does not start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter is not closed with ---")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, text[end + 5 :]


def reading_set_entries(data) -> list[tuple[str, list[str]]]:
    """Read named reading sets from the accepted manifest shapes."""
    if isinstance(data, dict):
        container = data.get(
            "sets",
            data.get("reading_sets", data.get("readingSets")),
        )
    else:
        container = data

    entries: list[tuple[str, list[str]]] = []
    if isinstance(container, dict):
        for name, value in container.items():
            if isinstance(value, list):
                files = value
            elif isinstance(value, dict):
                files = next(
                    (
                        value[key]
                        for key in ("files", "paths", "documents", "items")
                        if isinstance(value.get(key), list)
                    ),
                    None,
                )
                if files is None:
                    raise ValueError(f"set {name!r} needs a file list")
            else:
                raise ValueError(f"set {name!r} must be a list or an object")
            entries.append((str(name), files))
    elif isinstance(container, list):
        for index, value in enumerate(container):
            if not isinstance(value, dict):
                raise ValueError(f"set {index} must be an object")
            name = value.get("name", value.get("id", value.get("key")))
            files = next(
                (
                    value[key]
                    for key in ("files", "paths", "documents", "items")
                    if isinstance(value.get(key), list)
                ),
                None,
            )
            if name is None or files is None:
                raise ValueError(f"set {index} needs a name and a file list")
            entries.append((str(name), files))
    else:
        raise ValueError("manifest needs a 'sets' mapping or list")

    return entries


def is_new_page_set(name: str) -> bool:
    words = re.sub(r"[^a-z0-9]+", " ", name.casefold()).split()
    return ("new" in words and "page" in words) or "newpage" in words


def check_reading_sets(skill_dir: Path, body: str, errors: list[str]) -> None:
    manifest = skill_dir / "assets" / "reading-sets.json"
    if not manifest.is_file():
        errors.append(f"{manifest.relative_to(ROOT)}: missing reading-set manifest")
        return

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        entries = reading_set_entries(data)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        errors.append(f"{manifest.relative_to(ROOT)}: invalid manifest: {error}")
        return
    if not entries:
        errors.append(f"{manifest.relative_to(ROOT)}: no reading sets defined")
        return

    excluded = data.get("excluded", {}) if isinstance(data, dict) else {}
    if not isinstance(excluded, dict):
        errors.append(f"{manifest.relative_to(ROOT)}: 'excluded' must be a mapping")
        excluded = {}

    seen_names: set[str] = set()
    covered: set[Path] = set()
    new_page_sets: list[tuple[str, int]] = []
    for name, files in entries:
        where = f"{manifest.relative_to(ROOT)}: set {name!r}"
        normalized_name = name.casefold()
        if not name.strip():
            errors.append(f"{where} needs a non-empty name")
        elif normalized_name in seen_names:
            errors.append(f"{where} duplicates a set name")
        seen_names.add(normalized_name)
        if not files:
            errors.append(f"{where} has no files")
            continue

        total = 0
        seen_paths: set[Path] = set()
        for raw_path in files:
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append(f"{where} has an empty or non-string path")
                continue
            relative = Path(raw_path)
            candidate = (skill_dir / relative).resolve()
            if not candidate.exists() and not relative.is_absolute():
                candidate = (ROOT / relative).resolve()
            if not candidate.exists():
                errors.append(f"{where} path does not exist -> {raw_path}")
                continue
            if candidate in seen_paths:
                errors.append(f"{where} repeats path -> {raw_path}")
                continue
            seen_paths.add(candidate)
            covered.add(candidate)
            if not candidate.is_file():
                errors.append(f"{where} path is not a file -> {raw_path}")
                continue
            total += candidate.stat().st_size

            if candidate.suffix.lower() not in (".md", ".markdown"):
                continue
            try:
                routing_path = candidate.relative_to(skill_dir).as_posix()
            except ValueError:
                try:
                    routing_path = candidate.relative_to(ROOT).as_posix()
                except ValueError:
                    routing_path = candidate.name
            if candidate == (skill_dir / "SKILL.md").resolve():
                continue
            if routing_path not in body and candidate.name not in body:
                errors.append(
                    f"{where} Markdown file is not mentioned in SKILL routing -> {routing_path}"
                )

        if total > READING_SET_HARD_LIMIT:
            errors.append(f"{where} totals {total} B; hard limit is {READING_SET_HARD_LIMIT} B")
        if is_new_page_set(name):
            new_page_sets.append((name, total))

    excluded_paths = set()
    for raw_path, reason in excluded.items():
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"{manifest.relative_to(ROOT)}: excluded path must be a non-empty string")
            continue
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{manifest.relative_to(ROOT)}: excluded path {raw_path!r} needs a reason")
        candidate = (skill_dir / raw_path).resolve()
        if not candidate.is_file():
            errors.append(f"{manifest.relative_to(ROOT)}: excluded path does not exist -> {raw_path}")
            continue
        excluded_paths.add(candidate)

    all_markdown = {(skill_dir / "SKILL.md").resolve()}
    all_markdown.update(path.resolve() for path in (skill_dir / "references").rglob("*.md"))
    all_markdown.update(path.resolve() for path in (skill_dir / "assets").rglob("*.md"))
    missing_sets = sorted(
        path.relative_to(skill_dir).as_posix()
        for path in all_markdown - covered - excluded_paths
    )
    if missing_sets:
        errors.append(
            f"{manifest.relative_to(ROOT)}: Markdown file(s) not covered by a set or excluded: "
            + ", ".join(missing_sets)
        )

    if not new_page_sets:
        errors.append(f"{manifest.relative_to(ROOT)}: missing new-page set")
    for name, total in new_page_sets:
        if total > READING_SET_NEW_PAGE_LIMIT:
            errors.append(
                f"{manifest.relative_to(ROOT)}: new-page set {name!r} totals "
                f"{total} B; soft limit is {READING_SET_NEW_PAGE_LIMIT} B"
            )


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
        frontmatter, body = parse_frontmatter(skill_file)
    except (ValueError, yaml.YAMLError) as error:
        errors.append(f"{rel}: invalid frontmatter: {error}")
        return

    unknown_keys = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_KEYS)
    if unknown_keys:
        errors.append(f"{rel}: unknown frontmatter key(s): {', '.join(unknown_keys)}")

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

    if not body.strip():
        errors.append(f"{rel}: SKILL.md body is empty")

    for target in LOCAL_REF_RE.findall(body):
        if not (skill_dir / target).exists():
            errors.append(f"{rel}: missing referenced file -> {target}")

    for reference in sorted((skill_dir / "references").rglob("*.md")):
        routing_path = reference.relative_to(skill_dir).as_posix()
        if routing_path not in body and reference.name not in body:
            errors.append(f"{rel}: reference not mentioned in routing -> {routing_path}")

    check_reading_sets(skill_dir, body, errors)
    check_markdown_links(skill_file, errors)
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


def load_contrast_module(script: Path):
    spec = importlib.util.spec_from_file_location("_skills_hub_contrast", script)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {script.name}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(spec.name)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if previous is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous
        raise
    return module


def css_declarations(text: str) -> list[tuple[tuple[str, ...], str, str]]:
    """Return (block context, property, value) for simple custom properties."""
    text = CSS_COMMENT_RE.sub("", text)
    declarations: list[tuple[tuple[str, ...], str, str]] = []
    stack: list[str] = []
    buffer: list[str] = []

    def record() -> None:
        declaration = "".join(buffer).strip()
        buffer.clear()
        if not declaration.startswith("--") or ":" not in declaration:
            return
        name, value = declaration.split(":", 1)
        declarations.append((tuple(stack), name.strip(), value.strip()))

    for character in text:
        if character == "{":
            stack.append("".join(buffer).strip())
            buffer.clear()
        elif character == "}":
            record()
            if stack:
                stack.pop()
        elif character == ";":
            record()
        else:
            buffer.append(character)
    record()
    return declarations


def semantic_tokens(tokens_css: str) -> set[str]:
    return {name for _, name, _ in css_declarations(tokens_css) if name.startswith("--color-")}


def resolve_theme_tokens(tokens_css: str) -> dict[str, dict[str, str]]:
    root_properties: dict[str, str] = {}
    dark_properties: dict[str, str] = {}
    for context, name, value in css_declarations(tokens_css):
        inside_media = any(block.startswith(("@media", "@supports")) for block in context)
        if inside_media:
            continue
        if any(block.startswith('[data-theme="dark"') for block in context):
            dark_properties[name] = value
        elif any(block == ":root" for block in context):
            root_properties[name] = value

    def resolve(name: str, properties: dict[str, str], seen: set[str]) -> str | None:
        if name in seen or name not in properties:
            return None
        value = properties[name]
        match = VAR_RE.fullmatch(value)
        if match:
            return resolve(match.group(1), properties, seen | {name})
        return value

    themes: dict[str, dict[str, str]] = {}
    for theme, properties in (
        ("light", root_properties),
        ("dark", {**root_properties, **dark_properties}),
    ):
        resolved: dict[str, str] = {}
        for name in properties:
            if name.startswith("--color-"):
                value = resolve(name, properties, set())
                if value is not None:
                    resolved[name] = value
        themes[theme] = resolved
    return themes


def check_contrast_fixture(
    fixture: Path,
    tokens_css: Path,
    contrast,
    errors: list[str],
) -> None:
    try:
        data = json.loads(fixture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{fixture.relative_to(ROOT)}: invalid JSON: {error}")
        return
    if not isinstance(data, dict):
        errors.append(f"{fixture.relative_to(ROOT)}: fixture must be a JSON object")
        return

    pairs = data.get("pairs")
    if not isinstance(pairs, list):
        errors.append(f"{fixture.relative_to(ROOT)}: fixture needs a 'pairs' list")
        return
    if len(pairs) != CONTRAST_PAIR_COUNT:
        errors.append(
            f"{fixture.relative_to(ROOT)}: expected {CONTRAST_PAIR_COUNT} pairs, found {len(pairs)}"
        )

    labels: set[str] = set()
    theme_counts = {"light": 0, "dark": 0}
    for index, item in enumerate(pairs):
        where = f"{fixture.relative_to(ROOT)}: pair {index}"
        if not isinstance(item, dict):
            errors.append(f"{where} is not an object")
            continue
        missing = [
            field
            for field in ("label", "theme", "fg", "bg", "fg_token", "bg_token", "size")
            if field not in item
        ]
        if missing:
            errors.append(f"{where} missing field(s): {', '.join(missing)}")
            continue
        label = item["label"]
        fg, bg, size = item["fg"], item["bg"], item["size"]
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{where} needs a non-empty label")
            continue
        if label in labels:
            errors.append(f"{where} duplicates label {label!r}")
        labels.add(label)
        label_theme = label.split(":", 1)[0]
        if ":" in label and label_theme in theme_counts:
            theme_counts[label_theme] += 1
        else:
            errors.append(f"{where} label must start with 'light:' or 'dark:'")
        if not isinstance(size, str) or size not in CONTRAST_SIZES:
            errors.append(f"{where} has invalid size {size!r}")
        if not isinstance(fg, str) or not fg.strip():
            errors.append(f"{where} needs a non-empty fg color")
        if not isinstance(bg, str) or not bg.strip():
            errors.append(f"{where} needs a non-empty bg color")
        for field, value in (("fg", fg), ("bg", bg)):
            if isinstance(value, str) and value.strip():
                try:
                    contrast.parse_color(value)
                except (TypeError, ValueError):
                    errors.append(f"{where} has invalid {field} color {value!r}")

    for theme in ("light", "dark"):
        if theme_counts[theme] != CONTRAST_THEME_PAIR_COUNT:
            errors.append(
                f"{fixture.relative_to(ROOT)}: expected {CONTRAST_THEME_PAIR_COUNT} "
                f"{theme} pairs, found {theme_counts[theme]}"
            )

    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        errors.append(f"{fixture.relative_to(ROOT)}: fixture needs a 'coverage' mapping")
        coverage = {}

    combinations = data.get("combinations")
    if not isinstance(combinations, list):
        errors.append(f"{fixture.relative_to(ROOT)}: fixture needs a 'combinations' list")
        combinations = []

    if not tokens_css.is_file():
        errors.append(f"{tokens_css.relative_to(ROOT)}: missing token source")
        return

    tokens_css_text = tokens_css.read_text(encoding="utf-8")
    defined_tokens = semantic_tokens(tokens_css_text)
    resolved_tokens = resolve_theme_tokens(tokens_css_text)
    combination_labels: set[str] = set()
    label_tokens: dict[str, set[str]] = {}

    for item in pairs:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        theme = item.get("theme")
        fg_token = item.get("fg_token")
        bg_token = item.get("bg_token")
        if not all(isinstance(value, str) for value in (label, theme, fg_token, bg_token)):
            continue
        label_theme = label.split(":", 1)[0] if ":" in label else ""
        if theme != label_theme:
            errors.append(
                f"{fixture.relative_to(ROOT)}: pair {label!r} theme {theme!r} "
                f"does not match label theme {label_theme!r}"
            )
        if theme not in resolved_tokens:
            errors.append(f"{fixture.relative_to(ROOT)}: pair {label!r} has unknown theme {theme!r}")
            continue
        for field, token, literal in (
            ("fg", fg_token, item.get("fg")),
            ("bg", bg_token, item.get("bg")),
        ):
            value = resolved_tokens[theme].get(token)
            if value is None:
                errors.append(f"{fixture.relative_to(ROOT)}: pair {label!r} has unknown {field} token")
                continue
            try:
                expected = contrast.parse_color(value).hex()
                actual = contrast.parse_color(str(literal)).hex()
            except (TypeError, ValueError):
                continue
            if expected != actual:
                errors.append(
                    f"{fixture.relative_to(ROOT)}: pair {label!r} {field} {actual} "
                    f"does not match {token} ({expected})"
                )
        label_tokens[label] = {fg_token, bg_token}

    for index, item in enumerate(combinations):
        where = f"{fixture.relative_to(ROOT)}: combination {index}"
        if not isinstance(item, dict):
            errors.append(f"{where} is not an object")
            continue
        missing = [field for field in ("label", "theme", "fg", "bg", "size") if field not in item]
        if missing:
            errors.append(f"{where} missing field(s): {', '.join(missing)}")
            continue
        label, theme = item["label"], item["theme"]
        fg_token, bg_token, size = item["fg"], item["bg"], item["size"]
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{where} needs a non-empty label")
            continue
        if label in labels or label in combination_labels:
            errors.append(f"{where} duplicates label {label!r}")
        combination_labels.add(label)
        if isinstance(fg_token, str) and isinstance(bg_token, str):
            label_tokens[label] = {fg_token, bg_token}
        if theme not in resolved_tokens:
            errors.append(f"{where} has unknown theme {theme!r}")
            continue
        if size not in CONTRAST_SIZES:
            errors.append(f"{where} has invalid size {size!r}")
            continue
        colors: dict[str, object] = {}
        for field, token in (("fg", fg_token), ("bg", bg_token)):
            if not isinstance(token, str) or not token.startswith("--color-"):
                errors.append(f"{where} {field} must be a semantic --color-* token")
                continue
            value = resolved_tokens[theme].get(token)
            if value is None:
                errors.append(f"{where} references unknown token {token!r}")
                continue
            try:
                colors[field] = contrast.parse_color(value)
            except (TypeError, ValueError):
                errors.append(f"{where} token {token!r} does not resolve to a color")
        if len(colors) != 2:
            continue
        result = contrast.check_pair(colors["fg"], colors["bg"], label, size)
        if not result.aa:
            errors.append(
                f"{where} fails AA: {label} is {result.ratio:.2f}:1 "
                f"(needs {result.threshold:.1f}:1)"
            )

    known_labels = labels | combination_labels
    missing_coverage = sorted(defined_tokens - set(coverage))
    if missing_coverage:
        errors.append(
            f"{fixture.relative_to(ROOT)}: semantic token(s) without contrast "
            f"coverage: {', '.join(missing_coverage)}"
        )
    stale_coverage = sorted(set(coverage) - defined_tokens)
    if stale_coverage:
        errors.append(
            f"{fixture.relative_to(ROOT)}: coverage references unknown token(s): "
            f"{', '.join(stale_coverage)}"
        )

    for token, entry in sorted(coverage.items()):
        where = f"{fixture.relative_to(ROOT)}: coverage for {token}"
        if isinstance(entry, list):
            if not entry:
                errors.append(f"{where} must list at least one pair or combination")
                continue
            for label in entry:
                if not isinstance(label, str) or not label.strip():
                    errors.append(f"{where} needs non-empty pair labels")
                elif label not in known_labels:
                    errors.append(f"{where} references unknown label {label!r}")
                elif token not in label_tokens.get(label, set()):
                    errors.append(f"{where} label {label!r} does not test {token}")
        elif isinstance(entry, str):
            if not entry.strip():
                errors.append(f"{where} needs a non-empty reason")
            elif token not in {
                "--color-border",
                "--color-accent-subtle",
                "--color-overlay",
            }:
                errors.append(f"{where} cannot opt out; cover {token} with a pair or combination")
        else:
            errors.append(f"{where} must be a list of labels or a reason string")


def check_contrast(errors: list[str]) -> None:
    script = SKILLS_DIR / "frontend-design" / "scripts" / "contrast.py"
    fixture = SKILLS_DIR / "frontend-design" / "assets" / "token-contrast-pairs.json"
    tokens_css = SKILLS_DIR / "frontend-design" / "assets" / "tokens.css"

    if not script.is_file():
        errors.append(f"{script.relative_to(ROOT)}: missing contrast checker")
        return
    if not fixture.is_file():
        errors.append(f"{fixture.relative_to(ROOT)}: missing contrast fixture")
    if not tokens_css.is_file():
        errors.append(f"{tokens_css.relative_to(ROOT)}: missing token source")

    try:
        contrast = load_contrast_module(script)
    except Exception as error:  # noqa: BLE001 - report any import failure
        errors.append(f"{script.relative_to(ROOT)}: cannot import: {error}")
        return

    if fixture.is_file() and tokens_css.is_file():
        check_contrast_fixture(fixture, tokens_css, contrast, errors)

    for args, label in (
        ([sys.executable, str(script), "--self-test"], "contrast self-test"),
        (
            [sys.executable, str(script), "--pairs", str(fixture), "--check"],
            "token contrast fixture",
        ),
    ):
        if "--pairs" in args and not fixture.is_file():
            continue
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"{label}: failed\n{result.stdout}{result.stderr}".strip())


def check_root_docs(errors: list[str]) -> None:
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
        path = ROOT / name
        if not path.is_file():
            errors.append(f"{name}: missing")
            continue
        check_markdown_links(path, errors)
    for path in sorted((ROOT / "docs").glob("*.md")):
        check_markdown_links(path, errors)


def check_github_docs(errors: list[str]) -> None:
    for path in sorted((ROOT / ".github").rglob("*.md")):
        if path.stat().st_size == 0:
            errors.append(f"{path.relative_to(ROOT)}: empty markdown file")
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
    check_github_docs(errors)
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
