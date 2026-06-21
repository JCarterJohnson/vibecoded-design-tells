#!/usr/bin/env python3
"""
analyze.py - Turn the mined corpus into structured, normalized findings.

Two lenses:
  LENS 1 (headline): of posts where people are actually discussing AI-writing
     tells (Family A queries), what SHARE name each specific AI-ism? Broken out
     by year so we can see the 5-year trend.
  LENS 2 (cross-check): for the distinctive named tells we queried directly
     (Family B), how much AI-context airtime does each get, and across how many
     communities (breadth vs. one-sub artifact)?

Reading rule: shares, not raw counts. Outputs CSVs + summary.txt + quote bank.
"""
import json, os, re, csv, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "corpus_raw.jsonl")

FAMILY_A = {
    "sounds like ChatGPT","sounds like AI","reads like ChatGPT","reads like AI",
    "written by ChatGPT","written by AI","obviously ChatGPT","obviously AI",
    "clearly written by AI","AI slop","AI generated text","looks AI generated",
    "smells like ChatGPT","ChatGPT wrote this","spot AI writing","detect AI writing",
    "telltale signs ChatGPT","dead giveaway AI","screams AI","ChatGPT writing style",
    "obvious AI writing","AI writing tells","how to tell AI wrote",
}

AI_MARKER = re.compile(r"\b(chat\s?gpt|gpt-?[345]|gpt|openai|llm|large language model|"
                       r"a\.i\.|ai[- ]?(generated|written|slop|text)|language model|"
                       r"claude|gemini|copilot|bard|\bai\b)\b", re.I)

# A post is genuinely ABOUT spotting AI writing (not just an incidental ChatGPT mention)
# if it matches one of these. This filters out viral noise that the loose AND-match lets in.
ONTOPIC_RX = re.compile("|".join([
    r"sound(s|ed|ing)? like (a |an )?(chat ?gpt|ai|bot|robot)",
    r"read(s|ing)? like (a |an )?(chat ?gpt|ai|bot)",
    r"written by (a |an )?(chat ?gpt|ai|bot|llm|gpt)",
    r"(chat ?gpt|ai|gpt|llm) (wrote|writes|generated|produced)",
    r"ai[- ]?(generated|written) (text|content|writing|copy|essay|email|post|comment)",
    r"\bai slop\b", r"chat ?gpt[- ]?ese", r"\bai writing\b", r"writing (sounds|reads|looks) like",
    r"(spot|detect|recogniz|identif|tell)\w* .{0,25}(ai|chat ?gpt)[- ]?(writ|text|generat|content)",
    r"(obvious|clearly|blatant|definitely|so)\w* (ai|chat ?gpt)[- ]?(writ|generat|text)",
    r"screams (ai|chat ?gpt)", r"smells like (chat ?gpt|ai)", r"\btelltale\b",
    r"em[- ]?dash", r"\bem dashes\b",
    r"(dead )?give[- ]?away.{0,20}(ai|chat ?gpt)", r"(ai|chat ?gpt).{0,20}(dead )?give[- ]?away",
    r"(chat ?gpt|ai) (writing style|prose|essay|copy|wording|phrasing|tone|vocabulary)",
    r"(words|phrases|tells|signs|markers|patterns) .{0,25}(ai|chat ?gpt)",
    r"(ai|chat ?gpt) .{0,15}(words|phrases|tells|signs|markers|patterns|cliche)",
    r"how (to|do you|can you|can i) (tell|spot|detect|know).{0,30}(ai|chat ?gpt)",
    r"is this (written by |from )?(ai|chat ?gpt)", r"this (is|was|reads|sounds) .{0,15}(ai|chat ?gpt)",
]), re.I)

def rx(*pats):
    return [re.compile(p, re.I) for p in pats]

