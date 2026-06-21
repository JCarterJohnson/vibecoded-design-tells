# The AI-written-code tells: full catalog

Each entry has the data evidence (so you can weight it), a real quote from the threads, the
code-level signature the scanner keys on, and the fix. Ordered by the **verified share** of
the comments that name a specific tell, the cleanest signal. Source: 11,906 on-topic posts +
11,306 comments across 55 AI, coding, and SaaS subreddits, 2020 to 2026, classified by an LLM
into a fixed taxonomy of 19 tells and then adversarially verified quote by quote.

A note on weighting. Two numbers matter. **Raw** is the share the LLM classifier assigned.
**Verified** is what survived re-reading the actual quotes, discounted by precision. They
diverge a lot: over-commenting was classified at 18.2% but only about half the quotes really
named it, so it verifies at 8.5%. Trust verified over raw. And note the split below: the
loudest tells (Part B) are about shape and substance, and no regex can see them. The scanner
catches the mechanical surface tells in Part A.

## Contents

Part A, the tells the scanner catches:
1. Over-commenting / narrating comments
2. Emoji in code
3. Catch-all / swallowed errors
4. Generic placeholder names
5. Placeholder / ellipsis comments left in
6. Leftover chat / assistant artifacts
7. Over-verbose identifiers

Part B, the cited tells a regex cannot see (human or compiler pass required):
8. Boilerplate / tutorial-shaped code (the #1 tell)
9. Hallucinated APIs and made-up libraries
10. Over-engineering
11. "You can just tell" (the umbrella)
12. Style that ignores the surrounding codebase
13. Too clean, no human mess
14. Mixed skill level

Part C, cleared by the data (do not chase):
15. Left-in debug logging, reinventing the wheel, defensive checks for impossible cases

---

## Part A: the tells the scanner catches

### 1. Over-commenting / narrating comments

**Evidence.** Raw 18.2%, verified 8.5%, precision ~47.5% (inflated). The most over-claimed
tell: only about half the people who blamed "the comments" were naming this one. A regex
catches the obvious-restatement and step-by-step subset, not the judgment call.

**Quote.** "2.5 pro legit will add comments like `// include weights` before a line that
simply adds weights into a json object. Or `// define sort function` before defining a
function." (r/ChatGPTCoding). And: "if every line has a comment they stop being comments it
starts becoming a mess."

**Code signature (scanner).** A comment that restates the next line (`# increment i`,
`// return the result`) or narrates step by step (`# Step 1`, `# Now we...`, `# First,`).

**Why it reads as AI.** The model narrates because its training rewards explanation. A comment
on nearly every line, saying what the line plainly does, is the tell.

**Fix.** Comment why, not what. Delete any comment that restates the code next to it.

### 2. Emoji in code

**Evidence.** Verified 3.9%, precision ~77%, the highest-precision cosmetic tell. When people
name it, they are almost always right.

**Quote.** "Full of emojis + randomly bolded words = AI slop." (r/aipromptprogramming). And:
"its just a bunch of neon cards with emojis on a pitch black background in localhost."

**Code signature (scanner).** Any emoji character in source: in comments, string literals,
`console.log` / `print` output, or commit messages.

**Why it reads as AI.** The emoji survives from the model's chat output into the file. Almost
no human sprinkles them through real source.

**Fix.** Remove emoji from code and logs. If a CLI genuinely wants a checkmark, choose it on
purpose and mark the line `unslop-ignore`.

### 3. Catch-all / swallowed errors

**Evidence.** Verified 3.1% (try/except or try/catch wrapped around everything).

**Quote.** "they throw their own exception then catch it and convert it into a generic
'something went wrong' error." And the reviewer's version: "error handling that quietly eats
the one clue you needed."

**Code signature (scanner).** A bare `except:`, an `except Exception: pass`, an empty
`catch (e) {}`, a catch block that only swallows.

**Why it reads as AI.** The model wraps everything to make the happy path pass, which hides
the failure you needed to see.

**Fix.** Catch specific exceptions and handle them. Let unexpected failures surface.

### 4. Generic placeholder names

**Evidence.** Verified 1.9%, precision ~100% (solid). Every tagged quote was real, and they
all cite the same canonical example.

**Quote.** "a function called `process_data()` that somehow does 11 different things."
(r/AI_Agents). And: "They write `process_data()`
doing 11 things because from training data, that's what a function named process_data
typically does in a one-off script."

**Code signature (scanner).** Functions named `process_data`, `handle_data`, `do_stuff`,
`do_something`, `process_item`, and other domain-free placeholder names.

**Why it reads as AI.** The model reaches for the most common name in its training data
instead of naming the thing for what it does in your domain.

**Fix.** Name the function for its actual job. If you cannot, the function is doing too much.

### 5. Placeholder / ellipsis comments left in

**Evidence.** Verified 1.6%, precision ~100%. Shows up more in posted screenshots than in
conversation, but it is unmistakable.

**Quote.** A reply quoting the model: it "either gives you the exact same response or says
`//// rest of the code goes`." (r/ChatGPT)

**Code signature (scanner).** `// rest of your code`, `# ... your logic here`, `// existing
code unchanged`, `// implementation goes here`, `# TODO: implement`.

**Why it reads as AI.** The model elides the boring middle in chat and the user pastes it
verbatim. The stub means the file was never actually finished.

**Fix.** Write the real code the comment is standing in for.

### 6. Leftover chat / assistant artifacts

**Evidence.** Verified 1.2%. Aging out as people learn to delete it, but conclusive when it
survives into a file or a commit.

**Quote.** A pasted assistant reply left in a thread: "Good catch!! Testing is an essential
part of successful software development. I'll add TDD tests to the application now."
(r/ChatGPTCoding). And: "All of the em dashes, the markdown format, the same sentence
structure... no human would actually add."

**Code signature (scanner).** Triple-backtick fences inside a source file, `Here's the
updated code`, `As an AI`, `Good catch!`, `You're absolutely right`, a trailing `Note:` or
`Remember:` preamble.

**Why it reads as AI.** It is the model's chat voice, pasted into a file without cleanup.

**Fix.** Delete every line that is the assistant talking, including the polite preamble and
the closing offer.

### 7. Over-verbose identifiers

**Evidence.** Verified 0.4%, precision ~16.7% (inflated). People mostly argue *for* descriptive
names; only the truly robotic, whole-sentence identifier is mocked.

**Quote.** "None of this `inputProcessingAndFormatting()` crap."

**Code signature (scanner).** An identifier that is a whole sentence in camelCase or
snake_case (`getUserDataFromApiResponseHandler`, `input_processing_and_formatting_helper`).

**Why it reads as AI.** The model pads names to self-document. A name should be precise, not a
paragraph.

**Fix.** Trim the name to the precise noun or verb. Descriptive is good; a sentence is not.

---

## Part B: the cited tells a regex cannot see

These are the loudest tells in the data, and no pattern can catch them. The scanner will not
flag them. They are about shape and substance, so they need a human reader or a compiler.

### 8. Boilerplate / tutorial-shaped code (the #1 tell)

**Evidence.** Verified 18.6%, precision ~90% (solid), the top tell by a wide margin and the
cleanest in the set.

**Quote.** "If you just ask it to make your app and press generate it's normally one page
placeholder no backend and a bunch of dummy data." (r/ChatGPTCoding). And: "They've
memorized every design pattern from a textbook but have zero common sense to know when a
simple if/else will do."

**Why it reads as AI.** The model emits the average of public code: the tutorial, the sample
app, the textbook pattern, with dummy data and no real backend.

**Fix.** Build the actual thing, with real data and the real backend. The dummy-data marker
rule in the scanner is only a weak proxy; judging "tutorial-shaped" is a human call.

### 9. Hallucinated APIs and made-up libraries

**Evidence.** Verified 11.2%, precision ~62.5%. The tell that bites in production.

**Quote.** "those blocks didn't exist. At all. It just made them up." And: "hallucinated
library methods that compile but don't exist at runtime, confident-sounding edge case handling
that was never tested." (r/ExperiencedDevs)

**Why it reads as AI.** The model produces plausible-looking calls to things that do not
exist, or logic that reads right and is quietly wrong.

**Fix.** Run it. Check every import and method against real docs. A compiler, a type checker,
and a test catch this; a regex never will.

### 10. Over-engineering

**Evidence.** Verified 7.8%, precision ~60.6%.

**Quote.** "Giant functions, hidden side effects, random abstractions that nobody would
consciously design." And: "Claude has a natural tendency for over-engineering. You just need
to write a lot of KISS YAGNI, etc. statements in a md file."

**Why it reads as AI.** Needless layers and abstractions for a simple task, because the
training data is full of enterprise patterns.

**Fix.** Ask whether a simple if/else would do. Delete the abstraction that has one caller.

### 11. "You can just tell" (the umbrella)

**Evidence.** 17.8% of tell-naming comments, the near-as-loud second voice, but it names no
specific feature.

**Quote.** "You can spot the vibe coders in the comments." And, in full: "We can tell." And
the evocative one: "small model smell."

**Why it matters.** Most people are confident they can spot AI code and vague about what they
saw. The specific tells in this catalog are what that feeling resolves to when you press.

**Fix.** Not actionable on its own. Use the rest of the catalog.

### 12. Style that ignores the surrounding codebase

**Evidence.** Verified 3.5%, precision ~64.3%.

**Quote.** "a PR that should be 50 LoC because it follows naturally from the existing codebase
patterns vs a PR that is 2000 LoC that ignores the codebase conventions." (r/ExperiencedDevs)

**Why it reads as AI.** The model does not read the rest of the repo, so it invents a new way
to log, a new decorator approach, a new structure, mid-file.

**Fix.** Make the code follow the conventions already in the repo. This was the single most
repeated fix in the whole dataset: give the model the existing code, not a blank slate.

### 13. Too clean, no human mess

**Evidence.** Verified 2.3%, precision ~42.9% (genuinely contested).

**Quote.** "I miss when a PR review had so many code smells it took 2 seconds, now all the
smells are gone, only the bugs remain." (r/ChatGPT). And: "AI generated code often looks
clean. Passes linting, decent structure."

**Why it reads as AI.** Uniform, standard-following, no shortcuts or quirks. The surface is
clean and the logic can still be wrong. This is the weakest of the Part B tells (plenty of
careful humans write clean code), so weight it last.

**Fix.** None for the author. For the reviewer: do not let a clean surface end the review.

### 14. Mixed skill level

**Evidence.** Verified 1.9%, precision ~50%.

**Quote.** "use programming practices that were outdated 10 years ago or even mix
practices from the 90s with cutting edge practices from 2025." (r/ChatGPTPro). And the buyer's
version: "The seller couldn't explain: Why certain dependencies existed, How error handling
worked, What would break at scale."

**Why it reads as AI.** Advanced patterns sit next to beginner mistakes, and the author cannot
explain any of it, because no single developer wrote it.

**Fix.** If you cannot explain a line, do not ship it. Understand the code before it is yours.

---

## Part C: cleared by the data (do not chase)

The verification step exists to catch over-claims, and three popular ones did not survive.

- **Left-in debug logging** (`print` / `console.log` everywhere, chatty "Successfully..."
  logs): rejected outright, precision ~0%. Not one tagged comment actually pointed at left-in
  debug logging in code; all eight were workflow opinions. The scanner does not flag bare
  logging.
- **Reinventing the wheel** (re-implementing what the stdlib already does): inflated, precision
  ~16.7%. Mostly misattributed to duplication or hallucinated libraries once the quotes are
  read.
- **Over-defensive validation** (null checks for cases that cannot happen): inflated, precision
  ~40%. Half the tagged comments were complaining about the opposite, AI code with *no*
  validation at all.

Flag what the data supports, at the weight it supports. Over-flagging trains people to ignore
the tool.
