---
name: ghlatex
description: Lint LaTeX math in Markdown so it renders correctly on GitHub and GitHub Pages (GFM + MathJax). Use when writing, editing, reviewing, or fixing Markdown that contains dollar-delimited math (`$...$` or `$$...$$`) destined for GitHub, or when math appears as literal text, raises "Misplaced &", loses spacing, or fails on a GitHub Pages site. Runs the bundled scripts/lint_math.py to detect indented or malformed display blocks, missing blank lines, `\text{x}_{sub}` double-escaping, blocked `\operatorname` and `\phantom`, stripped `\!` and `\,` spacing, unsupported align/equation/gather environments, and bare pipes in inline math.
argument-hint: "[--fix] <file...>"
compatibility: Requires Python 3.8 or later. No third-party packages.
---

# ghlatex — GitHub-safe LaTeX linter

The bundled linter is a regex-based checker, not a TeX parser. It flags the
constructs that GitHub's GFM + MathJax pipeline silently drops or mangles, and
skips fenced code blocks and inline code.

## Arguments

`/ghlatex` accepts an optional `--fix` flag followed by one or more Markdown
file paths:

- `/ghlatex <file> ...` — report only. Run the linter, print every finding and
  the exit status, and do not modify any file.
- `/ghlatex --fix <file> ...` — fix. Run the linter, fix every reported finding
  in the Markdown source, and re-run until clean.

Invocation arguments (Claude Code): `$ARGUMENTS`

GitHub Copilot and other agents may pass the same instructions as natural
language. Infer the mode the same way: `--fix` or an explicit request to
fix/repair means fix mode; lint/check/review means report-only mode. Quote
paths that contain spaces.

`--fix` is a skill-level flag. Strip it before invoking the script; the Python
script itself only reports findings and has no `--fix` option.

## Report-only workflow

1. Choose the Markdown files to check: the paths in the arguments, or the
   Markdown files just edited. Ask only if neither is available.
2. Run the linter with the skill's script:
    - Claude Code: `python3 "${CLAUDE_SKILL_DIR}/scripts/lint_math.py" <file> ...`
    - GitHub Copilot or another agent: `python3 "<skill-directory>/scripts/lint_math.py" <file> ...`,
      where `<skill-directory>` is the directory containing this `SKILL.md`.
3. Print the linter's `path:line: message` output verbatim, followed by the
   exit status. If there are no findings, say so and report exit 0.
4. Do not edit, reformat, or otherwise modify any file in this mode.

## Fix workflow

1. Run the linter on the same targets.
2. Fix every reported finding in the Markdown source using the table below.
3. Re-run until the command exits 0 with no output.
4. Report the files changed, the findings fixed, and the final command with its
   exit status. Never claim a file is clean before an actual clean run. If a
   finding cannot be fixed without guessing the author's intent, stop and
   report it instead.

Exit status: `0` means no findings; `1` means one or more findings. Findings
are printed as `path:line: message`.

## Rule-to-fix table

| Finding                                                         | Fix                                                                                                                 |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Display math must start at column 0                             | Move the `$$` line to column 0, even inside lists or blockquotes.                                                   |
| Missing blank line before or after display math                 | Insert a blank line before the opening `$$` and after the closing `$$`.                                             |
| `$$` is not alone on its line                                   | Put `$$` on its own line; move math text to the lines between delimiters.                                           |
| Unterminated `$$` block                                         | Add the missing closing `$$` on its own line at column 0.                                                           |
| `\text{x}_{sub}`                                                | Rewrite as `\text{x} _{sub}` — a space between `}` and `_`.                                                         |
| Whitespace just inside inline `$`                               | Use `$x$`, not `$ x $`.                                                                                             |
| Inline math contains `\\`                                       | Convert the expression to a `$$` display block.                                                                     |
| Unbalanced inline `$`                                           | Pair the delimiters. For a literal dollar amount, write `&#36;`; the linter counts `\$` as a delimiter.             |
| `\operatorname` or `\phantom`                                   | Rewrite without them. For operators use `\mathop{\mathrm{...}}`; remove `\phantom` and express spacing another way. |
| `\!`                                                            | Remove it; GitHub strips it.                                                                                        |
| `\,`, `\:`, `\;`                                                | Remove them; GitHub renders `\,` as a comma.                                                                        |
| `align`, `align*`, `equation`, `equation*`, `gather`, `gather*` | Use `aligned` inside `$$...$$`, or split into separate display blocks.                                              |
| Bare pipe in inline math                                        | Use `\vert` (or `\mid` for set-builder bars).                                                                       |

## Fix rules

- Preserve mathematical meaning. Change syntax only; never re-derive or
  simplify an expression.
- Keep display math at column 0 even when the surrounding prose is indented in
  a list. If that breaks list grouping, restructure the list rather than
  indenting the math.
- Make the smallest edit. Do not reformat unrelated Markdown or rewrite valid
  math.
- Treat fenced code and inline code as out of scope; the linter ignores them.
- Do not add ignore comments, delete the math, or downgrade the check to make
  it pass.

For rationale and before/after examples, read
`references/github-math-rules.md` relative to this `SKILL.md` when a fix is
ambiguous. In Claude Code the absolute path is
`${CLAUDE_SKILL_DIR}/references/github-math-rules.md`.
