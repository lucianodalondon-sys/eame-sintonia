#!/usr/bin/env python3
"""RT1 - ACCUSATION 5: a second protocol hides inside the same schema.

The 2026 field ids in the 9xxx block report tot in the hundreds and fractional
infestation values. Print every column, including the stage columns, for those visits,
and test whether the value is a COUNT out of tot or a PERCENT.
"""
import os, sys, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

CORE = ["u", "l1v", "l1m", "l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"]


def main():
    rows = L.visit_table(years={2025, 2026}, with_stages=True)
    print("== every 2026 visit with tot > 100, with its stage columns ==")
    sel = [r for r in rows if r["year"] == 2026 and r["tot"] and r["tot"] > 100]
    print(f"  {len(sel)} such visits")
    for r in sorted(sel, key=lambda r: (r["id_field"], r["date"]))[:28]:
        st = " ".join(f"{c}={r[c]:g}" for c in CORE if r.get(c))
        ssum = sum(r[c] for c in CORE if r.get(c) is not None) \
            if all(r.get(c) is not None for c in CORE) else None
        print(f"  f{r['id_field']} {r['date']} {r['province'][:12]:12s} org={str(r['org'])[:14]:14s} "
              f"tot={r['tot']:>6g} att={r['attiva']} dan={r['dannosa']} "
              f"totale={r['totale']} sum(core)={ssum} | {st}")
    print()

    print("== the discriminating test: does totale == sum(core) on those rows too? ==")
    ok = [r for r in sel if all(r.get(c) is not None for c in CORE)
          and r["totale"] is not None]
    eq = sum(1 for r in ok if abs(sum(r[c] for c in CORE) - r["totale"]) < 1e-9)
    print(f"  {eq} of {len(ok)} visits with tot>100 satisfy totale == sum(10 core stages)")
    nonint_stage = [r for r in ok
                    if any(r[c] != int(r[c]) for c in CORE)]
    print(f"  visits with tot>100 where a STAGE column is itself fractional: "
          f"{len(nonint_stage)} of {len(ok)}")
    for r in nonint_stage[:8]:
        print(f"     f{r['id_field']} {r['date']} tot={r['tot']:g} "
              + " ".join(f"{c}={r[c]:g}" for c in CORE if r[c]))
    print()

    print("== distribution of tot for the 2026 field-id blocks ==")
    blocks = collections.defaultdict(list)
    for r in rows:
        if r["year"] != 2026 or r["tot"] is None:
            continue
        blocks["9xxx" if r["id_field"] >= 9000 else "<9000"].append(r)
    for b, rs in sorted(blocks.items()):
        tt = [r["tot"] for r in rs]
        at100 = sum(1 for t in tt if t == 100)
        ni = sum(1 for r in rs if r["totale"] is not None and r["totale"] != int(r["totale"]))
        print(f"  block {b}: {len(rs)} visits, tot==100 in {at100} "
              f"({100.0*at100/len(rs):.1f}%), median tot {statistics.median(tt):g}, "
              f"max {max(tt):g}, fractional totale in {ni}")
        pr = collections.Counter(r["province"] for r in rs)
        print(f"     provinces: {pr.most_common(6)}")
        og = collections.Counter(r["org"] for r in rs)
        print(f"     orgs: {og.most_common(6)}")
    print()

    print("== what the engine publishes vs what a percent reading would publish ==")
    win = [r for r in rows if r["date"] and "2026-08-10" <= r["date"] <= "2026-09-06"]
    for prov in ("Grosseto", "Pisa", "Firenze", "Siena"):
        p = [r for r in win if r["province"] == prov]
        usable = [r for r in p if r["tot"] and r["tot"] > 0
                  and r["attiva"] is not None and 0 <= r["attiva"] <= r["tot"]]
        num = sum(r["attiva"] for r in usable)
        den = sum(r["tot"] for r in usable)
        big = [r for r in usable if r["tot"] > 100]
        num_b = sum(r["attiva"] for r in big)
        den_b = sum(r["tot"] for r in big)
        # alternative: treat the tot>100 rows as already-percent
        alt_num = sum(r["attiva"] for r in usable if r["tot"] <= 100) + \
            sum(r["attiva"] / 100.0 * r["tot"] for r in big)
        print(f"  {prov:10s} pooled attiva rate {100.0*num/den:.4f}% "
              f"({int(num)} of {int(den)}) | tot>100 rows: {len(big)} of {len(usable)}, "
              f"{int(num_b)} of {int(den_b)} | if those are percents: "
              f"{100.0*alt_num/den:.4f}%")


if __name__ == "__main__":
    main()
