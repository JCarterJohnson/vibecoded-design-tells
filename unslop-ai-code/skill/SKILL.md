---
name: unslop-code
description: >-
  Strips the tells that make source code read as AI-generated and forces code that fits the
  project instead of the model's default average. It does not write the code for you and it
  has no preferred style. It removes the surface tells (leftover chat artifacts, placeholder
  comments, emoji, swallowed errors, narrating comments, generic placeholder names like
  process_data) AND points you at the structural tells a linter passes: boilerplate /
  tutorial-shaped code, hallucinated APIs, over-engineering, and code that ignores the
  surrounding codebase. Grounded in a Reddit analysis of 11,906 posts and 11,306 comments
  across 55 AI, coding, and SaaS subreddits of what developers actually name as a giveaway.
  Use whenever writing, generating, reviewing, refactoring, or auditing code, and especially
  when the user wants it to not look AI-written or vibe-coded, says it "looks AI-generated,"
  "reads like a tutorial," "is too generic," or "de-slop this." Trigger even if they never say
  "AI tell."
---

# unslop-code

Read this first, because the most common misunderstanding sinks the whole thing.

**This skill does not write good code for you, and it has no house style.** It does two narrow
things. It removes the specific surface cues that make code read as machine-generated, and it
points you at the deeper tells (the ones that ship bugs) that no scanner can catch. Whether the
code is correct, well-factored, and right for the problem is still your call. A guardrail is not
an engineer.

## The trap to avoid (this is the whole point)

The surface tells are the cheap part. You can strip every emoji, delete every `// rest of your
code` stub, and fix every bare `except`, and still ship a file that is tutorial-shaped, calls a
made-up API, over-engineers a simple task, and ignores how the rest of the repo works. Those
are the loudest tells in the data, and a clean lint hides them. The verified ranking is blunt
about it: boilerplate (18.6%), hallucinated APIs (11.2%), and over-engineering (7.8%) tower
over the cosmetic stuff (emoji 3.9%, verbose names 0.4%). So removing surface tells is the easy
40% of the job, not the job. Do not mistake a clean scan for clean code.

## How this differs from a linter or a formatter

A linter enforces style and catches a fixed set of bugs; a formatter makes everything uniform,
which is itself one of the tells. This skill is different. It finds the specific, cited tells
that developers actually use to spot AI code, ranked by how often they name them, and it is
explicit that the highest-ranked ones are structural and need a human or a compiler. Run your
linter, run this, and then read the diff for the things neither tool can see.

## Mode 1: Build (the important one)

Most "looks AI-written" outcomes are a specification problem, not a style problem. An
unspecified prompt gets the average of public code, and the average is the tutorial. So before
generating, establish the brief. Either pull it from the user, or state what you are assuming
and why, then proceed. Do not generate against a blank slate.

Establish, concretely:
- **The surrounding code.** Give the model the files it will sit next to: the module it
  extends, the nearest sibling that does something similar, and the project's conventions (how
  errors are handled, how things are logged, the structure, the naming vocabulary). This single
  input does more than every other rule combined. The most repeated fix in the entire dataset
  was "make it follow the existing code instead of guessing the average."
- **The real requirement.** What the code actually has to do, including the failure modes and
  the real integration, not the demo. Vague requirements get the sample-app shape: one page,
  dummy data, no backend.
- **Calls that exist.** Generated code invents plausible APIs. Plan to run it and check every
  import and method against real docs, because hallucinated calls are the tell that bites in
  production.

[references/tells.md](references/tells.md) is the full ranked catalog. [references/fitting-the-codebase.md](references/fitting-the-codebase.md)
is the method for making the code deliberate and project-specific, written as a process rather
than a prescription, precisely so it does not become the next default.

## Mode 2: Audit (the guardrail)

When reviewing or cleaning existing code, or when the user says "does this look AI-written,"
"de-slop this," run the scanner first, then fix in priority order.

```bash
python3 scripts/unslop_code_scan.py <path>                 # full report + slop score
python3 scripts/unslop_code_scan.py <path> --severity high # only the strongest signals
python3 scripts/unslop_code_scan.py <path> --json          # machine-readable, for CI
```

It scans Python, JS/TS, Java, Go, Rust, Ruby, PHP, C/C++, C#, and more, reports each finding
with file, line, the matched text, the data share it carries, and the fix, and gives a slop
score. The exit code is the high-severity count, so CI can gate on it. The scanner catches the
mechanical tells (chat artifacts, placeholder comments, emoji, swallowed errors, narrating
comments, generic names). It cannot see boilerplate shape, hallucinated APIs, over-engineering,
or whether the code matches the repo, and those are the loudest tells, so after the scan, read
the diff for those by hand against references/tells.md.

**Respecting intentional choices.** A line containing `unslop-ignore` is skipped. Use it when a
flagged construct is a real decision (a broad catch at a boundary, an emoji in a CLI banner), so
the audit stays trustworthy.

**Fixing well.** Do not "fix" `process_data()` by renaming it `processDataFunction()`, which is
just a different tell. Name it for what it does. A fix that adds a new unchosen default is not a
fix.

## What this deliberately does not flag

Grounded in the data, not vibes. Three popular complaints did not survive verification, so the
scanner leaves them alone: left-in debug logging (rejected outright, precision ~0%, the tagged
comments were all workflow opinions), reinventing the wheel (mostly misattributed), and
over-defensive validation (half the complaints were about the opposite, code with no validation
at all). Over-flagging trains people to ignore the tool, so the scanner stays narrow and ranks
by verified share.

## Reporting an audit

Lead with the verdict and the single highest-impact change. Then findings by priority with
file:line and the fix. Close with the slop score and the top three changes, and a reminder that
the structural tells (boilerplate, hallucinated APIs, repo fit) still need eyes. Plain and
specific. The goal is code that looks like it belongs in this project, which is the one thing
the scanner cannot check for you.
