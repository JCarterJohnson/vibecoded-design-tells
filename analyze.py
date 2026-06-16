#!/usr/bin/env python3
"""
Tabulate the design "tells" of vibe-coded sites from the harvested on-topic corpus.

Breakdown dimension = frequency of each visual tell among on-topic items, with the
share computed over a DESIGN-CONTEXT subset (items whose text carries appearance
vocabulary) so we measure people talking about how these sites *look*, not their
security or billing. Also rolls up growth-normalized share-of-posts by year.

Reads: corpus.jsonl, totals_by_year.csv, matched_by_year.csv
Writes: tell_counts.csv, tell_examples.md, growth_by_year.csv, summary.txt
"""
import json, csv, os, re, html
from collections import defaultdict, Counter

OUT = os.path.dirname(os.path.abspath(__file__))

# --- appearance vocabulary: an item is "design-context" if it mentions any ---
DESIGN_CTX = re.compile(
    r"\b(design|designer|ui|ux|interface|layout|landing\s*page|website|web\s*site|"
    r"webpage|web\s*page|homepage|front[\s-]?end|css|tailwind|theme|style|styling|"
    r"font|typography|colou?r|palette|aesthetic|visual|looks?|look\s*like|looked|"
    r"branding|template|hero|gradient|button)\b", re.I)

# --- negative aesthetic sentiment ---
NEG = re.compile(
    r"\b(ugly|terrible|awful|hideous|cringe|tacky|cheap|generic|bland|boring|soulless|"
    r"sterile|samey|cookie[\s-]?cutter|lazy|slop|garbage|trash|disgusting|amateur|"
    r"hate|sick of|tired of|over\s*used|overdone|avoid|red\s*flag|screams?\s+ai|"
    r"reeks?\s+of\s+ai|obvious(ly)?\s+ai|low[\s-]?effort)\b", re.I)

# --- the tells: name -> list of regex patterns (case-insensitive) ---
TELLS = {
    "Purple / violet (the 'AI purple')": [r"\bpurple", r"\bviolet", r"\bindigo\b", r"\blavender\b", r"blurple"],
    "Gradients everywhere / gradient text": [r"gradient"],
    "Dark mode + neon glow": [r"\bdark\s*mode\b", r"\bdark\s*theme\b", r"\bneon\b", r"\bglow(ing)?\b"],
    "Glassmorphism / frosted glass": [r"glassmorph", r"frosted\s*glass", r"glass[\s-]?effect", r"\bglassy\b", r"backdrop[\s-]?blur", r"glass\s*card"],
    "Bento grid": [r"\bbento\b"],
    "Generic sans font (Inter / Geist)": [r"\binter\s*font\b", r"\bgeist\b", r"helvetica", r"\b(default|generic|same|system)\s*font\b", r"\binter\b(?!\w)"],
    "Emoji / ✨ sparkles / 🚀 in copy": [r"\bemoji", r"✨", r"🚀", r"\bsparkles?\b", r"rocket\s*emoji"],
    "Same hero: huge headline + 2 buttons": [r"\bhero\s*section\b", r"\bhero\s*(image|banner|copy)\b", r"big\s*(headline|heading|title)", r"huge\s*(headline|heading|title|text)"],
    "shadcn / Tailwind default kit": [r"shadcn", r"\btailwind\b", r"\bradix\b", r"\bui\s*kit\b"],
    "Rounded corners / pill buttons": [r"rounded\s*corner", r"border[\s-]?radius", r"\brounded\b", r"pill[\s-]?(button|shaped)"],
    "Three-column feature cards": [r"feature\s*cards?", r"(three|3)[\s-]?column", r"card\s*layout", r"grid\s*of\s*cards", r"\bcards\b"],
    "Mesh / blob / aurora backgrounds": [r"\bblobs?\b", r"\bmesh\s*gradient\b", r"\baurora\b", r"floating\s*(shapes|orbs)", r"\borbs?\b"],
    "'All looks the same' / template / cookie-cutter": [r"look(s|ed)?\s+(the\s+)?same", r"look(s|ed)?\s+identical", r"same\s*template", r"cookie[\s-]?cutter", r"\bsamey\b", r"same\s*vibe", r"all\s+(the\s+)?same", r"\bgeneric\b", r"indistinguishable"],
    "'Screams AI' / soulless / slop": [r"screams?\s+ai", r"reeks?\s+of\s+ai", r"obvious(ly)?\s+ai", r"\bai\s*slop\b", r"soulless", r"\bsterile\b", r"made\s+by\s+ai", r"ai[\s-]?generated", r"looks?\s+(like\s+)?ai", r"chatgpt\s+(made|wrote|designed|built)"],
    "Too many animations / Framer fade-ins": [r"\banimations?\b", r"framer\s*motion", r"fade[\s-]?in", r"parallax", r"scroll\s*animation"],
    "Stock illustrations / clipart": [r"\billustrations?\b", r"undraw", r"clip\s*art", r"stock\s*(image|photo|illustration|art)"],
    "Centered everything / endless whitespace": [r"\bcentered\b", r"too\s*much\s*(white\s*space|whitespace|spacing|padding)", r"\bwhite\s*space\b"],
}
COMPILED = {name: [re.compile(p, re.I) for p in pats] for name, pats in TELLS.items()}

