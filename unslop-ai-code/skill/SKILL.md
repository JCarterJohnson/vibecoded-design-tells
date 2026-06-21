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

## Two kinds of tell: bugs and cosmetics

Sort every tell by one question before any other: is the code wrong, or does it just look
machine-made?

- **Bugs.** Swallowed and over-broad exception handling eats the failure you needed. A
  hallucinated or nonexistent API will not run. A `// rest of your code` stub means the file is
  unfinished. These are not style. Fix them because the code is broken, the same way you would
  fix any bug, whether or not anyone ever suspected AI.
- **Cosmetics.** Emoji, leftover chat artifacts, narrating comments, generic and over-verbose
  names. These are the model's chat voice leaking into the file. Worth removing because they
  read as AI, but nothing breaks if one survives. This is the lighter class.

The scanner reports both, tagged with the class; the catalog tags every tell the same way. The
point of the split: do not spend an audit polishing cosmetics while a swallowed error or a
made-up call ships. (There is a third class, *substance*: tutorial shape, over-engineering, and
repo mismatch. It is wrong for the job rather than locally broken, and needs a human reading the
diff. See references/tells.md.)

## The over-correction trap

Told to "write clean code" or "make this not look AI," a model does not become restrained; it
over-corrects. It adds defensive checks for cases that cannot happen, a type annotation on every
local, a comment on every block, an abstraction for a thing with one caller. It is trying to
look senior, and trying-to-look-senior is itself a tell. The fix is not more polish; it is the
same anchor as everything else here: match the level the surrounding code actually operates at.
Do not add a check, a type, a comment, or a layer the neighboring code would not have.

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
is the method for making the code fit the project instead of the model's average, written as a
process rather than a prescription, so it does not become the next default.

## Mode 2: Audit (the guardrail)

When reviewing or cleaning existing code, or when the user says "does this look AI-written" or
"de-slop this," work in this order. The order matters: the scanner is a regex and is blind to
the bug-class tells, so it is the second pass, not the first.

**1. Run what only code allows.** Unlike prose or a design, code can be executed, and that is
your strongest tool. This step catches the bug-class structural tells, hallucinated APIs above
all, which no regex can see. Build it, type-check it, lint it, and resolve its imports and calls
against real docs:

- Python: `python -m py_compile <files>`, `ruff check` or `pyflakes`, `mypy`, and actually
  import the module so a missing dependency fails loudly.
- JS / TS: `tsc --noEmit`, `eslint`, `node --check`, with a real install so a made-up package errors.
- Go: `go build ./...`, `go vet ./...`.
- Rust: `cargo check`, `cargo clippy`.

If the code will not build, or a call resolves to nothing, you have found the loudest tell in
the data before reading a line. Fix that first.

**2. Run the scanner** for the mechanical surface tells.

```bash
python3 scripts/unslop_code_scan.py <path>                 # full report + slop score
python3 scripts/unslop_code_scan.py <path> --severity high # only the strongest signals
python3 scripts/unslop_code_scan.py <path> --json          # machine-readable, for CI
```

It scans Python, JS/TS, Java, Go, Rust, Ruby, PHP, C/C++, C#, and more; reports each finding
with file, line, the matched text, the severity, the class (bug or cosmetic), the data share it
carries, and the fix; and gives a slop score. The exit code is the high-severity count, so CI
can gate on it. Severity is how loudly a finding reads as AI; class is whether it is broken. Fix
every bug-class finding regardless of severity.

**3. Read the diff for what neither step can see:** tutorial shape, over-engineering, and
whether the code matches the repo. These are the substance tells in references/tells.md, and
they are the loudest in the data.

**Respecting intentional choices.** A line containing `unslop-ignore` is skipped. Use it when a
flagged construct is a real decision (a broad catch at a boundary, an emoji in a CLI banner), so
the audit stays trustworthy.

**Fixing well: the anchor is correct, and fits this codebase.** Do not "fix" `process_data()`
by renaming it `processDataFunction()`, which is just a different tell. Name it for what it does,
the way the rest of the repo names things. Code has far less aesthetic latitude than prose or a
UI: there is rarely a "tasteful choice" to make here, only "is it correct, and does it match
what is already in this project." A fix that swaps the model's default for your own invented
default is not a fix; a fix that makes the line look like the code around it is.

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
