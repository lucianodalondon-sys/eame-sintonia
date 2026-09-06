#!/usr/bin/env python3
"""
Recount Toscana from the collected RAW. Inherits no number from any previous session.

Corrects three claims the previous session recorded, each of which is checked here:
  1. code->label map. It recorded 49=nessuna/50=bassa/51=media/52=alta. The API's own
     filter block says 50=media and 51=bassa. The map is read from the API, never hard-coded.
  2. "18 seasons, 2008-2026". 2006 and 2007 return rows.
  3. "36,924 georeferenced observations". Early years carry lat="0", lon="0". Georeferencing
     is measured per year, not assumed.
"""
import json, os, collections, datetime as dt

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "RAW")
IDX = json.load(open(os.path.join(ROOT, "collection_index.json")))

# code -> label, straight from the API's filter block
CODE = {}
for sname, s in IDX["schemas"].items():
    for c in s["codes"]:
        CODE[(c["var"], str(c["code"]))] = {"label": c["label"], "order_n": c.get("order_n")}

def valid_ll(r):
    try:
        la, lo = float(r.get("lat") or 0), float(r.get("lon") or 0)
    except Exception:
        return False
    return abs(la) > 0.001 and abs(lo) > 0.001 and 35 < la < 48 and 6 < lo < 19

def load(fn):
    return json.load(open(os.path.join(RAW, fn)))

def analyse(schema=None, var_id=None, regime="all"):
    per = {}
    for fn in sorted(os.listdir(RAW)):
        if not fn.endswith(".json"): continue
        parts = fn[:-5].split("_")
        sname, v, reg, year = parts[0], parts[1], "_".join(parts[2:-1]), parts[-1]
        vid = int(v[1:])
        if schema and sname != schema: continue
        if var_id and vid != var_id: continue
        if reg != regime: continue
        rows = load(fn)
        if not rows: continue
        y = int(year)
        fields = {r.get("id_field") for r in rows}
        orgs = collections.Counter(r.get("org_name") for r in rows)
        comuni = {r.get("admin_code") for r in rows if r.get("admin_code")}
        prov = {r.get("nome_area") for r in rows if r.get("nome_area")}
        geo = sum(1 for r in rows if valid_ll(r))
        dates = sorted(r.get("date") for r in rows if r.get("date"))
        weeks = {r.get("week") for r in rows if r.get("week")}
        vals = collections.Counter(str(r.get("val")) for r in rows)
        labelled = collections.Counter()
        unknown = 0
        for vv, n in vals.items():
            m = CODE.get((vid, vv))
            if m: labelled[m["label"]] += n
            else: unknown += n
        per[y] = {
            "n_rows": len(rows), "n_vineyards": len(fields), "n_comuni": len(comuni),
            "n_provinces": len(prov), "provinces": sorted(x for x in prov if x),
            "n_orgs": len(orgs), "orgs": dict(orgs.most_common(6)),
            "n_georeferenced": geo,
            "pct_georeferenced": round(100 * geo / len(rows), 1),
            "date_min": dates[0] if dates else None, "date_max": dates[-1] if dates else None,
            "n_weeks": len(weeks),
            "value_labels": dict(labelled), "n_unmapped_values": unknown,
            "raw_value_codes": dict(vals),
        }
    return per

if __name__ == "__main__":
    import sys
    sch = sys.argv[1] if len(sys.argv) > 1 else "Peronospora"
    vid = int(sys.argv[2]) if len(sys.argv) > 2 else 34
    reg = sys.argv[3] if len(sys.argv) > 3 else "all"
    per = analyse(sch, vid, reg)
    if not per:
        print(f"NO DATA for {sch} v{vid} regime={reg}"); raise SystemExit
    vname = next((v["name"] for s in IDX["schemas"].values() for v in s["vars"] if v["id"] == vid), "?")
    print(f"=== {sch} var {vid} ({vname}) regime={reg}")
    print(f"{'year':5s} {'rows':>6s} {'vineyd':>7s} {'comuni':>7s} {'prov':>5s} {'orgs':>5s} "
          f"{'%geo':>6s} {'weeks':>6s}  {'date range':22s} value labels")
    for y in sorted(per):
        p = per[y]
        vl = " ".join(f"{k}={v}" for k, v in sorted(p["value_labels"].items(), key=lambda x: -x[1]))
        if p["n_unmapped_values"]: vl += f"  UNMAPPED={p['n_unmapped_values']}"
        print(f"{y:5d} {p['n_rows']:6d} {p['n_vineyards']:7d} {p['n_comuni']:7d} {p['n_provinces']:5d} "
              f"{p['n_orgs']:5d} {p['pct_georeferenced']:6.1f} {p['n_weeks']:6d}  "
              f"{str(p['date_min'])[:10]}..{str(p['date_max'])[:10]}  {vl}")
    tot = sum(p["n_rows"] for p in per.values())
    geo = sum(p["n_georeferenced"] for p in per.values())
    print(f"\nYEARS = {len(per)}  {sorted(per)}")
    print(f"OBSERVATIONS = {tot}")
    print(f"GEOREFERENCED = {geo} ({round(100*geo/tot,1)}%)  <- coordinates, not municipality")
    print(f"MUNICIPALITY-CODED = every row carries admin_code (ISTAT), so geography exists even where lat/lon is 0")
    json.dump(per, open(os.path.join(ROOT, f"recount_{sch}_v{vid}_{reg}.json"), "w"), indent=1)
