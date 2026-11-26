#!/usr/bin/env python3
"""
WCAG 2.2 contrast checker.

Usage:
    python3 contrast.py "#1b1916" "#f7f6f2"
    python3 contrast.py "#1b1916" "#f7f6f2" --label "body on canvas"
    python3 contrast.py "#2f8f7f" "#f7f6f2" --size ui
    python3 contrast.py --pairs palette.json
    python3 contrast.py --pairs palette.json --check
    python3 contrast.py --self-test

Supported color formats:
    #rgb, #rgba, #rrggbb, #rrggbbaa
    rgb(27 25 22), rgb(27, 25, 22), rgb(10% 9% 8%)
    rgba(27, 25, 22, 0.8), rgb(27 25 22 / 80%)
    hsl(30 20% 20%), hsl(30, 20%, 20%), hsla(30 20% 20% / 0.8)
    transparent, white, black

Alpha is composited over the background. If the background itself is
translucent, it is first composited over white; document the real backdrop
when auditing a layered surface.

Exit codes:
    0  all checked pairs pass (or no --check was requested)
    1  at least one pair fails under --check
    2  invalid input or file error

No external dependencies.
"""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

NAMED_COLORS = {
    "transparent": (0.0, 0.0, 0.0, 0.0),
    "white": (255.0, 255.0, 255.0, 1.0),
    "black": (0.0, 0.0, 0.0, 1.0),
    "red": (255.0, 0.0, 0.0, 1.0),
    "green": (0.0, 128.0, 0.0, 1.0),
    "blue": (0.0, 0.0, 255.0, 1.0),
}

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
FN_RE = re.compile(r"^([a-zA-Z]+)\((.*)\)$")
HUE_RE = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)(deg|rad|grad|turn)?$")


@dataclass(frozen=True)
class Color:
    r: float
    g: float
    b: float
    a: float = 1.0

    def clamped(self) -> Color:
        return Color(
            min(255.0, max(0.0, self.r)),
            min(255.0, max(0.0, self.g)),
            min(255.0, max(0.0, self.b)),
            min(1.0, max(0.0, self.a)),
        )

    def hex(self) -> str:
        c = self.clamped()
        if c.a < 1.0:
            return f"#{round(c.r):02x}{round(c.g):02x}{round(c.b):02x}{round(c.a * 255):02x}"
        return f"#{round(c.r):02x}{round(c.g):02x}{round(c.b):02x}"


WHITE = Color(255.0, 255.0, 255.0, 1.0)


@dataclass(frozen=True)
class Result:
    label: str
    fg: Color
    bg: Color
    ratio: float
    size: str
    aa: bool
    aaa: bool
    threshold: float
    aaa_threshold: float = math.nan
    size_label: str = ""


def _parse_finite_float(raw: str) -> float:
    val = float(raw)
    if not math.isfinite(val):
        raise ValueError(f"Non-finite numeric value: {raw!r}")
    return val


def parse_channel(value: str, scale: float = 255.0) -> float:
    value = value.strip()
    if value.endswith("%"):
        return _parse_finite_float(value[:-1]) / 100.0 * scale
    return _parse_finite_float(value)


def parse_hsl_percent(value: str) -> float:
    """Parse CSS Color 4 HSL saturation/lightness (percentage or unitless 0..100)."""
    value = value.strip()
    raw = _parse_finite_float(value[:-1]) if value.endswith("%") else _parse_finite_float(value)
    return min(1.0, max(0.0, raw / 100.0))


def parse_hue(value: str) -> float:
    match = HUE_RE.fullmatch(value.strip().lower())
    if not match:
        raise ValueError(f"Invalid hue value: {value!r}")
    angle = _parse_finite_float(match.group(1))
    unit = match.group(2) or "deg"
    if unit == "rad":
        angle = math.degrees(angle)
    elif unit == "grad":
        angle *= 0.9
    elif unit == "turn":
        angle *= 360.0
    return angle % 360.0


def parse_hex(value: str) -> Color:
    match = HEX_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Invalid hex color: {value!r}")
    raw = match.group(1)
    if len(raw) in (3, 4):
        raw = "".join(ch * 2 for ch in raw)
    r = int(raw[0:2], 16)
    g = int(raw[2:4], 16)
    b = int(raw[4:6], 16)
    a = int(raw[6:8], 16) / 255.0 if len(raw) == 8 else 1.0
    return Color(float(r), float(g), float(b), a)


def parse_alpha(value: str | None) -> float:
    if value is None:
        return 1.0
    value = value.strip()
    if not value:
        raise ValueError("Empty alpha channel")
    if value.endswith("%"):
        return min(1.0, max(0.0, _parse_finite_float(value[:-1]) / 100.0))
    return min(1.0, max(0.0, _parse_finite_float(value)))


