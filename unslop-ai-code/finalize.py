#!/usr/bin/env python3
"""
finalize.py - Turn the classification workflow's output into the final, VERIFIED
ranking + quote bank for the write-up.

Inputs:
  workflow_output.json   the Workflow return: {totals, ranked, verify,
                         raw_comment_classifications}
  candidates.jsonl       to join comment index -> body/score/sub for quotes
  comments.jsonl         for total on-topic comment denominator

Outputs:
  final_tell_counts.csv  ranked tells with comment/post counts, shares, verdict
  final_quote_bank.md    verbatim quotes per top tell (verifier picks + joins)
  final_summary.txt      headline numbers for the post
"""
import json, os, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__))

LABEL = {
 "over_comment":"Over-commenting: a comment on nearly every line, narrating the obvious",
 "redundant_docstring":"A docstring/JSDoc on every trivial function that just restates its name",
 "placeholder_comment":"Placeholder comments left in (\"// rest of your code\", \"# ... your logic here\")",
 "verbose_naming":"Over-verbose, robotically self-documenting variable/function names",
 "generic_naming":"Generic placeholder names (data, result, temp, item, foo)",
 "excessive_try":"try/except (try/catch) wrapped around everything / swallowed errors",
 "over_validation":"Defensive null checks & validation for cases that can't happen",
 "over_engineered":"Over-engineered: needless abstraction / layers for a simple task",
 "boilerplate_tutorial":"Boilerplate, tutorial/textbook-shaped 'sample app' code",
 "reinvent_wheel":"Re-implements what the stdlib/a library already does",
 "too_clean":"Suspiciously clean/consistent/perfect formatting, no human mess",
 "style_mismatch":"Style doesn't match the surrounding codebase; a sudden shift",
 "type_everywhere":"Type hints/annotations added everywhere, even where unusual",
 "emoji":"Emoji in code, comments, console logs, or commit messages",
 "excess_logging":"Print/console.log debugging left in; chatty 'Successfully...' logs",
 "chat_artifact":"Leftover chat/markdown artifacts (``` fences, 'Here's the updated code', 'As an AI', 'Note:')",
 "hallucinated_api":"Calls to nonexistent/outdated APIs; plausible but wrong logic",
 "inconsistent_skill":"Mixed skill: advanced code beside beginner mistakes; author can't explain it",
 "umbrella_looks_ai":"Umbrella: 'you can just tell it's AI / too perfect' with no specific feature named",
}