def load_corpus():
    items, seen = [], set()
    p = os.path.join(OUT, "corpus.jsonl")
    if not os.path.exists(p): return items
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
                iid = d.get("id")
                if iid in seen: continue          # dedupe across any re-runs/appends
                seen.add(iid)
                d["_text"] = html.unescape((d.get("title") or "") + "\n" + (d.get("selftext") or ""))
                items.append(d)
            except: pass
    return items

def matches(text, name):
    return any(rx.search(text) for rx in COMPILED[name])

def main():
    items = load_corpus()
    n = len(items)
    if n == 0:
        print("corpus empty"); return
    ctx = [it for it in items if DESIGN_CTX.search(it["_text"])]
    nc = len(ctx)
    neg = [it for it in ctx if NEG.search(it["_text"])]

    # per-tell counts over design-context subset
    rows = []
    for name in TELLS:
        hit = [it for it in ctx if matches(it["_text"], name)]
        hit_neg = [it for it in hit if NEG.search(it["_text"])]
        rows.append((name, len(hit), len(hit) / nc * 100 if nc else 0,
                     len(hit_neg), len(hit_neg) / len(hit) * 100 if hit else 0))
    rows.sort(key=lambda r: -r[1])

    with open(os.path.join(OUT, "tell_counts.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tell", "items_mentioning", "share_of_designctx_pct", "neg_sentiment_items", "neg_share_of_tell_pct"])
        for r in rows:
            w.writerow([r[0], r[1], f"{r[2]:.1f}", r[3], f"{r[4]:.1f}"])

    # examples: top by score per tell, within design-context
    with open(os.path.join(OUT, "tell_examples.md"), "w") as f:
        f.write(f"# Tell examples (design-context corpus: {nc} of {n} on-topic items)\n\n")
        for name, cnt, share, *_ in rows:
            hit = [it for it in ctx if matches(it["_text"], name)]
            hit.sort(key=lambda x: -(x.get("score") or 0))
            f.write(f"## {name} — {cnt} items ({share:.1f}%)\n\n")
            for it in hit[:6]:
                t = " ".join((it.get("title") or "").split())
                body = " ".join((it.get("selftext") or "").split())
                snip = (body[:280] + "…") if len(body) > 280 else body
                f.write(f"- **[{it.get('score')}↑ r/{it.get('subreddit')}]** {t}\n")
                if snip: f.write(f"  > {snip}\n")
                f.write(f"  https://reddit.com{it.get('permalink','')}\n\n")

    # --- topic growth, growth-normalized (accurate uncapped Phase-2 aggregate) ---
    # numerator = "vibe coding" matched posts/yr (clean single signal, no dedup/double-count);
    # corpus is capped at 400/combo so it understates recent years -> use aggregate instead.
    totals = defaultdict(int)
    with open(os.path.join(OUT, "totals_by_year.csv")) as f:
        for r in csv.DictReader(f):
            totals[r["year"]] += int(r["total_posts"])
    matched = defaultdict(int)
    mbq = os.path.join(OUT, "matched_by_year.csv")
    if os.path.exists(mbq):
        with open(mbq) as f:
            for r in csv.DictReader(f):
                if r["query"] == "vibe coding":
                    matched[r["year"]] += int(r["matched"])
    years = [y for y in sorted(totals) if y.isdigit() and 2020 <= int(y) <= 2026]
    with open(os.path.join(OUT, "growth_by_year.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["year", "vibecoding_posts", "total_posts_all_subs", "per_10k_posts"])
        for yr in years:
            m = matched.get(yr, 0); t = totals[yr]
            w.writerow([yr, m, t, f"{(m/t*10000):.2f}" if t else ""])

    # --- per-year share of design-context corpus mentioning each top tell ---
    import time as _t
    def yr_of(it):
        ts = it.get("created_utc")
        return _t.strftime("%Y", _t.gmtime(int(ts))) if ts is not None else None
    ctx_by_year = defaultdict(list)
    for it in ctx:
        y = yr_of(it)
        if y: ctx_by_year[y].append(it)
    top_for_trend = [r[0] for r in rows[:6]]
    with open(os.path.join(OUT, "tell_share_by_year.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["tell"] + years)
        for name in top_for_trend:
            row = [name]
            for yr in years:
                grp = ctx_by_year.get(yr, [])
                share = (sum(1 for it in grp if matches(it["_text"], name)) / len(grp) * 100) if grp else 0
                row.append(f"{share:.1f}")
            w.writerow(row)

    # --- charts (graphs deliverable) ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # 1) ranked tells bar chart
        top = rows[:14][::-1]
        fig, ax = plt.subplots(figsize=(11, 7))
        labels = [r[0] for r in top]; vals = [r[2] for r in top]
        bars = ax.barh(labels, vals, color="#7c5cff")
        ax.set_xlabel("Share of on-topic (design-context) posts mentioning the tell (%)")
        ax.set_title(f"Vibe-coded site design 'tells' people complain about\n(n={nc:,} design-context posts across {len(set(it.get('subreddit') for it in items))} subreddits, 2020-2026)")
        for b, v in zip(bars, vals):
            ax.text(v + 0.3, b.get_y() + b.get_height()/2, f"{v:.1f}%", va="center", fontsize=8)
        plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_tells_ranked.png"), dpi=130); plt.close()
        # 2) topic growth
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(years, [matched.get(y, 0)/totals[y]*10000 if totals[y] else 0 for y in years], color="#7c5cff")
        ax.set_ylabel("'vibe coding' posts per 10,000 posts")
        ax.set_title("The vibe-coding conversation barely existed before 2024\n(growth-normalized: share of all posts, not raw counts)")
        plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_growth.png"), dpi=130); plt.close()
        # 3) tell trend by year (top 5)
        fig, ax = plt.subplots(figsize=(9, 5.5))
        for name in top_for_trend[:5]:
            ys = [(sum(1 for it in ctx_by_year.get(yr, []) if matches(it["_text"], name)) / len(ctx_by_year[yr]) * 100) if ctx_by_year.get(yr) else 0 for yr in years]
            ax.plot(years, ys, marker="o", label=(name[:28]))
        ax.set_ylabel("% of that year's design-context posts"); ax.set_title("Top tells, share by year")
        ax.legend(fontsize=7, loc="upper left"); plt.tight_layout()
        plt.savefig(os.path.join(OUT, "chart_tell_trend.png"), dpi=130); plt.close()
        charted = True
    except Exception as e:
        charted = f"chart error: {e}"

    # --- summary ---
    with open(os.path.join(OUT, "summary.txt"), "w") as f:
        def p(*a): print(*a); f.write(" ".join(str(x) for x in a) + "\n")
        p(f"On-topic items harvested (unique): {n}")
        p(f"Design-context subset: {nc} ({nc/n*100:.1f}% of corpus)")
        p(f"  ...of those, negative-aesthetic sentiment: {len(neg)} ({len(neg)/nc*100:.1f}%)")
        bysub = Counter(it.get("subreddit") for it in items)
        p(f"Subreddits represented: {len(bysub)}")
        p(f"Top subs by on-topic volume: " + ", ".join(f"{s}:{c}" for s, c in bysub.most_common(15)))
        p("\nTOP TELLS (share of design-context items, with negative-sentiment co-occurrence):")
        for name, cnt, share, negc, negsh in rows:
            p(f"  {share:5.1f}%  n={cnt:5d}  {name}   (neg {negsh:.0f}%)")
        p("\nTopic growth (vibe-coding posts per 10k posts/yr, all subs):")
        for yr in years:
            m = matched.get(yr, 0); t = totals[yr]
            p(f"  {yr}: {m:6d} / {t:8d} = {(m/t*10000):.2f} per 10k" if t else f"  {yr}: n/a")
        p(f"\ncharts: {charted}")

if __name__ == "__main__":
    main()
