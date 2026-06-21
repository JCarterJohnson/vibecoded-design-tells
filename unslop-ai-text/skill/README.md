# unslop-text

A Claude skill that strips the cues that make prose read as AI-generated and forces a
deliberate, human voice instead of the model's default register. It does not write the piece
for you or hand you a style. Every rule is weighted by the Reddit analysis in this repo
(89,239 posts pulled, 7,984 on-topic, across roughly 50 AI, writing, and SaaS subreddits,
2021 to 2026, plus a 600-post hand-audited sample).

The point that the naive version misses: replacing one default with another is not unslopping.
The 2024 tell was the smooth corporate voice (the em dash, `delve`, the `not just X, it's Y`
cadence). The 2026 over-correction is the clipped, forced-casual, fake-typo "anti-AI" voice,
and readers clock it just as fast. This skill flags the smooth defaults, warns against the
over-corrected ones, never prescribes a voice, and leans on a specification-first build mode
plus an `unslop-ignore` escape hatch for choices you made on purpose.

## What is here

- `SKILL.md` - the skill itself (build mode + audit mode).
- `references/tells.md` - the full ranked catalog: data evidence (cited share and keyword
  share), a real quote from the threads, the literal text the scanner keys on, and the fix for
  each tell, including a Part B for the structural tells a regex cannot see.
- `references/writing-with-intent.md` - a method for making deliberate voice, claim, and
  structure choices, written as a process rather than a prescription (because any prescription
  becomes the next default).
- `scripts/unslop_text_scan.py` - a standalone scanner (Python standard library only).
- `unslop-text.skill` - the packaged file for importing into Claude.

## Install the skill

Claude Code:

```bash
unzip unslop-text.skill -d ~/.claude/skills/
```

claude.ai: upload `unslop-text.skill` in the skills UI.

Once installed it triggers when you ask Claude to write, edit, or de-AI any prose, even if you
do not say "AI tell."

## Run the scanner without installing anything

```bash
python3 scripts/unslop_text_scan.py ./draft.md          # full report + slop score
python3 scripts/unslop_text_scan.py ./draft.md --severity high   # only the strongest signals
python3 scripts/unslop_text_scan.py ./draft.md --json            # machine-readable, for CI
```

It scans .md .markdown .mdx .txt .rst .html and prints each finding with the file, the line,
the matched text, the data share it carries, and the fix, plus a slop score. The exit code is
the number of high-severity findings, so a CI step can fail on it:

```yaml
- run: python3 skill/scripts/unslop_text_scan.py ./content --severity high
```

It lints your running prose: a line you are quoting (it starts with `>` or sits inside "double
quotes") or a literal example in `backticks` is skipped, so the scanner does not flag a cliche
you are quoting in order to discuss it. The em dash is the one exception, flagged everywhere.

## What it deliberately ignores

The generic diction the keyword pass over-counts but real readers almost never cite: a lone
"however," "comprehensive," "robust," "when it comes to." They are mostly the writer's own
ordinary prose, so the scanner weights them low. The structural tells (uniform rhythm,
sycophancy, saying nothing at length) are also not flagged, because a regex cannot see them;
they are documented in `references/tells.md` for a human pass. Over-flagging trains writers to
ignore the tool, so the scanner stays narrow and ranks by what real readers name.
