#!/usr/bin/env python3
"""RT3-06  The MATCHED PANEL is the published historical statement. It says
"the same groves". Its only evidence that a grove is the same grove is the integer id_field.

For every matched comparison the engine actually publishes, this asks:
  - is the grove in the SAME COMUNE now as it was then?
  - is it at the SAME COORDINATE now as it was then?  (metres)
  - or is its 'then' coordinate 0,0 - i.e. the claim of sameness has NO evidence at all
    beyond the integer?
and then recomputes the comparison with the unverifiable groves removed, to see whether the
published historical_state survives.
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

def hav(la1, lo1, la2, lo2):
    R = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    h = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) *
         math.sin(math.radians(lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

def usable_pt(r):
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if la is None or lo is None:
        return None
    if 42.2 <= la <= 44.5 and 9.6 <= lo <= 12.45:
        return (la, lo)
    return None

print("=" * 78)
print("RT3-06  matched-panel integrity")
print("=" * 78)

raw = L.visit_rows()
sheet = di_core.load_sheet()
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)
visits = loaded["visits"]
provs = sorted({v["province"] for v in visits if v["province"]})

lo_, hi_ = di_observe._win(AS_OF, P["WINDOW_DAYS"])

def geo_in_window(idf, a, b):
    """the geography this grove carried inside one window: comuni, points"""
    coms, pts, dates = set(), [], []
    for (i, d), r in raw.items():
        if i != idf:
            continue
        dd = dt.date.fromisoformat(str(d))
        if not (a <= dd <= b):
            continue
        coms.add(L.admin6(r.get("admin_code")))
        p = usable_pt(r)
        if p:
            pts.append(p)
        dates.append(dd)
    return coms, pts

summary = []
grand = collections.Counter()
for prov in provs:
    cur = di_observe.pooled(visits, lo_, hi_, prov, METRIC)
    if not cur:
        continue
    rows = []
    for y in range(2006, AS_OF.year):
        blo, bhi = di_observe._shift(lo_, y), di_observe._shift(hi_, y)
        b_all = di_observe.pooled(visits, blo, bhi, prov, METRIC)
        if not b_all:
            continue
        shared = cur["sites"] & b_all["sites"]
        if len(shared) < P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]:
            continue
        moved_com, moved_far, no_then_pt, verified = [], [], [], []
        for idf in sorted(shared):
            cn, cp = geo_in_window(idf, lo_, hi_)
            tn, tp = geo_in_window(idf, blo, bhi)
            if cn and tn and cn != tn:
                moved_com.append((idf, sorted(tn), sorted(cn)))
            if not tp:
                no_then_pt.append(idf)
                continue
            if not cp:
                no_then_pt.append(idf)
                continue
            d = min(hav(a[0], a[1], b[0], b[1]) for a in cp for b in tp)
            if d > 500:
                moved_far.append((idf, round(d)))
            else:
                verified.append(idf)
        rows.append({"season": y, "shared": len(shared),
                     "moved_comune": moved_com, "moved_over_500m": moved_far,
                     "then_coord_unusable": no_then_pt, "verified_same_place": verified})
        grand["matched_comparisons"] += 1
        grand["shared_grove_slots"] += len(shared)
        grand["slots_verified_same_place"] += len(verified)
        grand["slots_then_coord_unusable"] += len(no_then_pt)
        grand["slots_moved_over_500m"] += len(moved_far)
        grand["slots_moved_comune"] += len(moved_com)
    if not rows:
        continue
    n_ok = sum(1 for r in rows if not r["then_coord_unusable"] and not r["moved_over_500m"]
               and not r["moved_comune"])
    print(f"\n--- {prov}: {len(rows)} matched seasons published "
          f"(engine minimum is {P['MIN_BASELINE_SEASONS']}) ---")
    print(f"    {'season':>6} {'shared':>6} {'same place':>10} {'then 0,0':>9} "
          f"{'>500 m':>7} {'moved comune':>12}")
    for r in rows:
        print(f"    {r['season']:>6} {r['shared']:>6} {len(r['verified_same_place']):>10} "
              f"{len(r['then_coord_unusable']):>9} {len(r['moved_over_500m']):>7} "
              f"{len(r['moved_comune']):>12}")
        for idf, t, c in r["moved_comune"]:
            print(f"           id_field {idf}: comune {t} in {r['season']} -> {c} now")
        for idf, d in r["moved_over_500m"]:
            print(f"           id_field {idf}: {d:,} m between the two windows")
    print(f"    seasons where EVERY shared grove is verifiably the same place: "
          f"{n_ok} / {len(rows)}   (engine needs {P['MIN_BASELINE_SEASONS']})")
    summary.append({"province": prov, "matched_seasons_published": len(rows),
                    "matched_seasons_fully_verifiable": n_ok})

print("\n" + "=" * 78)
print("ACROSS EVERY MATCHED COMPARISON THE ENGINE PUBLISHES")
print("=" * 78)
tot = grand["shared_grove_slots"]
print(f"  matched comparisons                          {grand['matched_comparisons']:,}")
print(f"  grove-slots inside them                      {tot:,}")
print(f"    verifiably the same place (<=500 m)        "
      f"{grand['slots_verified_same_place']:,} / {tot:,}")
print(f"    'then' coordinate unusable (0,0 or out)    "
      f"{grand['slots_then_coord_unusable']:,} / {tot:,}")
print(f"    moved more than 500 m between the windows  "
      f"{grand['slots_moved_over_500m']:,} / {tot:,}")
print(f"    changed comune between the windows         "
      f"{grand['slots_moved_comune']:,} / {tot:,}")
print("\n  provinces whose published matched state would survive a rule of "
      "'every shared grove must be verifiably the same place':")
for s in summary:
    ok = s["matched_seasons_fully_verifiable"] >= P["MIN_BASELINE_SEASONS"]
    print(f"    {s['province']:15s} {s['matched_seasons_fully_verifiable']:>3} of "
          f"{s['matched_seasons_published']:>3} fully verifiable -> "
          f"{'SURVIVES' if ok else 'WOULD BECOME INSUFFICIENT_DATA'}")

json.dump({"per_province": summary, "totals": dict(grand)},
          open(os.path.join(HERE, "rt3_06_matched.json"), "w", encoding="utf-8"), indent=1)
