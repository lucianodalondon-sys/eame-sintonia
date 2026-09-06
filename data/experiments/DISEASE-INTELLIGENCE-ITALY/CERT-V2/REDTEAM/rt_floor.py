#!/usr/bin/env python3
"""
RED TEAM / LENS 2 — is MIN_POSITIVE_SITES=5 a discriminator or a post-hoc patch?

F1  TAUTOLOGY   p5's FALSE_POSITIVE_TEST and FALSE_NEGATIVE_TEST are the floor's own predicate
                read back. Swept over every floor value to show neither test can ever fail.
F2  THE GAP     the "kept min 7 / withheld max 4" gap, swept over every floor value.
F3  SWEEP       what any other floor value would have done, cell by cell.
F4  REDUNDANCY  does MIN_SITES already do this work? does a plain incidence threshold?
F5  NEW FAILURE the floor sets a per-province incidence bar of 5/n_sites. How many cells can
                only reach HIGHER with an outbreak larger than anything in their own archive?
F6  WHERE IT BITES  the cells where the floor changes a live decision, and where it does not.
F7  ROUNDING    the floor compares round(INCIDENCE,4)*n_sites, not the integer site count.

Out: REDTEAM/rt_floor.json (+ stdout)
"""
import json, os, collections
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = json.load(open(os.path.join(HERE, "rt_cells.json")))["CELLS"]
HIGHER, TYPICAL, LOWER = "HIGHER_THAN_USUAL", "TYPICAL_FOR_THE_DATE", "LOWER_THAN_USUAL"
CLASSED = (HIGHER, TYPICAL, LOWER)
cl = [c for c in CELLS if c["STATE_NO_FLOOR"] in CLASSED]
hi = [c for c in cl if c["STATE_NO_FLOOR"] == HIGHER]      # 40 rank-HIGHER cells
OUT = {}
print(f"rank-HIGHER cells (floor off) = {len(hi)} of {len(cl)} classified")


def apply_floor(c, T):
    """The shipped predicate, with the floor value as a free parameter."""
    return HIGHER if c["FLOOR_PRODUCT"] >= T else TYPICAL


# ── F1 + F2 + F3  SWEEP ──────────────────────────────────────────────────────────────
sweep = {}
for T in list(range(0, 21)) + [25, 30, 40, 50, 70] + [4.5, 5.5, 6.5]:
    kept = [c for c in hi if apply_floor(c, T) == HIGHER]
    wh = [c for c in hi if apply_floor(c, T) != HIGHER]
    # p5's two tests, recomputed at this T with p5's own definitions
    fails_open = sum(1 for c in kept if c["n_pos"] < T)
    fails_closed = sum(1 for c in wh if c["n_pos"] >= T)
    sweep[str(T)] = {
        "KEPT": len(kept), "WITHHELD": len(wh),
        "KEPT_POS_MIN": min((c["n_pos"] for c in kept), default=None),
        "WITHHELD_POS_MAX": max((c["n_pos"] for c in wh), default=None),
        "GAP": (min(c["n_pos"] for c in kept) - max(c["n_pos"] for c in wh))
               if kept and wh else None,
        "FAILS_OPEN(p5 FALSE_POSITIVE_TEST)": fails_open,
        "FAILS_CLOSED(p5 FALSE_NEGATIVE_TEST)": fails_closed,
        "KEPT_LIVE_2026": sum(1 for c in kept if c["DATE"].startswith("2026")),
        "WITHHELD_LIVE_2026": sum(1 for c in wh if c["DATE"].startswith("2026"))}
OUT["F1_F2_F3_FLOOR_SWEEP"] = sweep
print("F3 sweep (T: kept/withheld/gap/failsopen/failsclosed):")
for T, v in sweep.items():
    print(f"   T={T:<5} kept={v['KEPT']:<3} withheld={v['WITHHELD']:<3} "
          f"kept_min={v['KEPT_POS_MIN']} wh_max={v['WITHHELD_POS_MAX']} gap={v['GAP']} "
          f"open={v['FAILS_OPEN(p5 FALSE_POSITIVE_TEST)']} "
          f"closed={v['FAILS_CLOSED(p5 FALSE_NEGATIVE_TEST)']}")

hist = collections.Counter(c["n_pos"] for c in hi)
OUT["F2_POSITIVE_SITE_HISTOGRAM_OF_ALL_RANK_HIGHER_CELLS"] = dict(sorted(hist.items()))
OUT["F2_NOTE"] = ("the gap the certification reports is the empty interval in THIS histogram "
                  "between the largest withheld and the smallest kept value; every floor value "
                  "that falls inside an empty interval produces an equally 'clean' gap")
