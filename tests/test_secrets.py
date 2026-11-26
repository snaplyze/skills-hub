"""Tests for secret-related .gitignore coverage and Secret Scan workflow policy."""

from __future__ import annotations

import re
import shlex
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRET_SCAN_WORKFLOW = ROOT / ".github" / "workflows" / "secret-scan.yml"

REQUIRED_IGNORED = [
    ".env",
    ".env.local",
    ".env.production",
    "config/.env",
    "private.pem",
    "server.key",
    "certificate.p12",
    "secrets/database.env",
    "credentials",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
    ".opencode/config.json",
    ".claude/settings.json",
    ".agents/skills/example.md",
]

EXISTING_IGNORED = [
    "node_modules/package/index.js",
    ".venv/bin/python",
    ".ruff_cache/data",
    ".pytest_cache/state",
    ".playwright-cli/trace.zip",
    "__pycache__/module.pyc",
]


def _active_shell_commands(script: str) -> list[list[str]]:
    """Strip shell comments, join backslash continuations, and split commands into tokens."""
    logical_lines: list[str] = []
    current = ""
    for raw_line in script.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            if current:
                logical_lines.append(current)
                current = ""
            continue
        if stripped.endswith("\\"):
            current += stripped[:-1].rstrip() + " "
        else:
            current += stripped
            logical_lines.append(current)
            current = ""
    if current:
        logical_lines.append(current)
    commands: list[list[str]] = []
    for line in logical_lines:
        try:
            tokens = shlex.split(line, comments=True)
        except ValueError:
            tokens = line.split()
        if tokens:
            commands.append(tokens)
    return commands


def _flag_value(cmd: list[str], flag: str) -> str:
    assert flag in cmd, f"missing required flag {flag}"
    idx = cmd.index(flag)
    assert idx + 1 < len(cmd), f"flag {flag} missing argument"
    return cmd[idx + 1]


def _extract_heredoc_body(script: str, target_substring: str) -> str:
    """Extract body of an active (non-comment) heredoc redirected to target_substring."""
    lines = script.splitlines()
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.search(r"<<\s*['\"]?([A-Za-z0-9_]+)['\"]?", stripped)
        if match and target_substring in stripped.split("#", 1)[0]:
            delimiter = match.group(1)
            body_lines: list[str] = []
            for body_line in lines[index + 1 :]:
                if body_line.strip() == delimiter:
                    return "\n".join(body_lines)
                body_lines.append(body_line)
    raise AssertionError(f"missing active heredoc writing {target_substring!r}")


def _assert_secret_scan_contract(workflow_text: str) -> None:
    data = yaml.safe_load(workflow_text)
    assert isinstance(data, dict), "secret-scan workflow must be a YAML mapping"
    jobs = data.get("jobs")
    assert isinstance(jobs, dict) and "gitleaks" in jobs
    steps = jobs["gitleaks"].get("steps")
    assert isinstance(steps, list) and steps

    names = [step.get("name", "") for step in steps if isinstance(step, dict)]
    install_idx = names.index("Install gitleaks")
    pin_idx = names.index("Pin trusted scan configuration")
    scan_idx = names.index("Scan repository history")
    assert install_idx < pin_idx < scan_idx, f"unexpected step order: {names}"

    steps_by_name = {step.get("name"): step for step in steps if isinstance(step, dict)}

    install_step = steps_by_name["Install gitleaks"]
    assert isinstance(install_step.get("run"), str)
    install_commands = _active_shell_commands(install_step["run"])
    assert any("sha256sum" in cmd and "--check" in cmd for cmd in install_commands)

    pin_step = steps_by_name["Pin trusted scan configuration"]
    assert isinstance(pin_step.get("run"), str)
    toml_body = _extract_heredoc_body(pin_step["run"], "$RUNNER_TEMP/gitleaks.toml")
    parsed_toml = tomllib.loads(toml_body)
    assert parsed_toml.get("extend", {}).get("useDefault") is True, (
        "pinned gitleaks.toml must enable extend.useDefault = true"
    )
    pin_commands = _active_shell_commands(pin_step["run"])
    assert any("$RUNNER_TEMP/gitleaks.ignore" in " ".join(cmd) for cmd in pin_commands)

    scan_step = steps_by_name["Scan repository history"]
    assert isinstance(scan_step.get("run"), str)
    commands = _active_shell_commands(scan_step["run"])
    detect_cmd = next(
        (cmd for cmd in commands if len(cmd) >= 2 and "gitleaks" in cmd[0] and cmd[1] == "detect"),
        None,
    )
    assert detect_cmd is not None, "Scan repository history step must invoke gitleaks detect"
    assert _flag_value(detect_cmd, "--config") == "$RUNNER_TEMP/gitleaks.toml"
    assert _flag_value(detect_cmd, "--gitleaks-ignore-path") == "$RUNNER_TEMP/gitleaks.ignore"
    assert "--ignore-gitleaks-allow" in detect_cmd, (
        "gitleaks detect must pass --ignore-gitleaks-allow"
    )
    assert "--redact" in detect_cmd, "gitleaks detect must pass --redact"


