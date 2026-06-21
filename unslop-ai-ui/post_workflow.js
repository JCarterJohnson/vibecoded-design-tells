export const meta = {
  name: 'vibecoded-verify-synthesize',
  description: 'Adversarially verify ranked vibe-coded design tells against real quotes, then generate and judge Reddit-post angles',
  phases: [
    { title: 'Extract', detail: 'read tabulation, structure top tells + candidate quotes' },
    { title: 'Verify', detail: 'one skeptic per tell: real? visual? FP-risk? best quote?' },
    { title: 'Draft', detail: 'three independent post angles from verified tells' },
    { title: 'Judge', detail: 'score angles on accuracy/voice/usefulness, pick + graft' },
  ],
}

const DIR = '/Users/carterjohnson/Downloads/vibecoded_research'

const VOICE = `VOICE CALIBRATION (strict): plain and blunt, factual, minimal first person, no enthusiasm, no jokes or self-deprecation, no Reddit idioms (no "the hill you'd die on", "do better", "chef's kiss", "this", etc.), NO em dashes anywhere (use commas, parentheses, or periods), straight quotes only, no AI-cliche vocabulary (no delve/leverage/landscape/tapestry/robust/comprehensive/underscore/testament). Each claim earns its place; every tell is backed by a real quote or a figure.`

phase('Extract')
const EXTRACT_SCHEMA = {
  type: 'object', required: ['tells'], additionalProperties: false,
  properties: { tells: { type: 'array', items: {
    type: 'object', required: ['name','comment_share_pct','post_share_pct','quotes'], additionalProperties: false,
    properties: {
      name: { type: 'string' }, comment_share_pct: { type: 'number' }, post_share_pct: { type: 'number' },
      quotes: { type: 'array', items: { type: 'object', required: ['text','subreddit','permalink'], additionalProperties: false,
        properties: { text: {type:'string'}, subreddit: {type:'string'}, score: {type:'number'}, permalink: {type:'string'} } } }
    } } } }
}
const extracted = await agent(
  `Read these files: ${DIR}/comment_tell_counts.csv (CLEANEST ranking: share of on-topic comments mentioning each tell), ${DIR}/comment_tell_examples.md (verbatim on-topic comment quotes per tell with score/subreddit/permalink), ${DIR}/tell_counts.csv (post-level share, secondary), and ${DIR}/summary.txt. Return the TOP 12 tells ranked by comment_share. For each: name (as in the CSV), comment_share_pct, post_share_pct (look it up in tell_counts.csv; 0 if absent), and up to 3 candidate VERBATIM quotes pulled from comment_tell_examples.md (include subreddit, score, permalink). Do not invent quotes; only use ones present in the files. Prefer quotes that clearly describe how the SITE LOOKS.`,
  { schema: EXTRACT_SCHEMA, phase: 'Extract' })
log(`extracted ${extracted.tells.length} tells`)

phase('Verify')
const VERDICT_SCHEMA = {
  type: 'object', required: ['name','is_real','is_visual','false_positive_risk','verdict_note'], additionalProperties: false,
  properties: {
    name: { type: 'string' },
    is_real: { type: 'boolean' },
    is_visual: { type: 'boolean' },
    false_positive_risk: { type: 'string', enum: ['low','medium','high'] },
    best_quote: { type: 'object', additionalProperties: false,
      properties: { text:{type:'string'}, subreddit:{type:'string'}, permalink:{type:'string'} } },
    verdict_note: { type: 'string' }
  }
}
const verdicts = await pipeline(extracted.tells,
  (t) => agent(
    `Adversarially verify this claimed visual "tell" of vibe-coded (AI-built) websites: "${t.name}" — named in ${t.comment_share_pct}% of on-topic comments (${t.post_share_pct}% of design-context posts). Candidate quotes: ${JSON.stringify(t.quotes)}. You may grep ${DIR}/comments.jsonl and ${DIR}/corpus.jsonl for more context. Judge SKEPTICALLY: (1) is_real: a genuine recurring complaint, not a keyword artifact? (2) is_visual: about how the site LOOKS (vs security/function/cost/text-style)? (3) false_positive_risk low/medium/high: could the lexicon match unrelated text? Note: "emoji" and "three-column cards" were flagged as possibly inflated at post-level; check whether comments actually cite them as visual tells. (4) best_quote: the single strongest VERBATIM quote of a real person citing this as a giveaway/eyesore (with exact permalink); omit if none qualifies. (5) verdict_note: one blunt sentence. Default is_real=false if quotes do not actually show people citing this look.`,
    { schema: VERDICT_SCHEMA, label: `verify:${t.name.slice(0,18)}`, phase: 'Verify' })
)
const confirmed = verdicts.filter(Boolean).filter(v => v.is_real && v.is_visual)
log(`confirmed ${confirmed.length}/${verdicts.length} tells as real+visual`)

