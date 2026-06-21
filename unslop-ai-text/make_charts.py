#!/usr/bin/env python3
"""Final deliverable charts: the human-verified (cited) ranking + the regex-vs-cited
comparison. Mirrors the UI study's make_charts.py: the cleanest signal first, then the
chart that shows where the keyword pass over- and under-counts."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
PURPLE, BLUE, GREY = "#7c5cff", "#3b82f6", "#b9b3d6"

def short(name):
    """Compress the long verified-tally / lexicon labels to plottable ones."""
    m = {
        'Em dash overuse (—)': "Em dash (—)",
        'em dash ("—") as a tell': "Em dash (—)",
        '"It\'s not just X, it\'s Y" / "not X, but Y" construction (merged with #20, #23 variants)':
            '"not just X, it\'s Y"',
        '"it\'s not just X, it\'s Y"': '"not just X, it\'s Y"',
        'Uniform / robotic sentence rhythm': "Uniform sentence rhythm",
        "Positivity / sycophancy (gushing, 'great question!', yes-man)": "Sycophancy / 'great question'",
        'Perfectly-structured / formulaic essay shape': "Formulaic essay shape",
        'perfectly structured / formulaic': "Formulaic essay shape",
        'Everything turned into bullet lists / listicles': "Bullet lists / listicles",
        'everything in bullet points / lists': "Bullet lists / listicles",
        '"Dive in" / "deep dive"': '"dive in" / "deep dive"',
        '"dive in" / "deep dive" / "let\'s dive"': '"dive in" / "deep dive"',
        'Rule of three / triads': "Rule of three / triads",
        '"rule of three" / triads': "Rule of three / triads",
        "Empty summary / polished-but-hollow phrasing ('says nothing', word salad)": "Empty / hollow phrasing",
        'Bolded lead-in bullets (**Word:** ...) / title-case mini-headings (merged #24, #30)': "Bolded lead-in bullets",
        'bolded lead-in bullets (**Word:**)': "Bolded lead-in bullets",
        '"As an AI language model" / leftover assistant boilerplate (e.g. \'Want me to tweak the tone?\')':
            '"as an AI language model"',
        '"as an AI language model"': '"as an AI language model"',
        'Single-word diction memes: delve, unleash, tapestry, game-changer, comprehensive, elevate (cluster)':
            "Diction memes (delve, etc.)",
        'Hallucinated / fabricated citations and references': "Hallucinated citations",
        '"Honestly, ..." / fake-relatability openers (\'Look, I get it\', \'Imagine this\')':
            '"Honestly," openers',
        '"Unlock the power/potential" / "unlock" (merged #14, #19)': '"unlock the potential"',
        '"unlock/unleash the power/potential"': '"unlock the potential"',
        "Marketing / hype language ('revolutionary', 'transform your life', 'transformative')":
            "Marketing / hype language",
        'Verbosity / repetition / restating the same point across sections': "Verbosity / repetition",
        'Forced / overly-smooth transitions': "Forced transitions",
        'No contractions / overly formal register (merged #17, #21)': "No contractions / formal",
        "Hedging / both-sides balance ('it depends', 'on one hand... on the other')": "Hedging / both-sides",
        '"In today\'s fast-paced world" / dated scene-setting opener': '"in today\'s fast-paced world"',
        'Emoji as bullets or section headers': "Emoji bullets / headers",
        'emoji bullets / emoji headers': "Emoji bullets / headers",
        'Horizontal-rule dividers (---) between sections': "Horizontal-rule dividers",
        'Deliberately-inserted fake typos to beat detectors': "Fake typos (anti-detector)",
        '"In conclusion" / "in summary" closers': '"in conclusion" / "in summary"',
        '"in conclusion" / "in summary"': '"in conclusion" / "in summary"',
        'headers / bold everywhere / markdown': "Headers / bold everywhere",
        'delve': "delve", 'game-changer': "game-changer", 'unleash': "unleash",
        'tapestry': "tapestry", 'leverage': "leverage", 'comprehensive': "comprehensive",
        'nuanced / nuance': "nuanced / nuance", 'navigate / navigating': "navigate / navigating",
        'utilize (instead of "use")': "utilize", 'when it comes to': '"when it comes to"',
        '"when it comes to"': '"when it comes to"',
        'overuse of "however," / "thus," / "hence"': '"however / thus / hence"',
        '"in today\'s fast-paced/digital world"': '"in today\'s fast-paced world"',
        '"great question!"': '"great question!"',
    }
    if name in m:
        return m[name]
    return (name[:34] + "...") if len(name) > 37 else name

def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

# ---------- load the human-verified ranking ----------
verified = []
with open(os.path.join(OUT, "verified_tally.csv")) as f:
    for r in csv.DictReader(f):
        cite = fnum(r["cite_share_sample_pct"])
        if cite is None:
            continue
        verified.append({
            "tell": r["tell"], "cat": r["category"], "conf": r["confidence"],
            "cite": cite,
            "regex_full": fnum(r["regex_share_fullcorpus_pct"]),
            "blind": r["vs_regex"].startswith("REGEX-BLIND"),
        })

# ---------- CHART 1: the verified, cited ranking (cleanest signal) ----------
# Analog of the UI study's chart_tells_comment: the share humans actually CITE the tell,
# from the 600-post audited sample, not what a keyword pass merely matches.
rows = sorted(verified, key=lambda d: d["cite"])
labels = [short(d["tell"]) for d in rows]
vals = [d["cite"] for d in rows]
colors = [GREY if d["blind"] else PURPLE for d in rows]
fig, ax = plt.subplots(figsize=(11, 8.5))
bars = ax.barh(labels, vals, color=colors)
ax.set_xlabel("Share of audited on-topic posts that CITE the tell (%)")
ax.set_title("What people actually cite as AI-writing tells\n"
             "(verified citations, 600-post audited sample; cleanest signal. "
             "Grey = structural, no keyword catches it)")
for b, v in zip(bars, vals):
    ax.text(v + 0.05, b.get_y() + b.get_height()/2, f"{v:.1f}%", va="center", fontsize=8)
ax.margins(x=0.12)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_tells_cited.png"), dpi=130); plt.close()

# ---------- CHART 2: keyword match (full corpus) vs cited (audited sample) ----------
# Analog of the UI study's chart_post_vs_comment: two signals side by side, to show where
# the cheap keyword pass inflates a tell (its own prose) or misses a cited one. Sourced
# from comparison.csv so the worst over-counters (however/thus, nuanced) are visible.
comp = []
with open(os.path.join(OUT, "comparison.csv")) as f:
    for r in csv.DictReader(f):
        cite = fnum(r["cite_share_sample_pct"]); regf = fnum(r["regex_share_fullcorpus_pct"])
        if cite is None or regf is None:
            continue
        comp.append({"tell": r["tell"], "cite": cite, "regf": regf})
top_cite = sorted(comp, key=lambda d: -d["cite"])[:9]
top_over = sorted(comp, key=lambda d: -(d["regf"] - d["cite"]))[:5]
sel, seen = [], set()
for d in top_cite + top_over:
    if d["tell"] not in seen:
        seen.add(d["tell"]); sel.append(d)
sel = sorted(sel, key=lambda d: d["cite"])
y = np.arange(len(sel)); h = 0.4
cvals = [d["cite"] for d in sel]; rvals = [d["regf"] for d in sel]
fig, ax = plt.subplots(figsize=(11, 7.5))
ax.barh(y + h/2, cvals, h, label="cited (audited sample)", color=PURPLE)
ax.barh(y - h/2, rvals, h, label="keyword match (full corpus)", color=GREY)
ax.set_yticks(y); ax.set_yticklabels([short(d["tell"]) for d in sel])
ax.set_xlabel("Share mentioning the tell (%)")
ax.set_title("Cited vs keyword-matched, per tell\n"
             "('however/thus' and 'nuanced' look big to a keyword pass but go uncited; "
             "structure and 'as an AI' are cited but under-matched)")
ax.legend(loc="lower right"); ax.margins(x=0.02); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_regex_vs_cited.png"), dpi=130); plt.close()

print("wrote chart_tells_cited.png, chart_regex_vs_cited.png")
