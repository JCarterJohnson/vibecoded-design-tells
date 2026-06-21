#!/usr/bin/env python3
"""Build the candidate tell-bearing POST set for LLM classification. Same broad
union filter as the comments, over title+selftext of the on-topic posts. News /
debate / career posts that name no code-level property are dropped here and the
LLM confirms the rest."""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
posts = [json.loads(l) for l in open(os.path.join(HERE,"corpus.jsonl"))]
print("on-topic posts:", len(posts))

UNION = re.compile(r"(comment|docstring|jsdoc|naming|named|variable|var name|"
    r"try[ /]?(except|catch)|except|catch|defensive|error handling|"
    r"abstract|over[- ]?engineer|boilerplate|scaffold|tutorial|textbook|"
    r"emoji|✅|🚀|🎉|backtick|code ?fence|markdown|formatting|indent|"
    r"too clean|too perfect|consistent|verbose|concise|refactor|"
    r"type ?hint|type ?annotation|typed|placeholder|your code here|rest of (the|your) code|"
    r"as an ai|language model|here.?s the (updated|complete|corrected|fixed)|"
    r"certainly|note:|print|console\.log|logging|helper function|self[- ]?document|"
    r"over[- ]?explain|explain.{0,15}(every|obvious|what)|too (many|much)|unnecessary|"
    r"pointless|redundant|generic|hallucinat|made up|nonexistent|doesn.?t exist|"
    r"deprecated|outdated|reads? like|looks? like|feels? like|screams?|smells?|dead giveaway)", re.I)

cands = []
for p in posts:
    text = (p.get("title") or "") + "\n" + (p.get("selftext") or "")
    if len(text.strip()) < 40:          # skip linkposts with no body to read
        continue
    if UNION.search(text):
        cands.append(p)
print("candidate tell-bearing posts:", len(cands), "(%.0f%% of on-topic)" % (100*len(cands)/len(posts)))

# Posts are corroboration (comments are primary). Bound to a representative
# stride sample so the LLM budget stays on the cleaner comment signal.
CAP = 1500
if len(cands) > CAP:
    stride = len(cands) / CAP
    cands = [cands[int(k*stride)] for k in range(CAP)]
    print("stride-sampled to", len(cands), "posts for classification")

with open(os.path.join(HERE,"candidates_posts.jsonl"),"w") as f:
    for i,p in enumerate(cands):
        body = (p.get("title") or "") + " — " + (p.get("selftext") or "")
        rec={"i":i,"id":p.get("id"),"sub":p.get("subreddit"),"score":p.get("score"),
             "body":body[:1100]}
        f.write(json.dumps(rec,ensure_ascii=False)+"\n")
print("wrote candidates_posts.jsonl")
