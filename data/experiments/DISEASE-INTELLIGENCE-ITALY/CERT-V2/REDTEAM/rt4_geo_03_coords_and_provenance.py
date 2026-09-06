#!/usr/bin/env python3
"""RT4 / GEOGRAPHY probe 3 — coordinates, and WHOSE province nome_area is.

Three questions:
  A. how many rows sit outside Toscana? are any lat/lon transposed?
  B. does any id_field move position between seasons?
  C. is nome_area the province of the FIELD, of the ORG, or of the SUB-AREA (name_5)?
     tested by asking whether nome_area is a function of each candidate.
"""
import json, glob, os, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "CASES")
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = {"OLIVO-BACTROCERA-TOSCANA": "c2_s1_v-1002_*.json",
         "VITE-OIDIO-TOSCANA": "c3_s8_v39_*.json",
         "FRUMENTO-SEPTORIA-TOSCANA": "c19_s74_v372_*.json"}

# Toscana bounding box, generous (region extremes incl. Arcipelago Toscano)
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 42.20, 44.50, 9.60, 12.40


def load_all():
    rows = []
    for case, pat in CASES.items():
        for fn in sorted(glob.glob(os.path.join(ROOT, case, "RAW", pat))):
            for r in json.load(open(fn)):
                r["_case"] = case
                rows.append(r)
    return rows


def ll(r):
    try:
        return float(r.get("lat")), float(r.get("lon"))
    except (TypeError, ValueError):
        return None, None


