export const meta = {
  name: 'ai-isms-citation-extraction',
  description: 'Read mined Reddit posts and tally which AI-writing tells people actually cite; verify + synthesize',
  phases: [
    { title: 'Extract', detail: 'one agent per chunk file extracts CITED tells (not merely used)' },
    { title: 'Verify', detail: 'adversarial re-read of sampled chunks to catch over/under-counting' },
    { title: 'Synthesize', detail: 'merge into a final ranked, quoted, reconciled table' },
  ],
}

// Chunk paths are hardcoded so the run never depends on args serialization.
const DIR = "/Users/carterjohnson/Downloads/unslop-ai/unslop-ai-text/chunks"
const DEFAULT_CHUNKS = Array.from({ length: 20 }, (_, i) =>
  `${DIR}/chunk_${String(i).padStart(2, '0')}.txt`)
const chunkPaths = (args && Array.isArray(args.chunks) && args.chunks.length) ? args.chunks : DEFAULT_CHUNKS
// Keyword-pass (regex over the full 7,984-post on-topic corpus) high-confidence ranking, inlined.
const detTop = `em dash ("—") — 4.5% of on-topic posts (n=359)
"it's not just X, it's Y" — 1.9% (n=155)
bolded lead-in bullets (**Word:**) — 2.8% (n=220)
everything in bullet points / lists — 1.8% (n=143)
headers / bold / markdown everywhere — 1.4% (n=108)
game-changer — 1.6% (n=131)
"dive in" / "deep dive" — 1.6% (n=127)
delve — 1.5% (n=116)
"in conclusion" / "in summary" — 1.0% (n=76)
tapestry — 0.6% (n=51); unleash — 0.6% (n=49); testament to — 0.4% (n=31); underscore(s) — 0.3% (n=26); ever-evolving — 0.3% (n=27); embark — 0.3% (n=20)
"it's worth noting" — 0.4%; "it's important to note" — 0.6%; "in today's fast-paced world" — 0.4%
artifacts: "great question!" 0.4%; "let me know if/feel free" 0.4%; "I cannot/can't assist" 0.3%; "I hope this email finds you well" 0.3%; "knowledge cutoff" 0.3%; "I hope this helps" 0.3%; "would you like me to" 0.2%; "as an AI language model" 0.2%
"rule of three"/triads — 0.3%; perfectly structured/formulaic — 0.5%; rhetorical-question-then-answer — 0.2%
LOW-CONFIDENCE (regex matches the poster's OWN prose, not a citation — likely over-counted): "however/thus/hence" 6.3%; nuanced/nuance 2.3%; leverage 2.1%; "when it comes to" 1.9%; comprehensive 1.6%; navigate/navigating 1.5%; utilize 1.3%`
if (!chunkPaths.length) throw new Error("no chunk paths — aborting rather than synthesizing empty data")
log(`Extract over ${chunkPaths.length} chunk files`)

const CANON = `
DICTION (words): delve, leverage, utilize, seamless, robust, tapestry, testament to, realm, navigate/navigating, elevate, harness, unlock, unleash, showcase, foster, vibrant, boasts, comprehensive, meticulous, intricate, myriad, plethora, crucial, pivotal, nuanced, profound, game-changer, cutting-edge, ever-evolving, streamline, empower, holistic, synergy, treasure trove, bustling, captivating
PHRASING/CADENCE: "it's worth noting", "it's important to note", "when it comes to", "in today's fast-paced world", "rest assured", "look no further", "dive in / deep dive", "in conclusion", "first and foremost", "last but not least", "not only X but also Y", "it's not just X, it's Y", "more than just", "say goodbye to", "navigating the complexities", "unlock the power/potential", "elevate your", "without further ado", "that being said", "moreover/furthermore overuse", "the world of", "whether you're a X or a Y", uniform/robotic sentence rhythm, no contractions, overly hedged/balanced "on one hand / on the other", empty summary sentence that restates the prompt, positivity/sycophancy ("what a great question")
FORMAT/STRUCTURE: em dash overuse, bolded lead-in bullet points (**Word:** ...), emoji as bullets or section headers, everything turned into bullet lists, rule of three / triads, headers/bold everywhere, perfectly-structured / formulaic essay shape, title-case headings, numbered lists for everything, horizontal rule dividers
ARTIFACT (pasted giveaways): "as an AI language model", refusal boilerplate ("I cannot fulfill / I can't assist"), "would you like me to ...?", "I hope this helps!", "certainly! / absolutely!", knowledge-cutoff mentions, "let me know if you'd like..."
`.trim()

