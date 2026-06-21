# Writing with intent (a method, not a style)

This file does not give you a voice to copy. Any specific style, repeated, becomes the next
default and the next tell. The smooth corporate voice was the 2024 default; the clipped,
lowercase, swear-here-to-seem-real voice is the 2026 over-correction, and it reads as
machine-trying-not-to-look-like-a-machine just as fast. So this file gives you a way to
decide what the writing is, not a thing to imitate.

The goal is one outcome: prose where every major choice has a reason specific to this piece
and this writer. That is the single property a default register can never have, and it is what
makes writing stop reading as machine-made.

## Start from a voice: pin a register, then a speaker

This is the core mechanism, the text analog of the UI skill's reference site. A website's most
useful single input is one real site to design against; prose's is one real voice to write in.
Most AI text reads as AI because no one supplied that input, so the model wrote the median.
Unslopping it usually means injecting a deliberate voice that was never there, and supplying
that voice is most of the job.

Pin it in two steps. First the register, because it sets what "plain" means and what counts as
a tell:

- **A, casual** (texts, DMs, personal posts): contractions, fragments, slang, first person.
- **B, conversational-professional** (work email, Slack, updates, changelogs): plain, direct,
  contractions, light warmth, no throat-clearing.
- **C, expository** (essays, articles, READMEs, posts for a reader): a clear argument, varied
  rhythm, a point of view, paragraphs over bullets. The default, and where most unslopping
  happens.
- **D, formal** (papers, briefs, specs): no contractions, structured, impersonal, sourced.
  Formality here is correct, not a tell.

The register is also the guard against over-correcting. A fragment is native in A and a tell in
D; a contraction is right in A through C and wrong in D; a swear is voice in A and costume in C.
Decide which register the piece is in before deciding anything else, then hold the line on it.

Then a speaker inside it. If the user has past writing, a favorite author, a sample they like,
anchor to it: the sentence length, the vocabulary, the level of formality, how blunt they are.
If they cannot point to one, that is the conversation to have before drafting. If you must
choose, pick a *named direction* and commit to it, rather than "professional and engaging": for
example plain-technical (a senior engineer explaining a bug), dry and funny, reported and
concrete (a beat journalist), blunt operator, warm and personal. Register plus speaker is the
voice, and it is how a human injects a point of view into a model that otherwise averages.

## The claim

Before writing the body, state the one thing the piece asserts, in a sentence. AI prose reads
as empty because it is fluent with nothing to say, so this is the test that catches the deepest
tell early. If you cannot write the claim in a sentence, there is nothing to write yet, and no
amount of unslopping will fix a piece that says nothing. Every paragraph should earn its place
against that claim. If one could be cut with nothing lost, cut it.

## Structure

The order follows the argument, not a template. Decide what the reader needs first and let that
set the sections. This is how you avoid the intro / three-even-body-paragraphs / "in
conclusion" skeleton: that shape appears when structure is chosen by default instead of by
purpose. Most pieces do not need a summary at the end; if the reader needs one to follow it,
the piece is too long. Reserve bullet lists for genuinely list-like content. Argument lives in
paragraphs.

## Rhythm and diction

Vary sentence length on purpose. Let one run long and the next stop in three words. Uniform,
evenly-paced sentences are the single most keyword-invisible tell, and the one an ear catches
first, so read the draft aloud. Use contractions and the plain word: `use` not `utilize`,
`look at` not `delve into`. Cut the antithesis cadence (`it's not just X, it's Y`) and the
throat-clearing opener. The point goes in the first sentence, not after a warm-up.

## The escape hatch

A register chosen on purpose is not a tell. A legal brief is formal; an academic paper avoids
contractions; a particular writer loves the em dash. The skill removes *unchosen defaults*, not
deliberate choices. When a flagged word or form is a real decision, keep it and mark the line
`unslop-ignore` so the audit stays honest.

## The one-line version

If you do only one thing, get a real voice sample from the user and match it, then read the
draft aloud and fix whatever lulls. Everything else here is what to do when you cannot. The
skill removes the tells; this method is how you replace them with something chosen rather than
something defaulted.
