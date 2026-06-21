#!/usr/bin/env python3
"""
Scale, growth, and structure charts for the AI-writing-tells study, built from the cached
findings CSVs plus the local raw corpus. Mirrors the UI study's make_charts2.py: it
imports the analyzer (analyze.py) to rebuild the exact on-topic corpus, so every
corpus-derived number matches the published tables. No re-harvest, no API.
"""
import csv, os, json, html, re, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import analyze as A   # FAMILY_A / AI_MARKER / ONTOPIC_RX / LEX / year_of

OUT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(OUT, "corpus_raw.jsonl")
PURPLE, BLUE, GREY = "#7c5cff", "#3b82f6", "#b9b3d6"
AUDITED = 600   # posts read in the citation-extraction pass (analyze.py cand[:600])

CAT_COLOR = {"diction": PURPLE, "phrasing": BLUE, "format": "#e0a3ff", "artifact": "#9b87f5"}

def short(name):
    name = re.sub(r"\s+", " ", name).strip()
    m = {
        'em dash ("—") as a tell': "Em dash (—)",
        'bolded lead-in bullets (**Word:**)': "Bolded lead-in bullets",
        '"it\'s not just X, it\'s Y"': '"not just X, it\'s Y"',
        'everything in bullet points / lists': "Bullet lists / listicles",
        'game-changer': "game-changer",
        '"dive in" / "deep dive" / "let\'s dive"': '"dive in" / "deep dive"',
        'headers / bold everywhere / markdown': "Headers / bold / markdown",
        '"in conclusion" / "in summary"': '"in conclusion / in summary"',
        '"it\'s important to note/remember"': '"important to note"',
        'perfectly structured / formulaic': "Formulaic / over-structured",
        '"it\'s worth noting"': '"it\'s worth noting"',
        '"in today\'s fast-paced/digital world"': '"in today\'s fast-paced world"',
        '"great question!"': '"great question!"',
        'testament ("a testament to")': "testament",
        '"let me know if you\'d like / feel free"': '"let me know if you\'d like"',
        'ever-evolving / ever-changing': "ever-evolving",
        '"I cannot/can\'t assist/fulfill"': '"I cannot assist/fulfill"',
        '"rule of three" / triads': "Rule of three / triads",
        '"I hope this email finds you well"': '"hope this email finds you well"',
        '"knowledge cutoff / as of my last update"': '"knowledge cutoff"',
        'embark ("embark on a journey")': "embark",
        '"I hope this helps!"': '"I hope this helps!"',
        'rhetorical question then answer': "Rhetorical Q then answer",
        '"would you like me to ...?"': '"would you like me to"',
        'nuanced / nuance': "nuanced / nuance",
        'navigate / navigating': "navigate / navigating",
        'unlock ("unlock the potential")': "unlock",
        'overuse of "however," / "thus," / "hence"': '"however / thus / hence"',
        'overuse of "moreover/furthermore/additionally"': '"moreover / furthermore"',
        '"when it comes to"': '"when it comes to"',
        'utilize (instead of "use")': "utilize",
        'harness ("harness the power")': "harness",
        '"not only ... but also"': '"not only ... but also"',
        'realm ("in the realm of")': "realm",
        'intricate / intricacies': "intricate",
        'meticulous(ly)': "meticulous",
        'seamless(ly)': "seamless",
        'elevate / elevating': "elevate",
        '"first/secondly/lastly" stack': '"first / secondly / lastly"',
        '"the world of ..."': '"the world of"',
        'underscore(s)': "underscore",
        '"at the end of the day"': '"at the end of the day"',
    }
    if name in m:
        return m[name]
    name = re.sub(r'\s*\(.*?\)\s*', '', name)  # drop parentheticals
    return (name[:30] + "...") if len(name) > 33 else name

# ---------------- rebuild the exact on-topic corpus (mirrors analyze.main) ----------------
def load_corpus():
    posts = {}
    for line in open(RAW, encoding="utf-8"):
        try:
            it = json.loads(line)
        except Exception:
            continue
        pid = it.get("id")
        if not pid:
            continue
        if pid not in posts:
            posts[pid] = {
                "id": pid, "sub": it.get("subreddit", ""), "lane": it.get("_lane", "?"),
                "score": it.get("score", 0) or 0, "ncom": it.get("num_comments", 0) or 0,
                "year": A.year_of(it.get("created_utc", 0)),
                "text": ((it.get("title") or "") + "\n" + (it.get("selftext") or "")),
                "title": it.get("title") or "", "qs": set(),
            }
        posts[pid]["qs"].add(it.get("_q", ""))
    allp = list(posts.values())
    for p in allp:
        p["is_A"] = bool(p["qs"] & A.FAMILY_A)
    loose = [p for p in allp if p["is_A"]]
    # the tight on-topic filter only matters for Family-A posts, so only scan those
    corpusA = [p for p in loose if A.ONTOPIC_RX.search(p["text"])]
    return allp, loose, corpusA

