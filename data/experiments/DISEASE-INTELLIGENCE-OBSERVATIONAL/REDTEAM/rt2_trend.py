#!/usr/bin/env python3
"""
RT2 / A3 — THE TREND: "consecutive windows that have already ended".

Four accusations, each measured. Everything that produces a NUMBER goes through the real
di_observe.pooled() and, for every hit, through the real di_observe.cell(). The scans
pre-split the visit list by province first; pooled() filters by province itself, so the
result is identical and the scan is ~10x cheaper.

  T1  the loop builds 4 candidate windows and KEEPS only those that pass the gate. A window
      that fails is SKIPPED, not treated as a break. So `pts` can contain windows with a
      28-day HOLE, while the sentence says "over N consecutive 28-day windows".
  T2  can a direction be named from fewer than 3 points?
  T3  TREND_MIN_ABS_CHANGE_PCT = 1.0 pp. Siena 0.0 -> 0.2718 -> 0.6909 -> STABLE_OBSERVED.
  T4  the newest window ends at as_of but the data does not.
"""
import os, sys, json, datetime as dt, collections, math

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe

CASE = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
METRIC = "ACTIVE_INFESTATION_COUNT"
P = di_observe.PARAMS
AS_OF = dt.date(2026, 9, 6)
out = {}

sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
VIS = loaded["visits"]
PROVS = sorted({v["province"] for v in VIS if v["province"]})
BYPROV = {p: [v for v in VIS if v["province"] == p] for p in PROVS}


def cand(as_of):
    for i in range(P["TREND_MIN_WINDOWS"] + 1):
        h = as_of - dt.timedelta(days=P["WINDOW_DAYS"] * i)
        yield i, h - dt.timedelta(days=P["WINDOW_DAYS"] - 1), h


def kept_windows(prov, as_of):
    """Exactly the filter cell() applies, on the real pooled()."""
    keep = []
    for i, l, h in cand(as_of):
        w = di_observe.pooled(BYPROV[prov], l, h, prov, METRIC)
        if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
            keep.append({"i": i, "end": h.isoformat(), "rate_pct": w["rate_pct"],
                         "n_visits": w["n_visits"], "drupes": w["drupes_sampled"]})
    keep.reverse()
    return keep


def label(seq):
    delta = seq[-1] - seq[0]
    if abs(delta) < P["TREND_MIN_ABS_CHANGE_PCT"]:
        return "STABLE_OBSERVED", delta
    if all(b >= a for a, b in zip(seq, seq[1:])):
        return "INCREASING_OBSERVED", delta
    if all(b <= a for a, b in zip(seq, seq[1:])):
        return "DECREASING_OBSERVED", delta
    return "STABLE_OBSERVED", delta


# ── the scan ────────────────────────────────────────────────────────────────
DAYS = 220
holes, twopoint, scan = [], collections.Counter(), []
for prov in PROVS:
    for day in range(DAYS):
        as_of = AS_OF - dt.timedelta(days=day)
        keep = kept_windows(prov, as_of)
        idx = sorted(k["i"] for k in keep)
        twopoint[(len(keep), label([k["rate_pct"] for k in keep])[0]
                  if len(keep) >= P["TREND_MIN_WINDOWS"] else "UNKNOWN")] += 1
        if len(keep) >= P["TREND_MIN_WINDOWS"] and (max(idx) - min(idx) + 1) != len(idx):
            holes.append({"province": prov, "as_of": as_of.isoformat(),
                          "candidate_index_kept": idx,
                          "window_ends_kept": [k["end"] for k in keep]})
        if len(keep) >= P["TREND_MIN_WINDOWS"]:
            seq = [k["rate_pct"] for k in keep]
            lab, delta = label(seq)
            scan.append({"province": prov, "as_of": as_of.isoformat(), "seq": seq,
                         "delta_pp": round(delta, 4), "trend": lab,
                         "monotone_up": all(b >= a for a, b in zip(seq, seq[1:])),
                         "ends": [k["end"] for k in keep],
                         "drupes": [k["drupes"] for k in keep]})

