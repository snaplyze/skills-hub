"""Shared test helpers for isolated Git environments and active shell command parsing."""

from __future__ import annotations

import os
import shlex
from collections.abc import Mapping
from pathlib import Path

ISOLATED_GIT_CONFIG_ARGS: tuple[str, ...] = (
    "-c",
    "core.excludesFile=",
    "-c",
    "commit.gpgsign=false",
    "-c",
    "tag.gpgsign=false",
)

_GIT_CONFIG_ENV_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
_GIT_CONFIG_ENV_EXACT = frozenset(
    {
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
        "GIT_CONFIG_SYSTEM",
    }
)
_SHELL_COMMAND_SEPARATORS = frozenset({";", "&", "&&", "|", "||", "(", ")"})


def isolated_git_env(
    base_env: Mapping[str, str] | None = None,
    *,
    home: Path | str | None = None,
) -> dict[str, str]:
    """Return an environment immune to host global/system/env Git configuration."""
    source = os.environ if base_env is None else base_env
    env = {
        key: value
        for key, value in source.items()
        if key not in _GIT_CONFIG_ENV_EXACT and not key.startswith(_GIT_CONFIG_ENV_PREFIXES)
    }
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["LC_ALL"] = "C"
    if home is not None:
        env["HOME"] = str(home)
        env.pop("XDG_CONFIG_HOME", None)
    return env


def strip_shell_comments(line: str) -> str:
    """Remove full-line and inline shell comments while respecting single/double quotes."""
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and not in_single:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif (
            ch == "#"
            and not in_single
            and not in_double
            and (idx == 0 or line[idx - 1].isspace() or line[idx - 1] in ";|&()")
        ):
            return line[:idx].rstrip()
    return line.rstrip()


def _ends_with_line_continuation(raw_line: str, cleaned: str) -> bool:
    """Return True only when raw_line has no stripped comment and ends with an odd backslash run."""
    raw_no_eol = raw_line.rstrip("\r\n")
    if cleaned != raw_no_eol.strip():
        return False
    if not raw_no_eol.endswith("\\"):
        return False
    trailing_backslashes = len(raw_no_eol) - len(raw_no_eol.rstrip("\\"))
    return trailing_backslashes % 2 == 1


def active_shell_text(script: str) -> str:
    """Return active (comment-stripped) shell text joined across backslash continuations."""
    logical_lines: list[str] = []
    current = ""
    for raw_line in script.splitlines():
        cleaned = strip_shell_comments(raw_line).strip()
        if not cleaned:
            if current:
                logical_lines.append(current)
                current = ""
            continue
        if _ends_with_line_continuation(raw_line, cleaned):
            current += cleaned[:-1].rstrip() + " "
        else:
            current += cleaned
            logical_lines.append(current)
            current = ""
    if current:
        logical_lines.append(current)
    return "\n".join(logical_lines)


def _tokenize_shell_line(line: str) -> list[str]:
    """Tokenize an already comment-stripped shell line without treating mid-word # as comments."""
    lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:
        return line.split()


def active_shell_commands(script: str) -> list[list[str]]:
    """Split active (non-comment) shell script lines into individual simple commands."""
    commands: list[list[str]] = []
    for line in active_shell_text(script).splitlines():
        current: list[str] = []
        for token in _tokenize_shell_line(line):
            if token in _SHELL_COMMAND_SEPARATORS:
                if current:
                    commands.append(current)
                    current = []
            else:
                current.append(token)
        if current:
            commands.append(current)
    return commands


def active_shell_tokens(script: str) -> list[str]:
    """Return flat list of tokens across all active (non-comment) shell commands."""
    return [token for command in active_shell_commands(script) for token in command]
