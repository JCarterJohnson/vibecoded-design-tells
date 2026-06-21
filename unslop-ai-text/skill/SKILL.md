---
name: unslop-text
description: >-
  Strips the cues that make prose read as AI-generated and forces a deliberate, human voice
  instead of the model's default register. It does not write the piece for you and it has no
  preferred style. It removes the cited tells (the em dash, the "it's not just X, it's Y"
  cadence, leftover assistant boilerplate, sycophantic openers, the delve/tapestry/leverage
  diction, listicle scaffolding, the "in conclusion" wrap-up) AND warns against the newer
  over-corrected "trying not to sound like AI" register that swaps one default for another.
  Grounded in a Reddit analysis of 89,239 posts pulled and 7,984 on-topic, across roughly 50
  AI, writing, and SaaS subreddits, of what people actually name as a giveaway. Use whenever
  writing, drafting, editing, rewriting, reviewing, or auditing any prose meant for a reader
  (a post, an email, an essay, an article, a README, marketing copy), and especially when the
  user wants it to sound human rather than AI-generated, or says it "sounds like ChatGPT,"
  "reads like AI," "is too polished," "de-slop this," or "make it sound like me." Trigger even
  if they never say "AI tell."
---

# unslop-text

Read this first, because the most common misunderstanding sinks the whole thing.

**This skill does not write well for you, and it has no house style.** It does two narrow
things. It removes the specific cues that make text read as machine-written, and it forces a
deliberate voice where the model would otherwise reach for its default register. Argument,
taste, and what you actually want to say are still yours. A guardrail is not a writer.

## The trap to avoid (this is the whole point)

The failure mode of every anti-AI-writing effort is replacing one default register with
another. The 2024 tell was the smooth corporate voice: the em dash, "delve," "it's not just
a tool, it's a partner," a bulleted list for everything, a tidy "in conclusion." The 2026
over-correction is its mirror image: clipped three-word sentences, forced lowercase, a
swear dropped in to seem casual, and the truly desperate move of pasting fake typos to beat
a detector. People clock the second one just as fast. One auditor in the data flagged
deliberately-inserted typos ("excyted," "annownce") as themselves a tell.

So this skill never prescribes a voice. It detects the defaults (the smooth one and the
over-corrected one) and asks that whatever replaces them be a real choice you can defend, not
the model's next-most-likely guess and not a costume of "not-AI." The only universal rule is
"write like a specific person who means it," which is the one thing a default never does.

If the writing genuinely calls for a formal register (a legal brief, an academic paper) or
the author genuinely loves the em dash, that is not slop and the skill leaves it alone. A
tell is an *unspecified default*, not a banned word. Honor `unslop-ignore` (see Audit mode)
for anything used on purpose.

## How this differs from an AI detector

Detectors return a probability and a vibe, and they are wrong often enough to ruin a real
writer's day (the data is full of students and non-native speakers falsely flagged). This
skill does not guess whether a machine wrote something. It finds the *specific, cited* tells,
ranked by how often real readers name them, and removes them. It adds three things a detector
does not: a deterministic scanner you can run in CI, a data-grounded ranking so effort goes
where real complaints are, and an explicit warning against the over-corrected register so you
do not launder one default into another.

## Mode 1: Build (the important one)

Most "sounds like AI" outcomes are a specification problem, not a wording problem. An
unspecified prompt gets the median of the training data, and everyone's median is the same
smooth voice. So before drafting anything for a reader, establish the brief. Either pull it
from the user, or if they have not given one, state the choices you are making and why, then
write. Do not silently fall back to the default register.

Establish, concretely:
- **A speaker.** Who is talking, to whom, and why they care. One real person with a stake,
  not "a helpful assistant." This single input does more than every other rule combined. If
  the user has a voice sample (their past writing, a favorite author, a specific register),
  anchor to it. If not, pick a specific named direction (plain-technical, dry-funny,
  reported-and-concrete, blunt-operator) rather than "professional and engaging," which means
  nothing.
- **A claim.** The one thing the piece actually asserts, in a sentence, before you write the
  rest. AI prose reads as empty because it is fluent with nothing to say. If you cannot state
  the claim, there is nothing to unslop yet.
- **A shape that follows the idea.** What the reader needs first, which determines structure.
  This is how you avoid the intro / three-body-paragraphs / conclusion skeleton: the order
  follows the argument, not a template. Most pieces do not need a summary at the end.
- **Contractions and a real rhythm.** Write the way the speaker talks. Vary sentence length
  on purpose; let one run long and the next stop short. Uniform rhythm is the single most
  regex-invisible tell, and it is the one a human ear catches first.

When the user gives no brief and wants you to just write, do not produce one median draft.
Produce a deliberate one and say what you chose, or offer two genuinely distinct voices. The
value is breaking the monoculture, so vary away from the center on purpose.

Then, while writing, avoid the specific tells in [references/tells.md](references/tells.md).
[references/writing-with-intent.md](references/writing-with-intent.md) is a process for making
the voice, claim, and structure choices deliberately, written as a method rather than a
prescription, precisely so it does not become the next default.

## Mode 2: Audit (the guardrail)

When reviewing or cleaning existing prose, or when the user says "does this sound like AI,"
"de-slop this," "make it sound like me," run the scanner first, then fix in priority order.

```bash
python3 scripts/unslop_text_scan.py <path>                 # full report + slop score
python3 scripts/unslop_text_scan.py <path> --severity high # only the strongest signals
python3 scripts/unslop_text_scan.py <path> --json          # machine-readable, for CI
```

It scans .md .markdown .mdx .txt .rst .html and reports each finding with file, line, the
matched text, the data share it carries, and the fix, plus a slop score. The exit code is the
high-severity count, so CI can gate on it. The scanner catches the mechanical tells (the em
dash, the antithesis cadence, assistant boilerplate, the diction memes, the formatting tics).
It cannot see sentence rhythm, sycophancy, hedging, or whether a paragraph says nothing at
length, and those are also what make text read as AI, so after the scan, read the piece aloud
and check those by ear against the catalog.

**How it reads a file.** It lints your running prose. A line you are quoting (it starts with
`>` or sits inside "double quotes") or a literal example you show in `backticks` is skipped,
because flagging a cliche you are quoting in order to discuss it would be wrong. The one
exception is the em dash, which is flagged everywhere, because the rule is simply not to ship
one.

**Respecting intentional choices.** A line containing `unslop-ignore` is skipped. Use it when
a flagged word is a real decision, so the audit stays trustworthy and does not nag about a
register you chose on purpose.

**Fixing well.** Do not fix "delve into the data" by swapping in "dive into the data," which
is just a different tell. Fix it with the plain verb you would actually say ("look at the
data"). A fix that introduces the over-corrected register (choppy fragments, fake typos) is
not a fix.

## What this deliberately does not flag

Grounded in the data, not vibes. The audited sample showed that the generic diction words
(however, comprehensive, crucial, "when it comes to," utilize) light up a keyword pass but
are almost never what a reader actually *cites* as the giveaway. They are mostly the poster's
own ordinary prose. So the scanner weights them low and you should not over-rotate on a single
"however." A formal register itself is fine; only the unchosen default register is the tell.
Over-flagging trains people to ignore the tool, so the scanner stays narrow and ranks by what
real readers name.

## Reporting an audit

Lead with the verdict and the single highest-impact change. Then findings by priority with
file:line and the fix. Close with the slop score and the top three changes. Plain and
specific. The goal is prose that reads like one person who meant it, which is the one thing
the scanner cannot do for them.
