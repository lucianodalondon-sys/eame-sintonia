"""A row is not an observation. Count how many preserved rows actually carry a
value, per sensor type — and show the real shape of the stored value."""
import json, os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rec = json.load(open(os.path.join(ROOT, 'manifests', 'daily-series-recount.json'), encoding='utf-8'))

agg = defaultdict(lambda: {'rows': 0, 'nonnull': 0, 'files': 0})
for r in rec['per_file']:
    a = agg[r['tipo']]
    a['rows'] += r['rows']
    a['nonnull'] += r['nonnull_values']
    a['files'] += 1

print(f'{"tipo":10} {"files":>6} {"rows":>8} {"rows with a value":>18} {"%":>7}')
for k in sorted(agg, key=lambda k: -agg[k]['rows']):
    v = agg[k]
    pct = 100 * v['nonnull'] / v['rows'] if v['rows'] else 0
    print(f'{k:10} {v["files"]:6d} {v["rows"]:8d} {v["nonnull"]:18d} {pct:6.2f}%')

# show the true stored shape for one leaf-wetness file and one temperature file
import gzip
TAB = os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella')
for tipo in ('BFOGL', 'TARIA2M', 'UMID2M', 'PREC', 'RADSOL'):
    f = next((r for r in rec['per_file'] if r['tipo'] == tipo and r['anno'] == 2015), None)
    if not f:
        continue
    with gzip.open(os.path.join(TAB, f['file']), 'rb') as g:
        rows = json.loads(g.read())['data']
    mid = rows[len(rows) // 2]
    print(f'\n{tipo} sample ({f["stazione"]}, {f["anno"]}) unit={f["unit"]}:')
    print('  ', json.dumps(mid, ensure_ascii=False)[:240])
