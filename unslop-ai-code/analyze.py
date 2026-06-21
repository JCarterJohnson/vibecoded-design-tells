#!/usr/bin/env python3
"""
analyze.py - Turn the mined corpus of posts into structured, normalized findings
about the tells in AI-WRITTEN CODE.

Reading rule: SHARE of on-topic posts, not raw counts (subs grow over time).

Lens 1 (headline): among posts where people are actually discussing AI-written
   code (matched a Family-A intent phrase), what SHARE names each specific code
   tell? Broken out by year so the 5-year trend is visible. Detection is a
   synonym/idiom lexicon (LEX below), so it is deterministic and reproducible.

Lens 2 (cross-check): for the distinctive idioms we queried directly (Family B),
   how much code-context airtime does each get, and across how many communities
   (breadth vs. a one-sub artifact)?

Outputs: tell_counts.csv, tell_share_by_year.csv, lens2_idioms.csv,
   corpus_stats.txt, quote_bank.txt.
"""
import json, os, re, csv, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "corpus.jsonl")

FAMILY_A = {
    "AI generated code", "AI written code", "code written by AI",
    "ChatGPT wrote this code", "Copilot generated code", "Claude wrote this code",
    "Cursor generated code", "looks AI generated", "obviously AI code",
    "clearly AI code", "spot AI code", "detect AI code", "tell AI wrote code",
    "AI slop code", "screams AI", "smells like AI", "dead giveaway AI",
    "telltale signs AI", "obvious ChatGPT code", "looks like AI wrote",
    "vibe coded", "vibe coding", "is this AI code", "AI generated commit",
}

# A post counts as "code context" if it is in an AI/coding lane OR its text
# carries an AI marker near a code word (keeps SaaS-lane false positives out).
AI_MARKER = re.compile(r"\b(chat\s?gpt|gpt-?[0-9o]+|gpt|openai|copilot|claude|cursor|"
                       r"gemini|llm|large language model|codex|a\.?i\.?[- ]?(generated|written|code|slop)|"
                       r"\bai\b)\b", re.I)
CODE_WORD = re.compile(r"\b(code|coding|codebase|function|method|script|program|"
                       r"variable|comment|commit|repo|pull request|\bpr\b|snippet|"
                       r"refactor|class|api|syntax|compile|bug|python|javascript|"
                       r"typescript|rust|golang|java|c\+\+|sql)\b", re.I)

def rx(*pats):
    return [re.compile(p, re.I) for p in pats]