def parse_function(value: str) -> Color:
    match = FN_RE.match(value.strip())
    if not match:
        raise ValueError(f"Invalid color function: {value!r}")
    name = match.group(1).lower()
    body = match.group(2).strip()

    has_slash = "/" in body
    if has_slash:
        if body.count("/") > 1:
            raise ValueError(f"Invalid color function: {value!r}")
        main, alpha_part = body.split("/", 1)
        if "," in main:
            raise ValueError(f"Mixed comma and slash syntax in color function: {value!r}")
        alpha = parse_alpha(alpha_part)
    else:
        main = body
        alpha = 1.0

    # Support both comma-separated (legacy) and space-separated (CSS Color 4) syntax.
    if "," in main:
        parts = [p.strip() for p in main.split(",")]
        if any(not p for p in parts):
            raise ValueError(f"Empty argument in color function: {value!r}")
    else:
        parts = main.split()

    if has_slash:
        if len(parts) != 3:
            raise ValueError(f"Invalid {name}() color: {value!r}")
    elif len(parts) not in (3, 4):
        raise ValueError(f"Invalid {name}() color: {value!r}")

    if name in ("rgb", "rgba"):
        r = parse_channel(parts[0])
        g = parse_channel(parts[1])
        b = parse_channel(parts[2])
        if len(parts) == 4:
            alpha = parse_alpha(parts[3])
        return Color(r, g, b, alpha).clamped()

    if name in ("hsl", "hsla"):
        hue = parse_hue(parts[0])
        sat = parse_hsl_percent(parts[1])
        light = parse_hsl_percent(parts[2])
        if len(parts) == 4:
            alpha = parse_alpha(parts[3])
        r, g, b = colorsys.hls_to_rgb(hue / 360.0, light, sat)
        return Color(r * 255.0, g * 255.0, b * 255.0, alpha).clamped()

    raise ValueError(f"Unsupported color function: {name!r}")


def parse_color(value: str) -> Color:
    value = value.strip()
    if not value:
        raise ValueError("Empty color")
    lower = value.lower()
    if lower in NAMED_COLORS:
        return Color(*NAMED_COLORS[lower])
    if lower.startswith("#"):
        return parse_hex(lower)
    if lower.startswith(("rgb(", "rgba(", "hsl(", "hsla(")):
        return parse_function(lower)
    raise ValueError(f"Unsupported color {value!r}; use hex, rgb(), hsl(), or a named color")


def flatten(color: Color, backdrop: Color = WHITE) -> Color:
    """Composite a possibly translucent color over an opaque backdrop."""
    if color.a >= 1.0:
        return color if color.a == 1.0 else Color(color.r, color.g, color.b, 1.0)
    a = color.a
    inv = 1.0 - a
    return Color(
        color.r * a + backdrop.r * inv,
        color.g * a + backdrop.g * inv,
        color.b * a + backdrop.b * inv,
        1.0,
    )


def composite(fg: Color, bg: Color) -> tuple[Color, Color]:
    """Return the effective foreground and background after alpha compositing."""
    effective_bg = flatten(bg, WHITE)
    effective_fg = flatten(fg, effective_bg)
    return effective_fg, effective_bg


def linear_channel(channel: float) -> float:
    c = channel / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _opaque_luminance(color: Color) -> float:
    return (
        0.2126 * linear_channel(color.r)
        + 0.7152 * linear_channel(color.g)
        + 0.0722 * linear_channel(color.b)
    )


def luminance(color: Color) -> float:
    return _opaque_luminance(flatten(color))


def contrast_ratio(fg: Color, bg: Color) -> float:
    fg_eff, bg_eff = composite(fg, bg)
    l1 = _opaque_luminance(fg_eff)
    l2 = _opaque_luminance(bg_eff)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def thresholds(size: str) -> tuple[float, float, str]:
    """Return (AA threshold, AAA threshold, human label)."""
    normalized = size.strip().lower()
    if normalized in ("large", "large-text"):
        return 3.0, 4.5, "large text"
    if normalized in ("ui", "non-text", "nontext", "graphic"):
        return 3.0, math.nan, "UI / non-text"
    if normalized in ("normal", "body", "text"):
        return 4.5, 7.0, "normal text"
    raise ValueError(f"Unknown size {size!r}; use normal, large, or ui")


def check_pair(fg: Color, bg: Color, label: str, size: str = "normal") -> Result:
    aa_threshold, aaa_threshold, size_label = thresholds(size)
    ratio = contrast_ratio(fg, bg)
    aa = ratio + 1e-9 >= aa_threshold
    aaa = (ratio + 1e-9 >= aaa_threshold) if not math.isnan(aaa_threshold) else False
    return Result(label, fg, bg, ratio, size, aa, aaa, aa_threshold, aaa_threshold, size_label)


