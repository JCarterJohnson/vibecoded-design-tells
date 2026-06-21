#!/usr/bin/env python3
"""
unslop_code_scan.py - scan source code for the mechanical "tells" that give away
AI-written code, across languages.

Plain Python, standard library only. The patterns and their severity come from a Reddit
analysis (11,906 on-topic posts + 11,306 comments across 55 AI / coding / SaaS subreddits,
2020 to 2026) of what developers actually name as a giveaway that code was written by an
LLM. Every candidate was classified by an LLM into a fixed taxonomy of 19 tells, then each
top tell was adversarially verified by re-reading the quotes. Severity follows the verified
share, so the report tells you where to spend effort.

What it can and cannot see. The loudest tells in the data are about shape and substance:
boilerplate / tutorial-shaped code (verified 18.6%, the #1 tell), hallucinated APIs (11.2%),
over-engineering (7.8%), ignoring the surrounding codebase (3.5%), mixed skill level (1.9%).
A regex cannot judge any of those; they are documented in references/tells.md for a human or
a compiler. This scanner catches the mechanical, surface tells: leftover chat/assistant text,
placeholder comments, emoji, swallowed errors, narrating comments, and generic placeholder
names.

Usage:
    python3 unslop_code_scan.py <path>                 # scan a dir or file
    python3 unslop_code_scan.py <path> --severity high # only the strongest signals
    python3 unslop_code_scan.py <path> --json          # machine-readable (for CI)
    python3 unslop_code_scan.py <path> --max 8         # cap examples shown per rule

A line containing  unslop-ignore  is skipped, for a pattern you are using on purpose.
Exit code is the number of HIGH-severity findings (0 = none), so CI can gate on it.
"""
import os, re, sys, json, argparse

EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".rb", ".php",
        ".c", ".h", ".cpp", ".cc", ".hpp", ".cs", ".kt", ".kts", ".swift", ".scala",
        ".m", ".mm", ".sh", ".bash", ".lua", ".dart", ".vue", ".svelte", ".sql", ".r"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "vendor", "target",
             "coverage", ".venv", "venv", "__pycache__", ".idea", ".gradle", "bin", "obj"}
W = {"high": 3, "medium": 2, "low": 1}
CMT = r"(?://|#|/\*|\*|--|<!--)"   # comment openers across common languages
EMOJI = ("\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF"
         "\U00002B00-\U00002BFF\U0001F900-\U0001F9FF\U00002764")

