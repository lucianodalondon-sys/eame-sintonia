import gzip, json, os, glob, datetime, collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB  = os.path.join(BASE, 'raw', 'F4-arpav-rest', 'tabella')

W0 = datetime.date(2014, 3, 1)
W1 = datetime.date(2025, 10, 31)
WINDOW_DAYS = (W1 - W0).days + 1

files = sorted(glob.glob(os.path.join(TAB, '*.json.gz')))
print("total .json.gz files scanned:", len(files))

days = collections.defaultdict(set)
rows = collections.Counter()
bfogl_files = set()
tipos = collections.Counter()

for f in files:
    try:
        d = json.load(gzip.open(f))
    except Exception as e:
        print("UNREADABLE", f, e)
        continue
    for r in (d.get('data') or []):
        t = r.get('tipo')
        tipos[t] += 1
        if t != 'BFOGL':
            continue
        bfogl_files.add(os.path.basename(f))
        dt = datetime.date.fromisoformat(r['dataora'][:10])
        if W0 <= dt <= W1:
            key = "%s (%s)" % (r['nome_stazione'], r['codice_stazione'])
            days[key].add(dt)
            rows[key] += 1

print("distinct tipo codes across all files:", dict(tipos))
print("files containing >=1 BFOGL row:", len(bfogl_files))
print("distinct BFOGL stations:", len(days))
print("window", W0, "..", W1, "=", WINDOW_DAYS, "days")
print()
print("%-42s %6s %9s %13s %8s %8s" % ("station", "rows", "distinct", "pct", "ge99.4", "ge99.3"))
res = []
for k, v in days.items():
    n = len(v)
    pct = 100.0 * n / WINDOW_DAYS
    res.append((pct, k, rows[k], n))
res.sort(reverse=True)
for pct, k, rw, n in res:
    print("%-42s %6d %9d %12.4f%% %8s %8s" % (k, rw, n, pct, pct >= 99.4, pct >= 99.3))

strict4 = sum(1 for pct, _, _, _ in res if pct >= 99.4)
strict3 = sum(1 for pct, _, _, _ in res if pct >= 99.3)
lenient4 = sum(1 for pct, _, _, _ in res if round(pct, 1) >= 99.4)
print()
print("count pct >= 99.4 (strict) :", strict4, "of", len(res))
print("count pct >= 99.3 (strict) :", strict3, "of", len(res))
print("count round(pct,1) >= 99.4 :", lenient4, "of", len(res))
print("rows == distinct for all   :", all(rw == n for _, _, rw, n in res))