def format_result(result: Result) -> str:
    aaa_threshold = result.aaa_threshold
    size_label = result.size_label or thresholds(result.size)[2]
    lines = [
        f"{result.label}",
        f"  fg {result.fg.hex()}  bg {result.bg.hex()}  size: {size_label}",
        f"  contrast: {result.ratio:.2f}:1",
        f"  AA ({result.threshold:.1f}:1): {'PASS' if result.aa else 'FAIL'}",
    ]
    if math.isnan(aaa_threshold):
        lines.append("  AAA: not applicable to non-text content")
    else:
        lines.append(f"  AAA ({aaa_threshold:.1f}:1): {'PASS' if result.aaa else 'FAIL'}")
    return "\n".join(lines)


def load_pairs(path: str) -> list[dict]:
    if path == "-":
        data = json.load(sys.stdin)
    else:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("pairs", data.get("colors"))
        if data is None:
            raise ValueError("Pairs file object needs a 'pairs' or 'colors' list")
    if not isinstance(data, list):
        raise TypeError("Pairs file must be a JSON list or an object with a 'pairs' list")
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise TypeError(f"Pair {index} is not an object")
        if "fg" not in item or "bg" not in item:
            raise ValueError(f"Pair {index} needs 'fg' and 'bg'")
    return data


def run_pairs(items: Iterable[dict]) -> list[Result]:
    results = []
    for item in items:
        label = str(item.get("label") or f"{item['fg']} on {item['bg']}")
        size = str(item.get("size", "normal"))
        results.append(
            check_pair(parse_color(str(item["fg"])), parse_color(str(item["bg"])), label, size)
        )
    return results


def self_test() -> int:
    cases = [
        ("black on white", "#000000", "#ffffff", "normal", 21.0, True),
        ("white on black", "#ffffff", "#000000", "normal", 21.0, True),
        ("#767676 on white", "#767676", "#ffffff", "normal", 4.54, True),
        ("#777777 on white", "#777777", "#ffffff", "normal", 4.48, False),
        ("large gray on white", "#777777", "#ffffff", "large", 4.48, True),
        ("blue on white", "#0000ff", "#ffffff", "normal", 8.59, True),
        ("alpha black on white", "#00000080", "#ffffff", "normal", 4.00, False),
    ]
    failures = 0
    for label, fg, bg, size, expected, should_pass in cases:
        result = check_pair(parse_color(fg), parse_color(bg), label, size)
        ratio_ok = abs(result.ratio - expected) < 0.05
        pass_ok = result.aa == should_pass
        status = "ok" if ratio_ok and pass_ok else "FAIL"
        if status == "FAIL":
            failures += 1
        print(
            f"{status}: {label}: {result.ratio:.2f}:1 "
            f"(expected {expected:.2f}, AA={'PASS' if result.aa else 'FAIL'})"
        )
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check WCAG 2.2 contrast for foreground/background color pairs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("fg", nargs="?", help="Foreground color")
    parser.add_argument("bg", nargs="?", help="Background color")
    parser.add_argument("--label", default=None, help="Human-readable pair label")
    parser.add_argument(
        "--size",
        default="normal",
        choices=["normal", "large", "ui"],
        help="Text size or non-text UI (default: normal)",
    )
    parser.add_argument("--pairs", metavar="FILE", help="JSON file of color pairs, or - for stdin")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print failures and a summary",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any pair fails its AA threshold",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in sanity checks")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    try:
        if args.pairs:
            results = run_pairs(load_pairs(args.pairs))
        else:
            if not args.fg or not args.bg:
                parser.error("Provide fg and bg, or use --pairs")
            label = args.label or f"{args.fg} on {args.bg}"
            results = [check_pair(parse_color(args.fg), parse_color(args.bg), label, args.size)]
    except (ValueError, TypeError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.json:
        payload = [
            {
                "label": result.label,
                "fg": result.fg.hex(),
                "bg": result.bg.hex(),
                "size": result.size,
                "ratio": round(result.ratio, 2),
                "aa": result.aa,
                "aaa": None if math.isnan(result.aaa_threshold) else result.aaa,
                "aa_threshold": result.threshold,
            }
            for result in results
        ]
        print(json.dumps(payload, indent=2))
    else:
        for result in results:
            if args.quiet and result.aa:
                continue
            print(format_result(result))
        if args.quiet or len(results) > 1:
            passed = sum(1 for r in results if r.aa)
            failed = len(results) - passed
            print(f"\nSummary: {passed} pass, {failed} fail (AA)")

    if args.check and any(not result.aa for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
