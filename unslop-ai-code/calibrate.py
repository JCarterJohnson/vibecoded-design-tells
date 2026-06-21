#!/usr/bin/env python3
"""Calibration: count REAL descriptive phrasings in the on-topic comments to
rebuild the lexicon on evidence instead of a priori guesses."""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
coms = [json.loads(l) for l in open(os.path.join(HERE,"comments.jsonl"))]
bodies = [(c.get("body") or "").lower() for c in coms]
N = len(bodies)
print("comments:", N)
def cnt(label, *pats):
    rx = [re.compile(p, re.I) for p in pats]
    n = sum(1 for b in bodies if any(r.search(b) for r in rx))
    print("  %-46s %5d  %4.1f%%" % (label, n, 100*n/N))

print("--- COMMENTS cluster ---")
cnt("comment + every line", r"comment.{0,25}every.{0,6}line", r"every.{0,6}line.{0,25}comment")
cnt("too many/excessive/unnecessary/useless comments", r"(too many|excessive|unnecessary|pointless|useless|redundant|so many|pointless)\s+comment")
cnt("comments explain obvious/what code does", r"comment.{0,30}(obvious|what the (code|line)|every line|each line|what it)")
cnt("over-commented", r"over[- ]?comment")
cnt("comment(s) word (any)", r"\bcomment")
print("--- NAMING ---")
cnt("verbose/descriptive/long + name/var", r"(verbose|descriptive|long|generic|meaningless)\s+(variable|function|method|param|naming|names?)",
    r"names?\s+(are|that are|being)\s+(too|very|so|overly)\s+(verbose|long|descriptive)")
cnt("naming (any)", r"(variable|function)\s+names?|\bnaming\b")
print("--- ERROR HANDLING / STRUCTURE ---")
cnt("try/except|catch + every/wrap/around", r"try[ /]?(except|catch).{0,25}(every|everything|wrap|around)", r"wrap.{0,20}try[ /]?(except|catch)")
cnt("defensive / over-engineered", r"defensive|over[- ]?engineer|over[- ]?complicat|over[- ]?abstract")
cnt("unnecessary abstraction/too many layers", r"unnecessar.{0,15}(abstraction|class|layer)|too many (layers|abstraction|classes)")
cnt("boilerplate (any)", r"boilerplate")
cnt("tutorial/textbook/generic-looking code", r"tutorial[- ]?(style|like|code)|textbook|looks generic|generic[- ]?(looking|code)")
print("--- EMOJI / ARTIFACTS ---")
cnt("emoji + code/comment/commit/console", r"emoji.{0,25}(code|comment|commit|console|log|print|variable|readme)", r"(code|comment|commit|console|readme|print).{0,25}emoji")
cnt("emoji word (any)", r"emoji|✅|🚀|🎉")
cnt("leftover backticks/markdown/code fence", r"(left|leftover|forgot|still|stray).{0,22}(backtick|code ?fence|markdown)", r"markdown.{0,15}(in|inside).{0,8}code")
cnt("as an AI / language model / I cannot", r"as an ai|language model|i cannot|i can.?t (assist|help|provide)")
cnt("here is the complete/updated ...", r"here.?s (the|your) (complete|updated|full|corrected|fixed|refactored)")
cnt("'certainly'/'sure! here' preamble", r"\bcertainly\b|sure[!,. ]+here")
print("--- DICTION / COMMENT STYLE that ALSO shows in code ---")
cnt("perfect/too clean/consistent formatting", r"(too|suspiciously) (clean|perfect|consistent)|perfectly (formatted|consistent)|immaculate")
cnt("inconsistent w/ codebase / style mismatch", r"(doesn.?t|does not) match.{0,15}(style|codebase|rest)|inconsistent (style|with)")
cnt("placeholder // your code here / rest of code", r"your (code|logic|implementation) here|rest of (the|your) (code|implementation)|\.\.\..{0,12}(rest|etc)")
