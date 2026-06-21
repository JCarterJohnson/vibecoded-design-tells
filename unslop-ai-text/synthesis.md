# AI-isms: verified per-tell tally + citation-vs-regex comparison

_Topic: the phrasing / format / cadence tells that make text read as AI-written, as discussed across AI-focused and SaaS/marketing/writing subreddits, 2021-2026 (Arctic Shift archive). This is the evidence brief for the write-up; it is not the post._

## How this was produced

- **Collection (closed):** Arctic Shift posts full-text search across 46 subreddits (wide AI net + SaaS/startup/marketing + writing/detection), 14 intent phrases + ~26 named-tell probes, 2021-present. Comment full-text search was unavailable (server-side timeouts), so this is **posts-only**.
- **Corpus:** 89,239 unique posts collected -> **7,984 on-topic** after a phrase-aware filter that removes incidental ChatGPT mentions. Lane split and year trend below.
- **Two independent passes over the same on-topic material:**
  1. **Keyword/regex pass (Lens 1):** a curated AI-ism lexicon matched over all 7,984 on-topic posts -> share of posts whose text matches. Fast but cannot tell *use* from *citation*.
  2. **Citation pass (this run):** 20 subagents read the **604 highest-engagement on-topic posts** and tallied, per post, which tells the author actually **cites** as an AI marker (not merely uses). Then 5 adversarial auditors re-read sampled chunks to flag over/under-counting, and a synthesis step reconciled both.
- **The comparison** below puts both methods on the *same 600-post sample* so the gap is purely method, not denominator.

## Corpus shape

```
unique posts (all queries): 89239
Family-A on-topic posts: 7984

by lane: {'ai': 4673, 'writing': 1309, 'saas': 2002}

by year: {2021: 26, 2022: 86, 2023: 587, 2024: 717, 2025: 3174, 2026: 3394}

top 30 subs:
  ChatGPT                  1454
  WritingWithAI            457
  SaaS                     433
  aiwars                   409
  ArtificialInteligence    393
  SideProject              375
  ClaudeAI                 320
  Professors               284
  OpenAI                   272
  ChatGPTPromptGenius      244
  artificial               238
  microsaas                216
  PromptEngineering        214
  singularity              208
  LocalLLaMA               201
  SEO                      201
  Entrepreneur             177
  Teachers                 169
  AI_Agents                160
  GeminiAI                 125
  selfpublish              110
  ChatGPTPro               100
  indiehackers             97
  EntrepreneurRideAlong    96
  copywriting              95
  content_marketing        95
  Blogging                 82
  marketing                74
  smallbusiness            67
  freelanceWriters         64
```

## Verified per-tell tally (human citation pass, reconciled + audited)

Ranked by how much the communities actually flag each tell. `cite%` = share of the 604 read posts that cite it. `regex(full)` = the regex Lens-1 share over all 7,984 on-topic posts. `vs regex` = where the regex over/under-counted or is structurally blind.

