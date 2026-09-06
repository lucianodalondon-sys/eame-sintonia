#!/usr/bin/env python3
"""
Define the Toscana season outcome — and refuse to call it one thing.

A weekly ordinal observation per vineyard is NOT a season severity. Turning it into one
requires a choice, and each choice measures something different and is confounded
differently. So several are computed side by side, each named for what it actually is, and
each carrying its own confound in the name of its own field. The red team attacks all of
them; nothing downstream may silently pick one.

  OBSERVATION_POSITIVITY   fraction of VISITS recording any disease.
                           CONFOUND: visit intensity. A vineyard visited 20 times weighs
                           20x one visited once.
  SITE_INCIDENCE           fraction of distinct VINEYARDS with >=1 positive visit.
                           CONFOUND: panel composition and season length. Not confounded by
                           visit intensity. Closer to a true incidence across sites.
  SITE_MAX_CLASS_MEAN      mean over vineyards of that vineyard's highest class reached.
                           Uses the ordinal, so it needs the label order, never order_n.
  ONSET_WEEK_MEDIAN        median ISO week of each vineyard's FIRST positive observation.
                           A TIMING target, not an intensity one — arguably the most
                           decision-relevant, and the least sensitive to how bad the season
                           eventually got.
  BUNCH_INCIDENCE_BANDED   from var 36, which records real percentage bands on bunches.
                           The only variable here that carries a percentage at all.

ORDINAL ORDER comes from the LABELS (nessuna < bassa < media < alta), never from the API's
order_n (which ranks media below bassa) and never from the code number (50=media, 51=bassa).
"""
import json, os, glob, collections, statistics, datetime as dt

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "RAW")

# label -> rank. The ONLY ordinal authority in this pilot.
LEAF_ORDER = {"nessuna": 0, "bassa": 1, "media": 2, "alta": 3}
# var 36 bunch bands. Note the source's own gap: 10-15% has no band.
BUNCH_ORDER = {"nessuna": 0, "1-5%": 1, "5-10%": 2, ">15%": 3}
BUNCH_MIDPOINT = {"nessuna": 0.0, "1-5%": 3.0, "5-10%": 7.5, ">15%": 20.0}  # >15% midpoint is a GUESS, flagged

def code_map():
    idx = json.load(open(os.path.join(ROOT, "collection_index.json")))
    m = {}
    for s in idx["schemas"].values():
        for c in s["codes"]:
            m[(c["var"], str(c["code"]))] = c["name"] if "name" in c else c["label"]
    return m

def load(var_id, regime="all"):
    m = code_map()
    out = collections.defaultdict(list)
    for fn in sorted(glob.glob(os.path.join(RAW, f"*_v{var_id}_{regime}_*.json"))):
        base = os.path.basename(fn)[:-5]
        reg = "_".join(base.split("_")[2:-1])
        if reg != regime:
            continue
        y = int(base.split("_")[-1])
        for r in json.load(open(fn)):
            lab = m.get((var_id, str(r.get("val"))))
            if lab is None:
                continue
            out[y].append({"field": r.get("id_field"), "week": r.get("week"),
                           "date": r.get("date"), "label": lab,
                           "prov": r.get("nome_area"), "comune": r.get("admin_code"),
                           "org": r.get("org_name"), "lat": r.get("lat"), "lon": r.get("lon")})
    return dict(out)

def season_outcomes(var_id=34, regime="all", order=None, upto_week=None):
    order = order or LEAF_ORDER
    data = load(var_id, regime)
    res = {}
    for y, rows in sorted(data.items()):
        if upto_week is not None:
            rows = [r for r in rows if r["week"] and int(r["week"]) <= upto_week]
        if not rows:
            continue
        pos = [r for r in rows if order.get(r["label"], 0) > 0]
        sites = collections.defaultdict(list)
        for r in rows:
            sites[r["field"]].append(r)
        site_pos = {f for f, rs in sites.items() if any(order.get(x["label"], 0) > 0 for x in rs)}
        maxcls = [max(order.get(x["label"], 0) for x in rs) for rs in sites.values()]
        onsets = []
        for f, rs in sites.items():
            p = sorted((int(x["week"]) for x in rs if x["week"] and order.get(x["label"], 0) > 0))
            if p:
                onsets.append(p[0])
        res[y] = {
            "n_visits": len(rows),
            "n_sites": len(sites),
            "n_positive_visits": len(pos),
            "OBSERVATION_POSITIVITY": round(len(pos) / len(rows), 4),
            "SITE_INCIDENCE": round(len(site_pos) / len(sites), 4) if sites else None,
            "SITE_MAX_CLASS_MEAN": round(statistics.mean(maxcls), 4) if maxcls else None,
            "ONSET_WEEK_MEDIAN": statistics.median(onsets) if onsets else None,
            "n_sites_with_onset": len(onsets),
            "week_min": min(int(r["week"]) for r in rows if r["week"]),
            "week_max": max(int(r["week"]) for r in rows if r["week"]),
            "class_counts": dict(collections.Counter(r["label"] for r in rows)),
            "n_provinces": len({r["prov"] for r in rows if r["prov"]}),
            "n_comuni": len({r["comune"] for r in rows if r["comune"]}),
            "n_orgs": len({r["org"] for r in rows if r["org"]}),
        }
    return res

if __name__ == "__main__":
    import sys
    var = int(sys.argv[1]) if len(sys.argv) > 1 else 34
    reg = sys.argv[2] if len(sys.argv) > 2 else "all"
    order = BUNCH_ORDER if var == 36 else LEAF_ORDER
    r = season_outcomes(var, reg, order)
    if not r:
        print(f"NO DATA var={var} regime={reg}"); raise SystemExit
    print(f"=== var {var} regime={reg}   ordinal order from LABELS: {list(order)}")
    print(f"{'year':5s} {'visits':>7s} {'sites':>6s} {'obsPos':>7s} {'siteInc':>8s} "
          f"{'maxCls':>7s} {'onsetWk':>8s} {'wk range':>10s} {'prov':>5s} {'orgs':>5s}")
    for y, v in r.items():
        print(f"{y:5d} {v['n_visits']:7d} {v['n_sites']:6d} {v['OBSERVATION_POSITIVITY']:7.3f} "
              f"{(v['SITE_INCIDENCE'] or 0):8.3f} {(v['SITE_MAX_CLASS_MEAN'] or 0):7.3f} "
              f"{str(v['ONSET_WEEK_MEDIAN']):>8s} {v['week_min']:4d}-{v['week_max']:<5d} "
              f"{v['n_provinces']:5d} {v['n_orgs']:5d}")
    json.dump(r, open(os.path.join(ROOT, f"outcomes_v{var}_{reg}.json"), "w"), indent=1)
    print(f"\nYEARS={len(r)}  TOTAL_VISITS={sum(v['n_visits'] for v in r.values())}")
