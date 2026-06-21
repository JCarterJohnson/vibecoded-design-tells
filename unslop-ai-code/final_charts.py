#!/usr/bin/env python3
"""Final charts for the post, from the VERIFIED ranking (final_tell_counts.csv)
plus an honest raw on-topic-posts-by-year growth chart."""
import os, csv, json, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
INK="#1f2937"; ACC="#b45309"; ACC2="#0f766e"; GRID="#e5e7eb"; GREY="#94a3b8"

def style(ax):
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK, labelsize=9); ax.grid(axis="x",color=GRID,lw=.8); ax.set_axisbelow(True)

def short(s,n=58): return s if len(s)<=n else s[:n-1]+"…"

rows=list(csv.DictReader(open(os.path.join(HERE,"final_tell_counts.csv"))))
spec=[r for r in rows if r["code"]!="umbrella_looks_ai" and r["verdict"]!="artifact"
      and float(r["verified_share_pct"] or 0)>0]
spec=spec[:12][::-1]
labels=[short(r["tell"],60) for r in spec]
vals=[float(r["verified_share_pct"]) for r in spec]
raw=[float(r["raw_share_pct"]) for r in spec]
fig,ax=plt.subplots(figsize=(12,max(5,0.55*len(spec)+1)))
y=range(len(spec))
ax.barh([i+0.2 for i in y], vals, height=0.4, color=ACC, label="verified share")
ax.barh([i-0.2 for i in y], raw, height=0.4, color=GREY, label="raw (before precision check)")
ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=8.5)
for i,v in enumerate(vals): ax.text(v+0.15,i+0.2,"%.1f%%"%v,va="center",fontsize=8,color=INK)
style(ax); ax.legend(loc="lower right",fontsize=9,frameon=False)
ax.set_title("Tells that code was written by AI — verified share of tell-naming comments",
    color=INK,fontsize=13,fontweight="bold",loc="left",pad=12)
ax.set_xlabel("share of comments that name a specific tell (%)",color=INK,fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(HERE,"chart_verified_ranking.png"),dpi=135); plt.close()
print("wrote chart_verified_ranking.png")

# by-category (verified shares rolled up)
CAT={"over_comment":"comments/docs","redundant_docstring":"comments/docs","placeholder_comment":"comments/docs",
 "verbose_naming":"naming","generic_naming":"naming","excessive_try":"error handling","over_validation":"error handling",
 "over_engineered":"structure","boilerplate_tutorial":"structure","reinvent_wheel":"structure",
 "too_clean":"style/format","style_mismatch":"style/format","type_everywhere":"style/format",
 "emoji":"output","excess_logging":"output","chat_artifact":"artifacts",
 "hallucinated_api":"correctness","inconsistent_skill":"correctness"}
agg=collections.defaultdict(float)
for r in rows:
    if r["code"]=="umbrella_looks_ai" or r["verdict"]=="artifact": continue
    agg[CAT.get(r["code"],"other")]+=float(r["verified_share_pct"] or 0)
items=sorted(agg.items(),key=lambda kv:kv[1])
fig,ax=plt.subplots(figsize=(9,4.8))
ax.barh([k for k,_ in items],[v for _,v in items],color=ACC2,height=.66)
for i,(k,v) in enumerate(items): ax.text(v+0.3,i,"%.0f%%"%v,va="center",fontsize=9,color=INK)
style(ax); ax.set_title("AI-code tells by category (summed verified share)",
    color=INK,fontsize=13,fontweight="bold",loc="left",pad=12)
plt.tight_layout(); plt.savefig(os.path.join(HERE,"chart_by_category.png"),dpi=135); plt.close()
print("wrote chart_by_category.png")

# comment vs post mentions (verified-eligible, by raw mention counts)
cv=[r for r in rows if r["code"]!="umbrella_looks_ai" and int(r["comment_mentions"])>0][:12][::-1]
labels=[short(r["tell"],46) for r in cv]
cm=[int(r["comment_mentions"]) for r in cv]; pm=[int(r["post_mentions"]) for r in cv]
yy=range(len(cv))
fig,ax=plt.subplots(figsize=(11,max(4,0.5*len(cv)+1)))
ax.barh([i+0.2 for i in yy],cm,height=.4,color=ACC,label="comment mentions")
ax.barh([i-0.2 for i in yy],pm,height=.4,color=GREY,label="post mentions")
ax.set_yticks(list(yy)); ax.set_yticklabels(labels,fontsize=8.5)
style(ax); ax.legend(loc="lower right",fontsize=9,frameon=False)
ax.set_title("Each tell: comment vs post mentions",color=INK,fontsize=13,fontweight="bold",loc="left",pad=12)
plt.tight_layout(); plt.savefig(os.path.join(HERE,"chart_post_vs_comment.png"),dpi=135); plt.close()
print("wrote chart_post_vs_comment.png")

# growth: raw on-topic posts by year (honest; caveat in caption)
posts=[json.loads(l) for l in open(os.path.join(HERE,"corpus.jsonl"))]
yr=collections.Counter()
for p in posts:
    try: yr[datetime.datetime.fromtimestamp(int(p["created_utc"]),datetime.UTC).year]+=1
    except Exception: pass
years=[y for y in range(2020,2027) if y in yr]
vals=[yr[y] for y in years]
fig,ax=plt.subplots(figsize=(9,4.6))
ax.bar([str(y) for y in years], vals, color=ACC2, width=0.62)
for i,v in enumerate(vals): ax.text(i,v+max(vals)*0.01,str(v),ha="center",fontsize=9,color=INK)
style(ax); ax.grid(axis="y",color=GRID,lw=.8); ax.grid(axis="x",visible=False)
ax.set_title("On-topic posts about spotting AI-written code, by year (raw count)",
    color=INK,fontsize=12.5,fontweight="bold",loc="left",pad=12)
ax.set_ylabel("on-topic posts", color=INK, fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(HERE,"chart_growth_byyear.png"),dpi=135); plt.close()
print("wrote chart_growth_byyear.png")
