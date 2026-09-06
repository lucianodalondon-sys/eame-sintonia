#!/usr/bin/env python3
"""RT4 / SEMANTICS probe 4 -- the three questions kept SEPARATE.

  Q1 DATA    : does the raw observation carry a signal for the crop / issue / region?
  Q2 ENGINE  : does current_pressure canonicalise it into its output object?
  Q3 PORTAL  : does the portal vocabulary have a token that could render it?

READ ONLY on italia-portale. Nothing there is modified.
"""
import json, os, glob, collections, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "ENGINE")
CASESD = os.path.join(HERE, "..", "..", "CASES")
SNAP = os.path.join(HERE, "..", "..", "..", "..", "..",
                    "italia-portale", "client", "meeting-intelligence-snapshot.json")
sys.path.insert(0, os.path.abspath(ENGINE))
sys.path.insert(0, os.path.abspath(CASESD))

CASES = [("OLIVO-BACTROCERA-TOSCANA", -1002), ("VITE-OIDIO-TOSCANA", 39),
         ("FRUMENTO-SEPTORIA-TOSCANA", 372)]


def walk(o):
    if isinstance(o, dict):
        yield o
        for x in o.values():
            yield from walk(x)
    elif isinstance(o, list):
        for x in o:
            yield from walk(x)


