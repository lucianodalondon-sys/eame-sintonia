#!/usr/bin/env python3
"""RT3-E9. Does the published class depend on WHEN the archive was collected, rather than on
when the observations were made?

If the source is immutable for closed seasons, re-fetching season 2015 today must return
exactly what is on disk. If it is NOT immutable -- backfills, corrections, re-coded values --
then every baseline, every hindcast cell and therefore every published percentile is a
function of the collection date, and with no COLLECTED_AT recorded anywhere that function's
argument is unrecoverable.

Read-only against the network; writes nothing outside REDTEAM/.
"""
import sys, os, json, glob, hashlib, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
sys.path.insert(0, CAS)
import current_pressure as cp
from collect_generic import fetch, unwrap

PROBE_UTC = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
CASES = [("VITE-OIDIO-TOSCANA", 3, 8, 39), ("OLIVO-BACTROCERA-TOSCANA", 2, 1, -1002)]
OUT = {"PROBE_RUN_AT_UTC": PROBE_UTC,
       "NOTE": "this timestamp exists only because THIS script recorded it; no pipeline "
               "artifact records when any archive file was collected"}


def canon(rows):
    """Order-insensitive content fingerprint of a row set."""
    return hashlib.sha256(
        json.dumps(sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows),
                   ensure_ascii=False).encode()).hexdigest()


res = {}
for cname, crop, schema, var in CASES:
    d = os.path.join(CAS, cname)
    per_year = {}
    stored_years = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:-5])
                           for f in glob.glob(os.path.join(d, "RAW", f"*_v{var}_*.json"))})
    probe_years = [y for y in (2015, 2019, 2020, 2024, 2025, 2026) if y in stored_years]
    for y in probe_years:
        p = os.path.join(d, "RAW", f"c{crop}_s{schema}_v{var}_{y}.json")
        stored = json.loads(open(p, "rb").read().decode("utf-8"))
        js = fetch({"tipo_elab": "elab_pivot", "year": y, "crop": crop,
                    "survey_schema": schema, "survey_var": var, "difesa": "all",
                    "week": "all", "cultivar": "all", "area": "all",
                    "accesso": "all", "user_access": "all"})
        ok, rc, live, fb = unwrap(js)
        s_keys = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in stored}
        l_keys = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in live}
        # value-level comparison keyed on the identity of a visit
        def keyed(rows):
            m = {}
            for r in rows:
                m[(r.get("id_survey"), r.get("id_field"), r.get("date"))] = r.get("val")
            return m
        ks, kl = keyed(stored), keyed(live)
        common = set(ks) & set(kl)
        changed_val = [k for k in common if ks[k] != kl[k]]
        per_year[str(y)] = {
            "STORED_ROWS": len(stored), "LIVE_ROWS": len(live), "LIVE_ok": ok,
            "DELTA_ROWS": len(live) - len(stored),
            "CONTENT_HASH_IDENTICAL": canon(stored) == canon(live),
            "ROWS_ONLY_IN_STORED": len(s_keys - l_keys),
            "ROWS_ONLY_IN_LIVE": len(l_keys - s_keys),
            "N_VISITS_COMMON": len(common),
            "N_VISITS_WITH_CHANGED_val": len(changed_val),
            "SAMPLE_CHANGED": [{"key": str(k), "stored_val": ks[k], "live_val": kl[k]}
                               for k in changed_val[:4]],
        }
    res[cname] = per_year
OUT["REFETCH_VS_ARCHIVE"] = res

# --------------------------------------------- is the code table itself collection-dependent?
codetab = {}
for cname, crop, schema, var in CASES:
    d = os.path.join(CAS, cname)
    idx = json.load(open(os.path.join(d, "collection_index.json"), encoding="utf-8"))
    stored_codes = idx.get("codes") or []
    sizes = {}
    for y in (2006, 2015, 2025, 2026):
        js = fetch({"tipo_elab": "elab_pivot", "year": y, "crop": crop,
                    "survey_schema": schema, "survey_var": var, "difesa": "all",
                    "week": "all", "cultivar": "all", "area": "all",
                    "accesso": "all", "user_access": "all"})
        ok, rc, rows, fb = unwrap(js)
        cand = (fb or {}).get("survey_code") or {}
        sizes[str(y)] = len(cand.get("data") or [])
    codetab[cname] = {"N_CODES_STORED_IN_INDEX": len(stored_codes),
                      "N_CODES_SERVED_PER_YEAR_TODAY": sizes,
                      "CODE_TABLE_IS_YEAR_DEPENDENT": len(set(sizes.values())) > 1}
OUT["CODE_TABLE_COLLECTION_DEPENDENCE"] = codetab

json.dump(OUT, open(os.path.join(HERE, "rt3_e9_collection_time.json"), "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
