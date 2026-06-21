#!/usr/bin/env python3
"""
Tabulate visual tells across the COMMENT corpus (3k comments from 125 canonical
'why do AI sites look the same / dead giveaways' threads). These comments are
100% on-topic, so this is the cleanest tell-frequency signal + the best source
of verbatim quotes. Reuses the same lexicon as analyze.py.
"""
import json, os, csv, html, re
from collections import Counter
import analyze as A   # reuse TELLS / COMPILED / matches / NEG

OUT = os.path.dirname(os.path.abspath(__file__))

def load():
    items = []
    for l in open(os.path.join(OUT, "comments.jsonl")):
        try:
            d = json.loads(l)
            d["_text"] = html.unescape(d.get("body") or "")
            items.append(d)
        except: pass
    return items

def main():
    items = load()
    n = len(items)
    # de-dupe identical boilerplate bodies (bots)
    rows = []
    for name in A.TELLS:
        hit = [it for it in items if A.matches(it["_text"], name)]
        negc = sum(1 for it in hit if A.NEG.search(it["_text"]))
        rows.append((name, len(hit), len(hit)/n*100 if n else 0, negc))
    rows.sort(key=lambda r: -r[1])

    with open(os.path.join(OUT, "comment_tell_counts.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["tell", "comments_mentioning", "share_of_comments_pct", "neg_sentiment_comments"])
        for r in rows: w.writerow([r[0], r[1], f"{r[2]:.1f}", r[3]])

    with open(os.path.join(OUT, "comment_tell_examples.md"), "w") as f:
        f.write(f"# Comment-level tell quotes ({n} comments from 125 on-topic threads)\n\n")
        for name, cnt, share, _ in rows:
            hit = [it for it in items if A.matches(it["_text"], name)]
            # prefer substantive, higher-scored, non-boilerplate comments
            hit = [h for h in hit if 25 <= len(h["_text"]) <= 600]
            hit.sort(key=lambda x: -(x.get("score") or 0))
            f.write(f"## {name} — {cnt} comments ({share:.1f}%)\n\n")
            for it in hit[:8]:
                body = " ".join(it["_text"].split())
                f.write(f"- **[{it.get('score')}↑ r/{it.get('subreddit')}]** {body[:300]}\n")
                f.write(f"  https://reddit.com{it.get('permalink','')}\n\n")

    print(f"Comments analyzed: {n}")
    print("\nCOMMENT-LEVEL TELL RANKING (share of on-topic comments):")
    for name, cnt, share, negc in rows:
        print(f"  {share:5.1f}%  n={cnt:4d}  {name}   (neg {negc/cnt*100:.0f}%)" if cnt else f"  {share:5.1f}%  n=0  {name}")
    bysub = Counter(it.get("subreddit") for it in items)
    print("\nComment subs:", ", ".join(f"{s}:{c}" for s,c in bysub.most_common(10)))

if __name__ == "__main__":
    main()