allp, loose, corpusA = load_corpus()
N = len(corpusA)
print(f"unique posts={len(allp)}  Family-A loose={len(loose)}  on-topic(tight)={N}")
made = []

# ---------------- CHART: regex/keyword ranking (post-level, lens 1) ----------------
# Analog of the UI study's chart_tells_ranked: the broad keyword pass over all on-topic
# posts. Secondary to the cited ranking, kept because it covers the full lexicon.
lens1 = []
with open(os.path.join(OUT, "findings_lens1.csv")) as f:
    for r in csv.DictReader(f):
        lens1.append((r["category"], r["tell"], int(r["posts_mentioning"]),
                      float(r["share_pct_of_ontopic"]), r["confidence"]))
top = sorted(lens1, key=lambda r: r[3], reverse=True)[:28]
top = sorted(top, key=lambda r: r[3])
fig, ax = plt.subplots(figsize=(11, 10))
ax.barh([short(t[1]) for t in top], [t[3] for t in top],
        color=[CAT_COLOR.get(t[0], PURPLE) for t in top])
ax.set_xlabel("Share of on-topic posts whose text matches the tell (%)")
ax.set_title(f"Keyword pass: AI-writing tells by share of on-topic posts\n"
             f"(n={N:,} on-topic posts, 2021-2026; broad lexicon, noisier than the cited ranking)")
for i, t in enumerate(top):
    ax.text(t[3], i, f" {t[3]:.1f}%", va="center", fontsize=7)
ax.margins(x=0.1)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (PURPLE, BLUE, "#e0a3ff", "#9b87f5")]
ax.legend(handles, ["diction", "phrasing", "format", "artifact"], loc="lower right", fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_tells_ranked.png"), dpi=130); plt.close()
made.append("chart_tells_ranked.png")

# ---------------- CHART: topic growth (share, not raw) ----------------
# Analog of chart_growth. The text corpus has no neutral base (only query hits), so we
# normalize on-topic posts against all unique posts pulled that year: the share of the
# AI-discussion pull that is genuinely about spotting AI writing.
years = [2021, 2022, 2023, 2024, 2025, 2026]
tot_y = collections.Counter(p["year"] for p in allp)
on_y = collections.Counter(p["year"] for p in corpusA)
share_y = [on_y[y] / tot_y[y] * 100 if tot_y[y] else 0 for y in years]
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar([str(y) for y in years], share_y, color=PURPLE)
ax.set_ylabel("On-topic posts as % of that year's pulled posts")
ax.set_title("Talk of AI-writing tells, growth-normalized\n"
             "(share of the AI-discussion posts pulled each year; 2026 is a partial year)")
for b, v, y in zip(bars, share_y, years):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:.1f}%\n({on_y[y]:,})", ha="center", va="bottom", fontsize=8)
ax.margins(y=0.15)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_growth.png"), dpi=130); plt.close()
made.append("chart_growth.png")

# ---------------- CHART: top tells, share by year (trend) ----------------
# Analog of chart_tell_trend, straight from the per-year columns in findings_lens1.csv.
byrow = {}
with open(os.path.join(OUT, "findings_lens1.csv")) as f:
    rdr = csv.DictReader(f)
    yrcols = [c for c in rdr.fieldnames if re.fullmatch(r"share_\d{4}", c)]
    yrs = [int(c.split("_")[1]) for c in yrcols]
    for r in rdr:
        byrow[r["tell"]] = [float(r[c]) for c in yrcols]
TREND = ['em dash ("—") as a tell', '"it\'s not just X, it\'s Y"',
         'bolded lead-in bullets (**Word:**)', 'delve', 'game-changer',
         '"dive in" / "deep dive" / "let\'s dive"']
fig, ax = plt.subplots(figsize=(9.5, 5.8))
for tell in TREND:
    if tell in byrow:
        ax.plot(yrs, byrow[tell], marker="o", label=short(tell))
