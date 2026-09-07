#!/usr/bin/env python3
"""RT1 - ACCUSATION 12: is the definition the same in every season the engine compares?

The engine compares this window with the same window back to 2006. If the server-side
formula for attiva/dannosa/totale changed, the baseline is not a baseline.
Also: the Prato/Firenze province disagreement, the concrete tot=200 legend case, and
what drives the one province the tool calls INCREASING_OBSERVED.
"""
import os, sys, glob, json, collections, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

CORE = ["u", "l1v", "l1m", "l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"]
ATT = ["u", "l1v", "l2v"]
DAN = ["l3v", "l3m", "pv", "pm", "fu"]


def close(a, b, tol=0.101):
    return abs(a - b) <= tol


def main():
    yrs = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:4])
                  for f in os.listdir(L.FETCH) if f.startswith("c2_s1_v")})
    rows = L.visit_table(years=set(yrs), with_stages=True)
    full = [r for r in rows if all(r.get(c) is not None for c in CORE)
            and all(r.get(c) is not None for c in ("tot", "attiva", "dannosa", "totale"))
            and r["tot"] > 0]

    print("== is the server formula the same in every fetched season? ==")
    print(f"  {'year':>5} {'n':>6} {'attiva=u+l1v+l2v':>18} "
          f"{'dannosa=l3v+l3m+pv+pm+fu':>26} {'totale=10 core':>16}")
    for y in yrs:
        sub = [r for r in full if r["year"] == y]
        if not sub:
            continue
        a = sum(1 for r in sub if close(100.0 * sum(r[c] for c in ATT) / r["tot"], r["attiva"]))
        d = sum(1 for r in sub if close(100.0 * sum(r[c] for c in DAN) / r["tot"], r["dannosa"]))
        t = sum(1 for r in sub if close(100.0 * sum(r[c] for c in CORE) / r["tot"], r["totale"]))
        n = len(sub)
        print(f"  {y:>5} {n:>6} {a:>7} ({100.0*a/n:>5.2f}%) "
              f"{d:>10} ({100.0*d/n:>5.2f}%) {t:>7} ({100.0*t/n:>5.2f}%)")
    print()
    print("  same test restricted to visits where the stage sum is > 0 (the informative ones)")
    for y in yrs:
        sub = [r for r in full if r["year"] == y and sum(r[c] for c in CORE) > 0]
        if not sub:
            continue
        n = len(sub)
        a = sum(1 for r in sub if close(100.0 * sum(r[c] for c in ATT) / r["tot"], r["attiva"]))
        d = sum(1 for r in sub if close(100.0 * sum(r[c] for c in DAN) / r["tot"], r["dannosa"]))
        t = sum(1 for r in sub if close(100.0 * sum(r[c] for c in CORE) / r["tot"], r["totale"]))
        print(f"  {y:>5} {n:>6} {a:>7} ({100.0*a/n:>5.2f}%) "
              f"{d:>10} ({100.0*d/n:>5.2f}%) {t:>7} ({100.0*t/n:>5.2f}%)")
    print()

    print("== the gap totale-(attiva+dannosa) == l1m+l2m, per season ==")
    for y in yrs:
        sub = [r for r in full if r["year"] == y
               and (r["totale"] - r["attiva"] - r["dannosa"]) > 0]
        if not sub:
            print(f"  {y}: no visit with a positive gap")
            continue
        eq = sum(1 for r in sub
                 if close(100.0 * (r["l1m"] + r["l2m"]) / r["tot"],
                          r["totale"] - r["attiva"] - r["dannosa"]))
        print(f"  {y}: gap>0 in {len(sub)} visits; gap == 100*(l1m+l2m)/tot in {eq} "
              f"({100.0*eq/len(sub):.2f}%)")
    print()

    print("== the sheet's own counter-example, checked against the stages ==")
    print("  sheet: 'a dannosa of 6 out of 200 drupes is 3%, which the legend would paint "
          "yellow'")
    cases = [r for r in full if r["tot"] == 200 and r["dannosa"] and r["dannosa"] > 0]
    print(f"  visits with tot==200 and dannosa>0 in the fetched seasons: {len(cases)}")
    for r in sorted(cases, key=lambda r: -r["dannosa"])[:8]:
        sd = sum(r[c] for c in DAN)
        print(f"    f{r['id_field']} {r['date']} tot=200 dannosa={r['dannosa']:g} | "
              f"l3v={r['l3v']:g} l3m={r['l3m']:g} pv={r['pv']:g} pm={r['pm']:g} "
              f"fu={r['fu']:g} sum={sd:g} -> as a count {100.0*sd/200:.2f}% ; "
              f"as a percent the source wrote {r['dannosa']:g}%")
    print()

    print("== Prato: nome_area says Prato, the comune code says Firenze ==")
    seen = collections.Counter()
    for fn in sorted(glob.glob(os.path.join(L.CASE, "RAW", "*_v1_*.json"))):
        for row in json.load(open(fn, encoding="utf-8")):
            if row.get("nome_area") == "Prato":
                seen[(row.get("admin_code"), row.get("name_4"))] += 1
    print(f"  Prato rows carry {len(seen)} distinct comune codes: {seen.most_common(12)}")
    print()

    print("== Lucca, the one province the tool calls INCREASING_OBSERVED ==")
    arch = L.visit_table()
    as_of = dt.date(2026, 9, 6)
    for i in range(3):
        hi = as_of - dt.timedelta(days=28 * i)
        lo = hi - dt.timedelta(days=27)
        w = [r for r in arch if r["province"] == "Lucca" and r["date"]
             and lo.isoformat() <= r["date"] <= hi.isoformat()]
        u = [r for r in w if r["tot"] and r["tot"] > 0 and r["attiva"] is not None
             and 0 <= r["attiva"] <= r["tot"]]
        if not u:
            print(f"  window ending {hi}: no usable visit")
            continue
        num = sum(r["attiva"] for r in u)
        den = sum(r["tot"] for r in u)
        nz = [r for r in u if r["attiva"] > 0]
        bysite = collections.Counter()
        for r in u:
            bysite[r["id_field"]] += r["attiva"]
        print(f"  window ending {hi}: rate {100.0*num/den:.4f}% "
              f"({int(num)} of {int(den)}), {len(u)} visits at "
              f"{len({r['id_field'] for r in u})} groves, {len(nz)} visits non-zero, "
              f"orgs={sorted({r['org'] for r in u})}")
        print(f"     numerator by grove: {bysite.most_common(5)}")


if __name__ == "__main__":
    main()
