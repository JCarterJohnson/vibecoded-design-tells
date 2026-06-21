#!/usr/bin/env python3
"""
collect.py - Mine Reddit (via the free Arctic Shift archive) for discussion of
how to spot AI-written text ("AI-isms"), across a wide net of AI-focused and
SaaS-focused communities, since 2021.

Access mechanism: Arctic Shift public archive (arctic-shift.photon-reddit.com).
No key, no auth, stdlib only. POSTS full-text search only (comment full-text
search times out server-side right now). Precise AND match across title+selftext.

Reading rule downstream: use SHARE of posts, not raw count, because subs grow.
This script just collects; analyze.py does the normalization.
"""
import urllib.request, urllib.parse, json, time, os, sys

BASE = "https://arctic-shift.photon-reddit.com/api/posts/search"
UA = "unslop-ai-research/1.0 (personal research; polite)"
AFTER = "2021-01-01"          # past ~5 years
START_BEFORE = 1798761600     # 2027-01-01, safely in the future
LIMIT = 100                   # API max per request
MAX_PAGES = 2                 # cap pages per (sub,query) => up to 200 posts; logged if hit
SLEEP = 0.35                  # polite gap between requests (seconds); 429 backoff still applies
FIELDS = "id,title,selftext,subreddit,author,created_utc,score,num_comments"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus_raw.jsonl")
DONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "done_pairs.txt")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_log.txt")

# ---------------------------------------------------------------------------
# Communities: a wide net. Medium / topical subs where the conversation
# actually happens. Tagged by lane so analyze.py can treat AI-lane posts as
# AI-context by default.
# ---------------------------------------------------------------------------
SUBREDDITS = {
    # --- AI-focused (cast as wide as possible) ---
    "ChatGPT": "ai", "OpenAI": "ai", "ChatGPTPro": "ai", "ChatGPTCoding": "ai",
    "ChatGPTPromptGenius": "ai", "artificial": "ai", "ArtificialInteligence": "ai",
    "singularity": "ai", "LocalLLaMA": "ai", "ClaudeAI": "ai", "Bard": "ai",
    "GoogleGeminiAI": "ai", "GeminiAI": "ai", "perplexity_ai": "ai",
    "PromptEngineering": "ai", "LLMDevs": "ai", "AI_Agents": "ai",
    "aiwars": "ai", "deeplearning": "ai", "MachineLearning": "ai",
    "OpenAIDev": "ai", "GPT3": "ai", "Automate": "ai",
    # --- writing / detection (highly on-topic for "spotting AI text") ---
    "WritingWithAI": "writing", "writing": "writing", "freelanceWriters": "writing",
    "Copywriting": "writing", "editors": "writing", "selfpublish": "writing",
    "Professors": "writing", "Teachers": "writing", "Blogging": "writing",
    # --- SaaS / startup / marketing (where AI copy floods in) ---
    "SaaS": "saas", "startups": "saas", "Entrepreneur": "saas",
    "EntrepreneurRideAlong": "saas", "indiehackers": "saas", "microsaas": "saas",
    "SideProject": "saas", "marketing": "saas", "digital_marketing": "saas",
    "content_marketing": "saas", "SEO": "saas", "juststart": "saas",
    "Affiliatemarketing": "saas", "Emailmarketing": "saas", "smallbusiness": "saas",
}

# ---------------------------------------------------------------------------
# Family A: discussion-intent phrases. These reliably mean "someone is talking
# about whether text is AI-written / how to spot it" rather than incidental use.
# (Stopwords are ignored by the index; content words are AND-matched.)
# ---------------------------------------------------------------------------
QUERIES_A = [
    "sounds like ChatGPT", "sounds like AI", "reads like AI", "written by AI",
    "obviously AI", "AI slop", "looks AI generated", "ChatGPT wrote this",
    "spot AI writing", "detect AI writing", "ChatGPT writing style",
    "AI writing tells", "telltale signs ChatGPT", "screams AI",
]

