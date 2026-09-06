#!/usr/bin/env python3
"""RT4 probe 7 — two things probe 6 could only show as empty objects.

  H1  id_field is the SITE KEY (current_pressure.py:195). Is it unique to a field?
      Quantify id_field values that carry more than one comune, and measure what happens to
      n_sites when the site key is (id_field, admin_code) instead of id_field alone.
  H2  CATEGORY ERROR, demonstrated rather than asserted. Vars 42 / 371 / 381 were never
      collected, so probe 6 could only show an empty PROVINCES dict. Here real VITE rows are
      re-coded onto the var-42 (fungicide applied) code table and handed to the SHIPPED
      current_pressure through its own _pre argument. Nothing on disk is modified.
  H3  the FRUMENTO case name vs the variable it actually collected.
"""
import json, os, sys, glob, copy, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CASESD = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENGINE)
sys.path.insert(0, CASESD)
import current_pressure as cp
import run_case

OLIVO = os.path.join(CASESD, "OLIVO-BACTROCERA-TOSCANA")
VITE = os.path.join(CASESD, "VITE-OIDIO-TOSCANA")
FRUM = os.path.join(CASESD, "FRUMENTO-SEPTORIA-TOSCANA")
AS_OF = dt.date(2026, 9, 6)
ALL3 = [("OLIVO x BACTROCERA", OLIVO, -1002), ("VITE x OIDIO", VITE, 39),
        ("FRUMENTO var 372", FRUM, 372)]


