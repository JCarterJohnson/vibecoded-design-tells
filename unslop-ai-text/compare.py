#!/usr/bin/env python3
"""
compare.py - Same-sample comparison of the human CITATION pass vs the regex pass.

For the exact 600 posts the subagents read (the chunk files), compute:
  - regex_share_sample : % of those posts the Lens-1 regex flags for a tell
  - cite_share_sample  : % of those posts a human said the author CITES the tell
Both shares share one denominator (the sample), so the gap is purely method.
Also carries the full-corpus regex share for context, and lists human-only tells
the regex is structurally blind to (under-count) and regex-only noise (over-count).

Reads citation tally from extract_result.json (written from the workflow result).
"""
import os, re, json, csv, glob
import analyze  # for LEX regex set (import does not run its main())

HERE = os.path.dirname(os.path.abspath(__file__))

# --- load the exact sample posts the subagents read ---
def load_sample():
    posts = []
    for fp in sorted(glob.glob(os.path.join(HERE, "chunks", "chunk_*.txt"))):
        raw = open(fp, encoding="utf-8").read()
        for block in raw.split("### POST"):
            block = block.strip()
            if not block:
                continue
            # drop the "(r/sub, year, score N)" header line; keep the body for matching
            body = block.split("\n", 1)[1] if "\n" in block else block
            posts.append((block + "\n" + body))  # include header text too; harmless
    return posts

# --- concept join: map a LEX regex label to the human citation label(s) ---
# citation_aliases are lowercase substrings matched against the workflow's tell labels.
CONCEPTS = [
 ("em dash (\"—\") as a tell",                 ["em dash","em-dash","emdash"]),
 ("bolded lead-in bullets (**Word:**)",        ["bold","lead-in"]),
 ("everything in bullet points / lists",       ["bullet","listicle","over-list","everything in lists"]),
 ("headers / bold everywhere / markdown",      ["header","markdown","heading"]),
 ("\"rule of three\" / triads",                ["rule of three","triad","tricolon"]),
 ("perfectly structured / formulaic",          ["formulaic","perfectly structured","essay shape","too structured","structured"]),
 ("rhetorical question then answer",           ["rhetorical"]),
 ("emoji bullets / emoji headers",             ["emoji"]),
 ("\"it's not just X, it's Y\"",               ["it's not just","not just x","not just about","isn't just"]),
 ("\"dive in\" / \"deep dive\" / \"let's dive\"", ["dive in","deep dive","let's dive","dive"]),
 ("\"in conclusion\" / \"in summary\"",        ["in conclusion","in summary","conclusion"]),
 ("\"it's important to note/remember\"",       ["important to note","important to remember"]),
 ("\"it's worth noting\"",                     ["worth noting"]),
 ("\"in today's fast-paced/digital world\"",   ["fast-paced","today's digital","today's world","digital age"]),
 ("\"unlock/unleash the power/potential\"",    ["unlock the","unleash the","harness the","power/potential","the power"]),
 ("delve",        ["delve"]),
 ("tapestry",     ["tapestry"]),
 ("game-changer", ["game-changer","game changer"]),
 ("unleash",      ["unleash"]),
 ("testament (\"a testament to\")", ["testament"]),
 ("underscore(s)",["underscore"]),
 ("ever-evolving / ever-changing", ["ever-evolving","ever-changing","ever evolving"]),
 ("embark (\"embark on a journey\")", ["embark"]),
 ("leverage",     ["leverage"]),
 ("utilize (instead of \"use\")", ["utilize"]),
 ("seamless(ly)", ["seamless"]),
 ("robust",       ["robust"]),
 ("nuanced / nuance", ["nuance"]),
 ("comprehensive",["comprehensive"]),
 ("navigate / navigating", ["navigat"]),
 ("overuse of \"however,\" / \"thus,\" / \"hence\"", ["however","thus","hence","transition"]),
 ("overuse of \"moreover/furthermore/additionally\"", ["moreover","furthermore","additionally"]),
 ("\"when it comes to\"", ["when it comes to"]),
 ("\"great question!\"", ["great question","good question","excellent question"]),
 ("\"I hope this helps!\"", ["hope this helps"]),
 ("\"let me know if you'd like / feel free\"", ["let me know","feel free"]),
 ("\"would you like me to ...?\"", ["would you like me"]),
 ("\"as an AI language model\"", ["as an ai","language model"]),
 ("\"I cannot/can't assist/fulfill\"", ["cannot fulfill","can't assist","cannot assist","i can't help","refus"]),
 ("\"knowledge cutoff / as of my last update\"", ["knowledge cut","last update","training data","cutoff"]),
 ("\"I hope this email finds you well\"", ["finds you well"]),
 ("\"Certainly!\" / \"Absolutely!\" openers", ["certainly","absolutely","sure!"]),
]

