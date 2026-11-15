from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRAST = REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py"


def run_contrast(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONTRAST), *args],
        capture_output=True,
        text=True,
        input=input_text,
        timeout=30,
        check=False,
    )


@pytest.mark.parametrize(
    ("fg", "bg", "expected"),
    [
        ("#000000", "#ffffff", "21.00"),
        ("#000", "#fff", "21.00"),
        ("rgb(0 0 0)", "white", "21.00"),
        ("rgb(0, 0, 0)", "white", "21.00"),
        ("rgb(10% 10% 10%)", "white", "17.49"),
        ("hsl(0 0% 0%)", "white", "21.00"),
        ("black", "white", "21.00"),
        ("#00000080", "#ffffff", "4.00"),
        ("rgba(0, 0, 0, 0.8)", "white", "12.63"),
        ("hsla(0 0% 0% / 0.8)", "white", "12.63"),
    ],
)
def test_color_formats(fg: str, bg: str, expected: str) -> None:
    result = run_contrast(fg, bg)
    assert result.returncode == 0, result.stderr
    assert f"contrast: {expected}:1" in result.stdout


def test_json_output() -> None:
    result = run_contrast("#000000", "#ffffff", "--json", "--size", "ui")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    entry = payload[0]
    assert entry["fg"] == "#000000"
    assert entry["bg"] == "#ffffff"
    assert entry["size"] == "ui"
    assert entry["ratio"] == 21.0
    assert entry["aa"] is True
    assert entry["aaa"] is None
    assert entry["aa_threshold"] == 3.0


def test_quiet_output_and_exit_code() -> None:
    failing = run_contrast("#777777", "#ffffff", "--check", "--quiet")
    assert failing.returncode == 1
    assert "0 pass, 1 fail (AA)" in failing.stdout
    assert "contrast: 4.48:1" in failing.stdout

    passing = run_contrast("#000000", "#ffffff", "--quiet")
    assert passing.returncode == 0
    assert "1 pass, 0 fail (AA)" in passing.stdout
    assert "contrast:" not in passing.stdout


def test_pairs_from_stdin() -> None:
    payload = json.dumps(
        {
            "pairs": [
                {
                    "label": "stdin pass",
                    "fg": "#000000",
                    "bg": "#ffffff",
                    "size": "normal",
                }
            ]
        }
    )
    result = run_contrast("--pairs", "-", "--check", input_text=payload)
    assert result.returncode == 0, result.stderr
    assert "stdin pass" in result.stdout

    failing_payload = json.dumps(
        [{"label": "stdin fail", "fg": "#777777", "bg": "#ffffff", "size": "normal"}]
    )
    failing = run_contrast("--pairs", "-", "--check", input_text=failing_payload)
    assert failing.returncode == 1
    assert "stdin fail" in failing.stdout


def test_check_controls_exit_code() -> None:
    without_check = run_contrast("#777777", "#ffffff")
    assert without_check.returncode == 0
    assert "FAIL" in without_check.stdout

    with_check = run_contrast("#777777", "#ffffff", "--check")
    assert with_check.returncode == 1


def test_missing_file_exits_two() -> None:
    result = run_contrast("--pairs", "/nonexistent/contrast-pairs.json")
    assert result.returncode == 2
    assert "error:" in result.stderr


def test_invalid_colors_exit_two() -> None:
    direct = run_contrast("not-a-color", "#ffffff")
    assert direct.returncode == 2
    assert "error:" in direct.stderr

    payload = json.dumps([{"label": "bad", "fg": "#zzzzzz", "bg": "#ffffff"}])
    pairs = run_contrast("--pairs", "-", input_text=payload)
    assert pairs.returncode == 2
    assert "error:" in pairs.stderr


def test_invalid_pairs_shape_exits_two() -> None:
    payload = json.dumps([{"label": "missing bg", "fg": "#000000"}])
    result = run_contrast("--pairs", "-", input_text=payload)
    assert result.returncode == 2
    assert "needs 'fg' and 'bg'" in result.stderr


def test_self_test() -> None:
    result = run_contrast("--self-test")
    assert result.returncode == 0, result.stderr
    assert not any(line.startswith("FAIL:") for line in result.stdout.splitlines())
    assert result.stdout.count("ok:") >= 7