print("F2 histogram of positive sites over the 40 rank-HIGHER cells:",
      json.dumps(OUT["F2_POSITIVE_SITE_HISTOGRAM_OF_ALL_RANK_HIGHER_CELLS"]))

# how many DISTINCT partitions of the 40 rank-HIGHER cells does the floor family produce?
parts = {}
for T in range(0, 71):
    key = tuple(sorted((c["CROP"], c["DATE"], c["PROVINCE"]) for c in hi
                       if apply_floor(c, T) == HIGHER))
    parts.setdefault(key, []).append(T)
OUT["F3_DISTINCT_PARTITIONS"] = {
    "N_DISTINCT_OUTCOMES_OVER_T_0_TO_70": len(parts),
    "T_VALUES_GIVING_THE_SHIPPED_OUTCOME":
        next(v for k, v in parts.items()
             if set(k) == {(c["CROP"], c["DATE"], c["PROVINCE"]) for c in hi if c["STATE"] == HIGHER})}
print("F3 distinct outcomes over T=0..70:", OUT["F3_DISTINCT_PARTITIONS"])

# ── F4 REDUNDANCY ────────────────────────────────────────────────────────────────────
withheld5 = [c for c in hi if c["STATE"] != HIGHER]
wset = {(c["CROP"], c["DATE"], c["PROVINCE"]) for c in withheld5}
red = {}
for ms in (8, 10, 12, 15, 20, 25, 30):
    # what MIN_SITES would remove, floor OFF: cells drop out of the classified set entirely
    removed = {(c["CROP"], c["DATE"], c["PROVINCE"]) for c in hi if c["n_sites"] < ms}
    collateral = sum(1 for c in cl if c["n_sites"] < ms)     # all classified cells destroyed
    red[f"MIN_SITES={ms}"] = {
        "RANK_HIGHER_REMOVED": len(removed),
        "OVERLAP_WITH_THE_FLOORS_9": len(removed & wset),
        "MISSED_BY_MIN_SITES": len(wset - removed),
        "CLASSIFIED_CELLS_DESTROYED": f"{collateral}/{len(cl)}"}
inc = {}
for thr in (0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50):
    removed = {(c["CROP"], c["DATE"], c["PROVINCE"]) for c in hi if c["VALUE"] < thr}
    inc[f"INCIDENCE<{thr}"] = {"RANK_HIGHER_REMOVED": len(removed),
                               "IDENTICAL_PARTITION_TO_THE_FLOOR": removed == wset,
                               "SYMMETRIC_DIFFERENCE": len(removed ^ wset)}
OUT["F4_REDUNDANCY"] = {"WHAT_MIN_SITES_ALONE_WOULD_DO": red,
                        "WHAT_A_PLAIN_INCIDENCE_THRESHOLD_WOULD_DO": inc,
                        "FLOOR_WITHHELD_N_SITES": sorted(c["n_sites"] for c in withheld5),
                        "FLOOR_WITHHELD_INCIDENCE": sorted(c["VALUE"] for c in withheld5)}
print("F4 min_sites:", json.dumps(red))
print("F4 incidence threshold:", json.dumps(inc))

# ── F5 NEW FAILURE: the per-province incidence bar the floor creates ──────────────────
bar = []
for c in cl:
    need = 5.0 / c["n_sites"]                       # incidence needed to clear the floor
    hist_max = max((s["INCIDENCE"] for s in c["SEASONS_ALL"] if s["usable"]), default=0.0)
    bar.append({"CROP": c["CROP"], "DATE": c["DATE"], "PROVINCE": c["PROVINCE"],
                "n_sites": c["n_sites"], "FLOOR_NEEDS_INCIDENCE": round(need, 4),
                "HISTORICAL_MAX_INCIDENCE_SAME_WINDOW": round(hist_max, 4),
                "UNREACHABLE": need > hist_max,
                "STATE": c["STATE"]})
unreach = [b for b in bar if b["UNREACHABLE"]]
unreach_cells = {(b["CROP"], b["PROVINCE"]) for b in unreach}
by_bucket = collections.Counter()
for b in bar:
    k = "8-14" if b["n_sites"] < 15 else ("15-39" if b["n_sites"] < 40 else "40+")
    by_bucket[(k, "ALL")] += 1
    if b["UNREACHABLE"]:
        by_bucket[(k, "UNREACHABLE")] += 1