# (category, label, [compiled patterns]) -- a post "mentions" the tell if ANY matches.
LEX = [
 # ---- DICTION: the words people single out ----
 ("diction","delve", rx(r"\bdelv(e|es|ing|ed)\b")),
 ("diction","tapestry", rx(r"\btapestr(y|ies)\b")),
 ("diction","testament (\"a testament to\")", rx(r"\btestament\b")),
 ("diction","realm (\"in the realm of\")", rx(r"\brealm\b")),
 ("diction","navigate / navigating", rx(r"\bnavigat(e|es|ing|ed)\b")),
 ("diction","elevate / elevating", rx(r"\belevat(e|es|ing|ed)\b")),
 ("diction","seamless(ly)", rx(r"\bseamless(ly)?\b")),
 ("diction","leverage", rx(r"\bleverag(e|es|ing|ed)\b")),
 ("diction","robust", rx(r"\brobust\b")),
 ("diction","intricate / intricacies", rx(r"\bintricate\b", r"\bintricac(y|ies)\b")),
 ("diction","meticulous(ly)", rx(r"\bmeticulous(ly)?\b")),
 ("diction","comprehensive", rx(r"\bcomprehensive\b")),
 ("diction","myriad", rx(r"\bmyriad\b")),
 ("diction","plethora", rx(r"\bplethora\b")),
 ("diction","paramount", rx(r"\bparamount\b")),
 ("diction","pivotal", rx(r"\bpivotal\b")),
 ("diction","crucial", rx(r"\bcrucial\b")),
 ("diction","harness (\"harness the power\")", rx(r"\bharness(es|ing|ed)?\b")),
 ("diction","unleash", rx(r"\bunleash(es|ing|ed)?\b")),
 ("diction","unlock (\"unlock the potential\")", rx(r"\bunlock(s|ing|ed)?\b")),
 ("diction","showcase", rx(r"\bshowcas(e|es|ing|ed)\b")),
 ("diction","facilitate", rx(r"\bfacilitat(e|es|ing|ed)\b")),
 ("diction","utilize (instead of \"use\")", rx(r"\butiliz(e|es|ing|ed|ation)\b")),
 ("diction","foster", rx(r"\bfoster(s|ing|ed)?\b")),
 ("diction","embark (\"embark on a journey\")", rx(r"\bembark(s|ing|ed)?\b")),
 ("diction","vibrant", rx(r"\bvibrant\b")),
 ("diction","bustling", rx(r"\bbustling\b")),
 ("diction","captivating", rx(r"\bcaptivat(e|es|ing|ed)\b")),
 ("diction","boasts", rx(r"\bboasts?\b")),
 ("diction","nestled", rx(r"\bnestled\b")),
 ("diction","game-changer", rx(r"\bgame[- ]?chang(er|ing|ers)\b")),
 ("diction","cutting-edge", rx(r"\bcutting[- ]?edge\b")),
 ("diction","ever-evolving / ever-changing", rx(r"\bever[- ]?(evolving|changing|growing)\b")),
 ("diction","multifaceted", rx(r"\bmultifaceted\b")),
 ("diction","holistic", rx(r"\bholistic\b")),
 ("diction","synergy", rx(r"\bsynerg(y|ies|istic)\b")),
 ("diction","streamline", rx(r"\bstreamlin(e|es|ing|ed)\b")),
 ("diction","empower", rx(r"\bempower(s|ing|ed|ment)?\b")),
 ("diction","underscore(s)", rx(r"\bunderscore(s|d|ing)?\b")),
 ("diction","profound", rx(r"\bprofound(ly)?\b")),
 ("diction","nuanced / nuance", rx(r"\bnuance(d|s)?\b")),
 ("diction","treasure trove", rx(r"\btreasure trove\b")),

 # ---- PHRASING / CADENCE: connective and filler tics ----
 ("phrasing","\"it's worth noting\"", rx(r"worth noting")),
 ("phrasing","\"it's important to note/remember\"", rx(r"important to (note|remember|understand)")),
 ("phrasing","\"that being said\"", rx(r"that being said")),
 ("phrasing","\"when it comes to\"", rx(r"when it comes to")),
 ("phrasing","\"in today's fast-paced/digital world\"", rx(r"in today'?s (fast[- ]?paced|digital|ever[- ]?changing|modern)? ?(world|age|landscape|era|society)")),
 ("phrasing","\"at the end of the day\"", rx(r"at the end of the day")),
 ("phrasing","\"needless to say\"", rx(r"needless to say")),
 ("phrasing","\"rest assured\"", rx(r"rest assured")),
 ("phrasing","\"look no further\"", rx(r"look no further")),
 ("phrasing","\"the world of ...\"", rx(r"\bthe world of\b")),
 ("phrasing","\"dive in\" / \"deep dive\" / \"let's dive\"", rx(r"\b(deep dive|dive in|dive into|let'?s dive)\b")),
 ("phrasing","\"buckle up\"", rx(r"buckle up")),
 ("phrasing","\"in conclusion\" / \"in summary\"", rx(r"\bin (conclusion|summary)\b")),
 ("phrasing","\"first and foremost\"", rx(r"first and foremost")),
 ("phrasing","\"last but not least\"", rx(r"last but not least")),
 ("phrasing","\"first/secondly/lastly\" stack", rx(r"\b(firstly|secondly|thirdly|lastly)\b")),
 ("phrasing","\"whether you're a ... or ...\"", rx(r"whether you'?re (a|an|just)")),
 ("phrasing","\"not only ... but also\"", rx(r"not only\b.{0,60}\bbut also")),
 ("phrasing","\"it's not just X, it's Y\"", rx(r"(it'?s|its|it is) not just\b", r"\bisn'?t just\b", r"not just about\b")),
 ("phrasing","\"more than just\"", rx(r"more than just")),
 ("phrasing","\"say goodbye to\"", rx(r"say goodbye to")),
 ("phrasing","\"take it to the next level\"", rx(r"to the next level")),
 ("phrasing","\"the key to\"", rx(r"\bthe key to\b")),
 ("phrasing","\"navigating the complexities/landscape\"", rx(r"navigat\w* the (complexit|landscape|world|challeng)")),
 ("phrasing","\"unlock/unleash the power/potential\"", rx(r"(unlock|unleash|harness)\w* the (power|potential|full)")),
 ("phrasing","\"elevate your ...\"", rx(r"elevate your")),
 ("phrasing","\"in the ever-evolving landscape\"", rx(r"ever[- ]?evolving (landscape|world|field)")),
 ("phrasing","\"without further ado\"", rx(r"without further ado")),
 ("phrasing","overuse of \"moreover/furthermore/additionally\"", rx(r"\b(moreover|furthermore|additionally)\b")),
 ("phrasing","overuse of \"however,\" / \"thus,\" / \"hence\"", rx(r"\b(however|thus|hence|therefore),")),

 # ---- FORMAT / STRUCTURE ----
 ("format","em dash (\"—\") as a tell", rx(r"\bem[- ]?dash(es)?\b", r"\bemdash\b")),
 ("format","bolded lead-in bullets (**Word:**)", rx(r"bold(ed)? (bullet|lead|header|text|point)", r"\*\*[^*\n]{2,40}\*\*\s*:")),
 ("format","emoji bullets / emoji headers", rx(r"emoji (bullet|header|heading|in|at the start)", r"\bemoji[- ]?(spam|overload)\b")),
 ("format","everything in bullet points / lists", rx(r"\bbullet ?points?\b", r"\bbulleted? list")),
 ("format","\"rule of three\" / triads", rx(r"rule of three", r"\btriad", r"\btricolon")),
 ("format","headers / bold everywhere / markdown", rx(r"\bmarkdown\b", r"bold(ed)? (everything|every|words|headers)")),
 ("format","perfectly structured / formulaic", rx(r"\bformulaic\b", r"too (well|perfectly) structured", r"perfectly structured")),
 ("format","rhetorical question then answer", rx(r"rhetorical question")),

 # ---- SELF-DISCLOSURE / REFUSAL ARTIFACTS (pasted dead giveaways) ----
 ("artifact","\"as an AI language model\"", rx(r"as an? (ai|a\.i\.) (language )?model", r"as a large language model")),
 ("artifact","\"I cannot/can't assist/fulfill\"", rx(r"i (cannot|can'?t) (assist|help|fulfill|comply|provide)")),
 ("artifact","\"I don't have personal/the ability\"", rx(r"i (don'?t|do not) have (personal|the ability|access|feelings)")),
 ("artifact","\"knowledge cutoff / as of my last update\"", rx(r"knowledge cut[- ]?off", r"as of my last (knowledge )?update", r"my training data")),
 ("artifact","\"would you like me to ...?\"", rx(r"would you like me to")),
 ("artifact","\"let me know if you'd like / feel free\"", rx(r"let me know if you('?d| would)? ?(like|need|want)", r"feel free to (ask|reach)")),
 ("artifact","\"I hope this helps!\"", rx(r"i hope this helps")),
 ("artifact","\"Certainly!\" / \"Absolutely!\" openers", rx(r"\b(certainly|absolutely|sure)!\B", r"^(certainly|absolutely)\b")),
 ("artifact","\"great question!\"", rx(r"(great|good|excellent) question")),
 ("artifact","\"I hope this email finds you well\"", rx(r"hope (this|you'?re) .{0,20}finds? you well", r"hope this email finds you")),
]

