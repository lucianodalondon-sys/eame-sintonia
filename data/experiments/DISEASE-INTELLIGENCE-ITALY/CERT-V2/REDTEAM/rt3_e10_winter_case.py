#!/usr/bin/env python3
"""RT3-E10. The year-boundary defect made REACHABLE.

RT3-E2 showed the baseline window becomes a negative-length interval whenever the current
window crosses 31 December, and that the three shipped archives cannot reach it because they
hold 7 December-or-January rows out of 392,951. Gate I certifies that the pipeline
GENERALIZES. So: build a synthetic case that is winter-active (an over-wintering pest, a
winter cereal -- the ordinary Mediterranean case), feed it to the UNMODIFIED shipped engine,
and measure what it publishes.

The synthetic archive is deliberately BORING: identical sampling every season, a stable
incidence, no trend. Any province that fails to publish is failing on the calendar, not on
the data.

Nothing outside REDTEAM/_winter/ is written.
"""
import sys, os, json, shutil, hashlib, random, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
sys.path.insert(0, CAS)
import current_pressure as cp

W = os.path.join(HERE, "_winter")
CROP, SCHEMA, VAR = 99, 99, 900
PROVS = ["Arezzo", "Firenze", "Grosseto", "Livorno", "Lucca",
         "Massa-Carrara", "Pisa", "Pistoia", "Prato", "Siena"]
YEARS = list(range(2006, 2027))
SITES_PER_PROV = 12
CODES = [{"id_survey_var": VAR, "id_survey_code": 9001, "name": "Nessuna"},
         {"id_survey_var": VAR, "id_survey_code": 9002, "name": "Bassa"},
         {"id_survey_var": VAR, "id_survey_code": 9003, "name": "Media"},
         {"id_survey_var": VAR, "id_survey_code": 9004, "name": "Alta"}]
VARS = [{"id_survey_var": VAR, "id_survey_schema": SCHEMA, "name": "presenza",
         "widget": "select"}]

shutil.rmtree(W, ignore_errors=True)
os.makedirs(os.path.join(W, "RAW"))
rng = random.Random(20260906)

idx = {"api": "SYNTHETIC-REDTEAM-WINTER", "crop": CROP, "schema": SCHEMA,
       "requests": [], "codes": CODES, "vars": VARS}

