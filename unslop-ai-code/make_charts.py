#!/usr/bin/env python3
"""
make_charts.py - Render the charts for the write-up from the CSVs produced by
analyze.py / analyze_comments.py. Matplotlib only; no seaborn, no styles that
require network. Each chart is saved as a PNG in this folder.

Charts:
  chart_tells_comment.png   ranked tells, comment-level (the headline ranking)
  chart_tells_post.png      ranked tells, post-level (corroboration)
  chart_by_category.png     tells rolled up into categories
  chart_growth.png          share of posts about AI-code by year (per 10k posts)
  chart_scale_by_sub.png    scanned posts per subreddit (coverage)
  chart_post_vs_comment.png each tell: post share vs comment share
"""
import os, csv, collections

HERE = os.path.dirname(os.path.abspath(__file__))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#1f2937"; ACCENT = "#b45309"; ACCENT2 = "#0f766e"; GRID = "#e5e7eb"

def load_csv(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p): return None
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

def style(ax):
    ax.set_facecolor("white")
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)

def short(label, n=52):
    return label if len(label) <= n else label[:n-1] + "…"

def barh_ranked(rows, val_key, title, fname, color=ACCENT, top=18):
    if not rows: return
    rows = [r for r in rows if float(r.get(val_key,0) or 0) > 0][:top]
    if not rows: return
    rows = rows[::-1]
    labels = [short(r["tell"]) for r in rows]
    vals = [float(r[val_key]) for r in rows]
    fig, ax = plt.subplots(figsize=(11, max(4, 0.42*len(rows)+1)))
    ax.barh(range(len(rows)), vals, color=color, height=0.72)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(labels, fontsize=8.5)
    for i,v in enumerate(vals):
        ax.text(v+max(vals)*0.01, i, "%.1f%%"%v, va="center", fontsize=8, color=INK)
    style(ax); ax.set_title(title, color=INK, fontsize=13, fontweight="bold", loc="left", pad=12)
    ax.set_xlabel("share of on-topic items (%)", color=INK, fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(HERE,fname), dpi=130); plt.close()
    print("wrote", fname)

def chart_by_category(rows, fname="chart_by_category.png"):
    if not rows: return
    agg = collections.defaultdict(float)
    for r in rows:
        agg[r["category"]] += float(r.get("share_pct_of_comments", r.get("share_pct_of_ontopic",0)) or 0)
    items = sorted(agg.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(9,4.6))
    ax.barh([k for k,_ in items], [v for _,v in items], color=ACCENT2, height=0.66)
    for i,(k,v) in enumerate(items):
        ax.text(v+0.3, i, "%.0f%%"%v, va="center", fontsize=9, color=INK)
    style(ax); ax.set_title("AI-code tells rolled up by category (summed share)",
        color=INK, fontsize=13, fontweight="bold", loc="left", pad=12)
    plt.tight_layout(); plt.savefig(os.path.join(HERE,fname), dpi=130); plt.close()
    print("wrote", fname)

def chart_growth(fname="chart_growth.png"):
    rows = load_csv("totals_by_year.csv")
    if not rows: return
    tot = collections.defaultdict(int); matched = collections.defaultdict(int)
    for r in rows:
        try: yr = int(r["year"]); c = int(r["posts"])
        except Exception: continue
        if r["query"] == "_ALL_": tot[yr] += c
        else: matched[yr] += c
    years = sorted(y for y in tot if 2020 <= y <= 2026)
    if not years: return
    per10k = [ (matched[y]/tot[y]*10000) if tot[y] else 0 for y in years ]
    fig, ax = plt.subplots(figsize=(9,4.6))
    ax.plot(years, per10k, marker="o", color=ACCENT, linewidth=2.4)
    for x,y in zip(years, per10k):
        ax.text(x, y+max(per10k)*0.03, "%.0f"%y, ha="center", fontsize=9, color=INK)
    style(ax); ax.set_title("Talk about AI-written code, per 10,000 posts per year",
        color=INK, fontsize=13, fontweight="bold", loc="left", pad=12)
    ax.set_ylabel("matched posts per 10k", color=INK, fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(HERE,fname), dpi=130); plt.close()
    print("wrote", fname)

def chart_scale(fname="chart_scale_by_sub.png"):
    rows = load_csv("totals_by_year.csv")
    if not rows: return
    tot = collections.defaultdict(int)
    for r in rows:
        if r["query"] == "_ALL_":
            try: tot[r["subreddit"]] += int(r["posts"])
            except Exception: pass
    items = sorted(tot.items(), key=lambda kv: kv[1])[-26:]
    if not items: return
    fig, ax = plt.subplots(figsize=(10, max(4,0.34*len(items)+1)))
    ax.barh([k for k,_ in items], [v for _,v in items], color="#475569", height=0.7)
    style(ax); ax.set_title("Scanned posts per subreddit (2020-2026, where countable)",
        color=INK, fontsize=12.5, fontweight="bold", loc="left", pad=12)
    ax.set_xlabel("total posts", color=INK, fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(HERE,fname), dpi=130); plt.close()
    print("wrote", fname)

def chart_post_vs_comment(fname="chart_post_vs_comment.png"):
    cpost = load_csv("tell_counts.csv"); ccom = load_csv("comment_tell_counts.csv")
    if not cpost or not ccom: return
    pshare = {r["tell"]: float(r["share_pct_of_ontopic"]) for r in cpost}
    crows = [r for r in ccom if float(r["share_pct_of_comments"])>0][:14][::-1]
    if not crows: return
    labels = [short(r["tell"],46) for r in crows]
    cv = [float(r["share_pct_of_comments"]) for r in crows]
    pv = [pshare.get(r["tell"],0) for r in crows]
    y = range(len(crows))
    fig, ax = plt.subplots(figsize=(11, max(4,0.5*len(crows)+1)))
    ax.barh([i+0.2 for i in y], cv, height=0.4, color=ACCENT, label="comment share")
    ax.barh([i-0.2 for i in y], pv, height=0.4, color="#94a3b8", label="post share")
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=8.5)
    style(ax); ax.legend(loc="lower right", fontsize=9, frameon=False)
    ax.set_title("Each tell: comment-level vs post-level share",
        color=INK, fontsize=13, fontweight="bold", loc="left", pad=12)
    plt.tight_layout(); plt.savefig(os.path.join(HERE,fname), dpi=130); plt.close()
    print("wrote", fname)

def main():
    com = load_csv("comment_tell_counts.csv")
    post = load_csv("tell_counts.csv")
    if com:
        barh_ranked(com, "share_pct_of_comments",
            "What gives away AI-written code (comment-level, on-topic threads)",
            "chart_tells_comment.png", color=ACCENT)
        chart_by_category(com)
    if post:
        barh_ranked(post, "share_pct_of_ontopic",
            "What gives away AI-written code (post-level corroboration)",
            "chart_tells_post.png", color=ACCENT2)
        if not com: chart_by_category(post)
    chart_growth(); chart_scale(); chart_post_vs_comment()
    print("charts done.")

if __name__ == "__main__":
    main()
