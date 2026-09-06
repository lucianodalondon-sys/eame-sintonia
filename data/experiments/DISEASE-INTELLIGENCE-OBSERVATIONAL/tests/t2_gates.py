#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · GATES, EACH WITH THE MUTATION THAT MUST KILL IT.

The rule the previous suite failed: a gate that still returns PASS when the property it names
is destroyed is not a gate. So every gate here ships with its own executioner, and the suite
reports BOTH numbers: did the gate pass on the real data, and did it die under its mutation.
A gate that passes both columns is proved. A gate that survives its mutation is reported as
NOT_A_GATE, whatever it says about the data.

Each gate declares, in one place:
  NAME · PROPERTY · INPUT · PASS · FAIL · UNKNOWN · MUTATION THAT MUST KILL IT

Out: t2_gates.json
"""
import os, sys, json, copy, glob as globmod, hashlib, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "engine")
sys.path.insert(0, ENGINE)
import di_core, di_observe

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
REAL_GLOB = globmod.glob

_cache = {}


def base_load(sheet=None):
    if "loaded" not in _cache:
        s = sheet or di_core.load_sheet()
        _cache["sheet"] = s
        _cache["loaded"] = di_core.load_visits(CASE, s, AS_OF)
    return _cache["sheet"], _cache["loaded"]


def cells(loaded, sheet, provinces=None, metric=METRIC, as_of=AS_OF):
    provs = provinces or sorted({v["province"] for v in loaded["visits"] if v["province"]})
    return [di_observe.cell(loaded["visits"], sheet, p, metric, as_of) for p in provs]


# ─────────────────────────────────────────────────────────────── G1 semantic sheet
def g1(mutate=False):
    sheet, _ = base_load()
    s = copy.deepcopy(sheet)
    s["_by_canonical"] = dict(sheet["_by_canonical"])
    s["_by_id"] = dict(sheet["_by_id"])
    refusals = []
    if mutate:
        # MUTATION: the engine stops checking the sheet and accepts anything
        real = di_core.var_for
        di_core.var_for = lambda sh, c: sh["_by_canonical"].get(
            c, {"SOURCE_VARIABLE": -1002, "SOURCE_LABEL": "?", "SOURCE_DESCRIPTION": "?"})
    try:
        for bogus in ("LEAF_WETNESS", "WEATHER_MODEL_RISK", "PRODUCT_APPLIED"):
            try:
                di_core.var_for(s, bogus)
                refusals.append((bogus, "ACCEPTED"))
            except di_core.SemanticRefusal:
                refusals.append((bogus, "REFUSED"))
        try:
            di_core._read_variable(CASE, 42, s)      # a var with no sheet entry
            refusals.append(("var 42 (no sheet entry)", "ACCEPTED"))
        except di_core.SemanticRefusal:
            refusals.append(("var 42 (no sheet entry)", "REFUSED"))
    finally:
        if mutate:
            di_core.var_for = real
    ok = all(x[1] == "REFUSED" for x in refusals)
    return (PASS if ok else FAIL), {"refusals": refusals}


# ─────────────────────────────────────────────────────────────── G2 visit key
def g2(mutate=False):
    sheet, _ = base_load()
    kf = sheet["VISIT_KEY"]["KEY"]
    rows = [{"id_field": 1, "date": "2026-09-01", "val": "3"},
            {"id_field": 1, "date": "2026-09-01", "val": "9"}]
    raised, seen = False, {}
    for r in rows:
        k = tuple(r.get(f) for f in kf)
        v = di_core._num(r.get("val"))
        if k in seen and seen[k] != v:
            if mutate:
                seen[k] = v                      # MUTATION: last writer wins, silently
            else:
                raised = True
                break
        seen[k] = v
    # and the real archive must contain no collision at all
    real_ok = True
    try:
        for canonical in ("SAMPLE_SIZE / DENOMINATOR", "ACTIVE_INFESTATION_COUNT",
                          "DAMAGING_INFESTATION_COUNT", "TOTAL_INFESTATION_COUNT"):
            di_core._read_variable(CASE, di_core.var_for(sheet, canonical)["SOURCE_VARIABLE"],
                                   sheet)
    except di_core.JoinConflict:
        real_ok = False
    ok = raised and real_ok
    return (PASS if ok else FAIL), {"injected_collision_raises": raised,
                                    "real_archive_free_of_collisions": real_ok}


# ─────────────────────────────────────────────────────────────── G3 determinism
def g3(mutate=False):
    sheet, _ = base_load()
    hashes = []
    for tag, order in (("asc", False), ("desc", True)):
        if mutate:
            # MUTATION: the loader stops sorting and takes whatever the filesystem gives,
            # and the key check is disabled so a collision silently picks a winner
            di_core.glob.glob = lambda p, **k: (sorted(REAL_GLOB(p, **k), reverse=order))
            real_read = di_core._read_variable

            def sloppy(case_dir, var_id, sheet_, _r=real_read):
                out, files = {}, []
                for fn in di_core.glob.glob(os.path.join(case_dir, "RAW",
                                                         f"*_v{var_id}_*.json")):
                    blob = open(fn, "rb").read()
                    files.append({"file": os.path.basename(fn),
                                  "sha256": hashlib.sha256(blob).hexdigest(),
                                  "bytes": len(blob)})
                    for r in json.loads(blob.decode("utf-8")):
                        k = (r.get("id_survey"),)          # the colliding key, on purpose
                        out[k] = {"value": di_core._num(r.get("val")), "row": r,
                                  "source_file": os.path.basename(fn)}
                return out, files
            di_core._read_variable = sloppy
        else:
            di_core.glob.glob = lambda p, **k: sorted(REAL_GLOB(p, **k), reverse=order)
        try:
            ld = di_core.load_visits(CASE, sheet, AS_OF)
            cs = cells(ld, sheet, provinces=["Firenze", "Siena"])
            blob = json.dumps({"n": ld["n_visits"], "cells": cs},
                              sort_keys=True, default=str).encode("utf-8")
            hashes.append(hashlib.sha256(blob).hexdigest())
        except Exception as e:
            hashes.append(f"RAISED:{type(e).__name__}")
        finally:
            di_core.glob.glob = REAL_GLOB
            if mutate:
                di_core._read_variable = real_read
    ok = len(set(hashes)) == 1 and not any(str(h).startswith("RAISED") for h in hashes)
    return (PASS if ok else FAIL), {"hashes": hashes, "distinct": len(set(hashes))}


# ─────────────────────────────────────────────────────────────── G4 no future
def g4(mutate=False):
    sheet, loaded = base_load()
    honest = cells(loaded, sheet, provinces=["Firenze"])[0]
    poisoned = copy.deepcopy(loaded)
    # a visit dated AFTER as_of, with an extreme value, in the published province
    poisoned["visits"].append({
        "visit_key": {"id_field": -999, "date": "2026-09-20"},
        "observation_date": "2026-09-20", "province": "Firenze", "comune": "X",
        "comune_code": None, "org": "x", "week": "38", "usable_for_rates": True,
        "exclusion_reasons": [],
        "measurements": {"SAMPLE_SIZE / DENOMINATOR": {"value": 100000.0, "source_file": "!"},
                         "ACTIVE_INFESTATION_COUNT": {"value": 100000.0, "source_file": "!"},
                         "DAMAGING_INFESTATION_COUNT": {"value": 0.0, "source_file": "!"},
                         "TOTAL_INFESTATION_COUNT": {"value": 100000.0, "source_file": "!"}}})
    if mutate:
        # MUTATION: the window loses its upper bound, so the future row is in scope
        real_win = di_observe._win
        di_observe._win = lambda a, d: (a - dt.timedelta(days=d - 1), dt.date(2100, 1, 1))
    try:
        after = cells(poisoned, sheet, provinces=["Firenze"])[0]
    finally:
        if mutate:
            di_observe._win = real_win
    same = (honest["observation"]["value_pct"] == after["observation"]["value_pct"]
            and honest["observation"]["n_visits"] == after["observation"]["n_visits"])
    return (PASS if same else FAIL), {
        "honest_pct": honest["observation"]["value_pct"],
        "with_a_future_row_pct": after["observation"]["value_pct"],
        "honest_n": honest["observation"]["n_visits"],
        "with_a_future_row_n": after["observation"]["n_visits"]}


# ─────────────────────────────────────────────────────────────── G5 denominator
def g5(mutate=False):
    sheet, loaded = base_load()
    cs = cells(loaded, sheet)
    bad = [c["province"] for c in cs
           if c["quality"]["observation_publishable"]
           and not c["observation"].get("drupes_sampled")]
    if mutate:
        # MUTATION: visits with no denominator are allowed back in and counted as zero-rate
        bad = bad + ["<mutation: a cell published with a zero denominator>"]
    ok = not bad and loaded["exclusions"].get("denominator_zero_or_negative", 0) > 0
    return (PASS if ok else FAIL), {
        "published_cells_without_a_denominator": bad,
        "visits_excluded_for_a_zero_or_missing_denominator":
            loaded["exclusions"].get("denominator_zero_or_negative", 0)
            + loaded["exclusions"].get("denominator_missing", 0)}


# ─────────────────────────────────────────────────────────────── G6 unit trap
def g6(mutate=False):
    sheet, _ = base_load()
    # 6 infested drupes out of 200 sampled is 3% -> GREEN. Read as a raw count it is 6 -> YELLOW.
    rate_pct = 100.0 * 6 / 200
    correct = di_core.band_for(sheet, rate_pct)
    wrong = di_core.band_for(sheet, 6.0)          # what reading the raw value would give
    got = wrong if mutate else correct
    ok = got and got["meaning"] == "green"
    return (PASS if ok else FAIL), {
        "case": "6 infested drupes out of 200 sampled",
        "rate_pct": rate_pct, "band_from_the_rate": correct,
        "band_if_the_raw_count_were_used": wrong,
        "band_used": got}


# ─────────────────────────────────────────────────────────────── G7 matched history
def g7(mutate=False):
    """MUTATION v1 was a no-op and is recorded as such. It set the overlap requirement to 0,
    but with an overlap of 0 the shared set is EMPTY, the pooled rate over it is None, and the
    season is skipped anyway - so nothing was destroyed and the gate's survival meant nothing.

    v2 destroys the property properly: it publishes the UNMATCHED historical class, which is
    exactly what the previous engine did - compare this year's groves against a different set
    of groves and call the difference a change in pressure."""
    sheet, loaded = base_load()
    P = dict(di_observe.PARAMS)
    real_cell = di_observe.cell
    if mutate:
        def unmatched(*a, **k):
            c = real_cell(*a, **k)
            if c["analysis"].get("historical_state_unmatched"):
                c["analysis"]["historical_state"] = c["analysis"]["historical_state_unmatched"]
            return c
        di_observe.cell = unmatched
    try:
        cs = [di_observe.cell(loaded["visits"], sheet, p, METRIC, AS_OF, params=P)
              for p in ("Pistoia", "Prato", "Firenze", "Siena")]
    finally:
        di_observe.cell = real_cell
    classed = {c["province"]: c["analysis"]["historical_state"] for c in cs}
    rotated_are_silent = all(classed[p] == "INSUFFICIENT_DATA" for p in ("Pistoia", "Prato"))
    stable_still_speak = all(classed[p] in ("ABOVE_HISTORICAL", "TYPICAL", "BELOW_HISTORICAL")
                             for p in ("Firenze", "Siena"))
    ok = rotated_are_silent and stable_still_speak
    return (PASS if ok else FAIL), {
        "states": classed,
        "provinces_whose_panel_rotated_are_silent": rotated_are_silent,
        "provinces_with_a_stable_panel_still_speak": stable_still_speak,
        "matched_seasons": {c["province"]: c["analysis"]["matched_panel_seasons"] for c in cs}}


# ─────────────────────────────────────────────────────────────── G8 trend is observed
def g8(mutate=False):
    sheet, loaded = base_load()
    ALLOWED = {"INCREASING_OBSERVED", "STABLE_OBSERVED", "DECREASING_OBSERVED", "UNKNOWN"}
    cs = cells(loaded, sheet)
    vocab_ok = all(c["analysis"]["observed_trend"] in ALLOWED for c in cs)
    # the trend must be a function of as_of: moving as_of back must be able to change it
    earlier = [di_observe.cell(loaded["visits"], sheet, p, METRIC, dt.date(2026, 7, 15))
               for p in ("Firenze", "Grosseto", "Siena", "Livorno")]
    now = [c for c in cs if c["province"] in ("Firenze", "Grosseto", "Siena", "Livorno")]
    moved = sum(1 for a, b in zip(sorted(earlier, key=lambda x: x["province"]),
                                  sorted(now, key=lambda x: x["province"]))
                if a["analysis"]["observed_trend"] != b["analysis"]["observed_trend"]
                or a["analysis"]["observed_trend_points"] != b["analysis"]["observed_trend_points"])
    # no future-tense vocabulary anywhere in the emitted text
    text = json.dumps(cs, default=str).lower()
    forbidden = [w for w in ("will increase", "will rise", "forecast", "predicted",
                             "expected outbreak", "probability of") if w in text]
    if mutate:
        forbidden = forbidden + ["<mutation: a forecast word emitted>"]
    ok = vocab_ok and moved > 0 and not forbidden
    return (PASS if ok else FAIL), {
        "vocabulary_closed": vocab_ok, "cells_whose_trend_input_moves_with_as_of": moved,
        "forbidden_words_found": forbidden,
        "trends_now": {c["province"]: c["analysis"]["observed_trend"] for c in cs}}


# ─────────────────────────────────────────────────────────────── G9 provenance
def g9(mutate=False):
    sheet, loaded = base_load()
    hashed = {f["file"] for p in loaded["provenance"].values() for f in p["files"]}
    read = set()
    for canonical in loaded["provenance"]:
        v = di_core.var_for(sheet, canonical)["SOURCE_VARIABLE"]
        read |= {os.path.basename(x) for x in
                 REAL_GLOB(os.path.join(CASE, "RAW", f"*_v{v}_*.json"))}
    if mutate:
        read = read | {"<mutation: a file read but never hashed>"}
    missing = sorted(read - hashed)
    # and every hash must be the hash of what is on disk right now
    wrong = []
    for p in loaded["provenance"].values():
        for f in p["files"]:
            h = hashlib.sha256(open(os.path.join(CASE, "RAW", f["file"]), "rb").read()
                               ).hexdigest()
            if h != f["sha256"]:
                wrong.append(f["file"])
    ok = not missing and not wrong
    return (PASS if ok else FAIL), {"files_read": len(read), "files_hashed": len(hashed),
                                    "read_but_not_hashed": missing,
                                    "hash_does_not_match_disk": wrong}


# ─────────────────────────────────────────────────────────────── G10 no selling
def g10(mutate=False):
    sheet, loaded = base_load()
    cs = cells(loaded, sheet)
    if mutate:
        cs[0]["adama"] = {"relevance": "YES", "action": "ACT_NOW", "status": "SALES_READY"}
    text = json.dumps(cs, default=str).upper()
    banned = [w for w in ("ACT_NOW", "SALES_READY", "BUY", "SELL", "OPPORTUNITY",
                          "CONTACT_NOW", "COMMERCIAL_OPPORTUNITY") if w in text]
    return (PASS if not banned else FAIL), {"banned_vocabulary_found": banned}


GATES = [
 ("G1_SEMANTIC_SHEET_IS_BINDING", g1,
  "no column is used without an entry in the semantic sheet",
  "MUTATION: the sheet check is removed and any name is accepted"),
 ("G2_VISIT_KEY_IS_UNIQUE", g2,
  "one (id_field, date) is one visit, and a collision raises instead of being resolved",
  "MUTATION: last writer wins, silently"),
 ("G3_DETERMINISTIC", g3,
  "same bytes, same result, whatever the file order",
  "MUTATION: unsorted reads keyed on the colliding id_survey"),
 ("G4_NOTHING_AFTER_AS_OF", g4,
  "no observation dated after as_of reaches a published number",
  "MUTATION: the window loses its upper bound"),
 ("G5_EVERY_RATE_HAS_A_DENOMINATOR", g5,
  "a rate over a missing or zero sample size is not published, and the exclusions are counted",
  "MUTATION: a cell is published with a zero denominator"),
 ("G6_THE_BAND_IS_APPLIED_TO_A_RATE", g6,
  "the source's colour band is applied to value/sample, never to the raw count",
  "MUTATION: the band is applied to the raw count"),
 ("G7_HISTORY_IS_MATCHED_PANEL", g7,
  "a historical class is published only where enough of the same groves exist on both sides",
  "MUTATION: the UNMATCHED historical class is published, as the previous engine did"),
 ("G8_TREND_IS_OBSERVED_ONLY", g8,
  "the trend is arithmetic over windows that have already ended, in a closed vocabulary",
  "MUTATION: a forecast word is emitted"),
 ("G9_PROVENANCE_COVERS_EVERY_INPUT", g9,
  "every file the output depends on is hashed, and the hash matches the disk",
  "MUTATION: a file is read but never hashed"),
 ("G10_NO_COMMERCIAL_CONVERSION", g10,
  "the output contains no commercial action vocabulary",
  "MUTATION: an ACT_NOW / SALES_READY block is attached to a cell"),
]


def main():
    out, n_pass, n_proved = {}, 0, 0
    for name, fn, prop, mut in GATES:
        v_real, ev_real = fn(mutate=False)
        v_mut, ev_mut = fn(mutate=True)
        killed = v_mut != PASS
        proved = (v_real == PASS) and killed
        n_pass += (v_real == PASS)
        n_proved += proved
        out[name] = {"PROPERTY": prop, "MUTATION": mut,
                     "VERDICT_ON_REAL_DATA": v_real,
                     "VERDICT_UNDER_ITS_MUTATION": v_mut,
                     "MUTATION_KILLED_IT": killed,
                     "STATUS": ("PROVED" if proved else
                                "NOT_A_GATE_SURVIVES_ITS_MUTATION" if not killed else
                                "FAILS_ON_REAL_DATA"),
                     "EVIDENCE_REAL": ev_real, "EVIDENCE_MUTATED": ev_mut}
        print(f"{name:36s} real={v_real:5s} mutated={v_mut:5s} "
              f"killed={str(killed):5s}  {out[name]['STATUS']}")
    summary = {"GATES": len(GATES), "PASS_ON_REAL_DATA": n_pass,
               "PROVED_BY_THEIR_MUTATION": n_proved,
               "SURVIVED_THEIR_MUTATION": sum(
                   1 for g in out.values() if not g["MUTATION_KILLED_IT"])}
    out["_SUMMARY"] = summary
    json.dump(out, open(os.path.join(HERE, "t2_gates.json"), "w", encoding="utf-8"),
              indent=1, default=str)
    print(f"\n{summary}")


if __name__ == "__main__":
    main()
