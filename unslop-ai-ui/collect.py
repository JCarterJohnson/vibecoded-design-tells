#!/usr/bin/env python3
"""
Collect Reddit discussion about vibe-coded / AI-generated websites from the
Arctic Shift public archive (arctic-shift.photon-reddit.com). Stdlib only.

Two layers:
  1. AGGREGATE  -> growth-normalized counts (matched vs total) per sub per year.
                  Reading rule: share of posts, not raw count (subs grow over time).
  2. HARVEST    -> actual post text of on-topic items, so the design "tells"
                  can be tabulated against what people really wrote (and quoted).

Access mechanism: plain HTTP GET, no key, no auth. Endpoints:
  /api/posts/search            (full results, limit<=100, paginate via `before`)
  /api/posts/search/aggregate  (counts; aggregate=subreddit or aggregate=created_utc)
Search field is `query` (title+selftext, AND/phrase semantics).
422 "slow down" => transient, back off & retry. Other 422 => deterministic
full-text rejection on a too-active sub => give up cleanly for that sub+query.
"""
import urllib.request, urllib.parse, json, csv, time, os, sys

BASE = "https://arctic-shift.photon-reddit.com"
UA = {"User-Agent": "vibecoded-aesthetics-research/1.0 (personal research)"}
OUT = os.path.dirname(os.path.abspath(__file__))
START_YEAR = "2020-01-01"      # past ~5 years
THROTTLE = 1.2                 # seconds between calls (be polite)
MAX_PAGES = 4                  # up to 400 newest matched posts per (sub,query)

# Medium-sized, topic-specific communities. Wide net across AI-focused subs
# (as many as possible) plus no-code / indie / SaaS where launches get critiqued.
SUBREDDITS = [
    # vibe-coding / AI coding tools (corrected, archive-verified names)
    "vibecoding", "ChatGPTCoding", "cursor", "lovable", "boltnewbuilders",
    "windsurf", "Codeium", "replit", "v0dev", "base44",
    "AI_Agents", "ClaudeCode", "aipromptprogramming",
    # AI assistants / model communities (wide net, as requested)
    "ChatGPT", "ChatGPTPro", "ChatGPTcomplaints", "OpenAI",
    "ClaudeAI", "claude", "Anthropic", "ClaudeCowork",
    "GeminiAI", "GoogleGeminiAI", "GoogleGemini", "grok", "Perplexity", "perplexity_ai",
    # broader AI
    "artificial", "ArtificialInteligence", "singularity", "LocalLLaMA",
    # web / design / dev (where "this looks AI-made" critique lives)
    "webdev", "web_design", "Frontend", "userexperience", "UI_Design",
    "graphic_design", "css",
    # no-code / indie / SaaS launches
    "nocode", "NoCodeSaaS", "SaaS", "microsaas", "micro_saas", "SideProject",
    "IndieHackers", "indiebiz", "EntrepreneurRideAlong", "roastmystartup",
    "alphaandbetausers",
]

# Intent phrases. AND/phrase semantics => each reliably means on-topic chatter
# about AI-built sites/apps, biased toward how they look.
UNIVERSE_QUERIES = [
    "vibe coded",
    "vibe coding",
    "ai generated website",
    "ai generated site",
    "looks ai generated",
    "ai slop",
    "ai website",
    "ai landing page",
    "generic ai",
    "all look the same",
]
# Subset used for the per-year growth/share table (cleanest, least-noisy signal).
GROWTH_QUERIES = ["vibe coding", "vibe coded", "ai generated website", "ai slop"]

def get(path, params, tries=6):
    """HTTP GET with backoff. Returns (data, status). status in {ok,reject,giveup}."""
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.load(r).get("data"), "ok"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore").lower()
            if e.code in (429, 422, 500, 502, 503) and "slow down" in body:
                time.sleep(2.0 * (i + 1)); continue          # transient
            if e.code == 429:
                time.sleep(3.0 * (i + 1)); continue          # rate limit
            if e.code == 422:
                return None, "reject"                        # deterministic full-text rejection
            time.sleep(1.5 * (i + 1)); continue
        except Exception:
            time.sleep(2.0 * (i + 1)); continue
    return None, "giveup"

