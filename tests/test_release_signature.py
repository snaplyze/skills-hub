"""Verify release-signing trust material and SSH tag verification without .git dependence."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SIGNERS = ROOT / "docs" / "release-signing" / "allowed_signers"
SIGNERS_README = ROOT / "docs" / "release-signing" / "README.md"
RELEASE_PROCESS = ROOT / "docs" / "release-process.md"

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


@dataclass(frozen=True)
class SignedTagFixture:
    repo: Path
    good_signers: Path
    tampered_signers: Path
    signed_tag: str
    unsigned_tag: str


def _isolated_git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["LC_ALL"] = "C"
    return env


def run_git_verify(repo: Path, tag: str, *, signers: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "gpg.format=ssh",
            "-c",
            f"gpg.ssh.allowedSignersFile={signers}",
            "verify-tag",
            "--",
            f"refs/tags/{tag}",
        ],
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def repo_release_tag() -> str | None:
    if not (ROOT / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(ROOT), "tag", "--list", "v*", "--sort=-v:refname"],
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if result.returncode != 0:
        return None
    tags = [tag for tag in result.stdout.splitlines() if tag]
    return tags[0] if tags else None


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


@pytest.fixture(scope="module")
def signed_tag_fixture(tmp_path_factory: pytest.TempPathFactory) -> SignedTagFixture:
    """Create a deterministic temp git repo with an SSH-signed tag and tampered trust."""
    if shutil.which("git") is None or shutil.which("ssh-keygen") is None:
        pytest.fail("git and ssh-keygen are required for SSH tag signature verification tests")

    base = tmp_path_factory.mktemp("signed-tag-fixture")
    repo = base / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Fixture\n", encoding="utf-8")

    good_key = base / "good_key"
    wrong_key = base / "wrong_key"
    for key_path in (good_key, wrong_key):
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key_path)],
            check=True,
            timeout=10,
        )

    good_pub = Path(f"{good_key}.pub").read_text(encoding="utf-8").split()[1]
    wrong_pub = Path(f"{wrong_key}.pub").read_text(encoding="utf-8").split()[1]

    good_signers = base / "allowed_signers"
    good_signers.write_text(f"release@snaplyze.me ssh-ed25519 {good_pub}\n", encoding="utf-8")
    tampered_signers = base / "tampered_signers"
    tampered_signers.write_text(f"release@snaplyze.me ssh-ed25519 {wrong_pub}\n", encoding="utf-8")

    env = _isolated_git_env()
    git_identity = [
        "-c",
        "user.name=Release Test",
        "-c",
        "user.email=release@snaplyze.me",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "tag.gpgsign=false",
    ]
    subprocess.run(["git", "-C", str(repo), "init", "-q"], env=env, check=True, timeout=10)
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], env=env, check=True, timeout=10)
    subprocess.run(
        ["git", "-C", str(repo), *git_identity, "commit", "-qm", "initial"],
        env=env,
        check=True,
        timeout=10,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            *git_identity,
            "-c",
            "gpg.format=ssh",
            "-c",
            f"user.signingkey={good_key}",
            "tag",
            "-s",
            "v1.2.3",
            "-m",
            "Signed fixture release v1.2.3",
        ],
        env=env,
        check=True,
        timeout=10,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            *git_identity,
            "tag",
            "-a",
            "v1.2.4",
            "-m",
            "Unsigned annotated tag v1.2.4",
        ],
        env=env,
        check=True,
        timeout=10,
    )
    return SignedTagFixture(
        repo=repo,
        good_signers=good_signers,
        tampered_signers=tampered_signers,
        signed_tag="v1.2.3",
        unsigned_tag="v1.2.4",
    )


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


def test_signed_tag_verifies_with_matching_trust(signed_tag_fixture: SignedTagFixture) -> None:
    result = run_git_verify(
        signed_tag_fixture.repo,
        signed_tag_fixture.signed_tag,
        signers=signed_tag_fixture.good_signers,
    )
    assert result.returncode == 0, result.stderr
    assert 'Good "git" signature for release@snaplyze.me' in (result.stdout + result.stderr)

    # Also verify the real repository release tag whenever tags are present in a git checkout.
    tag = repo_release_tag()
    if tag is not None:
        real = run_git_verify(ROOT, tag, signers=SIGNERS)
        assert real.returncode == 0, real.stderr
        assert 'Good "git" signature for release@snaplyze.me' in (real.stdout + real.stderr)


def test_tampered_trust_and_unsigned_tag_fail(signed_tag_fixture: SignedTagFixture) -> None:
    tampered = run_git_verify(
        signed_tag_fixture.repo,
        signed_tag_fixture.signed_tag,
        signers=signed_tag_fixture.tampered_signers,
    )
    assert tampered.returncode != 0
    tampered_out = tampered.stdout + tampered.stderr
    assert 'Good "git" signature for ' not in tampered_out
    assert "No principal matched" in tampered_out

    unsigned = run_git_verify(
        signed_tag_fixture.repo,
        signed_tag_fixture.unsigned_tag,
        signers=signed_tag_fixture.good_signers,
    )
    assert unsigned.returncode != 0
    assert "Good" not in (unsigned.stdout + unsigned.stderr)

    tag = repo_release_tag()
    if tag is not None:
        real_tampered = run_git_verify(ROOT, tag, signers=signed_tag_fixture.tampered_signers)
        assert real_tampered.returncode != 0
        real_out = real_tampered.stdout + real_tampered.stderr
        assert 'Good "git" signature for ' not in real_out
        assert "No principal matched" in real_out


def test_tag_object_replay_and_direct_commit_binding(
    signed_tag_fixture: SignedTagFixture,
) -> None:
    env = _isolated_git_env()
    repo = signed_tag_fixture.repo

    # Verify the legitimate signed tag binds its embedded tag header and targets a commit.
    embedded = subprocess.run(
        ["git", "-C", str(repo), "for-each-ref", "--format=%(tag)", "refs/tags/v1.2.3"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.strip()
    assert embedded == "v1.2.3"

    raw_tag = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "tag", "refs/tags/v1.2.3"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout
    header_lines = raw_tag.split("\n\n", 1)[0].splitlines()
    target_type = next(line.split(None, 1)[1] for line in header_lines if line.startswith("type "))
    assert target_type == "commit"

    # A nested tag targeting another tag object peels to a commit via ^{commit}
    # but has header type == "tag", proving why release.yml checks target_type == "commit".
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Release Test",
            "-c",
            "user.email=release@snaplyze.me",
            "-c",
            "tag.gpgsign=false",
            "tag",
            "-a",
            "v1.2.5",
            "refs/tags/v1.2.3",
            "-m",
            "Nested tag targeting v1.2.3",
        ],
        env=env,
        check=True,
        timeout=10,
    )
    try:
        nested_raw = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "tag", "refs/tags/v1.2.5"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout
        nested_headers = nested_raw.split("\n\n", 1)[0].splitlines()
        nested_type = next(
            line.split(None, 1)[1] for line in nested_headers if line.startswith("type ")
        )
        assert nested_type == "tag"
    finally:
        subprocess.run(
            ["git", "-C", str(repo), "update-ref", "-d", "refs/tags/v1.2.5"],
            env=env,
            check=False,
            timeout=10,
        )

    # Replaying the signed tag OID under a different ref passes raw git verify-tag,
    # proving why release.yml must check %(tag) == $TAG.
    tag_oid = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "refs/tags/v1.2.3"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(repo), "update-ref", "refs/tags/v1.9.9", tag_oid],
        env=env,
        check=True,
        timeout=10,
    )
    try:
        replayed_verify = run_git_verify(repo, "v1.9.9", signers=signed_tag_fixture.good_signers)
        assert replayed_verify.returncode == 0
        replayed_embedded = subprocess.run(
            ["git", "-C", str(repo), "for-each-ref", "--format=%(tag)", "refs/tags/v1.9.9"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()
        assert replayed_embedded == "v1.2.3"
        assert replayed_embedded != "v1.9.9"
    finally:
        subprocess.run(
            ["git", "-C", str(repo), "update-ref", "-d", "refs/tags/v1.9.9"],
            env=env,
            check=False,
            timeout=10,
        )
