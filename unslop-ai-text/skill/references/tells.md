# The AI-writing tells: full catalog

Each entry has the data evidence (so you can weight it), a real quote from the threads, the
literal text the scanner keys on, and the fix. Ordered by priority: the **cited share** from
the 600-post audited sample, which is the cleanest signal, with the broad keyword-pass share
next to it. Source: 89,239 posts pulled, 7,984 on-topic, across roughly 50 AI, writing, and
SaaS subreddits, 2021 to 2026.

A note on weighting. Two numbers are reported per tell. **Cited** is the share of audited
posts where a human actually names the tell as a giveaway. **Matched** is the share of all
on-topic posts whose text a keyword pass flags. They diverge in informative ways. The em dash
is cited far more than it is matched (people talk about it more than they leave it in). The
generic diction words are matched far more than they are cited (they are mostly the poster's
own ordinary prose, not a giveaway). Trust cited over matched, and treat the structural tells
in Part B as under-counted, since no keyword can catch them at all.

Read by concentration, not by lone hits. A single `comprehensive` or one `delve` is almost
always the writer's own prose, not a tell; the signal is density, the same tic clustering. The
two exceptions are absolute, counted on a single instance wherever they appear: the em dash and
leftover assistant boilerplate (entry 7). For everything else, weight by how thickly it
clusters, and remember the scanner reports a lexical surface only. The Part B tells, which the
audited pass ranked above most of Part A, are where the real reading happens.

## Contents

Part A, the tells the scanner catches:
1. The em dash
2. "It's not just X, it's Y" (the antithesis cadence)
3. The formulaic essay shape and the "In conclusion" wrap-up
4. "Dive in" / "deep dive"
5. Everything turned into bullet lists
6. The diction memes (`delve`, `tapestry`, `leverage`, `seamless`, ...)
7. Leftover assistant boilerplate ("as an AI language model")
8. Bolded lead-in labels (**Word:** then a sentence)
9. "Unlock the potential" and marketing hype
10. "In today's fast-paced world" and other hollow openers
11. Emoji as bullets, icons, or headers
12. Trailing assistant offers ("Would you like me to ...")

Part B, the cited tells a regex cannot see (human pass required):
13. Uniform / robotic sentence rhythm
14. Sycophancy and the yes-man register
15. Saying nothing at length (the empty, polished paragraph)
16. No contractions / over-formal register
17. Hedging instead of committing
18. The rule of three
19. Hallucinated citations, "Honestly," openers, and fake typos
20. The over-corrected "anti-AI" register (the 2026 tell)

Part C, cleared by the data (do not over-chase):
21. The over-counted generic diction (`however`, `comprehensive`, "when it comes to", `utilize`)


## Part A: the tells the scanner catches

### 1. The em dash

**Evidence.** cited 7.1%, matched 4.5%. The single most-cited tell, and the one with the
sharpest before-and-after: essentially absent from the on-topic posts before 2024, then 6.7%
of them in 2025. The arrival of the ChatGPT era in one punctuation mark.

**Quote.** "If you're familiar with ChatGPT, you know it loves an em-dash. If you're familiar
with the average teenager, then you know they have no clue what an em-dash is." (r/Teachers).
And: "Em dashes have become the single most reliable tell of AI-generated text." (r/ChatGPT)

**Pattern (scanner).** the em dash character itself, anywhere in the file. Unlike the other
rules, this one is flagged inside quotes too, because the rule is simply not to ship one.

**Why it reads as AI.** almost nobody types a real em dash on a phone or in a quick post.
Models produce it constantly because their training favors "correct" typography. So the mark
that signals polish now signals a machine.

**Fix.** cut it. Use a comma, a period, or parentheses. Do not just swap in a colon, because
people have started flagging that too. If you genuinely write with em dashes by choice, mark
the line `unslop-ignore`, but know that readers will still read it as a tell.

### 2. "It's not just X, it's Y" (the antithesis cadence)

**Evidence.** cited 2.8%, matched 1.9%. The most-named *sentence* tell, often paired with the
em dash in the same complaint.

**Quote.** "even beyond the obvious em dashes and 'not just x, it's y' or 'straight up' or
'era' or 'honestly? that's growth'." (r/ChatGPT). And: "it's not even the 'That's not x;
that's y.' ChatGPT has a very recognizable cadence." (r/ChatGPT)

**Pattern (scanner).** `it's not just X, it's Y`, `not X, but Y`, `isn't just ... it's ...`.
The negate-then-assert shape.

**Why it reads as AI.** the construction manufactures profundity for free. It is the clearest
single piece of the "AI accent," a rhythm the model falls into to sound insightful.

**Fix.** state the thing plainly. If Y is the point, just say Y. Delete the throat-clearing
negation in front of it.

