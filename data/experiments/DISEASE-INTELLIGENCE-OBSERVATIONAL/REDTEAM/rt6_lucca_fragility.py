#!/usr/bin/env python3
"""RT6-G. How many olives does it take to switch the headline of the whole region report?
Lucca is the only INVESTIGATE and the only entry under 'a subir'. Perturb it."""
import os, sys, copy, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe, di_adama

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
M = "ACTIVE_INFESTATION_COUNT"
sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
adama = di_adama.relevance("Olive", "Olive Fruit Fly")

def lucca(visits, params=None):
    c = di_observe.cell(visits, sheet, "Lucca", M, AS_OF,
                        params=params or di_observe.PARAMS)
    return c, di_adama.attention_class(c, adama)

c0, a0 = lucca(loaded["visits"])
print(f"BASE  rate={c0['observation']['value_pct']}%  "
      f"({c0['observation']['infested_drupes']}/{c0['observation']['drupes_sampled']})  "
      f"trend={c0['analysis']['observed_trend']}  attention={a0['attention_class']}")
print(f"      trend reason: {c0['analysis']['observed_trend_reason']}")
print(f"      threshold TREND_MIN_ABS_CHANGE_PCT = "
      f"{di_observe.PARAMS['TREND_MIN_ABS_CHANGE_PCT']} pp; observed change "
      f"{c0['analysis']['observed_trend_points'][-1]['rate_pct'] - c0['analysis']['observed_trend_points'][0]['rate_pct']:.4f} pp")

print("\n--- 1. REMOVE INFESTED OLIVES FROM THE CURRENT WINDOW, ONE AT A TIME ---")
lo, hi = AS_OF - dt.timedelta(days=27), AS_OF
cand = sorted([v for v in loaded["visits"]
               if v["province"] == "Lucca" and v["usable_for_rates"]
               and lo <= dt.date.fromisoformat(v["observation_date"]) <= hi
               and (v["measurements"][M]["value"] or 0) > 0],
              key=lambda v: (v["observation_date"], str(v["visit_key"]["id_field"])))
print(f"  usable Lucca visits in the window with a positive count: {len(cand)}")
for k in range(0, 9):
    vs = copy.deepcopy(loaded["visits"])
    removed = 0
    for v in vs:
        if removed >= k:
            break
        if (v["province"] == "Lucca" and v["usable_for_rates"]
                and lo <= dt.date.fromisoformat(v["observation_date"]) <= hi
                and (v["measurements"][M]["value"] or 0) > 0):
            take = min(v["measurements"][M]["value"], k - removed)
            v["measurements"][M]["value"] -= take
            removed += take
    c, a = lucca(vs)
    print(f"  -{k:2d} infested olives  rate={c['observation']['value_pct']:.4f}%  "
          f"trend={c['analysis']['observed_trend']:19s} attention={a['attention_class']}")

print("\n--- 2. VARY ONE DECLARED PARAMETER AT A TIME ---")
for name, vals in (("TREND_MIN_ABS_CHANGE_PCT", [0.5, 0.9, 1.0, 1.05, 1.1, 1.5, 2.0]),
                   ("MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE", [2, 4, 6, 8, 10]),
                   ("MIN_BASELINE_SEASONS", [2, 3, 4, 5, 6]),
                   ("WINDOW_DAYS", [14, 21, 28, 35, 42])):
    print(f"  {name}:")
    for v in vals:
        P = dict(di_observe.PARAMS); P[name] = v
        c, a = lucca(loaded["visits"], P)
        star = "  <-- shipped" if v == di_observe.PARAMS[name] else ""
        print(f"    {v:>6}  rate={c['observation']['value_pct']}  "
              f"hist={c['analysis']['historical_state']:18s} "
              f"trend={c['analysis']['observed_trend']:19s} "
              f"attention={a['attention_class']:13s}{star}")

print("\n--- 3. WHAT THE REGION HEADLINE SAYS UNDER EACH ---")
for v in (1.0, 1.1):
    P = dict(di_observe.PARAMS); P["TREND_MIN_ABS_CHANGE_PCT"] = v
    provs = sorted({x["province"] for x in loaded["visits"] if x["province"]})
    cs = [di_observe.cell(loaded["visits"], sheet, p, M, AS_OF, params=P) for p in provs]
    rising = [x["province"] for x in cs
              if x["analysis"]["observed_trend"] == "INCREASING_OBSERVED"]
    inv = [x["province"] for x in cs
           if di_adama.attention_class(x, adama)["attention_class"] == "INVESTIGATE"]
    print(f"  TREND_MIN_ABS_CHANGE_PCT={v}: 'a subir'={rising}  INVESTIGATE={inv}")