# Each rule: id, label, severity, share (the verified data share), fix, patterns.
# Severity follows the verified shares, with the two conclusive paste-in artifacts raised
# to HIGH because when they survive into committed code they are unmistakable.
RULES = [
    # ---------- HIGH: the conclusive paste-in artifacts ----------
    {"id": "chat-artifact", "label": "Leftover chat / assistant / markdown artifact in the code", "sev": "high",
     "share": "verified 1.2%, but unmistakable when present",
     "fix": "Delete the assistant's voice before committing: code fences, 'Here's the updated code', 'As an AI', 'Good catch!', a trailing 'Note:'.",
     "pats": [r"^\s*```", r"\bhere'?s the (updated|complete|full|fixed|revised|new) (code|version|implementation|file)\b",
              r"\bas an? (ai|a\.i\.) (language )?model\b", r"\bas a large language model\b",
              r"\b(good|great) catch!", r"\byou'?re absolutely right\b",
              r"^\s*" + CMT + r"\s*(note|remember|important|keep in mind|tip)\s*:",
              r"\b(certainly|sure)! here('?s| is)\b", r"\bi'?ll (add|update|fix|implement) .{0,40}\bnow\b",
              r"\bi hope this helps\b", r"\blet me know if you'?d?\s*(like|need|want)\b"]},
    {"id": "placeholder-comment", "label": "Placeholder / ellipsis comment left in (\"// rest of your code\")", "sev": "high",
     "share": "verified 1.6%, precision ~100%",
     "fix": "Write the actual code. These '... rest of the code' stubs mean the file was pasted from a chat, not finished.",
     "pats": [r"" + CMT + r"\s*\.{2,}\s*(rest|the rest|your|remaining|existing|previous|other)\b",
              r"" + CMT + r"\s*(rest|remainder) of (your |the |my )?(code|implementation|logic|function|file|owl)\b",
              r"" + CMT + r"\s*(your|the) (code|logic|implementation|stuff) (goes )?here\b",
              r"" + CMT + r"\s*(add|insert|implement|put) (your )?(code|logic|implementation) here\b",
              r"" + CMT + r"\s*(implementation|code|logic) (goes |go )?here\b",
              r"" + CMT + r"\s*existing code (here|unchanged|stays|remains)\b",
              r"" + CMT + r"\s*\.\.\. ?\((?:rest|your|the|existing)[^)]*\)",
              r"" + CMT + r"\s*TODO:?\s*(implement|add|fill in|finish)\b"]},

    # ---------- MEDIUM: the surface tells ----------
    {"id": "emoji-in-code", "label": "Emoji in code, comments, strings, logs, or commit text", "sev": "medium",
     "share": "verified 3.9%, precision ~77% (the highest-precision cosmetic tell)",
     "fix": "Remove emoji from source. They survive from the model's chat output and read as vibe-coded.",
     "pats": [r"[" + EMOJI + r"]"]},
    {"id": "swallowed-errors", "label": "Catch-all / swallowed errors (bare except, empty catch)", "sev": "medium",
     "share": "verified 3.1% (try/except wrapped around everything)",
     "fix": "Catch specific exceptions and handle them. A bare except or an empty catch eats the one clue you needed.",
     "pats": [r"^\s*except\s*:", r"^\s*except\s+(Exception|BaseException)\s*:\s*(pass|\.\.\.|$)",
              r"\bcatch\s*\([^)]*\)\s*\{\s*\}", r"\bcatch\s*\{\s*\}",
              r"\brescue\s*=>\s*\w+\s*$", r"\bcatch\s*\([^)]*\)\s*\{\s*//"]},
    {"id": "narrating-comment", "label": "Narrating comment that restates the obvious / step-by-step '# Step 1'", "sev": "medium",
     "share": "verified 8.5% (over-commenting; the regex catches the obvious-restatement subset)",
     "fix": "Cut comments that say what the next line plainly does. Comment why, not what.",
     "pats": [r"" + CMT + r"\s*(step\s*\d+\b|now we\b|first,|next,|then,|finally,)",
              r"" + CMT + r"\s*(increment|decrement|initialize|declare|define|create|instantiate|loop (over|through)|iterate over|return the|set the|get the|assign|call the)\b",
              r"" + CMT + r"\s*this (function|method|line|loop|variable|class|block) (does|is|will|handles|returns|creates)\b",
              r"" + CMT + r"\s*(import|importing) (the |required )?(libraries|modules|dependencies)\b"]},
    {"id": "generic-naming", "label": "Generic placeholder function name (process_data, handleData, doStuff)", "sev": "medium",
     "share": "verified 1.9%, precision ~100% (process_data() is the canonical example)",
     "fix": "Name it for what it actually does in this domain. process_data() that does 11 things is the AI tell.",
     "pats": [r"\b(def|function|func|fn|fun|sub)\s+(process_?[Dd]ata|handle_?[Dd]ata|do_?[Ss]tuff|do_?[Ss]omething|my_?[Ff]unction|process_?[Ii]tem|process_?[Ii]nput|main_?[Ff]unction)\b",
              r"\b(process_?[Dd]ata|handle_?[Dd]ata|do_?[Ss]tuff|do_?[Ss]omething)\s*\("]},

    # ---------- LOW: weak / inflated signals ----------
    {"id": "verbose-naming", "label": "Over-verbose, robotically self-documenting identifier", "sev": "low",
     "share": "verified 0.4% (inflated; people mostly argue FOR descriptive names)", "cs": True,
     "fix": "A name that is a whole sentence (getUserDataFromApiResponseHandler) reads as machine-generated. Trim it.",
     "pats": [r"\b[a-z]+([A-Z][a-z0-9]+){4,}\b", r"\b[a-z]+(_[a-z0-9]+){5,}\b"]},
    {"id": "boilerplate-marker", "label": "Boilerplate / dummy-data marker (placeholder keys, sample data, 'Successfully' logs)", "sev": "low",
     "share": "weak proxy for the #1 tell (tutorial-shaped code), which is otherwise not regex-detectable",
     "fix": "Replace generated dummy data and placeholders with the real thing. Tutorial-shaped sample data is the loudest tell, but only a human can judge the shape.",
     "pats": [r"\blorem ipsum\b", r"\b(your|my)[-_]?api[-_]?key\b", r"\bYOUR_API_KEY\b", r"\bexample\.com\b",
              r"\b(John|Jane) (Doe|Smith)\b", r"['\"]sk-(xxx|your|placeholder|123)",
              r"(console\.log|print|println|fmt\.Print\w*|System\.out\.print\w*)\s*\(\s*['\"](✅|🚀|Successfully|Done!|Here we go)"]},
]