### 3. The formulaic essay shape and the "In conclusion" wrap-up

**Evidence.** formulaic shape cited 2.5%; the "In conclusion" / "in summary" closer cited
0.2% but matched 1.0% and is a classic giveaway. Several auditors called the shape
under-counted ("the exact same rigid three-paragraph formula").

**Quote.** "people using ChatGPT or other AI tools to write essays, posts, or even emails, and
they leave in those super obvious lines like: 'In conclusion, this essay has discussed...',
'As an AI developed by OpenAI...', 'To summarize the above points...'." (r/ChatGPT)

**Pattern (scanner).** `in conclusion`, `in summary`, `to summarize`, `to conclude`, `in
closing`. The shape itself (intro, three even body paragraphs, recap) is structural and needs
a human eye.

**Why it reads as AI.** the model defaults to the five-paragraph essay it was rewarded for.
The signposted recap at the end is the tell most writers forget to delete.

**Fix.** break the intro / three-body / conclusion mold and let the structure follow the idea.
End on a real last point. If the reader needs a summary to follow it, the piece is too long.

### 4. "Dive in" / "deep dive"

**Evidence.** cited 2.0%, matched 1.6%.

**Quote.** from a post written entirely in the register, offered as an example: "I wanted to
take a moment to delve into something that's been on my mind lately. In today's fast-paced
digital landscape, it seems like every single post..." (r/ClaudeAI)

**Pattern (scanner).** `dive in`, `dive into`, `deep dive`, `let's dive`, `diving in`.

**Why it reads as AI.** the model announces that it is starting before it starts. A person
just starts.

**Fix.** cut the metaphor and open with the actual topic.

### 5. Everything turned into bullet lists

**Evidence.** cited 1.7%, matched 1.8%. The "5 ways to" / "7 signs" listicle scaffolding.

**Quote.** a teacher compiling giveaways: "STUDENT TALKING TO TEACHERS, HERE ARE SOME
GIVEAWAYS FOR CHATGPT. I've compiled some sentence structures and phrases Chatgpt seems to
really enjoy." (r/Teachers)

**Pattern (scanner).** a numbered listicle header such as `5 ways to ...`, `7 signs ...`, `3
reasons ...`.

**Why it reads as AI.** prose gets shredded into bullets because lists are the model's safe
default for "organized." Real argument lives in paragraphs.

**Fix.** write prose. Reserve bullets for genuinely list-like content (steps, parts, options),
not as the shape of every answer.

### 6. The diction memes (`delve`, `tapestry`, `leverage`, `seamless`, `game-changer`, ...)

**Evidence.** cited 1.3% as a cluster, matched higher. The audited pass found the keyword
counts are inflated by people copy-pasting "words to avoid" lists, but the words are real
corpus-wide and instantly recognizable.

**Quote.** "Add this line to every ChatGPT prompt you use ... no telltale signs like em dashes,
overused words like 'seamless,'." (r/ChatGPT). And a whole genre of posts titled "Exclude
These 100+ Words From ChatGPT."

**Pattern (scanner).** `delve`, `tapestry`, `leverage`, `seamless`, `game-changer`, `unleash`,
`underscore`, `testament`, `embark`, `meticulous`, `elevate`, `harness`, `showcase`,
`captivating`, `ever-evolving`.

**Why it reads as AI.** these are the words the model reaches for over the plain ones. No real
register uses all of them.

**Fix.** swap for the word you would actually say. "delve into" is "look at." "leverage" is
"use." "utilize" is "use." Do not swap one fancy word for another.

### 7. Leftover assistant boilerplate ("as an AI language model")

**Evidence.** cited 1.2%. Aging out as people learn to delete it, but the single most
conclusive tell when it survives.

**Quote.** "they leave in those super obvious lines like ... 'As an AI developed by
OpenAI...'." (r/ChatGPT)

**Pattern (scanner).** `as an AI language model`, `as a large language model`, a refusal like
`I cannot assist`, a `knowledge cutoff` line, `I don't have personal opinions`.

**Why it reads as AI.** it is the machine speaking in its own voice. There is no human reading
of it.

**Fix.** delete every trace of the assistant before publishing: disclaimers, refusals, cutoff
dates, "I'm just an AI."

### 8. Bolded lead-in labels (**Word:** then a sentence)

**Evidence.** cited 0.3%, but matched 2.8% (n=220), the third-highest by keyword pass. The
title-case `**Bold:**` then a clause pattern.

**Quote.** named alongside the other format tells in the giveaway-list posts (r/ChatGPT,
r/Teachers).

**Pattern (scanner).** a line like `**Productivity:** Studies show ...`, a bolded label and
colon in front of a sentence.

