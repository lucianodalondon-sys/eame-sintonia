#!/usr/bin/env python3
"""
RT2 / A6 — 29 FEBRUARY, AND AN ARCHIVE THAT STOPPED 400 DAYS AGO.

LEAP
  _shift() maps 29 Feb to 28 Feb "declared". Two consequences are measured:
  L1  the fallback d.replace(year=y, day=28) is reached ONLY for 29 Feb, but it rewrites the
      DAY OF THE MONTH, not the date - so if it were ever reached for another date it would
      silently move it. Enumerate every date it fires on.
  L2  a window that spans 29 Feb is 28 days long in a leap year and 27 days long in the
      baseline seasons that are not leap years. Measure how many days and how many drupes
      that costs, on synthetic data with a known constant rate.

STALE
  S1  a case whose newest observation is 400 days before as_of. What does the tool publish?
  S2  does ANY field go red? Is there a latency threshold anywhere in the code?
  S3  the number that a threshold would need: how far apart are consecutive observations in
      the real archive, so that "stale" can be given a defensible value?
"""
import os, sys, json, shutil, datetime as dt, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe, di_adama, di_render

SRC = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA"))
LAB = os.path.join(HERE, "_lab_stale")
METRIC = "ACTIVE_INFESTATION_COUNT"
P = di_observe.PARAMS
out = {}
sheet = di_core.load_sheet()

# ── L1: every date the 29-Feb fallback fires on ────────────────────────────
fires = []
d = dt.date(2020, 1, 1)
while d <= dt.date(2028, 12, 31):
    try:
        d.replace(year=2026)
    except ValueError:
        fires.append(d.isoformat())
    d += dt.timedelta(days=1)
out["L1_WHEN_THE_FALLBACK_FIRES"] = {
    "dates_scanned": (dt.date(2028, 12, 31) - dt.date(2020, 1, 1)).days + 1,
    "dates_where_replace(year=2026)_raises": fires,
    "the_fallback_sets_day=28": True,
    "is_that_correct_for_every_firing_date": all(f[5:7] == "02" and f[8:] == "29"
                                                 for f in fires),
    "NOTE": "the fallback is only reachable for 29 Feb, so day=28 is right today. It is "
            "written as a day-of-month rewrite, not as 'the last day of that month', so it "
            "would be silently wrong if the guard ever widened."}

# ── L2: a window that spans 29 Feb ─────────────────────────────────────────
lens = []
for as_of_iso in ("2028-03-10", "2028-03-27", "2028-02-29", "2027-03-10"):
    a = dt.date.fromisoformat(as_of_iso)
    lo, hi = di_observe._win(a, P["WINDOW_DAYS"])
    row = {"as_of": as_of_iso, "current_window": [lo.isoformat(), hi.isoformat()],
           "current_window_days": (hi - lo).days + 1, "baselines": []}
    for y in (2024, 2025, 2026, 2027):
        slo, shi = di_observe._shift(lo, y), di_observe._shift(hi, y)
        row["baselines"].append({"season": y,
                                 "window": [slo.isoformat(), shi.isoformat()],
                                 "days": (shi - slo).days + 1,
                                 "days_vs_current": (shi - slo).days + 1
                                                    - ((hi - lo).days + 1)})
    lens.append(row)
out["L2_WINDOW_LENGTH_ACROSS_LEAP_YEARS"] = lens
short = [b for r in lens for b in r["baselines"] if b["days_vs_current"] != 0]
out["L2_SUMMARY"] = {
    "baseline_windows_examined": sum(len(r["baselines"]) for r in lens),
    "baseline_windows_shorter_or_longer_than_the_current_one": len(short),
    "worst_difference_days": (max(abs(b["days_vs_current"]) for b in short)
                              if short else 0),
    "as_a_share_of_the_window": f"{(max(abs(b['days_vs_current']) for b in short) if short else 0)}"
                                f" of {P['WINDOW_DAYS']} days = "
                                f"{100.0*(max(abs(b['days_vs_current']) for b in short) if short else 0)/P['WINDOW_DAYS']:.1f}%"}

# L2b: what a missing day costs, on synthetic data with a constant 5% rate and 20 groves
SLAB = os.path.join(HERE, "_lab_leap")
if os.path.exists(SLAB):
    shutil.rmtree(SLAB)
os.makedirs(os.path.join(SLAB, "RAW"))
for var, value in ((1, 100.0), (-1001, 5.0), (-1002, 0.0), (-1003, 5.0)):
    for season in range(2020, 2029):
        rows = []
        d0 = dt.date(season, 1, 1)
        while d0 <= dt.date(season, 12, 31):
            for g in range(20):
                rows.append({"id_field": 8000 + g, "date": d0.isoformat(),
                             "val": str(value), "nome_area": "Prato", "name_4": "L",
                             "admin_code": 1, "org_name": "rt2", "week": "1",
                             "id_survey": f"{season}{g}{d0}"})
            d0 += dt.timedelta(days=1)
        json.dump(rows, open(os.path.join(SLAB, "RAW", f"c2_s1_v{var}_{season}.json"),
                             "w", encoding="utf-8"))
