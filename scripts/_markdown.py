"""Shared stdlib-only CommonMark preprocessing helpers for repository scripts.

Loaded both as ``scripts._markdown`` (under ``pytest`` / package imports) and
by sibling path via ``importlib.util`` (under ``python3 -I`` isolated mode).
"""

from __future__ import annotations

import re

OPEN_BACKTICK_FENCE_RE = re.compile(r"^ {0,3}(`{3,})[^`]*$")
OPEN_TILDE_FENCE_RE = re.compile(r"^ {0,3}(~{3,}).*$")
BLOCKQUOTE_MARKER_RE = re.compile(r"^ {0,3}> ?")
MASK_TOKEN_RE = re.compile(r"<!--|`+")
BLANK_LINE_RE = re.compile(r"\n[ \t]*\n")


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_frontmatter(text: str) -> str:
    """Remove leading YAML frontmatter block if properly closed."""
    normalized = normalize_newlines(text)
    if normalized.startswith("---\n"):
        match = re.search(r"\n---(?:\n|$)", normalized[3:])
        if match is not None:
            return normalized[3 + match.end() :]
    return normalized


def mask_frontmatter(text: str) -> str:
    """Blank leading YAML frontmatter lines while preserving 1-based line numbers."""
    normalized = normalize_newlines(text)
    if normalized.startswith("---\n"):
        match = re.search(r"\n---(?:\n|$)", normalized[3:])
        if match is not None:
            end = 3 + match.end()
            prefix = normalized[:end]
            newline_count = prefix.count("\n")
            return ("\n" * newline_count) + normalized[end:]
    return normalized


def _split_blockquote_prefix(line: str) -> tuple[int, str]:
    depth = 0
    rest = line
    while True:
        match = BLOCKQUOTE_MARKER_RE.match(rest)
        if match is None:
            return depth, rest
        depth += 1
        rest = rest[match.end() :]


def _strip_n_blockquotes(line: str, count: int) -> str:
    rest = line
    for _ in range(count):
        match = BLOCKQUOTE_MARKER_RE.match(rest)
        if match is None:
            break
        rest = rest[match.end() :]
    return rest


def strip_fenced_code(text: str) -> str:
    """Blank CommonMark fenced code blocks (including blockquote fences) keeping line numbers."""
    lines: list[str] = []
    fence_char = ""
    fence_bq_depth = 0
    close_re: re.Pattern[str] | None = None

    for line in normalize_newlines(text).splitlines():
        bq_depth, rest = _split_blockquote_prefix(line)

        if fence_char:
            if bq_depth < fence_bq_depth:
                # Exiting the enclosing blockquote closes the fenced block in CommonMark;
                # re-process the current line as normal Markdown.
                fence_char = ""
                fence_bq_depth = 0
                close_re = None
            else:
                assert close_re is not None
                inner = _strip_n_blockquotes(line, fence_bq_depth) if fence_bq_depth else line
                if close_re.match(inner):
                    fence_char = ""
                    fence_bq_depth = 0
                    close_re = None
                lines.append("")
                continue

        match = OPEN_BACKTICK_FENCE_RE.match(rest) or OPEN_TILDE_FENCE_RE.match(rest)
        if match:
            fence = match.group(1)
            fence_char = fence[0]
            fence_bq_depth = bq_depth
            close_re = re.compile(rf"^ {{0,3}}{re.escape(fence_char)}{{{len(fence)},}}[ \t]*$")
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
            if token == "<!--":
                out.append(token)
                pos = end
            else:
                # Per CommonMark §2.4, a backslash escapes only the single next character,
                # so in \``code` the second backtick still opens a 1-tick code span.
                out.append("`")
                pos = start + 1
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
        blank = BLANK_LINE_RE.search(text, end)
        limit = n if blank is None else blank.start()
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


def preprocess_markdown(text: str, *, preserve_line_numbers: bool = False) -> tuple[str, str]:
    """Strip/mask frontmatter and fenced code, then mask inline code and HTML comments once."""
    without_fm = mask_frontmatter(text) if preserve_line_numbers else strip_frontmatter(text)
    stripped = strip_fenced_code(without_fm)
    return stripped, mask_code_and_comments(stripped)