# (category, label, [compiled patterns]) -- a post "mentions" the tell if ANY matches.
# Patterns target how PEOPLE DESCRIBE the tell, plus literal artifacts they paste.
LEX = [
 # ================= COMMENTS (the loudest AI-code cluster) =================
 ("comments","over-commenting / a comment on every line",
   rx(r"comment(s|ing)? on (almost )?every (single )?line", r"\bover[- ]?comment", r"too many comments",
      r"excessive comments?", r"comments? (for|on) every", r"comment(s|ing)? every line",
      r"a comment (above|before|on) (almost )?every")),
 ("comments","comments that restate / explain the obvious",
   rx(r"comment(s)? (that )?(just )?(restate|repeat|explain) (the )?(obvious|code|what)",
      r"obvious comments?", r"redundant comments?", r"comment(s)? explaining the obvious",
      r"explains? (what )?(the )?(code|every line) (does|is doing)",
      r"// ?increment", r"# ?increment", r"comment(s)? (that )?state the obvious")),
 ("comments","narrating / step-by-step comments ('# Step 1', '# Now we...')",
   rx(r"#\s*step\s*\d", r"//\s*step\s*\d", r"# ?now we", r"// ?now we",
      r"step[- ]by[- ]step comments?", r"narrat(es|ing|ion).{0,15}comment",
      r"# ?(first|next|then|finally),? we", r"comments? (that )?narrate")),
 ("comments","placeholder / ellipsis comments ('// rest of your code', '// ... your logic here')",
   rx(r"rest of (your|the) (code|implementation|logic|function)",
      r"your (code|logic|implementation) (goes )?here",
      r"(implementation|logic|code) (goes )?here",
      r"//\s*\.\.\.", r"#\s*\.\.\.", r"\.\.\.\s*(rest|etc|and so on)",
      r"// ?(add|insert) (your|the|more)", r"# ?(add|insert) (your|the|more)",
      r"placeholder comment", r"and so on\b.{0,12}comment")),
 ("comments","docstring/JSDoc on every trivial function",
   rx(r"docstring(s)? (on|for) every", r"useless docstring", r"obvious docstring",
      r"docstring(s)? (that )?(just )?(restate|repeat)", r"jsdoc (on|for) every",
      r"doc ?comment(s)? (on|for) every", r"docstring for a (one|two)[- ]liner")),
 ("comments","leftover TODO/placeholder ('# TODO: implement', '// your code here')",
   rx(r"#\s*todo:? ?implement", r"//\s*todo:? ?implement", r"todo:? ?(implement|add|fill)",
      r"# ?implement (this|the|me)", r"// ?implement (this|the|me)")),

 # ================= ERROR HANDLING / DEFENSIVE =================
 ("errors","try/except (try/catch) wrapped around everything",
   rx(r"try[/ ]?(except|catch) (around|on|for|wrapping) every",
      r"(wrap(s|ped|ping)?|wrapped) everything in (a )?try",
      r"try[/ ]?(except|catch) (everywhere|on everything|hell)",
      r"every (function|thing|block) (in|has|wrapped) .{0,12}try",
      r"unnecessary try[/ ]?(except|catch)", r"excessive (error handling|try[/ ]?catch)")),
 ("errors","catch-all / swallowed errors ('except Exception', bare catch)",
   rx(r"except\s+exception", r"catch\s*\(\s*\)", r"bare except",
      r"catch[- ]?all (except|catch|error)", r"swallow(s|ing|ed)? (the )?(error|exception)",
      r"catch\s*\(\s*e\s*\)\s*\{?\s*\}?", r"pokemon exception", r"catching (all|every) exception")),
 ("errors","over-defensive: null/None checks & validation for impossible cases",
   rx(r"defensive (programming|code|coding)", r"over[- ]?defensive",
      r"unnecessary (null|none|nil|undefined) checks?", r"null check(s|ing)? everywhere",
      r"validat(e|es|ing|ion) (every|everything|every input)",
      r"checks? for (cases|things|inputs) that (can'?t|cannot|never)",
      r"guard(s)? (against|for) (things|cases) that")),

 # ================= STRUCTURE / OVER-ENGINEERING =================
 ("structure","over-engineered / needless abstraction for a simple task",
   rx(r"over[- ]?engineer(ed|ing|s)?", r"overly (complex|complicated|abstract)",
      r"unnecessary abstraction", r"abstraction(s)? (for|with) no (reason|need)",
      r"too many (layers|abstractions|classes)", r"enterprise (fizzbuzz|grade)",
      r"a (class|factory|interface) for (a|every)", r"reinvent(s|ing|ed)? the wheel")),
 ("structure","everything split into tiny helper functions",
   rx(r"(tiny|small|extra|extracts? everything into) (helper )?function",
      r"helper function(s)? for (a|every|each|trivial)",
      r"break(s|ing)? .{0,12}into (tiny|small|separate) function",
      r"a (separate )?function for (every|each)")),
 ("structure","boilerplate / scaffolding / tutorial-shaped code",
   rx(r"\bboilerplate\b", r"\bscaffold", r"tutorial[- ]?(style|shaped|like|code)",
      r"looks like a tutorial", r"textbook (code|example|style)",
      r"like (a|an) (intro|cs ?101|hello world) (example|tutorial)")),
 ("structure","reimplements something the stdlib/library already provides",
   rx(r"reimplement(s|ing|ed)? (a )?(standard|built[- ]?in|stdlib|library)",
      r"hand[- ]?rolled (a )?(loop|function) (instead|when)",
      r"didn'?t (use|know about) the (built[- ]?in|standard|library)",
      r"there'?s a (built[- ]?in|library function) for that")),

 # ================= NAMING =================
 ("naming","generic placeholder names (data, result, temp, item, foo, value)",
   rx(r"variable(s)? (named|called) (data|result|temp|tmp|item|value|val|output|response|res)\b",
      r"generic (variable|var) names?", r"names? like (data|result|temp|foo|item)",
      r"\bfoo ?bar\b", r"(everything|every variable) (is )?(named|called) (data|result)")),
 ("naming","over-descriptive / verbose names (handleSubmitButtonClick, getUserDataFromApi)",
   rx(r"overly (descriptive|verbose|long) (variable|function|names?|naming)",
      r"verbose (variable|function|naming|names?)",
      r"(handle|get|set|process|do|create|update)[A-Z][a-z]+[A-Z]",
      r"function names? (that are )?(too )?(long|verbose|descriptive)",
      r"ridiculously (long|descriptive) (names?|variable)")),

 # ================= FORMATTING / STYLE =================
 ("style","too clean / too perfect / suspiciously consistent formatting",
   rx(r"too (clean|perfect|consistent|polished|tidy)", r"suspiciously (clean|consistent|perfect)",
      r"perfectly (formatted|consistent|aligned)", r"immaculate (formatting|code|spacing)",
      r"(formatting|indentation|style) is too (clean|perfect|consistent)",
      r"no (typos|inconsistencies)")),
 ("style","style doesn't match the rest of the codebase",
   rx(r"(doesn'?t|does not|didn'?t) match (the|our|its|my) (style|codebase|conventions?|rest)",
      r"inconsistent with the (rest|codebase|existing)", r"different (style|convention) (than|from) the rest",
      r"out of place (in|with) the codebase", r"stick(s|ing)? out from the (rest|codebase)")),
 ("style","type hints / annotations on everything (incl. dynamically-typed langs)",
   rx(r"type (hints?|annotations?) (on |for )?(every|everything|everywhere)",
      r"(fully|completely) typed", r"typing every(thing| (variable|function))",
      r"adds? type hints? (to|where)", r"annotat(es|ing|ed) every")),
 ("style","over-use of f-strings / list comprehensions / one-liners",
   rx(r"f[- ]?strings? everywhere", r"list comprehension(s)? (for|everywhere|nested)",
      r"unnecessar(y|ily) (clever|dense) one[- ]?liner", r"cram(med|s|ming)? .{0,15}one line")),

 # ================= LANGUAGE-SPECIFIC IDIOMS =================
 ("lang-specific","Python: if __name__ == '__main__' / dataclasses / main() on trivial scripts",
   rx(r"if __name__", r"__main__", r"def main\(\)", r"dataclass(es)? for (a|every|trivial)",
      r"wraps? (a|the) (script|snippet) in (a )?main\(\)")),
 ("lang-specific","JS/TS: async/await, const, arrow funcs, optional chaining everywhere",
   rx(r"async[/ ]?await everywhere", r"const everything", r"arrow function(s)? everywhere",
      r"optional chaining everywhere", r"every(thing)? (is )?(an )?arrow function",
      r"useState .{0,12}everything")),
 ("lang-specific","unnecessary semicolons / explicit returns / verbose typing idioms",
   rx(r"unnecessary semicolons?", r"explicit return (where|everywhere)",
      r"verbose (typescript|java|c#) (boilerplate|types)")),

 # ================= OUTPUT / LOGGING =================
 ("output","emoji in code / console logs / commit messages (✅ 🚀 🎉)",
   rx(r"emoji(s)? in (the )?(code|console|log|logs|print|output|commit|comments?|terminal)",
      r"console\.log.{0,15}(emoji|✅|🚀|🎉|✨|🔥)", r"print.{0,15}(emoji|✅|🚀|🎉|✨)",
      r"[✅🚀🎉✨🔥💡⚡📦🎯👍]", r"checkmark emoji", r"rocket emoji",
      r"emoji[- ]?(laden|filled|spam)")),
 ("output","print/console.log debugging left everywhere; 'Successfully ...' messages",
   rx(r"console\.log (everywhere|all over|left)", r"print (statements? )?(everywhere|all over|left)",
      r"print debug", r'(print|console\.log|log)\(.{0,20}success',
      r"logs? everything", r'"(successfully|done|completed)')),

 # ================= ARTIFACTS (leftover AI text in code = strongest tells) =================
 ("artifact","chat preamble left in: 'Here's the complete/updated code', 'Sure! Here is'",
   rx(r"here'?s the (complete|full|updated|refactored|corrected|fixed|final) (code|implementation|version|function)",
      r"sure[!,]? here('?s| is)", r"certainly[!,]? here", r"here is (the|an?) (updated|complete|corrected)",
      r"i'?ve (updated|refactored|rewritten) (the|your) (code|function)")),
 ("artifact","explanatory 'Note:' / 'Remember:' / 'Keep in mind' preambles in the code",
   rx(r"\bnote:? (that|this|the|you|we)\b", r"\bremember:? (to|that|you)\b",
      r"keep in mind (that|you)", r"(it'?s )?(worth noting|important to note)")),
 ("artifact","model self-disclosure / refusal text pasted into code ('As an AI', 'I cannot')",
   rx(r"as an? (ai|a\.?i\.?) (language )?model", r"as a large language model",
      r"i (cannot|can'?t) (provide|assist|help|fulfill)",
      r"i (don'?t|do not) have (the ability|access|personal)",
      r"my (training|knowledge) (data|cut[- ]?off)")),
 ("artifact","markdown / code-fence backticks or '```python' left in the file",
   rx(r"```", r"code fence", r"backticks? (in|left|around)", r"markdown (in|left) (the )?code",
      r"triple backtick")),
]