@pytest.fixture(scope="module")
def ignored_set(tmp_path_factory: pytest.TempPathFactory) -> set[str]:
    """Batch-query git check-ignore once for every candidate path in a module repo."""
    repo = tmp_path_factory.mktemp("ignore-repo")
    shutil.copyfile(ROOT / ".gitignore", repo / ".gitignore")
    subprocess.run(
        ["git", "init", "--quiet", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    candidates = [*REQUIRED_IGNORED, *EXISTING_IGNORED, ".env.example"]
    result = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "--no-index", "--stdin"],
        input="\n".join(candidates) + "\n",
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise AssertionError(f"git check-ignore failed: {result.stderr}")
    return set(result.stdout.splitlines())


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    """Create a throwaway repository with this project's .gitignore."""
    shutil.copyfile(ROOT / ".gitignore", tmp_path / ".gitignore")
    subprocess.run(
        ["git", "init", "--quiet", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return tmp_path


def create_placeholder(repo: Path, path: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("placeholder\n", encoding="utf-8")


@pytest.mark.parametrize("path", REQUIRED_IGNORED)
def test_secret_path_is_ignored(ignored_set: set[str], path: str) -> None:
    assert path in ignored_set


@pytest.mark.parametrize("path", EXISTING_IGNORED)
def test_existing_ignore_patterns_are_kept(ignored_set: set[str], path: str) -> None:
    assert path in ignored_set


def test_env_example_is_allowed(ignored_set: set[str]) -> None:
    assert ".env.example" not in ignored_set


def test_git_add_does_not_stage_secret_files(temp_repo: Path) -> None:
    for path in REQUIRED_IGNORED:
        create_placeholder(temp_repo, path)
    create_placeholder(temp_repo, ".env.example")
    create_placeholder(temp_repo, "safe.txt")

    subprocess.run(
        ["git", "-C", str(temp_repo), "add", "--all"],
        check=True,
        capture_output=True,
        text=True,
    )
    staged = set(
        subprocess.run(
            ["git", "-C", str(temp_repo), "diff", "--cached", "--name-only"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )

    assert {".env.example", "safe.txt"} <= staged
    assert not staged.intersection(REQUIRED_IGNORED)


def test_secret_scan_pins_rules_and_disables_inline_allow() -> None:
    _assert_secret_scan_contract(SECRET_SCAN_WORKFLOW.read_text(encoding="utf-8"))


def test_secret_scan_commented_flags_and_untrusted_config_fail() -> None:
    text = SECRET_SCAN_WORKFLOW.read_text(encoding="utf-8")

    # 1. Commenting out --ignore-gitleaks-allow must fail.
    mutated = "# --ignore-gitleaks-allow\n" + text.replace(
        "            --ignore-gitleaks-allow \\\n", ""
    )
    assert mutated != text
    with pytest.raises(AssertionError, match="--ignore-gitleaks-allow"):
        _assert_secret_scan_contract(mutated)

    # 2. Commenting out useDefault = true inside the TOML heredoc must fail.
    commented_toml = text.replace("useDefault = true", "# useDefault = true")
    with pytest.raises(AssertionError, match="useDefault"):
        _assert_secret_scan_contract(commented_toml)

    # 3. Pointing --config to a PR-controlled repo file instead of $RUNNER_TEMP must fail.
    pr_config = text.replace('"$RUNNER_TEMP/gitleaks.toml"', '".gitleaks.toml"')
    with pytest.raises(AssertionError):
        _assert_secret_scan_contract(pr_config)
