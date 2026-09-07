#!/usr/bin/env python3
"""RT5 · accusation 7. Multiplicity, and the base rate of a directional call.

The tool is a walk-forward screen: 10 provinces x 3 metrics x every date it is
asked. Nothing corrects for that. This runs the WHOLE screen over the archive
(7-day step, 2010-2026) and counts:

  - how many cells speak at all,
  - how many say BELOW_HISTORICAL or ABOVE_HISTORICAL,
  - what the EXPECTED number of directional calls is under exchangeability of
    the current season with its k matched seasons (P = (m+1)/(k+1) each tail,
    where m is the largest number of contrary seasons the rule still tolerates),
  - the BELOW/ABOVE balance, which under a stationary process should be roughly
    symmetric and is not.
"""
import os, sys, json, collections, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

P = L.PARAMS
LAST = dt.date(2026, 9, 6)
START = dt.date(2010, 4, 1)
STEP = 7
METRICS = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
           "TOTAL_INFESTATION_COUNT"]


def max_contrary(k):
    """Largest number of contrary seasons for which the rule still fires."""
    m = 0
    while m <= k and (k - m) / k >= P["HIGH_PCTL"]:
        m += 1
    return m - 1


rows = []
for metric in METRICS:
    idx, _ = L.get_index(metric)
    d = START
    while d <= LAST:
        for c in L.all_cells(idx, d):
            rows.append({"metric": metric, "date": d.isoformat(),
                         "prov": c["province"], "state": c["historical_state"],
                         "k": c.get("n_matched"), "lower": c.get("n_lower"),
                         "higher": c.get("n_higher"), "trend": c["observed_trend"],
                         "rate": c["value_pct"]})
        d += dt.timedelta(days=STEP)
    print(f"done {metric}: {len(rows)} cells so far", flush=True)

n = len(rows)
speak = [r for r in rows if r["state"] != "INSUFFICIENT_DATA"]
cnt = collections.Counter(r["state"] for r in rows)
below = cnt["BELOW_HISTORICAL"]
above = cnt["ABOVE_HISTORICAL"]
typ = cnt["TYPICAL"]

exp_below = exp_above = 0.0
for r in speak:
    k = r["k"]
    m = max_contrary(k)
    exp_below += (m + 1) / (k + 1)
    exp_above += (m + 1) / (k + 1)

dates = sorted({r["date"] for r in rows})
per_day = collections.Counter()
for r in rows:
    if r["state"] in ("BELOW_HISTORICAL", "ABOVE_HISTORICAL"):
        per_day[r["date"]] += 1
days_with_a_call = sum(1 for d in dates if per_day[d] > 0)

print(f"\nWALK-FORWARD SCREEN, {START} to {LAST}, every {STEP} days")
print(f"  publication dates                  : {len(dates):,}")
print(f"  cells run (10 provinces x 3 metrics x dates): {n:,}")
print(f"  INSUFFICIENT_DATA                  : {cnt['INSUFFICIENT_DATA']:,} of {n:,} "
      f"({100*cnt['INSUFFICIENT_DATA']/n:.1f}%)")
print(f"  cells with a historical class      : {len(speak):,} of {n:,} "
      f"({100*len(speak)/n:.1f}%)")
print(f"    TYPICAL                          : {typ:,} ({100*typ/len(speak):.1f}% of speaking)")
print(f"    BELOW_HISTORICAL                 : {below:,} ({100*below/len(speak):.1f}%)")
print(f"    ABOVE_HISTORICAL                 : {above:,} ({100*above/len(speak):.1f}%)")
print(f"  directional calls                  : {below+above:,} "
      f"({100*(below+above)/len(speak):.1f}% of speaking cells)")
print(f"  EXPECTED under exchangeability     : {exp_below+exp_above:.0f} "
      f"({100*(exp_below+exp_above)/len(speak):.1f}% of speaking cells), "
      f"{exp_below:.0f} BELOW + {exp_above:.0f} ABOVE")
print(f"  observed/expected                  : {(below+above)/(exp_below+exp_above):.2f}x")
print(f"  BELOW:ABOVE ratio observed         : {below}:{above} "
      f"({below/max(above,1):.2f}:1); expected 1:1")
print(f"  dates on which at least one province+metric gets a directional call: "
      f"{days_with_a_call:,} of {len(dates):,} ({100*days_with_a_call/len(dates):.1f}%)")

# per metric
print("\n  by metric:")
for m in METRICS:
    sub = [r for r in rows if r["metric"] == m]
    sp = [r for r in sub if r["state"] != "INSUFFICIENT_DATA"]
    c = collections.Counter(r["state"] for r in sub)
    print(f"    {m:30s} speak {len(sp):>5} of {len(sub):>5}  "
          f"BELOW {c['BELOW_HISTORICAL']:>5}  ABOVE {c['ABOVE_HISTORICAL']:>5}  "
          f"TYPICAL {c['TYPICAL']:>5}")

# per province, ACTIVE only
print("\n  by province (ACTIVE_INFESTATION_COUNT only):")
for prov in sorted({r["prov"] for r in rows}):
    sub = [r for r in rows if r["prov"] == prov and r["metric"] == METRICS[0]]
    c = collections.Counter(r["state"] for r in sub)
    sp = len(sub) - c["INSUFFICIENT_DATA"]
    print(f"    {prov:15s} speak {sp:>4} of {len(sub):>4}  BELOW {c['BELOW_HISTORICAL']:>4} "
          f" ABOVE {c['ABOVE_HISTORICAL']:>4}  TYPICAL {c['TYPICAL']:>4}")

# how often does a province's class flip between consecutive publication dates?
print("\n  CLASS CHURN (ACTIVE only): consecutive publication dates 7 days apart")
churn = {}
for prov in sorted({r["prov"] for r in rows}):
    seq = [r["state"] for r in sorted(
        (r for r in rows if r["prov"] == prov and r["metric"] == METRICS[0]),
        key=lambda x: x["date"])]
    pairs = [(a, b) for a, b in zip(seq, seq[1:])
             if a != "INSUFFICIENT_DATA" and b != "INSUFFICIENT_DATA"]
    flips = sum(1 for a, b in pairs if a != b)
    churn[prov] = {"consecutive_speaking_pairs": len(pairs), "class_changes": flips,
                   "pct": round(100 * flips / len(pairs), 1) if pairs else None}
    print(f"    {prov:15s} class changed on {flips} of {len(pairs)} consecutive "
          f"7-day steps ({churn[prov]['pct']}%)")

json.dump({"start": START.isoformat(), "last": LAST.isoformat(), "step_days": STEP,
           "n_cells": n, "n_speaking": len(speak), "counts": dict(cnt),
           "expected_directional_under_exchangeability": round(exp_below + exp_above, 1),
           "observed_directional": below + above,
           "dates": len(dates), "days_with_a_call": days_with_a_call,
           "churn": churn, "rows": rows},
          open(os.path.join(HERE, "rt5_07_multiplicity.json"), "w"), indent=1)
print("\nwrote rt5_07_multiplicity.json")
