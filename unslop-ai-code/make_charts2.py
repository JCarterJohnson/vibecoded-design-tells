#!/usr/bin/env python3
"""
UI-styled chart set for the AI-code-tells study, mirroring the design study's charts
(and the unslop-ai-text set): the verified ranking, the raw-vs-verified correction, the
LLM-classification ranking, growth, by-year trend, scale, numerators, funnel, top posts,
and the lens-2 idiom airtime. Purple house style, built from the committed findings tables
plus the raw corpus (gunzip corpus.jsonl.gz first).

Skipped vs the design set, by design:
- sentiment_by_tell -> replaced by by_category (the corpus is complaint-selected).
- cooccurrence -> the classifier assigned one primary tell per comment (only 29 of 2,136
  got a second), so a co-occurrence matrix is structurally near-empty.
- concentration -> the on-topic harvest was capped per query (many subs sit at the 200
  cap), so on-topic-share-of-a-sub is distorted and not comparable across subs.
"""
import os, csv, json, collections, datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PURPLE, BLUE, GREY = "#7c5cff", "#3b82f6", "#b9b3d6"
CAT_COLOR = {"structure": PURPLE, "correctness": BLUE, "comments/docs": "#e0a3ff",
             "naming": "#9b87f5", "error handling": "#6d5cd6", "style/format": "#c4b5fd",
             "output": "#b9b3d6", "artifacts": "#8b7fd9"}

def short(s, n=54):
    return s if len(s) <= n else s[:n - 1] + "..."

