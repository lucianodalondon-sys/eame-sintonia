import json, os, gzip, collections, datetime
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

MAN = rd('manifests/arpav-daily-manifest.jsonl')
bf = [r for r in MAN if 'agnatura' in r['sensore']]
W0 = datetime.date(2014, 3, 1); W1 = datetime.date(2025, 10, 31)
N = (W1 - W0).days + 1
print("window days:", N)

dates = collections.defaultdict(set)
rows = collections.Counter()
for r in bf:
    d = json.loads(gzip.decompress(open(P(r['raw_path']), 'rb').read()).decode('utf-8'))
    for row in d['data']:
        ds = str(row.get('dataora') or '')[:10]
        try:
            dt = datetime.date(int(ds[:4]), int(ds[5:7]), int(ds[8:10]))
        except Exception:
            continue
        if W0 <= dt <= W1:
            dates[r['stazione']].add(dt)
            rows[r['stazione']] += 1

print()
print("%-42s %8s %8s %12s %10s" % ("station", "rows", "distinct", "pct(distinct)", ">=99.4?"))
ge_strict = ge_round = 0
for st in sorted(dates, key=lambda k: -len(dates[k])):
    n = len(dates[st])
    pct = 100.0 * n / N
    strict = pct >= 99.4
    rnd = round(pct, 1) >= 99.4
    ge_strict += strict
    ge_round += rnd
    print("%-42s %8d %8d %12.4f%% %10s%s" % (st[:42], rows[st], n, pct, strict,
          "  <-- rounds UP to 99.4" if (rnd and not strict) else ""))
print()
print("stations with pct >= 99.4 (strict):", ge_strict, "of", len(dates))
print("stations with round(pct,1) >= 99.4 (lenient):", ge_round, "of", len(dates))
print("rows == distinct dates for every station?:", all(rows[s] == len(dates[s]) for s in dates))

# what does the recount file say
R = json.load(open(P('manifests/daily-series-recount.json'), encoding='utf-8'))
print()
print("recount top-level type:", type(R), (list(R.keys())[:15] if isinstance(R, dict) else len(R)))
