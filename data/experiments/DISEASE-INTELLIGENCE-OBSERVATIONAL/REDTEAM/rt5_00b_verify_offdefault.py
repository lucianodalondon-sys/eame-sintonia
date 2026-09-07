#!/usr/bin/env python3
"""RT5 · gate 0b. The fast harness must also match the engine AWAY from the
declared defaults, or the sweep proves nothing. Six off-default configurations,
all ten provinces, all three metrics for one of them.

It also probes an engine behaviour worth naming: cell() computes the matched
panel even when the observation gate fails, then overwrites historical_state with
the matched verdict. So a province can carry a historical class while
quality.publishable is False."""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L
sys.path.insert(0, L.ENGINE)
import di_core, di_observe

AS_OF = dt.date(2026, 9, 6)
M = "ACTIVE_INFESTATION_COUNT"
sheet = di_core.load_sheet()
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)
idx, _ = L.get_index(M)

CONFIGS = [
    ("MIN_PANEL_OVERLAP=3", {"MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE": 3}),
    ("MIN_PANEL_OVERLAP=15", {"MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE": 15}),
    ("WINDOW_DAYS=14", {"WINDOW_DAYS": 14}),
    ("WINDOW_DAYS=56", {"WINDOW_DAYS": 56}),
    ("HIGH_PCTL=0.6", {"HIGH_PCTL": 0.6}),
    ("MIN_VISITS=60, MIN_DRUPES=6000", {"MIN_VISITS": 60, "MIN_DRUPES": 6000}),
    ("MIN_BASELINE_SEASONS=2", {"MIN_BASELINE_SEASONS": 2}),
]

bad = 0
quirk = []
for label, over in CONFIGS:
    P = dict(L.PARAMS)
    P.update(over)
    for p in idx.provinces:
        ref = di_observe.cell(loaded["visits"], sheet, p, M, AS_OF, params=P)
        fast = L.cell(idx, p, AS_OF, P=P)
        pairs = {
            "hist": (ref["analysis"]["historical_state"], fast["historical_state"]),
            "matched_seasons": (ref["analysis"]["matched_panel_seasons"],
                                fast["matched_panel_seasons"]),
            "trend": (ref["analysis"]["observed_trend"], fast["observed_trend"]),
            "value": (ref["observation"].get("value_pct"), fast["value_pct"]),
            "pub": (ref["quality"]["publishable"], fast["publishable"]),
        }
        d = {k: v for k, v in pairs.items() if v[0] != v[1]}
        if d:
            bad += 1
            print(f"  MISMATCH {label:32s} {p:15s} {d}")
        if (not ref["quality"]["publishable"]
                and ref["analysis"]["historical_state"] != "INSUFFICIENT_DATA"):
            quirk.append({"config": label, "province": p,
                          "historical_state": ref["analysis"]["historical_state"],
                          "publishable": ref["quality"]["publishable"],
                          "n_visits": ref["observation"].get("n_visits", 0),
                          "drupes": ref["observation"].get("drupes_sampled", 0)})
    print(f"  {label:34s} checked {len(idx.provinces)} provinces")

print(f"\n{bad} mismatches across {len(CONFIGS)*len(idx.provinces)} province-configurations.")
print(f"\nENGINE QUIRK: cells carrying a historical class while quality.publishable "
      f"is False: {len(quirk)}")
for q in quirk:
    print(f"   {q['config']:32s} {q['province']:15s} {q['historical_state']} "
          f"but publishable={q['publishable']} ({q['n_visits']} visits, "
          f"{q['drupes']} drupes)")

# the emitted params field
P = dict(L.PARAMS); P["WINDOW_DAYS"] = 14
ref = di_observe.cell(loaded["visits"], sheet, "Firenze", M, AS_OF, params=P)
print(f"\nEMITTED PARAMS BUG: cell() run with WINDOW_DAYS=14 emits "
      f"params.WINDOW_DAYS = {ref['params']['WINDOW_DAYS']} "
      f"(the module default, not the one used); its window was "
      f"{ref['observation']['window']}")

json.dump({"mismatches": bad, "configs": [c[0] for c in CONFIGS],
           "publishable_false_with_a_class": quirk,
           "emitted_params_window_days": ref["params"]["WINDOW_DAYS"],
           "actual_window": ref["observation"]["window"]},
          open(os.path.join(HERE, "rt5_00b_verify_offdefault.json"), "w"), indent=1)
