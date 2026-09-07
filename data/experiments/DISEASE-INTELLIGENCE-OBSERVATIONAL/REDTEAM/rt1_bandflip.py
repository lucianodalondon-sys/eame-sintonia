#!/usr/bin/env python3
"""RT1 - how far the percent finding actually moves a PUBLISHED cell.

Every province x 28-day window in the archive that would pass the engine's own gates
(>=8 visits, >=400 drupes), scored under both readings, and the source colour band
compared. Plus the ISTAT check on nome_area done properly (6-digit comune codes).
"""
import os, sys, glob, json, collections, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

ISTAT = {"045": "Massa-Carrara", "046": "Lucca", "047": "Pistoia", "048": "Firenze",
         "049": "Livorno", "050": "Pisa", "051": "Arezzo", "052": "Siena",
         "053": "Grosseto", "100": "Prato"}


def band(p):
    if p is None:
        return "NONE"
    if p == 0:
        return "white"
    if p < 0.01:
        return "NO_BAND"
    if p < 6:
        return "green"
    if p < 10:
        return "yellow"
    return "red"


def main():
    rows = L.visit_table()
    byprov = collections.defaultdict(list)
    for r in rows:
        if r["province"] and r["date"]:
            byprov[r["province"]].append(r)

    print("== every province x 28-day window that passes the engine's gates ==")
    for metric in ("attiva", "dannosa", "totale"):
        cells = flips = nobandhits = 0
        worst = []
        for prov, rs in byprov.items():
            dates = sorted({r["date"] for r in rs})
            for d in dates:
                hi = dt.date.fromisoformat(d)
                lo = (hi - dt.timedelta(days=27)).isoformat()
                w = [r for r in rs if lo <= r["date"] <= d]
                u = [r for r in w if r["tot"] and r["tot"] > 0
                     and r[metric] is not None and 0 <= r[metric] <= r["tot"]]
                den = sum(r["tot"] for r in u)
                if len(u) < 8 or den < 400:
                    continue
                cells += 1
                e = 100.0 * sum(r[metric] for r in u) / den
                p = sum(r[metric] * r["tot"] for r in u) / den
                if band(e) == "NO_BAND" or band(p) == "NO_BAND":
                    nobandhits += 1
                if band(e) != band(p):
                    flips += 1
                    worst.append((abs(p - e), prov, d, e, p, band(e), band(p), len(u), den))
        worst.sort(key=lambda t: -t[0])
        print(f"  metric {metric}: {cells} gate-passing province-windows; "
              f"source band DIFFERS between the two readings in {flips} "
              f"({100.0*flips/cells:.3f}%); a window falls in the 0<rate<0.01 band hole in "
              f"{nobandhits}")
        for x in worst[:6]:
            print(f"     {x[1]:14s} window ending {x[2]}  engine {x[3]:.4f}% [{x[5]}] "
                  f"vs percent {x[4]:.4f}% [{x[6]}]  n={x[7]} den={int(x[8])}")
    print()

    print("== the band hole 0 < rate < 0.01: how often does a real window land in it? ==")
    for metric in ("attiva", "dannosa", "totale"):
        hits = []
        for prov, rs in byprov.items():
            dates = sorted({r["date"] for r in rs})
            for d in dates:
                hi = dt.date.fromisoformat(d)
                lo = (hi - dt.timedelta(days=27)).isoformat()
                w = [r for r in rs if lo <= r["date"] <= d]
                u = [r for r in w if r["tot"] and r["tot"] > 0
                     and r[metric] is not None and 0 <= r[metric] <= r["tot"]]
                den = sum(r["tot"] for r in u)
                if len(u) < 8 or den < 400:
                    continue
                e = round(100.0 * sum(r[metric] for r in u) / den, 4)
                if 0 < e < 0.01:
                    hits.append((prov, d, e, len(u), den))
        print(f"  {metric}: {len(hits)} gate-passing windows with 0 < rate < 0.01 "
              f"(band_for returns None; di_render.render_province raises TypeError)")
        for h in hits[:6]:
            print(f"     {h[0]:14s} ending {h[1]} rate {h[2]}% "
                  f"({h[3]} visits, {int(h[4])} drupes)")
    print()

    print("== is nome_area really the province? ISTAT comune code, 6 digits ==")
    ok = bad = unk = 0
    mism = collections.Counter()
    for fn in sorted(glob.glob(os.path.join(L.CASE, "RAW", "*_v1_*.json"))):
        for row in json.load(open(fn, encoding="utf-8")):
            ac, na = row.get("admin_code"), row.get("nome_area")
            if ac is None or na is None:
                unk += 1
                continue
            exp = ISTAT.get(str(ac).zfill(6)[:3])
            if exp is None:
                unk += 1
            elif exp == na:
                ok += 1
            else:
                bad += 1
                mism[(na, exp)] += 1
    tot = ok + bad + unk
    print(f"  rows {tot}: agrees {ok} ({100.0*ok/tot:.3f}%), disagrees {bad}, "
          f"unresolvable {unk}")
    if mism:
        print(f"  disagreements (nome_area -> ISTAT province of the comune): "
              f"{mism.most_common(10)}")


if __name__ == "__main__":
    main()
