# unslop-code

A Claude skill that strips the tells that make source code read as AI-generated and forces code
that fits the project instead of the model's default average. It does not write the code for you
or impose a style. Every rule is weighted by the Reddit analysis in this folder (11,906 posts +
11,306 comments across 55 AI, coding, and SaaS subreddits, classified by an LLM into 19 tells
and adversarially verified quote by quote).

The point that a linter misses: the loudest tells are not cosmetic. Stripping emoji and fixing a
bare `except` is the easy part. The verified ranking is dominated by boilerplate / tutorial-shaped
code (18.6%), hallucinated APIs (11.2%), and over-engineering (7.8%), none of which a regex can
see. This skill flags the mechanical surface tells AND tells you, explicitly, where the scanner is
blind so you read for the structural ones by hand.

Two axes run through the whole skill. **Severity** is how loudly a finding reads as AI; **class**
is whether it is a bug or a cosmetic. A swallowed error or a hallucinated API is a bug you fix
because the code is wrong; an emoji is cosmetic. And because code, unlike prose or a design, can
be run, the audit leans on that first: build, type-check, and lint to catch the hallucinated
calls, then the scanner for the surface tells, then a human read for shape and repo-fit.

## What is here

- `SKILL.md` - the skill itself (build mode + audit mode).
- `references/tells.md` - the full ranked catalog: verified and raw share, a real quote, the
  code-level signature, and the fix for each tell, split into Part A (what the scanner catches)
  and Part B (the louder structural tells a regex cannot see). Every tell is tagged bug /
  substance / cosmetic, and a language-coverage section says which tells are universal versus
  language-specific.
- `references/fitting-the-codebase.md` - a method for making generated code deliberate and
  project-specific, built around the data's single most-repeated fix: make it follow the existing
  code instead of guessing the average.
- `scripts/unslop_code_scan.py` - a standalone multi-language scanner (Python standard library
  only).
- `unslop-code.skill` - the packaged file for importing into Claude.

## Install the skill

Claude Code:

```bash
unzip unslop-code.skill -d ~/.claude/skills/
```

claude.ai: upload `unslop-code.skill` in the skills UI.

Once installed it triggers when you ask Claude to write, review, or de-AI code, even if you do not
say "AI tell."

## Run the scanner without installing anything

```bash
python3 scripts/unslop_code_scan.py ./src                 # full report + slop score
python3 scripts/unslop_code_scan.py ./src --severity high # only the strongest signals
python3 scripts/unslop_code_scan.py ./src --json          # machine-readable, for CI
```

It scans Python, JS/TS, Java, Go, Rust, Ruby, PHP, C/C++, C#, and more, and prints each finding
with the file, the line, the matched text, its severity, its class (bug or cosmetic), the data
share it carries, and the fix, plus a slop score. The exit code is the number of high-severity
findings, so a CI step can fail on it:

```yaml
- run: python3 skill/scripts/unslop_code_scan.py ./src --severity high
```

## What it deliberately ignores

The complaints that did not survive verification: left-in debug logging (rejected outright,
precision ~0%), reinventing the wheel (mostly misattributed), and over-defensive validation (half
the complaints were about the opposite). And it does not flag the structural tells (boilerplate,
hallucinated APIs, over-engineering, repo fit) because a regex cannot judge them; those are
documented in `references/tells.md` for a human pass. Over-flagging trains people to ignore the
tool, so the scanner stays narrow and ranks by verified share.
