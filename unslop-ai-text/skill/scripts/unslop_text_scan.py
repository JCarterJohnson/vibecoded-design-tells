#!/usr/bin/env python3
"""
unslop_text_scan.py - scan prose for the "tells" that make writing read as AI-generated.

Plain Python, standard library only. The detection patterns and their severity come from a
Reddit analysis (89,239 posts pulled, 7,984 on-topic, across ~50 AI / writing / SaaS
subreddits, 2021 to 2026) of what people actually name as a giveaway that text was written
by ChatGPT or Claude. Severity follows how often each tell is cited in that data, so the
report tells you where to spend effort. A 600-post sample was hand-audited to separate what
people cite from what a keyword pass merely matches; this scanner keys on the cited,
keyword-detectable tells.

What it can and cannot see. Some of the most-cited tells are structural (uniform sentence
rhythm, sycophancy, saying nothing at length, no contractions, hedging). A regex cannot
measure rhythm or emptiness, so those are reported in references/tells.md for a human pass,
not here. This scanner catches the mechanical tells: the em dash, the "not X, it's Y"
cadence, leftover assistant boilerplate, the diction memes, the formatting tics.

How it reads a file. It lints YOUR running prose. Material you are quoting (a line that
starts with >, or text inside "double quotes") and material shown as a literal example
(inside `backticks` or a fenced code block) is skipped, because flagging a cliche you are
quoting in order to discuss it would be wrong. The one exception is the em dash, which is
flagged everywhere, because the rule is simply not to ship one.

Usage:
    python3 unslop_text_scan.py <path>                 # scan a file or dir
    python3 unslop_text_scan.py <path> --severity high # only the strongest signals
    python3 unslop_text_scan.py <path> --json          # machine-readable (for CI)
    python3 unslop_text_scan.py <path> --max 8         # cap examples shown per rule

A line containing  unslop-ignore  is skipped, for a tell you are using on purpose.
Exit code is the number of HIGH-severity findings (0 = none), so CI can gate on it.
"""
import os, re, sys, json, argparse

EXTS = {".md", ".markdown", ".mdx", ".txt", ".text", ".rst", ".html", ".htm"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "vendor",
             "coverage", "__pycache__", ".venv", "venv"}
W = {"high": 3, "medium": 2, "low": 1}

EMOJI = ("\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF"
         "\U00002190-\U000021FF\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F\U00002764")