a = dt.date(2028, 3, 10)
ld = di_core.load_visits(SLAB, sheet, a)
c = di_observe.cell(ld["visits"], sheet, "Prato", METRIC, a, first_year=2020)
out["L2b_SYNTHETIC_CONSTANT_5PCT"] = {
    "as_of": a.isoformat(), "current_window": c["observation"]["window"],
    "current_drupes": c["observation"]["drupes_sampled"],
    "current_n_visits": c["observation"]["n_visits"],
    "baseline_detail": c["analysis"]["baseline_detail"],
    "rates_are_all_equal": len({b["rate_pct"] for b in
                                c["analysis"]["baseline_detail"]}) <= 1,
    "drupes_by_season": {b["season"]: b["drupes_sampled"]
                         for b in c["analysis"]["baseline_detail"]},
    "historical_state": c["analysis"]["historical_state"],
    "NOTE": "with a constant rate the missing day changes the DENOMINATOR, not the rate. "
            "It matters only where a season sits near MIN_VISITS or MIN_DRUPES."}
shutil.rmtree(SLAB, ignore_errors=True)

# how close do real baseline seasons sit to the gates?
ld_real = di_core.load_visits(SRC, sheet, dt.date(2026, 9, 6))
near = []
for prov in sorted({v["province"] for v in ld_real["visits"] if v["province"]}):
    cc = di_observe.cell(ld_real["visits"], sheet, prov, METRIC, dt.date(2026, 9, 6))
    for b in cc["analysis"]["baseline_detail"]:
        margin_v = b["n_visits"] - P["MIN_VISITS"]
        margin_d = b["drupes_sampled"] - P["MIN_DRUPES"]
        near.append({"province": prov, "season": b["season"], "n_visits": b["n_visits"],
                     "drupes": b["drupes_sampled"], "visits_above_gate": margin_v,
                     "drupes_above_gate": margin_d,
                     "would_a_4pct_smaller_window_drop_it":
                         b["n_visits"] * 27 / 28 < P["MIN_VISITS"]
                         or b["drupes_sampled"] * 27 / 28 < P["MIN_DRUPES"]})
out["L2c_HOW_MANY_REAL_BASELINE_SEASONS_SIT_WITHIN_ONE_DAY_OF_THE_GATE"] = {
    "baseline_season_cells": len(near),
    "that_a_27_day_window_would_drop": sum(1 for n in near
                                           if n["would_a_4pct_smaller_window_drop_it"]),
    "examples": [n for n in near if n["would_a_4pct_smaller_window_drop_it"]][:6]}

# ── STALE ──────────────────────────────────────────────────────────────────
# S1: shift the whole 2026 season back so the newest observation is 400 days before as_of
AS_OF = dt.date(2026, 9, 6)
if os.path.exists(LAB):
    shutil.rmtree(LAB)
os.makedirs(os.path.join(LAB, "RAW"))
newest = dt.date(2026, 9, 4)                       # the real newest observation
target_newest = AS_OF - dt.timedelta(days=400)     # 2025-08-02
shift_days = (newest - target_newest).days
for fn in sorted(os.listdir(os.path.join(SRC, "RAW"))):
    rows = json.load(open(os.path.join(SRC, "RAW", fn), encoding="utf-8"))
    for r in rows:
        r["date"] = (dt.date.fromisoformat(r["date"])
                     - dt.timedelta(days=shift_days)).isoformat()
    json.dump(rows, open(os.path.join(LAB, "RAW", fn), "w", encoding="utf-8"))
ld_s = di_core.load_visits(LAB, sheet, AS_OF)
dates = sorted(v["observation_date"] for v in ld_s["visits"])
adama = di_adama.relevance("Olive", "Olive Fruit Fly")
stale_cells = []
for prov in sorted({v["province"] for v in ld_s["visits"] if v["province"]}):
    c = di_observe.cell(ld_s["visits"], sheet, prov, METRIC,
                        dt.date.fromisoformat(dates[-1]))
    stale_cells.append(c)
# now the real question: as_of = 2026-09-06, 400 days after the newest row
pub, texts = [], []
for prov in sorted({v["province"] for v in ld_s["visits"] if v["province"]}):
    c = di_observe.cell(ld_s["visits"], sheet, prov, METRIC, AS_OF)
    c["adama"] = adama
    c["attention"] = di_adama.attention_class(c, adama)
    pub.append(c)
