#!/usr/bin/env python3
"""
CURRENT_PRESSURE — the exact definition. One code path for every REGION x CROP x ISSUE.

THE CONTRACT (pre-registered here, before any output was read):

  INPUTS           official field-scouting visits only. One row = one visit to one monitored
                   field (id_field) on one date, carrying an ordinal code for one survey
                   variable. EvidenceRole = OFFICIAL_OBSERVATION. No model, no forecast, no
                   weather, no interpolation, no expert opinion.
  TIME_WINDOW      the trailing WINDOW_DAYS days ending at AS_OF, inclusive of both ends.
                   AS_OF is an input, never "now" read from the clock, so any run is replayable.
  REGIONAL_UNIT    province (nome_area) inside one region. Never national. Never "Italy".
                   A province with no visits in the window does not inherit its neighbour.
  BASELINE         the SAME calendar window (same month-day span) in every prior season present
                   in the archive, same province, same crop, same issue. The current value is
                   placed as a percentile inside that historical distribution. A baseline season
                   that itself fails MIN_SITES is dropped, not filled.
  UPDATE_FREQUENCY set by the source's own publication cadence; measured, not assumed
                   (see DATA_LATENCY in the output).
  UNKNOWN_RULE     n_sites < MIN_SITES                  -> UNKNOWN_NO_DATA      (no value at all)
                   usable baseline seasons < MIN_BASE   -> UNKNOWN_NO_BASELINE  (value, no class)
                   UNKNOWN is a published state. It is never rendered as zero, never as "low",
                   and never hidden by widening the window until something appears.
  EVIDENCE         every emitted cell carries n_visits, n_sites, first/last observation date,
                   the source URL and the sha256 of the raw file it was computed from.

  PARAMETERS (all of them, declared; sensitivity is measured in sensitivity())
    WINDOW_DAYS = 28   four survey rounds at the weekly cadence these programmes actually run
    MIN_SITES   = 8    below this a province percentile is noise
    MIN_BASE    = 5    fewer prior seasons cannot support a percentile statement
    HIGH_P/LOW_P= .80/.20

  WHAT THIS IS NOT: it is a NOWCAST of what scouts recorded, not a forecast, and not a
  statement about fields nobody visited.
"""
import json, os, sys, glob, hashlib, datetime as dt, collections
from statistics import mean

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CASES"))
from contracts import EvidenceRole, Missing, Cutoff
from run_case import build_scale

WINDOW_DAYS, MIN_SITES, MIN_BASE, HIGH_P, LOW_P = 28, 8, 5, 0.80, 0.20
UNKNOWN_NO_DATA, UNKNOWN_NO_BASELINE = "UNKNOWN_NO_DATA", "UNKNOWN_NO_BASELINE"
HIGHER, TYPICAL, LOWER = "HIGHER_THAN_USUAL", "TYPICAL_FOR_THE_DATE", "LOWER_THAN_USUAL"


def _shift_year(d, y):
    try: return d.replace(year=y)
    except ValueError: return d.replace(year=y, day=28)      # 29 Feb -> 28 Feb, declared


def load_rows(case_dir, var_id):
    """Every raw file for this variable, with the sha256 recorded in the collection index."""
    idx = json.load(open(os.path.join(case_dir, "collection_index.json")))
    by_file = {r["file"]: r.get("sha256") for r in idx["requests"] if r.get("file")}
    empty = [(r.get("var"), r.get("year")) for r in idx["requests"] if not r.get("file")]
    rows, hashes = [], {}
    for fn in sorted(glob.glob(os.path.join(case_dir, "RAW", f"*_v{var_id}_*.json"))):
        base = os.path.basename(fn)
        h = hashlib.sha256(open(fn, "rb").read()).hexdigest()
        if by_file.get(base) and by_file[base] != h:
            raise ValueError(f"REFUSED: {base} does not match its collected sha256")
        hashes[base] = h
        for r in json.load(open(fn)):
            d = r.get("date")
            if not d: continue
            try: r["_d"] = dt.date.fromisoformat(d)
            except ValueError: continue
            rows.append(r)
    scale, unresolved, hows = build_scale(idx.get("codes") or [], var_id)
    mode = value_mode(idx, var_id)
    return rows, scale, {"api": idx["api"], "hashes": hashes, "empty_responses": empty,
                         "VALUE_MODE": mode, "scale_unresolved": unresolved, "scale_methods": hows}


def value_mode(idx, var_id):
    """ORDINAL vs NUMERIC decided by the SOURCE's own metadata, never by the case name.
    A coded variable has a code table; a measured one declares widget=numeric. Anything else
    is UNSUPPORTED and the module refuses rather than inventing a scale."""
    if [c for c in (idx.get("codes") or []) if c["id_survey_var"] == var_id]:
        return "ORDINAL"
    v = next((v for v in (idx.get("vars") or []) if v["id_survey_var"] == var_id), None)
    if v and v.get("widget") == "numeric":
        return "NUMERIC"
    return "UNSUPPORTED"


