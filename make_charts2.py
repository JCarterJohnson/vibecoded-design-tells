#!/usr/bin/env python3
"""
Additional deliverable charts (1-7) built entirely from cached files on disk.
No re-harvest, no API. Plain-text labels, no emoji glyphs.
"""
import csv, os, json, html, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import analyze as A   # lexicon: TELLS / COMPILED / matches / NEG

OUT = os.path.dirname(os.path.abspath(__file__))
PURPLE, BLUE, GREY = "#7c5cff", "#3b82f6", "#b9b3d6"

def clean(name):
    name = re.sub(r"[^\x00-\x7f]", "", name)          # strip emoji/non-ascii
    name = name.replace(" /  sparkles /  in copy", " / sparkles in copy").replace("  ", " ")
    return name.strip()

def short(name):
    m = {
        "'All looks the same' / template / cookie-cutter": "All look same / cookie-cutter",
        "'Screams AI' / soulless / slop": "Screams AI / slop",
        "shadcn / Tailwind default kit": "shadcn / Tailwind default",
        "Purple / violet (the 'AI purple')": "Purple (AI purple)",
        "Gradients everywhere / gradient text": "Gradients / gradient text",
        "Too many animations / Framer fade-ins": "Too many animations",
        "Rounded corners / pill buttons": "Rounded corners / pills",
        "Dark mode + neon glow": "Dark mode + neon glow",
        "Emoji / sparkles / rockets in copy": "Emoji as icons",
        "Generic sans font (Inter / Geist)": "Generic font (Inter/Geist)",
        "Three-column feature cards": "3 feature cards + CTA",
        "Mesh / blob / aurora backgrounds": "Mesh / blob backgrounds",
        "Centered everything / endless whitespace": "Centered / whitespace",
        "Stock illustrations / clipart": "Stock illustrations",
        "Same hero: huge headline + 2 buttons": "Same hero layout",
        "Glassmorphism / frosted glass": "Glassmorphism",
        "Bento grid": "Bento grid",
    }
    return m.get(name, clean(name))

# ---------- load cached counts ----------
post_counts, post_share, post_neg = {}, {}, {}
with open(os.path.join(OUT, "tell_counts.csv")) as f:
    for r in csv.DictReader(f):
        post_counts[r["tell"]] = int(r["items_mentioning"])
        post_share[r["tell"]] = float(r["share_of_designctx_pct"])
        post_neg[r["tell"]] = float(r["neg_share_of_tell_pct"])
com_counts, com_share = {}, {}
with open(os.path.join(OUT, "comment_tell_counts.csv")) as f:
    for r in csv.DictReader(f):
        com_counts[r["tell"]] = int(r["comments_mentioning"])
        com_share[r["tell"]] = float(r["share_of_comments_pct"])

made = []

# ---------- CHART 1: total scanned per sub (searched subs only, consistent headline) ----------
scan_path = os.path.join(OUT, "scanned_totals_by_sub.csv")
sub_total, sub_harv, searched_rows = {}, {}, []
with open(scan_path) as f:
    for r in csv.DictReader(f):
        s = r["subreddit"]; t = int(r["total_posts"]); hv = int(r["harvested_ontopic"])
        sub_total[s] = t; sub_harv[s] = hv
        if r["full_text_searched"] == "yes":
            searched_rows.append((s, t, hv))
grand = sum(t for _, t, _ in searched_rows)
items = sorted(searched_rows, key=lambda r: r[1])
fig, ax = plt.subplots(figsize=(10, 12))
ax.barh([s for s, _, _ in items], [t for _, t, _ in items], color=PURPLE)
ax.set_xlabel("Total posts in subreddit, 2020 to 2026")
ax.set_title(f"Scale and coverage: {grand:,} posts scanned across {len(searched_rows)} subreddits")
for i, (s, t, _) in enumerate(items):
    ax.text(t, i, f" {t:,}", va="center", fontsize=7)
ax.margins(x=0.13)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_scanned_by_sub.png"), dpi=130); plt.close()
made.append("chart_scanned_by_sub.png")

# ---------- CHART 2: raw mention counts per tell (posts + comments) ----------
tells = list(A.TELLS.keys())
tells = sorted(tells, key=lambda t: -(post_counts.get(t, 0) + com_counts.get(t, 0)))
y = np.arange(len(tells)); h = 0.4
pc = [post_counts.get(t, 0) for t in tells]; cc = [com_counts.get(t, 0) for t in tells]
fig, ax = plt.subplots(figsize=(11, 9))
ax.barh(y + h/2, pc, h, label="posts matching", color=GREY)
ax.barh(y - h/2, cc, h, label="comments matching", color=PURPLE)
ax.set_yticks(y); ax.set_yticklabels([short(t) for t in tells]); ax.invert_yaxis()
ax.set_xlabel("Raw number of items matching the tell (log scale)")
ax.set_xscale("log")
ax.set_title("Raw mention counts per tell (the numerators behind the percentages)")
for i, t in enumerate(tells):
    ax.text(max(pc[i], cc[i]) * 1.05, i, f" {pc[i]+cc[i]:,} total", va="center", fontsize=7)
ax.legend(loc="lower right"); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_raw_counts_by_tell.png"), dpi=130); plt.close()
made.append("chart_raw_counts_by_tell.png")