def compile_rules(min_sev):
    order = ["high", "medium", "low"]
    floor = order.index(min_sev) if min_sev else len(order) - 1
    out = []
    for r in RULES:
        if order.index(r["sev"]) > floor:
            continue
        r = dict(r)
        flags = 0 if r.get("cs") else re.IGNORECASE
        r["rx"] = [re.compile(p, flags) for p in r["pats"]]
        out.append(r)
    return out

def iter_files(path):
    if os.path.isfile(path):
        yield path; return
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".min.js") or f.endswith(".min.css") or f.endswith(".map"):
                continue
            if os.path.splitext(f)[1].lower() in EXTS:
                yield os.path.join(root, f)

def scan(path, min_sev):
    rules = compile_rules(min_sev)
    findings = []
    for fp in iter_files(path):
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except Exception:
            continue
        if len(lines) == 1 and len(lines[0]) > 5000:   # likely minified
            continue
        for i, line in enumerate(lines, 1):
            if "unslop-ignore" in line.lower():
                continue
            for r in rules:
                for rx in r["rx"]:
                    m = rx.search(line)
                    if m:
                        findings.append({"rule": r["id"], "label": r["label"], "sev": r["sev"],
                                         "share": r["share"], "fix": r["fix"], "file": fp, "line": i,
                                         "match": m.group(0).strip()[:50], "snippet": line.strip()[:160]})
                        break
    return findings

def verdict(by_sev, weighted):
    if by_sev.get("high", 0) >= 3 or weighted >= 15:
        return "STRONG AI-written-code tells"
    if by_sev.get("high", 0) >= 1 or weighted >= 6:
        return "Some AI tells present"
    if weighted > 0:
        return "Mostly clean, minor tells"
    return "Clean, no surface tells detected"

def main():
    ap = argparse.ArgumentParser(description="Scan source code for AI-written-code tells.")
    ap.add_argument("path")
    ap.add_argument("--severity", choices=["high", "medium", "low"], default="low",
                    help="minimum severity to report (default: low = everything)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--max", type=int, default=10, help="max examples shown per rule (text mode)")
    args = ap.parse_args()

    if not os.path.exists(args.path):
        print(f"path not found: {args.path}", file=sys.stderr); sys.exit(2)

    findings = scan(args.path, args.severity)
    by_sev, by_rule = {}, {}
    for f in findings:
        by_sev[f["sev"]] = by_sev.get(f["sev"], 0) + 1
        by_rule.setdefault(f["rule"], []).append(f)
    weighted = sum(W[s] * n for s, n in by_sev.items())
    files_scanned = sum(1 for _ in iter_files(args.path))

    if args.json:
        print(json.dumps({"path": args.path, "files_scanned": files_scanned, "counts": by_sev,
                          "slop_score": weighted, "verdict": verdict(by_sev, weighted),
                          "findings": findings}, indent=2))
        sys.exit(by_sev.get("high", 0))

    sev_order = {"high": 0, "medium": 1, "low": 2}
    rule_ids = sorted(by_rule, key=lambda rid: (sev_order[by_rule[rid][0]["sev"]], -len(by_rule[rid])))
    print(f"\n  unslop-code scan: {args.path}")
    print(f"  files scanned: {files_scanned}   findings: {len(findings)}   slop score: {weighted}")
    print(f"  verdict: {verdict(by_sev, weighted)}")
    print(f"  high: {by_sev.get('high',0)}   medium: {by_sev.get('medium',0)}   low: {by_sev.get('low',0)}\n")
    if not findings:
        print("  No surface tells flagged. The loudest tells are structural and a regex cannot see\n"
              "  them: boilerplate / tutorial-shaped code, hallucinated APIs, over-engineering, and\n"
              "  code that ignores the surrounding repo. Review those by hand against references/tells.md.\n")
        return
    for rid in rule_ids:
        items = by_rule[rid]
        f0 = items[0]
        print(f"  [{f0['sev'].upper()}] {f0['label']}  ({len(items)} hit{'s' if len(items)!=1 else ''})  [{f0['share']}]")
        print(f"        fix: {f0['fix']}")
        for it in items[:args.max]:
            print(f"        {it['file']}:{it['line']}  ({it['match']})  {it['snippet']}")
        if len(items) > args.max:
            print(f"        ... +{len(items) - args.max} more")
        print()
    top = [by_rule[rid][0]['label'] for rid in rule_ids[:3]]
    print("  Top things to change: " + "; ".join(top))
    print("  The big tells (boilerplate, hallucinated APIs, over-engineering) need eyes. See references/tells.md.\n")
    sys.exit(by_sev.get("high", 0))

if __name__ == "__main__":
    main()
