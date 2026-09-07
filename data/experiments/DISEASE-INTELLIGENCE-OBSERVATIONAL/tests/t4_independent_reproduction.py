#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · TEST 4 — THE SAME NUMBERS BY A SECOND ROAD.

Two scripts that both call di_observe.cell() are not two measurements. This file does not
import the engine. It re-implements the whole thing from the CONTRACT AS WRITTEN - the visit
key, the sanity rules, the pooled rate, the matched-panel baseline, the trend - reading the
raw JSON directly, in a different style, and then compares field by field.

Where the two roads disagree, the disagreement is the finding, not the average.

Out: t4_independent_reproduction.json
"""
import os, sys, json, glob, statistics, hashlib, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
W, MIN_VISITS, MIN_DRUPES, MIN_BASE, MIN_OVERLAP = 28, 8, 400, 5, 8
HIGH = 0.80
TREND_N = 3
# The contract moved twice while this file existed and this file follows it, in its own shape:
#  - a grove is (id_field, admin_code), because id_field alone is recycled between seasons
#  - a trend direction is named only when the first and last windows' 95% intervals separate,
#    because a fixed percentage-point threshold was uncalibrated to the sample
#  - the served value is a PERCENTAGE from 2020 and a COUNT before it: the source's own SQL
#    already divides by tot and multiplies by 100, so dividing again is wrong
VAR = {"num": -1001, "den": 1}          # active infestation over olives sampled


# ── road two: read the archive with a different shape ────────────────────────────
def read():
    """A flat table of visits, built by dict-of-dicts rather than by the engine's loader."""
    table = collections.defaultdict(dict)
    meta = collections.defaultdict(dict)
    hashes = {}
    for role, v in VAR.items():
        for fn in sorted(glob.glob(os.path.join(CASE, "RAW", f"*_v{v}_*.json"))):
            raw = open(fn, "rb").read()
            hashes[os.path.basename(fn)] = hashlib.sha256(raw).hexdigest()
            for r in json.loads(raw.decode("utf-8")):
                if r.get("id_field") is None or not r.get("date"):
                    continue
                k = (r["id_field"], r["date"])
                val = r.get("val")
                try:
                    val = None if val in (None, "") else float(str(val).replace(",", "."))
                except ValueError:
                    val = None
                table[k][role] = val
                meta[k] = {"province": r.get("nome_area"), "date": r["date"],
                           "grove": (None if r.get("admin_code") is None
                                     else (r["id_field"], r["admin_code"]))}
    return table, meta, hashes


def usable(rec):
    n, c = rec.get("den"), rec.get("num")
    if n is None or n <= 0:
        return False
    if c is None:
        return True
    return not (c < 0 or c > n)


def window(table, meta, lo, hi, province, sites=None):
    num = den = 0.0
    nv, groves, dates = 0, set(), []
    for k, rec in table.items():
        m = meta[k]
        if m["province"] != province:
            continue
        d = dt.date.fromisoformat(m["date"])
        if not (lo <= d <= hi):
            continue
        if sites is not None and m.get("grove") not in sites:
            continue
        if not usable(rec):
            continue
        c, n = rec.get("num"), rec.get("den")
        if c is None or n is None:
            continue
        if d.year >= 2020:
            c = c * n / 100.0
        num += c
        den += n
        nv += 1
        if m.get("grove") is not None:
            groves.add(m["grove"])
        dates.append(d)
    if nv == 0:
        return None
    return {"pct": round(100.0 * num / den, 4), "num": round(num, 2), "den": round(den, 2),
            "n_visits": nv, "groves": groves, "last": max(dates).isoformat()}


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (round(100 * max(0.0, c - h), 4), round(100 * min(1.0, c + h), 4))


def shift(d, y):
    try:
        return d.replace(year=y)
    except ValueError:
        return d.replace(year=y, day=28)