**Why it reads as AI.** it is the model formatting a chat answer, not writing prose. Human
writing rarely labels each sentence.

**Fix.** write the sentence without the boldface label. If you need structure, use real
sentences and paragraphs.

### 9. "Unlock the potential" and marketing hype

**Evidence.** "unlock / unleash the power/potential" cited 0.8%; the broader marketing
category (`revolutionary`, `transformative`, "transform your life") cited around 0.3% and named
repeatedly as a category.

**Quote.** the giveaway-list and "words to avoid" posts single out the hype verbs (r/ChatGPT,
r/marketing).

**Pattern (scanner).** `unlock the potential`, `unleash the power`, `revolutionary`,
`transform your business`, `take it to the next level`, `supercharge`, `game-changer`.

**Why it reads as AI.** it is the voice of a landing page no person wrote. It promises and
says nothing.

**Fix.** say what the thing literally does, with a specific. Strip the promotional adjective.

### 10. "In today's fast-paced world" and other hollow openers

**Evidence.** cited 0.7%, matched 0.4%. Iconic and low-volume, the empty scene-setting first
sentence.

**Quote.** from the example post: "In today's fast-paced digital landscape, it seems like
every single post..." (r/ClaudeAI)

**Pattern (scanner).** `in today's fast-paced world`, `in today's digital age`, `in the
modern era`, and the dated-opener family.

**Why it reads as AI.** the model warms up with a sentence that establishes nothing, because
it was trained to ease in.

**Fix.** delete it and open with something specific. The first sentence should carry the
claim, not set a scene.

### 11. Emoji as bullets, icons, or headers

**Evidence.** cited 0.8%. Decorative emoji standing in for list markers or section headings.

**Quote.** the example slop post opens "Hey everyone! [waving emoji] I wanted to take a moment
to delve..." (r/ClaudeAI), with the emoji as a greeting flourish.

**Pattern (scanner).** an emoji at the start of a heading or a list item, or wrapped around a
bold label.

**Why it reads as AI.** emoji-as-decoration is the model's free substitute for design. It
reads as templated.

**Fix.** use plain text headers and normal list markers. An emoji in a sentence where a person
would actually use one is fine; emoji as structure is not.

### 12. Trailing assistant offers ("Would you like me to ...")

**Evidence.** cited around 0.4% each. The sign-off that the writer forgot to cut: "Would you
like me to ...", "Let me know if ...", "I hope this helps!", "I hope this email finds you
well."

**Quote.** named in the giveaway-list posts as a line people forget to delete (r/ChatGPT).

**Pattern (scanner).** `would you like me to`, `let me know if you'd like`, `I hope this
helps`, `hope this email finds you well`, `is there anything else`.

**Why it reads as AI.** a person finishing a thought does not ask whether you want a revision.
It is the assistant's turn-ending move, pasted into a final draft.

**Fix.** delete the meta-offer and the form-letter sign-off. End on the last real sentence.


## Part B: the cited tells a regex cannot see

These are named as often as the top mechanical tells, sometimes more, but no pattern can catch
them. The scanner will not flag them. Read the piece aloud and check them by ear. The audited
pass put several of these above most of Part A.

### 13. Uniform / robotic sentence rhythm

**Evidence.** cited 4.0%, the second-most-cited tell overall, and entirely keyword-invisible.

**Quote.** "ChatGPT has a very recognizable cadence. And as soon as you catch it, it is
impossible to focus on what's being written, because it's not even someone's actual thoughts."
(r/ChatGPT). And: "Every YouTube video script I watch has the same cadence, the same verbiage,
the same fucking chatGPT slop." (r/ChatGPT)

**Why it reads as AI.** the model produces sentences of similar length and shape, evenly
paced, with no variation. The evenness is the tell. A human ear catches it before any single
word.

**Fix.** vary sentence length on purpose. Let one run long and the next be three words. Read it
aloud; if it lulls, break the meter.

### 14. Sycophancy and the yes-man register

**Evidence.** cited 2.5%, the fourth-most-cited tell, and one auditor found it rivals the em
dash for citation density. Keyword-invisible as tone, though the openers in Part A catch some
of it.

**Why it reads as AI.** the model opens with flattery ("Great question!"), agrees reflexively,
and refuses to take a side. The relentless positivity reads as a customer-service bot, not a
person with a view.

**Fix.** drop the flattery and the reflexive agreement. Disagree when you disagree. Stay
neutral when you are neutral. A real writer is willing to say no.

### 15. Saying nothing at length (the empty, polished paragraph)

**Evidence.** cited 0.7% and flagged by multiple auditors as under-counted (it folds in
"soulless," "word salad," "no opinion"). Keyword-invisible.

