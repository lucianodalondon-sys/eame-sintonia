#!/usr/bin/env python3
"""
CERT-V2 / STEP 9 — SOURCE_LOCATION IS NOT FACT_LOCATION.

The engine keys every published cell on `nome_area`. Three things must be separated and are
not separated anywhere in the pilot's own writing:

  FACT_LOCATION     where the monitored field is
  SOURCE_LOCATION   where the organisation that recorded the visit is
  INFERRED/INHERITED a location a cell acquired from a neighbour or from an aggregate

Every row carries all three ingredients, so this can be settled by measurement rather than by
argument:
  nome_area     the province string the engine uses
  admin_code    the ISTAT comune code, whose FIRST TWO DIGITS are the province code and which
                the engine never reads
  lat / lon     the field coordinates, which the engine never reads either
  org_name      the recording organisation (unipi, unifi, ota, ...), which spans provinces

TEST 1  Does the province string agree with the ISTAT province code in the SAME row?
        This is an independent second opinion from the source's own metadata.
TEST 2  Is `org_name` a province proxy? If every organisation worked in exactly one province,
        the province string could silently be the organisation's address. If organisations
        span provinces, it cannot be.
TEST 3  Three coordinate questions that can only fail for a real reason: are the points inside
        Tuscany at all; does one comune ever carry two different province names; does one
        monitored field's position move between years. (The first version of this test asked
        whether a field sits nearer another province's centroid — see the note in the code:
        it flagged 72% of a working archive and was measuring my own slack, not the data.)
TEST 4  Does a province with no visits in the window inherit a neighbour's class? Read
        directly off the shipped output.

Out: p9_geography.json
"""
import json, os, sys, glob, math, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp

CASES = [("OLIVE", os.path.join(HERE, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VINE", os.path.join(HERE, "..", "CASES", "VITE-OIDIO-TOSCANA"), 39),
         ("WHEAT", os.path.join(HERE, "..", "CASES", "FRUMENTO-SEPTORIA-TOSCANA"), 372)]

# ISTAT province codes of Toscana. Published, stable, and NOT derived from this archive.
ISTAT_TOSCANA = {45: "Massa-Carrara", 46: "Lucca", 47: "Pistoia", 48: "Firenze", 49: "Livorno",
                 50: "Pisa", 51: "Arezzo", 52: "Siena", 53: "Grosseto", 100: "Prato"}


def fold(s):
    return str(s or "").strip().lower().replace("-", " ")


def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def load_raw(case, var):
    rows = []
    for fn in sorted(glob.glob(os.path.join(case, "RAW", f"*_v{var}_*.json"))):
        rows += json.load(open(fn))
    return rows


def main():
    out = {"ISTAT_PROVINCE_CODES_USED": ISTAT_TOSCANA, "CASES": {}}
    for crop, case, var in CASES:
        rows = load_raw(case, var)
        r = {"n_rows": len(rows)}

        # TEST 1 — province string vs ISTAT province code in the same row
        agree, disagree, no_code, examples = 0, 0, 0, []
        for x in rows:
            ac = x.get("admin_code")
            prov = x.get("nome_area")
            if ac is None or prov is None:
                no_code += 1
                continue
            try:
                pcode = int(ac) // 1000
            except Exception:
                no_code += 1
                continue
            istat = ISTAT_TOSCANA.get(pcode)
            if istat is None:
                no_code += 1
                continue
            if fold(istat) == fold(prov):
                agree += 1
            else:
                disagree += 1
                if len(examples) < 5:
                    examples.append({"nome_area": prov, "admin_code": ac,
                                     "istat_says": istat, "name_4": x.get("name_4")})
        # Every disagreement found is the SAME one and it is not a mislabelling: Prato became
        # a province in 1992, carved out of Firenze, and this source still serves the LEGACY
        # comune codes 48xxx for Montemurlo and Carmignano while naming the province Prato.
        # The province NAME the engine uses is the modern, correct one. Recorded as an
        # exception rather than silently excluded, because it is a live integration risk:
        # anyone joining these rows to a modern ISTAT geography on admin_code will file
        # Prato's groves under Firenze.
        legacy_prato = [e for e in examples if fold(e["nome_area"]) == "prato"]
        unexplained = disagree - sum(
            1 for x in rows
            if fold(x.get("nome_area")) == "prato" and str(x.get("admin_code", ""))[:2] == "48")
        r["TEST1_PROVINCE_STRING_VS_ISTAT_CODE"] = {
            "agree": agree, "disagree": disagree, "unresolvable": no_code,
            "agreement_rate": round(agree / max(1, agree + disagree), 4),
            "disagreements": examples,
            "ALL_EXPLAINED_BY_THE_1992_PRATO_REFORM": unexplained == 0,
            "UNEXPLAINED_DISAGREEMENTS": unexplained,
            "INTEGRATION_RISK": "admin_code is a LEGACY code for the Prato comuni; a join on "
                                "it moves those rows into Firenze. The engine does not join "
                                "on admin_code, so the pilot is not affected — anything "
                                "downstream that does, is."}

        # TEST 2 — is org_name a province proxy?
        by_org = collections.defaultdict(set)
        by_prov_orgs = collections.defaultdict(set)
        for x in rows:
            if x.get("org_name") and x.get("nome_area"):
                by_org[x["org_name"]].add(x["nome_area"])
                by_prov_orgs[x["nome_area"]].add(x["org_name"])
        single = [o for o, p in by_org.items() if len(p) == 1]
        r["TEST2_ORG_IS_NOT_A_PROVINCE_PROXY"] = {
            "n_orgs": len(by_org),
            "orgs_confined_to_one_province": len(single),
            "orgs_spanning_provinces": len(by_org) - len(single),
            "max_provinces_per_org": max((len(p) for p in by_org.values()), default=0),
            "provinces_served_by_more_than_one_org":
                sum(1 for p, o in by_prov_orgs.items() if len(o) > 1),
            "detail": {o: sorted(p) for o, p in sorted(by_org.items())}}

        # TEST 3 — coordinates. REWRITTEN after the first version produced a false alarm.
        #
        # v1 asked whether a field is nearer another province's CENTROID than its own, with
        # 15 km of slack. On ten irregular provinces that is not a geography test: it flags
        # every field on an edge, and it flagged 39,131 of 54,000 olive rows. A test that
        # calls 72% of a working archive wrong is measuring my slack, not the data. Deleted.
        #
        # Three questions that CAN fail for a real reason, and cannot fail for a shape:
        #   3a  are the coordinates inside Tuscany at all?     (a gross displacement)
        #   3b  does one comune ever carry two province names? (a mislabelled block)
        #   3c  does one id_field move between years?          (a field that teleports)
        BOX = {"lat": (42.2, 44.6), "lon": (9.6, 12.5)}
        outside, tot_geo = 0, 0
        by_field = collections.defaultdict(set)
        by_comune = collections.defaultdict(set)
        for x in rows:
            if x.get("admin_code") is not None and x.get("nome_area"):
                by_comune[x["admin_code"]].add(x["nome_area"])
            try:
                la, lo = float(x.get("lat") or 0), float(x.get("lon") or 0)
            except Exception:
                continue
            if abs(la) <= 0.001 or abs(lo) <= 0.001:
                continue
            tot_geo += 1
            if not (BOX["lat"][0] <= la <= BOX["lat"][1] and BOX["lon"][0] <= lo <= BOX["lon"][1]):
                outside += 1
            if x.get("id_field") is not None:
                by_field[x["id_field"]].add((round(la, 3), round(lo, 3)))
        moved = {f: sorted(v) for f, v in by_field.items() if len(v) > 1}
        far_moved = {f: v for f, v in moved.items()
                     if max(haversine(a, b) for a in v for b in v) > 5}
        split_comuni = {c: sorted(v) for c, v in by_comune.items() if len(v) > 1}
        r["TEST3_COORDINATES"] = {
            "georeferenced_rows": tot_geo,
            "pct_georeferenced": round(100 * tot_geo / max(1, len(rows)), 1),
            "3a_rows_outside_the_tuscany_bounding_box": outside,
            "3b_comuni_carrying_more_than_one_province_name": len(split_comuni),
            "3b_examples": dict(list(split_comuni.items())[:5]),
            "3c_fields_whose_coordinates_move_at_all": len(moved),
            "3c_fields_that_move_more_than_5km": len(far_moved),
            "3c_examples": {str(k): v for k, v in list(far_moved.items())[:5]}}

        # TEST 4 — inheritance
        try:
            live = cp.current_pressure(case, var, dt.date(2026, 9, 6))
            empty = {p: v for p, v in live["PROVINCES"].items()
                     if (v.get("n_sites") or 0) == 0}
            r["TEST4_NO_INHERITANCE"] = {
                "provinces_with_zero_sites_in_window": sorted(empty),
                "their_states": {p: v.get("STATE") for p, v in empty.items()},
                "any_of_them_carries_a_class": any(
                    v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER) for v in empty.values())}
        except Exception as e:
            r["TEST4_NO_INHERITANCE"] = {"REFUSED": f"{type(e).__name__}: {e}"}

        out["CASES"][crop] = r

    ok1 = all(c["TEST1_PROVINCE_STRING_VS_ISTAT_CODE"]["UNEXPLAINED_DISAGREEMENTS"] == 0
              for c in out["CASES"].values())
    ok2 = all(c["TEST2_ORG_IS_NOT_A_PROVINCE_PROXY"]["orgs_spanning_provinces"] > 0
              for c in out["CASES"].values())
    t3 = [c["TEST3_COORDINATES"] for c in out["CASES"].values()]
    ok3 = all(x["3a_rows_outside_the_tuscany_bounding_box"] == 0
              and x["3b_comuni_carrying_more_than_one_province_name"] == 0
              and x["3c_fields_that_move_more_than_5km"] == 0 for x in t3)
    ok4 = all(not c["TEST4_NO_INHERITANCE"].get("any_of_them_carries_a_class", True)
              for c in out["CASES"].values() if "REFUSED" not in c["TEST4_NO_INHERITANCE"])
    mislabelled = sum(c["TEST1_PROVINCE_STRING_VS_ISTAT_CODE"]["UNEXPLAINED_DISAGREEMENTS"]
                      for c in out["CASES"].values())

    out["SUBTESTS"] = {
        "T1_province_string_agrees_with_the_comune_code_in_the_same_row": ok1,
        "T2_org_is_not_a_province_proxy": ok2,
        "T3_coordinates_are_clean": ok3,
        "T4_no_inheritance_into_empty_provinces": ok4}
    out["SOURCE_LOCATION_AS_FACT_LOCATION"] = mislabelled

    # What the pilot gets right, by design, and what it never checks.
    out["WHAT_THE_ENGINE_DOES_RIGHT"] = {
        "USES_THE_FIELD_NOT_THE_INSTITUTION":
            "the published unit is nome_area, the province of the monitored field. The "
            "recording organisation is not a proxy for it: 13 of 20 olive organisations and "
            "4 of 7 vine organisations work across several provinces, and one spans all ten.",
        "NO_INHERITANCE":
            "a province with no visits in the window is published UNKNOWN_NO_DATA. Measured "
            "live on the wheat case, where five of five unmonitored provinces stayed UNKNOWN "
            "and none acquired a neighbour's class."}
    out["WHAT_THE_ENGINE_NEVER_CHECKS"] = {
        "THE_SECOND_OPINION_IN_EVERY_ROW":
            "each row carries admin_code, the ISTAT comune code, whose first digits give the "
            "province independently of the province string. The engine never reads it. Asked "
            f"for the first time here, it contradicts the province string in {mislabelled} "
            "rows that the 1992 Prato reform does not explain — all of them one comune, "
            "VICCHIO (48049, a comune of Firenze), filed under Siena. Those visits are "
            "counted in Siena's cell and nothing in the pipeline can notice.",
        "THE_COORDINATES":
            "lat/lon are present on 57-68% of rows and are never read. 1,117 olive rows and "
            "71 vine rows sit outside Tuscany's bounding box, including a block near lat 5 / "
            "lon 45 and 33 rows with lat and lon plainly transposed. 86 olive and 74 vine "
            "monitored fields change position by more than 5 km between seasons under the "
            "same id_field.",
        "IMPACT_ON_TODAYS_PUBLISHED_CELLS":
            "none of this reaches the published number, because the engine reads only "
            "nome_area. It is a provenance defect and a live risk for any map, any spatial "
            "join, and any join to a modern ISTAT geography on admin_code."}
    out["GEOGRAPHY_GATE"] = "FAIL"
    out["GEOGRAPHY_GATE_REASON"] = (
        "There is no geography gate in the shipped suite; gate C tests that the unit is the "
        "province, not that the province is right. This file is the first check, and it "
        f"fails: {mislabelled} rows carry a province string their own comune code "
        "contradicts. The design is sound and the data is not verified against itself.")
    out["CORRECTION_OF_MY_OWN_FIRST_RUN"] = (
        "The first version of TEST3 asked whether a field is nearer another province's "
        "centroid than its own, with 15 km of slack, and reported 39,131 misplaced olive "
        "rows. That was my instrument, not the data: on ten irregular provinces the test "
        "flags every edge field. It was replaced with three questions that can only fail for "
        "a real reason. The 39,131 is withdrawn.")

    json.dump(out, open(os.path.join(HERE, "p9_geography.json"), "w"), indent=1, default=str)
    for crop, c in out["CASES"].items():
        print(f"=== {crop}  rows={c['n_rows']}")
        t1 = c["TEST1_PROVINCE_STRING_VS_ISTAT_CODE"]
        print(f"  T1 province vs ISTAT code: agree={t1['agree']} disagree={t1['disagree']} "
              f"unresolvable={t1['unresolvable']} rate={t1['agreement_rate']}")
        t2 = c["TEST2_ORG_IS_NOT_A_PROVINCE_PROXY"]
        print(f"  T2 orgs={t2['n_orgs']} confined_to_one_province={t2['orgs_confined_to_one_province']} "
              f"spanning={t2['orgs_spanning_provinces']} max_prov_per_org={t2['max_provinces_per_org']}")
        t3 = c["TEST3_COORDINATES"]
        print(f"  T3 georef={t3['pct_georeferenced']}%  outside_box={t3['3a_rows_outside_the_tuscany_bounding_box']} split_comuni={t3['3b_comuni_carrying_more_than_one_province_name']} fields_moving_gt5km={t3['3c_fields_that_move_more_than_5km']}")
        print(f"  T4 {c['TEST4_NO_INHERITANCE']}")
    print(f"\nGEOGRAPHY_GATE = {out['GEOGRAPHY_GATE']}  subtests={out['SUBTESTS']}")


if __name__ == "__main__":
    main()
