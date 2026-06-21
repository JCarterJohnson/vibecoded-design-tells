#!/usr/bin/env python3
"""
collect.py - Mine Reddit (via the free Arctic Shift archive) for discussion of
how to spot AI-WRITTEN CODE: the tells in the actual code itself (comments,
error handling, naming, structure, formatting, leftover artifacts) that give
away that a human did not write it. Wide net across AI-focused, coding/dev
(many languages), and SaaS/indie communities, since 2020 (~5 years).

Access mechanism: Arctic Shift public archive (arctic-shift.photon-reddit.com).
No key, no auth, stdlib only. Two layers, both sequential (the throttle is
sticky; concurrency 429s and corrupts):

  1. AGGREGATE -> total posts per sub per year (the DENOMINATOR). Reading rule
     downstream: SHARE of posts, not raw count, because subreddits grow.
     The aggregate endpoint TIMES OUT (422 "slow down") on the busiest subs even
     though full-text search works there; we get denominators where we can and
     harvest text everywhere.
  2. HARVEST   -> the actual post text of on-topic items (matched an intent
     phrase), so the code "tells" can be tabulated against what people wrote
     and quoted. `query` is an AND over content words and IGNORES STOPWORDS, so
     intent phrases are built from distinctive content-word idioms, never "no X".

Self-bounding (returns before any tool timeout) and resumable (checkpoints every
finished sub|query combo, dedupes corpus by id, appends). Re-run until it prints
ALL-DONE. 422 "slow down" = transient (back off); any other 422/400 = permanent
rejection for that sub+query (skip cleanly, do not burn retries).

Run:  python3 collect.py [max_seconds]    (default 300)
Exit: 0 = everything done, 2 = more combos remain (re-run to resume)
"""
import urllib.request, urllib.parse, json, csv, time, os, sys

BASE = "https://arctic-shift.photon-reddit.com"
UA = {"User-Agent": "unslop-ai-code-research/1.0 (personal research; polite)"}
HERE = os.path.dirname(os.path.abspath(__file__))
START = "2020-01-01"          # past ~5 years
THROTTLE = 0.8                # seconds between calls (polite; sticky throttle)
MAX_PAGES = 2                 # up to 200 newest matched posts per (sub,query)

CORPUS  = os.path.join(HERE, "corpus.jsonl")
TOTALS  = os.path.join(HERE, "totals_by_year.csv")
MATCHED = os.path.join(HERE, "matched_counts.csv")
CKPT    = os.path.join(HERE, "collect_done.txt")
LOG     = os.path.join(HERE, "run_log.txt")

# ---------------------------------------------------------------------------
# Communities: a deliberately wide net of medium/topical subs where this
# conversation actually happens. Tagged by lane so the analysis can treat the
# AI/coding lanes as code-context by default.
#   ai     = AI assistants / coding-agent tool subs
#   code   = language- and craft-specific dev subs (where "this is AI code"
#            critique lives, across many languages)
#   saas   = indie / startup / SaaS launch subs (AI code floods in there too)
# ---------------------------------------------------------------------------
SUBREDDITS = {
    # --- AI assistants & coding-agent tools (cast as wide as possible) ---
    "ChatGPTCoding": "ai", "ChatGPT": "ai", "ChatGPTPro": "ai", "OpenAI": "ai",
    "OpenAIDev": "ai", "ClaudeAI": "ai", "ClaudeCode": "ai", "Anthropic": "ai",
    "cursor": "ai", "vibecoding": "ai", "GithubCopilot": "ai", "copilot": "ai",
    "LocalLLaMA": "ai", "AI_Agents": "ai", "LLMDevs": "ai", "PromptEngineering": "ai",
    "artificial": "ai", "ArtificialInteligence": "ai", "singularity": "ai",
    "GoogleGeminiAI": "ai", "GeminiAI": "ai", "Bard": "ai", "perplexity_ai": "ai",
    "grok": "ai", "aipromptprogramming": "ai", "ChatGPTPromptGenius": "ai",
    # --- coding / dev craft & specific languages (where code gets critiqued) ---
    "programming": "code", "learnprogramming": "code", "webdev": "code",
    "ExperiencedDevs": "code", "cscareerquestions": "code", "codereview": "code",
    "programminghorror": "code", "ProgrammerHumor": "code", "SoftwareEngineering": "code",
    "javascript": "code", "Python": "code", "rust": "code", "golang": "code",
    "cpp": "code", "csharp": "code", "java": "code", "typescript": "code",
    "node": "code", "reactjs": "code", "PHP": "code", "ruby": "code",
    "gamedev": "code", "devops": "code", "dotnet": "code",
    # --- SaaS / indie / startup (some, as requested) ---
    "SaaS": "saas", "startups": "saas", "indiehackers": "saas",
    "SideProject": "saas", "microsaas": "saas", "EntrepreneurRideAlong": "saas",
}