def main():
    res = {}

    # ---------- Q1: what is in the DATA ----------
    q1 = {}
    for case, var in CASES:
        rows = []
        for fn in sorted(glob.glob(os.path.join(CASESD, case, "RAW", f"*_v{var}_*.json"))):
            rows += json.load(open(fn))
        idx = json.load(open(os.path.join(CASESD, case, "collection_index.json")))
        vmeta = next((v for v in (idx.get("vars") or []) if v["id_survey_var"] == var), None)
        q1[case] = {
            "ROW_KEYS": sorted(rows[0].keys()) if rows else [],
            "ANY_KEY_NAMING_THE_CROP": [k for k in (rows[0] if rows else {})
                                        if k in ("crop", "coltura", "crop_name")],
            "cultivar_NON_EMPTY": f"{sum(1 for r in rows if r.get('cultivar'))}/{len(rows)}",
            "cultivar_VALUES_SAMPLE": sorted({r.get("cultivar") for r in rows if r.get("cultivar")})[:12],
            "ANY_KEY_NAMING_THE_ISSUE": [k for k in (rows[0] if rows else {})
                                         if k in ("issue", "avversita", "pest", "disease")],
            "ANY_KEY_NAMING_THE_REGION": [k for k in (rows[0] if rows else {})
                                          if k in ("region", "regione", "nome_regione")],
            "CROP_SIGNAL_LOCATION": f"collection_index.crop = {idx.get('crop')} (an integer id, "
                                    f"not a name); no crop field on any row",
            "ISSUE_SIGNAL_LOCATION": (f"collection_index.vars[id_survey_var={var}].name = "
                                      f"{vmeta.get('name') if vmeta else None!r} "
                                      f"(+ schema={idx.get('schema')})"),
            "REGION_SIGNAL_LOCATION": "no region field on any row; only nome_area (province)",
        }
    res["Q1_DATA"] = q1

    # ---------- Q2: what the ENGINE emits ----------
    import current_pressure as cp
    out = cp.current_pressure(os.path.join(CASESD, "VITE-OIDIO-TOSCANA"), 39, dt.date(2026, 9, 6))
    top = sorted(out.keys())
    prov_keys = sorted(next(iter(out["PROVINCES"].values())).keys())
    res["Q2_ENGINE"] = {
        "CURRENT_PRESSURE_TOP_LEVEL_KEYS": top,
        "PER_PROVINCE_KEYS": prov_keys,
        "CARRIES_DATE": "YES -- AS_OF, WINDOW, CUTOFF_LABEL",
        "CARRIES_REGION": ("NO -- the only geographic token is the PROVINCES dict key, which is "
                           "the raw nome_area string. No region field exists anywhere in the "
                           "output object."),
        "CARRIES_CROP": "NO" if not any("CROP" in k.upper() for k in top) else "YES",
        "CARRIES_ISSUE": "NO" if not any("ISSUE" in k.upper() for k in top) else "YES",
        "SOURCE_FIELD_IS": out.get("SOURCE"),
        "PROVINCE_KEYS_EMITTED": sorted(out["PROVINCES"].keys()),
        "WHERE_CROP_AND_ISSUE_COME_FROM": ("ENGINE/gates.py:26 passes the literal strings "
                                           "'issue', 'crop', 'region' to answer_sheet()"),
    }
    # prove the gates.py:26 consequence
    from answer_sheet import answer_sheet
    sheet = answer_sheet(os.path.join(CASESD, "VITE-OIDIO-TOSCANA"), 39, dt.date(2026, 9, 6),
                         "issue", "crop", "region")
    res["Q2_ENGINE"]["GATES_LINE_26_PRODUCES"] = sheet["1_WHAT_HAPPENED"]["STATEMENT"]

    # ---------- Q3: the PORTAL vocabulary ----------
    q3 = {"SNAPSHOT_PATH": os.path.abspath(SNAP), "EXISTS": os.path.exists(SNAP)}
    if os.path.exists(SNAP):
        S = json.load(open(SNAP, encoding="utf-8"))
        cases = [d for d in walk(S) if isinstance(d, dict) and "ARCHETYPE" in d]
        q3["N_CASES_IN_PORTAL"] = len(cases)
        for f in ("CROP", "TARGET", "GEOGRAPHY", "ARCHETYPE"):
            q3[f"{f}_VOCABULARY"] = dict(sorted(collections.Counter(
                str(c.get(f)) for c in cases).items(), key=lambda kv: -kv[1]))
        # the three cases, asked of the portal vocabulary
        crops = set(q3["CROP_VOCABULARY"])
        targets = set(q3["TARGET_VOCABULARY"])
        geos = set(q3["GEOGRAPHY_VOCABULARY"])
        q3["CAN_THE_PORTAL_NAME_OUR_THREE_CELLS"] = {
            "OLIVO (olive)": {
                "CROP_TOKEN": sorted(t for t in crops if "OLIV" in t.upper()) or "ABSENT",
                "ISSUE_TOKEN": sorted(t for t in targets
                                      if "BACTRO" in t.upper() or "OLIV" in t.upper()
                                      or "OLEA" in t.upper()) or "ABSENT"},
            "VITE (grapevine)": {
                "CROP_TOKEN": sorted(t for t in crops
                                     if "GRAPE" in t.upper() or "VITE" in t.upper()) or "ABSENT",
                "ISSUE_TOKEN": sorted(t for t in targets
                                      if "OIDI" in t.upper() or "ERYSIPHE" in t.upper()
                                      or "UNCINULA" in t.upper()
                                      or "POWDERY" in t.upper()) or "ABSENT"},
            "FRUMENTO (wheat)": {
                "CROP_TOKEN": sorted(t for t in crops
                                     if "WHEAT" in t.upper() or "FRUMENT" in t.upper()
                                     or "CEREAL" in t.upper()) or "ABSENT",
                "ISSUE_TOKEN": sorted(t for t in targets
                                      if "SEPTOR" in t.upper() or "ZYMOSEPT" in t.upper()
                                      or "OIDI" in t.upper()) or "ABSENT"},
            "TOSCANA": {"GEO_TOKEN": sorted(t for t in geos if "TOSCAN" in t.upper()) or "ABSENT"},
        }
        q3["ANY_PROVINCE_LEVEL_GEO_TOKEN"] = sorted(
            t for t in geos if any(p.upper() in t.upper() for p in
                                   ("FIRENZE", "SIENA", "AREZZO", "GROSSETO", "PISA", "LIVORNO",
                                    "LUCCA", "PISTOIA", "PRATO", "MASSA"))) or "ABSENT"
        q3["GEO_GRANULARITY"] = ("every GEOGRAPHY token is a REGION or a COUNTRY; the portal has "
                                 "no province-level token" if not q3["ANY_PROVINCE_LEVEL_GEO_TOKEN"]
                                 or q3["ANY_PROVINCE_LEVEL_GEO_TOKEN"] == "ABSENT" else "has provinces")
    res["Q3_PORTAL"] = q3

    json.dump(res, open(os.path.join(HERE, "rt4_sem_04_portal_vocabulary.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
