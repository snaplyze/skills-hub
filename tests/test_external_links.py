"""Tests for the optional external-link audit."""

from __future__ import annotations

import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import scripts.check_external_links as cel
from scripts.check_external_links import (
    external_url_locations,
    external_urls,
    main,
    markdown_files,
    probe,
)


class Handler(BaseHTTPRequestHandler):
    in_flight_lock = threading.Lock()
    in_flight = 0
    peak_in_flight = 0
    trickle_get_hits = 0

    def do_HEAD(self) -> None:  # noqa: N802 - http.server API
        if self.path == "/head405":
            self.send_response(405)
            self.end_headers()
            return
        if self.path == "/head501":
            self.send_response(501)
            self.end_headers()
            return
        if self.path == "/redirect-trickle":
            # Force probe() to fall back to GET so _SafeRedirectHandler must avoid reading
            # the trickled 302 response body.
            self.send_response(405)
            self.end_headers()
            return
        if self.path == "/slow-head":
            time.sleep(0.35)
            self.send_response(200)
            self.end_headers()
            return
        if self.path in ("/bad-status", "/head-error-get-ok"):
            self.wfile.write(b"NOT_HTTP_GARBAGE\r\n\r\n")
            return
        self._respond(head=True)

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        if self.path == "/bad-status":
            self.wfile.write(b"NOT_HTTP_GARBAGE\r\n\r\n")
            return
        self._respond(head=False)

    def _respond(self, *, head: bool) -> None:
        if self.path.startswith("/paced/"):
            with Handler.in_flight_lock:
                Handler.in_flight += 1
                Handler.peak_in_flight = max(Handler.peak_in_flight, Handler.in_flight)
            try:
                time.sleep(0.08)
                self.send_response(200)
                self.end_headers()
                if not head:
                    self.wfile.write(b"ok")
            finally:
                with Handler.in_flight_lock:
                    Handler.in_flight -= 1
            return

        if self.path in ("/ok", "/head405", "/head501", "/head-error-get-ok", "/wiki/Foo_(bar)"):
            self.send_response(200)
            self.end_headers()
            if not head:
                self.wfile.write(b"ok")
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        elif self.path == "/redirect-loop":
            self.send_response(302)
            self.send_header("Location", "/redirect-loop")
            self.end_headers()
        elif self.path == "/redirect-trickle":
            if not head:
                with Handler.in_flight_lock:
                    Handler.trickle_get_hits += 1
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.send_header("Content-Length", "5")
            self.end_headers()
            if not head:
                for byte in b"hello":
                    try:
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        time.sleep(0.12)
                    except OSError:
                        break
        elif self.path == "/redirect-ftp":
            self.send_response(302)
            self.send_header("Location", "ftp://example.com/archive.tar.gz")
            self.end_headers()
        elif self.path == "/redirect-file":
            self.send_response(301)
            self.send_header("Location", "file:///etc/passwd")
            self.end_headers()
        elif self.path == "/redirect-loopback-302":
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.1/secret")
            self.end_headers()
        elif self.path == "/redirect-loopback-307":
            self.send_response(307)
            self.send_header("Location", "//127.0.0.1/secret")
            self.end_headers()
        elif self.path == "/redirect-loopback-308":
            self.send_response(308)
            self.send_header("Location", "http://[::1]/secret")
            self.end_headers()
        elif self.path == "/broken":
            self.send_response(404)
            self.end_headers()
        elif self.path == "/server-error":
            self.send_response(500)
            self.end_headers()
        elif self.path == "/blocked":
            self.send_response(403)
            self.end_headers()
        elif self.path == "/ratelimit":
            self.send_response(429)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, *_args: object) -> None:
        pass


@pytest.fixture(scope="module")
def server() -> tuple[str, int]:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}", httpd.server_port
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_probe_ok_redirect_and_head_fallback(server: tuple[str, int]) -> None:
    base, _ = server
    assert probe(f"{base}/ok", 2, allow_local=True)[0] == "ok"
    assert probe(f"{base}/redirect", 2, allow_local=True)[0] == "ok"
    assert probe(f"{base}/head405", 2, allow_local=True)[0] == "ok"
    assert probe(f"{base}/head501", 2, allow_local=True)[0] == "ok"


