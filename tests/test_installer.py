"""Installer behavior tests using isolated HOME and target directories only."""

from __future__ import annotations

import atexit
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
INSTALL_DIR = ROOT / "install"
_GIT_TEMPLATES: dict[str, Path] = {}

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
    shutil.copytree(INSTALL_DIR, repo / "install")
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
        antigravity_installer=repo / "install" / "antigravity.sh",
        opencode_installer=repo / "install" / "opencode.sh",
    )


@pytest.fixture
def workspace(tmp_path: Path) -> SimpleNamespace:
    return make_workspace(tmp_path)


def run_installer(
    workspace: SimpleNamespace,
    *args: str,
    env: dict[str, str] | None = None,
    installer: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(installer or workspace.installer), *args],
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
    if tag not in _GIT_TEMPLATES:
        tpl_root = Path(tempfile.mkdtemp(prefix=f"skills-hub-git-tpl-{tag}-"))
        atexit.register(shutil.rmtree, tpl_root, True)
        tpl_ws = make_workspace(tpl_root)
        assert run_git(tpl_ws, "init", "-q").returncode == 0
        assert run_git(tpl_ws, "add", "-A").returncode == 0
        commit = run_git(
            tpl_ws,
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
            tpl_ws,
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
        _GIT_TEMPLATES[tag] = tpl_ws.repo
    shutil.rmtree(workspace.repo)
    shutil.copytree(_GIT_TEMPLATES[tag], workspace.repo)


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
    shutil.copytree(INSTALL_DIR, repo / "install")
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

    for installer_name in ("antigravity.sh", "opencode.sh"):
        result = subprocess.run(
            [str(repo / "install" / installer_name), "--target", str(tmp_path / "target")],
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


def test_list_parses_quoted_literal_empty_nextline_and_crlf_descriptions(
    workspace: SimpleNamespace,
) -> None:
    write_skill(
        workspace.repo,
        "quoted-skill",
        '---\r\nname: q\r\ndescription: "Quoted: value with \\"escapes\\" inside." # note\r\nlicense: MIT\r\n---\r\n# Q\r\n',
    )
    write_skill(
        workspace.repo,
        "single-quoted",
        "---\nname: s\ndescription: 'Single ''quoted'' value'\nlicense: MIT\n---\n# S\n",
    )
    write_skill(
        workspace.repo,
        "literal-skill",
        "---\nname: l\ndescription: |- # comment\n  Line one.\n  Line two.\nlicense: MIT\n---\n# L\n",
    )
    write_skill(
        workspace.repo,
        "nextline-skill",
        "---\nname: n\ndescription:\n  Next line plain scalar # comment\nlicense: MIT\n---\n# N\n",
    )
    write_skill(
        workspace.repo,
        "empty-quoted",
        '---\nname: e\ndescription: ""\nlicense: MIT\n---\n# E\n',
    )

    env = workspace.env.copy()
    env.pop("HOME", None)
    listed = run_installer(workspace, "--list", env=env)
    assert listed.returncode == 0, listed.stderr
    assert '    Quoted: value with "escapes" inside.' in listed.stdout
    assert "    Single 'quoted' value" in listed.stdout
    assert "    Line one.\n    Line two." in listed.stdout
    assert "    Next line plain scalar" in listed.stdout
    assert '""' not in listed.stdout

    # Empty quoted description must still trigger the missing-description warning on install.
    install = run_installer(
        workspace, "--dry-run", "--target", str(workspace.target), "empty-quoted"
    )
    assert install.returncode == 0, install.stderr
    assert "empty-quoted has no description" in install.stderr


def test_refuses_internal_symlink_in_copy_and_link_modes(
    workspace: SimpleNamespace, tmp_path: Path
) -> None:
    secret = tmp_path / "outside.txt"
    secret.write_text("secret\n", encoding="utf-8")
    (workspace.repo / "skills" / "frontend-design" / "leak.md").symlink_to(secret)

    for mode in ("--copy", "--link"):
        result = run_installer(
            workspace, mode, "--target", str(workspace.target), "frontend-design"
        )
        assert result.returncode != 0
        assert "symlink inside skill source" in result.stderr
        assert not (workspace.target / "frontend-design").exists()


def test_copy_excludes_secret_files_but_keeps_env_example(workspace: SimpleNamespace) -> None:
    skill = workspace.repo / "skills" / "frontend-design"
    (skill / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (skill / ".env.local").write_text("SECRET=2\n", encoding="utf-8")
    (skill / ".env.example").write_text("EXAMPLE=1\n", encoding="utf-8")
    (skill / "private.key").write_text("KEY\n", encoding="utf-8")
    (skill / "secrets").mkdir()
    (skill / "secrets" / "db.txt").write_text("DB\n", encoding="utf-8")

    result = run_installer(workspace, "--target", str(workspace.target), "frontend-design")
    assert result.returncode == 0, result.stderr
    installed = workspace.target / "frontend-design"
    assert not (installed / ".env").exists()
    assert not (installed / ".env.local").exists()
    assert not (installed / "private.key").exists()
    assert not (installed / "secrets").exists()
    assert (installed / ".env.example").is_file()
    assert "opencode reload" in result.stdout


def test_verify_rejects_gitignored_secret_file_inside_skills(workspace: SimpleNamespace) -> None:
    shutil.copyfile(ROOT / ".gitignore", workspace.repo / ".gitignore")
    assert run_git(workspace, "init", "-q").returncode == 0
    assert run_git(workspace, "add", "-A").returncode == 0
    assert (
        run_git(
            workspace,
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@example.test",
            "commit",
            "-qm",
            "init",
        ).returncode
        == 0
    )
    assert (
        run_git(
            workspace,
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@example.test",
            "tag",
            "-a",
            "v1.2.3",
            "-m",
            "v1.2.3",
        ).returncode
        == 0
    )
    (workspace.repo / "skills" / "frontend-design" / ".env").write_text(
        "SECRET=1\n", encoding="utf-8"
    )

    result = run_installer(
        workspace, "--verify", "--ref", "v1.2.3", "--target", str(workspace.target)
    )
    assert result.returncode != 0
    assert "ignored files exist inside skills/" in result.stderr


def test_cli_edge_cases_default_xdg_dedup_all_link_and_backup_symlink(
    workspace: SimpleNamespace, tmp_path: Path
) -> None:
    # --all combined with positional skill is rejected.
    bad_all = run_installer(
        workspace, "--all", "frontend-design", "--target", str(workspace.target)
    )
    assert bad_all.returncode != 0
    assert "cannot combine --all" in bad_all.stderr

    # Invalid --ref syntax is rejected.
    bad_ref = run_installer(workspace, "--ref", "not-a-tag", "--target", str(workspace.target))
    assert bad_ref.returncode != 0
    assert "invalid --ref tag" in bad_ref.stderr

    # Duplicate positional skill arguments are deduplicated cleanly.
    dup = run_installer(
        workspace,
        "--target",
        str(workspace.target),
        "frontend-design",
        "frontend-design",
    )
    assert dup.returncode == 0, dup.stderr
    assert (workspace.target / "frontend-design" / "SKILL.md").is_file()

    # Symlinked .skills-hub-backups is refused on --force replacement.
    (workspace.target / ".skills-hub-backups").symlink_to(tmp_path)
    bad_bak = run_installer(
        workspace,
        "--force",
        "--target",
        str(workspace.target),
        "frontend-design",
    )
    assert bad_bak.returncode != 0
    assert "symlinked backup directory" in bad_bak.stderr

    # Default target honors XDG_CONFIG_HOME and idempotent --link reports already linked.
    xdg = tmp_path / "xdg"
    env = workspace.env.copy()
    env["XDG_CONFIG_HOME"] = str(xdg)
    first_link = run_installer(workspace, "--link", "frontend-design", env=env)
    assert first_link.returncode == 0, first_link.stderr
    assert (xdg / "opencode" / "skills" / "frontend-design").is_symlink()
    second_link = run_installer(workspace, "--link", "frontend-design", env=env)
    assert second_link.returncode == 0, second_link.stderr
    assert "already linked" in second_link.stdout


def test_verify_multi_tag_selects_highest_semver_and_honors_list_verify(
    workspace: SimpleNamespace,
) -> None:
    make_git_checkout(workspace, tag="v1.2.0-rc.1")
    for tag in ("v1.2.0", "v1.10.0-rc.1", "v1.10.0"):
        assert (
            run_git(
                workspace,
                "-c",
                "user.name=T",
                "-c",
                "user.email=t@example.test",
                "tag",
                "-a",
                tag,
                "-m",
                tag,
            ).returncode
            == 0
        )
    listed = run_installer(workspace, "--list", "--verify")
    assert listed.returncode == 0, listed.stderr
    assert "verified clean checkout at v1.10.0" in listed.stdout


def test_preflight_prevents_partial_install_on_conflict_and_symlink_in_second_skill(
    workspace: SimpleNamespace, tmp_path: Path
) -> None:
    # Pre-install only other-skill, then attempt to install both without --force:
    # frontend-design must NOT be installed partially.
    first = run_installer(workspace, "--target", str(workspace.target), "other-skill")
    assert first.returncode == 0, first.stderr
    conflict = run_installer(
        workspace, "--target", str(workspace.target), "frontend-design", "other-skill"
    )
    assert conflict.returncode == 1
    assert "no changes were written" in conflict.stderr
    assert not (workspace.target / "frontend-design").exists()

    # Symlink in a skill must fail before creating a fresh target directory.
    fresh_target = tmp_path / "fresh-target"
    secret = tmp_path / "outside.txt"
    secret.write_text("x\n", encoding="utf-8")
    (workspace.repo / "skills" / "other-skill" / "secrets").symlink_to(secret)

    # Even a pruned name like `secrets` as a symlink must be refused in --link mode.
    link_res = run_installer(
        workspace, "--link", "--target", str(fresh_target), "frontend-design", "other-skill"
    )
    assert link_res.returncode != 0
    assert "symlink inside skill source" in link_res.stderr
    assert not fresh_target.exists()


def test_copy_handles_dash_filename_and_extended_secret_exclusions(
    workspace: SimpleNamespace,
) -> None:
    skill = workspace.repo / "skills" / "frontend-design"
    (skill / "--checkpoint=1").write_text("safe dash file\n", encoding="utf-8")
    for secret_name in (
        "credentials_prod.json",
        "cert.pem",
        "keystore.p12",
        "id_rsa",
        "id_ed25519",
    ):
        (skill / secret_name).write_text("SECRET\n", encoding="utf-8")
    for secret_dir in (".opencode", ".claude", ".agents", ".gemini"):
        (skill / secret_dir).mkdir()
        (skill / secret_dir / "cfg.json").write_text("{}\n", encoding="utf-8")

    for idx, installer in enumerate((workspace.antigravity_installer, workspace.opencode_installer)):
        target = workspace.target / f"run-{idx}"
        res = run_installer(
            workspace, "--target", str(target), "frontend-design", installer=installer
        )
        assert res.returncode == 0, res.stderr
        installed = target / "frontend-design"
        assert (installed / "--checkpoint=1").read_text(encoding="utf-8") == "safe dash file\n"
        for name in (
            "credentials_prod.json",
            "cert.pem",
            "keystore.p12",
            "id_rsa",
            "id_ed25519",
            ".opencode",
            ".claude",
            ".agents",
            ".gemini",
        ):
            assert not (installed / name).exists()


def test_verify_rejects_tracked_symlink_and_ignores_benign_pycache_in_copy(
    workspace: SimpleNamespace, tmp_path: Path
) -> None:
    shutil.copyfile(ROOT / ".gitignore", workspace.repo / ".gitignore")
    assert run_git(workspace, "init", "-q").returncode == 0
    assert run_git(workspace, "add", "-A").returncode == 0
    assert (
        run_git(
            workspace,
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@example.test",
            "commit",
            "-qm",
            "init",
        ).returncode
        == 0
    )
    assert (
        run_git(
            workspace,
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@example.test",
            "tag",
            "-a",
            "v1.2.3",
            "-m",
            "v1.2.3",
        ).returncode
        == 0
    )

    # Benign __pycache__ in skills/ is tolerated in --verify --copy and never copied to target.
    cache_dir = workspace.repo / "skills" / "frontend-design" / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "x.pyc").write_bytes(b"pyc")
    ok = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v1.2.3",
        "--target",
        str(workspace.target),
        "frontend-design",
    )
    assert ok.returncode == 0, ok.stderr
    assert not (workspace.target / "frontend-design" / "__pycache__").exists()
    # --verify --link rejects even __pycache__ because the live directory would be exposed.
    link_target = tmp_path / "link-target"
    bad_link = run_installer(
        workspace,
        "--verify",
        "--link",
        "--ref",
        "v1.2.3",
        "--target",
        str(link_target),
        "frontend-design",
    )
    assert bad_link.returncode != 0
    assert "ignored files exist" in bad_link.stderr

    # Tracked symlink inside skills/ must be rejected by --verify (git ls-tree check).
    shutil.rmtree(cache_dir)
    (workspace.repo / "skills" / "frontend-design" / "secrets").symlink_to("/etc/hosts")
    assert run_git(workspace, "add", "-f", "skills/frontend-design/secrets").returncode == 0
    assert (
        run_git(
            workspace,
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@example.test",
            "commit",
            "-qm",
            "sym",
        ).returncode
        == 0
    )
    assert (
        run_git(
            workspace,
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@example.test",
            "tag",
            "-a",
            "v1.2.4",
            "-m",
            "v1.2.4",
        ).returncode
        == 0
    )
    sym_target = tmp_path / "sym-target"
    bad_sym = run_installer(
        workspace, "--verify", "--ref", "v1.2.4", "--target", str(sym_target), "frontend-design"
    )
    assert bad_sym.returncode != 0
    assert "symlink or gitlink inside verified skill source" in bad_sym.stderr
    assert not sym_target.exists()


def test_xdg_default_target_works_without_home_and_yaml_edge_cases(
    workspace: SimpleNamespace, tmp_path: Path
) -> None:
    write_skill(
        workspace.repo,
        "yaml-edges",
        "---\n"
        "name: y\n"
        "description: first ignored\n"
        "description:\n"
        "  # pure comment line\n"
        '  "next-line quoted"\n'
        "license: MIT\n"
        "---\n# Y\n",
    )
    write_skill(
        workspace.repo,
        "sq-sentinel",
        "---\nname: sq\ndescription: 'literal __SQ__ and ''quote'''\nlicense: MIT\n---\n# SQ\n",
    )
    write_skill(
        workspace.repo,
        "lit-blank",
        "---\nname: lb\ndescription: |\n\n  after blank\nlicense: MIT\n---\n# LB\n",
    )
    write_skill(
        workspace.repo,
        "plain-comment",
        "---\nname: pc\ndescription: hello\n  # pure comment\n  world\nlicense: MIT\n---\n# PC\n",
    )
    listed = run_installer(workspace, "--list")
    assert listed.returncode == 0, listed.stderr
    assert "    next-line quoted\n" in listed.stdout
    assert "    literal __SQ__ and 'quote'\n" in listed.stdout
    assert "    hello world\n" in listed.stdout
    assert "    after blank\n" in listed.stdout
    assert "# pure comment" not in listed.stdout

    # XDG_CONFIG_HOME without HOME must still resolve default target for OpenCode.
    xdg = tmp_path / "xdg-no-home"
    env = workspace.env.copy()
    env.pop("HOME", None)
    env["XDG_CONFIG_HOME"] = str(xdg)
    res = run_installer(workspace, "frontend-design", env=env)
    assert res.returncode == 0, res.stderr
    assert (xdg / "opencode" / "skills" / "frontend-design" / "SKILL.md").is_file()


def test_antigravity_installer_default_target_reload_verify_and_lib_guard(
    workspace: SimpleNamespace, tmp_path: Path
) -> None:
    # Default target uses $HOME/.gemini/config/skills even when XDG_CONFIG_HOME is set.
    xdg = tmp_path / "xdg-ignored"
    env = workspace.env.copy()
    env["XDG_CONFIG_HOME"] = str(xdg)
    copied = run_installer(
        workspace,
        "frontend-design",
        env=env,
        installer=workspace.antigravity_installer,
    )
    assert copied.returncode == 0, copied.stderr
    assert "Antigravity skill install" in copied.stdout
    assert "/skills reload" in copied.stdout
    expected_dir = workspace.home / ".gemini" / "config" / "skills" / "frontend-design"
    assert (expected_dir / "SKILL.md").is_file()
    assert not (xdg / "gemini").exists()

    # --link mode and idempotent re-run work cleanly.
    linked = run_installer(
        workspace,
        "--link",
        "other-skill",
        env=env,
        installer=workspace.antigravity_installer,
    )
    assert linked.returncode == 0, linked.stderr
    assert (workspace.home / ".gemini" / "config" / "skills" / "other-skill").is_symlink()
    relinked = run_installer(
        workspace,
        "--link",
        "other-skill",
        env=env,
        installer=workspace.antigravity_installer,
    )
    assert relinked.returncode == 0, relinked.stderr
    assert "already linked" in relinked.stdout

    # Without HOME, default target fails cleanly while --list still succeeds.
    no_home = env.copy()
    no_home.pop("HOME", None)
    bad = run_installer(
        workspace,
        "frontend-design",
        env=no_home,
        installer=workspace.antigravity_installer,
    )
    assert bad.returncode != 0
    assert "HOME is not set; pass --target DIR" in bad.stderr
    listed = run_installer(
        workspace,
        "--list",
        env=no_home,
        installer=workspace.antigravity_installer,
    )
    assert listed.returncode == 0, listed.stderr
    assert "frontend-design" in listed.stdout

    # --verify --ref works with install/antigravity.sh on a clean tagged git checkout.
    make_git_checkout(workspace, tag="v1.3.0")
    verified = run_installer(
        workspace,
        "--verify",
        "--ref",
        "v1.3.0",
        "--target",
        str(workspace.target),
        installer=workspace.antigravity_installer,
    )
    assert verified.returncode == 0, verified.stderr
    assert "verified clean checkout at v1.3.0" in verified.stdout
    assert (workspace.target / "frontend-design" / "SKILL.md").is_file()

    # Both installers refuse a symlinked install/lib.sh.
    real_lib = tmp_path / "real-lib.sh"
    shutil.move(str(workspace.repo / "install" / "lib.sh"), str(real_lib))
    (workspace.repo / "install" / "lib.sh").symlink_to(real_lib)
    for installer in (workspace.antigravity_installer, workspace.opencode_installer):
        sym_res = run_installer(workspace, "--dry-run", installer=installer)
        assert sym_res.returncode != 0
        assert "missing or symlinked" in sym_res.stderr