ax.set_xlabel("Year"); ax.set_ylabel("% of that year's on-topic posts")
ax.set_title("Top tells, share by year\n(the em dash is the signature ChatGPT-era arrival: ~0 before 2024)")
ax.set_xticks(yrs)
ax.legend(fontsize=8, ncol=2)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_tell_trend.png"), dpi=130); plt.close()
made.append("chart_tell_trend.png")

# ---------------- CHART: scale and coverage (posts per subreddit) ----------------
# Analog of chart_scanned_by_sub. Unique posts pulled per subreddit (the searched base).
sub_all = collections.Counter(p["sub"] for p in allp)
items = sub_all.most_common(30)[::-1]
grand = sum(sub_all.values())
fig, ax = plt.subplots(figsize=(10, 11))
ax.barh([s for s, _ in items], [c for _, c in items], color=PURPLE)
ax.set_xlabel("Unique posts pulled from the subreddit, 2021-2026")
ax.set_title(f"Scale and coverage: {grand:,} unique posts across {len(sub_all)} subreddits\n(top 30 shown)")
for i, (s, c) in enumerate(items):
    ax.text(c, i, f" {c:,}", va="center", fontsize=7)
ax.margins(x=0.13)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_scanned_by_sub.png"), dpi=130); plt.close()
made.append("chart_scanned_by_sub.png")

# ---------------- CHART: raw mention counts per tell (numerators) ----------------
# Analog of chart_raw_counts_by_tell: the actual post counts behind the percentages.
rc = sorted(lens1, key=lambda r: r[2], reverse=True)[:30]
rc = sorted(rc, key=lambda r: r[2])
fig, ax = plt.subplots(figsize=(11, 10))
ax.barh([short(t[1]) for t in rc], [t[2] for t in rc],
        color=[CAT_COLOR.get(t[0], PURPLE) for t in rc])
ax.set_xlabel("Number of on-topic posts whose text matches the tell (log scale)")
ax.set_xscale("log")
ax.set_title("Raw mention counts per tell (the numerators behind the percentages)")
for i, t in enumerate(rc):
    ax.text(t[2] * 1.03, i, f" {t[2]:,}", va="center", fontsize=7)
ax.margins(x=0.12)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_raw_counts_by_tell.png"), dpi=130); plt.close()
made.append("chart_raw_counts_by_tell.png")

# ---------------- CHART: the funnel ----------------
# Analog of chart_funnel: how the pulled posts narrow to the cleanest audited signal.
raw_hits = sum(1 for _ in open(RAW))
stages = [("Raw query hits", raw_hits), ("Unique posts", len(allp)),
          ("On-topic posts", N), ("Audited sample\n(cited-tell pass)", AUDITED)]
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar([s for s, _ in stages], [v for _, v in stages], color=[GREY, GREY, PURPLE, BLUE])
ax.set_yscale("log"); ax.set_ylabel("posts (log scale)")
ax.set_title("How the pull narrows to the clean signal")
for b, (_, v) in zip(bars, stages):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_funnel.png"), dpi=130); plt.close()
made.append("chart_funnel.png")

# ---------------- CHART: where the discussion concentrates ----------------
# Analog of chart_concentration: on-topic posts as a share of each sub's own pulled volume.
sub_on = collections.Counter(p["sub"] for p in corpusA)
rows = []
for s, tot in sub_all.items():
    if tot >= 200 and sub_on[s] >= 15:   # avoid tiny-N noise
        rows.append((s, sub_on[s] / tot * 100, sub_on[s], tot))
rows.sort(key=lambda r: r[1])
rows = rows[-22:]
fig, ax = plt.subplots(figsize=(10, 9))
ax.barh([r[0] for r in rows], [r[1] for r in rows], color=PURPLE)
ax.set_xlabel("On-topic posts as percent of the subreddit's own pulled posts")
ax.set_title("Where the AI-writing complaints concentrate\n(on-topic share of each sub, subs with >=200 pulled posts)")
for i, r in enumerate(rows):
    ax.text(r[1], i, f" {r[1]:.1f}% ({r[2]}/{r[3]:,})", va="center", fontsize=7)
ax.margins(x=0.2)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_concentration.png"), dpi=130); plt.close()
made.append("chart_concentration.png")

# ---------------- CHART: tell co-occurrence ----------------
# Analog of chart_cooccurrence: how often two tells show up in the same on-topic post.
counts = {}
for cat, label, pats in A.LEX:
    counts[label] = sum(1 for p in corpusA if any(pat.search(p["text"]) for pat in pats))
