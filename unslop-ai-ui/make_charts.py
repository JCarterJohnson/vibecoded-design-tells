#!/usr/bin/env python3
"""Final deliverable charts: honest comment-level ranking + post-vs-comment comparison."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
PURPLE, GREY = "#7c5cff", "#b9b3d6"

def clean(name):  # strip emoji glyphs that render as tofu
    return (name.replace("✨", "").replace("🚀", "").replace(" /  sparkles /  in copy", " / sparkles in copy")
                .replace("Emoji /  sparkles /  in copy", "Emoji / sparkles in copy")).strip()

def load(path, share_col):
    rows = []
    with open(os.path.join(OUT, path)) as f:
        for r in csv.DictReader(f):
            rows.append((r["tell"], float(r[share_col])))
    return rows

com = load("comment_tell_counts.csv", "share_of_comments_pct")
post = dict((t, s) for t, s in load("tell_counts.csv", "share_of_designctx_pct"))

# 1) honest ranked chart (comment-level, on-topic comments)
com_sorted = sorted(com, key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(11, 7.5))
labels = [clean(t) for t, _ in com_sorted]; vals = [s for _, s in com_sorted]
bars = ax.barh(labels, vals, color=PURPLE)
ax.set_xlabel("Share of on-topic comments naming the tell (%)")
ax.set_title("What people actually name as vibe-coded site 'tells'\n(3,033 comments from 125 on-topic threads; cleanest signal)")
for b, v in zip(bars, vals):
    ax.text(v + 0.08, b.get_y() + b.get_height()/2, f"{v:.1f}%", va="center", fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_tells_comment.png"), dpi=130); plt.close()

# 2) post vs comment comparison (shows the emoji / feature-card correction)
specific = [t for t, _ in com if not t.startswith("'")]  # drop the two meta-tells
specific = sorted(specific, key=lambda t: -dict(com)[t])[:10]
import numpy as np
y = np.arange(len(specific)); h = 0.4
cvals = [dict(com)[t] for t in specific]; pvals = [post.get(t, 0) for t in specific]
fig, ax = plt.subplots(figsize=(11, 7))
ax.barh(y + h/2, cvals, h, label="on-topic comments", color=PURPLE)
ax.barh(y - h/2, pvals, h, label="all design-context posts", color=GREY)
ax.set_yticks(y); ax.set_yticklabels([clean(t) for t in specific])
ax.invert_yaxis(); ax.set_xlabel("Share mentioning the tell (%)")
ax.set_title("Specific tells: comment vs post signal\n(emoji & 3-column cards look inflated at post level; comments are the honest read)")
ax.legend(); plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_post_vs_comment.png"), dpi=130); plt.close()
print("wrote chart_tells_comment.png, chart_post_vs_comment.png")
