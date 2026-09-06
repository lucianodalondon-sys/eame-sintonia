#!/usr/bin/env python3
"""RT2-A6 — the denominator is joined on a key that is not unique across seasons.

ENGINE/current_pressure.denominator_guard builds one dictionary over EVERY year's file:

    for fn in glob(RAW/*_v{denom_var}_*.json):
        for r in json.load(open(fn)):
            den[r["id_survey"]] = float(v) ...
    kept = [r for r in rows if den.get(r.get("id_survey"))]

id_survey is unique WITHIN a season file but is re-used ACROSS seasons: 79,251 rows of var
-1002 carry only 52,025 distinct id_survey strings. Whichever file glob returns last wins, so a
visit can be tested against a different visit's "Olive campionate".

The archive is accidentally partly protected because the source changed the JSON type of
id_survey at 2020 (int 2006-2019, string 2020-2026) and a dict keys int 5 and "5" separately.
This script measures the collisions the way the ENGINE sees them (raw type, no coercion), and
counts how many visits the guard therefore judges on the wrong denominator.
"""
import json, glob, os, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.join(HERE, "..", "..", "CASES", "OLIVO-BACTROCERA-TOSCANA")


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


if __name__ == "__main__":
    # exactly the engine's loop, but remembering every writer instead of only the last
    writers = collections.defaultdict(list)
    for fn in glob.glob(os.path.join(CASE, "RAW", "*_v1_*.json")):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn, encoding="utf-8")):
            writers[r["id_survey"]].append((y, num(r.get("val"))))

    coll = {k: v for k, v in writers.items() if len(v) > 1}
    print(f"denominator dictionary as the engine builds it (RAW key, no str()):")
    print(f"  distinct keys                    : {len(writers)}")
    print(f"  keys written by >1 season        : {len(coll)}")
    print(f"  var-1 rows involved in a collision: {sum(len(v) for v in coll.values())}")

    # a collision only changes the verdict when the winners disagree about truthiness
    harmful = {k: v for k, v in coll.items()
               if len({bool(x[1]) for x in v}) > 1}
    print(f"  collisions where the seasons DISAGREE about whether the denominator is usable: "
          f"{len(harmful)}")

    # how many -1002 visits are judged on another season's denominator
    aff = collections.Counter()
    seen = collections.defaultdict(dict)
    for fn in glob.glob(os.path.join(CASE, "RAW", "*_v-1002_*.json")):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn, encoding="utf-8")):
            k = r["id_survey"]
            if k in coll:
                own = [x for x in writers[k] if x[0] == y]
                other = [x for x in writers[k] if x[0] != y]
                if own and other and bool(own[0][1]) != any(bool(x[1]) for x in other):
                    aff[y] += 1
    print(f"  -1002 visits whose keep/drop verdict can flip on the collision, by season: "
          f"{dict(sorted(aff.items()))}  TOTAL {sum(aff.values())}")

    # what the guard actually drops, and whether the drop is era-structured
    den_last = {}
    for fn in glob.glob(os.path.join(CASE, "RAW", "*_v1_*.json")):
        for r in json.load(open(fn, encoding="utf-8")):
            den_last[r["id_survey"]] = num(r.get("val"))
    drop = collections.Counter(); tot = collections.Counter()
    win_drop = 0; win_tot = 0
    for fn in sorted(glob.glob(os.path.join(CASE, "RAW", "*_v-1002_*.json"))):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn, encoding="utf-8")):
            tot[y] += 1
            dropped = not den_last.get(r["id_survey"])
            drop[y] += dropped
            if r.get("date"):
                try:
                    d = dt.date.fromisoformat(r["date"])
                except ValueError:
                    continue
                if y == 2026 and dt.date(2026, 8, 10) <= d <= dt.date(2026, 9, 6):
                    win_tot += 1
                    win_drop += dropped
    print(f"\n  the guard's own effect, by season (dropped / scored):")
    for y in sorted(tot):
        print(f"    {y} {drop[y]:5d}/{tot[y]:5d}  {drop[y]/tot[y]:.4f}")
    print(f"  TOTAL {sum(drop.values())}/{sum(tot.values())}")
    print(f"  inside the published window 2026-08-10..2026-09-06: "
          f"{win_drop}/{win_tot} visits dropped for a zero or unknown denominator")