def test_probe_redirect_does_not_hang_reading_trickle_body(server: tuple[str, int]) -> None:
    base, _ = server
    with Handler.in_flight_lock:
        Handler.trickle_get_hits = 0
    t0 = time.monotonic()
    state, status, detail = probe(f"{base}/redirect-trickle", 1.5, allow_local=True)
    elapsed = time.monotonic() - t0
    assert (state, status) == ("ok", 200)
    assert detail.startswith("GET "), detail
    assert Handler.trickle_get_hits == 1
    assert elapsed < 0.3


def test_probe_broken_server_error_bad_status_and_blocked(server: tuple[str, int]) -> None:
    base, _ = server
    state, status, _ = probe(f"{base}/broken", 2, allow_local=True)
    assert (state, status) == ("failed", 404)

    state, status, _ = probe(f"{base}/server-error", 2, allow_local=True)
    assert (state, status) == ("failed", 500)

    state, status, _ = probe(f"{base}/bad-status", 2, allow_local=True)
    assert state == "failed"
    assert status is None

    state, status, _ = probe(f"{base}/blocked", 2, allow_local=True)
    assert (state, status) == ("unverified", 403)

    state, status, _ = probe(f"{base}/ratelimit", 2, allow_local=True)
    assert (state, status) == ("unverified", 429)


@pytest.mark.parametrize(
    "blocked_url",
    [
        "http://127.0.0.1/secret",
        "http://[::1]/secret",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::ffff:127.0.0.1]/secret",
        "http://10.0.0.1/internal",
        "http://224.0.0.1/multicast",
        "http://[fec0::1]/site-local",
        "http://user:pass@93.184.216.34/auth",
        "http://93.184.216.34:0/port-zero",
        "http://[::1/malformed",
        "ftp://example.com/file.txt",
        "file:///etc/passwd",
    ],
)
def test_probe_blocks_non_global_ips_malformed_and_non_http_schemes(blocked_url: str) -> None:
    state, status, detail = probe(blocked_url, 2)
    assert state == "failed"
    assert status is None
    assert "blocked" in detail


def test_probe_blocks_loopback_server_without_allow_local(server: tuple[str, int]) -> None:
    base, _ = server
    state, status, detail = probe(f"{base}/ok", 2)
    assert state == "failed"
    assert status is None
    assert "blocked" in detail


def test_probe_blocks_redirect_to_ftp_and_file_even_with_allow_local(
    server: tuple[str, int],
) -> None:
    base, _ = server
    for path in ("/redirect-ftp", "/redirect-file"):
        state, status, detail = probe(f"{base}{path}", 2, allow_local=True)
        assert state == "failed"
        assert status is None
        assert "blocked" in detail


@pytest.mark.parametrize(
    "redirect_path",
    [
        "/redirect-loopback-302",
        "/redirect-loopback-307",
        "/redirect-loopback-308",
    ],
)
def test_probe_end_to_end_blocks_redirects_to_loopback_without_allow_local(
    server: tuple[str, int],
    redirect_path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise _SafeRedirectHandler end-to-end against real 302/307/308 redirects to loopback."""
    _, port = server
    real_getaddrinfo = socket.getaddrinfo
    real_connect = socket.socket.connect
    synthetic_public_ip = "93.184.216.34"

    # Resolve synthetic host "public-origin.example" to a real global IP so real _is_global_ip
    # stays unmocked, and reroute ONLY that synthetic (ip, port) connect to the local server.
    def fake_getaddrinfo(host: str, p: int, *args: object, **kwargs: object) -> list:
        if host == "public-origin.example":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (synthetic_public_ip, p))]
        return real_getaddrinfo(host, p, *args, **kwargs)

    origin_connected = {"count": 0}

    def routed_connect(self: socket.socket, address: object) -> None:
        if address == (synthetic_public_ip, port):
            origin_connected["count"] += 1
            return real_connect(self, ("127.0.0.1", port))
        return real_connect(self, address)

    monkeypatch.setattr(cel.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(socket.socket, "connect", routed_connect)

    state, status, detail = probe(f"http://public-origin.example:{port}{redirect_path}", 2)
    assert origin_connected["count"] == 1, "initial request never connected to the local server"
    assert state == "failed"
    assert status is None
    assert "blocked" in detail


def test_probe_blocks_two_step_dns_rebinding_at_connect_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulate DNS rebinding: public IP on pre-check, loopback on connect-time getaddrinfo."""
    lookups = {"count": 0}

    def rebinding_getaddrinfo(host: str, port: int, *_args: object, **_kwargs: object) -> list:
        lookups["count"] += 1
        if lookups["count"] == 1:
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))]

    monkeypatch.setattr(cel.socket, "getaddrinfo", rebinding_getaddrinfo)
    state, status, detail = probe("http://rebind.example/test", 2, allow_local=False)
    assert lookups["count"] == 2
    assert state == "failed"
    assert status is None
    assert "blocked" in detail


