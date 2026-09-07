#!/usr/bin/env python3
"""RT3-01  Cross-examine nome_area (the string the engine groups by) against admin_code
(the ISTAT comune code, whose first three digits ARE the province).

Also checks that the four collected variables agree with each other on geography.
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt3_lib as L

print("=" * 78)
print("RT3-01  nome_area vs admin_code")
print("=" * 78)

# --- do the four variables agree on geography for the same visit key? -------------
geo_keys = ["nome_area", "admin_code", "name_4", "name_3", "admin_code_3",
            "lat", "lon", "org_name", "id_org", "name_5"]
per_var = {}
for v in L.VARS:
    d = {}
    for fn, r in L.rows(v):
        k = (r.get("id_field"), r.get("date"))
        if None in k:
            continue
        d[k] = tuple(str(r.get(g)) for g in geo_keys)
    per_var[v] = d
base = per_var["1"]
print(f"\nvisit keys in v1: {len(base):,}")
for v in L.VARS[1:]:
    d = per_var[v]
    common = set(base) & set(d)
    diff = sum(1 for k in common if base[k] != d[k])
    print(f"  v{v:>6}: {len(d):,} keys, {len(common):,} shared with v1, "
          f"{diff:,} disagree on {geo_keys}")

R = L.visit_rows()
N = len(R)
print(f"\nvisit rows (id_field,date) from v1: {N:,}")

# --- agreement -------------------------------------------------------------------
agree = 0
no_code = 0
disagree = collections.Counter()
disagree_rows = collections.defaultdict(list)
prov_missing = collections.Counter()
for k, r in R.items():
    na = r.get("nome_area")
    p = L.prov_of_admin(r.get("admin_code"))
    if p is None:
        no_code += 1
        continue
    expect = L.ISTAT_PROV.get(p)
    if expect is None:
        prov_missing[p] += 1
        continue
    if expect == na:
        agree += 1
    else:
        cell = (na, p, expect, L.admin6(r.get("admin_code")), str(r.get("name_4")).strip())
        disagree[cell] += 1
        disagree_rows[cell].append((k, r))

print(f"\nadmin_code present            {N - no_code:,} / {N:,}")
print(f"admin_code missing/blank      {no_code:,} / {N:,}")
print(f"province prefix not Tuscan    {sum(prov_missing.values()):,} / {N:,}  {dict(prov_missing)}")
print(f"nome_area AGREES with ISTAT   {agree:,} / {N:,}")
print(f"nome_area DISAGREES           {sum(disagree.values()):,} / {N:,}")

print("\n--- every disagreement class -------------------------------------------------")
print(f"{'nome_area':14s} {'code':>7} {'ISTAT prov':14s} {'comune':28s} {'rows':>6}  verdict")
tot_reform = tot_genuine = 0
for (na, p, expect, code, name4), n in sorted(disagree.items(), key=lambda x: -x[1]):
    if code in L.PRATO_REFORM and na == "Prato":
        verdict = "1992 PRATO REFORM (legacy 048 code, correctly filed under Prato)"
        tot_reform += n
    elif code in L.PRATO_REFORM:
        verdict = f"PRATO-REFORM COMUNE but filed under {na} -- CHECK"
        tot_genuine += n
    else:
        verdict = f"GENUINE MISLABEL: {name4} is a comune of {expect}, filed under {na}"
        tot_genuine += n
    print(f"{na:14s} {code:>7} {expect:14s} {name4[:28]:28s} {n:>6}  {verdict}")

print(f"\n1992 Prato reform rows        {tot_reform:,} / {N:,}")
print(f"genuine mislabelled rows      {tot_genuine:,} / {N:,}")

# --- detail on the genuine ones --------------------------------------------------
print("\n--- genuine mislabels, detail -----------------------------------------------")
out = []
for (na, p, expect, code, name4), rws in sorted(disagree_rows.items()):
    if code in L.PRATO_REFORM and na == "Prato":
        continue
    seasons = collections.Counter(str(r.get("date"))[:4] for _, r in rws)
    fields = sorted({r.get("id_field") for _, r in rws})
    orgs = sorted({str(r.get("org_name")) for _, r in rws})
    idorgs = sorted({str(r.get("id_org")) for _, r in rws})
    name3 = sorted({str(r.get("name_3")) for _, r in rws})
    ac3 = sorted({str(r.get("admin_code_3")) for _, r in rws})
    name5 = sorted({str(r.get("name_5")) for _, r in rws})
    dates = sorted(str(r.get("date")) for _, r in rws)
    print(f"\n  nome_area={na!r}  admin_code={code} ({name4}) -> really {expect}")
    print(f"    rows {len(rws)}   seasons {dict(sorted(seasons.items()))}")
    print(f"    id_field {fields}")
    print(f"    org_name {orgs}   id_org {idorgs}")
    print(f"    name_3 {name3}   admin_code_3 {ac3}   name_5 {name5}")
    print(f"    dates {dates[0]} .. {dates[-1]}")
    lat = sorted({(str(r.get('lat'))[:8], str(r.get('lon'))[:8]) for _, r in rws})
    print(f"    lat/lon {lat}")
    out.append({"nome_area": na, "admin_code": code, "comune": name4,
                "istat_province": expect, "rows": len(rws),
                "id_fields": fields, "orgs": orgs,
                "dates": [dates[0], dates[-1]],
                "seasons": dict(sorted(seasons.items()))})

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "rt3_01_mislabels.json"), "w", encoding="utf-8"),
          indent=1, default=str)

# --- what nome_area values exist at all ------------------------------------------
print("\n--- nome_area values present -------------------------------------------------")
for na, n in sorted(collections.Counter(str(r.get("nome_area")) for r in R.values()).items()):
    print(f"  {na:16s} {n:>7,}")
print("\n--- name_3 / admin_code_3 (the OTHER area fields) ----------------------------")
print("  name_3 values:", sorted({str(r.get('name_3')) for r in R.values()}))
print("  admin_code_3 values:", sorted({str(r.get('admin_code_3')) for r in R.values()}))
print("  id_area values:", sorted({str(r.get('id_area')) for r in R.values()}))
