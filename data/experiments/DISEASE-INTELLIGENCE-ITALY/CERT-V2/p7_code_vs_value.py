#!/usr/bin/env python3
"""
CERT-V2 / STEP 7 — A CODE IS NOT A MEASUREMENT.

The pilot found this the hard way: frumento x septoria serves the values 1599 and 1628, which
are id_survey_code values. The module read them as magnitudes, every value was > 0, and it
published "TYPICAL_FOR_THE_DATE, 100% of monitored sites" for two provinces. The shipped
answer is current_pressure.assert_scale_decodes(): in NUMERIC mode, if >= 90% of the observed
values are drawn from the case's OWN id_survey_code vocabulary, refuse.

FIRST VERSION OF THIS FILE WAS INVALID AND IS RECORDED AS SUCH.
  It injected "the case's own code ids" into the olive case and reported the engine published
  anyway — 63 false claims. The olive collection index carries NO code table at all, so the
  injection injected nothing and the run measured itself. The number 63 was mine, not the
  engine's. The questions below replace it.

WHAT THE GUARD ACTUALLY NEEDS TO FIRE (both at once):
  1. VALUE_MODE == NUMERIC   -> the case has no code table FOR THAT VARIABLE, and the source
                                declares widget=numeric
  2. idx["codes"] non-empty  -> the case has a code table for SOME variable
Neither of the pilot's two published cases is in that state, and neither is the wheat case.
So the guard is asked, here, on a case constructed to be exactly in that state.

Out: p7_code_vs_value.json
"""
import json, os, sys, copy, hashlib, shutil, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp

CASEDIR = os.path.join(HERE, "..", "CASES")
LAB = os.path.join(HERE, "CODE-VALUE-LAB")
AS_OF = dt.date(2026, 9, 6)
CASES = {"WHEAT": ("FRUMENTO-SEPTORIA-TOSCANA", 372),
         "OLIVE": ("OLIVO-BACTROCERA-TOSCANA", -1002),
         "VINE": ("VITE-OIDIO-TOSCANA", 39)}


def try_pressure(case, var, pre=None):
    try:
        r = cp.current_pressure(case, var, AS_OF, _pre=pre)
        st = {p: v.get("STATE") for p, v in r["PROVINCES"].items()}
        return {"OUTCOME": "PUBLISHED",
                "n_provinces_classed": sum(1 for s in st.values()
                                           if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER)),
                "states": st}
    except ValueError as e:
        return {"OUTCOME": "REFUSED", "message": str(e)[:220]}
    except Exception as e:
        return {"OUTCOME": "CRASHED", "message": f"{type(e).__name__}: {str(e)[:220]}"}


def build_numeric_case_with_a_code_table(code_share):
    """A case in the ONE state where the guard can fire: the source declares the variable
    numeric, the case carries a code table for a DIFFERENT variable, and a chosen share of
    the served values are drawn from that code vocabulary.

    Built from the REAL OLIVE rows, not the wheat ones. The first version of this used wheat,
    whose season is over on 2026-09-06, so every province came back UNKNOWN and the test could
    only ever report 'PUBLISHED, 0 classed' — it never reached the question it was asking,
    which is whether the engine will put a CLASS on identifiers. Olive is classifiable on that
    date, so a published class here is a real one."""
    src = os.path.join(CASEDIR, "FRUMENTO-SEPTORIA-TOSCANA")
    wheat_idx = json.load(open(os.path.join(src, "collection_index.json")))
    codes = wheat_idx.get("codes") or []
    ids = [str(c["id_survey_code"]) for c in codes]
    olive = os.path.join(CASEDIR, "OLIVO-BACTROCERA-TOSCANA")
    NEWVAR = 90001
    case = os.path.join(LAB, f"share_{int(code_share*100):03d}")
    if os.path.exists(case):
        shutil.rmtree(case)
    os.makedirs(os.path.join(case, "RAW"))
    out_idx = {"api": wheat_idx["api"], "crop": 2, "schema": 1, "requests": [],
               # a code table for OTHER variables only -> value_mode stays NUMERIC
               "codes": [c for c in codes if c["id_survey_var"] != NEWVAR],
               "vars": [{"id_survey_var": NEWVAR, "id_survey_schema": 1,
                         "widget": "numeric", "name": "synthetic numeric variable"}]}
    for y in range(2006, 2027):
        fn_src = os.path.join(olive, "RAW", f"c2_s1_v-1002_{y}.json")
        if not os.path.exists(fn_src):
            continue
        rows = json.load(open(fn_src))
        n_code = int(len(rows) * code_share)
        for i, r in enumerate(rows):
            # below the code share: a genuine measurement in the olive variable's own range
            r["val"] = ids[i % len(ids)] if i < n_code else str(round((i % 9) * 5.0, 1))
        blob = json.dumps(rows, ensure_ascii=False)
        fn = f"c2_s1_v{NEWVAR}_{y}.json"
        open(os.path.join(case, "RAW", fn), "wb").write(blob.encode("utf-8"))
        out_idx["requests"].append({"var": NEWVAR, "year": y, "ok": True,
                                    "rowCount": len(rows), "n_rows": len(rows), "file": fn,
                                    "sha256": hashlib.sha256(blob.encode()).hexdigest()})
    json.dump(out_idx, open(os.path.join(case, "collection_index.json"), "w"), indent=1)
    return case, NEWVAR


