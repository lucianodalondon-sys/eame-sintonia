#!/usr/bin/env python3
"""
RT2 / A3b — THE TREND, RE-MEASURED ON THE ENGINE AS IT STANDS NOW.

The engine moved twice during this audit. The 1.0-percentage-point rule that produced
STABLE_OBSERVED on a monotone 25x rise has been replaced by non-overlapping Wilson 95%
intervals plus monotonicity. This re-runs the same attacks on the current bytes:

  N1  the labels now, and how they moved.
  N2  TREND_MIN_ABS_CHANGE_PCT is still in PARAMS and still emitted in every cell. Is it
      used anywhere?
  N3  the consecutiveness claim: unchanged code, so re-test that a hole is possible.
      Synthetic case, built to make one window fail the gate while its neighbours pass.
  N4  the Wilson interval is computed over DRUPES as if each drupe were an independent
      trial. Count the clustering it ignores.
"""
import os, sys, json, shutil, hashlib, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe

CASE = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
METRIC = "ACTIVE_INFESTATION_COUNT"
AS_OF = dt.date(2026, 9, 6)
P = di_observe.PARAMS
out = {"ENGINE_SHA256": {f: hashlib.sha256(open(os.path.join(ENGINE, f), "rb").read()
                                           ).hexdigest()
                         for f in ("di_core.py", "di_observe.py", "di_refresh.py")},
       "MEASURED_AT_UTC": dt.datetime.now(dt.timezone.utc).replace(
           microsecond=0).isoformat()}
sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
VIS = loaded["visits"]
PROVS = sorted({v["province"] for v in VIS if v["province"]})
BYPROV = {p: [v for v in VIS if v["province"] == p] for p in PROVS}

# ── N1: the labels now ─────────────────────────────────────────────────────
now = {}
for p in PROVS:
    c = di_observe.cell(BYPROV[p], sheet, p, METRIC, AS_OF)
    pts = c["analysis"]["observed_trend_points"]
    now[p] = {"value_pct": c["observation"]["value_pct"],
              "sequence": [x["rate_pct"] for x in pts],
              "infested_over_drupes": [(x.get("infested"), x["drupes_sampled"])
                                       for x in pts],
              "n_visits_per_window": [x["n_visits"] for x in pts],
              "delta_pp": (round(pts[-1]["rate_pct"] - pts[0]["rate_pct"], 4)
                           if len(pts) >= 2 else None),
              "trend_now": c["analysis"]["observed_trend"],
              "reason_now": c["analysis"]["observed_trend_reason"][:230],
              "historical_state": c["analysis"]["historical_state"]}
out["N1_TRENDS_ON_THE_CURRENT_ENGINE"] = now
out["N1b_WHAT_THE_OLD_1_0_PP_RULE_WOULD_HAVE_SAID"] = {
    p: ("STABLE_OBSERVED" if (v["delta_pp"] is None or abs(v["delta_pp"]) < 1.0)
        else "INCREASING_OBSERVED" if v["delta_pp"] > 0 else "DECREASING_OBSERVED")
    for p, v in now.items() if len(v["sequence"]) >= P["TREND_MIN_WINDOWS"]}
out["N1c_PROVINCES_WHOSE_LABEL_THE_FIX_CHANGED"] = [
    p for p, v in out["N1b_WHAT_THE_OLD_1_0_PP_RULE_WOULD_HAVE_SAID"].items()
    if v != now[p]["trend_now"]]

# ── N2: is TREND_MIN_ABS_CHANGE_PCT used at all? ───────────────────────────
src = open(os.path.join(ENGINE, "di_observe.py"), encoding="utf-8").read()
uses = [ln.strip() for ln in src.splitlines() if "TREND_MIN_ABS_CHANGE_PCT" in ln]
c0 = di_observe.cell(BYPROV["Siena"], sheet, "Siena", METRIC, AS_OF)
P_zero = dict(P); P_zero["TREND_MIN_ABS_CHANGE_PCT"] = 0.0
P_huge = dict(P); P_huge["TREND_MIN_ABS_CHANGE_PCT"] = 9999.0
c_zero = di_observe.cell(BYPROV["Siena"], sheet, "Siena", METRIC, AS_OF, params=P_zero)
c_huge = di_observe.cell(BYPROV["Siena"], sheet, "Siena", METRIC, AS_OF, params=P_huge)
out["N2_A_DEAD_PARAMETER_STILL_PUBLISHED"] = {
    "lines_mentioning_it_in_di_observe": uses,
    "it_is_emitted_in_every_cell_params_block":
        "TREND_MIN_ABS_CHANGE_PCT" in c0["params"],
    "value_emitted": c0["params"].get("TREND_MIN_ABS_CHANGE_PCT"),
    "trend_with_the_parameter_at_0": c_zero["analysis"]["observed_trend"],
    "trend_with_the_parameter_at_9999": c_huge["analysis"]["observed_trend"],
    "trend_at_the_declared_1_0": c0["analysis"]["observed_trend"],
    "changing_it_from_0_to_9999_changes_nothing":
        c_zero["analysis"]["observed_trend"] == c_huge["analysis"]["observed_trend"]
        == c0["analysis"]["observed_trend"],
    "the_docstring_says": "EVERY parameter is declared here, emitted in PARAMS, and varied "
                          "by the sensitivity test. A parameter that never appears in the "
                          "output is a parameter nobody can audit."}