# ---------------------------------------------------------------------------
# Family A: discussion-intent phrases. Each reliably means "someone is talking
# about whether CODE is AI-written / how to spot it", biased toward the code
# itself by carrying a code content-word (code/coding/wrote/function/commit).
# (Stopwords are ignored by the index; the remaining content words are ANDed.)
# ---------------------------------------------------------------------------
QUERIES_A = [
    "AI generated code", "AI written code", "code written by AI",
    "ChatGPT wrote this code", "Copilot generated code", "Claude wrote this code",
    "Cursor generated code", "looks AI generated", "obviously AI code",
    "clearly AI code", "spot AI code", "detect AI code", "tell AI wrote code",
    "AI slop code", "screams AI", "smells like AI", "dead giveaway AI",
    "telltale signs AI", "obvious ChatGPT code", "looks like AI wrote",
    "vibe coded", "vibe coding", "is this AI code", "AI generated commit",
]
# A small set of distinctive tell-naming idioms, run everywhere to surface the
# threads that actually enumerate the tells. Generic single-word tells (e.g.
# "comments", "try except") are NOT queried here -> too noisy in SaaS/code subs.
# analyze.py detects those via the lexicon over the on-topic corpus instead.
QUERIES_B = [
    "rest of your code", "rest of the implementation", "unnecessary comments",
    "over engineered", "placeholder comments", "comments on every line",
    "emoji in code",
]
# Subset used for the per-year growth/share table (cleanest, least-noisy).
GROWTH_QUERIES = ["AI generated code", "vibe coded", "AI slop code", "code written by AI"]

def log(*a):
    line = "[%d] %s" % (int(time.time()), " ".join(str(x) for x in a))
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def get(path, params, tries=6, timeout=90, cap=30):
    """HTTP GET with backoff. Returns (data, status). status in {ok,reject,giveup}."""
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                body = r.read().decode("utf-8", "ignore")
                if not body.strip():                       # empty body => throttle
                    time.sleep(min(2 * (i + 1), cap)); continue
                return json.loads(body).get("data"), "ok"
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore").lower()
            if e.code == 429 or "slow down" in msg or e.code in (500, 502, 503, 504):
                time.sleep(min(2.0 * (i + 1), cap)); continue   # transient -> back off
            return None, "reject"                          # deterministic 422/400/404 -> skip
        except Exception:
            time.sleep(min(2.0 * (i + 1), cap)); continue  # timeout / conn reset
    return None, "giveup"

def count_by_year(sub, query=None):
    # Aggregate HANGS to the socket timeout on busy subs (sticky throttle). Fail
    # FAST: single attempt, short timeout. Denominators are best-effort color;
    # the tell ranking is share-of-on-topic-corpus and does not need them, and
    # growth is recomputed from the harvested corpus itself in analyze.py.
    p = {"subreddit": sub, "after": START, "aggregate": "created_utc", "frequency": "year"}
    if query: p["query"] = query
    data, st = get("/api/posts/search/aggregate", p, tries=1, timeout=9, cap=3)
    time.sleep(THROTTLE)
    if st != "ok" or not data:
        return None, st
    out = {}
    for b in data:
        yr = (b.get("created_utc") or "")[:4]
        try: out[yr] = int(b.get("count", 0))
        except Exception: out[yr] = 0
    return out, "ok"

def harvest(sub, query):
    """Page newest->oldest matched posts. Returns (items, status)."""
    items, before = [], None
    for _ in range(MAX_PAGES):
        p = {"subreddit": sub, "query": query, "limit": "100", "sort": "desc", "after": START}
        if before: p["before"] = str(before)
        data, st = get("/api/posts/search", p)
        time.sleep(THROTTLE)
        if st != "ok":
            return items, (st if not items else "ok")      # keep partial pages
        if not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        before = min(int(x["created_utc"]) for x in data) - 1
    return items, "ok"

def load_lines(path):
    if not os.path.exists(path): return set()
    with open(path) as f:
        return {ln.strip() for ln in f if ln.strip()}

