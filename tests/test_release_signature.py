"""Verify the public release-signing trust material."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SIGNERS = ROOT / "docs" / "release-signing" / "allowed_signers"
SIGNERS_README = ROOT / "docs" / "release-signing" / "README.md"
RELEASE_PROCESS = ROOT / "docs" / "release-process.md"
TAG = "v1.1.0"


def run_git(*args: str, signers: Path = SIGNERS) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            "gpg.format=ssh",
            "-c",
            f"gpg.ssh.allowedSignersFile={signers}",
            *args,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def tag_available() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{TAG}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    return result.returncode == 0


def test_allowed_signers_is_public_and_well_formed() -> None:
    text = SIGNERS.read_text(encoding="utf-8")
    assert "PRIVATE KEY" not in text
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    assert len(lines) == 1
    principal, key_type, key, *_ = lines[0].split()
    assert principal == "release@snaplyze.me"
    assert key_type == "ssh-ed25519"
    assert len(key) >= 60
    assert "docs/release-signing/allowed_signers" in (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "release-signing/allowed_signers" in RELEASE_PROCESS.read_text(encoding="utf-8")
    assert "Rotation" in SIGNERS_README.read_text(encoding="utf-8")


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_current_release_tag_verifies_with_repo_trust() -> None:
    if not tag_available():
        pytest.skip(f"{TAG} is not present in this checkout")
    result = run_git("verify-tag", TAG)
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_tampered_trust_fails(tmp_path: Path) -> None:
    if not tag_available():
        pytest.skip(f"{TAG} is not present in this checkout")
    text = SIGNERS.read_text(encoding="utf-8").strip()
    principal, key_type, key, *_ = text.split()
    tampered_key = key[:-1] + ("A" if key[-1] != "A" else "B")
    tampered = tmp_path / "allowed_signers"
    tampered.write_text(f"{principal} {key_type} {tampered_key}\n", encoding="utf-8")
    result = run_git("verify-tag", TAG, signers=tampered)
    assert result.returncode != 0