phase('Draft')
const confirmedData = confirmed.map(v => {
  const t = extracted.tells.find(x => x.name === v.name) || {}
  return { name: v.name, comment_share_pct: t.comment_share_pct, post_share_pct: t.post_share_pct,
           fp_risk: v.false_positive_risk, best_quote: v.best_quote, note: v.verdict_note }
})
const growth = await agent(`Read ${DIR}/growth_by_year.csv and return its contents verbatim as text.`, { phase: 'Draft', label: 'read-growth' })
const angles = [
  'Ranked list, most-mocked first. Each item: the tell, its share figure, one real quote. Open with the single blunt finding (these sites are recognizable on sight) and the method in two sentences.',
  'Diagnostic framing: explain WHY they all converge (default tool output: same stack, same starter template, same palette), then list the specific tells with shares and quotes as evidence.',
  'Avoid-this checklist for someone shipping an AI-built site: each tell stated as the thing to not do, with the share figure and a quote showing how people react.',
]
const drafts = await parallel(angles.map((ang, i) => () => agent(
  `Write a Reddit results post about the visual "tells" of vibe-coded websites people should avoid. ANGLE: ${ang}\n\nUse ONLY these verified tells (name, share %, verified best quote): ${JSON.stringify(confirmedData)}\nTopic-growth data to optionally cite: ${growth}\n\n${VOICE}\n\nThe post must: lead with the core finding, state the method briefly (Arctic Shift Reddit archive, ~44 subreddits, tens of thousands of on-topic posts 2020-2026, share of posts not raw counts), then present the tells ranked by share with a real quote or figure behind each. End with one blunt practical takeaway. 350-600 words. Return only the post text.`,
  { label: `draft:angle${i+1}`, phase: 'Draft' })))
const validDrafts = drafts.filter(Boolean)

phase('Judge')
const JUDGE_SCHEMA = {
  type: 'object', required: ['scores','best_index','why','grafts'], additionalProperties: false,
  properties: {
    scores: { type: 'array', items: { type: 'object', required: ['index','accuracy','voice','usefulness','total'], additionalProperties: false,
      properties: { index:{type:'integer'}, accuracy:{type:'number'}, voice:{type:'number'}, usefulness:{type:'number'}, total:{type:'number'} } } },
    best_index: { type: 'integer' },
    why: { type: 'string' },
    grafts: { type: 'string' }
  }
}
const judgment = await agent(
  `Score these ${validDrafts.length} candidate Reddit posts (0-10 each on accuracy-to-data, voice-fidelity per the calibration, practical usefulness; total = sum). Then pick best_index (0-based) and in "grafts" name the strongest specific lines/ideas from the OTHER drafts worth merging in.\n\n${VOICE}\n\nDrafts:\n${validDrafts.map((d,i)=>`=== DRAFT ${i} ===\n${d}`).join('\n\n')}`,
  { schema: JUDGE_SCHEMA, phase: 'Judge' })

return {
  confirmed: confirmedData,
  rejected: verdicts.filter(Boolean).filter(v => !(v.is_real && v.is_visual)).map(v => ({name:v.name, note:v.verdict_note})),
  growth,
  best_index: judgment.best_index,
  judge_why: judgment.why,
  grafts: judgment.grafts,
  best_draft: validDrafts[judgment.best_index] || validDrafts[0],
  all_drafts: validDrafts,
}
