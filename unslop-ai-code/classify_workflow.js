export const meta = {
  name: 'ai-code-tells-classify',
  description: 'LLM-classify on-topic Reddit comments/posts into a fixed taxonomy of AI-code tells, then adversarially verify the top tells',
  phases: [
    { title: 'Classify comments', detail: 'tag each candidate comment with the code tells it names (sonnet)' },
    { title: 'Classify posts', detail: 'same taxonomy over the post sample (sonnet)' },
    { title: 'Verify top tells', detail: 'skeptic audits the quotes assigned to each top tell (opus)' },
  ],
}

// Config baked in (args plumbing was unreliable). Paths + line counts are stable.
const DIR = '/Users/carterjohnson/Downloads/unslop-ai/unslop-ai-code'
const CF = DIR + '/candidates.jsonl'
const PF = DIR + '/candidates_posts.jsonl'
const NC = 2136, NP = 1500, BATCH = 40

const TAXONOMY = `You are auditing how Reddit developers describe TELLS that CODE was written by AI.
You will get a numbered batch of items (each a real comment/post). For EACH item,
decide which specific CODE-LEVEL tells, if any, the author NAMES. Return the tell
codes from this fixed list (a comment may name 0, 1, or several):

COMMENTS & DOCS
  over_comment        comments on nearly every line / narrating the obvious / over-explaining in comments
  redundant_docstring docstring/JSDoc/header block on every trivial function, often just restating its name
  placeholder_comment left-in placeholder/ellipsis comments: "// rest of your code", "# ... your logic here", "// TODO implement", "// (existing code)"
NAMING
  verbose_naming      overly long / self-documenting / robotic identifier names
  generic_naming      generic placeholder names (data, result, temp, foo, item, thing, myVariable)
ERROR HANDLING
  excessive_try       try/except or try/catch wrapped around everything / over-broad error handling / swallowed errors
  over_validation     defensive null/None checks & input validation for cases that cannot happen
STRUCTURE
  over_engineered     needless abstraction / too many layers, classes, or tiny helper functions for a simple task
  boilerplate_tutorial boilerplate, scaffolding, tutorial/textbook-shaped, "looks like a sample app / demo"
  reinvent_wheel      hand-rolls what a standard library or existing package already provides
STYLE / FORMAT
  too_clean           suspiciously clean/consistent/perfect formatting; no human messiness, no typos, uniform style
  style_mismatch      style/conventions don't match the surrounding codebase; a sudden shift mid-file
  type_everywhere     type hints/annotations added everywhere, especially where unusual for the language/project
OUTPUT / LOGGING
  emoji               emoji in code, comments, console logs, or commit messages
  excess_logging      print/console.log debugging left in; chatty "Successfully ...!" log lines
ARTIFACTS
  chat_artifact       leftover chat/markdown artifacts: triple-backtick fences, "Here's the updated code", "Certainly!", "As an AI", "Note:" preambles inside the code
CORRECTNESS
  hallucinated_api    calls to nonexistent/outdated APIs or made-up libraries; plausible-looking but subtly wrong logic
  inconsistent_skill  weirdly mixed skill level: advanced code beside beginner mistakes; works but author can't explain it
UMBRELLA / NONE
  umbrella_looks_ai   says it's obviously AI / "AI slop" / "you can just tell" / "too perfect" WITHOUT naming any specific code feature
  none                not about a code-level tell at all (careers, ethics, news, productivity, jokes, general debate)

RULES
- Tag a specific code tell ONLY if the author actually describes that property of the code.
- Bare "AI slop" / "obviously AI" with no specific feature => umbrella_looks_ai (NOT a specific tell).
- Career/jobs/ethics/"will AI replace us"/news/percentages => none.
- Do not infer tells that aren't stated. When unsure between a specific tell and umbrella, choose umbrella_looks_ai.
- Quote-grounded only: base the tag on words in the item.`

function batches(n) {
  const out = []
  for (let s = 0; s < n; s += BATCH) out.push([s, Math.min(s + BATCH, n)])
  return out
}

const CLS_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          i: { type: 'integer' },
          codes: { type: 'array', items: { type: 'string' } },
        },
        required: ['i', 'codes'],
      },
    },
  },
  required: ['results'],
}

function classifyPrompt(file, lo, hi) {
  const L1 = lo + 1, L2 = hi // line numbers (item i == line-1)
  return `${TAXONOMY}

Read your batch of items (one JSON object per line, fields i/sub/score/thread/body) by running:
\`\`\`
sed -n '${L1},${L2}p' ${file}
\`\`\`
That gives items with index i from ${lo} to ${hi - 1}. Classify EACH one.
Return {"results":[{"i":<index>,"codes":[<tell codes>]}, ...]} covering every item in the slice.
Use [] codes only if you would otherwise tag none — prefer the explicit "none" code. Codes MUST come from the fixed list.`
}

