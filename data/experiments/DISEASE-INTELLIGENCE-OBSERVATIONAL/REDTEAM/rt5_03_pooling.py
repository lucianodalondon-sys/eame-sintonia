#!/usr/bin/env python3
"""RT5 · accusation 3. Pooling is a choice of weights, and the choice is not neutral.

sum(infested)/sum(sampled) weights each grove by how many times it was visited
and by how many drupes were counted there. Four defensible alternatives are
recomputed end to end -- the current window, every baseline season, every matched
panel and the trend -- and the ten verdicts are read off each time.

Also reported: the weight concentration the pooling hides (visits per grove,
share of the denominator carried by the top grove / top 5 groves)."""
import os, sys, json, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
idx, raw = L.get_index("ACTIVE_INFESTATION_COUNT")
HOWS = ["pooled", "mean_visit", "median_visit", "mean_grove", "median_grove"]

base = {c["province"]: c for c in L.all_cells(idx, AS_OF, how="pooled")}
rows = {}
for how in HOWS:
    cells = L.all_cells(idx, AS_OF, how=how)
    rows[how] = {c["province"]: c for c in cells}

print(f"{'province':15s} " + " ".join(f"{h:>17}" for h in HOWS))
print("-- point estimate of the current window, % of sampled drupes --")
for p in idx.provinces:
    print(f"{p:15s} " + " ".join(f"{str(rows[h][p]['value_pct']):>17}" for h in HOWS))
print("\n-- historical_state --")
flips = []
for p in idx.provinces:
    print(f"{p:15s} " + " ".join(f"{rows[h][p]['historical_state']:>17}" for h in HOWS))
    for h in HOWS[1:]:
        if rows[h][p]["historical_state"] != base[p]["historical_state"]:
            flips.append((p, h, base[p]["historical_state"], rows[h][p]["historical_state"]))
print("\n-- observed_trend --")
tflips = []
for p in idx.provinces:
    print(f"{p:15s} " + " ".join(f"{rows[h][p]['observed_trend']:>17}" for h in HOWS))
    for h in HOWS[1:]:
        if rows[h][p]["observed_trend"] != base[p]["observed_trend"]:
            tflips.append((p, h, base[p]["observed_trend"], rows[h][p]["observed_trend"]))
print("\n-- matched-panel counts (lower of matched) --")
for p in idx.provinces:
    print(f"{p:15s} " + " ".join(
        f"{(str(rows[h][p].get('n_lower'))+'/'+str(rows[h][p].get('n_matched'))):>17}"
        for h in HOWS))

print("\nHISTORICAL VERDICT FLIPS vs pooled:")
for f in flips:
    print(f"   {f[0]:15s} {f[1]:14s} {f[2]} -> {f[3]}")
print("TREND FLIPS vs pooled:")
for f in tflips:
    print(f"   {f[0]:15s} {f[1]:14s} {f[2]} -> {f[3]}")

# ── weight concentration ─────────────────────────────────────────────────────
print("\n-- what pooling weights by, in the published window --")
lo, hi = L.win(AS_OF, L.PARAMS["WINDOW_DAYS"])
conc = {}
for p in idx.provinces:
    cur = idx.pooled(p, lo, hi, as_of=AS_OF)
    if not cur:
        continue
    den = cur["per_site_den"]
    tot = sum(den.values())
    vis = {}
    for v in idx.slice(p, lo, hi):
        if v["usable"] and v[idx.metric] is not None and v["den"] is not None:
            vis[v["id_field"]] = vis.get(v["id_field"], 0) + 1
    ordered = sorted(den.values(), reverse=True)
    conc[p] = {"n_groves": len(den), "n_visits": cur["n_visits"],
               "visits_per_grove_min": min(vis.values()), "max": max(vis.values()),
               "median": statistics.median(vis.values()),
               "top1_share_of_denominator": round(ordered[0] / tot, 4),
               "top5_share_of_denominator": round(sum(ordered[:5]) / tot, 4),
               "effective_n_groves_kish": round(tot ** 2 / sum(x * x for x in den.values()), 2)}
    c = conc[p]
    print(f"{p:15s} groves {c['n_groves']:>4}  visits {c['n_visits']:>4}  "
          f"visits/grove min {c['visits_per_grove_min']} med {c['median']} "
          f"max {c['max']}  top-1 {100*c['top1_share_of_denominator']:.1f}% "
          f"top-5 {100*c['top5_share_of_denominator']:.1f}%  "
          f"effective groves (Kish) {c['effective_n_groves_kish']} of {c['n_groves']}")

json.dump({"as_of": AS_OF.isoformat(),
           "by_how": {h: {p: {k: rows[h][p][k] for k in
                              ("value_pct", "historical_state", "observed_trend",
                               "matched_panel_seasons", "trend_points")
                              if k in rows[h][p]} for p in idx.provinces} for h in HOWS},
           "historical_flips": flips, "trend_flips": tflips,
           "weight_concentration": conc},
          open(os.path.join(HERE, "rt5_03_pooling.json"), "w"), indent=1)
