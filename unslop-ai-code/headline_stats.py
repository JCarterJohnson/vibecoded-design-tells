#!/usr/bin/env python3
"""Headline scale + 5-year growth numbers for the write-up."""
import json, os, csv, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))

posts = [json.loads(l) for l in open(os.path.join(HERE,"corpus.jsonl"))]
ncom = sum(1 for _ in open(os.path.join(HERE,"comments.jsonl")))
threads = len(set(json.loads(l)["link_id"] for l in open(os.path.join(HERE,"comments.jsonl"))))

lane = collections.Counter(p.get("lane","?") for p in posts)
subs = collections.Counter(p["subreddit"] for p in posts)
yr = collections.Counter()
for p in posts:
    try: yr[datetime.datetime.fromtimestamp(int(p["created_utc"]), datetime.UTC).year]+=1
    except Exception: pass

print("on-topic posts: %d" % len(posts))
print("on-topic comments: %d  from %d canonical threads" % (ncom, threads))
print("subreddits with >=1 on-topic post: %d" % len(subs))
print("by lane:", dict(lane))
print("posts by year:", dict(sorted(yr.items())))

# scanned base + growth (per-10k) where denominators exist
tot_by_sub_year = collections.defaultdict(int)
have_denom = set()
if os.path.exists(os.path.join(HERE,"totals_by_year.csv")):
    for r in csv.DictReader(open(os.path.join(HERE,"totals_by_year.csv"))):
        if r["query"]=="_ALL_":
            try:
                tot_by_sub_year[(r["subreddit"],int(r["year"]))]=int(r["posts"])
                have_denom.add(r["subreddit"])
            except Exception: pass
scanned = sum(tot_by_sub_year.values())
print("\nsubs with usable denominators: %d" % len(have_denom))
print("scanned base (posts 2020-2026 in those subs): %d" % scanned)

# growth: on-topic matched per 10k posts per year, restricted to subs with denominators
tot_year = collections.Counter()
for (s,y),c in tot_by_sub_year.items(): tot_year[y]+=c
match_year = collections.Counter()
for p in posts:
    if p["subreddit"] in have_denom:
        try: match_year[datetime.datetime.fromtimestamp(int(p["created_utc"]), datetime.UTC).year]+=1
        except Exception: pass
print("\nGROWTH (on-topic per 10k posts, subs with denominators):")
for y in range(2020,2027):
    if tot_year[y]:
        print("  %d: %.1f per 10k  (matched=%d / total=%d)" % (y, 10000*match_year[y]/tot_year[y], match_year[y], tot_year[y]))

print("\ntop 20 subs by on-topic posts:")
for s,c in subs.most_common(20): print("  %-22s %d  [%s]"%(s,c,
    'ai' if any(p['lane']=='ai' for p in posts if p['subreddit']==s) else ''))
