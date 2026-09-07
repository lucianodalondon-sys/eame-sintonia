#!/usr/bin/env python3
"""RT5 · STATISTICS · shared fast harness.

The engine's di_observe.pooled() rescans all 79,251 visits on every call, and
di_observe.cell() calls it ~90 times, so one province-cell costs ~1.5 s. A
parameter sweep of a few thousand configurations is not affordable at that
price. This module rebuilds the SAME arithmetic on a per-province, date-sorted
index, and rt5_00_verify.py proves the fast path reproduces the engine
bit-for-bit on the published configuration before any sweep is trusted.

Nothing in engine/ is modified. This file only reads.
"""
import os, sys, json, pickle, bisect, statistics, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
CASE = os.path.abspath(os.path.join(HERE, "..", "..",
                                    "DISEASE-INTELLIGENCE-ITALY", "CASES",
                                    "OLIVO-BACTROCERA-TOSCANA"))
CACHE = os.path.join(HERE, "_cache_visits.pkl")
sys.path.insert(0, ENGINE)

PARAMS = {
    "WINDOW_DAYS": 28,
    "MIN_VISITS": 8,
    "MIN_DRUPES": 400,
    "MIN_BASELINE_SEASONS": 5,
    "HIGH_PCTL": 0.80,
    "LOW_PCTL": 0.20,
    "TREND_MIN_WINDOWS": 3,
    "TREND_MIN_ABS_CHANGE_PCT": 1.0,
    "MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE": 8,
}

METRICS = ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
           "TOTAL_INFESTATION_COUNT")
DENOM = "SAMPLE_SIZE / DENOMINATOR"


# ── load once, cache ─────────────────────────────────────────────────────────
def load_raw(as_of=dt.date(2026, 9, 6), force=False):
    """Every visit dated on or before 2026-09-06, exactly as di_core returns it.

    We always load at the LATEST as_of and filter by date afterwards; di_core's
    only use of as_of is `if d > as_of: drop`, so filtering later is identical."""
    if not force and os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    import di_core
    sheet = di_core.load_sheet()
    loaded = di_core.load_visits(CASE, sheet, as_of)
    slim = []
    for v in loaded["visits"]:
        rec = {
            "id_field": v["visit_key"]["id_field"],
            "date": dt.date.fromisoformat(v["observation_date"]),
            "province": v["province"],
            "comune": v["comune"],
            "org": v["org"],
            "usable": v["usable_for_rates"],
            "den": v["measurements"][DENOM]["value"],
        }
        for m in METRICS:
            rec[m] = v["measurements"][m]["value"]
        slim.append(rec)
    bands = sheet["SOURCE_ACTION_BANDS"]
    out = {"visits": slim, "bands": bands,
           "n_visits": loaded["n_visits"],
           "n_usable": loaded["n_visits_usable_for_rates"]}
    with open(CACHE, "wb") as f:
        pickle.dump(out, f)
    return out


class Index:
    """Per-province, date-sorted arrays. One scan builds it; queries are slices."""

    def __init__(self, visits, metric):
        self.metric = metric
        self.by_prov = {}
        for v in visits:
            p = v["province"]
            if not p:
                continue
            self.by_prov.setdefault(p, []).append(v)
        for p in self.by_prov:
            self.by_prov[p].sort(key=lambda r: r["date"].toordinal())
        self.provinces = sorted(self.by_prov)
        self.dates = {p: [r["date"].toordinal() for r in self.by_prov[p]]
                      for p in self.provinces}

    def slice(self, province, lo, hi):
        rows = self.by_prov.get(province)
        if not rows:
            return []
        ds = self.dates[province]
        a = bisect.bisect_left(ds, lo.toordinal())
        b = bisect.bisect_right(ds, hi.toordinal())
        return rows[a:b]

    def pooled(self, province, lo, hi, only_sites=None, as_of=None):
        """Byte-identical to di_observe.pooled for the fields we use."""
        m = self.metric
        num = den = 0.0
        n_visits = 0
        sites = set()
        per_visit = []
        per_site_num = {}
        per_site_den = {}
        dates = []
        excluded = 0
        for v in self.slice(province, lo, hi):
            if as_of is not None and v["date"] > as_of:
                continue
            if only_sites is not None and v["id_field"] not in only_sites:
                continue
            if not v["usable"]:
                excluded += 1
                continue
            c = v[m]
            t = v["den"]
            if c is None or t is None:
                excluded += 1
                continue
            num += c
            den += t
            n_visits += 1
            sites.add(v["id_field"])
            dates.append(v["date"])
            per_visit.append(100.0 * c / t)
            k = v["id_field"]
            per_site_num[k] = per_site_num.get(k, 0.0) + c
            per_site_den[k] = per_site_den.get(k, 0.0) + t
        if n_visits == 0:
            return None
        return {"rate_pct": round(100.0 * num / den, 4) if den else None,
                "infested_drupes": int(num), "drupes_sampled": int(den),
                "n_visits": n_visits, "n_sites": len(sites),
                "n_visits_excluded_by_sanity_rules": excluded,
                "first_observation": min(dates).isoformat(),
                "last_observation": max(dates).isoformat(),
                "per_visit": per_visit,
                "per_site_num": per_site_num, "per_site_den": per_site_den,
                "sites": sites}


