#!/usr/bin/env python3
"""
RT2 / A4 — CAN A FUTURE-DATED OBSERVATION REACH A PUBLISHED NUMBER?

G4 in t2_gates.py injects the future row into loaded["visits"], i.e. AFTER di_core has
already filtered, and then checks only observation.value_pct and observation.n_visits.
This probe attacks all the places G4 does not look:

  F1  a future row in the RAW BYTES, so it goes through di_core's filter — end to end,
      on a lab copy of the real case, comparing every published field.
  F2  the BASELINE and MATCHED-PANEL windows, and the TREND windows, not just the
      observation window.
  F3  the date parser: what strings does dt.date.fromisoformat accept, and can any of them
      make a future date look like a past one (or vice versa)?
  F4  the refresh's own clock: validate() computes LAST_GOOD_OBSERVATION_AT as
      max(date) over the payload with NO as_of bound at all.
"""
import os, sys, json, shutil, copy, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe, di_refresh

SRC = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA"))
LAB = os.path.join(HERE, "_lab_future")
AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
out = {}
sheet = di_core.load_sheet()


def build(poison_dates=()):
    """A copy of the real archive; optionally with poisoned rows appended to 2026."""
    if os.path.exists(LAB):
        shutil.rmtree(LAB)
    os.makedirs(os.path.join(LAB, "RAW"))
    for fn in os.listdir(os.path.join(SRC, "RAW")):
        shutil.copyfile(os.path.join(SRC, "RAW", fn), os.path.join(LAB, "RAW", fn))
    if not poison_dates:
        return
    for var, val in ((1, "100000"), (-1001, "100000"), (-1002, "0"), (-1003, "100000")):
        p = os.path.join(LAB, "RAW", f"c2_s1_v{var}_2026.json")
        rows = json.load(open(p, encoding="utf-8"))
        template = rows[0]
        for j, dstr in enumerate(poison_dates):
            rows.append(dict(template, id_field=-900000 - j, date=dstr, val=val,
                             nome_area="Firenze", org_name="RT2", id_survey=f"rt2{j}"))
        json.dump(rows, open(p, "w", encoding="utf-8"), ensure_ascii=False)


def fullcell(case, prov, as_of=AS_OF):
    ld = di_core.load_visits(case, sheet, as_of)
    c = di_observe.cell(ld["visits"], sheet, prov, METRIC, as_of)
    return ld, c


def flat(c):
    a, o = c["analysis"], c["observation"]
    return {"value_pct": o["value_pct"], "n_visits": o["n_visits"],
            "n_sites": o["n_sites"], "drupes_sampled": o["drupes_sampled"],
            "infested_drupes": o.get("infested_drupes"),
            "last_observation": o["last_observation"],
            "per_visit_rate_pct_max": o.get("per_visit_rate_pct_max"),
            "source_band": (o.get("source_band") or {}).get("meaning"),
            "baseline_n": a["baseline_n"], "baseline_median": a["baseline_rate_pct_median"],
            "matched_panel_seasons": a["matched_panel_seasons"],
            "historical_state": a["historical_state"],
            "trend": a["observed_trend"],
            "trend_points": [(p["window_end"], p["rate_pct"]) for p in
                             a["observed_trend_points"]],
            "panel_overlap": a["panel_overlap_with_baseline_seasons"]}


# ── F1 / F2: future rows in the raw bytes, at several distances ─────────────
build()
ld0, c0 = fullcell(LAB, "Firenze")
honest = flat(c0)

POISON = ["2026-09-07",   # one day after as_of
          "2026-09-20",   # the date G4 uses
          "2026-12-31",   # end of the current season
          "2027-08-20",   # next season, inside next year's calendar window
          "2099-08-20"]   # absurd