def main():
    wf = json.load(open(os.path.join(HERE,"workflow_output.json")))
    ranked = wf["ranked"]; verify = {v["code"]: v for v in wf.get("verify",[])}
    totals = wf["totals"]
    raw = wf.get("raw_comment_classifications",[])

    n_all_comments = sum(1 for _ in open(os.path.join(HERE,"comments.jsonl")))
    cand = {json.loads(l)["i"]: json.loads(l) for l in open(os.path.join(HERE,"candidates.jsonl"))}

    # precision-adjust: verified mentions = raw * precision (default 100% if not audited)
    for r in ranked:
        v = verify.get(r["code"], {})
        prec = v.get("precision_pct", 100) if v else 100
        r["precision"] = prec
        r["verdict"] = v.get("verdict","") if v else ""
        r["adj_comments"] = round(r["comments"] * prec / 100.0)
    named = totals["comment_named"] or 1
    for r in ranked:
        r["adj_share_pct"] = round(100*r["adj_comments"]/named, 1)

    # final table (ordered by verified/adjusted mentions, umbrella shown separately)
    spec = sorted([r for r in ranked if r["code"]!="umbrella_looks_ai"],
                  key=lambda r:(r["adj_comments"], r["comments"]), reverse=True)
    with open(os.path.join(HERE,"final_tell_counts.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank","code","tell","comment_mentions","post_mentions",
                    "raw_share_pct","precision_pct","verdict","verified_mentions",
                    "verified_share_pct","note"])
        for rank,r in enumerate(spec,1):
            code=r["code"]; v=verify.get(code,{})
            w.writerow([rank, code, LABEL.get(code,code), r["comments"], r["posts"],
                        r["comment_share_pct"], r["precision"], r["verdict"],
                        r["adj_comments"], r["adj_share_pct"], v.get("note","")])
        u=[r for r in ranked if r["code"]=="umbrella_looks_ai"][0]
        w.writerow(["-","umbrella_looks_ai",LABEL["umbrella_looks_ai"],u["comments"],u["posts"],
                    u["comment_share_pct"],"","umbrella","","",""])

    # quote bank: prefer verifier best_quotes; else join indices->bodies
    idxByCode = collections.defaultdict(list)
    for it in raw:
        for code in it.get("codes",[]):
            if code not in ("none",): idxByCode[code].append(it["i"])
    with open(os.path.join(HERE,"final_quote_bank.md"),"w",encoding="utf-8") as f:
        f.write("# Verified quote bank per AI-code tell\n\n")
        for r in ranked:
            code = r["code"]
            if r["comments"] < 3: continue
            v = verify.get(code, {})
            f.write("## %s  (%d comments, %.1f%% of tell-naming comments)\n" %
                    (LABEL.get(code,code), r["comments"], r["comment_share_pct"]))
            if v: f.write("verdict: **%s**, precision ~%s%% — %s\n\n" %
                          (v.get("verdict","?"), v.get("precision_pct","?"), v.get("note","")))
            qs = v.get("best_quotes") or []
            if qs:
                for q in qs[:4]:
                    f.write("- “%s”\n" % q.strip()[:380])
            else:
                seen=set()
                for i in idxByCode.get(code,[])[:200]:
                    c = cand.get(i)
                    if not c: continue
                    body=c["body"].strip()[:300]
                    if body in seen: continue
                    seen.add(body)
                    f.write("- [r/%s|%s] %s\n" % (c.get("sub"), c.get("score"), body.replace("\n"," ")))
                    if len(seen)>=4: break
            f.write("\n")

    # summary
    with open(os.path.join(HERE,"final_summary.txt"),"w") as f:
        f.write("comments_classified: %d\n" % totals["comments_classified"])
        f.write("posts_classified: %d\n" % totals["posts_classified"])
        f.write("comments naming a specific tell: %d\n" % totals["comment_named"])
        f.write("posts naming a specific tell: %d\n" % totals["post_named"])
        f.write("total on-topic comments (denominator): %d\n\n" % n_all_comments)
        f.write("RANKED (verified):\n")
        for i,r in enumerate(ranked,1):
            v=verify.get(r["code"],{})
            f.write("%2d. %-22s comments=%4d posts=%4d share=%4.1f%%  [%s p~%s%%]\n" %
                    (i,r["code"],r["comments"],r["posts"],r["comment_share_pct"],
                     v.get("verdict","?"),v.get("precision_pct","?")))

    print("=== FINAL VERIFIED RANKING (specific tells, ordered by verified mentions) ===")
    print("classified: %d comments, %d posts | tell-naming: %d comments, %d posts | denom: %d on-topic comments\n"
          % (totals["comments_classified"],totals["posts_classified"],
             totals["comment_named"],totals["post_named"],n_all_comments))
    for i,r in enumerate(spec,1):
        print("%2d. raw=%4.1f%% adj=%4.1f%%  %-20s c=%-3d(->%-3d) p=%-3d  [%s p~%s%%] %s" %
              (i, r["comment_share_pct"], r["adj_share_pct"], r["code"], r["comments"],
               r["adj_comments"], r["posts"], r["verdict"] or "-", r["precision"],
               LABEL.get(r["code"],"")[:42]))
    u=[r for r in ranked if r["code"]=="umbrella_looks_ai"][0]
    print("\n    umbrella 'just looks AI, no specific feature': %d comments (%.1f%%), %d posts"
          % (u["comments"], u["comment_share_pct"], u["posts"]))

if __name__ == "__main__":
    main()
