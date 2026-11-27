from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import validate

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRAST = REPO_ROOT / "skills" / "frontend-design" / "scripts" / "contrast.py"
_CONTRAST_MODULE = validate.load_contrast_module(CONTRAST)


def run_contrast_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONTRAST), *args],
        capture_output=True,
        text=True,
        input=input_text,
        timeout=30,
        check=False,
    )


def run_contrast(*args: str, input_text: str | None = None) -> SimpleNamespace:
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    try:
        if input_text is not None:
            sys.stdin = io.StringIO(input_text)
        with redirect_stdout(out), redirect_stderr(err):
            try:
                rc = _CONTRAST_MODULE.main(list(args))
            except SystemExit as exc:
                rc = exc.code if isinstance(exc.code, int) else 2
    finally:
        sys.stdin = old_stdin
    return SimpleNamespace(returncode=rc, stdout=out.getvalue(), stderr=err.getvalue())


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


def test_cli_subprocess_smoke() -> None:
    ok = run_contrast_cli("#000000", "#ffffff", "--check")
    assert ok.returncode == 0, ok.stderr
    assert "contrast: 21.00:1" in ok.stdout

    stdin_fail = run_contrast_cli(
        "--pairs",
        "-",
        "--check",
        input_text=json.dumps([{"label": "cli fail", "fg": "#777777", "bg": "#ffffff"}]),
    )
    assert stdin_fail.returncode == 1
    assert "cli fail" in stdin_fail.stdout

    bad = run_contrast_cli("not-a-color", "#ffffff")
    assert bad.returncode == 2
    assert "error:" in bad.stderr


@pytest.mark.parametrize(
    "bad_color",
    [
        "####000000",
        "#+f+f+f",
        "#-1-1-1",
        "rgb(0, 0, 0, 1, 999)",
        "rgb(0, 0, 0 / 0.5)",
        "rgb(0 0 0 0.5)",
        "hsl(0 0% 0% 0.5)",
        "rgb(255, 50%, 0)",
        "rgb(1_00 0 0)",
        "rgb(100 % 0% 0%)",
        "rgb(100 %, 0%, 0%)",
        "rgb(12. 0 0)",
        "rgb(0 0 0 / 50 %)",
        "rgb(\u0662\u0665\u0665 0 0)",
        "rgb(nan 0 0)",
        "rgb(inf 0 0)",
        "hsl(1deg20 50% 50%)",
        "hsl(12.deg 50% 50%)",
        "hsl(0 50 % 50%)",
        "hsl(0, 50 %, 50%)",
        "hsl(0 50% 50% / 0.5 / 0.5)",
    ],
)
def test_malformed_hex_rgb_hsl_and_non_finite_colors_exit_two(bad_color: str) -> None:
    result = run_contrast(bad_color, "#ffffff")
    assert result.returncode == 2
    assert "error:" in result.stderr


@pytest.mark.parametrize(
    ("fg", "bg", "expected"),
    [
        ("#0008", "#ffffff", "4.48"),
        ("hsl(0 0 0)", "#ffffff", "21.00"),
        ("hsl(0.5turn 100 50)", "#000000", "16.75"),
        ("hsl(200grad 100% 50%)", "#000000", "16.75"),
        ("hsl(3.14159265rad 100% 50%)", "#000000", "16.75"),
        ("rgb(10%, 10%, 10%)", "white", "17.49"),
        ("rgb(+0e0 0 0 / .5)", "white", "3.98"),
        ("rgb(0 0 0 / 80%)", "white", "12.63"),
        ("hsl(0 0% 0% / 50%)", "white", "3.98"),
        ("#000000", "rgba(0, 0, 0, 0.5)", "5.28"),
        ("rgba(255, 255, 255, 0.9)", "rgba(0, 0, 0, 0.8)", "10.56"),
    ],
)
def test_css_color4_hsl_angles_unitless_and_rgba_hex(fg: str, bg: str, expected: str) -> None:
    result = run_contrast(fg, bg, "--label", "color4 probe", "--size", "large")
    assert result.returncode == 0, result.stderr
    assert "color4 probe" in result.stdout
    assert f"contrast: {expected}:1" in result.stdout


def test_color_hex_rounding_and_flatten_clamping() -> None:
    color_cls = _CONTRAST_MODULE.Color
    assert color_cls(0.0, 0.0, 0.0, 0.999).hex() == "#000000"
    assert color_cls(0.0, 0.0, 0.0, 0.5).hex() == "#00000080"

    # Directly constructed out-of-range Color instances must clamp safely in flatten().
    clamped_opaque = _CONTRAST_MODULE.flatten(color_cls(300.0, -50.0, 128.0, 1.5))
    assert clamped_opaque == color_cls(255.0, 0.0, 128.0, 1.0)

    clamped_blend = _CONTRAST_MODULE.flatten(
        color_cls(300.0, -20.0, 0.0, 0.5),
        color_cls(-10.0, 400.0, 0.0, 1.0),
    )
    assert clamped_blend == color_cls(127.5, 127.5, 0.0, 1.0)

    clamped_neg_alpha = _CONTRAST_MODULE.flatten(
        color_cls(100.0, 100.0, 100.0, -0.5),
        color_cls(0.0, 255.0, 0.0, 1.0),
    )
    assert clamped_neg_alpha == color_cls(0.0, 255.0, 0.0, 1.0)