def test_markdown_extraction_skips_code_keeps_balanced_parens_and_prunes_dirs(
    tmp_path: Path,
) -> None:
    ignored = tmp_path / "node_modules" / "pkg"
    ignored.mkdir(parents=True)
    (ignored / "README.md").write_text("https://ignored.example/node-modules\n", encoding="utf-8")
    venv = tmp_path / ".venv" / "docs"
    venv.mkdir(parents=True)
    (venv / "guide.md").write_text("https://ignored.example/venv\n", encoding="utf-8")

    (tmp_path / "doc.md").write_text(
        "\n".join(
            [
                "Real link: [Wiki](https://en.wikipedia.org/wiki/Foo_(bar)).",
                "Inline code: `https://inline.example/ignored` and ``https://double.example/ignored``.",
                "```bash",
                "curl https://fenced.example/ignored",
                "```",
                "> ```text",
                "> https://quoted-fence.example/ignored",
                "> ```",
                "~~~text",
                "https://tilde.example/ignored",
                "~~~",
                "Badge: [![CI](https://img.example/b.svg)](https://target.example/ci)",
                "Emphasis: *https://emph.example/path* and invalid http://[::1/",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert [p.name for p in markdown_files(tmp_path)] == ["doc.md"]
    locs = external_url_locations(tmp_path)
    assert external_urls(tmp_path) == [
        "https://emph.example/path",
        "https://en.wikipedia.org/wiki/Foo_(bar)",
        "https://img.example/b.svg",
        "https://target.example/ci",
    ]
    assert locs["https://en.wikipedia.org/wiki/Foo_(bar)"] == [("doc.md", 1)]
    assert locs["https://img.example/b.svg"] == [("doc.md", 12)]
    assert locs["https://target.example/ci"] == [("doc.md", 12)]
    assert locs["https://emph.example/path"] == [("doc.md", 13)]


def test_cli_reports_file_line_and_handles_balanced_parens(
    tmp_path: Path, server: tuple[str, int], capsys: pytest.CaptureFixture[str]
) -> None:
    base, _ = server
    (tmp_path / "page.md").write_text(
        f"Line 1 ok: [wiki]({base}/wiki/Foo_(bar))\n"
        f"Line 2 fail: [broken]({base}/broken)\n"
        f"Line 3 skip: [rate]({base}/ratelimit)\n",
        encoding="utf-8",
    )
    rc = main(["--root", str(tmp_path), "--timeout", "2", "--allow-local"])
    captured = capsys.readouterr()
    assert rc == 1
    assert f"FAIL {base}/broken" in captured.err
    assert "[page.md:2]" in captured.err
    assert f"SKIP {base}/ratelimit" in captured.err
    assert "[page.md:3]" in captured.err


def test_cli_passes_when_only_ok_and_blocked(tmp_path: Path, server: tuple[str, int]) -> None:
    base, _ = server
    (tmp_path / "page.md").write_text(
        f"[ok]({base}/ok)\n[blocked]({base}/blocked)\n[rate]({base}/ratelimit)\n",
        encoding="utf-8",
    )
    assert main(["--root", str(tmp_path), "--timeout", "2", "--allow-local"]) == 0


def test_cli_fails_on_missing_root_and_blocks_loopback_without_allow_local(
    tmp_path: Path, server: tuple[str, int], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--root", str(tmp_path / "does-not-exist")]) == 2

    base, _ = server
    (tmp_path / "page.md").write_text(f"[local]({base}/ok)\n", encoding="utf-8")
    rc = main(["--root", str(tmp_path), "--timeout", "2"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "blocked" in captured.err
    assert "[page.md:1]" in captured.err


def test_per_host_concurrency_cap_and_total_timeout(
    tmp_path: Path, server: tuple[str, int]
) -> None:
    base, _ = server
    with Handler.in_flight_lock:
        Handler.in_flight = 0
        Handler.peak_in_flight = 0

    lines = [f"[p{i}]({base}/paced/{i})" for i in range(6)]
    (tmp_path / "paced.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    rc = main(
        [
            "--root",
            str(tmp_path),
            "--timeout",
            "5",
            "--workers",
            "6",
            "--max-per-host",
            "2",
            "--allow-local",
        ]
    )
    assert rc == 0
    assert 1 <= Handler.peak_in_flight <= 2

    t0 = time.monotonic()
    state, status, _ = probe(f"{base}/slow-head", 0.15, allow_local=True)
    elapsed = time.monotonic() - t0
    assert state == "failed"
    assert status is None
    assert elapsed < 0.6


def test_aud47_max_redirects_head_error_fallback_template_urls_and_cli_args(
    tmp_path: Path, server: tuple[str, int], capsys: pytest.CaptureFixture[str]
) -> None:
    base, _ = server

    # Exceeding MAX_REDIRECTS fails closed instead of looping forever.
    state, status, _ = probe(f"{base}/redirect-loop", 2, allow_local=True)
    assert (state, status) == ("failed", 302)

    # Transport/protocol failure on HEAD falls back to GET while time remains.
    state, status, detail = probe(f"{base}/head-error-get-ok", 2, allow_local=True)
    assert (state, status, detail) == ("ok", 200, "GET 200")

    # Template URLs with $, {, or } placeholders are ignored; empty root exits 0 cleanly.
    (tmp_path / "templates.md").write_text(
        "https://example.com/${VAR}\nhttps://example.com/{id}/docs\nhttps://example.com/$slug\n",
        encoding="utf-8",
    )
    assert external_urls(tmp_path) == []
    assert main(["--root", str(tmp_path)]) == 0
    assert "No external links found." in capsys.readouterr().out

    # Invalid positive-int / positive-float CLI arguments fail argparse with exit 2.
    for bad_args in (
        ["--workers", "0"],
        ["--max-per-host", "0"],
        ["--timeout", "0"],
        ["--timeout", "nan"],
    ):
        with pytest.raises(SystemExit) as exc:
            main(bad_args)
        assert exc.value.code == 2


def test_aud49_shared_markdown_masking_and_private_dir_pruning(tmp_path: Path) -> None:
    for private_dir in (
        "venv",
        ".mypy_cache",
        "secrets",
        ".gemini",
        ".opencode",
        ".claude",
        ".agents",
    ):
        d = tmp_path / private_dir
        d.mkdir(parents=True)
        (d / "private.md").write_text(f"https://ignored.example/{private_dir}\n", encoding="utf-8")

    (tmp_path / "edge.md").write_text(
        "\n".join(
            [
                "---",
                "note: https://frontmatter.example/ignored",
                "---",
                "    ```python",
                "https://after-four-space-fence.example/ok",
                "> ```text",
                "> > ```",
                "> https://inside-blockquote-fence.example/ignored",
                "",
                "https://after-blockquote-exit.example/ok",
                r"Escaped \` https://after-escaped-tick.example/ok \`",
                r"Escaped pair \``https://in-code-after-esc.example/ignored` https://after-esc-pair.example/ok `bar`",
                "`https://multiline-code-1.example/ignored",
                "https://multiline-code-2.example/ignored`",
                "`unclosed-before-ws-blank",
                "   ",
                "https://after-ws-blank-line.example/ok `closed`",
                "<!--",
                "https://inside-html-comment.example/ignored",
                "-->",
                "https://final-line.example/ok",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "extra.markdown").write_text(
        "https://from-markdown-ext.example/ok\n", encoding="utf-8"
    )

    assert [p.name for p in markdown_files(tmp_path)] == ["edge.md", "extra.markdown"]
    locs = external_url_locations(tmp_path)
    assert external_urls(tmp_path) == [
        "https://after-blockquote-exit.example/ok",
        "https://after-esc-pair.example/ok",
        "https://after-escaped-tick.example/ok",
        "https://after-four-space-fence.example/ok",
        "https://after-ws-blank-line.example/ok",
        "https://final-line.example/ok",
        "https://from-markdown-ext.example/ok",
    ]
    assert locs["https://after-four-space-fence.example/ok"] == [("edge.md", 5)]
    assert locs["https://after-blockquote-exit.example/ok"] == [("edge.md", 10)]
    assert locs["https://after-escaped-tick.example/ok"] == [("edge.md", 11)]
    assert locs["https://after-esc-pair.example/ok"] == [("edge.md", 12)]
    assert locs["https://after-ws-blank-line.example/ok"] == [("edge.md", 17)]
    assert locs["https://final-line.example/ok"] == [("edge.md", 21)]
    assert locs["https://from-markdown-ext.example/ok"] == [("extra.markdown", 1)]
