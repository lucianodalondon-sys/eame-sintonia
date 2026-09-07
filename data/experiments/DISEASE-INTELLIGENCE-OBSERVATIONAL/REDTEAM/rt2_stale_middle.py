#!/usr/bin/env python3
"""
RT2 / A6b — THE MIDDLE OF THE STALENESS RANGE.

At 29+ days of staleness every province goes silent, because the 28-day window is an
implicit latency gate. The question that matters is the range BELOW that: 7, 14, 21 days.
There the tool still publishes, on a window that is mostly empty, and prints
last_observation without ever comparing it to as_of.

Measured: for each staleness in {0, 7, 14, 21, 27, 28, 29}, how many provinces publish,
on how many drupes, and how far the published number moves from the fresh one.
"""
import os, sys, json, shutil, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe, di_adama

SRC = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
sheet = di_core.load_sheet()
LAB = os.path.join(HERE, "_lab_mid")
out = {}

base = di_core.load_visits(SRC, sheet, AS_OF)
PROVS = sorted({v["province"] for v in base["visits"] if v["province"]})
fresh = {p: di_observe.cell(base["visits"], sheet, p, METRIC, AS_OF) for p in PROVS}

rows = []
for stale in (0, 7, 14, 21, 27, 28, 29, 60, 400):
    # shift every observation back by `stale` days relative to a newest of 2026-09-04
    shift = stale - (AS_OF - dt.date(2026, 9, 4)).days
    if shift < 0:
        shift = 0
    vis = []
    for v in base["visits"]:
        d = dt.date.fromisoformat(v["observation_date"]) - dt.timedelta(days=shift)
        w = dict(v)
        w["observation_date"] = d.isoformat()
        vis.append(w)
    newest = max(v["observation_date"] for v in vis)
    age = (AS_OF - dt.date.fromisoformat(newest)).days
    pub, drupes, moved = 0, 0, []
    for p in PROVS:
        c = di_observe.cell(vis, sheet, p, METRIC, AS_OF)
        a = di_adama.attention_class(c, {"relevance": "NO"})
        if c["quality"]["observation_publishable"]:
            pub += 1
            drupes += c["observation"]["drupes_sampled"]
            f = fresh[p]["observation"]["value_pct"]
            if f is not None and c["observation"]["value_pct"] is not None:
                moved.append(round(c["observation"]["value_pct"] - f, 4))
        rows.append({"staleness_days": stale, "province": p,
                     "newest_observation": newest, "age_of_newest_days": age,
                     "publishable": c["quality"]["observation_publishable"],
                     "value_pct": c["observation"]["value_pct"],
                     "n_visits": c["observation"]["n_visits"],
                     "drupes": c["observation"]["drupes_sampled"],
                     "last_observation": c["observation"]["last_observation"],
                     "days_between_last_observation_and_as_of":
                         None if not c["observation"]["last_observation"] else
                         (AS_OF - dt.date.fromisoformat(
                             c["observation"]["last_observation"])).days,
                     "attention": a["attention_class"]})
    out.setdefault("BY_STALENESS", []).append({
        "staleness_days": stale, "age_of_newest_observation_days": age,
        "provinces_publishing": pub, "of": len(PROVS),
        "total_drupes_behind_the_published_numbers": drupes,
        "max_shift_in_the_published_pct_vs_fresh": max(moved, default=None),
        "min_shift": min(moved, default=None)})
out["DETAIL"] = rows
out["THE_IMPLICIT_THRESHOLD"] = {
    "there_is_no_named_staleness_parameter": True,
    "but_the_window_is_one": "an observation older than WINDOW_DAYS-1 = 27 days cannot "
                             "enter the current window, so the tool goes silent at 28 days "
                             "of staleness without ever saying the word",
    "what_it_does_NOT_do": "between 1 and 27 days it publishes a number over a window that "
                           "is mostly empty, prints last_observation, and never subtracts "
                           "it from as_of"}
shutil.rmtree(LAB, ignore_errors=True)
json.dump(out, open(os.path.join(HERE, "rt2_stale_middle.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps(out["BY_STALENESS"], indent=1))
print()
for r in out["DETAIL"]:
    if r["province"] in ("Firenze", "Siena") and r["staleness_days"] in (0, 14, 21, 27, 28):
        print(f"  stale={r['staleness_days']:3d}d {r['province']:8s} pub={str(r['publishable']):5s} "
              f"pct={str(r['value_pct']):8s} visits={r['n_visits']:4d} drupes={r['drupes']:6d} "
              f"last_obs={r['last_observation']} ({r['days_between_last_observation_and_as_of']}d before as_of) "
              f"attention={r['attention']}")
