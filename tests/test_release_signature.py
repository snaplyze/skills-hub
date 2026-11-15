"""Verify the public release-signing trust material."""

from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SIGNERS = ROOT / "docs" / "release-signing" / "allowed_signers"
SIGNERS_README = ROOT / "docs" / "release-signing" / "README.md"
RELEASE_PROCESS = ROOT / "docs" / "release-process.md"



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


def release_tag() -> str | None:
    result = subprocess.run(
        ["git", "tag", "--list", "v*", "--sort=-v:refname"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    tags = [tag for tag in result.stdout.splitlines() if tag]
    return tags[0] if tags else None


KEY_TYPES = frozenset(
    {
        "ssh-ed25519",
        "ssh-rsa",
        "ecdsa-sha2-nistp256",
        "ecdsa-sha2-nistp384",
        "ecdsa-sha2-nistp521",
        "sk-ssh-ed25519@openssh.com",
        "sk-ecdsa-sha2-nistp256@openssh.com",
    }
)


def parse_signer_line(line: str) -> tuple[list[str], str, str]:
    fields = shlex.split(line, comments=True)
    try:
        key_index = next(index for index, field in enumerate(fields) if field in KEY_TYPES)
    except StopIteration:
        raise AssertionError(f"allowed_signers line has no key type: {line!r}") from None
    principals = fields[:key_index]
    assert principals, f"allowed_signers line has no principal: {line!r}"
    key = fields[key_index + 1] if key_index + 1 < len(fields) else ""
    assert key, f"allowed_signers line has no key: {line!r}"
    return principals, fields[key_index], key


def test_allowed_signers_is_public_and_well_formed() -> None:
    text = SIGNERS.read_text(encoding="utf-8")
    assert "PRIVATE KEY" not in text
    lines = [
        line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]
    assert lines
    for line in lines:
        principals, key_type, key = parse_signer_line(line)
        assert any("release@snaplyze.me" in principal.split(",") for principal in principals)
        assert key_type in KEY_TYPES
        assert len(key) >= 60
    assert "docs/release-signing/allowed_signers" in (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "release-signing/allowed_signers" in RELEASE_PROCESS.read_text(encoding="utf-8")
    assert "Rotation" in SIGNERS_README.read_text(encoding="utf-8")


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_current_release_tag_verifies_with_repo_trust() -> None:
    tag = release_tag()
    if tag is None:
        pytest.skip("no release tag is present in this checkout")
    result = run_git("verify-tag", tag)
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(
    shutil.which("git") is None or shutil.which("ssh-keygen") is None,
    reason="git and ssh-keygen are required",
)
def test_tampered_trust_fails(tmp_path: Path) -> None:
    tag = release_tag()
    if tag is None:
        pytest.skip("no release tag is present in this checkout")
    key_path = tmp_path / "wrong_key"
    subprocess.run(
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key_path)],
        check=True,
        timeout=10,
    )
    public_key = Path(f"{key_path}.pub").read_text(encoding="utf-8").split()[1]
    tampered = tmp_path / "allowed_signers"
    tampered.write_text(
        f"release@snaplyze.me ssh-ed25519 {public_key}\n",
        encoding="utf-8",
    )
    result = run_git("verify-tag", tag, signers=tampered)
    assert result.returncode != 0
    assert "Good" not in result.stdout
