# ghlatex

A portable agent skill for Claude Code and GitHub Copilot that lints LaTeX in
Markdown for GitHub's math renderer.

GitHub's GFM + MathJax pipeline silently drops or mangles some LaTeX. This
linter catches those constructs before you push. It is a standalone
repackaging of the `lint_math.py` tool from the gitbook project.

## What it checks

- Display math must start at column 0, be alone on its line, and have blank
  lines before and after.
- `\text{x}_{sub}` must be written as `\text{x} _{sub}`.
- Inline math must stay on one line, have no whitespace inside the delimiters,
  and contain no `\\`.
- `\operatorname` and `\phantom` are blocked. `\!` is stripped and `\,` renders
  as a comma, so `\,`, `\:`, `\;`, and `\!` must go.
- `align`, `equation`, and `gather` environments are unsupported; use
  `aligned` or separate display blocks.
- Bare pipes in inline math must become `\vert` or `\mid`.

All snippets above are inline code, so this README passes its own linter. The
full rationale and before/after examples are in
[references/github-math-rules.md](references/github-math-rules.md).

## Layout

```text
ghlatex/
├── SKILL.md                        # skill definition (frontmatter + workflow)
├── scripts/
│   └── lint_math.py                # the linter
├── references/
│   └── github-math-rules.md        # rule rationale and examples
├── README.md
└── .gitignore
```

The repository root is the skill directory, so cloning it into any skills
location works as-is. Keep the folder name `ghlatex` to match the skill name.

## Requirements

Python 3.8 or later. No third-party packages.

## Install

### Claude Code

Personal skills:

```bash
git clone <repo-url> ~/.claude/skills/ghlatex
```

Project skills:

```bash
git clone <repo-url> .claude/skills/ghlatex
```

Claude Code loads the skill from its description and invokes it automatically
when a request matches. You can also invoke it explicitly as `/ghlatex`.

### GitHub Copilot

Copilot reads project skills from `.github/skills`, `.claude/skills`, and
`.agents/skills`, and personal skills from `~/.copilot/skills` and
`~/.agents/skills`.

Project, Copilot-only location:

```bash
git clone <repo-url> .github/skills/ghlatex
```

Project, shared by both tools:

```bash
git clone <repo-url> .claude/skills/ghlatex
```

Personal:

```bash
git clone <repo-url> ~/.copilot/skills/ghlatex
```

Copilot activates the skill when a request matches its description, and can
invoke it manually as `/ghlatex` where manual invocation is supported.

## Command-line use

The linter works on its own, without an agent:

```bash
python3 scripts/lint_math.py docs/*.md README.md
```

With no arguments it checks the `*.md` files in the current directory. Each
finding is printed as `path:line: message`. Exit status is `0` when clean and
`1` when there are findings.

To check a directory tree:

```bash
find docs -name '*.md' -print0 | xargs -0 python3 scripts/lint_math.py
```

`--fix` is a skill-level flag: the agent applies the edits. The Python script
itself only reports findings and does not accept `--fix`.

## Use as a skill

Two slash-command modes are available:

```text
/ghlatex <file...>          # report findings only; no edits
/ghlatex --fix <file...>    # apply fixes, then re-run until clean
```

- Report-only mode prints the linter's `path:line: message` output and the
  exit status. It never modifies files.
- Fix mode applies the fixes documented in `SKILL.md`, re-runs the linter, and
  reports the changed files, the findings fixed, and the final exit status.

Natural-language requests work too and map to the same modes:

- "Lint the math in `docs/chapter-1.md` for GitHub." (report only)
- "My equations render as literal text on GitHub Pages; fix the Markdown." (fix)
- "Check these notes for GitHub-incompatible LaTeX before I push." (report only)

Claude Code passes slash-command arguments through. In agents that do not
support skill arguments, describe the mode and paths in the request. Quote
paths that contain spaces.

## GitHub Pages

Math on github.com renders natively. A Jekyll site on GitHub Pages does not
enable math by default, so the site needs MathJax or KaTeX configured. This
linter checks the Markdown source; it does not verify the deployed page's
renderer configuration.

## Limits

The linter is regex-based and deliberately narrow. It skips fenced code blocks
and inline code, does not validate TeX syntax generally, and cannot confirm how
GitHub will render an expression. Preview on GitHub when a result is
surprising.

## Provenance

`scripts/lint_math.py` is taken from the gitbook project's docs tooling. Its
rules were derived from GitHub's GFM + MathJax behavior.
