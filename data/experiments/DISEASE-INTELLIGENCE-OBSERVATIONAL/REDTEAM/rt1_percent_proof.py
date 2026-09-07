#!/usr/bin/env python3
"""RT1 - ACCUSATION 6, THE DECISIVE ONE.

Two rival hypotheses for attiva / dannosa / totale:
  COUNT    the value is a count, so totale == sum(10 core stage counts)
  PERCENT  the value is already a percentage, so totale == 100 * sum(core) / tot

They are indistinguishable when tot == 100. The stage variables, fetched live, let us
separate them on every visit where tot != 100.
"""
import os, sys, collections
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
    full = [r for r in rows
            if all(r.get(c) is not None for c in CORE)
            and all(r.get(c) is not None for c in ("tot", "attiva", "dannosa", "totale"))
            and r["tot"] > 0]
    print(f"seasons {yrs}: {len(full)} visits with tot>0 and all stage columns readable")

    def s(r, cols):
        return sum(r[c] for c in cols)

    for label, tgt, cols in (("attiva", "attiva", ATT), ("dannosa", "dannosa", DAN),
                             ("totale", "totale", CORE)):
        print(f"\n===== {label} =====")
        for name, sel in (("tot == 100", lambda r: r["tot"] == 100),
                          ("tot != 100", lambda r: r["tot"] != 100),
                          ("tot != 100 AND stage sum > 0",
                           lambda r: r["tot"] != 100 and s(r, cols) > 0)):
            sub = [r for r in full if sel(r)]
            if not sub:
                print(f"  {name:32s} 0 visits")
                continue
            n_count = sum(1 for r in sub if close(s(r, cols), r[tgt]))
            n_pct = sum(1 for r in sub if close(100.0 * s(r, cols) / r["tot"], r[tgt]))
            print(f"  {name:32s} {len(sub):>6} visits | COUNT hypothesis "
                  f"{n_count:>6} ({100.0*n_count/len(sub):.2f}%) | PERCENT hypothesis "
                  f"{n_pct:>6} ({100.0*n_pct/len(sub):.2f}%)")

    print("\n===== the rows that separate them, one by one =====")
    sep = [r for r in full if r["tot"] != 100 and s(r, CORE) > 0]
    print(f"  {len(sep)} visits where tot != 100 and at least one stage is present")
    hdr = f"  {'field':>6} {'date':>10} {'tot':>6} {'totale':>7} {'sum(core)':>9} " \
          f"{'100*sum/tot':>11}  verdict"
    print(hdr)
    agree_pct = agree_cnt = neither = both = 0
    for r in sorted(sep, key=lambda r: (-r["tot"], r["date"]))[:30]:
        sc = s(r, CORE)
        pv = 100.0 * sc / r["tot"]
        c_ok, p_ok = close(sc, r["totale"]), close(pv, r["totale"])
        verdict = ("BOTH" if c_ok and p_ok else "PERCENT" if p_ok
                   else "COUNT" if c_ok else "neither")
        print(f"  {r['id_field']:>6} {r['date']:>10} {r['tot']:>6g} {r['totale']:>7g} "
              f"{sc:>9g} {pv:>11.3f}  {verdict}")
    for r in sep:
        sc = s(r, CORE)
        pv = 100.0 * sc / r["tot"]
        c_ok, p_ok = close(sc, r["totale"]), close(pv, r["totale"])
        if c_ok and p_ok:
            both += 1
        elif p_ok:
            agree_pct += 1
        elif c_ok:
            agree_cnt += 1
        else:
            neither += 1
    print(f"\n  over all {len(sep)} separating visits: PERCENT only {agree_pct}, "
          f"COUNT only {agree_cnt}, both {both}, neither {neither}")

    print("\n===== the same test on tot < 100 alone =====")
    lo = [r for r in full if 0 < r["tot"] < 100 and s(r, CORE) > 0]
    p_ok = sum(1 for r in lo if close(100.0 * s(r, CORE) / r["tot"], r["totale"]))
    c_ok = sum(1 for r in lo if close(s(r, CORE), r["totale"]))
    print(f"  {len(lo)} visits with 0 < tot < 100 and a stage present: "
          f"PERCENT {p_ok}, COUNT {c_ok}")
    for r in sorted(lo, key=lambda r: r["tot"])[:12]:
        print(f"    f{r['id_field']} {r['date']} tot={r['tot']:g} totale={r['totale']:g} "
              f"sum(core)={s(r,CORE):g} 100*sum/tot={100.0*s(r,CORE)/r['tot']:.2f}")


if __name__ == "__main__":
    main()
