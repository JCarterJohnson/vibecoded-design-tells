#!/usr/bin/env python3
"""Inspect thread quality and build the 'candidate tell-bearing comment' set that
the LLM classifier will read. Broad union filter: keep any comment that plausibly
names a code-level property, so the LLM can confirm/deny + categorize. The rest
are treated as 'no specific tell' in the denominator (all on-topic comments)."""
import json, re, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
coms = [json.loads(l) for l in open(os.path.join(HERE,"comments.jsonl"))]
print("total on-topic comments:", len(coms))

# thread quality: show the biggest threads by comment volume harvested
byt = collections.Counter(c.get("link_id") for c in coms)
titles = {}
for c in coms:
    titles.setdefault(c.get("link_id"), c.get("thread_title"))
print("\n=== top 25 threads by harvested comments ===")
for lid, n in byt.most_common(25):
    print("  %4d  %s" % (n, (titles.get(lid) or "")[:88]))

# broad candidate filter
UNION = re.compile(r"(comment|docstring|jsdoc|naming|named|variable|var name|"
    r"try[ /]?(except|catch)|except|catch|defensive|error handling|"
    r"abstract|over[- ]?engineer|boilerplate|scaffold|tutorial|textbook|"
    r"emoji|✅|🚀|🎉|backtick|code ?fence|markdown|formatting|indent|"
    r"too clean|too perfect|consistent|verbose|concise|refactor|"
    r"type ?hint|type ?annotation|typed|placeholder|your code here|rest of (the|your) code|"
    r"as an ai|language model|i cannot|here.?s the (updated|complete|corrected|fixed)|"
    r"certainly|sure[!,. ]+here|note:|print|console\.log|logging|"
    r"helper function|wrapper|util|naming convention|self[- ]?document|"
    r"verbose|over[- ]?explain|explain.{0,15}(every|obvious|what)|"
    r"too (many|much)|unnecessary|pointless|redundant|generic|"
    r"hallucinat|made up|nonexistent|doesn.?t exist|deprecated|outdated|"
    r"reads? like|looks? like|feels? like|screams?|smells?|dead giveaway|tell\b|sign\b)", re.I)

cands = [c for c in coms if UNION.search(c.get("body") or "")]
print("\ncandidate tell-bearing comments:", len(cands), "(%.0f%% of on-topic)" % (100*len(cands)/len(coms)))

# write candidates (with stable index) for the classifier
with open(os.path.join(HERE,"candidates.jsonl"),"w") as f:
    for i,c in enumerate(cands):
        rec={"i":i,"id":c.get("id"),"sub":c.get("subreddit"),"score":c.get("score"),
             "thread":(c.get("thread_title") or "")[:120],
             "body":(c.get("body") or "")[:900]}
        f.write(json.dumps(rec,ensure_ascii=False)+"\n")
print("wrote candidates.jsonl")
