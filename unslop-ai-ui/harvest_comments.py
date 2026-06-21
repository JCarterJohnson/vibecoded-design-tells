#!/usr/bin/env python3
"""
Harvest COMMENTS from the canonical on-topic threads (the ones literally about
AI/vibe-coded sites looking the same / dead giveaways / generic AI slop design).
Comments are where people enumerate the specific visual tells, so this gives
clean on-topic quotes + a corroborating comment-level tally.

Selects thread ids from corpus.jsonl by a STRICT on-topic title pattern,
fetches each thread's comments via /api/comments/search?link_id=<id>.
Sequential, resumable (checkpoint by link_id), robust get() reused from harvest.
"""
import urllib.request, urllib.parse, json, re, os, time, sys
from harvest import get  # robust get()

OUT = os.path.dirname(os.path.abspath(__file__))
COMMENTS = os.path.join(OUT, "comments.jsonl")
CKPT = os.path.join(OUT, "comments_done.txt")

CORE = re.compile(r"(look(s|ed)?\s+(the\s+)?same|look(s|ed)?\s+identical|look\s+exactly\s+the\s+same|"
                  r"dead\s+giveaway|giveaways?\b|spot\s+an?\s+ai|screams?\s+ai|ai\s*slop|"
                  r"why\s+do\s+all|could\w*\s+tell\s+.*apart|same\s+(design|template|layout|cues|colou?rs)|"
                  r"ai\s*fatigue|anti.?ai\s*slop|generic\s+(ai|design|website|ui)|all\s+.*look\s+the\s+same)", re.I)
CTX = re.compile(r"(website|web\s*site|landing\s*page|\bsite\b|web\s*design|\bui\b|\bux\b|design|homepage|portfolio|app)", re.I)
PROMO = re.compile(r"(i'?ll\s+tell\s+you|tell\s+you\s+what\s+marketing|i'?ll\s+run|get\s+you\s+users|"
                   r"first\s+1,?000\s+customers|drop\s+your\s+(landing|link).*i'?ll|what\s+are\s+you\s+building)", re.I)

def select_threads():
    chosen = {}
    for line in open(os.path.join(OUT, "corpus.jsonl")):
        try: d = json.loads(line)
        except: continue
        t = d.get("title") or ""
        if CORE.search(t) and CTX.search(t) and not PROMO.search(t):
            nc = d.get("num_comments") or 0
            if nc >= 3:
                chosen[d["id"]] = (nc, d.get("subreddit"), t[:80])
    # sort by comment count desc
    return sorted(chosen.items(), key=lambda kv: -kv[1][0])

def fetch_comments(link_id, max_pages=3):
    out, before = [], None
    for _ in range(max_pages):
        p = {"link_id": link_id, "limit": "100", "sort": "desc"}
        if before: p["before"] = str(before)
        data, st = get("/api/comments/search", p)
        if st != "ok" or not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        before = min(int(x["created_utc"]) for x in data) - 1
        time.sleep(0.4)
    return out

def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 600.0
    t0 = time.time()
    threads = select_threads()
    done = set()
    if os.path.exists(CKPT):
        done = {l.strip() for l in open(CKPT) if l.strip()}
    seen = set()
    if os.path.exists(COMMENTS):
        for l in open(COMMENTS):
            try: seen.add(json.loads(l)["id"])
            except: pass
    todo = [(i, m) for i, m in threads if i not in done]
    print(f"[start] on-topic threads={len(threads)} done={len(done)} todo={len(todo)} comments_seen={len(seen)}", flush=True)

    cf = open(COMMENTS, "a"); ck = open(CKPT, "a")
    n_new = 0; processed = 0
    for link_id, (nc, sub, title) in todo:
        if time.time() - t0 > budget:
            print(f"[pause] budget hit after {processed}", flush=True); break
        coms = fetch_comments(link_id)
        kept = 0
        for c in coms:
            cid = c.get("id")
            if not cid or cid in seen: continue
            body = (c.get("body") or "")
            if body in ("[deleted]", "[removed]", ""): continue
            seen.add(cid)
            rec = {"id": cid, "link_id": link_id, "thread_title": title,
                   "subreddit": c.get("subreddit", sub), "score": c.get("score"),
                   "created_utc": c.get("created_utc"),
                   "body": body[:2000], "permalink": c.get("permalink")}
            cf.write(json.dumps(rec, ensure_ascii=False) + "\n"); kept += 1; n_new += 1
        cf.flush()
        ck.write(link_id + "\n"); ck.flush()
        processed += 1
        if processed % 15 == 0:
            print(f"  [{time.time()-t0:4.0f}s] {processed}/{len(todo)} threads, comments={len(seen)}", flush=True)
    cf.close(); ck.close()
    print(f"[end] processed={processed} new_comments={n_new} total_comments={len(seen)} remaining={len(todo)-processed}", flush=True)
    sys.exit(0 if processed >= len(todo) else 2)

if __name__ == "__main__":
    main()