LEX_BY_LABEL = {label: pats for (cat, label, pats) in analyze.LEX}

def main():
    if not os.path.exists(os.path.join(HERE, "extract_result.json")):
        print("extract_result.json not found - write it from the workflow result first.")
        return
    res = json.load(open(os.path.join(HERE, "extract_result.json")))
    cite = res.get("citationRanking", [])
    total_read = res.get("totalPostsRead") or 0
    # human citation counts keyed by lowercased tell label
    cite_posts = {}
    for c in cite:
        cite_posts[c["tell"].strip().lower()] = c.get("posts", 0)

    sample = load_sample()
    Ns = len(sample)
    print(f"sample posts parsed from chunks: {Ns}; subagent posts_read: {total_read}")

    # full-corpus regex shares for context
    full = {}
    for r in csv.DictReader(open(os.path.join(HERE, "findings_lens1.csv"))):
        full[r["tell"]] = float(r["share_pct_of_ontopic"])

    rows = []
    used_cite_keys = set()
    for lex_label, aliases in CONCEPTS:
        pats = LEX_BY_LABEL.get(lex_label)
        if pats is None:
            rgx_hits = None
        else:
            rgx_hits = sum(1 for t in sample if any(p.search(t) for p in pats))
        # sum human citations whose label contains any alias
        chits = 0
        for k, v in cite_posts.items():
            if any(a in k for a in aliases):
                chits += v; used_cite_keys.add(k)
        rgx_share = (100.0 * rgx_hits / Ns) if (rgx_hits is not None and Ns) else None
        cite_share = (100.0 * chits / total_read) if total_read else 0.0
        # verdict
        if rgx_share is None:
            verdict = "regex-blind (under-count)"
        elif cite_share == 0 and rgx_share >= 1.0:
            verdict = "REGEX OVER-COUNTS (noise: poster's own prose)"
        elif rgx_share == 0 and cite_share >= 0.5:
            verdict = "REGEX UNDER-COUNTS (missed wording)"
        else:
            ratio = (rgx_share + 0.01) / (cite_share + 0.01)
            if ratio >= 2.0:
                verdict = "regex over-counts"
            elif ratio <= 0.5:
                verdict = "regex under-counts"
            else:
                verdict = "agree"
        rows.append({
            "tell": lex_label,
            "cite_share_sample_pct": round(cite_share, 1),
            "cite_posts": chits,
            "regex_share_sample_pct": (round(rgx_share, 1) if rgx_share is not None else "n/a"),
            "regex_share_fullcorpus_pct": full.get(lex_label, ""),
            "verdict": verdict,
        })

    rows.sort(key=lambda r: r["cite_share_sample_pct"], reverse=True)
    with open(os.path.join(HERE, "comparison.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tell","cite_share_sample_pct","cite_posts",
            "regex_share_sample_pct","regex_share_fullcorpus_pct","verdict"])
        w.writeheader(); w.writerows(rows)

    # human-only tells (no concept matched) = things the regex never even tried / can't catch
    leftover = [(k, v) for k, v in cite_posts.items() if k not in used_cite_keys and v > 0]
    leftover.sort(key=lambda x: x[1], reverse=True)
    with open(os.path.join(HERE, "human_only_tells.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["tell_cited_by_humans","posts","cite_share_sample_pct"])
        for k, v in leftover:
            w.writerow([k, v, round(100.0*v/total_read,1) if total_read else 0])

    print("\n=== COMPARISON (human citation vs regex, same 600-post sample) ===")
    print(f"{'tell':42} {'cite%':>6} {'rgx%':>6}  verdict")
    for r in rows:
        print(f"{r['tell'][:42]:42} {r['cite_share_sample_pct']:>6} {str(r['regex_share_sample_pct']):>6}  {r['verdict']}")
    print("\n=== HUMAN-ONLY TELLS (regex blind / not in lexicon) ===")
    for k, v in leftover[:20]:
        print(f"  {v:4}  {k}")

if __name__ == "__main__":
    main()