topn = [lab for lab in sorted(counts, key=lambda l: -counts[l])][:10]
pats_for = {label: pats for cat, label, pats in A.LEX}
n = len(topn)
M = np.zeros((n, n), dtype=int)
for p in corpusA:
    present = [i for i, lab in enumerate(topn) if any(pat.search(p["text"]) for pat in pats_for[lab])]
    for a in present:
        for b in present:
            M[a][b] += 1
fig, ax = plt.subplots(figsize=(10, 8.8))
im = ax.imshow(M, cmap="Purples")
ax.set_xticks(range(n)); ax.set_xticklabels([short(l) for l in topn], rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(n)); ax.set_yticklabels([short(l) for l in topn], fontsize=8)
for i in range(n):
    for j in range(n):
        if M[i][j]:
            ax.text(j, i, M[i][j], ha="center", va="center", fontsize=7,
                    color="white" if M[i][j] > M.max() * 0.55 else "black")
ax.set_title("Tell co-occurrence in the same on-topic post (diagonal = total posts)")
fig.colorbar(im, fraction=0.046, pad=0.04)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_cooccurrence.png"), dpi=130); plt.close()
made.append("chart_cooccurrence.png")

# ---------------- CHART: share by tell category ----------------
# Replaces the UI study's chart_sentiment_by_tell (the text corpus is complaint-selected,
# so per-tell sentiment is ~uniformly negative and uninformative). Instead: what share of
# on-topic posts touch each FAMILY of tell (diction words, phrasing, format, artifacts)?
cats = ["diction", "phrasing", "format", "artifact"]
cat_pats = {c: [pats for (cat, lab, pats) in A.LEX if cat == c] for c in cats}
cat_share = {}
for c in cats:
    plist = cat_pats[c]
    hit = sum(1 for p in corpusA if any(pat.search(p["text"]) for pats in plist for pat in pats))
    cat_share[c] = hit / N * 100
order = sorted(cats, key=lambda c: cat_share[c])
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh([c for c in order], [cat_share[c] for c in order],
               color=[CAT_COLOR[c] for c in order])
ax.set_xlabel("Share of on-topic posts that name at least one tell in the family (%)")
ax.set_title("AI-writing tells by family\n(diction words, sentence phrasing, formatting, and pasted assistant artifacts)")
for i, c in enumerate(order):
    ax.text(cat_share[c], i, f" {cat_share[c]:.1f}%", va="center", fontsize=9)
ax.margins(x=0.12)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_by_category.png"), dpi=130); plt.close()
made.append("chart_by_category.png")

# ---------------- CHART: top on-topic posts (threads) by upvotes ----------------
# Analog of chart_top_threads.
threads = sorted(corpusA, key=lambda p: p["score"])[-12:]
fig, ax = plt.subplots(figsize=(11, 7))
ax.barh([f"r/{p['sub']}: {re.sub(chr(92)+'s+',' ', p['title'])[:44]}" for p in threads],
        [p["score"] for p in threads], color=PURPLE)
ax.set_xlabel("Post upvotes")
ax.set_title("Top on-topic posts behind the signal")
for i, p in enumerate(threads):
    ax.text(p["score"], i, f" {p['score']:,}", va="center", fontsize=7)
ax.margins(x=0.13)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_top_threads.png"), dpi=130); plt.close()
made.append("chart_top_threads.png")

# ---------------- CHART: Lens 2 - AI-context airtime by named term ----------------
# Text-specific (no UI analog): for the distinctive terms queried directly, what share of
# their mentions land in an AI context, and across how many subreddits (breadth).
l2 = []
with open(os.path.join(OUT, "findings_lens2.csv")) as f:
    for r in csv.DictReader(f):
        l2.append((r["term"], int(r["ai_context_posts"]), float(r["share_pct_of_term_mentions"]),
                   int(r["n_subreddits"])))
l2 = sorted(l2, key=lambda r: r[1])[-18:]
fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh([t[0] for t in l2], [t[1] for t in l2], color=PURPLE)
ax.set_xlabel("Posts where the term appears in an AI-writing context")
ax.set_title("Lens 2: AI-context airtime by named term\n(directly-queried tells; label shows breadth across subreddits)")
for i, t in enumerate(l2):
    ax.text(t[1], i, f" {t[1]:,} ({t[3]} subs)", va="center", fontsize=7)
ax.margins(x=0.16)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_lens2_terms.png"), dpi=130); plt.close()
made.append("chart_lens2_terms.png")

print("made:", made)
