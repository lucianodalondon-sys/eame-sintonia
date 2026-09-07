#!/usr/bin/env python3
"""RT4-09  The residual questions, each answered with a measurement.

A  Do the two EXACT-TIE windows found in rt4_04 have integer-only addends? If they do,
   summation order cannot move them at all and the two risks (tie, and order-sensitivity)
   do not intersect on this data. If any tie window has a fractional addend, they do.
B  Does any window the report publishes land in band_for's (0, 0.01) hole?
C  Is glob case-sensitive on this filesystem? (`*_v1_*` on a case-insensitive filesystem
   also matches `*_V1_*`; on Linux it does not. Same bytes, different platform, different
   file set.) Measured, not assumed - a probe file is created and removed OUTSIDE the repo.
D  Is `sorted()` inside the loader load-bearing, or does the payload also depend on the order
   the four variables are read in? Re-read with the `wanted` tuple permuted.
"""
import os, sys, json, glob, itertools, tempfile, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
DEN = "SAMPLE_SIZE / DENOMINATOR"
out = {}

sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
visits = loaded["visits"]
P = di_observe.PARAMS
lo0, hi0 = di_observe._win(AS_OF, P["WINDOW_DAYS"])


def addends(lo, hi, province, metric):
    r = []
    for v in visits:
        if v["province"] != province:
            continue
        d = dt.date.fromisoformat(v["observation_date"])
        if not (lo <= d <= hi):
            continue
        if not v["usable_for_rates"]:
            continue
        c = v["measurements"][metric]["value"]
        t = v["measurements"][DEN]["value"]
        if c is None or t is None:
            continue
        r.append((c, t))
    return r


# ---- A the two ties
TIES = [("ACTIVE_INFESTATION_COUNT", "Siena", 2025),
        ("TOTAL_INFESTATION_COUNT", "Livorno", 2020)]
A = []
for metric, prov, year in TIES:
    lo, hi = di_observe._shift(lo0, year), di_observe._shift(hi0, year)
    ps = addends(lo, hi, prov, metric)
    nonint = [(c, t) for c, t in ps if c != int(c) or t != int(t)]
    A.append({"metric": metric, "province": prov, "baseline_season": year,
              "n_addends": len(ps),
              "addends_that_are_NOT_integers": len(nonint),
              "sample_of_non_integer_addends": nonint[:5],
              "sum_is_EXACT_in_float_so_order_cannot_move_it": len(nonint) == 0})
_all_int = all(x["addends_that_are_NOT_integers"] == 0 for x in A)
out["A_TIE_WINDOWS"] = {
    "detail": A,
    "ALL_TIE_WINDOWS_HAVE_INTEGER_ONLY_ADDENDS": _all_int,
    "CONCLUSION": ("the exact ties are built from integer-only addends, so summation order "
                   "cannot move them by even one ULP; the tie is settled by round-half-to-"
                   "even and reproduces on any IEEE-754 platform. The two risks - a tie, and "
                   "order-sensitivity - do not intersect on this data."
                   if _all_int else
                   "AT LEAST ONE TIE WINDOW HAS A FRACTIONAL ADDEND: summation order can "
                   "move it across the boundary and the published digit is not stable.")}

# ---- B the band hole, over every window the report builds
windows = [("current", lo0, hi0)]
for y in range(2006, AS_OF.year):
    windows.append((f"baseline_{y}", di_observe._shift(lo0, y), di_observe._shift(hi0, y)))
for i in range(1, P["TREND_MIN_WINDOWS"] + 1):
    h = AS_OF - dt.timedelta(days=P["WINDOW_DAYS"] * i)
    windows.append((f"trend_-{i}", h - dt.timedelta(days=P["WINDOW_DAYS"] - 1), h))
provs = sorted({v["province"] for v in visits if v["province"]})
hole, scored, minnz = [], 0, None
for metric in ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
               "TOTAL_INFESTATION_COUNT"):
    for p in provs:
        for wname, lo, hi in windows:
            ps = addends(lo, hi, p, metric)
            if not ps:
                continue
            num = sum(c for c, _ in ps)
            den = sum(t for _, t in ps)
            if not den:
                continue
            scored += 1
            r = round(100.0 * num / den, 4)
            if 0 < r:
                minnz = r if minnz is None else min(minnz, r)
            if 0 < r < 0.01:
                hole.append({"metric": metric, "province": p, "window": wname,
                             "rate_pct": r, "num": num, "den": den,
                             "band": di_core.band_for(sheet, r)})
out["B_BAND_HOLE_ON_REAL_WINDOWS"] = {
    "windows_scored": scored,
    "windows_landing_in_the_(0,0.01)_hole": len(hole),
    "detail": hole[:10],
    "smallest_non_zero_published_rate_pct": minnz,
    "MEANING": ("the hole is not hit by this data at this as_of, so the crash is latent, "
                "not live" if not hole else "THE HOLE IS HIT: band_for returns None and "
                                            "di_render raises TypeError")}

# ---- C glob case sensitivity, probed outside the repo
d = tempfile.mkdtemp(prefix="rt4_glob_")
open(os.path.join(d, "c2_s1_V1_2099.json"), "w").write("[]")
open(os.path.join(d, "c2_s1_v1_2099.json"), "w").write("[]")
m = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "*_v1_*.json")))
for f in os.listdir(d):
    os.remove(os.path.join(d, f))
os.rmdir(d)
out["C_GLOB_CASE_SENSITIVITY"] = {
    "probe_dir": d, "files_created": ["c2_s1_V1_2099.json", "c2_s1_v1_2099.json"],
    "matched_by_pattern_*_v1_*.json": m,
    "CASE_INSENSITIVE_HERE": len(m) == 2,
    "MEANING": ("on this filesystem the loader's pattern matches BOTH cases, so a file "
                "differing only in case would be read here and skipped on a case-sensitive "
                "filesystem: the same bytes would give a different file set. No such file "
                "exists in CASES today." if len(m) == 2 else
                "case-sensitive here; the pattern binds exactly one case")}

# ---- D does the order the four variables are read in matter?
canon = ["SAMPLE_SIZE / DENOMINATOR", "ACTIVE_INFESTATION_COUNT",
         "DAMAGING_INFESTATION_COUNT", "TOTAL_INFESTATION_COUNT"]
import hashlib
hashes = {}
for perm in [tuple(canon), tuple(reversed(canon)),
             (canon[2], canon[0], canon[3], canon[1])]:
    L = di_core.load_visits(CASE, sheet, AS_OF, wanted=perm)
    key = json.dumps({k: v for k, v in L.items() if k not in ("visits", "provenance")},
                     sort_keys=True, default=str)
    vis = json.dumps([{kk: vv for kk, vv in v.items()} for v in L["visits"]],
                     sort_keys=True, default=str)
    hashes[" | ".join(perm)] = hashlib.sha256((key + vis).encode()).hexdigest()
out["D_VARIABLE_READ_ORDER"] = {
    "per_permutation": hashes,
    "distinct": len(set(hashes.values())),
    "INVARIANT_TO_THE_ORDER_THE_VARIABLES_ARE_REQUESTED_IN": len(set(hashes.values())) == 1}

print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_09_residual.json"), "w", encoding="utf-8"),
          indent=1, default=str)
