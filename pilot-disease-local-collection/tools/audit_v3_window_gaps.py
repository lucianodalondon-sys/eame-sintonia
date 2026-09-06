# INDEPENDENT window + gap arithmetic, from the date sets extracted from raw gz.
import json, os, datetime as dt

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
D = json.load(open(os.path.join(ROOT, 'tools', '_v3_bfogl_dates.json')))

W0 = dt.date(2014, 3, 1)
W1 = dt.date(2025, 10, 31)
wdays = [W0 + dt.timedelta(d) for d in range((W1 - W0).days + 1)]
print("window %s .. %s  = %d days" % (W0, W1, len(wdays)))
wset = {d.isoformat() for d in wdays}

def longest_gap(have, lo, hi):
    """longest run of consecutive absent days inside [lo,hi]"""
    best = 0; bestrange = None; run = 0; start = None
    d = lo
    while d <= hi:
        s = d.isoformat()
        if s not in have:
            if run == 0: start = d
            run += 1
            if run > best:
                best = run; bestrange = (start, d)
        else:
            run = 0
        d += dt.timedelta(1)
    return best, bestrange

print()
print("%-30s %8s %8s %8s %8s   %s" %
      ('station', 'inWin', 'missing', 'pct', 'totdays', 'longest gap inside window'))
rows = []
for s in sorted(D):
    have = set(D[s])
    inwin = len(have & wset)
    miss = len(wset) - inwin
    pct = 100.0 * inwin / len(wset)
    g, gr = longest_gap(have, W0, W1)
    rows.append((s, inwin, miss, pct, len(have), g, gr))
    grs = "" if not gr else "%d days (%s..%s)" % (g, gr[0], gr[1])
    print("%-30s %8d %8d %7.2f%% %8d   %s" % (s, inwin, miss, pct, len(have), grs))

print()
print("--- Breda specifics ---")
b = 'Breda di Piave - Via Bovon'
have = set(D[b])
print("days held total          :", len(have))
print("days held inside window  :", len(have & wset))
print("window size              :", len(wset))
print("pct of window            : %.2f%%" % (100.0 * len(have & wset) / len(wset)))
print("first day held anywhere  :", min(have))
print("last day held anywhere   :", max(have))
# the specific hole the finding names
h0, h1 = dt.date(2014, 3, 1), dt.date(2016, 10, 6)
span = (h1 - h0).days + 1
inhole = sum(1 for d in range(span) if (h0 + dt.timedelta(d)).isoformat() in have)
print("2014-03-01..2016-10-06 spans %d days; days held there = %d" % (span, inhole))

print()
print("--- contribution to 2010-01-01 .. 2016-10-06 ---")
P0, P1 = dt.date(2010, 1, 1), dt.date(2016, 10, 6)
pset = {(P0 + dt.timedelta(d)).isoformat() for d in range((P1 - P0).days + 1)}
print("period days:", len(pset))
for s in sorted(D):
    n = len(set(D[s]) & pset)
    print("%-30s %6d days%s" % (s, n, "   <-- ZERO" if n == 0 else ""))
