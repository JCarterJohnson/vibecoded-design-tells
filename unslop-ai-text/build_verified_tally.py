#!/usr/bin/env python3
"""
build_verified_tally.py - Join the human-verified citation ranking (workflow
synthesis.final_ranking, already deduped/reconciled/audited) to the regex Lens-1
shares, so each verified tell shows how the regex over/under/agreed/was-blind.
Writes verified_tally.csv.
"""
import json, csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(HERE, "extract_result.json")))
final = res["synthesis"]["final_ranking"]

# regex same-sample comparison, keyed by a short concept tag
comp = {}
for r in csv.DictReader(open(os.path.join(HERE, "comparison.csv"))):
    comp[r["tell"]] = r
def C(lexlabel):
    r = comp.get(lexlabel)
    if not r: return (None, None, None)
    rs = r["regex_share_sample_pct"]; rf = r["regex_share_fullcorpus_pct"]; v = r["verdict"]
    return (rs, rf, v)

# map each verified tell (by keyword) to its regex comparison concept (LEX label in comparison.csv)
# value None => regex has no lexicon entry for it (structurally blind)
def match(tell):
    t = tell.lower()
    if "em dash" in t: return 'em dash ("—") as a tell'
    if "not just x" in t or "not x, but y" in t or "not x but y" in t: return '"it\'s not just X, it\'s Y"'
    if "robotic sentence rhythm" in t or "uniform" in t: return None
    if "sycophancy" in t or "positivity" in t: return None
    if "formulaic" in t or "perfectly-structured" in t: return "perfectly structured / formulaic"
    if "bullet lists" in t or "listicle" in t: return "everything in bullet points / lists"
    if "dive in" in t or "deep dive" in t: return '"dive in" / "deep dive" / "let\'s dive"'
    if "rule of three" in t or "triad" in t: return '"rule of three" / triads'
    if "empty summary" in t or "says noth" in t or "soulless" in t: return None
    if "bolded lead-in" in t: return "bolded lead-in bullets (**Word:**)"
    if "as an ai" in t or "leftover assistant boilerpl" in t: return '"as an AI language model"'
    if "hallucinat" in t or "fabricated citation" in t: return None
    if "honestly" in t or "fake-relatability" in t or "filler opener" in t: return None
    if "unlock" in t: return '"unlock/unleash the power/potential"'
    if "marketing" in t or "hype language" in t: return None
    if "verbosity" in t or "repetition" in t: return None
    if "transitions" in t: return None  # "forced/smooth transitions" is structural; regex only counts the connective words, not forced-ness
    if "no contractions" in t or "over-formal" in t or "overly formal" in t: return None
    if "hedg" in t or "both-sides" in t: return None
    if "fast-paced" in t or "scene-setting" in t: return '"in today\'s fast-paced/digital world"'
    if "emoji" in t: return "emoji bullets / emoji headers"
    if "horizontal-rule" in t or "dividers" in t: return None
    if "fake typos" in t: return None
    if "in conclusion" in t or "in summary" in t: return '"in conclusion" / "in summary"'
    if "diction meme" in t or t.startswith("single-word"): return "delve"  # representative
    return None

rows = []
for r in final:
    tell = r.get("tell", "")
    concept = match(tell)
    rs, rf, verdict = C(concept) if concept else (None, None, None)
    if concept is None:
        vs = "REGEX-BLIND (no lexicon entry — cannot be regex-detected)"
        rf_out = "n/a"
    else:
        vs = verdict or "n/a"
        rf_out = rf if rf not in (None, "") else "n/a"
    rows.append({
        "rank": r.get("rank"),
        "tell": tell,
        "category": r.get("category"),
        "confidence": r.get("confidence"),
        "cite_share_sample_pct": r.get("share_pct"),
        "regex_share_sample_pct": rs if rs is not None else "n/a",
        "regex_share_fullcorpus_pct": rf_out,
        "vs_regex": vs,
        "what_to_do": r.get("note", ""),
    })

with open(os.path.join(HERE, "verified_tally.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["rank","tell","category","confidence",
        "cite_share_sample_pct","regex_share_sample_pct","regex_share_fullcorpus_pct",
        "vs_regex","what_to_do"])
    w.writeheader(); w.writerows(rows)

print(f"wrote verified_tally.csv ({len(rows)} verified tells)")
blind = sum(1 for r in rows if r["vs_regex"].startswith("REGEX-BLIND"))
print(f"regex-blind tells (regex structurally cannot catch): {blind}/{len(rows)}")
for r in rows:
    print(f'{r["rank"]:>2} [{r["confidence"]:6}] {r["tell"][:46]:46} cite {str(r["cite_share_sample_pct"]):>4}%  rgx(full) {str(r["regex_share_fullcorpus_pct"]):>4}  | {r["vs_regex"]}')
