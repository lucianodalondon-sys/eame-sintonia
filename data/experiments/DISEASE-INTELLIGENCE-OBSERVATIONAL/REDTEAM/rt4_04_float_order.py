#!/usr/bin/env python3
"""RT4-04  Float summation order and the rounding boundary.

The pooled rate is  round(100.0 * num / den, 4)  where num and den are built by  += over
the visits in whatever order the visit list happens to be in. Two questions:

  Q1  Do NON-INTEGER values actually enter the sums? (If every addend is an exact integer
      under 2^53, addition is associative and order cannot matter at all.)
  Q2  If they do, does ANY permutation of the addends move the published 4-decimal rate?
      I do not guess: for every province x metric x window that the report publishes I
      recompute the sum under 6 orders - as published, reversed, sorted ascending by value,
      sorted descending, and two fixed pseudo-random shuffles - and compare
      round(100*num/den,4), int(num) and int(den) each time.
  Q3  How close is each published rate to a rounding boundary (x.xxxx5)? I report the
      distance in ULPs of the quotient, so "could a different sum order flip it" has a
      number rather than an opinion.

This is a DIFFERENT experiment from the tool's: the tool permuted FILE order, which the
loader then re-sorts away. I permute the ADDENDS themselves, which nothing re-sorts.
"""
import os, sys, json, math, random, itertools, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
METRICS = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
           "TOTAL_INFESTATION_COUNT"]
DEN = "SAMPLE_SIZE / DENOMINATOR"


def addends(visits, lo, hi, province, metric):
    """Exactly the pairs pooled() would add, in exactly the order pooled() would add them."""
    out = []
    for v in visits:
        if v["province"] != province:
            continue
        d = dt.date.fromisoformat(v["observation_date"])
        if not (lo <= d <= hi):
            continue
        if not v["usable_for_rates"]:
            continue
        c = v["measurements"][metric]["value"]
        t = v["measurements"][DEN]["value"]
        if c is None or t is None:
            continue
        out.append((c, t))
    return out


def rate(pairs):
    num = den = 0.0
    for c, t in pairs:
        num += c
        den += t
    return (round(100.0 * num / den, 4) if den else None), num, den, int(num), int(den)


def ulps_to_boundary(q):
    """q is 100*num/den. round(q,4) flips at the midpoint. Distance in ULPs of q."""
    scaled = q * 1e4
    frac = scaled - math.floor(scaled)
    dist = abs(frac - 0.5)                 # in units of 1e-4 of q
    dist_abs = dist * 1e-4
    u = math.ulp(q)
    return dist_abs, (dist_abs / u if u else float("inf"))


sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
visits = loaded["visits"]
provs = sorted({v["province"] for v in visits if v["province"]})

report = {"AS_OF": AS_OF.isoformat(), "Q1_non_integer_addends": {}, "Q2_order": [],
          "Q3_boundary": [], "windows_tested": 0}

# ---- Q1
tot_c = tot_nonint_c = tot_nonint_t = 0
for v in visits:
    for m in METRICS:
        x = v["measurements"][m]["value"]
        if x is not None:
            tot_c += 1
            if x != int(x):
                tot_nonint_c += 1
    t = v["measurements"][DEN]["value"]
    if t is not None and t != int(t):
        tot_nonint_t += 1
report["Q1_non_integer_addends"] = {
    "numerator_values_read": tot_c,
    "numerator_values_that_are_NOT_integers": tot_nonint_c,
    "denominator_values_that_are_NOT_integers": tot_nonint_t,
    "NOTE": "if both are 0, float addition of these addends is exact and order is provably "
            "irrelevant; if not 0, order can matter and Q2 decides whether it does"}

# ---- Q2 + Q3 over every window the report actually builds:
#      the current window, every baseline season window, and the trend windows.
P = di_observe.PARAMS
lo0, hi0 = di_observe._win(AS_OF, P["WINDOW_DAYS"])
windows = [("current", lo0, hi0)]
for y in range(2006, AS_OF.year):
    windows.append((f"baseline_{y}", di_observe._shift(lo0, y), di_observe._shift(hi0, y)))
