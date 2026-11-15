"""Installer behavior tests using isolated HOME and target directories only."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install" / "opencode.sh"

FRONTEND_SKILL = """---
name: frontend-design
description: >
  Distinctive, accessible web interface design
  and frontend quality.
license: MIT
---

# Frontend Design

Use this skill for frontend design work.
"""

OTHER_SKILL = """---
name: other-skill
description: A second skill used by the installer tests.
license: MIT
---

# Other skill
"""


def write_skill(repo: Path, skill_id: str, frontmatter: str = FRONTEND_SKILL) -> Path:
    skill_dir = repo / "skills" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(frontmatter, encoding="utf-8")
    (skill_dir / "assets").mkdir(exist_ok=True)
    (skill_dir / "assets" / "keep.txt").write_text(f"content for {skill_id}\n", encoding="utf-8")
    return skill_dir


def make_workspace(tmp_path: Path) -> SimpleNamespace:
    repo = tmp_path / "repo"
    (repo / "install").mkdir(parents=True)
    shutil.copy2(INSTALLER, repo / "install" / "opencode.sh")
    write_skill(repo, "frontend-design")
    write_skill(repo, "other-skill", OTHER_SKILL)
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)
    env.pop("XDG_CONFIG_HOME", None)
    return SimpleNamespace(
        tmp_path=tmp_path,
        repo=repo,
        home=home,
        target=tmp_path / "target",
        env=env,
        installer=repo / "install" / "opencode.sh",
    )


@pytest.fixture
def workspace(tmp_path: Path) -> SimpleNamespace:
    return make_workspace(tmp_path)


def run_installer(
    workspace: SimpleNamespace,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(workspace.installer), *args],
        cwd=workspace.repo,
        env=env or workspace.env,
        capture_output=True,
        text=True,
        check=False,
    )


def run_git(workspace: SimpleNamespace, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(workspace.repo), *args],
        cwd=workspace.repo,
        env=workspace.env,
        capture_output=True,
        text=True,
        check=False,
    )


def tree_snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*")):
        rel = str(path.relative_to(root))
        if path.is_symlink():
            snapshot[rel] = ("link", os.readlink(path))
        elif path.is_dir():
            snapshot[rel] = ("dir", "")
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            snapshot[rel] = ("file", digest)
    return snapshot


def make_git_checkout(workspace: SimpleNamespace, tag: str = "v1.2.3") -> None:
    assert run_git(workspace, "init", "-q").returncode == 0
    assert run_git(workspace, "add", "-A").returncode == 0
    commit = run_git(
        workspace,
        "-c",
        "user.name=Installer Test",
        "-c",
        "user.email=installer@example.test",
        "commit",
        "-qm",
        "initial",
    )
    assert commit.returncode == 0, commit.stderr
    tagged = run_git(
        workspace,
        "-c",
        "user.name=Installer Test",
        "-c",
        "user.email=installer@example.test",
        "tag",
        "-a",
        tag,
        "-m",
        tag,
    )
    assert tagged.returncode == 0, tagged.stderr


def test_refuses_unsafe_target_matrix(workspace: SimpleNamespace, tmp_path: Path) -> None:
    symlink_target = tmp_path / "target-symlink"
    symlink_target.symlink_to(workspace.repo / "skills")
    parent_link = tmp_path / "parent-link"
    parent_link.symlink_to(workspace.repo)

    before = tree_snapshot(workspace.repo)
    targets = [
        "",
        "/",
        str(workspace.home),
        "~",
        str(workspace.repo),
        str(workspace.repo / "skills"),
        str(workspace.repo / "skills" / "frontend-design"),
        str(workspace.repo / "skills" / "frontend-design" / "nested"),
        str(tmp_path),
        str(tmp_path / "bad\nname"),
        str(symlink_target),
        str(symlink_target) + "/",
        str(parent_link / "skills"),
    ]

    for target in targets:
        result = run_installer(workspace, "--target", target)
        assert result.returncode != 0, f"target unexpectedly accepted: {target!r}"
        assert "error:" in result.stderr, f"no explanation for target: {target!r}"

    assert tree_snapshot(workspace.repo) == before
    assert not workspace.target.exists()


def test_refuses_symlinked_source_root(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "install").mkdir(parents=True)
    shutil.copy2(INSTALLER, repo / "install" / "opencode.sh")
    real_skills = repo / "real-skills"
    real_skills.mkdir()
    skill_dir = real_skills / "frontend-design"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(FRONTEND_SKILL, encoding="utf-8")
    (repo / "skills").symlink_to(real_skills)

    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    (tmp_path / "home").mkdir()
    env.pop("XDG_CONFIG_HOME", None)

    result = subprocess.run(
        [str(repo / "install" / "opencode.sh"), "--target", str(tmp_path / "target")],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "symlinked source root" in result.stderr
    assert not (tmp_path / "target").exists()


def test_refuses_symlinked_skill_source(workspace: SimpleNamespace, tmp_path: Path) -> None:
    real_skill = tmp_path / "real-skill"
    real_skill.mkdir()
    (real_skill / "SKILL.md").write_text(FRONTEND_SKILL, encoding="utf-8")
    (workspace.repo / "skills" / "frontend-design").rename(tmp_path / "moved-skill")
    (workspace.repo / "skills" / "frontend-design").symlink_to(real_skill)

    result = run_installer(workspace, "--target", str(workspace.target), "frontend-design")

    assert result.returncode != 0
    assert "symlinked skill source" in result.stderr
    assert not workspace.target.exists()

    all_result = run_installer(workspace, "--all", "--target", str(workspace.target))
    assert all_result.returncode != 0
    assert "symlinked skill source" in all_result.stderr
    assert not workspace.target.exists()


def test_default_copy_install_and_source_unchanged(
    workspace: SimpleNamespace,
) -> None:
    before = tree_snapshot(workspace.repo)

    result = run_installer(workspace, "--target", str(workspace.target))

    assert result.returncode == 0, result.stderr
    target_skill = workspace.target / "frontend-design"
    assert target_skill.is_dir()
    assert not target_skill.is_symlink()
    assert (target_skill / "SKILL.md").read_text(encoding="utf-8") == FRONTEND_SKILL
    assert (workspace.target / "other-skill" / "SKILL.md").is_file()
    assert tree_snapshot(workspace.repo) == before


def test_link_mode_is_explicit(workspace: SimpleNamespace) -> None:
    result = run_installer(
        workspace,
        "--link",
        "--target",
        str(workspace.target),
        "frontend-design",
    )

    assert result.returncode == 0, result.stderr
    target_skill = workspace.target / "frontend-design"
    assert target_skill.is_symlink()
    assert (
        Path(os.readlink(target_skill)) == (workspace.repo / "skills" / "frontend-design").resolve()
    )


def test_copy_force_replaces_symlink(workspace: SimpleNamespace) -> None:
    linked = run_installer(
        workspace,
        "--link",
        "--target",
        str(workspace.target),
        "frontend-design",
    )
    assert linked.returncode == 0, linked.stderr
    target_skill = workspace.target / "frontend-design"
    assert target_skill.is_symlink()

    replaced = run_installer(
        workspace,
        "--copy",
        "--force",
        "--target",
        str(workspace.target),
        "frontend-design",
    )

    assert replaced.returncode == 0, replaced.stderr
    assert target_skill.is_dir()
    assert not target_skill.is_symlink()
    assert (target_skill / "SKILL.md").read_text(encoding="utf-8") == FRONTEND_SKILL

    backups = list((workspace.target / ".skills-hub-backups").iterdir())
    assert len(backups) == 1
    assert backups[0].is_symlink()


def test_conflict_preserves_existing_and_force_backs_up(workspace: SimpleNamespace) -> None:
    first = run_installer(
        workspace,
        "--target",
        str(workspace.target),
        "frontend-design",
    )
    assert first.returncode == 0, first.stderr
    installed = workspace.target / "frontend-design" / "SKILL.md"
    installed.write_text("local customization\n", encoding="utf-8")

    conflict = run_installer(
        workspace,
        "--target",
        str(workspace.target),
        "frontend-design",
    )
    assert conflict.returncode == 1
    assert "already exists" in conflict.stderr
    assert installed.read_text(encoding="utf-8") == "local customization\n"

    forced = run_installer(
        workspace,
        "--force",
        "--target",
        str(workspace.target),
        "frontend-design",
    )
    assert forced.returncode == 0, forced.stderr
    assert installed.read_text(encoding="utf-8") == FRONTEND_SKILL
    backups = list((workspace.target / ".skills-hub-backups").glob("frontend-design.*"))
    assert len(backups) == 1
    assert (backups[0] / "SKILL.md").read_text(encoding="utf-8") == "local customization\n"


def test_all_rejects_invalid_skill_ids(workspace: SimpleNamespace) -> None:
    write_skill(workspace.repo, "Bad_Skill", OTHER_SKILL)

    result = run_installer(workspace, "--all", "--target", str(workspace.target))

    assert result.returncode != 0
    assert "invalid skill id" in result.stderr
    assert "Bad_Skill" in result.stderr
    assert not workspace.target.exists()


def test_copy_excludes_generated_artifacts(workspace: SimpleNamespace) -> None:
    skill_dir = workspace.repo / "skills" / "frontend-design"
    (skill_dir / "__pycache__").mkdir()
    (skill_dir / "__pycache__" / "cache.pyc").write_text("cache", encoding="utf-8")
    (skill_dir / "stray.pyc").write_text("stray", encoding="utf-8")
    (skill_dir / ".ruff_cache").mkdir()
    (skill_dir / ".ruff_cache" / "data").write_text("cache", encoding="utf-8")
    (skill_dir / "node_modules" / "pkg").mkdir(parents=True)
    (skill_dir / "node_modules" / "pkg" / "index.js").write_text("module", encoding="utf-8")
    for name in (".pytest_cache", ".mypy_cache", ".venv", ".git", ".playwright-cli"):
        (skill_dir / name).mkdir()
        (skill_dir / name / "ignored").write_text("ignored", encoding="utf-8")

    result = run_installer(
        workspace,
        "--copy",
        "--target",
        str(workspace.target),
        "frontend-design",
    )

    assert result.returncode == 0, result.stderr
    target_skill = workspace.target / "frontend-design"
    assert (target_skill / "SKILL.md").is_file()
    assert (target_skill / "assets" / "keep.txt").is_file()
    assert not (target_skill / "__pycache__").exists()
    assert not (target_skill / "stray.pyc").exists()
    assert not (target_skill / ".ruff_cache").exists()
    assert not (target_skill / "node_modules").exists()
    for name in (".pytest_cache", ".mypy_cache", ".venv", ".git", ".playwright-cli"):
        assert not (target_skill / name).exists()


def test_copy_handles_newline_in_source_filename(workspace: SimpleNamespace) -> None:
    skill_dir = workspace.repo / "skills" / "frontend-design"
    unusual = skill_dir / "assets" / "line\nbreak.txt"
    unusual.write_text("newline-safe\n", encoding="utf-8")

    result = run_installer(
        workspace,
        "--target",
        str(workspace.target),
        "frontend-design",
    )

    assert result.returncode == 0, result.stderr
    assert (workspace.target / "frontend-design" / "assets" / "line\nbreak.txt").is_file()


def test_expands_leading_tilde(workspace: SimpleNamespace) -> None:
    result = run_installer(
        workspace,
        "--target",
        "~/installed-skills",
        "frontend-design",
    )

    assert result.returncode == 0, result.stderr
    assert (workspace.home / "installed-skills" / "frontend-design" / "SKILL.md").is_file()


def test_list_reads_folded_yaml_description_and_writes_nothing(
    workspace: SimpleNamespace,
) -> None:
    result = run_installer(workspace, "--list")

    assert result.returncode == 0, result.stderr
    assert "frontend-design" in result.stdout
    assert "other-skill" in result.stdout
    assert "Distinctive, accessible web interface design and frontend quality." in result.stdout
    assert not workspace.target.exists()


def test_dry_run_does_not_create_target(workspace: SimpleNamespace) -> None:
    result = run_installer(workspace, "--dry-run", "--target", str(workspace.target))

    assert result.returncode == 0, result.stderr
    assert "dry run" in result.stdout
    assert not workspace.target.exists()


def test_verify_requires_clean_checkout_at_exact_tag(workspace: SimpleNamespace) -> None:
    make_git_checkout(workspace)
    before = tree_snapshot(workspace.repo / "skills")

    result = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v1.2.3",
        "--target",
        str(workspace.target),
    )

    assert result.returncode == 0, result.stderr
    assert "verified clean checkout at v1.2.3" in result.stdout + result.stderr
    assert (workspace.target / "frontend-design" / "SKILL.md").is_file()
    assert tree_snapshot(workspace.repo / "skills") == before


def test_verify_accepts_clean_checkout_at_any_exact_release_tag(
    workspace: SimpleNamespace,
) -> None:
    make_git_checkout(workspace, tag="v2.0.0")

    result = run_installer(
        workspace,
        "--verify",
        "--target",
        str(workspace.target),
    )

    assert result.returncode == 0, result.stderr
    assert "verified clean checkout at v2.0.0" in result.stdout + result.stderr
    assert (workspace.target / "frontend-design" / "SKILL.md").is_file()


def test_verify_rejects_dirty_checkout(workspace: SimpleNamespace) -> None:
    make_git_checkout(workspace)
    (workspace.repo / "skills" / "frontend-design" / "SKILL.md").write_text(
        FRONTEND_SKILL + "\nlocal edit\n",
        encoding="utf-8",
    )

    result = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v1.2.3",
        "--target",
        str(workspace.target),
    )

    assert result.returncode != 0
    assert "local changes" in result.stderr
    assert not workspace.target.exists()


def test_verify_rejects_untracked_files(workspace: SimpleNamespace) -> None:
    make_git_checkout(workspace)
    (workspace.repo / "untracked.txt").write_text("local\n", encoding="utf-8")

    result = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v1.2.3",
        "--target",
        str(workspace.target),
    )

    assert result.returncode != 0
    assert "local changes" in result.stderr


def test_verify_rejects_ref_not_at_head(workspace: SimpleNamespace) -> None:
    make_git_checkout(workspace)
    second = run_git(
        workspace,
        "-c",
        "user.name=Installer Test",
        "-c",
        "user.email=installer@example.test",
        "commit",
        "--allow-empty",
        "-qm",
        "second",
    )
    assert second.returncode == 0, second.stderr

    result = run_installer(
        workspace,
        "--ref",
        "v1.2.3",
        "--target",
        str(workspace.target),
    )

    assert result.returncode != 0
    assert "not the commit tagged" in result.stderr


def test_verify_rejects_missing_tag(workspace: SimpleNamespace) -> None:
    make_git_checkout(workspace)

    result = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v9.9.9",
        "--target",
        str(workspace.target),
    )

    assert result.returncode != 0
    assert "tag not found" in result.stderr


def test_verify_without_ref_requires_an_exact_release_tag(
    workspace: SimpleNamespace,
) -> None:
    assert run_git(workspace, "init", "-q").returncode == 0
    assert run_git(workspace, "add", "-A").returncode == 0
    commit = run_git(
        workspace,
        "-c",
        "user.name=Installer Test",
        "-c",
        "user.email=installer@example.test",
        "commit",
        "-qm",
        "initial",
    )
    assert commit.returncode == 0, commit.stderr

    result = run_installer(
        workspace,
        "--verify",
        "--target",
        str(workspace.target),
    )

    assert result.returncode != 0
    assert "exact vX.Y.Z tag" in result.stderr


def test_verify_rejects_archive_without_git(workspace: SimpleNamespace) -> None:
    assert not (workspace.repo / ".git").exists()

    result = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v1.2.3",
        "--target",
        str(workspace.target),
    )

    assert result.returncode != 0
    assert "not a git checkout" in result.stderr