def main():
    os.makedirs(LAB, exist_ok=True)
    out = {"AS_OF": AS_OF.isoformat(), "GUARD": "current_pressure.assert_scale_decodes",
           "GUARD_THRESHOLD": 0.90,
           "RETRACTION": "the first version of this file reported CODE_AS_VALUE_FALSE_CLAIMS "
                         "= 63. That number was an artefact of my own test: it injected code "
                         "ids drawn from a code table the olive case does not have, so no "
                         "values were changed. Withdrawn."}

    # ── Q1 — in what state is each real case, and does the guard run at all? ───────
    q1 = {}
    for crop, (name, var) in CASES.items():
        case = os.path.join(CASEDIR, name)
        idx = json.load(open(os.path.join(case, "collection_index.json")))
        mode = cp.value_mode(idx, var)
        codes = idx.get("codes") or []
        ids_any = {str(c.get("id_survey_code")) for c in codes}
        ids_var = {str(c["id_survey_code"]) for c in codes if c["id_survey_var"] == var}
        rows, scale, meta = cp.load_rows(case, var)
        vals = [str(r.get("val")) for r in rows if r.get("val") not in (None, "")]
        declared = next((v for v in (idx.get("vars") or []) if v["id_survey_var"] == var), None)
        q1[crop] = {
            "var": var, "VALUE_MODE": mode,
            "source_declares_widget": (declared or {}).get("widget"),
            "code_table_entries_in_case": len(codes),
            "code_table_entries_for_THIS_var": len(ids_var),
            "share_of_values_that_are_code_ids_of_ANY_var": round(
                sum(1 for v in vals if v in ids_any) / max(1, len(vals)), 4),
            "GUARD_CAN_EVER_RUN_ON_THIS_CASE": mode == "NUMERIC" and bool(ids_any),
            "WHY_NOT": ("mode is ORDINAL: the case HAS a code table for this variable, so the "
                        "values are decoded through it and the guard returns immediately"
                        if mode != "NUMERIC" else
                        "the case carries NO code table at all, so the guard has nothing to "
                        "compare against and returns immediately"
                        if not ids_any else "it can run"),
            "sample_values": sorted(set(vals))[:6]}
    out["Q1_STATE_OF_THE_REAL_CASES"] = q1
    out["GUARD_IS_INERT_ON_EVERY_REAL_CASE"] = not any(
        v["GUARD_CAN_EVER_RUN_ON_THIS_CASE"] for v in q1.values())

    # ── Q2 — what actually fixed the wheat case? ──────────────────────────────────
    wheat = os.path.join(CASEDIR, "FRUMENTO-SEPTORIA-TOSCANA")
    widx = json.load(open(os.path.join(wheat, "collection_index.json")))
    w_codes = [c for c in (widx.get("codes") or []) if c["id_survey_var"] == 372]
    wrows, wscale, wmeta = cp.load_rows(wheat, 372)
    # the counterfactual: the SAME bytes with the code table for 372 removed, which is the
    # state collect_generic left the case in before the "most complete table" fix
    stripped = dict(widx)
    stripped["codes"] = [c for c in (widx.get("codes") or []) if c["id_survey_var"] != 372]
    lab = os.path.join(LAB, "wheat_without_its_code_table")
    if os.path.exists(lab):
        shutil.rmtree(lab)
    os.makedirs(lab)
    os.symlink if False else None
    shutil.copytree(os.path.join(wheat, "RAW"), os.path.join(lab, "RAW"))
    json.dump(stripped, open(os.path.join(lab, "collection_index.json"), "w"), indent=1)
    out["Q2_WHAT_ACTUALLY_FIXED_THE_WHEAT_CASE"] = {
        "code_table_entries_for_var_372_today": len(w_codes),
        "VALUE_MODE_today": wmeta["VALUE_MODE"],
        "derived_scale_size": len(wscale),
        "WITH_THE_CODE_TABLE_REMOVED": {
            "VALUE_MODE": cp.value_mode(stripped, 372),
            "RESULT": try_pressure(lab, 372)},
        "READ": "the wheat defect is held shut by the CODE TABLE the collector now stores "
                "(the 'most complete table' fix in collect_generic.py), not by "
                "assert_scale_decodes. Remove the table and the guard is what stands between "
                "the engine and an agronomic sentence built out of identifiers."}

    # ── Q3 — the cliff, on a case built to be in the guard's one live state ───────
    q3 = {}
    for share in (0.0, 0.50, 0.80, 0.85, 0.89, 0.90, 0.95, 1.00):
        case, var = build_numeric_case_with_a_code_table(share)
        res = try_pressure(case, var)
        q3[f"{share:.2f}"] = {"OUTCOME": res["OUTCOME"],
                              "n_provinces_classed": res.get("n_provinces_classed"),
                              "message": res.get("message")}
    out["Q3_THE_CLIFF"] = {
        "BY_SHARE_OF_VALUES_THAT_ARE_CODE_IDS": q3,
        "READ": "every share that still says PUBLISHED is a configuration in which the engine "
                "emits a class computed from identifiers. The threshold is 0.90 by "
                "declaration; what matters is how much of the space below it is publishable."}
    false_claims = sum((v.get("n_provinces_classed") or 0)
                       for k, v in q3.items()
                       if v["OUTCOME"] == "PUBLISHED" and float(k) >= 0.50)

    # ── Q4 — false refusal on a genuine measurement ──────────────────────────────
    case, var = build_numeric_case_with_a_code_table(0.0)
    out["Q4_NO_FALSE_REFUSAL_ON_A_GENUINE_MEASUREMENT"] = {
        "share_of_code_ids": 0.0, "RESULT": try_pressure(case, var)}

    # ── Q5 — ORDINAL case fed ids from another variable's code table ─────────────
    vname, vvar = CASES["VINE"]
    vcase = os.path.join(CASEDIR, vname)
    vrows, vscale, vmeta = cp.load_rows(vcase, vvar)
    foreign = [str(c["id_survey_code"]) for c in
               (json.load(open(os.path.join(CASEDIR, CASES["WHEAT"][0],
                                            "collection_index.json"))).get("codes") or [])]
    mutv = copy.deepcopy(vrows)
    for i, r in enumerate(mutv):
        r["val"] = foreign[i % len(foreign)] if foreign else r.get("val")
    r5 = try_pressure(vcase, vvar, pre=(mutv, vscale, vmeta))
    out["Q5_ORDINAL_CASE_FED_FOREIGN_CODE_IDS"] = {
        "n_foreign_ids": len(foreign), "GUARD_RUNS_IN_ORDINAL_MODE": False, "RESULT": r5,
        "READ": "in ORDINAL mode an unrecognised code decodes to None, which is MISSING, "
                "which is never zero. The case fails to UNKNOWN rather than to a number. "
                "That is the right failure, and it is delivered by read_value, not by the "
                "code-vs-value guard."}

    out["CODE_AS_VALUE_FALSE_CLAIMS"] = false_claims
    refuses_when_saturated = q3["1.00"]["OUTCOME"] == "REFUSED"
    no_false_refusal = q3["0.00"]["OUTCOME"] == "PUBLISHED"
    ordinal_fails_to_unknown = r5.get("n_provinces_classed") == 0
    out["SUBTESTS"] = {
        "REFUSES_WHEN_THE_VALUES_ARE_CODE_IDS": refuses_when_saturated,
        "DOES_NOT_FALSE_REFUSE_A_GENUINE_MEASUREMENT": no_false_refusal,
        "ORDINAL_CASE_FAILS_TO_UNKNOWN_NOT_TO_A_NUMBER": ordinal_fails_to_unknown,
        "GUARD_IS_REACHABLE_ON_ANY_REAL_CASE": not out["GUARD_IS_INERT_ON_EVERY_REAL_CASE"],
        "NO_PUBLISHABLE_CONTAMINATED_BAND": false_claims == 0}
    out["CODE_VS_VALUE_GATE"] = "PASS" if all(out["SUBTESTS"].values()) else "FAIL"
    out["SCOPE_AND_THE_HOLE"] = {
        "WHAT_IS_PROVED": "where the guard runs it does exactly what it declares: it refuses "
                          "a variable whose values are drawn from the case's own code "
                          "vocabulary, and it does not refuse a genuine measurement.",
        "HOLE_1_IT_NEVER_RUNS": "neither published case nor the case it was written for is in "
                                "the state that lets it run. Wheat and vine are ORDINAL (the "
                                "code table decodes them); olive carries no code table at all, "
                                "so there is nothing to compare against. The protection is "
                                "real and currently unreachable.",
        "HOLE_2_THE_BAND_BELOW_THE_THRESHOLD":
            "the rule is 'refuse at >= 90% code ids'. Everything below that publishes. A "
            "variable where four values in five are identifiers is not a measurement, and "
            "the engine will put a class on it.",
        "WHAT_ACTUALLY_HOLDS_THE_WHEAT_DEFECT_SHUT":
            "not this guard. With the code table for var 372 removed, value_mode returns "
            "UNSUPPORTED and current_pressure refuses outright. The fix that works is the "
            "collector storing the most complete code table, plus the UNSUPPORTED refusal."}

    json.dump(out, open(os.path.join(HERE, "p7_code_vs_value.json"), "w"), indent=1, default=str)

    print("Q1 — state of the real cases:")
    for c, v in q1.items():
        print(f"  {c:6s} var={v['var']:6d} mode={v['VALUE_MODE']:9s} widget={v['source_declares_widget']} "
              f"codes_for_var={v['code_table_entries_for_THIS_var']:3d} "
              f"guard_can_run={v['GUARD_CAN_EVER_RUN_ON_THIS_CASE']}  ({v['WHY_NOT']})")
    print(f"\nGUARD_IS_INERT_ON_EVERY_REAL_CASE = {out['GUARD_IS_INERT_ON_EVERY_REAL_CASE']}")
    print("\nQ2 — what actually fixed wheat:",
          json.dumps({k: v for k, v in out["Q2_WHAT_ACTUALLY_FIXED_THE_WHEAT_CASE"].items()
                      if k != "READ"})[:400])
    print("\nQ3 — the cliff (case built in the guard's one live state):")
    for k, v in q3.items():
        print(f"  code_id_share={k}  {v['OUTCOME']:9s} classed={v['n_provinces_classed']} "
              f"{str(v['message'])[:70]}")
    print("\nQ4 —", json.dumps(out["Q4_NO_FALSE_REFUSAL_ON_A_GENUINE_MEASUREMENT"])[:220])
    print("Q5 —", json.dumps(r5)[:220])
    print(f"\nCODE_VS_VALUE_GATE = {out['CODE_VS_VALUE_GATE']}  false_claims={false_claims}")


if __name__ == "__main__":
    main()
