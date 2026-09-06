import json, collections, datetime as dt, sys

PF = r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json"
pf = json.load(open(PF, encoding="utf-8"))

A, B = "2014-03-01", "2025-10-31"
WIN = (dt.date(2025, 10, 31) - dt.date(2014, 3, 1)).days + 1
print("window 2014-03-01..2025-10-31 inclusive =", WIN, "days")

bf = [f for f in pf if f["tipo"] == ["BFOGL"]]
print("BFOGL files:", len(bf), "rows:", sum(f["rows"] for f in bf))

st = collections.defaultdict(set)
name, yrs, allrows, units = {}, collections.defaultdict(set), collections.Counter(), collections.defaultdict(set)
for f in bf:
    k = f["station_code"][0]
    name[k] = f["station"][0]
    yrs[k].add(f["year"])
    allrows[k] += f["rows"]
    units[k] |= set(f["unit"])
    for d in f["dates"]:
        if A <= d <= B:
            st[k].add(d)

print("BFOGL stations:", len(st))
print("units seen:", sorted(set().union(*units.values())))
print()
hdr = "{:<30} {:>6} {:>7} {:>8} {:>7}  {}".format("station", "code", "inwin", "pct", "rows", "years")
print(hdr)
rows = []
for k in sorted(st, key=lambda x: -len(st[x])):
    pct = 100.0 * len(st[k]) / WIN
    rows.append((name[k], k, len(st[k]), pct, allrows[k], min(yrs[k]), max(yrs[k]), len(yrs[k])))
for r in rows:
    print("{:<30} {:>6} {:>7} {:>7.2f}% {:>7}  {}-{} ({} yrs)".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
print()
ge = [r for r in rows if r[3] >= 99.4]
print("stations at or above 99.40 pct of window:", len(ge), "of", len(rows))
lt = [r for r in rows if r[3] < 99.4]
print("stations BELOW 99.40 pct:", [(r[0], round(r[3], 2)) for r in lt])
