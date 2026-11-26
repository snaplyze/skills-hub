#!/usr/bin/env python3
"""Check external HTTP(S) links in Markdown files.

The required checks stay offline and deterministic. This script is for a
separate scheduled/manual audit; it treats 404/410 and server errors as
failures, follows safe HTTP(S) redirects, blocks non-global IP addresses and
non-HTTP(S) schemes unless --allow-local is set, and reports bot-blocked
responses (403/429) as unverified rather than pretending they passed.

Usage:
    python3 scripts/check_external_links.py
    python3 scripts/check_external_links.py --root . --timeout 15
    python3 scripts/check_external_links.py --root /tmp/test --allow-local
"""

from __future__ import annotations

import argparse
import http.client
import ipaddress
import math
import os
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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
DEFAULT_WORKERS = 8
DEFAULT_MAX_PER_HOST = 2
MAX_REDIRECTS = 10

_FENCE_OPEN_RE = re.compile(r"^((?:[ \t]*>[ \t]*)*)[ \t]*(`{3,}|~{3,})")
_HTTP_URL_START_RE = re.compile(r"https?://", re.IGNORECASE)
_SSL_CONTEXT_LOCK = threading.Lock()
_SSL_CONTEXT: ssl.SSLContext | None = None


class SSRFBlockedError(ValueError):
    """Raised when a URL scheme, authority, or resolved IP violates the SSRF policy."""


def _default_ssl_context() -> ssl.SSLContext:
    global _SSL_CONTEXT
    with _SSL_CONTEXT_LOCK:
        if _SSL_CONTEXT is None:
            _SSL_CONTEXT = ssl.create_default_context()
        return _SSL_CONTEXT