**Why it reads as AI.** the prose is fluent and grammatical and makes no actual claim. It
restates the prompt, hedges, and moves on. Fluency with nothing behind it is the deepest tell.

**Fix.** make a real claim and cut the filler. If a paragraph could be deleted with nothing
lost, delete it. Say each thing once.

### 16. No contractions / over-formal register

**Evidence.** cited 0.7% (higher once "overly formal" is merged in). Keyword-invisible.

**Why it reads as AI.** "do not," "cannot," "it is" everywhere, in a casual context, reads as
stiff in the specific way the default register is stiff.

**Fix.** use contractions and write the way the speaker actually talks, unless the register
genuinely calls for formality (a brief, a paper).

### 17. Hedging instead of committing

**Evidence.** cited 0.3%. The scanner catches the cliche phrasings ("it depends," "on one hand
... on the other") but not the underlying refusal to commit.

**Why it reads as AI.** the model gives a balanced menu instead of an answer, because it is
trained to avoid being wrong. The reader wanted a position.

**Fix.** take a position. List the trade-off if it matters, but say what you would do.

### 18. The rule of three

**Evidence.** cited 1.2% and named spontaneously across several threads ("uses three-part
structures constantly"). A regex cannot reliably tell a deliberate triad from a normal list.

**Why it reads as AI.** the model loves parallel triplets and three-part lists. One is fine;
reaching for three every time is the tell.

**Fix.** vary the count. Two items, or four, or a single clean sentence. Do not let everything
arrive in threes.

### 19. Hallucinated citations, "Honestly," openers, and fake typos

- **Hallucinated citations** (cited by four auditors, no keyword share): invented sources,
  fake author names, made-up case law. A content-level giveaway. Verify every reference.
- **"Honestly," and fake-relatability openers** ("Look, I get it," "Imagine this"): one of the
  top threads is devoted to "Honestly" being "zombified by AI." The scanner catches the literal
  openers; cut the throat-clearing and start with the point.
- **Deliberately-inserted fake typos** to beat detectors ("excyted," "annownce"): named in the
  data as itself a tell. Do not fake errors. This is the over-corrected register, not a fix.

### 20. The over-corrected "anti-AI" register (the 2026 tell)

This is the mirror of the whole catalog above, and the moving target this skill exists to stay
ahead of. As writers learned the 2024 tells, a second default appeared: prose visibly straining
not to read as AI. It is its own tell, named in the data and clocked just as fast, the way a
cream-and-serif redesign is now its own tell in UI. Mostly keyword-invisible, so it belongs in
the human pass.

**What it looks like.** Staccato three-word fragments on every beat, so the rhythm is uniform
in a new way. Forced lowercase and dropped capitals in a context that is otherwise standard. A
"here's the thing," a "look," or a "real talk" cold open bolted onto formal content. Profanity
or a "lol" dropped in to seem off-the-cuff. And conspicuous em-dash avoidance: replacing every
natural dash with an ellipsis, a colon, or a sentence visibly contorted around the gap.

**Why it reads as AI.** It is still a default, just a newer one, and a reader feels the strain.
All-short sentences are as mechanical as all-medium ones; evenness is the tell whichever length
it lands on. Bolted-on slang is a costume rather than a voice, and the contortion to dodge a
dash is as legible as the dash would have been. The deliberately-inserted fake typo (entry 19)
is the most extreme form of the same move.

**Fix.** Do not over-apply the rules. The fix for a dash is a comma or a period in a sentence
you would actually write, not an ellipsis and not a contortion. The fix for the smooth voice is
a real voice (pick a register; see writing-with-intent.md), not the absence of voice dressed up
as casual. Vary sentence length for real, long ones included. If a casual marker is not native
to the register you chose, cut it.


## Part C: cleared by the data (do not over-chase)

The audited sample showed the keyword pass badly over-counts a set of ordinary words. They
match a lot of posts but are almost never what a reader actually cites, because they are the
poster's own normal prose, not a giveaway.

- "however," "thus," "hence": matched 6.3%, the single highest keyword share, and cited
  0%. Mostly the poster writing normally. Do not flag a lone "however."
- "when it comes to": matched 1.9%, cited 0%.
- "comprehensive," "robust," "crucial," "navigate," "utilize," "nuanced": matched 1 to 2%
  each, cited near 0%. Real words people use. "utilize" is worth swapping for "use," but it is
  not a smoking gun.
- "moreover / furthermore / additionally": matched 1.7%, over-counted. As a stacked
  sentence-opener it reads as machine-smoothed, but one of them is just a connective.

Flag what the data supports, at the weight it supports. The scanner weights all of these low
for exactly this reason. Over-flagging trains writers to ignore the tool.