# ---------- CHART 3: funnel ----------
stages = [("Posts scanned\n(47 subs)", grand)]
stages += [("On-topic posts\n(matched)", 46971), ("Design-context\nposts", 32822), ("Canonical-thread\ncomments", 3033)]
fig, ax = plt.subplots(figsize=(9, 5.5))
labels = [s for s, _ in stages]; vals = [v for _, v in stages]
bars = ax.bar(labels, vals, color=[GREY, PURPLE, PURPLE, BLUE][:len(stages)])
ax.set_yscale("log"); ax.set_ylabel("items (log scale)")
ax.set_title("How the universe narrows to the clean signal")
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_funnel.png"), dpi=130); plt.close()
made.append("chart_funnel.png")

from collections import Counter, defaultdict

# ---------- CHART 4: concentration (on-topic share of sub's own total) ----------
rows = []
for s, t, hv in searched_rows:
    if t >= 1000 and hv >= 20:                     # avoid tiny-N noise
        rows.append((s, hv / t * 100, hv, t))
rows.sort(key=lambda r: r[1])
fig, ax = plt.subplots(figsize=(10, 9))
ax.barh([r[0] for r in rows], [r[1] for r in rows], color=PURPLE)
ax.set_xlabel("On-topic vibe-coded posts as percent of the subreddit's own posts")
ax.set_title("Where the complaints concentrate (on-topic share of each sub, subs with >=1000 posts)")
for i, r in enumerate(rows):
    ax.text(r[1], i, f" {r[1]:.1f}% ({r[2]}/{r[3]:,})", va="center", fontsize=7)
ax.margins(x=0.18); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_concentration.png"), dpi=130); plt.close()
made.append("chart_concentration.png")

# ---------- CHART 5: tell co-occurrence heatmap (comments, cleaner signal) ----------
top = [t for t in sorted(A.TELLS, key=lambda t: -com_counts.get(t, 0))][:10]
comments = []
for line in open(os.path.join(OUT, "comments.jsonl")):
    try:
        d = json.loads(line); comments.append(html.unescape(d.get("body") or ""))
    except: pass
tagsets = []
for txt in comments:
    present = [t for t in top if A.matches(txt, t)]
    if present: tagsets.append(set(present))
n = len(top)
M = np.zeros((n, n), dtype=int)
for s in tagsets:
    idx = [top.index(t) for t in s]
    for a in idx:
        for b in idx:
            M[a][b] += 1
fig, ax = plt.subplots(figsize=(10, 8.5))
im = ax.imshow(M, cmap="Purples")
ax.set_xticks(range(n)); ax.set_xticklabels([short(t) for t in top], rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(n)); ax.set_yticklabels([short(t) for t in top], fontsize=8)
for i in range(n):
    for j in range(n):
        if M[i][j]:
            ax.text(j, i, M[i][j], ha="center", va="center", fontsize=7,
                    color="white" if M[i][j] > M.max()*0.55 else "black")
ax.set_title("Tell co-occurrence in the same comment (diagonal = total mentions)")
fig.colorbar(im, fraction=0.046, pad=0.04); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_cooccurrence.png"), dpi=130); plt.close()
made.append("chart_cooccurrence.png")

# ---------- CHART 6: negative-sentiment share by tell (post-level, matches the 91% figure) ----------
senti = [(t, post_neg.get(t, 0)) for t in sorted(A.TELLS, key=lambda t: -post_counts.get(t, 0))[:11]]
senti.sort(key=lambda r: r[1])
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh([short(t) for t, _ in senti], [v for _, v in senti], color=PURPLE)
ax.set_xlabel("Percent of post-level mentions carrying negative sentiment")
ax.set_title("Negative-sentiment share by tell (keyword-based, post-level)")
for i, (t, v) in enumerate(senti):
    ax.text(v, i, f" {v:.0f}%", va="center", fontsize=8)
ax.margins(x=0.10); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_sentiment_by_tell.png"), dpi=130); plt.close()
made.append("chart_sentiment_by_tell.png")

# ---------- CHART 7: top canonical threads by upvotes ----------
done = set()
if os.path.exists(os.path.join(OUT, "comments_done.txt")):
    done = {l.strip() for l in open(os.path.join(OUT, "comments_done.txt")) if l.strip()}
ONTOPIC = re.compile(r"(ai|vibe|generated|slop|claude|gpt|cursor)", re.I)
SITE = re.compile(r"(website|web ?site|site|design|\bui\b|\bux\b|landing|web ?page|\bapp\b|frontend|interface|theme)", re.I)
meta = {}
for line in open(os.path.join(OUT, "corpus.jsonl")):
    try:
        d = json.loads(line)
        title = d.get("title") or ""
        if d["id"] in done and ONTOPIC.search(title) and SITE.search(title):
            meta[d["id"]] = (d.get("score") or 0, title[:46], d.get("subreddit"))
    except: pass
threads = sorted(meta.values(), key=lambda x: x[0])[-12:]
fig, ax = plt.subplots(figsize=(11, 7))
ax.barh([f"r/{t[2]}: {clean(t[1])}" for t in threads], [t[0] for t in threads], color=PURPLE)
ax.set_xlabel("Thread upvotes")
ax.set_title("Top canonical threads behind the comment signal")
for i, t in enumerate(threads):
    ax.text(t[0], i, f" {t[0]:,}", va="center", fontsize=7)
ax.margins(x=0.12); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_top_threads.png"), dpi=130); plt.close()
made.append("chart_top_threads.png")

print("made:", made)
