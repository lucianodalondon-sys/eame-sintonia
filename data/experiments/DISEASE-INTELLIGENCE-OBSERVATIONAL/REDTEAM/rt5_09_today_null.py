#!/usr/bin/env python3
"""RT5 · accusation 9 and the counter-evidence.

(a) TODAY'S FAMILY-WISE NULL. On one publication day the tool runs 10 provinces
    x 3 metrics. Under exchangeability each speaking cell has a known probability
    of firing BELOW. What is the exact distribution of the number of BELOW
    headlines on a day when nothing is happening?

(b) WHERE DOES 2026 ACTUALLY SIT? Independently of the matched-panel machinery:
    the pooled rate in the 10 Aug - 6 Sep window, per province and for Toscana as
    a whole, for every season 2006-2026, with denominators. This is the question
    the verdict is trying to answer, asked without the counting rule.

(c) DOES THE VERDICT AGREE ACROSS METRICS? Three metrics measure the same
    infestation. Agreement is evidence; disagreement is noise."""
import os, sys, json, itertools, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
P = L.PARAMS
METRICS = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
           "TOTAL_INFESTATION_COUNT"]


def max_contrary(k):
    m = 0
    while m <= k and (k - m) / k >= P["HIGH_PCTL"]:
        m += 1
    return m - 1


# ── (a) family-wise null ─────────────────────────────────────────────────────
print("(a) FAMILY-WISE NULL FOR ONE PUBLICATION DAY")
cells_by_metric = {}
ps = []
for m in METRICS:
    idx, _ = L.get_index(m)
    cs = L.all_cells(idx, AS_OF)
    cells_by_metric[m] = cs
    for c in cs:
        if c["historical_state"] == "INSUFFICIENT_DATA":
            continue
        k = c["n_matched"]
        p = (max_contrary(k) + 1) / (k + 1)
        ps.append({"metric": m, "prov": c["province"], "k": k, "p_below": round(p, 4),
                   "state": c["historical_state"]})
        print(f"    {m[:6]:6s} {c['province']:14s} k={k:>3}  P(BELOW under exchangeability) "
              f"= {max_contrary(k)+1}/{k+1} = {p:.4f}   published {c['historical_state']}")


def dist(prob):
    d = [1.0]
    for p in prob:
        nd = [0.0] * (len(d) + 1)
        for i, x in enumerate(d):
            nd[i] += x * (1 - p)
            nd[i + 1] += x * p
        d = nd
    return d


active = [x for x in ps if x["metric"] == METRICS[0]]
obs_active = sum(1 for x in active if x["state"] == "BELOW_HISTORICAL")
d1 = dist([x["p_below"] for x in active])
print(f"\n    ACTIVE only, {len(active)} speaking provinces:")
print(f"      expected BELOW headlines under exchangeability = "
      f"{sum(x['p_below'] for x in active):.3f}")
print(f"      P(0)={d1[0]:.4f} P(1)={d1[1]:.4f} P(2)={d1[2]:.4f} P(3)={d1[3]:.4f}")
print(f"      observed {obs_active};  P(at least {obs_active}) = "
      f"{sum(d1[obs_active:]):.4f}")
print(f"      P(at least one BELOW headline on a nothing-happening day) = {1-d1[0]:.4f}")

obs_all = sum(1 for x in ps if x["state"] == "BELOW_HISTORICAL")
dA = dist([x["p_below"] for x in ps])
print(f"\n    all three metrics, {len(ps)} speaking cells:")
print(f"      expected BELOW = {sum(x['p_below'] for x in ps):.3f}; "
      f"observed {obs_all}; P(at least {obs_all}) = {sum(dA[obs_all:]):.4f}")
print(f"      P(at least one BELOW headline) = {1-dA[0]:.4f}")

# ── (b) the season level, without the counting rule ──────────────────────────
print("\n(b) POOLED RATE IN THE 10 AUG - 6 SEP WINDOW, BY SEASON "
      "(ACTIVE_INFESTATION_COUNT)")
idx, _ = L.get_index(METRICS[0])
lo, hi = L.win(AS_OF, P["WINDOW_DAYS"])
season_tab = {}
for prov in idx.provinces:
    row = {}
    for y in range(2006, 2027):
        w = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
            row[y] = {"rate": w["rate_pct"], "inf": w["infested_drupes"],
                      "den": w["drupes_sampled"], "groves": w["n_sites"]}
    season_tab[prov] = row
    if len(row) >= 5:
        rates = {y: r["rate"] for y, r in row.items()}
        now = rates.get(2026)
        prior = {y: v for y, v in rates.items() if y != 2026}
        rank = (sorted(prior.values()) + [now]).index(now) + 1 if now is not None else None
        n_below = sum(1 for v in prior.values() if v > now) if now is not None else None
        print(f"  {prov:15s} 2026 = {now}%  ({row[2026]['inf']}/{row[2026]['den']} drupes)  "
              f"is lower than {n_below} of {len(prior)} prior seasons with data;  "
              f"prior median {statistics.median(prior.values()):.4f}%, "
              f"min {min(prior.values())}% max {max(prior.values())}%")

# region-wide
print("\n  TOSCANA, all provinces pooled, same calendar window:")
reg = {}
for y in range(2006, 2027):
    num = den = 0
    gv = 0
    for prov in idx.provinces:
        w = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if w:
            num += w["infested_drupes"]
            den += w["drupes_sampled"]
            gv += w["n_sites"]
    if den:
        reg[y] = {"rate": round(100 * num / den, 4), "inf": num, "den": den, "groves": gv}
        print(f"    {y}  {reg[y]['rate']:>8.4f}%   {num:>6} infested of {den:>7} drupes, "
              f"{gv} groves")
prior = [v["rate"] for y, v in reg.items() if y != 2026]
print(f"    2026 is lower than {sum(1 for v in prior if v > reg[2026]['rate'])} of "
      f"{len(prior)} prior seasons region-wide")

# ── (c) agreement across metrics ─────────────────────────────────────────────
print("\n(c) DO THE THREE METRICS AGREE TODAY?")
print(f"  {'province':15s} " + " ".join(f"{m[:8]:>18}" for m in METRICS))
agree = {}
for i, prov in enumerate(idx.provinces):
    states = [cells_by_metric[m][i]["historical_state"] for m in METRICS]
    rates = [cells_by_metric[m][i]["value_pct"] for m in METRICS]
    agree[prov] = {"states": states, "rates": rates}
    print(f"  {prov:15s} " + " ".join(f"{s:>18}" for s in states))
print(f"  {'  rates %':15s} ")
for i, prov in enumerate(idx.provinces):
    print(f"  {prov:15s} " + " ".join(
        f"{str(cells_by_metric[m][i]['value_pct']):>18}" for m in METRICS))

json.dump({"family_wise": {"cells": ps, "dist_active": d1, "dist_all": dA,
                           "observed_active": obs_active, "observed_all": obs_all},
           "season_table": season_tab, "region": reg, "metric_agreement": agree},
          open(os.path.join(HERE, "rt5_09_today_null.json"), "w"), indent=1)
print("\nwrote rt5_09_today_null.json")
