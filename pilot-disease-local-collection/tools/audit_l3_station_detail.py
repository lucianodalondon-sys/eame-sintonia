import json, collections, datetime as dt

pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
A, B = dt.date(2014, 3, 1), dt.date(2025, 10, 31)
WIN = [A + dt.timedelta(d) for d in range((B - A).days + 1)]
WINS = set(x.isoformat() for x in WIN)
print("window days:", len(WINS))

# season = Mar 1 .. Oct 31 of each year in window (grape disease season)
SEASON = set(x.isoformat() for x in WIN if 3 <= x.month <= 10)
print("season days (Mar-Oct) inside window:", len(SEASON))
print()

bf = [f for f in pf if f["tipo"] == ["BFOGL"]]
have = collections.defaultdict(set)
name, byyear = {}, collections.defaultdict(dict)
for f in bf:
    k = f["station_code"][0]
    name[k] = f["station"][0]
    have[k] |= set(f["dates"])
    byyear[k][f["year"]] = (f["distinct_dates"], f["calendar_days"], f["first"], f["last"])

print("{:<30} {:>5} {:>7} {:>8} {:>9} {:>9} {:>8}".format(
    "station", "code", "win_ok", "win_pct", "season_ok", "seas_pct", "miss_in_season"))
res = []
for k in sorted(have, key=lambda x: -len(have[x] & WINS)):
    w = have[k] & WINS
    s = have[k] & SEASON
    miss_w = WINS - have[k]
    miss_s = SEASON - have[k]
    res.append((name[k], k, len(w), 100.0 * len(w) / len(WINS), len(s), 100.0 * len(s) / len(SEASON), len(miss_s), sorted(miss_w)))
for r in res:
    print("{:<30} {:>5} {:>7} {:>7.2f}% {:>9} {:>7.2f}% {:>8}".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6]))

print()
print("=== missing days in window, by station, grouped by month-of-year ===")
for r in res:
    miss = r[7]
    if not miss:
        print("{:<30} none".format(r[0])); continue
    mon = collections.Counter(d[5:7] for d in miss)
    runs = []
    prev = None; start = None
    for d in miss:
        cur = dt.date.fromisoformat(d)
        if prev is not None and (cur - prev).days == 1:
            pass
        else:
            if start is not None: runs.append((start, prev))
            start = cur
        prev = cur
    if start is not None: runs.append((start, prev))
    longest = max(runs, key=lambda x: (x[1] - x[0]).days)
    print("{:<30} missing={:<5} longest_gap={} days ({}..{})  months={}".format(
        r[0], len(miss), (longest[1] - longest[0]).days + 1, longest[0], longest[1], dict(sorted(mon.items()))))

print()
print("=== per-station per-year BFOGL distinct dates vs calendar ===")
for k in sorted(byyear, key=lambda x: name[x]):
    line = []
    for y in sorted(byyear[k]):
        dd, cal, fi, la = byyear[k][y]
        mark = "" if dd == cal else "*"
        line.append("{}:{}/{}{}".format(y, dd, cal, mark))
    print("{:<30} {}".format(name[k], " ".join(line)))
