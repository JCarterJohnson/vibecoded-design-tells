#!/usr/bin/env python3
"""
Phase-3 harvester (resumable). Pulls on-topic post TEXT from Arctic Shift.

Fixes the bug that wasted the prior run: the search endpoint rejects
`permalink` in `fields` with HTTP 400 (deterministic). We now request full
objects (permalink is included) and treat 400 / non-throttle 422 as PERMANENT
(no pointless retries). Phases 1-2 (aggregate CSVs) are left untouched.

Resumable: a checkpoint file records every (sub|query) combo we've finished
(ok or permanently-skipped). On start we reload it + existing corpus ids, so
re-running continues instead of restarting. Self-bounds to --max-seconds so a
foreground call returns loudly before any tool timeout; re-invoke to continue.

Strictly sequential. Exponential backoff on 429 / timeout / empty body.
Run:  python3 harvest.py [max_seconds]      (default 480)
Exit: 0 = all combos done, 2 = more remain (re-run to resume)
"""
import urllib.request, urllib.parse, json, time, os, sys
import collect  # reuse SUBREDDITS + UNIVERSE_QUERIES + START_YEAR

OUT = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(OUT, "corpus.jsonl")
CKPT = os.path.join(OUT, "harvest_done.txt")
LEDGER = os.path.join(OUT, "harvest_ledger.csv")
UA = {"User-Agent": "vibecoded-aesthetics-research/1.0 (personal research)"}
MAX_PAGES = 4
THROTTLE = 0.5
KNOWN_DEAD = {"GeminiAI", "v0dev"}   # do not exist in archive; skip fast

def get(path, params, tries=5):
    """Return (data, status). status: ok | permanent | giveup. Exp backoff on transient."""
    url = path + "?" + urllib.parse.urlencode(params)
    full = "https://arctic-shift.photon-reddit.com" + url
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(full, headers=UA), timeout=30) as r:
                body = r.read().decode("utf-8", "ignore")
                if not body.strip():                 # empty body => throttle
                    time.sleep(min(2 ** i, 30)); continue
                return json.loads(body).get("data"), "ok"
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore").lower()
            if "slow down" in msg or e.code == 429 or e.code in (500, 502, 503, 504):
                time.sleep(min(2 ** i + 1, 30)); continue        # transient
            return None, "permanent"                              # 400 / hard 422 / 404 etc.
        except Exception:
            time.sleep(min(2 ** i + 1, 30)); continue             # timeout / conn reset
    return None, "giveup"

def harvest(sub, query):
    """Page newest->oldest. Returns (items, status). status ok/permanent/giveup."""
    items, before = [], None
    for _ in range(MAX_PAGES):
        p = {"subreddit": sub, "query": query, "limit": "100", "sort": "desc", "after": collect.START_YEAR}
        if before:
            p["before"] = str(before)
        data, st = get("/api/posts/search", p)
        if st != "ok":
            return items, (st if not items else "ok")   # keep partial pages we already got
        time.sleep(THROTTLE)
        if not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        before = min(int(x["created_utc"]) for x in data) - 1
    return items, "ok"

def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 480.0
    t_start = time.time()

    done = set()
    if os.path.exists(CKPT):
        with open(CKPT) as f:
            done = {ln.strip() for ln in f if ln.strip()}
    seen = set()
    if os.path.exists(CORPUS):
        with open(CORPUS) as f:
            for ln in f:
                try: seen.add(json.loads(ln)["id"])
                except: pass

    combos = [(s, q) for s in collect.SUBREDDITS for q in collect.UNIVERSE_QUERIES]
    todo = [c for c in combos if f"{c[0]}|{c[1]}" not in done]
    print(f"[start] combos total={len(combos)} done={len(done)} todo={len(todo)} "
          f"corpus_ids={len(seen)} budget={budget:.0f}s", flush=True)

    cf = open(CORPUS, "a")
    lf = open(LEDGER, "a")
    if os.path.getsize(LEDGER) == 0:
        lf.write("subreddit,query,harvested,status\n")
    ck = open(CKPT, "a")

    processed = 0
    new_items = 0
    last_sub = None
    for sub, q in todo:
        if time.time() - t_start > budget:
            print(f"[pause] budget hit after {processed} combos", flush=True)
            break
        key = f"{sub}|{q}"
        if sub in KNOWN_DEAD:
            ck.write(key + "\n"); ck.flush()
            lf.write(f"{sub},{q},0,skip_dead\n"); lf.flush()
            processed += 1
            continue
        items, st = harvest(sub, q)
        hv = 0
        for it in items:
            iid = it.get("id")
            if not iid or iid in seen:
                continue
            seen.add(iid)
            rec = {"id": iid, "subreddit": it.get("subreddit", sub),
                   "created_utc": it.get("created_utc"), "score": it.get("score"),
                   "num_comments": it.get("num_comments"),
                   "title": (it.get("title") or "")[:500],
                   "selftext": (it.get("selftext") or "")[:3000],
                   "permalink": it.get("permalink"), "matched_query": q}
            cf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            hv += 1; new_items += 1
        cf.flush()
        lf.write(f"{sub},{q},{hv},{st}\n"); lf.flush()
        ck.write(key + "\n"); ck.flush()
        processed += 1
        if sub != last_sub:
            print(f"  [{time.time()-t_start:5.0f}s] {sub:18} corpus={len(seen)} (+{new_items} this run)", flush=True)
            last_sub = sub

    cf.close(); lf.close(); ck.close()
    remaining = len(todo) - processed
    print(f"[end] processed={processed} new_items={new_items} corpus_total={len(seen)} remaining_combos={remaining}", flush=True)
    sys.exit(0 if remaining == 0 else 2)

if __name__ == "__main__":
    main()
