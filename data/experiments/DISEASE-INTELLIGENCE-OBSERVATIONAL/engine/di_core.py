#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · CORE READER

Three rules, all of them enforced in code rather than promised in a docstring:

  1. NO COLUMN WITHOUT A SHEET ENTRY. Every variable read here must appear in
     S1-SEMANTICS/SOURCE-SEMANTIC-SHEET.json, and the caller must ask for it by its
     CANONICAL_MEANING, not by its number. Asking for a variable the sheet does not describe
     raises. The previous pilot lost a whole case to a folder name.

  2. ONE VISIT = ONE (id_field, date). Proved unique over 79,251 rows in all four collected
     variables. Files are read in sorted order; if the same key ever arrives twice with
     different values the loader RAISES instead of letting the filesystem pick a winner.

  3. NOTHING AFTER AS_OF. as_of is an argument, never a clock. Rows dated after it are
     dropped before anything else happens, and the count of what was dropped is returned.

Layer 1 only. This file computes no class, no baseline and no trend. It answers
"what was observed, how many observations, and of when".
"""
import json, os, glob, hashlib, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_PATH = os.path.join(HERE, "..", "S1-SEMANTICS", "SOURCE-SEMANTIC-SHEET.json")


class SemanticRefusal(Exception):
    """Raised when the engine is asked to use a column the sheet does not describe, or to
    use one for something the sheet forbids."""


class JoinConflict(Exception):
    """Raised when the visit key is not unique. Never resolved silently."""


def load_sheet(path=SHEET_PATH):
    s = json.load(open(path, encoding="utf-8"))
    s["_by_canonical"] = {v["CANONICAL_MEANING"]: v for v in s["VARIABLES"]}
    s["_by_id"] = {v["SOURCE_VARIABLE"]: v for v in s["VARIABLES"]}
    return s


def var_for(sheet, canonical):
    v = sheet["_by_canonical"].get(canonical)
    if v is None:
        raise SemanticRefusal(
            f"REFUSED: no variable in the semantic sheet has CANONICAL_MEANING={canonical!r}. "
            f"Known: {sorted(sheet['_by_canonical'])}. A column is not usable because its "
            f"name looks right.")
    return v


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def _read_variable(case_dir, var_id, sheet):
    """Every row of one variable, keyed by the visit key, in a deterministic order."""
    if var_id not in sheet["_by_id"]:
        raise SemanticRefusal(
            f"REFUSED: id_survey_var {var_id} has no entry in the semantic sheet.")
    key_fields = sheet["VISIT_KEY"]["KEY"]
    out, seen, files = {}, {}, []
    pattern = os.path.join(case_dir, "RAW", f"*_v{var_id}_*.json")
    for fn in sorted(glob.glob(pattern)):          # sorted: the filesystem does not decide
        blob = open(fn, "rb").read()
        files.append({"file": os.path.basename(fn),
                      "sha256": hashlib.sha256(blob).hexdigest(),
                      "bytes": len(blob)})
        for r in json.loads(blob.decode("utf-8")):
            k = tuple(r.get(f) for f in key_fields)
            if None in k:
                continue
            val = _num(r.get("val"))
            if k in seen and seen[k] != val:
                raise JoinConflict(
                    f"REFUSED: visit key {k} appears twice in variable {var_id} with "
                    f"different values ({seen[k]!r} then {val!r}). The key "
                    f"{key_fields} is not unique on this data and no winner will be picked "
                    f"for you.")
            seen[k] = val
            out[k] = {"value": val, "row": r, "source_file": os.path.basename(fn)}
    return out, files


def load_visits(case_dir, sheet, as_of, wanted=("SAMPLE_SIZE / DENOMINATOR",
                                                "ACTIVE_INFESTATION_COUNT",
                                                "DAMAGING_INFESTATION_COUNT",
                                                "TOTAL_INFESTATION_COUNT")):
    """One record per visit, carrying every requested canonical measurement, its provenance,
    and an explicit verdict on whether it may be used in a rate."""
    per_var, provenance = {}, {}
    for canonical in wanted:
        spec = var_for(sheet, canonical)
        rows, files = _read_variable(case_dir, spec["SOURCE_VARIABLE"], sheet)
        per_var[canonical] = rows
        provenance[canonical] = {"source_variable": spec["SOURCE_VARIABLE"],
                                 "source_label": spec["SOURCE_LABEL"],
                                 "source_description": spec["SOURCE_DESCRIPTION"],
                                 "files": files}

    denom_key = "SAMPLE_SIZE / DENOMINATOR"
    keys = sorted(set().union(*[set(v) for v in per_var.values()]), key=lambda t: (str(t[1]), str(t[0])))

    visits, dropped_future, excluded = [], 0, collections.Counter()
    for k in keys:
        any_row = next((per_var[c][k]["row"] for c in wanted if k in per_var[c]), None)
        if any_row is None:
            continue
        try:
            d = dt.date.fromisoformat(str(any_row.get("date")))
        except (TypeError, ValueError):
            excluded["unparseable_date"] += 1
            continue
        if d > as_of:                               # nothing after as_of, ever
            dropped_future += 1
            continue

        rec = {"visit_key": {"id_field": k[0], "date": k[1]},
               "observation_date": d.isoformat(),
               "province": any_row.get("nome_area"),
               "comune": any_row.get("name_4"),
               "comune_code": any_row.get("admin_code"),
               "org": any_row.get("org_name"),
               "week": any_row.get("week"),
               "measurements": {}, "usable_for_rates": True, "exclusion_reasons": []}
        for c in wanted:
            cell = per_var[c].get(k)
            rec["measurements"][c] = {
                "value": None if cell is None else cell["value"],
                "source_file": None if cell is None else cell["source_file"]}

        # Usability is decided PER MEASUREMENT, not per visit.
        #
        # The first version marked the WHOLE visit unusable when any column failed, so a visit
        # whose ACTIVE count is a clean 7 of 100 was dropped from the ACTIVE rate because its
        # TOTAL column read 106 of 100. That couples metrics which have nothing to do with each
        # other and quietly throws away good observations. Found by the independent
        # reproduction (t4), which read only the two columns it needed and therefore kept them.
        n = rec["measurements"].get(denom_key, {}).get("value")
        denom_bad = None
        if n is None:
            denom_bad = "denominator_missing"
        elif n <= 0:
            denom_bad = "denominator_zero_or_negative"
        rec["usable_by_measurement"] = {}
        for c in wanted:
            if c == denom_key:
                continue
            reasons = []
            if denom_bad:
                reasons.append(denom_bad)
            v = rec["measurements"][c]["value"]
            if v is None:
                reasons.append("value_missing")
            elif v < 0:
                reasons.append("negative_count")
            elif n is not None and n > 0 and v > n:
                reasons.append("count_exceeds_sample")
            rec["usable_by_measurement"][c] = {"usable": not reasons, "reasons": reasons}
            for r in reasons:
                excluded[f"{r}:{c}"] += 1
        # kept for readers that want a single flag: usable for at least one measurement
        rec["usable_for_rates"] = any(x["usable"]
                                      for x in rec["usable_by_measurement"].values())
        rec["exclusion_reasons"] = sorted(
            {f"{r}:{c}" for c, x in rec["usable_by_measurement"].items()
             for r in x["reasons"]})
        visits.append(rec)

    return {"AS_OF": as_of.isoformat(),
            "VISIT_KEY": sheet["VISIT_KEY"]["KEY"],
            "n_visits": len(visits),
            "n_visits_usable_for_at_least_one_measurement":
                sum(1 for v in visits if v["usable_for_rates"]),
            "n_visits_usable_by_measurement": {
                c: sum(1 for v in visits
                       if v.get("usable_by_measurement", {}).get(c, {}).get("usable"))
                for c in wanted if c != "SAMPLE_SIZE / DENOMINATOR"},
            "n_rows_dropped_because_dated_after_as_of": dropped_future,
            "exclusions": dict(sorted(excluded.items())),
            "provenance": provenance,
            "visits": visits}


def band_for(sheet, pct):
    """The SOURCE's own colour band, applied to a rate expressed in percent.
    Never applied to a raw count: see UNIT_TRAP in the sheet."""
    if pct is None:
        return None
    chosen = None
    for b in sheet["SOURCE_ACTION_BANDS"]["BANDS"]:
        if pct >= b["from_pct"] and (b["to_pct"] is None or pct < b["to_pct"] or
                                     (b["from_pct"] == 0 and pct == 0)):
            chosen = b
    if pct == 0:
        chosen = sheet["SOURCE_ACTION_BANDS"]["BANDS"][0]
    return None if chosen is None else {"label": chosen["label"],
                                        "meaning": chosen.get("meaning", "none"),
                                        "source": "the source's own legend"}


if __name__ == "__main__":
    import sys
    sheet = load_sheet()
    case = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                        "CASES", "OLIVO-BACTROCERA-TOSCANA"))
    as_of = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 9, 6)
    r = load_visits(case, sheet, as_of)
    print(f"AS_OF {r['AS_OF']}  visit key {r['VISIT_KEY']}")
    print(f"  visits loaded              {r['n_visits']:,}")
    print(f"  usable for >=1 measurement {r['n_visits_usable_for_at_least_one_measurement']:,}")
    for c, n in r["n_visits_usable_by_measurement"].items():
        print(f"    usable for {c:32s} {n:,}")
    print(f"  dropped: dated after as_of {r['n_rows_dropped_because_dated_after_as_of']:,}")
    print(f"  exclusions                 {r['exclusions']}")
    for c, p in r["provenance"].items():
        print(f"  {c:34s} var {p['source_variable']:>6} '{p['source_label']}' "
              f"({p['source_description']})  {len(p['files'])} files hashed")
