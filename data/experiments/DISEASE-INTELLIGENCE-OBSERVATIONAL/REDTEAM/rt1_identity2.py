#!/usr/bin/env python3
"""RT1 - ACCUSATION 1/2 part two. Same test on the FULL stage-complete set (ps excluded
from the completeness requirement, because ps is readable in only 894 of 6,481 rows),
plus the decisive unit test.
"""
import os, sys, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

CORE = ["u", "l1v", "l1m", "l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"]


def main():
    yrs = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:4])
                  for f in os.listdir(L.FETCH) if f.startswith("c2_s1_v")})
    rows = L.visit_table(years=set(yrs), with_stages=True)
    need = CORE + ["tot", "attiva", "dannosa", "totale"]
    full = [r for r in rows if all(r.get(c) is not None for c in need)]
    print(f"seasons {yrs}: {len(rows)} visits, {len(full)} with the 10 core stages + "
          f"tot/attiva/dannosa/totale readable")
    n = len(full)
    ps_ok = [r for r in full if r.get("ps") is not None]
    print(f"  of those, ps also readable in {len(ps_ok)}")
    print()

    def s(r, cols):
        return sum(r[c] for c in cols)

    print("== THE THREE IDENTITIES ==")
    tests = [
        ("attiva  == u+l1v+l2v", "attiva", ["u", "l1v", "l2v"]),
        ("attiva  == u+l1v+l2v+l3v", "attiva", ["u", "l1v", "l2v", "l3v"]),
        ("dannosa == l3v+l3m+pv+pm+fu", "dannosa", ["l3v", "l3m", "pv", "pm", "fu"]),
        ("totale  == 10 core stages", "totale", CORE),
    ]
    for label, tgt, cols in tests:
        eq = sum(1 for r in full if abs(s(r, cols) - r[tgt]) < 1e-9)
        print(f"  {label:34s} exact in {eq:>6} of {n} ({100.0*eq/n:.2f}%)")
    print()

    print("== THE GAP totale - (attiva + dannosa) ==")
    cands = {"l1m+l2m": ["l1m", "l2m"], "l1m": ["l1m"], "l2m": ["l2m"],
             "l1m+l2m+l3m": ["l1m", "l2m", "l3m"], "ps": None,
             "u": ["u"], "fu": ["fu"], "u+fu": ["u", "fu"]}
    for nm, cols in cands.items():
        if cols is None:
            eq = sum(1 for r in ps_ok
                     if abs((r["totale"] - r["attiva"] - r["dannosa"]) - r["ps"]) < 1e-9)
            print(f"  gap == {nm:14s} exact in {eq:>6} of {len(ps_ok)} "
                  f"({100.0*eq/len(ps_ok):.2f}%)  [ps-readable subset]")
            continue
        eq = sum(1 for r in full if abs((r["totale"] - r["attiva"] - r["dannosa"])
                                        - s(r, cols)) < 1e-9)
        print(f"  gap == {nm:14s} exact in {eq:>6} of {n} ({100.0*eq/n:.2f}%)")
    gapnz = [r for r in full if r["totale"] - r["attiva"] - r["dannosa"] > 0]
    print(f"  visits where the gap is > 0: {len(gapnz)} of {n}")
    if gapnz:
        eq = sum(1 for r in gapnz
                 if abs((r["totale"] - r["attiva"] - r["dannosa"])
                        - (r["l1m"] + r["l2m"])) < 1e-9)
        print(f"    of those, gap == l1m+l2m in {eq} of {len(gapnz)} "
              f"({100.0*eq/len(gapnz):.2f}%)")
        tot_gap = sum(r["totale"] - r["attiva"] - r["dannosa"] for r in gapnz)
        tot_dead = sum(r["l1m"] + r["l2m"] for r in gapnz)
        print(f"    summed gap {int(tot_gap)} drupes/individuals vs summed l1m+l2m "
              f"{int(tot_dead)}")
    print()

    print("== IS THE UNIT DRUPES OR INDIVIDUALS? ==")
    over_tot = [r for r in full if r["tot"] > 0 and s(r, CORE) > r["tot"]]
    print(f"  sum(10 core stages) > tot in {len(over_tot)} of {n}")
    for r in over_tot[:6]:
        print(f"     {r['date']} field {r['id_field']} {r['province']}: tot={r['tot']} "
              f"sum={s(r,CORE)} totale={r['totale']} attiva={r['attiva']} "
              f"dannosa={r['dannosa']} " + " ".join(f"{c}={r[c]:g}" for c in CORE if r[c]))
    over_totale = [r for r in full if r["totale"] > 0 and s(r, CORE) > r["totale"] + 1e-9]
    under_totale = [r for r in full if r["totale"] > 0 and s(r, CORE) < r["totale"] - 1e-9]
    print(f"  sum(core) > totale in {len(over_totale)} of {n}; "
          f"sum(core) < totale in {len(under_totale)} of {n}")
    # the sharpest test: two live stages both > 0 in the same visit summing beyond
    # what a per-drupe reading permits
    multi = [r for r in full if sum(1 for c in CORE if r[c] > 0) >= 3]
    print(f"  visits with 3 or more distinct stages present at once: {len(multi)} of {n}")
    print()

    print("== value/tot maximum: does a rate ever exceed 100%? ==")
    for tgt in ("attiva", "dannosa", "totale"):
        rr = [(r[tgt] / r["tot"], r) for r in full if r["tot"] > 0]
        rr.sort(key=lambda t: -t[0])
        print(f"  {tgt:8s} max value/tot = {rr[0][0]:.3f} "
              f"({rr[0][1][tgt]:g} of {rr[0][1]['tot']:g} on {rr[0][1]['date']}, "
              f"field {rr[0][1]['id_field']})")
        over = sum(1 for x, _ in rr if x > 1.0)
        print(f"           visits with {tgt} > tot: {over} of {len(rr)}")
    print()

    print("== ps (punture sterili): is it inside totale? ==")
    if ps_ok:
        pnz = [r for r in ps_ok if r["ps"] > 0]
        print(f"  ps readable {len(ps_ok)}, ps>0 in {len(pnz)}")
        eq_with = sum(1 for r in ps_ok if abs(s(r, CORE) + r["ps"] - r["totale"]) < 1e-9)
        eq_without = sum(1 for r in ps_ok if abs(s(r, CORE) - r["totale"]) < 1e-9)
        print(f"  totale == core+ps in {eq_with} of {len(ps_ok)}; "
              f"totale == core (ps outside) in {eq_without} of {len(ps_ok)}")
        if pnz:
            eq_w = sum(1 for r in pnz if abs(s(r, CORE) + r["ps"] - r["totale"]) < 1e-9)
            eq_wo = sum(1 for r in pnz if abs(s(r, CORE) - r["totale"]) < 1e-9)
            print(f"  on the {len(pnz)} visits with ps>0: core+ps {eq_w}, core alone {eq_wo}")
    return full


if __name__ == "__main__":
    main()
