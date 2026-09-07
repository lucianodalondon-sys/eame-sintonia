#!/usr/bin/env python3
"""RT3-07  Does the id_field instability change a PUBLISHED historical_state?

Re-runs the engine's own matched-panel logic three ways:
  AS_SHIPPED  shared = every id_field in both windows
  STRICT      shared minus groves that changed COMUNE or moved >500 m between the two windows
              (absence of a usable coordinate is NOT treated as evidence of a move)
  PARANOID    STRICT, and also minus groves whose 'then' coordinate is unusable (0,0), i.e.
              every grove kept is positively verified to be in the same place
and prints the published historical_state under each.
"""
import collections, math, os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "engine")))
sys.path.insert(0, HERE)
import rt3_lib as L
import di_core, di_observe

AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
P = di_observe.PARAMS

def hav(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) *
         math.sin(math.radians(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

def pt(r):
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if la is None or lo is None: return None
    return (la, lo) if 42.2 <= la <= 44.5 and 9.6 <= lo <= 12.45 else None

raw = L.visit_rows()
by_field_date = collections.defaultdict(list)
for (i, d), r in raw.items():
    by_field_date[i].append((dt.date.fromisoformat(str(d)), r))

def geo(idf, a, b):
    coms, pts = set(), []
    for d, r in by_field_date[idf]:
        if a <= d <= b:
            coms.add(L.admin6(r.get("admin_code")))
            p = pt(r)
            if p: pts.append(p)
    return coms, pts

sheet = di_core.load_sheet()
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)
visits = loaded["visits"]
provs = sorted({v["province"] for v in visits if v["province"]})
lo_, hi_ = di_observe._win(AS_OF, P["WINDOW_DAYS"])

def state_from(matched):
    if len(matched) < P["MIN_BASELINE_SEASONS"]:
        return "INSUFFICIENT_DATA", len(matched), None, None
    hi = sum(1 for m in matched if m[1] > m[2])
    lw = sum(1 for m in matched if m[1] < m[2])
    if lw / len(matched) >= P["HIGH_PCTL"]: s = "BELOW_HISTORICAL"
    elif hi / len(matched) >= P["HIGH_PCTL"]: s = "ABOVE_HISTORICAL"
    else: s = "TYPICAL"
    return s, len(matched), hi, lw

print("=" * 78)
print("RT3-07  does grove-identity failure change a published historical_state?")
print("=" * 78)
print(f"\n{'province':15s} {'mode':10s} {'state':>18s} {'seasons':>7s} "
      f"{'higher':>6s} {'lower':>6s}   groves dropped")
rowsout = []
for prov in provs:
    cur = di_observe.pooled(visits, lo_, hi_, prov, METRIC)
    if not cur:
        continue
    res = {}
    dropped = {"STRICT": 0, "PARANOID": 0}
    for mode in ("AS_SHIPPED", "STRICT", "PARANOID"):
        matched = []
        for y in range(2006, AS_OF.year):
            blo, bhi = di_observe._shift(lo_, y), di_observe._shift(hi_, y)
            b_all = di_observe.pooled(visits, blo, bhi, prov, METRIC)
            if not b_all:
                continue
            shared = set(cur["sites"] & b_all["sites"])
            if mode != "AS_SHIPPED":
                keep = set()
                for idf in shared:
                    cn, cp = geo(idf, lo_, hi_)
                    tn, tp = geo(idf, blo, bhi)
                    if cn and tn and cn != tn:
                        continue                       # changed comune
                    if cp and tp:
                        if min(hav(a, b) for a in cp for b in tp) > 500:
                            continue                   # moved
                        keep.add(idf)
                    else:
                        if mode == "STRICT":
                            keep.add(idf)              # unverifiable, not proven moved
                dropped[mode] += len(shared) - len(keep)
                shared = keep
            if len(shared) < P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]:
                continue
            now = di_observe.pooled(visits, lo_, hi_, prov, METRIC, only_sites=shared)
            then = di_observe.pooled(visits, blo, bhi, prov, METRIC, only_sites=shared)
            if not now or not then or not now["drupes_sampled"] or not then["drupes_sampled"]:
                continue
            matched.append((y, now["rate_pct"], then["rate_pct"]))
        res[mode] = state_from(matched)
    for mode in ("AS_SHIPPED", "STRICT", "PARANOID"):
        s, n, h, l = res[mode]
        d = "" if mode == "AS_SHIPPED" else f"{dropped[mode]} grove-slots removed"
        print(f"{prov if mode=='AS_SHIPPED' else '':15s} {mode:10s} {s:>18s} {n:>7} "
              f"{str(h):>6} {str(l):>6}   {d}")
    changed = len({res[m][0] for m in res}) > 1
    if changed:
        print(f"{'':15s} {'>>>':10s} PUBLISHED STATE CHANGES: "
              f"{res['AS_SHIPPED'][0]} -> STRICT {res['STRICT'][0]} "
              f"-> PARANOID {res['PARANOID'][0]}")
    rowsout.append({"province": prov,
                    **{m: {"state": res[m][0], "seasons": res[m][1]} for m in res},
                    "changes": changed})
    print()

print("provinces whose PUBLISHED historical_state moves when non-identical groves are "
      "removed:")
for r in rowsout:
    if r["changes"]:
        print(f"  {r['province']}: AS_SHIPPED {r['AS_SHIPPED']['state']} "
              f"({r['AS_SHIPPED']['seasons']} seasons) -> "
              f"STRICT {r['STRICT']['state']} ({r['STRICT']['seasons']}) -> "
              f"PARANOID {r['PARANOID']['state']} ({r['PARANOID']['seasons']})")
if not any(r["changes"] for r in rowsout):
    print("  none.")
json.dump(rowsout, open(os.path.join(HERE, "rt3_07_impact.json"), "w", encoding="utf-8"),
          indent=1)