def count(sub, query=None, after=START_YEAR, by_year=False):
    p = {"subreddit": sub, "after": after, "aggregate": "created_utc" if by_year else "subreddit"}
    if by_year: p["frequency"] = "year"
    if query: p["query"] = query
    data, st = get("/api/posts/search/aggregate", p)
    time.sleep(THROTTLE)
    if st != "ok" or data is None:
        return None, st
    if by_year:
        out = {}
        for b in data:
            yr = b.get("created_utc", "")[:4]
            try: out[yr] = int(b.get("count", 0))
            except: out[yr] = 0
        return out, "ok"
    try:
        return (int(data[0]["count"]) if data else 0), "ok"
    except Exception:
        return 0, "ok"

def harvest(sub, query, max_pages=MAX_PAGES):
    """Page newest->oldest matched posts. Returns (list_of_items, status, total_matched)."""
    items, before, status = [], None, "ok"
    for _ in range(max_pages):
        p = {"subreddit": sub, "query": query, "limit": "100", "sort": "desc",
             "fields": "id,subreddit,created_utc,score,num_comments,title,selftext,permalink",
             "after": START_YEAR}
        if before: p["before"] = str(before)
        data, st = get("/api/posts/search", p)
        time.sleep(THROTTLE)
        if st != "ok":
            status = st; break
        if not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        before = min(int(x["created_utc"]) for x in data) - 1
    return items, status

def main():
    totals_path = os.path.join(OUT, "totals_by_year.csv")
    growth_path = os.path.join(OUT, "matched_by_year.csv")
    corpus_path = os.path.join(OUT, "corpus.jsonl")
    matched_path = os.path.join(OUT, "matched_counts.csv")
    log = lambda *a: print(*a, flush=True)

    # ---- PHASE 1: denominators (total posts per sub per year) ----
    log("== PHASE 1: total posts per sub per year ==")
    with open(totals_path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["subreddit", "year", "total_posts"])
        for sub in SUBREDDITS:
            yrs, st = count(sub, by_year=True)
            if st != "ok" or not yrs:
                log(f"  {sub:22} totals: {st}"); continue
            for yr, c in sorted(yrs.items()):
                if yr.isdigit() and int(yr) >= 2020:
                    w.writerow([sub, yr, c])
            f.flush()
            log(f"  {sub:22} totals ok  ({sum(yrs.values())} since 2020)")

    # ---- PHASE 2: matched counts per sub per query (growth + share) ----
    log("== PHASE 2: matched-by-year for growth/share ==")
    with open(growth_path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["subreddit", "query", "year", "matched"])
        for sub in SUBREDDITS:
            for q in GROWTH_QUERIES:
                yrs, st = count(sub, query=q, by_year=True)
                if st != "ok" or not yrs:
                    continue
                for yr, c in sorted(yrs.items()):
                    if yr.isdigit() and int(yr) >= 2020 and c:
                        w.writerow([sub, q, yr, c])
                f.flush()

    # ---- PHASE 3: harvest on-topic post text ----
    log("== PHASE 3: harvest on-topic post text ==")
    seen = set()
    n_items = 0
    with open(corpus_path, "w") as cf, open(matched_path, "w", newline="") as mf:
        mw = csv.writer(mf); mw.writerow(["subreddit", "query", "matched_total", "harvested", "status"])
        for sub in SUBREDDITS:
            sub_new = 0
            for q in UNIVERSE_QUERIES:
                items, st = harvest(sub, q)
                # only spend a count call when we hit the page cap (to log under-coverage)
                if len(items) >= MAX_PAGES * 100:
                    tot, _ = count(sub, query=q)
                else:
                    tot = len(items)               # harvested everything; count == harvested
                hv = 0
                for it in items:
                    iid = it.get("id")
                    if not iid or iid in seen:
                        continue
                    seen.add(iid)
                    rec = {
                        "id": iid, "subreddit": it.get("subreddit", sub),
                        "created_utc": it.get("created_utc"),
                        "score": it.get("score"), "num_comments": it.get("num_comments"),
                        "title": (it.get("title") or "")[:500],
                        "selftext": (it.get("selftext") or "")[:3000],
                        "permalink": it.get("permalink"),
                        "matched_query": q,
                    }
                    cf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    hv += 1; sub_new += 1; n_items += 1
                cf.flush()
                mw.writerow([sub, q, tot if tot is not None else "", hv, st]); mf.flush()
            log(f"  {sub:22} +{sub_new} new items (corpus={n_items})")
    log(f"DONE. corpus items written: {n_items}")

if __name__ == "__main__":
    main()