# T1 — confirm every hole through the REAL cell()
confirmed = []
for h in holes[:6]:
    c = di_observe.cell(VIS, sheet, h["province"], METRIC, dt.date.fromisoformat(h["as_of"]))
    ends = [p["window_end"] for p in c["analysis"]["observed_trend_points"]]
    gaps = [(dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days
            for a, b in zip(ends, ends[1:])]
    confirmed.append({**h, "REAL_CELL_trend": c["analysis"]["observed_trend"],
                      "REAL_CELL_sentence": c["analysis"]["observed_trend_reason"],
                      "REAL_CELL_window_ends": ends, "gaps_between_window_ends_days": gaps,
                      "the_sentence_says_consecutive": "consecutive"
                                                       in c["analysis"]["observed_trend_reason"],
                      "the_windows_ARE_consecutive": all(g == P["WINDOW_DAYS"] for g in gaps)})
out["T1_NON_CONSECUTIVE_WINDOWS_CALLED_CONSECUTIVE"] = {
    "province_x_as_of_scanned": len(PROVS) * DAYS,
    "combinations_whose_kept_windows_have_a_hole": len(holes),
    "confirmed_through_the_real_cell": confirmed}

# T2
out["T2_DIRECTION_FROM_FEWER_THAN_THREE_POINTS"] = {
    "count_by_(n_points,label)": {f"{k[0]}pts/{k[1]}": v
                                  for k, v in sorted(twopoint.items())},
    "any_direction_named_on_fewer_than_3_points": any(
        k[1] != "UNKNOWN" for k in twopoint if k[0] < P["TREND_MIN_WINDOWS"])}
P2 = dict(P); P2["TREND_MIN_WINDOWS"] = 2
c2 = di_observe.cell(VIS, sheet, "Siena", METRIC, AS_OF, params=P2)
out["T2b_THE_PARAMETER_IS_BOTH_THE_MINIMUM_AND_THE_LOOP_BOUND"] = {
    "with_TREND_MIN_WINDOWS=2": {
        "trend": c2["analysis"]["observed_trend"],
        "n_points": len(c2["analysis"]["observed_trend_points"]),
        "sentence": c2["analysis"]["observed_trend_reason"]},
    "NOTE": "range(TREND_MIN_WINDOWS+1) means the parameter sets BOTH how many windows are "
            "built and how many are required, so it can never build fewer than the minimum. "
            "That is what makes a 2-point direction impossible with the shipped code."}

# T3 — Siena and every other publishable province, with denominators
t3 = {}
for prov in PROVS:
    c = di_observe.cell(VIS, sheet, prov, METRIC, AS_OF)
    pts = c["analysis"]["observed_trend_points"]
    if len(pts) < P["TREND_MIN_WINDOWS"]:
        continue
    seq = [p["rate_pct"] for p in pts]
    counts = [(round(p["rate_pct"] * p["drupes_sampled"] / 100.0), p["drupes_sampled"])
              for p in pts]
    n1, d1 = counts[0]
    n2, d2 = counts[-1]
    p1, p2 = (n1 / d1 if d1 else 0), (n2 / d2 if d2 else 0)
    pp = (n1 + n2) / (d1 + d2) if (d1 + d2) else 0
    se = math.sqrt(pp * (1 - pp) * (1 / d1 + 1 / d2)) if pp and d1 and d2 else 0
    t3[prov] = {"sequence_pct": seq, "delta_pp": round(seq[-1] - seq[0], 4),
                "monotone_non_decreasing": all(b >= a for a, b in zip(seq, seq[1:])),
                "published_trend": c["analysis"]["observed_trend"],
                "infested_over_sampled_by_window": counts,
                "relative_change_last_over_first": ("from zero" if p1 == 0
                                                    else round(p2 / p1, 2)),
                "z_first_vs_last": None if not se else round((p2 - p1) / se, 2),
                "pp_from_the_last_reading_to_the_source_yellow_band_at_6pct":
                    round(6.0 - seq[-1], 4)}
out["T3_THE_1_POINT_0_PP_RULE_ON_2026_09_06"] = t3

hidden = sorted([s for s in scan if s["trend"] == "STABLE_OBSERVED" and s["monotone_up"]
                 and s["delta_pp"] > 0], key=lambda s: -s["delta_pp"])
out["T3b_MONOTONE_RISES_LABELLED_STABLE"] = {
    "cells_with_a_publishable_trend_in_the_scan": len(scan),
    "of_those_monotone_up_but_labelled_STABLE": len(hidden),
    "largest_such_rise_pp": hidden[0]["delta_pp"] if hidden else None,
    "worst_five": hidden[:5],
    "how_many_of_those_would_have_crossed_the_sources_own_6pct_band":
        sum(1 for s in hidden if s["seq"][-1] >= 6.0)}

# T4 — the trailing window is still filling
t4 = {}
for prov in PROVS:
    rows = []
    for i, l, h in cand(AS_OF):
        w = di_observe.pooled(BYPROV[prov], l, h, prov, METRIC)
        if not w:
            rows.append({"i": i, "window": [l.isoformat(), h.isoformat()], "empty": True})
            continue
        rows.append({"i": i, "window": [l.isoformat(), h.isoformat()],
                     "last_observation": w["last_observation"],
                     "trailing_days_of_the_window_with_no_data":
                         (h - dt.date.fromisoformat(w["last_observation"])).days,
                     "n_visits": w["n_visits"], "rate_pct": w["rate_pct"]})
    t4[prov] = rows
out["T4_TRAILING_WINDOW_IS_STILL_FILLING"] = t4
gaps_now = [r["trailing_days_of_the_window_with_no_data"] for p in t4 for r in t4[p]
            if not r.get("empty")]
out["T4_SUMMARY"] = {
    "windows_measured": len(gaps_now),
    "trailing_dead_days_min": min(gaps_now), "max": max(gaps_now),
    "newest_window_dead_days_by_province":
        {p: t4[p][0].get("trailing_days_of_the_window_with_no_data") for p in t4}}

t4b = []
for prov in PROVS:
    for end_iso in ("2026-08-09", "2026-07-12", "2026-06-14"):
        h = dt.date.fromisoformat(end_iso)
        l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
        full = di_observe.pooled(BYPROV[prov], l, h, prov, METRIC)
        trunc = di_observe.pooled(BYPROV[prov], l, h - dt.timedelta(days=4), prov, METRIC)
        if full and trunc and full["rate_pct"] is not None and trunc["rate_pct"] is not None:
            t4b.append({"province": prov, "window_end": end_iso,
                        "rate_full_28d_pct": full["rate_pct"],
                        "rate_if_last_4_days_were_not_yet_collected_pct": trunc["rate_pct"],
                        "difference_pp": round(full["rate_pct"] - trunc["rate_pct"], 4),
                        "drupes_full": full["drupes_sampled"],
                        "drupes_truncated": trunc["drupes_sampled"]})
diffs = sorted(x["difference_pp"] for x in t4b)
out["T4b_WHAT_THE_MISSING_TAIL_IS_WORTH"] = {
    "complete_windows_measured": len(t4b),
    "median_difference_pp": diffs[len(diffs) // 2] if diffs else None,
    "max_difference_pp": max(diffs) if diffs else None,
    "min_difference_pp": min(diffs) if diffs else None,
    "windows_where_the_full_window_reads_HIGHER_than_the_truncated_one":
        sum(1 for d in diffs if d > 0), "of": len(diffs),
    "detail": t4b}

json.dump(out, open(os.path.join(HERE, "rt2_trend.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps({k: v for k, v in out.items()
                  if k not in ("T4_TRAILING_WINDOW_IS_STILL_FILLING", "T4b_WHAT_THE_MISSING_TAIL_IS_WORTH")},
                 indent=1, default=str)[:12000])
print("\nT4_SUMMARY", json.dumps(out["T4_SUMMARY"], indent=1))
print("\nT4b", json.dumps({k: v for k, v in out["T4b_WHAT_THE_MISSING_TAIL_IS_WORTH"].items()
                           if k != "detail"}, indent=1))