# ---------------------------------------------------------------------------
# Family B: candidate AI-isms (specific tells). DISTINCTIVE ones run everywhere;
# GENERIC single words run only on ai+writing subs (in SaaS they're normal usage
# and would be noise). analyze.py keeps a Family-B hit only if the post is in an
# AI lane or its text carries an AI marker.
# ---------------------------------------------------------------------------
QUERIES_B_DISTINCTIVE = [
    "delve", "tapestry", "rich tapestry", "em dash", "em-dash",
    "testament to", "game changer", "in conclusion", "buckle up",
    "let's dive in", "dive deep", "navigating the", "ever-evolving",
    "look no further", "rest assured", "it's worth noting", "underscores the",
    "i hope this email finds you well", "as an AI", "as a large language model",
    "would you like me to", "let me know if", "I cannot fulfill",
    "not just X but Y", "it's not just", " chef's kiss",
]
QUERIES_B_GENERIC = [
    "leverage", "robust", "seamless", "elevate", "comprehensive", "meticulous",
    "intricate", "moreover", "furthermore", "boasts", "realm", "vibrant",
    "captivating", "myriad", "plethora", "paramount", "pivotal", "harness",
    "unleash", "unlock", "showcase", "facilitate", "utilize", "crucial",
    "vital", "bustling", "embark", "foster",
]

def log(msg):
    line = f"[{int(_now())}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

# time.time() is allowed (not Date.now in a workflow); plain script context.
def _now():
    return time.time()

def fetch(params, tries=6):
    """Return (status, data_list_or_msg). Backs off on 429; clean-skips 422/400."""
    url = BASE + "?" + urllib.parse.urlencode(params)
    delay = 2.0
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
                d = data.get("data") if isinstance(data, dict) else data
                return r.status, (d if isinstance(d, list) else [])
        except urllib.error.HTTPError as e:
            code = e.code
            if code == 429:
                time.sleep(delay); delay = min(delay * 2, 60); continue
            if code in (422, 400):
                return code, e.read()[:160].decode("utf-8", "replace")  # deterministic skip
            # other 5xx: brief retry
            time.sleep(delay); delay = min(delay * 2, 30); continue
        except Exception as e:
            time.sleep(delay); delay = min(delay * 2, 30); continue
    return "FAIL", "exhausted retries"

def load_done():
    if not os.path.exists(DONE):
        return set()
    with open(DONE) as f:
        return set(line.rstrip("\n") for line in f)

def mark_done(key):
    with open(DONE, "a") as f:
        f.write(key + "\n")

def collect_pair(sub, query, family, out_f):
    """Paginate one (sub, query) pair; append posts. Returns count or -1 if skipped."""
    before = START_BEFORE
    total = 0
    for page in range(MAX_PAGES):
        params = {"subreddit": sub, "query": query, "after": AFTER,
                  "before": before, "limit": LIMIT, "fields": FIELDS, "sort": "desc"}
        status, data = fetch(params)
        if status in (422, 400):
            log(f"  SKIP {sub} q='{query}' -> {status} {str(data)[:60]}")
            return -1
        if status == "FAIL":
            log(f"  FAIL {sub} q='{query}' (kept partial {total})")
            return total
        if not data:
            break
        for it in data:
            it["_q"] = query
            it["_family"] = family
            it["_lane"] = SUBREDDITS.get(sub, "?")
            if isinstance(it.get("selftext"), str) and len(it["selftext"]) > 4000:
                it["selftext"] = it["selftext"][:4000]  # bound file size; enough to detect AI-isms
            out_f.write(json.dumps(it, ensure_ascii=False) + "\n")
        total += len(data)
        oldest = min(int(x.get("created_utc", before)) for x in data)
        if len(data) < LIMIT:
            break
        before = oldest - 1
        if page == MAX_PAGES - 1:
            log(f"  CAP  {sub} q='{query}' hit MAX_PAGES ({total} posts, may be truncated)")
        time.sleep(SLEEP)
    return total

def main():
    done = load_done()
    # Build the full job list.
    jobs = []
    for sub, lane in SUBREDDITS.items():
        for q in QUERIES_A:
            jobs.append((sub, q, "A"))
        for q in QUERIES_B_DISTINCTIVE:
            jobs.append((sub, q, "B"))
        # Generic single-word AI-isms (QUERIES_B_GENERIC) are intentionally NOT
        # collected as queries (too noisy in SaaS subs). analyze.py detects them
        # via the lexicon over the on-topic corpus instead -> cleaner share.
    log(f"START {len(jobs)} (sub,query) jobs; {len(done)} already done")
    grand = 0
    with open(OUT, "a", encoding="utf-8") as out_f:
        for i, (sub, q, fam) in enumerate(jobs):
            key = f"{sub}\t{q}"
            if key in done:
                continue
            n = collect_pair(sub, q, fam, out_f)
            out_f.flush()
            mark_done(key)
            if n and n > 0:
                grand += n
            if i % 25 == 0:
                log(f"progress {i}/{len(jobs)} pairs; ~{grand} posts this run")
            time.sleep(SLEEP)
    log(f"DONE this run; ~{grand} posts appended -> {OUT}")

if __name__ == "__main__":
    main()