# Each rule: id, label, severity, share (the data % it carries, shown so you can weight),
# fix, and patterns (compiled case-insensitive). Severity tiers follow the cited/keyword
# shares from the study: HIGH = the strongest cited tells, down to LOW = real but minor.
RULES = [
    # ---------- HIGH: the strongest, most-cited tells ----------
    {"id": "em-dash", "label": "Em dash (the single most-cited AI tell)", "sev": "high",
     "share": "cited 7.1% / matched 4.5%", "raw": True,
     "fix": "Cut it. Use a comma, a period, or parentheses. Do not just swap in a colon; people flag that now too.",
     "pats": [r"—", r"––", r"\s–\s"]},
    {"id": "not-just-x-y", "label": "\"It's not just X, it's Y\" / \"not X, but Y\" antithesis cadence", "sev": "high",
     "share": "cited 2.8% / matched 1.9%",
     "fix": "State the thing plainly. The negate-then-assert rhythm is the clearest 'AI accent'.",
     "pats": [r"\b(it'?s|its|it is|that'?s|this is|they'?re)\s+not\s+(just|only|merely|simply)\b[^.?!\n]{0,60}\bit'?s\b",
              r"\bnot\s+(just|only|merely|simply)\s+(a |an |the )?[\w-]+,?\s+but\b",
              r"\bisn'?t\s+(just|only|merely)\b[^.?!\n]{0,60}\bit'?s\b"]},
    {"id": "assistant-boilerplate", "label": "Leftover assistant boilerplate (\"as an AI language model\", a knowledge-cutoff line, a refusal)", "sev": "high",
     "share": "cited 1.2%, the ultimate proof when present",
     "fix": "Delete every trace of the assistant voice before publishing: disclaimers, refusals, cutoff dates.",
     "pats": [r"\bas an?\s+(ai|a\.i\.)\s+(language\s+)?model\b", r"\bas a large language model\b",
              r"\bi (cannot|can'?t|am unable to)\s+(assist|help|fulfil|fulfill|comply|provide)\b",
              r"\bknowledge cut[- ]?off\b", r"\bas of my last (knowledge )?(update|training)\b",
              r"\bi (do not|don'?t) have (personal|the ability|access|feelings|opinions)\b"]},
    {"id": "sycophancy-opener", "label": "Sycophantic opener (\"Great question!\", \"Certainly!\", \"I'd be happy to\")", "sev": "high",
     "share": "cited 2.5% (sycophancy is the #4 cited tell)",
     "fix": "Drop the flattery and the reflexive agreement. Open with the actual point. Disagree when warranted.",
     "pats": [r"\b(great|good|excellent|that'?s a (great|good))\s+question\b",
              r"(^|[\"'`(]\s*)(certainly|absolutely|sure thing|of course)\s*[!,]",
              r"\bi'?d be (happy|glad|delighted) to\b", r"\bhappy to help\b",
              r"\byou'?re absolutely right\b", r"\bwhat a (great|fascinating|wonderful)\b"]},
    {"id": "bolded-lead-in", "label": "Bolded lead-in label (**Word:** then a sentence) / title-case mini-headings", "sev": "high",
     "share": "matched 2.8% (n=220), rank 3 by keyword pass",
     "fix": "Write a normal sentence without the boldface label. The **Bold:** then clause pattern is a giveaway.",
     "pats": [r"(^|\s)\*\*[^*\n]{2,40}:\*\*\s", r"(^|\s)\*\*[^*\n]{2,40}\*\*\s*:",
              r"(^|\s)__[^_\n]{2,40}:?__\s*:?\s"]},
    {"id": "assistant-offer", "label": "Trailing assistant offer (\"Would you like me to ...\", \"Let me know if ...\", \"I hope this helps!\")", "sev": "high",
     "share": "cited 0.4% each, but unmistakable when present",
     "fix": "Delete the meta-offer and the sign-off. A person finishing a thought does not ask if you want a revision.",
     "pats": [r"\bwould you like me to\b", r"\blet me know if you'?d?\s*(like|need|want|have)\b",
              r"\bi hope this helps\b", r"\bhope (this|you'?re|it) .{0,20}finds? you well\b",
              r"\bfeel free to (ask|reach|let me)\b", r"\bis there anything else\b"]},

    # ---------- MEDIUM: diction memes and formatting tics ----------
    {"id": "ai-diction", "label": "AI diction memes (delve, tapestry, leverage, seamless, game-changer, ...)", "sev": "medium",
     "share": "cited ~1.3% as a cluster; the keyword pass inflates it (listicle copying)",
     "fix": "Swap for the plain word you would actually say. 'delve into' is 'look at'; 'leverage' is 'use'.",
     "pats": [r"\b(delv(e|es|ing|ed))\b", r"\btapestr(y|ies)\b", r"\bgame[- ]?chang(er|ers|ing)\b",
              r"\bseamless(ly)?\b", r"\bleverag(e|es|ing|ed)\b", r"\bunleash(es|ing|ed)?\b",
              r"\bunderscore(s|d|ing)?\b", r"\btestament\b", r"\bembark(s|ing|ed)?\b",
              r"\bmeticulous(ly)?\b", r"\bnuanc(e|es|ed)\b", r"\belevat(e|es|ing|ed)\b",
              r"\bharness(es|ing|ed)?\b", r"\bshowcas(e|es|ing|ed)\b", r"\bcaptivat(e|es|ing|ed)\b",
              r"\bever[- ]?(evolving|changing)\b"]},
    {"id": "dive-in", "label": "\"Dive in\" / \"deep dive\" / \"let's dive\"", "sev": "medium",
     "share": "cited 2.0% / matched 1.6%",
     "fix": "Cut the metaphor and just start the topic. You do not need to announce that you are starting.",
     "pats": [r"\b(deep dive|dives? in(to)?|let'?s dive|diving in|dive deep)\b"]},
    {"id": "listicle-scaffold", "label": "Listicle scaffolding (\"5 ways to ...\", \"7 signs ...\", \"3 reasons ...\")", "sev": "medium",
     "share": "cited 1.7% (everything turned into a list)",
     "fix": "Write prose paragraphs. Reserve bullets for genuinely list-like content, not as the default shape.",
     "pats": [r"(^|\s)#{0,4}\s*\d+\s+(ways|tips|signs|reasons|things|steps|tricks|secrets|lessons|mistakes|rules)\b"]},
    {"id": "fast-paced-opener", "label": "Hollow scene-setting opener (\"In today's fast-paced world ...\")", "sev": "medium",
     "share": "cited 0.7%, iconic",
     "fix": "Delete it and start with something specific. The opener says nothing.",
     "pats": [r"\bin today'?s\s+(fast[- ]?paced|digital|ever[- ]?changing|modern|competitive)?\s*(world|age|landscape|era|society|market)\b",
              r"\bin (the|this) (modern|digital) (world|age|era)\b"]},
    {"id": "unlock-potential", "label": "\"Unlock / unleash the power / potential\"", "sev": "medium",
     "share": "cited 0.8%",
     "fix": "Say what the thing actually does. The hype verb plus 'potential' is marketing filler.",
     "pats": [r"\b(unlock|unleash|harness|tap into)\w*\s+(the\s+|your\s+|its\s+|their\s+|full\s+)*(power|potential|capabilities|secrets)\b"]},
    {"id": "emoji-decoration", "label": "Emoji used as bullets, icons, or in headings", "sev": "medium",
     "share": "cited 0.8% (emoji bullets / headers)",
     "fix": "Use plain text headers and real list markers. Decorative emoji in headings reads as templated.",
     "pats": [r"^\s{0,3}#{1,6}\s*[" + EMOJI + r"]",
              r"^\s{0,3}[" + EMOJI + r"]\s+\S",
              r"[" + EMOJI + r"]\s*\*\*", r"\*\*\s*[" + EMOJI + r"]"]},
    {"id": "in-conclusion", "label": "\"In conclusion\" / \"in summary\" / \"to summarize\" closer", "sev": "medium",
     "share": "cited 0.2% / matched 1.0%, a classic giveaway",
     "fix": "End on a real last point, not a signposted recap. If the reader needs a summary, the piece is too long.",
     "pats": [r"\bin (conclusion|summary)\b", r"\bto (summari[sz]e|conclude|wrap (this |it )?up)\b",
              r"\bin closing\b"]},

    # ---------- LOW: real but minor; fix if cheap ----------
    {"id": "transition-stack", "label": "Stacked formal connectives (Moreover, Furthermore, Additionally, ...)", "sev": "low",
     "share": "matched 1.7%, but the keyword pass over-counts (often the poster's own prose)",
     "fix": "Let ideas connect without scaffolding. As a sentence opener these read as machine-smoothed.",
     "pats": [r"(^|\.\s+|\n)\s*(moreover|furthermore|additionally|consequently)\b",
              r"\b(firstly|secondly|thirdly|lastly)\b"]},
    {"id": "generic-diction", "label": "Inflated generic diction (utilize, comprehensive, robust, crucial, navigate, ...)", "sev": "low",
     "share": "matched 1 to 2% each, but mostly the poster's own prose",
     "fix": "Prefer the plain word: 'utilize' is 'use', 'comprehensive' is 'full', 'navigate' is 'handle'.",
     "pats": [r"\butili[sz](e|es|ing|ed|ation)\b", r"\bcomprehensive\b", r"\brobust\b",
              r"\bfacilitat(e|es|ing|ed)\b", r"\bstreamlin(e|es|ing|ed)\b", r"\bempower(s|ing|ed|ment)?\b",
              r"\bmyriad\b", r"\bplethora\b", r"\bparamount\b", r"\bpivotal\b", r"\bholistic\b",
              r"\bsynerg(y|ies|istic)\b", r"\bmultifaceted\b", r"\bintricac(y|ies)\b"]},
    {"id": "hype-marketing", "label": "Marketing hype (revolutionary, transformative, take it to the next level)", "sev": "low",
     "share": "cited 0.3% (broader marketing-language category)",
     "fix": "Strip the promotional adjectives and state plain facts about what it does.",
     "pats": [r"\brevolution(ary|i[sz]e)\b", r"\btransform(ative|s your| ative)\b", r"\btransform your (life|business|workflow)\b",
              r"\bto the next level\b", r"\bsupercharge\b", r"\bsay goodbye to\b", r"\blook no further\b",
              r"\bbuckle up\b", r"\bgame[- ]?changer\b", r"\bwithout further ado\b"]},
    {"id": "hedge-cliche", "label": "Hedging / both-sides cliche (\"it depends\", \"on one hand ... on the other\")", "sev": "low",
     "share": "cited 0.3% (the regex sees the phrase, not the hedging)",
     "fix": "Take a position. Listing every option instead of committing is a tell.",
     "pats": [r"\bon (the )?one hand\b[^.\n]{0,120}\bon the other\b", r"\bit (really )?depends\b",
              r"\bthere'?s no (one[- ]?size[- ]?fits[- ]?all|right answer)\b"]},
    {"id": "note-hedge", "label": "\"It's worth noting\" / \"it's important to note\" filler", "sev": "low",
     "share": "cited 0.4 to 0.6%",
     "fix": "If it is worth noting, just note it. The preamble adds nothing.",
     "pats": [r"\bit'?s worth (noting|mentioning|pointing out)\b", r"\b(it'?s |it is )?important to (note|remember|understand|recognize)\b",
              r"\bthat being said\b", r"\bneedless to say\b"]},
    {"id": "hr-divider", "label": "Horizontal-rule dividers (---, ***) between sections", "sev": "low",
     "share": "novel, from a vivid citation ('another obvious AI writing marker')",
     "fix": "Use a paragraph break. The rule between every section reads as generated markdown.",
     "pats": [r"^\s{0,3}([-*_])\s*\1\s*\1[\s\1]*$"]},
    {"id": "honestly-opener", "label": "Fake-relatability opener (\"Honestly, ...\", \"Look, I get it\", \"Imagine this\")", "sev": "low",
     "share": "novel; a top thread is devoted to 'Honestly' being 'zombified by AI'",
     "fix": "Cut the throat-clearing and start with the actual point.",
     "pats": [r"(^|\n)\s*honestly,\s", r"\blook,\s+i (get it|know)\b", r"(^|\n)\s*(imagine|picture) this\b",
              r"\blet'?s be (honest|real)\b"]},
]

