"""Tests for the optional external-link audit."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from scripts.check_external_links import main, probe


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self) -> None:  # noqa: N802 - http.server API
        if self.path == "/head405":
            self.send_response(405)
            self.end_headers()
            return
        self._respond()

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        self._respond()

    def _respond(self) -> None:
        if self.path == "/ok":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        elif self.path == "/broken":
            self.send_response(404)
            self.end_headers()
        elif self.path == "/blocked":
            self.send_response(403)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, *_args: object) -> None:
        pass


@pytest.fixture()
def server() -> str:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        thread.join(timeout=2)


def test_probe_ok_redirect_and_head_fallback(server: str) -> None:
    assert probe(f"{server}/ok", 2)[0] == "ok"
    assert probe(f"{server}/redirect", 2)[0] == "ok"
    assert probe(f"{server}/head405", 2)[0] == "ok"


def test_probe_broken_and_blocked(server: str) -> None:
    state, status, _ = probe(f"{server}/broken", 2)
    assert (state, status) == ("failed", 404)
    state, status, _ = probe(f"{server}/blocked", 2)
    assert (state, status) == ("unverified", 403)


def test_cli_fails_on_broken_link(tmp_path: Path, server: str) -> None:
    (tmp_path / "page.md").write_text(
        f"[ok]({server}/ok)\n[broken]({server}/broken)\n", encoding="utf-8"
    )
    assert main(["--root", str(tmp_path), "--timeout", "2"]) == 1


def test_cli_passes_when_only_ok_and_blocked(tmp_path: Path, server: str) -> None:
    (tmp_path / "page.md").write_text(
        f"[ok]({server}/ok)\n[blocked]({server}/blocked)\n", encoding="utf-8"
    )
    assert main(["--root", str(tmp_path), "--timeout", "2"]) == 0
