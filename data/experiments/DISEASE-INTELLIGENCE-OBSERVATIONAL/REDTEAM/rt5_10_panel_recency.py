#!/usr/bin/env python3
"""RT5 · accusation 10. The matched-panel gate is a recency filter in disguise.

The monitored network grows and rotates, so the number of groves this window
shares with season y rises almost monotonically with y. Requiring 8 shared groves
therefore does not select "comparable seasons" -- it selects RECENT seasons. The
baseline the tool calls "its own history" is a moving 6-to-17-year tail, different
per province, and it disagrees with the full-history comparison the engine also
computes but does not publish."""
import os, sys, json, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
P = L.PARAMS
idx, _ = L.get_index("ACTIVE_INFESTATION_COUNT")
lo, hi = L.win(AS_OF, P["WINDOW_DAYS"])


def spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for t in range(i, j + 1):
                r[s[t]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return round(num / den, 4) if den else None


print("SHARED GROVES vs SEASON: is the gate a recency filter?")
rows = {}
for prov in idx.provinces:
    cur = idx.pooled(prov, lo, hi, as_of=AS_OF)
    if not cur:
        continue
    ys, ns = [], []
    for y in range(2006, 2026):
        b = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if b:
            ys.append(y)
            ns.append(len(cur["sites"] & b["sites"]))
    rho = spearman(ys, ns)
    passing = [y for y, n in zip(ys, ns) if n >= P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]]
    rows[prov] = {"spearman_year_vs_shared_groves": rho,
                  "seasons_with_data": ys, "shared": ns,
                  "seasons_passing_the_gate": passing,
                  "earliest_baseline_season_used": min(passing) if passing else None,
                  "n_passing": len(passing), "n_with_data": len(ys)}
    print(f"  {prov:15s} Spearman(season, shared groves) = {rho:>7}   "
          f"gate admits {len(passing)} of {len(ys)} seasons, earliest "
          f"{min(passing) if passing else '-'}")

print("\nMATCHED (published) vs UNMATCHED (computed, not published)")
print(f"  {'province':15s} {'matched':>18} {'k':>3}  {'unmatched':>18} {'k':>3}  "
      f"{'2026 rate':>10} {'prior median':>12}  {'lower than':>12}")
disagree = []
for c in L.all_cells(idx, AS_OF):
    p = c["province"]
    # full-history rank on the complete network, same calendar window
    prior = []
    for y in range(2006, 2026):
        w = idx.pooled(p, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
            prior.append(w["rate_pct"])
    nb = sum(1 for v in prior if v > c["value_pct"]) if c["value_pct"] is not None else None
    print(f"  {p:15s} {c['historical_state']:>18} "
          f"{str(c.get('n_matched') or '-'):>3}  {c['historical_state_unmatched']:>18} "
          f"{len(prior):>3}  {str(c['value_pct']):>10} "
          f"{str(round(statistics.median(prior),4)) if prior else '-':>12}  "
          f"{f'{nb} of {len(prior)}':>12}")
    if (c["historical_state"] != c["historical_state_unmatched"]
            and "INSUFFICIENT_DATA" not in (c["historical_state"],
                                            c["historical_state_unmatched"])):
        disagree.append((p, c["historical_state"], c["historical_state_unmatched"]))
    rows.setdefault(p, {}).update({
        "matched_state": c["historical_state"], "matched_k": c.get("n_matched"),
        "unmatched_state": c["historical_state_unmatched"],
        "rate_2026": c["value_pct"], "prior_full_network": prior,
        "n_prior_seasons_higher": nb})

print("\n  matched and unmatched DISAGREE where both speak:")
for d in disagree:
    print(f"    {d[0]:15s} matched says {d[1]}, full history says {d[2]}")
if not disagree:
    print("    none")

json.dump(rows, open(os.path.join(HERE, "rt5_10_panel_recency.json"), "w"), indent=1)
print("\nwrote rt5_10_panel_recency.json")