# Generic words/phrases that humans use normally -> regex presence in a post does
# NOT reliably mean the author is CITING it as an AI tell. Reported as low-confidence
# keyword signal; the Workflow's per-post citation pass is authoritative for these.
LOW_CONF = {
 "realm (\"in the realm of\")","navigate / navigating","elevate / elevating",
 "seamless(ly)","leverage","robust","intricate / intricacies","comprehensive",
 "crucial","harness (\"harness the power\")","unlock (\"unlock the potential\")",
 "showcase","facilitate","foster","vibrant","holistic","synergy","streamline",
 "empower","profound","nuanced / nuance","cutting-edge","multifaceted","paramount",
 "pivotal","myriad","plethora","meticulous(ly)","utilize (instead of \"use\")",
 "captivating","\"when it comes to\"","\"the world of ...\"","\"the key to\"",
 "\"not only ... but also\"","overuse of \"however,\" / \"thus,\" / \"hence\"",
 "overuse of \"moreover/furthermore/additionally\"","\"at the end of the day\"",
 "\"more than just\"","\"first/secondly/lastly\" stack","\"needless to say\"",
 "\"that being said\"","\"take it to the next level\"","\"the key to\"",
}
def conf_of(label):
    return "low" if label in LOW_CONF else "high"

def year_of(ts):
    try:
        return datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).year
    except Exception:
        return 0

