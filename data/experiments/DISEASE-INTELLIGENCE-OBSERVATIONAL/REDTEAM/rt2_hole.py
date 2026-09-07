#!/usr/bin/env python3
"""
RT2 / A3c — "N CONSECUTIVE WINDOWS": THE ENGINE NEVER CHECKS IT.

The trend loop builds 4 candidate windows ending at as_of, as_of-28, as_of-56, as_of-84 and
KEEPS the ones that pass MIN_VISITS / MIN_DRUPES. A failing window is skipped, not treated
as a break in the chain. The sentence that is published then says
"over N consecutive 28-day windows", and nothing in the engine has checked that they are.

Synthetic case, real engine: three rich windows at -0d, -28d and -84d, and one starved
window at -56d (1 grove x 4 visit days = 4 visits, below MIN_VISITS = 8).
"""
import os, sys, json, shutil, hashlib, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe

P = di_observe.PARAMS
AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
LAB = os.path.join(HERE, "_lab_hole")
sheet = di_core.load_sheet()

# (groves, rate_pct) per candidate window index. index 2 is starved on purpose.
PLAN = {0: (20, 5.0), 1: (1, 1.0), 2: (1, 1.0), 3: (20, 1.0)}
PLAN = {0: (20, 5.0), 1: (20, 3.0), 2: (1, 9.0), 3: (20, 1.0)}

if os.path.exists(LAB):
    shutil.rmtree(LAB)
os.makedirs(os.path.join(LAB, "RAW"))
for var in (1, -1001, -1002, -1003):
    rows = []
    for i, (ngroves, pct) in PLAN.items():
        h = AS_OF - dt.timedelta(days=P["WINDOW_DAYS"] * i)
        for k in range(4):
            d = h - dt.timedelta(days=k * 5)
            for g in range(ngroves):
                val = {1: 100.0, -1001: pct, -1002: 0.0, -1003: pct}[var]
                rows.append({"id_field": 7000 + g, "date": d.isoformat(), "val": str(val),
                             "nome_area": "Prato", "name_4": "H", "admin_code": 1,
                             "org_name": "rt2", "week": "1", "id_survey": f"{i}{k}{g}"})
    json.dump(rows, open(os.path.join(LAB, "RAW", f"c2_s1_v{var}_2026.json"), "w",
                         encoding="utf-8"))

ld = di_core.load_visits(LAB, sheet, AS_OF)
c = di_observe.cell(ld["visits"], sheet, "Prato", METRIC, AS_OF, first_year=2020)

cands = []
for i in range(P["TREND_MIN_WINDOWS"] + 1):
    h = AS_OF - dt.timedelta(days=P["WINDOW_DAYS"] * i)
    l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
    w = di_observe.pooled(ld["visits"], l, h, "Prato", METRIC)
    cands.append({"i": i, "window_end": h.isoformat(),
                  "n_visits": None if not w else w["n_visits"],
                  "drupes": None if not w else w["drupes_sampled"],
                  "rate_pct": None if not w else w["rate_pct"],
                  "passes_the_gate": bool(w and w["n_visits"] >= P["MIN_VISITS"]
                                          and w["drupes_sampled"] >= P["MIN_DRUPES"])})
ends = [x["window_end"] for x in c["analysis"]["observed_trend_points"]]
gaps = [(dt.date.fromisoformat(y) - dt.date.fromisoformat(x)).days
        for x, y in zip(ends, ends[1:])]
out = {"ENGINE_SHA256": {f: hashlib.sha256(open(os.path.join(ENGINE, f), "rb").read()
                                           ).hexdigest()[:16]
                         for f in ("di_core.py", "di_observe.py")},
       "MEASURED_AT_UTC": dt.datetime.now(dt.timezone.utc).replace(
           microsecond=0).isoformat(),
       "candidate_windows": cands,
       "candidates_that_passed": [x["i"] for x in cands if x["passes_the_gate"]],
       "PUBLISHED_window_ends": ends,
       "gaps_between_published_window_ends_days": gaps,
       "all_gaps_are_28_days": all(g == P["WINDOW_DAYS"] for g in gaps),
       "PUBLISHED_trend": c["analysis"]["observed_trend"],
       "PUBLISHED_sentence": c["analysis"]["observed_trend_reason"],
       "the_sentence_claims_consecutive": "consecutive"
                                          in c["analysis"]["observed_trend_reason"],
       "REPRODUCED": (not all(g == P["WINDOW_DAYS"] for g in gaps))
                     and "consecutive" in c["analysis"]["observed_trend_reason"],
       "what_the_reader_can_still_do": "observed_trend_points carries window_end for every "
                                       "point, so a reader who subtracts them can catch it. "
                                       "The renderer prints the sentence, not the ends."}
shutil.rmtree(LAB, ignore_errors=True)
json.dump(out, open(os.path.join(HERE, "rt2_hole.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1))
