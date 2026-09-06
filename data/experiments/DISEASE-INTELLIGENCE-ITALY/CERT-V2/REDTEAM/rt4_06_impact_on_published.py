#!/usr/bin/env python3
"""RT4 probe 6 — does ANY of it reach a PUBLISHED number?

Nothing under ENGINE/ or CASES/ is modified. Everything here is an in-memory monkeypatch or a
mutated copy of the rows handed to current_pressure through its own _pre argument.

  G1 coordinates       corrupt every lat/lon -> is the published output byte-identical?
  G2 province mislabel move the 30 Vicchio rows Siena->Firenze -> does a published cell change?
  G3 inheritance       sweep every case x many as_of dates: does a province with 0 visits in
                       the window EVER receive HIGHER/TYPICAL/LOWER?
  G4 aggregation       is there any key above the province in any emitted object?
  G5 ordinal truncation how many observations carry a code the ladder DROPS, and what happens to
                       the published numbers when the dropped codes are restored?
  G6 category error    run the engine on var 381 (localizzazione) and var 42 (fungicide used).
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
PUBLISHED = [("OLIVO x BACTROCERA", OLIVO, -1002), ("VITE x OIDIO", VITE, 39)]
ALL3 = PUBLISHED + [("FRUMENTO (var 372)", FRUM, 372)]


def norm(o):
    return json.dumps(o, sort_keys=True, default=str)


def main():
    res = {}

    # ================= G1 coordinates =================
    g1 = {}
    for name, d, v in ALL3:
        pre = cp.load_rows(d, v)
        ref = cp.current_pressure(d, v, AS_OF, _pre=pre)
        rows2 = copy.deepcopy(pre[0])
        n_touched = 0
        for r in rows2:                       # every coordinate replaced with the Sahara
            r["lat"], r["lon"] = "23.4162", "25.6628"
            n_touched += 1
        alt = cp.current_pressure(d, v, AS_OF, _pre=(rows2, pre[1], pre[2]))
        # also: delete the keys entirely
        rows3 = copy.deepcopy(pre[0])
        for r in rows3:
            r.pop("lat", None), r.pop("lon", None)
        alt2 = cp.current_pressure(d, v, AS_OF, _pre=(rows3, pre[1], pre[2]))
        g1[name] = {"N_ROWS_TOUCHED": n_touched,
                    "IDENTICAL_AFTER_MOVING_EVERY_POINT_TO_THE_SAHARA": norm(ref) == norm(alt),
                    "IDENTICAL_AFTER_DELETING_lat_lon_ENTIRELY": norm(ref) == norm(alt2)}
    res["G1_COORDINATES_REACH_A_PUBLISHED_NUMBER"] = g1

    # same for admin_code / name_3 / name_4 / name_5 / org_name
    g1b = {}
    for name, d, v in ALL3:
        pre = cp.load_rows(d, v)
        ref = cp.current_pressure(d, v, AS_OF, _pre=pre)
        for field in ("admin_code", "admin_code_3", "name_3", "name_4", "name_5",
                      "org_name", "id_org", "uid", "cultivar", "name", "id_area", "week"):
            rows2 = copy.deepcopy(pre[0])
            for r in rows2:
                r[field] = "99" if field == "week" else "CORRUPTED"
            alt = cp.current_pressure(d, v, AS_OF, _pre=(rows2, pre[1], pre[2]))
            g1b.setdefault(name, {})[field] = ("IGNORED (output identical)" if norm(ref) == norm(alt)
                                               else "LOAD-BEARING (output changed)")
        # and nome_area, for contrast
        rows2 = copy.deepcopy(pre[0])
        for r in rows2:
            r["nome_area"] = "CORRUPTED"
        alt = cp.current_pressure(d, v, AS_OF, _pre=(rows2, pre[1], pre[2]))
        g1b[name]["nome_area"] = ("IGNORED (output identical)" if norm(ref) == norm(alt)
                                  else "LOAD-BEARING (output changed)")
    res["G1b_WHICH_ROW_FIELDS_ARE_LOAD_BEARING"] = g1b

    # ================= G2 the Vicchio mislabel =================
    pre = cp.load_rows(VITE, 39)
    ref = cp.current_pressure(VITE, 39, AS_OF, _pre=pre)
    rows2 = copy.deepcopy(pre[0])
    fixed = 0
    for r in rows2:
        if r.get("id_field") == 5082 and r.get("nome_area") == "Siena":
            r["nome_area"] = "Firenze"
            fixed += 1
    fix = cp.current_pressure(VITE, 39, AS_OF, _pre=(rows2, pre[1], pre[2]))
    changed_today = {p: (ref["PROVINCES"][p], fix["PROVINCES"][p])
                     for p in ref["PROVINCES"] if norm(ref["PROVINCES"][p]) != norm(fix["PROVINCES"][p])}
    # and across the whole walk-forward at this calendar date
    wf_ref = cp.hindcast(VITE, 39, AS_OF.month, AS_OF.day, range(2006, 2027))
    _orig = cp.load_rows
    try:
        cp.load_rows = lambda d, v: (rows2, pre[1], pre[2])
        wf_fix = cp.hindcast(VITE, 39, AS_OF.month, AS_OF.day, range(2006, 2027))
    finally:
        cp.load_rows = _orig
    wf_diff = {f"{y}/{p}": [wf_ref[y].get(p), wf_fix[y].get(p)]
               for y in wf_ref for p in set(wf_ref[y]) | set(wf_fix.get(y, {}))
               if wf_ref[y].get(p) != wf_fix.get(y, {}).get(p)}
    # sweep every 7 days over the seasons the mislabel exists (2021-2024)
    sweep_diff = {}
    for y in (2021, 2022, 2023, 2024):
        for doy in range(120, 300, 7):
            a = dt.date(y, 1, 1) + dt.timedelta(days=doy - 1)
            r1 = cp.current_pressure(VITE, 39, a, _pre=pre)
            r2 = cp.current_pressure(VITE, 39, a, _pre=(rows2, pre[1], pre[2]))
            for p in set(r1["PROVINCES"]) | set(r2["PROVINCES"]):
                s1 = r1["PROVINCES"].get(p, {}).get("STATE")
                s2 = r2["PROVINCES"].get(p, {}).get("STATE")
                v1 = r1["PROVINCES"].get(p, {}).get("VALUE")
                v2 = r2["PROVINCES"].get(p, {}).get("VALUE")
                if s1 != s2 or v1 != v2:
                    sweep_diff[f"{a}/{p}"] = {"STATE": [s1, s2], "VALUE": [v1, v2]}
    res["G2_PROVINCE_MISLABEL"] = {
        "ROWS_REASSIGNED": fixed,
        "TODAY_CELLS_CHANGED": len(changed_today), "TODAY_DETAIL": changed_today,
        "WALKFORWARD_CELLS_CHANGED": len(wf_diff), "WALKFORWARD_DETAIL": wf_diff,
        "N_SWEEP_DATES": 4 * len(range(120, 300, 7)),
        "SWEEP_CELLS_CHANGED": len(sweep_diff),
        "SWEEP_DETAIL": dict(list(sweep_diff.items())[:40]),
        "SWEEP_STATE_CHANGES_ONLY": {k: v for k, v in sweep_diff.items()
                                     if v["STATE"][0] != v["STATE"][1]},
    }

    # ================= G3 inheritance =================
    g3 = {"CHECKED": 0, "VIOLATIONS": [], "CELLS_WITH_ZERO_VISITS": 0,
          "CELLS_CLASSED": 0, "PROVINCES_ABSENT_FROM_OUTPUT": {}}
    for name, d, v in ALL3:
        pre = cp.load_rows(d, v)
        allprov = {r.get("nome_area") for r in pre[0] if r.get("nome_area")}
        for y in range(2006, 2027):
            for md in ((5, 15), (6, 15), (7, 15), (8, 15), (9, 6), (10, 15)):
                try:
                    a = dt.date(y, *md)
                except ValueError:
                    continue
                r = cp.current_pressure(d, v, a, _pre=pre)
                for p, cell in r["PROVINCES"].items():
                    g3["CHECKED"] += 1
                    if cell.get("n_visits", 0) == 0:
                        g3["CELLS_WITH_ZERO_VISITS"] += 1
                    if cell["STATE"] in (cp.HIGHER, cp.TYPICAL, cp.LOWER):
                        g3["CELLS_CLASSED"] += 1
                        if cell.get("n_visits", 0) == 0 or cell.get("n_sites", 0) == 0:
                            g3["VIOLATIONS"].append({"case": name, "as_of": str(a),
                                                     "prov": p, "cell": cell})
                # a province present in the archive but missing from this output entirely
                miss = allprov - set(r["PROVINCES"])
                if miss:
                    g3["PROVINCES_ABSENT_FROM_OUTPUT"].setdefault(name, set()).update(miss)
    g3["PROVINCES_ABSENT_FROM_OUTPUT"] = {k: sorted(v) for k, v in
                                          g3["PROVINCES_ABSENT_FROM_OUTPUT"].items()}
    g3["INHERITANCE_FOUND"] = len(g3["VIOLATIONS"]) > 0
    res["G3_INHERITANCE"] = g3

    # ================= G4 aggregation above the province =================
    keys = set()
    for name, d, v in ALL3:
        r = cp.current_pressure(d, v, AS_OF)
        keys |= set(r["PROVINCES"].keys())
    TUSCAN = {"Arezzo", "Firenze", "Grosseto", "Livorno", "Lucca", "Massa-Carrara",
              "Pisa", "Pistoia", "Prato", "Siena"}
    res["G4_AGGREGATION"] = {
        "ALL_PROVINCE_KEYS_EVER_EMITTED": sorted(keys),
        "NON_PROVINCE_KEYS": sorted(keys - TUSCAN),
        "ANY_REGION_OR_NATIONAL_KEY": bool(keys - TUSCAN),
        "answer_sheet_2_WHERE_REGIONAL_UNIT": "province (hardcoded string)",
        "NOTE": ("current_pressure has exactly one geographic grouping statement, "
                 "current_pressure.py:253  p = r.get('nome_area')"),
    }

    # ================= G5 ordinal truncation =================
    g5 = {}
    for name, d, v in [("FRUMENTO var 372 (Intensita Oidio)", FRUM, 372),
                       ("VITE var 39", VITE, 39)]:
        idx = json.load(open(os.path.join(d, "collection_index.json")))
        scale, unresolved, _ = run_case.build_scale(idx["codes"], v)
        unres_ids = {str(c["id_survey_code"]) for c in idx["codes"]
                     if c["id_survey_var"] == v and str(c["id_survey_code"]) not in scale}
        rows = []
        for fn in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{v}_*.json"))):
            rows += json.load(open(fn))
        hits = collections.Counter(str(r.get("val")) for r in rows if str(r.get("val")) in unres_ids)
        g5[name] = {"UNRESOLVED_LABELS": unresolved,
                    "UNRESOLVED_CODE_IDS": sorted(unres_ids),
                    "N_OBSERVATIONS_CARRYING_A_DROPPED_CODE": sum(hits.values()),
                    "OF_TOTAL_ROWS": len(rows),
                    "PCT": round(100.0 * sum(hits.values()) / max(len(rows), 1), 4),
                    "BY_CODE": dict(hits)}
    # restore the dropped severity words and re-measure
    ref372 = cp.current_pressure(FRUM, 372, AS_OF)
    ref_hind = cp.hindcast(FRUM, 372, 6, 1, range(2013, 2027))
    saved = dict(run_case.WORD_RANK)
    try:
        run_case.WORD_RANK.update({"gravissima": 4, "gravissina": 4, "completa": 5})
        fix372 = cp.current_pressure(FRUM, 372, AS_OF)
        fix_hind = cp.hindcast(FRUM, 372, 6, 1, range(2013, 2027))
        idx = json.load(open(os.path.join(FRUM, "collection_index.json")))
        g5["SCALE_AFTER_RESTORING_THE_DROPPED_WORDS"] = {
            k: (val["label"], val["ordinal"])
            for k, val in sorted(run_case.build_scale(idx["codes"], 372)[0].items(),
                                 key=lambda kv: kv[1]["ordinal"])}
    finally:
        run_case.WORD_RANK.clear()
        run_case.WORD_RANK.update(saved)
    g5["EFFECT_ON_var372_TODAY"] = {
        p: {"BEFORE": ref372["PROVINCES"][p], "AFTER": fix372["PROVINCES"][p]}
        for p in ref372["PROVINCES"]
        if norm(ref372["PROVINCES"][p]) != norm(fix372["PROVINCES"].get(p))}
    g5["EFFECT_ON_var372_WALKFORWARD_1_JUNE"] = {
        f"{y}/{p}": [ref_hind[y].get(p), fix_hind[y].get(p)]
        for y in ref_hind for p in set(ref_hind[y]) | set(fix_hind.get(y, {}))
        if ref_hind[y].get(p) != fix_hind.get(y, {}).get(p)}
    g5["N_WALKFORWARD_CELLS"] = sum(len(v) for v in ref_hind.values())
    res["G5_ORDINAL_TRUNCATION"] = g5

    # ================= G6 category error =================
    g6 = {}
    for name, d, v in [("FRUMENTO var 381 LOCALIZZAZIONE Septoria", FRUM, 381),
                       ("FRUMENTO var 371 LOCALIZZAZIONE Oidio", FRUM, 371),
                       ("VITE var 42 PRODOTTO (fungicide applied)", VITE, 42)]:
        try:
            pre = cp.load_rows(d, v)
            r = cp.current_pressure(d, v, AS_OF, _pre=pre)
            hind = cp.hindcast(d, v, 6, 1, range(2006, 2027), _pre_unused=None) \
                if False else cp.hindcast(d, v, 6, 1, range(2006, 2027))
            flat = collections.Counter(s for row in hind.values() for s in row.values())
            g6[name] = {"ENGINE_REFUSED": False, "VALUE_MODE": r["VALUE_MODE"],
                        "SCALE_SIZE": len(pre[1]),
                        "SCALE": {k: (x["label"], x["ordinal"]) for k, x in pre[1].items()},
                        "UNRESOLVED": pre[2]["scale_unresolved"],
                        "TODAY": {p: {"STATE": c["STATE"], "VALUE": c.get("VALUE"),
                                      "n_sites": c["n_sites"]} for p, c in r["PROVINCES"].items()},
                        "WALKFORWARD_1_JUNE_CLASS_COUNTS": dict(flat),
                        "N_CLASSED_CELLS": sum(flat[k] for k in (cp.HIGHER, cp.TYPICAL, cp.LOWER)),
                        "ALL_VALUES_ARE_ZERO": all(
                            c.get("VALUE") in (None, 0.0) for c in r["PROVINCES"].values())}
        except Exception as e:
            g6[name] = {"ENGINE_REFUSED": True, "ERROR": f"{type(e).__name__}: {e}"}
    res["G6_CATEGORY_ERROR"] = g6

    json.dump(res, open(os.path.join(HERE, "rt4_06_impact_on_published.json"), "w",
                        encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