const EXTRACT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['posts_read', 'tells', 'novel_tells', 'quotes'],
  properties: {
    posts_read: { type: 'integer' },
    tells: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['tell', 'category', 'posts_citing'],
        properties: {
          tell: { type: 'string' },
          category: { type: 'string', enum: ['diction', 'phrasing', 'format', 'artifact'] },
          posts_citing: { type: 'integer', description: 'distinct posts in THIS file that clearly cite this tell' },
        },
      },
    },
    novel_tells: { type: 'array', items: { type: 'string' },
      description: 'tells an author cited that are NOT in the canonical list; short labels' },
    quotes: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['text', 'tell'],
        properties: { text: { type: 'string' }, tell: { type: 'string' } },
      },
      description: 'up to 3 short, vivid verbatim quotes from this file naming a tell',
    },
  },
}

phase('Extract')
const extractions = await parallel(chunkPaths.map((path, i) => () =>
  agent(
    `Read the file at ${path}. It contains ~30 Reddit posts (separated by "### POST") from AI-focused and SaaS/marketing/writing subreddits where people discuss how to spot AI-written text.\n\n` +
    `For EACH post, identify which specific AI-writing "tells" the author is CITING or COMPLAINING ABOUT as a marker of AI text. CRITICAL: count a tell only when the author is calling it out as an AI marker, NOT when the author merely happens to use that word/structure in their own writing. (e.g. an author who writes "however," in their own post is NOT citing "however" as a tell.)\n\n` +
    `Use this canonical vocabulary for the "tell" field so labels aggregate cleanly; match to the closest canonical label. If a post cites something genuinely not covered, list it under novel_tells.\n\nCANONICAL TELLS:\n${CANON}\n\n` +
    `posts_citing = the number of DISTINCT posts in THIS file that clearly cite that tell. Return posts_read = number of posts you actually saw. Also return up to 3 short verbatim quotes that vividly name a tell.`,
    { label: `extract:${i}`, phase: 'Extract', schema: EXTRACT_SCHEMA }
  )
)).then(rs => rs.filter(Boolean))

// ---- aggregate in plain JS (no barrier needed beyond this collect) ----
const tally = {}        // tell -> {category, posts}
let totalPosts = 0
const novel = {}
const quotes = []
for (const ex of extractions) {
  totalPosts += ex.posts_read || 0
  for (const t of ex.tells || []) {
    const key = t.tell.trim().toLowerCase()
    if (!tally[key]) tally[key] = { tell: t.tell.trim(), category: t.category, posts: 0 }
    tally[key].posts += t.posts_citing || 0
  }
  for (const n of ex.novel_tells || []) {
    const k = n.trim().toLowerCase(); novel[k] = (novel[k] || 0) + 1
  }
  for (const q of ex.quotes || []) quotes.push(q)
}
const ranked = Object.values(tally)
  .map(x => ({ ...x, share_pct: totalPosts ? +(100 * x.posts / totalPosts).toFixed(1) : 0 }))
  .sort((a, b) => b.posts - a.posts)
const novelRanked = Object.entries(novel).map(([k, c]) => ({ tell: k, chunks: c }))
  .sort((a, b) => b.chunks - a.chunks)
log(`Extracted ${totalPosts} posts; ${ranked.length} distinct tells; ${novelRanked.length} novel labels`)
if (totalPosts === 0 || ranked.length === 0)
  throw new Error(`extraction produced no data (${extractions.length} extractions) — aborting`)

