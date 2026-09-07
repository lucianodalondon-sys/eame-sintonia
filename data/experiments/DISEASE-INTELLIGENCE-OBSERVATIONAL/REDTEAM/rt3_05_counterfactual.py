#!/usr/bin/env python3
"""RT3-05  Does any of the geography reach a published number?

Runs the REAL engine (di_core + di_observe + di_render) over rewritten inputs and diffs
every published field against the baseline.

  BASELINE   the shipped run
  NOGEO      lat, lon, admin_code, admin_code_3, name_3, name_4, name_5 deleted from every
             raw row on disk, and the engine re-run through di_core. If the output is
             byte-identical, the engine demonstrably reads none of them.
  ISTAT      province taken from admin_code instead of nome_area - the "obvious" geographic
             fix an auditor would apply. Shows what correcting the 1,401 Prato-reform rows
             would do.
  INJECT     one province's label rewritten to another, to see whether a wrong attribution
             is caught anywhere or simply published.
  BLANK      one province's nome_area blanked, to see whether the province vanishes without
             a trace in the output.

Usage: py rt3_05_counterfactual.py
"""
import os, sys, json, glob, shutil, copy, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENG)
sys.path.insert(0, HERE)
import rt3_lib as L
import di_core, di_observe, di_render, di_adama

AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
SHADOW = os.path.join(HERE, "_shadow")

FIELDS = ["province", "observation.value_pct", "observation.n_visits",
          "observation.n_sites", "observation.drupes_sampled",
          "observation.infested_drupes", "observation.n_orgs",
          "analysis.historical_state", "analysis.historical_state_unmatched",
          "analysis.matched_panel_seasons", "analysis.baseline_n",
          "analysis.baseline_rate_pct_median", "analysis.observed_trend",
          "quality.observation_publishable", "quality.historical_comparison_publishable",
          "attention.attention_class"]


def dig(c, path):
    x = c
    for p in path.split("."):
        if not isinstance(x, dict):
            return None
        x = x.get(p)
    return x


def summarise(cells):
    return {c["province"]: {f: dig(c, f) for f in FIELDS} for c in cells}


def run_cells(visits, sheet, adama):
    provs = sorted({v["province"] for v in visits if v["province"]})
    cells = []
    for p in provs:
        c = di_observe.cell(visits, sheet, p, METRIC, AS_OF)
        c["adama"] = adama
        c["attention"] = di_adama.attention_class(c, adama)
        cells.append(c)
    return cells


def diff(base, other, label):
    print(f"\n{'='*78}\n{label}\n{'='*78}")
    bp, op = set(base), set(other)
    if bp - op:
        print(f"  PROVINCES THAT DISAPPEARED: {sorted(bp-op)}")
    if op - bp:
        print(f"  PROVINCES THAT APPEARED   : {sorted(op-bp)}")
    same = True
    for p in sorted(bp & op):
        for f in FIELDS:
            a, b = base[p][f], other[p][f]
            if a != b:
                same = False
                print(f"  {p:15s} {f:48s} {a!r} -> {b!r}")
    if same and not (bp ^ op):
        print("  IDENTICAL on every published field.")
    return same and not (bp ^ op)


# ---------------------------------------------------------------- baseline
sheet = di_core.load_sheet()
adama = di_adama.relevance("Olive", "Olive Fruit Fly")
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)
base_cells = run_cells(loaded["visits"], sheet, adama)
BASE = summarise(base_cells)
print("BASELINE")
for p, d in BASE.items():
    print(f"  {p:15s} {str(d['observation.value_pct']):>8} "
          f"n_vis={d['observation.n_visits']:>4} sites={d['observation.n_sites']:>4} "
          f"drupes={d['observation.drupes_sampled']:>7} "
          f"hist={d['analysis.historical_state']:>18} "
          f"matched={d['analysis.matched_panel_seasons']:>3} "
          f"att={d['attention.attention_class']}")
base_region = di_render.render_region(base_cells, adama)

# ---------------------------------------------------------------- NOGEO on disk
STRIP = ["lat", "lon", "admin_code", "admin_code_3", "name_3", "name_4", "name_5",
         "id_area", "cultivar", "name"]
sd = os.path.join(SHADOW, "NOGEO")
if os.path.exists(sd):
    shutil.rmtree(sd)
os.makedirs(os.path.join(sd, "RAW"))
n_stripped = 0
for fn in sorted(glob.glob(os.path.join(L.RAW, "*.json"))):
    rows = json.load(open(fn, encoding="utf-8"))
    for r in rows:
        for k in STRIP:
            if k in r:
                del r[k]
                n_stripped += 1
    json.dump(rows, open(os.path.join(sd, "RAW", os.path.basename(fn)), "w",
                         encoding="utf-8"))
print(f"\nNOGEO: {n_stripped:,} geographic values deleted from disk across "
      f"{len(glob.glob(os.path.join(sd,'RAW','*.json')))} files")
nogeo_loaded = di_core.load_visits(sd, sheet, AS_OF)
nogeo_cells = run_cells(nogeo_loaded["visits"], sheet, adama)
ok = diff(BASE, summarise(nogeo_cells), "NOGEO - lat/lon/admin_code/name_3/name_4/name_5 "
                                        "physically deleted, engine re-run")
print(f"\n  visits loaded: baseline {loaded['n_visits']:,}  nogeo "
      f"{nogeo_loaded['n_visits']:,}")
print(f"  rendered region report identical: "
      f"{di_render.render_region(nogeo_cells, adama) == base_region}")

# ---------------------------------------------------------------- ISTAT province
istat = copy.deepcopy(loaded["visits"])
moved = 0
raw = L.visit_rows()
for v in istat:
    r = raw.get((v["visit_key"]["id_field"], v["visit_key"]["date"]))
    if r is None:
        continue
    p = L.ISTAT_PROV.get(L.prov_of_admin(r.get("admin_code")))
    if p and p != v["province"]:
        moved += 1
    if p:
        v["province"] = p
print(f"\nISTAT: {moved:,} of {len(istat):,} visits re-attributed from admin_code")
diff(BASE, summarise(run_cells(istat, sheet, adama)),
     "ISTAT - province taken from admin_code (the naive geographic 'fix')")

# ---------------------------------------------------------------- INJECT
inj = copy.deepcopy(loaded["visits"])
n = 0
for v in inj:
    if v["province"] == "Siena" and dt.date.fromisoformat(v["observation_date"]) >= \
            dt.date(2026, 8, 10):
        v["province"] = "Prato"
        n += 1
print(f"\nINJECT: {n:,} Siena visits in the current window relabelled 'Prato'")
inj_cells = run_cells(inj, sheet, adama)
diff(BASE, summarise(inj_cells), "INJECT - current-window Siena observations filed as Prato")
print("\n  --- what the reader is shown for Prato after the injection ---")
pc = next(c for c in inj_cells if c["province"] == "Prato")
print(di_render.render_province(pc, adama, pc["attention"]))

# ---------------------------------------------------------------- BLANK
bl = copy.deepcopy(loaded["visits"])
n = 0
for v in bl:
    if v["province"] == "Lucca":
        v["province"] = ""
        n += 1
print(f"\n\nBLANK: {n:,} Lucca visits given an empty province")
bl_cells = run_cells(bl, sheet, adama)
diff(BASE, summarise(bl_cells), "BLANK - Lucca's province label emptied")
print("\n  --- the regional report the reader sees ---")
print(di_render.render_region(bl_cells, adama))