def year_of(ts):
    try: return datetime.datetime.utcfromtimestamp(int(ts)).year
    except Exception: return 0

def main():
    if not os.path.exists(RAW):
        print("no corpus yet:", RAW); return
    posts = {}
    n_lines = 0
    for line in open(RAW, encoding="utf-8"):
        n_lines += 1
        try: it = json.loads(line)
        except Exception: continue
        pid = it.get("id")
        if not pid: continue
        if pid not in posts:
            posts[pid] = {
                "id": pid, "sub": it.get("subreddit",""), "lane": it.get("lane","?"),
                "score": it.get("score",0) or 0, "ncom": it.get("num_comments",0) or 0,
                "year": year_of(it.get("created_utc",0)),
                "text": ((it.get("title") or "") + "\n" + (it.get("selftext") or "")),
                "title": it.get("title") or "", "perma": it.get("permalink") or "",
                "qs": set(), "fams": set(),
            }
        posts[pid]["qs"].add(it.get("matched_query",""))
        posts[pid]["fams"].add(it.get("family",""))

    allp = list(posts.values())
    for p in allp:
        p["code_ctx"] = (p["lane"] in ("ai","code")) or (
            bool(AI_MARKER.search(p["text"])) and bool(CODE_WORD.search(p["text"])))
        p["is_A"] = bool(p["qs"] & FAMILY_A)

    corpusA = [p for p in allp if p["is_A"]]
    N = len(corpusA)
    print("raw lines=%d  unique posts=%d  Family-A on-topic=%d" % (n_lines, len(allp), N))

    # ---------- corpus stats ----------
    by_lane = collections.Counter(p["lane"] for p in corpusA)
    by_year = collections.Counter(p["year"] for p in corpusA)
    by_sub  = collections.Counter(p["sub"] for p in corpusA)
    with open(os.path.join(HERE,"corpus_stats.txt"),"w") as f:
        f.write("unique posts (all queries): %d\n" % len(allp))
        f.write("Family-A on-topic posts: %d\n\n" % N)
        f.write("by lane: %s\n\n" % dict(by_lane))
        f.write("by year: %s\n\n" % dict(sorted(by_year.items())))
        f.write("top 35 subs:\n")
        for s,c in by_sub.most_common(35):
            f.write("  %-24s %d\n" % (s,c))

    # ---------- Lens 1: tell shares over on-topic corpus, overall + by year ----------
    years = [y for y in sorted(by_year) if y >= 2020]
    rows, quote_targets = [], {}
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
        quote_targets[label] = sorted(hits, key=lambda p: p["score"], reverse=True)[:5]

    rows.sort(key=lambda r: r[2], reverse=True)
    with open(os.path.join(HERE,"tell_counts.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","category","tell","posts_mentioning","share_pct_of_ontopic"])
        for i,(cat,label,cnt,share,yr) in enumerate(rows,1):
            w.writerow([i,cat,label,cnt,"%.1f"%(share*100)])
    with open(os.path.join(HERE,"tell_share_by_year.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["category","tell"]+["share_%d"%y for y in years])
        for cat,label,cnt,share,yr in rows:
            w.writerow([cat,label]+["%.1f"%(yr[y]*100) for y in years])

    # ---------- Lens 2: distinctive idiom airtime (code-context) ----------
    DISTINCT = ["rest of your code","rest of the implementation","unnecessary comments",
        "over engineered","placeholder comments","comments on every line","emoji in code",
        "AI slop code","vibe coded","ChatGPT wrote this code","Copilot generated code"]
    l2 = []
    for term in DISTINCT:
        hits = [p for p in allp if term in p["qs"] and p["code_ctx"]]
        subs = len(set(p["sub"] for p in hits))
        l2.append((term, len(hits), subs))
    l2.sort(key=lambda r:r[1], reverse=True)
    tot2 = sum(c for _,c,_ in l2) or 1
    with open(os.path.join(HERE,"lens2_idioms.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["idiom","code_context_posts","share_pct_of_idiom_mentions","n_subreddits"])
        for term,c,subs in l2:
            w.writerow([term,c,"%.1f"%(c/tot2*100),subs])

    # ---------- quote bank ----------
    with open(os.path.join(HERE,"quote_bank.txt"),"w",encoding="utf-8") as f:
        f.write("=== TOP-SCORED ON-TOPIC POSTS (overall) ===\n")
        for p in sorted(corpusA,key=lambda x:x["score"],reverse=True)[:50]:
            body = p['text'].split('\n',1)[1] if '\n' in p['text'] else ''
            f.write("\n[%s|%s|%s] %s\n   %s\n" % (p['score'],p['sub'],p['year'],
                    p['title'][:120], body[:300].replace('\n',' ')))
        f.write("\n\n=== QUOTE CANDIDATES PER TOP TELL ===\n")
        for cat,label,cnt,share,yr in rows[:30]:
            f.write("\n--- %s  (%d posts, %.1f%%) ---\n" % (label,cnt,share*100))
            for p in quote_targets[label][:4]:
                snip = p["text"].replace("\n"," ")
                f.write("  [%s|%s] %s\n" % (p['score'],p['sub'],snip[:260]))

    print("\nTOP 30 TELLS (Lens 1, share of on-topic posts):")
    for i,(cat,label,cnt,share,yr) in enumerate(rows[:30],1):
        print("%2d. %5.1f%%  [%-13s] %s  (n=%d)" % (i,share*100,cat,label,cnt))

if __name__ == "__main__":
    main()
