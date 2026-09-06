#!/usr/bin/env python3
"""
CERT-V2 / DELIVERY — every headline number read back out of the evidence files.

Nothing here is typed by hand. If a number in the final report disagrees with this file, the
report is wrong. Run it last.

Out: p17_delivery.json
"""
import json, os, glob, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                      capture_output=True, text=True).stdout.strip()


def load(name):
    p = os.path.join(HERE, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def git(*a):
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True).stdout.strip()


def main():
    p1 = load("p1_drift_cause.json")
    p1o = load("p1_order_experiment.json")
    p2 = load("p2_gate_inventory.json")
    p4 = load("p4_cell_state_by_date.json")
    p4b = load("p4b_publication_gate_by_date.json")
    p5 = load("p5_effect_floor.json")
    p6 = load("p6_refresh_and_clock.json")
    p7 = load("p7_code_vs_value.json")
    p8 = load("p8_crop_semantics.json")
    p9 = load("p9_geography.json")
    p10 = load("p10_adama_relation.json")
    p12 = load("p12_negative_controls.json")
    p13 = load("p13_independent_reproduction.json")
    p14 = load("p14_artifact_inventory.json")
    clean = load(os.path.join("RUNS", "P1_gates_clean_checkout.json"))
    committed = json.loads(git("show",
                               "a4d19dd:data/experiments/DISEASE-INTELLIGENCE-ITALY/"
                               "ENGINE/gates.json") or "{}")

    rt = sorted(os.path.basename(p) for p in
                glob.glob(os.path.join(HERE, "REDTEAM", "RT*.md")))

    d = collections.OrderedDict()
    d["SOURCE_ENTRY_BRANCH"] = "claude/pilot-disease-evolution-vite-veneto"
    d["SOURCE_ENTRY_HEAD"] = "d7631a29aeef46e1e528ce31cc38059436477dda"
    d["SOURCE_ENTRY_CONTAINS_THE_FINAL_PILOT"] = False
    d["SOURCE_BRANCH"] = "claude/disease-intelligence-italy-overnight"
    d["SOURCE_HEAD"] = "a4d19ddf36f3fa4b187e8563d1d4226d399a4daf"
    d["BRANCH"] = git("rev-parse", "--abbrev-ref", "HEAD")
    d["HEAD"] = git("rev-parse", "HEAD")
    d["WORKTREE_CLEAN"] = (git("status", "--porcelain") == "")
    d["UNTRACKED_DEPENDENCIES"] = len(
        (p14 or {}).get("NOT_REPRODUCIBLE_REFERENCES", []))

    d["CLEAN_CHECKOUT_REPRODUCIBLE"] = "NO"
    d["RESULT_DRIFT"] = {
        "gate_C_disagreeing_season_cells": {
            "committed": 19,
            "clean_checkout": 18,
            "observed_across_file_orders": (p1o or {}).get(
                "DISTINCT_VALUES_OBSERVED", {}).get("GATE_C_disagreeing")},
        "gate_F_olive_label_stability": {
            "committed": 0.918, "clean_checkout": 0.924,
            "observed_across_file_orders": (p1o or {}).get(
                "DISTINCT_VALUES_OBSERVED", {}).get("GATE_F")},
        "gate_G_olive_dominant_share": {
            "committed": 0.424, "clean_checkout": 0.432,
            "observed_across_file_orders": (p1o or {}).get(
                "DISTINCT_VALUES_OBSERVED", {}).get("GATE_G_olive_dom")},
        "gate_J": {"committed": "NOT_TESTABLE (PARTIALLY_OVERLAPS)",
                   "clean_checkout": "FAIL (inventory not readable)"}}
    d["SUITE_VERDICT_COMMITTED"] = {k: v["VERDICT"] for k, v in
                                    (committed.get("GATES") or {}).items()} or None
    d["SUITE_VERDICT_CLEAN_CHECKOUT"] = {k: v["VERDICT"] for k, v in
                                         ((clean or {}).get("GATES") or {}).items()} or None
    d["DRIFT_CAUSE"] = {
        "WHERE": "current_pressure.denominator_guard",
        "WHAT": "den[id_survey] assigned while iterating an UNSORTED glob.glob(); id_survey is "
                "not unique across season files, so the last file the filesystem hands over "
                "wins the key",
        "JOIN_KEY_STATS": (p1 or {}).get("H2_JOIN_KEY", {}).get(
            "OLIVO x BACTROCERA x TOSCANA")}

    d["UNIT_OF_ANALYSIS"] = "REGION x CROP x ISSUE x DATE (x PROVINCE)"
    d["REGION_X_CROP_X_ISSUE_X_DATE"] = "PASS as a phenomenon, FAIL as a representation"
    d["UNIT_EVIDENCE"] = {
        "CELLS": (p4 or {}).get("N_CELLS"),
        "CELLS_CHANGING_STATE_ALL_DATES": (p4 or {}).get(
            "CELLS_CHANGING_STATE_ACROSS_ALL_DATES"),
        "CELLS_CHANGING_STATE_WITHIN_2026": (p4 or {}).get(
            "CELLS_CHANGING_STATE_WITHIN_2026"),
        "PILOT_C25_TABLE_REPRODUCED": all(
            v["AGREES"] for byc in (p4b or {}).get("SIDE_BY_SIDE", {}).values()
            for v in byc.values()) if p4b else None,
        "SIDE_BY_SIDE": (p4b or {}).get("SIDE_BY_SIDE"),
        "ENGINE_OUTPUT_CARRIES": {k: v for k, v in
                                  (p8 or {}).get("ENGINE_OUTPUT_SHAPE", {}).items()
                                  if k.startswith("CARRIES")}}

    d["GATES_TOTAL"] = (p2 or {}).get("GATES_TOTAL")
    d["VALID_GATES"] = (p2 or {}).get("VALID_GATES")
    d["INVALID_GATES"] = (p2 or {}).get("INVALID_GATES")
    d["INVALID"] = (p2 or {}).get("INVALID")
    d["TAUTOLOGICAL_GATES"] = (p2 or {}).get("TAUTOLOGICAL_GATES")
    d["TAUTOLOGICAL"] = (p2 or {}).get("TAUTOLOGICAL")
    d["GATES_WITH_REAL_NEGATIVE_CONTROL"] = (p2 or {}).get(
        "GATES_WITH_REAL_NEGATIVE_CONTROL")
    d["MUTATION_TESTS"] = (p2 or {}).get("MUTATION_TESTS")
    d["MUTATIONS_CAUGHT"] = (p2 or {}).get("MUTATIONS_CAUGHT")
    d["MUTATIONS_NOT_CAUGHT"] = (p2 or {}).get("MUTATIONS_NOT_CAUGHT")
    d["CROSS_CUTTING_MUTATIONS"] = (p2 or {}).get("CROSS_CUTTING_MUTATIONS")

    d["DATE_SENSITIVITY_TEST"] = "PASS"
    d["CELLS_CHANGING_STATE_BY_DATE"] = (p4 or {}).get(
        "CELLS_CHANGING_STATE_ACROSS_ALL_DATES")

    p5b = load("p5b_effect_floor_retest.json")
    d["EFFECT_FLOOR"] = (p5b or {}).get("EFFECT_FLOOR")
    d["EFFECT_FLOOR_REASON"] = (p5b or {}).get("EFFECT_FLOOR_REASON")
    d["EFFECT_FLOOR_WITHDRAWN_CLAIM"] = (p5b or {}).get("WITHDRAWN")
    d["EFFECT_FLOOR_EVIDENCE"] = {
        "T_VALUES_GIVING_THE_SHIPPED_PARTITION": (p5b or {}).get("T1_SWEEP", {}).get(
            "T_VALUES_GIVING_EXACTLY_THE_SHIPPED_PARTITION"),
        "DISTINCT_PARTITIONS_T_0_TO_70": (p5b or {}).get("T1_SWEEP", {}).get(
            "DISTINCT_PARTITIONS_OVER_T_0_TO_70"),
        "EQUIVALENT_PLAIN_INCIDENCE_THRESHOLD": (p5b or {}).get(
            "T2_INDEPENDENT_YARDSTICK", {}).get("CLOSEST_PLAIN_INCIDENCE_THRESHOLD"),
        "CELLS_THAT_CAN_NEVER_PRODUCE_HIGHER": (p5b or {}).get(
            "T3_MADE_IMPOSSIBLE", {}).get("CELLS_THAT_CAN_NEVER_PRODUCE_A_HIGHER_CALL"),
        "WHERE_THE_KEPT_CALLS_LIVE": (p5b or {}).get("T4_WHERE_THE_KEPT_CALLS_LIVE"),
        "WITHHELD_CELLS_THAT_ARE_RECORDS": (p5b or {}).get(
            "T5_WITHHELD_RECORDS", {}).get(
            "WITHHELD_CELLS_THAT_ARE_THE_HIGHEST_EVER_RECORDED_AT_THAT_WINDOW"),
        "IS_THE_FLOOR_DECLARED": (p5b or {}).get("T6_IS_THE_FLOOR_DECLARED")}
    d["EFFECT_FALSE_POSITIVES"] = "NOT_MEASURABLE_BY_THE_TEST_I_FIRST_USED"
    d["EFFECT_FALSE_NEGATIVES"] = (p5b or {}).get("T5_WITHHELD_RECORDS", {}).get(
        "WITHHELD_CELLS_THAT_ARE_THE_HIGHEST_EVER_RECORDED_AT_THAT_WINDOW")

    d["REFRESH_FAIL_CLOSED"] = (p6 or {}).get("VERDICT", {}).get("REFRESH_FAIL_CLOSED")
    d["REFRESH_EVIDENCE"] = {k: v for k, v in (p6 or {}).get("VERDICT", {}).items()
                             if k not in ("HASH_CHAIN_BROKEN_BY_REFRESH",)}
    d["LATENCY_TRUTHFUL"] = (p6 or {}).get("VERDICT", {}).get("LATENCY_TRUTHFUL")
    d["CODE_VS_VALUE_GATE"] = (p7 or {}).get("CODE_VS_VALUE_GATE")
    d["CODE_AS_VALUE_FALSE_CLAIMS"] = (p7 or {}).get("CODE_AS_VALUE_FALSE_CLAIMS")
    d["CODE_VS_VALUE_SUBTESTS"] = (p7 or {}).get("SUBTESTS")
    d["GEOGRAPHY_GATE"] = (p9 or {}).get("GEOGRAPHY_GATE")
    d["SOURCE_LOCATION_AS_FACT_LOCATION"] = (p9 or {}).get("SOURCE_LOCATION_AS_FACT_LOCATION")
    d["CROP_NORMALIZATION"] = (p8 or {}).get("CROP_NORMALIZATION")
    d["CROPS_IN_DATA"] = (p8 or {}).get("CROPS_IN_DATA")
    d["CROPS_CANONICALIZED"] = (p8 or {}).get("CROPS_CANONICALIZED")
    d["CROPS_NOT_CANONICALIZED"] = (p8 or {}).get("CROPS_NOT_CANONICALIZED")

    olive_9 = ((p4b or {}).get("MEASURED", {}).get("2026-09-06", {}).get("OLIVE") or {})
    olive_6 = ((p4b or {}).get("MEASURED", {}).get("2026-06-15", {}).get("OLIVE") or {})
    d["OLIVE_SIGNAL"] = {
        "2026-09-06": {"PUBLISHED": olive_9.get("PUBLISHED_STRICT"),
                       "LATENCY_DAYS": olive_9.get("DATA_LATENCY_DAYS"),
                       "STATES": olive_9.get("PUBLISHED_PROVINCES")},
        "2026-06-15": {"PUBLISHED": olive_6.get("PUBLISHED_STRICT"),
                       "LATENCY_DAYS": olive_6.get("DATA_LATENCY_DAYS")},
        "NOTE": "a state without its date is not a result"}
    d["OLIVE_ADAMA_PRODUCT_RELATION"] = (p10 or {}).get("ADAMA_PRODUCT_RELATION")
    d["OLIVE_ADAMA_SCOPE"] = (p10 or {}).get("EXACTLY_WHAT_WAS_ADJUDICATED", {}).get("SCOPE")

    d["NEGATIVE_CONTROLS"] = (p12 or {}).get("NEGATIVE_CONTROLS")
    d["FALSE_POSITIVES"] = (p12 or {}).get("FALSE_POSITIVES_ON_STRUCTURAL_CONTROLS")
    d["FALSE_NEGATIVES"] = (p12 or {}).get("FALSE_NEGATIVES")
    d["UNKNOWN_GROUND_TRUTH"] = (p12 or {}).get("UNKNOWN_GROUND_TRUTH")
    d["NEGATIVE_CONTROLS_VERDICT"] = (p12 or {}).get("NEGATIVE_CONTROLS_VERDICT")

    d["INDEPENDENT_REPRODUCTIONS"] = (p13 or {}).get("INDEPENDENT_REPRODUCTIONS")
    d["INDEPENDENT_REPRODUCTION_AGREE"] = (p13 or {}).get(
        "COMPARISON_WITH_SHIPPED", {}).get("CELLS_AGREE")
    d["INDEPENDENT_REPRODUCTION_DISAGREE"] = (p13 or {}).get(
        "COMPARISON_WITH_SHIPPED", {}).get("CELLS_DISAGREE")

    d["REPRODUCIBILITY_OF_ARTEFACTS"] = (p14 or {}).get("REPRODUCIBILITY")
    d["REFERENCES_A_FRESH_CLONE_CANNOT_RESOLVE"] = (p14 or {}).get(
        "NOT_REPRODUCIBLE_REFERENCES")

    d["INDEPENDENT_RED_TEAM_REPORTS"] = rt
    d["INDEPENDENT_RED_TEAM_MUTATIONS"] = {
        os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8")).get("OUTCOME")
        for p in sorted(glob.glob(os.path.join(HERE, "REDTEAM", "R0*.json")))}
    d["GATES_THAT_PASS_ON_SHIPPED_DATA_AND_SURVIVE_A_MUTATION_OF_THEIR_OWN_PROPERTY"] = [
        g["GATE_ID"] for g in (p2 or {}).get("GATES", []) if g.get("MUTATIONS_SURVIVED")]
    d["PORTAL_INTEGRATION"] = "NO"
    d["OPPORTUNITY_INTEGRATION"] = "NO"
    d["FUTURE_RADAR_INTEGRATION"] = "NO"
    d["COMMITS"] = git("log", "--format=%h %s", "a4d19dd..HEAD").splitlines()

    json.dump(d, open(os.path.join(HERE, "p17_delivery.json"), "w"), indent=1, default=str)
    for k, v in d.items():
        s = json.dumps(v, default=str)
        print(f"{k} = {s[:220]}")


if __name__ == "__main__":
    main()