def win(as_of, days):
    return as_of - dt.timedelta(days=days - 1), as_of


def shift(d, y):
    try:
        return d.replace(year=y)
    except ValueError:
        return d.replace(year=y, day=28)


# ── pooling estimators ───────────────────────────────────────────────────────
def estimate(p, how="pooled"):
    """Alternative point estimates on the same set of visits."""
    if p is None:
        return None
    if how == "pooled":
        return p["rate_pct"]
    if how == "mean_visit":
        return round(statistics.fmean(p["per_visit"]), 4)
    if how == "median_visit":
        return round(statistics.median(p["per_visit"]), 4)
    if how == "mean_grove":
        gm = [100.0 * p["per_site_num"][k] / p["per_site_den"][k]
              for k in p["per_site_num"] if p["per_site_den"][k]]
        return round(statistics.fmean(gm), 4) if gm else None
    if how == "median_grove":
        gm = [100.0 * p["per_site_num"][k] / p["per_site_den"][k]
              for k in p["per_site_num"] if p["per_site_den"][k]]
        return round(statistics.median(gm), 4) if gm else None
    raise ValueError(how)


# ── the engine's cell(), reimplemented on the index ──────────────────────────
def cell(idx, province, as_of, P=None, first_year=2006, how="pooled",
         want_matched_detail=False):
    P = dict(PARAMS if P is None else P)
    lo, hi = win(as_of, P["WINDOW_DAYS"])
    cur = idx.pooled(province, lo, hi, as_of=as_of)

    out = {"province": province, "as_of": as_of.isoformat(),
           "value_pct": None if cur is None else estimate(cur, how),
           "n_visits": 0 if cur is None else cur["n_visits"],
           "n_sites": 0 if cur is None else cur["n_sites"],
           "drupes_sampled": 0 if cur is None else cur["drupes_sampled"]}

    base, overlap = [], []
    for y in range(first_year, as_of.year):
        b = idx.pooled(province, shift(lo, y), shift(hi, y), as_of=as_of)
        if b and b["n_visits"] >= P["MIN_VISITS"] and b["drupes_sampled"] >= P["MIN_DRUPES"]:
            base.append({"season": y, "rate_pct": estimate(b, how)})
            if cur:
                overlap.append(len(cur["sites"] & b["sites"]))
    out["baseline_n"] = len(base)
    out["baseline_median"] = (round(statistics.median([b["rate_pct"] for b in base]), 4)
                              if base else None)

    enough = (cur is not None and cur["n_visits"] >= P["MIN_VISITS"]
              and cur["drupes_sampled"] >= P["MIN_DRUPES"])

    # unmatched (computed but not published by the engine)
    if not enough or len(base) < P["MIN_BASELINE_SEASONS"]:
        out["historical_state_unmatched"] = "INSUFFICIENT_DATA"
    else:
        v = out["value_pct"]
        rates = [b["rate_pct"] for b in base]
        below = sum(1 for r in rates if r < v) + 0.5 * sum(1 for r in rates if r == v)
        p = below / len(rates)
        out["pctl_unmatched"] = round(p, 4)
        out["historical_state_unmatched"] = ("ABOVE_HISTORICAL" if p >= P["HIGH_PCTL"]
                                             else "BELOW_HISTORICAL" if p <= P["LOW_PCTL"]
                                             else "TYPICAL")

    # matched panel
    matched = []
    if cur:
        for y in range(first_year, as_of.year):
            b_all = idx.pooled(province, shift(lo, y), shift(hi, y), as_of=as_of)
            if not b_all:
                continue
            shared = cur["sites"] & b_all["sites"]
            if len(shared) < P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]:
                continue
            now = idx.pooled(province, lo, hi, only_sites=shared, as_of=as_of)
            then = idx.pooled(province, shift(lo, y), shift(hi, y),
                              only_sites=shared, as_of=as_of)
            if not now or not then or not then["drupes_sampled"] or not now["drupes_sampled"]:
                continue
            matched.append({"season": y, "n_groves_shared": len(shared),
                            "now": estimate(now, how), "then": estimate(then, how),
                            "drupes_now": now["drupes_sampled"],
                            "drupes_then": then["drupes_sampled"],
                            "inf_now": now["infested_drupes"],
                            "inf_then": then["infested_drupes"]})
    out["matched_panel_seasons"] = len(matched)
    if want_matched_detail:
        out["matched"] = matched

    if not enough:
        out["historical_state"] = "INSUFFICIENT_DATA"
        out["hist_reason"] = "observation gate"
    elif len(matched) < P["MIN_BASELINE_SEASONS"]:
        out["historical_state"] = "INSUFFICIENT_DATA"
        out["hist_reason"] = f"{len(matched)} matched seasons"
    else:
        higher = sum(1 for m in matched if m["now"] > m["then"])
        lower = sum(1 for m in matched if m["now"] < m["then"])
        out["n_lower"] = lower
        out["n_higher"] = higher
        out["n_matched"] = len(matched)
        share_lower = lower / len(matched)
        out["historical_state"] = (
            "BELOW_HISTORICAL" if share_lower >= P["HIGH_PCTL"] else
            "ABOVE_HISTORICAL" if (higher / len(matched)) >= P["HIGH_PCTL"] else "TYPICAL")
        out["hist_reason"] = f"lower than {lower} of {len(matched)}"

    # NOTE: the engine reaches the matched branch even when `enough` is False and
    # then overwrites historical_state with the matched verdict. Reproduced above
    # by testing `enough` first, which is what the engine's quality gate does.
    if not enough:
        out["historical_state"] = "INSUFFICIENT_DATA" if len(matched) < P["MIN_BASELINE_SEASONS"] \
            else out["historical_state"]

    # trend
    pts = []
    for i in range(P["TREND_MIN_WINDOWS"] + 1):
        h = as_of - dt.timedelta(days=P["WINDOW_DAYS"] * i)
        l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
        w = idx.pooled(province, l, h, as_of=as_of)
        if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
            pts.append(estimate(w, how))
    pts.reverse()
    out["trend_points"] = pts
    if len(pts) < P["TREND_MIN_WINDOWS"]:
        out["observed_trend"] = "UNKNOWN"
    else:
        delta = pts[-1] - pts[0]
        out["trend_delta"] = round(delta, 4)
        if abs(delta) < P["TREND_MIN_ABS_CHANGE_PCT"]:
            out["observed_trend"] = "STABLE_OBSERVED"
        elif all(b >= a for a, b in zip(pts, pts[1:])):
            out["observed_trend"] = "INCREASING_OBSERVED"
        elif all(b <= a for a, b in zip(pts, pts[1:])):
            out["observed_trend"] = "DECREASING_OBSERVED"
        else:
            out["observed_trend"] = "STABLE_OBSERVED"
    out["publishable"] = bool(enough)
    return out


def all_cells(idx, as_of, P=None, how="pooled", first_year=2006, **kw):
    return [cell(idx, p, as_of, P=P, how=how, first_year=first_year, **kw)
            for p in idx.provinces]


def get_index(metric="ACTIVE_INFESTATION_COUNT"):
    raw = load_raw()
    return Index(raw["visits"], metric), raw
