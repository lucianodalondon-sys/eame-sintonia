import json, collections, datetime as dt

RC = json.load(open(r"C:/disease-local-collection-italy/pilot-disease-local-collection/manifests/daily-series-recount.json", encoding="utf-8"))
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))

A, B = "2014-03-01", "2025-10-31"
WIN = (dt.date(2025, 10, 31) - dt.date(2014, 3, 1)).days + 1

bf = [f for f in pf if f["tipo"] == ["BFOGL"]]
mine = collections.defaultdict(set)
codeof = {}
for f in bf:
    k = f["station"][0]
    codeof[k] = f["station_code"][0]
    for d in f["dates"]:
        if A <= d <= B:
            mine[k].add(d)

print("top-level recount keys:", list(RC.keys()))
print()
print("{:<32} {:>9} {:>9} {:>7} {:>9} {:>9} {:>7}".format(
    "station(recount name)", "rc_inwin", "my_inwin", "delta", "rc_pct", "my_pct", "flag"))
n_ge_rc = n_ge_my = 0
for e in RC["leaf_wetness"]:
    nm = e["stazione"]
    base = nm.rsplit(" (", 1)[0]
    my = len(mine.get(base, set()))
    rcv = e["days_in_window_2014_2025"]
    rcpct = e["window_coverage_pct"]
    mypct = 100.0 * my / WIN
    if rcpct >= 99.4: n_ge_rc += 1
    if mypct >= 99.4: n_ge_my += 1
    flag = "" if my == rcv else "MISMATCH"
    print("{:<32} {:>9} {:>9} {:>7} {:>8.2f}% {:>8.2f}% {:>7}".format(nm, rcv, my, my - rcv, rcpct, mypct, flag))
print()
print("recount rows claiming >=99.4 pct:", n_ge_rc, " my count:", n_ge_my, " of", len(RC["leaf_wetness"]))
print("recount window_days field values:", sorted(set(e["window_days"] for e in RC["leaf_wetness"])))
