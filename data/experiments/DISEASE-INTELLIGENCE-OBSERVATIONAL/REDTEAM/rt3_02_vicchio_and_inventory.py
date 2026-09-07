#!/usr/bin/env python3
"""RT3-02  (a) The specific prior-audit claim: 30 rows where comune 48049 VICCHIO is filed
under Siena.  Searched over EVERY raw row of EVERY variable, undeduplicated.
(b) Full comune inventory per nome_area, and the name_3 / nome_area relationship.
(c) Prato-reform completeness: is any Prato-province comune filed under Firenze?
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt3_lib as L

print("=" * 78)
print("RT3-02  the VICCHIO/Siena claim, and the comune inventory")
print("=" * 78)

# ---- (a) exhaustive search, all four variables, no dedup -------------------------
total_rows = 0
hit_code = collections.Counter()      # admin_code 48049 anywhere
hit_name = collections.Counter()      # name_4 contains VICCHIO anywhere
siena_with_firenze_code = collections.Counter()
firenze_code_elsewhere = collections.Counter()
per_file_rows = collections.Counter()
for fn, r in L.rows():
    total_rows += 1
    per_file_rows[fn] += 1
    a = L.admin6(r.get("admin_code"))
    na = str(r.get("nome_area"))
    n4 = str(r.get("name_4")).strip().upper()
    if a == "048049":
        hit_code[(na, n4)] += 1
    if "VICCHIO" in n4:
        hit_name[(na, a)] += 1
    if a and a.startswith("048") and na not in ("Firenze", "Prato"):
        firenze_code_elsewhere[(na, a, n4)] += 1
    if na == "Siena" and a and not a.startswith("052"):
        siena_with_firenze_code[(a, n4)] += 1

print(f"\ntotal raw rows across the 4 variables: {total_rows:,}")
print(f"  rows with admin_code 048049          : {sum(hit_code.values()):,}  {dict(hit_code)}")
print(f"  rows with name_4 containing VICCHIO  : {sum(hit_name.values()):,}  {dict(hit_name)}")
print(f"  rows nome_area=Siena with a non-052 admin_code: "
      f"{sum(siena_with_firenze_code.values()):,}  {dict(siena_with_firenze_code)}")
print(f"  rows with a 048 code filed OUTSIDE Firenze/Prato: "
      f"{sum(firenze_code_elsewhere.values()):,}  {dict(firenze_code_elsewhere)}")

# what IS comune 048049 in this source, if present?
print("\n  what comune numbers exist in province 048 here:")
p048 = collections.Counter()
for fn, r in L.rows("1"):
    a = L.admin6(r.get("admin_code"))
    if a and a.startswith("048"):
        p048[(a, str(r.get("name_4")).strip(), str(r.get("nome_area")))] += 1
for (a, n4, na), n in sorted(p048.items()):
    print(f"    {a}  {n4:30s} nome_area={na:10s} {n:>6,} rows")

# ---- (b) name_3 vs nome_area -----------------------------------------------------
R = L.visit_rows()
N = len(R)
mism = collections.Counter()
for r in R.values():
    if str(r.get("name_3")) != str(r.get("nome_area")):
        mism[(str(r.get("nome_area")), str(r.get("name_3")))] += 1
print(f"\nname_3 != nome_area : {sum(mism.values()):,} / {N:,}   {dict(mism)}")

pair = collections.Counter((str(r.get("nome_area")), str(r.get("admin_code_3")),
                            str(r.get("id_area"))) for r in R.values())
print("\nnome_area <-> admin_code_3 <-> id_area (all three must agree 1:1):")
for (na, ac3, ia), n in sorted(pair.items()):
    print(f"  {na:16s} admin_code_3={ac3:>3s} id_area={ia:>3s}  {n:>7,}")

# ---- (c) comune inventory per province ------------------------------------------
print("\n--- comuni per nome_area, with the ISTAT province their code implies -----------")
inv = collections.defaultdict(collections.Counter)
for r in R.values():
    inv[str(r.get("nome_area"))][(L.admin6(r.get("admin_code")),
                                  str(r.get("name_4")).strip())] += 1
for na in sorted(inv):
    codes = collections.Counter(c[0][:3] for c in inv[na])
    print(f"\n  {na}: {len(inv[na])} comuni, province prefixes {dict(codes)}")
    odd = [(c, n4, n) for (c, n4), n in sorted(inv[na].items())
           if L.ISTAT_PROV.get(c[:3]) != na]
    for c, n4, n in odd:
        tag = "PRATO-REFORM legacy code" if c in L.PRATO_REFORM else "UNEXPLAINED"
        print(f"      {c} {n4:28s} {n:>6,} rows  -> ISTAT says "
              f"{L.ISTAT_PROV.get(c[:3])}   [{tag}]")

# ---- (d) is any comune code shared by two nome_area values? ---------------------
by_code = collections.defaultdict(collections.Counter)
for r in R.values():
    by_code[L.admin6(r.get("admin_code"))][str(r.get("nome_area"))] += 1
split = {c: dict(v) for c, v in by_code.items() if len(v) > 1}
print(f"\ncomune codes appearing under MORE THAN ONE nome_area: {len(split)}  {split}")

by_name4 = collections.defaultdict(collections.Counter)
for r in R.values():
    by_name4[str(r.get("name_4")).strip().upper()][L.admin6(r.get("admin_code"))] += 1
dup = {n: dict(v) for n, v in by_name4.items() if len(v) > 1}
print(f"comune NAMES carrying more than one admin_code: {len(dup)}  {dup}")
print(f"\ndistinct comuni total: {len(by_code)}")