# every season: a visit to every site every 7 days, ALL YEAR ROUND, incidence ~0.33 constant
for y in YEARS:
    rows = []
    d = dt.date(y, 1, 3)
    sid = 0
    while d.year == y:
        for p in PROVS:
            for s in range(SITES_PER_PROV):
                sid += 1
                code = 9002 if ((s + d.timetuple().tm_yday) % 3 == 0) else 9001
                rows.append({"id_survey": f"{y}-{sid}", "id_field": f"{p}-F{s:02d}",
                             "nome_area": p, "date": d.isoformat(),
                             "week": int(d.strftime("%V")), "val": code,
                             "name": f"campo {p} {s}"})
        d += dt.timedelta(days=7)
    fn = f"c{CROP}_s{SCHEMA}_v{VAR}_{y}.json"
    blob = json.dumps(rows, ensure_ascii=False)
    open(os.path.join(W, "RAW", fn), "w", encoding="utf-8").write(blob)
    idx["requests"].append({"var": VAR, "year": y, "ok": True, "rowCount": len(rows),
                            "n_rows": len(rows), "file": fn,
                            "sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest()})
json.dump(idx, open(os.path.join(W, "collection_index.json"), "w", encoding="utf-8"), indent=1)

rows, scale, meta = cp.load_rows(W, VAR)
OUT = {"SYNTHETIC_CASE": {
    "N_ROWS": len(rows), "N_SEASONS": len(YEARS), "VALUE_MODE": meta["VALUE_MODE"],
    "SCALE": {k: v["ordinal"] for k, v in scale.items()},
    "ROWS_BY_MONTH": dict(collections.Counter(str(r["_d"].month) for r in rows)),
    "DESIGN": "identical weekly sampling in every province in every week of every season, "
              "incidence held near 0.33 with no trend"}}

pre = (rows, scale, meta)
sweep = {}
for day in range(1, 366, 1):
    as_of = dt.date(2026, 1, 1) + dt.timedelta(days=day - 1)
    if as_of.year != 2026:
        break
    r = cp.current_pressure(W, VAR, as_of, _pre=pre)
    st = collections.Counter(v["STATE"] for v in r["PROVINCES"].values())
    sweep[as_of.isoformat()] = {
        "WINDOW": r["WINDOW"],
        "CROSSES_YEAR_BOUNDARY": r["WINDOW"][0][:4] != r["WINDOW"][1][:4],
        "N_CLASSED": sum(n for s, n in st.items() if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER)),
        "N_UNKNOWN_NO_BASELINE": st.get(cp.UNKNOWN_NO_BASELINE, 0),
        "N_UNKNOWN_NO_DATA": st.get(cp.UNKNOWN_NO_DATA, 0),
        "MEDIAN_BASELINE_N": sorted(v.get("BASELINE_N") or 0
                                    for v in r["PROVINCES"].values())[len(PROVS) // 2],
    }

crossing = [d for d, v in sweep.items() if v["CROSSES_YEAR_BOUNDARY"]]
noncross = [d for d, v in sweep.items() if not v["CROSSES_YEAR_BOUNDARY"]]
OUT["DAY_SWEEP_2026"] = {
    "N_DAYS_TESTED": len(sweep),
    "N_DAYS_WINDOW_CROSSES_YEAR_BOUNDARY": len(crossing),
    "CROSSING_DAYS_RANGE": [crossing[0], crossing[-1]] if crossing else None,
    "ON_CROSSING_DAYS": {
        "N_CLASSED_min_max": [min(sweep[d]["N_CLASSED"] for d in crossing),
                              max(sweep[d]["N_CLASSED"] for d in crossing)],
        "N_UNKNOWN_NO_BASELINE_min_max": [min(sweep[d]["N_UNKNOWN_NO_BASELINE"] for d in crossing),
                                          max(sweep[d]["N_UNKNOWN_NO_BASELINE"] for d in crossing)],
        "MEDIAN_BASELINE_N_min_max": [min(sweep[d]["MEDIAN_BASELINE_N"] for d in crossing),
                                      max(sweep[d]["MEDIAN_BASELINE_N"] for d in crossing)]},
    "ON_NON_CROSSING_DAYS": {
        "N_CLASSED_min_max": [min(sweep[d]["N_CLASSED"] for d in noncross),
                              max(sweep[d]["N_CLASSED"] for d in noncross)],
        "N_UNKNOWN_NO_BASELINE_min_max": [min(sweep[d]["N_UNKNOWN_NO_BASELINE"] for d in noncross),
                                          max(sweep[d]["N_UNKNOWN_NO_BASELINE"] for d in noncross)],
        "MEDIAN_BASELINE_N_min_max": [min(sweep[d]["MEDIAN_BASELINE_N"] for d in noncross),
                                      max(sweep[d]["MEDIAN_BASELINE_N"] for d in noncross)]},
}
OUT["SAMPLE_DAYS"] = {d: sweep[d] for d in
                      ["2026-01-01", "2026-01-15", "2026-01-27", "2026-01-28", "2026-01-29",
                       "2026-02-15", "2026-07-15", "2026-12-31"] if d in sweep}
OUT["CELLS_LOST_TO_THE_CALENDAR"] = {
    "PROVINCE_DAYS_PUBLISHABLE_ON_NON_CROSSING_DAYS": sum(sweep[d]["N_CLASSED"] for d in noncross),
    "PROVINCE_DAYS_PUBLISHABLE_ON_CROSSING_DAYS": sum(sweep[d]["N_CLASSED"] for d in crossing),
    "PROVINCE_DAYS_AVAILABLE_ON_CROSSING_DAYS": len(crossing) * len(PROVS),
}

json.dump(OUT, open(os.path.join(HERE, "rt3_e10_winter_case.json"), "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
shutil.rmtree(W, ignore_errors=True)
