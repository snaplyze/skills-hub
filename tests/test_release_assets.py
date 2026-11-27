"""Verify the release archive/checksum/install path without publishing a release."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_DIR = ROOT / "install"


def _isolated_git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def git(repo: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def is_git_worktree(path: Path) -> bool:
    """Return True only when path itself is the root of a git worktree (never a parent repo)."""
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return Path(result.stdout.strip()).resolve() == path.resolve()


def test_release_archive_checksum_and_copy_install(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(INSTALL_DIR, repo / "install")
    skill = repo / "skills" / "frontend-design"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: frontend-design\ndescription: Archive install fixture.\n"
        "license: MIT\n---\n\n# Fixture\n",
        encoding="utf-8",
    )
    (skill / "asset.txt").write_text("archive payload\n", encoding="utf-8")

    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(
        repo,
        "-c",
        "user.name=Release Test",
        "-c",
        "user.email=release@example.test",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-qm",
        "fixture",
    )
    git(
        repo,
        "-c",
        "user.name=Release Test",
        "-c",
        "user.email=release@example.test",
        "-c",
        "tag.gpgsign=false",
        "tag",
        "-a",
        "v1.2.3",
        "-m",
        "v1.2.3",
    )

    archive = tmp_path / "skills-hub-v1.2.3.tar.gz"
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "archive",
            "--format=tar.gz",
            "--prefix=skills-hub-v1.2.3/",
            "-o",
            str(archive),
            "HEAD",
        ],
        env=_isolated_git_env(),
        check=True,
    )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = tmp_path / "SHA256SUMS"
    sums.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    checked = subprocess.run(
        ["sha256sum", "--check", sums.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr

    tampered = tmp_path / "tampered.tar.gz"
    tampered.write_bytes(archive.read_bytes() + b"tamper")
    sums.write_text(f"{digest}  {tampered.name}\n", encoding="utf-8")
    rejected = subprocess.run(
        ["sha256sum", "--check", sums.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode != 0

    extracted = tmp_path / "extracted"
    with tarfile.open(archive) as bundle:
        bundle.extractall(extracted, filter="data")
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)
    env.pop("XDG_CONFIG_HOME", None)
    for installer_name in ("antigravity.sh", "opencode.sh"):
        target = tmp_path / f"target-{installer_name}"
        result = subprocess.run(
            [
                str(extracted / "skills-hub-v1.2.3" / "install" / installer_name),
                "--copy",
                "--target",
                str(target),
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (installer_name, result.stderr)
        assert (target / "frontend-design" / "asset.txt").read_text() == "archive payload\n"


def test_current_tree_archive_contains_all_skills(tmp_path: Path) -> None:
    """Verify release archiving packages every skill in both git checkouts and extracted snapshots."""
    archive = tmp_path / "current.tar.gz"
    if is_git_worktree(ROOT):
        source_repo = ROOT
    else:
        source_repo = tmp_path / "snapshot-repo"
        source_repo.mkdir()
        shutil.copytree(ROOT / "skills", source_repo / "skills")
        shutil.copytree(ROOT / "install", source_repo / "install")
        gitattributes = ROOT / ".gitattributes"
        if gitattributes.is_file():
            shutil.copy2(gitattributes, source_repo / ".gitattributes")
        git(source_repo, "init", "-q")
        git(source_repo, "add", "-A")
        git(
            source_repo,
            "-c",
            "user.name=Release Test",
            "-c",
            "user.email=release@example.test",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "snapshot",
        )

    result = subprocess.run(
        [
            "git",
            "-C",
            str(source_repo),
            "archive",
            "--format=tar.gz",
            "--prefix=skills-hub-test/",
            "-o",
            str(archive),
            "HEAD",
        ],
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    expected = {
        f"skills/{path.parent.name}/SKILL.md" for path in (ROOT / "skills").glob("*/SKILL.md")
    } | {
        "install/antigravity.sh",
        "install/opencode.sh",
        "install/lib.sh",
    }
    assert expected
    with tarfile.open(archive) as bundle:
        names = set(bundle.getnames())
    missing = {relative for relative in expected if f"skills-hub-test/{relative}" not in names}
    assert not missing, missing