// ---- Verify: adversarial re-read to catch over/under-counting ----
phase('Verify')
const topForCheck = ranked.slice(0, 25)
const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['assessment', 'overcounted', 'undercounted', 'missing_important'],
  properties: {
    assessment: { type: 'string' },
    overcounted: { type: 'array', items: { type: 'string' }, description: 'tells the ranking likely inflates' },
    undercounted: { type: 'array', items: { type: 'string' }, description: 'tells likely under-counted' },
    missing_important: { type: 'array', items: { type: 'string' }, description: 'important tells absent from the top list' },
  },
}
const sampleChunks = chunkPaths.filter((_, i) => i % 4 === 0).slice(0, 6)
const verdicts = await parallel(sampleChunks.map((path, i) => () =>
  agent(
    `You are auditing a tally of AI-writing tells built from many Reddit posts. Here is the current TOP-25 ranked tally (by posts citing):\n` +
    topForCheck.map((t, n) => `${n + 1}. ${t.tell} (${t.category}) — ${t.posts} posts, ${t.share_pct}%`).join('\n') +
    `\n\nRe-read the posts in ${path} carefully. Judge whether this ranking faithfully reflects what authors actually cite. Be adversarial: flag tells that look over-counted (people use the word but rarely cite it as a tell), under-counted, or important tells missing from the top list entirely.`,
    { label: `verify:${i}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  )
)).then(rs => rs.filter(Boolean))

// ---- Synthesize: one agent reconciles everything into the final brief ----
phase('Synthesize')
const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['final_ranking', 'category_summary', 'best_quotes', 'reconciliation_notes'],
  properties: {
    final_ranking: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['rank', 'tell', 'category', 'share_pct', 'confidence', 'note'],
        properties: {
          rank: { type: 'integer' }, tell: { type: 'string' },
          category: { type: 'string' }, share_pct: { type: 'number' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
          note: { type: 'string', description: 'why it reads as AI + what to do instead, one line' },
        },
      },
    },
    category_summary: { type: 'string', description: 'short prose: diction vs phrasing vs format vs artifact, what dominates' },
    best_quotes: { type: 'array', items: { type: 'string' } },
    reconciliation_notes: { type: 'string', description: 'where citation-pass and keyword-pass agree/disagree' },
  },
}
const synthesis = await agent(
  `You are writing the evidence brief for a Reddit post about AI-writing tells ("AI-isms") to avoid.\n\n` +
  `SOURCE 1 — citation pass (humans read ${totalPosts} on-topic posts and tallied which tells authors actually CITE):\n` +
  ranked.slice(0, 40).map((t, n) => `${n + 1}. ${t.tell} (${t.category}) — ${t.posts} posts, ${t.share_pct}%`).join('\n') +
  `\n\nNOVEL tells surfaced (not in canonical list), by how many chunks raised them:\n` +
  novelRanked.slice(0, 25).map(n => `- ${n.tell} (${n.chunks})`).join('\n') +
  `\n\nSOURCE 2 — keyword pass (deterministic regex over the same corpus), high-confidence ranking:\n${detTop}\n\n` +
  `SOURCE 3 — audit verdicts on over/under-counting:\n` +
  verdicts.map((v, n) => `Auditor ${n + 1}: ${v.assessment}\n  over: ${v.overcounted.join('; ')}\n  under: ${v.undercounted.join('; ')}\n  missing: ${v.missing_important.join('; ')}`).join('\n\n') +
  `\n\nSOURCE 4 — verbatim quotes the extractors pulled (choose the best from THIS list only):\n` +
  quotes.slice(0, 80).map(q => `- "${(q.text || '').replace(/\n/g, ' ').slice(0, 200)}" [${q.tell || ''}]`).join('\n') +
  `\n\nProduce the FINAL reconciled ranking (~25 items) of AI-writing tells people should avoid, grouped conceptually but ranked by how much the communities actually flag them. For each: a confidence rating (weigh agreement between the two passes and the audit) and a one-line "why it reads as AI / what to do instead". Fold strong novel tells in. Pick the best verbatim quotes (short, vivid, real). Note where the two passes disagree.\n\n` +
  `STRICT GROUNDING RULES: Use ONLY the numbers given above. The share_pct for each tell MUST come from SOURCE 1 (citation pass) when present; if a tell only appears in SOURCE 2, label it clearly. NEVER invent percentages, "airtime", or subreddit counts — SOURCE 2 here is a text list without per-tell sub-counts, so do not claim "appears in N of M subs" for anything. Do not run tools or read files; work only from the data in this prompt. If a field is unknown, omit it rather than guessing. Quotes must be copied verbatim from what the extractors returned (the quotes list), not reconstructed.`,
  { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA, effort: 'high' }
)

return {
  totalPostsRead: totalPosts,
  citationRanking: ranked,
  novelTells: novelRanked,
  auditVerdicts: verdicts,
  synthesis,
  quotesRaw: quotes.slice(0, 60),
}