build(POISON)
ld1, c1 = fullcell(LAB, "Firenze")
poisoned = flat(c1)
out["F1_FUTURE_ROWS_IN_THE_RAW_BYTES"] = {
    "poison_dates": POISON,
    "poison_value": "100000 infested of 100000 sampled = 100% in Firenze",
    "rows_dropped_because_dated_after_as_of":
        ld1["n_rows_dropped_because_dated_after_as_of"],
    "rows_dropped_in_the_clean_run": ld0["n_rows_dropped_because_dated_after_as_of"],
    "visits_loaded_clean": ld0["n_visits"], "visits_loaded_poisoned": ld1["n_visits"],
    "HONEST": honest, "POISONED": poisoned,
    "FIELDS_THAT_MOVED": [k for k in honest if honest[k] != poisoned[k]],
    "IDENTICAL": honest == poisoned}

# F2b: does a future row change ANY province, or any other metric?
allmoved = {}
for prov in sorted({v["province"] for v in ld0["visits"] if v["province"]}):
    for metric in ("ACTIVE_INFESTATION_COUNT", "TOTAL_INFESTATION_COUNT"):
        a = flat(di_observe.cell(ld0["visits"], sheet, prov, metric, AS_OF))
        b = flat(di_observe.cell(ld1["visits"], sheet, prov, metric, AS_OF))
        if a != b:
            allmoved[f"{prov}/{metric}"] = [k for k in a if a[k] != b[k]]
out["F2_EVERY_PROVINCE_EVERY_METRIC"] = {
    "cells_compared": 20, "cells_that_moved": len(allmoved), "detail": allmoved}

# F2c: an as_of chosen so that NEXT season's poisoned row sits inside a BASELINE window
#      (as_of 2028-08-20 -> baseline window for season 2027 is 2027-07-24..2027-08-20,
#       which contains the 2027-08-20 poison row)
a2 = dt.date(2028, 8, 20)
ldA = di_core.load_visits(os.path.join(HERE, "_clean_future_ref"), sheet, a2) \
    if False else None
build()
ldc = di_core.load_visits(LAB, sheet, a2)
cc = di_observe.cell(ldc["visits"], sheet, "Firenze", METRIC, a2)
build(POISON)
ldp = di_core.load_visits(LAB, sheet, a2)
cp = di_observe.cell(ldp["visits"], sheet, "Firenze", METRIC, a2)
out["F2c_A_LATER_AS_OF_LETS_THE_ROW_IN_LEGITIMATELY"] = {
    "as_of": a2.isoformat(),
    "clean_baseline_n": cc["analysis"]["baseline_n"],
    "poisoned_baseline_n": cp["analysis"]["baseline_n"],
    "clean_baseline_max_pct": cc["analysis"]["baseline_rate_pct_max"],
    "poisoned_baseline_max_pct": cp["analysis"]["baseline_rate_pct_max"],
    "clean_historical_state": cc["analysis"]["historical_state"],
    "poisoned_historical_state": cp["analysis"]["historical_state"],
    "NOTE": "at as_of 2028-08-20 the 2027-08-20 row is NOT in the future any more, so "
            "di_core admits it by design. This measures what a row that was future when "
            "written does to the archive later - the filter is relative to as_of, and an "
            "archive is not re-audited when as_of moves past a poisoned date."}

# ── F3: what does the date parser accept? ──────────────────────────────────
probes = ["2026-09-07", "20260907", "2026-W38-1", "2026-09-07T23:59:59",
          "2026-09-07T00:00:00+14:00", "2026-250", "2026-09", "0001-01-01",
          "9999-12-31", "2026-9-7", " 2026-09-07", "2026-09-07 ", "2026-02-30"]
acc = {}
for s in probes:
    try:
        acc[s] = dt.date.fromisoformat(s).isoformat()
    except Exception as e:
        acc[s] = f"REJECTED {type(e).__name__}"
out["F3_WHAT_date_fromisoformat_ACCEPTS"] = {
    "python": sys.version.split()[0], "probes": acc,
    "any_string_that_parses_to_a_PAST_date_while_meaning_a_future_one": [
        s for s, v in acc.items() if not v.startswith("REJECTED")
        and dt.date.fromisoformat(v) <= AS_OF and s.startswith(("2027", "2099", "9999"))]}

