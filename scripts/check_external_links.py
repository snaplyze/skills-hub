#!/usr/bin/env python3
"""Check external HTTP(S) links in Markdown files.

The required checks stay offline and deterministic. This script is for a
separate scheduled/manual audit; it treats 404/410 and server errors as
failures, follows redirects, and reports bot-blocked responses (403/429) as
unverified rather than pretending they passed.

Usage:
    python3 scripts/check_external_links.py
    python3 scripts/check_external_links.py --root . --timeout 15
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s<>()\]\"']+")
SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".ruff_cache",
        ".pytest_cache",
        ".playwright-cli",
    }
)
USER_AGENT = "skills-hub-link-check/1.0 (+https://github.com/snaplyze/skills-hub)"


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.md") if not any(part in SKIP_DIRS for part in path.parts)
    )


def external_urls(root: Path) -> list[str]:
    urls: set[str] = set()
    for path in markdown_files(root):
        for match in URL_RE.finditer(path.read_text(encoding="utf-8")):
            url = match.group(0).rstrip(".,;:")
            if any(marker in url for marker in ("$", "{", "}")):
                continue
            parts = urllib.parse.urlsplit(url)
            if parts.scheme in ("http", "https") and parts.netloc:
                urls.add(url)
    return sorted(urls)


def probe(url: str, timeout: float) -> tuple[str, int | None, str]:
    """Return (state, status, detail); state is ok, unverified, or failed."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url,
            method=method,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return "ok", response.status, f"{method} {response.status}"
        except urllib.error.HTTPError as error:
            status = error.code
            if method == "HEAD" and status in (403, 405, 429):
                continue
            if status in (403, 429):
                return "unverified", status, f"{method} {status} (bot protection)"
            return "failed", status, f"{method} {status}"
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if method == "HEAD":
                continue
            return "failed", None, f"{method} {error}"
    return "failed", None, "no HTTP response"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    urls = external_urls(root)
    if not urls:
        print("No external links found.")
        return 0

    failures = 0
    unverified = 0
    for url in urls:
        state, status, detail = probe(url, args.timeout)
        if state == "failed":
            failures += 1
            print(f"FAIL {url} ({detail})", file=sys.stderr)
        elif state == "unverified":
            unverified += 1
            print(f"SKIP {url} ({detail})", file=sys.stderr)

    print(
        f"Checked {len(urls)} external link(s): "
        f"{len(urls) - failures - unverified} ok, {unverified} unverified, {failures} failed"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
