import json, collections, datetime as dt
from fractions import Fraction

pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
A, B = dt.date(2014, 3, 1), dt.date(2025, 10, 31)
W = set((A + dt.timedelta(i)).isoformat() for i in range((B - A).days + 1))
n = len(W)
print("window days recomputed by iteration:", n)
print("cross-check by arithmetic (11y + 3 leap + 244d + 1):", 11 * 365 + 3 + 244 + 1)

have = collections.defaultdict(set); name = {}
for f in pf:
    if f["tipo"] != ["BFOGL"]:
        continue
    k = f["station_code"][0]; name[k] = f["station"][0]
    have[k] |= set(f["dates"])

print()
print("{:<30} {:>6} {:>16} {:>8} {:>8} {:>8}".format("station", "days", "exact_pct", "2dp", "1dp", "ge99.4?"))
c_exact = c_1dp = 0
for k in sorted(have, key=lambda x: -len(have[x] & W)):
    d = len(have[k] & W)
    p = 100.0 * d / n
    ge = p >= 99.4
    ge1 = round(p, 1) >= 99.4
    c_exact += ge; c_1dp += ge1
    print("{:<30} {:>6} {:>16.6f} {:>8.2f} {:>8.1f} {:>8}".format(name[k], d, p, round(p, 2), round(p, 1), "YES" if ge else "no"))
print()
print("stations >= 99.4 pct on the EXACT value :", c_exact, "of", len(have))
print("stations >= 99.4 pct after rounding to 1 decimal FIRST:", c_1dp, "of", len(have))
print()
print("Castelfranco Veneto exact fraction:", Fraction(len(have[102] & W), n), "=", 100 * len(have[102] & W) / n)
print("days it would need for a true 99.4 pct:", -(-int(0.994 * n * 1000) // 1000), "->", (0.994 * n))