def main():
    res = {}

    # ================= H1 id_field collisions =================
    h1 = {}
    for name, d, v in ALL3:
        rows = []
        for fn in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{v}_*.json"))):
            rows += json.load(open(fn))
        f2c = collections.defaultdict(set)
        f2n4 = collections.defaultdict(set)
        for r in rows:
            f2c[r["id_field"]].add(str(r.get("admin_code")))
            f2n4[r["id_field"]].add(r.get("name_4"))
        bad = {k: sorted(v2) for k, v2 in f2c.items() if len(v2) > 1}
        badrows = [r for r in rows if r["id_field"] in bad]
        h1[name] = {
            "N_ROWS": len(rows), "N_DISTINCT_id_field": len(f2c),
            "N_id_field_WITH_2PLUS_COMUNI": len(bad),
            "PCT_OF_FIELDS": round(100.0 * len(bad) / max(len(f2c), 1), 3),
            "N_ROWS_ON_A_COLLIDING_id_field": len(badrows),
            "PCT_OF_ROWS": round(100.0 * len(badrows) / max(len(rows), 1), 3),
            "EXAMPLES": {str(k): {"admin_codes": v2,
                                  "comuni": sorted(x for x in f2n4[k] if x),
                                  "provinces": sorted({r.get("nome_area") for r in rows
                                                       if r["id_field"] == k})}
                         for k, v2 in list(bad.items())[:8]},
        }
        # does the collision ever collapse two comuni into one SITE inside one 28-day window?
        collapsed = []
        for y in range(2006, 2027):
            for md in ((5, 15), (6, 15), (7, 15), (8, 15), (9, 6), (10, 15)):
                try:
                    hi = dt.date(y, *md)
                except ValueError:
                    continue
                lo = hi - dt.timedelta(days=27)
                w = collections.defaultdict(set)
                for r in rows:
                    dd = r.get("date")
                    if not dd:
                        continue
                    try:
                        dv = dt.date.fromisoformat(dd)
                    except ValueError:
                        continue
                    if lo <= dv <= hi and r["id_field"] in bad:
                        w[r["id_field"]].add(str(r.get("admin_code")))
                for k, cs in w.items():
                    if len(cs) > 1:
                        collapsed.append({"as_of": str(hi), "id_field": k, "admin_codes": sorted(cs)})
        h1[name]["WINDOWS_WHERE_ONE_id_field_HELD_2_COMUNI_AT_ONCE"] = len(collapsed)
        h1[name]["COLLAPSE_EXAMPLES"] = collapsed[:6]
    res["H1_ID_FIELD_IS_THE_SITE_KEY"] = h1

    # measure n_sites under the stricter key, on the published cases
    strict = {}
    for name, d, v in ALL3:
        pre = cp.load_rows(d, v)
        ref = cp.current_pressure(d, v, AS_OF, _pre=pre)
        rows2 = copy.deepcopy(pre[0])
        for r in rows2:
            r["id_field"] = f"{r['id_field']}|{r.get('admin_code')}"
        alt = cp.current_pressure(d, v, AS_OF, _pre=(rows2, pre[1], pre[2]))
        diff = {p: {"n_sites": [ref["PROVINCES"][p]["n_sites"], alt["PROVINCES"][p]["n_sites"]],
                    "VALUE": [ref["PROVINCES"][p].get("VALUE"), alt["PROVINCES"][p].get("VALUE")],
                    "STATE": [ref["PROVINCES"][p]["STATE"], alt["PROVINCES"][p]["STATE"]]}
                for p in ref["PROVINCES"]
                if json.dumps(ref["PROVINCES"][p], sort_keys=True, default=str) !=
                json.dumps(alt["PROVINCES"][p], sort_keys=True, default=str)}
        strict[name] = {"CELLS_CHANGED_TODAY": len(diff), "DETAIL": diff,
                        "STATE_CHANGES": {p: x for p, x in diff.items()
                                          if x["STATE"][0] != x["STATE"][1]}}
    res["H1b_SITE_KEY_TIGHTENED_TO_id_field_PLUS_COMUNE"] = strict

    # ================= H2 category error, demonstrated =================
    idx = json.load(open(os.path.join(VITE, "collection_index.json")))
    scale42, unres42, _ = run_case.build_scale(idx["codes"], 42)
    pre39 = cp.load_rows(VITE, 39)
    # re-code the real survey answers onto the fungicide code table, preserving the shape of
    # the real data: nessuna->nessuno, bassa->zolfo, media->quinoxifen, alta->strobilurine
    remap = {"782": "306", "783": "307", "784": "309", "785": "311"}
    rows42 = copy.deepcopy(pre39[0])
    n_remap = 0
    for r in rows42:
        if str(r.get("val")) in remap:
            r["val"] = remap[str(r["val"])]
            n_remap += 1
    meta42 = dict(pre39[2])
    meta42["VALUE_MODE"] = "ORDINAL"
    meta42["scale_unresolved"] = unres42
    out42 = cp.current_pressure(VITE, 42, AS_OF, _pre=(rows42, scale42, meta42))
    hind42 = {}
    for y in range(2010, 2027):
        try:
            hind42[y] = {p: c["STATE"] for p, c in cp.current_pressure(
                VITE, 42, dt.date(y, 7, 15), _pre=(rows42, scale42, meta42))["PROVINCES"].items()}
        except Exception as e:
            hind42[y] = str(e)
    flat = collections.Counter(s for row in hind42.values() if isinstance(row, dict)
                               for s in row.values())
    res["H2_CATEGORY_ERROR_DEMONSTRATED"] = {
        "VARIABLE": "VITE id_survey_var 42 = 'prodotto' / 'prodotto utilizzato' "
                    "(WHICH FUNGICIDE THE GROWER APPLIED)",
        "N_ROWS_RECODED": n_remap, "OF": len(rows42),
        "SCALE_THE_ENGINE_BUILT": {k: (v["label"], v["ordinal"]) for k, v in scale42.items()},
        "LABELS_THE_ENGINE_DROPPED": unres42,
        "ENGINE_REFUSED": False,
        "VALUE_MODE_IT_CHOSE": out42["VALUE_MODE"],
        "EVIDENCE_ROLE_IT_STAMPED": out42["EVIDENCE_ROLE"],
        "PUBLISHED_TODAY": {p: {"STATE": c["STATE"], "VALUE": c.get("VALUE"),
                                "n_sites": c["n_sites"], "PERCENTILE": c.get("PERCENTILE")}
                            for p, c in out42["PROVINCES"].items()},
        "WALKFORWARD_15_JULY_CLASS_COUNTS": dict(flat),
        "N_CLASSED_CELLS": sum(flat[k] for k in (cp.HIGHER, cp.TYPICAL, cp.LOWER)),
        "ALL_PUBLISHED_VALUES_ZERO": all(c.get("VALUE") in (None, 0.0)
                                         for c in out42["PROVINCES"].values()),
    }

    # same demonstration for var 371 (localizzazione = WHERE on the plant), using FRUMENTO rows
    idxf = json.load(open(os.path.join(FRUM, "collection_index.json")))
    scale371, unres371, _ = run_case.build_scale(idxf["codes"], 371)
    pre372 = cp.load_rows(FRUM, 372)
    remap371 = {"1599": "1614", "1628": "1615", "1602": "1616", "1603": "1618",
                "1629": "1619", "1605": "1620"}
    rows371 = copy.deepcopy(pre372[0])
    n2 = 0
    for r in rows371:
        if str(r.get("val")) in remap371:
            r["val"] = remap371[str(r["val"])]
            n2 += 1
    meta371 = dict(pre372[2])
    meta371["VALUE_MODE"] = "ORDINAL"
    out371 = cp.current_pressure(FRUM, 371, AS_OF, _pre=(rows371, scale371, meta371))
    h371 = {}
    for y in range(2013, 2027):
        h371[y] = {p: (c["STATE"], c.get("VALUE")) for p, c in cp.current_pressure(
            FRUM, 371, dt.date(y, 6, 1), _pre=(rows371, scale371, meta371))["PROVINCES"].items()}
    res["H2b_LOCALISATION_READ_AS_SEVERITY"] = {
        "VARIABLE": "FRUMENTO id_survey_var 371 = 'Localizzazione Oidio' "
                    "(WHERE ON THE PLANT the mildew sits, not how much)",
        "SCALE_THE_ENGINE_BUILT": {k: (v["label"], v["ordinal"]) for k, v in scale371.items()},
        "LABELS_DROPPED": unres371,
        "READS_Parte_bassa_AS": "ordinal 1 (a LOW severity)",
        "READS_Parte_alta_AS": "ordinal 2 (a HIGH severity)",
        "TRUTH": ("'parte bassa' / 'parte alta' are the LOWER and UPPER part of the canopy. "
                  "The three positions that matter most agronomically -- penultima foglia, "
                  "ultima foglia (flag leaf), spiga (ear) -- are the three the ladder drops."),
        "N_ROWS_RECODED": n2,
        "PUBLISHED_WALKFORWARD_1_JUNE": {str(y): v for y, v in h371.items()},
    }

    # ================= H3 the case name vs the variable =================
    vmeta = {v["id_survey_var"]: v["name"] for v in idxf["vars"]}
    res["H3_CASE_NAME_VS_VARIABLE"] = {
        "CASE_DIRECTORY": "CASES/FRUMENTO-SEPTORIA-TOSCANA",
        "VARIABLE_ACTUALLY_COLLECTED": 372,
        "ITS_NAME_IN_THE_SOURCE_SCHEMA": vmeta.get(372),
        "THE_SEPTORIA_VARIABLE_IN_THE_SAME_SCHEMA": {
            "id_survey_var": 382, "name": vmeta.get(382),
            "COLLECTED": bool(glob.glob(os.path.join(FRUM, "RAW", "*_v382_*.json")))},
        "RAW_FILES_PRESENT": sorted({os.path.basename(f).rsplit("_", 1)[0]
                                     for f in glob.glob(os.path.join(FRUM, "RAW", "*.json"))}),
        "ALL_VARS_IN_SCHEMA_74": vmeta,
        "OUTCOMES_FILE_ON_DISK": sorted(os.path.basename(f) for f in
                                        glob.glob(os.path.join(FRUM, "outcomes_*.json"))),
    }

    json.dump(res, open(os.path.join(HERE, "rt4_07_idfield_and_injection.json"), "w",
                        encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