def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    t0 = time.time()
    done = load_lines(CKPT)
    seen = set()
    if os.path.exists(CORPUS):
        for ln in open(CORPUS):
            try: seen.add(json.loads(ln)["id"])
            except Exception: pass

    # HARVEST (the real signal) runs FIRST and resumes by "<sub>|<query>".
    # DENOMINATORS (best-effort color) run LAST, checkpointed per sub
    # ("TOTAL::<sub>"); the aggregate endpoint is flaky on busy subs so a miss is
    # fine -- growth is also recomputed from the harvested corpus in analyze.py.
    # QUERY-MAJOR order: every sub gets the top query before any sub gets the
    # second one. This front-loads breadth (all 56 subs, incl. the language subs)
    # instead of letting the giant ChatGPT subs soak up every page first.
    all_q = QUERIES_A + QUERIES_B
    combos = [(s, q) for q in all_q for s in SUBREDDITS]
    todo = [c for c in combos if ("%s|%s" % c) not in done]
    subs_total_todo = [s for s in SUBREDDITS if ("TOTAL::%s" % s) not in done]
    log("START budget=%ds harvest_todo=%d totals_todo=%d combos_done=%d corpus_ids=%d"
        % (budget, len(todo), len(subs_total_todo), len(done), len(seen)))

    # ---- PHASE 1: harvest on-topic post text ----
    cf = open(CORPUS, "a")
    mf = open(MATCHED, "a", newline=""); mw = csv.writer(mf)
    if os.path.getsize(MATCHED) == 0:
        mw.writerow(["subreddit", "lane", "query", "family", "harvested", "status"])
    ck = open(CKPT, "a")
    processed = new_items = 0
    last_sub = None
    for sub, q in todo:
        if time.time() - t0 > budget:
            log("[pause] budget hit after %d combos this run" % processed); break
        key = "%s|%s" % (sub, q)
        fam = "A" if q in QUERIES_A else "B"
        lane = SUBREDDITS[sub]
        items, st = harvest(sub, q)
        hv = 0
        for it in items:
            iid = it.get("id")
            if not iid or iid in seen: continue
            seen.add(iid)
            rec = {"id": iid, "subreddit": it.get("subreddit", sub), "lane": lane,
                   "created_utc": it.get("created_utc"), "score": it.get("score"),
                   "num_comments": it.get("num_comments"),
                   "title": (it.get("title") or "")[:500],
                   "selftext": (it.get("selftext") or "")[:3500],
                   "permalink": it.get("permalink"),
                   "matched_query": q, "family": fam}
            cf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            hv += 1; new_items += 1
        cf.flush()
        mw.writerow([sub, lane, q, fam, hv, st]); mf.flush()
        ck.write(key + "\n"); ck.flush()
        processed += 1
        if sub != last_sub:
            log("  [%4.0fs] %-22s corpus=%d (+%d this run)" % (time.time()-t0, sub, len(seen), new_items))
            last_sub = sub
    cf.close(); mf.close(); ck.close()
    harvest_remaining = len(todo) - processed
    log("[harvest end] processed=%d new_items=%d corpus_total=%d remaining=%d"
        % (processed, new_items, len(seen), harvest_remaining))

    # ---- PHASE 2: denominators (best-effort; only after harvest is fully done) ----
    totals_remaining = len(subs_total_todo)
    if harvest_remaining == 0 and subs_total_todo:
        write_header = not os.path.exists(TOTALS)
        tf = open(TOTALS, "a", newline=""); tw = csv.writer(tf)
        if write_header: tw.writerow(["subreddit", "lane", "query", "year", "posts"])
        tck = open(CKPT, "a")
        did = 0
        for sub in subs_total_todo:
            if time.time() - t0 > budget:
                log("[pause] budget hit during totals after %d subs" % did); break
            lane = SUBREDDITS[sub]
            yrs, st = count_by_year(sub)                    # one by-year call per sub
            if st == "ok" and yrs:
                for yr, c in sorted(yrs.items()):
                    if yr.isdigit() and int(yr) >= 2020:
                        tw.writerow([sub, lane, "_ALL_", yr, c])
                tf.flush()
            tck.write("TOTAL::%s\n" % sub); tck.flush()
            did += 1
            log("  totals %-22s %s" % (sub, st))
        tf.close(); tck.close()
        totals_remaining = len(subs_total_todo) - did

    all_done = (harvest_remaining == 0 and totals_remaining == 0)
    if all_done:
        log("ALL-DONE")
    sys.exit(0 if all_done else 2)

if __name__ == "__main__":
    main()