# a timezone trick: a row whose local date is 7 Sep in +14:00 is 6 Sep in UTC.
out["F3b_TIMEZONE"] = {
    "does_the_engine_ever_convert_a_timezone": False,
    "evidence": "di_core parses date-only strings with dt.date.fromisoformat and never "
                "constructs a datetime, so there is no tz conversion to exploit. "
                "The source ships date-only strings (checked: every row).",
    "rows_whose_date_field_is_not_a_bare_YYYY_MM_DD": None}

# measure that last claim on the real bytes
odd = 0
tot = 0
for fn in sorted(os.listdir(os.path.join(SRC, "RAW"))):
    for r in json.load(open(os.path.join(SRC, "RAW", fn), encoding="utf-8")):
        d = r.get("date")
        tot += 1
        if not (isinstance(d, str) and len(d) == 10 and d[4] == "-" and d[7] == "-"):
            odd += 1
out["F3b_TIMEZONE"]["rows_whose_date_field_is_not_a_bare_YYYY_MM_DD"] = f"{odd} of {tot}"

# ── F4: the refresh has no as_of at all ────────────────────────────────────
rows_future = [{"date": "2026-09-04", "val": "1", "id_field": 1},
               {"date": "2099-01-01", "val": "1", "id_field": 2}]
st, det, _, _ = di_refresh.validate(
    json.dumps({"data": {"ok": True, "data": rows_future}}).encode("utf-8"))
rec = di_refresh.refresh_one(os.path.join(HERE, "_no_such_canon"),
                             os.path.join(HERE, "_rt2_stage_future"), 2, 1, -1002, 2026,
                             _transport=lambda u: json.dumps(
                                 {"data": {"ok": True, "data": rows_future}}).encode("utf-8"))
out["F4_THE_REFRESH_HAS_NO_AS_OF"] = {
    "validate_status": st, "validate_detail": det,
    "LAST_GOOD_OBSERVATION_AT_written_into_the_index": rec.get("LAST_GOOD_OBSERVATION_AT"),
    "REFRESH_STATUS": rec["REFRESH_STATUS"],
    "the_row_that_produced_it": "2099-01-01",
    "VERDICT": "a future-dated row sets LAST_GOOD_OBSERVATION_AT to the future"
               if rec.get("LAST_GOOD_OBSERVATION_AT", "") > AS_OF.isoformat()
               else "clamped"}

# F4b: max() over strings is not chronological max when formats are mixed
mixed = [{"date": "2026-09-04", "val": "1"}, {"date": "20260905", "val": "1"},
         {"date": "not-a-date", "val": "1"}]
st2, det2, _, _ = di_refresh.validate(
    json.dumps({"data": {"ok": True, "data": mixed}}).encode("utf-8"))
out["F4b_STRING_MAX_IS_NOT_A_DATE_MAX"] = {
    "rows": [r["date"] for r in mixed], "validate_status": st2, "detail": det2,
    "NOTE": "latest_observation is max() over raw strings; no row is parsed as a date "
            "anywhere in validate()"}

# F4c: a mixed-TYPE date field
mixed2 = [{"date": "2026-09-04", "val": "1"}, {"date": 20260905, "val": "1"}]
try:
    st3, det3, _, _ = di_refresh.validate(
        json.dumps({"data": {"ok": True, "data": mixed2}}).encode("utf-8"))
    out["F4c_MIXED_TYPE_DATE"] = {"validate_status": st3, "detail": det3}
except Exception as e:
    out["F4c_MIXED_TYPE_DATE"] = {
        "RAISED_OUT_OF_VALIDATE": f"{type(e).__name__}: {e}",
        "NOTE": "fetch() promises never to raise; validate() carries no such guard and "
                "refresh_one calls it without a try, so this kills the whole refresh run"}

shutil.rmtree(LAB, ignore_errors=True)
json.dump(out, open(os.path.join(HERE, "rt2_future.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:9000])
