#!/usr/bin/env python3
"""RT1 - ACCUSATION 9/10/11.

 9. is `attiva` "infestation still alive"? measure how many LIVE individuals it leaves out.
10. does the published verdict change under the percent reading?
11. which columns does the engine read that the sheet does not describe at all?
"""
import os, sys, re, collections, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
import rt1_lib as L

CORE = ["u", "l1v", "l1m", "l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"]
ISTAT = {"045": "Massa-Carrara", "046": "Lucca", "047": "Pistoia", "048": "Firenze",
         "049": "Livorno", "050": "Pisa", "051": "Arezzo", "052": "Siena",
         "053": "Grosseto", "100": "Prato"}


def main():
    yrs = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:4])
                  for f in os.listdir(L.FETCH) if f.startswith("c2_s1_v")})
    rows = L.visit_table(years=set(yrs), with_stages=True)
    full = [r for r in rows if all(r.get(c) is not None for c in CORE)
            and r.get("attiva") is not None and r.get("dannosa") is not None]

    print("=" * 74)
    print("9. is `attiva` 'infestation still alive on the day of the visit'?")
    print("=" * 74)
    live_all = sum(r["u"] + r["l1v"] + r["l2v"] + r["l3v"] + r["pv"] for r in full)
    live_in_att = sum(r["u"] + r["l1v"] + r["l2v"] for r in full)
    live_out = sum(r["l3v"] + r["pv"] for r in full)
    print(f"  seasons {yrs}, {len(full)} visits with stages")
    print(f"  live individuals recorded (u+l1v+l2v+l3v+pv): {int(live_all)}")
    print(f"    inside attiva  (u+l1v+l2v):  {int(live_in_att)} "
          f"({100.0*live_in_att/live_all:.2f}%)")
    print(f"    OUTSIDE attiva (l3v+pv):     {int(live_out)} "
          f"({100.0*live_out/live_all:.2f}%)  -- these are alive and counted as `dannosa`")
    dan_tot = sum(r["l3v"] + r["l3m"] + r["pv"] + r["pm"] + r["fu"] for r in full)
    dan_live = sum(r["l3v"] + r["pv"] for r in full)
    print(f"  mass of `dannosa` (l3v+l3m+pv+pm+fu): {int(dan_tot)}, of which LIVE "
          f"(l3v+pv) {int(dan_live)} ({100.0*dan_live/dan_tot:.2f}%)")
    print(f"  -> the sheet says dannosa 'CANNOT_USE_FOR the current state of the pest'.")
    nz = [r for r in full if (r["l3v"] + r["pv"]) > 0]
    att0 = [r for r in nz if r["attiva"] == 0]
    print(f"  visits with live L3 or live pupae present: {len(nz)} of {len(full)}; "
          f"of those, attiva reads 0 in {len(att0)}")
    print(f"  eggs (u) are inside attiva: summed u = "
          f"{int(sum(r['u'] for r in full))} of {int(live_in_att)} of attiva's mass "
          f"({100.0*sum(r['u'] for r in full)/live_in_att:.2f}%)")
    print()

    print("=" * 74)
    print("10. does the published verdict change under the percent reading?")
    print("=" * 74)
    arch = L.visit_table()
    as_of = dt.date(2026, 9, 6)

    def pooled(rs, metric, engine=True):
        u = [r for r in rs if r["tot"] and r["tot"] > 0 and r[metric] is not None
             and 0 <= r[metric] <= r["tot"]]
        if not u:
            return None, 0
        den = sum(r["tot"] for r in u)
        if engine:
            return 100.0 * sum(r[metric] for r in u) / den, len(u)
        return sum(r[metric] * r["tot"] for r in u) / den, len(u)

    def band(p):
        if p is None:
            return "NONE"
        if p == 0:
            return "white"
        if p < 0.01:
            return "NO BAND"
        if p < 6:
            return "green"
        if p < 10:
            return "yellow"
        return "red"

    print("  matched-panel comparison, per province: this window vs the same window in each"
          "\n  prior season, on the shared groves, under each reading")
    lo, hi = as_of - dt.timedelta(days=27), as_of
    for prov in sorted({r["province"] for r in arch if r["province"]}):
        def w(d0, d1):
            a, b = d0.isoformat(), d1.isoformat()
            return [r for r in arch if r["province"] == prov and r["date"]
                    and a <= r["date"] <= b]
        cur = w(lo, hi)
        cur_sites = {r["id_field"] for r in cur}
        flips = 0
        seasons = 0
        for y in range(2006, 2026):
            try:
                l2, h2 = lo.replace(year=y), hi.replace(year=y)
            except ValueError:
                continue
            then = w(l2, h2)
            shared = cur_sites & {r["id_field"] for r in then}
            if len(shared) < 8:
                continue
            seasons += 1
            n_e, _ = pooled([r for r in cur if r["id_field"] in shared], "attiva", True)
            t_e, _ = pooled([r for r in then if r["id_field"] in shared], "attiva", True)
            n_p, _ = pooled([r for r in cur if r["id_field"] in shared], "attiva", False)
            t_p, _ = pooled([r for r in then if r["id_field"] in shared], "attiva", False)
            if None in (n_e, t_e, n_p, t_p):
                continue
            if (n_e > t_e) != (n_p > t_p):
                flips += 1
        pe, ne = pooled(cur, "attiva", True)
        pp, _ = pooled(cur, "attiva", False)
        print(f"  {prov:14s} engine {pe if pe is None else round(pe,4)}% "
              f"[{band(pe)}]  percent-reading "
              f"{pp if pp is None else round(pp,4)}% [{band(pp)}]  "
              f"matched seasons {seasons}, direction flips {flips}")
    print()

    print("=" * 74)
    print("11. columns the engine reads that the sheet does not describe")
    print("=" * 74)
    core_src = open(os.path.join(HERE, "..", "engine", "di_core.py"), encoding="utf-8").read()
    read = sorted(set(re.findall(r'any_row\.get\("([^"]+)"\)', core_src)) |
                  set(re.findall(r'r\.get\("([^"]+)"\)', core_src)))
    sheet_txt = open(os.path.join(HERE, "..", "S1-SEMANTICS",
                                  "SOURCE-SEMANTIC-SHEET.json"), encoding="utf-8").read()
    for c in read:
        print(f"  reads row column {c!r:14s} -> appears in the semantic sheet: "
              f"{'YES' if c in sheet_txt else 'NO'}")
    print()
    print("  is `nome_area` really the province? cross-check against the ISTAT comune code")
    bad = collections.Counter()
    n_ok = n_bad = n_unk = 0
    for r in arch:
        code = r.get("comune") and None
        ac = r.get("province"), r.get("comune")
        pass
    arch2 = L.visit_table()
    for r in arch2:
        adm = None
        # admin_code is on the raw row; re-read it
        break
    # re-read admin_code directly
    import json, glob
    for fn in sorted(glob.glob(os.path.join(L.CASE, "RAW", "*_v1_*.json"))):
        for row in json.load(open(fn, encoding="utf-8")):
            ac, na = row.get("admin_code"), row.get("nome_area")
            if ac is None or na is None:
                n_unk += 1
                continue
            pref = str(ac).zfill(5)[:3]
            exp = ISTAT.get(pref)
            if exp is None:
                n_unk += 1
            elif exp == na:
                n_ok += 1
            else:
                n_bad += 1
                bad[(na, exp)] += 1
    tot = n_ok + n_bad + n_unk
    print(f"    rows checked {tot}: nome_area agrees with the comune's ISTAT province in "
          f"{n_ok} ({100.0*n_ok/tot:.3f}%), disagrees in {n_bad}, "
          f"code not resolvable in {n_unk}")
    if bad:
        print(f"    disagreements (nome_area -> ISTAT province): {bad.most_common(10)}")


if __name__ == "__main__":
    main()
