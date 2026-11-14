#!/usr/bin/env python3
"""Lint Markdown for LaTeX that GitHub's renderer silently drops.

Usage: python3 scripts/lint_math.py [FILE ...]   (default: *.md in the current directory)

The rules come from GitHub's actual GFM + MathJax pipeline:
  1. A `$$` block must start at column 0. GitHub renders a display block that
     is indented inside a list item as literal text, not math.
  2. A `$$` line must be alone on its line, with blank lines before and after.
  3. Write `\\text{x} _{sub}`, not `\\text{x}_{sub}`. Two `{...}_{...}` groups on
     one line make GitHub HTML-escape the block twice, so MathJax receives
     `&amp;=` and fails with "Misplaced &".
  4. Inline math must fit on one line, have no whitespace just inside the `$`
     delimiters, and contain no `\\\\` (GitHub rejects the whole expression).
  5. GitHub blocks `\\operatorname` and `\\phantom`; use `\\mathop{\\mathrm{...}}`.
  6. GitHub strips `\\!` and renders `\\,` as a comma; remove `\\,`, `\\:`, `\\;` and `\\!`.
  7. Avoid bare `|` in inline math; use `\\vert`. `align`, `align*`, `equation`
     and `gather` environments are unsupported; use `aligned` or separate blocks.
"""

import glob
import re
import sys

DISPLAY_LINE = re.compile(r"^(\s*)\$\$\s*$")
INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)([^$\n]*?)(?<!\$)\$(?!\$)")
INLINE_CODE = re.compile(r"`[^`]*`")
FENCE = re.compile(r"^\s*(```|~~~)")
TEXT_SUBSCRIPT = re.compile(r"\\(?:text|mathrm)\{[^{}]*\}_")
BLOCKED_MACROS = re.compile(r"\\(?:operatorname|phantom)\b")
BANG = re.compile(r"\\!")
SPACING = re.compile(r"\\[,;:]")
UNSUPPORTED_ENV = re.compile(r"\\begin\{(?:align\*?|equation\*?|gather\*?)\}")

RULES = {
    "indent": "display math must start at column 0; GitHub drops indented blocks",
    "blank_before": "display math must be preceded by a blank line",
    "blank_after": "display math must be followed by a blank line",
    "alone": "$$ must be alone on its line",
    "unterminated": "unterminated $$ block",
    "subscript": r"write \text{x} _{sub}, not \text{x}_{sub}; GitHub double-escapes the latter",
    "inline_space": "no whitespace just inside an inline $...$ delimiter",
    "inline_newline": r"inline math cannot contain \\; use a $$ display block",
    "inline_unbalanced": "unbalanced inline $ delimiter",
    "blocked_macro": r"GitHub does not allow \operatorname or \phantom; use \mathop{\mathrm{...}}",
    "bang": r"GitHub strips \!; remove it",
    "spacing": r"GitHub renders \, as a comma; remove \, \: \; spacing commands",
    "unsupported_env": r"GitHub does not support align/equation/gather; use aligned or separate blocks",
    "bare_pipe": r"bare | in inline math breaks GitHub rendering; use \vert",
}


def check_math(expr, inline):
    errors = []
    if BLOCKED_MACROS.search(expr):
        errors.append(RULES["blocked_macro"])
    if BANG.search(expr):
        errors.append(RULES["bang"])
    if SPACING.search(expr):
        errors.append(RULES["spacing"])
    if UNSUPPORTED_ENV.search(expr):
        errors.append(RULES["unsupported_env"])
    if inline:
        cleaned = re.sub(
            r"\\left\||\\right\||\\vert\b|\\Vert\b|\\mid\b|\\lvert\b|\\rvert\b|\\\|",
            "",
            expr,
        )
        if "|" in cleaned:
            errors.append(RULES["bare_pipe"])
    return errors


def lint(path):
    errors = []
    with open(path, encoding="utf-8") as source:
        lines = source.read().splitlines()
    in_fence = False
    in_display = False

    for i, raw in enumerate(lines):
        lineno = i + 1
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        line = INLINE_CODE.sub("", raw)

        if in_display:
            if TEXT_SUBSCRIPT.search(line):
                errors.append((lineno, RULES["subscript"]))
            for message in check_math(line, inline=False):
                errors.append((lineno, message))
            match = DISPLAY_LINE.match(line)
            if match:
                in_display = False
                if match.group(1):
                    errors.append((lineno, RULES["indent"]))
                if i + 1 < len(lines) and lines[i + 1].strip():
                    errors.append((lineno, RULES["blank_after"]))
            continue

        match = DISPLAY_LINE.match(line)
        if match:
            if match.group(1):
                errors.append((lineno, RULES["indent"]))
            if i == 0 or lines[i - 1].strip():
                errors.append((lineno, RULES["blank_before"]))
            in_display = True
            continue

        if "$$" in line:
            errors.append((lineno, RULES["alone"]))
            continue

        if TEXT_SUBSCRIPT.search(line):
            errors.append((lineno, RULES["subscript"]))

        pairs = list(INLINE_MATH.finditer(line))
        if INLINE_MATH.sub("", line).count("$"):
            errors.append((lineno, RULES["inline_unbalanced"]))
        for pair in pairs:
            expr = pair.group(1)
            if expr != expr.strip():
                errors.append((lineno, RULES["inline_space"]))
            if "\\\\" in expr:
                errors.append((lineno, RULES["inline_newline"]))
            for message in check_math(expr, inline=True):
                errors.append((lineno, message))

    if in_display:
        errors.append((len(lines), RULES["unterminated"]))
    return errors


def main():
    paths = sys.argv[1:]
    if not paths:
        paths = sorted(glob.glob("*.md"))

    failures = 0
    for path in paths:
        for lineno, message in lint(path):
            print(f"{path}:{lineno}: {message}")
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