def markdown_files(root: Path) -> list[Path]:
    """Return sorted Markdown files under root, pruning ignored directories."""
    resolved_root = root.resolve()
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(resolved_root, topdown=True, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        current = Path(dirpath)
        for filename in sorted(filenames):
            if not filename.endswith(".md"):
                continue
            candidate = current / filename
            if candidate.is_symlink():
                continue
            files.append(candidate)
    files.sort(key=lambda path: path.relative_to(resolved_root).as_posix())
    return files


def _strip_inline_code(line: str) -> str:
    """Replace CommonMark inline code spans with spaces."""
    if "`" not in line:
        return line
    out: list[str] = []
    i = 0
    length = len(line)
    while i < length:
        if line[i] != "`":
            out.append(line[i])
            i += 1
            continue
        run_end = i
        while run_end < length and line[run_end] == "`":
            run_end += 1
        tick_len = run_end - i
        j = run_end
        closed = -1
        while j < length:
            if line[j] == "`":
                close_end = j
                while close_end < length and line[close_end] == "`":
                    close_end += 1
                if close_end - j == tick_len:
                    closed = close_end
                    break
                j = close_end
            else:
                j += 1
        if closed != -1:
            out.append(" " * (closed - i))
            i = closed
        else:
            out.append(line[i:run_end])
            i = run_end
    return "".join(out)


def _extract_urls_from_line(line: str) -> list[str]:
    """Extract HTTP(S) URLs from a single non-fenced Markdown line."""
    cleaned = _strip_inline_code(line)
    found: list[str] = []
    pos = 0
    length = len(cleaned)
    while pos < length:
        match = _HTTP_URL_START_RE.search(cleaned, pos)
        if not match:
            break
        start = match.start()
        i = match.end()
        paren = 0
        bracket = 0
        while i < length:
            ch = cleaned[i]
            if ch.isspace() or ch in "<>\"'`":
                break
            if ch == "(":
                paren += 1
            elif ch == ")":
                if paren == 0:
                    break
                paren -= 1
            elif ch == "[":
                bracket += 1
            elif ch == "]":
                if bracket == 0:
                    break
                bracket -= 1
            i += 1
        pos = i
        url = cleaned[start:i].rstrip(".,;:*_")
        if any(marker in url for marker in ("$", "{", "}")):
            continue
        try:
            parts = urllib.parse.urlsplit(url)
        except ValueError:
            continue
        if parts.scheme.lower() in ("http", "https") and parts.netloc:
            found.append(url)
    return found


def external_url_locations(root: Path) -> dict[str, list[tuple[str, int]]]:
    """Return mapping of external HTTP(S) URL -> sorted [(relative_path, line_no)]."""
    resolved_root = root.resolve()
    locations: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for path in markdown_files(resolved_root):
        rel = path.relative_to(resolved_root).as_posix()
        fence: tuple[str, str, int] | None = None
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if fence is None:
                open_match = _FENCE_OPEN_RE.match(line)
                if open_match:
                    quote_prefix, marker = open_match.group(1), open_match.group(2)
                    if marker[0] == "~" or "`" not in line[open_match.end() :]:
                        fence = (quote_prefix, marker[0], len(marker))
                        continue
            else:
                q_prefix, fence_char, fence_len = fence
                body = line[len(q_prefix) :] if q_prefix and line.startswith(q_prefix) else line
                close_pattern = rf"^[ \t]*{re.escape(fence_char)}{{{fence_len},}}[ \t]*$"
                if re.match(close_pattern, body):
                    fence = None
                continue
            for url in _extract_urls_from_line(line):
                entry = (rel, line_no)
                if entry not in locations[url]:
                    locations[url].append(entry)
    return {url: locations[url] for url in sorted(locations)}


def external_urls(root: Path) -> list[str]:
    return list(external_url_locations(root))


def _is_global_ip(raw_address: str) -> bool:
    ip = ipaddress.ip_address(raw_address)
    unwrapped = getattr(ip, "ipv4_mapped", None) or ip
    return (
        unwrapped.is_global
        and not unwrapped.is_private
        and not unwrapped.is_loopback
        and not unwrapped.is_link_local
        and not unwrapped.is_multicast
        and not unwrapped.is_reserved
        and not unwrapped.is_unspecified
        and not getattr(unwrapped, "is_site_local", False)
    )


def _resolve_and_validate(
    host: str, port: int, *, allow_local: bool
) -> list[tuple[int, int, int, str, tuple]]:
    try:
        infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    except (UnicodeError, ValueError) as err:
        raise OSError(f"invalid hostname {host!r}: {err}") from err
    if not infos:
        raise OSError(f"DNS lookup returned no addresses for {host!r}")
    if not allow_local:
        for _, _, _, _, sockaddr in infos:
            addr = str(sockaddr[0])
            if not _is_global_ip(addr):
                raise SSRFBlockedError(f"blocked non-global IP {addr} for host {host!r}")
    return infos


def _validate_url(url: str, *, allow_local: bool) -> tuple[str, int]:
    """Validate URL scheme, authority, port, and resolved IP addresses."""
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in url):
        raise SSRFBlockedError(f"control character in URL {url!r}")
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError as err:
        raise SSRFBlockedError(f"malformed URL {url!r}: {err}") from err
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        raise SSRFBlockedError(f"blocked non-HTTP(S) scheme {scheme!r}")
    if parts.username is not None or parts.password is not None:
        raise SSRFBlockedError("embedded credentials are not allowed in URL")
    host = parts.hostname
    if not host:
        raise SSRFBlockedError(f"missing host in URL {url!r}")
    try:
        explicit_port = parts.port
    except ValueError as err:
        raise SSRFBlockedError(f"invalid port in URL {url!r}") from err
    if explicit_port is not None:
        if explicit_port == 0:
            raise SSRFBlockedError("port 0 is not allowed")
        port = explicit_port
    else:
        port = 443 if scheme == "https" else 80
    if not allow_local:
        try:
            ipaddress.ip_address(host)
        except ValueError:
            _resolve_and_validate(host, port, allow_local=False)
        else:
            if not _is_global_ip(host):
                raise SSRFBlockedError(f"blocked non-global IP {host}")
    return host, port


def _connect_validated_socket(
    host: str,
    port: int,
    *,
    allow_local: bool,
    deadline: float,
    source_address: tuple[str, int] | None = None,
) -> socket.socket:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("request deadline exceeded")
    infos = _resolve_and_validate(host, port, allow_local=allow_local)
    last_error: OSError | None = None
    for family, socktype, proto, _, sockaddr in infos:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("request deadline exceeded")
        sock: socket.socket | None = None
        try:
            sock = socket.socket(family, socktype, proto)
            sock.settimeout(remaining)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            post_connect = deadline - time.monotonic()
            if post_connect <= 0:
                sock.close()
                raise TimeoutError("request deadline exceeded")
            sock.settimeout(post_connect)
            return sock
        except OSError as err:
            last_error = err
            if sock is not None:
                sock.close()
    if last_error is not None:
        raise last_error
    raise OSError(f"could not connect to {host}:{port}")


class _SafeHTTPConnection(http.client.HTTPConnection):
    def __init__(
        self,
        host: str,
        port: int | None = None,
        timeout: float | None = None,
        source_address: tuple[str, int] | None = None,
        *,
        allow_local: bool,
        deadline: float,
    ) -> None:
        super().__init__(host, port=port, timeout=timeout, source_address=source_address)
        self._allow_local = allow_local
        self._deadline = deadline

    def connect(self) -> None:
        self.sock = _connect_validated_socket(
            self.host,
            self.port,
            allow_local=self._allow_local,
            deadline=self._deadline,
            source_address=self.source_address,
        )


