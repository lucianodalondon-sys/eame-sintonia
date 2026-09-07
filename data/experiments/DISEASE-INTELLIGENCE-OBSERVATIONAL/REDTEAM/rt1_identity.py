#!/usr/bin/env python3
"""RT1 - ACCUSATION 1 & 2: what ARE attiva / dannosa / totale, and is the unit drupes?

Tests every additive combination of the 11 stage variables against attiva, dannosa and
totale, on visits where all of them are readable. If any of the three equals an exact sum
of per-individual stage counts, the sheet's "count of drupes" is wrong.
"""
import os, sys, json, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

YEARS = None            # all years present in FETCH


def main():
    yrs = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:4])
                  for f in os.listdir(L.FETCH) if f.startswith("c2_s1_v")})
    print(f"stage years available: {yrs}")
    rows = L.visit_table(years=set(yrs), with_stages=True)
    stages = list(L.STAGE_VARS.values())
    full = [r for r in rows if all(r.get(c) is not None
                                   for c in stages + ["tot", "attiva", "dannosa", "totale"])]
    print(f"visits in those seasons: {len(rows)}; with ALL 15 columns readable: {len(full)}")
    print()

    # ---- 1. does sum(all stages) relate to attiva/dannosa/totale? -------------
    def s(r, names):
        return sum(r[n] for n in names)

    live = ["u", "l1v", "l2v", "l3v", "pv"]
    dead = ["l1m", "l2m", "l3m", "pm"]
    print("== exact-equality hit rate for named candidate sums ==")
    cands = {
        "u+l1v+l2v+l3v+pv (live stages)": live,
        "u+l1v+l2v+l3v (live, no pupa)": ["u", "l1v", "l2v", "l3v"],
        "l1v+l2v+l3v (live larvae)": ["l1v", "l2v", "l3v"],
        "l2v+l3v+pv+fu (damaging classic)": ["l2v", "l3v", "pv", "fu"],
        "l2v+l2m+l3v+l3m+pv+pm+fu": ["l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"],
        "ALL 11 stages": stages,
        "ALL except ps": [x for x in stages if x != "ps"],
        "live+dead+fu": live + dead + ["fu"],
    }
    for tgt in ("attiva", "dannosa", "totale"):
        print(f"  -- target {tgt} --")
        for nm, cols in cands.items():
            eq = sum(1 for r in full if abs(s(r, cols) - r[tgt]) < 1e-9)
            print(f"     {nm:36s} exact in {eq:>6} of {len(full)}  ({100.0*eq/len(full):.2f}%)")
    print()

    # ---- 2. brute force: every subset of the 11 stages, best match ------------
    print("== brute force: best subset of the 11 stage vars for each target ==")
    for tgt in ("attiva", "dannosa", "totale"):
        best = []
        for k in range(1, len(stages) + 1):
            for combo in itertools.combinations(stages, k):
                eq = 0
                for r in full:
                    tot_ = 0.0
                    for c in combo:
                        tot_ += r[c]
                    if abs(tot_ - r[tgt]) < 1e-9:
                        eq += 1
                best.append((eq, combo))
        best.sort(key=lambda t: (-t[0], len(t[1])))
        print(f"  -- {tgt} --  (best 5 of {len(best)} subsets)")
        for eq, combo in best[:5]:
            print(f"     {'+'.join(combo):40s} exact in {eq:>6} of {len(full)} "
                  f"({100.0*eq/len(full):.2f}%)")
    print()

    # ---- 3. UNIT TEST: can the stage sum exceed tot? --------------------------
    print("== unit test: individuals vs drupes ==")
    over = [r for r in full if s(r, stages) > r["tot"] > 0]
    print(f"  sum(all 11 stages) > tot in {len(over)} of {len(full)} visits with tot>0")
    over_live = [r for r in full if s(r, live) > r["tot"] > 0]
    print(f"  sum(live stages)   > tot in {len(over_live)} of {len(full)}")
    # a drupe cannot hold more than one 'unit' if the count is drupes
    multi = [r for r in full if r["totale"] > 0 and s(r, stages) > r["totale"]]
    print(f"  sum(all 11 stages) > totale in {len(multi)} of {len(full)}")
    ratio = [s(r, stages) / r["totale"] for r in full if r["totale"] > 0]
    if ratio:
        ratio.sort()
        print(f"  ratio sum(stages)/totale: min {ratio[0]:.3f} "
              f"median {ratio[len(ratio)//2]:.3f} max {ratio[-1]:.3f}")
    print()

    # ---- 4. the gap: totale - (attiva+dannosa) vs each stage ------------------
    print("== the gap totale-(attiva+dannosa), matched against each stage column ==")
    gap_rows = [r for r in full]
    for c in stages + ["fu+ps", "ps", "l1m+l2m+l3m+pm"]:
        if c == "fu+ps":
            g = lambda r: r["fu"] + r["ps"]
        elif c == "l1m+l2m+l3m+pm":
            g = lambda r: r["l1m"] + r["l2m"] + r["l3m"] + r["pm"]
        else:
            g = lambda r, c=c: r[c]
        eq = sum(1 for r in gap_rows
                 if abs((r["totale"] - r["attiva"] - r["dannosa"]) - g(r)) < 1e-9)
        print(f"  gap == {c:22s} in {eq:>6} of {len(gap_rows)} ({100.0*eq/len(gap_rows):.2f}%)")
    print()

    # ---- 5. overlap: is attiva+dannosa double counting? ----------------------
    lt = sum(1 for r in full if r["attiva"] + r["dannosa"] < r["totale"])
    eqx = sum(1 for r in full if r["attiva"] + r["dannosa"] == r["totale"])
    gt = sum(1 for r in full if r["attiva"] + r["dannosa"] > r["totale"])
    print(f"== a+d vs totale on the stage-complete set: < {lt}, == {eqx}, > {gt} "
          f"of {len(full)}")
    return full


if __name__ == "__main__":
    main()