rows = list(csv.DictReader(open(os.path.join(HERE, "final_tell_counts.csv"))))
def fnum(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0
spec = [r for r in rows if r["code"] != "umbrella_looks_ai"]

# ---------- CHART 1: verified ranking (cleanest signal) ----------
v = [r for r in spec if r["verdict"] != "artifact" and fnum(r["verified_share_pct"]) > 0]
v = sorted(v, key=lambda r: fnum(r["verified_share_pct"]))
fig, ax = plt.subplots(figsize=(11.5, 7.5))
bars = ax.barh([short(r["tell"], 56) for r in v], [fnum(r["verified_share_pct"]) for r in v], color=PURPLE)
for b, r in zip(bars, v):
    ax.text(fnum(r["verified_share_pct"]) + 0.15, b.get_y() + b.get_height()/2,
            f'{fnum(r["verified_share_pct"]):.1f}%', va="center", fontsize=8)
ax.set_xlabel("Share of tell-naming comments that cite the tell (%)")
ax.set_title("What people actually cite as AI-written-code tells\n"
             "(verified, precision-adjusted share of tell-naming comments; cleanest signal)")
ax.margins(x=0.12); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_verified_ranking.png"), dpi=130); plt.close()

# ---------- CHART 2: raw LLM-classification ranking (secondary) ----------
r2 = sorted(spec, key=lambda r: fnum(r["raw_share_pct"]))
fig, ax = plt.subplots(figsize=(11.5, 8))
bars = ax.barh([short(r["tell"], 56) for r in r2], [fnum(r["raw_share_pct"]) for r in r2], color=GREY)
for b, r in zip(bars, r2):
    ax.text(fnum(r["raw_share_pct"]) + 0.12, b.get_y() + b.get_height()/2,
            f'{fnum(r["raw_share_pct"]):.1f}%', va="center", fontsize=7.5)
ax.set_xlabel("Share of tell-naming comments (%), raw LLM classification")
ax.set_title("LLM-classified code tells, raw share (before the precision check)\n"
             "(the broad first cut; several of these get discounted once the quotes are re-read)")
ax.margins(x=0.12); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_tells_ranked.png"), dpi=130); plt.close()

# ---------- CHART 3: raw vs verified, per tell (the precision correction) ----------
rv = sorted([r for r in spec if fnum(r["raw_share_pct"]) > 0],
            key=lambda r: fnum(r["raw_share_pct"]))[-12:]
y = np.arange(len(rv)); h = 0.4
fig, ax = plt.subplots(figsize=(11.5, 7.5))
ax.barh(y + h/2, [fnum(r["verified_share_pct"]) for r in rv], h, label="verified (precision-adjusted)", color=PURPLE)
ax.barh(y - h/2, [fnum(r["raw_share_pct"]) for r in rv], h, label="raw classification", color=GREY)
ax.set_yticks(y); ax.set_yticklabels([short(r["tell"], 48) for r in rv])
ax.set_xlabel("Share of tell-naming comments (%)")
ax.set_title("Raw classification vs verified, per tell\n"
             "(over-commenting and verbose naming shrink most once the quotes are audited)")
ax.legend(loc="lower right"); ax.margins(x=0.02); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_raw_vs_verified.png"), dpi=130); plt.close()

# ---------- CHART 4: comment vs post mentions ----------
cv = sorted([r for r in spec if int(r["comment_mentions"]) > 0], key=lambda r: int(r["comment_mentions"]))[-12:]
y = np.arange(len(cv)); h = 0.4
fig, ax = plt.subplots(figsize=(11, 7.5))
ax.barh(y + h/2, [int(r["comment_mentions"]) for r in cv], h, label="comment mentions", color=PURPLE)
ax.barh(y - h/2, [int(r["post_mentions"]) for r in cv], h, label="post mentions", color=GREY)
ax.set_yticks(y); ax.set_yticklabels([short(r["tell"], 46) for r in cv])
ax.set_xlabel("Number of items naming the tell")
ax.set_title("Each tell: comment vs post mentions\n(comments are the cleaner signal; posts skew toward pasted artifacts)")
ax.legend(loc="lower right"); ax.margins(x=0.08); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_post_vs_comment.png"), dpi=130); plt.close()

# ---------- CHART 5: by category (replaces sentiment) ----------
CAT = {"over_comment": "comments/docs", "redundant_docstring": "comments/docs", "placeholder_comment": "comments/docs",
       "verbose_naming": "naming", "generic_naming": "naming", "excessive_try": "error handling",
       "over_validation": "error handling", "over_engineered": "structure", "boilerplate_tutorial": "structure",
       "reinvent_wheel": "structure", "too_clean": "style/format", "style_mismatch": "style/format",
       "type_everywhere": "style/format", "emoji": "output", "excess_logging": "output",
       "chat_artifact": "artifacts", "hallucinated_api": "correctness", "inconsistent_skill": "correctness"}
agg = collections.defaultdict(float)
for r in rows:
    if r["code"] == "umbrella_looks_ai" or r["verdict"] == "artifact":
        continue
    agg[CAT.get(r["code"], "other")] += fnum(r["verified_share_pct"])
items = sorted(agg.items(), key=lambda kv: kv[1])
fig, ax = plt.subplots(figsize=(9.5, 5.2))
bars = ax.barh([k for k, _ in items], [val for _, val in items],
               color=[CAT_COLOR.get(k, PURPLE) for k, _ in items])
for i, (k, val) in enumerate(items):
    ax.text(val + 0.25, i, f"{val:.0f}%", va="center", fontsize=9)
ax.set_xlabel("Summed verified share of tell-naming comments (%)")
ax.set_title("AI-code tells by family\n(structure and correctness dominate; naming and formatting trail)")
ax.margins(x=0.12); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_by_category.png"), dpi=130); plt.close()

# ---------- load corpus (gunzip corpus.jsonl.gz first) ----------
CORPUS = os.path.join(HERE, "corpus.jsonl")
posts = []
if os.path.exists(CORPUS):
    for line in open(CORPUS):
        try: posts.append(json.loads(line))
        except Exception: pass
def year_of(p):
    try: return datetime.datetime.fromtimestamp(int(p["created_utc"]), datetime.timezone.utc).year
    except Exception: return None

# ---------- CHART 6: growth by year (raw on-topic posts) ----------
yr = collections.Counter(year_of(p) for p in posts if year_of(p))
years = [y for y in range(2020, 2027) if y in yr]
vals = [yr[y] for y in years]
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar([str(y) for y in years], vals, color=PURPLE)
for b, val in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, val, f"{val:,}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("On-topic posts (raw count)")
ax.set_title("Talk of spotting AI-written code, by year\n(barely existed before 2023; 2026 is a partial year)")
ax.margins(y=0.12); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_growth_byyear.png"), dpi=130); plt.close()

# ---------- CHART 7: top tells, share by year (keyword first pass) ----------
byrow = {}
with open(os.path.join(HERE, "tell_share_by_year.csv")) as f:
    rdr = csv.DictReader(f)
    yrcols = [c for c in rdr.fieldnames if c.startswith("share_")]
    yrs = [int(c.split("_")[1]) for c in yrcols]
    for r in rdr:
        byrow[r["tell"]] = [fnum(r[c]) for c in yrcols]
TREND = {
    "boilerplate / scaffolding / tutorial-shaped code": "boilerplate / tutorial-shaped",
    "emoji in code / console logs / commit messages (✅ \U0001f680 \U0001f389)": "emoji in code",
    "markdown / code-fence backticks or '```python' left in the file": "leftover code fences",
    "model self-disclosure / refusal text pasted into code ('As an AI', 'I cannot')": "'As an AI' pasted in",
    "placeholder / ellipsis comments ('// rest of your code', '// ... your logic here')": "placeholder comments",
}
fig, ax = plt.subplots(figsize=(9.5, 5.8))
for full, lab in TREND.items():
    if full in byrow:
        ax.plot(yrs, byrow[full], marker="o", label=lab)
ax.set_xlabel("Year"); ax.set_ylabel("% of that year's tell-bearing posts")
ax.set_title("Code tells, share by year (keyword first pass)\n"
             "(boilerplate rises with the agent era; the 'As an AI' paste-ins fade as people learn to delete them)")
ax.set_xticks(yrs); ax.legend(fontsize=8, ncol=2)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart_tell_trend.png"), dpi=130); plt.close()

# ---------- CHART 8: scale and coverage (on-topic posts per sub) ----------
sub = collections.Counter(p.get("subreddit", "") for p in posts)
items = sub.most_common(30)[::-1]
fig, ax = plt.subplots(figsize=(10, 11))
ax.barh([s for s, _ in items], [c for _, c in items], color=PURPLE)
for i, (s, c) in enumerate(items):
    ax.text(c, i, f" {c:,}", va="center", fontsize=7)
ax.set_xlabel("On-topic posts pulled from the subreddit, 2020-2026")
ax.set_title(f"Scale and coverage: {len(posts):,} on-topic posts across {len(sub)} subreddits\n(top 30 shown)")
ax.margins(x=0.13); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_scanned_by_sub.png"), dpi=130); plt.close()

# ---------- CHART 9: raw mention counts per tell (numerators) ----------
rc = sorted([r for r in spec if int(r["comment_mentions"]) + int(r["post_mentions"]) > 0],
            key=lambda r: int(r["comment_mentions"]) + int(r["post_mentions"]))
y = np.arange(len(rc)); h = 0.4
cm = [int(r["comment_mentions"]) for r in rc]; pm = [int(r["post_mentions"]) for r in rc]
fig, ax = plt.subplots(figsize=(11, 8.5))
ax.barh(y + h/2, cm, h, label="comment mentions", color=PURPLE)
ax.barh(y - h/2, pm, h, label="post mentions", color=GREY)
ax.set_yticks(y); ax.set_yticklabels([short(r["tell"], 46) for r in rc])
ax.set_xlabel("Number of items naming the tell (the numerators behind the percentages)")
ax.set_title("Raw mention counts per tell")
for i, r in enumerate(rc):
    tot = int(r["comment_mentions"]) + int(r["post_mentions"])
    ax.text(max(cm[i], pm[i]) + 0.4, i, f" {tot}", va="center", fontsize=7)
ax.legend(loc="lower right"); ax.margins(x=0.08); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_raw_counts_by_tell.png"), dpi=130); plt.close()

# ---------- CHART 10: the funnel ----------
stages = [("Posts pulled", 11906), ("On-topic posts", 11216),
          ("Candidates\nclassified", 2136 + 1500), ("Name a specific\ntell", 258 + 146)]
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar([s for s, _ in stages], [val for _, val in stages], color=[GREY, GREY, PURPLE, BLUE])
ax.set_yscale("log"); ax.set_ylabel("items (log scale)")
ax.set_title("How the pull narrows to the classified, tell-naming signal")
for b, (_, val) in zip(bars, stages):
    ax.text(b.get_x() + b.get_width()/2, val, f"{val:,}", ha="center", va="bottom", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart_funnel.png"), dpi=130); plt.close()

# ---------- CHART 11: top on-topic posts by upvotes ----------
def score(p):
    try: return int(p.get("score") or 0)
    except Exception: return 0
top = sorted(posts, key=score)[-12:]
import re as _re
fig, ax = plt.subplots(figsize=(11, 7))
ax.barh([f"r/{p.get('subreddit')}: {_re.sub(chr(92)+'s+',' ', p.get('title') or '')[:42]}" for p in top],
        [score(p) for p in top], color=PURPLE)
for i, p in enumerate(top):
    ax.text(score(p), i, f" {score(p):,}", va="center", fontsize=7)
ax.set_xlabel("Post upvotes")
ax.set_title("Top on-topic posts behind the signal")
ax.margins(x=0.13); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_top_threads.png"), dpi=130); plt.close()

# ---------- CHART 12: Lens 2, code-context idiom airtime ----------
l2 = []
with open(os.path.join(HERE, "lens2_idioms.csv")) as f:
    for r in csv.DictReader(f):
        l2.append((r["idiom"], int(r["code_context_posts"]), int(r["n_subreddits"])))
l2 = sorted(l2, key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.barh([t[0] for t in l2], [t[1] for t in l2], color=PURPLE)
for i, t in enumerate(l2):
    ax.text(t[1], i, f" {t[1]:,} ({t[2]} subs)", va="center", fontsize=8)
ax.set_xlabel("Posts where the idiom appears in a code context")
ax.set_title("Lens 2: code-context airtime by idiom\n(directly-queried phrases; label shows breadth across subreddits)")
ax.margins(x=0.18); plt.tight_layout()
plt.savefig(os.path.join(HERE, "chart_lens2_terms.png"), dpi=130); plt.close()

print("wrote 12 charts:",
      "verified_ranking, tells_ranked, raw_vs_verified, post_vs_comment, by_category,",
      "growth_byyear, tell_trend, scanned_by_sub, raw_counts_by_tell, funnel, top_threads, lens2_terms")