// ---------- Phase 1: classify comments ----------
phase('Classify comments')
const cBatches = batches(NC)
log(`classifying ${NC} comments in ${cBatches.length} batches of ${BATCH}`)
const cRes = await parallel(cBatches.map(([lo, hi]) => () =>
  agent(classifyPrompt(CF, lo, hi), {
    label: `c:${lo}-${hi}`, phase: 'Classify comments',
    schema: CLS_SCHEMA, model: 'sonnet', effort: 'low',
  }).then(r => (r && r.results) ? r.results.map(x => ({ ...x, src: 'c' })) : [])
))
const comment = cRes.filter(Boolean).flat()

// ---------- Phase 2: classify posts ----------
phase('Classify posts')
const pBatches = batches(NP)
log(`classifying ${NP} posts in ${pBatches.length} batches of ${BATCH}`)
const pRes = await parallel(pBatches.map(([lo, hi]) => () =>
  agent(classifyPrompt(PF, lo, hi), {
    label: `p:${lo}-${hi}`, phase: 'Classify posts',
    schema: CLS_SCHEMA, model: 'sonnet', effort: 'low',
  }).then(r => (r && r.results) ? r.results.map(x => ({ ...x, src: 'p' })) : [])
))
const post = pRes.filter(Boolean).flat()

// ---------- aggregate ----------
const SPECIFIC = ['over_comment','redundant_docstring','placeholder_comment','verbose_naming',
  'generic_naming','excessive_try','over_validation','over_engineered','boilerplate_tutorial',
  'reinvent_wheel','too_clean','style_mismatch','type_everywhere','emoji','excess_logging',
  'chat_artifact','hallucinated_api','inconsistent_skill']
function tally(items) {
  const c = {}; let named = 0
  for (const it of items) {
    const codes = (it.codes || []).filter(x => x && x !== 'none')
    if (codes.some(x => x !== 'umbrella_looks_ai')) named++
    for (const code of codes) c[code] = (c[code] || 0) + 1
  }
  return { counts: c, named, total: items.length }
}
const cAgg = tally(comment), pAgg = tally(post)

// indices per code (comments) for the verification phase
const idxByCode = {}
for (const it of comment) for (const code of (it.codes || [])) {
  if (code === 'none') continue
  ;(idxByCode[code] = idxByCode[code] || []).push(it.i)
}

// rank specific tells by combined comment+post count
const ranked = [...SPECIFIC, 'umbrella_looks_ai'].map(code => ({
  code,
  comments: cAgg.counts[code] || 0,
  posts: pAgg.counts[code] || 0,
  comment_share_pct: +(100 * (cAgg.counts[code] || 0) / Math.max(1, cAgg.named)).toFixed(1),
})).sort((a, b) => b.comments - a.comments)

// ---------- Phase 3: adversarial verification of the top tells ----------
phase('Verify top tells')
const VER_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    code: { type: 'string' },
    sampled: { type: 'integer' },
    genuine: { type: 'integer' },
    precision_pct: { type: 'number' },
    verdict: { type: 'string', enum: ['solid', 'mostly', 'inflated', 'artifact'] },
    note: { type: 'string' },
    best_quotes: { type: 'array', items: { type: 'string' } },
  },
  required: ['code', 'sampled', 'genuine', 'precision_pct', 'verdict', 'note', 'best_quotes'],
}
const topForVerify = ranked.filter(r => r.code !== 'umbrella_looks_ai' && r.comments >= 5).slice(0, 14)
const verify = await parallel(topForVerify.map(r => () => {
  const idx = (idxByCode[r.code] || []).slice(0, 40)
  const lines = idx.map(i => i + 1).join(',')
  const def = TAXONOMY.split('\n').find(l => l.trim().startsWith(r.code)) || r.code
  const prompt = `Adversarial audit of one AI-code tell: "${r.code}".
Definition: ${def.trim()}

These candidate comments (by line number in ${CF}) were tagged with "${r.code}":
lines: ${lines}
Read them: \`sed -n -e '${idx.map(i => (i + 1) + 'p').join(' -e \'')}' ${CF}\`
(or read the file and pick those line numbers).

For a sample of up to 40, judge how many GENUINELY name this specific tell (default to NO when the comment is vague, is just "AI slop" with no specifics, or names a different tell). Report sampled count, genuine count, precision = genuine/sampled, a verdict (solid/mostly/inflated/artifact), a one-line note, and up to 4 verbatim best_quotes that clearly express this tell.`
  return agent(prompt, { label: `verify:${r.code}`, phase: 'Verify top tells', schema: VER_SCHEMA, effort: 'medium' })
}))

return {
  totals: { comments_classified: comment.length, posts_classified: post.length,
            comment_named: cAgg.named, post_named: pAgg.named },
  ranked,
  verify: verify.filter(Boolean),
  raw_comment_classifications: comment,   // for quote bank join afterward
}