def compile_rules(min_sev):
    order = ["high", "medium", "low"]
    floor = order.index(min_sev) if min_sev else len(order) - 1
    out = []
    for r in RULES:
        if order.index(r["sev"]) > floor:
            continue
        r = dict(r)
        r["rx"] = [re.compile(p, re.IGNORECASE) for p in r["pats"]]
        out.append(r)
    return out

def iter_files(path):
    if os.path.isfile(path):
        yield path; return
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() in EXTS:
                yield os.path.join(root, f)

def strip_noise(line, in_code, in_quote):
    """Blank what the author is quoting or showing as a literal example, so the prose
    rules lint the author's own sentences. Inline-code spans (backticks) and double-quoted
    spans are removed, and the open/closed state is carried across lines so a span that
    wraps onto the next line is still skipped. Real prose quotes wrap, and a catalog of
    tells has to quote the tells; flagging a cliche you are quoting in order to discuss it
    would be a false positive. State is reset at every blank line by the caller, so an
    unbalanced quote can never swallow more than one paragraph."""
    out = []
    for ch in line:
        if in_code:
            if ch == "`":
                in_code = False
            out.append(" ")
        elif ch == "`":
            in_code = True
            out.append(" ")
        elif ch in "\"“”":
            in_quote = not in_quote
            out.append(" ")
        else:
            out.append(" " if in_quote else ch)
    return "".join(out), in_code, in_quote

