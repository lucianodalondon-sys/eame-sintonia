#!/usr/bin/env python3
"""
RT2 / A3 — THE TREND: "consecutive windows that have already ended".

Four separate accusations, each measured:

  T1  the loop builds 4 candidate windows and KEEPS only those that pass the gate. A window
      that fails is SKIPPED, not treated as a break in the chain. So `pts` can contain
      windows with a 28-day HOLE between them, and the emitted sentence still says
      "over N consecutive 28-day windows".

  T2  can a direction be named from 2 points when the minimum is 3?

  T3  TREND_MIN_ABS_CHANGE_PCT = 1.0 percentage points. Siena reads 0.0 -> 0.2718 -> 0.6909
      and is called STABLE_OBSERVED. Both sides, with denominators.

  T4  the newest window ends at as_of but the data does not: the trailing days of the
      current window are still being collected. Measure the gap and the size of the effect.
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
out = {}

sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, dt.date(2026, 9, 6))
VIS = loaded["visits"]
PROVS = sorted({v["province"] for v in VIS if v["province"]})


def windows(as_of):
    """Exactly what cell() builds, plus which candidates were dropped."""
    rows = []
    for i in range(P["TREND_MIN_WINDOWS"] + 1):
        h = as_of - dt.timedelta(days=P["WINDOW_DAYS"] * i)
        l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
        rows.append((i, l, h))
    return rows


# ── T1: hunt for a hole ─────────────────────────────────────────────────────
holes = []
scanned = 0
for prov in PROVS:
    for day in range(0, 180):
        as_of = dt.date(2026, 9, 6) - dt.timedelta(days=day)
        kept = []
        for i, l, h in windows(as_of):
            w = di_observe.pooled(VIS, l, h, prov, METRIC)
            ok = bool(w and w["n_visits"] >= P["MIN_VISITS"]
                      and w["drupes_sampled"] >= P["MIN_DRUPES"])
            kept.append((i, ok, None if not w else w["rate_pct"]))
        scanned += 1
        idx = [i for i, ok, _ in kept if ok]
        if len(idx) >= P["TREND_MIN_WINDOWS"] and (max(idx) - min(idx) + 1) != len(idx):
            c = di_observe.cell(VIS, sheet, prov, METRIC, as_of)
            holes.append({"province": prov, "as_of": as_of.isoformat(),
                          "candidate_windows_i_kept": idx,
                          "gap_in_days_between_the_two_oldest_kept_windows":
                              (sorted(idx)[-1] - sorted(idx)[-2]) * P["WINDOW_DAYS"],
                          "published_trend": c["analysis"]["observed_trend"],
                          "published_sentence": c["analysis"]["observed_trend_reason"],
                          "window_ends": [p["window_end"]
                                          for p in c["analysis"]["observed_trend_points"]]})
out["T1_NON_CONSECUTIVE_WINDOWS_CALLED_CONSECUTIVE"] = {
    "province_x_as_of_combinations_scanned": scanned,
    "combinations_where_the_kept_windows_have_a_hole": len(holes),
    "examples": holes[:8]}

# T1b: is it even checkable from the output? do the emitted points prove consecutiveness?
sample = di_observe.cell(VIS, sheet, "Firenze", METRIC, dt.date(2026, 9, 6))
ends = [p["window_end"] for p in sample["analysis"]["observed_trend_points"]]
gaps = [(dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days
        for a, b in zip(ends, ends[1:])]
out["T1b_THE_OUTPUT_DOES_CARRY_WINDOW_ENDS"] = {
    "firenze_2026_09_06_window_ends": ends, "gaps_days": gaps,
    "a_reader_can_check_consecutiveness": all(g == P["WINDOW_DAYS"] for g in gaps),
    "NOTE": "observed_trend_points carries window_end, so the claim is auditable by a reader "
            "who checks the gaps. The engine itself never checks them."}

# ── T2: two points ──────────────────────────────────────────────────────────
two = {}
for prov in PROVS:
    for day in range(0, 200):
        as_of = dt.date(2026, 9, 6) - dt.timedelta(days=day)
        c = di_observe.cell(VIS, sheet, prov, METRIC, as_of)
        n = len(c["analysis"]["observed_trend_points"])
        t = c["analysis"]["observed_trend"]
        two.setdefault(n, collections.Counter())[t] += 1
out["T2_DIRECTION_FROM_FEWER_THAN_THREE_POINTS"] = {
    "trend_by_number_of_points": {k: dict(v) for k, v in sorted(two.items())},
    "any_direction_named_on_fewer_than_3_points": any(
        t != "UNKNOWN" for n, v in two.items() if n < P["TREND_MIN_WINDOWS"] for t in v)}

# T2b: the loop range is TREND_MIN_WINDOWS+1, so lowering the parameter lowers BOTH the
# candidate count and the minimum. Does a 2-window parameter emit a direction?
P2 = dict(P); P2["TREND_MIN_WINDOWS"] = 2
c2 = di_observe.cell(VIS, sheet, "Siena", METRIC, dt.date(2026, 9, 6), params=P2)
out["T2b_PARAMETER_LOWERED_TO_2"] = {
    "trend": c2["analysis"]["observed_trend"],
    "n_points": len(c2["analysis"]["observed_trend_points"]),
    "sentence": c2["analysis"]["observed_trend_reason"]}

# ── T3: the 1.0 pp rule ─────────────────────────────────────────────────────
t3 = {}
for prov in PROVS:
    c = di_observe.cell(VIS, sheet, prov, METRIC, dt.date(2026, 9, 6))
    pts = c["analysis"]["observed_trend_points"]
    if len(pts) < P["TREND_MIN_WINDOWS"]:
        continue
    seq = [p["rate_pct"] for p in pts]
    delta = seq[-1] - seq[0]
    mono_up = all(b >= a for a, b in zip(seq, seq[1:]))
    # infested drupes implied by rate x denominator, for a Poisson-ish sanity check
    counts = [(round(p["rate_pct"] * p["drupes_sampled"] / 100.0), p["drupes_sampled"])
              for p in pts]
    n1, d1 = counts[0]
    n2, d2 = counts[-1]
    # two-proportion z on the pooled counts, first window vs last
    p1, p2 = (n1 / d1 if d1 else 0), (n2 / d2 if d2 else 0)
    pp = (n1 + n2) / (d1 + d2) if (d1 + d2) else 0
    se = math.sqrt(pp * (1 - pp) * (1 / d1 + 1 / d2)) if pp and d1 and d2 else 0
    z = (p2 - p1) / se if se else None
    t3[prov] = {"sequence_pct": seq, "delta_pp": round(delta, 4),
                "monotone_non_decreasing": mono_up,
                "published_trend": c["analysis"]["observed_trend"],
                "infested_over_sampled_first": [n1, d1],
                "infested_over_sampled_last": [n2, d2],
                "relative_change": ("from zero" if p1 == 0 else round(p2 / p1, 2)),
                "z_first_vs_last": None if z is None else round(z, 2),
                "band_now": c["observation"]["source_band"],
                "pp_to_the_next_source_band": round(6.0 - seq[-1], 4)}
out["T3_THE_1_POINT_0_PP_RULE"] = t3

# T3b: how big can a hidden rise be? the largest delta still called STABLE, and the
# smallest delta that would change the label
scan = []
for prov in PROVS:
    for day in range(0, 200):
        as_of = dt.date(2026, 9, 6) - dt.timedelta(days=day)
        c = di_observe.cell(VIS, sheet, prov, METRIC, as_of)
        pts = c["analysis"]["observed_trend_points"]
        if len(pts) < P["TREND_MIN_WINDOWS"]:
            continue
        seq = [p["rate_pct"] for p in pts]
        d = seq[-1] - seq[0]
        mono = all(b >= a for a, b in zip(seq, seq[1:]))
        scan.append({"province": prov, "as_of": as_of.isoformat(), "delta_pp": round(d, 4),
                     "monotone_up": mono, "trend": c["analysis"]["observed_trend"],
                     "seq": seq})
hidden = [s for s in scan if s["trend"] == "STABLE_OBSERVED" and s["monotone_up"]
          and s["delta_pp"] > 0]
hidden.sort(key=lambda s: -s["delta_pp"])
out["T3b_LARGEST_MONOTONE_RISE_CALLED_STABLE"] = {
    "cells_scanned": len(scan),
    "cells_that_are_monotone_up_but_labelled_STABLE": len(hidden),
    "worst_five": hidden[:5],
    "the_rule": f"|delta| < {P['TREND_MIN_ABS_CHANGE_PCT']} pp -> STABLE_OBSERVED"}

# ── T4: the trailing window is still filling ────────────────────────────────
t4 = {}
for prov in PROVS:
    as_of = dt.date(2026, 9, 6)
    rows = []
    for i, l, h in windows(as_of):
        w = di_observe.pooled(VIS, l, h, prov, METRIC)
        if not w:
            rows.append({"i": i, "window": [l.isoformat(), h.isoformat()], "empty": True})
            continue
        rows.append({"i": i, "window": [l.isoformat(), h.isoformat()],
                     "first_observation": w["first_observation"],
                     "last_observation": w["last_observation"],
                     "days_of_the_window_with_no_data_at_the_end":
                         (h - dt.date.fromisoformat(w["last_observation"])).days,
                     "n_visits": w["n_visits"], "rate_pct": w["rate_pct"]})
    t4[prov] = rows
out["T4_TRAILING_WINDOW_IS_STILL_FILLING"] = t4

# T4b: what does the SAME window read when the last 4 days are removed? that is what an
# as_of set 4 days later would have added. Measure it on windows that ARE complete.
t4b = []
for prov in PROVS:
    for end_iso in ("2026-08-09", "2026-07-12", "2026-06-14"):
        h = dt.date.fromisoformat(end_iso)
        l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
        full = di_observe.pooled(VIS, l, h, prov, METRIC)
        trunc = di_observe.pooled(VIS, l, h - dt.timedelta(days=4), prov, METRIC)
        if full and trunc:
            t4b.append({"province": prov, "window_end": end_iso,
                        "rate_full_28d_pct": full["rate_pct"],
                        "rate_if_last_4_days_missing_pct": trunc["rate_pct"],
                        "difference_pp": round(full["rate_pct"] - trunc["rate_pct"], 4),
                        "drupes_full": full["drupes_sampled"],
                        "drupes_truncated": trunc["drupes_sampled"]})
diffs = [x["difference_pp"] for x in t4b]
out["T4b_WHAT_THE_MISSING_TAIL_IS_WORTH"] = {
    "windows_measured": len(t4b),
    "median_difference_pp": round(sorted(diffs)[len(diffs) // 2], 4) if diffs else None,
    "max_difference_pp": max(diffs) if diffs else None,
    "min_difference_pp": min(diffs) if diffs else None,
    "windows_where_the_full_window_reads_HIGHER": sum(1 for d in diffs if d > 0),
    "of": len(diffs),
    "detail": t4b}

json.dump(out, open(os.path.join(HERE, "rt2_trend.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps({k: v for k, v in out.items()
                  if k not in ("T4_TRAILING_WINDOW_IS_STILL_FILLING",)},
                 indent=1, default=str)[:9000])
