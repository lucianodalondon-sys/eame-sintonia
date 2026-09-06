#!/usr/bin/env python3
"""
POWER ANALYSIS — what skill is even DETECTABLE at these sample sizes.

Run before any model, and independent of every label, because it answers a question that
does not depend on how the coding turns out: with n comparable seasons and k ordinal
classes, how many correct predictions would a model need before we could say it beat
chance rather than got lucky?

If the number of hits required exceeds what is plausibly attainable, then no result from
this dataset can be sold as a forecast — a good-looking accuracy would be unfalsifiable
rather than impressive. Knowing that in advance stops a lucky number being over-read later.

Exact binomial tail under the null "predictions are independent of the truth", i.e. each
prediction is right with probability p0 = 1/k.
"""
from math import comb
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def tail(n, hits, p0):
    """P(X >= hits) for X ~ Binomial(n, p0)."""
    return sum(comb(n, i) * p0**i * (1 - p0)**(n - i) for i in range(hits, n + 1))

def min_hits(n, p0, alpha):
    for h in range(n + 1):
        if tail(n, h, p0) <= alpha:
            return h
    return None

if __name__ == "__main__":
    rows = []
    print("k = number of ordinal classes; n = seasons actually scoreable in the backtest")
    print("'need' = minimum correct predictions for the result to clear the bar\n")
    for k in (2, 3):
        p0 = 1.0 / k
        print(f"=== k={k} classes (chance accuracy {p0:.2f})")
        print(f"{'n':>3s} {'need p<=.05':>12s} {'as acc':>7s} {'need Bonf p<=.01':>17s} {'as acc':>7s}")
        for n in (3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 24):
            h5 = min_hits(n, p0, 0.05)
            hb = min_hits(n, p0, 0.01)
            r = {"k": k, "n": n,
                 "need_hits_p05": h5, "need_acc_p05": round(h5 / n, 3) if h5 is not None else None,
                 "need_hits_bonf01": hb, "need_acc_bonf01": round(hb / n, 3) if hb is not None else None,
                 "attainable_p05": h5 is not None and h5 <= n,
                 "requires_perfection_p05": h5 == n}
            rows.append(r)
            f5 = f"{h5}/{n}" if h5 is not None else "impossible"
            fb = f"{hb}/{n}" if hb is not None else "impossible"
            a5 = f"{h5/n:.2f}" if h5 is not None else "-"
            ab = f"{hb/n:.2f}" if hb is not None else "-"
            flag = "  <- perfection required" if h5 == n else ""
            print(f"{n:3d} {f5:>12s} {a5:>7s} {fb:>17s} {ab:>7s}{flag}")
        print()

    notes = {
      "what_this_bounds": (
        "The backtest scores only seasons that have BOTH a comparable outcome AND enough "
        "prior labelled seasons to train on. Under strict temporal validation with a minimum "
        "training set of 5, a dataset of N labelled seasons yields roughly N-5 scoreable "
        "years, not N."),
      "the_hard_number": (
        "With 6 comparable seasons (the count both independent extraction runs agree on for "
        "2014-2025), strict temporal validation leaves about 1 scoreable year. One year cannot "
        "distinguish skill from chance under any test. PRELIMINARY_BACKTEST_RUN would be "
        "arithmetically meaningless, not merely weak."),
      "even_with_everything": (
        "If all 26 documents yielded comparable outcomes -- which the mechanical lexicon scan "
        "already rules out, since 14 of them carry no severity marker at all -- strict temporal "
        "validation gives ~21 scoreable years, needing 11/21 correct at k=3 to clear p<=0.05. "
        "That is the OPTIMISTIC ceiling for this pathosystem and this source."),
      "why_it_is_reported_before_modelling": (
        "Computing the detectability bound after seeing a result invites fitting the bar to the "
        "number. It is fixed here, in advance, and does not depend on any label."),
    }
    dest = os.path.join(ROOT, "BACKTEST", "power_analysis.json")
    json.dump({"rows": rows, "notes": notes}, open(dest, "w"), indent=1)
    for k, v in notes.items():
        print(f"{k}:\n  {v}\n")
    print(f"wrote {dest}")
