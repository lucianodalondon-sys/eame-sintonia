#!/usr/bin/env python3
"""
RT2 / A2 — THE 28-DAY WINDOW ACROSS 31 DECEMBER.

_win() builds the window with timedelta, so the CURRENT window is correct across new year.
_shift() then moves lo and hi into a prior season INDEPENDENTLY, by replacing the year on
each. When lo and hi are in different calendar years, this maps them to the SAME year, and
the shifted window has lo > hi.

Part 1: the arithmetic, printed for every as_of where the window crosses the boundary.
Part 2: does it bite on the real archive (are there winter observations at all)?
Part 3: a SYNTHETIC case with dense December+January observations in 8 seasons, so the
        baseline SHOULD be rich, run through the real engine.
"""
import os, sys, json, shutil, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe

CASE = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
LAB = os.path.join(HERE, "_lab_yearcross")
out = {}

# ── Part 1: pure arithmetic ──────────────────────────────────────────────────
rows = []
for day in range(1, 40):
    as_of = dt.date(2026, 1, 1) + dt.timedelta(days=day - 1)
    lo, hi = di_observe._win(as_of, 28)
    slo, shi = di_observe._shift(lo, 2020), di_observe._shift(hi, 2020)
    rows.append({"as_of": as_of.isoformat(),
                 "window": [lo.isoformat(), hi.isoformat()],
                 "window_days": (hi - lo).days + 1,
                 "crosses_new_year": lo.year != hi.year,
                 "baseline_window_for_season_2020": [slo.isoformat(), shi.isoformat()],
                 "baseline_window_days": (shi - slo).days + 1})
out["ARITHMETIC"] = rows
bad = [r for r in rows if r["baseline_window_days"] <= 0]
out["ARITHMETIC_SUMMARY"] = {
    "as_of_days_tested": len(rows),
    "as_of_days_whose_window_crosses_new_year": sum(1 for r in rows if r["crosses_new_year"]),
    "as_of_days_whose_baseline_window_is_impossible": len(bad),
    "worst_baseline_window_days": min(r["baseline_window_days"] for r in rows),
    "NOTE": "a window with lo > hi never matches a row, so the baseline is EMPTY, "
            "not shifted by -337 days"}

# ── Part 2: the real archive ─────────────────────────────────────────────────
sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, dt.date(2026, 12, 31))
bymonth = collections.Counter(v["observation_date"][5:7] for v in loaded["visits"])
out["REAL_ARCHIVE_OBSERVATIONS_BY_MONTH"] = dict(sorted(bymonth.items()))
out["REAL_ARCHIVE_TOTAL_VISITS"] = len(loaded["visits"])

real = {}
for iso in ("2026-01-15", "2026-01-28", "2026-01-29", "2026-02-10"):
    a = dt.date.fromisoformat(iso)
    c = di_observe.cell(loaded["visits"], sheet, "Firenze", "ACTIVE_INFESTATION_COUNT", a)
    real[iso] = {"window": c["observation"]["window"],
                 "crosses_new_year": c["observation"]["window"][0][:4] != iso[:4],
                 "n_visits": c["observation"]["n_visits"],
                 "value_pct": c["observation"]["value_pct"],
                 "baseline_n": c["analysis"]["baseline_n"],
                 "matched_panel_seasons": c["analysis"]["matched_panel_seasons"],
                 "historical_state": c["analysis"]["historical_state"],
                 "historical_reason": c["analysis"]["historical_reason"]}
out["REAL_ARCHIVE_FIRENZE"] = real

# ── Part 3: synthetic winter case ────────────────────────────────────────────
# 9 seasons, every season the same 20 groves visited every day from 1 Dec to 31 Jan,
# 100 drupes each, 5 infested (5.0%). The 2026 season reads 5 infested too.
# The baseline SHOULD find 8 prior seasons with identical data.
def build_synth():
    if os.path.exists(LAB):
        shutil.rmtree(LAB)
    os.makedirs(os.path.join(LAB, "RAW"))
    for var, value in ((1, 100.0), (-1001, 5.0), (-1002, 0.0), (-1003, 5.0)):
        peryear = collections.defaultdict(list)
        for season in range(2018, 2027):
            d = dt.date(season - 1, 12, 1)
            while d <= dt.date(season, 1, 31):
                for g in range(20):
                    peryear[season].append({
                        "id_field": 9000 + g, "date": d.isoformat(), "val": str(value),
                        "nome_area": "Prato", "name_4": "W", "admin_code": 1,
                        "org_name": "rt2", "week": "1", "id_survey": f"{season}{g}{d}"})
                d += dt.timedelta(days=1)
        for season, rws in peryear.items():
            json.dump(rws, open(os.path.join(LAB, "RAW", f"c2_s1_v{var}_{season}.json"),
                                "w", encoding="utf-8"))


build_synth()
sl = di_core.load_visits(LAB, sheet, dt.date(2026, 1, 15))
synth = {"visits_loaded": sl["n_visits"],
         "usable": sl.get("n_visits_usable_for_rates",
                          sl.get("n_visits_usable_for_at_least_one_measurement"))}
for iso in ("2026-01-15", "2026-01-28", "2026-01-29", "2026-02-25", "2025-12-20"):
    a = dt.date.fromisoformat(iso)
    ld = di_core.load_visits(LAB, sheet, a)
    c = di_observe.cell(ld["visits"], sheet, "Prato", "ACTIVE_INFESTATION_COUNT", a,
                        first_year=2018)
    lo, hi = di_observe._win(a, 28)
    synth[iso] = {
        "window": c["observation"]["window"],
        "window_crosses_new_year": lo.year != hi.year,
        "observation_pct": c["observation"]["value_pct"],
        "observation_n_visits": c["observation"]["n_visits"],
        "baseline_seasons_found": c["analysis"]["baseline_n"],
        "baseline_seasons_list": c["analysis"]["baseline_seasons"],
        "matched_panel_seasons": c["analysis"]["matched_panel_seasons"],
        "historical_state": c["analysis"]["historical_state"],
        "historical_reason": c["analysis"]["historical_reason"],
        "observed_trend": c["analysis"]["observed_trend"],
        "trend_points": [p["window_end"] for p in c["analysis"]["observed_trend_points"]]}
out["SYNTHETIC_WINTER_CASE"] = synth

json.dump(out, open(os.path.join(HERE, "rt2_yearcross.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "ARITHMETIC"}, indent=1, default=str))
print("\nARITHMETIC (first 5 and around the boundary):")
for r in out["ARITHMETIC"][:3] + out["ARITHMETIC"][26:32]:
    print(f"  as_of {r['as_of']}  win {r['window'][0]}..{r['window'][1]} "
          f"({r['window_days']}d, crosses={r['crosses_new_year']})  -> baseline 2020 "
          f"{r['baseline_window_for_season_2020'][0]}..{r['baseline_window_for_season_2020'][1]} "
          f"({r['baseline_window_days']}d)")