OUT["F5_STRUCTURAL_UNREACHABILITY"] = {
    "DEFINITION": "a classified province-date where the incidence the floor demands (5/n_sites) "
                  "is strictly greater than the highest incidence EVER recorded in that "
                  "province at that calendar window in any usable season — so no outbreak on "
                  "record would have been called HIGHER there",
    "COUNT": f"{len(unreach)}/{len(cl)}",
    "DISTINCT_PROVINCE_CELLS_AFFECTED": sorted(f"{a}|{b}" for a, b in unreach_cells),
    "BY_N_SITES_BUCKET": {k: f"{by_bucket[(k,'UNREACHABLE')]}/{by_bucket[(k,'ALL')]}"
                          for k in ("8-14", "15-39", "40+")},
    "EXAMPLES": sorted(unreach, key=lambda b: -b["FLOOR_NEEDS_INCIDENCE"])[:12],
    "INCIDENCE_BAR_BY_N_SITES": {n: round(5.0 / n, 3) for n in (8, 10, 12, 15, 20, 30, 41, 68, 119)}}
print("F5 unreachable:", OUT["F5_STRUCTURAL_UNREACHABILITY"]["COUNT"],
      json.dumps(OUT["F5_STRUCTURAL_UNREACHABILITY"]["BY_N_SITES_BUCKET"]))

# ── F6 WHERE IT BITES ────────────────────────────────────────────────────────────────
live_hi = [c for c in hi if c["DATE"].startswith("2026")]
OUT["F6_WHERE_IT_BITES"] = {
    "RANK_HIGHER_IN_THE_LIVE_2026_SEASON": len(live_hi),
    "OF_THOSE_WITHHELD_BY_THE_FLOOR": sum(1 for c in live_hi if c["STATE"] != HIGHER),
    "SHIPPED_HIGHER_CALLS_IN_2026": sum(1 for c in cl if c["STATE"] == HIGHER
                                        and c["DATE"].startswith("2026")),
    "SHIPPED_HIGHER_CALLS_IN_HINDCAST_ONLY": sum(1 for c in cl if c["STATE"] == HIGHER
                                                 and not c["DATE"].startswith("2026")),
    "LIVE_ROWS": [{k: c[k] for k in ("CROP", "DATE", "PROVINCE", "VALUE", "PERCENTILE",
                                     "n_sites", "n_pos", "BASELINE_N", "BASELINE_MEDIAN",
                                     "STATE", "STATE_NO_FLOOR")} for c in live_hi],
    "CHANGES_NOTHING_EXAMPLE": [{k: c[k] for k in ("CROP", "DATE", "PROVINCE", "n_sites",
                                                   "n_pos", "PERCENTILE", "STATE")}
                                for c in hi if c["STATE"] != HIGHER
                                and not c["DATE"].startswith("2026")]}
print("F6:", json.dumps({k: v for k, v in OUT["F6_WHERE_IT_BITES"].items()
                         if not isinstance(v, list)}))

# ── F7 ROUNDING ──────────────────────────────────────────────────────────────────────
edge = [{"n_sites": n, "product": round(round(5 / n, 4) * n, 6)}
        for n in range(8, 200) if round(5 / n, 4) * n < 5]
actual = [c for c in cl if c["n_pos"] == 5 and c.get("FLOOR_PRODUCT", 99) < 5]
OUT["F7_ROUNDING"] = {
    "THE_FLOOR_COMPARES": "round(INCIDENCE,4) * n_sites >= 5, not the integer positive count",
    "N_SITES_VALUES_8_TO_199_WHERE_EXACTLY_5_POSITIVE_SITES_FAILS_THE_FLOOR": [e["n_sites"] for e in edge],
    "EXAMPLES": edge[:6],
    "CELLS_IN_THIS_SAMPLE_HIT_BY_IT": len(actual),
    "CONSEQUENCE": "p5's FALSE_NEGATIVE_TEST compares against round(VALUE*n_sites,1), which "
                   "rounds 4.9995 back to 5.0 — so that test CAN fire, but only on this "
                   "floating-point edge, never on a substantive disagreement"}
print("F7:", json.dumps({k: v for k, v in OUT["F7_ROUNDING"].items() if k != "EXAMPLES"}))

json.dump(OUT, open(os.path.join(HERE, "rt_floor.json"), "w"), indent=1, default=str)
print("\nwrote rt_floor.json")