def main():
    if not os.path.exists(RAW):
        print("no corpus yet:", RAW); return
    posts = {}  # id -> record
    n_lines = 0
    for line in open(RAW, encoding="utf-8"):
        n_lines += 1
        try:
            it = json.loads(line)
        except Exception:
            continue
        pid = it.get("id")
        if not pid:
            continue
        if pid not in posts:
            posts[pid] = {
                "id": pid, "sub": it.get("subreddit",""), "lane": it.get("_lane","?"),
                "score": it.get("score",0) or 0, "ncom": it.get("num_comments",0) or 0,
                "year": year_of(it.get("created_utc",0)),
                "text": ((it.get("title") or "") + "\n" + (it.get("selftext") or "")),
                "title": it.get("title") or "",
                "qs": set(), "fams": set(),
            }
        posts[pid]["qs"].add(it.get("_q",""))
        posts[pid]["fams"].add(it.get("_family",""))

    allp = list(posts.values())
    for p in allp:
        p["text_l"] = p["text"].lower()
        p["ai_ctx"] = (p["lane"] == "ai") or bool(AI_MARKER.search(p["text"]))
        p["is_A"] = bool(p["qs"] & FAMILY_A)
        p["is_topic"] = bool(ONTOPIC_RX.search(p["text"]))

    # on-topic corpus = matched a Family A intent phrase AND genuinely about AI writing
    loose = [p for p in allp if p["is_A"]]
    corpusA = [p for p in loose if p["is_topic"]]
    N = len(corpusA)
    print(f"raw lines={n_lines}  unique posts={len(allp)}  Family-A loose={len(loose)}  on-topic(tight)={N}")

    # ---------- corpus stats ----------
    by_lane = collections.Counter(p["lane"] for p in corpusA)
    by_year = collections.Counter(p["year"] for p in corpusA)
    by_sub  = collections.Counter(p["sub"] for p in corpusA)
    with open(os.path.join(HERE,"corpus_stats.txt"),"w") as f:
        f.write(f"unique posts (all queries): {len(allp)}\n")
        f.write(f"Family-A on-topic posts: {N}\n\n")
        f.write("by lane: "+str(dict(by_lane))+"\n\n")
        f.write("by year: "+str(dict(sorted(by_year.items())))+"\n\n")
        f.write("top 30 subs:\n")
        for s,c in by_sub.most_common(30):
            f.write(f"  {s:24} {c}\n")

    # ---------- LENS 1: tell shares over on-topic corpus, overall + by year ----------
    years = [y for y in sorted(by_year) if y >= 2021]
    rows = []
    quote_targets = {}
    for cat, label, pats in LEX:
        hits = [p for p in corpusA if any(pat.search(p["text"]) for pat in pats)]
        cnt = len(hits)
        share = cnt / N if N else 0
        yr_share = {}
        for y in years:
            yp = [p for p in corpusA if p["year"] == y]
            yh = sum(1 for p in yp if any(pat.search(p["text"]) for pat in pats))
            yr_share[y] = (yh / len(yp)) if yp else 0
        rows.append((cat, label, cnt, share, yr_share))
        # keep top-scored hits as quote candidates
        quote_targets[label] = sorted(hits, key=lambda p: p["score"], reverse=True)[:4]

    rows.sort(key=lambda r: r[2], reverse=True)
    with open(os.path.join(HERE,"findings_lens1.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","confidence","category","tell","posts_mentioning","share_pct_of_ontopic"]+[f"share_{y}" for y in years])
        for i,(cat,label,cnt,share,yr) in enumerate(rows,1):
            w.writerow([i,conf_of(label),cat,label,cnt,f"{share*100:.1f}"]+[f"{yr[y]*100:.1f}" for y in years])

    # ---------- LENS 2: distinctive named-term airtime (AI-context) ----------
    DISTINCT = ["delve","tapestry","rich tapestry","em dash","em-dash","testament to",
        "game changer","in conclusion","buckle up","let's dive in","dive deep",
        "navigating the","ever-evolving","look no further","rest assured",
        "it's worth noting","underscores the","i hope this email finds you well",
        "as an AI","as a large language model","would you like me to","let me know if",
        "I cannot fulfill","it's not just"," chef's kiss"]
    l2 = []
    for term in DISTINCT:
        hits = [p for p in allp if term in p["qs"] and p["ai_ctx"]]
        subs = len(set(p["sub"] for p in hits))
        l2.append((term, len(hits), subs))
    tot2 = sum(c for _,c,_ in l2) or 1
    l2.sort(key=lambda r:r[1], reverse=True)
    with open(os.path.join(HERE,"findings_lens2.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["term","ai_context_posts","share_pct_of_term_mentions","n_subreddits"])
        for term,c,subs in l2:
            w.writerow([term,c,f"{c/tot2*100:.1f}",subs])

    # ---------- quote bank for grounding the write-up ----------
    with open(os.path.join(HERE,"quote_bank.txt"),"w",encoding="utf-8") as f:
        # top on-topic posts overall
        f.write("=== TOP-SCORED ON-TOPIC POSTS (overall) ===\n")
        for p in sorted(corpusA,key=lambda x:x["score"],reverse=True)[:40]:
            f.write(f"\n[{p['score']}|{p['sub']}|{p['year']}] {p['title'][:120]}\n")
            body=p['text'].split('\n',1)[1] if '\n' in p['text'] else ''
            f.write("   "+body[:300].replace('\n',' ')+"\n")
        f.write("\n\n=== QUOTE CANDIDATES PER TOP TELL ===\n")
        for cat,label,cnt,share,yr in rows[:25]:
            f.write(f"\n--- {label}  ({cnt} posts, {share*100:.1f}%) ---\n")
            for p in quote_targets[label][:3]:
                snip = p["text"].replace("\n"," ")
                f.write(f"  [{p['score']}|{p['sub']}] {snip[:240]}\n")

    # ---------- reading chunks for the Workflow citation-extraction pass ----------
    # Prefer substantive discussion posts: decent engagement OR enough length to
    # actually enumerate tells. These get read by subagents to extract CITED tells.
    cand = [p for p in corpusA if (p["score"] >= 5 or len(p["text"]) >= 300)]
    cand.sort(key=lambda p: (p["score"], len(p["text"])), reverse=True)
    cand = cand[:600]
    cdir = os.path.join(HERE, "chunks")
    os.makedirs(cdir, exist_ok=True)
    for fn in os.listdir(cdir):
        if fn.startswith("chunk_"):
            os.remove(os.path.join(cdir, fn))
    CHUNK = 30
    nchunks = 0
    for ci in range(0, len(cand), CHUNK):
        part = cand[ci:ci+CHUNK]
        with open(os.path.join(cdir, f"chunk_{ci//CHUNK:02d}.txt"), "w", encoding="utf-8") as f:
            for p in part:
                f.write(f"### POST (r/{p['sub']}, {p['year']}, score {p['score']})\n")
                f.write(p["text"][:1200].strip() + "\n\n")
        nchunks += 1
    print(f"wrote {nchunks} chunk files ({len(cand)} posts) -> {cdir}")

    # console summary
    print("\nTOP 25 HIGH-CONFIDENCE TELLS (Lens 1, share of on-topic posts):")
    hi = [r for r in rows if conf_of(r[1])=="high"]
    for i,(cat,label,cnt,share,yr) in enumerate(hi[:25],1):
        print(f"{i:2}. {share*100:5.1f}%  [{cat:9}] {label}  (n={cnt})")
    print("\nTOP 15 LOW-CONFIDENCE (generic words; need citation-pass confirmation):")
    lo = [r for r in rows if conf_of(r[1])=="low"]
    for i,(cat,label,cnt,share,yr) in enumerate(lo[:15],1):
        print(f"{i:2}. {share*100:5.1f}%  [{cat:9}] {label}  (n={cnt})")
    print("\nLENS 2 top 15 (AI-context term airtime):")
    for term,c,subs in l2[:15]:
        print(f"  {c:5}  {term:34} in {subs} subs")

if __name__ == "__main__":
    main()
