# Verified quote bank per AI-code tell

## Boilerplate, tutorial/textbook-shaped 'sample app' code  (53 comments, 20.5% of tell-naming comments)
verdict: **solid**, precision ~90% — Nearly all tagged comments explicitly name boilerplate/scaffolding/tutorial/sample-app-shaped output; a few are generic "AI saves boilerplate typing" but still on-target. Misses: 102 (copypaste jobs), 323 (posted spec, doesn't name tell), 826 (no-backend critique), 1113 (vague effort).

- “so instead of creating a reusable Featured$VARIABLESection you are generating boilerplate. uh nice I guess.”
- “They've memorized every design pattern from a textbook but have zero common sense to know when a simple if/else will do.”
- “If you just ask it to make your app and press generate it's normally one page placeholder no backend and a bunch of dummy data.”
- “the code that was correct, frequently was more verbose for my use case (it really look like examples you frequently find when searching for solutions to some common problem).”

## Over-commenting: a comment on nearly every line, narrating the obvious  (47 comments, 18.2% of tell-naming comments)
verdict: **inflated**, precision ~47.5% — Many tagged comments are the adjacent "explain why not what" tell, vague verbosity gripes, doc-not-inline complaints, or jokes/off-topic Reddit chatter; only ~half clearly name commenting nearly every line / narrating the obvious.

- “Gemini insists on a comment for every line of code, so no.”
- “2.5 pro legit will add comments like // include weights before a line that simply adds weights into a json object. Or // define sort function before defining a function.”
- “unnecessarily telling you exactly what every single line of code does”
- “if every line has a comment they stop being comments it starts becoming a mess”

## Calls to nonexistent/outdated APIs; plausible but wrong logic  (47 comments, 18.2% of tell-naming comments)
verdict: **mostly**, precision ~62.5% — Most hits genuinely describe made-up libraries/APIs/methods or plausible-but-wrong logic; a chunk are generic "hallucination/bugs" or off-topic (untested tests, lost context, accountability) that don't specifically name this tell.

- “those blocks didn't exist. At all. It just made them up.”
- “hallucinated library methods that compile but don't exist at runtime, confident-sounding edge case handling that was never tested, unrequested subsystems the diff quietly added”
- “It constantly hallucinates features, APIs, patches, deprecations, anything and everything”
- “It tried to gaslight me into believing that a version of a library exists that doesn't exist”

## Umbrella: 'you can just tell it's AI / too perfect' with no specific feature named  (46 comments, 17.8% of tell-naming comments)
- [r/OpenAI|1] I work in a utilities company, I have done for 20 years. They haven't touched AI. I can't use it at work. I use it heavily for my own projects though. They won't use it until it is safe and it is a long way from that at the moment. Just like they wouldn't hire entry level programmers to write critic
- [r/OpenAI|191] You can spot the vibe coders in the comments.
- [r/ChatGPTCoding|1] I dunno I find even 2.5 gemini has small model smell: https://x.com/paul_cal/status/1910960495294554241
- [r/ChatGPTCoding|4] We can tell.

## Over-engineered: needless abstraction / layers for a simple task  (33 comments, 12.8% of tell-naming comments)
verdict: **mostly**, precision ~60.6% — About 60% genuinely name needless abstraction/complexity; the rest are adjacent tells (excess volume/LOC, duplication, random dependencies, or giant under-decomposed functions, which is the opposite).

- “They've memorized every design pattern from a textbook but have zero common sense to know when a simple if/else will do.”
- “Claude has a natural tendency for over-engineering. You just need to write a lot of KISS YAGNI, etc. statements in a md file”
- “Giant functions, hidden side effects, random abstractions that nobody would consciously design.”
- “unnecessary complications and abstractions”

## try/except (try/catch) wrapped around everything / swallowed errors  (16 comments, 6.2% of tell-naming comments)
verdict: **mostly**, precision ~50% — Half genuinely name over-broad catching / swallowed errors; the other half are the opposite tell (MISSING error handling) or generic "error handling" mentions that don't fit this specific tell.

- “I use a lot of generic exception catching and believe that my programmer never crashed”
- “they throw their own exception then catch it and convert it into a generic "something went wrong" error”
- “Every external call handles the failure path explicitly, no bare try/except passes”
- “error handling that quietly eats the one clue you needed”

## Suspiciously clean/consistent/perfect formatting, no human mess  (14 comments, 5.4% of tell-naming comments)
verdict: **mostly**, precision ~42.9% — A solid core names AI code's "too clean / no quirks / uniform style" tell, but several tagged comments instead point at verbosity, em-dashes/markdown, design-library sameness, or clean-surface-hiding-bugs (logic), which are adjacent but distinct tells.

- “Check for overly clean/perfectly formatted code without quirks or personality since AI tends to follow standards. Humans have unique styles, shortcuts, and occasionally weird variable names.”
- “AI generated code often *looks* clean. Passes linting, decent structure.”
- “As models are getting "smarter" their code *looks* better and better but still has just as many issues.. I miss when a PR review had so many code smells it took 2 seconds, now all the smells are gone, only the bugs remain.”
- “It definitely has a sort of "way" it likes to write things and I'll have to nudge it to not do that.”

## Style doesn't match the surrounding codebase; a sudden shift  (14 comments, 5.4% of tell-naming comments)
verdict: **mostly**, precision ~64.3% — Most comments genuinely describe AI code breaking/ignoring existing codebase conventions and patterns; a few are off-topic (jail/rg rant, generic vibe-coding hate, design-process advice).

- “they can't tell when their edits break the patterns of the code base”
- “Any chance it gets, the llm stops using my preferred decorator approach, creates some brand new way of logging and I'd have duplicate and inconsistent ways of doing things all over the shop”
- “they completely miss the design-system drift that AI pumps out every day (arbitrary Tailwind values, token mismatches, broken dark-mode coverage, inconsistent spacing)”
- “a PR that should be 50 LoC because it follows naturally from the existing codebase patterns vs a PR that is 2000 LoC that ignores the codebase conventions”

## Emoji in code, comments, console logs, or commit messages  (13 comments, 5.0% of tell-naming comments)
verdict: **mostly**, precision ~76.9% — Most comments name emoji as an AI/vibe-code tell (in code, output, or AI prose); the two "random emoji rule" comments and one vague pattern-musing don't name it as a tell.

- “Full of emojis + randomly bolded words = AI slop”
- “its just a bunch of neon cards with emojis on a pitch black background in localhost”
- “Apple doesn't care if you write it in all emojis. Go for broke and pretty it up with the emojis like this: private func 🌀(”
- “Need more 📈 emojis 🤩”

## Mixed skill: advanced code beside beginner mistakes; author can't explain it  (10 comments, 3.9% of tell-naming comments)
verdict: **mostly**, precision ~50% — Half clearly name works-but-can't-explain or advanced-beside-outdated skill-mixing; the rest drift into generic correctness/review-process complaints, plus 3 near-duplicate comments (1391/1392/1393) and one ad (949) inflate the set.

- “use programming practices that were outdated 10 years ago or even mix practices from the 90s with cutting edge practices from 2025”
- “The seller couldn't explain: Why certain dependencies existed, How error handling worked, What would break at scale”
- “checking if they can explain me every line by line”
- “everything working great... suddenly onboarding was broken in ways I couldn't even Trace because... I didn't write half of it”

## Print/console.log debugging left in; chatty 'Successfully...' logs  (8 comments, 3.1% of tell-naming comments)
verdict: **artifact**, precision ~0% — All 8 are Reddit opinion comments about AI coding/logging workflow, none identify left-in debug prints or chatty success logs in code.

- [r/OpenAI|1] The simple fact you debug with the console and not with a debugger tell me everything i need to know
- [r/OpenAI|1] Or you just ask the AI to generate comprehensive console logging, paste the logs back into the chat, and have it solve the problem for you. What is this, amateur hour?
- [r/ExperiencedDevs|1] ***and you have a high confidence that yes it works***   And how do you get this confidence without actually going over and doing proper review? I am sure you have seen how nonsensical tests can AI happily generate. I've going tons of tautological tests which test nothing, tests which test the same 
- [r/ChatGPTCoding|5] Ok, that is true. AI code is definitely cleaner that it was a year ago. But the main issue with vibe coding is what you don't know you don't know. When you don't know what a memory leak is or what it's symptoms are, you don't know to tell the AI to fix the problem or how to prevent it.  Don't get me

## Over-verbose, robotically self-documenting variable/function names  (6 comments, 2.3% of tell-naming comments)
verdict: **inflated**, precision ~16.7% — Only one comment mocks long/robotic AI identifier names; the rest are about naming quality in general or argue FOR descriptive/semantic names, which is the opposite of this tell.

- “None of this inputProcessingAndFormatting() crap”

## Re-implements what the stdlib/a library already does  (6 comments, 2.3% of tell-naming comments)
verdict: **inflated**, precision ~16.7% — Only one comment names reinventing what an existing package provides; the rest are about duplication, hallucinated libs, verbosity, or generic redundancy.

- “Not surprised that vibe coders are now over engineering things they didn't know already existed.”
- “Real developers gave been doing this for years it isn't hard, you don't need to vibe code a platform to do it, NPM does it.”

## Generic placeholder names (data, result, temp, item, foo)  (5 comments, 1.9% of tell-naming comments)
verdict: **solid**, precision ~100% — All 5 cite process_data() as the canonical AI-generated generic placeholder function name; squarely the generic_naming tell.

- “They write process_data() doing 11 things because from training data, that's what a function named process_data typically does in a one-off script.”
- “no giant “process_data()” mystery boxes”
- “a function called process_data() that somehow does 11 different things”
- “process_data() style functions, no assertions, half the return values ignored”

## Defensive null checks & validation for cases that can't happen  (5 comments, 1.9% of tell-naming comments)
verdict: **inflated**, precision ~40% — Only 2/5 name defensive validation for impossible cases; two comments describe the OPPOSITE (code LACKING validation/auth) and one is about untested edge handling.

- “doing tryhard shit to “avoid an edge case” that never could have existed”
- “while is better about defensive programming it goes insane into it to where all the checks make the coder harder to debug and understand”

## Placeholder comments left in ("// rest of your code", "# ... your logic here")  (4 comments, 1.6% of tell-naming comments)
- [r/ChatGPT|6] Exactly, half the time I'm telling it "ok cool, that's a nice function. But it's never called anywhere in this code?" And it goes "oh thanks you're absolutely right, you are amazing, I love you. Here's a better example" and either gives you the exact same response or says "//// rest of the code goes
- [r/programminghorror|3] Other than the wrong error being thrown, it really just looks like placeholder code that is being used as an example to show inheritance. Don't really see any issue here. Pretty common stuff.
- [r/ExperiencedDevs|2] Yeah, just  "RUN"  Which is placeholder for "to not use it as opportunity to grow and only THEN leave".
- [r/codereview|1] tried to give you the entire pr template but reddit was being mean lol ! so you only get snippets :9) Checklist (Non-Negotiable)  # Code Quality  * No stubs / TODOs left * Errors handled where plausible * Types & schemas updated * Names match org vocabulary (no drift)  # Tests  * Unit tests added/up

## Leftover chat/markdown artifacts (``` fences, 'Here's the updated code', 'As an AI', 'Note:')  (3 comments, 1.2% of tell-naming comments)
- [r/ClaudeCode|1] the latest upload came through without readable content on my side, and some earlier uploaded files have expired. please re-upload/paste the post text and i’ll write the next comment.
- [r/AI_Agents|2] It's because it is an AI post.    All of the em dashes, the markdown format, the same sentence structure and expanded points that are irrelevant that no human would actually add.
- [r/ChatGPTCoding|1] Good catch!! Testing is an essential part of successful software development. I’ll add TDD tests to the application now.

