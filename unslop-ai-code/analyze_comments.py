#!/usr/bin/env python3
"""
analyze_comments.py - Comment-level tell tabulation. The comments come from
threads that are 100% on-topic (literally "how to tell code is AI-written"), so
this is the CLEANEST ranking signal -- treated as primary over the post-level
numbers, exactly as in the design-tells pipeline.

Reuses the LEX lexicon from analyze.py. Output: comment_tell_counts.csv and
comment_tell_examples.md (verbatim quotes + permalinks for grounding the post).
"""
import json, os, csv
from analyze import LEX

HERE = os.path.dirname(os.path.abspath(__file__))
COMMENTS = os.path.join(HERE, "comments.jsonl")

def main():
    if not os.path.exists(COMMENTS):
        print("no comments yet:", COMMENTS); return
    coms = []
    for line in open(COMMENTS, encoding="utf-8"):
        try: c = json.loads(line)
        except Exception: continue
        if c.get("body"):
            coms.append(c)
    N = len(coms)
    print("comments loaded: %d  from %d threads"
          % (N, len(set(c.get("link_id") for c in coms))))
    if not N: return

    rows = []
    examples = {}
    for cat, label, pats in LEX:
        hits = [c for c in coms if any(p.search(c["body"]) for p in pats)]
        rows.append((cat, label, len(hits), len(hits)/N))
        examples[label] = sorted(hits, key=lambda c: (c.get("score") or 0), reverse=True)[:6]
    rows.sort(key=lambda r: r[2], reverse=True)

    with open(os.path.join(HERE,"comment_tell_counts.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","category","tell","comments_mentioning","share_pct_of_comments"])
        for i,(cat,label,cnt,share) in enumerate(rows,1):
            w.writerow([i,cat,label,cnt,"%.1f"%(share*100)])

    with open(os.path.join(HERE,"comment_tell_examples.md"),"w",encoding="utf-8") as f:
        f.write("# Comment-level tell quotes (verbatim, with permalinks)\n\n")
        f.write("Comments harvested from canonical 'how to tell code is AI-written' threads.\n\n")
        for cat,label,cnt,share in rows:
            if not cnt: continue
            f.write("## %s  (%d comments, %.1f%%)\n\n" % (label,cnt,share*100))
            for c in examples[label][:4]:
                perma = c.get("permalink") or ""
                url = ("https://reddit.com"+perma) if perma.startswith("/") else perma
                f.write("- [%s | r/%s] %s\n  %s\n" % (c.get("score"), c.get("subreddit"),
                        url, c["body"][:400].replace("\n"," ")))
            f.write("\n")

    print("\nTOP 30 TELLS (comment-level, share of on-topic comments):")
    for i,(cat,label,cnt,share) in enumerate(rows[:30],1):
        print("%2d. %5.1f%%  [%-13s] %s  (n=%d)" % (i,share*100,cat,label,cnt))

if __name__ == "__main__":
    main()