class _SafeHTTPSConnection(http.client.HTTPSConnection):
    def __init__(
        self,
        host: str,
        port: int | None = None,
        timeout: float | None = None,
        source_address: tuple[str, int] | None = None,
        *,
        context: ssl.SSLContext | None = None,
        allow_local: bool,
        deadline: float,
    ) -> None:
        super().__init__(
            host,
            port=port,
            timeout=timeout,
            source_address=source_address,
            context=context,
        )
        self._allow_local = allow_local
        self._deadline = deadline

    def connect(self) -> None:
        sock = _connect_validated_socket(
            self.host,
            self.port,
            allow_local=self._allow_local,
            deadline=self._deadline,
            source_address=self.source_address,
        )
        try:
            remaining = self._deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("request deadline exceeded")
            sock.settimeout(remaining)
            wrapped = self._context.wrap_socket(sock, server_hostname=self.host)
            post_tls = self._deadline - time.monotonic()
            if post_tls <= 0:
                wrapped.close()
                raise TimeoutError("request deadline exceeded")
            wrapped.settimeout(post_tls)
            self.sock = wrapped
        except BaseException:
            sock.close()
            raise


class _SafeHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, *, allow_local: bool, deadline: float) -> None:
        super().__init__()
        self._allow_local = allow_local
        self._deadline = deadline

    def http_open(self, req: urllib.request.Request) -> http.client.HTTPResponse:
        return self.do_open(
            _SafeHTTPConnection,
            req,
            allow_local=self._allow_local,
            deadline=self._deadline,
        )


class _SafeHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, *, allow_local: bool, deadline: float, context: ssl.SSLContext) -> None:
        super().__init__(context=context)
        self._allow_local = allow_local
        self._deadline = deadline

    def https_open(self, req: urllib.request.Request) -> http.client.HTTPResponse:
        return self.do_open(
            _SafeHTTPSConnection,
            req,
            context=self._context,
            allow_local=self._allow_local,
            deadline=self._deadline,
        )


class _SafeRedirectHandler(urllib.request.BaseHandler):
    """Follow bounded HTTP(S) redirects without unbounded body reads or stale timeouts."""

    handler_order = 500

    def __init__(self, *, allow_local: bool, deadline: float) -> None:
        self._allow_local = allow_local
        self._deadline = deadline

    def http_error_302(
        self,
        req: urllib.request.Request,
        fp: object,
        code: int,
        msg: str,
        headers: http.client.HTTPMessage,
    ) -> object:
        try:
            location = headers.get("location") or headers.get("uri")
        finally:
            if hasattr(fp, "close"):
                fp.close()

        if not location:
            raise urllib.error.HTTPError(req.full_url, code, msg, headers, None)

        target = urllib.parse.urljoin(req.full_url, location.strip())
        _validate_url(target, allow_local=self._allow_local)

        count = int(getattr(req, "_redirect_count", 0)) + 1
        if count > MAX_REDIRECTS:
            raise urllib.error.HTTPError(
                req.full_url, code, f"exceeded max redirects ({MAX_REDIRECTS})", headers, None
            )

        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("request deadline exceeded")

        orig_method = req.get_method()
        if code in (307, 308):
            next_method = orig_method
        else:
            next_method = "HEAD" if orig_method == "HEAD" else "GET"

        new_req = urllib.request.Request(
            target,
            method=next_method,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"},
        )
        new_req._redirect_count = count  # type: ignore[attr-defined]
        return self.parent.open(new_req, timeout=remaining)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def _build_safe_opener(*, allow_local: bool, deadline: float) -> urllib.request.OpenerDirector:
    """Build an OpenerDirector limited strictly to validated HTTP(S) handlers."""
    opener = urllib.request.OpenerDirector()
    opener.add_handler(_SafeHTTPHandler(allow_local=allow_local, deadline=deadline))
    opener.add_handler(
        _SafeHTTPSHandler(
            allow_local=allow_local,
            deadline=deadline,
            context=_default_ssl_context(),
        )
    )
    opener.add_handler(_SafeRedirectHandler(allow_local=allow_local, deadline=deadline))
    opener.add_handler(urllib.request.HTTPDefaultErrorHandler())
    opener.add_handler(urllib.request.HTTPErrorProcessor())
    opener.add_handler(urllib.request.UnknownHandler())
    return opener


