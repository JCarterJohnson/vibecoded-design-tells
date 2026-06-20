# unslop-ui

A Claude skill that strips the cues that make a website read as AI-generated and forces
a deliberate, project-specific choice instead of the model's default. It does not impose
a look or hand you taste. Every rule is weighted by the Reddit analysis in this repo
(~3.2M posts across 47 AI and SaaS subreddits, plus 3,033 comments from 125 threads about
AI sites looking the same).

The point that the first version missed: replacing one default with another is not
unslopping. The 2024 tell was the purple gradient. The 2026 tell is the cream background
plus a serif display font plus sage green (the current Claude/Anthropic house look). This
version flags that new "tasteful default" too, never prescribes a single look, and leans
on a specification-first build mode plus an `unslop-ignore` escape hatch for choices you
made on purpose. See the [animated demo](../demo/demo.html): one prompt becomes four
distinct deliberate designs, all of which pass the scanner.

## What is here

- `SKILL.md` - the skill itself (build mode + audit mode).
- `references/tells.md` - the full ranked catalog: data evidence, a real quote, the
  code-level signatures, and the fix for each tell (including the new cream+serif tell).
- `references/choosing-a-look.md` - a method for making deliberate color/type/layout
  choices, written as a process rather than a prescription (because any prescription
  becomes the next default).
- `scripts/devibe_scan.py` - a standalone scanner (Python standard library only).
- `unslop-ui.skill` - the packaged file for importing into Claude.

## Install the skill

Claude Code:

```bash
unzip unslop-ui.skill -d ~/.claude/skills/
```

claude.ai: upload `unslop-ui.skill` in the skills UI.

Once installed it triggers when you ask Claude to build, review, or de-AI a website,
landing page, or UI component, even if you do not say "vibe-coded."

## Run the scanner without installing anything

```bash
python3 scripts/devibe_scan.py ./your-project        # full report + vibe score
python3 scripts/devibe_scan.py ./your-project --severity high   # only the strongest signals
python3 scripts/devibe_scan.py ./your-project --json            # machine-readable, for CI
```

It scans .html .css .scss .js .jsx .ts .tsx .vue .svelte .astro and prints each finding
with the file, the line, and the fix, plus a project vibe score. The exit code is the
number of high-severity findings, so a CI step can fail on it:

```yaml
- run: python3 skill/scripts/devibe_scan.py ./src --severity high
```

## What it deliberately ignores

Mesh and aurora backgrounds (a keyword artifact in the data), bento grids, and
glassmorphism. They get repeated as memes but barely register as real complaints, so the
scanner leaves them alone. Over-flagging trains people to ignore the tool.
