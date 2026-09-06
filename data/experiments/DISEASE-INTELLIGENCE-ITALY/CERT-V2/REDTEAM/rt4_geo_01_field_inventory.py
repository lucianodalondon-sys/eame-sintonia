#!/usr/bin/env python3
"""RT4 / GEOGRAPHY probe 1 — what geographic fields actually exist, and do they agree?

No engine imports. Reads RAW json only. Counts with denominators, nothing else.
"""
import json, glob, os, collections, sys

CASES = {
    "OLIVO-BACTROCERA-TOSCANA": ("c2_s1_v-1002_*.json", -1002),
    "VITE-OIDIO-TOSCANA": ("c3_s8_v39_*.json", 39),
    "FRUMENTO-SEPTORIA-TOSCANA": ("c19_s74_v372_*.json", 372),
}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "CASES")


def load(case, pat):
    rows = []
    for fn in sorted(glob.glob(os.path.join(ROOT, case, "RAW", pat))):
        for r in json.load(open(fn)):
            r["_file"] = os.path.basename(fn)
            rows.append(r)
    return rows


def main():
    out = {}
    for case, (pat, var) in CASES.items():
        rows = load(case, pat)
        n = len(rows)
        c = {}
        # 1. how populated is every geographic field?
        for f in ("nome_area", "name_3", "name_4", "name_5", "admin_code", "admin_code_3",
                  "id_area", "org_name", "id_org", "uid", "lat", "lon", "cultivar", "name"):
            nonnull = sum(1 for r in rows if r.get(f) not in (None, "", "0"))
            c[f] = {"NON_EMPTY": nonnull, "OF": n,
                    "PCT": round(100.0 * nonnull / n, 2) if n else None,
                    "N_DISTINCT": len({r.get(f) for r in rows})}
        # 2. does nome_area ever differ from name_3?
        diff = [r for r in rows if r.get("nome_area") != r.get("name_3")]
        c["_nome_area_vs_name_3"] = {"DISAGREE": len(diff), "OF": n,
                                     "EXAMPLES": [(r.get("nome_area"), r.get("name_3"))
                                                  for r in diff[:5]]}
        # 3. distinct nome_area values, with row counts
        c["_nome_area_values"] = dict(sorted(collections.Counter(
            r.get("nome_area") for r in rows).items(), key=lambda kv: -kv[1]))
        # 4. id_area <-> nome_area is it 1:1?
        m = collections.defaultdict(set)
        for r in rows:
            m[r.get("id_area")].add(r.get("nome_area"))
        c["_id_area_to_nome_area"] = {str(k): sorted(str(x) for x in v) for k, v in sorted(
            m.items(), key=lambda kv: (kv[0] is None, kv[0]))}
        # 5. does one id_field ever carry more than one nome_area / admin_code / lat-lon?
        f2p, f2a, f2ll = (collections.defaultdict(set) for _ in range(3))
        for r in rows:
            f2p[r.get("id_field")].add(r.get("nome_area"))
            f2a[r.get("id_field")].add(r.get("admin_code"))
            f2ll[r.get("id_field")].add((r.get("lat"), r.get("lon")))
        c["_id_field"] = {
            "N_FIELDS": len(f2p),
            "FIELDS_WITH_2PLUS_PROVINCES": sum(1 for v in f2p.values() if len(v) > 1),
            "FIELDS_WITH_2PLUS_ADMIN_CODES": sum(1 for v in f2a.values() if len(v) > 1),
            "FIELDS_WITH_2PLUS_LATLON": sum(1 for v in f2ll.values() if len(v) > 1),
            "EXAMPLES_MULTI_PROV": [(k, sorted(str(x) for x in v))
                                    for k, v in f2p.items() if len(v) > 1][:10],
            "EXAMPLES_MULTI_LATLON": [(k, sorted(str(x) for x in v))
                                      for k, v in f2ll.items() if len(v) > 1][:10],
        }
        out[case] = {"N_ROWS": n, "N_FILES": len({r["_file"] for r in rows}), "FIELDS": c}
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "rt4_geo_01_field_inventory.json"), "w"),
              indent=1, ensure_ascii=False, default=str)
    for case, v in out.items():
        print("=" * 70)
        print(case, "N_ROWS", v["N_ROWS"], "N_FILES", v["N_FILES"])
        for f, s in v["FIELDS"].items():
            if f.startswith("_"):
                continue
            print(f"   {f:14s} non_empty {s['NON_EMPTY']:7d}/{s['OF']:<7d} "
                  f"={str(s['PCT']):>6s}%  distinct={s['N_DISTINCT']}")
        print("   nome_area vs name_3 disagree:", v["FIELDS"]["_nome_area_vs_name_3"]["DISAGREE"],
              "/", v["N_ROWS"], v["FIELDS"]["_nome_area_vs_name_3"]["EXAMPLES"])
        print("   nome_area values:", v["FIELDS"]["_nome_area_values"])
        print("   id_area->nome_area:", v["FIELDS"]["_id_area_to_nome_area"])
        idf = v["FIELDS"]["_id_field"]
        print(f"   id_field: {idf['N_FIELDS']} fields; "
              f"multi-province {idf['FIELDS_WITH_2PLUS_PROVINCES']}, "
              f"multi-admin_code {idf['FIELDS_WITH_2PLUS_ADMIN_CODES']}, "
              f"multi-latlon {idf['FIELDS_WITH_2PLUS_LATLON']}")
        print("     multi-prov ex:", idf["EXAMPLES_MULTI_PROV"][:5])
        print("     multi-latlon ex:", idf["EXAMPLES_MULTI_LATLON"][:3])


if __name__ == "__main__":
    main()
