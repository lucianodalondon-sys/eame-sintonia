#!/usr/bin/env python3
"""RT1 - the consolidated numbers quoted in RT1-semantics.md, all 21 seasons of stage
data fetched from the live API."""
import os, sys, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

CORE = ["u", "l1v", "l1m", "l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"]
ATT = ["u", "l1v", "l2v"]
DAN = ["l3v", "l3m", "pv", "pm", "fu"]
DEAD_YOUNG = ["l1m", "l2m"]


def close(a, b, tol=0.101):
    return abs(a - b) <= tol


def main():
    yrs = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:4])
                  for f in os.listdir(L.FETCH) if f.startswith("c2_s1_v")})
    rows = L.visit_table(years=set(yrs), with_stages=True)
    full = [r for r in rows if all(r.get(c) is not None for c in CORE)
            and all(r.get(c) is not None for c in ("tot", "attiva", "dannosa", "totale"))
            and r["tot"] > 0]
    n = len(full)
    print(f"seasons fetched {yrs[0]}-{yrs[-1]} ({len(yrs)} seasons)")
    print(f"visits with tot>0 and all 14 columns readable: {n} "
          f"(archive has {len(L.visit_table())} visits in total)")
    print()

    def val(r, cols):
        """the source's own value, under the era rule, expressed as the source writes it"""
        s = sum(r[c] for c in cols)
        return 100.0 * s / r["tot"] if r["year"] >= 2020 else s

    print("== THE THREE DEFINITIONS (era rule: count <=2019, percent >=2020) ==")
    for label, tgt, cols in (("attiva  = u + l1v + l2v", "attiva", ATT),
                             ("dannosa = l3v + l3m + pv + pm + fu", "dannosa", DAN),
                             ("totale  = the 10 core stages (ps excluded)", "totale", CORE)):
        eq = sum(1 for r in full if close(val(r, cols), r[tgt]))
        print(f"  {label:44s} {eq} of {n} ({100.0*eq/n:.2f}%)")
    print()

    print("== THE THIRD COMPONENT OF `totale` ==")
    gap = [r for r in full if (r["totale"] - r["attiva"] - r["dannosa"]) > 0]
    eq = sum(1 for r in gap if close(val(r, DEAD_YOUNG),
                                     r["totale"] - r["attiva"] - r["dannosa"]))
    print(f"  totale - (attiva + dannosa) == l1m + l2m (DEAD first- and second-instar "
          f"larvae)")
    print(f"    on the {len(gap)} visits where the gap is > 0: {eq} exact "
          f"({100.0*eq/len(gap):.2f}%)")
    eq_all = sum(1 for r in full if close(val(r, DEAD_YOUNG),
                                          r["totale"] - r["attiva"] - r["dannosa"]))
    print(f"    on all {n} visits: {eq_all} ({100.0*eq_all/n:.2f}%)")
    print("  the sheet's three guesses, tested:")
    for nm, cols in (("u (eggs)", ["u"]), ("fu (exit holes)", ["fu"]),
                     ("u + fu", ["u", "fu"])):
        e = sum(1 for r in gap if close(val(r, cols),
                                        r["totale"] - r["attiva"] - r["dannosa"]))
        print(f"    gap == {nm:18s} {e} of {len(gap)} ({100.0*e/len(gap):.2f}%)")
    print()

    print("== ps (punture sterili) IS NOT IN totale ==")
    ps = [r for r in full if r.get("ps") is not None and r["ps"] > 0]
    if ps:
        w = sum(1 for r in ps if close(val(r, CORE + ["ps"]), r["totale"]))
        wo = sum(1 for r in ps if close(val(r, CORE), r["totale"]))
        print(f"  visits with ps > 0: {len(ps)}; totale == core+ps in {w}, "
              f"totale == core alone in {wo}")
        tot_ps = sum(r["ps"] for r in ps)
        print(f"  summed ps on those visits: {tot_ps:g}, invisible to every rate the "
              f"engine publishes")
    print()

    print("== IS THE UNIT DRUPES? ==")
    over = [r for r in full if sum(r[c] for c in CORE) > r["tot"]]
    print(f"  sum(10 core stages) > tot (more findings than olives sampled) in "
          f"{len(over)} of {n}")
    multi = [r for r in full if sum(1 for c in CORE if r[c] > 0) >= 3]
    print(f"  visits with 3 or more distinct stages present at once: {len(multi)} of {n} "
          f"({100.0*len(multi)/n:.2f}%) - a drupe holding an egg and a larva is counted "
          f"in both columns and twice in totale")
    ratios = sorted(sum(r[c] for c in CORE) / r["tot"] for r in full)
    print(f"  sum(core)/tot: median {ratios[len(ratios)//2]:.4f}, "
          f"p99 {ratios[int(0.99*len(ratios))]:.4f}, max {ratios[-1]:.4f}")
    print()

    print("== LIVENESS: what `attiva` leaves out ==")
    live = sum(r["u"] + r["l1v"] + r["l2v"] + r["l3v"] + r["pv"] for r in full)
    inn = sum(r["u"] + r["l1v"] + r["l2v"] for r in full)
    out = sum(r["l3v"] + r["pv"] for r in full)
    print(f"  live individuals recorded: {int(live)}; inside attiva {int(inn)} "
          f"({100.0*inn/live:.2f}%); outside it, inside dannosa {int(out)} "
          f"({100.0*out/live:.2f}%)")
    dan = sum(r["l3v"] + r["l3m"] + r["pv"] + r["pm"] + r["fu"] for r in full)
    print(f"  mass of dannosa {int(dan)}, of which live (l3v+pv) {int(out)} "
          f"({100.0*out/dan:.2f}%)")
    eggs = sum(r["u"] for r in full)
    print(f"  eggs inside attiva: {int(eggs)} of {int(inn)} ({100.0*eggs/inn:.2f}%) "
          f"- an egg is not yet an infestation of the drupe's flesh")
    nz = [r for r in full if (r["l3v"] + r["pv"]) > 0]
    z = [r for r in nz if r["attiva"] == 0]
    print(f"  visits with live third-instar larvae or live pupae present: {len(nz)}; "
          f"attiva reads 0 on {len(z)} of them ({100.0*len(z)/len(nz):.2f}%)")
    print()

    print("== the l1m+l2m gap is MORTALITY, and it is large ==")
    dead = sum(r["l1m"] + r["l2m"] for r in full)
    core_sum = sum(sum(r[c] for c in CORE) for r in full)
    print(f"  dead first- and second-instar larvae: {int(dead)} of {int(core_sum)} "
          f"total findings ({100.0*dead/core_sum:.2f}%)")
    byyear = collections.defaultdict(lambda: [0.0, 0.0])
    for r in full:
        byyear[r["year"]][0] += r["l1m"] + r["l2m"]
        byyear[r["year"]][1] += sum(r[c] for c in CORE)
    print("  share of `totale` that is dead young larvae, per season:")
    for y in sorted(byyear):
        a, b = byyear[y]
        print(f"    {y}: {100.0*a/b:5.2f}%  ({int(a)} of {int(b)})")


if __name__ == "__main__":
    main()