def scan(path, min_sev):
    rules = compile_rules(min_sev)
    findings = []
    total_words = 0
    for fp in iter_files(path):
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                raw_lines = fh.readlines()
        except Exception:
            continue
        # skip a leading YAML frontmatter block; it is metadata, not prose
        fm_end = 0
        if raw_lines and raw_lines[0].strip() == "---":
            for j in range(1, len(raw_lines)):
                if raw_lines[j].strip() == "---":
                    fm_end = j + 1
                    break
        in_fence = in_code = in_quote = False
        for i, raw in enumerate(raw_lines, 1):
            if i <= fm_end:
                continue
            stripped = raw.strip()
            if not stripped:                          # blank line ends any open span
                in_code = in_quote = False
                continue
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                in_code = in_quote = False
                continue
            if in_fence:
                continue
            total_words += len(stripped.split())      # denominator for density
            if "unslop-ignore" in raw.lower():        # respect intentional choices
                _, in_code, in_quote = strip_noise(raw, in_code, in_quote)
                continue
            is_quote = stripped.startswith(">")
            prose, in_code, in_quote = strip_noise(raw, in_code, in_quote)
            for r in rules:
                # the em dash (raw=True) is flagged everywhere; prose rules skip quotes
                target = raw if r.get("raw") else prose
                if not r.get("raw") and is_quote:
                    continue
                for rx in r["rx"]:
                    m = rx.search(target)
                    if m:
                        findings.append({"rule": r["id"], "label": r["label"], "sev": r["sev"],
                                         "share": r["share"], "fix": r["fix"], "file": fp, "line": i,
                                         "match": m.group(0).strip()[:60],
                                         "snippet": stripped[:160]})
                        break
    return findings, total_words

