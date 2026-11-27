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

import argparse
import importlib.util
import io
import json
import re
import subprocess
import sys
from collections.abc import Hashable, Sequence
from contextlib import redirect_stdout
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
ALLOWED_FRONTMATTER_KEYS = frozenset(
    {
        "name",
        "description",
        "license",
        "compatibility",
        "metadata",
        "disable-model-invocation",
        "allowed-tools",
    }
)
COMPATIBILITY_MAX_LEN = 500
AGGREGATE_DESCRIPTION_LIMIT = 16384
READING_SET_HARD_LIMIT = 32768

OPEN_BACKTICK_FENCE_RE = re.compile(r"^ {0,3}(`{3,})[^`]*$")
OPEN_TILDE_FENCE_RE = re.compile(r"^ {0,3}(~{3,}).*$")
ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
CLOSING_HASHES_RE = re.compile(r"[ \t]+#+[ \t]*$")
SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MASK_TOKEN_RE = re.compile(r"<!--|`+")
HTML_ID_RE = re.compile(
    r"<(?:a|h[1-6])\b[^>]*\s(?:id|name)\s*=\s*(?:\"([^\"]+)\"|'([^']+)')",
    re.IGNORECASE,
)
REF_DEF_RE = re.compile(
    r"^ {0,3}\[([^\]\n]+)\]:[ \t]*(<[^>\n]*>|[^\s]+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?[ \t]*$"
)
REF_LINK_RE = re.compile(r"!?\[([^\]\n]*)\](?:\[([^\]\n]*)\])?")
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
VAR_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*(?:,\s*(.*))?\)", re.DOTALL)


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML SafeLoader that rejects duplicate mapping keys, merge keys, and unhashable keys."""


def _construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        if isinstance(key_node, yaml.ScalarNode) and key_node.tag == "tag:yaml.org,2002:merge":
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "YAML merge key '<<' is not allowed",
                key_node.start_mark,
            )
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, Hashable):
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found unhashable key",
                key_node.start_mark,
            )
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def slug(text: str) -> str:
    """Match GitHub's GFM heading anchor slugging."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = text.strip().lower()
    # Preserve underscores inside inline code spans (e.g., `__init__`), strip emphasis elsewhere.
    parts = re.split(r"(`+[^`]*`+)", text)
    cleaned: list[str] = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            cleaned.append(part.strip("`"))
        else:
            part = re.sub(r"[*~]", "", part)
            part = re.sub(r"(?<!\w)_+|_+(?!\w)", "", part)
            cleaned.append(part)
    text = "".join(cleaned)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = text.replace("\t", " ")
    return text.replace(" ", "-")


def strip_frontmatter(text: str) -> str:
    text = normalize_newlines(text)
    if text.startswith("---\n"):
        match = re.search(r"\n---(?:\n|$)", text[3:])
        if match is not None:
            return text[3 + match.end() :]
    return text