for i in range(1, P["TREND_MIN_WINDOWS"] + 1):
    h = AS_OF - dt.timedelta(days=P["WINDOW_DAYS"] * i)
    windows.append((f"trend_-{i}", h - dt.timedelta(days=P["WINDOW_DAYS"] - 1), h))

rng = random.Random(20260906)
disagreements = []
worst = []
for metric in METRICS:
    for p in provs:
        for wname, lo, hi in windows:
            pairs = addends(visits, lo, hi, p, metric)
            if not pairs:
                continue
            report["windows_tested"] += 1
            base = rate(pairs)
            orders = {"as_published": pairs,
                      "reversed": list(reversed(pairs)),
                      "sorted_val_asc": sorted(pairs, key=lambda x: (x[0], x[1])),
                      "sorted_val_desc": sorted(pairs, key=lambda x: (-x[0], -x[1])),
                      "shuffle_a": rng.sample(pairs, len(pairs)),
                      "shuffle_b": rng.sample(pairs, len(pairs))}
            seen = {}
            for oname, pp in orders.items():
                r = rate(pp)
                seen[oname] = {"rate_pct": r[0], "num_float": repr(r[1]),
                               "den_float": repr(r[2]),
                               "int_num": r[3], "int_den": r[4]}
            distinct_rate = {v["rate_pct"] for v in seen.values()}
            distinct_int = {(v["int_num"], v["int_den"]) for v in seen.values()}
            distinct_float = {(v["num_float"], v["den_float"]) for v in seen.values()}
            if len(distinct_rate) > 1 or len(distinct_int) > 1:
                disagreements.append({"metric": metric, "province": p, "window": wname,
                                      "n_addends": len(pairs), "orders": seen})
            elif len(distinct_float) > 1:
                # exact float sum differed but the rounded answer survived - still worth it
                disagreements.append({"metric": metric, "province": p, "window": wname,
                                      "n_addends": len(pairs),
                                      "SAME_ROUNDED_DIFFERENT_FLOAT": True, "orders": seen})
            if base[2]:
                q = 100.0 * base[1] / base[2]
                dist, ulps = ulps_to_boundary(q)
                worst.append({"metric": metric, "province": p, "window": wname,
                              "rate_pct": base[0], "q": repr(q),
                              "distance_to_rounding_boundary": dist,
                              "distance_in_ULPs_of_q": ulps,
                              "n_addends": len(pairs),
                              "num": repr(base[1]), "den": repr(base[2])})

worst.sort(key=lambda x: x["distance_in_ULPs_of_q"])
report["Q2_order"] = {"n_windows_where_any_order_changed_something": len(disagreements),
                      "detail": disagreements[:20]}
report["Q3_boundary"] = {"n_windows_scored": len(worst),
                         "closest_20_to_a_rounding_boundary": worst[:20],
                         "n_within_1000_ULPs": sum(1 for w in worst
                                                   if w["distance_in_ULPs_of_q"] < 1000),
                         "n_within_1e6_ULPs": sum(1 for w in worst
                                                  if w["distance_in_ULPs_of_q"] < 1e6)}
json.dump(report, open(os.path.join(HERE, "rt4_04_float_order.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps({k: v for k, v in report.items() if k != "Q3_boundary"},
                 indent=1, default=str)[:4000])
print("\nCLOSEST TO A ROUNDING BOUNDARY (top 8):")
for w in worst[:8]:
    print(f"  {w['metric'][:6]} {w['province']:12s} {w['window']:14s} rate={w['rate_pct']} "
          f"gap={w['distance_to_rounding_boundary']:.3e} = {w['distance_in_ULPs_of_q']:.3e} ULP "
          f"n={w['n_addends']}")
print(f"\nwindows scored: {len(worst)}; within 1000 ULPs of a boundary: "
      f"{report['Q3_boundary']['n_within_1000_ULPs']}; within 1e6 ULPs: "
      f"{report['Q3_boundary']['n_within_1e6_ULPs']}")
