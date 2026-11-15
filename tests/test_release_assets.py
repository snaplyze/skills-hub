"""Verify the release archive/checksum/install path without publishing a release."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install" / "opencode.sh"


def git(repo: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_release_archive_checksum_and_copy_install(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "install").mkdir(parents=True)
    skill = repo / "skills" / "frontend-design"
    skill.mkdir(parents=True)
    shutil.copy2(INSTALLER, repo / "install" / "opencode.sh")
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
        check=True,
    )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (tmp_path / "SHA256SUMS").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest

    extracted = tmp_path / "extracted"
    with tarfile.open(archive) as bundle:
        bundle.extractall(extracted, filter="data")
    home = tmp_path / "home"
    home.mkdir()
    target = tmp_path / "target"
    env = os.environ.copy()
    env["HOME"] = str(home)
    env.pop("XDG_CONFIG_HOME", None)
    result = subprocess.run(
        [
            str(extracted / "skills-hub-v1.2.3" / "install" / "opencode.sh"),
            "--copy",
            "--target",
            str(target),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (target / "frontend-design" / "asset.txt").read_text() == "archive payload\n"