def strip_fenced_code(text: str) -> str:
    """Blank CommonMark fenced code blocks while keeping line numbers stable."""
    lines: list[str] = []
    fence_char = ""
    fence_length = 0
    close_re: re.Pattern[str] | None = None
    for line in normalize_newlines(text).splitlines():
        if fence_char:
            assert close_re is not None
            if close_re.match(line):
                fence_char = ""
                fence_length = 0
                close_re = None
            lines.append("")
            continue

        match = OPEN_BACKTICK_FENCE_RE.match(line) or OPEN_TILDE_FENCE_RE.match(line)
        if match:
            fence = match.group(1)
            fence_char = fence[0]
            fence_length = len(fence)
            close_re = re.compile(rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*$")
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def _is_escaped(text: str, pos: int) -> bool:
    backslashes = 0
    i = pos - 1
    while i >= 0 and text[i] == "\\":
        backslashes += 1
        i -= 1
    return (backslashes % 2) == 1


def _blank_preserving_newlines(segment: str) -> str:
    if "\n" not in segment:
        return " " * len(segment)
    return "\n".join(" " * len(part) for part in segment.split("\n"))


def mask_code_and_comments(text: str) -> str:
    """Mask CommonMark inline code spans and HTML comments in a single token-jumping pass."""
    out: list[str] = []
    pos = 0
    n = len(text)
    while pos < n:
        match = MASK_TOKEN_RE.search(text, pos)
        if match is None:
            out.append(text[pos:])
            break
        start, end = match.span()
        if start > pos:
            out.append(text[pos:start])
        token = match.group(0)
        if _is_escaped(text, start):
            out.append(token)
            pos = end
            continue
        if token == "<!--":
            close = text.find("-->", end)
            if close != -1:
                out.append(_blank_preserving_newlines(text[start : close + 3]))
                pos = close + 3
                continue
            out.append(token)
            pos = end
            continue
        # Backtick opener of length tick_len: find matching exact-length closer before blank line.
        tick_len = end - start
        para_end = text.find("\n\n", end)
        limit = n if para_end == -1 else para_end
        search_pos = end
        found = -1
        while search_pos < limit:
            next_tick = text.find("`", search_pos, limit)
            if next_tick == -1:
                break
            run_end = next_tick
            while run_end < limit and text[run_end] == "`":
                run_end += 1
            if run_end - next_tick == tick_len:
                found = run_end
                break
            search_pos = run_end
        if found != -1:
            out.append(_blank_preserving_newlines(text[start:found]))
            pos = found
        else:
            out.append(token)
            pos = end
    return "".join(out)


def mask_inline_code(text: str) -> str:
    """Mask CommonMark inline code spans without crossing paragraph boundaries."""
    out: list[str] = []
    pos = 0
    n = len(text)
    while pos < n:
        idx = text.find("`", pos)
        if idx == -1:
            out.append(text[pos:])
            break
        if idx > pos:
            out.append(text[pos:idx])
        run_end = idx
        while run_end < n and text[run_end] == "`":
            run_end += 1
        if _is_escaped(text, idx):
            out.append(text[idx:run_end])
            pos = run_end
            continue
        tick_len = run_end - idx
        para_end = text.find("\n\n", run_end)
        limit = n if para_end == -1 else para_end
        search_pos = run_end
        found = -1
        while search_pos < limit:
            next_tick = text.find("`", search_pos, limit)
            if next_tick == -1:
                break
            close_end = next_tick
            while close_end < limit and text[close_end] == "`":
                close_end += 1
            if close_end - next_tick == tick_len:
                found = close_end
                break
            search_pos = close_end
        if found != -1:
            out.append(_blank_preserving_newlines(text[idx:found]))
            pos = found
        else:
            out.append(text[idx:run_end])
            pos = run_end
    return "".join(out)


def mask_html_comments(text: str) -> str:
    return HTML_COMMENT_RE.sub(
        lambda match: _blank_preserving_newlines(match.group(0)),
        text,
    )


def preprocess_markdown(text: str) -> tuple[str, str]:
    """Strip frontmatter and fenced code, then mask inline code and HTML comments once."""
    stripped = strip_fenced_code(strip_frontmatter(text))
    return stripped, mask_code_and_comments(stripped)


def normalize_reference_label(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def _markdown_headings_from_preprocessed(stripped: str, masked: str) -> set[str]:
    anchors: set[str] = set()

    for match in HTML_ID_RE.finditer(masked):
        explicit_id = (match.group(1) or match.group(2) or "").strip()
        if explicit_id:
            anchors.add(explicit_id)

    lines = masked.splitlines()
    raw_lines = stripped.splitlines()

    def add(raw: str) -> None:
        base = slug(raw)
        if not base:
            return
        if base not in anchors:
            anchors.add(base)
            return
        suffix = 1
        while f"{base}-{suffix}" in anchors:
            suffix += 1
        anchors.add(f"{base}-{suffix}")

    index = 0
    while index < len(lines):
        line = lines[index]
        heading = ATX_HEADING_RE.match(line)
        if heading:
            raw_heading = ATX_HEADING_RE.match(raw_lines[index])
            raw = CLOSING_HASHES_RE.sub(
                "", (raw_heading.group(2) if raw_heading else heading.group(2)) or ""
            )
            add(raw)
            index += 1
            continue
        if (
            line.strip()
            and not line.lstrip().startswith(("-", "*", ">", "|"))
            and index + 1 < len(lines)
            and SETEXT_UNDERLINE_RE.match(lines[index + 1])
        ):
            add(raw_lines[index])
            index += 2
            continue
        index += 1
    return anchors


def markdown_headings(text: str) -> set[str]:
    stripped, masked = preprocess_markdown(text)
    return _markdown_headings_from_preprocessed(stripped, masked)


def _parse_inline_dest(text: str, pos: int) -> tuple[str, int] | None:
    """Parse ``(dest [title])`` starting at ``pos`` (pointing at '(')."""
    n = len(text)
    if pos >= n or text[pos] != "(":
        return None
    i = pos + 1
    while i < n and text[i] in " \t":
        i += 1
    if i >= n:
        return None

    if text[i] == "<":
        end = text.find(">", i + 1)
        if end == -1 or "\n" in text[i:end]:
            return None
        dest = text[i : end + 1]
        i = end + 1
    else:
        start = i
        paren_depth = 0
        while i < n:
            ch = text[i]
            if ch == "\\" and i + 1 < n and text[i + 1] != "\n":
                i += 2
                continue
            if ch in " \t\n":
                break
            if ch == "(":
                paren_depth += 1
            elif ch == ")":
                if paren_depth == 0:
                    break
                paren_depth -= 1
            i += 1
        if i == start or paren_depth != 0:
            return None
        dest = text[start:i]

    while i < n and text[i] in " \t":
        i += 1
    if i < n and text[i] in "\"'(":
        closer = ")" if text[i] == "(" else text[i]
        i += 1
        while i < n and text[i] != closer:
            if text[i] == "\n":
                return None
            if text[i] == "\\" and i + 1 < n and text[i + 1] != "\n":
                i += 2
                continue
            i += 1
        if i >= n or text[i] != closer:
            return None
        i += 1
        while i < n and text[i] in " \t":
            i += 1
    if i >= n or text[i] != ")":
        return None
    return dest, i + 1


def _scan_inline_links(text: str) -> tuple[list[str], str]:
    """Extract inline Markdown link/image destinations in O(n) without recursion."""
    n = len(text)
    match_bracket: dict[int, int] = {}
    stack: list[int] = []
    i = 0
    while i < n:
        ch = text[i]
        if ch == "\n":
            stack.clear()
            i += 1
            continue
        if ch == "\\" and i + 1 < n and text[i + 1] != "\n":
            i += 2
            continue
        if ch == "[":
            stack.append(i)
        elif ch == "]" and stack:
            match_bracket[stack.pop()] = i
        i += 1

    targets: list[str] = []
    masked = list(text)
    for open_pos, close_pos in sorted(match_bracket.items()):
        if close_pos + 1 < n and text[close_pos + 1] == "(":
            parsed = _parse_inline_dest(text, close_pos + 1)
            if parsed is not None:
                dest, end_pos = parsed
                targets.append(dest)
                start_mask = (
                    open_pos - 1 if open_pos > 0 and text[open_pos - 1] == "!" else open_pos
                )
                for k in range(start_mask, end_pos):
                    if masked[k] != "\n":
                        masked[k] = " "
    return targets, "".join(masked)


def _extract_markdown_links_from_masked(scan: str) -> list[str]:
    definitions: dict[str, str] = {}
    all_definition_targets: list[str] = []
    lines: list[str] = []
    for line in scan.splitlines():
        definition = REF_DEF_RE.match(line)
        if definition:
            label = normalize_reference_label(definition.group(1))
            dest = definition.group(2)
            definitions.setdefault(label, dest)
            all_definition_targets.append(dest)
            lines.append("")
        else:
            lines.append(line)
    body = "\n".join(lines)

    targets, without_inline = _scan_inline_links(body)
    seen_ref_targets: set[str] = set()
    for match in REF_LINK_RE.finditer(without_inline):
        text_label, reference_label = match.group(1), match.group(2)
        label = normalize_reference_label(reference_label if reference_label else text_label)
        target = definitions.get(label)
        if target is not None:
            seen_ref_targets.add(target)
            targets.append(target)
    for target in all_definition_targets:
        if target not in seen_ref_targets:
            seen_ref_targets.add(target)
            targets.append(target)
    return targets


def extract_markdown_links(text: str) -> list[str]:
    _, masked = preprocess_markdown(text)
    return _extract_markdown_links_from_masked(masked)


def check_markdown_links(
    path: Path,
    errors: list[str],
    *,
    root: Path | None = None,
    skill_dir: Path | None = None,
    text: str | None = None,
    heading_cache: dict[Path, set[str]] | None = None,
) -> None:
    base_root = ROOT if root is None else root
    raw_text = path.read_text(encoding="utf-8") if text is None else text
    stripped, masked = preprocess_markdown(raw_text)
    resolved_path = path.resolve()
    if heading_cache is not None and resolved_path in heading_cache:
        headings = heading_cache[resolved_path]
    else:
        headings = _markdown_headings_from_preprocessed(stripped, masked)
        if heading_cache is not None:
            heading_cache[resolved_path] = headings

    root_resolved = base_root.resolve()
    skill_resolved = skill_dir.resolve() if skill_dir is not None else None
    rel_display = path.relative_to(base_root)

    for raw_target in _extract_markdown_links_from_masked(masked):
        target = raw_target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        if not target or target.startswith("//"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            # http(s), mailto, tel, and other external schemes are skipped.
            continue

        parsed = urlsplit(target)
        if parsed.netloc:
            continue
        path_part = unquote(parsed.path)
        anchor = unquote(parsed.fragment)
        if "\x00" in path_part:
            errors.append(f"{rel_display}: broken link -> {target}")
            continue
        if path_part.startswith("/"):
            if skill_resolved is not None:
                errors.append(f"{rel_display}: skill link escapes skill directory -> {target}")
                continue
            candidate = (root_resolved / path_part.lstrip("/")).resolve()
            if not candidate.is_relative_to(root_resolved):
                errors.append(f"{rel_display}: link escapes repository root -> {target}")
                continue
        elif path_part:
            candidate = (path.parent / path_part).resolve()
            if not candidate.is_relative_to(root_resolved):
                errors.append(f"{rel_display}: link escapes repository root -> {target}")
                continue
            if skill_resolved is not None and not candidate.is_relative_to(skill_resolved):
                errors.append(f"{rel_display}: skill link escapes skill directory -> {target}")
                continue
        else:
            candidate = resolved_path

        if not candidate.exists():
            errors.append(f"{rel_display}: broken link -> {target}")
            continue
        if not anchor or candidate.is_dir():
            continue
        if candidate.suffix.lower() not in (".md", ".markdown"):
            continue

        if candidate == resolved_path:
            target_headings = headings
        elif heading_cache is not None and candidate in heading_cache:
            target_headings = heading_cache[candidate]
        else:
            target_headings = markdown_headings(candidate.read_text(encoding="utf-8"))
            if heading_cache is not None:
                heading_cache[candidate] = target_headings
        if anchor not in target_headings:
            errors.append(f"{rel_display}: missing anchor -> {target}")


def parse_frontmatter_text(raw_text: str) -> tuple[dict, str]:
    text = normalize_newlines(raw_text)
    if not text.startswith("---\n"):
        raise ValueError("file does not start with YAML frontmatter")
    match = re.search(r"\n---(?:\n|$)", text[3:])
    if match is None:
        raise ValueError("frontmatter is not closed with ---")
    raw_yaml = text[4 : 3 + match.start()] if match.start() > 0 else ""
    body = text[3 + match.end() :]
    data = yaml.load(raw_yaml, Loader=UniqueKeySafeLoader)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, body


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    return parse_frontmatter_text(path.read_text(encoding="utf-8"))


def _parse_byte_limit(raw: object, field: str) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int) or not 1 <= raw <= READING_SET_HARD_LIMIT:
        raise ValueError(f"{field} must be an integer between 1 and {READING_SET_HARD_LIMIT}")
    return raw


def reading_set_entries(data: object) -> tuple[list[tuple[str, list[str], int | None]], int]:
    """Read named reading sets from the documented ``{"sets": {...}}`` manifest shape."""
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    budget_limit = READING_SET_HARD_LIMIT
    if "budget_bytes" in data:
        budget_limit = _parse_byte_limit(data["budget_bytes"], "budget_bytes")

    container = data.get("sets")
    if not isinstance(container, dict):
        raise ValueError("manifest must contain a 'sets' object")

    entries: list[tuple[str, list[str], int | None]] = []
    for name, value in container.items():
        if not isinstance(name, str):
            raise ValueError("set name must be a string")
        set_limit: int | None = None
        if isinstance(value, list):
            files = value
        elif isinstance(value, dict):
            files = value.get("files")
            if not isinstance(files, list):
                raise ValueError(f"set {name!r} needs a 'files' list")
            if "limit_bytes" in value:
                set_limit = _parse_byte_limit(value["limit_bytes"], f"set {name!r} limit_bytes")
        else:
            raise ValueError(f"set {name!r} must be a list or an object")
        entries.append((name, files, set_limit))
    return entries, budget_limit


def is_new_page_set(name: str) -> bool:
    words = re.sub(r"[^a-z0-9]+", " ", name.casefold()).split()
    return ("new" in words and "page" in words) or "newpage" in words


def check_reading_sets(
    skill_dir: Path,
    body: str,
    errors: list[str],
    *,
    root: Path | None = None,
    md_files: Sequence[Path] | None = None,
) -> bool:
    """Validate reading-sets manifest. Returns True when a manifest was validated."""
    base_root = ROOT if root is None else root
    manifest = skill_dir / "assets" / "reading-sets.json"
    skill_resolved = skill_dir.resolve()
    skill_md_resolved = (skill_dir / "SKILL.md").resolve()

    if md_files is None:
        referenced = [
            p
            for p in (
                *((skill_dir / "references").rglob("*.md")),
                *((skill_dir / "assets").rglob("*.md")),
            )
            if not p.is_symlink() and p.is_file()
        ]
    else:
        referenced = [
            p for p in md_files if p.relative_to(skill_dir).parts[0] in ("references", "assets")
        ]

    if manifest.is_symlink():
        errors.append(
            f"{manifest.relative_to(base_root)}: symlinked reading-set manifest is not allowed"
        )
        return False
    if not manifest.is_file():
        if referenced:
            errors.append(f"{manifest.relative_to(base_root)}: missing reading-set manifest")
            return False
        skill_file = skill_dir / "SKILL.md"
        if skill_file.stat().st_size > READING_SET_HARD_LIMIT:
            errors.append(
                f"{skill_file.relative_to(base_root)}: {skill_file.stat().st_size} B; "
                f"hard limit is {READING_SET_HARD_LIMIT} B"
            )
        return False

    manifest_rel = manifest.relative_to(base_root)
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        entries, budget_limit = reading_set_entries(data)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        errors.append(f"{manifest_rel}: invalid manifest: {error}")
        return True
    if not entries:
        errors.append(f"{manifest_rel}: no reading sets defined")
        return True

    excluded = data.get("excluded", {}) if isinstance(data, dict) else {}
    if not isinstance(excluded, dict):
        errors.append(f"{manifest_rel}: 'excluded' must be a mapping")
        excluded = {}

    seen_names: set[str] = set()
    covered: set[Path] = set()
    has_new_page_set = False
    for name, files, set_limit in entries:
        where = f"{manifest_rel}: set {name!r}"
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
            if relative.is_absolute():
                errors.append(f"{where} path must be relative to skill directory -> {raw_path}")
                continue
            candidate = (skill_dir / relative).resolve()
            if not candidate.is_relative_to(skill_resolved):
                errors.append(f"{where} path escapes skill directory -> {raw_path}")
                continue
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
            routing_path = candidate.relative_to(skill_resolved).as_posix()
            if candidate == skill_md_resolved:
                continue
            if routing_path not in body:
                errors.append(
                    f"{where} Markdown file is not mentioned in SKILL routing -> {routing_path}"
                )

        if skill_md_resolved not in seen_paths:
            errors.append(f"{where} must include SKILL.md")
        effective_limit = min(set_limit or READING_SET_HARD_LIMIT, budget_limit)
        if total > READING_SET_HARD_LIMIT:
            errors.append(f"{where} totals {total} B; hard limit is {READING_SET_HARD_LIMIT} B")
        elif total > effective_limit:
            errors.append(f"{where} totals {total} B; limit is {effective_limit} B")
        if is_new_page_set(name):
            has_new_page_set = True

    excluded_paths = set()
    for raw_path, reason in excluded.items():
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"{manifest_rel}: excluded path must be a non-empty string")
            continue
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{manifest_rel}: excluded path {raw_path!r} needs a reason")
        relative = Path(raw_path)
        if relative.is_absolute():
            errors.append(
                f"{manifest_rel}: excluded path must be relative to skill directory -> {raw_path}"
            )
            continue
        candidate = (skill_dir / relative).resolve()
        if not candidate.is_relative_to(skill_resolved):
            errors.append(f"{manifest_rel}: excluded path escapes skill directory -> {raw_path}")
            continue
        if candidate == skill_md_resolved:
            errors.append(f"{manifest_rel}: SKILL.md cannot be excluded")
            continue
        if not candidate.is_file():
            errors.append(f"{manifest_rel}: excluded path does not exist -> {raw_path}")
            continue
        excluded_paths.add(candidate)

    all_markdown = {skill_md_resolved}
    for path in referenced:
        resolved = path.resolve()
        if resolved.is_relative_to(skill_resolved):
            all_markdown.add(resolved)
    missing_sets = sorted(
        path.relative_to(skill_resolved).as_posix()
        for path in all_markdown - covered - excluded_paths
    )
    if missing_sets:
        errors.append(
            f"{manifest_rel}: Markdown file(s) not covered by a set or excluded: "
            + ", ".join(missing_sets)
        )

    if skill_dir.name == "frontend-design" and not has_new_page_set:
        errors.append(f"{manifest_rel}: missing new-page set")
    return True


def _check_local_refs(
    md_path: Path, text: str, skill_dir: Path, errors: list[str], *, root: Path
) -> None:
    skill_resolved = skill_dir.resolve()
    rel = md_path.relative_to(root)
    for target in LOCAL_REF_RE.findall(strip_fenced_code(text)):
        candidate = (skill_dir / target).resolve()
        if not candidate.is_relative_to(skill_resolved):
            errors.append(f"{rel}: local reference escapes skill directory -> {target}")
        elif not candidate.exists():
            errors.append(f"{rel}: missing referenced file -> {target}")


def _check_placeholders(path: Path, content: str, errors: list[str], *, root: Path) -> None:
    for marker in PLACEHOLDER_MARKERS:
        if marker in content:
            errors.append(f"{path.relative_to(root)}: contains placeholder marker {marker}")


def check_skill(
    skill_dir: Path,
    errors: list[str],
    *,
    root: Path | None = None,
    heading_cache: dict[Path, set[str]] | None = None,
) -> int:
    base_root = ROOT if root is None else root
    skill_file = skill_dir / "SKILL.md"
    rel = skill_file.relative_to(base_root)

    if skill_dir.is_symlink():
        errors.append(
            f"{skill_dir.relative_to(base_root)}: symlinked skill directory is not allowed"
        )
        return 0

    all_entries = sorted(skill_dir.rglob("*"))
    found_symlinks = False
    for entry in all_entries:
        if entry.is_symlink():
            errors.append(
                f"{entry.relative_to(base_root)}: symlink inside skill directory is not allowed"
            )
            found_symlinks = True
    if found_symlinks:
        return 0

    if not skill_file.is_file():
        errors.append(f"{skill_dir.relative_to(base_root)}: missing SKILL.md")
        return 0

    if not SKILL_ID_RE.fullmatch(skill_dir.name):
        errors.append(f"{rel}: directory name must be lowercase kebab-case")
    if len(skill_dir.name) > 64:
        errors.append(f"{rel}: directory name must be 64 characters or fewer")

    skill_text = skill_file.read_text(encoding="utf-8")
    try:
        frontmatter, body = parse_frontmatter_text(skill_text)
    except (ValueError, yaml.YAMLError) as error:
        errors.append(f"{rel}: invalid frontmatter: {error}")
        return 0

    if any(not isinstance(key, str) for key in frontmatter):
        errors.append(f"{rel}: frontmatter keys must be strings")
    unknown_keys = sorted(
        key for key in frontmatter if isinstance(key, str) and key not in ALLOWED_FRONTMATTER_KEYS
    )
    if unknown_keys:
        errors.append(f"{rel}: unknown frontmatter key(s): {', '.join(unknown_keys)}")

    for key in ("name", "description", "license"):
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{rel}: frontmatter needs a non-empty '{key}'")

    name = frontmatter.get("name")
    if isinstance(name, str) and name.strip():
        if not SKILL_ID_RE.fullmatch(name) or len(name) > 64:
            errors.append(
                f"{rel}: frontmatter 'name' ({name!r}) must be lowercase kebab-case (1-64 chars)"
            )
        elif name != skill_dir.name:
            errors.append(
                f"{rel}: frontmatter 'name' ({name!r}) must match directory name ({skill_dir.name!r})"
            )

    if "compatibility" in frontmatter:
        compat = frontmatter["compatibility"]
        if not isinstance(compat, str) or not compat.strip():
            errors.append(f"{rel}: frontmatter 'compatibility' must be a non-empty string")
        elif len(compat) > COMPATIBILITY_MAX_LEN:
            errors.append(
                f"{rel}: frontmatter 'compatibility' exceeds {COMPATIBILITY_MAX_LEN} characters"
            )

    if "allowed-tools" in frontmatter:
        allowed_tools = frontmatter["allowed-tools"]
        if not isinstance(allowed_tools, str) or not allowed_tools.strip():
            errors.append(f"{rel}: frontmatter 'allowed-tools' must be a non-empty string")

    disable_model = frontmatter.get("disable-model-invocation")
    if "disable-model-invocation" in frontmatter and not isinstance(disable_model, bool):
        errors.append(f"{rel}: frontmatter 'disable-model-invocation' must be a boolean")

    autoinvoke: bool | None = None
    if "metadata" in frontmatter:
        metadata = frontmatter["metadata"]
        if not isinstance(metadata, dict):
            errors.append(f"{rel}: frontmatter 'metadata' must be a mapping")
        else:
            for meta_key, meta_val in metadata.items():
                if not isinstance(meta_key, str) or not meta_key.strip():
                    errors.append(f"{rel}: frontmatter 'metadata' keys must be non-empty strings")
                elif meta_key == "opencode/autoinvoke":
                    if not isinstance(meta_val, bool):
                        errors.append(
                            f"{rel}: frontmatter 'metadata.opencode/autoinvoke' must be a boolean"
                        )
                    else:
                        autoinvoke = meta_val
                elif not isinstance(meta_val, str):
                    errors.append(
                        f"{rel}: frontmatter 'metadata.{meta_key}' must be a string"
                    )

    if isinstance(disable_model, bool) and autoinvoke is not None and disable_model == autoinvoke:
        errors.append(
            f"{rel}: conflicting 'disable-model-invocation' ({disable_model}) and "
            f"'metadata.opencode/autoinvoke' ({autoinvoke})"
        )

    description = frontmatter.get("description", "")
    description_bytes = 0
    if isinstance(description, str):
        description_bytes = len(description.encode("utf-8"))
        if len(description.strip()) < 40:
            errors.append(f"{rel}: description is too short to advertise clearly")
        if len(description) > 1024:
            errors.append(f"{rel}: description exceeds 1024 characters")

    if not body.strip():
        errors.append(f"{rel}: SKILL.md body is empty")

    md_files = [p for p in all_entries if p.is_file() and p.suffix == ".md"]
    has_manifest = check_reading_sets(skill_dir, body, errors, root=base_root, md_files=md_files)

    if not has_manifest:
        for reference in md_files:
            parts = reference.relative_to(skill_dir).parts
            if parts[0] == "references":
                routing_path = reference.relative_to(skill_dir).as_posix()
                if routing_path not in body:
                    errors.append(f"{rel}: reference not mentioned in routing -> {routing_path}")

    _check_local_refs(skill_file, body, skill_dir, errors, root=base_root)
    check_markdown_links(
        skill_file,
        errors,
        root=base_root,
        skill_dir=skill_dir,
        text=skill_text,
        heading_cache=heading_cache,
    )
    _check_placeholders(skill_file, skill_text, errors, root=base_root)

    for path in all_entries:
        if not path.is_file() or path == skill_file:
            continue
        if path.suffix == ".md":
            content = path.read_text(encoding="utf-8")
            if not content:
                errors.append(f"{path.relative_to(base_root)}: empty markdown file")
            _check_local_refs(path, content, skill_dir, errors, root=base_root)
            check_markdown_links(
                path,
                errors,
                root=base_root,
                skill_dir=skill_dir,
                text=content,
                heading_cache=heading_cache,
            )
            _check_placeholders(path, content, errors, root=base_root)
        elif path.suffix in (".css", ".json", ".py", ".sh"):
            _check_placeholders(path, path.read_text(encoding="utf-8"), errors, root=base_root)

    return description_bytes


def check_installer(errors: list[str], *, root: Path | None = None) -> None:
    base_root = ROOT if root is None else root
    install_dir = base_root / "install"
    if install_dir.is_symlink():
        errors.append("install: symlinked installer directory is not allowed")
        return
    scripts = (
        ("install/antigravity.sh", True),
        ("install/opencode.sh", True),
        ("install/lib.sh", False),
    )
    for rel_str, require_exec in scripts:
        installer = install_dir / Path(rel_str).name
        if installer.is_symlink():
            errors.append(f"{rel_str}: symlinked installer script is not allowed")
            continue
        if not installer.is_file():
            errors.append(f"{rel_str}: missing")
            continue
        if require_exec and not installer.stat().st_mode & 0o111:
            errors.append(f"{rel_str}: not executable")
        result = subprocess.run(
            ["bash", "-n", str(installer)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            errors.append(f"{rel_str}: bash syntax error: {result.stderr.strip()}")


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
    """Return (block context, property, value) for simple custom properties (string-aware)."""
    declarations: list[tuple[tuple[str, ...], str, str]] = []
    stack: list[str] = []
    buffer: list[str] = []
    n = len(text)
    i = 0
    in_quote = ""

    def record() -> None:
        declaration = "".join(buffer).strip()
        buffer.clear()
        if not declaration.startswith("--") or ":" not in declaration:
            return
        name, value = declaration.split(":", 1)
        declarations.append((tuple(stack), name.strip(), value.strip()))

    while i < n:
        ch = text[i]
        if in_quote:
            buffer.append(ch)
            if ch == "\\" and i + 1 < n:
                buffer.append(text[i + 1])
                i += 2
                continue
            if ch == in_quote:
                in_quote = ""
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        if ch in ("'", '"'):
            in_quote = ch
            buffer.append(ch)
            i += 1
            continue
        if ch == "{":
            stack.append("".join(buffer).strip())
            buffer.clear()
        elif ch == "}":
            record()
            if stack:
                stack.pop()
        elif ch == ";":
            record()
        else:
            buffer.append(ch)
        i += 1
    record()
    return declarations


def _selector_matches(block: str, target: str) -> bool:
    for selector in block.split(","):
        normalized = re.sub(r"\s+", " ", selector.strip())
        if target == ":root" and normalized == ":root":
            return True
        if target == "dark" and normalized in (
            '[data-theme="dark"]',
            "[data-theme='dark']",
            ':root[data-theme="dark"]',
            ":root[data-theme='dark']",
        ):
            return True
    return False


def semantic_tokens_from_declarations(
    declarations: Sequence[tuple[tuple[str, ...], str, str]],
) -> set[str]:
    tokens: set[str] = set()
    for context, name, _ in declarations:
        if not name.startswith("--color-"):
            continue
        if any(block.startswith(("@media", "@supports")) for block in context):
            continue
        tokens.add(name)
    return tokens


def semantic_tokens(tokens_css: str) -> set[str]:
    return semantic_tokens_from_declarations(css_declarations(tokens_css))


def resolve_theme_tokens_from_declarations(
    declarations: Sequence[tuple[tuple[str, ...], str, str]],
) -> dict[str, dict[str, str]]:
    root_properties: dict[str, str] = {}
    dark_properties: dict[str, str] = {}
    for context, name, value in declarations:
        inside_media = any(block.startswith(("@media", "@supports")) for block in context)
        if inside_media:
            continue
        if any(_selector_matches(block, "dark") for block in context):
            dark_properties[name] = value
        elif any(_selector_matches(block, ":root") for block in context):
            root_properties[name] = value

    def resolve(name: str, properties: dict[str, str], seen: set[str]) -> str | None:
        if name in seen or name not in properties:
            return None
        value = properties[name]
        match = VAR_RE.fullmatch(value)
        if match:
            resolved = resolve(match.group(1), properties, seen | {name})
            if resolved is not None:
                return resolved
            fallback = match.group(2)
            return fallback.strip() if fallback and fallback.strip() else None
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


def resolve_theme_tokens(tokens_css: str) -> dict[str, dict[str, str]]:
    return resolve_theme_tokens_from_declarations(css_declarations(tokens_css))


def check_contrast_fixture(
    fixture: Path,
    tokens_css: Path,
    contrast,
    errors: list[str],
    *,
    root: Path | None = None,
) -> None:
    base_root = ROOT if root is None else root
    fixture_rel = fixture.relative_to(base_root)
    try:
        data = json.loads(fixture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{fixture_rel}: invalid JSON: {error}")
        return
    if not isinstance(data, dict):
        errors.append(f"{fixture_rel}: fixture must be a JSON object")
        return

    pairs = data.get("pairs")
    if not isinstance(pairs, list):
        errors.append(f"{fixture_rel}: fixture needs a 'pairs' list")
        return
    if len(pairs) != CONTRAST_PAIR_COUNT:
        errors.append(f"{fixture_rel}: expected {CONTRAST_PAIR_COUNT} pairs, found {len(pairs)}")

    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        errors.append(f"{fixture_rel}: fixture needs a 'coverage' mapping")
        coverage = {}

    combinations = data.get("combinations")
    if not isinstance(combinations, list):
        errors.append(f"{fixture_rel}: fixture needs a 'combinations' list")
        combinations = []

    has_tokens_css = tokens_css.is_file()
    if has_tokens_css:
        decls = css_declarations(tokens_css.read_text(encoding="utf-8"))
        defined_tokens = semantic_tokens_from_declarations(decls)
        resolved_tokens = resolve_theme_tokens_from_declarations(decls)
    else:
        errors.append(f"{tokens_css.relative_to(base_root)}: missing token source")
        defined_tokens = set()
        resolved_tokens = {}

    labels: set[str] = set()
    theme_counts = {"light": 0, "dark": 0}
    label_tokens: dict[str, set[str]] = {}
    label_themes: dict[str, str] = {}
    parsed_token_colors: dict[tuple[str, str], object] = {}

    def get_token_color(theme: str, token: str):
        cache_key = (theme, token)
        if cache_key in parsed_token_colors:
            return parsed_token_colors[cache_key]
        raw = resolved_tokens.get(theme, {}).get(token)
        if raw is None:
            return None
        color = contrast.parse_color(raw)
        parsed_token_colors[cache_key] = color
        return color

    for index, item in enumerate(pairs):
        where = f"{fixture_rel}: pair {index}"
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
        string_fields = ("label", "theme", "fg_token", "bg_token")
        if not all(isinstance(item[field], str) and item[field].strip() for field in string_fields):
            errors.append(f"{where} fields {', '.join(string_fields)} must be non-empty strings")
            continue
        label = item["label"]
        theme = item["theme"]
        fg_token = item["fg_token"]
        bg_token = item["bg_token"]
        fg, bg, size = item["fg"], item["bg"], item["size"]

        if label in labels:
            errors.append(f"{where} duplicates label {label!r}")
        labels.add(label)
        label_theme = label.split(":", 1)[0] if ":" in label else ""
        if label_theme in theme_counts:
            theme_counts[label_theme] += 1
        else:
            errors.append(f"{where} label must start with 'light:' or 'dark:'")
        if not isinstance(size, str) or size not in CONTRAST_SIZES:
            errors.append(f"{where} has invalid size {size!r}")
        if not isinstance(fg, str) or not fg.strip():
            errors.append(f"{where} needs a non-empty fg color")
        if not isinstance(bg, str) or not bg.strip():
            errors.append(f"{where} needs a non-empty bg color")

        parsed_pair: dict[str, object] = {}
        for field, value in (("fg", fg), ("bg", bg)):
            if isinstance(value, str) and value.strip():
                try:
                    parsed_pair[field] = contrast.parse_color(value)
                except (TypeError, ValueError):
                    errors.append(f"{where} has invalid {field} color {value!r}")

        if len(parsed_pair) == 2 and isinstance(size, str) and size in CONTRAST_SIZES:
            result = contrast.check_pair(parsed_pair["fg"], parsed_pair["bg"], label, size)
            if not result.aa:
                errors.append(
                    f"token contrast fixture: {label} fails AA "
                    f"({result.ratio:.2f}:1, needs {result.threshold:.1f}:1)"
                )

        if not has_tokens_css:
            continue

        if theme != label_theme:
            errors.append(
                f"{fixture_rel}: pair {label!r} theme {theme!r} "
                f"does not match label theme {label_theme!r}"
            )
        if theme not in resolved_tokens:
            errors.append(f"{fixture_rel}: pair {label!r} has unknown theme {theme!r}")
            continue
        for field, token in (("fg", fg_token), ("bg", bg_token)):
            value = resolved_tokens[theme].get(token)
            if value is None:
                errors.append(f"{fixture_rel}: pair {label!r} has unknown {field} token")
                continue
            actual_color = parsed_pair.get(field)
            if actual_color is None:
                continue
            try:
                expected_color = get_token_color(theme, token)
            except (TypeError, ValueError):
                continue
            if expected_color is None:
                continue
            expected_hex = expected_color.hex()
            actual_hex = actual_color.hex()
            if expected_hex != actual_hex:
                errors.append(
                    f"{fixture_rel}: pair {label!r} {field} {actual_hex} "
                    f"does not match {token} ({expected_hex})"
                )
        label_tokens[label] = {fg_token, bg_token}
        label_themes[label] = theme

    for theme in ("light", "dark"):
        if theme_counts[theme] != CONTRAST_THEME_PAIR_COUNT:
            errors.append(
                f"{fixture_rel}: expected {CONTRAST_THEME_PAIR_COUNT} "
                f"{theme} pairs, found {theme_counts[theme]}"
            )

    if not has_tokens_css:
        return

    combination_labels: set[str] = set()
    for index, item in enumerate(combinations):
        where = f"{fixture_rel}: combination {index}"
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
        if isinstance(theme, str):
            label_themes[label] = theme
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
            if token not in resolved_tokens[theme]:
                errors.append(f"{where} references unknown token {token!r}")
                continue
            try:
                color = get_token_color(theme, token)
            except (TypeError, ValueError):
                errors.append(f"{where} token {token!r} does not resolve to a color")
                continue
            if color is not None:
                colors[field] = color
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
            f"{fixture_rel}: semantic token(s) without contrast "
            f"coverage: {', '.join(missing_coverage)}"
        )
    stale_coverage = sorted(set(coverage) - defined_tokens)
    if stale_coverage:
        errors.append(
            f"{fixture_rel}: coverage references unknown token(s): {', '.join(stale_coverage)}"
        )

    for token, entry in sorted(coverage.items()):
        where = f"{fixture_rel}: coverage for {token}"
        if isinstance(entry, list):
            if not entry:
                errors.append(f"{where} must list at least one pair or combination")
                continue
            covered_themes: set[str] = set()
            for label in entry:
                if not isinstance(label, str) or not label.strip():
                    errors.append(f"{where} needs non-empty pair labels")
                elif label not in known_labels:
                    errors.append(f"{where} references unknown label {label!r}")
                elif token not in label_tokens.get(label, set()):
                    errors.append(f"{where} label {label!r} does not test {token}")
                else:
                    covered_theme = label_themes.get(label)
                    if covered_theme:
                        covered_themes.add(covered_theme)
            for required_theme in ("light", "dark"):
                if (
                    token in resolved_tokens.get(required_theme, {})
                    and required_theme not in covered_themes
                ):
                    errors.append(f"{where} is missing {required_theme} theme coverage")
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


def check_contrast(errors: list[str], *, root: Path | None = None) -> None:
    base_root = ROOT if root is None else root
    skills_dir = base_root / "skills"
    script = skills_dir / "frontend-design" / "scripts" / "contrast.py"
    fixture = skills_dir / "frontend-design" / "assets" / "token-contrast-pairs.json"
    tokens_css = skills_dir / "frontend-design" / "assets" / "tokens.css"

    if not script.is_file():
        errors.append(f"{script.relative_to(base_root)}: missing contrast checker")
        return
    if not fixture.is_file():
        errors.append(f"{fixture.relative_to(base_root)}: missing contrast fixture")
    if not tokens_css.is_file():
        errors.append(f"{tokens_css.relative_to(base_root)}: missing token source")

    try:
        contrast = load_contrast_module(script)
    except Exception as error:  # noqa: BLE001 - report any import failure
        errors.append(f"{script.relative_to(base_root)}: cannot import: {error}")
        return

    if fixture.is_file():
        check_contrast_fixture(fixture, tokens_css, contrast, errors, root=base_root)

    buf = io.StringIO()
    with redirect_stdout(buf):
        self_test_rc = contrast.self_test()
    if self_test_rc != 0:
        errors.append(f"contrast self-test: failed\n{buf.getvalue()}".strip())


def check_root_docs(
    errors: list[str],
    *,
    root: Path | None = None,
    heading_cache: dict[Path, set[str]] | None = None,
) -> None:
    base_root = ROOT if root is None else root
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
        path = base_root / name
        if not path.is_file():
            errors.append(f"{name}: missing")
            continue
        check_markdown_links(path, errors, root=base_root, heading_cache=heading_cache)
    docs_dir = base_root / "docs"
    if docs_dir.is_dir():
        for path in sorted(docs_dir.rglob("*.md")):
            if not path.is_file():
                continue
            check_markdown_links(path, errors, root=base_root, heading_cache=heading_cache)


def check_github_docs(
    errors: list[str],
    *,
    root: Path | None = None,
    heading_cache: dict[Path, set[str]] | None = None,
) -> None:
    base_root = ROOT if root is None else root
    github_dir = base_root / ".github"
    if not github_dir.is_dir():
        return
    for path in sorted(github_dir.rglob("*.md")):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if not content:
            errors.append(f"{path.relative_to(base_root)}: empty markdown file")
        check_markdown_links(
            path, errors, root=base_root, text=content, heading_cache=heading_cache
        )


def check_yaml(errors: list[str], *, root: Path | None = None) -> None:
    base_root = ROOT if root is None else root
    github_dir = base_root / ".github"
    if not github_dir.is_dir():
        return
    workflows_dir = (github_dir / "workflows").resolve()
    paths = sorted(github_dir.rglob("*.yml"))
    paths.extend(sorted(github_dir.rglob("*.yaml")))
    for path in paths:
        # Workflows are validated structurally and for policy by scripts/check_workflows.py.
        if path.parent.resolve() == workflows_dir:
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            errors.append(f"{path.relative_to(base_root)}: invalid YAML: {error}")


def validate_repo(
    root: Path | None = None,
    *,
    skills_dir: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Run all repository validations without mutating module globals."""
    base_root = ROOT if root is None else root
    target_skills = (
        skills_dir
        if skills_dir is not None
        else (SKILLS_DIR if root is None else base_root / "skills")
    )
    errors: list[str] = []
    heading_cache: dict[Path, set[str]] = {}

    if not target_skills.is_dir():
        raise FileNotFoundError("skills/ directory not found")

    for entry in sorted(target_skills.iterdir()):
        if entry.is_symlink() and not entry.is_dir():
            errors.append(f"{entry.relative_to(base_root)}: symlink inside skills/ is not allowed")

    skill_dirs = sorted(path for path in target_skills.iterdir() if path.is_dir())
    if not skill_dirs:
        raise FileNotFoundError("no skills found")

    total_description_bytes = 0
    for skill_dir in skill_dirs:
        total_description_bytes += check_skill(
            skill_dir, errors, root=base_root, heading_cache=heading_cache
        )
    if total_description_bytes > AGGREGATE_DESCRIPTION_LIMIT:
        errors.append(
            f"skills/: aggregate description bytes ({total_description_bytes} B) "
            f"exceed limit ({AGGREGATE_DESCRIPTION_LIMIT} B)"
        )

    check_installer(errors, root=base_root)
    check_contrast(errors, root=base_root)
    check_root_docs(errors, root=base_root, heading_cache=heading_cache)
    check_github_docs(errors, root=base_root, heading_cache=heading_cache)
    check_yaml(errors, root=base_root)
    return [skill_dir.name for skill_dir in skill_dirs], errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to validate (default: repository root)",
    )
    args = parser.parse_args([] if argv is None else argv)

    try:
        skill_names, errors = validate_repo(args.root.resolve() if args.root else None)
    except FileNotFoundError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if errors:
        print(f"Validation failed with {len(errors)} error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_names)} skill(s):")
    for name in skill_names:
        print(f"  - {name}")
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