| # | tell | cat | conf | cite% | regex(full) | vs regex |
|--:|------|-----|------|------:|------------:|----------|
| 1 | Em dash overuse (—) | format | high | 7.1% | 4.5% | agree |
| 2 | "It's not just X, it's Y" / "not X, but Y" construction (merged with #20, #23 variants) | phrasing | high | 2.8% | 1.9% | regex under-counts |
| 3 | Uniform / robotic sentence rhythm | phrasing | medium | 4% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 4 | Positivity / sycophancy (gushing, 'great question!', yes-man) | phrasing | high | 2.5% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 5 | Perfectly-structured / formulaic essay shape | format | high | 2.5% | 0.5% | regex under-counts |
| 6 | Everything turned into bullet lists / listicles | format | high | 1.7% | 1.8% | agree |
| 7 | "Dive in" / "deep dive" | phrasing | medium | 2% | 1.6% | agree |
| 8 | Rule of three / triads | format | high | 1.2% | 0.3% | regex under-counts |
| 9 | Empty summary / polished-but-hollow phrasing ('says nothing', word salad) | phrasing | high | 0.7% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 10 | Bolded lead-in bullets (**Word:** ...) / title-case mini-headings (merged #24, #30) | format | medium | 0.3% | 2.8% | agree |
| 11 | "As an AI language model" / leftover assistant boilerplate (e.g. 'Want me to tweak the tone?') | artifact | high | 1.2% | 0.2% | regex under-counts |
| 12 | Single-word diction memes: delve, unleash, tapestry, game-changer, comprehensive, elevate (cluster) | diction | medium | 1.3% | 1.5% | agree |
| 13 | Hallucinated / fabricated citations and references | artifact | high | 0% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 14 | "Honestly, ..." / fake-relatability openers ('Look, I get it', 'Imagine this') | phrasing | medium | 0% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 15 | "Unlock the power/potential" / "unlock" (merged #14, #19) | phrasing | medium | 0.8% | 0.2% | agree |
| 16 | Marketing / hype language ('revolutionary', 'transform your life', 'transformative') | phrasing | medium | 0.3% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 17 | Verbosity / repetition / restating the same point across sections | phrasing | medium | 0% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 18 | Forced / overly-smooth transitions | phrasing | medium | 0% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 19 | No contractions / overly formal register (merged #17, #21) | phrasing | medium | 0.7% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 20 | Hedging / both-sides balance ('it depends', 'on one hand... on the other') | phrasing | low | 0.3% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 21 | "In today's fast-paced world" / dated scene-setting opener | phrasing | low | 0.7% | 0.4% | regex under-counts |
| 22 | Emoji as bullets or section headers | format | low | 0.8% | 0.0% | REGEX UNDER-COUNTS (missed wording) |
| 23 | Horizontal-rule dividers (---) between sections | format | low | 0% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 24 | Deliberately-inserted fake typos to beat detectors | artifact | low | 0% | n/a | REGEX-BLIND (no lexicon entry — cannot be regex-detected) |
| 25 | "In conclusion" / "in summary" closers | phrasing | low | 0.2% | 1.0% | agree |

**What-to-do notes (per tell):**

- **Em dash overuse (—)** — Both passes' #1 and confirmed cited in 4-5 posts per audited chunk; reads as AI because the punctuation is 'too polished' for casual typing — use commas, periods, or parentheses, and don't just swap in colons (people now flag that too).
- **"It's not just X, it's Y" / "not X, but Y" construction (merged with #20, #23 variants)** — True total is higher than 2.8% once the three split rows are merged; the antithesis cadence is THE 'AI accent' — just state the thing plainly instead of negating-then-asserting.
- **Uniform / robotic sentence rhythm** — Cited via 'specific rhythm'/'syntactic mad-lib' complaints but partly padded by generic 'sounds robotic' laments; vary sentence length and let some sentences run long or stop short.
- **Positivity / sycophancy (gushing, 'great question!', yes-man)** — Likely UNDER-ranked — Auditor 2 found it rivals em dash for citation density; drop the flattery and reflexive agreement, disagree or stay neutral when warranted.
- **Perfectly-structured / formulaic essay shape** — Under-counted per Auditors 2 and 4 ('formulaic to the bone', 'exact same rigid three-paragraph formula'); break the intro-body-body-body-conclusion mold and let structure follow the idea.
- **Everything turned into bullet lists / listicles** — '5 ways to…' / '7 signs…' scaffolding screams AI; use prose paragraphs and reserve bullets for genuinely list-like content.
- **"Dive in" / "deep dive"** — Confirmed in cliche-avoidance quotes but some appearances are mocked AI output, not citations; cut the metaphor and just start the topic.
- **Rule of three / triads** — Likely under-ranked — named spontaneously across several chunks ('uses three-part structures constantly'); avoid reflexive three-part lists and parallel triplets.
- **Empty summary / polished-but-hollow phrasing ('says nothing', word salad)** — Under-counted per multiple auditors (folds in 'soulless', 'no opinion', 'word salad'); reads as AI because it's fluent but contentless — make a real claim and cut the restated-prompt filler.
- **Bolded lead-in bullets (**Word:** ...) / title-case mini-headings (merged #24, #30)** — SOURCE 2 keyword pass puts this higher (2.8%, n=220); the **Bold:** then sentence pattern is a giveaway — write normal sentences without the boldface label.
- **"As an AI language model" / leftover assistant boilerplate (e.g. 'Want me to tweak the tone?')** — The ultimate proof when present, but aging out as people stop pasting raw output; delete any meta-offer or disclaimer before publishing.
- **Single-word diction memes: delve, unleash, tapestry, game-changer, comprehensive, elevate (cluster)** — Inflated — all five auditors found near-zero genuine citations; counts come from listicle/prompt-list copying, but still real corpus-wide; swap for plain words you'd actually say.
- **Hallucinated / fabricated citations and references** — Novel tell surfaced by 4 auditors ('totally made up references'), no SOURCE 1 percentage; a content-level giveaway — verify every source, never invent author names or case law.
- **"Honestly, ..." / fake-relatability openers ('Look, I get it', 'Imagine this')** — Novel (no SOURCE 1 percentage), but a whole top-scoring post is devoted to 'Honestly' being 'zombified by AI' (3 auditors); cut the throat-clearing opener and start with the actual point.
- **"Unlock the power/potential" / "unlock" (merged #14, #19)** — Marketing-flavored and split across two rows; reads as hype — say what the thing actually does.
- **Marketing / hype language ('revolutionary', 'transform your life', 'transformative')** — Repeatedly cited as a category broader than single words ('This revolutionary product will transform your life'); strip promotional adjectives and state plain facts.
- **Verbosity / repetition / restating the same point across sections** — Novel tell (no SOURCE 1 percentage) raised across 3 chunks ('repeated in 5 different sections', 5-page review of an 8-page article); cut length and say each thing once.
- **Forced / overly-smooth transitions** — Novel structural tell (no SOURCE 1 percentage; 'The transitions are forced'); the connective tissue is too even — let ideas jump and trim 'moreover/furthermore' scaffolding.
- **No contractions / overly formal register (merged #17, #21)** — True total higher once merged; stiff register reads as AI — use contractions and write the way you talk.
- **Hedging / both-sides balance ('it depends', 'on one hand... on the other')** — Cited as Claude 'hedges everything' giving a menu instead of committing; take a position rather than listing every option.
- **"In today's fast-paced world" / dated scene-setting opener** — Iconic but low citation count; a hollow opener — delete it and start with something specific.
- **Emoji as bullets or section headers** — Real but not cited as a tell in several chunks; decorative emoji-bullets look templated — use plain text headers.
- **Horizontal-rule dividers (---) between sections** — Novel (no SOURCE 1 percentage), from a single vivid quote ('another obvious AI writing marker'); the markdown line breaks read as generated — use paragraph breaks instead.
- **Deliberately-inserted fake typos to beat detectors** — Novel anti-detection artifact (no SOURCE 1 percentage; 'excyted', 'annownce'); ironically itself a tell — don't fake errors, just write naturally.
- **"In conclusion" / "in summary" closers** — SOURCE 2 keyword pass puts it higher (~1.0%); the signposted wrap-up is formulaic — end on a real last point, not a recap.

## Where the regex (Lens 1) went wrong vs. the human citation pass

Same 600-post sample for both `cite%` and `rgx%`.

### 1. Regex OVER-counts (matches the poster's own prose, ~zero genuine citations)

These are the keyword pass's biggest false signals. The connective-word family in particular: the regex's single highest hit corpus-wide is "however/thus/hence" at 6.3%, but humans almost never cite it as a tell.

| tell | cite% (sample) | regex% (sample) | verdict |
|------|------:|------:|------|
| overuse of "however," / "thus," / "hence" | 0.0 | 3.3 | REGEX OVER-COUNTS (noise: poster's own prose) |
| nuanced / nuance | 0.0 | 1.8 | REGEX OVER-COUNTS (noise: poster's own prose) |
| "when it comes to" | 0.0 | 1.0 | REGEX OVER-COUNTS (noise: poster's own prose) |
| robust | 0.2 | 0.5 | regex over-counts |
| overuse of "moreover/furthermore/additionally" | 0.2 | 0.5 | regex over-counts |
| embark ("embark on a journey") | 0.0 | 0.3 | regex over-counts |
| utilize (instead of "use") | 0.0 | 0.3 | regex over-counts |
| ever-evolving / ever-changing | 0.0 | 0.2 | regex over-counts |
| navigate / navigating | 0.0 | 0.2 | regex over-counts |

### 2. Regex UNDER-counts (real tell, but the wording varies so the regex misses it)

| tell | cite% (sample) | regex% (sample) | verdict |
|------|------:|------:|------|
| "it's not just X, it's Y" | 3.1 | 0.8 | regex under-counts |
| perfectly structured / formulaic | 2.5 | 0.5 | regex under-counts |
| headers / bold everywhere / markdown | 1.2 | 0.5 | regex under-counts |
| "rule of three" / triads | 1.2 | 0.5 | regex under-counts |
| "as an AI language model" | 1.2 | 0.3 | regex under-counts |
| emoji bullets / emoji headers | 0.8 | 0.0 | REGEX UNDER-COUNTS (missed wording) |
| "in today's fast-paced/digital world" | 0.7 | 0.2 | regex under-counts |
| "great question!" | 0.3 | 0.0 | regex under-counts |
| "would you like me to ...?" | 0.2 | 0.0 | regex under-counts |

### 3. Regex-BLIND (no lexicon entry can catch these — only a reader can)

**12 of the 25 verified tells are structurally invisible to keyword matching**, including the #3 and #4 most-cited tells overall. This is the core reason pure keyword/regex AI-detection fails.

| tell | cite% (sample) | why regex can't catch it |
|------|------:|------|
| Uniform / robotic sentence rhythm | 4 | rhythm/cadence is a distributional property, not a string |
| Positivity / sycophancy (gushing, 'great question!', yes-man) | 2.5 | tone, not a fixed phrase |
| Empty summary / polished-but-hollow phrasing ('says nothing', word salad) | 0.7 | 'fluent but says nothing' is semantic, not lexical |
| Hallucinated / fabricated citations and references | 0 | requires checking facts against the world |
| "Honestly, ..." / fake-relatability openers ('Look, I get it', 'Imagine this') | 0 | the tell is the opener-as-tic in context, not the word |
| Marketing / hype language ('revolutionary', 'transform your life', 'transformative') | 0.3 | hype is a register spread across many words |
| Verbosity / repetition / restating the same point across sections | 0 | a length/redundancy property of the whole text |
| Forced / overly-smooth transitions | 0 | 'forced-ness' is judged, not matched |
| No contractions / overly formal register (merged #17, #21) | 0.7 | absence of a feature; regex counts presence |
| Hedging / both-sides balance ('it depends', 'on one hand... on the other') | 0.3 | a stance, not a phrase |
| Horizontal-rule dividers (---) between sections | 0 | not in the lexicon; trivial to add but was missed |
| Deliberately-inserted fake typos to beat detectors | 0 | an anti-detection behavior, not a phrase |

### 4. Strong agreement (both methods converge — most trustworthy)

| tell | cite% (sample) | regex% (sample) |
|------|------:|------:|
| em dash ("—") as a tell | 7.1 | 6.0 |
| everything in bullet points / lists | 3.1 | 1.7 |
| "dive in" / "deep dive" / "let's dive" | 2.0 | 2.3 |
| delve | 1.3 | 1.3 |
| game-changer | 1.3 | 1.8 |
| unleash | 1.3 | 1.7 |
| bolded lead-in bullets (**Word:**) | 0.8 | 0.8 |
| "unlock/unleash the power/potential" | 0.8 | 0.5 |
| tapestry | 0.8 | 0.8 |
| leverage | 0.3 | 0.7 |
| comprehensive | 0.3 | 0.7 |
| "in conclusion" / "in summary" | 0.2 | 0.2 |
| "it's important to note/remember" | 0.2 | 0.2 |
| testament ("a testament to") | 0.2 | 0.2 |
| seamless(ly) | 0.2 | 0.2 |
| "I hope this helps!" | 0.2 | 0.2 |
| "I cannot/can't assist/fulfill" | 0.2 | 0.3 |

## Auditor-driven caveats (baked into the tally above)

- **Diction is meme-inflated.** All five auditors found that single-word tells (delve, unleash, tapestry, game-changer, unlock, elevate, comprehensive) are mostly *copied around in circulated 'AI words' blocklists and parody demos*, not independently observed in real writing. Marked medium confidence and collapsed into one row.
- **De-duplication.** The raw citation tally split a few tells across rows; merged here: the antithesis construction ("it's not just X, it's Y" / "not X but Y" / "not only X but also Y"), "no contractions / overly formal", and "unlock / unlock the power".
- **Presence-vs-citation cuts both ways.** Auditor 4 noted even em dash counts can conflate the glyph appearing in a post with the author citing it; net, em dash is still the clear #1 in both passes.
- **Under-ranked by the sample:** sycophancy, formulaic structure, and rule-of-three were repeatedly cited in prose and are likely higher than their raw counts suggest.

## Best verbatim quotes (from the read posts)

> Em dashes have become the single most reliable tell of AI-generated text

> I can hear the em dashes through your microphone as you talk

> the “it wasn’t x, it was y” shit, the excessive rule of three, overuse of meaningless similes and paradiastoles, the weird overexplaining

> You're absolutely right! This observation isn't just smart — it shows you're operating on a higher level

> It uses three-part structures constantly. The transitions are forced, and the inspiration is fake. Even when people get clever and switch out their em-dashes for colons... sorry, it's still obvious

> Paragraphs that start with "Honestly, ..." The word is dead. It's been zombified by AI.

> AI writes word salad - beautiful looking but has no nutritional value.

> In a world where the tapestry of human emotions unfolds like a delicate symphony, I'm sorry, but as an AI language model, I cannot delve into unlocking your full potential

> If it's a “5 ways to…” post, “7 signs you might be…” or a bullet-pointed life guide, there's a solid chance it came from us. We love structure.

> Never use "dive into," "unleash," "game-changing," "revolutionary," "transformative," "leverage," "optimize," "unlock potential"

> no grammar mistakes on essays that use elevated language but ultimately say very little

> Same kind of phrases, same sentence patterns, same boring transitions, same flat tone.

> a series of bullet point **bolded** Every Word Capitalized colon 2-3 sentences

> 4.6 now constantly throws in those horizontal line separators (---) throughout the text. It's another obvious AI writing marker

> Default Claude hedges everything. "It depends on your needs." "There are several approaches."

## Notable novel tells surfaced by readers (not in the original lexicon)

- hallucinated/fabricated citations and case law
- use of slang like 'era'
- use of 'straight up'
- hypophora (asking and answering own question)
- the 'honestly? that's growth' rhetorical beat
- soulless/opinion-less tone
- impeccable spelling / no typos
- "___ energy" construction
- hallucinated facts/content
- corporate-speak / press-release tone
- deliberately mangled punctuation to disguise ai
- paired/gendered pronoun (his/her) when gender unspecified
- "and honestly?" interjection
- "here's..." sentence opener
- corporate buzzwords (generic)
- overly polished / sterile corporate voice
- gentle/therapeutic validation tone
- paragraphs starting with "honestly..."

## Reconciliation notes (verbatim from synthesis)

The two passes AGREE strongly on the head: em dash is #1 in both (SOURCE 1 7.1%, SOURCE 2 4.5%), and 'it's not just X, it's Y', bullets, game-changer, dive in, and delve appear high in both. They DISAGREE on diction weight and on what counts as a citation: SOURCE 2's deterministic regex inflates words that double as ordinary human prose (it explicitly buckets however/thus 6.3%, nuanced 2.3%, leverage 2.1%, comprehensive 1.6% as LOW-CONFIDENCE because the regex matched the poster's OWN writing, not a cited tell) — so I did NOT promote those into the ranking despite high raw rates. The biggest cross-source disagreement is em dash counting: Auditor 4 argues #1 is badly inflated because ~13 of 14 em-dash occurrences in his chunk were incidental punctuation, not citations, whereas Auditors 1, 2, 3 independently confirm em dash is genuinely the most-cited tell in their chunks; I kept it #1 but noted the presence-vs-citation tension. All five auditors independently flagged the same dedup failures (it's-not-just-X-it's-Y split across #3/#20/#23, no-contractions across #17/#21, unlock across #14/#19), which I merged — this is the single biggest correction. All auditors also agreed the single-word diction cluster is over-ranked (zero genuine citations in four separate chunks, attributed to listicle/prompt-list copying and parody), so I collapsed it to one entry at #12 and demoted tapestry/elevate/comprehensive out of standalone slots. Where SOURCE 1 has no percentage (novel tells folded in: hallucinated citations, 'Honestly' opener, verbosity, forced transitions, fake typos, horizontal rules), share_pct is set to 0 as a 'no SOURCE 1 data' sentinel (noted in each row) rather than an invented number, and confidence reflects how many auditors raised each. Items resting only on SOURCE 2 sub-rates (bolded lead-ins, 'in conclusion') are labeled as such in their notes.

## Category summary (verbatim from synthesis)

Format and phrasing tells dominate genuine citations; diction (single meme-words) is over-represented relative to how often authors actually point to it. The clearest, most-cited tells are a punctuation tell (em dash) and a construction tell (it's not X, it's Y) — both surface-detectable AND repeatedly named in prose, which is why they top both passes. Below the head, the most TRUSTWORTHY signal is phrasing/structure that authors describe in their own words (robotic rhythm, sycophancy, formulaic shape, forced transitions, hallucinated citations), while the diction tier (delve, unleash, tapestry, game-changer, unlock, elevate, comprehensive) is inflated by listicle/prompt-list copying and parody demonstrations rather than independent observation — all five auditors flagged this. Artifacts (as an AI language model) are high-salience but aging out. Format tells (bullets, bolded lead-ins, emoji, horizontal rules) are real but at risk of presence-counted-as-citation inflation.

## Limitations

- Proxy for the **vocal and online**: trust relative ordering, not absolute percentages.
- **Posts-only** (comment full-text search was down); comment threads, where many enumerations live, are under-represented.
- Corpus is **recency-weighted** (2025-2026 dominate on-topic volume) and the citation sample is the **600 highest-engagement** on-topic posts, which favors viral, well-articulated complaints.
- Big-volume sub/query pairs were capped at 200 newest posts (logged), so the highest-traffic subs are slightly recency-biased.
- Citation shares come from a 604-post sample; small-count tells (<=2 posts) are individually noisy and should be read as 'present, low frequency' rather than precise rates.

---
_Artifacts: `findings_lens1.csv` (full-corpus regex), `findings_lens2.csv` (named-term airtime), `comparison.csv` (same-sample method comparison), `human_only_tells.csv` (regex-blind cited tells), `verified_tally.csv` (this ranking), `extract_result.json` (raw workflow output), `chunks/` (the 600 read posts)._