# ── N3: the hole. real archive first, then a synthetic case built to trigger it ─
holes = 0
scanned = 0
for p in PROVS:
    for day in range(0, 220):
        a = AS_OF - dt.timedelta(days=day)
        keep = []
        for i in range(P["TREND_MIN_WINDOWS"] + 1):
            h = a - dt.timedelta(days=P["WINDOW_DAYS"] * i)
            l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
            w = di_observe.pooled(BYPROV[p], l, h, p, METRIC)
            if w and w["n_visits"] >= P["MIN_VISITS"] \
                    and w["drupes_sampled"] >= P["MIN_DRUPES"]:
                keep.append(i)
        scanned += 1
        if len(keep) >= P["TREND_MIN_WINDOWS"] and (max(keep) - min(keep) + 1) != len(keep):
            holes += 1
out["N3_HOLES_ON_THE_REAL_ARCHIVE"] = {"province_x_as_of_scanned": scanned,
                                       "with_a_hole": holes}

# synthetic: windows i=0, i=1 and i=3 rich; window i=2 has only 4 visits (below MIN_VISITS 8)
LAB = os.path.join(HERE, "_lab_hole")
if os.path.exists(LAB):
    shutil.rmtree(LAB)
os.makedirs(os.path.join(LAB, "RAW"))
a = dt.date(2026, 9, 6)
plan = {0: (20, 5.0), 1: (20, 3.0), 2: (2, 1.0), 3: (20, 1.0)}   # (groves, pct)
for var in (1, -1001, -1002, -1003):
    rows = []
    for i, (ngroves, pct) in plan.items():
        h = a - dt.timedelta(days=P["WINDOW_DAYS"] * i)
        for k in range(4):                       # 4 visit days inside each window
            d = h - dt.timedelta(days=k * 5)
            for g in range(ngroves):
                val = {1: 100.0, -1001: pct, -1002: 0.0, -1003: pct}[var]
                rows.append({"id_field": 7000 + g, "date": d.isoformat(),
                             "val": str(val), "nome_area": "Prato", "name_4": "H",
                             "admin_code": 1, "org_name": "rt2", "week": "1",
                             "id_survey": f"{i}{k}{g}"})
    json.dump(rows, open(os.path.join(LAB, "RAW", f"c2_s1_v{var}_2026.json"), "w",
                         encoding="utf-8"))
ldh = di_core.load_visits(LAB, sheet, a)
ch = di_observe.cell(ldh["visits"], sheet, "Prato", METRIC, a, first_year=2020)
ends = [x["window_end"] for x in ch["analysis"]["observed_trend_points"]]
gaps = [(dt.date.fromisoformat(y) - dt.date.fromisoformat(x)).days
        for x, y in zip(ends, ends[1:])]
out["N3b_SYNTHETIC_CASE_WITH_A_HOLE"] = {
    "design": "windows ending at as_of-0d, -28d, -84d are rich; the window ending -56d has "
              "2 groves x 4 days = 8 visits but only 800 drupes... measured below",
    "window_ends_kept": ends,
    "gaps_between_kept_window_ends_days": gaps,
    "they_are_28_days_apart": all(g == P["WINDOW_DAYS"] for g in gaps),
    "published_trend": ch["analysis"]["observed_trend"],
    "published_sentence": ch["analysis"]["observed_trend_reason"],
    "the_sentence_uses_the_word_consecutive":
        "consecutive" in ch["analysis"]["observed_trend_reason"],
    "n_points": len(ends)}
shutil.rmtree(LAB, ignore_errors=True)

# ── N4: what the Wilson interval assumes ───────────────────────────────────
c = di_observe.cell(BYPROV["Siena"], sheet, "Siena", METRIC, AS_OF)
pts = c["analysis"]["observed_trend_points"]
last = pts[-1]
sites = set()
for v in BYPROV["Siena"]:
    d = dt.date.fromisoformat(v["observation_date"])
    lo = dt.date.fromisoformat(last["window_end"]) - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
    if lo <= d <= dt.date.fromisoformat(last["window_end"]):
        sites.add(v["visit_key"]["id_field"])
out["N4_WHAT_THE_INTERVAL_TREATS_AS_INDEPENDENT"] = {
    "province": "Siena", "window_end": last["window_end"],
    "drupes_the_interval_treats_as_independent_trials": last["drupes_sampled"],
    "visits_they_actually_came_from": last["n_visits"],
    "groves_those_visits_came_from": len(sites),
    "drupes_per_visit": round(last["drupes_sampled"] / last["n_visits"], 1),
    "NOTE": "a Wilson interval on 18,383 drupes is far narrower than one on 186 visits or "
            "61 groves. Clustering is not modelled, so 'the intervals do not overlap' is "
            "easier to achieve than the sentence implies. This is a statistics point, not "
            "a time point, but it is what now decides the direction."}

json.dump(out, open(os.path.join(HERE, "rt2_trend2.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:9000])