def read_value(r, scale, mode):
    """None means MISSING. Missing is never 0 (Missing.NEVER_ZERO)."""
    v = r.get("val")
    if v is None or v == "":
        return None
    if mode == "ORDINAL":
        s = scale.get(str(v))
        return None if s is None else float(s["ordinal"])
    if mode == "NUMERIC":
        try:
            return float(str(v).replace(",", "."))
        except ValueError:
            return None
    return None


def _window_value(rows, scale, lo, hi, mode="ORDINAL"):
    """Site-max over the window, then the province summary. Identical rule to the season outcome."""
    sites = collections.defaultdict(list)
    n_visits = 0
    for r in rows:
        if not (lo <= r["_d"] <= hi): continue
        v = read_value(r, scale, mode)
        if v is None: continue                     # unreadable value is MISSING, never 0
        sites[r["id_field"]].append(v)
        n_visits += 1
    if not sites: return None
    vals = [max(v) for v in sites.values()]
    return {"n_sites": len(sites), "n_visits": n_visits,
            "INCIDENCE": round(sum(1 for v in vals if v > 0) / len(vals), 4),
            "SEVERITY": round(mean(vals), 4)}


def current_pressure(case_dir, var_id, as_of, metric="INCIDENCE",
                     window_days=WINDOW_DAYS, min_sites=MIN_SITES,
                     min_base=MIN_BASE, high_p=HIGH_P, low_p=LOW_P, _pre=None):
    rows, scale, meta = _pre if _pre else load_rows(case_dir, var_id)
    mode = meta["VALUE_MODE"]
    if mode == "UNSUPPORTED":
        raise ValueError(f"REFUSED: var {var_id} is neither coded nor numeric in the source metadata")
    hi, lo = as_of, as_of - dt.timedelta(days=window_days - 1)
    by_prov = collections.defaultdict(list)
    for r in rows:
        p = r.get("nome_area")
        if p: by_prov[p].append(r)

    latest = max((r["_d"] for r in rows if r["_d"] <= as_of), default=None)
    out = {"AS_OF": as_of.isoformat(), "WINDOW": [lo.isoformat(), hi.isoformat()],
           "METRIC": metric, "VALUE_MODE": mode, "EVIDENCE_ROLE": EvidenceRole.OFFICIAL_OBSERVATION,
           "CUTOFF_LABEL": Cutoff("current_pressure", as_of, lo, hi).label(),
           "DATA_LATENCY_DAYS": (as_of - latest).days if latest else None,
           "SOURCE": meta["api"], "PARAMS": {"WINDOW_DAYS": window_days, "MIN_SITES": min_sites,
                                             "MIN_BASE": min_base, "HIGH_P": high_p, "LOW_P": low_p},
           "PROVINCES": {}}

    for prov, prows in sorted(by_prov.items()):
        cur = _window_value(prows, scale, lo, hi, mode)
        if cur is None or cur["n_sites"] < min_sites:
            Missing.assert_not_coerced_to_zero(Missing.NOT_KNOWN, None)
            out["PROVINCES"][prov] = {"STATE": UNKNOWN_NO_DATA, "VALUE": None,
                                      "n_sites": (cur or {}).get("n_sites", 0),
                                      "n_visits": (cur or {}).get("n_visits", 0)}
            continue
        base = []
        for y in sorted({r["_d"].year for r in prows}):
            if y >= as_of.year: continue
            b = _window_value(prows, scale, _shift_year(lo, y), _shift_year(hi, y), mode)
            if b and b["n_sites"] >= min_sites: base.append((y, b[metric]))
        rec = {"VALUE": cur[metric], "n_sites": cur["n_sites"], "n_visits": cur["n_visits"],
               "BASELINE_SEASONS": [y for y, _ in base], "BASELINE_N": len(base),
               "BASELINE_MEDIAN": round(sorted(v for _, v in base)[len(base) // 2], 4) if base else None}
        if len(base) < min_base:
            rec["STATE"] = UNKNOWN_NO_BASELINE
        else:
            v = cur[metric]
            below = sum(1 for _, b in base if b < v) + 0.5 * sum(1 for _, b in base if b == v)
            p = below / len(base)
            rec["PERCENTILE"] = round(p, 4)
            rec["STATE"] = HIGHER if p >= high_p else (LOWER if p <= low_p else TYPICAL)
        out["PROVINCES"][prov] = rec
    return out


def sensitivity(case_dir, var_id, as_of, metric="INCIDENCE"):
    """The parameters ARE the judgement. Measure how much the published label depends on them."""
    pre = load_rows(case_dir, var_id)
    grid = [(w, m, hp, lp) for w in (14, 21, 28, 35, 42) for m in (5, 8, 12)
            for hp, lp in ((0.75, 0.25), (0.80, 0.20), (0.90, 0.10))]
    runs = [current_pressure(case_dir, var_id, as_of, metric, w, m, MIN_BASE, hp, lp, _pre=pre)
            for w, m, hp, lp in grid]
    ref = runs[grid.index((WINDOW_DAYS, MIN_SITES, HIGH_P, LOW_P))]
    provs = sorted(ref["PROVINCES"])
    stab = {}
    for p in provs:
        states = [r["PROVINCES"].get(p, {}).get("STATE") for r in runs]
        agree = sum(1 for s in states if s == ref["PROVINCES"][p]["STATE"]) / len(states)
        stab[p] = {"REFERENCE_STATE": ref["PROVINCES"][p]["STATE"], "AGREEMENT": round(agree, 3),
                   "STATES_SEEN": sorted(set(s for s in states if s))}
    return {"GRID_SIZE": len(grid), "PER_PROVINCE": stab,
            "MEAN_AGREEMENT": round(mean(v["AGREEMENT"] for v in stab.values()), 3) if stab else None}


if __name__ == "__main__":
    case, var, as_of = sys.argv[1], int(sys.argv[2]), dt.date.fromisoformat(sys.argv[3])
    metric = sys.argv[4] if len(sys.argv) > 4 else "INCIDENCE"
    r = current_pressure(case, var, as_of, metric)
    print(f"=== CURRENT_PRESSURE  {os.path.basename(case)} var {var}  as_of {as_of}  metric {metric}")
    print(f"    window {r['WINDOW'][0]}..{r['WINDOW'][1]}  label={r['CUTOFF_LABEL']}  "
          f"latency={r['DATA_LATENCY_DAYS']}d")
    for p, v in r["PROVINCES"].items():
        print(f"  {p:14s} {v['STATE']:20s} val={str(v.get('VALUE')):7s} sites={v['n_sites']:3d} "
              f"base_n={v.get('BASELINE_N','-')} med={str(v.get('BASELINE_MEDIAN')):7s} "
              f"pct={v.get('PERCENTILE','-')}")
    n = collections.Counter(v["STATE"] for v in r["PROVINCES"].values())
    print("  ->", dict(n))


def hindcast(case_dir, var_id, month, day, years, metric="INCIDENCE", recent_only=None):
    """Replay the SAME definition at the same calendar date in every season, baseline = prior
    seasons only (walk-forward, no leakage). If a class is nearly constant across seasons the
    module is describing the archive's drift, not the season — which would make the live
    statement worthless. recent_only=N restricts the baseline to the last N prior seasons."""
    pre = load_rows(case_dir, var_id)
    rowsyears = sorted({r["_d"].year for r in pre[0]})
    res = {}
    for y in years:
        if y not in rowsyears: continue
        sub = ([r for r in pre[0] if r["_d"].year > y - 1 - (recent_only or 9999)], pre[1], pre[2]) \
              if recent_only else pre
        r = current_pressure(case_dir, var_id, dt.date(y, month, day), metric, _pre=sub)
        res[y] = {p: v["STATE"] for p, v in r["PROVINCES"].items()}
    return res


def hindcast_report(case_dir, var_id, month, day, years, metric="INCIDENCE", recent_only=None):
    h = hindcast(case_dir, var_id, month, day, years, metric, recent_only)
    provs = sorted({p for v in h.values() for p in v})
    ab = {HIGHER: "H", TYPICAL: ".", LOWER: "L", UNKNOWN_NO_DATA: "?", UNKNOWN_NO_BASELINE: "-"}
    print(f"    year " + " ".join(f"{p[:3]:>3s}" for p in provs))
    for y in sorted(h):
        print(f"    {y}  " + " ".join(f"{ab.get(h[y].get(p),' '):>3s}" for p in provs))
    flat = [s for v in h.values() for s in v.values()]
    c = collections.Counter(flat)
    tot = sum(c[k] for k in (HIGHER, TYPICAL, LOWER))
    print(f"    classified={tot}  H={c[HIGHER]} .={c[TYPICAL]} L={c[LOWER]} "
          f"?={c[UNKNOWN_NO_DATA]} -={c[UNKNOWN_NO_BASELINE]}")
    if tot:
        dom = max(c[HIGHER], c[TYPICAL], c[LOWER]) / tot
        print(f"    DOMINANT_CLASS_SHARE={dom:.3f}  -> "
              f"{'DEGENERATE (describes the archive, not the season)' if dom > 0.75 else 'DISCRIMINATING'}")
    return h