def main():
    rows = load_all()
    N = len(rows)
    res = {"N_ROWS": N}

    # ---------- A. coordinates ----------
    zero = unparse = inside = outside = 0
    out_rows, transposed = [], []
    for r in rows:
        la, lo = ll(r)
        if la is None:
            unparse += 1
            continue
        if abs(la) < 0.001 and abs(lo) < 0.001:
            zero += 1
            continue
        if LAT_MIN <= la <= LAT_MAX and LON_MIN <= lo <= LON_MAX:
            inside += 1
            continue
        outside += 1
        out_rows.append(r)
        # transposition test: does swapping put it inside, or is lat<lon (impossible in Toscana)?
        swap_inside = LAT_MIN <= lo <= LAT_MAX and LON_MIN <= la <= LON_MAX
        transposed.append({"case": r["_case"], "id_field": r.get("id_field"),
                           "date": r.get("date"), "nome_area": r.get("nome_area"),
                           "name_4": r.get("name_4"), "admin_code": r.get("admin_code"),
                           "lat": r.get("lat"), "lon": r.get("lon"),
                           "SWAP_PUTS_IT_IN_TOSCANA": swap_inside,
                           "LAT_LT_LON": la < lo})
    res["COORDINATES"] = {
        "N_ROWS": N, "PARSEABLE_NONZERO_INSIDE_TOSCANA": inside,
        "PARSEABLE_NONZERO_OUTSIDE_TOSCANA": outside,
        "ZERO_ZERO (no georeference at all)": zero,
        "UNPARSEABLE_OR_NULL": unparse,
        "PCT_OUTSIDE_OF_GEOREFERENCED": round(100.0 * outside / max(inside + outside, 1), 4),
        "OUTSIDE_BY_CASE": dict(collections.Counter(r["_case"] for r in out_rows)),
        "OUTSIDE_BY_PROVINCE_LABEL": dict(collections.Counter(r.get("nome_area") for r in out_rows)),
        "OUTSIDE_DISTINCT_FIELDS": sorted({r.get("id_field") for r in out_rows}),
        "OUTSIDE_DISTINCT_POINTS": sorted({f"{r.get('lat')},{r.get('lon')}" for r in out_rows}),
        "OUTSIDE_YEARS": dict(collections.Counter(r.get("date", "")[:4] for r in out_rows)),
        "N_SWAP_WOULD_FIX": sum(1 for t in transposed if t["SWAP_PUTS_IT_IN_TOSCANA"]),
        "N_LAT_LESS_THAN_LON (impossible in Toscana)": sum(1 for t in transposed if t["LAT_LT_LON"]),
        "SAMPLE": transposed[:12],
    }

    # ---------- B. does an id_field move? ----------
    f2pt = collections.defaultdict(set)
    f2yearpt = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        la, lo = ll(r)
        if la is None or (abs(la) < 0.001 and abs(lo) < 0.001):
            continue
        f2pt[(r["_case"], r.get("id_field"))].add((round(la, 6), round(lo, 6)))
        f2yearpt[(r["_case"], r.get("id_field"))][r.get("date", "")[:4]].add((round(la, 6), round(lo, 6)))

    def km(p, q):
        return ((p[0] - q[0]) ** 2 + ((p[1] - q[1]) * 0.73) ** 2) ** 0.5 * 111.0

    movers = []
    for k, pts in f2pt.items():
        if len(pts) < 2:
            continue
        pl = sorted(pts)
        d = max(km(a, b) for i, a in enumerate(pl) for b in pl[i + 1:])
        yrs = {y: sorted(v) for y, v in f2yearpt[k].items()}
        movers.append({"case": k[0], "id_field": k[1], "N_POSITIONS": len(pts),
                       "MAX_SEPARATION_KM": round(d, 3),
                       "CROSSES_SEASONS": len(yrs) > 1 and any(
                           len(set(map(tuple, yrs[a]))) and set(map(tuple, yrs[a])) !=
                           set(map(tuple, yrs[b])) for a in yrs for b in yrs if a != b),
                       "BY_YEAR": {y: [f"{a},{b}" for a, b in v] for y, v in sorted(yrs.items())}})
    movers.sort(key=lambda m: -m["MAX_SEPARATION_KM"])
    res["FIELD_MOVEMENT"] = {
        "N_FIELDS_GEOREFERENCED": len(f2pt),
        "N_FIELDS_WITH_2PLUS_POSITIONS": len(movers),
        "N_MOVED_OVER_1KM": sum(1 for m in movers if m["MAX_SEPARATION_KM"] > 1),
        "N_MOVED_OVER_10KM": sum(1 for m in movers if m["MAX_SEPARATION_KM"] > 10),
        "N_MOVED_OVER_100KM": sum(1 for m in movers if m["MAX_SEPARATION_KM"] > 100),
        "N_MOVED_ACROSS_SEASONS": sum(1 for m in movers if m["CROSSES_SEASONS"]),
        "TOP_20": movers[:20],
    }

    # ---------- C. whose province is nome_area? ----------
    def functional(keyf, name):
        m = collections.defaultdict(set)
        for r in rows:
            m[keyf(r)].add(r.get("nome_area"))
        multi = {str(k): sorted(str(x) for x in v) for k, v in m.items() if len(v) > 1}
        return {"CANDIDATE": name, "N_DISTINCT_KEYS": len(m),
                "N_KEYS_MAPPING_TO_2PLUS_PROVINCES": len(multi),
                "IS_NOME_AREA_A_FUNCTION_OF_THIS": len(multi) == 0,
                "EXAMPLES": dict(list(multi.items())[:8])}

    res["WHOSE_PROVINCE"] = {
        "by_admin_code_comune": functional(lambda r: r.get("admin_code"), "admin_code (comune)"),
        "by_name_5_subarea": functional(lambda r: r.get("name_5"), "name_5 (sub-area)"),
        "by_org_name": functional(lambda r: r.get("org_name"), "org_name"),
        "by_id_field": functional(lambda r: (r["_case"], r.get("id_field")), "id_field"),
        "by_name_3": functional(lambda r: r.get("name_3"), "name_3"),
    }
    # org -> provinces spread (is an org confined to one province?)
    o2p = collections.defaultdict(collections.Counter)
    for r in rows:
        if r.get("org_name"):
            o2p[r["org_name"]][r.get("nome_area")] += 1
    res["ORG_SPREAD"] = {o: dict(c) for o, c in sorted(o2p.items(), key=lambda kv: -sum(kv[1].values()))}
    res["ORG_NULL_ROWS"] = sum(1 for r in rows if not r.get("org_name"))

    json.dump(res, open(os.path.join(HERE, "rt4_geo_03_coords_and_provenance.json"), "w"),
              indent=1, ensure_ascii=False, default=str)

    C = res["COORDINATES"]
    print("A. COORDINATES")
    for k, v in C.items():
        if k in ("SAMPLE",):
            continue
        print(f"   {k}: {v}")
    print("   sample outside rows:")
    for s in C["SAMPLE"]:
        print("     ", s)
    F = res["FIELD_MOVEMENT"]
    print("\nB. FIELD MOVEMENT")
    for k, v in F.items():
        if k != "TOP_20":
            print(f"   {k}: {v}")
    for m in F["TOP_20"][:10]:
        print(f"     {m['case'][:12]:12s} field {m['id_field']} n_pos={m['N_POSITIONS']} "
              f"max_sep={m['MAX_SEPARATION_KM']}km by_year={m['BY_YEAR']}")
    print("\nC. WHOSE PROVINCE IS nome_area?")
    for k, v in res["WHOSE_PROVINCE"].items():
        print(f"   {v['CANDIDATE']:22s} keys={v['N_DISTINCT_KEYS']:5d} "
              f"keys->2+ provinces={v['N_KEYS_MAPPING_TO_2PLUS_PROVINCES']:4d}  "
              f"function? {v['IS_NOME_AREA_A_FUNCTION_OF_THIS']}  {v['EXAMPLES']}")
    print("\n   ORG -> provinces (org_name null on", res["ORG_NULL_ROWS"], "rows):")
    for o, c in list(res["ORG_SPREAD"].items()):
        print(f"     {o:28s} {len(c):2d} provinces  {c}")


if __name__ == "__main__":
    main()
