"""L4 AUDIT — independent recount of the daily series, opening every gz file.

Read-only. Recomputes: file count, sha256, row count, value-presence, sensor mix,
Treviso leaf-wetness scope, and per-station coverage in the C4 window.
"""
import json, gzip, os, hashlib, collections, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella')

man = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'),
                                   encoding='utf-8') if l.strip()]

disk = sorted(f for f in os.listdir(TAB) if f.endswith('.json.gz'))
print('manifest rows        :', len(man))
print('files on disk (.gz)  :', len(disk))
print('manifest raw_paths   :', len(set(r['raw_path'] for r in man)))
print('PRESERVED rows       :', sum(1 for r in man if r.get('preservation') == 'PRESERVED'))
print('api_success true     :', sum(1 for r in man if r.get('api_success') is True))
print('http_status != 200   :', sum(1 for r in man if r.get('http_status') != 200))

# ---- C6 distinct sha256, recomputed from the bytes on disk
sha_manifest = collections.Counter(r['sha256'] for r in man)
print('distinct sha256 in manifest :', len(sha_manifest))
dups = {k: v for k, v in sha_manifest.items() if v > 1}
print('manifest sha collisions     :', len(dups))

real_sha = {}
mismatch = []
for r in man:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    if not os.path.exists(p):
        mismatch.append((r['local_item_id'], 'MISSING_FILE'))
        continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    real_sha[r['raw_path']] = h
    if h != r['sha256']:
        mismatch.append((r['local_item_id'], 'SHA_MISMATCH'))
print('recomputed sha mismatches   :', len(mismatch), mismatch[:5])
print('distinct sha256 on disk     :', len(set(real_sha.values())))

# ---- C2 rows + value presence, opening each gz
total_rows = 0
rows_with_value = 0
rows_null = 0
sensor_rows = collections.Counter()
sensor_files = collections.Counter()
unit_by_sensor = collections.defaultdict(collections.Counter)
valuekeys = collections.Counter()
per_file_rows = {}
bfogl_dates = collections.defaultdict(set)   # station name -> set of dates
bfogl_years = collections.Counter()
bfogl_prov = collections.Counter()
station_prov = {}

for r in man:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    with gzip.open(p, 'rb') as fh:
        d = json.loads(fh.read().decode('utf-8'))
    data = d.get('data') if isinstance(d, dict) else d
    if data is None:
        for k in ('rows', 'result', 'items'):
            if isinstance(d, dict) and k in d:
                data = d[k]
                break
    n = len(data) if isinstance(data, list) else 0
    per_file_rows[r['raw_path']] = n
    total_rows += n
    sensor_files[r['sensore']] += 1
    sensor_rows[r['sensore']] += n
    unit_by_sensor[r['sensore']][r.get('unit')] += 1
    if isinstance(data, list):
        for row in data:
            if not isinstance(row, dict):
                continue
            for k in row:
                valuekeys[k] += 1
            v = row.get('valore', row.get('valore_giornaliero', row.get('value')))
            if v is None or v == '':
                rows_null += 1
            else:
                rows_with_value += 1
    if r.get('tipo') == 'BFOGL':
        bfogl_years[r['anno']] += 1
        for row in (data or []):
            dt = row.get('data') or row.get('dataora') or row.get('giorno')
            if dt:
                bfogl_dates[r['stazione']].add(str(dt)[:10])

print()
print('TOTAL ROWS recounted        :', total_rows)
print('rows with a value           :', rows_with_value)
print('rows with null/empty value  :', rows_null)
print('manifest sum(rows)          :', sum(r.get('rows', 0) for r in man))
print('row-key names seen          :', dict(valuekeys.most_common(12)))
print()
print('--- sensors (files / rows / units) ---')
for s, c in sensor_files.most_common():
    print('  %-34s files=%4d rows=%7d units=%s' % (s, c, sensor_rows[s], dict(unit_by_sensor[s])))

# ---- C3 leaf wetness scope
bf = [r for r in man if r.get('tipo') == 'BFOGL']
print()
print('--- C3 leaf wetness (tipo=BFOGL) ---')
print('BFOGL files                 :', len(bf))
print('BFOGL manifest rows sum     :', sum(r.get('rows', 0) for r in bf))
print('BFOGL recounted rows        :', sum(per_file_rows[r['raw_path']] for r in bf))
print('BFOGL distinct stations     :', len(set(r['stazione'] for r in bf)))
print('BFOGL years                 :', sorted(bfogl_years))
print('BFOGL units                 :', dict(collections.Counter(r.get('unit') for r in bf)))
print('BFOGL stations             :')
for s in sorted(set(r['stazione'] for r in bf)):
    print('   ', s)

# ---- C4 coverage in window
W0 = datetime.date(2014, 3, 1)
W1 = datetime.date(2025, 10, 31)
ndays = (W1 - W0).days + 1
print()
print('--- C4 window %s..%s = %d days ---' % (W0, W1, ndays))
cov = []
for st, ds in bfogl_dates.items():
    inw = set()
    for s in ds:
        try:
            dd = datetime.date(int(s[0:4]), int(s[5:7]), int(s[8:10]))
        except Exception:
            continue
        if W0 <= dd <= W1:
            inw.add(dd)
    cov.append((len(inw) / ndays * 100, len(inw), st))
cov.sort(reverse=True)
for pct, n, st in cov:
    print('  %6.2f%%  %5d/%d  %s' % (pct, n, ndays, st))
print('stations >= 99.4%%          :', sum(1 for p, _, _ in cov if p >= 99.4))
