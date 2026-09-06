# INDEPENDENT: builds the leaf-wetness picture ONLY from raw gz payloads.
# Ignores every manifest-claimed field (rows, first_date, completeness...).
import gzip, json, glob, os
from collections import defaultdict

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
files = sorted(glob.glob(os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella', '*.json.gz')))
print("gz files on disk:", len(files))

st_dates   = defaultdict(set)     # station -> set(date) for BFOGL rows
st_files   = defaultdict(set)     # station -> set(filename)
st_years   = defaultdict(set)     # station -> set(year seen in payload)
st_fileyrs = defaultdict(set)     # station -> set(year taken from filename)
units      = defaultdict(set)
bf_rows    = 0
bf_empty   = 0
allsens    = defaultdict(int)

for f in files:
    with gzip.open(f, 'rt', encoding='utf-8') as fh:
        d = json.load(fh)
    rows = d.get('data') or []
    base = os.path.basename(f)
    fyear = int(base.split('_')[1].split('.')[0])
    for r in rows:
        allsens[r.get('tipo')] += 1
        if r.get('tipo') != 'BFOGL':
            continue
        bf_rows += 1
        v = r.get('valore')
        if v is None or v == '':
            bf_empty += 1
        s = r['nome_stazione']
        day = r['dataora'][:10]
        st_dates[s].add(day)
        st_files[s].add(base)
        st_years[s].add(int(day[:4]))
        st_fileyrs[s].add(fyear)
        units[s].add(r.get('unitnm'))

print("BFOGL stations:", len(st_dates))
print("BFOGL files   :", sum(len(v) for v in st_files.values()))
print("BFOGL rows    :", bf_rows, "| rows with empty value:", bf_empty)
print("units seen    :", sorted({u for s in units.values() for u in s}))
print("sensor tipos in whole tabella corpus:",
      dict(sorted(allsens.items(), key=lambda kv: -kv[1])))

with open(os.path.join(ROOT, 'tools', '_v3_bfogl_dates.json'), 'w') as fh:
    json.dump({s: sorted(v) for s, v in st_dates.items()}, fh)

print()
print("=== per-station span, computed from raw payload dates ===")
print("%-38s %5s %9s %10s %10s %4s  %s" %
      ('station', 'files', 'daysheld', 'minDate', 'maxDate', 'yrs', 'yearsPresent'))
tot = 0
for s in sorted(st_dates):
    ds = sorted(st_dates[s])
    yrs = sorted(st_years[s])
    tot += len(st_files[s])
    print("%-38s %5d %9d %10s %10s %4d  %d-%d" %
          (s, len(st_files[s]), len(ds), ds[0], ds[-1], len(yrs), yrs[0], yrs[-1]))
print("total BFOGL files:", tot)

print()
print("=== does each station have a file for every year 2010..2026? ===")
full = set(range(2010, 2027))
missing_total = 0
for s in sorted(st_fileyrs):
    miss = sorted(full - st_fileyrs[s])
    missing_total += len(miss)
    flag = "" if not miss else "  <-- NO FILE FOR " + ",".join(map(str, miss))
    print("%-38s fileyears=%2d%s" % (s, len(st_fileyrs[s]), flag))
print("14 stations x 17 years = %d; missing station-years = %d; => expected files = %d"
      % (14 * 17, missing_total, 14 * 17 - missing_total))
