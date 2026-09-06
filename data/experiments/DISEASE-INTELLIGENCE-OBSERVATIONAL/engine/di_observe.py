#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · LAYERS 1 AND 2

LAYER 1 — OBSERVATION. What the source recorded, with its denominator and its dates.
  The unit is a RATE WITH A REAL DENOMINATOR: infested drupes over drupes sampled, pooled
  across every usable visit in the window. The previous pilot published "share of monitored
  sites where the value is above zero", which throws the sample size away: a grove with 1
  infested olive in 100 and a grove with 60 in 100 both counted as one positive site.

LAYER 2 — ANALYSIS. Only transformations that can be defended:
  historical_state   ABOVE_HISTORICAL | TYPICAL | BELOW_HISTORICAL | INSUFFICIENT_DATA
                     the same calendar window in prior seasons, same province, pooled the
                     same way. Reported WITH the absolute numbers and WITH the source's own
                     colour band, never as a rank alone.
  observed_trend     INCREASING_OBSERVED | STABLE_OBSERVED | DECREASING_OBSERVED | UNKNOWN
                     consecutive windows ending at as_of. This is arithmetic about the past.
                     It is not a forecast and the word "will" appears nowhere.

EVERY parameter is declared here, emitted in PARAMS, and varied by the sensitivity test.
A parameter that never appears in the output is a parameter nobody can audit.
"""
import os, json, statistics, collections, datetime as dt
import di_core

# ── declared parameters. All of them. ────────────────────────────────────────────
PARAMS = {
    "WINDOW_DAYS": 28,               # four weekly scouting rounds
    "MIN_VISITS": 8,                 # below this a province-window is not summarised
    "MIN_DRUPES": 400,               # a pooled rate needs a real denominator
    "MIN_BASELINE_SEASONS": 5,       # fewer prior seasons cannot support a comparison
    "HIGH_PCTL": 0.80,
    "LOW_PCTL": 0.20,
    "TREND_MIN_WINDOWS": 3,          # consecutive windows required before naming a direction
    "TREND_MIN_ABS_CHANGE_PCT": 1.0, # percentage points; below this the change is called STABLE
    "MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE": 8,   # groves shared with a baseline season
}


def _win(as_of, days):
    return as_of - dt.timedelta(days=days - 1), as_of


def _shift(d, y):
    try:
        return d.replace(year=y)
    except ValueError:                       # 29 Feb -> 28 Feb, declared
        return d.replace(year=y, day=28)


def pooled(visits, lo, hi, province, metric, only_sites=None):
    """The observation: infested drupes over drupes sampled, pooled over the window.

    Only visits the core marked usable_for_rates take part. The ones excluded are counted
    and returned, never silently dropped."""
    num = den = 0.0
    n_visits = 0
    sites, dates, orgs, excluded = set(), [], set(), 0
    per_site = []
    for v in visits:
        if v["province"] != province:
            continue
        d = dt.date.fromisoformat(v["observation_date"])
        if not (lo <= d <= hi):
            continue
        if only_sites is not None and v["visit_key"]["id_field"] not in only_sites:
            continue
        if not v["usable_for_rates"]:
            excluded += 1
            continue
        c = v["measurements"][metric]["value"]
        t = v["measurements"]["SAMPLE_SIZE / DENOMINATOR"]["value"]
        if c is None or t is None:
            excluded += 1
            continue
        num += c
        den += t
        n_visits += 1
        sites.add(v["visit_key"]["id_field"])
        dates.append(d)
        if v["org"]:
            orgs.add(v["org"])
        per_site.append(100.0 * c / t)
    if n_visits == 0:
        return None
    return {"rate_pct": round(100.0 * num / den, 4) if den else None,
            "infested_drupes": int(num), "drupes_sampled": int(den),
            "n_visits": n_visits, "n_sites": len(sites), "n_orgs": len(orgs),
            "n_visits_excluded_by_sanity_rules": excluded,
            "first_observation": min(dates).isoformat(),
            "last_observation": max(dates).isoformat(),
            "per_visit_rate_pct_median": round(statistics.median(per_site), 4),
            "per_visit_rate_pct_max": round(max(per_site), 4),
            "sites": sites}


def cell(visits, sheet, province, metric, as_of, params=PARAMS, first_year=2006):
    """One REGION x CROP x ISSUE x DATE x PROVINCE cell, in the three layers."""
    P = params
    lo, hi = _win(as_of, P["WINDOW_DAYS"])
    cur = pooled(visits, lo, hi, province, metric)

    obs = {"metric": metric, "unit": "percent of sampled drupes",
           "window": [lo.isoformat(), hi.isoformat()]}
    if cur is None:
        obs.update({"value_pct": None, "n_visits": 0, "n_sites": 0,
                    "drupes_sampled": 0, "last_observation": None})
    else:
        obs.update({k: v for k, v in cur.items() if k != "sites"})
        obs["value_pct"] = cur["rate_pct"]
    obs["source_band"] = di_core.band_for(sheet, obs.get("value_pct"))

    # ── baseline: the same calendar window in every prior season ─────────────────
    base, overlap = [], []
    for y in range(first_year, as_of.year):
        b = pooled(visits, _shift(lo, y), _shift(hi, y), province, metric)
        if b and b["n_visits"] >= P["MIN_VISITS"] and b["drupes_sampled"] >= P["MIN_DRUPES"]:
            base.append({"season": y, "rate_pct": b["rate_pct"],
                         "n_visits": b["n_visits"], "n_sites": b["n_sites"],
                         "drupes_sampled": b["drupes_sampled"]})
            if cur:
                overlap.append(len(cur["sites"] & b["sites"]))

    ana = {"baseline_seasons": [b["season"] for b in base],
           "baseline_n": len(base),
           "baseline_rate_pct_median": round(statistics.median(
               [b["rate_pct"] for b in base]), 4) if base else None,
           "baseline_rate_pct_min": min([b["rate_pct"] for b in base]) if base else None,
           "baseline_rate_pct_max": max([b["rate_pct"] for b in base]) if base else None,
           "baseline_detail": base}

    enough = (cur is not None and cur["n_visits"] >= P["MIN_VISITS"]
              and cur["drupes_sampled"] >= P["MIN_DRUPES"])
    if not enough:
        ana["historical_state"] = "INSUFFICIENT_DATA"
        ana["historical_reason"] = (
            "no visits in the window" if cur is None else
            f"{cur['n_visits']} visits / {cur['drupes_sampled']} drupes, below the declared "
            f"minimum of {P['MIN_VISITS']} / {P['MIN_DRUPES']}")
    elif len(base) < P["MIN_BASELINE_SEASONS"]:
        ana["historical_state"] = "INSUFFICIENT_DATA"
        ana["historical_reason"] = (f"{len(base)} usable prior seasons, below the declared "
                                    f"minimum of {P['MIN_BASELINE_SEASONS']}")
    else:
        v = cur["rate_pct"]
        rates = [b["rate_pct"] for b in base]
        below = sum(1 for r in rates if r < v) + 0.5 * sum(1 for r in rates if r == v)
        p = below / len(rates)
        ana["percentile_against_own_history"] = round(p, 4)
        ana["historical_state"] = ("ABOVE_HISTORICAL" if p >= P["HIGH_PCTL"]
                                   else "BELOW_HISTORICAL" if p <= P["LOW_PCTL"]
                                   else "TYPICAL")
        ana["historical_reason"] = (
            f"{v}% of sampled drupes now, against a median of "
            f"{ana['baseline_rate_pct_median']}% over {len(base)} prior seasons "
            f"(range {ana['baseline_rate_pct_min']}-{ana['baseline_rate_pct_max']}%)")

    # ── like-for-like: the MATCHED-PANEL comparison ──────────────────────────────
    #
    # The baseline above is the same CALENDAR WINDOW, not the same panel, and the monitored
    # network rotates hard: in some provinces this season shares a median of ZERO groves with
    # a typical prior season. Comparing this year's groves against a different set of groves
    # and calling the difference a change in pressure is a mistake, not a nuance.
    #
    # So the headline comparison is MATCHED: for each prior season, restrict BOTH sides to the
    # groves present in both, and compare only those. A season that does not share at least
    # MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE groves does not take part at all.
    enough_overlap = sum(1 for o in overlap
                         if o >= P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"])
    ana["panel_overlap_with_baseline_seasons"] = {
        "median_groves_shared": statistics.median(overlap) if overlap else None,
        "min": min(overlap) if overlap else None, "max": max(overlap) if overlap else None,
        "seasons_sharing_at_least_the_declared_minimum": enough_overlap,
        "of_seasons": len(overlap),
        "NOTE": "the unmatched baseline is the same calendar window, not the same groves"}

    matched = []
    if cur:
        for y in range(first_year, as_of.year):
            b_all = pooled(visits, _shift(lo, y), _shift(hi, y), province, metric)
            if not b_all:
                continue
            shared = cur["sites"] & b_all["sites"]
            if len(shared) < P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]:
                continue
            now = pooled(visits, lo, hi, province, metric, only_sites=shared)
            then = pooled(visits, _shift(lo, y), _shift(hi, y), province, metric,
                          only_sites=shared)
            if not now or not then or not then["drupes_sampled"] or not now["drupes_sampled"]:
                continue
            matched.append({"season": y, "n_groves_shared": len(shared),
                            "rate_now_on_those_groves_pct": now["rate_pct"],
                            "rate_then_on_those_groves_pct": then["rate_pct"],
                            "drupes_now": now["drupes_sampled"],
                            "drupes_then": then["drupes_sampled"]})
    ana["matched_panel_comparisons"] = matched
    ana["matched_panel_seasons"] = len(matched)

    if len(matched) < P["MIN_BASELINE_SEASONS"]:
        ana["historical_state_matched"] = "INSUFFICIENT_DATA"
        ana["historical_matched_reason"] = (
            f"{len(matched)} prior seasons share at least "
            f"{P['MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE']} groves with this window, below the "
            f"declared minimum of {P['MIN_BASELINE_SEASONS']}. A comparison against a "
            f"different set of groves is not a comparison, so none is published.")
    else:
        higher = sum(1 for m in matched
                     if m["rate_now_on_those_groves_pct"] > m["rate_then_on_those_groves_pct"])
        lower = sum(1 for m in matched
                    if m["rate_now_on_those_groves_pct"] < m["rate_then_on_those_groves_pct"])
        share_lower = lower / len(matched)
        ana["matched_seasons_now_is_higher_than_then"] = higher
        ana["matched_seasons_now_is_lower_than_then"] = lower
        ana["historical_state_matched"] = (
            "BELOW_HISTORICAL" if share_lower >= P["HIGH_PCTL"] else
            "ABOVE_HISTORICAL" if (higher / len(matched)) >= P["HIGH_PCTL"] else "TYPICAL")
        ana["historical_matched_reason"] = (
            f"on the groves shared with each prior season, this window reads lower than "
            f"{lower} of {len(matched)} of them and higher than {higher}")

    # the published historical statement is the MATCHED one
    ana["historical_state_unmatched"] = ana.get("historical_state")
    ana["historical_state"] = ana["historical_state_matched"]
    ana["historical_reason"] = ana["historical_matched_reason"]

    # ── observed trend: consecutive windows ending at as_of ──────────────────────
    pts = []
    for i in range(P["TREND_MIN_WINDOWS"] + 1):
        h = as_of - dt.timedelta(days=P["WINDOW_DAYS"] * i)
        l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
        w = pooled(visits, l, h, province, metric)
        if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
            pts.append({"window_end": h.isoformat(), "rate_pct": w["rate_pct"],
                        "n_visits": w["n_visits"], "drupes_sampled": w["drupes_sampled"]})
    pts.reverse()
    if len(pts) < P["TREND_MIN_WINDOWS"]:
        trend, treason = "UNKNOWN", (f"{len(pts)} usable consecutive windows, below the "
                                     f"declared minimum of {P['TREND_MIN_WINDOWS']}")
    else:
        seq = [p["rate_pct"] for p in pts]
        delta = seq[-1] - seq[0]
        if abs(delta) < P["TREND_MIN_ABS_CHANGE_PCT"]:
            trend = "STABLE_OBSERVED"
        elif all(b >= a for a, b in zip(seq, seq[1:])):
            trend = "INCREASING_OBSERVED"
        elif all(b <= a for a, b in zip(seq, seq[1:])):
            trend = "DECREASING_OBSERVED"
        else:
            trend = "STABLE_OBSERVED"
        treason = (f"{' -> '.join(f'{s}%' for s in seq)} over "
                   f"{len(seq)} consecutive {P['WINDOW_DAYS']}-day windows ending "
                   f"{as_of.isoformat()}; change {round(delta, 4)} percentage points. "
                   f"This describes windows that have already happened.")
    ana["observed_trend"] = trend
    ana["observed_trend_reason"] = treason
    ana["observed_trend_points"] = pts

    qual = {"semantic_validity": "PROVED_BY_SOURCE_METADATA",
            "denominator_validity": ("PRESENT" if obs.get("drupes_sampled") else "ABSENT"),
            "temporal_validity": "NO_OBSERVATION_AFTER_AS_OF",
            "n_visits_excluded_by_sanity_rules":
                obs.get("n_visits_excluded_by_sanity_rules", 0)}
    qual["historical_comparison_is_matched_panel"] = True
    qual["matched_panel_seasons"] = ana["matched_panel_seasons"]
    # The OBSERVATION is publishable on its own terms: it is what the source recorded.
    # The HISTORICAL COMPARISON is a separate claim with a separate gate.
    qual["observation_publishable"] = bool(enough)
    qual["historical_comparison_publishable"] = bool(
        enough and ana["historical_state"] in ("ABOVE_HISTORICAL", "TYPICAL",
                                               "BELOW_HISTORICAL"))
    qual["publishable"] = qual["observation_publishable"]
    qual["publishable_reason"] = (
        "enough visits and enough sampled drupes for the observation"
        if qual["observation_publishable"] else ana.get("historical_reason"))

    return {"country": "Italy", "region": "Toscana", "province": province,
            "as_of": as_of.isoformat(),
            "crop": {"canonical_id": "CROP_OLIVE", "source_label": "Olivo",
                     "evidence": "source crop id 2"},
            "problem": {"type": "PEST", "canonical_id": "PEST_BACTROCERA_OLEAE",
                        "source_label": "Infestazione mosca dell'olivo",
                        "evidence": "source survey_schema id 1"},
            "observation": obs, "analysis": ana, "quality": qual,
            "params": dict(PARAMS)}
