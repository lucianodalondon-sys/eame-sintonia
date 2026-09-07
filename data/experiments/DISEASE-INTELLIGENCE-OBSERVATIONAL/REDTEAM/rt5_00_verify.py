#!/usr/bin/env python3
"""RT5 · gate 0. The fast harness must reproduce engine/di_observe.cell() exactly
on the published configuration, for all ten provinces, or nothing below counts."""
import os, sys, json, glob, hashlib, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L
sys.path.insert(0, L.ENGINE)
import di_core, di_observe

AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"

# The engine is being edited while this audit runs. Pin the exact bytes.
ENGINE_HASH = {os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest()
               for f in sorted(glob.glob(os.path.join(L.ENGINE, "*.py")))}
for k in ("di_core.py", "di_observe.py"):
    print(f"engine {k}  sha256 {ENGINE_HASH[k]}")
L.load_raw(force=True)          # never sweep against a stale cache

sheet = di_core.load_sheet()
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)
provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})

idx, raw = L.get_index(METRIC)
assert idx.provinces == provs, (idx.provinces, provs)
assert raw["n_visits"] == loaded["n_visits"], (raw["n_visits"], loaded["n_visits"])

rows, bad = [], 0
for p in provs:
    ref = di_observe.cell(loaded["visits"], sheet, p, METRIC, AS_OF)
    fast = L.cell(idx, p, AS_OF)
    checks = {
        "value_pct": (ref["observation"].get("value_pct"), fast["value_pct"]),
        "n_visits": (ref["observation"].get("n_visits", 0), fast["n_visits"]),
        "n_sites": (ref["observation"].get("n_sites", 0), fast["n_sites"]),
        "drupes": (ref["observation"].get("drupes_sampled", 0), fast["drupes_sampled"]),
        "hist": (ref["analysis"]["historical_state"], fast["historical_state"]),
        "matched_seasons": (ref["analysis"]["matched_panel_seasons"],
                            fast["matched_panel_seasons"]),
        "trend": (ref["analysis"]["observed_trend"], fast["observed_trend"]),
        "baseline_n": (ref["analysis"]["baseline_n"], fast["baseline_n"]),
        "n_lower": (ref["analysis"].get("matched_seasons_now_is_lower_than_then"),
                    fast.get("n_lower")),
        "n_higher": (ref["analysis"].get("matched_seasons_now_is_higher_than_then"),
                     fast.get("n_higher")),
        "publishable": (ref["quality"]["publishable"], fast["publishable"]),
        "trend_points": ([q["rate_pct"] for q in ref["analysis"]["observed_trend_points"]],
                         fast["trend_points"]),
    }
    diffs = {k: v for k, v in checks.items() if v[0] != v[1]}
    if diffs:
        bad += 1
    rows.append({"province": p, "ok": not diffs, "diffs": diffs,
                 "published": {"value_pct": fast["value_pct"],
                               "historical_state": fast["historical_state"],
                               "n_lower": fast.get("n_lower"),
                               "n_matched": fast.get("n_matched"),
                               "trend": fast["observed_trend"],
                               "trend_points": fast["trend_points"]}})
    print(f"{p:15s} {'OK ' if not diffs else 'MISMATCH'} {diffs if diffs else ''}")

print(f"\n{len(provs) - bad} of {len(provs)} provinces reproduce the engine exactly.")
json.dump({"as_of": AS_OF.isoformat(), "metric": METRIC,
           "engine_sha256": ENGINE_HASH,
           "n_visits_loaded": loaded["n_visits"],
           "n_visits_usable_by_measurement":
               loaded.get("n_visits_usable_by_measurement"),
           "provinces_matching": len(provs) - bad, "of": len(provs), "rows": rows},
          open(os.path.join(HERE, "rt5_00_verify.json"), "w"), indent=1)