def density(weighted, words):
    """Weighted slop score per 1,000 words. Concentration is the real signal: the same
    six 'comprehensive's mean slop in a 200-word paragraph and nothing in a 5,000-word
    essay, because humans write 'comprehensive' and 'delve' too."""
    return weighted / max(words, 1) * 1000.0

def verdict(by_sev, weighted, words):
    hi, med = by_sev.get("high", 0), by_sev.get("medium", 0)
    if weighted == 0:
        return "Clean, no tells detected"
    dens = density(weighted, words)
    # The LOW tier (generic diction, stray connectives) is matched far more than it is
    # ever cited; it is mostly the writer's own ordinary prose. On its own it never
    # escalates past "minor", however much of it a long piece accumulates.
    if hi == 0 and med == 0:
        return "Mostly clean, minor tells"
    # STRONG: a real cluster of strong tells, or a high concentration in a piece long
    # enough for "concentration" to mean something.
    if hi >= 3 or weighted >= 15 or (words >= 300 and dens >= 10):
        return "STRONG AI-writing tells"
    # The absolute tells (em dash, assistant boilerplate, the antithesis cadence) live in
    # HIGH; one real one always surfaces here and is never suppressed by density.
    if hi >= 1:
        return "Some AI tells present"
    # A moderate run of mid-tier tics is "some" unless it is a sparse scatter across a
    # long, otherwise-clean piece, which would be nagging.
    if weighted >= 6 and not (words >= 600 and dens < 2.0):
        return "Some AI tells present"
    return "Mostly clean, minor tells"

def main():
    ap = argparse.ArgumentParser(description="Scan prose for AI-writing tells.")
    ap.add_argument("path")
    ap.add_argument("--severity", choices=["high", "medium", "low"], default="low",
                    help="minimum severity to report (default: low = everything)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--max", type=int, default=10, help="max examples shown per rule (text mode)")
    args = ap.parse_args()

    if not os.path.exists(args.path):
        print(f"path not found: {args.path}", file=sys.stderr); sys.exit(2)

    findings, total_words = scan(args.path, args.severity)
    by_sev, by_rule = {}, {}
    for f in findings:
        by_sev[f["sev"]] = by_sev.get(f["sev"], 0) + 1
        by_rule.setdefault(f["rule"], []).append(f)
    weighted = sum(W[s] * n for s, n in by_sev.items())
    files_scanned = sum(1 for _ in iter_files(args.path))
    dens = round(density(weighted, total_words), 1)

    if args.json:
        print(json.dumps({"path": args.path, "files_scanned": files_scanned,
                          "words": total_words, "counts": by_sev, "slop_score": weighted,
                          "density_per_1k_words": dens,
                          "verdict": verdict(by_sev, weighted, total_words),
                          "findings": findings}, indent=2))
        sys.exit(by_sev.get("high", 0))

    sev_order = {"high": 0, "medium": 1, "low": 2}
    rule_ids = sorted(by_rule, key=lambda rid: (sev_order[by_rule[rid][0]["sev"]], -len(by_rule[rid])))
    print(f"\n  unslop-text scan: {args.path}")
    print(f"  files scanned: {files_scanned}   words: {total_words}   findings: {len(findings)}")
    print(f"  slop score: {weighted}   density: {dens}/1k words")
    print(f"  verdict: {verdict(by_sev, weighted, total_words)}")
    print(f"  high: {by_sev.get('high',0)}   medium: {by_sev.get('medium',0)}   low: {by_sev.get('low',0)}")
    print("  (density is the read, not the raw count: weight by concentration, not lone hits)\n")
    if not findings:
        print("  Nothing flagged. Either it is clean or the tells are structural ones a regex\n"
              "  cannot see (uniform rhythm, sycophancy, saying nothing at length). Read it aloud\n"
              "  and check those by eye against references/tells.md.\n")
        return
    for rid in rule_ids:
        items = by_rule[rid]
        f0 = items[0]
        print(f"  [{f0['sev'].upper()}] {f0['label']}  ({len(items)} hit{'s' if len(items)!=1 else ''})  [{f0['share']}]")
        print(f"        fix: {f0['fix']}")
        for it in items[:args.max]:
            print(f"        {it['file']}:{it['line']}  ({it['match']})  {it['snippet']}")
        if len(items) > args.max:
            print(f"        ... +{len(items) - args.max} more")
        print()
    top = [by_rule[rid][0]['label'] for rid in rule_ids[:3]]
    print("  Top things to change: " + "; ".join(top))
    print("  Structural tells (rhythm, sycophancy, emptiness) need a human pass. See references/tells.md.\n")
    sys.exit(by_sev.get("high", 0))

if __name__ == "__main__":
    main()