def cell_road_two(table, meta, province, as_of=AS_OF):
    lo, hi = as_of - dt.timedelta(days=W - 1), as_of
    cur = window(table, meta, lo, hi, province)
    out = {"province": province,
           "value_pct": cur["pct"] if cur else None,
           "n_visits": cur["n_visits"] if cur else 0,
           "n_sites": len(cur["groves"]) if cur else 0,
           "drupes_sampled": cur["den"] if cur else 0,
           "infested_drupes": cur["num"] if cur else 0,
           "last_observation": cur["last"] if cur else None}

    matched = []
    if cur:
        for y in range(2006, as_of.year):
            b = window(table, meta, shift(lo, y), shift(hi, y), province)
            if not b:
                continue
            shared = cur["groves"] & b["groves"]
            if len(shared) < MIN_OVERLAP:
                continue
            now = window(table, meta, lo, hi, province, sites=shared)
            then = window(table, meta, shift(lo, y), shift(hi, y), province, sites=shared)
            if now and then:
                matched.append((y, now["pct"], then["pct"]))
    out["matched_panel_seasons"] = len(matched)
    if len(matched) < MIN_BASE:
        out["historical_state"] = "INSUFFICIENT_DATA"
    else:
        lower = sum(1 for _, n, t in matched if n < t)
        higher = sum(1 for _, n, t in matched if n > t)
        out["historical_state"] = ("BELOW_HISTORICAL" if lower / len(matched) >= HIGH else
                                   "ABOVE_HISTORICAL" if higher / len(matched) >= HIGH
                                   else "TYPICAL")
        out["matched_lower"] = lower
        out["matched_higher"] = higher

    ws = []
    for i in range(TREND_N + 1):
        h = as_of - dt.timedelta(days=W * i)
        w = window(table, meta, h - dt.timedelta(days=W - 1), h, province)
        if w and w["n_visits"] >= MIN_VISITS and w["den"] >= MIN_DRUPES:
            ws.append(w)
    ws.reverse()
    pts = [w["pct"] for w in ws]
    if len(ws) < TREND_N:
        out["observed_trend"] = "UNKNOWN"
    else:
        alo, ahi = wilson(ws[0]["num"], ws[0]["den"])
        blo, bhi = wilson(ws[-1]["num"], ws[-1]["den"])
        sep = (blo > ahi) or (alo > bhi)
        up = all(b >= a for a, b in zip(pts, pts[1:]))
        dn = all(b <= a for a, b in zip(pts, pts[1:]))
        out["observed_trend"] = ("INCREASING_OBSERVED" if sep and up else
                                 "DECREASING_OBSERVED" if sep and dn else "STABLE_OBSERVED")
    out["trend_points"] = pts
    return out


def main():
    table, meta, hashes = read()
    provs = sorted({m["province"] for m in meta.values() if m["province"]})
    mine = {p: cell_road_two(table, meta, p) for p in provs}

    # road one: the engine, loaded only now, only to read its answer
    sys.path.insert(0, os.path.join(HERE, "..", "engine"))
    import di_core, di_observe
    sheet = di_core.load_sheet()
    loaded = di_core.load_visits(CASE, sheet, AS_OF)
    theirs = {}
    for p in provs:
        c = di_observe.cell(loaded["visits"], sheet, p, "ACTIVE_INFESTATION_COUNT", AS_OF)
        theirs[p] = {"value_pct": c["observation"].get("value_pct"),
                     "n_visits": c["observation"].get("n_visits", 0),
                     "n_sites": c["observation"].get("n_sites", 0),
                     "drupes_sampled": c["observation"].get("drupes_sampled", 0),
                     "infested_drupes": c["observation"].get("infested_drupes", 0),
                     "last_observation": c["observation"].get("last_observation"),
                     "historical_state": c["analysis"]["historical_state"],
                     "matched_panel_seasons": c["analysis"]["matched_panel_seasons"],
                     "observed_trend": c["analysis"]["observed_trend"],
                     "trend_points": [x["rate_pct"]
                                      for x in c["analysis"]["observed_trend_points"]]}

    FIELDS = ["value_pct", "n_visits", "n_sites", "drupes_sampled", "infested_drupes",
              "last_observation", "historical_state", "matched_panel_seasons",
              "observed_trend", "trend_points"]
    agree = disagree = 0
    detail = {}
    for p in provs:
        d = {}
        for f in FIELDS:
            a, b = mine[p].get(f), theirs[p].get(f)
            if a == b:
                agree += 1
            else:
                disagree += 1
                d[f] = {"road_two": a, "engine": b}
        if d:
            detail[p] = d

    # provenance: does road two hash the same files?
    engine_files = {f["file"] for pv in loaded["provenance"].values() for f in pv["files"]}
    out = {"AS_OF": AS_OF.isoformat(), "PROVINCES": len(provs), "FIELDS_PER_PROVINCE": len(FIELDS),
           "FIELDS_COMPARED": agree + disagree, "AGREE": agree, "DISAGREE": disagree,
           "DISAGREEMENTS": detail,
           "PROVENANCE": {"files_hashed_road_two": len(hashes),
                          "files_hashed_engine": len(engine_files),
                          "same_set": sorted(hashes) == sorted(engine_files)
                          if len(hashes) == len(engine_files) else "different counts",
                          "note": "road two reads only the two variables it needs (num, den); "
                                  "the engine reads all four canonical measurements"},
           "VERDICT": "AGREE" if disagree == 0 else "DISAGREE"}
    json.dump(out, open(os.path.join(HERE, "t4_independent_reproduction.json"), "w",
                        encoding="utf-8"), indent=1, default=str)
    print(f"provinces {len(provs)}  fields compared {agree + disagree}  "
          f"agree {agree}  disagree {disagree}")
    for p, d in detail.items():
        print(f"  {p}: {json.dumps(d, default=str)[:300]}")
    print(f"\nprovenance: road two hashed {len(hashes)} files, engine hashed "
          f"{len(engine_files)}")
    print(f"VERDICT = {out['VERDICT']}")


if __name__ == "__main__":
    main()
