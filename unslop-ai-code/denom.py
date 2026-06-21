#!/usr/bin/env python3
"""Standalone best-effort denominator pass: per-sub per-year TOTAL posts via the
Arctic Shift aggregate endpoint. Fast-fail on the busy subs that time out; record
what we can. Writes/overwrites totals_by_year.csv. Resumable (skips subs already
present). Run: python3 denom.py [max_seconds]"""
import os, csv, sys, time
from collect import SUBREDDITS, count_by_year, log
HERE = os.path.dirname(os.path.abspath(__file__))
TOTALS = os.path.join(HERE, "totals_by_year.csv")

def main():
    budget = float(sys.argv[1]) if len(sys.argv)>1 else 420.0
    t0=time.time()
    done=set()
    if os.path.exists(TOTALS):
        for r in csv.DictReader(open(TOTALS)):
            done.add(r["subreddit"])
    write_header = not os.path.exists(TOTALS)
    f=open(TOTALS,"a",newline=""); w=csv.writer(f)
    if write_header: w.writerow(["subreddit","lane","query","year","posts"])
    ok=0
    for sub,lane in SUBREDDITS.items():
        if sub in done: continue
        if time.time()-t0>budget:
            log("[denom pause] budget hit"); break
        yrs,st=count_by_year(sub)
        if st=="ok" and yrs:
            for yr,c in sorted(yrs.items()):
                if yr.isdigit() and int(yr)>=2020:
                    w.writerow([sub,lane,"_ALL_",yr,c])
            f.flush(); ok+=1
        log("  denom %-22s %s"%(sub,st))
    f.close()
    log("[denom end] subs_with_totals(this run)=%d"%ok)

if __name__=="__main__":
    main()