out["S1_ARCHIVE_400_DAYS_OLD"] = {
    "as_of": AS_OF.isoformat(),
    "newest_observation_in_the_archive": dates[-1],
    "age_of_the_newest_observation_days": (AS_OF - dt.date.fromisoformat(dates[-1])).days,
    "provinces": {c["province"]: {
        "value_pct": c["observation"]["value_pct"],
        "n_visits": c["observation"]["n_visits"],
        "last_observation": c["observation"]["last_observation"],
        "observation_publishable": c["quality"]["observation_publishable"],
        "historical_state": c["analysis"]["historical_state"],
        "trend": c["analysis"]["observed_trend"],
        "attention_class": c["attention"]["attention_class"],
        "temporal_validity": c["quality"]["temporal_validity"]} for c in pub},
    "provinces_with_a_publishable_observation":
        sum(1 for c in pub if c["quality"]["observation_publishable"]),
    "of": len(pub)}

# S1b: an archive that is stale by exactly one window boundary - 29 days
target29 = AS_OF - dt.timedelta(days=29)
shift29 = (newest - target29).days
LAB29 = os.path.join(HERE, "_lab_stale29")
if os.path.exists(LAB29):
    shutil.rmtree(LAB29)
os.makedirs(os.path.join(LAB29, "RAW"))
for fn in sorted(os.listdir(os.path.join(SRC, "RAW"))):
    rows = json.load(open(os.path.join(SRC, "RAW", fn), encoding="utf-8"))
    for r in rows:
        r["date"] = (dt.date.fromisoformat(r["date"])
                     - dt.timedelta(days=shift29)).isoformat()
    json.dump(rows, open(os.path.join(LAB29, "RAW", fn), "w", encoding="utf-8"))
ld29 = di_core.load_visits(LAB29, sheet, AS_OF)
p29 = []
for prov in sorted({v["province"] for v in ld29["visits"] if v["province"]}):
    c = di_observe.cell(ld29["visits"], sheet, prov, METRIC, AS_OF)
    p29.append((prov, c["observation"]["value_pct"], c["observation"]["n_visits"],
                c["quality"]["observation_publishable"]))
out["S1b_ARCHIVE_29_DAYS_OLD"] = {
    "newest_observation": max(v["observation_date"] for v in ld29["visits"]),
    "provinces_publishable": sum(1 for x in p29 if x[3]), "of": len(p29),
    "detail": p29,
    "NOTE": "at 29 days the whole archive falls outside the 28-day window, so every "
            "province goes silent. Between 1 and 28 days of staleness the tool publishes a "
            "window that is partly empty and says nothing about it."}

# S2: is there any latency threshold in the code at all?
src_all = "".join(open(os.path.join(ENGINE, f), encoding="utf-8").read()
                  for f in ("di_core.py", "di_observe.py", "di_refresh.py", "di_render.py",
                            "di_adama.py", "di_report.py"))
words = ["MAX_AGE", "STALE", "stale", "latency", "LATENCY", "freshness", "FRESHNESS",
         "age_days", "MAX_LAG", "too_old"]
out["S2_IS_THERE_A_LATENCY_THRESHOLD"] = {
    "engine_bytes_searched": len(src_all),
    "hits": {w: src_all.count(w) for w in words},
    "last_observation_is_reported": "last_observation" in src_all,
    "last_observation_is_compared_to_anything": False,
    "renderer_prints_it": "última observação" in
                          open(os.path.join(ENGINE, "di_render.py"),
                               encoding="utf-8").read()}

# S3: the number a threshold would need — real revisit intervals per grove
gaps = collections.Counter()
bysite = collections.defaultdict(list)
for v in ld_real["visits"]:
    if v["observation_date"] >= "2026-01-01":
        bysite[v["visit_key"]["id_field"]].append(v["observation_date"])
allgaps = []
for site, ds in bysite.items():
    ds = sorted(set(ds))
    for a1, b1 in zip(ds, ds[1:]):
        g = (dt.date.fromisoformat(b1) - dt.date.fromisoformat(a1)).days
        allgaps.append(g)
        gaps[g] += 1
allgaps.sort()


def pct(v, q):
    return v[int(q * (len(v) - 1))] if v else None


out["S3_WHAT_A_THRESHOLD_WOULD_BE_BUILT_ON"] = {
    "groves_with_at_least_two_2026_visits": sum(1 for s in bysite.values()
                                                if len(set(s)) > 1),
    "revisit_intervals_measured": len(allgaps),
    "median_days_between_visits_to_the_same_grove": statistics.median(allgaps)
        if allgaps else None,
    "p90_days": pct(allgaps, 0.90), "p99_days": pct(allgaps, 0.99),
    "max_days": max(allgaps) if allgaps else None,
    "most_common_intervals": gaps.most_common(6),
    "days_since_the_newest_observation_in_the_real_archive_at_as_of_2026_09_06":
        (dt.date(2026, 9, 6) - dt.date.fromisoformat(
            max(v["observation_date"] for v in ld_real["visits"]))).days}

shutil.rmtree(LAB, ignore_errors=True)
shutil.rmtree(LAB29, ignore_errors=True)
json.dump(out, open(os.path.join(HERE, "rt2_leap_and_stale.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:11000])
