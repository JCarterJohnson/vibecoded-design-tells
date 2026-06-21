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
things. It removes the specific cues that make text read as machine-written, and, where the
text reads as AI because nobody ever chose a voice, it forces a deliberate one. Argument,
taste, and what you actually want to say are still yours. A guardrail is not a writer.

**Most of the work is the first thing, and most of the first thing is mechanical.** This is
where text differs from a website. A UI has no correct look, so its skill can only ever say
"make a deliberate choice." Prose is not like that. Nearly every cited tell has a plain
correct fix that needs no taste at all: the em dash becomes a comma or a period, `delve into`
becomes `look at`, the sycophantic opener gets cut, the `as an AI` boilerplate gets deleted,
the "in conclusion" recap goes. These are not style calls and there is no voice to invent.
You remove the tic and write the plain sentence a person would write. So lead with the plain
fix. Reserve the deliberate-voice work below for the genuinely stylistic choices, and for
prose that reads as empty because nobody decided what it was.

## The trap to avoid (this is the whole point)

The failure mode of every anti-AI-writing effort is replacing one default register with
another. The 2024 tell was the smooth corporate voice: the em dash, "delve," "it's not just
a tool, it's a partner," a bulleted list for everything, a tidy "in conclusion." The 2026
over-correction is its mirror image, the "trying not to sound like AI" voice: staccato
three-word fragments, forced lowercase, a "here's the thing" or "look" cold open, a swear
dropped in to seem casual, and the truly desperate move of pasting fake typos to beat a
detector. People clock the second one just as fast. One auditor in the data flagged
deliberately-inserted typos ("excyted," "annownce") as themselves a tell.

**Treat the over-corrected register as its own tell, the way a cream-and-serif redesign is
its own tell.** The most common way to fail this skill is to apply its rules too hard and
land in that second voice. Watch three moves in particular. Conspicuous em-dash avoidance:
the fix for a dash is a comma or a period, not an ellipsis, not a colon, and not a visibly
contorted sentence that bends around the gap, because the bending is as legible as the dash
was. Manufactured casualness: a "honestly," a lowercase "i," a "lol" bolted onto writing
that is otherwise formal reads as costume, not voice. And rhythm that is uniform in a new
way: all-short sentences are as mechanical as all-medium ones. Evenness is the tell, whichever
length it settles on. The over-corrected register is documented as a catalog entry in
[references/tells.md](references/tells.md) so the human pass checks for it by name.

So for the stylistic calls this skill never prescribes a voice. It detects the defaults (the
smooth one and the over-corrected one) and asks that whatever replaces them be a real choice
you can defend, not the model's next-most-likely guess and not a costume of "not-AI." The one
universal rule is "write like a specific person who means it," which is the thing a default,
old or new, never does.

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

**The one move that matters most is pinning a voice, and the four registers are how you pin
it.** This is the text analog of the UI skill's reference site: the single anchor that, once
chosen, settles a hundred small decisions and keeps you off the model's median. Unslopping AI
text usually means injecting a deliberate voice that was never there, and "write in a human
voice" is too vague to act on, the same way "make it modern" is too vague for a designer. So
first decide which of four registers the piece is in, because that decides what "plain" even
looks like here:

- **Register A, casual.** Texts, DMs, personal posts. Contractions, fragments, slang, first
  person, the occasional one-line paragraph. Here a dropped subject is native, not a costume.
- **Register B, conversational-professional.** Work email, Slack, a team update, a changelog.
  Plain and direct, contractions, light warmth, no throat-clearing. Most workplace writing.
- **Register C, expository.** Essays, articles, READMEs, blog and forum posts. The default for
  "a piece for a reader": a clear argument, varied rhythm, a point of view, paragraphs over
  bullets. This is where most unslopping happens.
- **Register D, formal.** Papers, briefs, specs, official docs. No contractions, structured,
  impersonal, sourced. Formality here is the correct register, not a tell.

Pinning the register is also what stops the over-correction. A contraction is right in A, B,
and C and wrong in D; a fragment is native in A and a tell in D; a "lol" is voice in A and
costume in C. Most "sounds like AI" prose is Register C written as the model's median C. Pin
the register, then anchor to a real speaker inside it.

Establish, concretely:
- **A speaker, inside that register.** Who is talking, to whom, and why they care. One real
  person with a stake, not "a helpful assistant." Register plus speaker is the voice, and the
  voice does more than every other rule combined. If the user has a sample (their past
  writing, a favorite author), anchor to it. If not, pick a specific named direction within
  the register (plain-technical, dry-funny, reported-and-concrete, blunt-operator) rather than
  "professional and engaging," which means nothing.
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
matched text, the data share it carries, and the fix, plus a slop score and a density (slop
weight per 1,000 words). The exit code is the high-severity count, so CI can gate on it.

**Be honest about what this scanner is.** For text it is a thin lexical filter, much thinner
than the UI scanner is for a website. A CSS file wears most of its tells on the surface (the
default color, the default font, the gradient), so catching the mechanical ones catches most
of the problem. Prose does not. The highest-value tells are structural, and a regex cannot
see any of them: uniform sentence rhythm (cited second-most of all, more than any word),
sycophancy and the yes-man tone (cited fourth), the rule of three, the over-formal register,
and a paragraph that is fluent and says nothing. The scanner catches the surface tics: the em
dash, the antithesis cadence, the assistant boilerplate, the diction memes, the formatting
tics. Useful, but the minority of what readers actually name.

So a clean scan does not mean the writing reads as human. It means the lexical layer is clean.
A green check is not a verdict. The real signal is the structural catalog in
[references/tells.md](references/tells.md) read against the piece, plus the density number,
not the pass/fail. After every scan, read the draft aloud and check the Part B structural
tells by ear. That pass is the work; the scanner just clears the easy stuff first.

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
(`however`, `comprehensive`, `crucial`, `when it comes to`, `utilize`) light up a keyword pass
but are almost never what a reader actually *cites* as the giveaway. They are mostly the
poster's own ordinary prose. So the scanner weights them low and you should not over-rotate on
a single `however`. A formal register itself is fine; only the unchosen default register is
the tell. Over-flagging trains people to ignore the tool, so the scanner stays narrow and
ranks by what real readers name.

**Weight by density and concentration, not by lone hits.** Humans write `comprehensive` and
`delve` sometimes. Six of them in a 200-word paragraph is slop; six scattered across a
5,000-word essay is just how the person writes. That is why the report leads with a density
number and the verdict is concentration-aware: a single low-tier or mid-tier hit reads as
"mostly clean," and a sparse scatter across a long, otherwise-clean piece will not be escalated
to "some." A lone `comprehensive`, a lone `delve`, a lone `however` is never on its own a tell.
The two absolute tells are the exception, scanned everywhere and counted on a single instance:
the em dash, and leftover assistant boilerplate (`as an AI language model`). One of either is a
real signal regardless of how long or clean the rest is. Everything else, judge by how thickly
it clusters.

## Reporting an audit

Lead with the verdict and the single highest-impact change. Then findings by priority with
file:line and the fix. Close with the slop score and the top three changes. Plain and
specific. The goal is prose that reads like one person who meant it, which is the one thing
the scanner cannot do for them.