def probe(url: str, timeout: float, *, allow_local: bool = False) -> tuple[str, int | None, str]:
    """Return (state, status, detail); state is ok, unverified, or failed."""
    deadline = time.monotonic() + max(0.05, float(timeout))
    try:
        _validate_url(url, allow_local=allow_local)
    except SSRFBlockedError as error:
        return "failed", None, f"blocked: {error}"
    except (OSError, TimeoutError, ValueError) as error:
        return "failed", None, f"DNS/network {error}"

    opener = _build_safe_opener(allow_local=allow_local, deadline=deadline)
    for method in ("HEAD", "GET"):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "failed", None, f"timeout after {timeout:g}s"
        request = urllib.request.Request(
            url,
            method=method,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"},
        )
        try:
            with opener.open(request, timeout=remaining) as response:
                return "ok", response.status, f"{method} {response.status}"
        except SSRFBlockedError as error:
            return "failed", None, f"blocked: {error}"
        except urllib.error.HTTPError as error:
            try:
                status = error.code
            finally:
                error.close()
            if method == "HEAD" and status in (400, 403, 405, 429, 501):
                continue
            if status in (403, 429):
                return "unverified", status, f"{method} {status} (bot protection)"
            return "failed", status, f"{method} {status}"
        except (
            urllib.error.URLError,
            http.client.HTTPException,
            TimeoutError,
            OSError,
            ValueError,
        ) as error:
            if method == "HEAD" and deadline - time.monotonic() > 0.05:
                continue
            return "failed", None, f"{method} {error}"
    return "failed", None, "no HTTP response"


def _interleave_by_host(urls: list[str]) -> list[str]:
    """Round-robin URLs across hosts so busy hosts do not starve other hosts."""
    buckets: dict[str, deque[str]] = defaultdict(deque)
    for url in urls:
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        buckets[host].append(url)
    ordered_hosts = sorted(buckets, key=lambda host: (-len(buckets[host]), host))
    interleaved: list[str] = []
    while ordered_hosts:
        next_hosts: list[str] = []
        for host in ordered_hosts:
            interleaved.append(buckets[host].popleft())
            if buckets[host]:
                next_hosts.append(host)
        ordered_hosts = next_hosts
    return interleaved


def check_urls(
    urls: list[str],
    timeout: float,
    *,
    workers: int = DEFAULT_WORKERS,
    max_per_host: int = DEFAULT_MAX_PER_HOST,
    allow_local: bool = False,
) -> dict[str, tuple[str, int | None, str]]:
    """Probe URLs concurrently with a per-host concurrency cap."""
    if not urls:
        return {}
    per_host_limit = max(1, max_per_host)
    sem_lock = threading.Lock()
    host_semaphores: dict[str, threading.BoundedSemaphore] = {}

    def _run_one(url: str) -> tuple[str, tuple[str, int | None, str]]:
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        with sem_lock:
            semaphore = host_semaphores.get(host)
            if semaphore is None:
                semaphore = threading.BoundedSemaphore(per_host_limit)
                host_semaphores[host] = semaphore
        with semaphore:
            return url, probe(url, timeout, allow_local=allow_local)

    scheduled = _interleave_by_host(urls)
    pool_size = max(1, min(workers, len(scheduled)))
    results: dict[str, tuple[str, int | None, str]] = {}
    with ThreadPoolExecutor(max_workers=pool_size) as executor:
        for url, outcome in executor.map(_run_one, scheduled):
            results[url] = outcome
    return results


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return value


def _positive_float(raw: str) -> float:
    value = float(raw)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("must be a finite number > 0")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--timeout", type=_positive_float, default=15.0)
    parser.add_argument("--workers", type=_positive_int, default=DEFAULT_WORKERS)
    parser.add_argument("--max-per-host", type=_positive_int, default=DEFAULT_MAX_PER_HOST)
    parser.add_argument(
        "--allow-local",
        action="store_true",
        help="Allow loopback/private/non-global IP addresses (for local test servers).",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: root directory not found: {root}", file=sys.stderr)
        return 2

    url_locations = external_url_locations(root)
    if not url_locations:
        print("No external links found.")
        return 0

    urls = list(url_locations)
    outcomes = check_urls(
        urls,
        args.timeout,
        workers=args.workers,
        max_per_host=args.max_per_host,
        allow_local=args.allow_local,
    )

    failures = 0
    unverified = 0
    for url in urls:
        state, _, detail = outcomes[url]
        where = ", ".join(f"{path}:{line}" for path, line in url_locations[url])
        if state == "failed":
            failures += 1
            print(f"FAIL {url} ({detail}) [{where}]", file=sys.stderr)
        elif state == "unverified":
            unverified += 1
            print(f"SKIP {url} ({detail}) [{where}]", file=sys.stderr)

    print(
        f"Checked {len(urls)} external link(s): "
        f"{len(urls) - failures - unverified} ok, {unverified} unverified, {failures} failed"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
